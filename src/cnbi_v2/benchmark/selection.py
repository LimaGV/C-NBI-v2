"""One deterministic extreme-preserving maximin ordering per genuine front."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cnbi_v2.simplex.lattice import positive_integer

from .metrics import matrix


def farthest_order(points: ArrayLike) -> NDArray[np.int64]:
    a = matrix(points)
    # Stable archived row/source ID breaks every exact numeric tie.
    extremes = list(dict.fromkeys(map(int, np.argmin(a, axis=0))))
    order = extremes.copy()
    selected = np.zeros(len(a), dtype=bool)
    selected[extremes] = True
    d = np.full(len(a), np.inf)
    for i in extremes:
        d = np.minimum(d, np.sum((a - a[i]) ** 2, axis=1))
    d[selected] = -np.inf
    while len(order) < len(a):
        i = int(np.argmax(d))
        order.append(i)
        selected[i] = True
        d = np.minimum(d, np.sum((a - a[i]) ** 2, axis=1))
        d[selected] = -np.inf
    return np.array(order, dtype=np.int64)


def seed_subsamples(
    r: int, *, count: int, rng: np.random.Generator, total: int = 30
) -> NDArray[np.int64]:
    from math import comb

    positive_integer(r, "runs")
    positive_integer(count, "subsamples")
    if r > total or count > comb(total, r):
        raise ValueError("not enough distinct seed subsets")
    chosen: dict[tuple[int, ...], None] = {}
    while len(chosen) < count:
        key = tuple(sorted(map(int, rng.choice(total, r, replace=False))))
        chosen.setdefault(key, None)
    return np.array(list(chosen), dtype=np.int64)
