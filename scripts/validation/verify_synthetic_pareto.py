"""Read-only Phase10C verification; no sampling,FPS,HV recalculation or fitting."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from cnbi_v2.synthetic.design import factorial_design
from cnbi_v2.synthetic.pareto.serialization import array_sha256, sha256_file, verify_checksums

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/phase_10_synthetic_pareto/analytical_20261029"


def verify(directory):
    hashes = verify_checksums(directory)
    manifest = json.loads((directory / "generation_manifest.json").read_text(encoding="utf-8"))
    if (
        manifest["status"] != "COMPLETE"
        or manifest["failures"]
        or manifest["scenarios"] != 27
        or manifest["primary_points_per_scenario"] != 5000
        or manifest["primary_points_total"] != 135000
    ):
        raise ValueError("incomplete reference campaign")
    cells = factorial_design()
    for archive, arrays in manifest["array_manifest"].items():
        with np.load(directory / archive, allow_pickle=False) as data:
            if set(data.files) != set(arrays):
                raise ValueError("missing numerical arrays")
            for key, meta in arrays.items():
                if (
                    list(data[key].shape) != meta["shape"]
                    or str(data[key].dtype) != meta["dtype"]
                    or array_sha256(data[key]) != meta["sha256"]
                    or not np.isfinite(data[key]).all()
                ):
                    raise ValueError("numerical array integrity mismatch: " + key)
    for name, columns in (("decisions", "nx"), ("objectives", "m"), ("normalized", "m")):
        with np.load(directory / f"pareto_reference_{name}.npz", allow_pickle=False) as data:
            if set(data.files) != {c.scenario_id for c in cells}:
                raise ValueError("wrong structural IDs")
            for cell in cells:
                if data[cell.scenario_id].shape != (5000, getattr(cell, columns)):
                    raise ValueError("wrong primary reference shape")
    with (directory / "pareto_reference_index.csv").open(encoding="utf-8", newline="") as stream:
        index = list(csv.DictReader(stream))
    if len(index) != 81:
        raise ValueError("missing reference sensitivity index")
    frozen = json.loads((directory / "frozen_inputs_manifest.json").read_text(encoding="utf-8"))
    for name, digest in frozen.items():
        if sha256_file(ROOT / name) != digest:
            raise ValueError("Phase0–10B file changed: " + name)
    return dict(
        status="VERIFIED",
        scenarios=27,
        points_per_reference=5000,
        total=135000,
        checksums=len(hashes),
        frozen_files=len(frozen),
        hypervolume_status=manifest["hypervolume_status"],
        coverage_review_required=manifest["coverage_review_required"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    print(json.dumps(verify(parser.parse_args().directory), indent=2))
