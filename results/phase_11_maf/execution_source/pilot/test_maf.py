"""Small Phase 11 function, geometry, seed and V2 solver gates."""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.chim import nominal_normalization
from cnbi_v2.maf import MaF, anchors, metrics, run, spectral_screen
from cnbi_v2.optimization import Direction


@pytest.mark.parametrize('number', [8, 9])
@pytest.mark.parametrize('m', [4, 6, 8, 10, 15])
def test_equations_domain_and_derivatives(number, m):
    p = MaF(number, m)
    assert_allclose(p.values([0., 0.]), 1. if number == 8 else np.cos(np.pi/m), atol=8e-16)
    assert p.feasible(p.vertices).all()
    assert p.feasible([[10000, 10000]])[0]
    assert not p.feasible([[10000.1, 0]])[0]
    x, f = p.sample(500, 101)
    assert p.feasible(x).all()
    assert_array_equal(f, p.values(x))
    xx, ff = p.sample(500, 101)
    assert_array_equal(x, xx)
    assert_array_equal(f, ff)
    probe = np.array([.125, -.23])
    h = 1e-6
    finite = np.column_stack([(p.values(probe+h*e)-p.values(probe-h*e))/(2*h)
                              for e in np.eye(2)])
    assert_allclose(p.jacobian(probe), finite, atol=3e-10, rtol=3e-9)
    if number == 9 and p.polygons:
        outside = [q.mean(axis=0) for q in p.polygons]
        assert not p.feasible(outside).all()
        assert all((p.margin(t)[0] >= 0) == p.feasible(t)[0] for t in outside)


@pytest.mark.parametrize('number', [8, 9])
def test_payoff_permutation_and_selection(number):
    p = MaF(number, 4)
    x, payoff, _ = anchors(p, 101)
    assert p.feasible(x).all()
    assert_allclose(np.diag(payoff), 0, atol=1e-10)
    n = nominal_normalization(payoff, (Direction.MIN,)*4)
    assert_allclose(np.diag(n.normalize(payoff)), 0, atol=1e-15)
    s, repeated = spectral_screen(p, payoff, 101), spectral_screen(p, payoff, 101)
    assert s['rank'] == 2
    assert s['null'].shape == (1000, 4)
    assert_array_equal(s['null'], repeated['null'])
    assert_array_equal(s['q95'], repeated['q95'])
    assert len(s['subsets']) == 10
    assert any(t['selected'] for t in s['subsets'])


@pytest.mark.parametrize('number', [8, 9])
def test_small_direct_nbi_pilot(number):
    a, b = run(number, 4, 101), run(number, 4, 101)
    assert_array_equal(a['X'], b['X'])
    assert_array_equal(a['F'], b['F'])
    assert a['geometry_failures'] == []
    accepted = [r for r in a['subproblems'] if r['accepted']]
    assert accepted and all(r['eq_l2'] <= 1e-5 for r in accepted)
    assert MaF(number, 4).feasible(a['X']).all()
    assert len(a['nd']) > 2


def test_metric_protocol():
    a = np.array([[0., 1.], [.3, .6], [1., 0.]])
    result = metrics(a, a, 101)
    assert result['GD'] == result['IGD'] == 0
    assert result['HV'] > 0
    d = np.array([.5, .5, np.sqrt(.85)])
    assert_allclose(result['Spacing'], d.std(ddof=0))
    assert_allclose(result['Sparsity'], d.mean())
