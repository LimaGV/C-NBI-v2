"""True isotropic squared distances; no fitted model or response transformation."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

type FloatArray = NDArray[np.float64]


def real_array(values: ArrayLike, name: str) -> FloatArray:
    raw = np.asarray(values)
    if raw.dtype.kind not in "iuf" or not np.isfinite(raw).all():
        raise ValueError(f"{name} must contain finite real numbers")
    return np.array(raw, dtype=np.float64, copy=True)


def evaluate(points: ArrayLike, anchors: ArrayLike) -> FloatArray:
    """Return (n_points,m): f_j(x)=sum_k (x_k-a_jk)**2, in original coordinates."""
    x = real_array(points, "points")
    a = real_array(anchors, "anchors")
    if x.ndim != 2 or a.ndim != 2 or x.shape[1] != a.shape[1] or min(a.shape) < 1:
        raise ValueError("points and anchors must be nonempty matrices with equal dimension")
    if len(x) == 0:
        raise ValueError("points must be nonempty")
    with np.errstate(over="raise", invalid="raise"):
        return np.sum((x[:, None, :] - a[None, :, :]) ** 2, axis=2)


def frozen(values: ArrayLike) -> FloatArray:
    result = real_array(values, "values")
    result.setflags(write=False)
    return result
