"""Sequential comparator blocks; only FPS and frozen offline indicators execute."""

import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from time import perf_counter

import numpy as np
from phase10e_derive import paired_tasks
from phase10e_pairwise_inputs import (
    COMPARATORS,
    INPUT,
    OUTPUT,
    PARETO,
    PREVIOUS,
    ROOT,
    STRUCTURAL,
    digest,
    name,
    pair_id,
    read,
    table,
    verify,
    write,
)

from cnbi_v2.synthetic.analysis.pairwise import equalized_pair_indices
from cnbi_v2.synthetic.pareto.metrics import evaluate_metrics
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context

METRICS = {"GD", "IGD", "HV", "Spacing", "Sparsity", "local_density_status"}


def cell(comparator, sid):
    context = load_evaluation_context(PARETO, sid, STRUCTURAL)
    previous_rows = {
        (r["replica_id"], r["method"]): r
        for r in read(PREVIOUS / f"cell_records/{sid}.json")["equalized"]
    }
    result, diagnostics = [], []
    destination = OUTPUT / "subsets" / pair_id(comparator)
    destination.mkdir(parents=True, exist_ok=True)
    for replica in range(1, 6):
        block = []
        for method in ("C-NBI", comparator):
            task = dict(instance_id=f"{sid}__replica{replica}", method=method)
            run = name(task)
            with np.load(INPUT / f"raw_decisions/{run}.npz", allow_pickle=False) as f:
                x = f["decisions"]
            with np.load(INPUT / f"external_evaluation/{run}.npz", allow_pickle=False) as f:
                z, nd = f["normalized_responses"], f["nondominated_indices"]
            if x.dtype != np.float64 or z.dtype != np.float64:
                raise ValueError("original float64 arrays required")
            original = read(INPUT / f"external_evaluation/{run}.json")["metrics"]
            block.append((method, run, x, z, nd, original))
        count, first, second = equalized_pair_indices(
            block[0][3][block[0][4]], block[0][4], block[1][3][block[1][4]], block[1][4]
        )
        for (method, run, x, z, nd, original), selected in zip(block, (first, second), strict=True):
            base = dict(
                pair_id=pair_id(comparator),
                comparator=comparator,
                scenario_id=sid,
                replica_id=replica,
                method=method,
                K=count,
                N_native=len(nd),
            )
            source = "unchanged_Phase10C_metric_recalculation"
            if len(selected) == len(nd) and np.array_equal(np.sort(selected), np.sort(nd)):
                metrics, source = original, "identical_complete_native_ND_set"
            else:
                previous = previous_rows[replica, method]
                metrics = None
                if previous["K"] == count:
                    with np.load(PREVIOUS / f"subsets/{run}.npz", allow_pickle=False) as f:
                        if np.array_equal(selected, f["equalized_raw_indices"]):
                            if not np.array_equal(z[selected], f["equalized_normalized"]):
                                raise ValueError("previous identical-ID objectives differ")
                            metrics = {
                                k: v
                                for k, v in previous.items()
                                if k in METRICS or k.startswith("HV_")
                            }
                            source = "verified_identical_previous_selected_point_set"
                if metrics is None:
                    metrics = evaluate_metrics(
                        z[selected], context.reference_normalized, context.hv
                    )
            result.extend(
                [
                    dict(**base, variant="native", metric_source="official_Phase10D", **original),
                    dict(**base, variant="equalized", metric_source=source, **metrics),
                ]
            )
            extremes = list(dict.fromkeys(map(int, np.argmin(z[nd], axis=0))))
            diagnostics.append(
                dict(
                    **base,
                    retained_fraction=count / len(nd),
                    distinct_extremes=len(extremes),
                    preserved_extremes=min(count, len(extremes)),
                    extreme_truncation=count < len(extremes),
                    seed=None,
                    rule="objective-order extremes; FPS; first original raw ID",
                )
            )
            payload = dict(
                selected_raw_indices=selected, decisions=x[selected], normalized=z[selected]
            )
            target = destination / f"{run}.npz"
            if target.exists():
                with np.load(target, allow_pickle=False) as existing:
                    if set(existing.files) != set(payload) or any(
                        not np.array_equal(v, existing[k]) for k, v in payload.items()
                    ):
                        raise ValueError("pairwise subset replay mismatch")
            else:
                np.savez_compressed(target, **payload)
    write(
        OUTPUT / "cell_records" / pair_id(comparator) / f"{sid}.json",
        dict(comparator=comparator, scenario_id=sid, rows=result, diagnostics=diagnostics),
    )
    return sid


def derive():
    start = perf_counter()
    protected = verify()
    tasks, blocks = paired_tasks()
    table(OUTPUT / "paired_RSM_inputs.csv", blocks)
    scenarios = sorted({t["scenario_id"] for t in tasks})
    chronology = []
    for comparator in COMPARATORS:
        began = datetime.now(UTC).isoformat()
        with ProcessPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(cell, comparator, sid) for sid in scenarios]
            for future in as_completed(futures):
                print(
                    json.dumps(
                        dict(
                            comparator=comparator,
                            scenario_id=future.result(),
                            status="EQUALIZED_PAIR",
                        )
                    ),
                    flush=True,
                )
        chronology.append(
            dict(
                comparator=comparator,
                started_utc=began,
                completed_utc=datetime.now(UTC).isoformat(),
                scenario_replica_blocks=135,
                subsets=270,
            )
        )
        write(OUTPUT / "execution_chronology.json", chronology)
    records = [read(p) for p in sorted((OUTPUT / "cell_records").rglob("*.json"))]
    rows = [r for record in records for r in record["rows"]]
    table(OUTPUT / "replica_metrics.csv", rows)
    table(
        OUTPUT / "selection_diagnostics.csv",
        [r for record in records for r in record["diagnostics"]],
    )
    write(
        OUTPUT / "derivation_manifest.json",
        dict(
            status="COMPLETED",
            paired_blocks=405,
            selected_sets=810,
            metric_rows=len(rows),
            protected_files_before=protected,
            protected_files_after=verify(),
            optimizer_executions=0,
            refits=0,
            wall_seconds=perf_counter() - start,
            script_sha256=digest(ROOT / "scripts/validation/phase10e_pairwise_derive.py"),
            protocol_sha256=digest(ROOT / "docs/policies/synthetic_analysis_10e_pairwise.json"),
        ),
    )


if __name__ == "__main__":
    derive()
