"""Mathematical fixtures are not new benchmark anchor configurations."""

from itertools import product

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scipy.spatial import QhullError

from cnbi_v2.benchmark.selection import farthest_order
from cnbi_v2.nbi import nondominated_mask
from cnbi_v2.synthetic.design import Scenario
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.pareto import geometry as geo
from cnbi_v2.synthetic.pareto.geometry import (
    hull_geometry,
    sample_hull_weights,
    seed_for,
    unit_sobol,
)
from cnbi_v2.synthetic.pareto.normalization import analytic_normalization
from cnbi_v2.synthetic.pareto.reference import candidates, generate_reference, sensitivity
from cnbi_v2.synthetic.pareto.selection import partial_fps, unique_indices

A = np.array([[0.5, 0], [-0.5, 0], [0, 0.5], [0, -0.5]])
CELL = Scenario(2, 1, 0.25)


def test_both_inclusions_projection_and_unique_weighted_minima():
    for x, p in (([1, 0], [0.5, 0]), ([0.8, 0.8], [0.25, 0.25])):
        original, projection = evaluate([x], A)[0], evaluate([p], A)[0]
        gap = np.sum((np.array(x) - p) ** 2)
        assert np.all(original >= projection + gap - 1e-15)
        assert np.all(original > projection)
    geometry = hull_geometry(A)
    weights = sample_hull_weights(geometry, 6, 19)
    x = weights @ A
    assert np.all(nondominated_mask(evaluate(x, A), equality_tolerance=np.zeros(4)))
    for w, point in zip(np.vstack((np.eye(4), weights)), np.vstack((A, x)), strict=True):
        other = point + np.array([0.1, -0.2])
        scalar_gap = float((evaluate([other], A)[0] - evaluate([point], A)[0]) @ w)
        assert_allclose(scalar_gap, np.sum((other - point) ** 2), atol=8e-16, rtol=1e-14)
        assert scalar_gap > 0  # Includes zero weights at every individual anchor.


def test_uniform_coned_hull_volume_with_redundant_interior_anchor():
    a = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.1, 0.1]])
    geometry = hull_geometry(a)
    assert geometry.volume == pytest.approx(0.5, abs=1e-15)
    assert_allclose(geometry.cone_volumes.sum(), 0.5, atol=1e-15, rtol=0)
    assert geometry.condition > 0
    weights = sample_hull_weights(geometry, 13, 123)
    x = weights @ a
    assert weights.shape == (8192, 4) and np.all(weights >= 0)
    assert_allclose(weights.sum(axis=1), 1, atol=5e-16, rtol=0)
    assert_allclose(x.mean(axis=0), [1 / 3, 1 / 3], atol=4e-4, rtol=0)
    assert_allclose((x * x).mean(axis=0), [1 / 6, 1 / 6], atol=4e-4, rtol=0)
    assert np.all(x.sum(axis=1) <= 1 + 1e-15)
    assert not np.allclose(x.mean(axis=0), a.mean(axis=0), atol=0.01)
    boundary = sample_hull_weights(geometry, 10, 124, boundary=True) @ a
    slack = -(boundary @ geometry.equations[:, :-1].T + geometry.equations[:, -1])
    assert_allclose(slack.min(axis=1), 0, atol=3e-16, rtol=0)


def test_qhull_precision_fallback_is_explicit_and_never_joggles(monkeypatch):
    def fail(*args, **kwargs):
        assert "QJ" not in kwargs.get("qhull_options", "")
        raise QhullError("forced numerical precision fixture")

    monkeypatch.setattr(geo, "ConvexHull", fail)
    geometry = hull_geometry(A)
    assert geometry.volume is None and "NONUNIFORM_FALLBACK" in geometry.method
    assert "forced" in geometry.limitation
    assert_array_equal(geometry.anchors, A)
    for boundary in (False, True):
        w = sample_hull_weights(geometry, 5, 456, boundary=boundary)
        assert np.all(w >= 0)
        assert_allclose(w.sum(axis=1), 1, atol=5e-16, rtol=0)
        assert np.all(np.linalg.norm(w @ A, axis=1) <= 0.5 + 1e-15)


def test_geometry_rank_and_input_failures():
    for a in ([[1, 2], [2, 4], [3, 6]], [[np.nan, 1], [0, 0], [1, 1]], [[1]], np.zeros((2, 2))):
        with pytest.raises(ValueError):
            hull_geometry(a)
    for power, seed in ((0, 1), (True, 1), (3, -1), (3, True)):
        with pytest.raises(ValueError):
            unit_sobol(2, power, seed)
    for master, key, role in ((-1, "a", "b"), (True, "a", "b"), (1, "", "b"), (1, "a", "")):
        with pytest.raises(ValueError):
            seed_for(master, key, role)


def test_exact_analytic_ideal_nadir_and_unclipped_values():
    normalization = analytic_normalization(A)
    assert_array_equal(normalization.ideal, np.zeros(4))
    assert_array_equal(normalization.nadir, evaluate(A, A).max(axis=0))
    assert_array_equal(np.diag(evaluate(A, A)), np.zeros(4))
    assert_array_equal(normalization.transform(evaluate(A, A)).max(axis=0), np.ones(4))
    assert np.any(normalization.transform(evaluate([[1, 0]], A)) > 1)
    with pytest.raises(ValueError):
        analytic_normalization(np.zeros((4, 2)))
    with pytest.raises(ValueError):
        normalization.transform([[1, 2]])


def test_stable_identity_no_transitive_merging_and_nested_fps():
    x = [[0, 0], [0.75, 0], [1.5, 0]]
    assert_array_equal(unique_indices(x, 1), [0, 2])
    z = np.array([[0, 1], [1, 0], [0.5, 0.5], [0.2, 0.8], [0.8, 0.2]])
    assert_array_equal(partial_fps(z, 5, [0, 1]), farthest_order(z))
    assert_array_equal(partial_fps(z, 3, [0, 1]), partial_fps(z, 5, [0, 1])[:3])
    assert partial_fps(z, 5, [0, 1])[3] == 3
    for count, forced in (
        (6, [0]),
        (True, [0]),
        (3, []),
        (3, [0, 0]),
        (3, [-1]),
        (3, [9]),
        (3, [0.0]),
    ):
        with pytest.raises(ValueError):
            partial_fps(z, count, forced)
    with pytest.raises(ValueError):
        unique_indices([], 1e-12)
    with pytest.raises(ValueError):
        unique_indices(x, -1)


def test_strata_seed_independence_and_order_reproducibility():
    geometry = hull_geometry(A)
    first = candidates(CELL, geometry, 777)
    roles = (
        "candidate_interior",
        "candidate_boundary",
        "candidate_anchor_neighborhood",
        "independent_probe",
        "independent_boundary_probe",
    )
    forward = {
        r: sample_hull_weights(geometry, 5, seed_for(777, CELL.scenario_id, r)) for r in roles
    }
    reverse = {
        r: sample_hull_weights(geometry, 5, seed_for(777, CELL.scenario_id, r))
        for r in reversed(roles)
    }
    assert len({seed_for(777, CELL.scenario_id, r) for r in roles}) == 5
    for role in roles:
        assert_array_equal(forward[role], reverse[role])
    again = candidates(CELL, geometry, 777)
    assert_array_equal(first.decisions, again.decisions)
    assert_array_equal(first.weights, again.weights)
    assert_array_equal(first.decisions[:4], A)
    assert set(first.origins) == set(range(5))
    assert first.before_identity_count == 4 + 8192 + 4096 + 2048 + 6 * 17


@pytest.fixture(scope="module")
def reference_fixture():
    return generate_reference(CELL, A, 777)


def test_full_reference_certification_noiseless_oracle_only_and_nested_counts(reference_fixture):
    r = reference_fixture
    assert r.decisions.shape == (10000, 2) and r.responses.shape == (10000, 4)
    assert r.certificate["status"] == "CERTIFIED"
    assert r.certificate["apparent_tolerance_dominance_pairs"] == 0
    assert_array_equal(r.decisions[:4], A)
    assert_array_equal(r.responses, evaluate(r.decisions, A))
    assert_allclose(r.weights @ A, r.decisions, atol=2e-16, rtol=0)
    assert np.all(np.linalg.norm(r.decisions, axis=1) <= 2**0.5)
    for n in (2500, 5000, 10000):
        assert len(r.decisions[:n]) == n
        assert len(np.unique(r.decisions[:n], axis=0)) == n
    rows, probes = sensitivity(r, 777)
    assert [row["count"] for row in rows] == [2500, 5000, 10000]
    assert all(row["directed_to_dense_max"] == 0 for row in rows)
    assert rows[-1]["directed_from_dense_max"] == 0
    assert rows[0]["directed_from_dense_max"] > rows[1]["directed_from_dense_max"] > 0
    assert probes["probe_decisions"].shape == (4096, 2)
    assert not any(np.any(np.all(r.decisions == x, axis=1)) for x in probes["probe_decisions"][:10])
    assert rows[1]["boundary_count"] > 0


def test_simple_hull_vertices_are_all_on_true_front():
    for signs in product((-1, 1), repeat=2):
        point = np.array(signs, dtype=float) / 4
        assert np.all(
            nondominated_mask(evaluate(np.vstack((A, point)), A), equality_tolerance=np.zeros(4))
        )
