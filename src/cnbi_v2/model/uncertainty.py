"""Analytic plug-in uncertainty estimates for shared fitted coefficients."""

from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike

from .multivariate_rsm import RSMFit
from .quadratic_design import FloatArray, _as_finite_real, quadratic_design


def _point_design(result: RSMFit, point: ArrayLike) -> FloatArray:
    values = _as_finite_real(point, "point")
    if values.shape != (result.n_factors,):
        raise ValueError(f"point must have shape ({result.n_factors},)")
    return np.asarray(quadratic_design(values.reshape(1, -1))[0], dtype=np.float64)


def _quadratic_factor(result: RSMFit, contrast: FloatArray) -> float:
    projected = np.linalg.solve(result.design_r_factor.T, contrast)
    with np.errstate(over="raise", invalid="raise"):
        return float(projected @ projected)


def coefficient_covariance(result: RSMFit) -> FloatArray:
    """Estimated Cov(vec(B_hat)), column stacking / NumPy order='F'."""
    with np.errstate(over="raise", invalid="raise"):
        return np.asarray(
            np.kron(result.residual_covariance, result.xtx_covariance_factor), dtype=np.float64
        )


def coefficient_covariance_by_response(result: RSMFit, response_index: int) -> FloatArray:
    """Estimated coefficient covariance MSE_j V_X for zero-based response j."""
    if (
        isinstance(response_index, bool)
        or not isinstance(response_index, Integral)
        or not 0 <= response_index < result.n_responses
    ):
        raise ValueError("response_index must be an integer in [0, n_responses)")
    with np.errstate(over="raise", invalid="raise"):
        return result.mse_by_response[response_index] * result.xtx_covariance_factor


def prediction_leverage(result: RSMFit, point: ArrayLike) -> float:
    """Return h(x)=z(x)^T V_X z(x) via a QR solve and squared norm."""
    return _quadratic_factor(result, _point_design(result, point))


def mean_prediction_covariance(result: RSMFit, point: ArrayLike) -> FloatArray:
    """Estimated covariance of the fitted mean, h Sigma_hat_e (no 1+h)."""
    with np.errstate(over="raise", invalid="raise"):
        return prediction_leverage(result, point) * result.residual_covariance


def mean_prediction_variance(result: RSMFit, point: ArrayLike) -> FloatArray:
    """Estimated variance of each fitted mean, h MSE_j."""
    with np.errstate(over="raise", invalid="raise"):
        return prediction_leverage(result, point) * result.mse_by_response


def cross_prediction_leverage(result: RSMFit, point_a: ArrayLike, point_b: ArrayLike) -> float:
    """Return z_a^T V_X z_b; a cross leverage may be negative."""
    projected_a = np.linalg.solve(result.design_r_factor.T, _point_design(result, point_a))
    projected_b = np.linalg.solve(result.design_r_factor.T, _point_design(result, point_b))
    with np.errstate(over="raise", invalid="raise"):
        return float(projected_a @ projected_b)


def cross_prediction_covariance(
    result: RSMFit, point_a: ArrayLike, point_b: ArrayLike
) -> FloatArray:
    """Estimated cross covariance of means predicted with the same B_hat."""
    with np.errstate(over="raise", invalid="raise"):
        return cross_prediction_leverage(result, point_a, point_b) * result.residual_covariance


def difference_prediction_leverage(result: RSMFit, point_a: ArrayLike, point_b: ArrayLike) -> float:
    """Return (z_a-z_b)^T V_X (z_a-z_b), without subtracting marginal leverages."""
    contrast = _point_design(result, point_a) - _point_design(result, point_b)
    return _quadratic_factor(result, contrast)


def difference_prediction_covariance(
    result: RSMFit, point_a: ArrayLike, point_b: ArrayLike
) -> FloatArray:
    """Estimated covariance of the difference between two fitted means."""
    with np.errstate(over="raise", invalid="raise"):
        return difference_prediction_leverage(result, point_a, point_b) * result.residual_covariance
