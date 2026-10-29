"""Read-only numerical inputs: shorten crowded RMSE labels without refitting."""

import csv
import json
import os
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from matplotlib import rc_context
from synthetic_rsm_diagnostics import figures

from cnbi_v2.synthetic.rsm.rsm_inputs import load_structural_cases, sha256_file, verify_checksums
from cnbi_v2.synthetic.rsm.rsm_serialization import load_models, write_json
from cnbi_v2.synthetic.rsm.rsm_validation import ExternalSample

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/phase_10_synthetic_rsm/rsm_20261029"


def archive_figure_inputs(directory):
    def read(name):
        with (directory / name).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    cases = load_structural_cases(
        ROOT / "results/phase_10_synthetic_generation/structural_20261029"
    )
    cells = {c.scenario_id: c for c, _ in cases}
    models = load_models(directory)
    rows = read("synthetic_rsm_instances.csv")
    noise = read("synthetic_noise_parameters.csv")
    items, samples = [], {}
    with (
        np.load(directory / "synthetic_experimental_arrays.npz", allow_pickle=False) as data,
        np.load(directory / "synthetic_external_sample.npz", allow_pickle=False) as holdout,
    ):
        for row in rows:
            key, sid = row["instance_id"], row["scenario_id"]
            fit = SimpleNamespace(
                coefficients=models[key].coefficients,
                predict=models[key].predict,
                residuals=data[key + "__residuals"],
                fitted_values=data[key + "__fitted"],
            )
            items.append(
                SimpleNamespace(
                    scenario=cells[sid],
                    replica_id=int(row["replica_id"]),
                    fit=fit,
                    noise=data[key + "__noise"],
                    sigma_squared=np.array(
                        [float(n["noise_variance"]) for n in noise if n["instance_id"] == key]
                    ),
                )
            )
            samples[sid] = ExternalSample(
                int(row["external_seed"]), holdout[sid + "__points"], holdout[sid + "__truth"]
            )
    # Plotting needs numeric dictionaries, not recomputed diagnostics.
    diagnostics, external = (
        read("synthetic_rsm_diagnostics.csv"),
        read("synthetic_external_validation.csv"),
    )
    for row in diagnostics + external:
        row["nx"] = int(row["nx"])
        row["rho_target"] = float(row["rho_target"])
        for name in ("r_squared", "adjusted_r_squared", "predicted_r_squared", "rmse"):
            if name in row:
                row[name] = float(row[name])
    return tuple(items), {c.scenario_id: a for c, a in cases}, samples, diagnostics, external


def refine(directory=OUTPUT):
    verify_checksums(directory)
    numerical = {
        p.name: sha256_file(p) for p in directory.iterdir() if p.suffix in (".npz", ".csv")
    }
    started = time.perf_counter()
    paths = [directory / "figures" / ("external_rmse" + suffix) for suffix in (".png", ".pdf")]
    previous = {p.name: sha256_file(p) for p in paths}
    with rc_context(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.grid": False,
            "pdf.fonttype": 42,
            "axes.linewidth": 0.7,
        }
    ):
        fig = figures(*archive_figure_inputs(directory))["external_rmse"]
        for ax, nx in zip(fig.axes, (2, 3, 5), strict=True):
            ax.set_title(f"{nx} factors")
            ax.set_xlabel("Structural absolute-correlation target", fontsize=8)
        fig.suptitle("All excess levels and replicas", fontsize=9)
        for path in paths:
            fig.savefig(path, dpi=600)
    assert numerical == {
        p.name: sha256_file(p) for p in directory.iterdir() if p.suffix in (".npz", ".csv")
    }
    script = Path(__file__).resolve()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest_path = directory / "generation_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["figure_layout_refinement"] = dict(
        code_commit=commit,
        script=str(script.relative_to(ROOT)).replace("\\", "/"),
        sha256=sha256_file(script),
        reason="Shorter panel titles prevent crowding; no numerical or methodological change",
        previous_figure_sha256=previous,
        numerical_files_unchanged=len(numerical),
        elapsed_seconds=time.perf_counter() - started,
    )
    write_json(manifest_path, manifest)
    entries = {}
    for line in (directory / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        _, name = line.split("  ", 1)
        entries[name] = sha256_file(directory / name)
    entries[Path(os.path.relpath(script, directory)).as_posix()] = sha256_file(script)
    (directory / "checksums.sha256").write_text(
        "".join(digest + "  " + name + "\n" for name, digest in sorted(entries.items())),
        encoding="utf-8",
    )
    return manifest["figure_layout_refinement"]


if __name__ == "__main__":
    print(json.dumps(refine(), indent=2))
