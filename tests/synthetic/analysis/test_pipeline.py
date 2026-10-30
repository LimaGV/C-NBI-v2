import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "results/phase_10_synthetic_analysis/statistical_20261030"


def test_hv_complete_cells_not_partial_replica_medians(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/validation"))
    from phase10e_statistics import METHODS, medians

    rows = [
        dict(
            scenario_id=sid,
            replica_id=r,
            method=m,
            HV=float(r),
            HV_status="PRECISION_CRITERIA_PASSED",
        )
        for sid in ("a", "b")
        for r in range(1, 6)
        for m in METHODS
    ]
    frame = pd.DataFrame(rows)
    frame.loc[0, "HV_status"] = "PRECISION_PENDING"
    summary, wide, excluded = medians(frame, "HV")
    assert len(wide) == 1 and list(wide.index) == ["b"]
    assert len(summary) == 4 and summary["median"].eq(3).all()
    assert excluded[0]["scenario_id"] == "a"
    assert len(medians(frame, "HV", strict_hv=False)[1]) == 2
    frame.loc[0, "HV"] = np.nan
    assert len(medians(frame, "HV", strict_hv=False)[1]) == 1
    for malformed in (frame.iloc[:-1], pd.concat([frame, frame.iloc[:1]])):
        with pytest.raises(ValueError):
            medians(malformed, "HV")
    frame["replica_id"] = 0
    with pytest.raises(ValueError):
        medians(frame, "HV")


def test_analysis_has_no_search_fit_reference_generation_or_official_write_channel():
    paths = list((ROOT / "src/cnbi_v2/synthetic/analysis").glob("*.py")) + list(
        (ROOT / "scripts/validation").glob("phase10e_*.py")
    )
    forbidden = {
        "run_method",
        "solve_nbi_lattice",
        "run_evolutionary",
        "fit_multivariate_rsm",
        "solve_quadratic_ball",
        "sample_coefficient_ensemble",
        "generate_instance",
        "full_ccd",
        "experimental_noise",
        "calibrate",
    }
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                function = getattr(node.func, "id", getattr(node.func, "attr", ""))
                assert function not in forbidden, (path, function)
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(
                    (
                        "cnbi_v2.synthetic.benchmark.runner",
                        "cnbi_v2.synthetic.benchmark.cnbi_runner",
                        "cnbi_v2.synthetic.benchmark.vrf_runner",
                        "cnbi_v2.synthetic.benchmark.ea_runner",
                    )
                )
    policy = json.loads((ROOT / "docs/policies/synthetic_analysis_10e.json").read_text())
    assert policy["input_campaign"].endswith("campaign_v2")
    assert not any(policy["scope"].values())
    assert policy["bootstrap"]["unit"].startswith("complete scenario")


def test_input_snapshot_and_official_pairing(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/validation"))
    from phase10e_derive import paired_tasks
    from phase10e_inputs import digest, read

    inventory = read(RESULT / "frozen_inputs_manifest.json")
    assert len(inventory["files"]) == 7156
    assert inventory["input_commit"] == "5c3829dbd1bdd41ee828cfaf919c551d4f869d32"
    for relative, expected in inventory["files"].items():
        assert digest(ROOT / relative) == expected, relative
    tasks, blocks = paired_tasks()
    assert len(tasks) == 540 and len(blocks) == 135
