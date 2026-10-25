"""Historical parent-grid Phase8B reproduction; official correction is standalone.

Use turning_standalone_analysis for the corrected H5. No optimizers execute here.
"""

import argparse
import importlib.metadata
import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.spatial import cKDTree

from cnbi_v2.benchmark.dominance import DominanceIndex
from cnbi_v2.benchmark.hypervolume import HVGrid
from cnbi_v2.benchmark.metrics import gd_igd, nearest_distances, spacing_sparsity, summary
from cnbi_v2.benchmark.selection import farthest_order
from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import nondominated_mask

from . import turning_benchmark_inputs as data
from . import turning_reference_campaign as phase7
from .turning_reference import ROOT, write_json
from .turning_reference_sensitivity import union_mask

PRIMARY = ("GD", "IGD", "HV", "Spacing", "Sparsity")
COMMON = "COMMON_REFERENCE_SELF_INCLUDED"
LOO = "LEAVE_ONE_FAMILY_OUT"
CONTEXT = {}


def reference_arrays():
    result = {}
    for name in ("all", "minus_cnbi", "minus_nsga3", "minus_moead", "minus_vrf"):
        with np.load(phase7.OUTPUT / f"reference_{name}.npz", allow_pickle=False) as d:
            result[name] = d["z"]
    return result


def grouped_summaries(records, keys, metrics):
    groups = {}
    for row in records:
        groups.setdefault(tuple(row[k] for k in keys), []).append(row)
    output = []
    for values, members in groups.items():
        for metric in metrics:
            observed = [r[metric] for r in members if r.get(metric) is not None]
            if not observed:
                continue
            output.append(dict(zip(keys, values, strict=True), metric=metric, **summary(observed)))
    return output


def better_fractions(records, variant):
    comparable = [r for r in records if r["label"] == COMMON]
    result = []
    for deterministic in ("CNBI5", "VRF"):
        fixed = next(r for r in comparable if r["method"] == deterministic)
        for stochastic in ("NSGA3", "MOEAD"):
            runs = [r for r in comparable if r["method"] == stochastic]
            for metric in PRIMARY:
                sign = 1 if metric == "HV" else -1
                score = sign * np.array([r[metric] for r in runs])
                target = sign * fixed[metric]
                result.append(
                    dict(
                        variant=variant,
                        label=COMMON,
                        metric=metric,
                        deterministic=deterministic,
                        stochastic=stochastic,
                        n_runs=len(runs),
                        proportion_runs_strictly_better=float(np.mean(score > target)),
                        proportion_exact_estimator_ties=float(np.mean(score == target)),
                        deterministic_percentile_higher_is_better=100
                        * float(np.mean(score < target) + 0.5 * np.mean(score == target)),
                    )
                )
    return result


def feasibility(name, x, alpha):
    norm = np.linalg.norm(x, axis=1)
    return dict(
        set=name,
        points=len(x),
        max_norm=float(norm.max()),
        max_radial_violation=float(np.maximum(norm - alpha, 0).max()),
        norm_tolerance=1e-9,
        violations=int((norm > alpha + 1e-9).sum()),
        frozen_squared_margin_violations=int((np.sum(x * x, axis=1) > alpha**2 + 1e-9).sum()),
    )


def cost_worker_init(output):
    global CONTEXT
    output = Path(output)
    h = json.loads((output / "hv_reference_point.json").read_text())
    grid = HVGrid(np.array(h["lower"]), np.array(h["reference"]))
    samples = np.load(ROOT / "experiments/runs" / data.RUN_ID / "hv_samples.npy", mmap_mode="r")
    CONTEXT = dict(
        output=output,
        grid=grid,
        samples=samples,
        refs=reference_arrays(),
        problem=phase7.load_problem()[0],
    )


def cost_worker(task):
    family, seed = task
    ctx = CONTEXT
    output = ctx["output"]
    stem = output / "controlled_timing" / f"{family.lower()}_seed{seed}"
    meta = json.loads(stem.with_suffix(".json").read_text())
    records, checks = [], []
    with np.load(stem.with_suffix(".npz"), allow_pickle=False) as d:
        for cp in meta["checkpoints"]:
            g = cp["generation"]
            x, z = d[f"g{g}_x"], d[f"g{g}_z"]
            f = d[f"g{g}_natural_f"]
            predicted = ctx["problem"].natural(x, scalar_check=True)
            if not np.allclose(predicted, f, atol=5e-14, rtol=2e-14):
                raise ValueError("checkpoint canonical RSM verification failed")
            if not np.allclose(z, ctx["problem"].normalize(f), atol=5e-14, rtol=2e-14):
                raise ValueError("checkpoint fixed global normalization differs")
            checks.append(feasibility(f"{family}_seed{seed}_g{g}", x, phase7.frozen.ALPHA))
            mask = np.bitwise_or.reduce(ctx["grid"].masks(z, ctx["samples"]), axis=0)
            spacing, sparsity = spacing_sparsity(z)
            intrinsic = dict(**ctx["grid"].estimate(mask), Spacing=spacing, Sparsity=sparsity)
            for label, ref in ((COMMON, "all"), (LOO, f"minus_{family.lower()}")):
                gd, igd = gd_igd(z, ctx["refs"][ref])
                records.append(
                    dict(
                        method=family,
                        seed=seed,
                        generation=g,
                        label=label,
                        reference=ref,
                        reference_size=len(ctx["refs"][ref]),
                        NFE=cp["nfe"],
                        T_total=cp["T_total"],
                        cpu_seconds=cp["cpu_seconds"],
                        observer_seconds=cp["observer_seconds_cumulative"],
                        N_returned=cp["N_returned"],
                        N_ND_before_dedup=cp["N_ND_before_dedup"],
                        N_unique_ND=cp["N_unique_ND"],
                        GD=gd,
                        IGD=igd,
                        **intrinsic,
                    )
                )
    return records, checks


def run(output):
    started = perf_counter()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    if dirty:
        raise ValueError("commit quality-analysis code and timing artifacts before evaluation")
    if (output / "phase8b_quality_completion.json").exists():
        raise ValueError("completed quality archive is immutable")
    if not (output / "timing_completion.json").exists():
        raise ValueError("finish isolated EA timing before other scientific postprocessing")
    policy = json.loads(data.POLICY.read_text())
    inputs = data.load_historical_parent_grid_inputs()
    x, z = inputs["x"], inputs["z"]
    with np.load(output / "dominance_index.npz", allow_pickle=False) as d:
        index = DominanceIndex(
            inputs["independent_count"], d["dominators"], d["dominated"], d["duplicate_pairs"]
        )
    h = json.loads((output / "hv_reference_point.json").read_text())
    grid = HVGrid(np.array(h["lower"]), np.array(h["reference"]))
    cache_dir = ROOT / "experiments/runs" / data.RUN_ID
    cache_meta = json.loads((cache_dir / "cache_metadata.json").read_text())
    if cache_meta["identity"]["reference"] != grid.reference.tolist():
        raise ValueError("common frozen HV integration cache differs")
    cache = np.memmap(
        cache_dir / "point_attainment.uint8",
        dtype=np.uint8,
        mode="r",
        shape=(len(z), grid.bytes_per_point),
    )
    refs = reference_arrays()
    with np.load(phase7.PHASE6 / "local_nbi_solutions_H20.npz", allow_pickle=False) as d:
        col = int(np.flatnonzero(d["H_values"] == 5)[0])
        raw_h5 = inputs["cnbi_offset"] + np.flatnonzero(d["H_membership"][:, col] & d["accepted"])
    native_sets = [
        dict(
            method="CNBI5",
            seed=0,
            ids=inputs["h5"],
            returned=492,
            nd_raw=int(nondominated_mask(z[raw_h5], equality_tolerance=inputs["tau"]).sum()),
        ),
        dict(method="VRF", seed=0, ids=inputs["vrf"], returned=66, nd_raw=66),
    ]
    for (family, seed), ids in inputs["runs"].items():
        selected, _ = index.front(ids)
        native_sets.append(
            dict(
                method=family,
                seed=seed,
                ids=selected,
                returned=inputs["returned"][(family, seed)],
                nd_raw=len(ids),
            )
        )
    kmax = min(len(item["ids"]) for item in native_sets if item["method"] != "VRF")
    kcommon = min(66, min(len(item["ids"]) for item in native_sets))
    write_json(
        output / "cardinality_availability.json",
        dict(
            K_common=kcommon,
            K_max_common_without_VRF=kmax,
            rule="minimum over all genuine fronts, never average",
        ),
    )
    if kcommon != 66:
        raise RuntimeError("a front has fewer than66 genuine points; no duplication is allowed")
    extended = [k for k in policy["K_extended_candidates"] if k <= kmax]
    grid_k = sorted(set(policy["K_four"] + extended + [kmax]))
    timing = {
        (r["method"], int(r["seed"])): r
        for f in ("nsga3", "moead")
        for r in data.rows(output / f"timing_{f}.csv")
    }
    native, curves, nearest, feasibility_records, orderings = [], [], [], [], {}

    def evaluate(item, ids, variant, k):
        method, seed = item["method"], item["seed"]
        points = z[ids]
        spacing, sparsity = spacing_sparsity(points)
        intrinsic = dict(
            **grid.estimate(union_mask(cache, ids)), Spacing=spacing, Sparsity=sparsity
        )
        runtime = timing.get((method, seed))
        result = []
        for label, ref in (
            (COMMON, "all"),
            (LOO, "minus_cnbi" if method == "CNBI5" else f"minus_{method.lower()}"),
        ):
            gd, igd = gd_igd(points, refs[ref])
            result.append(
                dict(
                    method=method,
                    seed=seed,
                    variant=variant,
                    K=k,
                    label=label,
                    reference=ref,
                    reference_size=len(refs[ref]),
                    N_returned=item["returned"] if variant == "native" else len(ids),
                    N_ND_before_dedup=item["nd_raw"] if variant == "native" else len(ids),
                    N_unique_ND=len(ids),
                    native_unique_ND=len(item["ids"]),
                    T_total_controlled=float(runtime["T_total"])
                    if runtime and variant == "native"
                    else None,
                    runtime_status="QUALITY_ONLY_CARDINALITY_ANALYSIS"
                    if variant != "native"
                    else "CONTROLLED_MATCHING_SEED"
                    if runtime
                    else (
                        "PENDING_H5_EQUIVALENCE"
                        if method == "CNBI5"
                        else "USER_FORBIDS_EXECUTION"
                        if method == "VRF"
                        else "SEED_NOT_TIMED"
                    ),
                    GD=gd,
                    IGD=igd,
                    **intrinsic,
                )
            )
        return result

    for item in native_sets:
        method, seed, ids = item["method"], item["seed"], item["ids"]
        name = f"{method}_seed{seed}"
        orderings[name] = ids[farthest_order(z[ids])]
        native.extend(evaluate(item, ids, "native", "native"))
        feasible = feasibility(name, x[ids], inputs["problem"].alpha)
        feasibility_records.append(feasible)
        d = nearest_distances(z[ids])
        nearest.append(
            dict(
                method=method,
                seed=seed,
                N=len(ids),
                min=float(d.min()),
                q01=float(np.quantile(d, 0.01)),
                q05=float(np.quantile(d, 0.05)),
                median=float(np.median(d)),
                threshold=policy["near_duplicate_diagnostic_threshold"],
                fraction_extremely_close=float(
                    np.mean(d <= policy["near_duplicate_diagnostic_threshold"])
                ),
                solutions_removed=0,
            )
        )
        for k in grid_k:
            if method == "VRF" and k > 66:
                continue
            curves.extend(evaluate(item, orderings[name][:k], "cardinality", k))
        print(f"Quality {name}: native={len(ids)}, full FPS ordering and K curves", flush=True)
    data.table(output / "native_metrics.csv", native)
    equalized = [dict(r, variant="equalized_K66") for r in curves if r["K"] == 66]
    data.table(output / "equalized_k66_metrics.csv", equalized)
    data.table(output / "cardinality_curve_metrics.csv", curves)
    np.savez_compressed(output / "candidate_farthest_orderings.npz", **orderings)
    data.table(output / "nearest_neighbor_diagnostics.csv", nearest)
    for name, records, keys in (
        ("native_metrics_summary.csv", native, ["method", "label"]),
        ("equalized_k66_summary.csv", equalized, ["method", "label"]),
        ("cardinality_curve_summary.csv", curves, ["method", "label", "K"]),
    ):
        data.table(
            output / name,
            grouped_summaries(records, keys, [*PRIMARY, "N_unique_ND", "T_total_controlled"]),
        )
    data.table(
        output / "deterministic_percentiles.csv",
        better_fractions(native, "native") + better_fractions(equalized, "K66"),
    )
    # All metrics below are computed after the serial timing campaign has ended.
    cost, checkpoint_checks = [], []
    tasks = [(family, seed) for family in ("NSGA3", "MOEAD") for seed in range(1001, 1011)]
    bounds = []
    for family, seed in tasks:
        stem = output / "controlled_timing" / f"{family.lower()}_seed{seed}"
        meta = json.loads(stem.with_suffix(".json").read_text())
        with np.load(stem.with_suffix(".npz"), allow_pickle=False) as d:
            for cp in meta["checkpoints"]:
                points = d[f"g{cp['generation']}_z"]
                bounds.append(
                    dict(
                        method=family,
                        seed=seed,
                        generation=cp["generation"],
                        outside_HV_reference=int(np.any(points >= grid.reference, axis=1).sum()),
                        below_common_lower=int(np.any(points < grid.lower, axis=1).sum()),
                    )
                )
    data.table(output / "checkpoint_hv_bounds_audit.csv", bounds)
    if any(r["outside_HV_reference"] or r["below_common_lower"] for r in bounds):
        raise ValueError("a checkpoint exceeds the frozen common HV box; no silent clipping")
    with ProcessPoolExecutor(
        max_workers=policy["postprocessing_workers"],
        initializer=cost_worker_init,
        initargs=(str(output),),
    ) as executor:
        for i, (metric_rows, checks) in enumerate(executor.map(cost_worker, tasks), start=1):
            cost.extend(metric_rows)
            checkpoint_checks.extend(checks)
            print(f"Post-timing checkpoint metrics {i}/20", flush=True)
    data.table(output / "cost_quality_metrics.csv", cost)
    cost_summary = grouped_summaries(
        cost, ["method", "label", "generation"], [*PRIMARY, "T_total", "cpu_seconds", "N_unique_ND"]
    )
    data.table(output / "cost_quality_summary.csv", cost_summary)
    feasibility_records.extend(checkpoint_checks)
    feasibility_records.append(
        feasibility("all_frozen_Phase7_candidates", x, inputs["problem"].alpha)
    )
    data.table(output / "feasibility.csv", feasibility_records)
    if any(r["violations"] or r["frozen_squared_margin_violations"] for r in feasibility_records):
        raise ValueError("an evaluated front violates the frozen sphere")
    # Quality-cost efficiency is computed only against one common target.
    efficient = []
    for family in ("NSGA3", "MOEAD"):
        for generation in policy["timing"]["generations"]:
            members = [
                r
                for r in cost
                if r["method"] == family and r["label"] == COMMON and r["generation"] == generation
            ]
            efficient.append(
                dict(
                    method=family,
                    generation=generation,
                    label=COMMON,
                    T_total_median=float(np.median([r["T_total"] for r in members])),
                    IGD_median=float(np.median([r["IGD"] for r in members])),
                    HV_median=float(np.median([r["HV"] for r in members])),
                    scope="EA_CONFIGURATIONS_ONLY_CNBI_VRF_COST_UNAVAILABLE",
                )
            )
    time_values = np.array([r["T_total_median"] for r in efficient])
    for criterion, values in (
        ("IGD", np.array([r["IGD_median"] for r in efficient])),
        ("negative_HV", -np.array([r["HV_median"] for r in efficient])),
    ):
        keep = nondominated_mask(
            np.column_stack([time_values, values]), equality_tolerance=np.zeros(2)
        )
        for row, selected in zip(efficient, keep, strict=True):
            row[f"nondominated_time_{criterion}"] = bool(selected)
    data.table(output / "quality_cost_pareto.csv", efficient)
    # Largest independent-reference coverage gaps are diagnostics, not new metrics.
    with np.load(output / "reference_final.npz", allow_pickle=False) as d:
        reference_ids = d["point_ids"]
    gap, nearest_id = cKDTree(z[inputs["h5"]]).query(z[reference_ids], k=1, eps=0.0, workers=1)
    coverage = []
    for rank, j in enumerate(np.argsort(-gap, kind="stable")[:50], start=1):
        source = int(reference_ids[j])
        f, run_id, seed, source_id = inputs["sources"][source]
        closest = int(inputs["h5"][nearest_id[j]])
        coverage.append(
            dict(
                rank=rank,
                reference_point_id=source,
                family=f,
                run_id=run_id,
                seed=seed,
                source_id=source_id,
                nearest_H5_point_id=closest,
                distance=float(gap[j]),
                **{f"x{k + 1}": float(v) for k, v in enumerate(x[source])},
                **{
                    f"z_{name}": float(z[source, k])
                    for k, name in enumerate(phase7.frozen.RESPONSES)
                },
                **{
                    f"delta_z_{name}": float(z[source, k] - z[closest, k])
                    for k, name in enumerate(phase7.frozen.RESPONSES)
                },
            )
        )
    data.table(output / "cnbi5_coverage_gaps.csv", coverage)
    paired_precision = []
    with np.load(output / "reference_sensitivity_lineage.npz", allow_pickle=False) as lineage:
        names = list(map(str, lineage["names"]))

        def composition_hv(name):
            i = names.index(f"composition_{name}")
            ids = lineage["front_ids"][
                lineage["front_offsets"][i] : lineage["front_offsets"][i + 1]
            ]
            return grid.values(union_mask(cache, ids))

        full_hv = composition_hv("NMV")
        for family, base in (("VRF", "NM"), ("NSGA3", "MV"), ("MOEAD", "NV")):
            delta = full_hv - composition_hv(base)
            paired_precision.append(
                dict(
                    added_family=family,
                    base=base,
                    delta_HV=float(delta.mean()),
                    paired_QMC_SE=float(delta.std(ddof=1) / 2),
                    min_scramble_gain=float(delta.min()),
                    max_scramble_gain=float(delta.max()),
                    integration_replicates=4,
                    ground_truth_claim=False,
                )
            )
    data.table(output / "reference_marginal_hv_precision.csv", paired_precision)
    code = [
        Path(__file__),
        Path(data.__file__),
        data.POLICY,
        *sorted((ROOT / "src/cnbi_v2/benchmark").glob("*.py")),
    ]
    metadata = dict(
        run_id=data.RUN_ID,
        status="QUALITY_COMPLETE_CNBI_COST_PENDING",
        quality_source_commit=commit,
        quality_working_tree_dirty_at_launch=False,
        code_config_sha256=phase7.hashes(code),
        phase8a=json.loads((output / "phase8a_completion.json").read_text()),
        controlled_timing=json.loads((output / "timing_completion.json").read_text()),
        input_sha256=inputs["phase7_metadata"]["input_sha256"],
        phase8_input_sha256=phase7.hashes(
            [
                output / "phase8a_completion.json",
                output / "hv_reference_point.json",
                output / "reference_final.npz",
                data.POLICY,
                ROOT / "references/metadata/phase_08_legacy_metrics/source_audit.json",
                ROOT / "tests/reference_cases/legacy_metrics/spacing_oracle.npz",
            ]
        ),
        phase7_manifest_sha256=sha256_file(phase7.OUTPUT / "checksums.sha256"),
        phase7_metadata_sha256=sha256_file(phase7.OUTPUT / "metadata.json"),
        canonical_response_order=list(phase7.frozen.RESPONSES),
        alpha=inputs["problem"].alpha,
        protocol=policy,
        hv_reference=h,
        normalization_unchanged=True,
        candidate_reference_clipping=False,
        baseline_H=5,
        baseline_cardinality=408,
        numerical_x_tolerance=inputs["xtol"],
        numerical_dominance_tolerance=inputs["tau"].tolist(),
        K_common=66,
        K_max_common_without_VRF=kmax,
        K_curve_grid=grid_k,
        stochastic_quality_runs_per_family=30,
        deterministic_quality_sets_per_family=1,
        stochastic_cost_runs_per_family=10,
        candidate_orderings_nested=True,
        benchmark_references_complete=True,
        common_self_included=True,
        family_LOO_targets_differ_no_automatic_ranking=True,
        better_fraction_reference=COMMON,
        percentile_definition=(
            "100*(fraction of runs with worse oriented score +.5*ties); higher better"
        ),
        HV_exact=False,
        HV_estimator="four common scrambled Sobol nets, power16; see protocol/SE",
        HV_ties_may_reflect_quadrature_resolution=True,
        max_norm=max(r["max_norm"] for r in feasibility_records),
        sphere_violations=sum(r["violations"] for r in feasibility_records),
        max_radial_violation=max(r["max_radial_violation"] for r in feasibility_records),
        CNBI_cost="PENDING_H5_DIRECT_EQUIVALENCE_FAILED_OWNER_PRESERVES408",
        CNBI_timing_executions=0,
        VRF_cost="NOT_MEASURED_USER_FORBIDS_EXECUTION",
        VRF_optimization_executions=0,
        VRF_timing_executions=0,
        RSM_refit=False,
        data_reconstructed=False,
        previous_MC_anchors_PA_NBI_H20_pipelines_repeated=False,
        new_synthetic_benchmark_scenarios=False,
        adaptive_refinement_started=False,
        versions={
            n: importlib.metadata.version(n) for n in ("numpy", "scipy", "pymoo", "matplotlib")
        },
        quality_postprocessing_seconds=perf_counter() - started,
    )
    write_json(output / "metadata.json", metadata)
    write_json(
        output / "phase8b_quality_completion.json",
        dict(
            status=metadata["status"],
            native_rows=len(native),
            cardinality_rows=len(curves),
            cost_checkpoint_rows=len(cost),
            source_commit=commit,
            K_max=kmax,
            CNBI_cost=metadata["CNBI_cost"],
            VRF_executions=0,
            sphere_violations=metadata["sphere_violations"],
        ),
    )
    print(
        json.dumps(
            {
                "status": metadata["status"],
                "Kmax": kmax,
                "seconds": metadata["quality_postprocessing_seconds"],
            }
        ),
        flush=True,
    )


def finalize_archive(output):
    path = output / "metadata.json"
    metadata = json.loads(path.read_text())
    metadata["output_sha256"] = {
        p.relative_to(output).as_posix(): sha256_file(p)
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name not in {"metadata.json", "checksums.sha256"}
    }
    write_json(path, metadata)
    (output / "checksums.sha256").write_text(
        "".join(
            f"{sha256_file(p)}  {p.relative_to(output).as_posix()}\n"
            for p in sorted(output.rglob("*"))
            if p.is_file() and p.name != "checksums.sha256"
        ),
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=data.OUTPUT)
    args = parser.parse_args()
    run(args.output)
