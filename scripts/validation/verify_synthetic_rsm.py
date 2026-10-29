"""Read-only archive verification: no calibration, OLS or stochastic regeneration."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from cnbi_v2.synthetic.rsm.rsm_inputs import array_sha256, sha256_file, verify_checksums
from cnbi_v2.synthetic.rsm.rsm_serialization import load_models

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/phase_10_synthetic_rsm/rsm_20261029"


def verify(directory: Path):
    hashes = verify_checksums(directory)
    manifest = json.loads((directory / "generation_manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] != "COMPLETE" or manifest["failures"] or manifest["failed_models"]:
        raise ValueError("campaign is incomplete or failed")
    models = load_models(directory)
    with (directory / "synthetic_rsm_instances.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 135 or set(models) != {r["instance_id"] for r in rows}:
        raise ValueError("all 135 identified noisy models are required")
    if sum(int(r["n"]) for r in rows) != 3555 or sum(int(r["m"]) for r in rows) != 990:
        raise ValueError("experiment or response counts differ")
    if len({r["seed"] for r in rows}) != 135:
        raise ValueError("noise streams must be unique")
    for archive, arrays in manifest["array_manifest"].items():
        with np.load(directory / archive, allow_pickle=False) as data:
            if set(data.files) != set(arrays):
                raise ValueError("incomplete numerical archive")
            for key, meta in arrays.items():
                if (
                    list(data[key].shape) != meta["shape"]
                    or str(data[key].dtype) != meta["dtype"]
                    or array_sha256(data[key]) != meta["sha256"]
                ):
                    raise ValueError("numerical array integrity failure: " + key)
    frozen = json.loads((directory / "frozen_inputs_manifest.json").read_text(encoding="utf-8"))
    for name, digest in frozen.items():
        if sha256_file(ROOT / name) != digest:
            raise ValueError("frozen Phase0–10A input changed: " + name)
    return dict(
        status="VERIFIED",
        models=len(models),
        experimental_rows=3555,
        response_models=990,
        checksums=len(hashes),
        frozen_files=len(frozen),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    print(json.dumps(verify(parser.parse_args().directory), indent=2))
