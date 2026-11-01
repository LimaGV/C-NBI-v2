"""Post-hoc applied PA/anisotropy ablation: archived solutions only, no solves.

uv run python -m scripts.validation.turning_pa_anisotropy [--input-root PATH]
"""

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from importlib.metadata import version
from math import comb
from pathlib import Path
from time import perf_counter

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from cnbi_v2.benchmark.hypervolume import HVGrid
from cnbi_v2.benchmark.metrics import gd_igd, spacing_sparsity
from cnbi_v2.benchmark.selection import farthest_order
from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import canonical_decision_points, nondominated_mask
from cnbi_v2.reference.indicators import distances

ROOT = Path(__file__).resolve().parents[2]
P5 = Path("results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024")
P8 = Path("results/phase_08_final_benchmark/turning_standalone_correction_20261025")
REF = Path("results/phase_08_final_benchmark/turning_reference_sensitivity_20261024")
OUTPUT = Path("results/phase_08_pa_anisotropy/turning_pa_anisotropy_20261101")
METRICS = ("GD", "IGD", "HV", "Spacing", "Sparsity")
RESPONSES = ("T", "MTTF", "WR", "Ra", "Rt", "Kp", "ROI", "OEE")
POLICY = Path("docs/policies/cnbi_standalone_correction.json")
BENCHMARK = Path("docs/policies/benchmark_cardinality_cost.json")


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def table(path, values):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, list(values[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(values)


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def arrays(path):
    with np.load(path, allow_pickle=False) as data:
        return {key: data[key] for key in data.files}


def selection(root):
    global_rows = rows(root / P5 / "global_pa_B2000.csv")
    if [r["pass"] for r in global_rows] != ["True", "True"] + ["False"] * 5:
        raise ValueError("Frozen global PA dimension is not two")
    cutoff = float(global_rows[1]["observed_singular"]) / float(global_rows[0]["observed_singular"])
    selected = []
    for row in rows(root / P5 / "selected_subsets_B2000.csv"):
        s = json.loads(row["observed_singular_values"])
        k = int(row["k"])
        if row["selected"] != "True" or len(s) != k - 1 or min(s) <= 0:
            raise ValueError("Invalid archived PA subset spectrum")
        q = s[-1] / s[0]
        selected.append(
            dict(
                subset_id=row["subset_id"],
                responses=row["responses"],
                k=k,
                sigma_max=s[0],
                sigma_min=s[-1],
                q=q,
                q_cutoff=cutoff,
                retain_anisotropy=q >= cutoff,
                H=5,
                subproblems=comb(5 + k - 1, k - 1),
            )
        )
    kept = [r for r in selected if r["retain_anisotropy"]]
    if (
        len(selected),
        len(kept),
        sum(r["k"] == 2 for r in kept),
        sum(r["k"] == 3 for r in kept),
        sum(r["subproblems"] for r in kept),
    ) != (37, 27, 19, 8, 282):
        raise ValueError("Expected 37 -> 27 (19 pairs / 8 trios), 282 subproblems not confirmed")
    return cutoff, selected


def front(raw, source_rows, policy):
    ids = np.asarray(source_rows, dtype=np.int64)
    ids = ids[raw["accepted"][ids]]
    representatives, _ = canonical_decision_points(raw["x"][ids], tolerance=policy["x_tolerance"])
    unique = ids[representatives]
    nd = unique[nondominated_mask(raw["z"][unique], equality_tolerance=policy["z_tolerance"])]
    return unique, nd


def matched(a, b, tolerance):
    return np.any(np.max(np.abs(a[:, None, :] - b[None, :, :]), axis=2) <= tolerance, axis=1)


def frozen_paths():
    paths = [POLICY, BENCHMARK]
    paths += [
        P5 / n
        for n in (
            "global_pa_B2000.csv",
            "selected_subsets_B2000.csv",
            "metadata.json",
            "nominal_normalization.csv",
            "nominal_chim.npz",
            "checksums.sha256",
        )
    ]
    paths += [
        P8 / n
        for n in (
            "H5_rep1.npz",
            "official_cnbi5.npz",
            "H5_rep1_records.csv",
            "native_metrics.csv",
            "equalized_k66_metrics.csv",
            "checksums.sha256",
            "timing_cnbi.csv",
            "metadata.json",
        )
    ]
    paths += [P8 / f"H5_rep{i}.npz" for i in range(2, 6)]
    paths += [
        REF / n
        for n in (
            "reference_final.npz",
            "hv_reference_point.json",
            "hv_numerical_cache.json",
            "checksums.sha256",
        )
    ]
    return paths


def audit(root):
    hashes = {}
    for path in frozen_paths():
        if not (root / path).is_file():
            raise FileNotFoundError(f"Required frozen artifact missing: {path.as_posix()}")
        digest = sha256_file(root / path)
        committed = subprocess.check_output(["git", "show", f"HEAD:{path.as_posix()}"], cwd=ROOT)
        if hashlib.sha256(committed).hexdigest() != digest:
            raise ValueError(f"Frozen input differs from published Git blob: {path}")
        hashes[path.as_posix()] = digest
    return hashes


def figures(output, comparison, subsets, coverage_distances):
    colors = ["#426b8a", "#ba7543"]
    fig = Figure(figsize=(9, 4.4), layout="constrained")
    FigureCanvasAgg(fig)
    axes = fig.subplots(1, 2)
    for ax, mode in zip(axes, ("native", "equalized_K66"), strict=True):
        values = [
            next(r for r in comparison if r["mode"] == mode and r["metric"] == m)["delta_percent"]
            for m in METRICS
        ]
        ax.bar(METRICS, values, color=colors[1])
        ax.axhline(0, color="0.3", linewidth=0.7)
        ax.set(title=mode.replace("_", " "), ylabel="Change from PA (%)")
        ax.grid(False)
    fig.suptitle("PA + anisotropy: signed metric changes relative to PA")
    export(fig, output, "metric_changes")
    fig = Figure(figsize=(9, 4), layout="constrained")
    FigureCanvasAgg(fig)
    for ax, key, title in zip(
        fig.subplots(1, 3),
        ("subsets", "subproblems", "ND"),
        ("Subsets", "NBI subproblems", "Native ND solutions"),
        strict=True,
    ):
        values = (
            [37, 27] if key == "subsets" else [492, 282] if key == "subproblems" else [409, 228]
        )
        ax.bar(["PA", "PA + anisotropy"], values, color=colors)
        ax.set(title=title, ylabel="Count")
        ax.tick_params(axis="x", labelsize=8)
        for i, v in enumerate(values):
            ax.text(i, v, str(v), ha="center", va="bottom")
        ax.set_ylim(0, max(values) * 1.18)
        ax.grid(False)
    export(fig, output, "effort_and_cardinality")
    fig = Figure(figsize=(7, 4), layout="constrained")
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    triples = sorted((r for r in subsets if r["k"] == 3), key=lambda r: r["q"])
    ax.bar(
        [r["subset_id"] for r in triples],
        [r["q"] for r in triples],
        color=[colors[int(r["retain_anisotropy"])] for r in triples],
    )
    ax.axhline(subsets[0]["q_cutoff"], color="0.25", linestyle="--", label="Global cutoff")
    ax.set(ylabel="q = smallest / largest singular value", title="PA-approved trios")
    ax.tick_params(axis="x", rotation=70, labelsize=8)
    ax.legend(frameon=False)
    ax.grid(False)
    export(fig, output, "anisotropy_selection")
    fig = Figure(figsize=(6, 4), layout="constrained")
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    for label, values, color in zip(
        ("PA", "PA + anisotropy"), coverage_distances, colors, strict=True
    ):
        ax.plot(
            np.sort(values), np.arange(1, len(values) + 1) / len(values), label=label, color=color
        )
    ax.set(
        xlabel="Independent reference → front nearest distance",
        ylabel="Cumulative fraction",
        title="Reference coverage (fixed normalization)",
    )
    ax.legend(frameon=False)
    ax.grid(False)
    export(fig, output, "reference_coverage")


def export(fig, output, name):
    folder = output / "figures"
    folder.mkdir(exist_ok=True)
    fig.savefig(folder / f"{name}.png", dpi=600)
    fig.savefig(folder / f"{name}.pdf", metadata={"CreationDate": None, "ModDate": None})


def run(root, output):
    if output.exists():
        raise ValueError("Output already exists; completed ablations are immutable")
    started = perf_counter()
    hashes = audit(root)
    cutoff, subsets = selection(root)
    policy = json.loads((root / POLICY).read_text())
    benchmark = json.loads((root / BENCHMARK).read_text())
    raw = arrays(root / P8 / "H5_rep1.npz")
    records = rows(root / P8 / "H5_rep1_records.csv")
    if len(records) != 492 or not raw["accepted"].all():
        raise ValueError("Standalone archive is not the complete accepted 492-row H5 run")
    catalog = [r["subset_id"] for r in subsets]
    for i, record in enumerate(records):
        if (
            int(record["row_id"]) != i
            or record["subset"] != catalog[raw["subsets"][i]]
            or float(record["eq_norm"]) > policy["solver_options"]["equality_tolerance"]
            or float(record["sphere_margin"]) < -policy["solver_options"]["sphere_tolerance"]
        ):
            raise ValueError("Subset/row identity or frozen feasibility acceptance mismatch")
    for i in range(2, 6):
        repeat = arrays(root / P8 / f"H5_rep{i}.npz")
        if any(not np.array_equal(raw[k], repeat[k]) for k in raw):
            raise ValueError("Archived H5 timing repetitions differ scientifically")
    norm = rows(root / P5 / "nominal_normalization.csv")
    if [r["response"] for r in norm] != list(RESPONSES):
        raise ValueError("Frozen response order changed")
    z = (
        raw["natural_f"] * [float(r["sign"]) for r in norm] - [float(r["utopia"]) for r in norm]
    ) / [float(r["amplitude"]) for r in norm]
    if not np.array_equal(z, raw["z"]):
        raise ValueError("Stored global normalization differs from frozen Phase5 transform")
    kept = {r["subset_id"] for r in subsets if r["retain_anisotropy"]}
    filtered_rows = np.array([i for i, r in enumerate(records) if r["subset"] in kept])
    unique_pa, nd_pa = front(raw, np.arange(492), policy)
    unique_combined, nd_combined = front(raw, filtered_rows, policy)
    if not np.array_equal(nd_pa, raw["nd_ids"]) or not np.array_equal(unique_pa, raw["unique_ids"]):
        raise ValueError("PA recomposition does not reproduce official standalone front")
    reference = arrays(root / REF / "reference_final.npz")
    if len(reference["z"]) != 18503 or reference["point_ids"].max() >= 19866:
        raise ValueError("Independent reference identity/size changed")
    bounds = json.loads((root / REF / "hv_reference_point.json").read_text())
    hv = benchmark["hv_quadrature"]
    grid = HVGrid(
        np.array(bounds["lower"]),
        np.array(bounds["reference"]),
        power=hv["power"],
        seeds=tuple(hv["seeds"]),
    )
    sample_path = root / "experiments/runs/turning_reference_sensitivity_20261024/hv_samples.npy"
    samples = np.load(sample_path, allow_pickle=False) if sample_path.exists() else grid.samples()
    sample_digest = hashlib.sha256(samples.tobytes()).hexdigest()
    cache_meta = json.loads((root / REF / "hv_numerical_cache.json").read_text())
    if sample_digest != cache_meta["samples_sha256"]:
        raise ValueError("HV quadrature nodes differ from official Phase8 nodes")
    masks = grid.masks(raw["z"], samples)

    def union(ids):
        return np.bitwise_or.reduce(masks[ids], axis=0)

    def evaluate(ids):
        gd, igd = gd_igd(raw["z"][ids], reference["z"])
        spacing, sparsity = spacing_sparsity(raw["z"][ids])
        return dict(GD=gd, IGD=igd, **grid.estimate(union(ids)), Spacing=spacing, Sparsity=sparsity)

    order_pa, order_combined = (
        farthest_order(raw["z"][nd_pa]),
        farthest_order(raw["z"][nd_combined]),
    )
    evaluated, membership, fronts = [], [], {}
    for mode, k in (
        ("native", None),
        ("equalized_pairwise", min(len(nd_pa), len(nd_combined))),
        ("equalized_K66", 66),
    ):
        for arm, nd, order, nraw, nuniq, nsub in (
            ("PA", nd_pa, order_pa, 492, len(unique_pa), 37),
            ("PA_ANISOTROPY", nd_combined, order_combined, 282, len(unique_combined), 27),
        ):
            ids = nd if k is None else nd[order[:k]]
            fronts[f"{mode}_{arm}_source_rows"] = ids
            evaluated.append(
                dict(
                    mode=mode,
                    arm=arm,
                    K=len(ids),
                    source_subsets=nsub,
                    source_subproblems=nraw,
                    native_unique=nuniq,
                    native_ND=len(nd),
                    **evaluate(ids),
                )
            )
            membership.extend(
                dict(mode=mode, arm=arm, rank=j, source_row=int(i), subset_id=records[i]["subset"])
                for j, i in enumerate(ids)
            )
    official = next(
        r
        for r in rows(root / P8 / "native_metrics.csv")
        if r["method"] == "CNBI5" and r["reference"] == "minus_cnbi"
    )
    for metric in (*METRICS, "HV_QMC_SE"):
        if not np.isclose(evaluated[0][metric], float(official[metric]), rtol=2e-14, atol=2e-15):
            raise ValueError(f"Official native PA metric not reproduced: {metric}")
    official66 = next(
        r
        for r in rows(root / P8 / "equalized_k66_metrics.csv")
        if r["method"] == "CNBI5" and r["reference"] == "minus_cnbi"
    )
    for metric in (*METRICS, "HV_QMC_SE"):
        if not np.isclose(evaluated[4][metric], float(official66[metric]), rtol=2e-14, atol=2e-15):
            raise ValueError(f"Official K66 PA metric not reproduced: {metric}")
    comparison = []
    for a, b in zip(evaluated[::2], evaluated[1::2], strict=True):
        for metric in METRICS:
            delta = b[metric] - a[metric]
            comparison.append(
                dict(
                    mode=a["mode"],
                    metric=metric,
                    PA=a[metric],
                    PA_ANISOTROPY=b[metric],
                    delta=delta,
                    delta_percent=100 * delta / a[metric] if a[metric] else None,
                )
            )
    retained = matched(raw["x"][nd_pa], raw["x"][nd_combined], policy["x_tolerance"])
    pa_hv = evaluated[0]["HV"]
    contributions = []
    for subset in (r for r in subsets if not r["retain_anisotropy"]):
        sid = subset["subset_id"]
        remaining = np.array([i for i, r in enumerate(records) if r["subset"] != sid])
        other_unique, other_nd = front(raw, remaining, policy)
        supported = matched(raw["x"][nd_pa], raw["x"][other_unique], policy["x_tolerance"])
        without_hv = grid.estimate(union(other_nd))["HV"]
        contributions.append(
            dict(
                subset_id=sid,
                responses=subset["responses"],
                q=subset["q"],
                removed_subproblems=subset["subproblems"],
                PA_ND_exclusively_supported=int((~supported).sum()),
                exclusive_HV=pa_hv - without_hv,
                exclusive_HV_percent=100 * (pa_hv - without_hv) / pa_hv,
            )
        )
    coverage = []
    for j, response in enumerate(RESPONSES):
        a, b = raw["z"][nd_pa, j], raw["z"][nd_combined, j]
        npa = sum(response in r["responses"].split("|") for r in subsets)
        ncombined = sum(
            response in r["responses"].split("|") for r in subsets if r["retain_anisotropy"]
        )
        coverage.append(
            dict(
                response=response,
                PA_subsets=npa,
                combined_subsets=ncombined,
                PA_min=float(a.min()),
                combined_min=float(b.min()),
                PA_max=float(a.max()),
                combined_max=float(b.max()),
                range_ratio=float(np.ptp(b) / np.ptp(a)),
            )
        )
    coverage_distances = [distances(reference["z"], raw["z"][ids]) for ids in (nd_pa, nd_combined)]
    reference_coverage = [
        dict(
            arm=arm,
            reference_points=len(values),
            mean_distance=float(values.mean()),
            median_distance=float(np.median(values)),
            q95_distance=float(np.quantile(values, 0.95)),
            max_distance=float(values.max()),
        )
        for arm, values in zip(("PA", "PA_ANISOTROPY"), coverage_distances, strict=True)
    ]
    timing = [r for r in rows(root / P8 / "timing_cnbi.csv") if int(r["H"]) == 5]
    costs = [
        dict(
            arm="PA",
            subsets=37,
            subproblems=492,
            unique=len(unique_pa),
            ND=len(nd_pa),
            eliminated_subproblems=0,
            theoretical_reduction_percent=0.0,
            observed_end_to_end_seconds=float(np.median([float(r["T_total"]) for r in timing])),
            counterfactual_end_to_end_seconds=None,
        ),
        dict(
            arm="PA_ANISOTROPY",
            subsets=27,
            subproblems=282,
            unique=len(unique_combined),
            ND=len(nd_combined),
            eliminated_subproblems=210,
            theoretical_reduction_percent=100 * 210 / 492,
            observed_end_to_end_seconds=None,
            counterfactual_end_to_end_seconds=None,
        ),
    ]
    if any(sha256_file(root / p) != digest for p, digest in hashes.items()):
        raise ValueError("Frozen source changed during postprocessing")
    output.mkdir(parents=True)
    for name, values in (
        ("subset_selection", subsets),
        ("metrics", evaluated),
        ("metric_deltas", comparison),
        ("front_membership", membership),
        ("removed_subset_contributions", contributions),
        ("objective_coverage", coverage),
        ("reference_coverage", reference_coverage),
        ("costs", costs),
    ):
        table(output / f"{name}.csv", values)
    np.savez_compressed(
        output / "fronts.npz",
        **fronts,
        PA_x=raw["x"][nd_pa],
        PA_z=raw["z"][nd_pa],
        combined_x=raw["x"][nd_combined],
        combined_z=raw["z"][nd_combined],
    )
    figures(output, comparison, subsets, coverage_distances)
    protocol = dict(
        status="EXPERIMENTAL_POST_HOC_ABLATION_MAIN_METHOD_UNCHANGED",
        created_at_utc=datetime.now(UTC).isoformat(),
        source_base_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        input_sha256=hashes,
        source_sha256=sha256_file(Path(__file__)),
        versions={p: version(p) for p in ("numpy", "scipy", "matplotlib")},
        rule="q_S=sigma_(k-1)/sigma_1; retain q_S >= global_sigma_2/global_sigma_1",
        global_dimension=2,
        q_cutoff=cutoff,
        cutoff_selection="owner-specified; no metric tuning",
        spectra="stored centered CHIM spectra from Phase5; no new PA or SVD simulation",
        solution_source="Phase8 standalone H5 repetition1, all raw rows before dedup/ND",
        timing_repeats="five bitwise-identical H5 outputs, not five independent quality replicates",
        independent_reference=(
            "18503 frozen points; all CNBI resolutions excluded; empirical, not truth"
        ),
        normalization="Phase5 fixed global MIN orientation, verified bitwise; no clipping",
        policy=policy,
        HV_quadrature=hv,
        HV_bounds=bounds,
        HV_samples_sha256=sample_digest,
        equalization=(
            "frozen extreme-preserving FPS, stable source-row ties; "
            "pairwise min ND and official K66"
        ),
        PA_native_and_K66_reproduce_official_metrics=True,
        PA_ND_retained=int(retained.sum()),
        PA_ND_lost=int((~retained).sum()),
        PA_ND_retention_percent=100 * float(retained.mean()),
        combined_new_ND=int(
            (~matched(raw["x"][nd_combined], raw["x"][nd_pa], policy["x_tolerance"])).sum()
        ),
        all_objectives_represented=all(r["combined_subsets"] > 0 for r in coverage),
        reference_nearest_distance_worsened_count=int(
            np.sum(coverage_distances[1] > coverage_distances[0])
        ),
        new_optimizer_calls=0,
        new_MC=0,
        new_RSM=0,
        new_anchors=0,
        new_Pareto_reference_points=0,
        wall_time_postprocessing_seconds=perf_counter() - started,
        time_savings="NOT_MEASURED; eliminated subproblem count is not a measured speedup",
    )
    save_json(output / "protocol.json", protocol)
    report(output, comparison, protocol, contributions)
    (output / ".gitattributes").write_text(
        "* -text\n* whitespace=cr-at-eol\n", encoding="utf-8"
    )
    payloads = sorted(p for p in output.rglob("*") if p.is_file())
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.relative_to(output).as_posix()}\n" for p in payloads),
        encoding="utf-8",
    )
    print(
        json.dumps(
            dict(
                status="COMPLETE",
                q_cutoff=cutoff,
                subsets=27,
                subproblems=282,
                PA_ND=len(nd_pa),
                combined_ND=len(nd_combined),
                seconds=protocol["wall_time_postprocessing_seconds"],
            )
        )
    )


def report(output, comparisons, protocol, contributions):
    lines = [
        "# Applied PA versus PA + anisotropy ablation",
        "",
        "Experimental post-hoc analysis; the principal C-NBI method is unchanged.",
        "",
        "## Frozen design and integrity",
        "",
        f"q_S = sigma_(k-1)/sigma_1; retain q_S >= {protocol['q_cutoff']:.16g}. "
        "The cutoff is the global second/first singular-value ratio (d=2), "
        "specified before evaluation. "
        "All 37 PA-approved centered spectra are read from Phase5; 27 survive (19 pairs, 8 trios). "
        "All pairs have q=1; ten trios are removed.",
        "",
        "The full standalone H5 archive (492 accepted rows) is filtered by subset identity BEFORE "
        "decision deduplication and full eight-objective dominance. PA recomposition reproduces "
        "411 unique / 409 ND; the combined filter gives 228 unique / 228 ND. "
        "All five archived timing repetitions are bitwise identical scientifically.",
        "",
        "## Quality",
        "",
        "Independent empirical reference: 18,503 archived points, "
        "excluding the entire C-NBI family. "
        "Fixed Phase5 global MIN normalization and Phase8 coordinate tolerances are unchanged. "
        "GD/IGD use mean Euclidean nearest distances; Spacing uses ddof=1; Sparsity is mean "
        "nearest-neighbor distance. HV reuses the official bounds and exact quadrature nodes: "
        "four PCG64 scrambled Sobol nets, 2^16 nodes each, seeds 20260–20263. "
        "Native PA and K66 metrics reproduce their official saved values. "
        "HV is an estimate, with the original across-scramble QMC SE.",
        "",
        "|Comparison|Metric|PA|PA + anisotropy|Change (%)|",
        "|---|---|---:|---:|---:|",
    ]
    for r in comparisons:
        lines.append(
            f"|{r['mode']}|{r['metric']}|{r['PA']:.8g}|{r['PA_ANISOTROPY']:.8g}|"
            f"{r['delta_percent']:+.4f}|"
        )
    lines += [
        "",
        "Lower GD/IGD is better; higher HV is better. Lower Spacing describes regularity; "
        "lower Sparsity describes density and is not a universal quality ranking. "
        "Equalization uses the unchanged Phase8 extreme-preserving FPS and archived-row tie rule: "
        "K=228 for this pair and K=66 for the official Phase8 cardinality control.",
        "",
        "## Coverage and eliminated subsets",
        "",
        f"The combined front retains {protocol['PA_ND_retained']} of 409 PA ND decisions "
        f"({protocol['PA_ND_retention_percent']:.4f}%), loses {protocol['PA_ND_lost']}, "
        f"and introduces {protocol['combined_new_ND']} formerly non-ND decisions. "
        "Decision correspondence uses the frozen L-infinity deduplication tolerance, "
        "rather than requiring identical representative row IDs. All eight objectives remain "
        "represented by retained subsets. Per-objective extrema, range ratios and subset counts "
        "are in objective_coverage.csv. The reference coverage table and ECDF show "
        "nearest-front distances across all 18,503 reference points. "
        "Geometric/objective coverage is not certified Pareto coverage.",
        "",
        "Removed-subset contributions below are leave-one-subset-out, holding the rest of PA "
        "fixed. Exclusive ND support accounts for duplicate decisions across subsets. "
        "Exclusive HV uses the same common quadrature nodes; these marginal contributions are "
        "not additive when several subsets are removed together.",
        "",
        "|Removed subset|q|Exclusively supported PA ND|Exclusive HV (%)|",
        "|---|---:|---:|---:|",
    ]
    for r in contributions:
        lines.append(
            f"|{r['subset_id']}|{r['q']:.6g}|{r['PA_ND_exclusively_supported']}|"
            f"{r['exclusive_HV_percent']:.5f}|"
        )
    native = {r["metric"]: r for r in comparisons if r["mode"] == "native"}
    lines += [
        "",
        "## Cost and practical conclusion",
        "",
        "The filter removes 10/37 subsets (27.0270%) and 210/492 NBI subproblems (42.6829%). "
        "These are theoretical reductions in requested work, not measured runtime savings. "
        "No filtered optimization campaign was run. The original PA runtime is historical "
        "evidence only; filtered end-to-end runtime is left undefined. Postprocessing time "
        "is recorded separately in protocol.json. No proportional speedup is claimed.",
        "",
        f"Native IGD changes by {native['IGD']['delta_percent']:+.4f}% and native HV by "
        f"{native['HV']['delta_percent']:+.4f}%. "
        "Equalized IGD and HV also deteriorate, so the loss is not explained solely by "
        "different front cardinalities. The geometric cutoff removes useful trade-off regions "
        "despite preserving all individual-objective minima. It does not meet the stated goal "
        "of reducing cost without compromising quality. No practical advantage is demonstrated "
        "for this cutoff; retain PA as the principal applied-case configuration. "
        "A quality-sacrificing alternative would require an explicit acceptance criterion and "
        "measured runtime, neither inferred here.",
        "",
        "## Reproducibility and limits",
        "",
        "No optimizer, new subproblem, Monte Carlo, RSM fit, anchor or reference construction "
        "is executed. Frozen inputs are checked against their published Git blobs and rehashed "
        "after analysis. Source rows and all evaluated front memberships are exported. "
        "No old result is overwritten. Figures are in English, PNG 600 dpi and vector PDF, "
        "without axis grids. This is one deterministic applied case; timing repetitions are "
        "not independent quality replicates, and no inferential statistics are used.",
        "",
        "Reproduce: `uv run python -m scripts.validation.turning_pa_anisotropy` "
        "from a full checkout (or pass `--input-root` for an immutable source checkout). "
        "The output path must not already exist; use `--output` for a separate reproduction.",
        "",
    ]
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / OUTPUT)
    args = parser.parse_args()
    run(args.input_root.resolve(), args.output.resolve())
