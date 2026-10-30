"""Two-front equalization: no third method can constrain the paired count."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ..model import real_array
from .selection import equalized_indices


def equalized_pair_indices(
    first: ArrayLike, first_raw_ids: ArrayLike, second: ArrayLike, second_raw_ids: ArrayLike
) -> tuple[int, NDArray[np.int64], NDArray[np.int64]]:
    a, b = real_array(first, "first native ND front"), real_array(second, "second native ND front")
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[1]:
        raise ValueError("two native ND matrices with matching objective dimensions required")
    count = min(len(a), len(b))
    return (
        count,
        equalized_indices(a, first_raw_ids, count),
        equalized_indices(b, second_raw_ids, count),
    )
