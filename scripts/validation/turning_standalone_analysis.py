"""Reevaluate only dependencies of the standalone Phase8 CNBI correction.

The previous Phase8 archive is immutable, historical_parent_grid_analysis.
No optimizer, reference resampling, reference FPS, EA or VRF is executed here.
"""

import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from cnbi_v2.benchmark.hypervolume import HVGrid
from cnbi_v2.benchmark.metrics import gd_igd, spacing_sparsity, summary
from cnbi_v2.benchmark.selection import farthest_order
from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import nondominated_mask

from . import turning_benchmark_inputs as historical
from . import turning_cnbi_standalone as standalone
from .turning_final_benchmark import PRIMARY, feasibility, grouped_summaries
from .turning_reference import ROOT, write_json

OLD = historical.OUTPUT
OUTPUT = standalone.OUTPUT
COMMON = "HISTORICAL_COMMON_H20_TARGET"
LOO = "LEAVE_ONE_FAMILY_OUT"
HISTORICAL_NAME = "CNBI_H5_extracted_from_H20_parent_grid"


def load(path):
    with np.load(path, allow_pickle=False) as d:
        return {k: d[k] for k in d.files}


def numeric_rows(path):
    rows = historical.rows(path)
    for row in rows:
        for key, value in row.items():
            if value == "":
                row[key] = None
            else:
                try:
                    row[key] = float(value)
                except (ValueError, TypeError):
                    pass
    return rows


def metric_values(z, ref, grid, masks):
    gd, igd = gd_igd(z, ref)
    spacing, sparsity = spacing_sparsity(z)
    return dict(
        GD=gd,
        IGD=igd,
        **grid.estimate(np.bitwise_or.reduce(masks, axis=0)),
        Spacing=spacing,
        Sparsity=sparsity,
    )


def percentiles(records, variant):
    result = []
    members = [r for r in records if r["label"] == COMMON]
    for method in ("NSGA3", "MOEAD"):
        for metric in PRIMARY:
            sign = 1 if metric == "HV" else -1
            target = sign * next(r[metric] for r in members if r["method"] == "CNBI5")
            values = sign * np.array([r[metric] for r in members if r["method"] == method])
            result.append(
                dict(
                    variant=variant,
                    label=COMMON,
                    stochastic=method,
                    metric=metric,
                    proportion_runs_strictly_better=float(np.mean(values > target)),
                    deterministic_percentile_higher_is_better=100
                    * float(np.mean(values < target) + 0.5 * np.mean(values == target)),
                )
            )
    return result


def analyze(output=OUTPUT):
    if (output / "analysis_completion.json").exists():
        raise ValueError("completed correction is immutable")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise ValueError("commit analysis source/timed outputs before evaluation")
    for line in (OLD / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        if sha256_file(OLD / name) != digest:
            raise ValueError(f"historical Phase8 artifact changed: {name}")
    policy = json.loads(standalone.POLICY.read_text())
    h = json.loads((OLD / "hv_reference_point.json").read_text())
    grid = HVGrid(np.array(h["lower"]), np.array(h["reference"]))
    samples = grid.samples()
    canonical = load(OLD / "canonical_candidates.npz")
    independent = load(OLD / "reference_final.npz")
    if len(independent["z"]) != 18503 or independent["point_ids"].max() >= 19866:
        raise ValueError("independent reference identity/family exclusion changed")
    phase7 = ROOT / "results/phase_07_reference_front/turning_multifamily_loo_20261024"
    refs = {"minus_cnbi": independent["z"], "all": load(phase7 / "reference_all.npz")["z"]}
    main = load(output / "H5_rep1.npz")
    ids = main["nd_ids"]
    x, z = main["x"][ids], main["z"][ids]
    masks = grid.masks(z, samples)
    order = farthest_order(z)
    np.savez_compressed(
        output / "official_cnbi5.npz", x=x, z=z, natural_f=main["natural_f"][ids], source_rows=ids
    )
    np.savez_compressed(
        output / "cnbi5_farthest_order.npz",
        local_order=order,
        source_rows=ids[order],
        K66_source_rows=ids[order[:66]],
    )
    timing = numeric_rows(output / "timing_cnbi.csv")
    t5 = [r for r in timing if r["H"] == 5]
    runtime = float(np.median([r["T_total"] for r in t5]))
    counts = t5[0]
    kgrid = [20, 30, 40, 50, 66, 100, 150, 200, 250, 300, 303]
    native, curves = [], []

    def evaluate(selected, variant, k):
        result = []
        for label, ref in ((COMMON, "all"), (LOO, "minus_cnbi")):
            result.append(
                dict(
                    method="CNBI5",
                    seed=0,
                    variant=variant,
                    K=k,
                    label=label,
                    reference=ref,
                    reference_size=len(refs[ref]),
                    N_returned=492 if variant == "native" else len(selected),
                    N_ND_before_dedup=int(
                        nondominated_mask(main["z"], equality_tolerance=policy["z_tolerance"]).sum()
                    )
                    if variant == "native"
                    else len(selected),
                    N_unique_ND=len(selected),
                    native_unique_ND=len(z),
                    T_total_controlled=runtime if variant == "native" else None,
                    runtime_status="CONTROLLED_STANDALONE_MATCHING_OUTPUT"
                    if variant == "native"
                    else "QUALITY_ONLY_CARDINALITY_ANALYSIS",
                    **metric_values(z[selected], refs[ref], grid, masks[selected]),
                )
            )
        return result

    native = evaluate(np.arange(len(z)), "native", "native")
    for k in kgrid:
        curves.extend(evaluate(order[:k], "cardinality", k))
    # Keep every other-method number exactly. Only relabel the historical common
    # target so it cannot falsely claim self-inclusion of the corrected H5.
    for name, rows in (("native_metrics.csv", native), ("cardinality_curve_metrics.csv", curves)):
        for old in numeric_rows(OLD / name):
            if old["method"] == "CNBI5":
                continue
            if old["label"] == "COMMON_REFERENCE_SELF_INCLUDED":
                old["label"] = COMMON
            rows.append(old)
        standalone.table(output / name, rows)
    equal = [dict(r, variant="equalized_K66") for r in curves if r["K"] == 66]
    standalone.table(output / "equalized_k66_metrics.csv", equal)
    for name, rows, keys in (
        ("native_metrics_summary.csv", native, ["method", "label"]),
        ("equalized_k66_summary.csv", equal, ["method", "label"]),
        ("cardinality_curve_summary.csv", curves, ["method", "label", "K"]),
    ):
        standalone.table(output / name, grouped_summaries(rows, keys, PRIMARY))
    standalone.table(
        output / "deterministic_percentiles.csv",
        percentiles(native, "native") + percentiles(equal, "K66"),
    )
    # Reuse the exact archived references and seed subsets. No resampling/ND/FPS.
    lineage = load(OLD / "reference_sensitivity_lineage.npz")
    distances = cKDTree(z).query(canonical["z"], k=1, eps=0.0, workers=1)[0]
    lookup = {}
    for i, name in enumerate(lineage["names"]):
        front = lineage["front_ids"][lineage["front_offsets"][i] : lineage["front_offsets"][i + 1]]
        gd = float(cKDTree(canonical["z"][front]).query(z, k=1, eps=0.0, workers=1)[0].mean())
        lookup[str(name)] = (gd, float(distances[front].mean()))
    run_rows = historical.rows(OLD / "reference_run_sensitivity_replicates.csv")
    for row in run_rows:
        row["GD_CNBI5"], row["IGD_CNBI5"] = lookup[row["reference_name"]]
        for key in ("r", "replicate"):
            row[key] = int(row[key])
    standalone.table(output / "reference_run_sensitivity_replicates.csv", run_rows)
    # summarize also includes immutable structural values originally read as text.
    summaries = []
    for r in (5, 10, 15, 20, 25, 30):
        selected = [v for v in run_rows if v["r"] == r and v["selection"] != "prefix"]
        for metric in ("GD_CNBI5", "IGD_CNBI5"):
            summaries.append(dict(r=r, metric=metric, **summary([v[metric] for v in selected])))
    unchanged = [
        r
        for r in historical.rows(OLD / "reference_run_sensitivity.csv")
        if r["metric"] not in ("GD_CNBI5", "IGD_CNBI5")
    ]
    standalone.table(output / "reference_run_sensitivity.csv", summaries + unchanged)
    compositions = historical.rows(OLD / "reference_composition_sensitivity.csv")
    for row in compositions:
        row["GD_CNBI5"], row["IGD_CNBI5"] = lookup[row["reference_name"]]
    standalone.table(output / "reference_composition_sensitivity.csv", compositions)
    by_name = {r["composition"]: r for r in compositions}
    marginals = historical.rows(OLD / "reference_marginal_effects.csv")
    for row in marginals:
        a, b = by_name[row["base"]], by_name[row["full"]]
        row["delta_GD"] = b["GD_CNBI5"] - a["GD_CNBI5"]
        row["delta_IGD"] = b["IGD_CNBI5"] - a["IGD_CNBI5"]
    standalone.table(output / "reference_marginal_effects.csv", marginals)
    ref_order = load(OLD / "farthest_orderings.npz")["reference_final"]
    ref_k = historical.rows(OLD / "reference_cardinality_sensitivity.csv")
    for row in ref_k:
        row["GD_CNBI5"], row["IGD_CNBI5"] = gd_igd(z, canonical["z"][ref_order[: int(row["K_R"])]])
    standalone.table(output / "reference_cardinality_sensitivity.csv", ref_k)
    print("512 frozen references reevaluated; structural reference outputs preserved", flush=True)
    # Each resolution's own measured output supplies its quality; no membership.
    resolution, checks, timing_summary = [], [], []
    for h_value in policy["H_values"]:
        d = load(output / f"H{h_value}_rep1.npz")
        nd = d["nd_ids"]
        points = d["z"][nd]
        h_masks = masks if h_value == 5 else grid.masks(points, samples)
        runs = [r for r in timing if r["H"] == h_value]
        for key in ("T_solver", "T_total"):
            timing_summary.append(dict(H=h_value, quantity=key, **summary([r[key] for r in runs])))
        for label, ref in ((COMMON, "all"), (LOO, "minus_cnbi")):
            for run in runs:
                resolution.append(
                    dict(
                        **run,
                        label=label,
                        reference=ref,
                        reference_size=len(refs[ref]),
                        **metric_values(points, refs[ref], grid, h_masks),
                    )
                )
        checks.append(
            feasibility(f"standalone_H{h_value}", d["x"][d["accepted"]], standalone.frozen.ALPHA)
        )
        print(
            f"Standalone H{h_value}: {len(points)}ND, quality paired with own runtime", flush=True
        )
    standalone.table(output / "standalone_resolution_metrics.csv", resolution)
    standalone.table(output / "timing_summary.csv", timing_summary)
    standalone.table(output / "feasibility.csv", checks)
    if any(r["violations"] or r["frozen_squared_margin_violations"] for r in checks):
        raise ValueError("standalone sphere feasibility failed")
    # Historical correspondence is audit-only and never selects the baseline.
    parent = load(
        ROOT / "results/phase_06_local_nbi/turning_local_nbi_h20_20261024/"
        "local_nbi_solutions_H20.npz"
    )
    parent_lookup = {
        (int(s), tuple(c)): j
        for j, (s, c) in enumerate(
            zip(parent["subset_indices"], parent["integer_compositions"], strict=True)
        )
    }
    diagnostic = []
    tau = np.array(policy["z_tolerance"])
    for j, (s, composition) in enumerate(zip(main["subsets"], main["compositions"], strict=True)):
        p = parent_lookup[(int(s), tuple(4 * composition))]
        dx, dz = main["x"][j] - parent["x"][p], main["z"][j] - parent["normalized_responses"][p]
        diagnostic.append(
            dict(
                row=j,
                subset=int(s),
                composition=json.dumps(composition.tolist()),
                parent_row=p,
                x_Linf=float(np.max(np.abs(dx))),
                x_L2=float(np.linalg.norm(dx)),
                z_Linf=float(np.max(np.abs(dz))),
                z_L2=float(np.linalg.norm(dz)),
                t_parent=float(parent["t"][p]),
                t_standalone=float(main["t"][j]),
                delta_t=float(main["t"][j] - parent["t"][p]),
                parent_dominates_new=bool(np.all(dz >= -tau) and np.any(dz > tau)),
                new_dominates_parent=bool(np.all(dz <= tau) and np.any(dz < -tau)),
                divergent=bool(np.max(np.abs(dx)) > 1e-5 or np.max(np.abs(dz)) > 1e-5),
            )
        )
    standalone.table(output / "parent_vs_standalone_all492.csv", diagnostic)
    standalone.table(
        output / "historical_24_divergent_cases.csv", [r for r in diagnostic if r["divergent"]]
    )
    old_metrics = numeric_rows(OLD / "native_metrics.csv")
    impact = []
    for label in (COMMON, LOO):
        previous_label = "COMMON_REFERENCE_SELF_INCLUDED" if label == COMMON else LOO
        previous = next(
            r for r in old_metrics if r["method"] == "CNBI5" and r["label"] == previous_label
        )
        new = next(r for r in native if r["method"] == "CNBI5" and r["label"] == label)
        for key in ("N_unique_ND", *PRIMARY):
            impact.append(
                dict(
                    label=label,
                    metric=key,
                    old_H5_from_H20=previous[key],
                    new_standalone_H5=new[key],
                    delta=new[key] - previous[key],
                )
            )
    standalone.table(output / "old_vs_new_metrics.csv", impact)
    # Controlled EA numbers/time remain read-only. Only the corrected CNBI family
    # is added to the same historical-target quality-cost comparison.
    cost = numeric_rows(OLD / "cost_quality_metrics.csv")
    for row in cost:
        if row["label"] == "COMMON_REFERENCE_SELF_INCLUDED":
            row["label"] = COMMON
    cnbi_cost = [
        dict(r, method="CNBI5" if r["H"] == 5 else f"CNBI_H{int(r['H'])}") for r in resolution
    ]
    standalone.table(output / "cost_quality_ea_preserved.csv", cost)
    standalone.table(output / "cost_quality_cnbi.csv", cnbi_cost)
    efficient = []
    for method in ("NSGA3", "MOEAD"):
        for generation in (50, 100, 200, 300, 400):
            rows = [
                r
                for r in cost
                if r["label"] == COMMON and r["method"] == method and r["generation"] == generation
            ]
            efficient.append(
                dict(
                    method=method,
                    configuration=f"g{generation}",
                    T_total=float(np.median([r["T_total"] for r in rows])),
                    IGD=float(np.median([r["IGD"] for r in rows])),
                    HV=float(np.median([r["HV"] for r in rows])),
                )
            )
    for h_value in policy["H_values"]:
        rows = [r for r in cnbi_cost if r["label"] == COMMON and r["H"] == h_value]
        efficient.append(
            dict(
                method=f"CNBI_H{h_value}",
                configuration=f"H{h_value}",
                T_total=float(np.median([r["T_total"] for r in rows])),
                IGD=rows[0]["IGD"],
                HV=rows[0]["HV"],
            )
        )
    for metric, sign in (("IGD", 1), ("HV", -1)):
        keep = nondominated_mask(
            np.array([[r["T_total"], sign * r[metric]] for r in efficient]),
            equality_tolerance=np.zeros(2),
        )
        for row, accepted in zip(efficient, keep, strict=True):
            row[f"nondominated_time_{metric}"] = bool(accepted)
    standalone.table(output / "quality_cost_pareto.csv", efficient)
    # Store hashes for every reused reference input, rather than copying/rebuilding.
    used = [
        OLD / name
        for name in (
            "checksums.sha256",
            "reference_final.npz",
            "canonical_candidates.npz",
            "reference_seed_subsamples.npz",
            "reference_sensitivity_lineage.npz",
            "farthest_orderings.npz",
            "hv_reference_point.json",
            "candidate_farthest_orderings.npz",
            "native_metrics.csv",
            "cardinality_curve_metrics.csv",
            "cost_quality_metrics.csv",
            "reference_run_sensitivity_replicates.csv",
            "reference_composition_sensitivity.csv",
            "reference_cardinality_sensitivity.csv",
        )
    ]
    metadata = dict(
        status="STANDALONE_CORRECTION_COMPLETE",
        baseline="standalone H5 repetition1",
        baseline_cardinality=len(z),
        H5_subproblems=492,
        accepted=counts["accepted"],
        failures=counts["failures"],
        unique=counts["unique"],
        official_H=5,
        historical_baseline_label=HISTORICAL_NAME,
        historical_archive_status="historical_parent_grid_analysis; immutable",
        historical_common_target_label=COMMON,
        common_target_change="none; historical target relabeled, not new self-included reference",
        official_independent_reference_size=18503,
        independent_reference_CNBI_points=0,
        old_archive_sha256=sha256_file(OLD / "checksums.sha256"),
        reused_input_sha256={p.relative_to(ROOT).as_posix(): sha256_file(p) for p in used},
        source_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        source_sha256=sha256_file(Path(__file__)),
        HV_bounds=h,
        K_common=66,
        K_max_common_without_VRF=303,
        historical_correspondence=dict(
            coincident=sum(not r["divergent"] for r in diagnostic),
            divergent=sum(r["divergent"] for r in diagnostic),
            max_x_Linf=max(r["x_Linf"] for r in diagnostic),
            max_z_Linf=max(r["z_Linf"] for r in diagnostic),
        ),
        EA_runs_or_timing_repeated=False,
        VRF_executions=0,
        reference_resampling_repeated=False,
        reference_FPS_repeated=False,
        RSM_refit=False,
        data_reconstructed=False,
        solver_options_changed=False,
        subsets_changed=False,
    )
    write_json(output / "metadata.json", metadata)
    write_json(output / "analysis_completion.json", dict(status="COMPLETE", references_reused=512))


if __name__ == "__main__":
    analyze()
