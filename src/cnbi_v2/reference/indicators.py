"""Signed MIN epsilon and Euclidean distances in one fixed normalized space."""

import numpy as np
from numpy.typing import ArrayLike
from scipy.spatial import cKDTree  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real


def pair(candidate: ArrayLike, target: ArrayLike) -> tuple[FloatArray, FloatArray]:
    a, b = (_as_finite_real(p, "indicator points") for p in (candidate, target))
    if (a.ndim != 2 or b.ndim != 2 or not len(a) or not len(b)
            or a.shape[1] == 0 or a.shape[1] != b.shape[1]):
        raise ValueError("indicators require nonempty matrices with matching objectives")
    return a, b


def distances(source: ArrayLike, target: ArrayLike) -> FloatArray:
    a, b = pair(source, target)
    return np.asarray(cKDTree(b).query(a, k=1, eps=0., workers=1)[0], dtype=np.float64)


def additive_epsilon(candidate: ArrayLike, target: ArrayLike) -> float:
    """max_b min_a max_i(a_i-b_i), including genuinely negative values.

    A nearest Euclidean candidate gives an upper bound for each target's minimum.
    Targets whose bound cannot increase the running maximum can be skipped exactly.
    No approximate nearest neighbor or epsilon-dominance is involved.
    """
    a, b = pair(candidate, target)
    _, nearest = cKDTree(a).query(b, k=1, eps=0., workers=1)
    upper = np.max(a[nearest]-b, axis=1)
    result = -np.inf
    for j in np.argsort(-upper, kind="stable"):
        if upper[j] <= result:
            continue
        value = np.inf
        for start in range(0, len(a), 4096):
            value = min(value, float(np.max(a[start:start+4096]-b[j], axis=1).min()))
        result = max(result, value)
    return float(result)


def diagnostics(candidate: ArrayLike, target: ArrayLike) -> dict[str, float]:
    forward, reverse = distances(candidate, target), distances(target, candidate)
    return {"GD_p1": float(forward.mean()), "IGD_p1": float(reverse.mean()),
            "hausdorff_candidate_to_reference": float(forward.max()),
            "hausdorff_reference_to_candidate": float(reverse.max()),
            "epsilon_plus_candidate_reference": additive_epsilon(candidate, target)}
