"""Experimental mean-centered response-cloud regions, separate from residual error."""

from dataclasses import dataclass
from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike
from scipy.stats import chi2  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real

from .quadratic import immutable


@dataclass(frozen=True, slots=True)
class ResponseRegion:
    center: FloatArray
    covariance: FloatArray
    cholesky: FloatArray
    eigenvalues: FloatArray
    rank: int
    condition_number: float
    log_determinant: float
    n_observations: int
    rank_relative_tolerance: float

    def __post_init__(self) -> None:
        for name in ("center", "covariance", "cholesky", "eigenvalues"):
            object.__setattr__(self, name, immutable(getattr(self, name)))

    def deviations(self, points: ArrayLike) -> FloatArray:
        values = _as_finite_real(points, "responses")
        if values.ndim != 2 or values.shape[1] != len(self.center):
            raise ValueError("response vectors must have shape (q,m)")
        return values - self.center

    def distances_squared(self, points: ArrayLike) -> FloatArray:
        deviations = self.deviations(points)
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            solved = np.linalg.solve(self.cholesky, deviations.T)
            return np.sum(solved * solved, axis=0)

    def distance_squared(self, point: ArrayLike) -> float:
        values = _as_finite_real(point, "response point")
        if values.shape != self.center.shape:
            raise ValueError("response point must have shape (m,)")
        return float(self.distances_squared(values[None, :])[0])

    def metric_gradient(self, point: ArrayLike) -> FloatArray:
        values = _as_finite_real(point, "response point")
        if values.shape != self.center.shape:
            raise ValueError("response point must have shape (m,)")
        first = np.linalg.solve(self.cholesky, values - self.center)
        return 2 * np.linalg.solve(self.cholesky.T, first)


def response_cloud_region(observations: ArrayLike) -> ResponseRegion:
    """Compute sample mean and S_Y (n-1); reject numerically singular covariance.

    Rank threshold is eps*max(n,m)*largest eigenvalue in the supplied units.
    No standardization, sign flip, pseudoinverse, response deletion or jitter.
    """
    y = _as_finite_real(observations, "observations")
    if y.ndim != 2 or y.shape[0] < 2 or y.shape[1] < 1:
        raise ValueError("observations must have nonempty shape (n>=2,m)")
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        offsets = y - y[0]
        center_offset = offsets.mean(axis=0)
        center = y[0] + center_offset
        deviations = offsets - center_offset
        covariance = deviations.T @ deviations / (len(y) - 1)
    eigenvalues = np.linalg.eigvalsh(covariance)
    relative_tolerance = float(np.finfo(float).eps * max(y.shape))
    rank = int(np.count_nonzero(eigenvalues > eigenvalues[-1] * relative_tolerance))
    if rank < y.shape[1] or eigenvalues[0] <= 0:
        raise np.linalg.LinAlgError("response-cloud covariance is singular or numerically unstable")
    cholesky = np.linalg.cholesky(covariance)
    return ResponseRegion(center, covariance, cholesky, eigenvalues, rank,
                          float(eigenvalues[-1] / eigenvalues[0]),
                          float(2 * np.log(np.diag(cholesky)).sum()), len(y), relative_tolerance)


def legacy_chi_square_threshold(n_responses: int, nominal_coverage: float = 0.95) -> float:
    """Experimental legacy cutoff only, not exact finite-sample confidence."""
    if (isinstance(n_responses, bool) or not isinstance(n_responses, Integral)
            or n_responses < 1 or not 0 < nominal_coverage < 1):
        raise ValueError("positive integer response dimension and coverage in (0,1) required")
    return float(chi2.ppf(nominal_coverage, n_responses))
