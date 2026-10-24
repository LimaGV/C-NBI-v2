"""Independent small oracles; no real campaign rerun in the test suite."""

from dataclasses import replace

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation import turning_reference_campaign as workflow

from cnbi_v2.reference import CanonicalProblem, EAConfig, radial_repair, run_evolutionary
from cnbi_v2.reference.evolutionary import BallSampling, RSMAdapter, SphereRepair
from cnbi_v2.reference.indicators import additive_epsilon, diagnostics, distances
from cnbi_v2.reference.leave_one_out import reference
from cnbi_v2.reference.pools import Origin, PointPool, front


@pytest.fixture
def problem():
    b = np.zeros((10, 8))
    b[0] = np.arange(8)
    b[1:4, :3] = np.eye(3)
    b[4:7, 3:6] = np.eye(3)
    b[7:, 6:] = [[1., 0.], [0., 1.], [1., 1.]]
    return CanonicalProblem(b, np.array([1., -1.]*4), np.arange(8.), np.ones(8), 2.)


def pool(family, points, label="run"):
    z = np.pad(np.array(points, dtype=float), ((0, 0), (0, 6)))
    x = np.column_stack([z[:, :2], np.zeros(len(z))])
    return PointPool(x, z, z, tuple((Origin(family, label, str(i)),) for i in range(len(z))))


def test_canonical_matrix_scalar_normalization_and_immutability(problem):
    x = np.random.default_rng(123).uniform(-1, 1, (20, 3))
    assert_allclose(problem.natural(x), problem.natural(x, scalar_check=True), atol=5e-15)
    f = problem.natural(x)
    assert_array_equal(problem.normalize(f), (f*problem.signs-problem.utopia)/problem.amplitudes)
    assert not problem.coefficients.flags.writeable
    assert problem.feasible([[0, 0, 0], [2, 0, 0]]).all()
    assert not problem.feasible([[2, 1, 0]]).any()
    assert np.max(problem.normalize(f)) > 1  # no clipping
    assert problem.natural(np.empty((0, 3)), scalar_check=True).shape == (0, 8)


@pytest.mark.parametrize("kwargs", [
    {"coefficients": np.zeros((9, 8))}, {"alpha": 0}, {"alpha": np.nan},
    {"sphere_tolerance": -1}, {"amplitudes": np.zeros(8)}, {"signs": np.zeros(8)},
    {"utopia": np.zeros(7)}, {"amplitudes": np.full(8, np.nan)}])
def test_invalid_canonical(problem, kwargs):
    with pytest.raises(ValueError):
        replace(problem, **kwargs)


@pytest.mark.parametrize("bad", [[[0, 0]], [0, 0, 0], [[np.inf, 0, 0]]])
def test_invalid_points(problem, bad):
    with pytest.raises(ValueError):
        problem.natural(bad)
    with pytest.raises(ValueError):
        radial_repair(bad, 2.)


def test_bad_normalization_shape(problem):
    with pytest.raises(ValueError):
        problem.normalize(np.zeros((4, 7)))


def test_radial_repair_and_sampling(problem):
    x = np.array([[0, 0, 0], [3, 4, 0], [1, 1, 0.]])
    result = radial_repair(x, 2.)
    assert_allclose(result, [[0, 0, 0], [1.2, 1.6, 0], [1, 1, 0]])
    assert_array_equal(x[1], [3, 4, 0])
    repaired = SphereRepair(2.)
    assert_allclose(repaired._do(None, x), result)
    assert repaired.repaired_candidates == 1
    for radius in (0, -1, np.nan):
        with pytest.raises(ValueError):
            radial_repair(x, radius)
    samples = BallSampling(2.)._do(None, 20000, random_state=np.random.default_rng(12))
    assert problem.feasible(samples).all()
    # For a uniform 3-ball, (r/alpha)^3 is uniform, mean1/2, E[x]=0.
    assert abs(np.mean((np.linalg.norm(samples, axis=1)/2)**3)-.5) < .01
    assert np.max(np.abs(samples.mean(axis=0))) < .02


@pytest.mark.parametrize("family", ["NSGA3", "MOEAD"])
def test_small_ea_seed_budget_feasibility_and_current_responses(problem, family):
    config = EAConfig(family, n_partitions=1, generations=3)
    a, b = (run_evolutionary(problem, config, 101) for _ in range(2))
    assert a["nfe"] == config.nfe_max == 24
    assert a["population"] == 8
    assert problem.feasible(a["x"]).all()
    assert_array_equal(a["x"], b["x"])
    assert_array_equal(a["natural_f"], b["natural_f"])
    assert_allclose(a["natural_f"], problem.natural(a["x"], scalar_check=True), atol=5e-15)
    assert_allclose(a["optimizer_f"], problem.normalize(a["natural_f"]))
    assert a["repair_operations"] >= 0


@pytest.mark.parametrize("kwargs", [
    {"family": "UNKNOWN"}, {"generations": 0}, {"n_partitions": -1},
    {"n_neighbors": 0}, {"sbx_probability": 0}, {"prob_neighbor_mating": 2},
    {"sbx_eta": np.nan}, {"pm_eta": -1}])
def test_invalid_ea_configuration(kwargs):
    with pytest.raises(ValueError):
        EAConfig(**({"family": "NSGA3"} | kwargs))


def test_adapter_ceiling_and_sphere_guard(problem):
    adapter = RSMAdapter(problem, 1)
    out = {}
    adapter._evaluate(np.zeros((1, 3)), out)
    assert_array_equal(out["natural_F"], problem.natural(np.zeros((1, 3))))
    with pytest.raises(RuntimeError, match="ceiling"):
        adapter._evaluate(np.zeros((1, 3)), {})
    with pytest.raises(ValueError, match="infeasible"):
        RSMAdapter(problem, 3)._evaluate(np.array([[3., 0., 0.]]), {})


def test_known_union_shared_provenance_and_revival():
    a = pool("A", [[0, 1], [1, 0]])
    b = pool("B", [[0, 1], [1, 1], [2, 0]])
    c = pool("C", [[.5, .5], [3, 3]])
    settings = dict(x_tolerance=1e-14, dominance_tolerance=np.zeros(8))
    all_front = reference({"A": a, "B": b, "C": c}, **settings)
    assert len(all_front.x) == 3
    assert {o.family for o in all_front.origins[0]} == {"A", "B"}
    minus = reference({"A": a, "B": b, "C": c}, excluded="A", **settings)
    assert len(minus.x) == 3  # B(2,0) revives, previously dominated by A(1,0)
    assert any(np.array_equal(p[:2], [2, 0]) for p in minus.z)
    assert all(o.family != "A" for g in minus.origins for o in g)
    assert {o.family for o in minus.origins[0]} == {"B"}
    with pytest.raises(ValueError, match="homogeneous"):
        reference({"A": all_front, "B": b}, excluded="A", **settings)
    with pytest.raises(ValueError, match="absent"):
        reference({"A": a}, excluded="C", **settings)
    with pytest.raises(ValueError, match="at least one"):
        reference({"A": a}, excluded="A", **settings)


def test_entire_cnbi_family_excluded_and_roundoff_shared_coordinate():
    h5 = pool("CNBI", [[0, 1]], "H5")
    h20 = pool("CNBI", [[1, 0]], "H20")
    shared = pool("NSGA3", [[0, 1]])
    settings = dict(x_tolerance=1e-14, dominance_tolerance=np.zeros(8))
    cnbi = front([h5, h20], **settings)
    minus = reference({"CNBI": cnbi, "NSGA3": shared}, excluded="CNBI", **settings)
    assert len(minus.x) == 1
    assert all(o.family == "NSGA3" for g in minus.origins for o in g)
    # Exclusion before dedup retains B's own slightly different coordinate.
    shifted = PointPool(shared.x+2e-15, shared.f, shared.z, shared.origins)
    minus = reference({"CNBI": h5, "NSGA3": shifted}, excluded="CNBI", **settings)
    assert_array_equal(minus.x, shifted.x)


def test_pool_validation():
    a = pool("A", [[0, 1]])
    with pytest.raises(ValueError, match="dimensions"):
        replace(a, x=np.zeros((2, 3)))
    with pytest.raises(ValueError, match="origin"):
        replace(a, origins=((),))


@pytest.mark.parametrize("seed", range(6))
def test_indicator_oracles(seed):
    rng = np.random.default_rng(seed)
    a, b = rng.normal(size=(9, 8)), rng.normal(size=(13, 8))
    brute_dist = np.linalg.norm(a[:, None]-b[None], axis=2)
    brute_epsilon = np.max(np.min(np.max(a[:, None]-b[None], axis=2), axis=0))
    assert_allclose(distances(a, b), brute_dist.min(axis=1), atol=1e-15)
    assert_allclose(additive_epsilon(a, b), brute_epsilon, atol=0, rtol=0)
    d = diagnostics(a, b)
    assert_allclose(d["GD_p1"], brute_dist.min(axis=1).mean())
    assert_allclose(d["IGD_p1"], brute_dist.min(axis=0).mean())
    assert_allclose(d["hausdorff_reference_to_candidate"], brute_dist.min(axis=0).max())
    assert additive_epsilon([[0, 0]], [[1, 2]]) == -1
    assert additive_epsilon(a, a) == 0


@pytest.mark.parametrize("a,b", [([], []), ([[1, 2]], [[1]]), ([[np.nan]], [[1]])])
def test_invalid_indicators(a, b):
    with pytest.raises(ValueError):
        diagnostics(a, b)


def test_frozen_case_recovery_vrf_and_roundtrip(tmp_path):
    p, xtol, tau = workflow.load_problem()
    raw, h5, counts = workflow.materialize_h(p, 5)
    assert (len(raw.x), counts["unique"], len(h5.x)) == (492, 411, 408)
    vrf = workflow.materialize_vrf(p)
    assert len(vrf.x) == 66 and p.feasible(vrf.x).all()
    assert_allclose(vrf.f, p.natural(vrf.x, scalar_check=True), atol=0, rtol=0)
    path = tmp_path / "pool.npz"
    workflow.save_pool(path, h5)
    recovered = workflow.load_pool(path)
    assert_array_equal(h5.x, recovered.x)
    assert h5.origins == recovered.origins
    target = reference({"CNBI": h5, "VRF": front([vrf], xtol, tau)}, excluded="CNBI",
                       x_tolerance=xtol, dominance_tolerance=tau)
    assert all(o.family != "CNBI" for group in target.origins for o in group)
