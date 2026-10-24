"""Real full-precision inputs, explicit hypotheses and honest partial reproduction."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation.turning_reference import (
    HEADERS,
    PROCESSED,
    RAW,
    RAW_SHA256,
    RESPONSES,
    design_cases,
    read_literal_values,
    rounding_comparison,
    run_validation,
    wr_rounding_diagnostic,
)

from cnbi_v2.data import sha256_file
from cnbi_v2.model import fit_multivariate_rsm


@pytest.fixture(scope="module")
def actual_run(tmp_path_factory):
    directory = tmp_path_factory.mktemp("real_turning")
    before, mtime = RAW.read_bytes(), RAW.stat().st_mtime_ns
    summary = run_validation(directory / "results", directory / "literal.csv", True)
    assert RAW.read_bytes() == before
    assert RAW.stat().st_mtime_ns == mtime
    return directory, summary


def test_literal_revision_is_19_by_11_without_rounding():
    values, lexemes = read_literal_values()
    assert values[:, 1:].shape == (19, 11)
    assert values[:, 4:].shape == (19, 8)
    assert_array_equal(values[:, 0], np.arange(1, 20))
    assert lexemes[0][5] == "68.306215222565058"
    assert lexemes[0][6] == "4.4924127802190104E-3"
    assert sha256_file(RAW) == RAW_SHA256
    with PROCESSED.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream)
        assert tuple(next(reader)) == HEADERS
        assert list(reader) == lexemes


def test_wrong_revision_is_rejected(tmp_path):
    wrong = tmp_path / "different.xlsx"
    wrong.write_bytes(b"not the verified revision")
    with pytest.raises(ValueError, match="Unexpected CCD revision hash"):
        read_literal_values(wrong)


def test_actual_multivariate_fit_matches_eight_separate_full_precision_fits():
    values, _ = read_literal_values()
    original = values.copy()
    cases = design_cases(values[:, 1:4])
    assert_array_equal(cases["physical_cells"], values[:, 1:4])
    coded = cases["rotatable_alpha_hypothesis"]
    assert_allclose(coded[8, 0], -(8**0.25), rtol=0, atol=0)
    result = fit_multivariate_rsm(coded, values[:, 4:])
    assert (result.rank, result.residual_degrees_of_freedom) == (10, 9)
    assert result.coefficients.shape == (10, 8)
    assert_array_equal(np.diag(result.residual_covariance), result.mse_by_response)
    for j in range(8):
        separate = fit_multivariate_rsm(coded, values[:, 4 + j])
        assert_allclose(
            result.coefficients[:, j], separate.coefficients[:, 0], rtol=1e-12, atol=2e-13
        )
    assert_array_equal(values, original)
    # Observed physical axial spacing is not exactly the nominal Table 6 CCD.
    assert not np.allclose(cases["affine_from_cells"], coded, rtol=0, atol=0.001)


def test_real_coefficient_comparison_is_partial_not_80_of_80(actual_run):
    _, summary = actual_run
    ideal = summary["cases"]["rotatable_alpha_hypothesis"]["comparisons"]
    assert ideal["table3_footnote_1e-2"]["matched_total"] == 50
    diagnostic = ideal["diagnostic_1e-3_NOT_FOOTNOTE"]
    assert diagnostic["matched_total"] == 70
    assert diagnostic["matched_by_response"] == dict.fromkeys(RESPONSES, 10) | {"WR": 0}
    assert summary["full_80_coefficient_reproduction"] is False
    assert summary["wr_rounding_diagnostic_matches_excluded_from_totals"] == 10


def test_all_80_coefficients_are_compared_for_every_explicit_case(actual_run):
    directory, _ = actual_run
    with (directory / "results/all_80_coefficient_comparisons.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 4 * 2 * 80
    keys = {(r["design_case"], r["scaling_case"], r["coefficient"], r["response"]) for r in rows}
    assert len(keys) == len(rows)
    assert all(r["published_exact_text"] for r in rows)
    assert all(float(r["rounding_half_width"]) == 0.0005 for r in rows)
    assert all(float(r["numerical_allowance"]) < 1e-9 for r in rows)


def test_real_fit_outputs_keep_original_response_units(actual_run):
    directory, _ = actual_run
    folder = directory / "results/rotatable_alpha_hypothesis"
    with (folder / "coefficients_raw_units.csv").open() as stream:
        coefficients = list(csv.DictReader(stream))
    assert_allclose(float(coefficients[0]["ROI"]), 0.202514385993, rtol=0, atol=1e-12)
    assert_allclose(float(coefficients[0]["WR"]), 0.006643905899, rtol=0, atol=1e-12)
    assert float(coefficients[7]["WR"]) > 0  # published beta12=-0.250 has opposite sign
    for name in ["fitted_values.csv", "residuals.csv", "factors_used.csv"]:
        with (folder / name).open() as stream:
            assert len(list(csv.DictReader(stream))) == 19


def test_lossy_wr_diagnostic_does_not_change_real_data_or_validation():
    values, _ = read_literal_values()
    before = values.copy()
    result = wr_rounding_diagnostic(values)
    assert result["matches"] == 10
    assert result["changed_values_in_hypothetical_copy"] == 19
    assert result["original_observations_modified"] is False
    assert result["used_in_main_fits_or_match_totals"] is False
    assert result["status"] == "POST_HOC_DIAGNOSTIC_ONLY_NOT_FULL_PRECISION_VALIDATION"
    assert_array_equal(values, before)


@pytest.mark.parametrize(
    "calculated, printed, expected",
    [
        (0.0025, "0.003", True),
        (0.0035000001, "0.003", False),
        (0.0005, "0.000", True),
        (0.00051, "0.000", False),
        (6.7854, "6.785", True),
        (6.7856, "6.785", False),
    ],
)
def test_printed_rounding_intervals_do_not_expand_to_fit_data(calculated, printed, expected):
    half_width, numerical, matches = rounding_comparison(calculated, printed)
    assert half_width == 0.0005
    assert numerical < 1e-12
    assert matches is expected


def test_run_manifest_and_every_artifact_checksum(actual_run):
    directory, _ = actual_run
    output = directory / "results"
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["raw_unchanged"]
    assert not manifest["responses_changed_or_rounded"]
    assert not manifest["display_scaling_applied_to_Y"]
    assert not manifest["full_80_coefficient_reproduction"]
    assert len(manifest["git_execution_commit"]) == 40
    for name, digest in manifest["artifact_hashes"].items():
        assert sha256_file(output / name) == digest
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        assert sha256_file(output / name) == digest
    recorded = Path("results/turning_8responses_validation")
    recorded_manifest = json.loads((recorded / "manifest.json").read_text())
    assert recorded_manifest["working_tree_dirty_at_start"] is False
    assert recorded_manifest["raw_unchanged"] is True
    for line in (recorded / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        assert sha256_file(recorded / name) == digest


def test_new_and_historical_raw_are_separate_immutable_files():
    historical = Path("data/raw/turning_application/CCD_original.xlsx")
    assert (
        sha256_file(historical)
        == "fd9c463efdcd62ff3d7eaa7eec18d9e112543675c30b1f36838beeb38deebf4a"
    )
    assert RAW.name != historical.name
    assert sha256_file(RAW) == RAW_SHA256
    manifest = Path("data/metadata/turning_application/values_20261023/checksums.sha256")
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        assert sha256_file(Path(relative)) == digest
