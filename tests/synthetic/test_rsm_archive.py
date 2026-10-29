"""Frozen Phase10B scientific outputs and their independent validation evidence."""

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from PIL import Image

from cnbi_v2.model import quadratic_design
from cnbi_v2.synthetic.ccd import full_ccd
from cnbi_v2.synthetic.noise import experimental_noise, stream_seed
from cnbi_v2.synthetic.rsm_generation import true_coefficients
from cnbi_v2.synthetic.rsm_inputs import array_sha256, load_structural_cases, verify_checksums
from cnbi_v2.synthetic.rsm_serialization import load_models
from cnbi_v2.synthetic.rsm_validation import external_metrics

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/phase_10_synthetic_rsm/rsm_20261029"
STRUCTURAL = ROOT / "results/phase_10_synthetic_generation/structural_20261029"


def read(name):
    with (OUTPUT / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_official_campaign_complete_five_replicas_and_identifiable_models():
    manifest = json.loads((OUTPUT / "generation_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "COMPLETE" and manifest["official_run"]
    assert not manifest["working_tree_dirty_at_start"] and not manifest["failures"]
    assert manifest["scenarios"] == manifest["noise_free_certifications"] == 27
    assert manifest["instances"] == manifest["reverse_order_reproduced"] == 135
    assert manifest["models_reloaded_without_refit"] == 135
    assert manifest["experimental_rows"] == 3555 and manifest["response_models"] == 990
    assert manifest["scalar_response_observations"] == 28530
    assert manifest["failed_models"] == 0 and manifest["all_replicas_retained"]
    assert not manifest["multiobjective_methods_executed"]
    assert not manifest["Pareto_reference_or_metrics_generated"]
    assert not manifest["external_validation_used_for_selection"]
    protocol = json.loads((OUTPUT / "generation_config.json").read_text(encoding="utf-8"))
    assert protocol == json.loads(
        (ROOT / "docs/policies/synthetic_generation_10b.json").read_text(encoding="utf-8")
    )
    rows = read("synthetic_rsm_instances.csv")
    assert len(rows) == len(load_models(OUTPUT)) == 135
    assert sum(int(r["n"]) for r in rows) == 3555
    assert sum(int(r["m"]) for r in rows) == 990
    assert Counter(r["nx"] for r in rows) == {"2": 45, "3": 45, "5": 45}
    groups = defaultdict(list)
    for row in rows:
        groups[row["scenario_id"]].append(row)
        assert row["status"] == "FITTED_RETAINED"
        assert int(row["seed"]) == stream_seed(20261029, row["scenario_id"], int(row["replica_id"]))
    assert len(groups) == 27
    assert all(
        sorted(int(r["replica_id"]) for r in group) == [1, 2, 3, 4, 5] for group in groups.values()
    )
    assert len({int(r["seed"]) for r in rows} | {int(r["external_seed"]) for r in rows}) == 162


def test_archive_hashes_all_arrays_and_frozen_phase0_to_10a():
    assert len(verify_checksums(OUTPUT)) >= 43
    manifest = json.loads((OUTPUT / "generation_manifest.json").read_text(encoding="utf-8"))
    frozen = json.loads((OUTPUT / "frozen_inputs_manifest.json").read_text(encoding="utf-8"))
    assert len(frozen) == manifest["frozen_inputs_verified"] == 1150
    assert manifest["frozen_inputs_unchanged"]
    for name, digest in frozen.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    for name, digest in manifest["source_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
        committed = subprocess.check_output(
            ["git", "show", manifest["code_commit"] + ":" + name], cwd=ROOT
        )
        assert hashlib.sha256(committed).hexdigest() == digest, name
    refinement = manifest.get("figure_layout_refinement")
    if refinement:
        committed = subprocess.check_output(
            ["git", "show", refinement["code_commit"] + ":" + refinement["script"]], cwd=ROOT
        )
        assert hashlib.sha256(committed).hexdigest() == refinement["sha256"]
    for filename, arrays in manifest["array_manifest"].items():
        with np.load(OUTPUT / filename, allow_pickle=False) as data:
            assert set(data.files) == set(arrays)
            for key, meta in arrays.items():
                assert list(data[key].shape) == meta["shape"]
                assert data[key].dtype == np.float64
                assert np.isfinite(data[key]).all()
                assert array_sha256(data[key]) == meta["sha256"]


def test_all_noisy_observations_centers_raw_covariances_and_coefficients():
    cases = load_structural_cases(STRUCTURAL)
    rows = read("synthetic_rsm_instances.csv")
    models = load_models(OUTPUT)
    observations = read("synthetic_observations.csv")
    assert len(observations) == 28530
    assert len({(r["instance_id"], r["design_point_id"]) for r in observations}) == 3555
    by_instance = defaultdict(list)
    for row in observations:
        by_instance[row["instance_id"]].append(row)
    case_map = {c.scenario_id: (c, a) for c, a in cases}
    negative, singular = 0, 0
    with (
        np.load(OUTPUT / "synthetic_experimental_arrays.npz", allow_pickle=False) as data,
        np.load(OUTPUT / "synthetic_residual_covariance.npz", allow_pickle=False) as covariance,
    ):
        for row in rows:
            key = row["instance_id"]
            c, a = case_map[row["scenario_id"]]
            x = data[f"nx{c.nx}__ccd"]
            assert_array_equal(x, full_ccd(c.nx).points)
            y, true, noise = (data[key + suffix] for suffix in ("__observed", "__truth", "__noise"))
            assert_array_equal(y, true + noise)
            assert_array_equal(noise, experimental_noise(true, int(row["seed"])))
            assert len(np.unique(noise[-5:, 0])) == 5
            # Analytic coefficients are validation-only, not a source for noisy observations.
            assert_allclose(
                quadratic_design(x) @ true_coefficients(a), true, atol=1e-14, rtol=2e-15
            )
            residuals = data[key + "__residuals"]
            assert_array_equal(y - models[key].predict(x), residuals)
            assert_allclose(quadratic_design(x).T @ residuals, 0, atol=5e-12, rtol=0)
            raw = residuals.T @ residuals / int(row["residual_df"])
            assert_array_equal(covariance[key + "__covariance"], raw)
            if int(row["residual_covariance_rank"]) < c.m:
                singular += 1
                assert row["residual_covariance_condition"] == ""
                assert c.nx == 2 and c.m == 8
            for record in by_instance[key]:
                j, i = int(record["response_id"][1:]) - 1, int(record["design_point_id"]) - 1
                assert float(record["observed"]) == y[i, j]
                assert float(record["noise"]) == noise[i, j]
            negative += int(np.sum(y < 0))
    assert singular == 15 and negative == 369
    coefficient_rows = read("synthetic_rsm_coefficients.csv")
    assert len(coefficient_rows) == 13275
    assert len(read("synthetic_true_coefficients.csv")) == 2655
    assert len(read("synthetic_coefficient_errors.csv")) == 13275
    for row in coefficient_rows:
        assert (
            float(row["coefficient"])
            == models[row["instance_id"]].coefficients[
                int(row["term_id"]), int(row["response_id"][1:]) - 1
            ]
        )


def test_noise_free_certificates_df_statistics_and_external_metrics():
    certificates = read("noiseless_certification.csv")
    assert len(certificates) == 27
    assert all(
        r["status"] == "CERTIFIED" and float(r["max_coefficient_error"]) <= float(r["tolerance"])
        for r in certificates
    )
    noise = read("synthetic_noise_parameters.csv")
    assert len(noise) == 990
    for row in noise:
        sf, variance = float(row["signal_variance"]), float(row["noise_variance"])
        # Matrix-axis and per-column reductions may differ by a few float64 ulps.
        assert_allclose(variance, sf / 19, rtol=2e-15, atol=0)
        assert sf / (sf + variance) == pytest.approx(0.95, abs=5e-16)
    diagnostics = read("synthetic_rsm_diagnostics.csv")
    assert len(diagnostics) == 990
    for row in diagnostics:
        nx = int(row["nx"])
        n, p, lof = {2: (13, 6, 3), 3: (19, 10, 5), 5: (47, 21, 22)}[nx]
        assert int(row["design_rank"]) == p
        assert int(row["error_df"]) == n - p
        assert int(row["pure_error_df"]) == 4 and int(row["lack_of_fit_df"]) == lof
        assert all(row[k] == "OK" for k in ("press_status", "model_status", "lack_of_fit_status"))
    external = read("synthetic_external_validation.csv")
    models = load_models(OUTPUT)
    grouped = defaultdict(list)
    for row in external:
        grouped[row["instance_id"]].append(row)
    with np.load(OUTPUT / "synthetic_external_sample.npz", allow_pickle=False) as data:
        assert len(data.files) == 54
        for key, records in grouped.items():
            sid = records[0]["scenario_id"]
            points, truth = data[sid + "__points"], data[sid + "__truth"]
            assert len(points) == 4096
            assert int(records[0]["external_seed"]) == stream_seed(20261029, sid, 0)
            metrics = external_metrics(models[key].predict(points), truth)
            stored = np.array(
                [
                    [
                        float(row[k])
                        for k in ("rmse", "mae", "r_squared_external", "max_absolute_error")
                    ]
                    for row in records
                ]
            )
            assert_allclose(metrics, stored, atol=2e-12, rtol=2e-12)
    assert len(external) == 990 and len(grouped) == 135
    assert len(read("synthetic_replica_variation.csv")) == 27
    assert len(read("synthetic_rsm_summary.csv")) == 37


def test_all_six_english_figures_600_dpi_and_vector_pdf():
    images = sorted((OUTPUT / "figures").glob("*.png"))
    assert len(images) == 6
    for path in images:
        with Image.open(path) as png:
            assert png.info["dpi"][0] == pytest.approx(600, abs=0.1)
            assert png.width >= 3800
        pdf = path.with_suffix(".pdf").read_bytes()
        assert pdf.startswith(b"%PDF-") and b"/Subtype /Image" not in pdf


def test_read_only_verifier_and_layout_reader_do_not_fit(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/validation"))
    from refine_synthetic_rsm_figure_layout import archive_figure_inputs
    from verify_synthetic_rsm import verify

    def forbidden(*args, **kwargs):
        raise AssertionError("archive readers must not fit")

    monkeypatch.setattr("cnbi_v2.model.fit_multivariate_rsm", forbidden)
    monkeypatch.setattr("cnbi_v2.synthetic.rsm_generation.fit_multivariate_rsm", forbidden)
    assert verify(OUTPUT)["models"] == 135
    items, anchors, samples, diagnostics, external = archive_figure_inputs(OUTPUT)
    assert len(items) == 135 and len(anchors) == len(samples) == 27
    assert len(diagnostics) == len(external) == 990
