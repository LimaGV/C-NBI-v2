"""Post-hoc proposed v2 policy; operates only on existing prefix PA decisions."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real

from ._validation import frozen, integer
from .parallel_analysis import PACheckpoint


@dataclass(frozen=True, slots=True)
class AdjacentSpectralGaps:
    absolute: FloatArray
    normalized: FloatArray
    degenerate: NDArray[np.bool_]

    def __post_init__(self) -> None:
        for field in ("absolute", "normalized", "degenerate"):
            object.__setattr__(self, field, frozen(getattr(self, field)))


def normalized_adjacent_gaps(
    q95: ArrayLike,
    *,
    epsilon: float = float(np.finfo(float).tiny),
) -> AdjacentSpectralGaps:
    """Finite descending nonnegative spectrum; a one-component pair has no gaps."""
    q = _as_finite_real(q95, "q95")
    if (
        q.ndim != 1
        or not len(q)
        or np.any(q < 0)
        or isinstance(epsilon, bool)
        or not np.isfinite(epsilon)
        or epsilon <= 0
    ):
        raise ValueError("need nonempty nonnegative q95 and positive finite numerical epsilon")
    absolute = q[:-1] - q[1:]
    tolerance = 8 * np.finfo(float).eps * max(float(q[0]), epsilon)
    if np.any(absolute < -tolerance):
        raise ValueError("q95 spectrum must be ordered descending")
    absolute = np.maximum(absolute, 0.0)  # Only accepted ordering roundoff, not q95 clipping.
    degenerate = (q[:-1] <= epsilon) & (q[1:] <= epsilon)
    normalized = np.divide(absolute, np.maximum(q[:-1], epsilon))
    normalized[degenerate] = 0.0
    return AdjacentSpectralGaps(absolute, normalized, degenerate)


@dataclass(frozen=True, slots=True)
class Q95GapSpectrum:
    scope: str
    subset_id: str
    k: int
    q95: FloatArray
    gaps: AdjacentSpectralGaps

    def __post_init__(self) -> None:
        object.__setattr__(self, "q95", frozen(self.q95))


def checkpoint_spectral_gaps(
    checkpoint: PACheckpoint,
    *,
    epsilon: float = float(np.finfo(float).tiny),
) -> tuple[Q95GapSpectrum, ...]:
    """Group identified thresholds; observed values and PA margins are never used."""
    if (
        checkpoint.decision_quantiles.ndim != 1
        or not checkpoint.quantile_ids
        or len(checkpoint.quantile_ids) != len(checkpoint.decision_quantiles)
        or len(set(checkpoint.quantile_ids)) != len(checkpoint.quantile_ids)
    ):
        raise ValueError("checkpoint needs unique matching quantile identities")
    groups: dict[str, list[float]] = {}
    for identifier, value in zip(
        checkpoint.quantile_ids, checkpoint.decision_quantiles, strict=True
    ):
        subset, rank = identifier.rsplit(":", 1)
        values = groups.setdefault(subset, [])
        if rank != str(len(values) + 1):
            raise ValueError("quantile ranks must be consecutive within each spectrum")
        values.append(float(value))
    if next(iter(groups)) != "GLOBAL":
        raise ValueError("global spectrum must be first")
    result = []
    for subset, values in groups.items():
        k = len(values) + 1
        if subset != "GLOBAL":
            parts = subset.split("_")
            if (
                parts[0] != "C"
                or len(parts) != k + 1
                or any(not p.isdigit() or int(p) < 1 for p in parts[1:])
                or sorted(set(map(int, parts[1:]))) != list(map(int, parts[1:]))
            ):
                raise ValueError("local subset ID must identify k ordered response indices")
        result.append(
            Q95GapSpectrum(
                "GLOBAL" if subset == "GLOBAL" else "LOCAL",
                subset,
                k,
                np.array(values),
                normalized_adjacent_gaps(values, epsilon=epsilon),
            )
        )
    if not checkpoint.selected_ids <= (groups.keys() - {"GLOBAL"}):
        raise ValueError("selected subset IDs must have matching spectra")
    return tuple(result)


@dataclass(frozen=True, slots=True)
class SpectralGapStopPolicy:
    checkpoints: tuple[int, ...]
    checkpoint_step: int
    minimum_B: int
    stability_window: int
    earliest_full_window_B: int
    gap_tolerance: float
    epsilon_q: float
    maximum_B: int


def gap_policy_from_mapping(data: Mapping[str, object]) -> SpectralGapStopPolicy:
    """Reject parameter drift from the explicitly requested, frozen v2 contract."""
    expected: dict[str, object] = {
        "policy_id": "pa_normalized_spectral_gap_stability_v2",
        "version": 2,
        "status": "PROPOSED_REVISED",
        "post_hoc_on_turning_case": True,
        "current_policy": "normalized_spectral_gap_stability",
        "gap_metric": "normalized_adjacent_q95_gap",
        "quantile": 0.95,
        "quantile_method": "linear",
        "gap_tolerance": 0.05,
        "epsilon_q": float(np.finfo(float).tiny),
    }
    if any(
        data.get(key) != value or type(data.get(key)) is not type(value)
        for key, value in expected.items()
    ):
        raise ValueError("unsupported or modified spectral-gap policy v2")
    raw = data["checkpoints"]
    if not isinstance(raw, list):
        raise ValueError("policy checkpoints must be a list")
    points = tuple(integer(b, "checkpoint", 2) for b in raw)
    names = (
        "checkpoint_step",
        "minimum_B",
        "stability_window",
        "earliest_full_window_B",
        "maximum_B",
    )
    numbers = tuple(integer(data[name], name, 1) for name in names)
    if points != tuple(range(100, 2001, 100)) or numbers != (100, 500, 3, 700, 2000):
        raise ValueError("inconsistent spectral-gap checkpoint/window policy")
    return SpectralGapStopPolicy(
        points, *numbers[:4], 0.05, float(np.finfo(float).tiny), numbers[4]
    )


@dataclass(frozen=True, slots=True)
class GapStopCheckpoint:
    B: int
    eligible: bool
    selection_changed_from_previous: bool | None
    global_gap_max_change: float | None
    selected_local_gap_max_change: float | None
    overall_monitored_gap_max_change: float | None
    previous_transition_monitored_gap_max_change: float | None
    window_monitored_gap_max_change: float | None
    three_checkpoint_dimension_stable: bool
    three_checkpoint_selection_stable: bool
    monitored_spectra_consistent: bool
    spectral_gap_stable: bool
    early_stop_condition_met: bool
    monitored_subset_ids: tuple[str, ...]
    monitored_gap_count: int
    degenerate_gap_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GapEarlyStopValidation:
    first_B_stop: int | None
    reference_B: int
    stop_status: str
    retrospective_status: str
    changed_later_checkpoints: tuple[int, ...]
    same_final_selection: bool | None
    same_final_dimension: bool | None
    post_stop_max_gap_change: float | None
    post_stop_gap_tolerance_exceeded_at: tuple[int, ...]
    replicate_reduction_fraction: float | None
    trajectory: tuple[GapStopCheckpoint, ...]


def evaluate_gap_early_stop(
    records: Sequence[PACheckpoint],
    policy: SpectralGapStopPolicy,
) -> GapEarlyStopValidation:
    """Same window monitor set for both transitions; every later decision is checked."""
    if tuple(r.B for r in records) != policy.checkpoints:
        raise ValueError("validation must supply every policy checkpoint through maximum_B")
    if any(r.quantile_ids != records[0].quantile_ids for r in records):
        raise ValueError("quantile identities/order must remain identical across checkpoints")
    spectra = [checkpoint_spectral_gaps(r, epsilon=policy.epsilon_q) for r in records]
    gaps = [{s.subset_id: s.gaps.normalized for s in row} for row in spectra]

    def change(left: int, right: int, monitored: tuple[str, ...]) -> float:
        return max(
            float(np.max(np.abs(gaps[right][key] - gaps[left][key]), initial=0.0))
            for key in monitored
        )

    first_index = None
    trajectory = []
    for index, current in enumerate(records):
        start = max(0, index - policy.stability_window + 1)
        window = records[start : index + 1]
        stable_ids = frozenset.intersection(*(r.selected_ids for r in window))
        local = tuple(
            s.subset_id for s in spectra[index][1:] if s.k >= 3 and s.subset_id in stable_ids
        )
        monitored = ("GLOBAL", *local)
        complete = len(window) == policy.stability_window
        eligible = complete and window[0].B >= policy.minimum_B
        dimension_stable = complete and len({r.global_dimension for r in window}) == 1
        selection_stable = complete and all(r.selected_ids == current.selected_ids for r in window)
        consistent = selection_stable  # Fixed quantile IDs/ranks already verified above.
        global_change = local_change = overall = prior = maximum = None
        if index:
            global_change = change(index - 1, index, ("GLOBAL",))
            local_change = change(index - 1, index, local) if local else None
            overall = change(index - 1, index, monitored)
        if complete:
            prior = change(index - 2, index - 1, monitored)
            assert overall is not None
            maximum = max(prior, overall)
        spectral_stable = maximum is not None and maximum < policy.gap_tolerance
        condition = (
            eligible and dimension_stable and selection_stable and consistent and spectral_stable
        )
        if condition and first_index is None:
            first_index = index
        degenerate = tuple(
            f"{s.subset_id}:{j + 1}"
            for s in spectra[index]
            for j, flag in enumerate(s.gaps.degenerate)
            if flag
        )
        trajectory.append(
            GapStopCheckpoint(
                current.B,
                eligible,
                current.selected_ids != records[index - 1].selected_ids if index else None,
                global_change,
                local_change,
                overall,
                prior,
                maximum,
                dimension_stable,
                selection_stable,
                consistent,
                spectral_stable,
                condition,
                local,
                sum(len(gaps[index][key]) for key in monitored),
                degenerate,
            )
        )
    if first_index is None:
        return GapEarlyStopValidation(
            None,
            policy.maximum_B,
            "EARLY_STOP_NOT_REACHED",
            "NOT_APPLICABLE_NO_EARLY_STOP",
            (),
            None,
            None,
            None,
            (),
            None,
            tuple(trajectory),
        )
    stopped, final = records[first_index], records[-1]
    later = tuple(i for i in range(first_index + 1, len(records)))
    changed = tuple(
        records[i].B
        for i in later
        if records[i].selected_ids != stopped.selected_ids
        or records[i].global_dimension != stopped.global_dimension
    )
    monitored = ("GLOBAL", *trajectory[first_index].monitored_subset_ids)
    later_changes = [(records[i].B, change(i - 1, i, monitored)) for i in later]
    return GapEarlyStopValidation(
        stopped.B,
        policy.maximum_B,
        "EARLY_STOP_CONDITION_MET",
        "PREMATURE_STOP_DETECTED"
        if changed
        else "EARLY_STOP_RETROSPECTIVELY_DECISION_STABLE"
        if later
        else "NOT_APPLICABLE_STOP_AT_REFERENCE",
        changed,
        final.selected_ids == stopped.selected_ids,
        final.global_dimension == stopped.global_dimension,
        max((delta for _, delta in later_changes), default=None),
        tuple(b for b, delta in later_changes if delta >= policy.gap_tolerance),
        1 - stopped.B / policy.maximum_B,
        tuple(trajectory),
    )
