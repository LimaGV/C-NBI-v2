"""Full quadratic basis in explicit, untransformed factor coordinates."""

from itertools import combinations
from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike, NDArray

type FloatArray = NDArray[np.float64]


def _as_finite_real(values: ArrayLike, name: str) -> FloatArray:
    """Copy numeric input to float64 without silently discarding imaginary parts."""
    raw = np.asarray(values)
    if raw.dtype.kind not in "iuf":
        raise ValueError(f"{name} must contain real numeric values")
    with np.errstate(over="raise", invalid="raise"):
        result = np.array(raw, dtype=np.float64, copy=True)
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite values")
    return result


def quadratic_term_names(n_factors: int) -> tuple[str, ...]:
    """Name intercept, linears, squares, then lexicographic i<j interactions."""
    if isinstance(n_factors, bool) or not isinstance(n_factors, Integral) or n_factors < 1:
        raise ValueError("n_factors must be a positive integer")
    names = tuple(f"x{i + 1}" for i in range(n_factors))
    return (
        "intercept",
        *names,
        *(f"{name}^2" for name in names),
        *(f"{a}*{b}" for a, b in combinations(names, 2)),
    )


def quadratic_design(factors: ArrayLike) -> FloatArray:
    """Return an (n,p) design for real factors (n,n_x), including one row.

    No implicit coding, centering, scaling, or input mutation is performed.
    Empty designs and polynomial overflow fail explicitly.
    """
    values = _as_finite_real(factors, "factors")
    if values.ndim != 2 or min(values.shape) == 0:
        raise ValueError("factors must have nonempty shape (n_observations, n_factors)")
    with np.errstate(over="raise", invalid="raise"):
        columns = [np.ones(values.shape[0]), *values.T, *(values * values).T]
        columns.extend(
            values[:, i] * values[:, j] for i, j in combinations(range(values.shape[1]), 2)
        )
        return np.column_stack(columns)
