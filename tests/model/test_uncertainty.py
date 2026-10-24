import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.model import (
    coefficient_covariance,
    coefficient_covariance_by_response,
    cross_prediction_covariance,
    cross_prediction_leverage,
    difference_prediction_covariance,
    difference_prediction_leverage,
    fit_multivariate_rsm,
    mean_prediction_covariance,
    mean_prediction_variance,
    prediction_leverage,
    quadratic_design,
)


def test_coefficient_covariance_blocks_and_column_vectorization(hand_case):
    factors, _, _, residual_covariance, vx, responses = hand_case
    result = fit_multivariate_rsm(factors, responses)
    estimated = coefficient_covariance(result)
    assert estimated.shape == (6, 6)
    # Check every term/response pair, not merely a duplicated call to np.kron.
    for j in range(2):
        assert_allclose(
            coefficient_covariance_by_response(result, j),
            residual_covariance[j, j] * vx,
            rtol=1e-13,
            atol=1e-14,
        )
        for k in range(2):
            for i in range(3):
                for ell in range(3):
                    assert_allclose(
                        estimated[j * 3 + i, k * 3 + ell],
                        residual_covariance[j, k] * vx[i, ell],
                        rtol=1e-13,
                        atol=1e-14,
                    )
    b = result.coefficients
    assert_array_equal(b.reshape(-1, order="F"), np.concatenate([b[:, 0], b[:, 1]]))
    # The preprint uses vec(B.T); its covariance is a permutation of our result.
    row_order = np.arange(6).reshape(3, 2, order="F").reshape(-1)
    assert_allclose(
        estimated[np.ix_(row_order, row_order)],
        np.kron(vx, residual_covariance),
        rtol=1e-13,
        atol=1e-14,
    )
    assert_allclose(estimated, estimated.T, rtol=1e-14, atol=1e-14)
    assert np.linalg.eigvalsh(estimated)[0] >= -1e-13


def test_matrix_normal_covariance_from_observation_linear_map(hand_case):
    factors, _, _, sigma, vx, responses = hand_case
    result = fit_multivariate_rsm(factors, responses)
    # vec(B_hat-B)=(I_m tensor A)vec(E), A=V_X X.T.
    # The hand-derived V_X provides an independent exact-design oracle.
    design = quadratic_design(factors)
    observation_map = np.kron(np.eye(2), vx @ design.T)
    observation_covariance = np.kron(sigma, np.eye(5))
    propagated = observation_map @ observation_covariance @ observation_map.T
    assert_allclose(coefficient_covariance(result), propagated, rtol=1e-13, atol=2e-14)


def test_applied_dimensions_only_with_synthetic_eight_response_data(ccd_factors):
    design = quadratic_design(ccd_factors)
    responses = design @ np.arange(80).reshape(10, 8) / 10
    result = fit_multivariate_rsm(ccd_factors, responses)
    assert result.coefficients.shape == (10, 8)
    assert result.residual_covariance.shape == (8, 8)
    assert result.residual_degrees_of_freedom == 9
    assert coefficient_covariance(result).shape == (80, 80)


def test_leverage_hand_value_and_mean_uncertainty_without_observation_error(hand_case):
    factors, _, _, sigma, _, responses = hand_case
    result = fit_multivariate_rsm(factors, responses)
    center = [0.0]
    expected_h = 17 / 35
    assert_allclose(prediction_leverage(result, center), expected_h, rtol=1e-14)
    predicted_covariance = mean_prediction_covariance(result, center)
    assert_allclose(predicted_covariance, expected_h * sigma, rtol=1e-14)
    assert_array_equal(np.diag(predicted_covariance), mean_prediction_variance(result, center))
    assert not np.allclose(predicted_covariance, (1 + expected_h) * sigma)
    for j in range(2):
        single = fit_multivariate_rsm(factors, responses[:, j])
        assert_allclose(
            mean_prediction_variance(result, center)[j],
            mean_prediction_variance(single, center)[0],
            rtol=1e-14,
        )


def test_training_leverages_equal_hat_diagonal_and_sum_to_rank(correlated_case):
    factors, _, result = correlated_case
    q, _ = np.linalg.qr(quadratic_design(factors), mode="reduced")
    leverages = np.array([prediction_leverage(result, point) for point in factors])
    assert_allclose(leverages, np.sum(q * q, axis=1), rtol=1e-13, atol=1e-15)
    assert_allclose(leverages.sum(), result.rank, rtol=1e-14)
    assert np.all(leverages >= 0)
    assert np.all(leverages <= 1 + 1e-14)


def test_cross_covariance_via_coefficient_linear_maps(correlated_case):
    _, _, result = correlated_case
    point_a, point_b = np.array([0.4, 0.2, -0.8]), np.array([-0.2, 0.5, 0.1])
    z_a, z_b = quadratic_design([point_a, point_b])
    linear_a = np.kron(np.eye(3), z_a.reshape(1, -1))
    linear_b = np.kron(np.eye(3), z_b.reshape(1, -1))
    propagated = linear_a @ coefficient_covariance(result) @ linear_b.T
    assert_allclose(
        cross_prediction_covariance(result, point_a, point_b), propagated, rtol=1e-13, atol=1e-15
    )
    assert_allclose(
        cross_prediction_leverage(result, point_a, point_b),
        z_a @ result.xtx_covariance_factor @ z_b,
        rtol=1e-13,
    )
    assert_allclose(
        cross_prediction_covariance(result, point_b, point_a), propagated.T, rtol=1e-13, atol=1e-15
    )


def test_negative_cross_leverage_is_not_clipped(hand_case):
    factors, _, _, sigma, _, responses = hand_case
    result = fit_multivariate_rsm(factors, responses)
    # z(0)^T V_X z(2)=17/35-4/7=-3/35.
    assert_allclose(cross_prediction_leverage(result, [0], [2]), -3 / 35, rtol=1e-14)
    assert_allclose(cross_prediction_covariance(result, [0], [2]), -3 / 35 * sigma, rtol=1e-14)


def test_covariance_of_difference_includes_both_cross_terms(correlated_case):
    _, _, result = correlated_case
    a, b = [0.2, -0.3, 0.5], [-0.7, 0.4, -0.1]
    actual = difference_prediction_covariance(result, a, b)
    marginal_sum = mean_prediction_covariance(result, a) + mean_prediction_covariance(result, b)
    expanded = marginal_sum - cross_prediction_covariance(result, a, b)
    expanded -= cross_prediction_covariance(result, b, a)
    assert_allclose(actual, expanded, rtol=1e-13, atol=1e-15)
    assert not np.allclose(actual, marginal_sum, rtol=1e-3)
    c = quadratic_design([a])[0] - quadratic_design([b])[0]
    assert_allclose(
        difference_prediction_leverage(result, a, b),
        c @ result.xtx_covariance_factor @ c,
        rtol=1e-13,
    )
    assert_allclose(actual, difference_prediction_covariance(result, b, a), rtol=1e-14)
    assert_allclose(actual, actual.T, rtol=1e-14, atol=1e-15)
    assert np.linalg.eigvalsh(actual)[0] >= -1e-15
    delta_mean = result.predict(a) - result.predict(b)
    assert_allclose(delta_mean, -(result.predict(b) - result.predict(a)), rtol=1e-14)


def test_identical_points_have_exactly_zero_difference_covariance(correlated_case):
    _, _, result = correlated_case
    point = [0.3, 0.4, -0.2]
    assert difference_prediction_leverage(result, point, point) == 0
    assert_array_equal(difference_prediction_covariance(result, point, point), np.zeros((3, 3)))
    assert_allclose(
        cross_prediction_covariance(result, point, point),
        mean_prediction_covariance(result, point),
        rtol=1e-14,
    )


def test_nearby_point_difference_avoids_marginal_cancellation(hand_case):
    factors, _, _, sigma, _, responses = hand_case
    result = fit_multivariate_rsm(factors, responses)
    # h for the contrast z(0)-z(d)=[0,-d,-d^2] is d^2/10+d^4/14.
    d = 1e-10
    expected_h = d * d / 10 + d**4 / 14
    assert_allclose(difference_prediction_leverage(result, [0], [d]), expected_h, rtol=1e-14)
    assert_allclose(
        difference_prediction_covariance(result, [0], [d]), expected_h * sigma, rtol=1e-14, atol=0
    )


@pytest.mark.parametrize("j", [-1, 3, 0.5, True, "0"])
def test_response_index_validation(correlated_case, j):
    with pytest.raises(ValueError, match="response_index"):
        coefficient_covariance_by_response(correlated_case[2], j)


@pytest.mark.parametrize(
    "point", [[0, 1], [0, 1, 2, 3], [[0, 1, 2]], [0, np.nan, 2], [0, np.inf, 2], [1j, 0, 1]]
)
@pytest.mark.parametrize(
    "function", [prediction_leverage, mean_prediction_covariance, mean_prediction_variance]
)
def test_point_uncertainty_input_validation(correlated_case, point, function):
    with pytest.raises(ValueError):
        function(correlated_case[2], point)


@pytest.mark.parametrize(
    "function",
    [
        cross_prediction_leverage,
        cross_prediction_covariance,
        difference_prediction_leverage,
        difference_prediction_covariance,
    ],
)
@pytest.mark.parametrize("bad_side", [0, 1])
def test_pair_input_validation(correlated_case, function, bad_side):
    points = [[0, 0, 0], [1, 1, 1]]
    points[bad_side] = [np.nan, 1, 0]
    with pytest.raises(ValueError, match="finite"):
        function(correlated_case[2], *points)


def test_uncertainty_functions_do_not_mutate_inputs_or_result(correlated_case):
    _, _, result = correlated_case
    a, b = np.array([0.4, 0.2, -0.8]), np.array([-0.2, 0.5, 0.1])
    before_a, before_b = a.copy(), b.copy()
    coefficients, sigma = result.coefficients.copy(), result.residual_covariance.copy()
    for function in [prediction_leverage, mean_prediction_covariance, mean_prediction_variance]:
        function(result, a)
    for function in [
        cross_prediction_leverage,
        cross_prediction_covariance,
        difference_prediction_leverage,
        difference_prediction_covariance,
    ]:
        function(result, a, b)
    coefficient_covariance(result)
    coefficient_covariance_by_response(result, 0)
    assert_array_equal(a, before_a)
    assert_array_equal(b, before_b)
    assert_array_equal(result.coefficients, coefficients)
    assert_array_equal(result.residual_covariance, sigma)
