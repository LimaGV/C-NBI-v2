"""Global full quadratic optima on a ball, with spectral KKT certificates."""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray

from .quadratic import Direction, QuadraticResponse, immutable


@dataclass(frozen=True, slots=True)
class SphereAnchor:
    point: FloatArray
    objective: float
    direction: Direction
    radius: float
    norm: float
    sphere_margin: float
    boundary_active: bool
    solution_case: str
    multiplier: float
    normalized_stationarity: float
    normalized_complementarity: float
    normalized_shifted_min_eigenvalue: float
    objective_scale: float
    iterations: int
    certificate_tolerance: float
    converged: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "point", immutable(self.point))


def solve_quadratic_ball(
    model: QuadraticResponse,
    radius: float,
    direction: Direction,
    *,
    certificate_tolerance: float = 1e-10,
) -> SphereAnchor:
    """Solve min/max beta0+b'x+x'Qx over ||x||<=radius globally.

    z=x/radius, then positive objective normalization, only improves numerical
    scale. Spectral nullspace handling is specific to the TRS hard case, never
    a covariance pseudoinverse. See individual_anchors.md for the certificate.
    """
    direction = Direction(direction)
    if (not np.isfinite(radius) or radius <= 0
            or not np.isfinite(certificate_tolerance) or certificate_tolerance <= 0):
        raise ValueError("radius and certificate_tolerance must be finite and positive")
    sign = direction.minimization_sign
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        hessian = 2 * sign * model.quadratic * radius**2
        gradient = sign * model.linear * radius
        scale = max(float(np.linalg.norm(hessian, ord=2)), float(np.linalg.norm(gradient)))
    if scale == 0:
        scale = 1.0
    hessian, gradient = hessian / scale, gradient / scale
    eigenvalues, vectors = np.linalg.eigh(hessian)
    projected = vectors.T @ gradient
    lower = max(0.0, -float(eigenvalues[0]))
    shifted = eigenvalues + lower
    tolerance = np.finfo(float).eps * 16 * len(gradient)
    null = shifted <= tolerance
    base = np.zeros_like(projected)
    base[~null] = -projected[~null] / shifted[~null]
    base_norm = float(np.linalg.norm(base))
    iterations = 0
    if np.linalg.norm(projected[null]) <= tolerance and base_norm <= 1:
        multiplier = lower
        if lower == 0:
            z = vectors @ base
            case = "INTERIOR_OR_PSD_MINIMUM_NORM"
        else:
            # Deterministic direction in the minimum-eigenvalue eigenspace.
            index = int(np.flatnonzero(null)[0])
            v = vectors[:, index]
            orientation = 1 if v[np.argmax(np.abs(v))] >= 0 else -1
            base[index] = orientation * np.sqrt(max(0.0, 1 - base_norm**2))
            z = vectors @ base
            case = "BOUNDARY_HARD_CASE"
    else:
        def secular(delta: float) -> float:
            if delta == 0 and np.any(projected[null] != 0):
                return float("inf")  # Exact limiting norm at the singular endpoint.
            denominator = shifted + delta
            terms = np.divide(projected, denominator, out=np.zeros_like(projected),
                              where=denominator != 0)
            return float(np.linalg.norm(terms) - 1)

        upper = float(np.linalg.norm(projected))
        if secular(upper) == 0:
            delta = upper
        else:
            delta, info = brentq(secular, 0.0, upper, xtol=np.finfo(float).tiny,
                                rtol=8 * np.finfo(float).eps, maxiter=256, full_output=True)
            iterations = int(info.iterations)
        multiplier = lower + float(delta)
        z = vectors @ (-projected / (shifted + delta))
        case = "BOUNDARY_SECULAR"
    norm = float(np.linalg.norm(z))
    stationarity = float(np.linalg.norm(hessian @ z + gradient + multiplier * z))
    complementarity = abs(multiplier * (1 - norm**2))
    min_eigenvalue = float(eigenvalues[0] + multiplier)
    certified = (
        np.isfinite(z).all() and norm**2 <= 1 + certificate_tolerance
        and stationarity <= certificate_tolerance
        and complementarity <= certificate_tolerance
        and min_eigenvalue >= -tolerance and multiplier >= 0
    )
    if not certified:
        raise np.linalg.LinAlgError("quadratic-ball global KKT/PSD certificate failed")
    point = radius * z
    return SphereAnchor(
        point, model.value(point), direction, radius, radius * norm,
        radius**2 * (1 - norm**2), abs(1 - norm**2) <= certificate_tolerance,
        case, multiplier * scale / radius**2, stationarity, complementarity,
        min_eigenvalue, scale, iterations, certificate_tolerance, True,
    )
