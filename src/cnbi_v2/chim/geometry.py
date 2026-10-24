"""Centered vertex geometry; columns are vertices and rows are local responses."""

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real

from ._validation import frozen, integer


def centering_matrix(k: int) -> FloatArray:
    size = integer(k, "k", 2)
    return frozen(np.eye(size) - np.ones((size, size))/size)


def centered_chim(vertices: ArrayLike) -> FloatArray:
    values = _as_finite_real(vertices, "vertices")
    if values.ndim < 2 or values.shape[-1] < 2 or values.shape[-2] < 1:
        raise ValueError("vertices require at least one coordinate and two vertex columns")
    with np.errstate(over="raise", invalid="raise"):
        result = values @ centering_matrix(values.shape[-1])
    if not np.isfinite(result).all():
        raise FloatingPointError("nonfinite centered geometry")
    return frozen(result)


def vertex_differences(vertices: ArrayLike, reference: int = 0) -> FloatArray:
    """Rank-equivalent diagnostic; never the canonical PA spectrum."""
    values = _as_finite_real(vertices, "vertices")
    index = integer(reference, "reference", 0)
    if values.ndim != 2 or values.shape[1] < 2 or index >= values.shape[1]:
        raise ValueError("reference must index a 2D matrix with at least two vertices")
    columns = [j for j in range(values.shape[1]) if j != index]
    with np.errstate(over="raise", invalid="raise"):
        return frozen(values[:, columns] - values[:, index:index+1])


def chim_singular_values(vertices: ArrayLike) -> FloatArray:
    centered = centered_chim(vertices)
    k = centered.shape[-1]
    if centered.shape[-2] != k:
        raise ValueError("local CHIM spectra require k response rows and k anchor columns")
    singular = np.linalg.svd(centered, compute_uv=False)[..., :k-1]
    if not np.isfinite(singular).all() or np.any(singular < 0):
        raise FloatingPointError("invalid computed CHIM singular values")
    return frozen(singular)
