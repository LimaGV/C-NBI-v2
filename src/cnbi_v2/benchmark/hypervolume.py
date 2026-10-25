"""Shared-box scrambled Sobol HV, matching the historical applied integral.

Packed per-point attainment masks make unions, nested K and 500 seed subsets
reuse exactly the same quadrature nodes, without changing the HV definition.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.stats import qmc  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real
from cnbi_v2.optimization.quadratic import immutable

from .metrics import matrix

BIT_COUNTS = np.array([int(i).bit_count() for i in range(256)], dtype=np.uint8)


def historical_box(points: FloatArray) -> tuple[FloatArray, FloatArray]:
    a = matrix(points)
    lo = np.minimum(0.0, a.min(axis=0))
    hi = a.max(axis=0)
    ref = np.maximum(1.1, hi + 0.05 * np.maximum(hi - lo, 1.0))
    return immutable(lo), immutable(ref)


@dataclass(frozen=True)
class HVGrid:
    lower: FloatArray
    reference: FloatArray
    power: int = 16
    seeds: tuple[int, ...] = (20260, 20261, 20262, 20263)

    def __post_init__(self) -> None:
        lo, ref = (_as_finite_real(v, "HV bounds") for v in (self.lower, self.reference))
        if (
            lo.ndim != 1
            or ref.shape != lo.shape
            or not len(lo)
            or np.any(ref <= lo)
            or isinstance(self.power, bool)
            or not 3 <= self.power <= 24
            or len(self.seeds) < 2
            or len(set(self.seeds)) != len(self.seeds)
        ):
            raise ValueError("invalid common HV box or quadrature configuration")
        object.__setattr__(self, "lower", immutable(lo))
        object.__setattr__(self, "reference", immutable(ref))

    @property
    def volume(self) -> float:
        return float(np.prod(self.reference - self.lower))

    @property
    def bytes_per_point(self) -> int:
        return int(len(self.seeds) * (2**self.power // 8))

    def samples(self) -> FloatArray:
        blocks = [
            qmc.Sobol(
                len(self.lower), scramble=True, rng=np.random.Generator(np.random.PCG64(seed))
            ).random_base2(self.power)
            for seed in self.seeds
        ]
        return self.lower + np.concatenate(blocks) * (self.reference - self.lower)

    def masks(self, points: FloatArray, samples: FloatArray) -> NDArray[np.uint8]:
        a = matrix(points)
        if (
            a.shape[1] != len(self.lower)
            or np.any(a < self.lower)
            or np.any(a >= self.reference)
            or samples.shape != (len(self.seeds) * 2**self.power, a.shape[1])
        ):
            raise ValueError("HV reference must strictly dominate every evaluated point")
        result = np.empty((len(a), self.bytes_per_point), dtype=np.uint8)
        for start in range(0, len(samples), 4096):
            hits = np.all(a[:, None, :] <= samples[None, start : start + 4096, :], axis=2)
            packed = np.packbits(hits, axis=1, bitorder="little")
            result[:, start // 8 : start // 8 + packed.shape[1]] = packed
        return result

    def values(self, mask: NDArray[np.uint8], *, power: int | None = None) -> FloatArray:
        p = self.power if power is None else power
        if mask.shape != (self.bytes_per_point,) or not 3 <= p <= self.power:
            raise ValueError("HV mask or nested precision mismatch")
        rows = mask.reshape(len(self.seeds), -1)[:, : 2**p // 8]
        return np.asarray(BIT_COUNTS[rows].sum(axis=1) * self.volume / 2**p, dtype=float)

    def estimate(self, mask: NDArray[np.uint8]) -> dict[str, float]:
        h = self.values(mask)
        return {"HV": float(h.mean()), "HV_QMC_SE": float(h.std(ddof=1) / np.sqrt(len(h)))}
