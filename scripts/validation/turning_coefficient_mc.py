"""Archive one original-coded, joint coefficient ensemble; no anchor optimization.

uv run python -m scripts.validation.turning_coefficient_mc --run-id <id>
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
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from cnbi_v2.data import sha256_file
from cnbi_v2.model import coefficient_covariance, fit_multivariate_rsm
from cnbi_v2.uncertainty import mc_prefix_sensitivity, sample_coefficient_ensemble

from .turning_anchors import CODES, CODING_METADATA, load_original_coded_case
from .turning_reference import RAW, RAW_SHA256, RESPONSES, ROOT, TERMS, write_csv, write_json

PHASE_2_RUN = "turning_original_codes_20261024"
PHASE_2_MODELS = ROOT / "results/phase_02_anchors" / PHASE_2_RUN / "coded_models.csv"
POLICY = ROOT / "docs/policies/history/pa_early_stop_policy_v1.json"
RUN_ID = "turning_original_codes_mc_777_20261024"
B_MAX = 2000


def array_identity(array: np.ndarray) -> dict:
    """Hash C-contiguous float64 bytes with dtype/shape recorded separately."""
    return {"sha256": hashlib.sha256(array.tobytes(order="C")).hexdigest(),
            "dtype": str(array.dtype), "shape": list(array.shape), "memory_order": "C",
            "machine_byte_order": "little" if np.little_endian else "big"}


def plot_moments(path: Path, records) -> None:
    figure = Figure(figsize=(10, 4), layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.subplots(1, 2)
    b = [row.B for row in records]
    axes[0].plot(b, [row.mean_relative_frobenius_error for row in records], "o-")
    axes[1].plot(b, [row.covariance_relative_frobenius_error for row in records], "o-")
    for axis, title in zip(axes, ["Mean error", "Full covariance error"], strict=True):
        axis.set(xlabel="Prefix B (one ensemble)", ylabel="Relative Frobenius error", title=title)
        axis.grid(alpha=.25)
    figure.suptitle("Plug-in coefficient Monte Carlo: sampler diagnostics only")
    figure.savefig(path, dpi=150, metadata={"Software": "C-NBI-v2 Phase 3"})


def run_coefficient_mc(output: Path, *, run_id: str, seed: int = 777) -> dict:
    """Fit once through the existing fitter and generate exactly 2,000 replicas."""
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                         for c in run_id):
        raise ValueError("run_id must be a nonempty explicit alphanumeric/underscore/hyphen ID")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("run output already exists; choose a new run_id/output directory")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    raw_before = sha256_file(RAW)
    raw_mtime = RAW.stat().st_mtime_ns
    values, factors, coding = load_original_coded_case()
    fit = fit_multivariate_rsm(factors, values[:, 4:])
    previous = np.loadtxt(PHASE_2_MODELS, delimiter=",", skiprows=1, usecols=range(1, 9))
    # Platform BLAS may differ in last bits: this gate identifies the same fit,
    # not an assertion of cross-platform bitwise floating-point equality.
    if not np.allclose(previous, fit.coefficients, rtol=1e-12, atol=1e-13):
        raise ValueError("canonical coefficients do not reproduce the archived Phase 2 model")
    ensemble = sample_coefficient_ensemble(
        fit.coefficients, fit.design_r_factor, fit.residual_covariance, B_MAX,
        seed=seed, batch_size=100, response_names=RESPONSES, term_names=TERMS,
    )
    if not np.allclose(ensemble.design_covariance, fit.xtx_covariance_factor,
                       rtol=1e-12, atol=1e-14):
        raise ValueError("C_X C_X.T does not match the same-fit V_X")
    effective = ensemble.effective_residual_covariance
    if not np.allclose(ensemble.residual_covariance_factor
                       @ ensemble.residual_covariance_factor.T, effective,
                       rtol=1e-12, atol=1e-14):
        raise ValueError("residual root does not reconstruct its reported covariance")
    theoretical = coefficient_covariance(fit)  # Independent existing analytic implementation.
    records = mc_prefix_sensitivity(ensemble, theoretical_covariance=theoretical)
    vectors = ensemble.samples.transpose(0, 2, 1).reshape(B_MAX, 80)
    centered = vectors - vectors.mean(axis=0)
    empirical = centered.T @ centered / (B_MAX - 1)
    summary = {
        "B": B_MAX, "shape": list(ensemble.samples.shape), "seed": seed,
        "mean": ensemble.samples.mean(axis=0).tolist(),
        "final_diagnostics": asdict(records[-1]),
        "empirical_covariance_file": "empirical_covariance_B2000.npy",
        "empirical_covariance_definition": "unbiased column-vec covariance, divisor B-1",
        "early_stop_status": "NOT_APPLIED_PHASE_3",
        "interpretation": "Finite-seed moment diagnostics, not a PA stopping criterion; "
                          "errors need not decrease at every checkpoint.",
    }
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output / "coefficient_samples.npz", samples=ensemble.samples)
    np.save(output / "theoretical_covariance.npy", theoretical, allow_pickle=False)
    np.save(output / "empirical_covariance_B2000.npy", empirical, allow_pickle=False)
    write_csv(output / "mc_prefix_sensitivity.csv", [
        "B", "mean_relative_frobenius_error", "covariance_relative_frobenius_error"],
        [[row.B, row.mean_relative_frobenius_error, row.covariance_relative_frobenius_error]
         for row in records])
    write_json(output / "empirical_summary_B2000.json", summary)
    plot_moments(output / "mc_convergence.png", records)
    input_paths = [RAW, CODES, CODING_METADATA, PHASE_2_MODELS, POLICY, ROOT / "uv.lock",
                   Path(__file__), ROOT / "scripts/validation/turning_anchors.py",
                   ROOT / "scripts/validation/turning_reference.py",
                   *sorted((ROOT / "src/cnbi_v2/model").glob("*.py")),
                   *sorted((ROOT / "src/cnbi_v2/uncertainty").glob("*.py")),
                   *sorted((ROOT / "src/cnbi_v2/data").glob("*.py"))]
    if sha256_file(RAW) != raw_before or raw_before != RAW_SHA256 \
            or RAW.stat().st_mtime_ns != raw_mtime:
        raise RuntimeError("raw changed during coefficient sampling")
    write_json(output / "metadata.json", {
        "run_id": run_id, "executed_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": commit, "git_working_tree_dirty": dirty,
        "git_branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "dataset_sha256": RAW_SHA256,
        "model_identifier": f"{PHASE_2_RUN}/original_spreadsheet_codes_1_682",
        "phase_2_coefficient_file_sha256": sha256_file(PHASE_2_MODELS),
        "phase_2_coefficient_match": "ALLCLOSE_rtol_1e-12_atol_1e-13",
        "coding": coding["coding_id"], "factor_order": coding["coded_factor_order"],
        "n_observations": fit.n_observations, "p": fit.n_terms, "m": fit.n_responses,
        "residual_degrees_of_freedom": fit.residual_degrees_of_freedom,
        "coefficient_order": TERMS, "design_term_order": fit.term_names,
        "response_order": RESPONSES, "sampling_method": ensemble.sampling_method,
        "sampling_formula": "B_hat + C_X @ G @ L_Sigma.T",
        "covariance_estimator": "raw E.T @ E / nu, no shrinkage",
        "theoretical_covariance": "Sigma_hat_e tensor V_X; column-stacked vec",
        "seed": seed, "rng": ensemble.rng, "B_max": B_MAX, "batch_size": 100,
        "checkpoints": [row.B for row in records], "ensemble_count": 1,
        "samples_index_order": "samples[replica,term,response]",
        "normal_order": "flat float64 standard_normal -> C reshape(B,p,m); response fastest",
        "normal_count": B_MAX * fit.n_terms * fit.n_responses, "dtype": "float64",
        "mode": "validation/sensitivity", "mean_norm_floor": float(np.finfo(float).eps),
        "factorization_method": {"design": "solve_triangular(R,I), upper reduced QR",
                                 "residual": ensemble.residual_factorization_method},
        "psd_eigenvalue_tolerance": ensemble.psd_eigenvalue_tolerance,
        "zeroed_negative_eigenvalues": ensemble.zeroed_negative_eigenvalues,
        "design_reconstruction_max_abs": float(np.max(np.abs(
            ensemble.design_covariance - fit.xtx_covariance_factor))),
        "residual_reconstruction_max_abs": float(np.max(np.abs(
            ensemble.residual_covariance_factor @ ensemble.residual_covariance_factor.T
            - fit.residual_covariance))),
        "object_identities": {name: array_identity(array) for name, array in {
            "B_hat": fit.coefficients, "V_X": fit.xtx_covariance_factor,
            "Sigma_hat_e": fit.residual_covariance, "R": fit.design_r_factor,
            "C_X": ensemble.design_covariance_factor,
            "L_Sigma": ensemble.residual_covariance_factor,
            "Sigma_effective": effective, "samples": ensemble.samples,
        }.items()},
        "early_stop_policy": json.loads(POLICY.read_text(encoding="utf-8")),
        "early_stop_minimum_B": 500, "early_stop_quantile_tolerance": .01,
        "early_stop_applied": False, "early_stop_status": "NOT_APPLIED_PHASE_3",
        "anchors_reoptimized": False, "per_replica_payoff_computed": False,
        "observed_responses_modified": False, "raw_unchanged": True,
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: version(name) for name in ["numpy", "scipy", "matplotlib", "openpyxl"]},
        "input_sha256": {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in input_paths},
        "artifact_sha256": {p.name: sha256_file(p) for p in sorted(output.iterdir())},
        "command": "uv run python -m scripts.validation.turning_coefficient_mc "
                   f"--run-id {run_id} --seed {seed}",
        "output_directory": "explicit --output if supplied; otherwise "
                            "results/phase_03_coefficient_mc/run_id",
    })
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.name}\n" for p in sorted(output.iterdir())
                if p.is_file() and p.name != "checksums.sha256"),
        encoding="utf-8", newline="\n",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=RUN_ID)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seed", type=int, default=777)
    args = parser.parse_args()
    output = args.output or ROOT / "results/phase_03_coefficient_mc" / args.run_id
    summary = run_coefficient_mc(output, run_id=args.run_id, seed=args.seed)
    print(json.dumps(summary["final_diagnostics"], indent=2))


if __name__ == "__main__":
    main()
