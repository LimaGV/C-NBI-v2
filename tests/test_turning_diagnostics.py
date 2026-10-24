"""Reproducible applied diagnostics without changing data, design or terms."""

import csv
import json
from dataclasses import fields

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation.turning_diagnostics import run_diagnostics
from scripts.validation.turning_reference import (
    RAW,
    RAW_SHA256,
    RESPONSES,
    ROOT,
    design_cases,
    read_literal_values,
)

from cnbi_v2.data import sha256_file
from cnbi_v2.model import diagnose_rsm, fit_multivariate_rsm


@pytest.fixture(scope="module")
def applied_diagnostics(tmp_path_factory):
    output = tmp_path_factory.mktemp("turning_diagnostics")
    before, mtime = RAW.read_bytes(), RAW.stat().st_mtime_ns
    summary = run_diagnostics(output)
    assert RAW.read_bytes() == before
    assert RAW.stat().st_mtime_ns == mtime
    assert sha256_file(RAW) == RAW_SHA256
    return output, summary


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_applied_fits_preserve_every_response_and_existing_coefficients():
    values, _ = read_literal_values()
    for case, x in design_cases(values[:, 1:4]).items():
        fit = fit_multivariate_rsm(x, values[:, 4:])
        recorded = np.loadtxt(
            ROOT / "results/turning_8responses_validation" / case / "coefficients_raw_units.csv",
            delimiter=",", skiprows=1, usecols=range(1, 9),
        )
        assert_array_equal(fit.observed_responses, values[:, 4:])
        assert_array_equal(fit.experimental_factors, x)
        assert_allclose(fit.coefficients, recorded, rtol=2e-14, atol=1e-15)
        d = diagnose_rsm(fit, x, RESPONSES)
        assert fit.n_terms == fit.rank == 10
        assert d.replicate_groups == ((14, 15, 16, 17, 18),)
        assert len(d.factor_groups) == 15
        for response in d.responses:
            assert (response.model_df, response.error_df,
                    response.pure_error_df, response.lack_of_fit_df) == (9, 9, 4, 5)
            assert_allclose(response.sse, response.lack_of_fit_ss + response.pure_error_ss,
                            rtol=3e-13, atol=1e-20)


def test_primary_table_is_eight_physical_full_precision_models(applied_diagnostics):
    output, summary = applied_diagnostics
    rows = read_csv(output / "model_diagnostics.csv")
    assert len(rows) == 8
    assert [row["Response"] for row in rows] == list(RESPONSES)
    assert summary["primary_case"] == "physical_cells"
    assert_allclose(float(rows[2]["R2"]), 0.9773716805933569, rtol=1e-12)
    assert float(rows[2]["LOF_p"]) > 0.05
    assert all(float(row["Model_p"]) < 0.05 for row in rows)
    assert summary["physical_case_lof_p_below_alpha"] == [r for r in RESPONSES if r != "WR"]


def test_secondary_comparison_keeps_discrepancies_and_method_limit(applied_diagnostics):
    output, summary = applied_diagnostics
    rows = read_csv(output / "published_summary_comparison.csv")
    assert len(rows) == 4 * 8 * 4
    nominal = [r for r in rows if r["Case"] == "rotatable_alpha_hypothesis"]
    assert summary["publication_rounding_compatible_out_of_8"]["rotatable_alpha_hypothesis"] == {
        "S": 6, "R2": 7, "R2_adj": 7, "R2_pred": 5,
    }
    for row in nominal:
        if row["Metric"] == "R2_pred":
            assert row["Comparability_status"] == "PUBLISHED_R2_PRED_METHOD_UNSPECIFIED"
        if row["Response"] == "WR":
            assert row["Rounding_compatible"] == "False"
    ra_pred = next(r for r in nominal if r["Response"] == "Ra" and r["Metric"] == "R2_pred")
    assert float(ra_pred["Calculated_display"]) < 35
    assert ra_pred["Published_text"] == "75.95"
    assert summary["wr_rounding_status"].startswith("PUBLICATION_RECONCILIATION_NOTE")


def test_replicates_decomposition_and_provenance_artifacts(applied_diagnostics):
    output, summary = applied_diagnostics
    assert len(read_csv(output / "anova.csv")) == 4 * 8 * 3
    assert len(read_csv(output / "lack_of_fit.csv")) == 4 * 8
    assert len(read_csv(output / "press_residuals.csv")) == 4 * 19
    for case in summary["diagnostics_by_case"].values():
        assert case["replicate_run_ids"] == [[15, 16, 17, 18, 19]]
        assert case["unique_configurations"] == 15
        assert case["press_undefined_run_ids"] == []
        assert_allclose(case["leverage_sum"], 10, rtol=1e-14)
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["raw_before_sha256"] == manifest["raw_after_sha256"] == RAW_SHA256
    assert manifest["canonical_data_rounded"] is False
    assert manifest["wr_rounding_experiment_executed"] is False
    for name, expected in manifest["output_sha256"].items():
        assert sha256_file(output / name) == expected
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(output / name) == digest


def test_recorded_diagnostics_match_rerun_and_hashes(applied_diagnostics):
    output, _ = applied_diagnostics
    recorded = ROOT / "results/validation/turning_rsm"
    # Preserve original numerical artifacts; execution-state provenance is explicit.
    for name in ["model_diagnostics.csv", "all_cases_model_diagnostics.csv", "anova.csv",
                 "lack_of_fit.csv", "press_residuals.csv", "published_summary_comparison.csv"]:
        fresh, saved = read_csv(output / name), read_csv(recorded / name)
        assert len(fresh) == len(saved)
        for actual, expected in zip(fresh, saved, strict=True):
            assert actual.keys() == expected.keys()
            for column, value in actual.items():
                try:
                    numeric, previous = float(value), float(expected[column])
                except ValueError:
                    assert value == expected[column]
                else:
                    # Physical X is ill-conditioned (~1.1e7); this checks artifact
                    # reproducibility, not agreement with rounded publication values.
                    # Cancellation in the SSE partition has its own absolute bound.
                    atol = 3e-9 if column == "decomposition_error" else 1e-16
                    assert_allclose(numeric, previous, rtol=5e-7, atol=atol)
    for line in (recorded / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(recorded / name) == digest


def test_affine_reparameterization_preserves_diagnostics():
    values, _ = read_literal_values()
    cases = design_cases(values[:, 1:4])
    a, b = [diagnose_rsm(fit_multivariate_rsm(cases[c], values[:, 4:]), cases[c])
            for c in ["physical_cells", "affine_from_cells"]]
    for da, db in zip(a.responses, b.responses, strict=True):
        for field in fields(da):
            left, right = getattr(da, field.name), getattr(db, field.name)
            if isinstance(left, float):
                assert_allclose(left, right, rtol=2e-8)
            else:
                assert left == right
