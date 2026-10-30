"""Search-only dispatch and original-objective diagnostics; no Pareto truth API."""

from time import perf_counter
from typing import Any

import numpy as np

from cnbi_v2.nbi.sensitivity import nondominated_mask

from .cnbi_runner import run_cnbi
from .contracts import METHODS, RunOutput, SearchInput, array_hash
from .ea_runner import run_ea
from .instrumentation import KernelCounter
from .vrf_runner import run_vrf


def run_method(data: SearchInput, method: str, seed: int,
               ea_config: dict[str, Any] | None = None) -> RunOutput:
    if method not in METHODS:
        raise ValueError("unknown benchmark method")
    started = perf_counter()
    with KernelCounter() as instrumentation:
        if method == "C-NBI":
            output = run_cnbi(data, seed)
        elif method == "VRF-NBI":
            output = run_vrf(data, seed)
        else:
            if ea_config is None:
                raise ValueError("EA requires the pinned calibration record")
            output = run_ea(data, method, ea_config, seed)
    output.validate(data)
    output.counters.update(instrumentation.counts)
    original_points = output.counters.get("original_rsm_point_evaluations", 0)
    # EA search counts exclude its separate batch export and validation; NBI
    # original-vector counts already include export, but not validation replay.
    original_points += len(output.decisions)*(2 if method in METHODS[2:] else 1)
    output.counters["original_full_vector_points_computed"] = original_points
    output.counters["model_vector_point_events"] = (
        original_points+output.counters.get("quadratic_response_vector_calls", 0)
        +output.counters.get("factor_model_vector_evaluations", 0)
    )
    feasible = np.linalg.norm(output.decisions, axis=1) <= data.alpha
    indices = np.flatnonzero(feasible)
    nd = (indices[nondominated_mask(output.rsm_responses[indices])]
          if len(indices) else indices)
    output.diagnostics.update(
        frozen_coefficients_sha256=array_hash(data.model.coefficients),
        raw_decisions_preserved=True, original_objective_nd_indices=nd,
        original_objective_feasible_indices=indices, original_objective_count=data.m,
        counter_policy="full_original_RSM_points_plus_separate_scalar_kernel_calls",
        instrumentation="Python_call_events; overhead included consistently in optimization time",
        counter_schema=2,
    )
    elapsed = perf_counter()-started
    output.timings["postprocessing"] = (
        elapsed-output.timings.get("preparation", 0.)-output.timings.get("solver", 0.)
    )
    output.timings["total"] = elapsed
    return output
