"""Numerical decision duplicates, full-space nondominance and retained origins."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real
from cnbi_v2.nbi import canonical_decision_points, nondominated_mask
from cnbi_v2.optimization.quadratic import immutable


@dataclass(frozen=True, slots=True)
class Origin:
    family: str
    run_id: str
    source_id: str


@dataclass(frozen=True, slots=True)
class PointPool:
    x: FloatArray
    f: FloatArray
    z: FloatArray
    origins: tuple[tuple[Origin, ...], ...]

    def __post_init__(self) -> None:
        for name, columns in (("x", 3), ("f", 8), ("z", 8)):
            a = _as_finite_real(getattr(self, name), name)
            if a.shape != (len(self.origins), columns):
                raise ValueError("pool coordinate and origin dimensions disagree")
            object.__setattr__(self, name, immutable(a))
        if any(not group for group in self.origins):
            raise ValueError("each point requires an identifiable origin")

    def subset(self, indices: NDArray[np.int64] | NDArray[np.bool_]) -> "PointPool":
        selected = np.arange(len(self.x))[indices]
        return PointPool(self.x[indices], self.f[indices], self.z[indices],
                         tuple(self.origins[int(i)] for i in selected))


def front(pools: list[PointPool], x_tolerance: float, dominance_tolerance: FloatArray) -> PointPool:
    """Union, first representative at roundoff, then numerical MIN dominance."""
    if not pools:
        raise ValueError("a reference requires at least one retained pool")
    x, f, z = (np.concatenate([getattr(p, k) for p in pools]) for k in ("x", "f", "z"))
    groups = [group for p in pools for group in p.origins]
    representatives, canonical = canonical_decision_points(x, tolerance=x_tolerance)
    origins: dict[int, list[Origin]] = {int(i): [] for i in representatives}
    for i, group in enumerate(groups):
        origins[int(canonical[i])].extend(group)
    merged = PointPool(x[representatives], f[representatives], z[representatives],
                       tuple(tuple(dict.fromkeys(origins[int(i)])) for i in representatives))
    keep = nondominated_mask(merged.z, equality_tolerance=dominance_tolerance)
    return merged.subset(keep)
