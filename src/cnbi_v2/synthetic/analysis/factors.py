"""Descriptive orthogonal decomposition of the complete fixed 3x3x3 design."""

from itertools import combinations

import numpy as np
from numpy.typing import ArrayLike

from ..model import real_array


def factorial_decomposition(values: ArrayLike) -> list[dict[str, object]]:
    y = real_array(values, "paired-contrast factorial cube")
    if y.shape != (3, 3, 3):
        raise ValueError("complete 3x3x3 cube required; no imputation of missing cells")
    grand = float(y.mean())
    components: dict[tuple[int, ...], np.ndarray] = {}
    rows: list[dict[str, object]] = []
    total = float(np.sum((y - grand) ** 2))
    names = ("nx", "delta", "rho_target")
    for size in (1, 2, 3):
        for axes in combinations(range(3), size):
            other = tuple(a for a in range(3) if a not in axes)
            component = y.mean(axis=other, keepdims=True) - grand
            for subset, previous in components.items():
                if set(subset).issubset(axes):
                    component = component - previous
            components[axes] = component
            ss = float(np.sum(np.broadcast_to(component, y.shape) ** 2))
            rows.append(
                dict(
                    effect=":".join(names[i] for i in axes),
                    degrees_of_freedom=2**size,
                    sum_squares=ss,
                    total_sum_squares=total,
                    fraction_of_contrast_variation=ss / total if total > 0 else None,
                    causal_interpretation=False,
                )
            )
    return rows
