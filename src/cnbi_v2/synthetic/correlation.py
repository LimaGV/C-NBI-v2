"""Exact covariance algebra for the calibration sample; no OLS or regularization."""

import numpy as np
from numpy.typing import ArrayLike

from .model import FloatArray, real_array


def summaries(matrix: ArrayLike) -> tuple[float, float]:
    r = real_array(matrix, "correlation")
    if r.ndim != 2 or r.shape[0] != r.shape[1] or len(r) < 2:
        raise ValueError("correlation must be a square matrix with at least two responses")
    pairs = r[np.triu_indices(len(r), 1)]
    return float(np.mean(np.abs(pairs))), float(np.mean(pairs))


def feature_covariance(points: ArrayLike) -> FloatArray:
    x = real_array(points, "points")
    if x.ndim != 2 or len(x) < 2 or x.shape[1] < 1:
        raise ValueError("at least two point observations required")
    h = np.column_stack((np.sum(x * x, axis=1), x))
    return np.asarray(np.cov(h, rowvar=False, ddof=1), dtype=np.float64)


def from_feature_covariance(anchors: ArrayLike, covariance: ArrayLike) -> FloatArray:
    a = real_array(anchors, "anchors")
    c = real_array(covariance, "feature covariance")
    if a.ndim != 2 or len(a) < 2 or c.shape != (a.shape[1] + 1,) * 2:
        raise ValueError("incompatible anchor/covariance shapes")
    q = np.column_stack((np.ones(len(a)), -2 * a))
    response_cov = q @ c @ q.T
    variances = np.diag(response_cov)
    if np.any(variances <= 0):
        raise ValueError("positive response variances required")
    return np.asarray(response_cov / np.sqrt(np.outer(variances, variances)), dtype=np.float64)


def population_correlation(anchors: ArrayLike, alpha: float) -> FloatArray:
    a = real_array(anchors, "anchors")
    if a.ndim != 2 or min(a.shape) < 1 or not np.isfinite(alpha) or alpha <= 0:
        raise ValueError("anchors must be a matrix and alpha positive")
    nx = a.shape[1]
    c = nx * alpha**2 / ((nx + 4) * (nx + 2))
    v = c + np.sum(a * a, axis=1)
    return np.asarray((c + a @ a.T) / np.sqrt(np.outer(v, v)), dtype=np.float64)


def calibration_loss_gradient(
    unit_coordinates: FloatArray,
    m: int,
    nx: int,
    alpha: float,
    covariance: FloatArray,
    target: float,
) -> tuple[float, FloatArray]:
    """J=(mean_abs_rho-target)**2 and exact coordinate derivative (sign(0)=0)."""
    a = unit_coordinates.reshape(m, nx) * alpha
    q = np.column_stack((np.ones(m), -2 * a))
    cq = covariance @ q.T
    response_cov = q @ cq
    v = np.diag(response_cov)
    denominator = np.sqrt(np.outer(v, v))
    r = response_cov / denominator
    error = summaries(r)[0] - target
    gradient = np.zeros((m, nx))
    weight = 2 / (m * (m - 1))
    for k in range(m):
        indices = np.arange(m) != k
        derivatives = -2 * (
            cq[1:, indices].T / denominator[k, indices, None]
            - r[k, indices, None] * cq[1:, k] / v[k]
        )
        gradient[k] = weight * np.sum(np.sign(r[k, indices, None]) * derivatives, axis=0)
    return error**2, np.asarray((2 * error * alpha * gradient).ravel(), dtype=np.float64)
