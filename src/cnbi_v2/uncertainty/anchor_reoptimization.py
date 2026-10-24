"""Deterministic reoptimization of every sampled full-quadratic objective."""

from collections.abc import Sequence
from dataclasses import dataclass, fields

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cnbi_v2.model import quadratic_term_names
from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real
from cnbi_v2.optimization import (
    Direction,
    QuadraticResponse,
    SphereAnchor,
    payoff_matrix,
    quadratic_responses_from_coefficients,
    solve_quadratic_ball,
)


@dataclass(frozen=True, slots=True)
class AnchorFailure:
    replicate_id: int  # One-based, matching the public failure log.
    response: str
    failure_type: str
    failure_message: str


@dataclass(frozen=True, slots=True)
class AnchorEnsemble:
    anchors: FloatArray
    optimal_values: FloatArray
    payoffs: FloatArray
    norms: FloatArray
    solver_cases: NDArray[np.str_]
    locations: NDArray[np.str_]
    valid_anchors: NDArray[np.bool_]
    valid_payoffs: NDArray[np.bool_]
    certificates: FloatArray
    certificate_fields: tuple[str, ...]
    response_names: tuple[str, ...]
    directions: tuple[Direction, ...]
    radius: float
    failures: tuple[AnchorFailure, ...]

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, np.ndarray):
                frozen = np.frombuffer(value.tobytes(), dtype=value.dtype).reshape(value.shape)
                object.__setattr__(self, field.name, frozen)

    @property
    def attempted(self) -> int:
        return int(self.valid_anchors.size)

    @property
    def successful(self) -> int:
        return int(np.count_nonzero(self.valid_anchors))

    @property
    def failed(self) -> int:
        return self.attempted - self.successful


def _validate_anchor(
    model: QuadraticResponse, answer: SphereAnchor, radius: float, direction: Direction,
) -> tuple[str, FloatArray]:
    """Recompute the existing normalized global certificate, without relaxing it."""
    values = np.array([
        answer.objective, answer.norm, answer.multiplier, answer.objective_scale,
        answer.normalized_stationarity, answer.normalized_complementarity,
        answer.normalized_shifted_min_eigenvalue, answer.certificate_tolerance,
    ])
    if (not np.isfinite(values).all() or not np.isfinite(answer.point).all()
            or answer.point.shape != model.linear.shape or not answer.converged
            or answer.radius != radius or answer.direction != direction
            or answer.objective_scale <= 0 or answer.certificate_tolerance != 1e-10
            or not isinstance(answer.solution_case, str) or len(answer.solution_case) > 40):
        raise ValueError("invalid finite/convergence/shape/direction fields in anchor certificate")
    z = answer.point / radius
    scale = answer.objective_scale
    sign = direction.minimization_sign
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        raw_hessian = 2 * sign * model.quadratic * radius**2
        raw_gradient = sign * model.linear * radius
        expected_scale = max(float(np.max(np.abs(np.linalg.eigvalsh(raw_hessian)))),
                             float(np.linalg.norm(raw_gradient))) or 1.0
        hessian = raw_hessian / scale
        gradient = raw_gradient / scale
        multiplier = answer.multiplier * radius**2 / scale
        norm = float(np.linalg.norm(answer.point))
        z_norm_squared = float(z @ z)
        stationarity = float(np.linalg.norm(hessian @ z + gradient + multiplier * z))
        complementarity = abs(multiplier * (1 - z_norm_squared))
        minimum_eigenvalue = float(np.linalg.eigvalsh(hessian)[0] + multiplier)
    tolerance = answer.certificate_tolerance
    spectral_tolerance = np.finfo(float).eps * 16 * len(z)  # Exact existing solver rule.
    if (abs(scale - expected_scale) > spectral_tolerance * expected_scale
            or z_norm_squared > 1 + tolerance or multiplier < 0
            or stationarity > tolerance or complementarity > tolerance
            or minimum_eigenvalue < -spectral_tolerance
            or answer.normalized_stationarity > tolerance
            or answer.normalized_complementarity > tolerance
            or answer.normalized_shifted_min_eigenvalue < -spectral_tolerance
            or model.value(answer.point) != answer.objective
            or abs(norm - answer.norm) > spectral_tolerance * radius):
        raise ValueError("independent global feasibility/KKT/PSD/value certificate failed")
    # The existing certificate bounds normalized squared norm by 1+tol.
    # radius*tol is a conservative radial equivalent, not a new fitted threshold.
    radial_tolerance = radius * tolerance
    location = "BOUNDARY" if abs(norm - radius) <= radial_tolerance else "INTERIOR"
    return location, np.array([stationarity, complementarity, minimum_eigenvalue,
                               multiplier, z_norm_squared, tolerance])


def reoptimize_coefficient_ensemble(
    samples: ArrayLike,
    n_factors: int,
    directions: Sequence[Direction],
    radius: float,
    *,
    response_names: Sequence[str] | None = None,
) -> AnchorEnsemble:
    """Every replica/response is solved afresh, with no RNG, RC or fallback.

    Failures retain their original indices and NaN payloads with explicit masks.
    A payoff is available only when all that replica's anchors are certified.
    No reduced-ensemble summary is silently computed here.
    """
    n_terms = len(quadratic_term_names(n_factors))
    coefficients = _as_finite_real(samples, "samples")
    if (coefficients.ndim != 3 or coefficients.shape[0] == 0
            or coefficients.shape[1] != n_terms or coefficients.shape[2] == 0):
        raise ValueError("samples must have nonempty shape (B,full quadratic terms,responses)")
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("radius must be finite and positive")
    count, _, m = coefficients.shape
    orientations = tuple(Direction(d) for d in directions)
    names = (tuple(f"response_{j}" for j in range(m)) if response_names is None
             else tuple(response_names))
    if (len(orientations) != m or len(names) != m
            or any(not isinstance(name, str) or not name.strip() for name in names)
            or len(set(names)) != m):
        raise ValueError("directions and unique response names must match the response dimension")
    anchors = np.full((count, m, n_factors), np.nan)
    optimum = np.full((count, m), np.nan)
    norms = np.full((count, m), np.nan)
    payoffs = np.full((count, m, m), np.nan)
    cases = np.full((count, m), "FAILED", dtype="U40")
    locations = np.full((count, m), "FAILED", dtype="U8")
    valid = np.zeros((count, m), dtype=np.bool_)
    valid_payoffs = np.zeros(count, dtype=np.bool_)
    certificates = np.full((count, m, 6), np.nan)
    failures = []
    for b in range(count):
        models = quadratic_responses_from_coefficients(coefficients[b], n_factors)
        for j, (model, direction) in enumerate(zip(models, orientations, strict=True)):
            stage = "SOLVER_EXCEPTION"
            try:
                answer = solve_quadratic_ball(model, radius, direction)  # Defaults unchanged.
                stage = "INVALID_CERTIFICATE"
                location, certificate = _validate_anchor(model, answer, radius, direction)
            except Exception as error:
                failures.append(AnchorFailure(b + 1, names[j], stage,
                                              f"{type(error).__name__}: {error}"))
                continue
            anchors[b, j] = answer.point
            optimum[b, j] = answer.objective
            norms[b, j] = answer.norm
            cases[b, j] = answer.solution_case
            locations[b, j] = location
            certificates[b, j] = certificate
            valid[b, j] = True
        if valid[b].all():
            try:
                payoff = payoff_matrix(models, anchors[b])
                if (not np.isfinite(payoff).all()
                        or not np.array_equal(np.diag(payoff), optimum[b])):
                    raise ValueError("payoff must be finite with diagonal exactly equal to optima")
                payoffs[b] = payoff
                valid_payoffs[b] = True
            except Exception as error:
                failures.append(AnchorFailure(b + 1, "ALL_RESPONSES", "PAYOFF_FAILURE",
                                              f"{type(error).__name__}: {error}"))
    return AnchorEnsemble(
        anchors, optimum, payoffs, norms, cases, locations, valid, valid_payoffs, certificates,
        ("stationarity", "complementarity", "shifted_min_eigenvalue", "normalized_multiplier",
         "normalized_norm_squared", "certificate_tolerance"),
        names, orientations, radius, tuple(failures),
    )
