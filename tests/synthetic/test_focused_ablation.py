"""Small quality-blind randomization and deterministic budget checks."""

import hashlib
import inspect
import json
from itertools import combinations
from pathlib import Path

import pytest

from cnbi_v2.synthetic.ablation import random_subsets, select_scenarios, solve_subset, subset_counts


def universe():
    return {
        "C_" + "_".join(str(i + 1) for i in ids): ids
        for k in (2, 3)
        for ids in combinations(range(6), k)
    }


def test_per_k_budget_determinism_and_seed_independence():
    u = universe()
    args = (u, {2: 4, 3: 3}, "frozen_scenario", 2)
    a, deficits = random_subsets(*args, 181001)
    assert a == random_subsets(*args, 181001)[0]
    assert a != random_subsets(*args, 181002)[0]
    assert subset_counts(a, u) == {2: 4, 3: 3}
    assert len(set(a)) == 7 and not deficits
    assert a == random_subsets(dict(reversed(list(u.items()))), *args[1:], 181001)[0]


def test_insufficient_geometry_is_explicit():
    names, deficits = random_subsets({"pair": (0, 1)}, {2: 2, 3: 1}, "s", 1, 181001)
    assert names == ["pair"] and deficits == {2: 1, 3: 1}
    with pytest.raises(ValueError):
        random_subsets(universe(), {2: -1}, "s", 1, 181001)


def test_selection_and_search_have_no_oracle_or_mc_api():
    code = inspect.getsource(random_subsets) + inspect.getsource(solve_subset)
    for forbidden in ("true_anchors", "evaluate_metrics", "sample_coefficient", "reoptimize"):
        assert forbidden not in code


def test_cost_only_selection_rule():
    ranked = [dict(scenario_id=str(i), total_seconds=i, nx=2 if i < 5 else 3) for i in range(1, 7)]
    assert select_scenarios(ranked) == ("1", "2", "3", "5")
    ranked[1]["nx"] = 3
    assert select_scenarios(ranked) == ("1", "2", "3", "4")


def test_completed_artifacts_match_frozen_plan_and_hashes():
    root = Path(__file__).resolve().parents[2]
    output = root / "results/phase_10_synthetic_ablation/focused_20261031"
    protocol_path = output / "ablation_protocol.json"
    if not protocol_path.exists() or json.loads(protocol_path.read_text())["status"] != "COMPLETED":
        pytest.skip("campaign not complete yet")
    protocol = json.loads(protocol_path.read_text())
    assert len(protocol["selected_scenarios"]) == 4 and len(protocol["plans"]) == 20
    assert select_scenarios(protocol["cost_ranking"]) == tuple(
        c["scenario_id"] for c in protocol["selected_scenarios"]
    )
    for relative, expected in protocol["artifact_sha256"].items():
        assert hashlib.sha256((output / relative).read_bytes()).hexdigest() == expected
    for p in protocol["plans"].values():
        universe = p["universe"]
        targets = {int(k): v for k, v in p["target_counts"].items()}
        assert all(len(universe[s]) == 2 for s in p["A3"])
        for draw in p["A2"].values():
            assert subset_counts(draw["subsets"], universe) == targets
            assert not draw["deficits"]
