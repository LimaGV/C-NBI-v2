"""Original-coded turning anchors: sphere vs experimental 8-D response cloud.

This is an explicitly distinct coded-input case, not an equivalent coordinate
change of the previously fitted physical RSM. No continuous inverse is asserted.
"""

import argparse
import hashlib
import json
import platform
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import numpy as np
import openpyxl

from cnbi_v2.data import sha256_file
from cnbi_v2.model import fit_multivariate_rsm
from cnbi_v2.optimization import (
    Direction,
    RCOptions,
    classify_response_distance,
    deterministic_ball_starts,
    evaluate_responses,
    legacy_chi_square_threshold,
    payoff_matrix,
    quadratic_responses,
    response_cloud_region,
    solve_quadratic_ball,
    solve_response_region_anchor,
)

from .turning_reference import (
    RAW,
    RAW_SHA256,
    RESPONSES,
    ROOT,
    TERMS,
    read_literal_values,
    write_csv,
    write_json,
)

CODES = ROOT / "data/processed/turning_application/original_coded_factors.csv"
CODING_METADATA = ROOT / "data/metadata/turning_application/phase_02_coding.json"
SOURCE_HASH = "7792a25a8c88d29206665d8797587dc6a11e932e1a8bba0a1ac8b539385f7d4e"
DIRECTIONS = (Direction.MAX, Direction.MAX, Direction.MIN, Direction.MIN,
              Direction.MIN, Direction.MIN, Direction.MAX, Direction.MAX)
ALPHA = 8**0.25


def extract_original_coding(source: Path) -> None:
    """Read literal IDs/coded/physical columns only; never save/recalculate source."""
    before, mtime = sha256_file(source), source.stat().st_mtime_ns
    if before != SOURCE_HASH:
        raise ValueError("original coding source hash differs; review revision explicitly")
    workbook = openpyxl.load_workbook(source, read_only=True, data_only=False, keep_links=False)
    try:
        rows = list(workbook["Original Data"].iter_rows(min_row=4, max_row=22,
                                                     min_col=2, max_col=8))
        if any(cell.data_type != "n" for row in rows for cell in row):
            raise ValueError("original factor coordinates must be numeric literals, not caches")
        coordinates = np.array([[cell.value for cell in row] for row in rows], dtype=float)
    finally:
        workbook.close()
    values, _ = read_literal_values()
    if (not np.isfinite(coordinates).all()
            or not np.array_equal(coordinates[:, 0], values[:, 0])
            or not np.array_equal(coordinates[:, 4:], values[:, 1:4])):
        raise ValueError("original factor coordinates/IDs do not match the canonical CCD")
    physical = fit_multivariate_rsm(values[:, 1:4], values[:, 4:])
    coded = fit_multivariate_rsm(coordinates[:, 1:4], values[:, 4:])
    differences = np.max(np.abs(physical.fitted_values - coded.fitted_values), axis=0)
    relative = differences / np.ptp(values[:, 4:], axis=0)
    write_csv(CODES, ["Exp", "x1", "x2", "x3", "Vc", "f", "ap"], coordinates.tolist())
    if sha256_file(source) != before or source.stat().st_mtime_ns != mtime:
        raise RuntimeError("read-only original coding inspection altered the source")
    write_json(CODING_METADATA, {
        "coding_id": "original_spreadsheet_codes_1_682",
        "status": "VERIFIED_ORIGINAL_CODES_DISTINCT_FROM_PHYSICAL_MODEL",
        "source_file_name": source.name, "source_sha256": before,
        "source_sheet": "Original Data", "source_range": "B4:H22",
        "run_id_range": "B4:B22", "coded_range": "C4:E22", "physical_range": "F4:H22",
        "source_read_only": True, "source_unchanged": True, "source_cells": "numeric literals",
        "canonical_dataset_sha256": RAW_SHA256,
        "extracted_csv_sha256": sha256_file(CODES), "n_runs": 19,
        "coded_factor_order": ["Vc", "f", "ap"], "source_axial_code": 1.682,
        "sphere_radius": ALPHA, "sphere_definition": "x.T x <= (8**0.25)**2",
        "continuous_physical_coded_transform": None,
        "physical_coordinates_for_new_anchors": "UNDEFINED_NO_VERIFIED_TRANSFORM",
        "physical_coded_fitted_equivalence_gate": "FAILED",
        "maximum_fitted_difference_by_response": dict(
            zip(RESPONSES, differences.tolist(), strict=True)),
        "maximum_fitted_difference_over_response_range": dict(
            zip(RESPONSES, relative.tolist(), strict=True)),
        "owner_clarification": "a planilha esta correta o artigo esta errado",
        "interpretation": "Prioritize original spreadsheet codes as a distinct coded-input case; "
                          "no claim of equivalent physical reparameterization.",
        "changes_to_observed_responses": "NONE", "factorial_corners_outside_requested_ball": 8,
    })


def load_original_coded_case():
    metadata = json.loads(CODING_METADATA.read_text(encoding="utf-8"))
    if sha256_file(CODES) != metadata["extracted_csv_sha256"]:
        raise ValueError("original coding extract hash mismatch")
    coordinates = np.loadtxt(CODES, delimiter=",", skiprows=1)
    values, _ = read_literal_values()
    if (coordinates.shape != (19, 7) or not np.array_equal(coordinates[:, 0], values[:, 0])
            or not np.array_equal(coordinates[:, 4:], values[:, 1:4])):
        raise ValueError("coded/physical experiment join failed")
    return values, coordinates[:, 1:4], metadata


def serializable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serializable(item) for item in value]
    return value


def run_anchors(output: Path, *, run_id: str, sensitivity: bool = True) -> dict:
    """Record all starts/solutions and keep both payoff matrices independent."""
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                         for c in run_id):
        raise ValueError("run_id must be a nonempty explicit alphanumeric/underscore/hyphen ID")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("run output already exists; choose a new run_id/output directory")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    values, factors, coding = load_original_coded_case()
    fit = fit_multivariate_rsm(factors, values[:, 4:])
    models = quadratic_responses(fit)
    region = response_cloud_region(values[:, 4:])
    threshold = legacy_chi_square_threshold(8, .95)
    distances = region.distances_squared(values[:, 4:])
    sphere = [solve_quadratic_ball(model, ALPHA, direction)
              for model, direction in zip(models, DIRECTIONS, strict=True)]
    proposals = np.vstack([deterministic_ball_starts(3, ALPHA), factors,
                           np.array([anchor.point for anchor in sphere])])
    options = RCOptions()
    rc = [solve_response_region_anchor(models, j, direction, ALPHA, region, threshold,
                                       proposals, options=options)
          for j, direction in enumerate(DIRECTIONS)]
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "coded_models.csv", ["coefficient", *RESPONSES],
              [[term, *row] for term, row in zip(TERMS, fit.coefficients, strict=True)])
    write_csv(output / "coded_factors.csv", ["Exp", "x1", "x2", "x3"],
              [[int(run), *point] for run, point in zip(values[:, 0], factors, strict=True)])
    write_csv(output / "experimental_mahalanobis.csv", ["Exp", "D2", "threshold", "inside"],
              [[int(run), distance, threshold, bool(distance <= threshold)]
               for run, distance in zip(values[:, 0], distances, strict=True)])
    write_json(output / "response_region.json", {
        "center_definition": "arithmetic mean of observed canonical responses",
        "covariance_definition": "centered_Y.T @ centered_Y / (n-1)",
        "response_order": RESPONSES, "center": region.center.tolist(),
        "covariance": region.covariance.tolist(), "eigenvalues": region.eigenvalues.tolist(),
        "rank": region.rank, "condition_number": region.condition_number,
        "log_determinant": region.log_determinant,
        "rank_relative_tolerance": region.rank_relative_tolerance,
        "cutoff_name": "legacy_chi_square_threshold", "threshold": threshold,
        "nominal_coverage": .95, "statistical_status": "EXPERIMENTAL_NOT_EXACT_CONFIDENCE",
        "n": 19, "m": 8, "empirical_distance_quantiles": {
            str(q): float(np.quantile(distances, q, method="linear"))
            for q in [0, .25, .5, .75, .9, .95, 1]},
        "empirical_quantile_method": "linear",
        "experimental_inside": int(np.count_nonzero(distances <= threshold)),
        "experimental_outside": int(np.count_nonzero(distances > threshold)),
        "distance_sum": float(distances.sum()), "theoretical_in_sample_sum": 8 * 18,
    })
    cutoff_candidates = [
        ("legacy_chi_square_0_95", threshold, "EXPERIMENTAL"),
        ("empirical_MD2_quantile_0_95", float(np.quantile(distances, .95, method="linear")),
         "DIAGNOSTIC_NOT_CONFIDENCE"),
        ("legacy_chi_square_0_99", legacy_chi_square_threshold(8, .99), "EXPERIMENTAL"),
    ]
    write_csv(output / "cutoff_coverage.csv", [
        "candidate", "threshold", "status", "n_inside", "n_outside", "minimum", "median", "maximum",
    ], [[label, cutoff, status, int(np.count_nonzero(distances <= cutoff)),
         int(np.count_nonzero(distances > cutoff)), float(np.min(distances)),
         float(np.median(distances)), float(np.max(distances))]
        for label, cutoff, status in cutoff_candidates])
    write_csv(output / "anchors_sphere.csv", [
        "response", "direction", "x1", "x2", "x3", "physical_Vc", "physical_f", "physical_ap",
        "objective", "norm", "sphere_margin", "D2", "RC_classification", "boundary_active",
        "solution_case", "converged", "KKT_stationarity", "KKT_complementarity", "PSD_min",
    ], [
        [name, direction, *a.point, None, None, None, a.objective, a.norm, a.sphere_margin,
         region.distance_squared(evaluate_responses(models, a.point)),
         classify_response_distance(region.distance_squared(evaluate_responses(models, a.point)),
                                    threshold, options.response_tolerance),
         a.boundary_active, a.solution_case, a.converged, a.normalized_stationarity,
         a.normalized_complementarity, a.normalized_shifted_min_eigenvalue]
        for name, direction, a in zip(RESPONSES, DIRECTIONS, sphere, strict=True)
    ])
    write_csv(output / "anchors_response_region.csv", [
        "response", "direction", "x1", "x2", "x3", "physical_Vc", "physical_f", "physical_ap",
        "objective", "norm", "sphere_margin", "D2", "response_margin", "sphere_boundary_active",
        "response_boundary_active", "global_certified", "solver",
        "feasible_starts", "accepted_trials",
    ], [
        [name, direction, *a.point, None, None, None, a.objective, a.norm, a.sphere_margin,
         a.distance_squared, a.response_margin, a.sphere_boundary_active,
         a.response_boundary_active, a.global_optimum_certified, a.solver,
         len(a.feasible_starts), sum(t.accepted for t in a.trials)]
        for name, direction, a in zip(RESPONSES, DIRECTIONS, rc, strict=True)
    ])
    comparison = []
    for name, direction, a, b in zip(RESPONSES, DIRECTIONS, sphere, rc, strict=True):
        old_distance = region.distance_squared(evaluate_responses(models, a.point))
        deterioration = direction.minimization_sign * (b.objective - a.objective)
        relative = deterioration / abs(a.objective) if a.objective != 0 else None
        comparison.append([
            name, direction, a.objective, b.objective, b.objective - a.objective,
            (b.objective - a.objective) / abs(a.objective) if a.objective != 0 else None,
            deterioration, relative, old_distance, b.distance_squared, threshold,
            old_distance <= threshold + options.response_tolerance,
            b.response_margin >= -options.response_tolerance, a.norm, b.norm,
            float(np.linalg.norm(a.point - b.point)), a.boundary_active,
            b.sphere_boundary_active, b.response_boundary_active,
        ])
    write_csv(output / "anchor_comparison.csv", [
        "response", "direction", "sphere_objective", "rc_objective", "objective_change",
        "relative_objective_change", "objective_deterioration", "relative_deterioration",
        "sphere_D2", "rc_D2", "threshold", "sphere_inside_RC", "rc_inside_RC",
        "sphere_norm", "rc_norm", "distance_x", "sphere_boundary_active",
        "rc_sphere_boundary_active", "rc_response_boundary_active",
    ], comparison)
    for label, anchors in [("sphere", sphere), ("response_region", rc)]:
        payoff = payoff_matrix(models, np.array([a.point for a in anchors]))
        write_csv(output / f"payoff_{label}.csv", ["response", *RESPONSES],
                  [[name, *row] for name, row in zip(RESPONSES, payoff, strict=True)])
    utopia_sphere = np.array([a.objective for a in sphere])
    utopia_rc = np.array([a.objective for a in rc])
    write_json(output / "utopia_diagnostic.json", {
        "response_order": RESPONSES, "definition": "diagonal of the corresponding payoff",
        "sphere": utopia_sphere.tolist(), "response_region": utopia_rc.tolist(),
        "sphere_D2": region.distance_squared(utopia_sphere),
        "response_region_D2": region.distance_squared(utopia_rc), "threshold": threshold,
        "anchor_membership_does_not_imply_diagonal_membership": True,
        "interpretation": "A vector assembled from different individual optima need not "
                          "belong to the response region; no joint attainability claim.",
    })
    write_json(output / "solver_diagnostics.json", serializable({
        "proposed_starts": proposals, "sphere": [asdict(a) for a in sphere],
        "response_region": [asdict(a) for a in rc],
    }))
    sensitivity_rows = []
    if sensitivity:
        for label, cutoff, _ in cutoff_candidates[1:]:
            for j, (name, direction, original) in enumerate(
                    zip(RESPONSES, DIRECTIONS, sphere, strict=True)):
                a = solve_response_region_anchor(models, j, direction, ALPHA, region, cutoff,
                                                  proposals, options=options)
                loss = direction.minimization_sign * (a.objective - original.objective)
                relative_loss = loss / abs(original.objective) if original.objective else None
                sensitivity_rows.append([label, cutoff, name, *a.point, a.objective,
                                         a.distance_squared, loss,
                                         relative_loss,
                                         float(np.linalg.norm(a.point - original.point)),
                                         len(a.trials), a.global_optimum_certified])
                write_json(output / f"solver_trials_{label}_{name}.json",
                           serializable(asdict(a)))
    write_csv(output / "cutoff_sensitivity.csv", [
        "cutoff_candidate", "threshold", "response", "x1", "x2", "x3", "objective", "D2",
        "deterioration", "relative_deterioration", "displacement", "trials", "global_certified",
    ], sensitivity_rows)
    displacements = np.array([row[15] for row in comparison])
    relative_losses = [row[7] for row in comparison if row[7] is not None]
    summary = {
        "classical_outside": sum(not row[11] for row in comparison),
        "classical_outside_responses": [row[0] for row in comparison if not row[11]],
        "number_moved": int(np.count_nonzero(displacements > 1e-6)),
        "median_displacement": float(np.median(displacements)),
        "maximum_displacement": float(np.max(displacements)),
        "median_relative_deterioration": float(np.median(relative_losses)),
        "maximum_relative_deterioration": float(np.max(relative_losses)),
        "utopia_sphere_D2": region.distance_squared(utopia_sphere),
        "utopia_response_region_D2": region.distance_squared(utopia_rc),
        "utopia_inside_response_region": region.distance_squared(utopia_rc) <= threshold,
        "unaffected_responses": [row[0] for row in comparison if row[15] <= 1e-6],
        "moved_definition": "Euclidean coded displacement >1e-6 (reporting only)",
        "recommendation_status": "EXPERIMENTAL_ABLATION_REQUIRES_CUTOFF_AND_MODEL_REVIEW",
    }
    write_json(output / "summary.json", summary)
    input_paths = [RAW, CODES, CODING_METADATA, ROOT / "uv.lock", Path(__file__),
                   ROOT / "scripts/validation/turning_reference.py",
                   *sorted((ROOT / "src/cnbi_v2/model").glob("*.py")),
                   *sorted((ROOT / "src/cnbi_v2/optimization").glob("*.py"))]
    write_json(output / "metadata.json", {
        "run_id": run_id, "executed_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": commit, "git_working_tree_dirty": dirty,
        "git_branch": "feature/02-individual-anchors-response-region",
        "dataset_sha256": RAW_SHA256, "alpha": ALPHA, "source_axial_code": 1.682,
        "coding": coding, "directions": dict(zip(RESPONSES, DIRECTIONS, strict=True)),
        "center_definition": "mean of observed Y",
        "covariance_definition": "centered_Y.T @ centered_Y / (n-1)",
        "cutoff": threshold, "cutoff_status": "LEGACY_EXPERIMENTAL", "nominal_coverage": .95,
        "sphere_solver": "spectral secular equation plus hard-case global certificate",
        "rc_solver": "SLSQP deterministic feasible multistart with analytic gradients",
        "rc_options": asdict(options), "proposed_starts_file": "solver_diagnostics.json",
        "coefficient_bytes_sha256": hashlib.sha256(fit.coefficients.tobytes()).hexdigest(),
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: version(name) for name in ["numpy", "scipy", "openpyxl"]},
        "input_sha256": {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in input_paths},
        "raw_after_sha256": sha256_file(RAW), "observed_responses_modified": False,
        "command": f"uv run python -m scripts.validation.turning_anchors --run-id {run_id}",
        "sensitivity_executed": sensitivity,
    })
    if sha256_file(RAW) != RAW_SHA256:
        raise RuntimeError("raw changed during anchor computation")
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.name}\n" for p in sorted(output.iterdir())
                if p.is_file() and p.name != "checksums.sha256"),
        encoding="utf-8", newline="\n",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract-coding-source", type=Path)
    parser.add_argument("--run-id", default="turning_original_codes_20261024")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-sensitivity", action="store_true")
    args = parser.parse_args()
    if args.extract_coding_source:
        extract_original_coding(args.extract_coding_source)
    else:
        output = args.output or ROOT / "results/phase_02_anchors" / args.run_id
        print(json.dumps(run_anchors(output, run_id=args.run_id,
                                      sensitivity=not args.no_sensitivity), indent=2))


if __name__ == "__main__":
    main()
