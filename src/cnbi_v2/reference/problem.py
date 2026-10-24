"""One immutable nominal coded RSM problem for every reference family."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real
from cnbi_v2.optimization import evaluate_responses, quadratic_responses_from_coefficients
from cnbi_v2.optimization.quadratic import immutable


@dataclass(frozen=True, slots=True)
class CanonicalProblem:
    coefficients: FloatArray
    signs: FloatArray
    utopia: FloatArray
    amplitudes: FloatArray
    alpha: float
    sphere_tolerance: float = 1e-9

    def __post_init__(self) -> None:
        b = _as_finite_real(self.coefficients, "coefficients")
        if (b.shape != (10, 8) or not np.isfinite(self.alpha) or self.alpha <= 0
                or self.sphere_tolerance < 0 or not np.isfinite(self.sphere_tolerance)):
            raise ValueError("canonical turning problem needs10x8 coefficients and positive radius")
        for name in ("coefficients", "signs", "utopia", "amplitudes"):
            values = _as_finite_real(getattr(self, name), name)
            if name != "coefficients" and values.shape != (8,):
                raise ValueError("response normalization vectors must have eight entries")
            object.__setattr__(self, name, immutable(values))
        if np.any(self.amplitudes <= 0) or not np.isin(self.signs, [-1., 1.]).all():
            raise ValueError("need positive amplitudes and explicit MIN/MAX signs")

    def points(self, points: ArrayLike) -> FloatArray:
        x = _as_finite_real(points, "points")
        if x.ndim != 2 or x.shape[1] != 3:
            raise ValueError("decisions must be an N-by-3 matrix")
        return x

    def feasible(self, points: ArrayLike) -> np.ndarray[tuple[int, ...], np.dtype[np.bool_]]:
        x = self.points(points)
        return np.sum(x*x, axis=1) <= self.alpha**2+self.sphere_tolerance

    def natural(self, points: ArrayLike, *, scalar_check: bool = False) -> FloatArray:
        x = self.points(points)
        if scalar_check:
            models = quadratic_responses_from_coefficients(self.coefficients, 3)
            return np.array([evaluate_responses(models, row) for row in x]).reshape(-1, 8)
        design = np.column_stack([np.ones(len(x)), x, x*x,
                                  x[:, 0]*x[:, 1], x[:, 0]*x[:, 2], x[:, 1]*x[:, 2]])
        return design@self.coefficients

    def normalize(self, natural: ArrayLike) -> FloatArray:
        values = _as_finite_real(natural, "natural responses")
        if values.ndim != 2 or values.shape[1] != 8:
            raise ValueError("natural responses must have eight columns")
        return (values*self.signs-self.utopia)/self.amplitudes


def radial_repair(points: ArrayLike, alpha: float) -> FloatArray:
    x = _as_finite_real(points, "repair points").copy()
    if x.ndim != 2 or x.shape[1] != 3 or not np.isfinite(alpha) or alpha <= 0:
        raise ValueError("radial repair needs N-by-3 points and a positive radius")
    norm = np.linalg.norm(x, axis=1)
    outside = norm > alpha
    x[outside] *= (alpha/norm[outside])[:, None]
    # Correct representational overshoot only, after the prescribed radial map.
    for _ in range(3):
        norm = np.linalg.norm(x, axis=1)
        outside = norm > alpha
        if not outside.any():
            return x
        x[outside] *= (np.nextafter(alpha, 0.)/norm[outside])[:, None]
    raise FloatingPointError("radial projection failed numerical feasibility")
