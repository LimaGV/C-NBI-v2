"""Fixed analytic evaluation normalization, isolated from noisy RSM search APIs."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from ..model import FloatArray, evaluate, frozen, real_array


@dataclass(frozen=True, slots=True)
class AnalyticalNormalization:
    ideal: FloatArray
    nadir: FloatArray

    def transform(self, values: ArrayLike) -> FloatArray:
        z = real_array(values, "true responses")
        if z.ndim != 2 or z.shape[1] != len(self.nadir):
            raise ValueError("response dimension does not match fixed analytic normalization")
        return (z - self.ideal) / (self.nadir - self.ideal)  # No clipping, including values >1.


def analytic_normalization(anchors: ArrayLike) -> AnalyticalNormalization:
    responses = evaluate(anchors, anchors)
    nadir = responses.max(axis=0)
    if np.any(nadir <= 0):
        raise ValueError("analytic Pareto response ranges must be strictly positive")
    return AnalyticalNormalization(frozen(np.zeros(len(nadir))), frozen(nadir))
