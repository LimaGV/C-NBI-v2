"""Audit every paired subset, metric replay, ordering barrier and prior file."""

from concurrent.futures import ProcessPoolExecutor, as_completed
from time import perf_counter

import numpy as np
import pandas as pd
from phase10e_pairwise_inputs import (
    COMPARATORS,
    INPUT,
    OUTPUT,
    PARETO,
    PREVIOUS,
    STRUCTURAL,
    name,
    pair_id,
    read,
    verify,
    write,
)

from cnbi_v2.synthetic.analysis.inference import holm
from cnbi_v2.synthetic.analysis.selection import equalized_indices
from cnbi_v2.synthetic.pareto.metrics import evaluate_metrics
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context


def audit_cell(comparator, sid):
    context = load_evaluation_context(PARETO, sid, STRUCTURAL)
    record = read(OUTPUT / f"cell_records/{pair_id(comparator)}/{sid}.json")
    rows = {(r["replica_id"], r["method"], r["variant"]): r for r in record["rows"]}
    checked, recalculated, reused = 0, 0, 0
    previous = {
        (r["replica_id"], r["method"]): r
        for r in read(PREVIOUS / f"cell_records/{sid}.json")["equalized"]
    }
    for replica in range(1, 6):
        sources = {}
        for method in ("C-NBI", comparator):
            run = name(dict(instance_id=f"{sid}__replica{replica}", method=method))
            with np.load(INPUT / f"raw_decisions/{run}.npz", allow_pickle=False) as f:
                x = f["decisions"]
            with np.load(INPUT / f"external_evaluation/{run}.npz", allow_pickle=False) as f:
                z, nd = f["normalized_responses"], f["nondominated_indices"]
            sources[method] = (run, x, z, nd)
        count = min(len(sources[m][3]) for m in sources)
        for method, (run, x, z, nd) in sources.items():
            row = rows[replica, method, "equalized"]
            assert row["K"] == count and row["N_native"] == len(nd)
            with np.load(
                OUTPUT / f"subsets/{pair_id(comparator)}/{run}.npz", allow_pickle=False
            ) as f:
                ids = f["selected_raw_indices"]
                assert len(ids) == count and len(np.unique(ids)) == count
                assert np.isin(ids, nd).all()
                assert np.array_equal(ids, equalized_indices(z[nd], nd, count))
                assert np.array_equal(f["decisions"], x[ids])
                assert np.array_equal(f["normalized"], z[ids])
                assert f["decisions"].dtype == f["normalized"].dtype == np.float64
            original = read(INPUT / f"external_evaluation/{run}.json")["metrics"]
            for metric in ("GD", "IGD", "HV", "Spacing", "Sparsity"):
                assert rows[replica, method, "native"][metric] == original[metric]
            if row["metric_source"] == "identical_complete_native_ND_set":
                assert len(ids) == len(nd) and set(ids) == set(nd)
                expected = original
                reused += 1
            elif row["metric_source"] == "verified_identical_previous_selected_point_set":
                with np.load(PREVIOUS / f"subsets/{run}.npz", allow_pickle=False) as f:
                    assert np.array_equal(ids, f["equalized_raw_indices"])
                expected = previous[replica, method]
                reused += 1
            else:
                expected = evaluate_metrics(z[ids], context.reference_normalized, context.hv)
                recalculated += 1
            for metric in ("GD", "IGD", "HV", "Spacing", "Sparsity", "HV_status"):
                assert row[metric] == expected[metric], (comparator, sid, replica, method, metric)
            checked += 1
    return checked, recalculated, reused


def audit():
    start = perf_counter()
    protected = verify()
    source = pd.read_csv(INPUT / "benchmark_native_metrics.csv")
    cells = sorted(source.scenario_id.unique())
    totals = np.zeros(3, dtype=int)
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(audit_cell, comparator, sid) for comparator in COMPARATORS for sid in cells
        ]
        for future in as_completed(futures):
            totals += future.result()
    assert int(totals[0]) == 810
    frame = pd.read_csv(OUTPUT / "replica_metrics.csv")
    assert (
        len(frame) == 1620
        and not frame.duplicated(
            ["comparator", "scenario_id", "replica_id", "method", "variant"]
        ).any()
    )
    tests = pd.read_csv(OUTPUT / "statistical_tests.csv")
    for _, group in tests.groupby("family", sort=False):
        assert np.array_equal(holm(group.pvalue.to_numpy()), group.p_holm.to_numpy())
    chronology = read(OUTPUT / "execution_chronology.json")
    assert [r["comparator"] for r in chronology] == list(COMPARATORS)
    assert all(
        a["completed_utc"] <= b["started_utc"]
        for a, b in zip(chronology, chronology[1:], strict=False)
    )
    assert verify() == protected
    write(
        OUTPUT / "audit_report.json",
        dict(
            status="PASSED",
            sets=int(totals[0]),
            fresh_metric_replays=int(totals[1]),
            exact_set_cached_metric_checks=int(totals[2]),
            paired_blocks=405,
            protected_previous_files=protected,
            sequential_pair_order=True,
            original_values_unchanged=True,
            real_selected_points_only=True,
            FPS_indices_reproduced=True,
            float64_preserved=True,
            optimization_executions=0,
            wall_seconds=perf_counter() - start,
        ),
    )
    print("Pairwise correction audit PASSED", flush=True)


if __name__ == "__main__":
    audit()
