"""Analytic global oracles, independent optimizers, geometry and payoff orientation."""

from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scipy.optimize import minimize

from cnbi_v2.model import fit_multivariate_rsm, quadratic_design
from cnbi_v2.optimization import (
    Direction,
    QuadraticResponse,
    RCOptions,
    classify_response_distance,
    deterministic_ball_starts,
    evaluate_responses,
    legacy_chi_square_threshold,
    payoff_matrix,
    quadratic_responses,
    response_cloud_region,
    solve_quadratic_ball,
    solve_response_region_anchor,
)


def quadratic(linear, matrix, intercept=0.0):
    return QuadraticResponse(intercept, np.asarray(linear), np.asarray(matrix))


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("direction", [Direction.MIN, Direction.MAX])
def test_convex_min_concave_max_interior_oracle(n, direction):
    sign = direction.minimization_sign
    optimum = np.arange(1, n + 1) / (4 * n)
    model = quadratic(-2 * sign * optimum, sign * np.eye(n), 3.0)
    result = solve_quadratic_ball(model, 2.0, direction)
    assert_allclose(result.point, optimum, atol=2e-15)
    assert_allclose(result.objective, 3 - sign * (optimum @ optimum))
    assert not result.boundary_active
    assert result.multiplier == 0
    assert result.converged


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("direction", [Direction.MIN, Direction.MAX])
def test_linear_boundary_global_oracle(n, direction):
    b = np.arange(1, n + 1, dtype=float)
    result = solve_quadratic_ball(quadratic(b, np.zeros((n, n))), 1.7, direction)
    expected = -direction.minimization_sign * 1.7 * b / np.linalg.norm(b)
    assert_allclose(result.point, expected, atol=2e-15)
    assert result.boundary_active
    assert_allclose(result.norm, 1.7)
    assert result.normalized_stationarity < 1e-14


def test_indefinite_hard_case_global_not_saddle():
    model = quadratic([0, -2], [[-1, 0], [0, 1]])
    result = solve_quadratic_ball(model, 1, Direction.MIN)
    # (Q+mu I)x=-b/2, mu=1 => x2=1/2, |x1|=sqrt(3)/2.
    assert result.solution_case == "BOUNDARY_HARD_CASE"
    assert_allclose(abs(result.point[0]), np.sqrt(3) / 2)
    assert_allclose(result.point[1], 0.5)
    assert_allclose(result.objective, -1.5)
    assert result.normalized_shifted_min_eigenvalue == 0
    assert result.objective < model.value([0, 1])


def test_repeated_negative_eigenvalues_and_psd_flat_directions():
    hard = solve_quadratic_ball(quadratic([0, 0, 0], np.diag([-2, -2, 1])), 2, Direction.MIN)
    assert_allclose(hard.objective, -8)
    assert_allclose(hard.norm, 2)
    flat = solve_quadratic_ball(quadratic([0, -1], np.diag([0, 2])), 1, Direction.MIN)
    assert_allclose(flat.point, [0, 0.25])
    constant = solve_quadratic_ball(quadratic([0], [[0]], 7), 1, Direction.MAX)
    assert_array_equal(constant.point, [0])
    assert constant.objective == 7


def test_regular_secular_case_and_independent_scipy_validation():
    for q, b in [(np.diag([2., 1.]), [-7., 3.]),
                 (np.diag([-2., 1.]), [0.1, -2.]),
                 (np.array([[1., .2, .3], [.2, -1., .1], [.3, .1, 2.]]), [1., 2., -1.])]:
        model = quadratic(b, q)
        answer = solve_quadratic_ball(model, 1, Direction.MIN)
        assert answer.solution_case == "BOUNDARY_SECULAR"
        candidates = []
        for start in deterministic_ball_starts(len(b), 1):
            external = minimize(model.value, start, jac=model.gradient, method="SLSQP",
                                constraints={"type": "ineq", "fun": lambda x: 1 - x @ x,
                                             "jac": lambda x: -2 * x},
                                options={"ftol": 1e-12, "maxiter": 500})
            if external.success and np.linalg.norm(external.x) <= 1 + 1e-8:
                candidates.append(external.fun)
        assert candidates
        assert_allclose(answer.objective, min(candidates), atol=2e-10)
        assert answer.iterations > 0


def test_quadratic_extraction_full_interactions_and_gradients():
    points = np.array(list(np.ndindex(3, 3, 3)), dtype=float) - 1
    coefficients = np.arange(20).reshape(10, 2) / 10 - 0.6
    fit = fit_multivariate_rsm(points, quadratic_design(points) @ coefficients)
    models = quadratic_responses(fit)
    for j, model in enumerate(models):
        assert_allclose(model.linear, coefficients[1:4, j], atol=2e-15)
        assert_allclose(np.diag(model.quadratic), coefficients[4:7, j], atol=2e-15)
        assert_allclose([model.quadratic[0, 1], model.quadratic[0, 2], model.quadratic[1, 2]],
                        coefficients[7:, j] / 2, atol=2e-15)
    for point in points:
        assert_allclose(evaluate_responses(models, point), fit.predict(point), atol=5e-15)
    model = models[0]
    x = np.array([.1, .2, -.4])
    finite_difference = [(model.value(x + d) - model.value(x - d)) / 2e-6
                         for d in np.eye(3) * 1e-6]
    assert_allclose(model.gradient(x), finite_difference, atol=1e-9)


def identity_cloud(n=2):
    # 2n points +/-sqrt((2n-1)/2) e_i => sample covariance exactly I.
    observed = np.vstack([np.eye(n), -np.eye(n)]) * np.sqrt((2*n-1)/2)
    return observed, response_cloud_region(observed)


@pytest.mark.parametrize("n", [2, 3])
def test_response_region_manual_geometry_spd_and_metric_gradient(n):
    observed, region = identity_cloud(n)
    assert_allclose(region.center, 0, atol=2e-16)
    assert_allclose(region.covariance, np.eye(n), atol=3e-16)
    assert region.rank == n
    assert_allclose(region.condition_number, 1)
    assert_allclose(region.log_determinant, 0, atol=2e-15)
    assert_allclose(region.distance_squared(np.zeros(n)), 0, atol=1e-30)
    point = np.arange(1, n + 1, dtype=float)
    assert_allclose(region.distance_squared(point), point @ point)
    assert_allclose(region.metric_gradient(point), 2 * point)
    assert_allclose(region.distances_squared(observed).sum(), n * (len(observed) - 1))
    assert_allclose(region.distance_squared(point), region.distance_squared(-point))


def test_mahalanobis_invariant_to_nonsingular_linear_transform_and_offset():
    y, a = identity_cloud(3)
    transform = np.array([[1, 2, 0], [0, .01, 1], [1, 0, 3.]])
    offset = np.array([10, -5, 1])
    b = response_cloud_region(y @ transform.T + offset)
    point = np.array([.5, .2, -.3])
    assert_allclose(a.distance_squared(point),
                    b.distance_squared(transform @ point + offset), rtol=2e-13)


@pytest.mark.parametrize("y", [[[1, 1], [2, 2], [3, 3]], np.ones((5, 3)),
                              [[0, 0], [1, 1e-20], [-1, 1e-20]]])
def test_singular_or_unstable_covariance_fails_without_correction(y):
    with pytest.raises(np.linalg.LinAlgError, match="singular or numerically unstable"):
        response_cloud_region(y)


@pytest.mark.parametrize("bad", [[], [1, 2], [[]], [[1, 2]]])
def test_cloud_shape_validation(bad):
    with pytest.raises(ValueError, match="shape"):
        response_cloud_region(bad)


def identity_models():
    return (quadratic([1, 0], np.zeros((2, 2))), quadratic([0, 1], np.zeros((2, 2))))


@pytest.mark.parametrize("j,direction,expected", [(0, Direction.MAX, [.5, 0]),
                                                (1, Direction.MIN, [0, -.5])])
def test_rc_manual_oracle_multistart_and_payoff(j, direction, expected):
    _, region = identity_cloud()
    models = identity_models()
    proposals = np.vstack([[[0, 0]], [[0, 0]], [[2, 0]], deterministic_ball_starts(2, 1)])
    result = solve_response_region_anchor(models, j, direction, 1, region, .25, proposals)
    assert_allclose(result.point, expected, atol=2e-8)
    assert not result.global_optimum_certified  # SLSQP has no general global proof.
    assert result.response_boundary_active
    assert not result.sphere_boundary_active
    assert result.sphere_margin >= -result.options.sphere_tolerance
    assert result.response_margin >= -result.options.response_tolerance
    assert result.rejected_start_indices
    assert len(result.trials) == len(result.feasible_starts)
    assert any(t.accepted for t in result.trials)
    assert all(not t.accepted or t.solver_success for t in result.trials)
    assert classify_response_distance(result.distance_squared, .25, 1e-6) == "BOUNDARY_NEAR"


def test_feasible_classical_anchor_reused_with_global_certificate():
    models = identity_models()
    _, region = identity_cloud()
    result = solve_response_region_anchor(models, 0, Direction.MAX, 1, region, 2, [[0, 0]])
    assert result.global_optimum_certified
    assert result.solver == "SPHERE_GLOBAL_CERTIFICATE"
    assert_allclose(result.point, [1, 0])
    assert len(result.trials) == 1


@pytest.mark.parametrize("objective", [0, 1])
def test_quartic_response_constraint_and_nonconvex_objective_multistart(objective):
    _, region = identity_cloud()
    models = [quadratic([1], [[0]]), quadratic([0], [[1]])]
    # D²=x²+x^4<=5/16 gives |x|<=1/2. For MAX x², zero is an
    # unhelpful stationary start; deterministic nonzero starts find the boundary.
    result = solve_response_region_anchor(models, objective, Direction.MAX,
                                         1, region, 5/16, [[-.4], [0], [.4]])
    assert_allclose(abs(result.point[0]), .5, atol=2e-8)
    assert_allclose(result.objective, .5 if objective == 0 else .25, atol=2e-8)
    assert not result.global_optimum_certified
    assert result.response_boundary_active


def test_disconnected_quartic_response_region_has_manual_optimum():
    _, region = identity_cloud()
    models = [quadratic([0, 0], [[1, 0], [0, 0]], -1),
              quadratic([0, 1], np.zeros((2, 2)))]
    # (x1²-1)²+x2²<=1/4 has disconnected lobes. MAX x2=1/2 at
    # x1=+/-1, strictly inside the decision ball of radius two.
    result = solve_response_region_anchor(models, 1, Direction.MAX, 2, region, .25,
                                         [[0, 0], [-1, 0], [1, 0]])
    assert result.rejected_start_indices == (0,)
    assert_allclose(result.point[1], .5, atol=2e-8)
    assert_allclose(abs(result.point[0]), 1, atol=2e-8)
    assert not result.sphere_boundary_active


def test_oriented_payoff_rows_responses_columns_anchors():
    models = identity_models()
    points = np.array([[1, .2], [.3, -1]])
    payoff = payoff_matrix(models, points)
    assert payoff.shape == (2, 2)
    assert_array_equal(payoff, points.T)
    assert_array_equal(np.diag(payoff), [1, -1])
    for j, point in enumerate(points):
        assert_array_equal(payoff[:, j], evaluate_responses(models, point))
    order = [1, 0]
    reordered = payoff_matrix([models[i] for i in order], points[order])
    assert_array_equal(reordered, payoff[np.ix_(order, order)])


def test_feasible_anchors_do_not_imply_feasible_assembled_utopia():
    _, region = identity_cloud()
    points = np.array([[.5, 0], [0, .5]])
    payoff = payoff_matrix(identity_models(), points)
    assert_allclose(region.distances_squared(payoff.T), [.25, .25])
    assert_allclose(region.distance_squared(np.diag(payoff)), .5)
    assert region.distance_squared(np.diag(payoff)) > .25


def test_region_model_and_result_immutability():
    models = identity_models()
    _, region = identity_cloud()
    result = solve_response_region_anchor(models, 0, Direction.MAX, 1, region, .25,
                                         deterministic_ball_starts(2, 1))
    sphere = solve_quadratic_ball(models[0], 1, Direction.MAX)
    for array in [models[0].linear, models[0].quadratic, region.center, region.covariance,
                  region.cholesky, region.eigenvalues, result.point, result.feasible_starts,
                  result.trials[0].start, result.trials[0].point, sphere.point]:
        with pytest.raises(ValueError):
            array.setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        result.objective = 0


@pytest.mark.parametrize("distance,expected", [(0, "INSIDE_RESPONSE_REGION"),
                                               (1, "BOUNDARY_NEAR"),
                                               (2, "OUTSIDE_RESPONSE_REGION")])
def test_explicit_distance_classification(distance, expected):
    assert classify_response_distance(distance, 1, 1e-8) == expected


def test_threshold_is_legacy_chi_square_not_exact_confidence():
    # Chi-square with two df has CDF 1-exp(-x/2).
    assert_allclose(legacy_chi_square_threshold(2, .95), -2 * np.log(.05))
    assert_allclose(legacy_chi_square_threshold(8), 15.50731305586545)


@pytest.mark.parametrize("dimension,coverage", [(0, .95), (True, .95), (2.5, .95),
                                               (2, 0), (2, 1), (2, np.nan)])
def test_invalid_threshold_arguments(dimension, coverage):
    with pytest.raises(ValueError):
        legacy_chi_square_threshold(dimension, coverage)


@pytest.mark.parametrize("radius,tolerance", [(0, 1e-10), (-1, 1e-10), (np.inf, 1e-10),
                                              (1, 0), (1, np.nan)])
def test_invalid_sphere_arguments(radius, tolerance):
    with pytest.raises(ValueError):
        solve_quadratic_ball(quadratic([1], [[1]]), radius, Direction.MIN,
                             certificate_tolerance=tolerance)


def test_invalid_quadratic_and_point_contracts():
    for args in [([1, 2], [[1]]), ([], []), ([1], [[1]], np.inf)]:
        with pytest.raises(ValueError):
            quadratic(*args)
    with pytest.raises(ValueError, match="symmetric"):
        quadratic([1, 2], [[1, 2], [0, 1]])
    with pytest.raises(ValueError, match="factor dimension"):
        quadratic([1], [[1]]).value([1, 2])


def test_invalid_region_points_payoff_and_starts():
    _, region = identity_cloud()
    for fn, arg in [(region.distances_squared, [1, 2]),
                    (region.distance_squared, [[1, 2]]),
                    (region.metric_gradient, [1])]:
        with pytest.raises(ValueError):
            fn(arg)
    with pytest.raises(ValueError):
        payoff_matrix(identity_models(), [[0, 0]])
    for dimension, radius in [(0, 1), (True, 1), (2, 0)]:
        with pytest.raises(ValueError):
            deterministic_ball_starts(dimension, radius)
    with pytest.raises(ValueError):
        classify_response_distance(-1, 1, 0)
    with pytest.raises(ValueError):
        RCOptions(ftol=0)


def test_rc_checks_model_dimensions_start_shape_and_feasibility():
    _, region = identity_cloud()
    models = identity_models()
    for args in [(models, 2, Direction.MAX, 1, region, .25, [[0, 0]]),
                 (models, 0, Direction.MAX, 1, region, -1, [[0, 0]]),
                 (models, 0, Direction.MAX, 1, region, .25, [0, 0]),
                 ([models[0], quadratic([1], [[0]])], 0, Direction.MAX,
                  1, region, .25, [[0, 0]])]:
        with pytest.raises(ValueError):
            solve_response_region_anchor(*args)
    with pytest.raises(ValueError, match="no feasible deterministic start"):
        solve_response_region_anchor(models, 0, Direction.MAX, 1, region, .25, [[.9, .9]])


@pytest.mark.parametrize("point,success", [([2., 0.], True), ([.8, 0.], True),
                                           ([0., 0.], False)])
def test_solver_success_alone_does_not_accept_infeasible_rc(point, success, monkeypatch):
    import cnbi_v2.optimization.anchors as module
    monkeypatch.setattr(module, "minimize", lambda *a, **k: SimpleNamespace(
        x=np.array(point), success=success, status=0, message="test solver", nit=1))
    _, region = identity_cloud()
    with pytest.raises(RuntimeError, match="both independent feasibility checks"):
        solve_response_region_anchor(identity_models(), 0, Direction.MAX,
                                     1, region, .25, [[0, 0]])


def test_nonfinite_rc_solver_output_fails(monkeypatch):
    import cnbi_v2.optimization.anchors as module
    monkeypatch.setattr(module, "minimize",
                        lambda *a, **k: SimpleNamespace(x=np.array([np.nan, 0])))
    _, region = identity_cloud()
    with pytest.raises(FloatingPointError):
        solve_response_region_anchor(identity_models(), 0, Direction.MAX,
                                     1, region, .25, [[0, 0]])


def test_rc_constant_objective_and_classical_certificate_guard(monkeypatch):
    import cnbi_v2.optimization.trust_region as module
    _, region = identity_cloud()
    models = [quadratic([0, 0], np.zeros((2, 2))), identity_models()[1]]
    anchor = solve_response_region_anchor(models, 0, Direction.MIN, 1, region, .25, [[0, 0]])
    assert anchor.objective_scale == 1
    # A failed spectral decomposition must not be reported as a certified optimum.
    monkeypatch.setattr(module.np.linalg, "eigh", lambda x: (np.array([1.]), np.array([[2.]])))
    with pytest.raises(np.linalg.LinAlgError, match="certificate failed"):
        solve_quadratic_ball(quadratic([1], [[1]]), 1, Direction.MIN)
