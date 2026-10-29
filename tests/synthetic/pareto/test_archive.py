"""Frozen analytical references,independent proofs and lossless future loading."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from PIL import Image
from scipy.spatial import cKDTree

from cnbi_v2.synthetic.domain import radius
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.pareto.geometry import seed_for
from cnbi_v2.synthetic.pareto.reference import certify_reference
from cnbi_v2.synthetic.pareto.serialization import (
    array_sha256,
    load_evaluation_context,
    load_reference,
    load_true_anchors,
    verify_checksums,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "results/phase_10_synthetic_pareto/analytical_20261029"
SOURCE = ROOT / "results/phase_10_synthetic_generation/structural_20261029"


def read(name):
    with (OUTPUT / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_complete27_primary_references135000_and_no_method_data():
    meta = json.loads((OUTPUT / "generation_manifest.json").read_text(encoding="utf-8"))
    assert meta["status"] == "COMPLETE" and not meta["failures"]
    assert meta["official_run"] and not meta["working_tree_dirty_at_start"]
    assert meta["scenarios"] == 27 and meta["primary_points_per_scenario"] == 5000
    assert meta["primary_points_total"] == 135000 and meta["reverse_order_reproduced"] == 27
    assert meta["references_per_scenario"] == 1 and meta["shared_by_all_five_replicas"]
    assert not meta["multiobjective_methods_executed"]
    assert not meta["new_CCD_noise_RSM_generated"] and not meta["equalization_executed"]
    policy = json.loads((OUTPUT / "reference_sampling_config.json").read_text(encoding="utf-8"))
    assert policy == json.loads(
        (ROOT / "docs/policies/synthetic_pareto_reference_10c.json").read_text(encoding="utf-8")
    )
    rows = read("pareto_reference_index.csv")
    assert (
        len(rows) == 81
        and sum(int(r["n_reference"]) for r in rows if r["primary"] == "True") == 135000
    )
    assert all(
        r["source"] == "Phase10A frozen anchors only" and r["shared_replicas"] == "1;2;3;4;5"
        for r in rows
    )
    assert len(read("pareto_sampling_diagnostics.csv")) == 135
    assert len(read("pareto_geometry_certificates.csv")) == 27


def test_all27_convex_membership_direct_functions_extremes_and_nested_sensitivity():
    cases = load_true_anchors(SOURCE)
    index = {
        (r["scenario_id"], int(r["n_reference"])): r for r in read("pareto_reference_index.csv")
    }
    with (
        np.load(OUTPUT / "pareto_reference_decisions.npz", allow_pickle=False) as decisions,
        np.load(OUTPUT / "pareto_reference_objectives.npz", allow_pickle=False) as objectives,
        np.load(OUTPUT / "pareto_reference_normalized.npz", allow_pickle=False) as normalized,
        np.load(OUTPUT / "pareto_reference_nested.npz", allow_pickle=False) as nested,
        np.load(OUTPUT / "pareto_candidates.npz", allow_pickle=False) as candidates,
    ):
        expected = {c.scenario_id for c, _ in cases}
        assert set(decisions.files) == set(objectives.files) == set(normalized.files) == expected
        for cell, a in cases:
            sid = cell.scenario_id
            x, z, t = decisions[sid], objectives[sid], normalized[sid]
            assert x.shape == (5000, cell.nx) and z.shape == t.shape == (5000, cell.m)
            assert x.dtype == z.dtype == t.dtype == np.float64
            assert_array_equal(x[: cell.m], a)
            assert_array_equal(np.diag(z[: cell.m]), np.zeros(cell.m))
            assert_allclose(z, evaluate(x, a), atol=1e-14, rtol=5e-15)
            nadir = evaluate(a, a).max(axis=0)
            assert np.all(nadir > 0)
            assert_allclose(t, z / nadir, atol=0, rtol=2e-15)
            assert_array_equal(t.max(axis=0), np.ones(cell.m))
            assert np.all(t >= 0) and np.all(t <= 1 + 1e-14)
            dense_x = np.vstack((x, nested[sid + "__decisions_extension"]))
            dense_z = np.vstack((z, nested[sid + "__objectives_extension"]))
            dense_t = np.vstack((t, nested[sid + "__normalized_extension"]))
            w = nested[sid + "__weights"]
            assert w.shape == (10000, cell.m) and np.all(w >= 0)
            assert_allclose(w.sum(axis=1), 1, atol=8e-16, rtol=0)
            assert_allclose(w @ a, dense_x, atol=1e-14, rtol=1e-14)
            assert np.all(np.linalg.norm(dense_x, axis=1) <= radius(cell.nx))
            assert cKDTree(dense_x).query(dense_x, k=2, eps=0, workers=1)[0][
                :, 1
            ].min() > 1e-12 * radius(cell.nx)
            # Recheck the mathematical witness using this platform's direct
            # oracle;stored response bytes are separately hashed and compared.
            certificate = certify_reference(cell, a, dense_x, w, evaluate(dense_x, a))
            assert certificate["analytic_pareto_membership"]
            # Independent scalarized-gap identity certifies unique minima,including
            # all zero-weight individual extrema,without arbitrary ND filtering.
            ids = np.arange(0, 10000, 397)
            other = (ids + 1) % 10000
            gap = np.sum(w[ids] * (dense_z[other] - dense_z[ids]), axis=1)
            assert_allclose(
                gap, np.sum((dense_x[other] - dense_x[ids]) ** 2, axis=1), atol=2e-13, rtol=2e-13
            )
            assert np.all(gap > 0)
            source_ids = candidates[sid + "__original_ids"]
            positions = np.searchsorted(source_ids, nested[sid + "__candidate_ids"])
            assert_array_equal(candidates[sid + "__weights"][positions], w)
            for n in (2500, 5000, 10000):
                row = index[(sid, n)]
                assert array_sha256(dense_x[:n]) == row["reference_decisions_sha256"]
                assert array_sha256(dense_z[:n]) == row["reference_objectives_sha256"]
                assert array_sha256(dense_t[:n]) == row["reference_normalized_sha256"]
    sensitivity = read("reference_cardinality_sensitivity.csv")
    assert len(sensitivity) == 81
    assert all(float(r["directed_to_dense_max"]) == 0 for r in sensitivity)
    assert all(float(r["igd_from_dense"]) > 0 for r in sensitivity if int(r["count"]) < 10000)
    assert all(float(r["probe_mean"]) > 0 for r in sensitivity)


def test_every_payload_array_source_commit_and_frozen_phase0_to_10b():
    hashes = verify_checksums(OUTPUT)
    assert len(hashes) >= 50
    meta = json.loads((OUTPUT / "generation_manifest.json").read_text(encoding="utf-8"))
    frozen = json.loads((OUTPUT / "frozen_inputs_manifest.json").read_text(encoding="utf-8"))
    assert len(frozen) == meta["frozen_inputs_verified"] == 1204 and meta["frozen_inputs_unchanged"]
    for name, digest in frozen.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    for name, digest in meta["source_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
        source = subprocess.check_output(
            ["git", "show", meta["code_commit"] + ":" + name], cwd=ROOT
        )
        assert hashlib.sha256(source).hexdigest() == digest, name
    refinement = meta.get("figure_layout_refinement")
    if refinement:
        source = subprocess.check_output(
            ["git", "show", refinement["code_commit"] + ":" + refinement["script"]], cwd=ROOT
        )
        assert hashlib.sha256(source).hexdigest() == refinement["sha256"]
    for filename, arrays in meta["array_manifest"].items():
        with np.load(OUTPUT / filename, allow_pickle=False) as data:
            assert set(data.files) == set(arrays)
            for key, info in arrays.items():
                assert (
                    list(data[key].shape) == info["shape"] and str(data[key].dtype) == info["dtype"]
                )
                assert np.isfinite(data[key]).all()
                assert array_sha256(data[key]) == info["sha256"]


def test_hv_analytic_oracles_and_precision_statuses_are_honest():
    config = json.loads(
        (OUTPUT / "hypervolume_integration_config.json").read_text(encoding="utf-8")
    )
    oracles = json.loads((OUTPUT / "metric_validation_oracles.json").read_text(encoding="utf-8"))
    assert len(oracles["hypervolume"]) == 32 and oracles["all_analytic_HV_oracles_passed"]
    assert {o["m"] for o in oracles["hypervolume"]} == set(range(4, 12))
    assert all(o["relative_error"] <= 1e-12 for o in oracles["hypervolume"])
    assert config["final_power"] in (16, 18, 20)
    assert config["samples_per_scramble"] == 2 ** config["final_power"] and config["scrambles"] == 4
    assert config["reference_point"] == 1.1 and config["lower_bound"] == 0
    rows = read("hypervolume_precision_diagnostics.csv")
    for row in rows:
        if float(row["HV_QMC"]) == 0 and int(row["eligible_count"]) > 0:
            assert row["qmc_status"] == "UNRESOLVED_ZERO_HITS"
    main = [
        r
        for r in rows
        if r["case_type"] == "pareto_reference"
        and r["n_reference"] == "5000"
        and int(r["power"]) == int(r["tier_max_power"]) == config["final_power"]
    ]
    assert len(main) == 27
    count = sum(r["qmc_status"] == "PRECISION_CRITERIA_PASSED" for r in main)
    assert count == config["reference_cases_passed"]
    assert (config["status"] == "VALIDATED_REFERENCE_REGIME") == (count == 27)
    meta = json.loads((OUTPUT / "generation_manifest.json").read_text(encoding="utf-8"))
    for m, item in meta["hypervolume_integration_samples"].items():
        assert item["seeds"] == [seed_for(20261029, f"hv_m{m}", f"scramble_{r}") for r in range(4)]
    coverage = read("reference_coverage_diagnostics.csv")
    assert len(coverage) == 27
    for row in coverage:
        if row["status"] == "FINITE_AUDIT_BUDGET_PASSED":
            assert all(
                float(row[k]) <= 0.05
                for k in ("volume_probe_rms_max", "boundary_probe_rms_max", "dense_hausdorff_rms")
            )


def test_lossless_primary_and_nested_loading_offline_context_and_verifier(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/validation"))
    from refine_synthetic_pareto_layout import archive_inputs
    from synthetic_pareto_diagnostics import figures
    from verify_synthetic_pareto import verify

    def forbidden(*args, **kwargs):
        raise AssertionError("loading cannot optimize or fit")

    monkeypatch.setattr("cnbi_v2.model.fit_multivariate_rsm", forbidden)
    monkeypatch.setattr("cnbi_v2.synthetic.calibration.calibrate", forbidden)
    report = verify(OUTPUT)
    assert report["scenarios"] == 27 and report["total"] == 135000
    sid = "nx2_delta1_rho025"
    small = load_reference(OUTPUT, sid, 2500)
    main = load_reference(OUTPUT, sid, 5000)
    dense = load_reference(OUTPUT, sid, 10000)
    for i in range(3):
        assert_array_equal(small[i], main[i][:2500])
        assert_array_equal(main[i], dense[i][:5000])
        assert not main[i].flags.writeable
    context = load_evaluation_context(OUTPUT, sid, SOURCE)
    result = context.evaluate(sid, 1, "C-NBI", main[0][:2], {"fixture": "offline-loader-only"})
    assert result.diagnostics["raw_count"] == 2 and result.metrics["GD"] == 0
    assert result.metrics["IGD"] > 0
    assert result.diagnostics["reference_coverage_status"] in {
        "FINITE_AUDIT_BUDGET_PASSED",
        "REVIEW_REQUIRED",
        "GEOMETRY_FALLBACK_REVIEW_REQUIRED",
    }
    with pytest.raises(ValueError):
        load_evaluation_context(OUTPUT, "missing", SOURCE)
    inputs = archive_inputs(OUTPUT)
    assert len(inputs[0]) == 27
    assert len(figures(*inputs)) == 6


def test_six_600dpi_figures_and_vector_pdf():
    paths = sorted((OUTPUT / "figures").glob("*.png"))
    assert len(paths) == 6
    for path in paths:
        with Image.open(path) as png:
            assert png.info["dpi"][0] == pytest.approx(600, abs=0.1) and png.width >= 4200
        pdf = path.with_suffix(".pdf").read_bytes()
        assert pdf.startswith(b"%PDF-") and b"/Subtype /Image" not in pdf
