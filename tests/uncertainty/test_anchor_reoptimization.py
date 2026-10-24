"""Independent optimizer/payoff oracles and exact deterministic batch contracts."""

from dataclasses import FrozenInstanceError, replace

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.model import fit_multivariate_rsm, quadratic_design
from cnbi_v2.optimization import (
    Direction,
    quadratic_responses,
    quadratic_responses_from_coefficients,
)
from cnbi_v2.uncertainty import reoptimize_coefficient_ensemble


def test_single_replica_manual_min_max_and_payoff_oracle():
    # f0=(x-.25)^2, MIN at .25. f1=-(x+.5)^2+2, MAX at -.5.
    coefficients = np.array([[.0625, 1.75], [-.5, -1], [1, -1]])
    result = reoptimize_coefficient_ensemble(coefficients[None], 1,
                                            [Direction.MIN, Direction.MAX], 1)
    assert result.attempted == result.successful == 2 and result.failed == 0
    assert not result.failures
    assert result.anchors.shape == (1, 2, 1) and result.payoffs.shape == (1, 2, 2)
    assert_allclose(result.anchors[0, :, 0], [.25, -.5], atol=1e-15)
    assert_allclose(result.optimal_values, [[0, 2]], atol=1e-15)
    assert_allclose(result.payoffs[0], [[0, .5625], [1.4375, 2]], atol=1e-15)
    assert_array_equal(result.locations, [["INTERIOR", "INTERIOR"]])
    assert_array_equal(np.diagonal(result.payoffs, axis1=1, axis2=2), result.optimal_values)


def test_array_extraction_reuses_the_fitted_model_transform_with_all_interactions():
    coefficients = np.arange(30, dtype=float).reshape(10, 3) / 10
    points = np.random.default_rng(8).normal(size=(30, 3))
    fit = fit_multivariate_rsm(points, quadratic_design(points) @ coefficients)
    direct = quadratic_responses_from_coefficients(fit.coefficients, 3)
    legacy = quadratic_responses(fit)
    for j, (a, b) in enumerate(zip(direct, legacy, strict=True)):
        assert a.intercept == b.intercept
        assert_array_equal(a.linear, b.linear)
        assert_array_equal(a.quadratic, b.quadratic)
        assert a.quadratic[0, 1] == fit.coefficients[7, j] / 2
        assert a.quadratic[0, 2] == fit.coefficients[8, j] / 2
        assert a.quadratic[1, 2] == fit.coefficients[9, j] / 2
        assert_allclose([a.value(x) for x in points], fit.predict(points)[:, j], atol=1e-13)
    with pytest.raises(ValueError, match="shape"):
        quadratic_responses_from_coefficients(np.ones((9, 8)), 3)
    with pytest.raises(ValueError):
        quadratic_responses_from_coefficients(np.ones((10, 0)), 3)


def test_boundaries_hard_case_flat_case_and_independent_certificates():
    # Three two-factor functions: linear maximum, hard-case minimum, flat minimum.
    coefficients = np.array([[0, 0, 7], [1, 0, 0], [2, -2, 0],
                             [0, -1, 0], [0, 1, 0], [0, 0, 0]], dtype=float)
    result = reoptimize_coefficient_ensemble(coefficients[None], 2,
                                            [Direction.MAX, Direction.MIN, Direction.MIN], 1)
    assert result.successful == 3
    assert_array_equal(result.solver_cases,
                       [["BOUNDARY_SECULAR", "BOUNDARY_HARD_CASE", "INTERIOR_OR_PSD_MINIMUM_NORM"]])
    assert_array_equal(result.locations, [["BOUNDARY", "BOUNDARY", "INTERIOR"]])
    assert_allclose(result.anchors[0, 0], [1/np.sqrt(5), 2/np.sqrt(5)])
    assert_allclose(abs(result.anchors[0, 1, 0]), np.sqrt(3)/2)
    assert_allclose(result.anchors[0, 1, 1], .5)
    assert_array_equal(result.anchors[0, 2], [0, 0])
    assert_allclose(result.optimal_values[0], [np.sqrt(5), -1.5, 7])
    assert np.all(result.certificates[:, :, 0:2] <= 1e-10)
    assert np.all(result.certificates[:, :, 2] >= -np.finfo(float).eps*32)
    assert np.all(result.certificates[:, :, 4] <= 1+1e-10)


def test_replica_independence_prefix_permutation_and_no_global_rng_changes():
    coefficients = np.array([[[1., 2.], [2., -1.], [-1., 2.]],
                             [[3., 7.], [-1., 2.], [1., -2.]],
                             [[2., 3.], [1., 1.], [-1., 1.]]])
    directions = [Direction.MAX, Direction.MIN]
    before = coefficients.copy()
    state = np.random.get_state()
    full = reoptimize_coefficient_ensemble(coefficients, 1, directions, 1)
    repeat = reoptimize_coefficient_ensemble(coefficients, 1, directions, 1)
    short = reoptimize_coefficient_ensemble(coefficients[:2], 1, directions, 1)
    isolated = reoptimize_coefficient_ensemble(coefficients[1:2], 1, directions, 1)
    shuffled = reoptimize_coefficient_ensemble(coefficients[[2, 0, 1]], 1, directions, 1)
    permuted = reoptimize_coefficient_ensemble(coefficients[:, :, ::-1], 1, directions[::-1], 1)
    for name in ["anchors", "optimal_values", "payoffs", "certificates", "solver_cases"]:
        a, b = getattr(full, name), getattr(repeat, name)
        assert a.tobytes() == b.tobytes()
        assert_array_equal(a[:2], getattr(short, name))
        assert_array_equal(a[1:2], getattr(isolated, name))
        assert_array_equal(a[[2, 0, 1]], getattr(shuffled, name))
    assert_array_equal(permuted.anchors, full.anchors[:, ::-1])
    assert_array_equal(permuted.optimal_values, full.optimal_values[:, ::-1])
    assert_array_equal(permuted.payoffs, full.payoffs[:, ::-1, ::-1])
    assert_array_equal(before, coefficients)
    now = np.random.get_state()
    assert state[0] == now[0] and state[2:] == now[2:]
    assert_array_equal(state[1], now[1])
    for name in ["anchors", "optimal_values", "payoffs", "norms", "solver_cases",
                 "locations", "valid_anchors", "valid_payoffs", "certificates"]:
        with pytest.raises(ValueError):
            getattr(full, name).setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        full.radius = 2


@pytest.mark.parametrize("field,value", [
    ("converged", False), ("objective", np.inf), ("point", np.array([np.nan])),
    ("point", np.array([0., 0.])), ("direction", Direction.MIN), ("radius", 2.),
    ("objective_scale", -1.), ("objective_scale", 1e20), ("certificate_tolerance", 1e-3),
    ("normalized_stationarity", 1.), ("normalized_complementarity", 1.),
    ("normalized_shifted_min_eigenvalue", -1.), ("objective", -99.),
    ("norm", -1.), ("multiplier", -1.), ("point", np.array([2.])),
    ("solution_case", "a"*41),
])
def test_invalid_solver_result_is_logged_without_any_substitute(monkeypatch, field, value):
    import cnbi_v2.uncertainty.anchor_reoptimization as module
    original = module.solve_quadratic_ball
    def invalid(*args, **kwargs):
        return replace(original(*args, **kwargs), **{field: value})
    monkeypatch.setattr(module, "solve_quadratic_ball", invalid)
    result = reoptimize_coefficient_ensemble([[[1.], [1.], [1.]]], 1, [Direction.MAX], 1)
    assert result.attempted == result.failed == 1 and result.successful == 0
    assert result.failures[0].replicate_id == 1
    assert result.failures[0].failure_type == "INVALID_CERTIFICATE"
    assert np.isnan(result.anchors).all() and np.isnan(result.optimal_values).all()
    assert np.isnan(result.payoffs).all() and not result.valid_payoffs.any()


def test_solver_exception_keeps_ids_and_successful_anchors_without_dropping_replica(monkeypatch):
    import cnbi_v2.uncertainty.anchor_reoptimization as module
    original = module.solve_quadratic_ball
    def partial(model, *args, **kwargs):
        if model.intercept == 7:
            raise np.linalg.LinAlgError("deliberate failure")
        return original(model, *args, **kwargs)
    monkeypatch.setattr(module, "solve_quadratic_ball", partial)
    samples = np.array([[[1., 2.], [1., 1.], [1., 1.]],
                        [[7., 2.], [1., 1.], [1., 1.]]])
    result = reoptimize_coefficient_ensemble(samples, 1, [Direction.MIN]*2, 1,
                                            response_names=["a", "b"])
    assert result.attempted == 4 and result.successful == 3 and result.failed == 1
    assert result.failures[0].replicate_id == 2 and result.failures[0].response == "a"
    assert result.failures[0].failure_type == "SOLVER_EXCEPTION"
    assert "deliberate failure" in result.failures[0].failure_message
    assert np.isnan(result.anchors[1, 0]).all() and np.isfinite(result.anchors[1, 1]).all()
    assert np.isfinite(result.payoffs[0]).all() and np.isnan(result.payoffs[1]).all()


@pytest.mark.parametrize("payoff", [np.array([[np.inf]]), np.array([[999.]])])
def test_payoff_failure_is_separate_from_successful_optimization(monkeypatch, payoff):
    import cnbi_v2.uncertainty.anchor_reoptimization as module
    monkeypatch.setattr(module, "payoff_matrix", lambda *args: payoff)
    result = reoptimize_coefficient_ensemble([[[0.], [0.], [1.]]], 1, [Direction.MIN], 1)
    assert result.successful == 1 and result.failed == 0
    assert not result.valid_payoffs[0] and np.isnan(result.payoffs).all()
    assert result.failures[0].failure_type == "PAYOFF_FAILURE"


@pytest.mark.parametrize("samples,n,directions,radius", [
    (np.ones((0, 3, 1)), 1, [Direction.MIN], 1),
    (np.ones((1, 2, 1)), 1, [Direction.MIN], 1),
    (np.ones((1, 3, 0)), 1, [], 1), (np.ones((3, 1)), 1, [Direction.MIN], 1),
    (np.full((1, 3, 1), np.inf), 1, [Direction.MIN], 1),
    (np.ones((1, 3, 1)), True, [Direction.MIN], 1),
    (np.ones((1, 3, 1)), 1, [], 1), (np.ones((1, 3, 1)), 1, ["BAD"], 1),
    (np.ones((1, 3, 1)), 1, [Direction.MIN], 0),
])
def test_invalid_input_fails_before_solving(samples, n, directions, radius):
    with pytest.raises(ValueError):
        reoptimize_coefficient_ensemble(samples, n, directions, radius)


def test_invalid_response_names():
    for names in [[""], ["a", "a"], [1], []]:
        with pytest.raises(ValueError):
            reoptimize_coefficient_ensemble([[[1.], [1.], [1.]]], 1, [Direction.MIN], 1,
                                            response_names=names)


def test_radial_classification_uses_existing_solver_tolerance():
    centers = np.array([1-5e-11, 1-2e-10])
    samples = np.stack([centers**2, -2*centers, np.ones(2)], axis=1)[:, :, None]
    result = reoptimize_coefficient_ensemble(samples, 1, [Direction.MIN], 1)
    assert_array_equal(result.locations[:, 0], ["BOUNDARY", "INTERIOR"])
    assert np.all(result.solver_cases == "INTERIOR_OR_PSD_MINIMUM_NORM")


def test_independent_certificate_rejects_falsely_reported_stationary_psd(monkeypatch):
    import cnbi_v2.uncertainty.anchor_reoptimization as module
    original = module.solve_quadratic_ball
    def forged(model, *args, **kwargs):
        answer = original(model, *args, **kwargs)
        return replace(answer, point=np.zeros(1), norm=0., objective=model.value([0]),
                       multiplier=0., normalized_stationarity=0.,
                       normalized_complementarity=0., normalized_shifted_min_eigenvalue=0.)
    monkeypatch.setattr(module, "solve_quadratic_ball", forged)
    # Origin is a stationary maximum of -x², not the requested global minimum.
    result = reoptimize_coefficient_ensemble([[[0.], [0.], [-1.]]], 1, [Direction.MIN], 1)
    assert result.failed == 1 and result.failures[0].failure_type == "INVALID_CERTIFICATE"
