"""Small validation helpers for immutable CHIM results."""

from numbers import Integral
from typing import cast

import numpy as np
from numpy.typing import NDArray


def frozen[Scalar: np.generic](values: NDArray[Scalar]) -> NDArray[Scalar]:
    return cast(NDArray[Scalar], np.frombuffer(values.tobytes(), dtype=values.dtype)
                .reshape(values.shape))


def integer(value: object, name: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)
