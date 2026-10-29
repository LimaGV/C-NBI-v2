import ast
import csv
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from numpy.testing import assert_array_equal

import cnbi_v2.synthetic.calibration as implementation
from cnbi_v2.synthetic import CalibrationConfig, Scenario, calibrate
from cnbi_v2.synthetic.correlation import summaries
from cnbi_v2.synthetic.serialization import correlation_row, export_scenarios, write_csv


def test_small_scenarios_are_certified_in_calibration_and_untouched_validation(small_results):
    for result in small_results:
        assert result.valid, result.failures
        assert not result.failures
        assert result.calibration_seed != result.validation_seed
        assert result.calibration_sample_sha256 != result.validation_sample_sha256
        for matrix in (result.calibration_matrix, result.validation_matrix):
            assert abs(summaries(matrix)[0] - result.scenario.rho_target) <= 0.05
        assert len(result.trials) == 2
        assert not result.anchors.flags.writeable
        assert any(t.solver_success for t in result.trials)
        assert result.elapsed_seconds > 0


def test_reproducible_and_cell_execution_order_invariant(small_results, small_config):
    reference = {r.scenario: r for r in small_results}
    for cell in reversed(tuple(reference)):
        repeated = calibrate(cell, small_config)
        expected = reference[cell]
        for field in ("anchors", "calibration_matrix", "validation_matrix", "population_matrix"):
            assert_array_equal(getattr(repeated, field), getattr(expected, field))
        assert repeated.selected_start == expected.selected_start
        assert repeated.calibration_sample_sha256 == expected.calibration_sample_sha256


def test_holdout_changes_and_precision_failure_cannot_select_other_anchors(
    small_results, small_config
):
    reference = small_results[0]
    result = calibrate(reference.scenario, replace(small_config, validation_power=13))
    assert_array_equal(result.anchors, reference.anchors)
    assert_array_equal(result.calibration_matrix, reference.calibration_matrix)
    assert result.validation_sample_sha256 != reference.validation_sample_sha256
    failed = calibrate(reference.scenario, replace(small_config, sampling_precision_budget=1e-16))
    assert not failed.valid and "VALIDATION_SAMPLING_PRECISION_FAILED" in failed.failures
    assert_array_equal(failed.anchors, reference.anchors)
    assert failed.selected_start == reference.selected_start
    assert len(failed.trials) == len(reference.trials)


def test_selection_reads_only_calibration_structure_convergence_and_index(small_results):
    assert (
        implementation.select_trial(small_results[0].trials).start
        == small_results[0].selected_start
    )
    with pytest.raises(ValueError):
        implementation.select_trial(())
    tree = ast.parse(Path(implementation.__file__).read_text(encoding="utf-8"))
    selector = next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "select_trial"
    )
    attributes = {n.attr for n in ast.walk(selector) if isinstance(n, ast.Attribute)}
    assert attributes <= {"solver_success", "structurally_valid", "calibration_error", "start"}
    assert "rho_signed" not in implementation.CalibrationTrial.__dataclass_fields__


def test_failed_solver_keeps_best_configuration_and_does_not_fabricate_success(
    monkeypatch, small_config, tmp_path
):
    def failure(*args, **kwargs):
        raise ValueError("intentional solver failure")

    monkeypatch.setattr(implementation, "minimize", failure)
    result = calibrate(Scenario(2, 1, 0.6), small_config)
    assert not result.valid and "NO_CONVERGED_CALIBRATION_TRIAL" in result.failures
    assert all(t.solver_status == -1 and not t.solver_success for t in result.trials)
    assert np.isfinite(result.anchors).all()
    export_scenarios((result,), tmp_path)
    with (tmp_path / "synthetic_correlations.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["status"] == "NOT_VALIDATED" and rows[0]["valid"] == "False"


def test_nonfinite_solver_output_and_iteration_limit_are_reported(monkeypatch, small_config):
    def bad_output(fun, x, **kwargs):
        return SimpleNamespace(
            x=np.full_like(x, np.nan),
            success=False,
            status=-3,
            message="nonfinite solver output",
            nit=1,
            nfev=1,
            njev=1,
        )

    monkeypatch.setattr(implementation, "minimize", bad_output)
    result = calibrate(Scenario(2, 1, 0.6), small_config)
    assert not result.valid
    assert np.isinf(result.trials[0].final_solver_error)
    assert np.isfinite(result.anchors).all()


def test_one_configuration_per_cell_and_float64_export_roundtrip(small_results, tmp_path):
    export_scenarios(small_results, tmp_path)
    with (tmp_path / "synthetic_anchors.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with np.load(tmp_path / "synthetic_correlation_matrices.npz", allow_pickle=False) as archive:
        for result in small_results:
            key = result.scenario.scenario_id
            assert_array_equal(archive[key + "__anchors"], result.anchors)
            assert_array_equal(archive[key + "__validation"], result.validation_matrix)
            selected = [r for r in rows if r["scenario_id"] == key]
            recovered = np.array([float(r["value"]) for r in selected]).reshape(
                result.anchors.shape
            )
            assert_array_equal(recovered, result.anchors)
            row = correlation_row(result)
            assert row["anchor_rank"] == result.scenario.nx
            assert row["correlation_rank"] <= result.scenario.nx + 1
    with pytest.raises(FileExistsError):
        export_scenarios(small_results, tmp_path)
    with pytest.raises(ValueError):
        export_scenarios((small_results[0], small_results[0]), tmp_path / "duplicates")
    with pytest.raises(ValueError):
        export_scenarios((), tmp_path / "empty")
    with pytest.raises(ValueError):
        write_csv(tmp_path / "empty.csv", [])
    inconsistent = replace(small_results[1], config=replace(small_results[1].config, maxiter=2))
    with pytest.raises(ValueError):
        export_scenarios((small_results[0], inconsistent), tmp_path / "inconsistent")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"master_seed": True},
        {"n_starts": 0},
        {"maxiter": 0},
        {"calibration_power": 3},
        {"validation_power": 25},
        {"ftol": np.nan},
        {"ftol": 0},
        {"acceptance_tolerance": 0.051},
        {"acceptance_tolerance": 0},
        {"sampling_precision_budget": 0.03},
        {"matrix_tolerance": 0.1},
        {"separation_ratio": 1},
        {"rank_rtol": 1},
    ],
)
def test_invalid_calibration_configuration_cannot_relax_acceptance(kwargs):
    with pytest.raises(ValueError):
        CalibrationConfig(**kwargs)


def test_diagnostics_have_exactly_four_types_and_no_coordinate_grids(small_results):
    from scripts.validation.synthetic_diagnostics import figures

    plots = figures(small_results)
    assert set(plots) == {
        "target_vs_realized",
        "calibration_errors",
        "signed_correlation_distribution",
        "representative_correlation_matrices",
    }
    for fig in plots.values():
        assert all(
            not line.get_visible()
            for ax in fig.axes
            for line in (*ax.get_xgridlines(), *ax.get_ygridlines())
        )
        assert all(not c.get_rasterized() for ax in fig.axes for c in ax.collections)
        fig.clear()


def test_new_modules_never_import_or_execute_frozen_scientific_pipelines():
    root = Path(__file__).resolve().parents[2]
    paths = [
        *(root / "src/cnbi_v2/synthetic").glob("*.py"),
        root / "scripts/validation/generate_synthetic_scenarios.py",
        root / "scripts/validation/synthetic_diagnostics.py",
    ]
    forbidden = {
        "fit_multivariate_rsm",
        "solve_nbi_lattice",
        "run_evolutionary",
        "gd_igd",
        "spacing_sparsity",
        "sample_coefficient_ensemble",
        "solve_quadratic_ball",
    }
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = (
                    node.func.id
                    if isinstance(node.func, ast.Name)
                    else getattr(node.func, "attr", "")
                )
                assert name not in forbidden, (path, name)
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(
                    (
                        "cnbi_v2.model",
                        "cnbi_v2.nbi",
                        "cnbi_v2.chim",
                        "cnbi_v2.reference",
                        "cnbi_v2.benchmark",
                        "cnbi_v2.optimization",
                    )
                )
