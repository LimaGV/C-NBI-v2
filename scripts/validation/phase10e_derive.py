"""Secondary subset/feasibility metrics from immutable completed Phase10D runs."""

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from phase10e_inputs import (
    INPUT,
    METHODS,
    OUTPUT,
    PARETO,
    STRUCTURAL,
    digest,
    name,
    read,
    table,
    verify,
    write,
)

from cnbi_v2.synthetic.analysis.selection import equalized_indices, feasible_nd_indices
from cnbi_v2.synthetic.domain import radius
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.pareto.hypervolume import FixedHypervolume
from cnbi_v2.synthetic.pareto.metrics import evaluate_metrics
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context

TOLERANCES = (0.0, 1e-12, 1e-10, 1e-9)


def paired_tasks():
    tasks = [t for t in read(INPUT / "seed_manifest.json")["tasks"] if t["stage"] == "official"]
    keys = [(t["scenario_id"], t["replica_id"], t["method"]) for t in tasks]
    if len(tasks) != 540 or len(set(keys)) != 540:
        raise ValueError("exactly 540 unique official tasks required")
    scenarios = sorted({t["scenario_id"] for t in tasks})
    if len(scenarios) != 27:
        raise ValueError("exactly 27 structural scenarios required")
    pairing = []
    for sid in scenarios:
        for replica in range(1, 6):
            group = [t for t in tasks if t["scenario_id"] == sid and t["replica_id"] == replica]
            if {t["method"] for t in group} != set(METHODS) or len(group) != 4:
                raise ValueError("incomplete method block")
            hashes = set()
            for task in group:
                run = name(task)
                cp = read(INPUT / f"campaign_checkpoints/{run}.json")
                meta = read(INPUT / f"algorithm_diagnostics/{run}.json")
                if cp["identity"] != task or cp["state"] != "COMPLETED":
                    raise ValueError("wrong identity or incomplete official search")
                if (
                    cp["protocol_hash"]
                    != "19dff29411ad39293f4e429f8f77babd424213a5da61baf7e69855c0ea7209cf"
                ):
                    raise ValueError("wrong official protocol")
                coefficient = meta["coefficients_sha256"]
                if coefficient != meta["diagnostics"]["frozen_coefficients_sha256"]:
                    raise ValueError("inconsistent model hashes")
                hashes.add(coefficient)
            if len(hashes) != 1:
                raise ValueError("methods did not consume identical RSMs")
            pairing.append(
                dict(
                    scenario_id=sid,
                    replica_id=replica,
                    methods=4,
                    coefficients_sha256=next(iter(hashes)),
                )
            )
    return tasks, pairing


def cell(sid):
    started = perf_counter()
    context = load_evaluation_context(PARETO, sid, STRUCTURAL)
    alpha = radius(context.scenario.nx)
    tasks = [
        t
        for t in read(INPUT / "seed_manifest.json")["tasks"]
        if t["stage"] == "official" and t["scenario_id"] == sid
    ]
    equalized, sensitivity, supplemental, geometry = [], [], [], []
    destination = OUTPUT / "subsets"
    destination.mkdir(exist_ok=True)
    for replica in range(1, 6):
        block = {}
        for task in sorted(
            (t for t in tasks if t["replica_id"] == replica),
            key=lambda t: METHODS.index(t["method"]),
        ):
            run = name(task)
            with np.load(INPUT / f"raw_decisions/{run}.npz", allow_pickle=False) as f:
                x = f["decisions"]
            with np.load(INPUT / f"external_evaluation/{run}.npz", allow_pickle=False) as f:
                stored = {k: f[k] for k in f.files}
            if x.dtype != np.float64 or stored["normalized_responses"].dtype != np.float64:
                raise ValueError("scientific arrays must remain float64")
            true = evaluate(x, context.anchors)
            z = context.normalization.transform(true)
            if not np.array_equal(true, stored["true_responses"]) or not np.array_equal(
                z, stored["normalized_responses"]
            ):
                raise ValueError("external true-response reproduction mismatch")
            original = read(INPUT / f"external_evaluation/{run}.json")
            block[task["method"]] = (task, x, z, stored, original)
        target_count = min(len(v[3]["nondominated_indices"]) for v in block.values())
        for method, (task, x, z, stored, original) in block.items():
            run = name(task)
            nd = stored["nondominated_indices"]
            ids = equalized_indices(z[nd], nd, target_count)
            metrics = (
                evaluate_metrics(z[ids], context.reference_normalized, context.hv)
                if len(ids)
                else {k: None for k in ("GD", "IGD", "HV", "Spacing", "Sparsity")}
            )
            base = dict(scenario_id=sid, replica_id=replica, method=method)
            extremes = list(dict.fromkeys(map(int, np.argmin(z[nd], axis=0))))
            equalized.append(
                dict(
                    **base,
                    K=target_count,
                    N_native=len(nd),
                    **metrics,
                    analysis="equalized_secondary",
                )
            )
            geometry.append(
                dict(
                    **base,
                    K=target_count,
                    N_native=len(nd),
                    retained_fraction=target_count / len(nd) if len(nd) else None,
                    distinct_extremes=len(extremes),
                    preserved_extremes=min(target_count, len(extremes)),
                    extreme_truncation=target_count < len(extremes),
                    seed=None,
                    tie="first raw row ID; objective-order forced extremes",
                )
            )
            payload = dict(
                equalized_raw_indices=ids, equalized_decisions=x[ids], equalized_normalized=z[ids]
            )
            cache = {tuple(nd): original["metrics"]}
            norms = np.linalg.norm(x, axis=1)
            for index, epsilon in enumerate(TOLERANCES):
                feasible, unique, candidate_nd = feasible_nd_indices(x, z, alpha, epsilon)
                if epsilon == 0 and (
                    not np.array_equal(feasible, stored["feasible_mask"])
                    or not np.array_equal(unique, stored["unique_indices"])
                    or not np.array_equal(candidate_nd, nd)
                ):
                    raise ValueError("epsilon zero must reproduce the official strict selection")
                key = tuple(candidate_nd)
                reused = key in cache
                if not reused:
                    cache[key] = evaluate_metrics(
                        z[candidate_nd], context.reference_normalized, context.hv
                    )
                sensitivity.append(
                    dict(
                        **base,
                        epsilon=epsilon,
                        N_raw=len(x),
                        N_feasible=int(feasible.sum()),
                        N_unique=len(unique),
                        N_ND=len(candidate_nd),
                        **cache[key],
                        reused_metrics_for_identical_ND=reused,
                        maximum_norm_excess=float(max(0.0, (norms - alpha).max())),
                    )
                )
                payload[f"epsilon_{index}_nd_raw_indices"] = candidate_nd
            path = destination / f"{run}.npz"
            if path.exists():
                with np.load(path, allow_pickle=False) as existing:
                    if set(existing.files) != set(payload) or any(
                        not np.array_equal(existing[k], v) for k, v in payload.items()
                    ):
                        raise ValueError("derived subset replay mismatch: " + run)
            else:
                np.savez_compressed(path, **payload)
            if original["metrics"]["HV_status"] == "PRECISION_PENDING":
                for power in (18, 20):
                    hv = FixedHypervolume(context.scenario.m, context.hv.master_seed, power)
                    study = hv.study(z[nd])
                    for row in study:
                        supplemental.append(
                            dict(
                                **base,
                                supplementary_max_power=power,
                                original_HV=original["metrics"]["HV"],
                                original_status="PRECISION_PENDING",
                                **row,
                            )
                        )
    result = dict(
        scenario_id=sid,
        equalized=equalized,
        feasibility=sensitivity,
        hv_supplement=supplemental,
        selection=geometry,
        analysis_seconds=perf_counter() - started,
    )
    write(OUTPUT / f"cell_records/{sid}.json", result)
    return sid


def derive(workers=4):
    started = perf_counter()
    protected = verify()
    tasks, pairing = paired_tasks()
    table(OUTPUT / "paired_inputs.csv", pairing)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(cell, sid) for sid in sorted({t["scenario_id"] for t in tasks})]
        for future in as_completed(futures):
            print(json.dumps(dict(scenario=future.result(), status="DERIVED")), flush=True)
    records = [read(p) for p in sorted((OUTPUT / "cell_records").glob("*.json"))]
    for field, filename in (
        ("equalized", "equalized_replica_metrics.csv"),
        ("feasibility", "feasibility_replica_metrics.csv"),
        ("hv_supplement", "hv_supplement_precision.csv"),
        ("selection", "equalization_diagnostics.csv"),
    ):
        table(OUTPUT / filename, [row for record in records for row in record[field]])
    correlations = pd.read_csv(
        STRUCTURAL / "synthetic_correlations.csv", float_precision="round_trip"
    )
    metrics = pd.read_csv(INPUT / "benchmark_native_metrics.csv", float_precision="round_trip")
    runtime = pd.read_csv(INPUT / "benchmark_runtime.csv", float_precision="round_trip")
    keys = ["scenario_id", "replica_id", "method"]
    merged = metrics.merge(runtime.drop(columns=["state"]), on=keys, validate="one_to_one")
    merged = merged.merge(
        correlations[["scenario_id", "rho_abs_realized", "rho_signed"]],
        on="scenario_id",
        validate="many_to_one",
    )
    merged.to_csv(OUTPUT / "native_replica_metrics.csv", index=False, lineterminator="\n")
    write(
        OUTPUT / "derivation_manifest.json",
        dict(
            status="COMPLETED",
            official_runs=len(tasks),
            pairing_blocks=len(pairing),
            protected_files_before=protected,
            protected_files_after=verify(),
            raw_values_reproduced_exactly=True,
            epsilon_zero_matches_official=True,
            workers=workers,
            optimization_executions=0,
            wall_seconds=perf_counter() - started,
            script_sha256=digest(Path(__file__)),
            numerical_threads={
                k: os.environ.get(k)
                for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
            },
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    derive(args.workers)
