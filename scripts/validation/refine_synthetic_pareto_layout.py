"""Display-only archive rendering; preserve all reference and diagnostic bytes."""

import csv
import json
import os
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from matplotlib import rc_context
from matplotlib.ticker import MaxNLocator
from synthetic_pareto_diagnostics import figures

from cnbi_v2.synthetic.pareto.geometry import hull_geometry
from cnbi_v2.synthetic.pareto.serialization import (
    load_true_anchors,
    sha256_file,
    verify_checksums,
    write_json,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/phase_10_synthetic_pareto/analytical_20261029"


def archive_inputs(directory):
    cases = load_true_anchors(ROOT / "results/phase_10_synthetic_generation/structural_20261029")
    refs = []
    with (
        np.load(directory / "pareto_reference_decisions.npz", allow_pickle=False) as x,
        np.load(directory / "pareto_reference_normalized.npz", allow_pickle=False) as z,
    ):
        for cell, a in cases:
            refs.append(
                SimpleNamespace(
                    scenario=cell,
                    geometry=hull_geometry(a),
                    decisions=x[cell.scenario_id],
                    normalized=z[cell.scenario_id],
                )
            )

    def read(name):
        with (directory / name).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    diagnostics = read("reference_cardinality_sensitivity.csv")
    for row in diagnostics:
        for key in ("nx", "count"):
            row[key] = int(row[key])
        for key in ("probe_rms_coordinate_max", "hausdorff_rms_coordinate"):
            row[key] = float(row[key])
    config = json.loads(
        (directory / "hypervolume_integration_config.json").read_text(encoding="utf-8")
    )
    hv = [
        r
        for r in read("hypervolume_precision_diagnostics.csv")
        if int(r["tier_max_power"]) == config["final_power"]
    ]
    for row in hv:
        for key in ("power", "n_reference"):
            row[key] = int(row[key]) if row[key] else None
        for key in ("HV_QMC", "HV_QMC_SE", "relative_se", "relative_change_previous"):
            row[key] = float(row[key]) if row[key] else None
    return refs, diagnostics, hv, read("pareto_ideal_nadir.csv")


def refine(directory=OUTPUT):
    verify_checksums(directory)
    script = Path(__file__).resolve()
    relative = script.relative_to(ROOT).as_posix()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    import hashlib

    committed = subprocess.check_output(["git", "show", commit + ":" + relative], cwd=ROOT)
    if hashlib.sha256(committed).hexdigest() != sha256_file(script):
        raise ValueError("commit the display script before rendering")
    numerical = {
        p.name: sha256_file(p) for p in directory.iterdir() if p.suffix in (".npz", ".csv")
    }
    names = ("pareto_decision_geometry", "hypervolume_precision")
    paths = [
        directory / "figures" / (name + extension)
        for name in names
        for extension in (".png", ".pdf")
    ]
    previous = {p.name: sha256_file(p) for p in paths}
    started = time.perf_counter()
    with rc_context(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.grid": False,
            "pdf.fonttype": 42,
            "axes.linewidth": 0.7,
        }
    ):
        plots = figures(*archive_inputs(directory))
        ax = plots["pareto_decision_geometry"].axes[1]
        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.set_major_locator(MaxNLocator(nbins=3))
        ax.tick_params(labelsize=8, pad=1)
        plots["hypervolume_precision"].axes[0].legend(
            loc="center right", bbox_to_anchor=(1, 0.68), frameon=False, fontsize=8
        )
        for path in paths:
            plots[path.stem].savefig(path, dpi=600)
    assert numerical == {
        p.name: sha256_file(p) for p in directory.iterdir() if p.suffix in (".npz", ".csv")
    }
    manifest_path = directory / "generation_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["figure_layout_refinement"] = dict(
        code_commit=commit,
        script=relative,
        sha256=sha256_file(script),
        reason="Reduce 3D tick overlap and move HV legend off curves",
        numerical_files_unchanged=len(numerical),
        previous_figure_sha256=previous,
        elapsed_seconds=time.perf_counter() - started,
    )
    write_json(manifest_path, manifest)
    entries = {}
    for row in (directory / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        _, name = row.split("  ", 1)
        entries[name] = sha256_file(directory / name)
    entries[Path(os.path.relpath(script, directory)).as_posix()] = sha256_file(script)
    (directory / "checksums.sha256").write_bytes(
        "".join(h + "  " + n + "\n" for n, h in sorted(entries.items())).encode("utf-8")
    )
    return manifest["figure_layout_refinement"]


if __name__ == "__main__":
    print(json.dumps(refine(), indent=2))
