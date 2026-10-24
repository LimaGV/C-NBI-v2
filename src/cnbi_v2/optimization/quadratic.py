"""Natural-orientation full quadratic response functions."""

from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.model import RSMFit, quadratic_term_names
from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real


def immutable(values: FloatArray) -> FloatArray:
    return np.frombuffer(values.tobytes(), dtype=np.float64).reshape(values.shape)


class Direction(StrEnum):
    MIN = "MIN"
    MAX = "MAX"

    @property
    def minimization_sign(self) -> int:
        """Explicit solver conversion only; observed Y/covariance never change."""
        return 1 if self is Direction.MIN else -1


@dataclass(frozen=True, slots=True)
class QuadraticResponse:
    intercept: float
    linear: FloatArray
    quadratic: FloatArray

    def __post_init__(self) -> None:
        linear = _as_finite_real(self.linear, "linear")
        matrix = _as_finite_real(self.quadratic, "quadratic")
        if (not np.isfinite(self.intercept) or linear.ndim != 1 or len(linear) == 0
                or matrix.shape != (len(linear), len(linear))):
            raise ValueError("quadratic requires finite intercept, vector b and square Q")
        if not np.array_equal(matrix, matrix.T):
            raise ValueError("Q must be symmetric; interactions occupy half in each off-diagonal")
        object.__setattr__(self, "linear", immutable(linear))
        object.__setattr__(self, "quadratic", immutable(matrix))

    def point(self, point: ArrayLike) -> FloatArray:
        values = _as_finite_real(point, "point")
        if values.shape != self.linear.shape:
            raise ValueError("point must match the factor dimension")
        return values

    def value(self, point: ArrayLike) -> float:
        x = self.point(point)
        with np.errstate(over="raise", invalid="raise"):
            return float(self.intercept + self.linear @ x + x @ self.quadratic @ x)

    def gradient(self, point: ArrayLike) -> FloatArray:
        x = self.point(point)
        with np.errstate(over="raise", invalid="raise"):
            return self.linear + 2 * self.quadratic @ x


def quadratic_responses(fit: RSMFit) -> tuple[QuadraticResponse, ...]:
    """Extract beta0,b,Q from the unchanged canonical coefficient order."""
    return quadratic_responses_from_coefficients(fit.coefficients, fit.n_factors)


def quadratic_responses_from_coefficients(
    coefficients: ArrayLike, n_factors: int,
) -> tuple[QuadraticResponse, ...]:
    """The same canonical extraction for fitted or sampled coefficient matrices."""
    n_terms = len(quadratic_term_names(n_factors))
    values = _as_finite_real(coefficients, "coefficients")
    if values.ndim != 2 or values.shape[0] != n_terms or values.shape[1] == 0:
        raise ValueError("coefficients must have shape (full quadratic terms, responses)")
    n = n_factors
    models = []
    for j in range(values.shape[1]):
        beta = values[:, j]
        matrix = np.diag(beta[1 + n:1 + 2 * n])
        for index, (a, b) in enumerate(combinations(range(n), 2), start=1 + 2 * n):
            matrix[a, b] = matrix[b, a] = beta[index] / 2
        models.append(QuadraticResponse(float(beta[0]), beta[1:1 + n], matrix))
    return tuple(models)
