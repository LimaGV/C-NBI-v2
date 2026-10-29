import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from PIL import Image

from cnbi_v2.synthetic import evaluate, factorial_design, radius
from cnbi_v2.synthetic.correlation import population_correlation, summaries
from cnbi_v2.synthetic.validation import certify_anchors, certify_correlation

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/phase_10_synthetic_generation/structural_20261029"


def read_csv(name):
    with (OUTPUT / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_published_scenarios_all27_known_minima_correlations_and_precision():
    meta = json.loads((OUTPUT / "calibration_manifest.json").read_text(encoding="utf-8"))
    assert meta["status"] == "COMPLETE" and meta["validated"] == meta["scenarios"] == 27
    assert meta["official_run"] and not meta["working_tree_dirty_at_start"]
    assert meta["configurations_per_cell"] == 1 and not meta["failed_scenarios"]
    assert meta["starts_total"] == 216
    assert not meta["multiobjective_methods_executed"]
    assert not meta["noise_CCD_RSM_generated"] and not meta["Pareto_reference_or_metrics_generated"]
    protocol = json.loads((OUTPUT / "calibration_config.json").read_text(encoding="utf-8"))
    assert protocol == json.loads(
        (ROOT / "docs/policies/synthetic_generation_10a.json").read_text(encoding="utf-8")
    )
    rows = read_csv("synthetic_scenarios.csv")
    correlations = read_csv("synthetic_correlations.csv")
    assert len(rows) == len(correlations) == 27
    assert [r["scenario_id"] for r in rows] == [c.scenario_id for c in factorial_design()]
    anchor_rows = read_csv("synthetic_anchors.csv")
    with np.load(OUTPUT / "synthetic_correlation_matrices.npz", allow_pickle=False) as matrices:
        assert len(matrices.files) == 108
        for cell, row in zip(factorial_design(), correlations, strict=True):
            key = cell.scenario_id
            a = matrices[key + "__anchors"]
            assert a.shape == (cell.m, cell.nx) and a.dtype == np.float64
            assert certify_anchors(a, radius(cell.nx)).valid
            assert_array_equal(np.diag(evaluate(a, a)), np.zeros(cell.m))
            recovered = np.array(
                [float(r["value"]) for r in anchor_rows if r["scenario_id"] == key]
            )
            assert_array_equal(recovered.reshape(a.shape), a)
            cal = matrices[key + "__calibration"]
            val = matrices[key + "__validation"]
            pop = matrices[key + "__population"]
            assert_array_equal(pop, population_correlation(a, radius(cell.nx)))
            for r in (cal, val):
                assert certify_correlation(r, cell.nx).valid
                assert abs(summaries(r)[0] - cell.rho_target) <= 0.05
                assert np.max(np.abs(r - pop)) <= 0.005
            assert_allclose(float(row["rho_abs_realized"]), summaries(val)[0], atol=0, rtol=0)
            assert_allclose(float(row["rho_signed"]), summaries(val)[1], atol=0, rtol=0)
            assert row["valid"] == "True" and int(row["anchor_rank"]) == cell.nx
            assert row["calibration_seed"] != row["validation_seed"]
    diagnostics = read_csv("calibration_diagnostics.csv")
    assert len(diagnostics) == 216
    assert sum(r["selected"] == "True" for r in diagnostics) == 27


def test_published_historical_files_and_source_manifests_are_unchanged():
    frozen = json.loads((OUTPUT / "frozen_inputs_manifest.json").read_text(encoding="utf-8"))
    assert len(frozen) > 1000
    for name, digest in frozen.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    for line in (OUTPUT / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        assert hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest() == digest, name
    meta = json.loads((OUTPUT / "calibration_manifest.json").read_text(encoding="utf-8"))
    assert meta["frozen_inputs_verified"] == len(frozen)
    assert meta["frozen_inputs_unchanged"]
    for name, digest in meta["source_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest


def test_published_exactly_four_english_diagnostics_high_resolution_and_vector_pdf():
    pngs = sorted((OUTPUT / "figures").glob("*.png"))
    pdfs = sorted((OUTPUT / "figures").glob("*.pdf"))
    assert len(pngs) == len(pdfs) == 4
    for path in pngs:
        with Image.open(path) as image:
            assert_allclose(image.info["dpi"], [600, 600], atol=0.01, rtol=0)
    for path in pdfs:
        assert b"/Subtype /Image" not in path.read_bytes()
    assert (
        json.loads((OUTPUT / "calibration_manifest.json").read_text())["figure_language"]
        == "English"
    )
