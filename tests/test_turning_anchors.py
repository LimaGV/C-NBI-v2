"""Real-data join, distinct original coding and independently certified payoffs."""

import csv
import json

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation.turning_anchors import (
    ALPHA,
    CODES,
    CODING_METADATA,
    DIRECTIONS,
    load_original_coded_case,
    run_anchors,
)
from scripts.validation.turning_reference import RAW, RAW_SHA256, RESPONSES

from cnbi_v2.data import sha256_file
from cnbi_v2.model import fit_multivariate_rsm
from cnbi_v2.optimization import (
    Direction,
    evaluate_responses,
    legacy_chi_square_threshold,
    quadratic_responses,
    response_cloud_region,
    solve_quadratic_ball,
)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_original_coding_matches_each_id_and_physical_input_without_invented_inverse():
    values, factors, metadata = load_original_coded_case()
    assert metadata["physical_coded_fitted_equivalence_gate"] == "FAILED"
    assert metadata["continuous_physical_coded_transform"] is None
    assert metadata["source_range"] == "B4:H22"
    assert sha256_file(CODES) == metadata["extracted_csv_sha256"]
    assert factors.shape == (19, 3)
    assert_array_equal(factors[14:], np.zeros((5, 3)))
    assert_array_equal(factors[8:14],
                       [[-1.682, 0, 0], [1.682, 0, 0], [0, -1.682, 0],
                        [0, 1.682, 0], [0, 0, -1.682], [0, 0, 1.682]])
    physical = fit_multivariate_rsm(values[:, 1:4], values[:, 4:])
    coded = fit_multivariate_rsm(factors, values[:, 4:])
    differences = np.max(np.abs(physical.fitted_values - coded.fitted_values), axis=0)
    assert_allclose(differences,
                    list(metadata["maximum_fitted_difference_by_response"].values()), rtol=1e-8)
    assert max(differences / np.ptp(values[:, 4:], axis=0)) > .02
    assert_allclose(ALPHA, 8**.25, rtol=0, atol=0)
    assert ALPHA < np.sqrt(3) < np.linalg.norm(factors[8]) + .1
    assert DIRECTIONS == (Direction.MAX, Direction.MAX, Direction.MIN, Direction.MIN,
                          Direction.MIN, Direction.MIN, Direction.MAX, Direction.MAX)


def test_eight_classical_anchors_have_valid_global_kkt_certificates_and_RC_membership():
    values, factors, _ = load_original_coded_case()
    fit = fit_multivariate_rsm(factors, values[:, 4:])
    models = quadratic_responses(fit)
    region = response_cloud_region(values[:, 4:])
    cutoff = legacy_chi_square_threshold(8)
    assert region.rank == 8
    assert_allclose(region.condition_number, 2.171049038e9, rtol=2e-6)
    for model, direction in zip(models, DIRECTIONS, strict=True):
        anchor = solve_quadratic_ball(model, ALPHA, direction)
        assert anchor.converged
        assert anchor.sphere_margin >= -1e-12
        assert anchor.normalized_stationarity < 1e-13
        assert anchor.normalized_complementarity < 1e-13
        assert anchor.normalized_shifted_min_eigenvalue >= -1e-14
        assert region.distance_squared(evaluate_responses(models, anchor.point)) < cutoff
    assert_allclose(region.distances_squared(values[:, 4:]).sum(), 8 * 18, rtol=1e-12)
    assert_array_equal(fit.observed_responses, values[:, 4:])


@pytest.fixture(scope="module")
def actual_anchors(tmp_path_factory):
    output = tmp_path_factory.mktemp("phase02_original_coded")
    before, mtime = RAW.read_bytes(), RAW.stat().st_mtime_ns
    summary = run_anchors(output, run_id="turning_original_codes_test", sensitivity=True)
    assert RAW.read_bytes() == before
    assert RAW.stat().st_mtime_ns == mtime
    assert sha256_file(RAW) == RAW_SHA256
    return output, summary


def test_real_anchors_both_payoffs_and_full_cutoff_sensitivity_are_recorded(actual_anchors):
    output, summary = actual_anchors
    assert summary["classical_outside"] == summary["number_moved"] == 0
    assert summary["unaffected_responses"] == list(RESPONSES)
    assert summary["maximum_displacement"] == 0
    assert summary["maximum_relative_deterioration"] == 0
    assert summary["utopia_inside_response_region"] is False
    assert summary["utopia_sphere_D2"] > 70000
    sphere = read_csv(output / "anchors_sphere.csv")
    rc = read_csv(output / "anchors_response_region.csv")
    assert len(sphere) == len(rc) == 8
    assert ((output / "payoff_sphere.csv").read_bytes()
            == (output / "payoff_response_region.csv").read_bytes())
    payoff = read_csv(output / "payoff_sphere.csv")
    assert [row["response"] for row in payoff] == list(RESPONSES)
    for j, (a, b) in enumerate(zip(sphere, rc, strict=True)):
        assert a["objective"] == b["objective"] == payoff[j][RESPONSES[j]]
        assert b["global_certified"] == "True"
        assert a["physical_Vc"] == b["physical_Vc"] == ""
        assert a["physical_f"] == b["physical_f"] == ""
        assert a["physical_ap"] == b["physical_ap"] == ""
    sensitivity = read_csv(output / "cutoff_sensitivity.csv")
    assert len(sensitivity) == 16
    assert all(float(row["displacement"]) == 0 for row in sensitivity)
    coverage = read_csv(output / "cutoff_coverage.csv")
    assert [int(row["n_inside"]) for row in coverage] == [19, 18, 19]
    assert [int(row["n_outside"]) for row in coverage] == [0, 1, 0]
    utopia = json.loads((output / "utopia_diagnostic.json").read_text())
    assert utopia["sphere"] == utopia["response_region"]
    assert utopia["anchor_membership_does_not_imply_diagonal_membership"] is True


def test_real_region_provenance_hashes_and_recorded_starts(actual_anchors):
    output, _ = actual_anchors
    region = json.loads((output / "response_region.json").read_text())
    assert region["experimental_inside"] == 19
    assert region["experimental_outside"] == 0
    assert region["statistical_status"] == "EXPERIMENTAL_NOT_EXACT_CONFIDENCE"
    assert_allclose(region["distance_sum"], 144, rtol=1e-12)
    metadata = json.loads((output / "metadata.json").read_text())
    assert metadata["dataset_sha256"] == metadata["raw_after_sha256"] == RAW_SHA256
    assert metadata["observed_responses_modified"] is False
    source_metadata = json.loads(CODING_METADATA.read_text())
    assert metadata["coding"]["source_sha256"] == source_metadata["source_sha256"]
    assert metadata["rc_options"]["response_tolerance"] == 1e-8
    diagnostics = json.loads((output / "solver_diagnostics.json").read_text())
    assert len(diagnostics["proposed_starts"]) == 80
    assert len(diagnostics["sphere"]) == len(diagnostics["response_region"]) == 8
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(output / name) == digest


def test_invalid_run_id_rejected_before_output(tmp_path):
    with pytest.raises(ValueError, match="run_id"):
        run_anchors(tmp_path, run_id="../escape")
    (tmp_path / "preserved.txt").write_text("prior result")
    with pytest.raises(FileExistsError, match="already exists"):
        run_anchors(tmp_path, run_id="existing_result")
    assert (tmp_path / "preserved.txt").read_text() == "prior result"
