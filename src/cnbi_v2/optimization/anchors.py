"""Deterministic local response-region anchors and oriented payoff matrices."""

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import product

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import minimize  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real

from .quadratic import Direction, QuadraticResponse, immutable
from .response_region import ResponseRegion
from .trust_region import solve_quadratic_ball


def evaluate_responses(models: Sequence[QuadraticResponse], point: ArrayLike) -> FloatArray:
    return np.array([model.value(point) for model in models], dtype=np.float64)


def payoff_matrix(models: Sequence[QuadraticResponse], anchor_points: ArrayLike) -> FloatArray:
    """A[i,j]=f_i(x_anchor_j): rows responses, columns anchors, same order."""
    points = _as_finite_real(anchor_points, "anchor points")
    if (not models or points.ndim != 2 or points.shape != (len(models), len(models[0].linear))):
        raise ValueError("payoff requires one anchor per response, with matching factor dimension")
    return immutable(np.column_stack([evaluate_responses(models, point) for point in points]))


def deterministic_ball_starts(n_factors: int, radius: float) -> FloatArray:
    """Origin and all nonzero ternary directions, at half and full radius.

    These are proposals only; feasibility is independently checked by the RC
    solver. No random generator or seed is used. Intended for small DOE models.
    """
    if isinstance(n_factors, bool) or not isinstance(n_factors, int) or n_factors < 1:
        raise ValueError("n_factors must be a positive integer")
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("radius must be finite and positive")
    rows = [np.zeros(n_factors)]
    for coordinates in product((-1.0, 0.0, 1.0), repeat=n_factors):
        vector = np.array(coordinates)
        norm = float(np.linalg.norm(vector))
        if norm:
            rows.extend([radius * fraction * vector / norm for fraction in (0.5, 1.0)])
    return np.array(rows)


def classify_response_distance(distance: float, threshold: float, tolerance: float) -> str:
    if (not np.isfinite([distance, threshold, tolerance]).all()
            or distance < 0 or threshold <= 0 or tolerance < 0):
        raise ValueError("finite nonnegative distance/tolerance and positive threshold required")
    if abs(threshold - distance) <= tolerance:
        return "BOUNDARY_NEAR"
    return "INSIDE_RESPONSE_REGION" if distance < threshold else "OUTSIDE_RESPONSE_REGION"


@dataclass(frozen=True, slots=True)
class RCOptions:
    ftol: float = 1e-11
    maxiter: int = 1000
    sphere_tolerance: float = 1e-9
    response_tolerance: float = 1e-8
    active_tolerance: float = 1e-6

    def __post_init__(self) -> None:
        tolerances = [self.ftol, self.sphere_tolerance,
                      self.response_tolerance, self.active_tolerance]
        if (not np.isfinite(tolerances).all() or min(tolerances) <= 0
                or isinstance(self.maxiter, bool) or not isinstance(self.maxiter, int)
                or self.maxiter < 1):
            raise ValueError("RC tolerances and integer maxiter must be finite and positive")


_DEFAULT_RC_OPTIONS = RCOptions()


@dataclass(frozen=True, slots=True)
class RCTrial:
    start: FloatArray
    point: FloatArray
    objective: float
    distance_squared: float
    sphere_margin: float
    response_margin: float
    solver_success: bool
    solver_status: int
    solver_message: str
    iterations: int
    accepted: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "start", immutable(self.start))
        object.__setattr__(self, "point", immutable(self.point))


@dataclass(frozen=True, slots=True)
class ResponseRegionAnchor:
    point: FloatArray
    objective: float
    direction: Direction
    norm: float
    sphere_margin: float
    distance_squared: float
    response_margin: float
    sphere_boundary_active: bool
    response_boundary_active: bool
    global_optimum_certified: bool
    solver: str
    trials: tuple[RCTrial, ...]
    feasible_starts: FloatArray
    rejected_start_indices: tuple[int, ...]
    objective_scale: float
    options: RCOptions

    def __post_init__(self) -> None:
        object.__setattr__(self, "point", immutable(self.point))
        object.__setattr__(self, "feasible_starts", immutable(self.feasible_starts))


def solve_response_region_anchor(
    models: Sequence[QuadraticResponse],
    objective_index: int,
    direction: Direction,
    radius: float,
    region: ResponseRegion,
    threshold: float,
    starts: ArrayLike,
    *,
    options: RCOptions = _DEFAULT_RC_OPTIONS,
) -> ResponseRegionAnchor:
    """Best feasible converged SLSQP result found; no general global claim.

    A feasible certified sphere optimum is already a global RC optimum, and is
    reused exactly. Otherwise all supplied feasible unique starts are run.
    Both actual margins are verified separately from solver success.
    """
    direction = Direction(direction)
    if (not models or not 0 <= objective_index < len(models)
            or len(models) != len(region.center)):
        raise ValueError("models, objective index and response-region dimension must agree")
    model = models[objective_index]
    if any(len(m.linear) != len(model.linear) for m in models):
        raise ValueError("all quadratic models must have the same factor dimension")
    if not np.isfinite(threshold) or threshold <= 0:
        raise ValueError("threshold must be finite and positive")
    proposed = _as_finite_real(starts, "starts")
    if proposed.ndim != 2 or proposed.shape[1] != len(model.linear):
        raise ValueError("starts must have shape (q,n_factors)")
    sphere = solve_quadratic_ball(model, radius, direction)

    def margins(x: FloatArray) -> tuple[float, float, float]:
        distance = region.distance_squared(evaluate_responses(models, x))
        return radius**2 - float(x @ x), threshold - distance, distance

    feasible, rejected, seen = [], [], set()
    for i, point in enumerate(proposed):
        gs, gr, _ = margins(point)
        key = tuple(float(x) for x in point)
        if (gs >= -options.sphere_tolerance and gr >= -options.response_tolerance
                and key not in seen):
            feasible.append(point)
            seen.add(key)
        else:
            rejected.append(i)
    feasible_array = np.array(feasible, dtype=np.float64).reshape(-1, len(model.linear))
    gs, gr, distance = margins(sphere.point)
    scale = max(abs(model.intercept), float(np.linalg.norm(model.linear)) * radius,
                float(np.linalg.norm(model.quadratic, ord=2)) * radius**2)
    if scale == 0:
        scale = 1.0
    if gr >= 0:  # No tolerance needed for the exact feasible-subset argument.
        trial = RCTrial(sphere.point, sphere.point, sphere.objective, distance, gs, gr,
                        True, 0, "Certified sphere optimum is response-region feasible", 0, True)
        return ResponseRegionAnchor(
            sphere.point, sphere.objective, direction, sphere.norm, gs, distance, gr,
            abs(gs) <= options.active_tolerance, abs(gr) <= options.active_tolerance,
            True, "SPHERE_GLOBAL_CERTIFICATE", (trial,), feasible_array,
            tuple(rejected), scale, options,
        )
    if len(feasible_array) == 0:
        raise ValueError("no feasible deterministic start; global infeasibility is not proved")

    def objective(x: FloatArray) -> float:
        return direction.minimization_sign * model.value(x) / scale

    def jacobian(x: FloatArray) -> FloatArray:
        return direction.minimization_sign * model.gradient(x) / scale

    def constraint(x: FloatArray) -> FloatArray:
        sphere_margin, response_margin, _ = margins(x)
        return np.array([sphere_margin / radius**2, response_margin / threshold])

    def constraint_jacobian(x: FloatArray) -> FloatArray:
        predicted = evaluate_responses(models, x)
        gradients = np.stack([m.gradient(x) for m in models])
        response_gradient = gradients.T @ region.metric_gradient(predicted)
        return np.vstack([-2 * x / radius**2, -response_gradient / threshold])

    trials = []
    for start in feasible_array:
        result = minimize(objective, start, jac=jacobian, method="SLSQP",
                          constraints={"type": "ineq", "fun": constraint,
                                       "jac": constraint_jacobian},
                          options={"ftol": options.ftol, "maxiter": options.maxiter})
        point = np.array(result.x, dtype=np.float64)
        if not np.isfinite(point).all():
            raise FloatingPointError("nonfinite RC solver output")
        gs, gr, distance = margins(point)
        accepted = (bool(result.success) and gs >= -options.sphere_tolerance
                    and gr >= -options.response_tolerance)
        trials.append(RCTrial(start, point, model.value(point), distance, gs, gr,
                              bool(result.success), int(result.status), str(result.message),
                              int(result.nit), accepted))
    accepted_trials = [trial for trial in trials if trial.accepted]
    if not accepted_trials:
        raise RuntimeError("no converged RC solution passed both independent feasibility checks")
    best = min(accepted_trials, key=lambda trial: direction.minimization_sign * trial.objective)
    return ResponseRegionAnchor(
        best.point, best.objective, direction, float(np.linalg.norm(best.point)),
        best.sphere_margin, best.distance_squared, best.response_margin,
        abs(best.sphere_margin) <= options.active_tolerance,
        abs(best.response_margin) <= options.active_tolerance, False,
        "SLSQP_DETERMINISTIC_MULTISTART_BEST_FOUND", tuple(trials), feasible_array,
        tuple(rejected), scale, options,
    )
