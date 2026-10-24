"""Local NBI SLSQP with exact derivatives and independently checked acceptance."""

from collections.abc import Sequence
from dataclasses import dataclass
from time import perf_counter

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import minimize  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real
from cnbi_v2.optimization import QuadraticResponse, evaluate_responses
from cnbi_v2.optimization.quadratic import immutable
from cnbi_v2.simplex import SimplexLattice
from cnbi_v2.simplex.lattice import positive_integer

from .geometry import LocalNBIGeometry


@dataclass(frozen=True, slots=True)
class NBIOptions:
    ftol: float = 1e-11
    maxiter: int = 1000
    equality_tolerance: float = 1e-4
    sphere_tolerance: float = 1e-9
    retry_neighbours: int = 3

    def __post_init__(self) -> None:
        values = [self.ftol, self.equality_tolerance, self.sphere_tolerance]
        if (
            not np.isfinite(values).all()
            or min(values) <= 0
            or any(isinstance(v, bool) for v in values)
        ):
            raise ValueError("NBI tolerances must be finite and positive")
        positive_integer(self.maxiter, "maxiter")
        positive_integer(self.retry_neighbours, "retry_neighbours")


DEFAULT_OPTIONS = NBIOptions()


@dataclass(frozen=True, slots=True)
class LocalNBIProblem:
    models: tuple[QuadraticResponse, ...]
    geometry: LocalNBIGeometry
    anchors: FloatArray
    radius: float

    def __post_init__(self) -> None:
        points = _as_finite_real(self.anchors, "anchors")
        if (
            len(self.models) != len(self.geometry.vertices)
            or not self.models
            or points.shape != (len(self.models), len(self.models[0].linear))
            or any(m.linear.shape != self.models[0].linear.shape for m in self.models)
            or not np.isfinite(self.radius)
            or self.radius <= 0
            or isinstance(self.radius, bool)
        ):
            raise ValueError("NBI models, anchors, geometry and positive radius must agree")
        if np.any(np.sum(points**2, axis=1) > self.radius**2 + 1e-9):
            raise ValueError("nominal anchors must lie in the decision ball")
        predicted = np.column_stack([evaluate_responses(self.models, x) for x in points])
        payoff = self.geometry.normalization.nominal_payoff
        tolerance = 256 * np.finfo(float).eps * np.maximum(1.0, np.abs(payoff))
        if np.any(np.abs(predicted - payoff) > tolerance):
            raise ValueError("nominal model evaluations at anchors differ from local payoff")
        object.__setattr__(self, "anchors", immutable(points))

    @property
    def n_factors(self) -> int:
        return len(self.models[0].linear)

    def beta(self, weights: ArrayLike) -> FloatArray:
        values = _as_finite_real(weights, "beta")
        if (
            values.shape != (len(self.models),)
            or np.any(values < 0)
            or abs(float(values.sum()) - 1) > 64 * len(values) * np.finfo(float).eps
        ):
            raise ValueError("beta must be a nonnegative simplex weight vector")
        return values

    def normalized_values(self, point: ArrayLike) -> FloatArray:
        norm = self.geometry.normalization
        return (norm.signs * evaluate_responses(self.models, point) - norm.utopia) / norm.amplitudes

    def residual(self, variables: FloatArray, weights: FloatArray) -> FloatArray:
        result: FloatArray = (
            self.normalized_values(variables[:-1])
            - self.geometry.vertices @ weights
            - variables[-1] * self.geometry.normal
        )
        return result

    def equality_jacobian(self, variables: FloatArray) -> FloatArray:
        norm = self.geometry.normalization
        gradients = np.array([m.gradient(variables[:-1]) for m in self.models])
        return np.column_stack(
            [gradients * norm.signs[:, None] / norm.amplitudes[:, None], -self.geometry.normal]
        )

    def sphere_margin(self, variables: FloatArray) -> float:
        return float(self.radius**2 - variables[:-1] @ variables[:-1])

    def sphere_jacobian(self, variables: FloatArray) -> FloatArray:
        return np.concatenate([-2 * variables[:-1], np.zeros(1)])


@dataclass(frozen=True, slots=True)
class NBIStart:
    point: FloatArray
    t: float
    kind: str

    def __post_init__(self) -> None:
        values = _as_finite_real(self.point, "start point")
        if values.ndim != 1 or not np.isfinite(self.t):
            raise ValueError("NBI start must be finite")
        object.__setattr__(self, "point", immutable(values))


@dataclass(frozen=True, slots=True)
class NBITrial:
    point: FloatArray
    t: float
    sphere_margin: float
    eq_norm: float
    solver_success: bool
    accepted: bool
    iterations: int
    status: int
    message: str
    start: NBIStart

    def __post_init__(self) -> None:
        object.__setattr__(self, "point", immutable(self.point))


@dataclass(frozen=True, slots=True)
class NBISolution:
    point: FloatArray | None
    t: float | None
    trials: tuple[NBITrial, ...]

    @property
    def accepted(self) -> bool:
        return self.point is not None

    def __post_init__(self) -> None:
        if self.point is not None:
            object.__setattr__(self, "point", immutable(self.point))


def solve_local_nbi(
    problem: LocalNBIProblem,
    weights: ArrayLike,
    starts: Sequence[NBIStart],
    *,
    options: NBIOptions = DEFAULT_OPTIONS,
) -> NBISolution:
    beta = problem.beta(weights)
    if not starts or any(s.point.shape != (problem.n_factors,) for s in starts):
        raise ValueError("supply deterministic starts with the model factor dimension")
    objective_gradient = np.r_[np.zeros(problem.n_factors), -1.0]
    constraints = [
        {
            "type": "eq",
            "fun": lambda v: problem.residual(v, beta),
            "jac": problem.equality_jacobian,
        },
        {"type": "ineq", "fun": problem.sphere_margin, "jac": problem.sphere_jacobian},
    ]
    trials = []
    for start in starts:
        initial = np.r_[start.point, start.t]
        try:
            result = minimize(
                lambda v: -float(v[-1]),
                initial,
                jac=lambda v: objective_gradient,
                method="SLSQP",
                constraints=constraints,
                options={"ftol": options.ftol, "maxiter": options.maxiter},
            )
            candidate = np.asarray(result.x, dtype=float)
            if candidate.shape != initial.shape:
                raise ValueError("solver returned an invalid variable shape")
            finite = np.isfinite(candidate).all() and np.isfinite(result.fun)
            eq_norm = (
                float(np.linalg.norm(problem.residual(candidate, beta))) if finite else float("inf")
            )
            margin = problem.sphere_margin(candidate) if finite else float("-inf")
            finite = finite and np.isfinite([eq_norm, margin]).all()
            accepted = bool(
                result.success
                and finite
                and margin >= -options.sphere_tolerance
                and eq_norm <= options.equality_tolerance
            )
            trial = NBITrial(
                candidate[:-1],
                float(candidate[-1]),
                margin,
                eq_norm,
                bool(result.success),
                accepted,
                int(result.nit),
                int(result.status),
                str(result.message),
                start,
            )
        except (FloatingPointError, ValueError, OverflowError) as error:
            trial = NBITrial(
                np.full(problem.n_factors, np.nan),
                float("nan"),
                float("-inf"),
                float("inf"),
                False,
                False,
                0,
                -1,
                f"{type(error).__name__}: {error}",
                start,
            )
        trials.append(trial)
        if trial.accepted:
            return NBISolution(trial.point, trial.t, tuple(trials))
    return NBISolution(None, None, tuple(trials))


@dataclass(frozen=True, slots=True)
class LatticeNBIResult:
    solutions: tuple[NBISolution, ...]  # Original lexicographic parent-weight order.
    processing_order: tuple[int, ...]
    elapsed_seconds: FloatArray

    def __post_init__(self) -> None:
        object.__setattr__(self, "elapsed_seconds", immutable(self.elapsed_seconds))


def solve_nbi_lattice(
    problem: LocalNBIProblem,
    lattice: SimplexLattice,
    *,
    options: NBIOptions = DEFAULT_OPTIONS,
) -> LatticeNBIResult:
    """Vertices first, then lexicographic; warm-start ties use exact integer distance."""
    if lattice.k != len(problem.models):
        raise ValueError("lattice k must match local response count")
    vertices = np.count_nonzero(lattice.compositions, axis=1) == 1
    order = (*map(int, np.flatnonzero(vertices)), *map(int, np.flatnonzero(~vertices)))
    solved: dict[int, NBISolution] = {}
    accepted: list[int] = []
    elapsed = np.zeros(len(lattice.weights))
    for index in order:
        started = perf_counter()
        beta = lattice.weights[index]
        nearest = sorted(
            accepted,
            key=lambda j: (
                int(np.sum((lattice.compositions[j] - lattice.compositions[index]) ** 2)),
                j,
            ),
        )
        convex = NBIStart(beta @ problem.anchors, 0.0, "CONVEX_COMBINATION")
        proposals = []
        if nearest and not vertices[index]:
            first = solved[nearest[0]]
            assert first.point is not None and first.t is not None
            proposals.append(NBIStart(first.point, first.t, f"NEAREST_WEIGHT:{nearest[0]}"))
        proposals.append(convex)
        proposals.extend(NBIStart(x, 0.0, f"ANCHOR:{j}") for j, x in enumerate(problem.anchors))
        for j in nearest[: options.retry_neighbours]:
            result = solved[j]
            assert result.point is not None and result.t is not None
            proposals.append(NBIStart(result.point, result.t, f"NEAREST_WEIGHT:{j}"))
        starts: list[NBIStart] = []
        for proposal in proposals:
            if not any(
                np.array_equal(proposal.point, s.point) and proposal.t == s.t for s in starts
            ):
                starts.append(proposal)
        solution = solve_local_nbi(problem, beta, starts, options=options)
        solved[index] = solution
        if solution.accepted:
            accepted.append(index)
        elapsed[index] = perf_counter() - started
    return LatticeNBIResult(tuple(solved[j] for j in range(len(lattice.weights))), order, elapsed)
