from dataclasses import FrozenInstanceError, fields

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.model import RSMFit, fit_multivariate_rsm, quadratic_design
from cnbi_v2.model.multivariate_rsm import _check_symmetric_psd


@pytest.mark.parametrize("n_responses", [1, 3, 8])
def test_exact_synthetic_coefficient_recovery(ccd_factors, n_responses):
    design = quadratic_design(ccd_factors)
    coefficients = np.arange(10 * n_responses).reshape(10, n_responses) / 10 - 2
    responses = design @ coefficients
    result = fit_multivariate_rsm(ccd_factors, responses)
    assert_allclose(result.coefficients, coefficients, rtol=1e-13, atol=3e-14)
    assert_allclose(result.fitted_values, responses, rtol=1e-13, atol=1e-13)
    assert_allclose(result.residuals, 0, rtol=0, atol=1e-13)
    assert_allclose(result.residual_covariance, 0, rtol=0, atol=1e-25)
    assert result.rank == result.n_terms == 10
    assert result.residual_degrees_of_freedom == 9
    assert (result.n_observations, result.n_factors, result.n_responses) == (19, 3, n_responses)
    assert result.rank_relative_tolerance == np.finfo(float).eps * 19
    assert np.isfinite(result.design_condition_number)


def test_hand_derived_residuals_mse_and_vx(hand_case):
    factors, coefficients, residuals, residual_covariance, vx, responses = hand_case
    result = fit_multivariate_rsm(factors, responses)
    assert result.residual_degrees_of_freedom == 2
    assert_allclose(result.coefficients, coefficients, rtol=1e-13, atol=2e-14)
    assert_allclose(result.residuals, residuals, rtol=1e-13, atol=2e-14)
    assert_allclose(result.residual_covariance, residual_covariance, rtol=1e-14)
    assert_allclose(result.mse_by_response, [35, 145], rtol=1e-14)
    assert_allclose(result.xtx_covariance_factor, vx, rtol=1e-13, atol=2e-16)


def test_multivariate_matches_separate_univariate_ols(correlated_case):
    factors, responses, multi = correlated_case
    design = quadratic_design(factors)
    for j in range(responses.shape[1]):
        single = fit_multivariate_rsm(factors, responses[:, j])
        independent = np.linalg.lstsq(design, responses[:, j], rcond=None)[0]
        assert_allclose(single.coefficients[:, 0], independent, rtol=1e-13, atol=5e-15)
        assert_allclose(multi.coefficients[:, j], single.coefficients[:, 0], rtol=1e-13, atol=5e-15)
        assert_allclose(
            multi.fitted_values[:, j], single.fitted_values[:, 0], rtol=1e-13, atol=1e-14
        )
        assert_allclose(multi.residuals[:, j], single.residuals[:, 0], rtol=1e-13, atol=1e-14)
        assert_allclose(multi.mse_by_response[j], single.mse_by_response[0], rtol=1e-14)
        assert single.coefficients.shape == (10, 1)
        assert single.residual_covariance.shape == (1, 1)


def test_correlated_error_algebra_and_psd(correlated_case):
    factors, responses, result = correlated_case
    design = quadratic_design(factors)
    residuals = responses - design @ result.coefficients
    assert_array_equal(result.residuals, residuals)
    assert_allclose(result.residual_covariance, residuals.T @ residuals / 9, rtol=1e-15)
    assert_array_equal(np.diag(result.residual_covariance), result.mse_by_response)
    for j in range(result.n_responses):
        assert_allclose(
            result.mse_by_response[j], residuals[:, j] @ residuals[:, j] / 9, rtol=1e-14
        )
    assert_allclose(design.T @ residuals, 0, rtol=0, atol=2e-13)
    assert abs(result.residual_covariance[0, 1]) > 0.01
    for matrix in [result.residual_covariance, result.xtx_covariance_factor]:
        assert_allclose(matrix, matrix.T, rtol=0, atol=1e-15)
        assert np.linalg.eigvalsh(matrix)[0] >= -1e-15
    assert_allclose(
        (design.T @ design) @ result.xtx_covariance_factor, np.eye(10), rtol=1e-13, atol=2e-14
    )
    assert not np.allclose(result.residual_covariance, np.cov(responses, rowvar=False))


def test_response_permutation(correlated_case):
    factors, responses, original = correlated_case
    order = [2, 0, 1]
    permuted = fit_multivariate_rsm(factors, responses[:, order])
    for name in ["coefficients", "fitted_values", "residuals"]:
        assert_allclose(
            getattr(permuted, name), getattr(original, name)[:, order], rtol=1e-13, atol=2e-14
        )
    assert_allclose(
        permuted.mse_by_response, original.mse_by_response[order], rtol=1e-13, atol=1e-14
    )
    assert_allclose(
        permuted.residual_covariance,
        original.residual_covariance[np.ix_(order, order)],
        rtol=1e-13,
        atol=1e-14,
    )


def test_observation_permutation(correlated_case):
    factors, responses, original = correlated_case
    order = np.random.default_rng(42).permutation(len(factors))
    permuted = fit_multivariate_rsm(factors[order], responses[order])
    assert_allclose(permuted.coefficients, original.coefficients, rtol=1e-13, atol=2e-14)
    assert_allclose(permuted.fitted_values, original.fitted_values[order], rtol=1e-13, atol=3e-14)
    assert_allclose(permuted.residuals, original.residuals[order], rtol=1e-13, atol=3e-14)
    assert_allclose(
        permuted.residual_covariance, original.residual_covariance, rtol=1e-13, atol=1e-14
    )
    assert_allclose(
        permuted.xtx_covariance_factor, original.xtx_covariance_factor, rtol=1e-13, atol=2e-15
    )


def test_prediction_one_many_and_input_immutability(correlated_case):
    factors, responses, result = correlated_case
    original_x, original_y = factors.copy(), responses.copy()
    point = np.array([0.1, 0.3, -0.2])
    original_point = point.copy()
    points = np.array([point, -point, np.zeros(3)])
    original_points = points.copy()
    batch = result.predict(points)
    assert batch.shape == (3, 3)
    assert_allclose(batch, np.vstack([result.predict(p) for p in points]), rtol=1e-13, atol=1e-15)
    assert_allclose(result.predict(factors), result.fitted_values, rtol=1e-13, atol=1e-14)
    assert_allclose(
        result.predict(point),
        quadratic_design([point])[0] @ result.coefficients,
        rtol=1e-13,
        atol=1e-14,
    )
    assert_array_equal(point, original_point)
    assert_array_equal(points, original_points)
    assert_array_equal(factors, original_x)
    assert_array_equal(responses, original_y)


def test_fit_preserves_readonly_input_arrays(correlated_case):
    factors, responses, _ = correlated_case
    before_x, before_y = factors.copy(), responses.copy()
    factors.setflags(write=False)
    responses.setflags(write=False)
    result = fit_multivariate_rsm(factors, responses)
    assert_array_equal(factors, before_x)
    assert_array_equal(responses, before_y)
    for field in fields(result):
        array = getattr(result, field.name)
        if isinstance(array, np.ndarray):
            assert not np.shares_memory(array, factors)
            assert not np.shares_memory(array, responses)
            with pytest.raises(ValueError):
                array.flat[0] = 9
            with pytest.raises(ValueError):
                array.setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        result.rank = 0


def test_fit_does_not_depend_on_later_caller_mutation(correlated_case):
    factors, responses, result = correlated_case
    saved = result.coefficients.copy()
    factors[:] = 99
    responses[:] = -99
    assert_array_equal(result.coefficients, saved)


@pytest.mark.parametrize(
    "factors",
    [np.zeros((12, 2)), np.array([[0], [1]]), np.column_stack([np.arange(12), np.arange(12)])],
)
def test_rank_deficiency_fails(factors):
    with pytest.raises(ValueError, match="rank deficient"):
        fit_multivariate_rsm(factors, np.ones((len(factors), 2)))


def test_zero_residual_degrees_of_freedom_fails():
    with pytest.raises(ValueError, match="positive residual degrees"):
        fit_multivariate_rsm([[-1], [0], [1]], [1, 2, 3])


@pytest.mark.parametrize("responses", [np.ones(18), np.empty((19, 0)), np.ones((19, 1, 1)), 1])
def test_response_shape_validation(ccd_factors, responses):
    with pytest.raises(ValueError, match="responses must have shape"):
        fit_multivariate_rsm(ccd_factors, responses)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_response_rejected(ccd_factors, bad):
    responses = np.ones((19, 2))
    responses[3, 1] = bad
    with pytest.raises(ValueError, match="finite"):
        fit_multivariate_rsm(ccd_factors, responses)


def test_complex_response_rejected(ccd_factors):
    with pytest.raises(ValueError, match="real numeric"):
        fit_multivariate_rsm(ccd_factors, np.ones(19) + 1j)


@pytest.mark.parametrize(
    "points", [[], [1, 2], np.ones((2, 2)), np.ones((2, 3, 1)), [np.nan, 0, 1], [np.inf, 0, 1]]
)
def test_prediction_rejects_invalid_points(correlated_case, points):
    with pytest.raises(ValueError):
        correlated_case[2].predict(points)


def test_singular_residual_covariance_is_preserved(correlated_case):
    factors, responses, _ = correlated_case
    result = fit_multivariate_rsm(factors, np.column_stack([responses[:, 0]] * 2))
    assert_allclose(
        result.residual_covariance, np.full((2, 2), result.mse_by_response[0]), rtol=1e-14
    )
    assert abs(np.linalg.det(result.residual_covariance)) < 1e-14


@pytest.mark.parametrize(
    "matrix, message",
    [
        (np.array([[1.0, 0.2], [0, 1]]), "symmetric"),
        (np.diag([1.0, -0.01]), "positive semidefinite"),
    ],
)
def test_invalid_covariance_is_diagnosed_without_repair(matrix, message):
    original = matrix.copy()
    with pytest.raises(np.linalg.LinAlgError, match=message):
        _check_symmetric_psd(matrix, "test matrix")
    assert_array_equal(matrix, original)


def test_nonfinite_computed_covariance_fails():
    with pytest.raises(FloatingPointError, match="nonfinite computed"):
        _check_symmetric_psd(np.array([[np.inf]]), "test matrix")


def test_zero_response_has_exact_zero_residual_covariance(ccd_factors):
    result = fit_multivariate_rsm(ccd_factors, np.zeros((19, 2)))
    assert_array_equal(result.residual_covariance, np.zeros((2, 2)))
    assert_array_equal(result.mse_by_response, np.zeros(2))


def test_psd_diagnostic_handles_extreme_units_without_repair():
    # A direct row-sum norm would overflow although every matrix entry is finite.
    valid = np.array([[1.2e308, 1e308], [1e308, 1.2e308]])
    original = valid.copy()
    _check_symmetric_psd(valid, "large covariance")
    assert_array_equal(valid, original)
    with pytest.raises(np.linalg.LinAlgError, match="positive semidefinite"):
        _check_symmetric_psd(np.array([[1e308, 1.2e308], [1.2e308, 1e308]]), "large invalid")


def test_covariance_overflow_fails_explicitly(ccd_factors):
    huge_responses = np.arange(57, dtype=float).reshape(19, 3) * 1e200
    with pytest.raises(FloatingPointError, match="overflow"):
        fit_multivariate_rsm(ccd_factors, huge_responses)


def test_public_result_type(correlated_case):
    assert isinstance(correlated_case[2], RSMFit)
