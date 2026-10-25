"""V1 corrected applied metric definitions, in one global MIN normalization."""

import numpy as np
from numpy.typing import ArrayLike
from scipy.spatial import cKDTree  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real
from cnbi_v2.reference.indicators import distances


def matrix(value: ArrayLike) -> FloatArray:
    a = _as_finite_real(value, "objective matrix")
    if a.ndim != 2 or not len(a) or not a.shape[1]:
        raise ValueError("need a nonempty objective matrix")
    return a


def nearest_distances(points: ArrayLike) -> FloatArray:
    a = matrix(points)
    if len(a) < 2:
        raise ValueError("Spacing/Sparsity require at least two genuine points")
    return np.asarray(cKDTree(a).query(a, k=2, eps=0.0, workers=1)[0][:, 1], dtype=float)


def spacing_sparsity(points: ArrayLike) -> tuple[float, float]:
    """Corrected applied V1 uses sample SD (ddof1), not earlier ddof0."""
    d = nearest_distances(points)
    return float(np.std(d, ddof=1)), float(d.mean())


def gd_igd(points: ArrayLike, reference: ArrayLike) -> tuple[float, float]:
    return float(distances(points, reference).mean()), float(distances(reference, points).mean())


def summary(values: ArrayLike) -> dict[str, float | int | None]:
    a = _as_finite_real(values, "summary")
    if a.ndim != 1 or not len(a):
        raise ValueError("summary needs a nonempty vector")
    q = np.quantile(a, [0.05, 0.25, 0.5, 0.75, 0.95], method="linear")
    return {
        "n": len(a),
        "mean": float(a.mean()),
        "median": float(q[2]),
        "SD": float(a.std(ddof=1)) if len(a) > 1 else None,
        "IQR": float(q[3] - q[1]),
        "q05": float(q[0]),
        "q95": float(q[4]),
        "min": float(a.min()),
        "max": float(a.max()),
    }
