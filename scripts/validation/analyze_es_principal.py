"""Reuse10E paired analysis; only missing FPS-set metrics are computed."""

import csv
import hashlib
import json
import mmap
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from phase10e_pairwise_inputs import COMPARATORS, INPUT, PARETO, ROOT, STRUCTURAL, pair_id
from phase10e_pairwise_inputs import OUTPUT as PREVIOUS
from phase10e_pairwise_statistics import compare

from cnbi_v2.synthetic.analysis.pairwise import equalized_pair_indices
from cnbi_v2.synthetic.analysis.selection import feasible_nd_indices
from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, write_json
from cnbi_v2.synthetic.domain import radius
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.pareto.metrics import evaluate_metrics
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context

ES = ROOT / "results/phase_10_synthetic_early_stop/gaps_adr0009_20261031_090729"
OUT = ES / "principal_20261031"
METRICS = ("GD", "IGD", "HV", "Spacing", "Sparsity")
CONTEXTS = {}


def context(sid):
    if sid not in CONTEXTS:
        CONTEXTS[sid] = load_evaluation_context(PARETO, sid, STRUCTURAL)
    return CONTEXTS[sid]


def stored(sid, replica, method):
    run = f"official__{sid}__replica{replica}__{method.replace('/', '_')}"
    record = read_json(INPUT / f"external_evaluation/{run}.json")
    with np.load(INPUT / f"external_evaluation/{run}.npz", allow_pickle=False) as data:
        ids = data["nondominated_indices"]
        z = data["normalized_responses"][ids]
    return run, z, ids, record


def prepare(group):
    """Recover missing coordinates for FPS, never recompute native indicators."""
    sid, rows = group
    ctx = context(sid)
    result = []
    for row in rows:
        instance, replica = row["instance_id"], int(row["replica_id"])
        assert row["integrity"] == "PASS"
        assert file_hash(ES / f"raw_decisions/{instance}.npz") == row["ES_decisions_sha256"]
        assert file_hash(ES / f"checkpoints/{instance}.json") == row["ES_checkpoint_sha256"]
        run, oldz, oldids, old = stored(sid, replica, "C-NBI")
        assert (
            file_hash(INPUT / f"external_evaluation/{run}.json") == row["original_metrics_sha256"]
        )
        with np.load(ES / f"raw_decisions/{instance}.npz", allow_pickle=False) as data:
            x = data["decisions"]
        with np.load(INPUT / f"raw_decisions/{run}.npz", allow_pickle=False) as data:
            identical = np.array_equal(x, data["decisions"])
        if identical:
            z, ids = oldz, oldids
        else:
            full = ctx.normalization.transform(evaluate(x, ctx.anchors))
            _, _, ids = feasible_nd_indices(x, full, radius(ctx.scenario.nx), 0.0)
            z = full[ids]
        assert len(ids) == int(float(row["ND_ES"]))
        metrics = {m: float(row[f"{m}_ES"]) if row[f"{m}_ES"] else None for m in METRICS}
        metrics["HV_status"] = row["HV_status_ES"]
        control = {
            m: float(row[f"{m}_original"]) if row[f"{m}_original"] else None for m in METRICS
        }
        control["HV_status"] = row["HV_status_original"]
        result.append(
            dict(
                instance_id=instance,
                scenario_id=sid,
                replica_id=replica,
                nx=ctx.scenario.nx,
                B=int(row["B_effective"]),
                z=z,
                ids=ids,
                metrics=metrics,
                control=control,
                ND_control=int(float(row["ND_original"])),
            )
        )
    return result


def point_key(z):
    values = np.asarray(np.unique(z, axis=0), dtype="<f8")
    return hashlib.sha256(values.tobytes()).hexdigest()


def metric_fields(record):
    return {k: v for k, v in record.items() if k in METRICS or k.startswith("HV_")}


def paired(job):
    comparator, fronts = job
    sid = fronts[0]["scenario_id"]
    ctx = context(sid)
    prior = read_json(PREVIOUS / f"cell_records/{pair_id(comparator)}/{sid}.json")
    native, equalized = [], []
    for front in fronts:
        replica = front["replica_id"]
        cache = {point_key(front["z"]): (front["metrics"], "stored_ES_native")}
        run, z, ids, original = stored(sid, replica, comparator)
        cache[point_key(z)] = (original["metrics"], "stored_comparator_native")
        for method in ("C-NBI", comparator):
            oldrun = f"official__{sid}__replica{replica}__{method.replace('/', '_')}"
            with np.load(PREVIOUS / f"subsets/{pair_id(comparator)}/{oldrun}.npz") as data:
                oldset = data["normalized"]
            metrics = next(
                r
                for r in prior["rows"]
                if r["method"] == method
                and r["replica_id"] == replica
                and r["variant"] == "equalized"
            )
            cache.setdefault(
                point_key(oldset), (metric_fields(metrics), "stored_10E_identical_set")
            )
        K, selected_es, selected_other = equalized_pair_indices(front["z"], front["ids"], z, ids)
        base = {k: front[k] for k in ("instance_id", "scenario_id", "replica_id", "nx", "B")}
        base.update(
            primary_method="C-NBI-ES",
            comparator=comparator,
            K=K,
            ND_ES=len(front["ids"]),
            ND_comparator=len(ids),
            ND_B2000=front["ND_control"],
        )
        n = dict(base)
        for label, metrics in (
            ("ES", front["metrics"]),
            ("comparator", original["metrics"]),
            ("B2000", front["control"]),
        ):
            n.update({f"{label}_{m}": metrics.get(m) for m in METRICS})
            n[f"{label}_HV_status"] = metrics.get("HV_status")
        native.append(n)
        q = dict(base)
        for label, matrix, rawids, selected in (
            ("ES", front["z"], front["ids"], selected_es),
            ("comparator", z, ids, selected_other),
        ):
            lookup = {int(value): i for i, value in enumerate(rawids)}
            subset = matrix[[lookup[int(value)] for value in selected]]
            key = point_key(subset)
            if key in cache:
                metrics, source = cache[key]
            else:
                metrics = evaluate_metrics(subset, ctx.reference_normalized, ctx.hv)
                source = "new_FPS_set_frozen_10C_metrics"
            q.update({f"{label}_{m}": metrics.get(m) for m in METRICS})
            q[f"{label}_HV_status"] = metrics.get("HV_status")
            q[f"{label}_metric_source"] = source
            q[f"{label}_subset_sha256"] = key
            q[f"{label}_ids_sha256"] = hashlib.sha256(selected.tobytes()).hexdigest()
        equalized.append(q)
    return native, equalized


def scalar_fields(path):
    # Read scalar metadata without parsing large, already stored trial arrays.
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        result = {}
        for key, prefix in (
            ("timings", b'\n  "timings": '),
            ("counters", b'\n  "counters": '),
            ("mc", b'\n    "mc_anchor_seconds": '),
        ):
            offset = data.find(prefix)
            result[key] = (
                json.JSONDecoder().raw_decode(
                    data[offset + len(prefix) : offset + len(prefix) + 4096].decode()
                )[0]
                if offset >= 0
                else None
            )
        return result


def cost(front, runtime):
    instance = front["instance_id"]
    meta = scalar_fields(ES / f"algorithm_diagnostics/{instance}.json")
    cp = read_json(ES / f"checkpoints/{instance}.json")
    old = runtime[front["scenario_id"], front["replica_id"]]
    m = front["z"].shape[1]
    row = dict(
        instance_id=instance,
        scenario_id=front["scenario_id"],
        replica_id=front["replica_id"],
        nx=front["nx"],
        B_ES=front["B"],
        B_control=2000,
        ND_ES=len(front["ids"]),
        ND_control=front["ND_control"],
        ND_delta=len(front["ids"]) - front["ND_control"],
    )
    for label, value in (
        ("ES", meta["counters"]["mc_anchor_solves"]),
        ("control", int(float(old["mc_anchor_solves"]))),
    ):
        row[f"MC_anchor_solves_{label}"] = value
    assert row["MC_anchor_solves_ES"] == front["B"] * m
    for label, field in (
        ("preparation", "kernel_preparation_seconds"),
        ("NBI", "kernel_solver_seconds"),
        ("total", "kernel_total_seconds"),
    ):
        newkey = {"NBI": "solver"}.get(label, label)
        row[f"{label}_ES"] = meta["timings"][newkey]
        row[f"{label}_control"] = float(old[field])
        row[f"{label}_delta"] = row[f"{label}_ES"] - row[f"{label}_control"]
    assert row["total_ES"] == cp["kernel_seconds"]
    oldmeta = scalar_fields(INPUT / f"algorithm_diagnostics/official__{instance}__C-NBI.json")
    row.update(
        MC_seconds_ES=meta["mc"],
        MC_seconds_control=oldmeta["mc"],
        subproblems_ES=meta["counters"]["nbi_subproblems"],
        subproblems_control=int(float(old["nbi_subproblems"])),
        total_ratio=row["total_ES"] / row["total_control"],
    )
    return row


def statistics(rows, variant):
    frame = []
    for row in rows:
        for method, label in (("C-NBI", "ES"), (row["comparator"], "comparator")):
            frame.append(
                dict(
                    variant=variant,
                    comparator=row["comparator"],
                    scenario_id=row["scenario_id"],
                    replica_id=row["replica_id"],
                    method=method,
                    **{m: row[f"{label}_{m}"] for m in METRICS},
                    HV_status=row[f"{label}_HV_status"],
                )
            )
    tests, exclusions = [], []
    for family in (("IGD", "HV"), ("GD", "Spacing", "Sparsity")):
        new, _, _, omitted = compare(pd.DataFrame(frame), variant, family)
        for row in new:
            row.update(method_a="C-NBI-ES", pair_id=row["pair_id"].replace("CNBI_vs", "ES_vs"))
        tests.extend(new)
        exclusions.extend(omitted)
    return tests, exclusions


def table(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, list(dict.fromkeys(k for row in rows for k in row)), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def cost_summary(rows):
    return dict(
        cases=len(rows),
        B_median=float(np.median([r["B_ES"] for r in rows])),
        MC_reduction=1
        - sum(r["MC_anchor_solves_ES"] for r in rows)
        / sum(r["MC_anchor_solves_control"] for r in rows),
        kernel_sum_ES=sum(r["total_ES"] for r in rows),
        kernel_sum_control=sum(r["total_control"] for r in rows),
        median_kernel_ratio=float(np.median([r["total_ratio"] for r in rows])),
        median_paired_seconds=float(np.median([r["total_delta"] for r in rows])),
        ND_delta=sum(r["ND_delta"] for r in rows),
        subproblem_delta=sum(r["subproblems_ES"] - r["subproblems_control"] for r in rows),
        MC_solves_ES=sum(r["MC_anchor_solves_ES"] for r in rows),
        MC_solves_control=sum(r["MC_anchor_solves_control"] for r in rows),
        stages={
            stage: dict(
                sum_ES=sum(r[f"{stage}_ES"] for r in rows if r[f"{stage}_ES"] is not None),
                sum_control=sum(
                    r[f"{stage}_control"] for r in rows if r[f"{stage}_control"] is not None
                ),
                median_paired_delta=float(
                    np.median(
                        [
                            r[f"{stage}_ES"] - r[f"{stage}_control"]
                            for r in rows
                            if r[f"{stage}_ES"] is not None and r[f"{stage}_control"] is not None
                        ]
                    )
                ),
            )
            for stage in ("preparation", "MC_seconds", "NBI", "total")
        },
    )


def main():
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    with (ES / "postprocess_20261031/paired_135.csv").open(encoding="utf-8") as stream:
        previous = list(csv.DictReader(stream))
    assert len(previous) == 135 and len({r["instance_id"] for r in previous}) == 135
    policy = read_json(ES / "manifest.json")["policy"]
    assert (policy["minimum_B"], policy["earliest_full_window_B"], policy["maximum_B"]) == (
        300,
        500,
        2000,
    )
    groups = [
        (sid, [r for r in previous if r["scenario_id"] == sid])
        for sid in sorted({r["scenario_id"] for r in previous})
    ]
    assert len(groups) == 27 and all(len(group) == 5 for _, group in groups)
    OUT.mkdir(exist_ok=False)
    with ProcessPoolExecutor(max_workers=4) as pool:
        fronts = list(pool.map(prepare, groups))
        native, equalized = [], []
        for comparator in COMPARATORS:  # Global barriers preserve10E pair order.
            for a, b in pool.map(paired, [(comparator, group) for group in fronts]):
                native.extend(a)
                equalized.extend(b)
    assert len(native) == len(equalized) == 405
    assert all(r["K"] == min(r["ND_ES"], r["ND_comparator"]) for r in equalized)
    table(OUT / "native_comparisons.csv", native)
    table(OUT / "equalized_comparisons.csv", equalized)
    with (INPUT / "benchmark_runtime.csv").open(encoding="utf-8") as stream:
        runtime = {
            (r["scenario_id"], int(r["replica_id"])): r
            for r in csv.DictReader(stream)
            if r["method"] == "C-NBI"
        }
    costs = [cost(front, runtime) for group in fronts for front in group]
    table(OUT / "cost_comparison.csv", costs)
    tests, exclusions = [], []
    for rows, variant in ((native, "native"), (equalized, "equalized")):
        a, b = statistics(rows, variant)
        tests.extend(a)
        exclusions.extend(b)
    summary = dict(
        primary_method="C-NBI-ES",
        fixed_sampling_control="C-NBI-B2000",
        policy=policy,
        authorization="Explicit owner decision: primary for synthetic experiments only",
        native_pairs=405,
        equalized_pairs=405,
        cost_pairs=135,
        integrity="PASS",
        statistics=tests,
        exclusions=exclusions,
        cost=cost_summary(costs),
        cost_by_nx={nx: cost_summary([r for r in costs if r["nx"] == nx]) for nx in (2, 3, 5)},
        metric_sources=dict(
            pd.Series(
                [r[f"{m}_metric_source"] for r in equalized for m in ("ES", "comparator")]
            ).value_counts()
        ),
        previous_results_modified=False,
        new_optimizer_executions=0,
    )
    write_json(OUT / "statistical_summary.json", summary)
    lines = [
        "# Synthetic C-NBI: ES as the primary variant",
        "",
        "By explicit owner decision, ADR0009 spectral-gap ES (minimum B300, first stop500, "
        "cap2000) is the primary synthetic variant; B2000 remains the fixed-sampling control. "
        "The applied case and historical10D/10E records are unchanged.",
        "",
        "Native indicators are reused. Missing objective coordinates/ND membership were "
        "reconstructed only for FPS; indicators were computed only for new selected objective "
        "sets. Each comparator has its own K=min(two ND counts), "
        "frozen FPS/ties and normalization.",
        "",
        "Inference reuses10E exactly: medians of all five replicas in27 structural cells; "
        "conditional paired Wilcoxon, Holm6 for IGD/HV and Holm9 for other indicators separately "
        "per analysis, existing effect sizes and50000 scenario bootstrap draws/seeds. "
        "Intervals are pointwise; analyses remain exploratory.",
        "",
        "|Analysis|Comparator|Metric|Cells|Median ES−comparator|Rank-biserial benefit|Holm p|",
        "|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"|{r['variant']}|{r['comparator']}|{r['metric']}|{r['n_scenarios']}|"
        f"{r['median_difference']:.6g}|{r['rank_biserial']:.4f}|{r['p_holm']:.6g}|"
        for r in tests
        if r["metric"] in ("IGD", "HV")
    )
    for nx, values in [("all", summary["cost"]), *summary["cost_by_nx"].items()]:
        ratio = values["kernel_sum_ES"] / values["kernel_sum_control"]
        lines += [
            "",
            f"nx={nx}: MC anchor solves {100 * values['MC_reduction']:.2f}% fewer; "
            f"kernel sum {ratio:.5f}× control; median per-run ratio "
            f"{values['median_kernel_ratio']:.5f}; ΔND={values['ND_delta']}; "
            f"ΔNBI subproblems={values['subproblem_delta']}.",
        ]
    lines += [
        "",
        "Cost interpretation: fewer Monte Carlo solves do not imply lower total cost. "
        "Timings come from distinct historical campaigns with different scheduling/cache "
        "conditions; ES kernel includes incremental persistence. No global controlled speedup "
        "is established. ND, subproblem counts and NBI stage times are paired in the cost CSV; "
        "worker elapsed boundaries are not conflated with kernel time.",
        "",
        "Integrity:135 input cases,405 independent native pairs and405 equalized pairs. "
        f"Metric/scenario exclusions: {len(exclusions)}; original HV precision flags are retained. "
        "No equalized joint ranking, new hypotheses, reference changes, "
        "optimizers, fits or figures.",
    ]
    lines += [
        "",
        "Stage sums (ES / control; seconds): "
        + "; ".join(
            f"{key} {row['sum_ES']:.3f} / {row['sum_control']:.3f}"
            for key, row in summary["cost"]["stages"].items()
        )
        + ".",
    ]
    (OUT / "report.md").write_bytes(("\n".join(lines) + "\n").encode())
    print(
        json.dumps(dict(status="COMPLETED", native=405, equalized=405, cost=135, output=str(OUT)))
    )


if __name__ == "__main__":
    main()
