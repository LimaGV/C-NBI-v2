"""Uniform-volume ball samples from a fixed scrambled Sobol digital net."""

from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike
from scipy.special import ndtri  # type: ignore[import-untyped]
from scipy.stats import qmc  # type: ignore[import-untyped]

from .design import DIMENSIONS
from .model import FloatArray, real_array


def radius(nx: int) -> float:
    if isinstance(nx, bool) or not isinstance(nx, Integral) or nx not in DIMENSIONS:
        raise ValueError("nx must be 2,3 or5")
    return float(2.0 ** (nx / 4.0))


def feasible(points: ArrayLike, alpha: float) -> bool:
    x = real_array(points, "points")
    if x.ndim != 2 or min(x.shape) < 1 or not np.isfinite(alpha) or alpha <= 0:
        raise ValueError("nonempty points and positive finite alpha required")
    return bool(np.all(np.linalg.norm(x, axis=1) <= alpha))


def sample_ball(nx: int, power: int, seed: int) -> FloatArray:
    """N=2**power, directions from normal quantiles, radial CDF (r/alpha)**nx.

    A half-grid offset places all32-bit digital coordinates in the open unit
    interval, without clipping/dropping/resampling any Sobol point.
    """
    alpha = radius(nx)
    if (
        isinstance(power, bool)
        or not isinstance(power, Integral)
        or not 4 <= power <= 24
        or isinstance(seed, bool)
        or not isinstance(seed, Integral)
        or seed < 0
    ):
        raise ValueError("power must be4..24 and seed a nonnegative integer")
    engine = qmc.Sobol(
        nx + 1, scramble=True, bits=32, rng=np.random.Generator(np.random.PCG64(seed))
    )
    unit = engine.random_base2(int(power)) + 2.0**-33
    directions = np.asarray(ndtri(unit[:, :nx]), dtype=np.float64)
    lengths = np.linalg.norm(directions, axis=1)
    if np.any(lengths == 0) or not np.isfinite(directions).all():
        raise FloatingPointError("nonfinite or zero normal direction")
    result = (directions / lengths[:, None]) * (alpha * unit[:, -1] ** (1 / nx))[:, None]
    if not feasible(result, alpha):
        raise FloatingPointError("ball sampling produced an infeasible point")
    return np.asarray(result, dtype=np.float64)
