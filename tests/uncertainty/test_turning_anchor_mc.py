"""Pinned real evidence, 2000-replica nominal control and complete archive integrity."""

import csv
import json
from dataclasses import replace

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation import turning_anchor_mc as workflow
from scripts.validation.turning_anchors import ALPHA, DIRECTIONS
from scripts.validation.turning_reference import RESPONSES, ROOT

from cnbi_v2.data import sha256_file
from cnbi_v2.uncertainty import AnchorEnsemble, AnchorFailure, reoptimize_coefficient_ensemble


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_exact_nominal_ensemble_control_2000_by_eight_fresh_solves(monkeypatch):
    import cnbi_v2.uncertainty.anchor_reoptimization as module
    coefficients = np.loadtxt(workflow.NOMINAL.parent / "coded_models.csv",
                              delimiter=",", skiprows=1, usecols=range(1, 9))
    nominal, optimum = workflow.load_nominal_anchors()
    payoff = np.loadtxt(workflow.NOMINAL.parent / "payoff_sphere.csv",
                        delimiter=",", skiprows=1, usecols=range(1, 9))
    before = coefficients.copy(), nominal.copy(), optimum.copy()
    calls = 0
    original = module.solve_quadratic_ball
    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)
    monkeypatch.setattr(module, "solve_quadratic_ball", counted)
    result = reoptimize_coefficient_ensemble(np.broadcast_to(coefficients, (2000, 10, 8)),
                                            3, DIRECTIONS, ALPHA, response_names=RESPONSES)
    assert calls == 16000
    assert result.successful == 16000 and result.failed == 0 and not result.failures
    for matrix in [result.anchors, result.optimal_values, result.payoffs]:
        assert_array_equal(matrix, np.broadcast_to(matrix[0], matrix.shape))
    assert_allclose(result.anchors, np.broadcast_to(nominal, result.anchors.shape), atol=1e-12)
    assert_allclose(result.optimal_values, np.broadcast_to(optimum, (2000, 8)), atol=1e-13)
    assert_allclose(result.payoffs, np.broadcast_to(payoff, (2000, 8, 8)), atol=1e-13)
    assert_array_equal(coefficients, before[0])
    assert_array_equal(nominal, before[1])
    assert_array_equal(optimum, before[2])


@pytest.fixture(scope="module")
def real_archive(tmp_path_factory):
    output = tmp_path_factory.mktemp("anchor_mc")
    input_paths = [workflow.ENSEMBLE, workflow.METADATA, workflow.NOMINAL, workflow.RAW]
    before = [(sha256_file(p), p.stat().st_mtime_ns) for p in input_paths]
    with pytest.MonkeyPatch.context() as patch:
        import cnbi_v2.model as model
        import cnbi_v2.optimization as optimization
        import cnbi_v2.uncertainty as uncertainty
        import cnbi_v2.uncertainty.coefficient_sampling as sampling
        def forbidden(*args, **kwargs):
            pytest.fail("new draws, OLS or response-region optimization attempted")
        patch.setattr(uncertainty, "sample_coefficient_ensemble", forbidden)
        patch.setattr(sampling, "sample_coefficient_ensemble", forbidden)
        patch.setattr(sampling, "iter_coefficient_batches", forbidden)
        patch.setattr(model, "fit_multivariate_rsm", forbidden)
        patch.setattr(optimization, "solve_response_region_anchor", forbidden)
        patch.setattr(np.random, "Generator", forbidden)
        metadata = workflow.run_anchor_mc(output, run_id="integration_anchor_mc")
    assert before == [(sha256_file(p), p.stat().st_mtime_ns) for p in input_paths]
    return output, metadata


def test_real_archive_counts_shapes_finite_values_diagonal_and_checksums(real_archive):
    output, metadata = real_archive
    assert metadata["status"] == "SUCCESS"
    assert metadata["attempted"] == metadata["successful"] == 16000
    assert metadata["failed"] == 0 and metadata["payoff_successful"] == 2000
    assert metadata["phase_3_ensemble_sha256"] == workflow.ENSEMBLE_SHA
    assert metadata["phase_3_scientific_commit"] == workflow.PHASE_3_SOURCE_COMMIT
    assert metadata["new_random_draws"] == 0 and metadata["RC_applied"] is False
    assert metadata["nominal_anchors_used_as_substitutes"] is False
    assert metadata["early_stop_applied"] is False and metadata["payoffs_normalized"] is False
    assert metadata["diagonal_identity"] is True
    assert metadata["mean_seconds_per_optimization"] > 0
    with np.load(output / "anchor_samples.npz", allow_pickle=False) as stored:
        for name in stored.files:
            assert stored[name].dtype != object
        anchors, values, norms = stored["anchors"], stored["optimal_values"], stored["norms"]
        certificates = stored["certificates"]
        assert stored["solver_cases"].shape == (2000, 8)
        assert stored["solver_cases"].dtype.kind == "U"
        assert stored["valid_anchors"].all()
        assert_allclose(norms, np.linalg.norm(anchors, axis=2), atol=1e-14)
    with np.load(output / "payoff_samples.npz", allow_pickle=False) as stored:
        payoffs = stored["payoffs"]
        assert stored["valid_payoffs"].all()
    assert anchors.shape == (2000, 8, 3) and payoffs.shape == (2000, 8, 8)
    assert np.isfinite(anchors).all() and np.isfinite(values).all() and np.isfinite(payoffs).all()
    assert_array_equal(np.diagonal(payoffs, axis1=1, axis2=2), values)
    assert np.all(norms <= ALPHA * np.sqrt(1+1e-10))
    assert np.all(certificates[:, :, :2] <= 1e-10)
    assert np.all(certificates[:, :, 2] >= -np.finfo(float).eps*48)
    assert read_rows(output / "failure_log.csv") == []
    assert len(read_rows(output / "solver_case_summary.csv")) == 8
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(output / name) == digest
    for name, digest in metadata["artifact_sha256"].items():
        assert sha256_file(output / name) == digest
    for path, digest in metadata["input_sha256"].items():
        assert sha256_file(ROOT / path) == digest
    with pytest.raises(FileExistsError):
        workflow.run_anchor_mc(output, run_id="duplicate_run")


def test_real_summaries_and_all_prefixes_recomputed_independently(real_archive):
    output, _ = real_archive
    nominal, nominal_values = workflow.load_nominal_anchors()
    with np.load(output / "anchor_samples.npz", allow_pickle=False) as stored:
        anchors, values = stored["anchors"], stored["optimal_values"]
        location = stored["locations"]
        assert_array_equal(stored["optimal_value_differences"], values - nominal_values)
    with np.load(output / "payoff_samples.npz", allow_pickle=False) as stored:
        payoffs = stored["payoffs"]
    delta = np.linalg.norm(anchors - nominal[None], axis=2)
    rows = read_rows(output / "anchor_summary.csv")
    optimum = read_rows(output / "optimal_value_summary.csv")
    for j, row in enumerate(rows):
        assert row["response"] == RESPONSES[j]
        assert float(row["median_delta_x"]) == pytest.approx(np.median(delta[:, j]))
        assert float(row["q95_delta_x"]) == pytest.approx(np.quantile(delta[:, j], .95))
        assert float(row["std_delta_x"]) == pytest.approx(np.std(delta[:, j], ddof=1))
        assert float(row["fraction_boundary"]) == np.mean(location[:, j] == "BOUNDARY")
        assert float(optimum[j]["mean_sampled_optimum"]) == pytest.approx(values[:, j].mean())
        assert float(optimum[j]["mean_delta_f"]) == pytest.approx(
            (values[:, j] - nominal_values[j]).mean())
    prefix = read_rows(output / "prefix_anchor_sensitivity.csv")
    assert len(prefix) == 160
    assert sorted({int(row["B"]) for row in prefix}) == list(range(100, 2001, 100))
    for row in prefix:
        n, j = int(row["B"]), RESPONSES.index(row["response"])
        assert float(row["mean_displacement"]) == pytest.approx(delta[:n, j].mean())
        assert float(row["q95_displacement"]) == pytest.approx(np.quantile(delta[:n, j], .95))
        assert float(row["fraction_boundary"]) == np.mean(location[:n, j] == "BOUNDARY")
    payoff_rows = read_rows(output / "prefix_payoff_sensitivity.csv")
    assert len(payoff_rows) == 20
    target = payoffs.mean(axis=0)
    for row in payoff_rows:
        n = int(row["B"])
        expected = np.linalg.norm(payoffs[:n].mean(axis=0) - target) / np.linalg.norm(target)
        assert float(row["mean_payoff_relative_frobenius_error"]) == pytest.approx(expected)
    assert float(payoff_rows[-1]["mean_payoff_relative_frobenius_error"]) == 0


def test_pinned_ensemble_rejects_file_or_metadata_hash_mismatch(tmp_path):
    bad = tmp_path / "bad.npz"
    bad.write_bytes(b"different")
    with pytest.raises(ValueError, match="ensemble SHA"):
        workflow.load_phase3_ensemble(bad)
    with pytest.raises(ValueError, match="metadata SHA"):
        workflow.load_phase3_ensemble(metadata_path=bad)


@pytest.mark.parametrize("key,value", [("seed", 5), ("git_commit", "wrong"),
                                       ("coefficient_order", []), ("response_order", [])])
def test_semantic_metadata_gate_even_if_file_hash_is_reapproved(tmp_path, monkeypatch, key, value):
    metadata = json.loads(workflow.METADATA.read_text())
    metadata[key] = value
    path = tmp_path / "metadata.json"
    path.write_text(json.dumps(metadata))
    monkeypatch.setattr(workflow, "METADATA_SHA", sha256_file(path))
    with pytest.raises(ValueError, match="configuration"):
        workflow.load_phase3_ensemble(metadata_path=path)


@pytest.mark.parametrize("kind", ["keys", "shape", "dtype", "nonfinite", "array_hash"])
def test_semantic_array_gate_even_if_file_hash_is_reapproved(tmp_path, monkeypatch, kind):
    samples, _ = workflow.load_phase3_ensemble()
    path = tmp_path / "bad.npz"
    if kind == "keys":
        np.savez_compressed(path, wrong=samples)
    else:
        altered = (samples[:1] if kind == "shape" else samples.astype(np.float32)
                   if kind == "dtype" else samples.copy())
        if kind == "nonfinite":
            altered[0, 0, 0] = np.nan
        if kind == "array_hash":
            altered[0, 0, 0] += 1
        np.savez_compressed(path, samples=altered)
    monkeypatch.setattr(workflow, "ENSEMBLE_SHA", sha256_file(path))
    with pytest.raises(ValueError):
        workflow.load_phase3_ensemble(path)


def test_incomplete_summaries_refused_and_invalid_run_id(tmp_path):
    result = reoptimize_coefficient_ensemble([[[1.], [1.], [1.]]], 1, DIRECTIONS[:1], 1)
    with pytest.raises(ValueError, match="B=2000"):
        workflow.build_summaries(result, np.zeros((1, 1)), np.zeros(1))
    failed = replace(result, valid_anchors=np.zeros((1, 1), dtype=bool))
    with pytest.raises(ValueError, match="incomplete"):
        workflow.build_summaries(failed, np.zeros((1, 1)), np.zeros(1))
    with pytest.raises(ValueError, match="run_id"):
        workflow.run_anchor_mc(tmp_path, run_id="../invalid")


def test_fixed_anchor_does_not_propagate_location_counterexample():
    # f_theta(x)=-(x-theta)^2, |theta|<1: x*=theta, whereas fixed anchor stays zero.
    theta = np.array([-.5, 0, .25])
    samples = np.stack([-theta**2, 2*theta, -np.ones(3)], axis=1)[:, :, None]
    result = reoptimize_coefficient_ensemble(samples, 1, DIRECTIONS[:1], 1)
    assert_allclose(result.anchors[:, 0, 0], theta, atol=1e-15)
    assert_allclose(result.optimal_values[:, 0], 0, atol=1e-15)
    assert np.any(-theta**2 < result.optimal_values[:, 0])
    assert len(set(result.anchors[:, 0, 0])) > 1


def test_incomplete_archive_keeps_failure_log_indices_and_refuses_distribution_summaries(
    real_archive, tmp_path, monkeypatch,
):
    output, _ = real_archive
    with np.load(output / "anchor_samples.npz", allow_pickle=False) as stored:
        arrays = {name: stored[name].copy() for name in
                  ["anchors", "optimal_values", "norms", "solver_cases", "locations",
                   "valid_anchors", "certificates"]}
        fields = tuple(stored["certificate_fields"])
    with np.load(output / "payoff_samples.npz", allow_pickle=False) as stored:
        payoffs, valid_payoffs = stored["payoffs"].copy(), stored["valid_payoffs"].copy()
    for name in ["anchors", "optimal_values", "norms", "certificates"]:
        arrays[name][16, 3] = np.nan
    arrays["solver_cases"][16, 3] = "FAILED"
    arrays["locations"][16, 3] = "FAILED"
    arrays["valid_anchors"][16, 3] = False
    payoffs[16] = np.nan
    valid_payoffs[16] = False
    failed = AnchorEnsemble(**arrays, payoffs=payoffs, valid_payoffs=valid_payoffs,
                            certificate_fields=fields, response_names=RESPONSES,
                            directions=DIRECTIONS, radius=ALPHA,
                            failures=(AnchorFailure(17, "Ra", "SOLVER_EXCEPTION", "test failure"),))
    monkeypatch.setattr(workflow, "reoptimize_coefficient_ensemble", lambda *a, **k: failed)
    metadata = workflow.run_anchor_mc(tmp_path, run_id="incomplete_case")
    assert metadata["status"] == "INCOMPLETE_FAILURE_NO_DISTRIBUTION_SUMMARIES"
    assert metadata["successful"] == 15999 and metadata["failed"] == 1
    assert metadata["payoff_successful"] == 1999
    assert read_rows(tmp_path / "failure_log.csv") == [{
        "replicate_id": "17", "response": "Ra", "failure_type": "SOLVER_EXCEPTION",
        "failure_message": "test failure"}]
    assert read_rows(tmp_path / "anchor_summary.csv") == []
    assert read_rows(tmp_path / "optimal_value_summary.csv") == []
    assert read_rows(tmp_path / "prefix_payoff_sensitivity.csv") == []
    solver = read_rows(tmp_path / "solver_case_summary.csv")
    assert solver[3]["failure_count"] == "1"


def test_incomplete_cli_exit_is_nonzero(monkeypatch, tmp_path):
    import sys
    monkeypatch.setattr(sys, "argv", ["turning_anchor_mc", "--output", str(tmp_path)])
    metadata = dict(status="INCOMPLETE_FAILURE_NO_DISTRIBUTION_SUMMARIES", attempted=16000,
                    successful=15999, failed=1, compute_seconds=1, elapsed_total_seconds=2)
    monkeypatch.setattr(workflow, "run_anchor_mc", lambda *a, **k: metadata)
    with pytest.raises(SystemExit) as error:
        workflow.main()
    assert error.value.code == 1
