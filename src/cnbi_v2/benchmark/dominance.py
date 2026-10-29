"""Cache exact numerical dominance/equality relations for many fixed subsets.

This changes computational reuse only: each subset still selects its own first
representatives, then applies the unchanged Phase6 MIN equality-band definition.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import cKDTree  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray

from .metrics import matrix


@dataclass(frozen=True)
class DominanceIndex:
    n: int
    dominators: NDArray[np.int64]
    dominated: NDArray[np.int64]
    duplicate_pairs: NDArray[np.int64]

    @classmethod
    def build(
        cls, x: FloatArray, z: FloatArray, xtol: float, tolerance: FloatArray, block: int = 128
    ) -> "DominanceIndex":
        x, z = matrix(x), matrix(z)
        if (
            len(x) != len(z)
            or tolerance.shape != (z.shape[1],)
            or np.any(tolerance < 0)
            or xtol < 0
            or block < 1
        ):
            raise ValueError("invalid fixed dominance-index inputs")
        left, right = [], []
        for start in range(0, len(z), block):
            diff = z[None, :, :] - z[start : start + block, None, :]
            hit = np.all(diff <= tolerance, axis=2) & np.any(diff < -tolerance, axis=2)
            query, candidate = np.nonzero(hit)
            left.append(candidate)
            right.append(query + start)
        pairs = cKDTree(x).query_pairs(xtol, p=np.inf, eps=0.0, output_type="ndarray")
        return cls(
            len(x),
            np.concatenate(left).astype(np.int64),
            np.concatenate(right).astype(np.int64),
            np.asarray(pairs, dtype=np.int64),
        )

    def front(self, indices: NDArray[np.int64]) -> tuple[NDArray[np.int64], NDArray[np.int64]]:
        ids = np.asarray(indices, dtype=np.int64)
        if (
            ids.ndim != 1
            or not len(ids)
            or np.any(ids < 0)
            or np.any(ids >= self.n)
            or len(np.unique(ids)) != len(ids)
        ):
            raise ValueError("subset IDs must be nonempty unique in-range values")
        active = np.zeros(self.n, dtype=bool)
        active[ids] = True
        canonical = np.arange(self.n, dtype=np.int64)
        neighbours: dict[int, list[int]] = {}
        for a, b in self.duplicate_pairs:
            if active[a] and active[b]:
                neighbours.setdefault(int(a), []).append(int(b))
                neighbours.setdefault(int(b), []).append(int(a))
        # Iterate the supplied ordering, not a global dedup representative. This
        # preserves independent coordinates after family/seed exclusion.
        for i in ids:
            if not active[i]:
                continue
            for j in neighbours.get(int(i), []):
                if active[j]:
                    active[j] = False
                    canonical[j] = i
        valid_edge = active[self.dominators] & active[self.dominated]
        keep = active.copy()
        keep[self.dominated[valid_edge]] = False
        return ids[keep[ids]], canonical[ids]
