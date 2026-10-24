"""End-to-end integrity of the original-coded Phase 3 archive, not PA results."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest
from scripts.validation import turning_anchors, turning_coefficient_mc
from scripts.validation.turning_reference import RAW, RAW_SHA256, RESPONSES, TERMS

from cnbi_v2.data import sha256_file
from cnbi_v2.model import coefficient_covariance, fit_multivariate_rsm


@pytest.fixture(scope="module")
def archive(tmp_path_factory):
    output = tmp_path_factory.mktemp("coefficient_mc")
    before = sha256_file(RAW), RAW.stat().st_mtime_ns
    # Count the only fit and ensemble; reject every optimizer exported by the
    # old workflow module. Loading its verified coded data needs none of them.
    with pytest.MonkeyPatch.context() as patch:
        counts = {"fit": 0, "ensemble": 0}
        original_fit = turning_coefficient_mc.fit_multivariate_rsm
        original_sampler = turning_coefficient_mc.sample_coefficient_ensemble

        def counted_fit(*args, **kwargs):
            counts["fit"] += 1
            return original_fit(*args, **kwargs)

        def counted_sampler(*args, **kwargs):
            counts["ensemble"] += 1
            assert args[3] == 2000
            return original_sampler(*args, **kwargs)

        def forbidden(*args, **kwargs):
            pytest.fail("Phase 3 attempted an anchor optimization or payoff")

        patch.setattr(turning_coefficient_mc, "fit_multivariate_rsm", counted_fit)
        patch.setattr(turning_coefficient_mc, "sample_coefficient_ensemble", counted_sampler)
        for name in ["run_anchors", "solve_quadratic_ball", "solve_response_region_anchor",
                     "payoff_matrix"]:
            patch.setattr(turning_anchors, name, forbidden)
        summary = turning_coefficient_mc.run_coefficient_mc(output, run_id="test_mc")
        assert counts == {"fit": 1, "ensemble": 1}
    assert (sha256_file(RAW), RAW.stat().st_mtime_ns) == before
    return output, summary


def test_real_archive_shape_order_moments_and_hashes(archive):
    output, summary = archive
    metadata = json.loads((output / "metadata.json").read_text())
    with np.load(output / "coefficient_samples.npz", allow_pickle=False) as stored:
        assert stored.files == ["samples"]
        samples = stored["samples"]
    assert samples.shape == (2000, 10, 8)
    assert samples.dtype == np.float64
    assert np.isfinite(samples).all()
    assert metadata["normal_count"] == 160000
    assert metadata["dataset_sha256"] == RAW_SHA256
    assert metadata["coefficient_order"] == list(TERMS)
    assert metadata["response_order"] == list(RESPONSES)
    assert metadata["factor_order"] == ["Vc", "f", "ap"]
    assert metadata["residual_degrees_of_freedom"] == 9
    assert metadata["factorization_method"]["residual"] == "CHOLESKY_SPD"
    assert metadata["zeroed_negative_eigenvalues"] == 0
    assert metadata["anchors_reoptimized"] is False
    assert metadata["per_replica_payoff_computed"] is False
    assert metadata["observed_responses_modified"] is False
    values, factors, _ = turning_anchors.load_original_coded_case()
    fit = fit_multivariate_rsm(factors, values[:, 4:])
    for name, matrix in [("B_hat", fit.coefficients), ("V_X", fit.xtx_covariance_factor),
                         ("Sigma_hat_e", fit.residual_covariance)]:
        assert metadata["object_identities"][name] == turning_coefficient_mc.array_identity(matrix)
    theoretical = np.load(output / "theoretical_covariance.npy", allow_pickle=False)
    np.testing.assert_array_equal(theoretical, coefficient_covariance(fit))
    np.testing.assert_allclose(np.diag(theoretical)[:10],
                               fit.mse_by_response[0] * np.diag(fit.xtx_covariance_factor))
    assert np.count_nonzero(theoretical[:10, 10:20]) > 0
    vectors = np.stack([sample.reshape(-1, order="F") for sample in samples])
    empirical = np.load(output / "empirical_covariance_B2000.npy", allow_pickle=False)
    np.testing.assert_allclose(empirical, np.cov(vectors, rowvar=False), atol=1e-14)
    np.testing.assert_allclose(summary["mean"], samples.mean(axis=0))
    with (output / "mc_prefix_sensitivity.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert list(rows[0]) == ["B", "mean_relative_frobenius_error",
                             "covariance_relative_frobenius_error"]
    assert [int(row["B"]) for row in rows] == list(range(100, 2001, 100))
    for row in rows:
        n = int(row["B"])
        expected_mean = np.linalg.norm(samples[:n].mean(axis=0) - fit.coefficients)
        expected_mean /= np.linalg.norm(fit.coefficients)
        expected_cov = np.linalg.norm(np.cov(vectors[:n], rowvar=False) - theoretical)
        expected_cov /= np.linalg.norm(theoretical)
        assert float(row["mean_relative_frobenius_error"]) == pytest.approx(expected_mean)
        assert float(row["covariance_relative_frobenius_error"]) == pytest.approx(expected_cov)
    for filename, digest in metadata["artifact_sha256"].items():
        assert sha256_file(output / filename) == digest
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, filename = line.split("  ")
        assert sha256_file(output / filename) == digest
    assert (output / "mc_convergence.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    with pytest.raises(FileExistsError):
        turning_coefficient_mc.run_coefficient_mc(output, run_id="test_mc")


def test_future_policy_is_recorded_but_not_applied(archive):
    output, _ = archive
    metadata = json.loads((output / "metadata.json").read_text())
    policy = metadata["early_stop_policy"]
    assert metadata["early_stop_applied"] is False
    assert metadata["early_stop_status"] == "NOT_APPLIED_PHASE_3"
    assert metadata["mode"] == "validation/sensitivity"
    assert policy["status"] == "PROPOSED"
    assert policy["minimum_eligible_B"] == 500
    assert policy["epsilon_q"] == np.finfo(float).tiny
    assert policy["quantile_relative_tolerance"] == .01
    assert policy["not_reached_status"] == "EARLY_STOP_NOT_REACHED"


def test_invalid_run_id_before_writing(tmp_path: Path):
    with pytest.raises(ValueError, match="run_id"):
        turning_coefficient_mc.run_coefficient_mc(tmp_path, run_id="../escape")
