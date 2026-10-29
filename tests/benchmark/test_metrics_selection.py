import json
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.benchmark.dominance import DominanceIndex
from cnbi_v2.benchmark.hypervolume import HVGrid, historical_box
from cnbi_v2.benchmark.metrics import gd_igd, nearest_distances, spacing_sparsity, summary
from cnbi_v2.benchmark.selection import farthest_order, seed_subsamples
from cnbi_v2.nbi import canonical_decision_points, nondominated_mask

ROOT = Path(__file__).resolve().parents[2]


def test_metric_geometric_oracles_and_legacy_ddof():
    a = np.array([[0.0, 0.0], [1.0, 0.0], [3.0, 0.0]])
    assert_array_equal(nearest_distances(a), [1.0, 1.0, 2.0])
    spacing, sparsity = spacing_sparsity(a)
    assert_allclose(spacing, np.sqrt(1 / 3))
    assert_allclose(sparsity, 4 / 3)
    assert_allclose(spacing_sparsity(3 * a), [3 * spacing, 3 * sparsity])
    gd, igd = gd_igd(a, [[0, 0], [2, 0]])
    assert_allclose([gd, igd], [2 / 3, 0.5])


def test_archived_v1_corrected_applied_numbers():
    source = json.loads(
        (ROOT / "references/metadata/phase_08_legacy_metrics/source_audit.json").read_text()
    )
    with np.load(ROOT / source["fixture"]["path"], allow_pickle=False) as d:
        spacing, sparsity = spacing_sparsity(d["historical_z"])
    assert_allclose(spacing, source["fixture"]["Spacing_published"], atol=1e-14, rtol=0)
    assert_allclose(sparsity, source["fixture"]["Sparsity_published"], atol=1e-14, rtol=0)
    assert spacing != source["fixture"]["Spacing_earlier_ddof0"]


def test_shared_hv_box_masks_exact_boxes_and_monotonicity():
    points = np.array([[0.0, 0.5], [0.5, 0.0]])
    lo, ref = historical_box(points)
    assert_array_equal(lo, [0, 0])
    assert_array_equal(ref, [1.1, 1.1])
    grid = HVGrid(lo, ref, power=10)
    samples = grid.samples()
    assert_array_equal(samples, grid.samples())
    masks = grid.masks(np.array([[0.0, 0.0], [0.8, 0.2], [0.2, 0.8]]), samples)
    assert_allclose(grid.estimate(masks[0])["HV"], 1.21, atol=1e-14)
    assert grid.estimate(np.zeros(grid.bytes_per_point, dtype=np.uint8))["HV"] == 0
    merged = np.bitwise_or.reduce(masks[1:], axis=0)
    h = grid.values(merged)
    # Exact union area .45; four independent scrambled dyadic quadratures.
    assert abs(h.mean() - 0.45) < 0.012
    assert grid.estimate(merged)["HV"] >= grid.estimate(masks[1])["HV"]
    assert len(grid.values(merged, power=8)) == 4
    assert grid.estimate(merged)["HV_QMC_SE"] >= 0
    with pytest.raises(ValueError):
        grid.masks(np.array([[1.2, 0.0]]), samples)
    with pytest.raises(ValueError):
        grid.values(np.zeros(3, dtype=np.uint8))
    with pytest.raises(ValueError):
        grid.values(merged, power=11)


@pytest.mark.parametrize(
    "lo,ref,power,seeds",
    [([0], [0], 4, (1, 2)), ([0], [1], 2, (1, 2)), ([0], [1], 4, (1, 1)), ([0], [1, 2], 4, (1, 2))],
)
def test_invalid_hv(lo, ref, power, seeds):
    with pytest.raises(ValueError):
        HVGrid(np.array(lo), np.array(ref), power=power, seeds=seeds)


def test_farthest_order_extremes_nested_unique_and_ties():
    z = np.array([[0, 1], [1, 0], [0.5, 0.5], [0.2, 0.8], [0.8, 0.2]])
    order = farthest_order(z)
    assert_array_equal(order[:2], [0, 1])
    assert order[2] == 2
    assert_array_equal(order, farthest_order(z))
    assert len(set(order)) == len(z)
    assert set(order[:3]) <= set(order[:4]) <= set(order)
    assert order[3] == 3  # stable original row/source ID for symmetric tie


def test_seed_subsamples_are_distinct_without_replacement_and_repeatable():
    a = seed_subsamples(5, count=100, rng=np.random.Generator(np.random.PCG64(20261024)))
    b = seed_subsamples(5, count=100, rng=np.random.Generator(np.random.PCG64(20261024)))
    assert_array_equal(a, b)
    assert len(set(map(tuple, a))) == 100
    assert np.all(np.diff(a, axis=1) > 0)
    assert a.min() >= 0 and a.max() < 30
    with pytest.raises(ValueError):
        seed_subsamples(30, count=2, rng=np.random.default_rng(3))
    with pytest.raises(ValueError):
        seed_subsamples(31, count=1, rng=np.random.default_rng(3))


@pytest.mark.parametrize("seed", range(4))
def test_cached_subset_dominance_matches_frozen_full_algorithm(seed):
    rng = np.random.default_rng(seed)
    x, z = rng.normal(size=(50, 3)), rng.normal(size=(50, 8))
    x[10] = x[0]
    z[10] = z[0]
    x[11] = x[0] + 2e-15
    z[11] = z[0]
    tau = np.full(8, 1e-14)
    index = DominanceIndex.build(x, z, 1e-14, tau, block=7)
    for _ in range(6):
        ids = rng.choice(50, 25, replace=False)
        actual, mapping = index.front(ids)
        reps, canonical = canonical_decision_points(x[ids], tolerance=1e-14)
        keep = nondominated_mask(z[ids[reps]], equality_tolerance=tau)
        assert_array_equal(actual, ids[reps[keep]])
        assert_array_equal(mapping, ids[canonical])


def test_excluded_first_representative_does_not_leak_and_nontransitive_equality():
    x = np.array([[0.0, 0.0, 0.0], [0.75e-14, 0, 0], [1.5e-14, 0, 0]])
    z = np.ones((3, 8))
    index = DominanceIndex.build(x, z, 1e-14, np.zeros(8))
    ids, _ = index.front(np.array([0, 1, 2]))
    assert_array_equal(ids, [0, 2])
    ids, mapping = index.front(np.array([1, 2]))
    assert_array_equal(ids, [1])
    assert_array_equal(mapping, [1, 1])
    with pytest.raises(ValueError):
        index.front(np.array([1, 1]))
    with pytest.raises(ValueError):
        DominanceIndex.build(x, z, -1.0, np.zeros(8))


def test_summary_sample_sd_and_singleton():
    s = summary([1.0, 2.0, 3.0])
    assert s["SD"] == 1 and s["median"] == 2 and s["IQR"] == 1
    assert summary([2.0])["SD"] is None
    for bad in ([], [[1]], [np.nan]):
        with pytest.raises(ValueError):
            summary(bad)
    for bad in ([], [[1.0, np.nan]], [[1.0, 2.0]]):
        with pytest.raises(ValueError):
            spacing_sparsity(bad)
