"""Exact structural/RNG contracts and statistically scaled Monte Carlo oracles."""

from dataclasses import FrozenInstanceError, fields

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.uncertainty import (
    coefficient_checkpoints,
    iter_coefficient_batches,
    mc_prefix_sensitivity,
    sample_coefficient_ensemble,
)


def test_identity_case_is_exact_standard_normal_stream_and_orientation():
    expected = np.random.Generator(np.random.PCG64(777)).standard_normal(80 * 6).reshape(80, 2, 3)
    result = sample_coefficient_ensemble(np.zeros((2, 3)), np.eye(2), np.eye(3), 80)
    assert result.samples.tobytes() == expected.tobytes()
    assert result.samples.shape == (80, 2, 3)
    assert result.samples.dtype == np.float64
    assert result.coefficient_shape == (2, 3)
    assert result.seed == 777
    assert result.rng == "Generator(PCG64)"
    assert result.sampling_method == "MATRIX_NORMAL_PLUGIN"
    assert result.response_names == ("response_0", "response_1", "response_2")
    assert result.term_names == ("term_0", "term_1")


def test_manual_triangular_factor_covariance_and_matrix_normal_transform():
    mean = np.array([[3., -1.], [.2, .8]])
    r = np.array([[2., 1.], [0., 3.]])
    sigma = np.array([[4., 1.], [1., 2.]])
    result = sample_coefficient_ensemble(mean, r, sigma, 7, seed=42,
                                        response_names=["a", "b"], term_names=["c", "x"])
    cx = np.array([[.5, -1/6], [0, 1/3]])
    expected_vx = np.array([[5/18, -1/18], [-1/18, 1/9]])
    assert_allclose(result.design_covariance_factor, cx, rtol=1e-15)
    assert_allclose(cx @ cx.T, expected_vx, rtol=1e-15)
    assert_allclose(result.design_covariance, expected_vx, rtol=1e-15)
    assert_allclose(result.residual_covariance_factor @ result.residual_covariance_factor.T, sigma)
    assert_array_equal(result.residual_covariance, sigma)
    assert_array_equal(result.effective_residual_covariance, sigma)
    assert result.residual_factorization_method == "CHOLESKY_SPD"
    assert result.zeroed_negative_eigenvalues == 0
    normals = np.random.Generator(np.random.PCG64(42)).standard_normal(28).reshape(7, 2, 2)
    expected = np.array([mean + cx @ g @ np.linalg.cholesky(sigma).T for g in normals])
    assert_allclose(result.samples, expected, atol=1e-15)
    assert result.response_names == ("a", "b")
    assert result.term_names == ("c", "x")


@pytest.mark.parametrize("r,sigma", [
    (np.eye(2), np.eye(2)),
    (np.diag([1., .5]), np.diag([2., 3.])),
    (np.array([[1., .3], [0., 2.]]), np.array([[4., 1.2], [1.2, 1.]])),
])
def test_empirical_means_covariance_and_cross_response_blocks(r, sigma):
    # Gaussian unbiased sample covariance has Var(S_ij)=(K_ii*K_jj+K_ij²)/(N-1).
    # Six SE bounds on 4 coefficients/16 covariance entries are conservative,
    # fixed-seed sampling checks, not a scientific stopping criterion.
    n = 50_000  # Large ensembles occur only in synthetic tests.
    mean = np.array([[3., -1.], [.2, .8]])
    result = sample_coefficient_ensemble(mean, r, sigma, n, seed=20261024)
    cx = np.linalg.solve(r, np.eye(2))
    vx = cx @ cx.T
    target = np.kron(sigma, vx)
    vectors = np.stack([sample.reshape(-1, order="F") for sample in result.samples])
    empirical = np.cov(vectors, rowvar=False, ddof=1)
    mean_bound = 6 * np.sqrt(np.diag(target) / n)
    assert np.all(np.abs(vectors.mean(axis=0) - mean.reshape(-1, order="F")) < mean_bound)
    bound = 6 * np.sqrt((np.diag(target)[:, None] * np.diag(target)[None, :]
                         + target**2) / (n - 1))
    assert np.all(np.abs(empirical - target) < bound)
    for j in range(2):
        for k in range(2):
            left = result.samples[:, :, j] - result.samples[:, :, j].mean(axis=0)
            right = result.samples[:, :, k] - result.samples[:, :, k].mean(axis=0)
            block = left.T @ right / (n - 1)
            block_target = sigma[j, k] * vx
            assert np.all(np.abs(block - block_target) < bound[2*j:2*j+2, 2*k:2*k+2])


@pytest.mark.parametrize("size", [1, 3, 100, 333, 2000])
def test_chunking_reproduces_the_identical_full_sequence(size):
    args = (np.ones((3, 2)), [[1, .2, .3], [0, 2, .4], [0, 0, 3]], [[4, 1], [1, 2]], 2000)
    full = sample_coefficient_ensemble(*args, seed=777, batch_size=2000)
    parts = list(iter_coefficient_batches(*args, seed=777, batch_size=size))
    combined = np.concatenate(parts)
    assert full.samples.tobytes() == combined.tobytes()
    for part in parts:
        with pytest.raises(ValueError):
            part.setflags(write=True)


@pytest.mark.parametrize("prefix", [1, 17, 100, 500, 1900])
def test_prefix_reproducibility_is_bitwise(prefix):
    args = (np.ones((10, 8)), np.eye(10), np.eye(8))
    full = sample_coefficient_ensemble(*args, 2000, seed=777, batch_size=2000)
    short = sample_coefficient_ensemble(*args, prefix, seed=777, batch_size=37)
    assert full.samples[:prefix].tobytes() == short.samples.tobytes()


def test_same_seed_repeats_different_seed_changes_and_global_rng_is_untouched():
    before = np.random.get_state()
    args = (np.zeros((2, 3)), np.eye(2), np.eye(3), 100)
    a = sample_coefficient_ensemble(*args, seed=777)
    b = sample_coefficient_ensemble(*args, seed=777)
    other = sample_coefficient_ensemble(*args, seed=778)
    assert a.samples.tobytes() == b.samples.tobytes()
    assert a.samples.tobytes() != other.samples.tobytes()
    after = np.random.get_state()
    assert before[0] == after[0] and before[2:] == after[2:]
    assert_array_equal(before[1], after[1])


def test_singular_psd_and_roundoff_only_negative_eigenvalue_are_explicit():
    sigma = np.ones((2, 2))
    result = sample_coefficient_ensemble(np.zeros((2, 2)), np.eye(2), sigma, 100)
    assert result.residual_factorization_method == "SPECTRAL_PSD"
    assert_allclose(result.residual_covariance_factor @ result.residual_covariance_factor.T, sigma)
    assert_allclose(result.samples[:, :, 0], result.samples[:, :, 1], atol=1e-15)
    small_negative = np.diag([-np.finfo(float).eps / 2, 1.0])
    rounded = sample_coefficient_ensemble(np.zeros((1, 2)), [[1]], small_negative, 10)
    assert rounded.zeroed_negative_eigenvalues == 1
    assert 0 < rounded.psd_eigenvalue_tolerance < 1e-14
    assert_array_equal(rounded.residual_covariance, small_negative)
    assert_array_equal(rounded.effective_residual_covariance, np.diag([0., 1.]))
    assert_array_equal(rounded.samples[:, 0, 0], 0)


def test_zero_covariance_keeps_mean_and_relative_covariance_error_undefined():
    result = sample_coefficient_ensemble([[3., 4.]], [[1]], np.zeros((2, 2)), 2000)
    assert_array_equal(result.samples, np.tile([[[3., 4.]]], (2000, 1, 1)))
    diagnostics = mc_prefix_sensitivity(result)
    assert all(row.mean_relative_frobenius_error == 0 for row in diagnostics)
    assert all(row.covariance_relative_frobenius_error is None for row in diagnostics)
    assert all(row.covariance_status == "ZERO_THEORETICAL_COVARIANCE" for row in diagnostics)


def test_result_input_and_name_immutability():
    mean, upper, sigma = np.ones((2, 2)), np.eye(2), np.eye(2)
    names = ["a", "b"]
    before = [array.copy() for array in [mean, upper, sigma]]
    result = sample_coefficient_ensemble(mean, upper, sigma, 10, response_names=names)
    for actual, old in zip([mean, upper, sigma], before, strict=True):
        assert_array_equal(actual, old)
    mean[0, 0] = upper[0, 0] = sigma[0, 0] = 99
    names[0] = "changed"
    assert result.coefficient_mean[0, 0] == 1
    assert result.residual_covariance[0, 0] == 1
    assert result.response_names == ("a", "b")
    for field in fields(result):
        value = getattr(result, field.name)
        if isinstance(value, np.ndarray):
            assert np.isfinite(value).all()
            with pytest.raises(ValueError):
                value.setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        result.seed = 1


@pytest.mark.parametrize("parameter,value", [("n_samples", 0), ("n_samples", -1),
    ("n_samples", True), ("n_samples", 2.5), ("seed", -1), ("seed", 1.5),
    ("seed", True), ("seed", "777"), ("batch_size", 0), ("batch_size", np.nan)])
def test_B_seed_and_chunk_validation(parameter, value):
    options = {"n_samples": 10, "seed": 777, "batch_size": 100, parameter: value}
    for sampler in [sample_coefficient_ensemble, iter_coefficient_batches]:
        with pytest.raises(ValueError):
            sampler(np.ones((1, 1)), [[1]], [[1]], **options)


@pytest.mark.parametrize("mean,r,sigma", [
    ([1, 2], np.eye(2), np.eye(2)), (np.empty((0, 2)), [], np.eye(2)),
    ([[1]], [[1, 0]], [[1]]), (np.ones((2, 1)), [[1, 0], [1, 1]], [[1]]),
    ([[1]], [[1]], [[1, 0], [0, 1]]), ([[1]], [[np.inf]], [[1]]),
    ([[np.nan]], [[1]], [[1]]), ([[True]], [[1]], [[1]]),
])
def test_invalid_sampling_matrices_fail(mean, r, sigma):
    with pytest.raises(ValueError):
        sample_coefficient_ensemble(mean, r, sigma, 10)


def test_indefinite_asymmetric_and_singular_R_fail_without_regularization():
    with pytest.raises(np.linalg.LinAlgError, match="negative eigenvalue"):
        sample_coefficient_ensemble(np.ones((1, 2)), [[1]], [[1, 2], [2, 1]], 10)
    with pytest.raises(ValueError, match="exactly symmetric"):
        sample_coefficient_ensemble(np.ones((1, 2)), [[1]], [[1, .2], [.1, 1]], 10)
    with pytest.raises(np.linalg.LinAlgError):
        sample_coefficient_ensemble([[1]], [[0]], [[1]], 10)


@pytest.mark.parametrize("names", [[], ["a"], ["a", "a"], ["", "b"], [1, "b"]])
def test_term_and_response_name_validation(names):
    with pytest.raises(ValueError):
        sample_coefficient_ensemble(np.ones((2, 2)), np.eye(2), np.eye(2), 10,
                                    response_names=names)
    with pytest.raises(ValueError):
        sample_coefficient_ensemble(np.ones((2, 2)), np.eye(2), np.eye(2), 10,
                                    term_names=names)


def test_checkpoint_schedule_and_manual_prefix_moment_definitions():
    assert coefficient_checkpoints() == tuple(range(100, 2001, 100))
    assert len(coefficient_checkpoints()) == 20
    result = sample_coefficient_ensemble([[2, 3], [1, 4]], [[1, .5], [0, 2]],
                                        [[4, 1], [1, 1]], 2000)
    k = np.kron(result.residual_covariance, result.design_covariance)
    records = mc_prefix_sensitivity(result, theoretical_covariance=k)
    assert len(records) == 20
    for n, row in zip(coefficient_checkpoints(), records, strict=True):
        prefix = result.samples[:n]
        vectors = np.stack([sample.reshape(-1, order="F") for sample in prefix])
        expected_mean = np.linalg.norm(prefix.mean(axis=0) - result.coefficient_mean)
        expected_mean /= np.linalg.norm(result.coefficient_mean)
        expected_cov = np.linalg.norm(np.cov(vectors, rowvar=False, ddof=1) - k)
        expected_cov /= np.linalg.norm(k)
        assert row.B == n
        assert_allclose(row.mean_relative_frobenius_error, expected_mean, rtol=1e-14)
        assert_allclose(row.covariance_relative_frobenius_error, expected_cov, rtol=1e-14)
        assert row.covariance_status == "OK"


@pytest.mark.parametrize("checkpoints", [[], [100, 100], [200, 100], [1], [2001], [True]])
def test_invalid_checkpoint_lists(checkpoints):
    result = sample_coefficient_ensemble([[1]], [[1]], [[1]], 2000)
    with pytest.raises(ValueError):
        mc_prefix_sensitivity(result, checkpoints=checkpoints)


def test_invalid_sensitivity_target_and_numeric_floor():
    result = sample_coefficient_ensemble([[1]], [[1]], [[1]], 2000)
    with pytest.raises(ValueError, match="dimension"):
        mc_prefix_sensitivity(result, theoretical_covariance=np.eye(2))
    for floor in [0, -1, np.inf, np.nan]:
        with pytest.raises(ValueError, match="mean_norm_floor"):
            mc_prefix_sensitivity(result, mean_norm_floor=floor)


def test_finite_output_guards_and_arithmetic_overflow(monkeypatch):
    import cnbi_v2.uncertainty.coefficient_sampling as module
    with pytest.raises(FloatingPointError):
        sample_coefficient_ensemble([[1.7e308]], [[1e-308]], [[1]], 10)
    with monkeypatch.context() as patch:
        patch.setattr(module, "solve_triangular", lambda *a, **k: np.array([[np.nan]]))
        with pytest.raises(FloatingPointError, match="sampling factor"):
            sample_coefficient_ensemble([[1]], [[1]], [[1]], 10)
    class NonfiniteRNG:
        def standard_normal(self, count, **kwargs):
            return np.full(count, np.nan)
    monkeypatch.setattr(module.np.random, "Generator", lambda *args: NonfiniteRNG())
    with pytest.raises(FloatingPointError, match="nonfinite coefficient sample"):
        sample_coefficient_ensemble([[1]], [[1]], [[1]], 10)


def test_sensitivity_rejects_nonfinite_computed_metrics(monkeypatch):
    import cnbi_v2.uncertainty.mc_sensitivity as module
    result = sample_coefficient_ensemble([[1]], [[1]], [[1]], 2000)
    monkeypatch.setattr(module.np.linalg, "norm", lambda *a, **k: float("nan"))
    with pytest.raises(FloatingPointError, match="nonfinite computed"):
        mc_prefix_sensitivity(result)
