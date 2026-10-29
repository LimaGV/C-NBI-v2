"""Independent integrity/recomposition checks for the Phase8 correction.

Timing repetitions are read as evidence, never rerun as part of CI. A tiny
upstream-only QA solve checks denied-parent access without a new campaign.
"""

import ast
import inspect
import json
import subprocess
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation import turning_cnbi_standalone as run
from scripts.validation import turning_standalone_analysis as analysis

from cnbi_v2.benchmark.metrics import gd_igd, spacing_sparsity
from cnbi_v2.benchmark.selection import farthest_order
from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import canonical_decision_points, nondominated_mask
from cnbi_v2.optimization import evaluate_responses
from cnbi_v2.simplex import simplex_lattice


@pytest.fixture(scope="module")
def archive():
    return run.OUTPUT, json.loads(run.POLICY.read_text()), analysis.load(run.OUTPUT / "H5_rep1.npz")


@pytest.mark.parametrize("h,count", [(2, 165), (4, 365), (5, 492), (10, 1397), (20, 4557)])
def test_standalone_mesh_counts_and_exact_compositions(h, count):
    _, _, _, _, _, _, _, catalog = run.frozen.verified_inputs()
    assert len(catalog) == 37
    assert sum(len(simplex_lattice(len(indices), h).weights) for _, indices in catalog) == count
    for k in (2, 3):
        mesh = simplex_lattice(k, h)
        assert np.all(mesh.compositions.sum(axis=1) == h)
        assert_array_equal(mesh.weights, mesh.compositions / h)
        assert len(set(map(tuple, mesh.compositions))) == len(mesh.weights)


def test_five_timing_runs_same_science_and_isolated_parent_files(archive):
    folder, policy, first = archive
    completion = json.loads((folder / "completion.json").read_text())
    assert completion["measured_runs"] == 9 and completion["H5_repetitions"] == 5
    assert completion["parent_artifacts_unavailable_during_every_solve"] is True
    assert completion["parent_artifacts_restored"] is True
    assert policy["repeat_atol"] == 1e-12 and policy["repeat_rtol"] == 0
    for i in range(1, 6):
        repeated = analysis.load(folder / f"H5_rep{i}.npz")
        for key in first:
            assert_array_equal(first[key], repeated[key])
    launch = json.loads((folder / "launch.json").read_text())
    assert launch["working_tree_dirty_at_launch"] is False
    assert launch["methods_sequential"] is True
    assert launch["hardware"]["external_active_python"] == []
    assert launch["EA_executions"] == launch["VRF_executions"] == 0
    # Historical execution source is verified at its actual commit, not against
    # a later formatting-only version of the same script.
    for name, digest in launch["input_sha256"].items():
        blob = subprocess.check_output(
            ["git", "show", f"{launch['git_commit']}:{name}"], cwd=run.ROOT
        )
        import hashlib

        assert hashlib.sha256(blob).hexdigest() == digest


def test_recomposition_acceptance_dedup_nd_and_own_runtime(archive):
    folder, policy, first = archive
    models, *_ = run.frozen.verified_inputs()
    reevaluated = np.array([evaluate_responses(models, point) for point in first["x"]])
    # Same canonical reevaluation bound as Phase7; platform BLAS/libm may differ
    # in the last bits. Archived timing repeats themselves remain bitwise equal.
    assert_allclose(reevaluated, first["natural_f"], atol=5e-14, rtol=2e-14)
    assert first["accepted"].shape == (492,) and first["accepted"].all()
    reps, _ = canonical_decision_points(first["x"], tolerance=policy["x_tolerance"])
    assert_array_equal(reps, first["unique_ids"])
    keep = nondominated_mask(first["z"][reps], equality_tolerance=policy["z_tolerance"])
    assert_array_equal(reps[keep], first["nd_ids"])
    assert len(reps) == 411 and keep.sum() == 409
    for r in analysis.numeric_rows(folder / "H5_rep1_records.csv"):
        assert r["eq_norm"] <= 1e-4 and r["sphere_margin"] >= -1e-9
        assert r["initial_start_kind"] and r["used_start_kind"]
        assert r["solve_seconds"] >= 0
    timing = analysis.numeric_rows(folder / "timing_cnbi.csv")
    for r in analysis.numeric_rows(folder / "standalone_resolution_metrics.csv"):
        own = next(t for t in timing if t["H"] == r["H"] and t["repetition"] == r["repetition"])
        assert r["T_total"] == own["T_total"] and r["T_solver"] == own["T_solver"]


def test_pipeline_uses_upstream_only_when_parent_access_is_denied(monkeypatch, archive):
    _, policy, _ = archive
    original = run.frozen.verified_inputs()
    # One actual six-weight QA subset; the full nine campaigns already exercised
    # filesystem-level absence of all Phase6/7 result directories.
    monkeypatch.setattr(run.frozen, "verified_inputs", lambda: (*original[:-1], original[-1][:1]))
    path_open = Path.open

    def guarded(path, *args, **kwargs):
        if any(p in str(path) for p in ("phase_06_local_nbi", "phase_07_reference_front")):
            raise AssertionError("official H5 tried to read a parent artifact")
        return path_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    values, stats, _, _ = run.execute(5, policy)
    assert stats["subproblems"] == 6 and values["accepted"].all()
    source = ast.parse(inspect.getsource(run.execute))
    assert not any(
        isinstance(n, ast.Attribute) and n.attr in ("PHASE6", "PHASE7") for n in ast.walk(source)
    )


def test_official_artifact_and_k66_use_new_h5(archive):
    folder, _, first = archive
    front = analysis.load(folder / "official_cnbi5.npz")
    assert_array_equal(front["x"], first["x"][first["nd_ids"]])
    assert len(front["x"]) == 409
    order = analysis.load(folder / "cnbi5_farthest_order.npz")
    assert_array_equal(order["local_order"], farthest_order(front["z"]))
    assert_array_equal(order["K66_source_rows"], first["nd_ids"][order["local_order"][:66]])
    ref = analysis.load(analysis.OLD / "reference_final.npz")
    assert len(ref["z"]) == 18503 and ref["point_ids"].max() < 19866
    for filename, selected in (
        ("native_metrics.csv", np.arange(409)),
        ("equalized_k66_metrics.csv", order["local_order"][:66]),
    ):
        row = next(
            r
            for r in analysis.numeric_rows(folder / filename)
            if r["method"] == "CNBI5" and r["label"] == analysis.LOO
        )
        assert_allclose(
            [row["GD"], row["IGD"]], gd_igd(front["z"][selected], ref["z"]), rtol=0, atol=0
        )
        assert_allclose(
            [row["Spacing"], row["Sparsity"]],
            spacing_sparsity(front["z"][selected]),
            rtol=0,
            atol=2e-14,
        )


def test_other_methods_and_reference_structure_unchanged(archive):
    folder, _, _ = archive
    for name in (
        "native_metrics.csv",
        "equalized_k66_metrics.csv",
        "cardinality_curve_metrics.csv",
    ):
        old = [r for r in analysis.numeric_rows(analysis.OLD / name) if r["method"] != "CNBI5"]
        new = [r for r in analysis.numeric_rows(folder / name) if r["method"] != "CNBI5"]
        for row in old:
            if row["label"] == "COMMON_REFERENCE_SELF_INCLUDED":
                row["label"] = analysis.COMMON
        assert old == new
    for name in (
        "reference_run_sensitivity_replicates.csv",
        "reference_composition_sensitivity.csv",
        "reference_cardinality_sensitivity.csv",
    ):
        old = analysis.numeric_rows(analysis.OLD / name)
        new = analysis.numeric_rows(folder / name)
        assert len(old) == len(new)
        for before, after in zip(old, new, strict=True):
            for key in before.keys() - {"GD_CNBI5", "IGD_CNBI5"}:
                assert before[key] == after[key]
    for filename in (folder / "checksums.sha256", analysis.OLD / "checksums.sha256"):
        for line in filename.read_text().splitlines():
            digest, name = line.split("  ")
            assert sha256_file(filename.parent / name) == digest
    assert sha256_file(analysis.OLD / "checksums.sha256") == (
        "c0e8ab1ccd8d4b8d42ca03dffec22afb86200d4dc371da5993276001bf3b3988"
    )


def test_historical_diagnostic_is_not_a_baseline_selector(archive):
    folder, _, _ = archive
    records = analysis.numeric_rows(folder / "parent_vs_standalone_all492.csv")
    assert len(records) == 492
    assert len(analysis.numeric_rows(folder / "historical_24_divergent_cases.csv")) == 24
    assert_allclose(max(r["x_Linf"] for r in records), 3.118120710729887, rtol=0, atol=1e-10)
    meta = json.loads((folder / "metadata.json").read_text())
    assert meta["baseline"] == "standalone H5 repetition1"
    assert meta["independent_reference_CNBI_points"] == 0
    assert meta["historical_common_target_label"] == analysis.COMMON
    assert meta["EA_runs_or_timing_repeated"] is False and meta["VRF_executions"] == 0
    for name, digest in meta["reused_input_sha256"].items():
        assert sha256_file(run.ROOT / name) == digest
