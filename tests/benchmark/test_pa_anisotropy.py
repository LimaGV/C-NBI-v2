"""Integrity of the applied postprocessing ablation; no optimizer executions."""

import ast
import json
import os
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation import turning_pa_anisotropy as analysis

from cnbi_v2.benchmark.metrics import gd_igd, spacing_sparsity
from cnbi_v2.benchmark.selection import farthest_order
from cnbi_v2.data import sha256_file


@pytest.fixture(scope="module")
def archive():
    root = Path(os.environ.get("CNBI_APPLIED_INPUT_ROOT", analysis.ROOT))
    output = analysis.ROOT / analysis.OUTPUT
    protocol = json.loads((output / "protocol.json").read_text())
    raw = analysis.arrays(root / analysis.P8 / "H5_rep1.npz")
    return root, output, protocol, raw, analysis.arrays(output / "fronts.npz")


def test_frozen_inputs_and_result_checksums(archive):
    root, output, protocol, _, _ = archive
    assert analysis.audit(root) == protocol["input_sha256"]
    assert sha256_file(Path(analysis.__file__)) == protocol["source_sha256"]
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        assert sha256_file(output / name) == digest
    assert protocol["new_optimizer_calls"] == protocol["new_MC"] == 0
    assert protocol["new_RSM"] == protocol["new_anchors"] == 0
    assert protocol["new_Pareto_reference_points"] == 0


def test_selection_uses_frozen_centered_spectra_and_global_ratio(archive):
    root, output, protocol, _, _ = archive
    cutoff, subsets = analysis.selection(root)
    assert cutoff == protocol["q_cutoff"] == 0.3129205407188535
    saved = analysis.rows(output / "subset_selection.csv")
    assert len(saved) == len(subsets) == 37
    for row, original in zip(saved, subsets, strict=True):
        assert row["subset_id"] == original["subset_id"]
        assert float(row["q"]) == original["q"]
        assert original["retain_anisotropy"] == (original["q"] >= cutoff)
    kept = [r for r in subsets if r["retain_anisotropy"]]
    assert sum(r["k"] == 2 for r in kept) == 19
    assert sum(r["k"] == 3 for r in kept) == 8
    assert sum(r["subproblems"] for r in subsets) == 492
    assert sum(r["subproblems"] for r in kept) == 282
    assert all(r["q"] == 1 for r in subsets if r["k"] == 2)


def test_raw_filter_then_dedup_and_dominance_without_solver(archive, monkeypatch):
    import scipy.optimize

    def forbidden(*args, **kwargs):
        pytest.fail("Postprocessing must never execute an optimizer")

    monkeypatch.setattr(scipy.optimize, "minimize", forbidden)
    root, _, protocol, raw, saved = archive
    _, subsets = analysis.selection(root)
    records = analysis.rows(root / analysis.P8 / "H5_rep1_records.csv")
    assert len(records) == len(raw["x"]) == 492
    names = [r["subset_id"] for r in subsets]
    for i, record in enumerate(records):
        assert int(record["row_id"]) == i
        assert record["subset"] == names[raw["subsets"][i]]
        assert int(record["H"]) == 5
    keep = {r["subset_id"] for r in subsets if r["retain_anisotropy"]}
    source_rows = np.array([i for i, r in enumerate(records) if r["subset"] in keep])
    assert len(source_rows) == 282
    for name, ids, count in (("PA", np.arange(492), 409), ("PA_ANISOTROPY", source_rows, 228)):
        unique, nd = analysis.front(raw, ids, protocol["policy"])
        assert len(nd) == count
        assert_array_equal(nd, saved[f"native_{name}_source_rows"])
        assert set(nd) <= set(unique) <= set(ids)
        if name == "PA":
            assert_array_equal(unique, raw["unique_ids"])
            assert_array_equal(nd, raw["nd_ids"])
        else:
            assert_array_equal(saved["combined_x"], raw["x"][nd])
            assert_array_equal(saved["combined_z"], raw["z"][nd])
    assert protocol["PA_ND_lost"] == 181
    assert protocol["PA_ND_retained"] == 228
    assert protocol["combined_new_ND"] == 0


def test_equalization_preserves_official_fps_and_ties(archive):
    _, _, _, raw, saved = archive
    for arm in ("PA", "PA_ANISOTROPY"):
        nd = saved[f"native_{arm}_source_rows"]
        order = farthest_order(raw["z"][nd])
        for mode, k in (("equalized_pairwise", 228), ("equalized_K66", 66)):
            chosen = saved[f"{mode}_{arm}_source_rows"]
            assert_array_equal(chosen, nd[order[:k]])
            assert len(np.unique(chosen)) == k


def test_metrics_and_percentage_deltas_match_frozen_protocol(archive):
    root, output, protocol, raw, saved = archive
    reference = analysis.arrays(root / analysis.REF / "reference_final.npz")["z"]
    assert reference.shape == (18503, 8)
    records = analysis.rows(output / "metrics.csv")
    assert len(records) == 6
    for row in records:
        ids = saved[f"{row['mode']}_{row['arm']}_source_rows"]
        gd, igd = gd_igd(raw["z"][ids], reference)
        spacing, sparsity = spacing_sparsity(raw["z"][ids])
        assert_allclose(
            [float(row[k]) for k in ("GD", "IGD", "Spacing", "Sparsity")],
            [gd, igd, spacing, sparsity],
            rtol=2e-14,
            atol=2e-15,
        )
        assert all(np.isfinite(float(row[k])) for k in (*analysis.METRICS, "HV_QMC_SE"))
    for name, mode in (
        ("native_metrics.csv", "native"),
        ("equalized_k66_metrics.csv", "equalized_K66"),
    ):
        official = next(
            r
            for r in analysis.rows(root / analysis.P8 / name)
            if r["method"] == "CNBI5" and r["reference"] == "minus_cnbi"
        )
        current = next(r for r in records if r["mode"] == mode and r["arm"] == "PA")
        for metric in (*analysis.METRICS, "HV_QMC_SE"):
            assert_allclose(float(current[metric]), float(official[metric]), rtol=2e-14, atol=2e-15)
    for row in analysis.rows(output / "metric_deltas.csv"):
        a, b = float(row["PA"]), float(row["PA_ANISOTROPY"])
        assert float(row["delta"]) == b - a
        assert float(row["delta_percent"]) == 100 * (b - a) / a
    hv = protocol["HV_quadrature"]
    assert hv["power"] == 16 and hv["seeds"] == [20260, 20261, 20262, 20263]
    cache = json.loads((root / analysis.REF / "hv_numerical_cache.json").read_text())
    assert protocol["HV_samples_sha256"] == cache["samples_sha256"]


def test_cost_is_theoretical_and_excluded_trios_contribute(archive):
    _, output, _, _, _ = archive
    costs = analysis.rows(output / "costs.csv")
    assert int(costs[1]["eliminated_subproblems"]) == 210
    assert costs[1]["observed_end_to_end_seconds"] == ""
    assert costs[1]["counterfactual_end_to_end_seconds"] == ""
    removed = analysis.rows(output / "removed_subset_contributions.csv")
    assert len(removed) == 10
    assert sum(int(r["PA_ND_exclusively_supported"]) for r in removed) == 181
    assert all(float(r["exclusive_HV"]) > 0 for r in removed)
    coverage = analysis.rows(output / "objective_coverage.csv")
    assert len(coverage) == 8
    assert all(int(r["combined_subsets"]) > 0 for r in coverage)
    assert all(float(r["combined_min"]) == float(r["PA_min"]) for r in coverage)


def test_script_does_not_import_or_call_solvers():
    tree = ast.parse(Path(analysis.__file__).read_text(encoding="utf-8"))
    forbidden = {"minimize", "solve_nbi_lattice", "least_squares", "fit_multivariate_ols"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            assert node.id not in forbidden
        if isinstance(node, ast.ImportFrom):
            assert not forbidden.intersection(alias.name for alias in node.names)
