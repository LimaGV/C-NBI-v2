"""Fixed analytic HV box, efficient exact indicators and explicit precision states."""

from dataclasses import dataclass
from itertools import combinations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cnbi_v2.benchmark.hypervolume import HVGrid
from cnbi_v2.benchmark.metrics import matrix

from ..model import FloatArray
from .geometry import seed_for


@dataclass(slots=True)
class _Node:
    lower: FloatArray
    upper: FloatArray
    points: FloatArray | None
    left: "_Node | None" = None
    right: "_Node | None" = None


def _tree(points: FloatArray) -> _Node:
    low, high = points.min(axis=0), points.max(axis=0)
    if len(points) <= 32 or np.array_equal(low, high):
        return _Node(low, high, points[:1] if np.array_equal(low, high) else points)
    axis = int(np.argmax(high - low))
    order = np.argsort(points[:, axis], kind="stable")
    mid = len(points) // 2
    return _Node(low, high, None, _tree(points[order[:mid]]), _tree(points[order[mid:]]))


def orthant_hits(points: ArrayLike, samples: ArrayLike) -> NDArray[np.bool_]:
    """Exactly the same finite-set indicator as OR of historical HVGrid masks."""
    a, u = matrix(points), matrix(samples)
    if a.shape[1] != u.shape[1]:
        raise ValueError("HV point/sample dimensions differ")
    hit = np.zeros(len(u), dtype=bool)

    def walk(node: _Node, ids: NDArray[np.int64]) -> None:
        ids = ids[~hit[ids]]
        if not len(ids):
            return
        ids = ids[np.all(u[ids] >= node.lower, axis=1)]
        if not len(ids):
            return
        all_hit = np.all(u[ids] >= node.upper, axis=1)
        hit[ids[all_hit]] = True
        ids = ids[~all_hit]
        if node.points is not None:
            for start in range(0, len(ids), 1024):
                block = ids[start : start + 1024]
                hit[block] = np.any(
                    np.all(node.points[:, None, :] <= u[block][None, :, :], axis=2), axis=0
                )
        else:
            assert node.left is not None and node.right is not None
            walk(node.left, ids)
            walk(node.right, ids)

    walk(_tree(a), np.arange(len(u), dtype=np.int64))
    return hit


def exact_small_union(points: ArrayLike) -> tuple[float, float]:
    """Inclusion-exclusion of <=8 boxes, independently auditable roundoff bound."""
    a = matrix(points)
    if len(a) > 8 or np.any(a < 0) or np.any(a >= 1.1):
        raise ValueError("exact branch requires 1..8 eligible nonnegative points")
    terms = []
    for count in range(1, len(a) + 1):
        sign = 1 if count % 2 else -1
        for ids in combinations(range(len(a)), count):
            terms.append(sign * float(np.prod(1.1 - np.max(a[list(ids)], axis=0))))
    # Sum in extended precision where supported; final artifacts remain float64.
    value = float(np.sum(np.asarray(terms, dtype=np.longdouble)))
    bound = float(64 * np.finfo(float).eps * np.sum(np.abs(terms)))
    return value, bound


@dataclass(frozen=True, slots=True)
class FixedHypervolume:
    m: int
    master_seed: int = 20261029
    power: int = 16

    def __post_init__(self) -> None:
        _ = self.grid  # Validate the common protocol even when the exact branch is used.

    @property
    def grid(self) -> HVGrid:
        if (
            isinstance(self.power, bool)
            or not isinstance(self.power, int)
            or not 13 <= self.power <= 20
        ):
            raise ValueError("HV study exponent must be13..20")
        if isinstance(self.m, bool) or not isinstance(self.m, int) or self.m < 2:
            raise ValueError("HV requires at least two objective coordinates")
        seeds = tuple(
            seed_for(self.master_seed, f"hv_m{self.m}", f"scramble_{r}") for r in range(4)
        )
        return HVGrid(np.zeros(self.m), np.full(self.m, 1.1), self.power, seeds)

    def study(self, points: ArrayLike) -> list[dict[str, object]]:
        a = matrix(points)
        if a.shape[1] != self.m or np.any(a < 0):
            raise ValueError(
                "HV requires true nonnegative normalized responses of matching dimension"
            )
        eligible = a[np.all(a < 1.1, axis=1)]
        grid = self.grid
        if len(eligible):
            hits = orthant_hits(eligible, grid.samples())
        else:
            hits = np.zeros(4 * 2**self.power, dtype=bool)
        packed = np.packbits(hits, bitorder="little")
        rows = []
        previous: float | None = None
        for power in range(13, self.power + 1):
            estimates = grid.values(packed, power=power)
            mean = float(estimates.mean())
            se = float(estimates.std(ddof=1) / 2)
            quantum = grid.volume / 2**power
            counts = np.rint(estimates / quantum).astype(np.int64)
            relative_se = se / mean if mean > 0 else None
            relative_change = (
                abs(mean - previous) / mean if mean > 0 and previous is not None else None
            )
            if not len(eligible):
                status = "ZERO_CONTRIBUTION_CERTIFIED"
            elif mean == 0 or np.any(counts == 0):
                status = "UNRESOLVED_ZERO_HITS"
            elif (
                counts.min() < 128
                or relative_se is None
                or relative_se > 0.02
                or quantum / mean > 0.01
                or relative_change is None
                or relative_change > 0.02
            ):
                status = "PRECISION_PENDING"
            else:
                status = "PRECISION_CRITERIA_PASSED"
            row: dict[str, object] = dict(
                m=self.m,
                power=power,
                points_per_scramble=2**power,
                scrambles=4,
                HV_QMC=mean,
                HV_QMC_SE=se,
                HV_quantum=quantum,
                relative_se=relative_se,
                relative_change_previous=relative_change,
                min_scramble_hits=int(counts.min()),
                eligible_count=len(eligible),
                excluded_zero_contribution_count=len(a) - len(eligible),
                qmc_status=status,
            )
            for k, value in enumerate(estimates):
                row[f"scramble_{k}"] = float(value)
            rows.append(row)
            previous = mean
        return rows

    def estimate(self, points: ArrayLike) -> dict[str, object]:
        a = matrix(points)
        if a.shape[1] != self.m or np.any(a < 0):
            raise ValueError("HV response dimension or sign is invalid")
        eligible = np.unique(a[np.all(a < 1.1, axis=1)], axis=0)
        if not len(eligible):
            return dict(
                HV=0.0,
                HV_SE=0.0,
                HV_status="ZERO_CONTRIBUTION_CERTIFIED",
                HV_method="exact empty union",
                HV_excluded=len(a),
            )
        if len(eligible) <= 8:
            value, bound = exact_small_union(eligible)
            status = (
                "EXACT_UP_TO_FLOAT64"
                if value > bound and bound / value <= 1e-10
                else "PRECISION_PENDING"
            )
            return dict(
                HV=value if status == "EXACT_UP_TO_FLOAT64" else None,
                HV_raw_inclusion_exclusion=value,
                HV_SE=None,
                HV_roundoff_bound=bound,
                HV_status=status,
                HV_method="exact small-set inclusion-exclusion",
                HV_excluded=len(a) - len(eligible),
            )
        row = self.study(a)[-1]
        return dict(
            HV=row["HV_QMC"],
            HV_SE=row["HV_QMC_SE"],
            HV_status=row["qmc_status"],
            HV_method="scrambled Sobol indicator estimate",
            HV_excluded=len(a) - len(eligible),
        )
