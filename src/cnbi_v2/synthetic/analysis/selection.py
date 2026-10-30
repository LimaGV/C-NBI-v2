"""Secondary subsets of real archived decisions; no repair or reference input."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cnbi_v2.nbi import nondominated_mask

from ..model import real_array
from ..pareto.selection import partial_fps, unique_indices


def equalized_indices(points: ArrayLike, raw_ids: ArrayLike, count: int) -> NDArray[np.int64]:
    """Return selected original row IDs; exact ties favor increasing raw IDs."""
    z = real_array(points, "native ND normalized objectives")
    ids = np.asarray(raw_ids)
    if (
        z.ndim != 2
        or not z.shape[1]
        or ids.ndim != 1
        or ids.dtype.kind not in "iu"
        or len(ids) != len(z)
        or len(set(map(int, ids))) != len(ids)
        or np.any(ids < 0)
        or isinstance(count, bool)
        or not isinstance(count, int)
        or not 0 <= count <= len(z)
    ):
        raise ValueError("unique nonnegative raw row IDs and valid K required")
    if count == 0:
        return np.empty(0, dtype=np.int64)
    order = np.argsort(ids, kind="stable")
    sorted_z = z[order]
    extremes = list(dict.fromkeys(map(int, np.argmin(sorted_z, axis=0))))[:count]
    selected = partial_fps(sorted_z, count, np.asarray(extremes, dtype=np.int64))
    return np.asarray(ids[order[selected]], dtype=np.int64)


def feasible_nd_indices(
    decisions: ArrayLike, normalized: ArrayLike, alpha: float, epsilon: float
) -> tuple[NDArray[np.bool_], NDArray[np.int64], NDArray[np.int64]]:
    x, z = real_array(decisions, "raw decisions"), real_array(normalized, "true responses")
    if (
        x.ndim != 2
        or z.ndim != 2
        or len(x) != len(z)
        or not x.shape[1]
        or not z.shape[1]
        or not np.isfinite(alpha)
        or alpha <= 0
        or not np.isfinite(epsilon)
        or epsilon < 0
    ):
        raise ValueError("aligned matrices, positive radius and nonnegative norm epsilon required")
    feasible = np.linalg.norm(x, axis=1) <= alpha + epsilon
    valid = np.flatnonzero(feasible)
    unique = valid[unique_indices(x[valid], 1e-12 * alpha)] if len(valid) else valid
    nd = (
        unique[nondominated_mask(z[unique], equality_tolerance=np.full(z.shape[1], 1e-12))]
        if len(unique)
        else unique
    )
    return feasible, unique, nd
