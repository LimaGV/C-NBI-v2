"""Offline descriptive tables/figures from preserved runs; never search or tune."""

import argparse
import csv
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from execute_synthetic_benchmark import OUTPUT, run_id

from cnbi_v2.synthetic.benchmark.archive import read_json, write_json
from cnbi_v2.synthetic.benchmark.contracts import METHODS, PILOT_SCENARIOS

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

COLORS = dict(zip(METHODS, ("#0072B2", "#D55E00", "#009E73", "#CC79A7"), strict=True))


def export(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    columns = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tables(directory: Path) -> pd.DataFrame:
    metrics, counts, runtimes, precision, failures = [], [], [], [], []
    tasks = [task for task in read_json(directory/"seed_manifest.json")["tasks"]
             if task["stage"] == "official"]
    for task in tasks:
        name, sid = run_id(task), task["scenario_id"]
        nx, delta, rho = sid.split("_")
        base = dict(scenario_id=sid, replica_id=task["replica_id"], method=task["method"],
                    nx=int(nx[2:]), delta=int(delta[5:]), rho=float(rho[3:])/100)
        base["m"] = base["nx"]+base["delta"]+1
        path = directory/f"campaign_checkpoints/{name}.json"
        cp = read_json(path) if path.exists() else dict(state="PENDING")
        payload = cp.get("payload_run_id", name)
        meta_path = directory/f"algorithm_diagnostics/{payload}.json"
        external_path = directory/f"external_evaluation/{name}.json"
        metadata = read_json(meta_path) if meta_path.exists() else {}
        external = read_json(external_path) if external_path.exists() else {}
        values, diagnostic = external.get("metrics", {}), external.get("diagnostics", {})
        status = cp.get("algorithm_status", cp["state"])
        metrics.append(dict(**base, state=cp["state"], algorithm_status=status, **values))
        counts.append(dict(**base, state=cp["state"], N_returned=diagnostic.get("raw_count"),
                           N_feasible=diagnostic.get("feasible_count"),
                           N_unique=diagnostic.get("unique_count"),
                           N_ND=diagnostic.get("nondominated_count"),
                           N_above_normalized_one=diagnostic.get("above_normalized_one")))
        times, counters = metadata.get("timings", {}), metadata.get("counters", {})
        total = metadata.get("input_load_plus_search_seconds")
        kernel = times.get("total")
        runtime = dict(**base, state=cp["state"], end_to_end_seconds=total,
                       kernel_preparation_seconds=times.get("preparation"),
                       kernel_solver_seconds=times.get("solver"),
                       kernel_postprocessing_seconds=times.get("postprocessing"),
                       kernel_total_seconds=kernel,
                       measured_load_validation_metadata_overhead_seconds=(total-kernel)
                       if total is not None and kernel is not None else None,
                       external_evaluation_seconds=external.get("external_evaluation_seconds"),
                       peak_process_memory_bytes=metadata.get("peak_process_memory_bytes"),
                       **counters)
        runtimes.append(runtime)
        precision.append(dict(**base, HV=values.get("HV"), HV_SE=values.get("HV_SE"),
                              HV_status=values.get("HV_status", "UNDEFINED_NO_EVALUATION"),
                              HV_method=values.get("HV_method"),
                              precision_protocol="Phase10C_frozen_four_scrambles_2^16_or_exact"))
        failures.append(dict(**base, state=cp["state"], algorithm_status=status,
                             error=cp.get("error"), attempt=cp.get("attempt", 0),
                             undefined_metrics=external.get("metrics", {}).get("status"),
                             maximum_raw_sphere_violation=diagnostic.get("maximum_sphere_violation")))
    export(directory/"benchmark_cardinalities.csv", counts)
    export(directory/"benchmark_runtime.csv", runtimes)
    export(directory/"benchmark_hv_precision.csv", precision)
    export(directory/"benchmark_failures.csv", failures)
    # Keep the evaluator's detailed primary table unchanged; this aligned table
    # includes PENDING/FAILED tasks as well, without manufacturing their metrics.
    export(directory/"benchmark_task_metrics.csv", metrics)
    keys = ["scenario_id", "replica_id", "method", "nx", "delta", "rho", "m", "state"]
    frame = pd.DataFrame(metrics).merge(pd.DataFrame(counts), on=keys)
    frame = frame.merge(pd.DataFrame(runtimes), on=keys)
    quantities = ["GD", "IGD", "HV", "Spacing", "Sparsity", "N_ND", "end_to_end_seconds"]
    summaries = []
    for group, data in frame.groupby(["scenario_id", "method", "nx", "m", "delta", "rho"]):
        for metric in quantities:
            values = data[metric].dropna().to_numpy(dtype=float) if metric in data else np.array([])
            summaries.append(dict(
                scenario_id=group[0], method=group[1], nx=group[2], m=group[3], delta=group[4],
                rho=group[5], aggregation_unit="structural_cell_with_five_nested_replicas",
                metric=metric, planned_replicas=5, defined_replicas=len(values),
                median=float(np.median(values)) if len(values) else None,
                q25=float(np.quantile(values, .25)) if len(values) else None,
                q75=float(np.quantile(values, .75)) if len(values) else None,
                minimum=float(np.min(values)) if len(values) else None,
                maximum=float(np.max(values)) if len(values) else None,
            ))
    export(directory/"benchmark_summary.csv", summaries)
    write_json(directory/"descriptive_report.json", dict(
        planned_runs=540, recorded_runs=len(frame),
        statuses={str(k): int(v) for k, v in frame.groupby(["method", "state"]).size().items()},
        inferential_tests=False, equalization=False, retuning=False,
        primary_cardinality="native_true_full_objective_ND",
        timing="end_to_end_per_run_under_archived_hardware_concurrency",
        figures_use="structural_cell_medians; five replicas are nested, not independent cells",
    ))
    return frame


def figures(directory: Path, frame: pd.DataFrame) -> None:
    plt.rcParams.update({"font.size": 8, "axes.grid": False, "font.family": "DejaVu Sans",
                         "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False})
    out = directory/"figures"
    out.mkdir(exist_ok=True)
    numeric = [name for name in ("GD", "IGD", "HV", "Spacing", "Sparsity", "N_ND",
                                "end_to_end_seconds") if name in frame]
    cells = frame.groupby(["scenario_id", "method", "nx", "m"])[numeric].median().reset_index()

    def save(fig, name):
        fig.savefig(out/f"{name}.png", dpi=600, bbox_inches="tight")
        fig.savefig(out/f"{name}.pdf", bbox_inches="tight")
        plt.close(fig)

    def scatter(ax, x, y, ylabel, logarithmic=False):
        for i, method in enumerate(METHODS):
            data = cells[cells.method.eq(method)]
            if y in data:
                ax.scatter(data[x]+(i-1.5)*.055, data[y], s=13, color=COLORS[method],
                           label=method, alpha=.8, edgecolors="none")
        ax.set(xlabel="Number of objectives" if x == "m" else "Decision-space dimension",
               ylabel=ylabel)
        if logarithmic:
            ax.set_yscale("log")
        ax.grid(False)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3), layout="constrained")
    scatter(axes[0], "m", "IGD", "IGD (true normalized objectives)", True)
    scatter(axes[1], "nx", "IGD", "IGD (true normalized objectives)", True)
    axes[0].legend(frameon=False, fontsize=7)
    save(fig, "igd_by_structure")
    for name, quantity, label, log in (
        ("gd_by_objectives", "GD", "GD (true normalized objectives)", True),
        ("hypervolume_by_objectives", "HV", "Hypervolume (fixed reference 1.1)", False),
        ("end_to_end_runtime", "end_to_end_seconds", "End-to-end runtime (s)", True),
        ("native_nd_cardinality", "N_ND", "Native ND cardinality", True),
    ):
        fig, ax = plt.subplots(figsize=(5.4, 3.3), layout="constrained")
        scatter(ax, "m", quantity, label, log)
        if quantity == "HV":
            ax.set_title("Estimates shown; per-run precision flags archived", fontsize=8)
        ax.legend(frameon=False, ncol=2, fontsize=7)
        save(fig, name)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3), layout="constrained")
    scatter(axes[0], "m", "Spacing", "Spacing (sample SD, ddof=1)")
    scatter(axes[1], "m", "Sparsity", "Sparsity (mean nearest-neighbor distance)")
    axes[0].legend(frameon=False, fontsize=7)
    save(fig, "density_spacing_sparsity")
    fig, ax = plt.subplots(figsize=(5.8, 3.2), layout="constrained")
    bottom = np.zeros(4)
    for state, color in (("COMPLETED", "#009E73"), ("FAILED", "#D55E00"),
                         ("INCOMPLETE", "#E69F00"), ("PENDING", "#999999")):
        values = [int(np.sum(frame.method.eq(method)&frame.state.eq(state))) for method in METHODS]
        ax.bar(METHODS, values, bottom=bottom, label=state, color=color)
        bottom += values
    ax.set(ylabel="Number of planned runs", ylim=(0, 145))
    ax.legend(frameon=False, ncol=2, fontsize=7)
    save(fig, "run_outcomes")
    fig, ax = plt.subplots(figsize=(5.6, 3.4), layout="constrained")
    for method in METHODS:
        data = cells[cells.method.eq(method)]
        if "IGD" in data:
            ax.scatter(data.end_to_end_seconds, data.IGD, label=method,
                       color=COLORS[method], s=17, alpha=.8)
    ax.set(xscale="log", yscale="log", xlabel="Median end-to-end runtime per cell (s)",
           ylabel="Median IGD per cell")
    ax.legend(frameon=False, fontsize=7)
    save(fig, "quality_cost")
    fig, axes = plt.subplots(1, 3, figsize=(9, 3.1), layout="constrained")
    for sid, ax in zip(PILOT_SCENARIOS, axes, strict=True):
        for method in METHODS:
            task = dict(stage="official", instance_id=sid+"__replica1", method=method)
            path = directory/f"external_evaluation/{run_id(task)}.npz"
            if not path.exists():
                continue
            with np.load(path, allow_pickle=False) as arrays:
                z = arrays["normalized_responses"][arrays["nondominated_indices"]]
            if len(z):
                for line in z:
                    ax.plot(np.arange(1, len(line)+1), line, color=COLORS[method],
                            alpha=.13, lw=.5)
        ax.set(title=sid.replace("_", " "), xlabel="Original objective index",
               ylabel="True normalized objective")
        ax.grid(False)
    fig.suptitle("Preselected replica1 cases — all native ND lines", fontsize=9)
    fig.legend([Line2D([], [], color=COLORS[m]) for m in METHODS], METHODS,
               loc="outside lower center", ncol=4, frameon=False, fontsize=8)
    save(fig, "representative_parallel_coordinates")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    parser.add_argument("--figures", action="store_true")
    args = parser.parse_args()
    frame = tables(args.directory)
    if args.figures:
        figures(args.directory, frame)
