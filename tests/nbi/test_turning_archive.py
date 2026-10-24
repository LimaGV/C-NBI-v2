"""Independent checks of the single real parent archive; do not re-solve it."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation import turning_local_nbi as workflow

from cnbi_v2.data import sha256_file

ARCHIVE = Path(__file__).resolve().parents[2] / "results/phase_06_local_nbi" / workflow.RUN_ID


@pytest.fixture(scope="module")
def real_case():
    metadata = json.loads((ARCHIVE / "metadata.json").read_text())
    with np.load(ARCHIVE / "local_nbi_solutions_H20.npz", allow_pickle=False) as stored:
        arrays = {name: stored[name] for name in stored.files}
    return metadata, arrays


def rows(name):
    with (ARCHIVE / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_hashes_shapes_failure_masks_and_frozen_nominal_evaluations(real_case):
    metadata, data = real_case
    assert metadata["git_commit"] == "d8d3de5f89efcca9d3c52eeac5a2d1d57dac09af"
    assert metadata["git_working_tree_dirty"] is False
    assert data["x"].shape == (4557, 3)
    assert data["accepted"].dtype == np.bool_
    assert data["H_membership"].shape == (4557, 5)
    assert int(data["accepted"].sum()) == metadata["accepted"]
    assert int((~data["accepted"]).sum()) == metadata["failed"]
    assert np.isnan(data["x"][~data["accepted"]]).all()
    for key in [
        "new_PA",
        "anchors_reoptimized",
        "RC_applied",
        "external_benchmarks",
        "parallelism",
    ]:
        assert metadata[key] is False
    assert metadata["new_random_draws"] == 0 and metadata["final_H_accepted"] is None
    for line in (ARCHIVE / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(ARCHIVE / name) == digest
    for name, digest in metadata["input_sha256"].items():
        assert sha256_file(workflow.ROOT / name) == digest
    coefficients = np.array(
        [
            [float(r[name]) for name in workflow.RESPONSES]
            for r in workflow.read_rows(workflow.MODELS)
        ]
    )
    x = data["x"][data["accepted"]]
    # Independent full quadratic matrix evaluation; no fit or optimizer.
    design = np.column_stack(
        [np.ones(len(x)), x, x * x, x[:, 0] * x[:, 1], x[:, 0] * x[:, 2], x[:, 1] * x[:, 2]]
    )
    assert_allclose(
        data["natural_responses"][data["accepted"]], design @ coefficients, atol=5e-14, rtol=2e-14
    )
    _, _, _, utopia, amplitude, signs, _, _ = workflow.verified_inputs()
    assert_array_equal(
        data["oriented_responses"][data["accepted"]],
        data["natural_responses"][data["accepted"]] * signs,
    )
    assert_array_equal(
        data["normalized_responses"][data["accepted"]],
        (data["oriented_responses"][data["accepted"]] - utopia) / amplitude,
    )


def test_all_accepted_ray_residuals_sphere_margins_and_local_normal_geometry(real_case):
    metadata, data = real_case
    records = rows("local_nbi_records.csv")
    geometries = json.loads((ARCHIVE / "local_geometry.json").read_text())
    signs = np.array([d.minimization_sign for d in workflow.DIRECTIONS])
    for j, geometry in enumerate(geometries):
        indices = geometry["indices"]
        k = len(indices)
        parent = np.flatnonzero((data["subset_indices"] == j) & data["accepted"])
        beta = data["integer_compositions"][parent, :k] / 20
        vertex = np.array(geometry["vertices"])
        normal = np.array(geometry["normal"])
        centered = vertex - vertex.mean(axis=1, keepdims=True)
        assert_allclose(centered.T @ normal, 0, atol=5e-15)
        assert_allclose(np.linalg.norm(normal), 1, atol=1e-15)
        assert normal @ vertex.mean(axis=1) < 0
        local_values = (
            data["natural_responses"][parent][:, indices] * signs[indices]
            - np.array(geometry["utopia"])
        ) / np.array(geometry["amplitudes"])
        residuals = local_values - beta @ vertex.T - data["t"][parent, None] * normal
        independent_eq = np.linalg.norm(residuals, axis=1)
        assert independent_eq.max() <= metadata["solver_options"]["equality_tolerance"]
        saved_eq = np.array([float(records[int(idx)]["eq_norm"]) for idx in parent])
        assert_allclose(saved_eq, independent_eq, atol=3e-15, rtol=0)
    valid = data["accepted"]
    margins = metadata["alpha"] ** 2 - np.sum(data["x"][valid] ** 2, axis=1)
    assert margins.min() >= -metadata["solver_options"]["sphere_tolerance"]
    assert_allclose(
        [float(r["sphere_margin"]) for r in records if r["accepted"] == "True"],
        margins,
        atol=1e-15,
        rtol=0,
    )
    attempts = rows("solver_attempts.csv")
    assert len(attempts) == metadata["total_solver_attempts"]
    assert sum(r["accepted"] == "True" for r in attempts) == metadata["accepted"]
    for row in records:
        selected = [r for r in attempts if r["solution_id"] == row["solution_id"]]
        assert len(selected) == int(row["attempt_count"])
        assert selected[-1]["accepted"] == row["accepted"]


def test_exact_h_membership_and_every_provenance_origin(real_case):
    metadata, data = real_case
    provenance = rows("provenance.csv")
    summaries = rows("h_sensitivity.csv")
    assert_array_equal(data["H_values"], [2, 4, 5, 10, 20])
    for column, h in enumerate(data["H_values"]):
        exact = np.all(data["integer_compositions"] % (20 // h) == 0, axis=1)
        assert_array_equal(data["H_membership"][:, column], exact)
        assert int(exact.sum()) == metadata["theoretical_counts"][str(h)]
        current = [r for r in provenance if int(r["H"]) == h]
        assert {int(r["solution_id"]) for r in current} == set(
            np.flatnonzero(exact & data["accepted"])
        )
        for row in current:
            idx, canonical = int(row["solution_id"]), int(row["canonical_solution_id"])
            assert exact[canonical] and data["accepted"][canonical]
            assert (
                np.max(np.abs(data["x"][idx] - data["x"][canonical]))
                <= metadata["deduplication_tolerance_x_Linf"]
            )
            subset = data["subset_indices"][idx]
            k = len(metadata["subset_ids"][subset].split("_")) - 1
            assert_array_equal(
                json.loads(row["integer_composition_at_H"]),
                data["integer_compositions"][idx, :k] // (20 // h),
            )
            assert_array_equal(json.loads(row["beta"]), data["integer_compositions"][idx, :k] / 20)
        summary = summaries[column]
        assert len(current) == int(summary["accepted_subproblems"])
        assert len({r["canonical_solution_id"] for r in current}) == int(
            summary["unique_decision_points"]
        )


def test_full_space_nd_and_both_coverage_directions_independently(real_case):
    metadata, data = real_case
    provenance = rows("provenance.csv")
    distances = rows("h_coverage_distances.csv")
    summaries = rows("h_sensitivity.csv")
    tolerance = np.array(metadata["dominance_coordinate_equality_tolerance"])
    nd_sets = {}
    for h in [2, 4, 5, 10, 20]:
        current = [r for r in provenance if int(r["H"]) == h]
        canonical = np.array(sorted({int(r["canonical_solution_id"]) for r in current}))
        z = data["normalized_responses"][canonical]
        independently_kept = []
        for start in range(0, len(z), 128):
            difference = z[None, :, :] - z[start : start + 128, None, :]
            equal = np.abs(difference) <= tolerance
            no_worse = ((difference < 0) | equal).all(axis=2)
            strictly_better = ((difference < 0) & ~equal).any(axis=2)
            independently_kept.extend((~(no_worse & strictly_better).any(axis=1)).tolist())
        nd = canonical[np.array(independently_kept)]
        archived_nd = {
            int(r["canonical_solution_id"])
            for r in current
            if r["canonical_point_nondominated"] == "True"
        }
        assert set(nd) == archived_nd
        assert len(nd) == int(
            next(r for r in summaries if int(r["H"]) == h)["full_space_nd_points"]
        )
        nd_sets[h] = nd
    for h in [2, 4, 5, 10, 20]:
        for direction, source, target in [
            ("ND20_TO_NDH", nd_sets[20], nd_sets[h]),
            ("NDH_TO_ND20", nd_sets[h], nd_sets[20]),
        ]:
            expected = {}
            for start in range(0, len(source), 128):
                ids = source[start : start + 128]
                delta = (
                    data["normalized_responses"][ids, None, :]
                    - data["normalized_responses"][target][None, :, :]
                )
                values = np.sqrt(np.sum(delta * delta, axis=2)).min(axis=1)
                expected.update(zip(map(int, ids), values, strict=True))
            actual = [r for r in distances if int(r["H"]) == h and r["direction"] == direction]
            assert {int(r["source_solution_id"]) for r in actual} == set(expected)
            assert_allclose(
                [float(r["nearest_distance"]) for r in actual],
                [expected[int(r["source_solution_id"])] for r in actual],
                atol=2e-16,
                rtol=1e-14,
            )
