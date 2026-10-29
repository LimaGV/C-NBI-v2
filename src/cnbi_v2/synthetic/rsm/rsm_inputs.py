"""Read-only, checksum-verified consumption of the approved Phase10A archive."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from ..design import Scenario, factorial_design
from ..domain import radius
from ..model import FloatArray, frozen


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_sha256(values: FloatArray) -> str:
    """C-order little-endian float64 payload; shape/dtype are separate metadata."""
    return hashlib.sha256(np.asarray(values, dtype="<f8", order="C").tobytes()).hexdigest()


def verify_checksums(directory: Path) -> dict[str, str]:
    rows = (directory / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    hashes: dict[str, str] = {}
    for row in rows:
        digest, name = row.split("  ", 1)
        if name in hashes or len(digest) != 64:
            raise ValueError("invalid or duplicate checksum entry")
        if sha256_file(directory / name) != digest:
            raise ValueError("checksum mismatch: " + name)
        hashes[name] = digest
    if not hashes:
        raise ValueError("empty checksum manifest")
    return hashes


def load_structural_cases(directory: Path) -> tuple[tuple[Scenario, FloatArray], ...]:
    """No calibration, no anchor selection and no signed-correlation filtering."""
    verify_checksums(directory)
    manifest = json.loads((directory / "calibration_manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] != "COMPLETE" or manifest["validated"] != 27:
        raise ValueError("Phase10A archive is not complete and validated")
    with (directory / "synthetic_scenarios.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with (directory / "synthetic_anchors.csv").open(encoding="utf-8", newline="") as stream:
        anchor_rows = list(csv.DictReader(stream))
    cells = factorial_design()
    if [row["scenario_id"] for row in rows] != [c.scenario_id for c in cells]:
        raise ValueError("all 27 canonical structural IDs are required exactly once")
    cases = []
    with np.load(directory / "synthetic_correlation_matrices.npz", allow_pickle=False) as arrays:
        for cell, row in zip(cells, rows, strict=True):
            if (
                int(row["nx"]),
                int(row["m"]),
                int(row["delta"]),
                float(row["rho_target"]),
                float(row["alpha"]),
                row["valid"],
                row["directions"],
                int(row["anchor_configurations"]),
            ) != (cell.nx, cell.m, cell.delta, cell.rho_target, radius(cell.nx), "True", "MIN", 1):
                raise ValueError("structural metadata differs from approved design")
            a = frozen(arrays[cell.scenario_id + "__anchors"])
            literal = np.array(
                [float(r["value"]) for r in anchor_rows if r["scenario_id"] == cell.scenario_id]
            )
            if a.shape != (cell.m, cell.nx) or not np.array_equal(literal, a.ravel()):
                raise ValueError("CSV/NPZ anchors differ or have incorrect dimensions")
            cases.append((cell, a))
    return tuple(cases)
