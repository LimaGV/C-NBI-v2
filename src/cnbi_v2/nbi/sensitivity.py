"""Internal H diagnostics in one fixed full-response normalization."""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.spatial.distance import cdist  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real
from cnbi_v2.simplex.lattice import positive_integer


def _points(points: ArrayLike) -> FloatArray:
    values = _as_finite_real(points, "points")
    if values.ndim != 2 or values.shape[1] == 0:
        raise ValueError("points must be a finite observation-by-coordinate matrix")
    return values


def canonical_decision_points(
    points: ArrayLike,
    *,
    tolerance: float,
) -> tuple[NDArray[np.int64], NDArray[np.int64]]:
    """First representative within L-infinity roundoff; no transitive clustering."""
    values = _points(points)
    if isinstance(tolerance, bool) or not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("deduplication tolerance must be finite and nonnegative")
    representatives: list[int] = []
    canonical = np.empty(len(values), dtype=np.int64)
    for j, point in enumerate(values):
        matching = np.flatnonzero(
            np.all(np.abs(values[representatives] - point) <= tolerance, axis=1)
        )
        if len(matching):
            canonical[j] = representatives[int(matching[0])]
        else:
            representatives.append(j)
            canonical[j] = j
    return np.asarray(representatives, dtype=np.int64), canonical


def nondominated_mask(
    points: ArrayLike,
    *,
    equality_tolerance: ArrayLike | None = None,
    block_size: int = 128,
) -> NDArray[np.bool_]:
    """Minimization; only coordinate differences inside a numerical bound are equal."""
    values = _points(points)
    block = positive_integer(block_size, "block_size")
    if not len(values):
        return np.empty(0, dtype=np.bool_)
    tolerance = (
        64 * np.finfo(float).eps * np.maximum(1.0, np.max(np.abs(values), axis=0))
        if equality_tolerance is None
        else _as_finite_real(equality_tolerance, "equality_tolerance")
    )
    if tolerance.shape != (values.shape[1],) or np.any(tolerance < 0):
        raise ValueError("equality_tolerance must be a nonnegative coordinate vector")
    keep = np.ones(len(values), dtype=np.bool_)
    for start in range(0, len(values), block):
        difference = values[None, :, :] - values[start : start + block, None, :]
        no_worse = np.all(difference <= tolerance, axis=2)
        better = np.any(difference < -tolerance, axis=2)
        keep[start : start + block] = ~np.any(no_worse & better, axis=1)
    return keep


def directed_coverage_distances(
    source: ArrayLike,
    target: ArrayLike,
    *,
    block_size: int = 256,
) -> FloatArray:
    """Euclidean distance from each source point to its nearest target point."""
    left, right = _points(source), _points(target)
    block = positive_integer(block_size, "block_size")
    if left.shape[1] != right.shape[1] or not len(right):
        raise ValueError("coverage needs matching coordinates and a nonempty target")
    distances = np.empty(len(left))
    for start in range(0, len(left), block):
        distances[start : start + block] = cdist(
            left[start : start + block], right, metric="euclidean"
        ).min(axis=1)
    return distances
