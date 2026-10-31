"""Four frozen cells only; cached ES, minimal missing NBI, then frozen evaluation."""

import os

for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[key] = "1"

# ruff: noqa: E402 -- numerical thread limits precede imports
import argparse
import hashlib
import json
import platform
import subprocess
from collections import Counter
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from cnbi_v2.chim.spectral_gap_stop import SpectralGapStopPolicy
from cnbi_v2.nbi.geometry import local_nbi_geometry
from cnbi_v2.nbi.solver import DEFAULT_OPTIONS
from cnbi_v2.optimization import Direction
from cnbi_v2.synthetic.ablation import random_subsets, solve_subset, subset_counts
from cnbi_v2.synthetic.analysis.selection import feasible_nd_indices
from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, write_json
from cnbi_v2.synthetic.benchmark.contracts import array_hash
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get("CNBI_ABLATION_INPUT_ROOT", str(ROOT)))
OUT = ROOT / "results/phase_10_synthetic_ablation/focused_20261031"
OLD = Path("results/phase_10_synthetic_benchmark/benchmark_20261029/campaign_v2")
ES = Path("results/phase_10_synthetic_early_stop/gaps_adr0009_20261031_090729")
RSM = Path("results/phase_10_synthetic_rsm/rsm_20261029")
PARETO = Path("results/phase_10_synthetic_pareto/analytical_20261029")
STRUCTURAL = Path("results/phase_10_synthetic_generation/structural_20261029")
METRICS = ("GD", "IGD", "HV", "Spacing", "Sparsity")
INPUT_HASHES = {}
BLOBS = {}
POLICY = SpectralGapStopPolicy(
    tuple(range(100, 2001, 100)), 100, 300, 3, 500, 0.05, float(np.finfo(float).tiny), 2000
)


def protect(relative):
    path = SOURCE / relative
    raw = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if BLOBS.get(Path(relative).as_posix()) != blob:
        raise ValueError("Input differs from base Git tree: " + str(relative))
    INPUT_HASHES[Path(relative).as_posix()] = hashlib.sha256(raw).hexdigest()
    return path


def read(relative):
    return read_json(protect(relative))


def metadata(instance, variant):
    directory, name = (ES, instance) if variant == "A0" else (OLD, f"official__{instance}__C-NBI")
    cp = read(
        directory
        / ("checkpoints" if variant == "A0" else "campaign_checkpoints")
        / (name + ".json")
    )
    assert cp["state"] == "COMPLETED"
    doc = read(directory / "algorithm_diagnostics" / (name + ".json"))
    for path, expected in cp["payload_checksums"].items():
        assert file_hash(protect(directory / path)) == expected
    with np.load(protect(directory / "raw_decisions" / (name + ".npz"))) as a:
        x = a["decisions"].copy()
    return doc, x


def extract(doc, x, identifier, source):
    d = doc["diagnostics"]
    rows = [i for i, r in enumerate(d["raw_origins"]) if r["subset_id"] == identifier]
    records = [r for r in d["subproblems"] if r["subset_id"] == identifier]
    trials = [t for t in d["trials"] if t["subset_id"] == identifier]
    assert len(rows) == sum(r["accepted"] for r in records)
    effort = sum(t["iterations"] for t in trials)
    total_effort = sum(t["iterations"] for t in d["trials"])
    return dict(
        X=x[rows],
        weights=[d["raw_origins"][i]["weight_id"] for i in rows],
        subproblems=records,
        trials=trials,
        iterations=effort,
        attempts=sum(r["attempts"] for r in records),
        counters=None,
        source=source,
        solver_seconds_estimate=doc["timings"]["solver"] * effort / total_effort,
        solver_seconds=None,
        geometry_seconds=None,
    )


def cache_path(instance, identifier):
    return OUT / "subset_cache" / instance / identifier


def save_subset(instance, identifier, result):
    path = cache_path(instance, identifier)
    path.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(path / "decisions.npz", decisions=result.pop("X"))
    write_json(path / "record.json", result)
    return load_subset(instance, identifier)


def load_subset(instance, identifier):
    path = cache_path(instance, identifier)
    d = read_json(path / "record.json")
    d["X"] = np.load(path / "decisions.npz")["decisions"]
    return d


def prepare(protocol, inputs):
    """Plans are frozen before any external metric/reference is read."""
    plans = {}
    for cell in protocol["selected_scenarios"]:
        sid = cell["scenario_id"]
        for replica in range(1, 6):
            instance = f"{sid}__replica{replica}"
            data = inputs[instance]
            a0, x0 = metadata(instance, "A0")
            a1, x1 = metadata(instance, "A1")
            d = a0["diagnostics"]
            assert d["generated_samples"] == d["reoptimized_samples"] == d["B"]
            assert d["no_future_draws"] and d["policy"] == json.loads(json.dumps(asdict(POLICY)))
            assert d["B"] >= 500 and d["B"] <= 2000
            trajectory = d["checkpoints"]
            assert not any(t["stop"] for t in trajectory[:-1])
            assert trajectory[-1]["early_stop_condition_met"] or d["B"] == 2000
            assert array_hash(data.model.coefficients) == a0["coefficients_sha256"]
            universe, rejected = {}, []
            for s in d["subsets"][1:]:
                ids = tuple(s["indices"])
                try:
                    local_nbi_geometry(
                        np.array(d["nominal_payoff"])[np.ix_(ids, ids)], (Direction.MIN,) * len(ids)
                    )
                    universe[s["subset_id"]] = ids
                except ValueError as error:
                    rejected.append(dict(subset_id=s["subset_id"], reason=str(error)))
            a0_ids = [s["subset_id"] for s in d["subsets"][1:] if s["selected"]]
            assert all(s in universe for s in a0_ids)
            targets = subset_counts(a0_ids, universe)
            tick = perf_counter()
            draws = {}
            for seed in protocol["A2_selection_seeds"]:
                names, deficits = random_subsets(universe, targets, sid, replica, seed)
                draws[str(seed)] = dict(subsets=names, deficits=deficits)
            selection_seconds = perf_counter() - tick
            compatible = np.array_equal(
                d["nominal_anchors"], a1["diagnostics"]["nominal_anchors"]
            ) and np.array_equal(d["nominal_payoff"], a1["diagnostics"]["nominal_payoff"])
            for identifier in a0_ids:
                if not (cache_path(instance, identifier) / "record.json").exists():
                    save_subset(instance, identifier, extract(a0, x0, identifier, "A0"))
            if compatible:
                for s in a1["diagnostics"]["subsets"][1:]:
                    identifier = s["subset_id"]
                    if not s["selected"]:
                        continue
                    previous = extract(a1, x1, identifier, "A1")
                    if (cache_path(instance, identifier) / "record.json").exists():
                        same = load_subset(instance, identifier)
                        assert same["weights"] == previous["weights"]
                        assert np.array_equal(same["X"], previous["X"])
                    else:
                        save_subset(instance, identifier, previous)
            plans[instance] = dict(
                scenario_id=sid,
                replica_id=replica,
                B=d["B"],
                original_seed=d["seed"],
                target_counts=targets,
                universe=universe,
                degenerate_exclusions=rejected,
                A0=a0_ids,
                A1=[s["subset_id"] for s in a1["diagnostics"]["subsets"][1:] if s["selected"]],
                A2=draws,
                A3=[s for s in a0_ids if len(universe[s]) == 2],
                A1_cache_compatible=compatible,
                random_selection_seconds=selection_seconds,
                payoff=d["nominal_payoff"],
                anchors=d["nominal_anchors"],
            )
    protocol.update(
        plans=plans,
        status="SUBSET_PLANS_FROZEN_BEFORE_EXTERNAL_QUALITY_ACCESS",
        versions={k: version(k) for k in ("numpy", "scipy", "pandas", "matplotlib")},
        python=platform.python_version(),
        platform=platform.platform(),
        policy=asdict(POLICY),
        solver=asdict(DEFAULT_OPTIONS),
        H="unchanged lattice_resolution(k): H5 k2..4, H2 k5..6",
        input_sha256=INPUT_HASHES,
        cost_estimation="Cached subset solver time allocated by recorded SLSQP "
        "iterations / all recorded iterations within paired A0. All modeled NBI times "
        "use that unit cost. Actual new optimization time is separate. "
        "Reused A0 preparation unchanged. "
        "No full A2/A3 pipeline runtime or unrecorded gradient counts fabricated.",
        aggregation="Mean A2 random seeds within each instance first; median five "
        "replicas per scenario; focused summary median of four scenario medians. "
        "All relative changes paired to the same scenario/replica A0; no inference.",
    )
    write_json(OUT / "ablation_protocol.json", protocol)


def search(protocol, inputs):
    """Pilot replays one cached subset; campaign solves only unique cache misses."""
    plans = protocol["plans"]
    pilot_path = OUT / "pilot.json"
    if not pilot_path.exists():
        instance = next(iter(plans))
        p = plans[instance]
        identifier = p["A0"][0]
        result = solve_subset(
            inputs[instance],
            np.array(p["payoff"]),
            np.array(p["anchors"]),
            tuple(p["universe"][identifier]),
        )
        cached = load_subset(instance, identifier)
        assert np.array_equal(result["X"], cached["X"]) and result["weights"] == cached["weights"]
        assert not result["counters"].get("quadratic_ball_solves", 0)
        write_json(
            pilot_path,
            dict(
                status="PASS",
                instance=instance,
                subset=identifier,
                bitwise_cached_decisions=True,
                seconds=result["elapsed_seconds"],
                counters=result["counters"],
                new_mc_or_anchor_solves=0,
            ),
        )
    new_count = 0
    for instance, p in plans.items():
        required = {s for draw in p["A2"].values() for s in draw["subsets"]}
        for identifier in sorted(required):
            if (cache_path(instance, identifier) / "record.json").exists():
                continue
            ids = tuple(p["universe"][identifier])
            result = solve_subset(
                inputs[instance], np.array(p["payoff"]), np.array(p["anchors"]), ids
            )
            assert not result["counters"].get("quadratic_ball_solves", 0)
            if not len(result["X"]):
                raise ValueError("Systematic local failure: " + instance + "/" + identifier)
            result.update(source="NEW_A2", solver_seconds_estimate=result["solver_seconds"])
            save_subset(instance, identifier, result)
            new_count += 1
        print("Search checkpoint:", instance, "new subsets cumulatively", new_count, flush=True)
    return new_count


def true_set(context, x):
    z = context.normalization.transform(evaluate(x, context.anchors))
    feasible, unique, nd = feasible_nd_indices(x, z, inputs_radius(context.scenario.nx), 0.0)
    a = np.unique(z[nd], axis=0)
    return a, (int(feasible.sum()), len(unique), len(nd))


def inputs_radius(nx):
    return 2 ** (nx / 4)


def quality(protocol):
    """Search finished before loading any reference or metric; prior metrics reused."""
    paired_path = protect(ES / "postprocess_20261031/paired_135.csv")
    paired = pd.read_csv(paired_path).set_index("instance_id")
    rows, costs, evaluation_cache = [], [], {}
    for cell in protocol["selected_scenarios"]:
        sid = cell["scenario_id"]
        for path in (SOURCE / PARETO).glob("*"):
            if path.is_file():
                protect(path.relative_to(SOURCE))
        for path in (SOURCE / STRUCTURAL).glob("*"):
            if path.is_file():
                protect(path.relative_to(SOURCE))
        ctx = load_evaluation_context(SOURCE / PARETO, sid, SOURCE / STRUCTURAL)
        for replica in range(1, 6):
            instance = f"{sid}__replica{replica}"
            p = protocol["plans"][instance]
            previous = paired.loc[instance]
            assert previous.integrity == "PASS"
            sources = {}
            for variant, suffix in [("A0", "ES"), ("A1", "original")]:
                doc, x = metadata(instance, variant)
                metrics = {
                    k: None
                    if pd.isna(previous[f"{k}_{suffix}"])
                    else float(previous[f"{k}_{suffix}"])
                    for k in METRICS
                }
                metrics["HV_status"] = previous[f"HV_status_{suffix}"]
                z, counts = true_set(ctx, x)
                assert len(z) == int(previous[f"ND_{suffix}"])
                evaluation_cache[(sid, array_hash(z))] = metrics
                sources[variant] = dict(doc=doc, x=x, metrics=metrics, counts=counts)
            variants = [("A0", 0, p["A0"]), ("A1", 0, p["A1"])]
            variants += [("A2", int(seed), draw["subsets"]) for seed, draw in p["A2"].items()]
            variants += [("A3", 0, p["A3"])]
            for variant, seed, names in variants:
                begun = perf_counter()
                groups = (
                    [load_subset(instance, s) for s in names] if variant in ("A2", "A3") else []
                )
                x = (
                    np.vstack([g["X"] for g in groups])
                    if groups
                    else sources[variant]["x"]
                    if variant in sources
                    else np.empty((0, ctx.scenario.nx))
                )
                recomposition_seconds = perf_counter() - begun
                if variant in sources:
                    values, counts = sources[variant]["metrics"], sources[variant]["counts"]
                    metric_source = "STORED_10F_POSTPROCESS"
                    evaluation_seconds = 0.0
                else:
                    tick = perf_counter()
                    z, counts = true_set(ctx, x)
                    key = sid, array_hash(z)
                    if key in evaluation_cache:
                        values = evaluation_cache[key]
                        metric_source = "IDENTICAL_ND_SET_CACHE"
                    else:
                        result = ctx.evaluate(
                            sid, replica, "C-NBI", x, dict(variant=variant, random_seed=seed)
                        )
                        values = result.metrics
                        evaluation_cache[key] = values
                        metric_source = "FROZEN_10C_API"
                    evaluation_seconds = perf_counter() - tick
                covered = set(
                    i
                    for s in names
                    for i in p["universe"].get(s, tuple(int(i) - 1 for i in s.split("_")[1:]))
                )
                row = dict(
                    variant=variant,
                    scenario_id=sid,
                    replica_id=replica,
                    random_seed=seed,
                    nx=ctx.scenario.nx,
                    m=ctx.scenario.m,
                    B_effective=2000 if variant == "A1" else p["B"],
                    raw_cardinality=len(x),
                    feasible_cardinality=counts[0],
                    unique_cardinality=counts[1],
                    ND=counts[2],
                    objectives_covered=len(covered),
                    objectives_total=ctx.scenario.m,
                    coverage_fraction=len(covered) / ctx.scenario.m,
                    subsets=len(names),
                    counts_by_k=json.dumps(dict(Counter(len(s.split("_")) - 1 for s in names))),
                    metric_source=metric_source,
                    HV_status=values.get("HV_status"),
                    evaluation_seconds=evaluation_seconds,
                )
                for k in METRICS:
                    value, base = values.get(k), sources["A0"]["metrics"][k]
                    row[k] = value
                    row[k + "_delta_A0"] = (
                        value - base if value is not None and base is not None else None
                    )
                    row[k + "_relative_A0_pct"] = (
                        100 * (value / base - 1)
                        if value is not None and base is not None and base != 0
                        else None
                    )
                row["ND_delta_A0"] = counts[2] - sources["A0"]["counts"][2]
                rows.append(row)
                if variant in sources:
                    doc = sources[variant]["doc"]
                    cost = dict(
                        time_basis="HISTORICAL_OBSERVED",
                        pipeline_seconds_observed=doc["timings"]["total"],
                        preparation_seconds_observed=doc["timings"]["preparation"],
                        nbi_seconds_observed=doc["timings"]["solver"],
                        postprocessing_seconds_observed=doc["timings"]["postprocessing"],
                        pipeline_seconds_estimated=None,
                        nbi_attempts=doc["counters"]["nbi_attempts"],
                        nbi_iterations=doc["counters"]["nbi_iterations"],
                        nbi_subproblems=doc["counters"]["nbi_subproblems"],
                        function_value_calls=doc["counters"].get("scalar_quadratic_values"),
                        gradient_calls=doc["counters"].get("scalar_quadratic_gradients"),
                        nbi_equality_jacobians=doc["counters"].get("nbi_equality_jacobians"),
                        nominal_anchor_solves=ctx.scenario.m,
                        mc_anchor_solves=row["B_effective"] * ctx.scenario.m,
                        new_subset_solver_seconds=0.0,
                        new_subset_count=0,
                        cached_subset_count=len(names),
                        actual_new_function_value_calls=0,
                        actual_new_gradient_calls=0,
                    )
                    stages = doc["diagnostics"].get("stage_seconds", {})
                    cost["screening_seconds_observed"] = (
                        sum(
                            stages.get(k, 0.0)
                            for k in ("spectra", "pa_checkpoints", "geometry_certification")
                        )
                        if stages
                        else None
                    )
                else:
                    base = sources["A0"]["doc"]
                    new = [g for g in groups if g["source"] == "NEW_A2"]
                    reference_iterations = sum(
                        t["iterations"] for t in base["diagnostics"]["trials"]
                    )
                    estimated_nbi = (
                        base["timings"]["solver"]
                        * sum(g["iterations"] for g in groups)
                        / reference_iterations
                    )
                    estimated_total = (
                        base["timings"]["preparation"]
                        + estimated_nbi
                        + base["timings"]["postprocessing"]
                    )
                    cost = dict(
                        time_basis="MODELED_REUSE_NOT_OBSERVED_FULL_PIPELINE",
                        pipeline_seconds_observed=None,
                        preparation_seconds_observed=None,
                        nbi_seconds_observed=None,
                        postprocessing_seconds_observed=None,
                        pipeline_seconds_estimated=estimated_total,
                        preparation_seconds_estimated=base["timings"]["preparation"],
                        nbi_seconds_estimated=estimated_nbi,
                        screening_seconds_inherited=sum(
                            base["diagnostics"]["stage_seconds"][k]
                            for k in ("spectra", "pa_checkpoints", "geometry_certification")
                        ),
                        postprocessing_seconds_estimated=base["timings"]["postprocessing"],
                        nbi_attempts=sum(g["attempts"] for g in groups),
                        nbi_iterations=sum(g["iterations"] for g in groups),
                        nbi_subproblems=sum(len(g["subproblems"]) for g in groups),
                        function_value_calls=None,
                        gradient_calls=None,
                        nbi_equality_jacobians=None,
                        nominal_anchor_solves=ctx.scenario.m,
                        mc_anchor_solves=p["B"] * ctx.scenario.m,
                        new_subset_solver_seconds=sum(g["solver_seconds"] for g in new),
                        new_subset_count=len(new),
                        cached_subset_count=len(groups) - len(new),
                        actual_new_function_value_calls=sum(
                            g["counters"].get("scalar_quadratic_values", 0) for g in new
                        ),
                        actual_new_gradient_calls=sum(
                            g["counters"].get("scalar_quadratic_gradients", 0) for g in new
                        ),
                    )
                cost.update(
                    variant=variant,
                    scenario_id=sid,
                    replica_id=replica,
                    random_seed=seed,
                    B_effective=row["B_effective"],
                    subsets=len(names),
                    recomposition_seconds_observed=recomposition_seconds,
                    evaluation_seconds_observed=evaluation_seconds,
                    actual_new_MC_anchor_solves=0,
                    cost_limitation="Historical campaigns and modeled subset allocations "
                    "do not establish controlled wall-clock speedup",
                )
                denom = sources["A0"]["doc"]["timings"]["total"]
                effective_time = (
                    cost["pipeline_seconds_observed"] or cost["pipeline_seconds_estimated"]
                )
                cost["pipeline_relative_A0_pct"] = 100 * (effective_time / denom - 1)
                costs.append(cost)
    return pd.DataFrame(rows), pd.DataFrame(costs)


def summaries(results, costs):
    keys = ["variant", "scenario_id", "replica_id"]
    columns = [
        *METRICS,
        "ND",
        "subsets",
        "B_effective",
        "coverage_fraction",
        *[k + "_relative_A0_pct" for k in METRICS],
        "ND_delta_A0",
    ]
    # Three A2 draws are nested, never treated as fifteen independent replicas.
    collapsed = results.groupby(keys)[columns].mean().reset_index()
    cost = costs.groupby(keys)[["pipeline_relative_A0_pct", "nbi_subproblems"]].mean().reset_index()
    collapsed = collapsed.merge(cost, on=keys)
    summary = collapsed.groupby(["variant", "scenario_id"]).median(numeric_only=True).reset_index()
    summary["aggregation"] = "MEDIAN_OF_5_REPLICAS_AFTER_A2_SEED_MEAN"
    overall = summary.groupby("variant").median(numeric_only=True).reset_index()
    overall["scenario_id"] = "FOCUSED_4_CELLS_ONLY"
    overall["aggregation"] = "MEDIAN_OF_4_CELL_MEDIANS_EXPLORATORY"
    return pd.concat([summary, overall], ignore_index=True)


def report(protocol, results, costs, summary):
    focus = summary[summary.scenario_id == "FOCUSED_4_CELLS_ONLY"].set_index("variant")
    lines = [
        "# Focused C-NBI V2 ablation",
        "",
        "Exploratory evidence from four cost-selected cells, five frozen replicas each. "
        "C-NBI-ES (ADR0009, minimum300 / first500 / maximum2000) is the principal method. "
        "No conclusion is extrapolated to the27-cell benchmark.",
        "",
        "## Selection and frozen protocol",
        "",
        "The three cheapest B2000 cells were selected by the sum of recorded kernel "
        "timings.total across five replicas. The cheapest remaining nx=3 cell adds a "
        "decision dimension. No quality indicator entered selection. Cost ranking, "
        "exact subset plans, seeds and hashes were frozen before external evaluation.",
        "",
        "|Scenario|nx|Five-replica B2000 cost (s)|",
        "|---|---:|---:|",
    ]
    for c in protocol["selected_scenarios"]:
        lines.append(f"|{c['scenario_id']}|{c['nx']}|{c['total_seconds']:.4f}|")
    lines += [
        "",
        "## Article-ready focused comparison",
        "",
        "Values below are medians of four scenario medians of paired relative changes "
        "against A0. A2 first averages its three random draws within each replica. "
        "Negative IGD/GD/Spacing/Sparsity changes and positive HV changes favor the variant. "
        "Spacing/Sparsity also depend on cardinality; no equalization or inference is used.",
        "",
        "|Variant|IGD change (%)|HV change (%)|ND change|NBI subproblems|"
        "Pipeline cost change (%)|Cost basis|",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for v, r in focus.iterrows():
        lines.append(
            f"|{v}|{r['IGD_relative_A0_pct']:.3f}|{r['HV_relative_A0_pct']:.3f}|"
            f"{r['ND_delta_A0']:.1f}|{r['nbi_subproblems']:.1f}|"
            f"{r['pipeline_relative_A0_pct']:.2f}|"
            f"{'Historical observed' if v in ('A0', 'A1') else 'Estimated reuse'}|"
        )
    a1, a2, a3 = (focus.loc[v] for v in ("A1", "A2", "A3"))
    lines += [
        "",
        "## Interpretation",
        "",
        f"Disabling ES (A1) changes focused IGD by {a1.IGD_relative_A0_pct:.3f}% and HV "
        f"by {a1.HV_relative_A0_pct:.3f}%. Its historical pipeline cost change is "
        f"{a1.pipeline_relative_A0_pct:.2f}%; this is not a controlled speedup experiment.",
        f"Replacing PA selection with random matched per-k budgets (A2) changes IGD by "
        f"{a2.IGD_relative_A0_pct:.3f}% and HV by {a2.HV_relative_A0_pct:.3f}%. This isolates "
        "subset choice at the retained budget, not the computational removal of the PA "
        "diagnostic: the original ES uncertainty/stability history is retained.",
        "A2 and A3 keep the paired A0 stopping decision fixed, including its monitored "
        "PA-selected IDs. Random subsets are not used to re-adapt the stopping time. "
        "The experiment therefore isolates subset choice/composition at matched uncertainty "
        "prefixes, not alternative ES dynamics for each random draw.",
        f"Retaining pairs only (A3) changes IGD by {a3.IGD_relative_A0_pct:.3f}% and HV "
        f"by {a3.HV_relative_A0_pct:.3f}%, at {a3.pipeline_relative_A0_pct:.2f}% estimated "
        "pipeline cost change. This measures the marginal contribution of higher-k "
        "solutions in the archived complete run, not a newly tuned pair-only method.",
        "",
        "## Reuse, costs and limits",
        "",
        "A0/A1 metrics are reused without reevaluation. A3 filters A0 raw pair candidates "
        "and repeats only frozen feasibility/uniqueness/ND recomposition and evaluation. "
        "A2 uniformly samples eligible nominally certified subsets without replacement "
        "within each k, using seeds181001/181002/181003 and independent per-instance "
        "hashed streams. It matches A0 counts at the same saved ES stopping prefix. "
        "Degenerate subsets and any budget deficit are explicitly recorded.",
        "Nominal/MC anchors and models are read-only cached inputs. Local NBI caches "
        "from A0/A1 are reusable only for identical anchors, payoff and kernels; shared "
        "decisions are checked bitwise. A pilot reproduces one local solution set "
        "bitwise before solving only missing subset caches. No new MC, coefficient "
        "draw, anchor optimization, RSM fit, reference, comparator or MaF run occurs.",
        "A0/A1 times are historical observed kernel times. A2/A3 full-pipeline costs "
        "are explicitly modeled: inherited A0 preparation plus cached subset solver "
        "time allocated proportionally to recorded SLSQP iterations, using the same paired "
        "A0 time per iteration for every subset, plus inherited postprocessing time. "
        "Actual new solver times are reported separately and never mixed into that model. "
        "Allocation is not measured local runtime and ignores fixed and retry-dependent "
        "overhead. It can understate costly line searches in random subsets, so estimated "
        "A2 costs cannot establish a processing-time benefit or equivalence. "
        "No total function/gradient counts are invented for cached subsets. "
        "The actual new execution cost is separately recorded; shared cache work must "
        "not be summed repeatedly across random draws.",
        "Screening, nominal/MC optimization, NBI and postprocessing fields remain "
        "separate where originally observed. A1 preparation was not historically "
        "split into every screening component; missing components remain unavailable. "
        "Timing comparisons across historical and current campaigns have hardware/load "
        "and profiler limitations. No claim of global speedup is made.",
        "All metrics use the unchanged analytical10C reference, normalization, strict "
        "feasibility and duplicate/ND tolerances and frozen HV precision rules. "
        "Undefined HV remains undefined; no precision escalation or clipping is added. "
        "Objective coverage counts distinct objective IDs in selected subsets, not an "
        "invented front-coverage indicator. Only nx=2 and nx=3 are represented.",
        f"Rows: {len(results)} (A0/A1/A3:20 each; A2:60). Undefined metric entries: "
        f"{int(results[list(METRICS)].isna().sum().sum())}.",
        "Existing27-cell principal analyses and pairwise10E equalization remain unchanged.",
    ]
    formatted = [s if not s or s.startswith(("|", "#")) else s + "\n" for s in lines]
    (OUT / "ABLATION_REPORT.md").write_text(
        "\n".join(formatted).rstrip() + "\n", encoding="utf-8", newline="\n"
    )


def figures(summary):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    focus = (
        summary[summary.scenario_id == "FOCUSED_4_CELLS_ONLY"]
        .set_index("variant")
        .loc[["A0", "A1", "A2", "A3"]]
    )
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 9,
            "axes.grid": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    folder = OUT / "figures"
    folder.mkdir(exist_ok=True)

    def save(fig, name):
        fig.savefig(folder / (name + ".png"), dpi=600, bbox_inches="tight")
        fig.savefig(folder / (name + ".pdf"), bbox_inches="tight")
        plt.close(fig)

    colors = ["#264653", "#2a9d8f", "#e9c46a", "#e76f51"]
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.9), layout="constrained")
    for ax, metric in zip(axes, ["IGD", "HV"], strict=True):
        ax.bar(focus.index, focus[metric + "_relative_A0_pct"], color=colors)
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set(ylabel=metric + " change vs A0 (%)", title="Focused quality — " + metric)
    save(fig, "quality_by_variant")
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.9), layout="constrained")
    for ax, ids, title in zip(
        axes, [["A0", "A1"], ["A2", "A3"]], ["Historical observed", "Modeled reuse"], strict=True
    ):
        ax.bar(
            ids,
            100 + focus.loc[ids, "pipeline_relative_A0_pct"],
            color=[colors[int(s[1])] for s in ids],
            hatch=None if ids[0] == "A0" else "//",
        )
        ax.set(ylabel="Pipeline cost / A0 (%)", title=title)
    save(fig, "cost_by_variant")
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.9), layout="constrained")
    fig.suptitle("Circles: historical observed cost; squares: modeled cost", fontsize=9)
    for ax, metric in zip(axes, ["IGD", "HV"], strict=True):
        for v, r in focus.iterrows():
            x, y = 100 + r.pipeline_relative_A0_pct, r[metric + "_relative_A0_pct"]
            ax.scatter(x, y, color=colors[int(v[1])], marker="o" if v in ("A0", "A1") else "s")
            ax.annotate(
                v,
                (x, y),
                xytext=(-5, 5) if v == "A1" else (5, 5),
                ha="right" if v == "A1" else "left",
                textcoords="offset points",
            )
        ax.margins(x=0.14, y=0.18)
        ax.set(
            xlabel="Pipeline cost / A0 (%)",
            ylabel=metric + " change vs A0 (%)",
            title=metric + " trade-off",
        )
    save(fig, "cost_quality_tradeoff")


def finalize_outputs():
    """Reports/integrity only; never evaluates a metric or executes a solver."""
    import ast

    protocol = read_json(OUT / "ablation_protocol.json")
    results = pd.read_csv(OUT / "ablation_results.csv")
    costs = pd.read_csv(OUT / "ablation_costs.csv")
    assert len(results) == len(costs) == 120
    # Keep original executed bytes and certify that later edits changed only reporting.
    for archive_name, current, functions in (
        (
            "ablation.py",
            ROOT / "src/cnbi_v2/synthetic/ablation.py",
            ("random_subsets", "subset_counts", "solve_subset"),
        ),
        ("run_phase10f_focused_ablation.py", Path(__file__), ("prepare", "search", "quality")),
    ):
        old = OUT / "execution_source" / archive_name
        if old.exists():
            a = {
                n.name: ast.dump(n)
                for n in ast.parse(old.read_text()).body
                if isinstance(n, ast.FunctionDef)
            }
            b = {
                n.name: ast.dump(n)
                for n in ast.parse(current.read_text()).body
                if isinstance(n, ast.FunctionDef)
            }
            assert all(a[k] == b[k] for k in functions)
    cache = {}
    for path in (OUT / "subset_cache").glob("*/*/record.json"):
        cache[(path.parent.parent.name, path.parent.name)] = read_json(path)
    rejected = []
    for row in costs.to_dict("records"):
        instance = f"{row['scenario_id']}__replica{row['replica_id']}"
        p = protocol["plans"][instance]
        if row["variant"] in ("A0", "A1"):
            directory, name = (
                (ES, instance) if row["variant"] == "A0" else (OLD, f"official__{instance}__C-NBI")
            )
            doc = read_json(SOURCE / directory / "algorithm_diagnostics" / (name + ".json"))
            records = doc["diagnostics"]["subproblems"]
        else:
            names = (
                p["A3"] if row["variant"] == "A3" else p["A2"][str(row["random_seed"])]["subsets"]
            )
            records = [r for name in names for r in cache[(instance, name)]["subproblems"]]
        rejected.append(sum(not r["accepted"] for r in records))
    costs["nbi_rejected_subproblems"] = rejected
    costs = costs.rename(
        columns={
            "new_subset_solver_seconds": "new_cache_solver_seconds_attributed_nonadditive",
            "new_subset_count": "new_cache_subsets_attributed_nonadditive",
            "actual_new_function_value_calls": "new_cache_value_calls_attributed_nonadditive",
            "actual_new_gradient_calls": "new_cache_gradient_calls_attributed_nonadditive",
        }
    )
    costs.to_csv(OUT / "ablation_costs.csv", index=False, lineterminator="\n")
    new = [r for r in cache.values() if r["source"] == "NEW_A2"]
    counts = Counter()
    for r in new:
        counts.update(r["counters"])
    actual = dict(
        unique_new_subsets=len(new),
        new_NBI_subproblems=sum(len(r["subproblems"]) for r in new),
        rejected_new_NBI_subproblems=sum(not s["accepted"] for r in new for s in r["subproblems"]),
        observed_unique_new_solver_seconds=sum(r["solver_seconds"] for r in new),
        observed_unique_new_geometry_seconds=sum(r["geometry_seconds"] for r in new),
        counters=dict(counts),
        pilot=read_json(OUT / "pilot.json"),
        new_MC_draws=0,
        new_anchor_solves=0,
        original_campaign_wall_seconds=protocol["total_wall_seconds_this_invocation"],
        attribution="Unique actual work; do not sum repeated cache attributions in CSV",
    )
    write_json(OUT / "execution_costs.json", actual)
    summary = summaries(results, costs)
    summary.to_csv(OUT / "ablation_summary.csv", index=False, lineterminator="\n")
    report(protocol, results, costs, summary)
    with (OUT / "ABLATION_REPORT.md").open("a", encoding="utf-8", newline="\n") as stream:
        a1 = results[results.variant == "A1"]
        stream.write(
            "\nThe zero focused median does not imply identical results in every "
            "replica. B2000 and ES have identical IGD/HV in15/20 paired cases. "
            "B2000 improves both in four cases and worsens both in one. "
            f"Its IGD change ranges from {a1.IGD_relative_A0_pct.min():.3f}% to "
            f"{a1.IGD_relative_A0_pct.max():.3f}%; HV ranges from "
            f"{a1.HV_relative_A0_pct.min():.3f}% to "
            f"{a1.HV_relative_A0_pct.max():.3f}%.\n"
        )
        stream.write("\n## Scenario sensitivity and measured added work\n\n")
        stream.write("|Scenario|Variant|IGD change (%)|HV change (%)|Cost change (%)|\n")
        stream.write("|---|---|---:|---:|---:|\n")
        for r in summary[summary.scenario_id != "FOCUSED_4_CELLS_ONLY"].to_dict("records"):
            if r["variant"] == "A0":
                continue
            stream.write(
                f"|{r['scenario_id']}|{r['variant']}|{r['IGD_relative_A0_pct']:.3f}|"
                f"{r['HV_relative_A0_pct']:.3f}|{r['pipeline_relative_A0_pct']:.2f}|\n"
            )
        stream.write("\n|Variant|B median|NBI subproblems (sum)|Pipeline time sum (s)|Basis|\n")
        stream.write("|---|---:|---:|---:|---|\n")
        by_rep = costs.groupby(["variant", "scenario_id", "replica_id"]).mean(numeric_only=True)
        for variant in ("A0", "A1", "A2", "A3"):
            a = by_rep.loc[variant]
            field = (
                "pipeline_seconds_observed"
                if variant in ("A0", "A1")
                else "pipeline_seconds_estimated"
            )
            stream.write(
                f"|{variant}|{a.B_effective.median():.0f}|{a.nbi_subproblems.sum():.1f}|"
                f"{a[field].sum():.4f}|"
                f"{'Historical observed' if variant in ('A0', 'A1') else 'Iteration model'}|\n"
            )
        stream.write(
            f"\nActual added search: {len(new)} unique subset solves, "
            f"{actual['new_NBI_subproblems']} NBI subproblems, "
            f"{actual['observed_unique_new_solver_seconds']:.3f} s in the solver and "
            f"{actual['rejected_new_NBI_subproblems']} rejected local weights, plus "
            f"{actual['pilot']['seconds']:.4f} s for the mandatory cached-subset pilot. "
            "Exact function/gradient/internal-optimization counts are in "
            "execution_costs.json. A2 full-pipeline time was not observed; the sum "
            "above is an allocation model and must not be compared as a measured speedup.\n"
        )
    figures(summary)
    protocol.update(
        study_status="EXPERIMENTAL_FOCUSED_ABLATION",
        verified_no_search_kernel_changes_after_execution=True,
        cost_estimation="All A2/A3 full-pipeline estimates use paired A0 time per "
        "recorded SLSQP iteration, inherited preparation and postprocessing. Actual "
        "unique added work is separate in execution_costs.json; attribution fields "
        "in ablation_costs.csv are explicitly nonadditive.",
        source_sha256={
            p.relative_to(ROOT).as_posix(): file_hash(p)
            for p in (
                Path(__file__),
                ROOT / "src/cnbi_v2/synthetic/ablation.py",
                ROOT / "tests/synthetic/test_focused_ablation.py",
                ROOT / "uv.lock",
            )
        },
        artifact_sha256={
            p.relative_to(OUT).as_posix(): file_hash(p)
            for p in OUT.rglob("*")
            if p.is_file() and p.name != "ablation_protocol.json"
        },
    )
    write_json(OUT / "ablation_protocol.json", protocol)
    print("Finalized without optimization or metric recomputation", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--finalize-only", action="store_true")
    args = parser.parse_args()
    if args.finalize_only:
        finalize_outputs()
        return
    # A completed campaign resumes through reporting only: no repeated metrics or solves.
    if (OUT / "ablation_results.csv").exists() and (
        read_json(OUT / "ablation_protocol.json").get("status") == "COMPLETED"
    ):
        finalize_outputs()
        return
    begun = perf_counter()
    entries = subprocess.check_output(["git", "ls-tree", "-r", "-z", "HEAD"], cwd=ROOT)
    BLOBS.update(
        {
            p.split(b"\t")[1].decode(): p.split(b"\t")[0].split()[2].decode()
            for p in entries.split(b"\0")
            if p
        }
    )
    protocol = read_json(OUT / "ablation_protocol.json")
    for relative, sha in protocol["selection_cost_source_sha256"].items():
        assert file_hash(protect(relative)) == sha
    assert read(ES / "self_test.json")["status"] == "PASS"
    INPUT_HASHES.update(protocol.get("input_sha256", {}))
    for relative in (SOURCE / RSM).glob("*"):
        if relative.is_file():
            protect(relative.relative_to(SOURCE))
    inputs = load_search_inputs(SOURCE / RSM)
    if "plans" not in protocol:
        frozen = OUT / "selection_frozen.json"
        frozen.write_bytes((OUT / "ablation_protocol.json").read_bytes())
        protocol["cost_only_selection_sha256"] = file_hash(frozen)
        prepare(protocol, inputs)
    else:
        for relative, sha in protocol["input_sha256"].items():
            assert file_hash(protect(relative)) == sha
    if args.prepare:
        print("FROZEN:20 instances;60 matched random draws; no quality read", flush=True)
        return
    archive = OUT / "execution_source"
    archive.mkdir(exist_ok=True)
    for source in (Path(__file__), ROOT / "src/cnbi_v2/synthetic/ablation.py"):
        target = archive / source.name
        if not target.exists():
            target.write_bytes(source.read_bytes())
    new_subsets = search(protocol, inputs)
    search_seconds = perf_counter() - begun
    tick = perf_counter()
    results, costs = quality(protocol)
    summary = summaries(results, costs)
    for data, name in [
        (results, "ablation_results.csv"),
        (summary, "ablation_summary.csv"),
        (costs, "ablation_costs.csv"),
    ]:
        data.to_csv(OUT / name, index=False, lineterminator="\n")
    report(protocol, results, costs, summary)
    figures(summary)
    protocol.update(
        status="COMPLETED",
        input_sha256=INPUT_HASHES,
        new_subset_solves_this_invocation=new_subsets,
        search_and_load_seconds_this_invocation=search_seconds,
        evaluation_summary_figures_seconds_this_invocation=perf_counter() - tick,
        total_wall_seconds_this_invocation=perf_counter() - begun,
        source_sha256={
            p.relative_to(ROOT).as_posix(): file_hash(p)
            for p in (
                Path(__file__),
                ROOT / "src/cnbi_v2/synthetic/ablation.py",
                ROOT / "tests/synthetic/test_focused_ablation.py",
                ROOT / "uv.lock",
            )
        },
        artifact_sha256={
            p.relative_to(OUT).as_posix(): file_hash(p)
            for p in OUT.rglob("*")
            if p.is_file() and p.name != "ablation_protocol.json"
        },
    )
    write_json(OUT / "ablation_protocol.json", protocol)
    finalize_outputs()
    print("COMPLETE:", len(results), "rows;", new_subsets, "new subset solves", flush=True)


if __name__ == "__main__":
    main()
