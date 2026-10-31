"""Online joint-decision guard; no future ensemble or quality indicator is accessible."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.chim.parallel_analysis import PACheckpoint
from cnbi_v2.model.quadratic_design import _as_finite_real

CANDIDATE_CHECKPOINTS = (200, 400, 600, 800, 1000, 1200, 1500, 2000)


@dataclass(frozen=True)
class StopPolicy:
    checkpoints: tuple[int, ...] = tuple(range(200, 2001, 100))
    maximum_B: int = 2000
    minimum_B: int = 800
    window: int = 5
    relative_q95_range: float = 0.05
    margin_range_multiplier: float = 2.0

    def __post_init__(self) -> None:
        if (
            not self.checkpoints
            or tuple(sorted(set(self.checkpoints))) != self.checkpoints
            or self.checkpoints[-1] != self.maximum_B
            or self.maximum_B != 2000
            or any(isinstance(b, bool) or not isinstance(b, int) or b < 2 for b in self.checkpoints)
            or self.window < 2
            or self.minimum_B < self.checkpoints[0]
            or not 0 < self.relative_q95_range < 1
            or self.margin_range_multiplier < 1
        ):
            raise ValueError("invalid adaptive PA policy")


def assess_stop(
    history: list[PACheckpoint],
    observed: ArrayLike,
    numerical_scales: ArrayLike,
    policy: StopPolicy,
    *,
    certified: bool = True,
) -> dict[str, object]:
    if not history or tuple(r.B for r in history) != policy.checkpoints[: len(history)]:
        raise ValueError("online history must contain exactly the consumed checkpoint prefix")
    current = history[-1]
    actual = _as_finite_real(observed, "observed spectra")
    scales = _as_finite_real(numerical_scales, "per-component nominal leading scales")
    if (
        actual.ndim != 1
        or actual.shape != current.decision_quantiles.shape
        or scales.shape != actual.shape
        or np.any(scales <= 0)
        or any(r.quantile_ids != current.quantile_ids for r in history)
    ):
        raise ValueError("all component identities and nominal scales must agree")
    window = history[-policy.window :]
    complete = len(window) == policy.window
    eligible = complete and current.B >= policy.minimum_B
    dimensions = complete and all(r.global_dimension == current.global_dimension for r in window)
    selections = complete and all(r.selected_ids == current.selected_ids for r in window)
    flags = [np.concatenate([c.passes for c in r.components]) for r in window]
    components = complete and all(np.array_equal(f, flags[-1]) for f in flags)
    quantiles = np.stack([r.decision_quantiles for r in window])
    spread = np.ptp(quantiles, axis=0)
    numerical = 64 * np.finfo(float).eps * np.maximum(1.0, scales)
    relative = spread / np.maximum(current.decision_quantiles, numerical)
    stable_q95 = bool(complete and np.all(relative < policy.relative_q95_range))
    margins = np.abs(actual - current.decision_quantiles)
    safe_margin = bool(
        complete and np.all(margins > policy.margin_range_multiplier * spread + numerical)
    )
    condition = bool(
        eligible
        and dimensions
        and selections
        and components
        and stable_q95
        and safe_margin
        and certified
    )
    stop = condition and current.B < policy.maximum_B
    return dict(
        B=current.B,
        eligible=eligible,
        dimension_stable=dimensions,
        selected_ids_stable=selections,
        all_component_decisions_stable=components,
        q95_stable=stable_q95,
        margin_guard=safe_margin,
        certified=bool(certified),
        maximum_relative_q95_range=float(relative.max()),
        minimum_margin_over_guard=float(
            np.min(margins / (policy.margin_range_multiplier * spread + numerical))
        ),
        condition_met=condition,
        stop=stop,
        status="EARLY_STOP"
        if stop
        else ("MAX_B_REACHED" if current.B == policy.maximum_B else "CONTINUE"),
    )
