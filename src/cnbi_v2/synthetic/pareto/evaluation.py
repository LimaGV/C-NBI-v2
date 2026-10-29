"""Offline evaluation only: raw decisions preserved; no oracle feedback to search."""

import json
from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cnbi_v2.nbi import nondominated_mask

from ..design import Scenario
from ..domain import radius
from ..model import FloatArray, evaluate, frozen, real_array
from .hypervolume import FixedHypervolume
from .metrics import evaluate_metrics
from .normalization import AnalyticalNormalization
from .selection import unique_indices

METHODS = ("C-NBI", "VRF-NBI", "NSGA-III", "MOEA/D")


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    scenario_id: str
    replica_id: int
    method: str
    raw_decisions: FloatArray
    true_responses: FloatArray
    normalized_responses: FloatArray
    feasible_mask: NDArray[np.bool_]
    unique_indices: NDArray[np.int64]
    nondominated_indices: NDArray[np.int64]
    metrics: dict[str, object]
    diagnostics: dict[str, object]
    run_metadata: str


@dataclass(frozen=True, slots=True)
class EvaluationContext:
    scenario: Scenario
    anchors: FloatArray
    normalization: AnalyticalNormalization
    reference_normalized: FloatArray
    hv: FixedHypervolume
    hv_protocol_status: str = "STUDY_ONLY_NOT_YET_FROZEN"
    reference_coverage_status: str = "REVIEW_NOT_EVALUATED"

    def evaluate(
        self,
        scenario_id: str,
        replica_id: int,
        method: str,
        decisions: ArrayLike,
        run_metadata: Mapping[str, object],
        *,
        seconds: float | None = None,
        nfe: int | None = None,
    ) -> EvaluationResult:
        if (
            scenario_id != self.scenario.scenario_id
            or method not in METHODS
            or isinstance(replica_id, bool)
            or not isinstance(replica_id, int)
            or replica_id not in range(1, 6)
        ):
            raise ValueError("known scenario, method and experimental replica1..5 required")
        if (seconds is not None and (not np.isfinite(seconds) or seconds < 0)) or (
            nfe is not None and (isinstance(nfe, bool) or not isinstance(nfe, int) or nfe < 0)
        ):
            raise ValueError("nonnegative finite runtime and integer NFE required when supplied")
        metadata = json.dumps(dict(run_metadata), allow_nan=False, sort_keys=True)
        x = real_array(decisions, "raw decisions")
        if x.ndim != 2 or x.shape[1] != self.scenario.nx:
            raise ValueError("raw decision dimension does not match scenario")
        if len(x):
            true = evaluate(x, self.anchors)
        else:
            true = np.empty((0, self.scenario.m))
        normalized = self.normalization.transform(true)
        norms = np.linalg.norm(x, axis=1)
        feasible = norms <= radius(self.scenario.nx)  # No repair, projection or hidden tolerance.
        valid = np.flatnonzero(feasible)
        unique = (
            valid[unique_indices(x[valid], 1e-12 * radius(self.scenario.nx))]
            if len(valid)
            else valid
        )
        nd = (
            unique[
                nondominated_mask(
                    normalized[unique], equality_tolerance=np.full(self.scenario.m, 1e-12)
                )
            ]
            if len(unique)
            else unique
        )
        metrics: dict[str, object] = (
            evaluate_metrics(normalized[nd], self.reference_normalized, self.hv)
            if len(nd)
            else dict(
                GD=None,
                IGD=None,
                HV=None,
                Spacing=None,
                Sparsity=None,
                status="UNDEFINED_EMPTY_FEASIBLE_ND_SET",
            )
        )
        diagnostics: dict[str, object] = dict(
            raw_count=len(x),
            feasible_count=len(valid),
            unique_count=len(unique),
            nondominated_count=len(nd),
            infeasible_count=len(x) - len(valid),
            above_normalized_one=int(np.sum(np.any(normalized > 1, axis=1))),
            maximum_sphere_violation=float(np.maximum(norms - radius(self.scenario.nx), 0).max())
            if len(x)
            else 0.0,
            seconds=seconds,
            nfe=nfe,
            cardinality_mode="native",
            oracle_feedback_to_search=False,
            raw_decisions_modified=False,
            hv_protocol_status=self.hv_protocol_status,
            reference_coverage_status=self.reference_coverage_status,
        )
        return EvaluationResult(
            scenario_id,
            replica_id,
            method,
            frozen(x),
            frozen(true),
            frozen(normalized),
            feasible,
            unique,
            nd,
            metrics,
            diagnostics,
            metadata,
        )


def equalization_plan(
    scenario_id: str, replica_id: int, eligible_counts: Mapping[str, int]
) -> dict[str, object]:
    if (
        not scenario_id
        or replica_id not in range(1, 6)
        or set(eligible_counts) != set(METHODS)
        or any(
            isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in eligible_counts.values()
        )
    ):
        raise ValueError("one paired block with all four nonnegative cardinalities required")
    return dict(
        scenario_id=scenario_id,
        replica_id=replica_id,
        target_count=min(eligible_counts.values()),
        status="PLAN_ONLY_NOT_EXECUTED",
        rule="candidate-only FPS with stable raw IDs; no reference distances or interpolation",
        primary_analysis="native ND",
        secondary_analysis="minimum eligible count per paired block",
    )
