"""Revise only stopping diagnostics using the immutable Phase 5 noise spectra."""

import argparse
import csv
import json
import platform
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import version
from itertools import combinations
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from cnbi_v2.chim import (
    ChimSpectrum,
    checkpoint_spectral_gaps,
    evaluate_gap_early_stop,
    evaluate_pa_prefixes,
    gap_policy_from_mapping,
)
from cnbi_v2.data import sha256_file

from .turning_reference import ROOT, write_csv, write_json

SOURCE_COMMIT = "fc57b05c96a72a8cc6128f49ef270a689cc9bac0"
SOURCE = ROOT / "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024"
POLICY = ROOT / "docs/policies/pa_early_stop_policy.json"
RUN_ID = "turning_spectral_gap_policy_v2_20261024"
ARCHIVE_HASHES = {
    "early_stop_validation.json":
        "f00bd2e0b871813e08ea7a5a7380c9f2103b1ea17c5980e01045dac225ec96ec",
    "global_pa_B2000.csv": "694a1243917ae9b6c29a96e9ccb0ac311bcc61a7910e433dfe361967c9781b6f",
    "local_pa_B2000.csv": "244d77ef82a6d5fa7b8bb60984641248cf763ef370dc894522196087f652118e",
    "metadata.json": "61f84b930aa8b0adb9a9bc48f2129dbcc675f73bc582d7053f500188d5f87992",
    "nominal_chim.npz": "181420d3baec324fe02df7274c7130452e562ef5974e527fe63da5c935e6eb40",
    "nominal_normalization.csv": "bc19f7ef44d5ee86b10b4fb789fe55742b0dc6dc2119277d5811e7464bb76dc0",
    "pa_noise_singular_values.npz":
        "4496326958f35ad7a322702e43db3d99eade1497d98e0b179974d424b5e71dba",
    "pa_quantile_trajectories.csv":
        "15df4a3c7a18674f65a04bb633ddf2fe0fb506b9d00874777aec4f9fe925d441",
    "prefix_pa_sensitivity.csv": "171b3679573b1a624628569d388ed3f6fba875e3aabcc02bdfe1d26a655f343c",
    "selected_subsets_B2000.csv":
        "198d03f7756ba9f0633d87a6142e5ac6da014a135f78df405994cc10b6b77e46",
}


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def verify_archive():
    for name, digest in ARCHIVE_HASHES.items():
        if sha256_file(SOURCE / name) != digest:
            raise ValueError(f"immutable Phase 5 SHA-256 mismatch: {name}")
    manifest = dict(
        line.split("  ")[::-1]
        for line in (SOURCE / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    )
    if manifest != ARCHIVE_HASHES:
        raise ValueError("historical checksum manifest mismatch")


def load_saved_spectra():
    """No normalization, CHIM or SVD; reconstruct containers from saved arrays only."""
    verify_archive()
    global_rows = read_rows(SOURCE / "global_pa_B2000.csv")
    local_rows = read_rows(SOURCE / "local_pa_B2000.csv")
    if [int(row["singular_index"]) for row in global_rows] != list(range(1, 8)):
        raise ValueError("saved global component order mismatch")
    local_lookup = {row["subset_id"]: row for row in local_rows}
    result = []
    with np.load(SOURCE / "pa_noise_singular_values.npz", allow_pickle=False) as archive:
        expected_keys = {
            "global",
            "pairs",
            "pairs_indices",
            "triples",
            "triples_indices",
            "quadruples",
            "quadruples_indices",
        }
        if set(archive.files) != expected_keys:
            raise ValueError("saved noise array keys mismatch")
        global_noise = archive["global"]
        if global_noise.shape != (2000, 7) or global_noise.dtype != np.float64:
            raise ValueError("saved global noise shape/dtype mismatch")
        result.append(
            ChimSpectrum(
                "GLOBAL",
                "GLOBAL",
                tuple(range(8)),
                np.array([float(r["observed_singular"]) for r in global_rows]),
                global_noise,
            )
        )
        for name, k in [("pairs", 2), ("triples", 3), ("quadruples", 4)]:
            indices = np.asarray(list(combinations(range(8), k)), dtype=np.int64)
            noise = archive[name]
            if (
                not np.array_equal(archive[f"{name}_indices"], indices)
                or noise.shape != (2000, len(indices), k - 1)
                or noise.dtype != np.float64
            ):
                raise ValueError("saved local noise indices/shape/dtype mismatch")
            for j, subset in enumerate(indices):
                identifier = "C_" + "_".join(str(i + 1) for i in subset)
                observed = np.array(
                    json.loads(local_lookup[identifier]["observed_singular_values"])
                )
                if observed.shape != (k - 1,):
                    raise ValueError("saved observed local component shape mismatch")
                result.append(
                    ChimSpectrum(
                        "LOCAL", identifier, tuple(map(int, subset)), observed, noise[:, j]
                    )
                )
    if (
        len(result) != 155
        or len(local_rows) != 154
        or any(
            not np.isfinite(s.noise).all()
            or np.any(s.noise < 0)
            or np.any(s.noise[:, :-1] < s.noise[:, 1:])
            for s in result
        )
    ):
        raise ValueError("saved spectra must be complete, finite nonnegative and descending")
    return tuple(result)


def verify_historical_decisions(records, spectra):
    """Every q95, observed value, margin, PASS/FAIL and selected ID stays exact."""
    expected_rows = []
    for record in records:
        if not np.array_equal(record.decision_quantiles,
                              np.concatenate([d.q95 for d in record.components])):
            raise ValueError("checkpoint quantile vector differs from component q95")
        for spectrum, decision in zip(spectra, record.components, strict=True):
            for j in range(len(spectrum.observed)):
                expected_rows.append(
                    (
                        record.B,
                        spectrum.scope,
                        spectrum.subset_id,
                        len(spectrum.indices),
                        j + 1,
                        spectrum.observed[j],
                        decision.q95[j],
                        decision.margins[j],
                        bool(decision.passes[j]),
                    )
                )
    historical = read_rows(SOURCE / "pa_quantile_trajectories.csv")
    actual_rows = [
        (
            int(r["B"]),
            r["scope"],
            r["subset_id"],
            int(r["k"]),
            int(r["singular_index"]),
            float(r["observed_singular"]),
            float(r["q95"]),
            float(r["margin"]),
            r["pass"] == "True",
        )
        for r in historical
    ]
    if expected_rows != actual_rows:
        raise ValueError("historical q95/margin/PASS decision changed")
    old_prefix = read_rows(SOURCE / "prefix_pa_sensitivity.csv")
    if len(old_prefix) != len(records):
        raise ValueError("historical prefix count mismatch")
    for record, old in zip(records, old_prefix, strict=True):
        old_selection = {}
        for row in historical:
            if int(row["B"]) == record.B and row["scope"] == "LOCAL":
                old_selection.setdefault(row["subset_id"], []).append(row["pass"] == "True")
        selected = frozenset(key for key, flags in old_selection.items() if all(flags))
        if (
            selected != record.selected_ids
            or int(old["B"]) != record.B
            or int(old["global_dimension"]) != record.global_dimension
            or old["global_pattern"] != record.global_pattern
            or tuple(int(old[f"selected_{name}"]) for name in ("pairs", "triples", "quadruples"))
            != record.selected_counts
        ):
            raise ValueError("historical dimension/selection identities changed")
    final_ids = {r["subset_id"] for r in read_rows(SOURCE / "selected_subsets_B2000.csv")}
    if (
        records[-1].selected_ids != final_ids
        or records[-1].selected_counts != (19, 18, 0)
        or records[-1].global_dimension != 2
    ):
        raise ValueError("B=2000 scientific reference changed")
    return old_prefix


def plot_global_gaps(output, records, histories, first_stop):
    figure = Figure(figsize=(9, 4.5), layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.add_subplot()
    b_values = [r.B for r in records]
    axes.plot(
        b_values,
        [h[0].gaps.normalized[0] for h in histories],
        label="g1: ranks 1–2",
        marker="o",
        markersize=3,
        linewidth=1.8,
    )
    axes.plot(
        b_values,
        [h[0].gaps.normalized[1] for h in histories],
        label="g2: ranks 2–3 (critical)",
        marker="s",
        markersize=3,
        linewidth=1.8,
    )
    if first_stop is not None:
        axes.axvline(
            first_stop,
            color="0.45",
            linestyle="--",
            linewidth=1,
            label=f"retrospective stop B={first_stop}",
        )
    axes.set(
        xlabel="Prefix B (same frozen 2000 replicas)",
        ylabel="Normalized q95 spectral gap",
        title="Global q95 spectrum: adjacent normalized gaps",
        xlim=(50, 2050),
    )
    axes.grid(alpha=0.2)
    axes.legend(loc="best")
    figure.savefig(
        output / "global_q95_spectral_gaps.png",
        dpi=180,
        metadata={"Software": "C-NBI v2; Matplotlib Agg"},
    )


def run_gap_revision(output: Path, *, run_id: str):
    if not run_id or any(
        c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in run_id
    ):
        raise ValueError("run_id must be nonempty alphanumeric/underscore/hyphen")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("nonempty run directory: choose a fresh output")
    policy_data = json.loads(POLICY.read_text(encoding="utf-8"))
    policy = gap_policy_from_mapping(policy_data)
    spectra = load_saved_spectra()
    records = evaluate_pa_prefixes(spectra, policy.checkpoints)  # Quantiles only, no SVD.
    legacy = verify_historical_decisions(records, spectra)
    validation = evaluate_gap_early_stop(records, policy)
    histories = [checkpoint_spectral_gaps(r, epsilon=policy.epsilon_q) for r in records]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    source_paths = [SOURCE / name for name in ARCHIVE_HASHES]
    source_paths += [
        SOURCE / "checksums.sha256",
        POLICY,
        ROOT / policy_data["previous_policy_file"],
        Path(__file__),
        ROOT / "uv.lock",
        ROOT / "src/cnbi_v2/chim/spectral_gap_stop.py",
        ROOT / "src/cnbi_v2/chim/parallel_analysis.py",
    ]
    before = {str(p.relative_to(ROOT).as_posix()): sha256_file(p) for p in source_paths}
    output.mkdir(parents=True, exist_ok=True)
    gap_rows, global_rows, prefix_rows, window_rows = [], [], [], []
    for i, (record, history, diagnostic) in enumerate(
        zip(records, histories, validation.trajectory, strict=True)
    ):
        previous = {s.subset_id: s for s in histories[i - 1]} if i else {}
        for spectrum in history:
            for j, value in enumerate(spectrum.gaps.normalized):
                change = (
                    abs(float(value) - float(previous[spectrum.subset_id].gaps.normalized[j]))
                    if i
                    else None
                )
                gap_rows.append(
                    [
                        record.B,
                        spectrum.scope,
                        spectrum.subset_id,
                        spectrum.k,
                        j + 1,
                        spectrum.q95[j],
                        spectrum.q95[j + 1],
                        spectrum.gaps.absolute[j],
                        value,
                        change,
                        spectrum.scope == "GLOBAL"
                        or spectrum.subset_id in diagnostic.monitored_subset_ids,
                    ]
                )
        global_gaps = history[0].gaps.normalized
        critical = (
            global_gaps[record.global_dimension - 1]
            if 0 < record.global_dimension < len(history[0].q95)
            else None
        )
        global_rows.append(
            [record.B, record.global_dimension, *global_gaps, global_gaps[0], critical]
        )
        row = asdict(diagnostic)
        prefix_rows.append(
            [
                record.B,
                record.global_dimension,
                *record.selected_counts,
                len(record.selected_ids),
                *[row[name] for name in PREFIX_DIAGNOSTICS],
                legacy[i]["max_decision_quantile_relative_change"],
            ]
        )
        window_rows.append(
            [
                record.B,
                json.dumps([r.B for r in records[max(0, i - 2) : i + 1]]),
                diagnostic.eligible,
                json.dumps(sorted(record.selected_ids)),
                json.dumps(diagnostic.monitored_subset_ids),
                diagnostic.monitored_gap_count,
                json.dumps(diagnostic.degenerate_gap_ids),
            ]
        )
    write_csv(
        output / "spectral_gap_trajectories.csv",
        [
            "B",
            "scope",
            "subset_id",
            "k",
            "gap_index",
            "q_r",
            "q_r_plus_1",
            "absolute_gap",
            "normalized_gap",
            "normalized_gap_change_from_previous",
            "monitored_for_early_stop",
        ],
        gap_rows,
    )
    write_csv(
        output / "global_spectral_gap_trajectory.csv",
        [
            "B",
            "global_dimension",
            "g1",
            "g2",
            "g3",
            "g4",
            "g5",
            "g6",
            "first_global_gap",
            "critical_global_gap",
        ],
        global_rows,
    )
    write_csv(
        output / "prefix_pa_sensitivity.csv",
        [
            "B",
            "global_dimension",
            "selected_pairs",
            "selected_triples",
            "selected_quadruples",
            "total_selected",
            *PREFIX_DIAGNOSTICS,
            "legacy_max_decision_quantile_relative_change",
        ],
        prefix_rows,
    )
    write_csv(
        output / "window_monitoring.csv",
        [
            "B",
            "window_checkpoints",
            "eligible_full_window",
            "selected_subset_ids",
            "monitored_local_subset_ids",
            "monitored_gap_count",
            "degenerate_gap_ids",
        ],
        window_rows,
    )
    stopped = next((r for r in records if r.B == validation.first_B_stop), None)
    write_json(
        output / "early_stop_validation.json",
        {
            **asdict(validation),
            "policy_version": 2,
            "policy_status": policy_data["status"],
            "post_hoc_on_turning_case": True,
            "policy_promoted": False,
            "selected_ids_at_stop": sorted(stopped.selected_ids) if stopped else None,
            "global_dimension_at_stop": stopped.global_dimension if stopped else None,
            "selected_counts_at_stop": list(stopped.selected_counts) if stopped else None,
            "selected_ids_at_reference": sorted(records[-1].selected_ids),
            "post_stop_gap_monitoring": (
                "fixed gap set from the stop window, every later transition"
            ),
            "validation_continued_to_B": 2000,
        },
    )
    plot_global_gaps(output, records, histories, validation.first_B_stop)
    verify_archive()
    if before != {p: sha256_file(ROOT / p) for p in before}:
        raise RuntimeError("input modified during spectral-gap revision")
    metadata = {
        "run_id": run_id,
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": commit,
        "git_working_tree_dirty": dirty,
        "original_archive_commit": SOURCE_COMMIT,
        "original_archive": SOURCE.relative_to(ROOT).as_posix(),
        "policy_version": 2,
        "policy_status": policy_data["status"],
        "policy_sha256": before[POLICY.relative_to(ROOT).as_posix()],
        "post_hoc_on_turning_case": True,
        "external_validation": False,
        "policy_promoted": False,
        "new_random_draws": 0,
        "anchors_reoptimized": False,
        "payoffs_recalculated": False,
        "normalization_recalculated": False,
        "chim_recalculated": False,
        "svd_recalculated": False,
        "all_historical_thresholds_and_decisions_identical": True,
        "gap_filter_applied_to_pa": False,
        "reference_B": 2000,
        "global_dimension_B2000": records[-1].global_dimension,
        "selected_counts_B2000": list(records[-1].selected_counts),
        "B_stop_gap": validation.first_B_stop,
        "retrospective_status": validation.retrospective_status,
        "same_final_selection": validation.same_final_selection,
        "same_final_dimension": validation.same_final_dimension,
        "replicate_reduction_fraction": validation.replicate_reduction_fraction,
        "reduction_interpretation": (
            "potential replica reduction, not measured wall-clock savings; "
            "full frozen B=2000 was already available"
        ),
        "gap_row_count": len(gap_rows),
        "gap_units": "normalized fractions; multiply change by 100 for percentage points",
        "monitored_set_semantics": (
            "global plus local k>=3 IDs in intersection of current three-checkpoint window; "
            "before 3 points diagnostic intersection only; unequal full selections prevent stopping"
        ),
        "post_stop_gap_monitoring": (
            "freeze monitor set at stop, compare every later adjacent transition"
        ),
        "degenerate_q95_status": "DEGENERATE_Q95_SPECTRUM"
        if any(r.degenerate_gap_ids for r in validation.trajectory)
        else "NOT_DETECTED",
        "input_sha256": before,
        "python": platform.python_version(),
        "packages": {name: version(name) for name in ["numpy", "matplotlib"]},
        "command": "uv run python -m scripts.validation.turning_spectral_gap_stop "
        f"--run-id {run_id} [--output fresh_directory]",
    }
    write_json(output / "metadata.json", metadata)
    (output / "checksums.sha256").write_text(
        "".join(
            f"{sha256_file(p)}  {p.name}\n"
            for p in sorted(output.iterdir())
            if p.is_file() and p.name != "checksums.sha256"
        ),
        encoding="utf-8",
        newline="\n",
    )
    return metadata


PREFIX_DIAGNOSTICS = [
    "selection_changed_from_previous",
    "global_gap_max_change",
    "selected_local_gap_max_change",
    "overall_monitored_gap_max_change",
    "previous_transition_monitored_gap_max_change",
    "window_monitored_gap_max_change",
    "three_checkpoint_dimension_stable",
    "three_checkpoint_selection_stable",
    "monitored_spectra_consistent",
    "spectral_gap_stable",
    "eligible",
    "early_stop_condition_met",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=RUN_ID)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    metadata = run_gap_revision(
        args.output or ROOT / "results/phase_05_chim_pa" / args.run_id, run_id=args.run_id
    )
    print(
        json.dumps(
            {
                key: metadata[key]
                for key in [
                    "B_stop_gap",
                    "retrospective_status",
                    "same_final_selection",
                    "same_final_dimension",
                    "replicate_reduction_fraction",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
