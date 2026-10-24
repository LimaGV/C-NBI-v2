"""Nested-prefix moment diagnostics only; no PA or scientific stopping rule."""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.model.quadratic_design import _as_finite_real

from .coefficient_sampling import CoefficientEnsemble, _integer


def coefficient_checkpoints() -> tuple[int, ...]:
    """The explicit Phase 3 methodological schedule, not a fitted parameter."""
    return tuple(range(100, 2001, 100))


@dataclass(frozen=True, slots=True)
class PrefixMomentDiagnostics:
    B: int
    mean_relative_frobenius_error: float
    covariance_relative_frobenius_error: float | None
    covariance_status: str


def mc_prefix_sensitivity(
    ensemble: CoefficientEnsemble,
    *,
    checkpoints: Sequence[int] | None = None,
    theoretical_covariance: ArrayLike | None = None,
    mean_norm_floor: float = float(np.finfo(float).eps),
) -> tuple[PrefixMomentDiagnostics, ...]:
    """Compare nested prefix means and unbiased column-vec empirical covariances.

    No monotonicity or early stop is assumed. A zero theoretical covariance has
    an undefined relative covariance error, represented by None and its status.
    """
    points = coefficient_checkpoints() if checkpoints is None else tuple(checkpoints)
    validated = tuple(_integer(n, "checkpoint", 2) for n in points)
    if (not validated or tuple(sorted(set(validated))) != validated
            or validated[-1] > ensemble.n_samples):
        raise ValueError("checkpoints must be nonempty, increasing, unique and within the ensemble")
    if not np.isfinite(mean_norm_floor) or mean_norm_floor <= 0:
        raise ValueError("mean_norm_floor must be finite and positive")
    p, m = ensemble.coefficient_shape
    target = (
        np.kron(ensemble.effective_residual_covariance, ensemble.design_covariance)
        if theoretical_covariance is None
        else _as_finite_real(theoretical_covariance, "theoretical_covariance")
    )
    if target.shape != (p * m, p * m):
        raise ValueError("theoretical_covariance must match the column-vec coefficient dimension")
    records = []
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        mean_denominator = max(float(np.linalg.norm(ensemble.coefficient_mean)), mean_norm_floor)
        covariance_denominator = float(np.linalg.norm(target))
        for n in validated:
            prefix = ensemble.samples[:n]
            mean_error = float(np.linalg.norm(prefix.mean(axis=0) - ensemble.coefficient_mean)
                               / mean_denominator)
            # This is each sample.reshape(-1,order='F'), with replicas retained.
            vectors = prefix.transpose(0, 2, 1).reshape(n, p * m)
            centered = vectors - vectors.mean(axis=0)
            empirical = centered.T @ centered / (n - 1)
            error = (float(np.linalg.norm(empirical - target) / covariance_denominator)
                     if covariance_denominator else None)
            if not np.isfinite(mean_error) or (error is not None and not np.isfinite(error)):
                raise FloatingPointError("nonfinite computed Monte Carlo diagnostic")
            records.append(PrefixMomentDiagnostics(
                n, mean_error, error,
                "OK" if error is not None else "ZERO_THEORETICAL_COVARIANCE",
            ))
    return tuple(records)
