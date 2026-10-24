"""Fixed-normalization centered CHIM screening of the frozen Phase 4 payoffs."""

import argparse
import csv
import json
import platform
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np

from cnbi_v2.chim import (
    centered_chim,
    centering_matrix,
    compute_chim_spectra,
    evaluate_early_stop,
    evaluate_pa_prefixes,
    nominal_normalization,
    policy_from_mapping,
    vertex_differences,
)
from cnbi_v2.data import sha256_file
from cnbi_v2.optimization import Direction

from .turning_reference import RAW, RAW_SHA256, RESPONSES, ROOT, TERMS, write_csv, write_json

PHASE2 = ROOT / "results/phase_02_anchors/turning_original_codes_20261024"
PHASE4 = ROOT / "results/phase_04_anchor_mc/turning_original_codes_anchor_mc_777_20261024"
NOMINAL = PHASE2 / "payoff_sphere.csv"
PAYOFFS = PHASE4 / "payoff_samples.npz"
ANCHORS = PHASE4 / "anchor_samples.npz"
METADATA = PHASE4 / "metadata.json"
CERTIFICATES = PHASE2 / "solver_diagnostics.json"
POLICY = ROOT / "docs/policies/pa_early_stop_policy.json"
INPUT_HASHES = {
    NOMINAL: "2e410a2d3e222047442d75d526166c6af5e5d6787c2c93dcbe2b184003e124c2",
    PAYOFFS: "98a12097a25cf2178e8ffce79499ad627cfb8345fd00a31b3b1521d88c6407d1",
    ANCHORS: "0ece76217c22fb9c8a606b50aa8e8a787f9a7828083bc1f7e3bd5c74c5e28dba",
    METADATA: "6c5a81c75e2ca759f1daa54235b270f30527ed21fafe0d932c3e9bfc7b13250d",
    CERTIFICATES: "80dbd5880b92eb158c35dfdf6a363a1dfc37291523274aedae1f3645b4924fd7",
    POLICY: "e738a49b7df5aca0beaca8ed7a4229dbbfeed2aecd5160de0a4414eda73b43db",
    RAW: RAW_SHA256,
}
DIRECTIONS = (Direction.MAX, Direction.MAX, Direction.MIN, Direction.MIN,
              Direction.MIN, Direction.MIN, Direction.MAX, Direction.MAX)
RUN_ID = "turning_fixed_nominal_chim_pa_777_20261024"


def load_canonical_inputs():
    for path, digest in INPUT_HASHES.items():
        if sha256_file(path) != digest:
            raise ValueError(f"canonical input SHA-256 mismatch: {path.name}")
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    expected = {
        "git_commit": "ac9eb72af9f91de2b860df4b17ba8ab417e94e07",
        "git_working_tree_dirty": False, "response_order": list(RESPONSES),
        "coefficient_order": list(TERMS),
        "directions": dict(zip(RESPONSES, DIRECTIONS, strict=True)),
        "seed_original": 777, "B_max": 2000, "payoff_shape": [2000, 8, 8], "dtype": "float64",
        "diagonal_identity": True, "failed": 0, "payoff_failed": 0, "payoff_successful": 2000,
        "dataset_sha256": RAW_SHA256, "new_random_draws": 0, "RC_applied": False,
        "payoffs_normalized": False,
    }
    if any(metadata.get(key) != value for key, value in expected.items()):
        raise ValueError("Phase 4 metadata identity/order/diagonal/success contract mismatch")
    with NOMINAL.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream)
        if next(reader) != ["response", *RESPONSES]:
            raise ValueError("nominal sphere payoff anchor order mismatch")
        rows = list(reader)
    if [row[0] for row in rows] != list(RESPONSES):
        raise ValueError("nominal sphere payoff response order mismatch")
    nominal = np.asarray([row[1:] for row in rows], dtype=np.float64)
    if nominal.shape != (8, 8) or not np.isfinite(nominal).all():
        raise ValueError("nominal payoff must be finite 8x8")
    with np.load(PAYOFFS, allow_pickle=False) as stored:
        if (set(stored.files) != {"payoffs", "valid_payoffs"}
                or stored["valid_payoffs"].shape != (2000,)
                or stored["valid_payoffs"].dtype != np.bool_ or not stored["valid_payoffs"].all()):
            raise ValueError("incomplete or unexpected Phase 4 payoff arrays")
        samples = stored["payoffs"]
    with np.load(ANCHORS, allow_pickle=False) as stored:
        optimum = stored["optimal_values"]
        if (stored["valid_anchors"].shape != (2000, 8)
                or stored["valid_anchors"].dtype != np.bool_ or not stored["valid_anchors"].all()):
            raise ValueError("Phase 4 anchor validity mask is incomplete")
    if (samples.shape != (2000, 8, 8) or samples.dtype != np.float64
            or not np.isfinite(samples).all() or optimum.shape != (2000, 8)
            or not np.array_equal(np.diagonal(samples, axis1=1, axis2=2), optimum)):
        raise ValueError("Phase 4 payoff shape/dtype/finite/diagonal identity mismatch")
    certificates = json.loads(CERTIFICATES.read_text(encoding="utf-8"))["sphere"]
    if (len(certificates) != 8 or [a["direction"] for a in certificates] != list(DIRECTIONS)
            or any(not a["converged"] or a["certificate_tolerance"] != 1e-10
                   for a in certificates)
            or not np.array_equal(np.diag(nominal), [a["objective"] for a in certificates])):
        raise ValueError("nominal payoff diagonal/certificate order mismatch")
    scale = np.asarray([a["objective_scale"] for a in certificates])
    # Four normalized certificate units cover stationarity/PSD/complementarity
    # roundoff on the unit ball; the second term covers represented row values.
    tolerance = 4*scale*1e-10 + np.finfo(float).eps*16*8*np.max(np.abs(nominal), axis=1)
    policy_data = json.loads(POLICY.read_text(encoding="utf-8"))
    return nominal, samples, tolerance, metadata, policy_data


def component_rows(spectrum, decision):
    return [[r+1, observed, q95, margin, bool(passed)] for r, (observed, q95, margin, passed)
            in enumerate(zip(spectrum.observed, decision.q95, decision.margins,
                             decision.passes, strict=True))]


def run_chim_pa(output: Path, *, run_id: str) -> dict:
    started = perf_counter()
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                         for c in run_id):
        raise ValueError("run_id must be nonempty alphanumeric/underscore/hyphen")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("nonempty run directory: choose a fresh run_id/output")
    nominal, samples, tolerance, phase4, policy_data = load_canonical_inputs()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    normalization = nominal_normalization(nominal, DIRECTIONS, optimality_tolerance=tolerance)
    z = normalization.normalize(nominal)
    delta = normalization.perturbations(samples)
    spectra = compute_chim_spectra(z, delta, 3)
    policy = policy_from_mapping(policy_data)
    checkpoints = evaluate_pa_prefixes(spectra, policy.checkpoints)
    stop = evaluate_early_stop(checkpoints, policy)
    final = checkpoints[-1]
    counts = {k: sum(len(s.indices) == k for s in spectra[1:]) for k in (2, 3, 4)}
    if counts != {2: 28, 3: 56, 4: 70} or len(final.decision_quantiles) != 357:
        raise RuntimeError("candidate/decision-quantile count contract mismatch")
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "nominal_normalization.csv",
              ["response", "direction", "sign", "utopia", "payoff_worst", "amplitude",
               "optimality_tolerance", "degeneracy_tolerance"],
              [[name, direction, normalization.signs[j], normalization.utopia[j],
                normalization.payoff_worst[j], normalization.amplitudes[j], tolerance[j],
                normalization.degeneracy_tolerance[j]]
               for j, (name, direction) in enumerate(zip(RESPONSES, DIRECTIONS, strict=True))])
    component_header = ["singular_index", "observed_singular", "q95", "margin", "pass"]
    write_csv(output / "global_pa_B2000.csv", component_header,
              component_rows(spectra[0], final.components[0]))
    local_rows, selected_rows, trajectory_rows = [], [], []
    for spectrum, decision in zip(spectra[1:], final.components[1:], strict=True):
        selected = spectrum.subset_id in final.selected_ids
        row = [spectrum.subset_id, "|".join(RESPONSES[j] for j in spectrum.indices),
               len(spectrum.indices), json.dumps(spectrum.observed.tolist()),
               json.dumps(decision.q95.tolist()), json.dumps(decision.margins.tolist()),
               json.dumps(decision.passes.tolist()), selected]
        local_rows.append(row)
        if selected:
            selected_rows.append(row)
    local_header = ["subset_id", "responses", "k", "observed_singular_values", "q95_values",
                    "margins", "component_passes", "selected"]
    write_csv(output / "local_pa_B2000.csv", local_header, local_rows)
    write_csv(output / "selected_subsets_B2000.csv", local_header, selected_rows)
    prefix_rows = []
    for checkpoint, diagnostic in zip(checkpoints, stop.trajectory, strict=True):
        prefix_rows.append([
            checkpoint.B, checkpoint.global_dimension, *checkpoint.selected_counts,
            len(checkpoint.selected_ids), diagnostic.selection_changed_from_previous,
            diagnostic.max_decision_quantile_relative_change, diagnostic.early_stop_condition_met,
            checkpoint.global_pattern,
        ])
        for spectrum, decision in zip(spectra, checkpoint.components, strict=True):
            for row in component_rows(spectrum, decision):
                trajectory_rows.append([checkpoint.B, spectrum.scope, spectrum.subset_id,
                                        len(spectrum.indices), *row])
    write_csv(output / "prefix_pa_sensitivity.csv", [
        "B", "global_dimension", "selected_pairs", "selected_triples", "selected_quadruples",
        "total_selected", "selection_changed_from_previous",
        "max_decision_quantile_relative_change", "early_stop_condition_met", "global_pattern",
    ], prefix_rows)
    write_csv(output / "pa_quantile_trajectories.csv",
              ["B", "scope", "subset_id", "k", *component_header], trajectory_rows)
    payload = {"global": spectra[0].noise}
    for k, name in [(2, "pairs"), (3, "triples"), (4, "quadruples")]:
        group = [s for s in spectra[1:] if len(s.indices) == k]
        payload[name] = np.stack([s.noise for s in group], axis=1)
        payload[f"{name}_indices"] = np.asarray([s.indices for s in group], dtype=np.int64)
    np.savez_compressed(output / "pa_noise_singular_values.npz", allow_pickle=False, **payload)
    np.savez_compressed(output / "nominal_chim.npz", allow_pickle=False,
                        normalized=z, centered=centered_chim(z), centering=centering_matrix(8))
    write_json(output / "early_stop_validation.json", {
        **asdict(stop), "policy_status": policy_data["status"], "validation_continued_to_B": 2000,
        "reference_selection_B": 2000, "policy_promoted": False,
        "selected_ids_at_stop": sorted(next(r.selected_ids for r in checkpoints
                                           if r.B == stop.first_B_stop))
                                if stop.first_B_stop is not None else None,
        "selected_ids_at_reference": sorted(final.selected_ids),
    })
    for path, digest in INPUT_HASHES.items():
        if sha256_file(path) != digest:
            raise RuntimeError(f"immutable input changed during PA: {path.name}")
    input_paths = [*INPUT_HASHES, ROOT / "uv.lock", Path(__file__),
                   ROOT / "scripts/validation/turning_reference.py",
                   *sorted((ROOT / "src/cnbi_v2/chim").glob("*.py")),
                   ROOT / "src/cnbi_v2/model/quadratic_design.py",
                   ROOT / "src/cnbi_v2/optimization/quadratic.py",
                   *sorted((ROOT / "src/cnbi_v2/data").glob("*.py"))]
    metadata = {
        "run_id": run_id, "executed_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": commit, "git_working_tree_dirty": dirty,
        "nominal_payoff": NOMINAL.relative_to(ROOT).as_posix(),
        "nominal_payoff_sha256": INPUT_HASHES[NOMINAL],
        "phase_4_payoff_sha256": INPUT_HASHES[PAYOFFS],
        "phase_4_source_commit": phase4["git_commit"],
        "dataset_sha256": RAW_SHA256, "response_order": RESPONSES, "anchor_order": RESPONSES,
        "directions": dict(zip(RESPONSES, DIRECTIONS, strict=True)),
        "orientation": "G=D_s A; MIN=+1, MAX=-1",
        "normalization": "FIXED_NOMINAL_PAYOFF", "normalization_formula": "Z=(D_s A-u)/a",
        "utopia_nominal_oriented": normalization.utopia.tolist(),
        "nominal_amplitudes": normalization.amplitudes.tolist(),
        "nominal_optimality_tolerance_definition": "4*objective_scale*1e-10 + "
                                                  "eps64*16*m*max_abs_nominal_row",
        "amplitude_degeneracy_tolerance": "eps64*16*m*max_abs_nominal_row",
        "geometry": "CENTERED_CHIM: Z[C,C] @ (I-ones/k)",
        "noise_geometry": "Delta[C,C] @ H_k; Delta=D_a^-1 D_s (A_b-A_nom)",
        "terminology": "Monte Carlo uncertainty-calibrated Parallel Analysis / "
                       "PA-inspired spectral screening; no equivalence claim to classical Horn PA",
        "quantile": .95, "quantile_method": "linear", "comparison": "strict observed > q95",
        "candidate_sizes": [2, 3, 4], "candidate_counts": counts,
        "candidate_order": "increasing k, lexicographic zero-based response index combinations",
        "subset_id_convention": "C_ followed by one-based response indices joined with underscores",
        "B_max": 2000, "reference_B": 2000, "checkpoints": list(policy.checkpoints),
        "decision_quantile_count": len(final.decision_quantiles),
        "decision_quantile_ids": final.quantile_ids,
        "global_dimension_B2000": final.global_dimension,
        "global_pattern_B2000": final.global_pattern,
        "selected_counts_B2000": dict(zip(["pairs", "triples", "quadruples"],
                                          final.selected_counts, strict=True)),
        "selected_ids_B2000": sorted(final.selected_ids),
        "selected_total_B2000": len(final.selected_ids),
        "early_stop_policy_sha256": INPUT_HASHES[POLICY], "early_stop_policy": policy_data,
        "B_stop": stop.first_B_stop, "early_stop_status": stop.stop_status,
        "retrospective_status": stop.retrospective_status, "policy_promoted": False,
        "validation_continued_to_B": 2000,
        "centering_max_abs_vertex_sum": float(np.max(np.abs(centered_chim(z).sum(axis=1)))),
        "centered_rank_diagnostic": int(np.linalg.matrix_rank(centered_chim(z))),
        "vertex_difference_rank_diagnostic": int(np.linalg.matrix_rank(vertex_differences(z))),
        "rank_diagnostic_tolerance": "NumPy default s_max*max(shape)*eps64; not a selection filter",
        "new_random_draws": 0, "anchors_reoptimized": False, "RC_applied": False,
        "qmax_filter": False, "volume_filter": False, "clipping": False, "H_chosen": False,
        "elapsed_seconds": perf_counter()-started, "dtype": "float64", "seed_original": 777,
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: version(name) for name in ["numpy", "scipy"]},
        "input_sha256": {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in input_paths},
        "artifact_sha256": {p.name: sha256_file(p) for p in sorted(output.iterdir())},
        "command": "uv run python -m scripts.validation.turning_chim_pa "
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
    metadata = run_chim_pa(args.output or ROOT / "results/phase_05_chim_pa" / args.run_id,
                           run_id=args.run_id)
    keys = ["global_dimension_B2000", "selected_counts_B2000", "B_stop",
            "early_stop_status", "retrospective_status"]
    print(json.dumps({k: metadata[k] for k in keys},
                     indent=2))


if __name__ == "__main__":
    main()
