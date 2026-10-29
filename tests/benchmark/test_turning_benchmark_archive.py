"""Independent frozen-artifact contracts; no real optimizer is rerun by pytest."""

import json

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation import turning_benchmark_inputs as data
from scripts.validation import turning_reference_campaign as phase7

from cnbi_v2.data import sha256_file


@pytest.fixture(scope="module")
def archive():
    output = data.OUTPUT
    meta = json.loads((output / "metadata.json").read_text())
    with np.load(output / "canonical_candidates.npz", allow_pickle=False) as d:
        x, z = d["x"], d["z"]
    return output, meta, x, z


def test_frozen_input_output_hashes_and_reference_identity(archive):
    output, meta, _, z = archive
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(output / name) == digest
    for name, digest in meta["output_sha256"].items():
        assert sha256_file(output / name) == digest
    for name, digest in {**meta["input_sha256"], **meta["phase8_input_sha256"]}.items():
        assert sha256_file(data.ROOT / name) == digest
    with np.load(output / "reference_final.npz", allow_pickle=False) as r:
        with np.load(phase7.OUTPUT / "reference_minus_cnbi.npz", allow_pickle=False) as old:
            assert_array_equal(r["z"], old["z"])
            assert_array_equal(r["x"], old["x"])
        assert len(r["z"]) == 18503
        assert_array_equal(z[r["point_ids"]], r["z"])
    assert meta["baseline_cardinality"] == 408
    assert meta["sphere_violations"] == 0
    assert meta["RSM_refit"] is False and meta["data_reconstructed"] is False


def test_reference_resampling_and_all_preserved_origins_exclude_cnbi(archive):
    output, meta, x, _ = archive
    with np.load(output / "reference_seed_subsamples.npz", allow_pickle=False) as sets:
        for r in (5, 10, 15, 20, 25):
            a = sets[str(r)]
            assert a.shape == (100, r)
            assert len(set(map(tuple, a))) == 100
            assert np.all(np.diff(a, axis=1) > 0)
            assert a.min() >= 0 and a.max() < 30
        assert_array_equal(sets["30"], np.arange(30).reshape(1, 30))
    with np.load(output / "reference_sensitivity_lineage.npz", allow_pickle=False) as d:
        assert len(d["names"]) == 512  # 506 run-sensitivity refs plus6 compositions
        assert d["front_ids"].max() < meta["phase8a"]["independent_candidates"]
        assert d["origin_ids"].max() < meta["phase8a"]["independent_candidates"]
        assert len(d["origin_ids"]) == len(d["origin_representatives"])
        for start in range(0, len(d["origin_ids"]), 100000):
            origins = d["origin_ids"][start : start + 100000]
            reps = d["origin_representatives"][start : start + 100000]
            assert np.max(np.abs(x[origins] - x[reps])) <= meta["numerical_x_tolerance"]
    assert meta["phase8a"]["no_CNBI_in_any_reference"] is True


def test_native_equalized_k_and_nested_extremes(archive):
    output, meta, _, z = archive
    native = data.rows(output / "native_metrics.csv")
    equal = data.rows(output / "equalized_k66_metrics.csv")
    assert len(native) == len(equal) == 124  # 62 sets x2 reference labels
    assert meta["K_max_common_without_VRF"] == 303
    assert all(int(r["N_unique_ND"]) == 66 for r in equal)
    refs = {r["reference"]: int(r["reference_size"]) for r in native}
    assert refs == dict(
        all=22523, minus_cnbi=18503, minus_nsga3=14202, minus_moead=12836, minus_vrf=22460
    )
    curves = data.rows(output / "cardinality_curve_metrics.csv")
    with np.load(output / "candidate_farthest_orderings.npz", allow_pickle=False) as orders:
        assert len(orders.files) == 62
        for name in orders.files:
            order = orders[name]
            assert len(np.unique(order)) == len(order)
            original = next(r for r in native if name == f"{r['method']}_seed{r['seed']}")
            assert len(order) == int(original["N_unique_ND"])
            points = z[order]
            minima = points.min(axis=0)
            assert_allclose(points[:8].min(axis=0), minima, atol=0, rtol=0)
    groups = {}
    for r in curves:
        assert int(r["K"]) == int(r["N_unique_ND"])
        assert int(r["reference_size"]) == refs[r["reference"]]
        groups.setdefault((r["method"], r["seed"], r["label"]), []).append(r)
    for group in groups.values():
        group.sort(key=lambda r: int(r["K"]))
        assert np.all(np.diff([float(r["HV"]) for r in group]) >= -1e-14)
    # Reference-independent indicators are identical under the two target labels.
    by_key = {}
    for r in native + curves:
        key = r["method"], r["seed"], r["variant"], r["K"]
        values = tuple(float(r[k]) for k in ("HV", "Spacing", "Sparsity"))
        if key in by_key:
            assert values == by_key[key]
        by_key[key] = values


def test_timing_is_controlled_and_no_vrf_or_cnbi_cost_fabricated(archive):
    output, meta, _, _ = archive
    launch = json.loads((output / "timing_launch.json").read_text())
    assert launch["working_tree_dirty_at_launch"] is False
    assert launch["no_parallel_methods"] is True
    assert launch["hardware"]["external_active_python"] == []
    assert set(launch["thread_environment"].values()) == {"1"}
    assert meta["controlled_timing"]["runs"] == 20
    assert meta["controlled_timing"]["measured_optimizer_NFE"] == 20 * 132000
    assert meta["controlled_timing"]["code_config_unchanged"] is True
    for family in ("NSGA3", "MOEAD"):
        records = data.rows(output / f"timing_{family.lower()}.csv")
        assert [int(r["seed"]) for r in records] == list(range(1001, 1011))
        for row in records:
            assert row["git_commit"] == launch["git_commit"]
            assert int(row["NFE"]) == 132000
            assert row["phase7_final_exact"] == "True"
            assert float(row["T_total"]) > float(row["optimizer_seconds_excluding_observer"]) > 0
            stem = output / "controlled_timing" / f"{family.lower()}_seed{row['seed']}"
            cp = json.loads(stem.with_suffix(".json").read_text())["checkpoints"]
            assert [r["generation"] for r in cp] == [50, 100, 200, 300, 400]
            assert [r["nfe"] for r in cp] == [g * 330 for g in [50, 100, 200, 300, 400]]
            assert np.all(np.diff([r["T_total"] for r in cp]) > 0)
    for name in ("timing_cnbi.csv", "timing_vrf.csv"):
        assert all(
            r["T_total"] == "" and int(r["repetitions_executed"]) == 0
            for r in data.rows(output / name)
        )
    assert meta["VRF_optimization_executions"] == meta["VRF_timing_executions"] == 0


def test_failed_h5_gate_is_preserved_without_relaxing_bounds(archive):
    output, _, _, _ = archive
    gate = json.loads((output / "h5_direct_equivalence.json").read_text())
    assert gate["status"] == "H5_DIRECT_EQUIVALENCE_FAILED"
    assert gate["x_disagreements"] == 24
    assert gate["x_tolerance_predeclared"] == gate["z_tolerance_predeclared"] == 1e-5
    assert gate["max_x_Linf"] > 3 and gate["max_z_Linf"] > 0.5
    assert gate["timing_usable_for_official_H5"] is False
    assert gate["archived_baseline_modified"] is False
