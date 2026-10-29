"""Read-only evolutionary checkpoints; quality metrics are computed after timing."""

from time import perf_counter, process_time
from typing import Any

import numpy as np
from pymoo.core.callback import Callback  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.nbi import canonical_decision_points, nondominated_mask


class PopulationObserver(Callback):  # type: ignore[misc]
    def __init__(
        self,
        checkpoints: tuple[int, ...],
        x_tolerance: float,
        dominance_tolerance: FloatArray,
        wall_start: float,
        cpu_start: float,
    ) -> None:
        super().__init__()
        self.checkpoints = frozenset(checkpoints)
        self.x_tolerance = x_tolerance
        self.dominance_tolerance = dominance_tolerance
        self.wall_start = wall_start
        self.cpu_start = cpu_start
        self.observation_seconds = 0.0
        self.records: list[dict[str, Any]] = []

    def notify(self, algorithm: Any) -> None:
        generation = int(algorithm.n_gen)
        if generation not in self.checkpoints:
            return
        start = perf_counter()
        # Copies only: never set a population field or read/advance its RNG.
        x = np.asarray(algorithm.pop.get("X"), dtype=float).copy()
        f = np.asarray(algorithm.pop.get("natural_F"), dtype=float).copy()
        z = np.asarray(algorithm.pop.get("F"), dtype=float).copy()
        representatives, _ = canonical_decision_points(x, tolerance=self.x_tolerance)
        keep = nondominated_mask(z[representatives], equality_tolerance=self.dominance_tolerance)
        selected = representatives[keep]
        n_nd_raw = int(nondominated_mask(z, equality_tolerance=self.dominance_tolerance).sum())
        observed = perf_counter() - start
        self.observation_seconds += observed
        self.records.append(
            dict(
                generation=generation,
                nfe=int(algorithm.evaluator.n_eval),
                x=x[selected],
                natural_f=f[selected],
                z=z[selected],
                population_indices=selected,
                N_returned=len(x),
                N_ND_before_dedup=n_nd_raw,
                N_unique_ND=len(selected),
                T_total=perf_counter() - self.wall_start,
                cpu_seconds=process_time() - self.cpu_start,
                observer_seconds_cumulative=self.observation_seconds,
            )
        )
