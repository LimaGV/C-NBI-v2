"""Canonical-LF metadata, float64 arrays and immutable-source reference loading."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ..design import Scenario, factorial_design
from ..model import FloatArray, frozen
from .evaluation import EvaluationContext
from .hypervolume import FixedHypervolume
from .normalization import analytic_normalization


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_sha256(values: NDArray[np.generic]) -> str:
    canonical = np.asarray(values, dtype=values.dtype.newbyteorder("<"), order="C")
    return hashlib.sha256(canonical.tobytes()).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.write_bytes((json.dumps(data, indent=2, allow_nan=False) + "\n").encode("utf-8"))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("nonempty table required")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: format(v, ".17g") if isinstance(v, float) else v for k, v in row.items()}
            )


def verify_checksums(directory: Path) -> dict[str, str]:
    rows = (directory / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    result = {}
    for row in rows:
        digest, name = row.split("  ", 1)
        if len(digest) != 64 or name in result or sha256_file(directory / name) != digest:
            raise ValueError("invalid or inconsistent checksum: " + name)
        result[name] = digest
    if not result:
        raise ValueError("empty checksum archive")
    return result


def load_true_anchors(directory: Path) -> tuple[tuple[Scenario, FloatArray], ...]:
    """Only the 27 approved Phase10A anchor arrays; no RSM or algorithm outputs."""
    checksums = verify_checksums(directory)
    for required in (
        "synthetic_scenarios.csv",
        "synthetic_anchors.csv",
        "synthetic_correlation_matrices.npz",
        "calibration_manifest.json",
    ):
        if required not in checksums:
            raise ValueError("source manifest misses " + required)
    manifest = json.loads((directory / "calibration_manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] != "COMPLETE" or manifest["validated"] != 27:
        raise ValueError("Phase10A source is incomplete")
    with (directory / "synthetic_scenarios.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    cells = factorial_design()
    if [r["scenario_id"] for r in rows] != [c.scenario_id for c in cells]:
        raise ValueError("exactly the 27 approved structural identifiers are required")
    result = []
    with np.load(directory / "synthetic_correlation_matrices.npz", allow_pickle=False) as arrays:
        for cell, row in zip(cells, rows, strict=True):
            anchors = frozen(arrays[cell.scenario_id + "__anchors"])
            if anchors.shape != (cell.m, cell.nx) or row["valid"] != "True":
                raise ValueError("invalid frozen source anchors")
            result.append((cell, anchors))
    return tuple(result)


def load_reference(
    directory: Path, scenario_id: str, count: int = 5000
) -> tuple[FloatArray, FloatArray, FloatArray]:
    if count not in (2500, 5000, 10000) or scenario_id not in {
        c.scenario_id for c in factorial_design()
    }:
        raise ValueError("known structural ID and reference cardinality required")
    verify_checksums(directory)
    values = []
    with np.load(directory / "pareto_reference_nested.npz", allow_pickle=False) as extension:
        for filename, suffix in (
            ("decisions", "decisions"),
            ("objectives", "objectives"),
            ("normalized", "normalized"),
        ):
            with np.load(
                directory / f"pareto_reference_{filename}.npz", allow_pickle=False
            ) as data:
                primary = data[scenario_id]
                matrix = (
                    np.vstack((primary, extension[scenario_id + "__" + suffix + "_extension"]))
                    if count == 10000
                    else primary[:count]
                )
                if len(matrix) != count:
                    raise ValueError("incomplete reference archive")
                values.append(frozen(matrix))
    return values[0], values[1], values[2]


def load_evaluation_context(
    directory: Path, scenario_id: str, structural_directory: Path
) -> EvaluationContext:
    cells = {c.scenario_id: (c, a) for c, a in load_true_anchors(structural_directory)}
    if scenario_id not in cells:
        raise ValueError("unknown structural scenario")
    _, _, normalized = load_reference(directory, scenario_id)
    protocol = json.loads(
        (directory / "hypervolume_integration_config.json").read_text(encoding="utf-8")
    )
    cell, anchors = cells[scenario_id]
    with (directory / "reference_coverage_diagnostics.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        coverage = {r["scenario_id"]: r["status"] for r in csv.DictReader(stream)}
    return EvaluationContext(
        cell,
        anchors,
        analytic_normalization(anchors),
        normalized,
        FixedHypervolume(cell.m, protocol["master_seed"], protocol["final_power"]),
        protocol["status"],
        coverage[scenario_id],
    )
