"""Independent oracle diagnostics; never used to choose or repair fitted models."""

from dataclasses import dataclass
from itertools import combinations

import numpy as np
from numpy.typing import ArrayLike

from .design import Scenario
from .domain import sample_ball
from .model import FloatArray, evaluate, frozen, real_array
from .noise import stream_seed
from .rsm_generation import RSMInstance


@dataclass(frozen=True, slots=True)
class ExternalSample:
    seed: int
    points: FloatArray
    truth: FloatArray


def external_sample(scenario: Scenario, anchors: ArrayLike, master_seed: int) -> ExternalSample:
    """4096 fresh uniform-volume Sobol points, shared across the five replicas."""
    seed = stream_seed(master_seed, scenario.scenario_id, 0)
    points = sample_ball(scenario.nx, 12, seed)
    truth = evaluate(points, anchors)
    if truth.shape[1] != scenario.m:
        raise ValueError("external oracle response count differs from scenario")
    return ExternalSample(seed, frozen(points), frozen(truth))


def external_metrics(predictions: ArrayLike, truth: ArrayLike) -> FloatArray:
    """Columns are RMSE, MAE, external R², maximum absolute prediction error."""
    predicted = real_array(predictions, "predictions")
    actual = real_array(truth, "truth")
    if predicted.shape != actual.shape or actual.ndim != 2 or min(actual.shape) < 1:
        raise ValueError("predictions and truth must be nonempty equal-shaped matrices")
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        error = predicted - actual
        denominator = np.sum((actual - actual.mean(axis=0)) ** 2, axis=0)
        if np.any(denominator <= 0):
            raise ValueError("external truth must have positive variance")
        return np.column_stack(
            (
                np.sqrt(np.mean(error**2, axis=0)),
                np.mean(abs(error), axis=0),
                1 - np.sum(error**2, axis=0) / denominator,
                np.max(abs(error), axis=0),
            )
        )


def hessian_eigenvalues(coefficients: ArrayLike, nx: int) -> FloatArray:
    """Observed curvature only; no convexity constraint or coefficient correction."""
    values = real_array(coefficients, "coefficients")
    p = (nx + 1) * (nx + 2) // 2
    if nx not in (2, 3, 5) or values.ndim != 2 or values.shape[0] != p:
        raise ValueError("coefficient shape must match a supported full quadratic")
    hessians = np.zeros((values.shape[1], nx, nx))
    for k in range(nx):
        hessians[:, k, k] = 2 * values[1 + nx + k]
    for term, (k, other) in enumerate(combinations(range(nx), 2), start=1 + 2 * nx):
        hessians[:, k, other] = hessians[:, other, k] = values[term]
    return np.linalg.eigvalsh(hessians)


def covariance_diagnostics(instance: RSMInstance) -> dict[str, object]:
    covariance = instance.fit.residual_covariance
    eigenvalues = np.linalg.eigvalsh(covariance)
    rank = int(np.linalg.matrix_rank(covariance))
    m = instance.scenario.m
    return dict(
        residual_covariance_rank=rank,
        residual_covariance_min_eigenvalue=float(eigenvalues[0]),
        residual_covariance_max_eigenvalue=float(eigenvalues[-1]),
        residual_covariance_condition=float(np.linalg.cond(covariance)) if rank == m else None,
        residual_covariance_condition_status="DEFINED" if rank == m else "RANK_DEFICIENT",
        residual_covariance_regularized=False,
    )


def replica_prediction_spread(predictions: ArrayLike) -> dict[str, float]:
    values = real_array(predictions, "replica predictions")
    if values.ndim != 3 or values.shape[0] != 5 or min(values.shape[1:]) < 1:
        raise ValueError("predictions must have shape (5,n_test,m)")
    sd = np.std(values, axis=0, ddof=1)
    return dict(
        replica_prediction_sd_mean=float(sd.mean()), replica_prediction_sd_max=float(sd.max())
    )
