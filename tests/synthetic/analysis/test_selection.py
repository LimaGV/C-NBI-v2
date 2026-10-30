import numpy as np
import pytest
from numpy.testing import assert_array_equal

from cnbi_v2.synthetic.analysis.selection import equalized_indices, feasible_nd_indices


def test_equalization_real_points_extremes_small_k_and_raw_id_ties():
    z = np.array([[0, 3, 2], [3, 0, 2], [2, 3, 0], [1, 1, 1], [1, 1, 1.0]])
    ids = np.array([10, 20, 30, 40, 50])
    assert_array_equal(equalized_indices(z, ids, 2), [10, 20])
    assert_array_equal(equalized_indices(z, ids, 4), [10, 20, 30, 40])
    assert_array_equal(equalized_indices(z[::-1], ids[::-1], 4), [10, 20, 30, 40])
    assert len(equalized_indices(z, ids, 0)) == 0
    assert set(equalized_indices(z, ids, 5)) == set(ids)
    before = z.copy()
    equalized_indices(z, ids, 4)
    assert_array_equal(z, before)
    for raw_ids, count in (
        ([1, 1, 3, 4, 5], 2),
        ([-1, 2, 3, 4, 5], 2),
        ([1, 2], 2),
        (ids, 6),
        (ids, True),
        (ids.astype(float), 2),
    ):
        with pytest.raises(ValueError):
            equalized_indices(z, raw_ids, count)
    with pytest.raises(ValueError):
        equalized_indices(np.ones((5, 0)), ids, 2)


def test_feasibility_exact_epsilon_no_projection_identity_dominance():
    x = np.array([[1.0, 0], [1 + 2e-12, 0], [0, 0], [0, 0]])
    z = np.array([[0, 2], [1, 1], [2, 0], [2, 0.0]])
    before_x, before_z = x.copy(), z.copy()
    feasible, unique, nd = feasible_nd_indices(x, z, 1.0, 0.0)
    assert_array_equal(feasible, [True, False, True, True])
    assert_array_equal(unique, [0, 2])
    assert_array_equal(nd, [0, 2])
    feasible, unique, nd = feasible_nd_indices(x, z, 1.0, 1e-10)
    assert_array_equal(nd, [0, 1, 2])
    assert feasible.all()
    assert_array_equal(x, before_x)
    assert_array_equal(z, before_z)
    assert len(feasible_nd_indices([[2, 0]], [[0, 0]], 1, 0)[2]) == 0
    for alpha, epsilon in ((0, 0), (1, -0.1), (np.nan, 0), (1, np.nan)):
        with pytest.raises(ValueError):
            feasible_nd_indices(x, z, alpha, epsilon)
    with pytest.raises(ValueError):
        feasible_nd_indices(x, z[:1], 1, 0)
