"""Artifact validation must detect scientific edits, not merely file presence."""

import copy
import shutil
from pathlib import Path

import numpy as np
import pytest

from cnbi_v2.synthetic.benchmark.archive import read_json
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context

ROOT = Path(__file__).resolve().parents[3]
CASE = ROOT/"results/phase_10_synthetic_benchmark/benchmark_20261029/campaign_v2"
NAME = "pilot__nx2_delta1_rho025__replica1__C-NBI"


@pytest.fixture(scope="module")
def data():
    return load_search_inputs(ROOT/"results/phase_10_synthetic_rsm/rsm_20261029")[
        "nx2_delta1_rho025__replica1"]


@pytest.fixture
def auditor(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/"scripts/validation"))
    import audit_phase10d_outputs
    return audit_phase10d_outputs


def test_recomposition_rejects_data_edits_and_float32(auditor, data):
    with np.load(CASE/f"raw_decisions/{NAME}.npz", allow_pickle=False) as arrays:
        x = arrays["decisions"]
    y = data.model.predict(x)
    auditor.check_recomposition(x, y, data)
    changed = y.copy()
    changed[0, 0] += 1e-7
    with pytest.raises(ValueError, match="recomposition mismatch"):
        auditor.check_recomposition(x, changed, data)
    with pytest.raises(ValueError, match="preserve float64"):
        auditor.check_recomposition(x.astype(np.float32), y, data)


def test_pa_audit_rejects_subset_omission_and_threshold_edits(auditor, data):
    original = read_json(CASE/f"algorithm_diagnostics/{NAME}.json")["diagnostics"]
    with np.load(CASE/f"algorithm_diagnostics/{NAME}.npz", allow_pickle=False) as arrays:
        auditor.check_cnbi(data, original, arrays, len(original["raw_origins"]))
        changed = copy.deepcopy(original)
        changed["subsets"].pop()
        with pytest.raises(ValueError, match="eligible subsets"):
            auditor.check_cnbi(data, changed, arrays, len(original["raw_origins"]))
        changed = copy.deepcopy(original)
        local = next(row for row in changed["subsets"] if row["scope"] == "LOCAL")
        local["q95"][0] = local["observed"][0]  # Strict equality must fail PA.
        with pytest.raises(ValueError, match="strict local PA criterion"):
            auditor.check_cnbi(data, changed, arrays, len(original["raw_origins"]))


def test_external_audit_detects_clipping_without_mutating_raw(auditor, data, tmp_path):
    context = load_evaluation_context(
        ROOT/"results/phase_10_synthetic_pareto/analytical_20261029", data.scenario_id,
        ROOT/"results/phase_10_synthetic_generation/structural_20261029")
    with np.load(CASE/f"raw_decisions/{NAME}.npz", allow_pickle=False) as arrays:
        x = arrays["decisions"]
    original = x.copy()
    result = auditor.check_external(CASE, NAME, data, x, context)
    assert result["above_one"] > 0
    out = tmp_path/"external_evaluation"
    out.mkdir()
    shutil.copyfile(CASE/f"external_evaluation/{NAME}.json", out/f"{NAME}.json")
    with np.load(CASE/f"external_evaluation/{NAME}.npz", allow_pickle=False) as arrays:
        changed = {key: arrays[key] for key in arrays.files}
    changed["normalized_responses"] = np.clip(changed["normalized_responses"], 0, 1)
    np.savez_compressed(out/f"{NAME}.npz", **changed)
    with pytest.raises(ValueError, match="fixed analytical normalization"):
        auditor.check_external(tmp_path, NAME, data, x, context)
    np.testing.assert_array_equal(x, original)
