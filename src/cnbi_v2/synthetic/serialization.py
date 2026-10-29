"""Lossless numerical exports, independent of visualization and historical data."""

import csv
from pathlib import Path

import numpy as np

from .calibration import CalibratedScenario
from .correlation import summaries
from .domain import radius
from .model import FloatArray
from .validation import certify_anchors, certify_correlation


def correlation_row(result: CalibratedScenario) -> dict[str, object]:
    cell = result.scenario
    cal_abs, cal_signed = summaries(result.calibration_matrix)
    val_abs, val_signed = summaries(result.validation_matrix)
    pop_abs, pop_signed = summaries(result.population_matrix)
    anchor = certify_anchors(
        result.anchors, radius(cell.nx), result.config.separation_ratio, result.config.rank_rtol
    )
    matrix = certify_correlation(result.validation_matrix, cell.nx, result.config.matrix_tolerance)
    return dict(
        scenario_id=cell.scenario_id,
        nx=cell.nx,
        delta=cell.delta,
        m=cell.m,
        rho_target=cell.rho_target,
        rho_abs_calibration=cal_abs,
        rho_abs_realized=val_abs,
        rho_signed=val_signed,
        rho_signed_calibration=cal_signed,
        rho_abs_population=pop_abs,
        rho_signed_population=pop_signed,
        error_calibration=abs(cal_abs - cell.rho_target),
        error_validation=abs(val_abs - cell.rho_target),
        maximum_entry_error_calibration=float(
            np.max(abs(result.calibration_matrix - result.population_matrix))
        ),
        maximum_entry_error_validation=float(
            np.max(abs(result.validation_matrix - result.population_matrix))
        ),
        anchor_rank=anchor.rank,
        minimum_separation=anchor.minimum_separation,
        maximum_anchor_norm=anchor.maximum_norm,
        correlation_rank=matrix.rank,
        minimum_correlation_eigenvalue=matrix.minimum_eigenvalue,
        calibration_n=2**result.config.calibration_power,
        validation_n=2**result.config.validation_power,
        calibration_seed=result.calibration_seed,
        validation_seed=result.validation_seed,
        calibration_sample_sha256=result.calibration_sample_sha256,
        validation_sample_sha256=result.validation_sample_sha256,
        selected_start=result.selected_start,
        n_starts=len(result.trials),
        elapsed_seconds=result.elapsed_seconds,
        valid=result.valid,
        status="VALIDATED" if result.valid else "NOT_VALIDATED",
        failures=";".join(result.failures),
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot export an empty table")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: format(value, ".17g") if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )


def export_scenarios(results: tuple[CalibratedScenario, ...], output: Path) -> None:
    if not results or len({r.scenario.scenario_id for r in results}) != len(results):
        raise ValueError("export requires nonempty, unique scenario configurations")
    if any(r.config != results[0].config for r in results):
        raise ValueError("all scenarios must use the same frozen configuration")
    if any(
        (output / name).exists()
        for name in (
            "synthetic_scenarios.csv",
            "synthetic_anchors.csv",
            "synthetic_correlations.csv",
            "calibration_diagnostics.csv",
            "synthetic_correlation_matrices.npz",
        )
    ):
        raise FileExistsError("scenario payloads already exist; choose a fresh output")
    output.mkdir(parents=True, exist_ok=True)
    scenarios: list[dict[str, object]] = []
    anchors: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    matrices: dict[str, FloatArray] = {}
    for result in results:
        cell = result.scenario
        key = cell.scenario_id
        scenarios.append(
            dict(
                scenario_id=key,
                nx=cell.nx,
                delta=cell.delta,
                m=cell.m,
                alpha=radius(cell.nx),
                rho_target=cell.rho_target,
                directions="MIN",
                anchor_configurations=1,
                valid=result.valid,
            )
        )
        for j, vector in enumerate(result.anchors, 1):
            for k, value in enumerate(vector, 1):
                anchors.append(dict(scenario_id=key, response=j, coordinate=k, value=float(value)))
        for trial in result.trials:
            diagnostics.append(
                dict(scenario_id=key, selected=trial.start == result.selected_start, **trial.row())
            )
        for name, matrix in (
            ("anchors", result.anchors),
            ("calibration", result.calibration_matrix),
            ("validation", result.validation_matrix),
            ("population", result.population_matrix),
        ):
            matrices[key + "__" + name] = matrix
    write_csv(output / "synthetic_scenarios.csv", scenarios)
    write_csv(output / "synthetic_anchors.csv", anchors)
    write_csv(output / "synthetic_correlations.csv", [correlation_row(r) for r in results])
    write_csv(output / "calibration_diagnostics.csv", diagnostics)
    np.savez_compressed(
        output / "synthetic_correlation_matrices.npz", allow_pickle=False, **matrices
    )
