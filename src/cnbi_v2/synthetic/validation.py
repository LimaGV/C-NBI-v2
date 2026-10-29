"""Independent structural certificates; singular correlations are permitted."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from .domain import feasible
from .model import real_array


@dataclass(frozen=True, slots=True)
class AnchorCertificate:
    rank: int
    minimum_separation: float
    maximum_norm: float
    valid: bool


def certify_anchors(
    anchors: ArrayLike,
    alpha: float,
    separation_ratio: float = 1e-4,
    rank_rtol: float = 1e-10,
) -> AnchorCertificate:
    a = real_array(anchors, "anchors")
    if a.ndim != 2 or len(a) <= a.shape[1] or a.shape[1] < 1:
        raise ValueError("need more anchors than dimensions")
    if separation_ratio <= 0 or rank_rtol <= 0:
        raise ValueError("certificate tolerances must be positive")
    singular = np.linalg.svd(a - a.mean(axis=0), compute_uv=False)
    rank = int(np.sum(singular > rank_rtol * singular[0])) if singular[0] > 0 else 0
    i, j = np.triu_indices(len(a), 1)
    separation = float(np.min(np.linalg.norm(a[i] - a[j], axis=1)))
    maximum = float(np.max(np.linalg.norm(a, axis=1)))
    valid = feasible(a, alpha) and separation >= separation_ratio * alpha and rank == a.shape[1]
    return AnchorCertificate(rank, separation, maximum, valid)


@dataclass(frozen=True, slots=True)
class CorrelationCertificate:
    symmetry_error: float
    diagonal_error: float
    minimum_eigenvalue: float
    rank: int
    valid: bool


def certify_correlation(
    matrix: ArrayLike,
    nx: int,
    numerical_tolerance: float = 1e-10,
) -> CorrelationCertificate:
    r = real_array(matrix, "correlation")
    if r.ndim != 2 or r.shape[0] != r.shape[1] or len(r) <= nx + 1 or nx < 1:
        raise ValueError("correlation must have m>nx+1")
    symmetry = float(np.max(np.abs(r - r.T)))
    diagonal = float(np.max(np.abs(np.diag(r) - 1)))
    eigenvalue = float(np.linalg.eigvalsh(r).min())
    rank = int(np.linalg.matrix_rank(r, tol=numerical_tolerance))
    valid = (
        symmetry <= numerical_tolerance
        and diagonal <= numerical_tolerance
        and eigenvalue >= -numerical_tolerance
        and rank <= nx + 1
        and float(np.max(np.abs(r))) <= 1 + numerical_tolerance
    )
    return CorrelationCertificate(symmetry, diagonal, eigenvalue, rank, valid)
