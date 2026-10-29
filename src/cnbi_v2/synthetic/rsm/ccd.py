"""Conventional full rotatable CCD; the training region is not the feasible ball."""

from dataclasses import dataclass
from itertools import product

import numpy as np

from ..domain import radius
from ..model import FloatArray, frozen


@dataclass(frozen=True, slots=True)
class CCD:
    points: FloatArray
    kinds: tuple[str, ...]
    inside_ball: tuple[bool, ...]
    alpha: float


def full_ccd(nx: int) -> CCD:
    """Lexicographic factorials, axes k ascending (-,+), then five centers."""
    alpha = radius(nx)
    factorial = np.array(list(product((-1.0, 1.0), repeat=nx)))
    axial = np.zeros((2 * nx, nx))
    for k in range(nx):
        axial[2 * k, k], axial[2 * k + 1, k] = -alpha, alpha
    points = np.vstack((factorial, axial, np.zeros((5, nx))))
    kinds = ("factorial",) * len(factorial) + ("axial",) * (2 * nx) + ("center",) * 5
    inside = tuple(bool(v) for v in (np.linalg.norm(points, axis=1) <= alpha))
    return CCD(frozen(points), kinds, inside, alpha)
