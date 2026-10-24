"""Consume the pinned Phase 3 ensemble; reoptimize sphere anchors and raw payoffs."""

import argparse
import csv
import hashlib
import json
import platform
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np

from cnbi_v2.data import sha256_file
from cnbi_v2.uncertainty import (
    AnchorEnsemble,
    coefficient_checkpoints,
    reoptimize_coefficient_ensemble,
)

from .turning_anchors import ALPHA, DIRECTIONS
from .turning_reference import RAW, RAW_SHA256, RESPONSES, ROOT, TERMS, write_csv, write_json

PHASE_3 = ROOT / "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024"
ENSEMBLE = PHASE_3 / "coefficient_samples.npz"
METADATA = PHASE_3 / "metadata.json"
ENSEMBLE_SHA = "5df42af4ef36fe6e2ce1948897d12a0d90a4a9f3449b1180898cf6adc9d84674"
METADATA_SHA = "000888b8b35e88e22c4c42a62d8a8033254c78c4896cfa41925858569eaf7bcb"
PHASE_3_SOURCE_COMMIT = "5a102dd337a5c9b7108fac6997b612c7d02a8684"
NOMINAL = ROOT / "results/phase_02_anchors/turning_original_codes_20261024/anchors_sphere.csv"
NOMINAL_SHA = "462b6b18002c2ae784758a26ebe500bf95de3a8ff1c504aab6986924d9d5bafd"
RUN_ID = "turning_original_codes_anchor_mc_777_20261024"
STAT_NAMES = ("mean", "median", "std", "q05", "q25", "q75", "q95", "min", "max")
TABLE_HEADERS = {
    "anchor_summary": ("response", "nominal_x1", "nominal_x2", "nominal_x3",
                       *(f"{s}_delta_x" for s in STAT_NAMES if s != "min"),
                       "fraction_interior", "fraction_boundary"),
    "optimal_value_summary": ("response", "nominal_optimum",
                              *(f"{s}_sampled_optimum" for s in STAT_NAMES),
                              "mean_delta_f", "q05_delta_f", "q95_delta_f"),
    "solver_case_summary": ("response", "interior_count", "boundary_count", "hard_case_count",
                            "other_count", "failure_count"),
    "prefix_anchor_sensitivity": ("B", "response", "mean_displacement", "median_displacement",
                                  "q95_displacement", "fraction_boundary"),
    "prefix_payoff_sensitivity": ("B", "mean_payoff_relative_frobenius_error"),
}


def load_phase3_ensemble(ensemble_path: Path = ENSEMBLE, metadata_path: Path = METADATA):
    """Both files and scientific identity are pinned; never regenerate missing draws."""
    if sha256_file(ensemble_path) != ENSEMBLE_SHA:
        raise ValueError("Phase 3 ensemble SHA-256 mismatch")
    if sha256_file(metadata_path) != METADATA_SHA:
        raise ValueError("Phase 3 metadata SHA-256 mismatch")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected = {
        "git_commit": PHASE_3_SOURCE_COMMIT, "git_working_tree_dirty": False,
        "dataset_sha256": RAW_SHA256, "seed": 777, "B_max": 2000, "p": 10, "m": 8,
        "coefficient_order": list(TERMS), "response_order": list(RESPONSES),
        "factor_order": ["Vc", "f", "ap"], "dtype": "float64", "ensemble_count": 1,
        "checkpoints": list(coefficient_checkpoints()), "sampling_method": "MATRIX_NORMAL_PLUGIN",
        "samples_index_order": "samples[replica,term,response]",
    }
    if any(metadata.get(key) != value for key, value in expected.items()):
        raise ValueError("Phase 3 metadata/source commit/order/configuration mismatch")
    with np.load(ensemble_path, allow_pickle=False) as archive:
        if archive.files != ["samples"]:
            raise ValueError("Phase 3 archive must contain exactly the single samples ensemble")
        samples = archive["samples"]
    if (samples.shape != (2000, 10, 8) or samples.dtype != np.float64
            or not np.isfinite(samples).all()):
        raise ValueError("Phase 3 samples must be finite float64 with shape (2000,10,8)")
    if hashlib.sha256(samples.tobytes(order="C")).hexdigest() != \
            metadata["object_identities"]["samples"]["sha256"]:
        raise ValueError("Phase 3 sample-array byte hash mismatch")
    return np.frombuffer(samples.tobytes(), dtype=np.float64).reshape(samples.shape), metadata


def load_nominal_anchors():
    if sha256_file(NOMINAL) != NOMINAL_SHA:
        raise ValueError("nominal Phase 2 anchor SHA-256 mismatch")
    with NOMINAL.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if ([r["response"] for r in rows] != list(RESPONSES)
            or [r["direction"] for r in rows] != list(DIRECTIONS)):
        raise ValueError("nominal anchor response/direction order mismatch")
    points = np.array([[float(row[f"x{i}"]) for i in range(1, 4)] for row in rows])
    optimum = np.array([float(row["objective"]) for row in rows])
    return points, optimum


def descriptive_stats(values: np.ndarray) -> dict:
    quantiles = np.quantile(values, [.05, .25, .5, .75, .95], method="linear")
    return dict(zip(STAT_NAMES, [float(values.mean()), float(quantiles[2]),
                                float(values.std(ddof=1)), float(quantiles[0]),
                                float(quantiles[1]), float(quantiles[3]), float(quantiles[4]),
                                float(values.min()), float(values.max())], strict=True))


def solver_case_rows(result: AnchorEnsemble) -> list[dict]:
    rows = []
    for j, name in enumerate(result.response_names):
        cases = result.solver_cases[:, j]
        known = np.isin(cases, ["INTERIOR_OR_PSD_MINIMUM_NORM", "BOUNDARY_SECULAR",
                                "BOUNDARY_HARD_CASE"])
        rows.append({
            "response": name,
            "interior_count": int(np.sum(cases == "INTERIOR_OR_PSD_MINIMUM_NORM")),
            "boundary_count": int(np.sum(cases == "BOUNDARY_SECULAR")),
            "hard_case_count": int(np.sum(cases == "BOUNDARY_HARD_CASE")),
            "other_count": int(np.sum(~known & result.valid_anchors[:, j])),
            "failure_count": int(np.sum(~result.valid_anchors[:, j])),
        })
    return rows


def build_summaries(result: AnchorEnsemble, nominal: np.ndarray, nominal_values: np.ndarray):
    """Complete-ensemble descriptive summaries only, never filtered failure averages."""
    if result.failures or not result.valid_anchors.all() or not result.valid_payoffs.all():
        raise ValueError("incomplete ensemble: refusing summaries over silently reduced samples")
    count, m, n = result.anchors.shape
    if ((count, m, n) != (2000, 8, 3) or nominal.shape != (m, n)
            or nominal_values.shape != (m,)):
        raise ValueError("real summaries require B=2000 and matching nominal dimensions")
    if not all(np.isfinite(v).all() for v in
               (result.anchors, result.optimal_values, result.payoffs, nominal, nominal_values)):
        raise ValueError("summary arrays and nominal references must be finite")
    displacement = np.linalg.norm(result.anchors - nominal[None, :, :], axis=2)
    differences = result.optimal_values - nominal_values
    tables = {name: [] for name in TABLE_HEADERS}
    for j, name in enumerate(result.response_names):
        stats = descriptive_stats(displacement[:, j])
        tables["anchor_summary"].append({
            "response": name, **{f"nominal_x{i+1}": float(x) for i, x in enumerate(nominal[j])},
            **{f"{key}_delta_x": value for key, value in stats.items() if key != "min"},
            "fraction_interior": float(np.mean(result.locations[:, j] == "INTERIOR")),
            "fraction_boundary": float(np.mean(result.locations[:, j] == "BOUNDARY")),
        })
        stats = descriptive_stats(result.optimal_values[:, j])
        delta = descriptive_stats(differences[:, j])
        tables["optimal_value_summary"].append({
            "response": name, "nominal_optimum": float(nominal_values[j]),
            **{f"{key}_sampled_optimum": value for key, value in stats.items()},
            "mean_delta_f": delta["mean"], "q05_delta_f": delta["q05"],
            "q95_delta_f": delta["q95"],
        })
    tables["solver_case_summary"] = solver_case_rows(result)
    final_payoff_mean = result.payoffs.mean(axis=0)
    denominator = max(float(np.linalg.norm(final_payoff_mean)), float(np.finfo(float).eps))
    for count in coefficient_checkpoints():
        for j, name in enumerate(result.response_names):
            d = displacement[:count, j]
            tables["prefix_anchor_sensitivity"].append({
                "B": count, "response": name, "mean_displacement": float(d.mean()),
                "median_displacement": float(np.median(d)),
                "q95_displacement": float(np.quantile(d, .95, method="linear")),
                "fraction_boundary": float(np.mean(result.locations[:count, j] == "BOUNDARY")),
            })
        tables["prefix_payoff_sensitivity"].append({
            "B": count, "mean_payoff_relative_frobenius_error": float(np.linalg.norm(
                result.payoffs[:count].mean(axis=0) - final_payoff_mean) / denominator),
        })
    return tables


def run_anchor_mc(output: Path, *, run_id: str) -> dict:
    started = perf_counter()
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                         for c in run_id):
        raise ValueError("run_id must be nonempty alphanumeric/underscore/hyphen")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("nonempty run directory: choose a fresh run_id/output")
    samples, phase3 = load_phase3_ensemble()
    raw_before = sha256_file(RAW)
    raw_time = RAW.stat().st_mtime_ns
    if raw_before != RAW_SHA256:
        raise ValueError("raw dataset does not match the Phase 3 model")
    nominal, nominal_values = load_nominal_anchors()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    compute_start = perf_counter()
    result = reoptimize_coefficient_ensemble(samples, 3, DIRECTIONS, ALPHA,
                                            response_names=RESPONSES)
    compute_seconds = perf_counter() - compute_start
    complete = result.failed == 0 and result.valid_payoffs.all() and not result.failures
    tables = (build_summaries(result, nominal, nominal_values) if complete
              else {name: [] for name in TABLE_HEADERS})
    tables["solver_case_summary"] = solver_case_rows(result)
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output / "anchor_samples.npz", allow_pickle=False,
        anchors=result.anchors, optimal_values=result.optimal_values, norms=result.norms,
        solver_cases=result.solver_cases, locations=result.locations,
        valid_anchors=result.valid_anchors, certificates=result.certificates,
        certificate_fields=np.asarray(result.certificate_fields, dtype="U32"),
        displacements=np.linalg.norm(result.anchors - nominal[None, :, :], axis=2),
        optimal_value_differences=result.optimal_values - nominal_values,
    )
    np.savez_compressed(output / "payoff_samples.npz", allow_pickle=False,
                        payoffs=result.payoffs, valid_payoffs=result.valid_payoffs)
    for name, header in TABLE_HEADERS.items():
        write_csv(output / f"{name}.csv", header,
                  [[row[key] for key in header] for row in tables[name]])
    failure_headers = ("replicate_id", "response", "failure_type", "failure_message")
    write_csv(output / "failure_log.csv", failure_headers,
              [[asdict(f)[key] for key in failure_headers] for f in result.failures])
    if (sha256_file(ENSEMBLE) != ENSEMBLE_SHA or sha256_file(METADATA) != METADATA_SHA
            or sha256_file(RAW) != raw_before
            or RAW.stat().st_mtime_ns != raw_time or sha256_file(NOMINAL) != NOMINAL_SHA):
        raise RuntimeError("immutable Phase 3/raw/nominal inputs changed during propagation")
    input_paths = [ENSEMBLE, METADATA, NOMINAL, RAW, ROOT / "uv.lock", Path(__file__),
                   ROOT / "scripts/validation/turning_anchors.py",
                   ROOT / "scripts/validation/turning_reference.py",
                   ROOT / "docs/policies/history/pa_early_stop_policy_v1.json",
                   *sorted((ROOT / "src/cnbi_v2/model").glob("*.py")),
                   *sorted((ROOT / "src/cnbi_v2/uncertainty").glob("*.py")),
                   *sorted((ROOT / "src/cnbi_v2/optimization").glob("*.py")),
                   *sorted((ROOT / "src/cnbi_v2/data").glob("*.py"))]
    metadata = {
        "run_id": run_id, "executed_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": commit, "git_working_tree_dirty": dirty,
        "phase_3_ensemble_sha256": ENSEMBLE_SHA, "phase_3_metadata_sha256": METADATA_SHA,
        "phase_3_scientific_commit": phase3["git_commit"],
        "phase_3_identity_verification": "pinned ensemble and metadata SHA; source commit, "
                                         "orders, counts, dtype, finite values and sample byte SHA",
        "dataset_sha256": RAW_SHA256, "nominal_anchor_sha256": NOMINAL_SHA,
        "seed_original": phase3["seed"], "rng_in_phase_4": "NONE_FROZEN_PHASE_3_INPUT",
        "B_max": len(samples), "checkpoints": list(coefficient_checkpoints()),
        "alpha": ALPHA, "coefficient_order": TERMS, "response_order": RESPONSES,
        "directions": dict(zip(RESPONSES, DIRECTIONS, strict=True)), "dtype": "float64",
        "anchor_shape": list(result.anchors.shape), "payoff_shape": list(result.payoffs.shape),
        "solver": "existing solve_quadratic_ball, spectral global TRS; unchanged",
        "solver_tolerances": {"certificate": 1e-10, "spectral": "eps64*16*n_x",
                              "brent_xtol": float(np.finfo(float).tiny),
                              "brent_rtol": float(8*np.finfo(float).eps), "brent_maxiter": 256},
        "radial_location_tolerance": "alpha * existing certificate_tolerance",
        "certificate_fields": result.certificate_fields,
        "attempted": result.attempted, "successful": result.successful, "failed": result.failed,
        "payoff_successful": int(result.valid_payoffs.sum()),
        "payoff_failed": int((~result.valid_payoffs).sum()),
        "failure_log_rows": len(result.failures),
        "status": "SUCCESS" if complete else "INCOMPLETE_FAILURE_NO_DISTRIBUTION_SUMMARIES",
        "diagonal_identity": bool(complete and np.array_equal(
            np.diagonal(result.payoffs, axis1=1, axis2=2), result.optimal_values)),
        "quantile_method": "linear", "standard_deviation_ddof": 1,
        "solver_boundary_count_definition": "BOUNDARY_SECULAR only; hard cases counted separately",
        "compute_seconds": compute_seconds, "elapsed_total_seconds": perf_counter() - started,
        "mean_seconds_per_optimization": compute_seconds / result.attempted,
        "mean_seconds_per_replica": compute_seconds / len(samples),
        "timing_scope": "serial compute includes extraction, all solves, certificates and payoffs; "
                        "total includes loading, summaries and payload writes before metadata",
        "early_stop_applied": False, "early_stop_policy_status": "PROPOSED",
        "early_stop_status": "NOT_APPLIED_PHASE_4", "RC_applied": False,
        "nominal_anchors_used_as_substitutes": False, "payoffs_normalized": False,
        "new_random_draws": 0, "shrinkage_applied": False,
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: version(name) for name in ["numpy", "scipy"]},
        "input_sha256": {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in input_paths},
        "artifact_sha256": {p.name: sha256_file(p) for p in sorted(output.iterdir())},
        "command": "uv run python -m scripts.validation.turning_anchor_mc "
                   f"--run-id {run_id} [--output fresh_directory]",
    }
    write_json(output / "metadata.json", metadata)
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.name}\n" for p in sorted(output.iterdir())
                if p.is_file() and p.name != "checksums.sha256"), encoding="utf-8", newline="\n")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=RUN_ID)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    metadata = run_anchor_mc(args.output or ROOT / "results/phase_04_anchor_mc" / args.run_id,
                             run_id=args.run_id)
    print(json.dumps({key: metadata[key] for key in ["status", "attempted", "successful", "failed",
                                                   "compute_seconds", "elapsed_total_seconds"]},
                     indent=2))
    if metadata["status"] != "SUCCESS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
