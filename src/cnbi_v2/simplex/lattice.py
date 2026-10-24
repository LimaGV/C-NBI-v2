"""Weak integer compositions in ascending lexicographic order."""

from collections.abc import Iterator
from dataclasses import dataclass
from math import comb
from numbers import Integral

import numpy as np
from numpy.typing import NDArray

from cnbi_v2.model.quadratic_design import FloatArray


def positive_integer(value: object, name: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _compositions(total: int, size: int) -> Iterator[tuple[int, ...]]:
    if size == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for tail in _compositions(total - first, size - 1):
                yield (first, *tail)


@dataclass(frozen=True, slots=True)
class SimplexLattice:
    k: int
    H: int
    compositions: NDArray[np.int64]
    weights: FloatArray

    def __post_init__(self) -> None:
        for field in ("compositions", "weights"):
            values = getattr(self, field)
            object.__setattr__(
                self,
                field,
                np.frombuffer(values.tobytes(), dtype=values.dtype).reshape(values.shape),
            )


def simplex_lattice(k: int, H: int) -> SimplexLattice:
    size, resolution = positive_integer(k, "k", 2), positive_integer(H, "H")
    compositions = np.array(list(_compositions(resolution, size)), dtype=np.int64)
    if len(compositions) != comb(resolution + size - 1, size - 1):
        raise RuntimeError("integer composition count disagrees with stars-and-bars")
    return SimplexLattice(size, resolution, compositions, compositions.astype(float) / resolution)


def nested_indices(parent: SimplexLattice, H: int) -> NDArray[np.int64]:
    resolution = positive_integer(H, "H")
    if parent.H % resolution:
        raise ValueError("nested resolution must divide parent H exactly")
    multiplier = parent.H // resolution
    return np.flatnonzero(np.all(parent.compositions % multiplier == 0, axis=1))
