import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.synthetic import Scenario, evaluate, factorial_design, feasible, radius, sample_ball
from cnbi_v2.synthetic.model import frozen, real_array


def test_exact_squared_euclidean_distances_nonnegativity_and_minima():
    a = np.array([[0.0, 0.0], [0.5, -0.25], [-0.8, 0.4], [0.25, 0.7]])
    original = a.copy()
    x = np.array([[0.25, 0.5], [-0.3, -0.1]])
    expected = [
        [
            sum((float(xi) - float(ai)) ** 2 for xi, ai in zip(point, anchor, strict=True))
            for anchor in a
        ]
        for point in x
    ]
    assert_array_equal(evaluate(x, a), expected)
    assert (evaluate(x, a) >= 0).all()
    assert_array_equal(np.diag(evaluate(a, a)), np.zeros(len(a)))
    for j in range(len(a)):
        assert_allclose(evaluate([a[j] + [0.2, -0.4]], a)[0, j], 0.2**2 + 0.4**2)
    assert feasible(a, radius(2))
    assert_array_equal(a, original)
    assert not frozen(a).flags.writeable


@pytest.mark.parametrize("nx,expected", [(2, np.sqrt(2)), (3, 8**0.25), (5, 32**0.25)])
def test_dimension_specific_radius_and_uniform_volume_moments(nx, expected):
    assert radius(nx) == expected
    points = sample_ball(nx, 13, 90317)
    assert points.shape == (8192, nx) and feasible(points, expected)
    radial = np.linalg.norm(points, axis=1) / expected
    # Volume radial CDF, not surface-only or uniform radius/cube sampling.
    assert_allclose(np.mean(radial**nx), 0.5, atol=2e-4, rtol=0)
    assert_allclose(np.mean(radial**2), nx / (nx + 2), atol=8e-4, rtol=0)
    assert_allclose(points.mean(axis=0), 0, atol=0.004, rtol=0)
    assert_allclose(np.cov(points, rowvar=False), np.eye(nx) * expected**2 / (nx + 2), atol=0.008)
    assert radial.min() < 0.5 and radial.max() < 1
    assert_array_equal(points, sample_ball(nx, 13, 90317))
    assert not np.array_equal(points, sample_ball(nx, 13, 90318))


def test_factorial_design_and_order_independent_cell_seed_keys():
    cells = factorial_design()
    assert len(cells) == len(set(cells)) == 27
    assert len({c.scenario_id for c in cells}) == 27
    assert [c.ordinal for c in cells] == list(range(27))
    assert {(c.nx, c.delta, c.m) for c in cells} == {
        (2, 1, 4),
        (2, 3, 6),
        (2, 5, 8),
        (3, 1, 5),
        (3, 3, 7),
        (3, 5, 9),
        (5, 1, 7),
        (5, 3, 9),
        (5, 5, 11),
    }
    assert all(c.m > c.nx + 1 for c in cells)
    seeds = [s for c in cells for s in c.seeds(20261029)]
    assert len(seeds) == len(set(seeds)) == 81
    assert {c: c.seeds(20261029) for c in cells} == {c: c.seeds(20261029) for c in reversed(cells)}


@pytest.mark.parametrize(
    "nx,delta,target",
    [(1, 1, 0.25), (2, 0, 0.25), (2, 1, 0.5), (True, 1, 0.25), (2.0, 1, 0.25), (2, 3.0, 0.6)],
)
def test_invalid_scenario_factors(nx, delta, target):
    with pytest.raises(ValueError):
        Scenario(nx, delta, target)


@pytest.mark.parametrize(
    "nx,power,seed",
    [
        (4, 10, 1),
        (True, 10, 1),
        (2.0, 10, 1),
        (2, 3, 1),
        (2, 25, 1),
        (2, True, 1),
        (2, 10, -1),
        (2, 10, True),
    ],
)
def test_invalid_domain_configuration(nx, power, seed):
    with pytest.raises(ValueError):
        sample_ball(nx, power, seed)


@pytest.mark.parametrize(
    "points,anchors",
    [
        ([1, 2], [[0, 0]]),
        ([[1, 2]], [[0]]),
        ([], [[0, 0]]),
        ([[1j, 2]], [[0, 0]]),
        ([[np.inf, 2]], [[0, 0]]),
        ([[True, False]], [[0, 0]]),
    ],
)
def test_invalid_true_model_input(points, anchors):
    with pytest.raises(ValueError):
        evaluate(points, anchors)


def test_invalid_certificate_inputs_do_not_become_plausible_values():
    with pytest.raises(ValueError):
        feasible([[0, 0]], 0)
    with pytest.raises(ValueError):
        feasible([1, 2], 1)
    with pytest.raises(ValueError):
        real_array(["2"], "input")
