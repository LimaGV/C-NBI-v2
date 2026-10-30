"""Descriptive release tables, with structural cells as the aggregation unit."""

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from execute_synthetic_benchmark import OUTPUT

from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, write_json
from cnbi_v2.synthetic.benchmark.contracts import METHODS


def checkpoint_chronology():
    """Capture original filesystem observations; reload them after Git checkout."""
    target = OUTPUT/"execution_chronology.json"
    if target.exists():
        return read_json(target)
    windows = []
    for method in METHODS:
        paths = list((OUTPUT/"campaign_checkpoints").glob(
            "official__*__"+method.replace("/", "_")+".json"))
        if len(paths) != 135:
            raise ValueError("chronology requires all135 checkpoints for each method")
        times = [path.stat() for path in paths]
        if any(not hasattr(info, "st_birthtime") for info in times):
            raise ValueError("original creation timestamps required for chronology capture")
        start = min(info.st_birthtime for info in times)
        end = max(info.st_mtime for info in times)
        windows.append(dict(method=method, runs=135, first_checkpoint_epoch=start,
                            last_checkpoint_epoch=end,
                            first_checkpoint_utc=datetime.fromtimestamp(start, UTC).isoformat(),
                            last_checkpoint_utc=datetime.fromtimestamp(end, UTC).isoformat(),
                            checkpoint_activity_seconds=end-start))
    if any(left["last_checkpoint_epoch"] > right["first_checkpoint_epoch"]
           for left, right in zip(windows, windows[1:], strict=False)):
        raise ValueError("observed method windows overlap or are out of order")
    result = dict(status="PASS", method_order=list(METHODS), windows=windows,
                  source="original Windows checkpoint creation/last-write times before checkout",
                  definition="checkpoint activity windows, not complete process lifecycle timers",
                  all_previous_checkpoints_finished_before_next_method_started=True)
    write_json(target, result)
    return result


def summarize():
    if (OUTPUT/"scheduler.lock").exists():
        raise ValueError("wait for all searches and offline evaluation")
    native = pd.read_csv(OUTPUT/"benchmark_native_metrics.csv")
    cells = pd.read_csv(OUTPUT/"benchmark_summary.csv")
    runtime = pd.read_csv(OUTPUT/"benchmark_runtime.csv")
    cardinality = pd.read_csv(OUTPUT/"benchmark_cardinalities.csv")
    precision = pd.read_csv(OUTPUT/"benchmark_hv_precision.csv")
    runs = pd.read_csv(OUTPUT/"campaign_runs.csv")
    if len(native) != 540 or len(runs) != 540 or runs.state.isin(["PENDING", "RUNNING"]).any():
        raise ValueError("all540 official attempts and evaluations are required")
    chronology = checkpoint_chronology()
    quantities = ("GD", "IGD", "HV", "Spacing", "Sparsity", "N_ND", "end_to_end_seconds",
                  "model_vector_point_events", "original_rsm_point_evaluations")
    result = {}
    for method in METHODS:
        subset = cells[cells.method.eq(method)]
        records = runs[runs.method.eq(method)]
        observations = native[native.method.eq(method)]
        times = runtime[runtime.method.eq(method)]
        counts = cardinality[cardinality.method.eq(method)]
        hv = precision[precision.method.eq(method)]
        metric_rows = {}
        for metric in quantities:
            selected = subset[subset.metric.eq(metric)]
            values = selected["median"].dropna().to_numpy(dtype=float)
            metric_rows[metric] = dict(
                defined_structural_cells=len(values),
                defined_replicas=int(selected.defined_replicas.sum()),
                median_of_cell_medians=float(np.median(values)) if len(values) else None,
                q25_of_cell_medians=float(np.quantile(values, .25)) if len(values) else None,
                q75_of_cell_medians=float(np.quantile(values, .75)) if len(values) else None,
                min_cell_median=float(values.min()) if len(values) else None,
                max_cell_median=float(values.max()) if len(values) else None,
            )
        ratio = hv.HV_SE/hv.HV.where(hv.HV.gt(0))
        per_run_undefined = {key: int(observations[key].isna().sum()) for key in quantities[:5]}
        result[method] = dict(
            planned=135, recorded=len(records), states=records.state.value_counts().to_dict(),
            algorithm_statuses=records.algorithm_status.value_counts().to_dict(),
            metrics=metric_rows, hv_statuses=hv.HV_status.value_counts().to_dict(),
            hv_max_relative_se=float(ratio.max()) if ratio.notna().any() else None,
            hv_median_relative_se=float(ratio.median()) if ratio.notna().any() else None,
            undefined_per_run_metrics=per_run_undefined,
            counter_totals={key: int(times[key].sum()) for key in (
                "original_rsm_point_evaluations", "original_full_vector_points_computed",
                "model_vector_point_events", "scalar_quadratic_values",
                "scalar_quadratic_gradients", "factor_model_vector_evaluations",
                "mc_anchor_solves", "nbi_subproblems", "nbi_attempts", "nbi_iterations",
            ) if key in times},
            summed_worker_wall_seconds=float(times.end_to_end_seconds.sum()),
            summed_kernel_wall_seconds=float(times.kernel_total_seconds.sum()),
            summed_external_evaluation_seconds=float(times.external_evaluation_seconds.sum()),
            minimum_per_run_worker_seconds=(float(times.end_to_end_seconds.min())
                                            if times.end_to_end_seconds.notna().any() else None),
            maximum_per_run_worker_seconds=(float(times.end_to_end_seconds.max())
                                            if times.end_to_end_seconds.notna().any() else None),
            lifecycle_observation_statuses=times.lifecycle_status.value_counts().to_dict(),
            observed_lifecycle_seconds_median_of_cell_medians=(
                float(times.groupby("scenario_id").observed_lifecycle_seconds.median().median())
                if times.observed_lifecycle_seconds.notna().any() else None),
            summed_observed_lifecycle_seconds=float(times.observed_lifecycle_seconds.sum()),
            maximum_process_memory_bytes=(
                int(times.peak_process_memory_bytes.max())
                if times.peak_process_memory_bytes.notna().any() else None),
            raw_payload_defined_runs=int(counts.N_returned.notna().sum()),
            total_raw_points=int(counts.N_returned.sum()),
            total_feasible_points=int(counts.N_feasible.sum()),
            total_unique_points=int(counts.N_unique.sum()),
            total_native_nd_points=int(counts.N_ND.sum()),
            runs_with_infeasible_raw=int((counts.N_returned > counts.N_feasible).sum()),
            raw_points_above_normalized_one=int(counts.N_above_normalized_one.sum()),
        )
    audit = read_json(OUTPUT/"artifact_audit_official.json")
    values = dict(
        status="DESCRIPTIVE_ONLY", scenarios=27, replicas_per_scenario=5, planned_runs=540,
        aggregation="median of five nested replicas, then descriptive summaries over27 cells",
        statistical_superiority_claim=False, equalized_cardinality=False,
        numerical_source=audit["frozen_scientific_source"], protocol_hash=audit["protocol_hash"],
        source_sha256=file_hash(Path(__file__)), methods=result,
        observed_method_order_status=chronology["status"],
        varimax_nonconverged_runs=sum(r.get("varimax_nonconverged", False) for r in audit["runs"]),
        cnbi_candidate_subsets=sum(r.get("candidate_subsets") or 0 for r in audit["runs"]),
        cnbi_selected_subsets=sum(r.get("selected_subsets") or 0 for r in audit["runs"]),
    )
    write_json(OUTPUT/"release_summary.json", values)
    lines = ["# Descriptive benchmark release tables\n\n",
             "Entries summarize defined structural-cell medians, up to27 cells.\n",
             "Within-cell replicas are nested; defined counts are in release_summary.json.\n",
             "HV precision flags are preserved; this is not statistical inference.\n\n",
             "| Method | Planned | Completed | Failed | Incomplete |\n",
             "|---|---:|---:|---:|---:|\n"]
    for method in METHODS:
        states = result[method]["states"]
        lines.append(f"| {method} | 135 | {states.get('COMPLETED', 0)} | "
                     f"{states.get('FAILED', 0)} | {states.get('INCOMPLETE', 0)} |\n")
    lines.extend(["\n| Method | GD | IGD | HV | Spacing | Sparsity | Native ND | Time(s) |\n",
                  "|---|---:|---:|---:|---:|---:|---:|---:|\n"])
    for method in METHODS:
        row = [result[method]["metrics"][key]["median_of_cell_medians"] for key in quantities[:7]]
        rendered = [f"{value:.8g}" if value is not None else "undefined" for value in row]
        lines.append(f"| {method} | "+" | ".join(rendered)+" |\n")
    (OUTPUT/"release_tables.md").write_bytes("".join(lines).encode())
    return values


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2))
