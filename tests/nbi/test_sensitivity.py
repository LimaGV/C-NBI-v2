"""Numeric equality, exact dominance oracles and independently known distances."""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.nbi import (
    canonical_decision_points,
    directed_coverage_distances,
    nondominated_mask,
)


def test_deduplication_preserves_origin_to_canonical_mapping_without_chaining():
    points = [[0, 0], [0, 0], [1, 1], [1 + 1e-14, 1], [2, 2]]
    representatives, mapping = canonical_decision_points(points, tolerance=2e-14)
    assert_array_equal(representatives, [0, 2, 4])
    assert_array_equal(mapping, [0, 0, 2, 2, 4])
    reps, assigned = canonical_decision_points([[0], [1e-14], [2e-14]], tolerance=1.1e-14)
    assert_array_equal(reps, [0, 2])
    assert_array_equal(assigned, [0, 0, 2])


def test_full_space_dominance_needs_all_responses_and_no_strict_equal_point_dominance():
    values = [[0, 1, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 10]]
    assert_array_equal(nondominated_mask(values, block_size=2), [True, True, False, True, True])
    assert_array_equal(nondominated_mask(np.empty((0, 8))), [])
    assert_array_equal(nondominated_mask([[0, 0], [1e-16, 0]]), [True, True])
    assert_array_equal(
        nondominated_mask([[0, 0], [1e-16, 0]], equality_tolerance=[0, 0]), [True, False]
    )


def test_directed_and_reverse_distance_oracles_and_identical_sets():
    reference, coarse = [[0, 0], [3, 4], [6, 8]], [[0, 0], [6, 8]]
    assert_array_equal(directed_coverage_distances(reference, coarse, block_size=1), [0, 5, 0])
    assert_array_equal(directed_coverage_distances(coarse, reference), [0, 0])
    assert_allclose(directed_coverage_distances([[1, 1]], [[0, 0]]), [np.sqrt(2)])
    assert_array_equal(directed_coverage_distances(reference, reference), np.zeros(3))


def test_invalid_points_tolerances_blocks_and_empty_target_fail():
    for points in [[], [1, 2], [[np.inf]], np.empty((2, 0))]:
        with pytest.raises(ValueError):
            nondominated_mask(points)
    for tolerance in [-1, True, np.nan]:
        with pytest.raises(ValueError):
            canonical_decision_points([[0, 0]], tolerance=tolerance)
    for tolerance in [[0], [-1, 0]]:
        with pytest.raises(ValueError):
            nondominated_mask([[0, 0]], equality_tolerance=tolerance)
    with pytest.raises(ValueError):
        nondominated_mask([[0, 0]], block_size=0)
    for target in [np.empty((0, 2)), [[0]]]:
        with pytest.raises(ValueError):
            directed_coverage_distances([[0, 0]], target)
