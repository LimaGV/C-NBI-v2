"""Independent small oracles and degenerate-state contracts for diagnostics."""

from dataclasses import FrozenInstanceError, fields, replace

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.model import (
    DiagnosticStatus,
    diagnose_rsm,
    factor_configuration_groups,
    fit_multivariate_rsm,
    prediction_leverage,
    quadratic_design,
)
from cnbi_v2.model.diagnostics import _f_test, _training_leverages


def manual_case():
    x = np.arange(-2.0, 3.0).reshape(-1, 1)
    # beta=(2,3,1/2), residual=(1,-4,6,-4,1), X.T e=0 by hand.
    y = np.array([-1, -4.5, 8, 1.5, 11])
    fit = fit_multivariate_rsm(x, y)
    return x, y, fit, diagnose_rsm(fit, x).responses[0]


def test_manual_sums_r_squared_mse_and_global_anova():
    _, _, fit, d = manual_case()
    assert_allclose([d.sse, d.sst, d.ssr, d.mse], [70, 163.5, 93.5, 35], rtol=1e-14)
    assert_allclose([d.r_squared, d.adjusted_r_squared], [187 / 327, 47 / 327], rtol=1e-14)
    assert (d.model_df, d.error_df) == (2, 2)
    assert_allclose([d.model_ms, d.error_ms, d.model_f], [46.75, 35, 187 / 140])
    # Independently, the F(2,2) survival probability at f is 1/(1+f).
    assert_allclose(d.model_p_value, 140 / 327, rtol=1e-14)
    assert d.model_status == DiagnosticStatus.OK
    assert d.r_squared_status == DiagnosticStatus.OK
    assert_allclose(d.s**2, d.mse)
    assert_allclose(d.mse, fit.residual_covariance[0, 0])


def test_manual_leverages_and_press_preserves_negative_predicted_r_squared():
    x, _, fit, d = manual_case()
    result = diagnose_rsm(fit, x)
    expected_residuals = [35 / 4, -70 / 11, 35 / 3, -70 / 11, 35 / 4]
    press = 1225 / 8 + 9800 / 121 + 1225 / 9
    assert_allclose(result.hat_diagonal, np.array([31, 13, 17, 13, 31]) / 35, rtol=1e-14)
    assert_allclose(result.press_residuals[:, 0], expected_residuals, rtol=1e-14)
    assert_allclose(d.press, press, rtol=1e-14)
    assert_allclose(d.predicted_r_squared, 1 - press / 163.5, rtol=1e-14)
    assert d.predicted_r_squared < 0
    assert d.press_status == DiagnosticStatus.OK


@pytest.mark.parametrize("case", ["manual", "multivariate"])
def test_press_equals_independent_explicit_loocv(case, correlated_case):
    x, y, fit = manual_case()[:3] if case == "manual" else correlated_case
    y = np.asarray(y).reshape(len(x), -1)
    result = diagnose_rsm(fit, x)
    explicit = np.empty_like(y)
    for i in range(len(x)):
        keep = np.arange(len(x)) != i
        reduced = fit_multivariate_rsm(x[keep], y[keep])
        explicit[i] = y[i] - reduced.predict(x[i])
    assert_allclose(result.press_residuals, explicit, rtol=2e-12, atol=2e-13)
    assert_allclose([d.press for d in result.responses], np.sum(explicit**2, axis=0), rtol=2e-12)


def test_per_response_identities_and_leverages(correlated_case):
    x, _, fit = correlated_case
    result = diagnose_rsm(fit, x, ["a", "b", "c"])
    assert [d.response_name for d in result.responses] == ["a", "b", "c"]
    assert_allclose(result.hat_diagonal.sum(), fit.rank, rtol=1e-14)
    assert np.all((result.hat_diagonal >= 0) & (result.hat_diagonal <= 1))
    assert_allclose(result.hat_diagonal, [prediction_leverage(fit, row) for row in x], rtol=1e-13)
    for j, d in enumerate(result.responses):
        assert_allclose(d.sst, d.ssr + d.sse)
        assert_allclose(d.adjusted_r_squared, 1 - (1 - d.r_squared) * 18 / 9)
        assert d.adjusted_r_squared <= d.r_squared + 1e-15
        assert_allclose(d.s**2, fit.residual_covariance[j, j])
        assert_allclose(d.sse, d.lack_of_fit_ss + d.pure_error_ss, rtol=1e-13)


def test_exact_polynomial_perfect_fit():
    x = np.arange(-3.0, 4.0).reshape(-1, 1)
    fit = fit_multivariate_rsm(x, 2 + 3 * x[:, 0] - x[:, 0] ** 2)
    d = diagnose_rsm(fit, x).responses[0]
    assert d.sse < 1e-25
    assert d.press < 1e-24
    assert_allclose([d.r_squared, d.adjusted_r_squared, d.predicted_r_squared], 1)


@pytest.mark.parametrize("cubic", [0.0, 2.0])
def test_hand_pure_error_and_lack_of_fit(cubic):
    x = np.array([-2, -1, 0, 0, 0, 1, 2], dtype=float).reshape(-1, 1)
    y = 1 + 2 * x[:, 0] + x[:, 0] ** 2 + cubic * x[:, 0] ** 3
    y[2:5] += [-1, 0, 1]
    result = diagnose_rsm(fit_multivariate_rsm(x, y), x)
    d = result.responses[0]
    assert result.replicate_groups == ((2, 3, 4),)
    assert (d.pure_error_df, d.lack_of_fit_df) == (2, 2)
    assert_allclose(d.pure_error_ss, 2, rtol=1e-14)
    assert_allclose(d.lack_of_fit_ss, 14.4 * cubic**2, atol=1e-25, rtol=1e-14)
    assert_allclose(d.sse, 2 + 14.4 * cubic**2, rtol=1e-14)
    assert_allclose(d.lack_of_fit_ms, 7.2 * cubic**2, atol=1e-25, rtol=1e-14)
    assert_allclose(d.lack_of_fit_f, 7.2 * cubic**2, atol=1e-25, rtol=1e-14)
    assert_allclose(d.lack_of_fit_p_value, 1 / (1 + 7.2 * cubic**2), rtol=1e-14)
    assert d.lack_of_fit_status == DiagnosticStatus.OK


def test_no_replicates_explicitly_undefined_lack_of_fit():
    d = manual_case()[3]
    assert d.pure_error_df == 0
    assert d.pure_error_ss == 0
    assert d.pure_error_ms is d.lack_of_fit_f is d.lack_of_fit_p_value is None
    assert d.lack_of_fit_status == DiagnosticStatus.NO_REPLICATES
    assert_allclose(d.lack_of_fit_ss, d.sse)


def test_zero_lack_of_fit_degrees_of_freedom():
    x = np.array([-1, -1, 0, 0, 1, 1], dtype=float).reshape(-1, 1)
    d = diagnose_rsm(fit_multivariate_rsm(x, [0, 2, 1, 3, 4, 6]), x).responses[0]
    assert d.pure_error_df == 3
    assert d.lack_of_fit_df == 0
    assert d.lack_of_fit_ms is d.lack_of_fit_f is d.lack_of_fit_p_value is None
    assert d.lack_of_fit_status == DiagnosticStatus.NO_LACK_OF_FIT_DF
    assert_allclose(d.lack_of_fit_ss, 0, atol=1e-26)


def test_zero_pure_error_has_no_f_or_p():
    x = np.array([-2, -1, 0, 0, 1, 2], dtype=float).reshape(-1, 1)
    d = diagnose_rsm(fit_multivariate_rsm(x, x[:, 0] ** 3), x).responses[0]
    assert d.pure_error_ss == d.pure_error_ms == 0
    assert d.lack_of_fit_ss > 0
    assert d.lack_of_fit_f is d.lack_of_fit_p_value is None
    assert d.lack_of_fit_status == DiagnosticStatus.ZERO_PURE_ERROR


@pytest.mark.parametrize("constant", [0, 0.1, 1e9])
def test_constant_response_is_explicitly_undefined(constant):
    x = np.arange(-2.0, 3.0).reshape(-1, 1)
    d = diagnose_rsm(fit_multivariate_rsm(x, np.full(5, constant)), x).responses[0]
    assert d.sst == 0
    assert d.r_squared is d.adjusted_r_squared is d.predicted_r_squared is None
    assert d.model_f is d.model_p_value is None
    assert d.r_squared_status == d.model_status == DiagnosticStatus.CONSTANT_RESPONSE


def test_near_unit_leverage_does_not_divide_by_zero():
    x = np.array([0, 0, 1, 1, 2], dtype=float).reshape(-1, 1)
    result = diagnose_rsm(fit_multivariate_rsm(x, [0, 1, 2, 3, 8]), x)
    assert result.press_undefined_rows == (4,)
    assert result.press_residuals is None
    assert result.responses[0].press is result.responses[0].predicted_r_squared is None
    assert result.responses[0].press_status == DiagnosticStatus.PRESS_LEVERAGE_NEAR_ONE


def test_exact_groups_do_not_merge_nearby_factors():
    factors = [[0, 0], [-0.0, 0], [1, 2], [1, np.nextafter(2.0, 3.0)], [1, 2]]
    assert factor_configuration_groups(factors) == ((0, 1), (2, 4), (3,))


@pytest.mark.parametrize("bad", [[], [[]], [1, 2], np.zeros((2, 2, 2))])
def test_grouping_requires_nonempty_matrix(bad):
    with pytest.raises(ValueError, match="shape"):
        factor_configuration_groups(bad)


def test_response_scale_invariance_and_dimensional_scaling(correlated_case):
    x, y, fit = correlated_case
    original = diagnose_rsm(fit, x)
    scaled = diagnose_rsm(fit_multivariate_rsm(x, -7 * y), x)
    for a, b in zip(original.responses, scaled.responses, strict=True):
        for name in ["r_squared", "adjusted_r_squared", "predicted_r_squared", "model_f",
                     "model_p_value", "lack_of_fit_f", "lack_of_fit_p_value"]:
            assert_allclose(getattr(a, name), getattr(b, name), rtol=2e-13)
        for name in ["sse", "sst", "ssr", "mse", "press", "pure_error_ss", "lack_of_fit_ss"]:
            assert_allclose(getattr(b, name), 49 * getattr(a, name), rtol=2e-13)
        assert_allclose(b.s, 7 * a.s, rtol=1e-13)


def test_result_immutability_and_preservation_of_actual_inputs():
    x, y, fit, _ = manual_case()
    result = diagnose_rsm(fit, x)
    assert [d.response_name for d in result.responses] == ["response_0"]
    assert_array_equal(fit.experimental_factors, x)
    assert_array_equal(fit.observed_responses[:, 0], y)
    x[0] = 99
    y[0] = 99
    assert fit.experimental_factors[0, 0] == -2
    assert fit.observed_responses[0, 0] == -1
    for array in [result.hat_diagonal, result.press_residuals]:
        with pytest.raises(ValueError):
            array.setflags(write=True)
        with pytest.raises(ValueError):
            array.flat[0] = 99
    with pytest.raises(FrozenInstanceError):
        result.responses[0].sse = 99


@pytest.mark.parametrize("names", [[], ["a", "b"], [""], ["  "], [1]])
def test_response_name_validation(names):
    x, _, fit, _ = manual_case()
    with pytest.raises(ValueError, match="response_names"):
        diagnose_rsm(fit, x, names)


def test_duplicate_response_names(correlated_case):
    x, _, fit = correlated_case
    with pytest.raises(ValueError, match="unique"):
        diagnose_rsm(fit, x, ["a", "b", "a"])


@pytest.mark.parametrize("change", ["order", "coordinate", "shape"])
def test_factors_must_match_fit_in_original_row_order(change):
    x, _, fit, _ = manual_case()
    other = x[::-1] if change == "order" else x.copy()
    if change == "coordinate":
        other[0, 0] = np.nextafter(other[0, 0], 0)
    if change == "shape":
        other = other[:, 0]
    with pytest.raises(ValueError, match="same row order"):
        diagnose_rsm(fit, other)


def test_observation_and_response_permutations(correlated_case):
    x, y, fit = correlated_case
    original = diagnose_rsm(fit, x, ["a", "b", "c"])
    order = np.arange(len(x))[::-1]
    r_order = [2, 0, 1]
    permuted = diagnose_rsm(
        fit_multivariate_rsm(x[order], y[order][:, r_order]), x[order], ["c", "a", "b"]
    )
    assert_allclose(permuted.hat_diagonal, original.hat_diagonal[order], rtol=1e-13)
    for j, d in enumerate(permuted.responses):
        expected = original.responses[r_order[j]]
        for field in fields(d):
            a, b = getattr(d, field.name), getattr(expected, field.name)
            if isinstance(a, float):
                assert_allclose(a, b, rtol=1e-12)
            else:
                assert a == b


def test_leverage_trace_guard_detects_inconsistent_rank():
    with pytest.raises(np.linalg.LinAlgError, match="trace identity"):
        _training_leverages(quadratic_design(np.arange(5.0).reshape(-1, 1)), 2)


def test_nonfinite_f_is_a_diagnosed_error():
    with pytest.raises(FloatingPointError, match="nonfinite"):
        _f_test(1e308, 1e-308, 2, 2)


@pytest.mark.parametrize("bad", [np.inf, np.nan, -np.inf])
def test_result_cannot_silently_contain_nonfinite_statistics(bad):
    with pytest.raises(FloatingPointError, match="nonfinite computed diagnostic: press"):
        replace(manual_case()[3], press=bad)


def test_zero_error_mean_square_and_negative_model_ss_are_not_fabricated():
    # Exact nonconstant fit with zero arithmetic residual: singular F denominator.
    x = np.array([-2, -1, 0, 0, 1, 2], dtype=float).reshape(-1, 1)
    fit = fit_multivariate_rsm(x, x[:, 0] ** 2)
    zero_error = replace(fit, residuals=np.zeros((6, 1)), mse_by_response=np.zeros(1))
    d = diagnose_rsm(zero_error, x).responses[0]
    assert d.model_f is d.model_p_value is None
    assert d.model_status == DiagnosticStatus.ZERO_ERROR_MEAN_SQUARE
    # Deliberately inconsistent fit verifies the numerical-diagnostic branch.
    invalid = replace(fit, residuals=np.full((6, 1), 99.0))
    d = diagnose_rsm(invalid, x).responses[0]
    assert d.ssr < 0
    assert d.model_f is None
    assert d.model_status == DiagnosticStatus.NEGATIVE_MODEL_SS
