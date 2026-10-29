"""Stable identity and partial FPS in normalized true objective space."""

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.spatial import cKDTree  # type: ignore[import-untyped]

from ..model import real_array


def unique_indices(points: ArrayLike, tolerance: float) -> NDArray[np.int64]:
    x = real_array(points, "decisions")
    if x.ndim != 2 or not len(x) or not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("nonempty decisions and nonnegative identity tolerance required")
    pairs = cKDTree(x).query_pairs(tolerance, p=np.inf, eps=0, output_type="ndarray")
    neighbours: dict[int, list[int]] = {}
    for left, right in pairs:
        neighbours.setdefault(int(left), []).append(int(right))
    active = np.ones(len(x), dtype=bool)
    for i in range(len(x)):
        if active[i]:
            active[neighbours.get(i, [])] = False
    return np.flatnonzero(active).astype(np.int64)


def partial_fps(points: ArrayLike, count: int, forced: ArrayLike) -> NDArray[np.int64]:
    z = real_array(points, "normalized objectives")
    raw = np.asarray(forced)
    if (
        z.ndim != 2
        or not len(z)
        or isinstance(count, bool)
        or not isinstance(count, int)
        or not 1 <= count <= len(z)
        or raw.ndim != 1
        or raw.dtype.kind not in "iu"
        or not len(raw)
        or len(raw) > count
        or len(set(map(int, raw))) != len(raw)
        or np.any(raw < 0)
        or np.any(raw >= len(z))
    ):
        raise ValueError("valid FPS count and unique forced candidate IDs required")
    selected = np.zeros(len(z), dtype=bool)
    distances = np.full(len(z), np.inf)
    order = list(map(int, raw))
    for index in order:
        distances = np.minimum(distances, np.sum((z - z[index]) ** 2, axis=1))
        selected[index] = True
    distances[selected] = -np.inf
    while len(order) < count:
        index = int(np.argmax(distances))  # First original source ID breaks exact numeric ties.
        order.append(index)
        distances = np.minimum(distances, np.sum((z - z[index]) ** 2, axis=1))
        selected[index] = True
        distances[selected] = -np.inf
    return np.asarray(order, dtype=np.int64)
