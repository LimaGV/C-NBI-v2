"""Analytic NBI oracles, high-precision quadratic reference and acceptance gates."""

from dataclasses import replace
from decimal import Decimal, localcontext
from types import SimpleNamespace

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.nbi import (
    LocalNBIProblem,
    NBIOptions,
    NBIStart,
    local_nbi_geometry,
    solve_local_nbi,
    solve_nbi_lattice,
)
from cnbi_v2.optimization import Direction, QuadraticResponse, payoff_matrix
from cnbi_v2.simplex import simplex_lattice


def linear_problem():
    models = (
        QuadraticResponse(0.0, np.array([1.0, 0.0]), np.zeros((2, 2))),
        QuadraticResponse(0.0, np.array([0.0, 1.0]), np.zeros((2, 2))),
    )
    anchors = np.array([[-1.0, 0.0], [0.0, -1.0]])
    return LocalNBIProblem(
        models,
        local_nbi_geometry(payoff_matrix(models, anchors), [Direction.MIN] * 2),
        anchors,
        1.0,
    )


def quadratic_problem():
    anchors = np.array([[1.0, 0.0], [-0.5, np.sqrt(3) / 2], [-0.5, -np.sqrt(3) / 2]])
    models = tuple(QuadraticResponse(1.0, -2 * x, np.eye(2)) for x in anchors)
    geometry = local_nbi_geometry(payoff_matrix(models, anchors), [Direction.MIN] * 3)
    return LocalNBIProblem(models, geometry, anchors, 1.5)


@pytest.mark.parametrize("problem", [linear_problem(), quadratic_problem()])
def test_unit_normal_orientation_orthogonality_and_exact_anchor_feasibility(problem):
    geometry = problem.geometry
    assert_allclose(geometry.centered.T @ geometry.normal, 0, atol=1e-15)
    assert_allclose(np.linalg.norm(geometry.normal), 1, atol=1e-15)
    assert geometry.normal @ geometry.centroid < 0
    assert_array_equal(np.diag(geometry.vertices), np.zeros(len(problem.models)))
    assert_array_equal(geometry.vertices.max(axis=1), np.ones(len(problem.models)))
    for j, anchor in enumerate(problem.anchors):
        weights = np.eye(len(problem.models))[j]
        assert_allclose(problem.residual(np.r_[anchor, 0.0], weights), 0, atol=1e-15)
        assert np.linalg.norm(weights @ problem.anchors) <= problem.radius
    for values in [geometry.normal, geometry.vertices, problem.anchors]:
        with pytest.raises(ValueError):
            values.setflags(write=True)


def test_linear_nbi_closed_form_intersection_with_the_ball():
    problem = linear_problem()
    for beta in ([0.5, 0.5], [0.2, 0.8], [1.0, 0.0]):
        start = NBIStart(np.array(beta) @ problem.anchors, 0.0, "CONVEX_COMBINATION")
        result = solve_local_nbi(problem, beta, [start])
        assert result.accepted
        # x1-x2 = beta2-beta1; maximize -(x1+x2) on the unit circle.
        difference = beta[1] - beta[0]
        total = -np.sqrt(2 - difference**2)
        expected_x = np.array([(total + difference) / 2, (total - difference) / 2])
        expected_t = (-1 - total) / np.sqrt(2)
        assert_allclose(result.point, expected_x, atol=3e-8, rtol=0)
        assert_allclose(result.t, expected_t, atol=3e-11, rtol=0)
        assert result.trials[-1].eq_norm < 1e-12
        assert result.trials[-1].sphere_margin >= -1e-9


def test_quadratic_nbi_matches_independent_sixty_digit_reference():
    problem = quadratic_problem()
    beta = np.array([0.2, 0.3, 0.5])
    with localcontext() as context:
        context.prec = 60
        # Equal Hessians cancel in pairwise equations: x=sum(beta*anchor).
        expected_x = [Decimal("-0.2"), -Decimal("0.1") * Decimal(3).sqrt()]
        expected_t = (1 - sum(x * x for x in expected_x)) / Decimal(3).sqrt()
    solution = solve_local_nbi(
        problem, beta, [NBIStart(beta @ problem.anchors, 0.0, "CONVEX_COMBINATION")]
    )
    assert solution.accepted
    assert_allclose(solution.point, list(map(float, expected_x)), atol=2e-12, rtol=0)
    assert_allclose(solution.t, float(expected_t), atol=2e-12, rtol=0)
    assert solution.trials[-1].eq_norm < 1e-12


def test_analytic_jacobians_match_central_differences_only_in_test():
    problem = quadratic_problem()
    vector, beta = np.array([0.2, -0.1, 0.3]), np.array([0.2, 0.3, 0.5])
    step = 1e-6
    numerical = np.column_stack(
        [
            (problem.residual(vector + step * d, beta) - problem.residual(vector - step * d, beta))
            / (2 * step)
            for d in np.eye(3)
        ]
    )
    assert_allclose(problem.equality_jacobian(vector), numerical, atol=1e-10, rtol=1e-8)
    sphere = np.array(
        [
            (problem.sphere_margin(vector + step * d) - problem.sphere_margin(vector - step * d))
            / (2 * step)
            for d in np.eye(3)
        ]
    )
    assert_allclose(problem.sphere_jacobian(vector), sphere, atol=2e-10, rtol=1e-8)


def test_simultaneous_objective_anchor_permutation_and_min_max_equivalence():
    problem = quadratic_problem()
    beta, permutation = np.array([0.2, 0.3, 0.5]), np.array([2, 0, 1])
    reordered = tuple(problem.models[j] for j in permutation)
    anchors = problem.anchors[permutation]
    other = LocalNBIProblem(
        reordered,
        local_nbi_geometry(payoff_matrix(reordered, anchors), [Direction.MIN] * 3),
        anchors,
        problem.radius,
    )
    assert_allclose(
        other.geometry.normal[np.argsort(permutation)], problem.geometry.normal, atol=1e-15
    )
    a = solve_local_nbi(problem, beta, [NBIStart(beta @ problem.anchors, 0.0, "original")])
    b = solve_local_nbi(
        other, beta[permutation], [NBIStart(beta @ problem.anchors, 0.0, "permuted")]
    )
    assert_allclose(a.point, b.point, atol=1e-12)
    assert_allclose(a.t, b.t, atol=1e-12)
    # Negate one natural response and declare it MAX; oriented functions stay equal.
    first = problem.models[0]
    negated = (
        QuadraticResponse(-first.intercept, -first.linear, -first.quadratic),
        *problem.models[1:],
    )
    mixed = LocalNBIProblem(
        negated,
        local_nbi_geometry(
            payoff_matrix(negated, problem.anchors), [Direction.MAX, Direction.MIN, Direction.MIN]
        ),
        problem.anchors,
        1.5,
    )
    c = solve_local_nbi(mixed, beta, [NBIStart(beta @ problem.anchors, 0.0, "mixed")])
    assert_allclose(a.point, c.point, atol=1e-12)
    assert_allclose(a.t, c.t, atol=1e-12)


def test_rank_deficient_ambiguous_or_bad_numeric_normal_fails_explicitly(monkeypatch):
    with pytest.raises(ValueError, match="affine rank"):
        local_nbi_geometry([[0, 0, 1], [0, 0, 1], [1, 1, 0]], [Direction.MIN] * 3)
    with pytest.raises(ValueError, match="ambiguous"):
        local_nbi_geometry([[0, 1, 1], [0, 0, 1], [0, 1, 0]], [Direction.MIN] * 3)
    original = np.linalg.svd

    def inaccurate(*args, **kwargs):
        u, s, v = original(*args, **kwargs)
        return 2 * u, s, v

    monkeypatch.setattr(np.linalg, "svd", inaccurate)
    with pytest.raises(ValueError, match="unit and orthogonal"):
        local_nbi_geometry([[0, 1], [1, 0]], [Direction.MIN] * 2)


@pytest.mark.parametrize(
    "mode", ["solver_failure", "equality", "sphere", "nonfinite", "overflow", "invalid_shape"]
)
def test_independent_acceptance_and_failure_log_without_false_points(mode, monkeypatch):
    from cnbi_v2.nbi import solver

    problem = linear_problem()

    def fake(*args, **kwargs):
        if mode == "overflow":
            raise FloatingPointError("forced overflow")
        x = np.array([-0.5, -0.5, 0.0])
        if mode == "equality":
            x[-1] = 1
        elif mode == "sphere":
            x[:] = [-1.5, -1.5, np.sqrt(2)]
        elif mode == "nonfinite":
            x[:] = np.nan
        elif mode == "invalid_shape":
            x = np.ones(4)
        return SimpleNamespace(
            x=x,
            fun=-x[-1],
            success=mode != "solver_failure",
            nit=2,
            status=8 if mode == "solver_failure" else 0,
            message="forced trial",
        )

    monkeypatch.setattr(solver, "minimize", fake)
    solution = solve_local_nbi(problem, [0.5, 0.5], [NBIStart(np.zeros(2), 0.0, "forced")])
    assert not solution.accepted and solution.point is solution.t is None
    assert len(solution.trials) == 1 and not solution.trials[0].accepted


def test_deterministic_retry_then_success_and_nearest_continuation(monkeypatch):
    from cnbi_v2.nbi import solver

    problem = quadratic_problem()
    original = solver.minimize
    calls = []

    def fail_once(*args, **kwargs):
        result = original(*args, **kwargs)
        if not calls:
            result.success = False
            result.message = "forced first-attempt failure"
        calls.append(1)
        return result

    monkeypatch.setattr(solver, "minimize", fail_once)
    lattice = simplex_lattice(3, 2)
    result = solve_nbi_lattice(problem, lattice)
    assert sum(s.accepted for s in result.solutions) == 6
    assert len(result.solutions[result.processing_order[0]].trials) == 2
    assert result.processing_order[:3] == (0, 2, 5)
    assert result.solutions[1].trials[0].start.kind.startswith("NEAREST_WEIGHT:")
    assert_array_equal(lattice.weights, simplex_lattice(3, 2).weights)
    # Same inputs yield same solutions and processing order, excluding wall-clock time.
    repeated = solve_nbi_lattice(problem, lattice)
    assert result.processing_order == repeated.processing_order
    assert_allclose(
        [s.point for s in result.solutions], [s.point for s in repeated.solutions], atol=1e-11
    )


def test_bad_problem_weight_start_and_options_are_rejected():
    problem = linear_problem()
    for data in [
        dict(anchors=np.zeros((1, 2))),
        dict(radius=0),
        dict(radius=True),
        dict(anchors=np.full((2, 2), 10)),
        dict(anchors=np.zeros((2, 2))),
    ]:
        with pytest.raises(ValueError):
            replace(problem, **data)
    for weights in ([0.2, 0.2], [-1, 2], [1, 0, 0]):
        with pytest.raises(ValueError, match="beta"):
            solve_local_nbi(problem, weights, [NBIStart(np.zeros(2), 0.0, "invalid")])
    for starts in ([], [NBIStart(np.ones(3), 0.0, "wrong")]):
        with pytest.raises(ValueError, match="starts"):
            solve_local_nbi(problem, [0.5, 0.5], starts)
    with pytest.raises(ValueError, match="lattice k"):
        solve_nbi_lattice(problem, simplex_lattice(3, 2))
    with pytest.raises(ValueError):
        NBIStart(np.ones((1, 2)), 0.0, "invalid")
    with pytest.raises(ValueError):
        NBIStart(np.ones(2), np.nan, "invalid")
    for data in [
        dict(ftol=0),
        dict(maxiter=0),
        dict(maxiter=True),
        dict(ftol=True),
        dict(equality_tolerance=np.inf),
        dict(retry_neighbours=0),
    ]:
        with pytest.raises(ValueError):
            NBIOptions(**data)
