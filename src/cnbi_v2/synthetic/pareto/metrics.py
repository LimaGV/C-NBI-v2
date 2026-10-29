"""Validated p1 Euclidean indicators with explicit undefined-cardinality states."""

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.benchmark.metrics import gd_igd, matrix, spacing_sparsity

from .hypervolume import FixedHypervolume


def evaluate_metrics(
    points: ArrayLike, reference: ArrayLike, hv: FixedHypervolume
) -> dict[str, object]:
    a, r = matrix(points), matrix(reference)
    a = np.unique(a, axis=0)
    if a.shape[1] != r.shape[1] or a.shape[1] != hv.m:
        raise ValueError("indicator dimensions must match the fixed scenario")
    gd, igd = gd_igd(a, r)
    if len(a) >= 2:
        spacing, sparsity = spacing_sparsity(a)
        local_status = "DEFINED"
    else:
        spacing, sparsity, local_status = None, None, "UNDEFINED_FEWER_THAN_TWO_DISTINCT_POINTS"
    return dict(
        GD=gd,
        IGD=igd,
        Spacing=spacing,
        Sparsity=sparsity,
        local_density_status=local_status,
        **hv.estimate(a),
    )
