"""Integrity of complete local unions and preserved historical caches."""

import csv
import hashlib
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = ROOT / "results/phase_10_synthetic_ablation/focused_20261031"
OUT = ROOT / "results/phase_10_synthetic_ablation/svd_pa_definitive_20261031"


def test_complete_universe_and_frozen_missing_budget():
    plan = json.loads((PREVIOUS / "ablation_protocol.json").read_text())
    audit = json.loads((OUT / "cache_compatibility_audit.json").read_text())
    assert len(audit["historical_caches"]) == 477
    assert len(audit["missing"]) == 378
    assert sum(t["subproblems"] for t in audit["missing"]) == 13208
    for instance, p in plan["plans"].items():
        nx = int(instance[2])
        m = len(p["payoff"])
        expected = {tuple(c) for k in range(2, nx + 2) for c in combinations(range(m), k)}
        assert {tuple(v) for v in p["universe"].values()} == expected
    for row in audit["historical_caches"]:
        path = PREVIOUS / "subset_cache" / row["instance"] / row["subset_id"]
        for name, key in [("record.json", "record_sha256"), ("decisions.npz", "decisions_sha256")]:
            assert hashlib.sha256((path / name).read_bytes()).hexdigest() == row[key]


def test_all_nd_is_recomputed_from_complete_local_candidates():
    for path in (OUT / "instances").glob("*/ALL_candidates.npz"):
        instance = path.parent.name
        plan = json.loads((PREVIOUS / "ablation_protocol.json").read_text())["plans"][instance]
        names = sorted(
            plan["universe"], key=lambda s: (len(plan["universe"][s]), plan["universe"][s])
        )
        points = []
        for name in names:
            old = PREVIOUS / "subset_cache" / instance / name / "decisions.npz"
            new = OUT / "subset_cache" / instance / name / "decisions.npz"
            points.append(np.load(old if old.exists() else new)["decisions"])
        stored = np.load(path)
        np.testing.assert_array_equal(stored["raw_decisions"], np.vstack(points))
        assert len(stored["source_weights"]) == len(stored["raw_decisions"])


def test_three_arms_same_B_and_preserved_random_seed_variability():
    p = json.loads((OUT / "ablation_protocol.json").read_text())
    if p["status"] != "COMPLETED":
        pytest.skip("nx3 execution still in progress")

    def exact(path):
        with path.open(newline="", encoding="utf-8") as stream:
            records = list(csv.DictReader(stream))
        for r in records:
            for k in ("replica_id", "random_seed", "B_effective"):
                r[k] = int(r[k])
            for k in ("GD", "IGD", "HV", "Spacing", "Sparsity"):
                r[k] = float(r[k])
        return pd.DataFrame(records)

    rows = exact(OUT / "ablation_results.csv")
    before = exact(PREVIOUS / "ablation_results.csv")
    assert len(rows) == 100 and set(rows.variant) == {"FILTER", "RANDOM", "ALL"}
    for _, group in rows.groupby(["scenario_id", "replica_id"]):
        assert group.B_effective.nunique() == 1
        assert set(group[group.variant == "RANDOM"].random_seed) == {181001, 181002, 181003}
        assert group[group.variant == "FILTER"].counts_by_k.iloc[0] in set(
            group[group.variant == "RANDOM"].counts_by_k
        )
    for r in rows[rows.variant != "ALL"].itertuples():
        source = before[
            (before.scenario_id == r.scenario_id)
            & (before.replica_id == r.replica_id)
            & (before.random_seed == r.random_seed)
            & (before.variant == ("A0" if r.variant == "FILTER" else "A2"))
        ].iloc[0]
        for k in ("GD", "IGD", "HV", "Spacing", "Sparsity"):
            assert getattr(r, k) == source[k]
    for relative, sha in p["artifact_sha256"].items():
        assert hashlib.sha256((OUT / relative).read_bytes()).hexdigest() == sha
