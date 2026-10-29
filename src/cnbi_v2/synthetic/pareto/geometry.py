"""Unperturbed convex hull geometry and explicitly identified sampling fallbacks."""

import hashlib
from dataclasses import dataclass
from itertools import combinations
from math import factorial

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.spatial import ConvexHull, QhullError  # type: ignore[import-untyped]
from scipy.stats import qmc  # type: ignore[import-untyped]

from ..model import FloatArray, frozen, real_array


def seed_for(master: int, key: str, role: str) -> int:
    if isinstance(master, bool) or not isinstance(master, int) or master < 0 or not key or not role:
        raise ValueError("nonnegative integer master and nonempty stream identifiers required")
    message = f"C-NBI-v2/phase10c/v1/{master}/{key}/{role}".encode()
    return int.from_bytes(hashlib.sha256(message).digest()[:16], "big")


def unit_sobol(dimension: int, power: int, seed: int) -> FloatArray:
    if (
        isinstance(power, bool)
        or not isinstance(power, int)
        or not 1 <= power <= 24
        or isinstance(seed, bool)
        or not isinstance(seed, int)
        or seed < 0
    ):
        raise ValueError("valid Sobol exponent and seed required")
    engine = qmc.Sobol(
        dimension, scramble=True, bits=32, rng=np.random.Generator(np.random.PCG64(seed))
    )
    return np.asarray(engine.random_base2(power) + 2.0**-33, dtype=np.float64)


def simplex_weights(unit: FloatArray) -> FloatArray:
    """Sorted uniform spacings: uniform volume in a nondegenerate simplex."""
    n = len(unit)
    return np.diff(np.column_stack((np.zeros(n), np.sort(unit, axis=1), np.ones(n))), axis=1)


@dataclass(frozen=True, slots=True)
class HullGeometry:
    anchors: FloatArray
    facets: NDArray[np.int64]
    equations: FloatArray
    cone_volumes: FloatArray
    facet_areas: FloatArray
    volume: float | None
    condition: float
    method: str
    limitation: str


def hull_geometry(anchors: ArrayLike) -> HullGeometry:
    a = real_array(anchors, "anchors")
    if a.ndim != 2 or a.shape[1] not in (2, 3, 5) or a.shape[0] <= a.shape[1]:
        raise ValueError("anchors must span a supported-dimensional convex hull")
    centered = a - a.mean(axis=0)
    singular = np.linalg.svd(centered, compute_uv=False)
    if np.linalg.matrix_rank(centered) < a.shape[1]:
        raise ValueError("anchor geometry is rank deficient; do not perturb anchors")
    condition = float(singular[0] / singular[-1])
    nx = a.shape[1]
    try:
        hull = ConvexHull(a, qhull_options="Qc Qx")  # Qt is always enabled; no QJ.
        facets = np.asarray(sorted(map(tuple, np.sort(hull.simplices, axis=1))), dtype=np.int64)
        center = a.mean(axis=0)
        volumes = np.abs(np.linalg.det(a[facets] - center)) / factorial(nx)
        faces = a[facets[:, 1:]] - a[facets[:, 0, None]]
        areas = np.prod(np.linalg.svd(faces, compute_uv=False), axis=1) / factorial(nx - 1)
        relative_error = abs(float(volumes.sum()) - float(hull.volume)) / float(hull.volume)
        if np.any(volumes <= 0) or np.any(areas <= 0) or relative_error > 1e-8:
            raise ValueError(f"coned triangulation volume audit failed: {relative_error}")
        return HullGeometry(
            frozen(a),
            facets,
            frozen(hull.equations),
            frozen(volumes),
            frozen(areas),
            float(hull.volume),
            condition,
            "CONED_HULL_UNIFORM_VOLUME",
            "none",
        )
    except (QhullError, ValueError) as exc:
        # All n_x-anchor subsimplices include every triangulable hull facet,
        # but their mixture is explicitly NOT uniform surface/volume sampling.
        facets = np.asarray(list(combinations(range(len(a)), nx)), dtype=np.int64)
        return HullGeometry(
            frozen(a),
            facets,
            frozen(np.empty((0, nx + 1))),
            frozen(np.empty(0)),
            frozen(np.ones(len(facets))),
            None,
            condition,
            "BARYCENTRIC_STRATA_NONUNIFORM_FALLBACK",
            str(exc),
        )


def sample_hull_weights(
    geometry: HullGeometry, power: int, seed: int, *, boundary: bool = False
) -> FloatArray:
    m, nx = geometry.anchors.shape
    if geometry.volume is None and not boundary:
        unit = unit_sobol(m, power, seed)
        exp = -np.log(unit)
        return exp / exp.sum(axis=1, keepdims=True)
    probabilities = geometry.facet_areas if boundary else geometry.cone_volumes
    cdf = np.cumsum(probabilities / probabilities.sum())
    cdf[-1] = 1.0  # Numerical CDF endpoint, not a geometric modification.
    unit = unit_sobol(nx if boundary else nx + 1, power, seed)
    face = geometry.facets[np.searchsorted(cdf, unit[:, 0], side="right")]
    beta = simplex_weights(unit[:, 1:])
    weights = (
        np.zeros((len(unit), m)) if boundary else np.repeat((beta[:, 0] / m)[:, None], m, axis=1)
    )
    offset = 0 if boundary else 1
    for k in range(nx):
        weights[np.arange(len(unit)), face[:, k]] += beta[:, k + offset]
    return weights
