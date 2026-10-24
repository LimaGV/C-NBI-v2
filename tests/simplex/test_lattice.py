"""Stars-and-bars and exact rational nesting, independent of optimizer output."""

from math import comb

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.simplex import nested_indices, simplex_lattice


@pytest.mark.parametrize("k,H", [(2, 2), (3, 2), (3, 10), (2, 20), (3, 20), (4, 5)])
def test_counts_simplex_integer_identity_deterministic_order(k, H):
    lattice = simplex_lattice(k, H)
    assert len(lattice.weights) == comb(H + k - 1, k - 1)
    assert_array_equal(lattice.compositions.sum(axis=1), np.full(len(lattice.weights), H))
    assert np.all(lattice.weights >= 0)
    assert_allclose(lattice.weights.sum(axis=1), 1, rtol=0, atol=3e-16)
    rows = list(map(tuple, lattice.compositions))
    assert rows == sorted(set(rows))
    assert_array_equal(lattice.weights, lattice.compositions / H)
    assert_array_equal(lattice.weights, simplex_lattice(k, H).weights)
    with pytest.raises(ValueError):
        lattice.compositions[0, 0] = 1
    with pytest.raises(ValueError):
        lattice.weights.setflags(write=True)


def test_explicit_pair_weights_and_all_requested_total_counts():
    assert_array_equal(simplex_lattice(2, 2).weights, [[0, 1], [0.5, 0.5], [1, 0]])
    assert [
        19 * len(simplex_lattice(2, h).weights) + 18 * len(simplex_lattice(3, h).weights)
        for h in [2, 4, 5, 10, 20]
    ] == [165, 365, 492, 1397, 4557]


@pytest.mark.parametrize("k", [2, 3, 4])
@pytest.mark.parametrize("H", [2, 4, 5, 10, 20])
def test_parent_membership_uses_exact_integer_compositions(k, H):
    parent, child = simplex_lattice(k, 20), simplex_lattice(k, H)
    indices = nested_indices(parent, H)
    assert_array_equal(parent.compositions[indices], child.compositions * (20 // H))
    assert len(indices) == comb(H + k - 1, k - 1)
    assert_array_equal(parent.weights[indices], child.weights)


@pytest.mark.parametrize("k,H", [(1, 2), (2, 0), (True, 2), (2, True), (2.0, 2), (2, 2.5)])
def test_invalid_lattice_and_non_nested_resolution_fail(k, H):
    with pytest.raises(ValueError):
        simplex_lattice(k, H)
    with pytest.raises(ValueError, match="divide"):
        nested_indices(simplex_lattice(2, 20), 3)
