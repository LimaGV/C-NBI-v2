"""Deterministic local NBI from frozen B=2000 subset identities, with nested H."""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import version
from math import comb
from pathlib import Path
from time import perf_counter

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import (
    LocalNBIProblem,
    NBIOptions,
    canonical_decision_points,
    directed_coverage_distances,
    local_nbi_geometry,
    nondominated_mask,
    solve_nbi_lattice,
)
from cnbi_v2.optimization import (
    Direction,
    evaluate_responses,
    quadratic_responses_from_coefficients,
)
from cnbi_v2.simplex import nested_indices, simplex_lattice

from .turning_reference import RAW, RAW_SHA256, RESPONSES, ROOT, TERMS, write_csv, write_json

PHASE2 = ROOT / "results/phase_02_anchors/turning_original_codes_20261024"
PHASE5 = ROOT / "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024"
SELECTED = PHASE5 / "selected_subsets_B2000.csv"
MODELS = PHASE2 / "coded_models.csv"
ANCHORS = PHASE2 / "anchors_sphere.csv"
PAYOFF = PHASE2 / "payoff_sphere.csv"
NORMALIZATION = PHASE5 / "nominal_normalization.csv"
INPUT_HASHES = {
    SELECTED: "198d03f7756ba9f0633d87a6142e5ac6da014a135f78df405994cc10b6b77e46",
    PHASE5 / "metadata.json": "61f84b930aa8b0adb9a9bc48f2129dbcc675f73bc582d7053f500188d5f87992",
    MODELS: "9d5590b5f2ba43592fa13753cd86afaa583fadbbd4f0d180acb1b5eef0b3e3e9",
    ANCHORS: "462b6b18002c2ae784758a26ebe500bf95de3a8ff1c504aab6986924d9d5bafd",
    PAYOFF: "2e410a2d3e222047442d75d526166c6af5e5d6787c2c93dcbe2b184003e124c2",
    PHASE2 / "metadata.json": "880971d1bbf449e10f4abe6ca949998ecb59eac39f28b382e2d7902604be61af",
    NORMALIZATION: "bc19f7ef44d5ee86b10b4fb789fe55742b0dc6dc2119277d5811e7464bb76dc0",
    RAW: RAW_SHA256,
}
DIRECTIONS = (
    Direction.MAX,
    Direction.MAX,
    Direction.MIN,
    Direction.MIN,
    Direction.MIN,
    Direction.MIN,
    Direction.MAX,
    Direction.MAX,
)
H_VALUES = (2, 4, 5, 10, 20)
ALPHA = 8**0.25
RUN_ID = "turning_local_nbi_h20_20261024"


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def verified_inputs():
    for path, digest in INPUT_HASHES.items():
        if sha256_file(path) != digest:
            raise ValueError(f"canonical SHA-256 mismatch: {path.name}")
    phase2 = json.loads((PHASE2 / "metadata.json").read_text(encoding="utf-8"))
    phase5 = json.loads((PHASE5 / "metadata.json").read_text(encoding="utf-8"))
    if (
        phase2["dataset_sha256"] != RAW_SHA256
        or phase2["alpha"] != ALPHA
        or phase2["coding"]["coding_id"] != "original_spreadsheet_codes_1_682"
        or phase2["directions"] != dict(zip(RESPONSES, DIRECTIONS, strict=True))
        or phase5["response_order"] != list(RESPONSES)
        or phase5["anchor_order"] != list(RESPONSES)
        or phase5["dataset_sha256"] != RAW_SHA256
        or phase5["nominal_payoff_sha256"] != INPUT_HASHES[PAYOFF]
        or phase5["reference_B"] != 2000
        or phase5["global_dimension_B2000"] != 2
        or phase5["selected_counts_B2000"] != {"pairs": 19, "triples": 18, "quadruples": 0}
    ):
        raise ValueError("canonical source metadata/order/coding/selection contract mismatch")
    model_rows = read_rows(MODELS)
    if list(model_rows[0]) != ["coefficient", *RESPONSES] or [
        row["coefficient"] for row in model_rows
    ] != list(TERMS):
        raise ValueError("nominal coefficient order mismatch")
    coefficients = np.array([[float(row[r]) for r in RESPONSES] for row in model_rows])
    if hashlib.sha256(coefficients.tobytes()).hexdigest() != phase2["coefficient_bytes_sha256"]:
        raise ValueError("nominal coefficient byte identity mismatch")
    models = quadratic_responses_from_coefficients(coefficients, 3)
    anchor_rows = read_rows(ANCHORS)
    norm_rows = read_rows(NORMALIZATION)
    payoff_rows = read_rows(PAYOFF)
    if (
        any(
            [r["response"] for r in rows] != list(RESPONSES)
            for rows in (anchor_rows, norm_rows, payoff_rows)
        )
        or any(
            [r["direction"] for r in rows] != list(DIRECTIONS) for rows in (anchor_rows, norm_rows)
        )
        or list(payoff_rows[0]) != ["response", *RESPONSES]
    ):
        raise ValueError("nominal response/direction/anchor order mismatch")
    anchors = np.array([[float(r[f"x{i}"]) for i in range(1, 4)] for r in anchor_rows])
    payoff = np.array([[float(r[name]) for name in RESPONSES] for r in payoff_rows])
    utopia = np.array([float(r["utopia"]) for r in norm_rows])
    amplitude = np.array([float(r["amplitude"]) for r in norm_rows])
    signs = np.array([d.minimization_sign for d in DIRECTIONS])
    if (
        not np.array_equal(utopia, phase5["utopia_nominal_oriented"])
        or not np.array_equal(amplitude, phase5["nominal_amplitudes"])
        or not np.array_equal(utopia, signs * np.diag(payoff))
    ):
        raise ValueError("fixed Phase 5 normalization mismatch")
    tolerance = np.array([float(r["optimality_tolerance"]) for r in norm_rows])
    subsets = read_rows(SELECTED)
    identities = [r["subset_id"] for r in subsets]
    if (
        len(subsets) != 37
        or len(set(identities)) != 37
        or sorted(identities) != phase5["selected_ids_B2000"]
        or [sum(int(r["k"]) == k for r in subsets) for k in (2, 3, 4)] != [19, 18, 0]
    ):
        raise ValueError("must consume the exact 37 B=2000 identities")
    catalog = []
    for row in subsets:
        indices = tuple(int(i) - 1 for i in row["subset_id"].split("_")[1:])
        if (
            len(indices) != int(row["k"])
            or tuple(sorted(set(indices))) != indices
            or row["responses"] != "|".join(RESPONSES[j] for j in indices)
            or row["selected"] != "True"
            or not all(json.loads(row["component_passes"]))
        ):
            raise ValueError("selected subset index/response/PASS mismatch")
        catalog.append((row["subset_id"], indices))
    return models, anchors, payoff, utopia, amplitude, signs, tolerance, catalog


def distribution(values):
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if not len(finite):
        return dict.fromkeys(["min", "median", "q95", "max", "mean"])
    return {
        "min": float(finite.min()),
        "median": float(np.median(finite)),
        "q95": float(np.quantile(finite, 0.95, method="linear")),
        "max": float(finite.max()),
        "mean": float(finite.mean()),
    }


def csv_number(value):
    return value if np.isfinite(value) else ""


def plot_sensitivity(output, summaries):
    figure = Figure(figsize=(8, 4.2), layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.add_subplot()
    axes.plot(
        [r["H"] for r in summaries],
        [r["coverage_mean"] for r in summaries],
        marker="o",
        label="Mean directed coverage distance",
    )
    axes.plot(
        [r["H"] for r in summaries],
        [r["coverage_q95"] for r in summaries],
        marker="s",
        label="q95 directed coverage distance",
    )
    axes.set(
        xlabel="Simplex-Lattice H",
        ylabel="Euclidean distance in fixed 8-response space",
        title="Internal coverage of H=20 nondominated set",
    )
    axes.set_xticks(H_VALUES)
    axes.grid(alpha=0.2)
    axes.legend()
    figure.savefig(output / "h_coverage_sensitivity.png", dpi=180)


def run_local_nbi(output: Path, *, run_id: str):
    started = perf_counter()
    if not run_id or any(
        c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in run_id
    ):
        raise ValueError("run_id must be nonempty alphanumeric/underscore/hyphen")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("nonempty run directory: choose a fresh run_id/output")
    models, anchors, payoff, utopia, amplitudes, signs, optimality, catalog = verified_inputs()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    options = NBIOptions()
    lattices = {k: simplex_lattice(k, 20) for k in (2, 3)}
    count = sum(len(lattices[len(c)].weights) for _, c in catalog)
    points, natural, oriented, normalized = (
        np.full((count, width), np.nan) for width in (3, 8, 8, 8)
    )
    accepted = np.zeros(count, dtype=np.bool_)
    t_values = np.full(count, np.nan)
    memberships = np.zeros((count, len(H_VALUES)), dtype=np.bool_)
    compositions = np.zeros((count, 3), dtype=np.int64)
    subset_indices = np.zeros(count, dtype=np.int64)
    parent_weight_indices = np.zeros(count, dtype=np.int64)
    records, attempts, solver_rows, geometries = [], [], [], []
    all_solutions, elapsed = [], []
    cursor = 0
    for subset_index, (identifier, indices) in enumerate(catalog):
        k = len(indices)
        geometry = local_nbi_geometry(
            payoff[np.ix_(indices, indices)],
            [DIRECTIONS[j] for j in indices],
            optimality_tolerance=optimality[list(indices)],
        )
        problem = LocalNBIProblem(
            tuple(models[j] for j in indices), geometry, anchors[list(indices)], ALPHA
        )
        lattice = lattices[k]
        result = solve_nbi_lattice(problem, lattice, options=options)
        n = len(result.solutions)
        segment = slice(cursor, cursor + n)
        subset_indices[segment] = subset_index
        compositions[segment, :k] = lattice.compositions
        parent_weight_indices[segment] = np.arange(n)
        for column, h in enumerate(H_VALUES):
            memberships[cursor + nested_indices(lattice, h), column] = True
        geometries.append(
            {
                "subset_id": identifier,
                "indices": indices,
                "vertices": geometry.vertices.tolist(),
                "utopia": geometry.normalization.utopia.tolist(),
                "amplitudes": geometry.normalization.amplitudes.tolist(),
                "normal": geometry.normal.tolist(),
                "centroid": geometry.centroid.tolist(),
                "orientation_dot": geometry.orientation_dot,
                "unit_norm": float(np.linalg.norm(geometry.normal)),
                "orthogonality_residual": geometry.orthogonality_residual,
                "singular_values": geometry.singular_values.tolist(),
                "rank_tolerance": geometry.rank_tolerance,
                "processing_order": result.processing_order,
            }
        )
        for j, solution in enumerate(result.solutions):
            idx = cursor + j
            chosen = solution.trials[-1]
            accepted[idx] = solution.accepted
            if solution.accepted:
                points[idx] = solution.point
                t_values[idx] = solution.t
                natural[idx] = evaluate_responses(models, solution.point)
                oriented[idx] = signs * natural[idx]
                normalized[idx] = (oriented[idx] - utopia) / amplitudes
            records.append(
                [
                    idx,
                    identifier,
                    k,
                    20,
                    j,
                    json.dumps(lattice.compositions[j].tolist()),
                    json.dumps(lattice.weights[j].tolist()),
                    *[csv_number(v) for v in points[idx]],
                    csv_number(t_values[idx]),
                    csv_number(t_values[idx]),
                    csv_number(chosen.sphere_margin),
                    csv_number(chosen.eq_norm),
                    chosen.solver_success,
                    solution.accepted,
                    chosen.iterations,
                    chosen.status,
                    chosen.message,
                    chosen.start.kind,
                    len(solution.trials),
                    result.elapsed_seconds[j],
                ]
            )
            for attempt_index, trial in enumerate(solution.trials):
                attempts.append(
                    [
                        idx,
                        identifier,
                        attempt_index,
                        trial.start.kind,
                        json.dumps(trial.start.point.tolist()),
                        trial.start.t,
                        *[csv_number(v) for v in trial.point],
                        csv_number(trial.t),
                        csv_number(trial.eq_norm),
                        csv_number(trial.sphere_margin),
                        trial.solver_success,
                        trial.accepted,
                        trial.iterations,
                        trial.status,
                        trial.message,
                    ]
                )
        ok = [s for s in result.solutions if s.accepted]
        eq_stats = distribution([s.trials[-1].eq_norm for s in ok])
        iterations = distribution([s.trials[-1].iterations for s in result.solutions])
        solver_rows.append(
            [
                identifier,
                k,
                n,
                len(ok),
                n - len(ok),
                sum(len(s.trials) for s in result.solutions),
                sum(t.iterations for s in result.solutions for t in s.trials),
                *[iterations[key] for key in ["min", "median", "q95", "max"]],
                *[eq_stats[key] for key in ["median", "q95", "max"]],
                float(result.elapsed_seconds.sum()),
                float(result.elapsed_seconds.mean()),
            ]
        )
        all_solutions.extend(result.solutions)
        elapsed.extend(result.elapsed_seconds.tolist())
        cursor += n
    output.mkdir(parents=True, exist_ok=True)
    write_csv(
        output / "local_nbi_records.csv",
        [
            "solution_id",
            "subset_id",
            "k",
            "H_parent",
            "parent_weight_index",
            "composition",
            "beta",
            "x1",
            "x2",
            "x3",
            "t",
            "objective_t",
            "sphere_margin",
            "eq_norm",
            "solver_success",
            "accepted",
            "iterations",
            "status",
            "message",
            "start_type",
            "attempt_count",
            "solve_seconds",
        ],
        records,
    )
    write_csv(
        output / "solver_attempts.csv",
        [
            "solution_id",
            "subset_id",
            "attempt_index",
            "start_type",
            "start_x",
            "start_t",
            "x1",
            "x2",
            "x3",
            "t",
            "eq_norm",
            "sphere_margin",
            "solver_success",
            "accepted",
            "iterations",
            "status",
            "message",
        ],
        attempts,
    )
    write_csv(
        output / "solver_summary.csv",
        [
            "subset_id",
            "k",
            "subproblems",
            "accepted",
            "failed",
            "attempts",
            "total_iterations",
            "iterations_min",
            "iterations_median",
            "iterations_q95",
            "iterations_max",
            "eq_median",
            "eq_q95",
            "eq_max",
            "solve_seconds",
            "seconds_per_problem",
        ],
        solver_rows,
    )
    write_json(output / "local_geometry.json", geometries)
    x_tolerance = float(64 * np.finfo(float).eps * max(1.0, ALPHA))
    objective_tolerance = (
        64 * np.finfo(float).eps * np.maximum(1.0, np.max(np.abs(normalized[accepted]), axis=0))
        if accepted.any()
        else np.zeros(8)
    )
    nd_sets, provenance, nd_summary, lattice_summary = {}, [], [], []
    for column, h in enumerate(H_VALUES):
        selected_indices = np.flatnonzero(memberships[:, column])
        valid_indices = selected_indices[accepted[selected_indices]]
        representatives, canonical = canonical_decision_points(
            points[valid_indices], tolerance=x_tolerance
        )
        keep = nondominated_mask(
            normalized[valid_indices[representatives]], equality_tolerance=objective_tolerance
        )
        nd = valid_indices[representatives[keep]]
        nd_sets[h] = nd
        nd_set = set(map(int, nd))
        for local_index, parent in enumerate(valid_indices):
            canonical_id = int(valid_indices[canonical[local_index]])
            subset_index = subset_indices[parent]
            k = len(catalog[subset_index][1])
            provenance.append(
                [
                    h,
                    int(parent),
                    catalog[subset_index][0],
                    json.dumps((compositions[parent, :k] // (20 // h)).tolist()),
                    json.dumps((compositions[parent, :k] / 20).tolist()),
                    canonical_id,
                    canonical_id in nd_set,
                ]
            )
        theoretical = sum(comb(h + len(c) - 1, len(c) - 1) for _, c in catalog)
        lattice_summary.append(
            [h, theoretical, len(selected_indices), comb(h + 1, 1), comb(h + 2, 2)]
        )
        nd_summary.append([h, theoretical, len(valid_indices), len(representatives), len(nd)])
    coverage_rows, sensitivity = [], []
    for j, h in enumerate(H_VALUES):
        nd = nd_sets[h]
        reference = nd_sets[20]
        distances = (
            directed_coverage_distances(normalized[reference], normalized[nd])
            if len(reference) and len(nd)
            else np.empty(0)
        )
        reverse = (
            directed_coverage_distances(normalized[nd], normalized[reference])
            if len(reference) and len(nd)
            else np.empty(0)
        )
        coverage, reversed_stats = distribution(distances), distribution(reverse)
        for direction, ids, values in [
            ("ND20_TO_NDH", reference, distances),
            ("NDH_TO_ND20", nd, reverse),
        ]:
            for idx, value in zip(ids, values, strict=False):
                coverage_rows.append([h, direction, int(idx), float(value)])
        item = dict(
            zip(
                [
                    "H",
                    "theoretical_subproblems",
                    "accepted_subproblems",
                    "unique_decision_points",
                    "full_space_nd_points",
                ],
                nd_summary[j],
                strict=True,
            )
        )
        item.update({f"coverage_{key}": coverage[key] for key in ["mean", "median", "q95", "max"]})
        item.update({f"reverse_{key}": reversed_stats[key] for key in ["mean", "q95", "max"]})
        item["delta_nd_from_previous_H"] = len(nd) - len(nd_sets[H_VALUES[j - 1]]) if j else None
        item["coverage_q95_reduction_from_previous_H"] = (
            sensitivity[-1]["coverage_q95"] - coverage["q95"]
            if j and coverage["q95"] is not None and sensitivity[-1]["coverage_q95"] is not None
            else None
        )
        sensitivity.append(item)
    write_csv(
        output / "simplex_lattice_summary.csv",
        [
            "H",
            "theoretical_subproblems",
            "parent_memberships",
            "weights_per_pair",
            "weights_per_trio",
        ],
        lattice_summary,
    )
    write_csv(
        output / "full_space_nd_summary.csv",
        [
            "H",
            "theoretical_subproblems",
            "accepted_subproblems",
            "unique_decision_points",
            "full_space_nd_points",
        ],
        nd_summary,
    )
    write_csv(
        output / "h_sensitivity.csv", list(sensitivity[0]), [list(r.values()) for r in sensitivity]
    )
    write_csv(
        output / "h_coverage_distances.csv",
        ["H", "direction", "source_solution_id", "nearest_distance"],
        coverage_rows,
    )
    write_csv(
        output / "provenance.csv",
        [
            "H",
            "solution_id",
            "subset_id",
            "integer_composition_at_H",
            "beta",
            "canonical_solution_id",
            "canonical_point_nondominated",
        ],
        provenance,
    )
    np.savez_compressed(
        output / "local_nbi_solutions_H20.npz",
        allow_pickle=False,
        x=points,
        t=t_values,
        natural_responses=natural,
        oriented_responses=oriented,
        normalized_responses=normalized,
        accepted=accepted,
        integer_compositions=compositions,
        subset_indices=subset_indices,
        parent_weight_indices=parent_weight_indices,
        H_membership=memberships,
        H_values=np.array(H_VALUES, dtype=np.int64),
    )
    plot_sensitivity(output, sensitivity)
    for path, digest in INPUT_HASHES.items():
        if sha256_file(path) != digest:
            raise RuntimeError(f"immutable input changed during NBI: {path.name}")
    code_paths = [
        Path(__file__),
        ROOT / "scripts/validation/turning_reference.py",
        ROOT / "uv.lock",
        *sorted((ROOT / "src/cnbi_v2/nbi").glob("*.py")),
        *sorted((ROOT / "src/cnbi_v2/simplex").glob("*.py")),
        ROOT / "src/cnbi_v2/optimization/quadratic.py",
        ROOT / "src/cnbi_v2/optimization/anchors.py",
        ROOT / "src/cnbi_v2/chim/normalization.py",
        ROOT / "src/cnbi_v2/chim/geometry.py",
    ]
    last_trials = [s.trials[-1] for s in all_solutions if s.accepted]
    metadata = {
        "run_id": run_id,
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": commit,
        "git_working_tree_dirty": dirty,
        "dataset_sha256": RAW_SHA256,
        "selected_subsets_sha256": INPUT_HASHES[SELECTED],
        "nominal_model_sha256": INPUT_HASHES[MODELS],
        "nominal_payoff_sha256": INPUT_HASHES[PAYOFF],
        "nominal_anchor_sha256": INPUT_HASHES[ANCHORS],
        "subset_ids": [s for s, _ in catalog],
        "subset_counts": {"pairs": 19, "triples": 18, "quadruples": 0},
        "response_order": RESPONSES,
        "directions": dict(zip(RESPONSES, DIRECTIONS, strict=True)),
        "alpha": ALPHA,
        "H_values": H_VALUES,
        "H_parent": 20,
        "unique_subproblems": count,
        "theoretical_counts": dict(zip(H_VALUES, [r[1] for r in nd_summary], strict=True)),
        "solver": "SLSQP deterministic local solve, no global-optimality certificate",
        "solver_options": asdict(options),
        "acceptance_rule": "success and all finite and "
        "alpha^2-x.T*x >= -sphere_tolerance and ||equality residual||_2 <= equality_tolerance",
        "accepted": int(accepted.sum()),
        "failed": int((~accepted).sum()),
        "success_rate": float(accepted.mean()),
        "total_solver_attempts": len(attempts),
        "failed_solution_ids": np.flatnonzero(~accepted).tolist(),
        "eq_norm_distribution": distribution([t.eq_norm for t in last_trials]),
        "sphere_margin_distribution": distribution([t.sphere_margin for t in last_trials]),
        "chosen_iterations_distribution": distribution(
            [s.trials[-1].iterations for s in all_solutions]
        ),
        "total_solver_iterations": sum(t.iterations for s in all_solutions for t in s.trials),
        "solve_seconds": float(sum(elapsed)),
        "seconds_per_unique_subproblem": float(np.mean(elapsed)),
        "elapsed_seconds_total": perf_counter() - started,
        "local_normalization": "per-subset nominal payoff; independent of Phase 5 normalization",
        "full_space_normalization": "unchanged fixed nominal Phase 5 u/a; all eight responses",
        "deduplication_tolerance_x_Linf": x_tolerance,
        "dominance_coordinate_equality_tolerance": objective_tolerance.tolist(),
        "numerical_equality_policy": (
            "64*eps64 coordinate scale; no statistical epsilon dominance or clustering"
        ),
        "reference_status": "H20 finest evaluated internal resolution; not a true Pareto reference",
        "final_H_accepted": None,
        "new_PA": False,
        "new_random_draws": 0,
        "anchors_reoptimized": False,
        "RC_applied": False,
        "external_benchmarks": False,
        "parallelism": False,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": {name: version(name) for name in ["numpy", "scipy", "matplotlib"]},
        "input_sha256": {
            p.relative_to(ROOT).as_posix(): sha256_file(p) for p in [*INPUT_HASHES, *code_paths]
        },
        "artifact_sha256": {p.name: sha256_file(p) for p in sorted(output.iterdir())},
        "command": "uv run python -m scripts.validation.turning_local_nbi "
        f"--run-id {run_id} [--output fresh_directory]",
    }
    write_json(output / "metadata.json", metadata)
    (output / "checksums.sha256").write_text(
        "".join(
            f"{sha256_file(p)}  {p.name}\n"
            for p in sorted(output.iterdir())
            if p.name != "checksums.sha256"
        ),
        encoding="utf-8",
        newline="\n",
    )
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=RUN_ID)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    metadata = run_local_nbi(
        args.output or ROOT / "results/phase_06_local_nbi" / args.run_id, run_id=args.run_id
    )
    print(
        json.dumps(
            {
                key: metadata[key]
                for key in [
                    "unique_subproblems",
                    "accepted",
                    "failed",
                    "eq_norm_distribution",
                    "sphere_margin_distribution",
                    "solve_seconds",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
