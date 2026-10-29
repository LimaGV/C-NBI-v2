"""Oracle separation, frozen pairing, call accounting and hard budgets."""

import ast
import json
from pathlib import Path

import numpy as np
import pytest

from cnbi_v2.model import quadratic_design
from cnbi_v2.optimization.quadratic import quadratic_responses_from_coefficients
from cnbi_v2.synthetic.benchmark.archive import (
    begin_attempt,
    file_hash,
    json_value,
    read_json,
    recover_attempt,
    save_output,
    verify_payload,
    write_json,
)
from cnbi_v2.synthetic.benchmark.configuration import (
    ea_ceiling,
    lattice_resolution,
    load_ea_configuration,
)
from cnbi_v2.synthetic.benchmark.contracts import METHODS, RunOutput, array_hash, stream_seed
from cnbi_v2.synthetic.benchmark.ea_runner import radial_repair, run_ea
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs
from cnbi_v2.synthetic.benchmark.runner import run_method
from cnbi_v2.synthetic.benchmark.vrf_runner import (
    factor_analysis,
    factor_count,
    vrf_jacobian,
    vrf_values,
)

ROOT = Path(__file__).resolve().parents[3]
RSM = ROOT/"results/phase_10_synthetic_rsm/rsm_20261029"
PACKAGE = ROOT/"src/cnbi_v2/synthetic/benchmark"


@pytest.fixture(scope="module")
def inputs():
    return load_search_inputs(RSM)


def test_frozen_models_are_paired_without_refitting(inputs, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("original model refit forbidden")
    monkeypatch.setattr("cnbi_v2.model.fit_multivariate_rsm", forbidden)
    models = load_search_inputs(RSM)
    assert len(models) == 135
    for key in models:
        np.testing.assert_array_equal(
            models[key].model.coefficients, inputs[key].model.coefficients,
        )
        assert not models[key].observed.flags.writeable
        paired = {method: models[key] for method in METHODS}
        assert len({id(item.model) for item in paired.values()}) == 1
        assert array_hash(models[key].model.coefficients) == array_hash(
            inputs[key].model.coefficients,
        )


def test_search_has_no_truth_or_metric_imports():
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert ".pareto" not in module
                assert module not in {"cnbi_v2.synthetic.rsm.rsm_generation",
                                       "cnbi_v2.synthetic.model"}
                assert not module.startswith("cnbi.")
        if path.name != "vrf_runner.py":
            assert "fit_multivariate_rsm(" not in path.read_text(encoding="utf-8")


def test_seeds_and_budget_policy():
    records = [(sid, r, method, purpose) for sid in ("a", "b") for r in (1, 2)
               for method in METHODS for purpose in ("pilot_search", "official_search")]
    first = {key: stream_seed(*key) for key in records}
    assert first == {key: stream_seed(*key) for key in reversed(records)}
    assert len(set(first.values())) == len(first)
    assert ea_ceiling(4) == 50000 and ea_ceiling(11) == 400400
    assert [lattice_resolution(k) for k in range(2, 7)] == [5, 5, 5, 2, 2]
    with pytest.raises(ValueError):
        lattice_resolution(7)


@pytest.mark.parametrize("nx", [2, 3, 5])
def test_dimension_independent_radial_repair(nx):
    rng = np.random.default_rng(nx)
    alpha = 2**(nx/4)
    x = np.vstack([rng.normal(size=(100, nx))*100, np.zeros((1, nx))])
    original = x.copy()
    repaired = radial_repair(x, alpha)
    np.testing.assert_array_equal(x, original)
    assert np.all(np.linalg.norm(repaired, axis=1) <= alpha)
    np.testing.assert_array_equal(repaired[-1], x[-1])


@pytest.mark.parametrize("method", METHODS[2:])
@pytest.mark.parametrize("nx,delta", [(2, 1), (3, 3), (5, 5)])
def test_ea_reproducibility_full_population_and_no_overshoot(inputs, method, nx, delta):
    data = inputs[f"nx{nx}_delta{delta}_rho060__replica1"]
    config = dict(n_partitions=1, sbx_probability=.9, sbx_eta=15., pm_eta=20.,
                  neighbor_fraction=.2, prob_neighbor_mating=.9)
    first = run_ea(data, method, config, 107, budget=data.m*3+1)
    second = run_ea(data, method, config, 107, budget=data.m*3+1)
    np.testing.assert_array_equal(first.decisions, second.decisions)
    first.validate(data)
    assert len(first.decisions) == data.m
    assert first.counters["original_rsm_point_evaluations"] <= data.m*3+1
    assert first.diagnostics["unspent_budget"] >= 1
    assert np.all(np.linalg.norm(first.decisions, axis=1) <= data.alpha)
    with pytest.raises(ValueError):
        run_ea(data, "unknown", config, 107)
    with pytest.raises(ValueError):
        run_ea(data, method, config, 107, budget=1)


def test_factor_scores_and_complete_vrf_gradient(inputs):
    data = inputs["nx3_delta3_rho060__replica1"]
    analysis = factor_analysis(data.observed, 2)
    loadings = analysis["loadings"]
    weights = loadings@np.linalg.pinv(loadings.T@loadings, rcond=1e-15)
    z = (data.observed-analysis["mean"])/analysis["scale"]
    np.testing.assert_allclose(analysis["scores"], z@weights, atol=2e-14, rtol=2e-14)
    np.testing.assert_allclose(analysis["rotation"].T@analysis["rotation"], np.eye(2), atol=2e-14)
    models = quadratic_responses_from_coefficients(data.model.coefficients[:, :2], 3)
    targets, variance, point = np.array([-.1, .2]), np.array([1., 2.]), np.array([.1, -.2, .3])
    raw = vrf_values(models, targets, variance, point)
    assert np.all(raw >= variance)
    jac = vrf_jacobian(models, targets, point)
    for j in range(3):
        h = np.eye(3)[j]*1e-6
        numerical = (vrf_values(models, targets, variance, point+h)
                     -vrf_values(models, targets, variance, point-h))/(2e-6)
        np.testing.assert_allclose(jac[:, j], numerical, atol=2e-8, rtol=2e-8)
    assert factor_count(np.array([.95, .98, 1.])) == 2
    assert factor_count(np.array([.4, .7, .85, .96, 1.])) == 4
    for invalid in (np.array([1.]), np.array([.9, .8]), np.array([.4, .5])):
        with pytest.raises(ValueError):
            factor_count(invalid)


def test_archive_integrity_checkpoint_and_no_rerun(inputs, tmp_path):
    data = inputs["nx2_delta1_rho025__replica1"]
    x = np.zeros((2, 2))
    output = RunOutput(x, data.model.predict(x), "COMPLETED", dict(example=np.inf))
    output.validate(data)
    hashes = save_output(tmp_path, "case", output, dict(seed="17"))
    verify_payload(tmp_path, hashes)
    with pytest.raises(FileExistsError):
        save_output(tmp_path, "case", output, {})
    checkpoint = tmp_path/"checkpoint.json"
    identity = dict(method="C-NBI", scenario="case")
    record = begin_attempt(checkpoint, identity, "a")
    assert record["state"] == "RUNNING"
    with pytest.raises(ValueError):
        begin_attempt(checkpoint, identity, "a")
    record["state"] = "COMPLETED"
    write_json(checkpoint, record)
    assert begin_attempt(checkpoint, identity, "a") is None
    with pytest.raises(ValueError):
        begin_attempt(checkpoint, identity, "b")
    assert read_json(checkpoint)["state"] == "COMPLETED"
    assert json_value(np.array([np.nan])) == [{"nonfinite_diagnostic": "nan"}]
    assert json_value(np.int64(2)) == 2
    (tmp_path/next(iter(hashes))).write_bytes(b"corrupted")
    with pytest.raises(ValueError):
        verify_payload(tmp_path, hashes)
    assert len(file_hash(checkpoint)) == 64
    with pytest.raises(ValueError):
        recover_attempt(checkpoint, "")
    with pytest.raises(ValueError):
        recover_attempt(checkpoint, "cannot replace a completed result")
    record["state"] = "FAILED"
    record["payload_checksums"] = hashes
    write_json(checkpoint, record)
    with pytest.raises(ValueError, match="scientific outcome"):
        recover_attempt(checkpoint, "cannot replace unfavorable scientific outputs")
    del record["payload_checksums"]
    write_json(checkpoint, record)
    recover_attempt(checkpoint, "documented process interruption; preserve attempt1")
    assert read_json(checkpoint)["state"] == "PENDING"
    assert read_json(tmp_path/"attempt_history/checkpoint.attempt1.json")["state"] == "FAILED"
    recovered = begin_attempt(checkpoint, identity, "a")
    assert recovered["state"] == "RUNNING" and recovered["attempt"] == 2


def test_calibration_selection_and_dispatch_validation(inputs, tmp_path):
    cfg = tmp_path/"cfg.json"
    cfg.write_text(json.dumps({"NSGA-III_nx2_m4": {"status": "COMPLETED"}}))
    assert load_ea_configuration(cfg, "NSGA-III", 2, 4)["status"] == "COMPLETED"
    with pytest.raises(ValueError):
        load_ea_configuration(cfg, "C-NBI", 2, 4)
    data = inputs["nx2_delta1_rho025__replica1"]
    with pytest.raises(ValueError):
        run_method(data, "invalid", 1)
    with pytest.raises(ValueError):
        run_method(data, "NSGA-III", 1)
    np.testing.assert_allclose(data.model.predict(data.ccd),
                               quadratic_design(data.ccd)@data.model.coefficients, atol=0, rtol=0)
