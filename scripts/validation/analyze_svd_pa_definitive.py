"""FILTER/RANDOM reuse; ALL is recomposed from complete local candidate sets."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from complete_svd_pa_all import OUT, PLAN, PREVIOUS, ROOT, cache
from run_phase10f_focused_ablation import ES, PARETO, SOURCE, STRUCTURAL

from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, write_json
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context

METRICS = ("GD", "IGD", "HV", "Spacing", "Sparsity")


def read_exact_csv(path):
    """Use Python's decimal-to-float round trip for stored scientific values."""
    with path.open(encoding="utf-8", newline="") as stream:
        records = list(csv.DictReader(stream))
    for row in records:
        for name, value in row.items():
            try:
                row[name] = float(value) if value else None
            except ValueError:
                pass
    return pd.DataFrame(records)


def universe_names(instance):
    u = PLAN["plans"][instance]["universe"]
    return sorted(u, key=lambda s: (len(u[s]), u[s]))


def local_records(instance, names):
    return [read_json(cache(instance, s) / "record.json") for s in names]


def evaluate_all(instance, context):
    folder = OUT / "instances" / instance
    done = folder / "ALL_evaluation.json"
    if done.exists():
        d = read_json(done)
        assert file_hash(folder / "ALL_candidates.npz") == d["payload_sha256"]
        return d
    p = PLAN["plans"][instance]
    names = universe_names(instance)
    tick = perf_counter()
    points = []
    origins = []
    weights = []
    for s in names:
        path = cache(instance, s)
        r = read_json(path / "record.json")
        x = np.load(path / "decisions.npz")["decisions"]
        points.append(x)
        origins.extend([s] * len(x))
        weights.extend(r["weights"])
    x = np.vstack(points)
    recomposition_seconds = perf_counter() - tick
    # No previously computed ND front is an input to this evaluation.
    tick = perf_counter()
    result = context.evaluate(
        p["scenario_id"],
        p["replica_id"],
        "C-NBI",
        x,
        dict(variant="ALL", B_effective=p["B"], complete_local_union=True),
    )
    evaluation_seconds = perf_counter() - tick
    np.savez_compressed(
        folder / "ALL_candidates.npz",
        raw_decisions=x,
        true_responses=result.true_responses,
        normalized_responses=result.normalized_responses,
        feasible_mask=result.feasible_mask,
        unique_indices=result.unique_indices,
        nondominated_indices=result.nondominated_indices,
        source_subsets=np.array(origins),
        source_weights=np.array(weights),
    )
    d = dict(
        metrics=result.metrics,
        ND=len(result.nondominated_indices),
        raw_cardinality=len(x),
        feasible_cardinality=int(result.feasible_mask.sum()),
        unique_cardinality=len(result.unique_indices),
        recomposition_seconds_observed=recomposition_seconds,
        external_evaluation_seconds_observed=evaluation_seconds,
        B_effective=p["B"],
        subsets=len(names),
        payload_sha256=file_hash(folder / "ALL_candidates.npz"),
    )
    write_json(done, d)
    return d


def assemble(nx):
    original = read_exact_csv(PREVIOUS / "ablation_results.csv")
    rows = []
    costs = []
    for cell in PLAN["selected_scenarios"]:
        if cell["nx"] not in nx:
            continue
        sid = cell["scenario_id"]
        context = load_evaluation_context(SOURCE / PARETO, sid, SOURCE / STRUCTURAL)
        for replica in range(1, 6):
            instance = f"{sid}__replica{replica}"
            p = PLAN["plans"][instance]
            all_result = evaluate_all(instance, context)
            before = original[(original.scenario_id == sid) & (original.replica_id == replica)]
            base = before[before.variant == "A0"].iloc[0]
            blocks = []
            for v, seed, names in [
                ("FILTER", 0, p["A0"]),
                *[("RANDOM", int(seed), d["subsets"]) for seed, d in p["A2"].items()],
                ("ALL", 0, universe_names(instance)),
            ]:
                if v == "ALL":
                    metrics = all_result["metrics"]
                    counts = all_result
                else:
                    o = before[
                        (before.variant == ("A0" if v == "FILTER" else "A2"))
                        & (before.random_seed == seed)
                    ].iloc[0]
                    metrics = o.to_dict()
                    counts = o.to_dict()
                r = dict(
                    variant=v,
                    scenario_id=sid,
                    replica_id=replica,
                    random_seed=seed,
                    nx=cell["nx"],
                    B_effective=p["B"],
                    ND=counts["ND"],
                    subsets=len(names),
                    raw_cardinality=counts["raw_cardinality"],
                    HV_status=metrics["HV_status"],
                    metric_source="FROZEN_10C_ALL_COMPLETE_UNION"
                    if v == "ALL"
                    else "EXISTING_METRICS",
                )
                for k in METRICS:
                    value = metrics[k]
                    r[k] = value
                    r[k + "_delta_FILTER"] = value - base[k] if value is not None else None
                    r[k + "_relative_FILTER_pct"] = (
                        100 * (value / base[k] - 1) if value is not None and base[k] != 0 else None
                    )
                local = local_records(instance, names)
                r["subproblems"] = sum(len(g["subproblems"]) for g in local)
                r["ND_delta_FILTER"] = r["ND"] - base.ND
                r["counts_by_k"] = json.dumps(dict(Counter(len(p["universe"][s]) for s in names)))
                rows.append(r)
                blocks.append(r)
                known = [g for g in local if g.get("counters") is not None]
                added = [g for g in local if g["source"] == "NEW_ALL"]
                times = {
                    origin: sum(
                        g.get("solver_seconds") or 0 for g in known if g["source"] == origin
                    )
                    for origin in {g["source"] for g in known}
                }
                historical = read_json(SOURCE / ES / "algorithm_diagnostics" / (instance + ".json"))
                c = dict(
                    variant=v,
                    scenario_id=sid,
                    replica_id=replica,
                    random_seed=seed,
                    B_effective=p["B"],
                    subsets=len(names),
                    subproblems=r["subproblems"],
                    accepted_subproblems=sum(
                        s["accepted"] for g in local for s in g["subproblems"]
                    ),
                    nbi_attempts=sum(g["attempts"] for g in local),
                    nbi_iterations=sum(g["iterations"] for g in local),
                    solver_seconds_observed_by_origin_nonadditive=json.dumps(times),
                    counter_known_subsets=len(known),
                    counter_unknown_subsets=len(local) - len(known),
                    known_local_value_calls_partial=sum(
                        g["counters"].get("scalar_quadratic_values", 0) for g in known
                    ),
                    known_local_gradient_calls_partial=sum(
                        g["counters"].get("scalar_quadratic_gradients", 0) for g in known
                    ),
                    new_ALL_subsets=len(added),
                    new_ALL_solver_seconds_observed=sum(g["solver_seconds"] for g in added),
                    shared_preparation_seconds_historical=historical["timings"]["preparation"],
                    full_pipeline_seconds_observed_historical=historical["timings"]["total"]
                    if v == "FILTER"
                    else None,
                    full_pipeline_seconds_estimated=None,
                    recomposition_seconds_observed=all_result["recomposition_seconds_observed"]
                    if v == "ALL"
                    else None,
                    evaluation_seconds_observed=all_result["external_evaluation_seconds_observed"]
                    if v == "ALL"
                    else None,
                    new_MC_draws=0,
                    new_anchor_solves=0,
                    cost_basis="Observed components from identified campaigns; "
                    "no full RANDOM/ALL timing or allocation-model speedup",
                )
                costs.append(c)
            write_json(OUT / "instances" / instance / "comparison.json", blocks)
        print("Evaluated:", sid, flush=True)
    return pd.DataFrame(rows), pd.DataFrame(costs)


def summarize(rows):
    fields = [
        *METRICS,
        "ND",
        "subsets",
        "subproblems",
        *[m + "_relative_FILTER_pct" for m in METRICS],
    ]
    nested = rows.groupby(["variant", "scenario_id", "replica_id"])[fields].mean().reset_index()
    summary = nested.groupby(["variant", "scenario_id"])[fields].median().reset_index()
    random = rows[rows.variant == "RANDOM"]
    variability = random.groupby(["scenario_id", "replica_id"])[["IGD", "HV"]].agg(
        ["std", "min", "max"]
    )
    for metric in ("IGD", "HV"):
        for stat in ("std", "min", "max"):
            values = variability[(metric, stat)].groupby("scenario_id").mean()
            summary[f"{metric}_random_seed_{stat}_mean"] = summary.scenario_id.map(values).where(
                summary.variant == "RANDOM"
            )
    macro = summary.groupby("variant")[fields].median().reset_index()
    macro["scenario_id"] = "FOCUSED_SCENARIO_MEDIANS"
    return pd.concat([summary, macro], ignore_index=True)


def write_report(rows, costs, summary):
    focus = summary[summary.scenario_id == "FOCUSED_SCENARIO_MEDIANS"]
    focus = focus.set_index("variant").loc[["FILTER", "RANDOM", "ALL"]].reset_index()
    lines = [
        "# Definitive SVD + PA filter ablation",
        "",
        "Only FILTER, RANDOM and ALL are compared. FILTER is the existing C-NBI-ES A0; "
        "RANDOM reuses all three existing A2 draws with the same per-k subset counts. "
        "ALL uses every admissible subset. The four cost-selected scenarios and all five "
        "original replicas are unchanged. This is a focused exploratory study; "
        "it does not support27-cell inference.",
        "",
        "|Arm|IGD change vs FILTER (%)|HV change (%)|ND median|Subsets median|"
        "NBI subproblems median|",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in focus.to_dict("records"):
        lines.append(
            f"|{r['variant']}|{r['IGD_relative_FILTER_pct']:.3f}|{r['HV_relative_FILTER_pct']:.3f}|"
            f"{r['ND']:.1f}|{r['subsets']:.1f}|{r['subproblems']:.1f}|"
        )
    totals = rows.groupby(["variant", "scenario_id", "replica_id"])[
        ["subsets", "subproblems"]
    ].mean()
    total_all = totals.loc["ALL"].sum()
    total_filter = totals.loc["FILTER"].sum()
    f = focus.set_index("variant")
    lines += [
        "",
        f"At the same per-k budgets, RANDOM changes focused IGD by "
        f"{f.loc['RANDOM', 'IGD_relative_FILTER_pct']:.3f}% and HV by "
        f"{f.loc['RANDOM', 'HV_relative_FILTER_pct']:.3f}%. ALL changes IGD by "
        f"{f.loc['ALL', 'IGD_relative_FILTER_pct']:.3f}% and HV by "
        f"{f.loc['ALL', 'HV_relative_FILTER_pct']:.3f}%. FILTER requests "
        f"{total_filter.subproblems:.0f} versus {total_all.subproblems:.0f} NBI "
        f"subproblems ({100 * (1 - total_filter.subproblems / total_all.subproblems):.2f}% fewer). "
        "This is an exact effort comparison, not measured runtime savings.",
    ]
    lines += [
        "",
        "Quality entries are medians of scenario medians of paired changes. RANDOM "
        "first averages the three draws within each scenario/replica. Its three seed-level "
        "rows remain separate in ablation_results.csv, and within-replica SD/range summaries "
        "remain in ablation_summary.csv. No seed is treated as another structural scenario.",
        "",
        "## Design, compatibility and complete ALL reconstruction",
        "",
        "All three arms share the exact model, nominal payoff/anchors, consumed uncertainty "
        "prefix and effective B of FILTER. No ES-versus-fixed-B comparison is performed. "
        "The stopping time is matched, not re-adapted to the random draw or ALL membership.",
        "The477 previous local caches were checked before reuse: frozen coefficient hashes, "
        "payoff/anchors, local geometry, H, objective directions, solver defaults/tolerances, "
        "library versions and mathematical kernel bytes/AST. Historical cache points match "
        "their source records; accepted weights satisfy the unchanged NBI residual/ball checks. "
        "The original source and a byte-identical historical result copy remain available.",
        "The universe has855 admissible instance/subset pairs. Only378 missing subsets "
        "(13208 NBI subproblems) were solved: nx=2 first (50/975), then nx=3 (328/12233) "
        "after the nx=2 integrity and measured-cost gate. Per-subset and per-instance "
        "checkpoints permit resumption without repeating completed solves.",
        "ALL_candidates.npz contains the complete concatenation of accepted local candidates "
        "with subset/weight origins. ALL nondominance is rebuilt from that raw union via the "
        "unchanged10C evaluator, never from another arm's ND front. FILTER/RANDOM metrics "
        "are reused. The same5000-point references, normalization, strict feasibility, "
        "duplicate/dominance tolerances, indicators and HV precision rules are retained.",
        "",
        "## Cost and interpretation limits",
        "",
        "New solver times and function/gradient/internal-solve counters are observed for "
        "the missing complement and reported per instance. Cached component times retain "
        "their source campaign; known counters are explicitly partial when older local "
        "instrumentation did not record them. Shared cached work is nonadditive across "
        "random seeds. A full fresh RANDOM/ALL pipeline runtime was not observed.",
        "No allocation-model time saving is claimed. Exact subset, NBI-attempt and candidate "
        "counts describe effort; they do not prove wall-clock speedup. FILTER versus RANDOM "
        "isolates selection at matched per-k budgets. FILTER versus ALL also changes "
        "candidate/ND cardinality, so it cannot isolate geometry from the benefit of more "
        "candidates. Solver rejections remain recorded rather than replaced with points.",
        "The previous A1/A3 analyses are historical only; their caches remain available. "
        "No CCD, noise, RSM fit, MC sample, anchor/payoff optimization, reference, applied-case "
        "or MaF experiment was generated or changed.",
        "",
        "## Scenario results",
        "",
        "|Scenario|Arm|IGD|HV|IGD change (%)|HV change (%)|",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in summary[summary.scenario_id != "FOCUSED_SCENARIO_MEDIANS"].to_dict("records"):
        lines.append(
            f"|{r['scenario_id']}|{r['variant']}|{r['IGD']:.6g}|{r['HV']:.6g}|"
            f"{r['IGD_relative_FILTER_pct']:.3f}|{r['HV_relative_FILTER_pct']:.3f}|"
        )
    ledger = []
    for nx in (2, 3):
        path = OUT / f"nx{nx}_gate.json"
        if path.exists():
            gate = read_json(path)
            ledger.append(
                dict(
                    nx=nx,
                    wall_seconds_observed=gate["wall_seconds_this_invocation"],
                    added_subsets=sum(r["added_subsets"] for r in gate["instances"]),
                    added_solver_seconds_observed=sum(
                        r["added_solver_seconds_observed"] for r in gate["instances"]
                    ),
                )
            )
    records = [read_json(p) for p in (OUT / "subset_cache").glob("*/*/record.json")]
    counters = Counter()
    for r in records:
        counters.update(r["counters"])
    rejected = sum(not s["accepted"] for r in records for s in r["subproblems"])
    write_json(
        OUT / "execution_summary.json",
        dict(
            stages=ledger,
            unique_added_subsets=len(records),
            requested_new_subproblems=sum(len(r["subproblems"]) for r in records),
            rejected_new_weights=rejected,
            profiled_local_kernel_counters=dict(counters),
            new_MC_draws=0,
            new_anchor_solves=0,
            workers=4,
            threads_per_worker=1,
            note="Stage wall times and sums of local solver elapsed times "
            "are separate measured quantities",
        ),
    )
    lines += [
        "",
        "## Observed execution ledger",
        "",
        "|Stage|Added subsets|Observed stage wall (s)|Sum of observed added solver times (s)|",
        "|---|---:|---:|---:|",
    ]
    for r in ledger:
        lines.append(
            f"|nx={r['nx']}|{r['added_subsets']}|{r['wall_seconds_observed']:.4f}|"
            f"{r['added_solver_seconds_observed']:.4f}|"
        )
    lines += [
        "",
        f"Four numerical workers (one BLAS thread each) completed {len(records)} added "
        f"subsets. {rejected} local weights were rejected and retained in diagnostics. "
        f"The profiled local routines recorded {counters['scalar_quadratic_values']} scalar "
        f"quadratic value calls, {counters['scalar_quadratic_gradients']} analytic gradient "
        f"calls and {counters['slsqp_solves']} internal SLSQP solves. Counts include local "
        "geometry preparation where instrumented. The timing ledger measures only the "
        "missing complement and validation, not a fresh full ALL pipeline.",
    ]
    (OUT / "ABLATION_REPORT.md").write_text(
        "\n".join(s if not s or s.startswith(("|", "#")) else s + "\n" for s in lines).rstrip()
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def figures(rows, summary):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    order = ["FILTER", "RANDOM", "ALL"]
    colors = ["#264653", "#e9c46a", "#e76f51"]
    focus = (
        summary[summary.scenario_id == "FOCUSED_SCENARIO_MEDIANS"].set_index("variant").loc[order]
    )
    effort = rows.groupby(["variant", "scenario_id", "replica_id"])[
        ["subsets", "subproblems"]
    ].mean()
    effort = effort.groupby("variant").sum().loc[order]
    plt.rcParams.update(
        {"font.family": "DejaVu Serif", "font.size": 9, "axes.grid": False, "pdf.fonttype": 42}
    )
    folder = OUT / "figures"
    folder.mkdir(exist_ok=True)

    def save(fig, name):
        fig.savefig(folder / (name + ".png"), dpi=600, bbox_inches="tight")
        fig.savefig(folder / (name + ".pdf"), bbox_inches="tight")
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7, 3), layout="constrained")
    for ax, m in zip(axes, ["IGD", "HV"], strict=True):
        ax.bar(order, focus[m + "_relative_FILTER_pct"], color=colors)
        ax.axhline(0, color="black", lw=0.5)
        ax.set(ylabel=m + " change vs FILTER (%)", title=m + " quality")
    save(fig, "quality_by_arm")
    fig, axes = plt.subplots(1, 2, figsize=(7, 3), layout="constrained")
    for ax, field in zip(axes, ["subsets", "subproblems"], strict=True):
        ax.bar(order, effort[field], color=colors)
        ax.set(ylabel="Total " + field, title="Exact requested effort")
    save(fig, "effort_by_arm")
    fig, axes = plt.subplots(1, 2, figsize=(7, 3), layout="constrained")
    for ax, m in zip(axes, ["IGD", "HV"], strict=True):
        for i, v in enumerate(order):
            x = 100 * effort.loc[v, "subproblems"] / effort.loc["FILTER", "subproblems"]
            y = focus.loc[v, m + "_relative_FILTER_pct"]
            ax.scatter(x, y, color=colors[i])
            ax.annotate(
                v,
                (x, y),
                xytext=(-4, 5) if v == "ALL" else (4, 5),
                ha="right" if v == "ALL" else "left",
                textcoords="offset points",
                fontsize=8,
            )
        ax.margins(x=0.15, y=0.2)
        ax.set(
            xlabel="NBI subproblems / FILTER (%)",
            ylabel=m + " change (%)",
            title=m + " versus effort",
        )
    save(fig, "effort_quality_tradeoff")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nx", type=int, choices=[2, 3])
    args = parser.parse_args()
    dimensions = [args.nx] if args.nx else [2, 3]
    for nx in dimensions:
        assert read_json(OUT / f"nx{nx}_gate.json")["status"] == "PASS"
    rows, costs = assemble(dimensions)
    if args.nx and (OUT / "ablation_results.csv").exists():
        prior = pd.read_csv(OUT / "ablation_results.csv")
        rows = pd.concat([prior[prior.nx != args.nx], rows])
        previous = pd.read_csv(OUT / "ablation_costs.csv")
        costs = pd.concat(
            [previous[previous.scenario_id.map(lambda s: int(s[2])) != args.nx], costs]
        )
    summary = summarize(rows)
    for d, name in [
        (rows, "ablation_results.csv"),
        (costs, "ablation_costs.csv"),
        (summary, "ablation_summary.csv"),
    ]:
        d.to_csv(OUT / name, index=False, lineterminator="\n")
    write_report(rows, costs, summary)
    figures(rows, summary)
    protocol = dict(
        status="COMPLETED" if len(rows) == 100 else "NX2_COMPLETED",
        previous_commit="eb936474b2d174fa959a7b6c5091d421a54cb979",
        protocol_id="definitive_svd_pa_ablation_20261031",
        arms=["FILTER", "RANDOM", "ALL"],
        versions=PLAN["versions"],
        solver=PLAN["solver"],
        ES_policy_shared=PLAN["policy"],
        H_by_k={k: 5 for k in (2, 3, 4)},
        objective_directions="MIN for every original objective",
        aggregation="Three RANDOM draws remain separate; their mean within each replica "
        "precedes five-replica scenario medians. Focused summary: median of four scenario medians.",
        random_seed_sd_ddof=1,
        scenarios=PLAN["selected_scenarios"],
        seeds=PLAN["A2_selection_seeds"],
        shared_B={i: p["B"] for i, p in PLAN["plans"].items()},
        historical_directory="results/phase_10_synthetic_ablation/history/focused_20261031",
        canonical_cache_directory="results/phase_10_synthetic_ablation/focused_20261031/subset_cache",
        historical_caches=477,
        missing_subsets=378,
        missing_subproblems=13208,
        historical_protocol_sha256=file_hash(PREVIOUS / "ablation_protocol.json"),
        input_sha256=PLAN["input_sha256"],
        source_sha256={
            p.relative_to(ROOT).as_posix(): file_hash(p)
            for p in (
                Path(__file__).resolve(),
                ROOT / "scripts/validation/complete_svd_pa_all.py",
                ROOT / "src/cnbi_v2/synthetic/ablation/core.py",
                ROOT / "tests/synthetic/test_definitive_ablation.py",
            )
        },
        artifact_sha256={
            p.relative_to(OUT).as_posix(): file_hash(p)
            for p in OUT.rglob("*")
            if p.is_file() and p.name != "ablation_protocol.json"
        },
    )
    write_json(OUT / "ablation_protocol.json", protocol)
    print("POSTPROCESS COMPLETE:", len(rows), "rows; FILTER/RANDOM metrics reused", flush=True)


if __name__ == "__main__":
    main()
