"""Deterministic subset normalization and a unit CHIM normal toward the ideal."""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.chim import PayoffNormalization, centered_chim, nominal_normalization
from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.optimization import Direction
from cnbi_v2.optimization.quadratic import immutable


@dataclass(frozen=True, slots=True)
class LocalNBIGeometry:
    normalization: PayoffNormalization
    vertices: FloatArray
    centered: FloatArray
    centroid: FloatArray
    normal: FloatArray
    singular_values: FloatArray
    rank_tolerance: float
    orthogonality_residual: float
    orientation_dot: float

    def __post_init__(self) -> None:
        for field in ("vertices", "centered", "centroid", "normal", "singular_values"):
            object.__setattr__(self, field, immutable(getattr(self, field)))


def local_nbi_geometry(
    payoff: ArrayLike,
    directions: Sequence[Direction],
    *,
    optimality_tolerance: ArrayLike | None = None,
) -> LocalNBIGeometry:
    """Normalization is computed from this local payoff, never a global row range."""
    normalization = nominal_normalization(
        payoff, directions, optimality_tolerance=optimality_tolerance
    )
    vertices = normalization.normalize(payoff)
    centered = centered_chim(vertices)
    left, singular, _ = np.linalg.svd(centered, full_matrices=True)
    k = len(vertices)
    rank_tolerance = float(singular[0] * k * np.finfo(float).eps)
    if singular[-2] <= rank_tolerance or singular[-1] > rank_tolerance:
        raise ValueError("local CHIM needs affine rank k-1 and a unique normal")
    normal = left[:, -1]
    centroid = vertices.mean(axis=1)
    numerical = 64 * k * np.finfo(float).eps
    dot = float(normal @ centroid)
    if abs(dot) <= numerical * max(1.0, float(np.linalg.norm(centroid))):
        raise ValueError("normal sign toward ideal is numerically ambiguous")
    if dot > 0:
        normal = -normal
    residual = float(np.linalg.norm(centered.T @ normal))
    if abs(float(np.linalg.norm(normal)) - 1) > numerical or residual > numerical * max(
        1.0, float(singular[0])
    ):
        raise ValueError("computed normal is not unit and orthogonal within numerical tolerance")
    return LocalNBIGeometry(
        normalization,
        vertices,
        centered,
        centroid,
        normal,
        singular,
        rank_tolerance,
        residual,
        float(normal @ centroid),
    )
