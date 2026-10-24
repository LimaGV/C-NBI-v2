"""Evaluate the pre-existing PA policy without changing it or truncating validation."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from ._validation import integer
from .parallel_analysis import PACheckpoint


@dataclass(frozen=True, slots=True)
class PAStopPolicy:
    checkpoints: tuple[int, ...]
    minimum_eligible_B: int
    comparison_lag: int
    quantile_relative_tolerance: float
    epsilon_q: float
    maximum_B: int


def policy_from_mapping(data: Mapping[str, object]) -> PAStopPolicy:
    raw = data["checkpoints"]
    if not isinstance(raw, list):
        raise ValueError("policy checkpoints must be a list")
    points = tuple(integer(b, "policy checkpoint", 2) for b in raw)
    minimum = integer(data["minimum_eligible_B"], "minimum_eligible_B", 2)
    lag = integer(data["comparison_lag"], "comparison_lag", 1)
    maximum = integer(data["maximum_B"], "maximum_B", 2)
    relative, epsilon = data["quantile_relative_tolerance"], data["epsilon_q"]
    if (isinstance(relative, bool) or isinstance(epsilon, bool)
            or not isinstance(relative, (float, int)) or not isinstance(epsilon, (float, int))):
        raise ValueError("policy relative tolerance and epsilon must be numeric")
    if (not points or tuple(sorted(set(points))) != points or maximum != points[-1]
            or minimum not in points or minimum-lag not in points
            or any(b-a != lag for a, b in zip(points, points[1:], strict=False))
            or not np.isfinite(relative) or not 0 < relative < 1
            or not np.isfinite(epsilon) or epsilon <= 0
            or data["policy_id"] != "future_pa_adjacent_checkpoint_stability_v1"
            or data["status"] != "PROPOSED"):
        raise ValueError("unsupported or inconsistent PA early-stop policy")
    return PAStopPolicy(points, minimum, lag, float(relative), float(epsilon), maximum)


@dataclass(frozen=True, slots=True)
class StopCheckpoint:
    B: int
    selection_changed_from_previous: bool | None
    dimension_changed_from_previous: bool | None
    max_decision_quantile_relative_change: float | None
    eligible: bool
    early_stop_condition_met: bool


@dataclass(frozen=True, slots=True)
class EarlyStopValidation:
    first_B_stop: int | None
    reference_B: int
    stop_status: str
    retrospective_status: str
    changed_later_checkpoints: tuple[int, ...]
    trajectory: tuple[StopCheckpoint, ...]


def evaluate_early_stop(
    records: Sequence[PACheckpoint], policy: PAStopPolicy,
) -> EarlyStopValidation:
    if tuple(r.B for r in records) != policy.checkpoints:
        raise ValueError("validation must supply every policy checkpoint through maximum_B")
    if any(r.decision_quantiles.ndim != 1 or len(r.quantile_ids) != len(r.decision_quantiles)
           or not len(r.quantile_ids) or len(set(r.quantile_ids)) != len(r.quantile_ids)
           or not np.isfinite(r.decision_quantiles).all() or np.any(r.decision_quantiles < 0)
           for r in records):
        raise ValueError("every checkpoint needs finite nonnegative uniquely identified quantiles")
    first_stop = None
    trajectory = []
    for index, current in enumerate(records):
        changed = dimension_changed = None
        maximum_change = None
        eligible = current.B >= policy.minimum_eligible_B
        condition = False
        if index:
            previous = records[index-1]
            if (current.quantile_ids != previous.quantile_ids
                    or current.decision_quantiles.shape != previous.decision_quantiles.shape):
                raise ValueError("decision quantile identities/shapes mismatch")
            changed = current.selected_ids != previous.selected_ids
            dimension_changed = current.global_dimension != previous.global_dimension
            denominator = np.maximum(np.maximum(np.abs(current.decision_quantiles),
                                                 np.abs(previous.decision_quantiles)),
                                     policy.epsilon_q)
            maximum_change = float(np.max(np.abs(current.decision_quantiles
                                                 - previous.decision_quantiles) / denominator))
            condition = (eligible and not changed and not dimension_changed
                         and maximum_change < policy.quantile_relative_tolerance)
            if condition and first_stop is None:
                first_stop = current.B
        trajectory.append(StopCheckpoint(current.B, changed, dimension_changed,
                                          maximum_change, eligible, condition))
    later_changes: tuple[int, ...] = ()
    if first_stop is None:
        status, retrospective = "EARLY_STOP_NOT_REACHED", "NOT_APPLICABLE_NO_EARLY_STOP"
    else:
        stopped = next(r for r in records if r.B == first_stop)
        later_changes = tuple(r.B for r in records if r.B > first_stop and
                              (r.global_dimension != stopped.global_dimension
                               or r.selected_ids != stopped.selected_ids))
        status = "EARLY_STOP_CONDITION_MET"
        retrospective = ("PREMATURE_STOP_DETECTED" if later_changes else
                         "EARLY_STOP_RETROSPECTIVELY_STABLE" if first_stop < policy.maximum_B
                         else "NOT_APPLICABLE_STOP_AT_REFERENCE")
    return EarlyStopValidation(first_stop, policy.maximum_B, status, retrospective,
                                later_changes, tuple(trajectory))
