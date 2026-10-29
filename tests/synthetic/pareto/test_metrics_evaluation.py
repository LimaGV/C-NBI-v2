import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.benchmark.hypervolume import HVGrid
from cnbi_v2.synthetic.design import Scenario
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.pareto.evaluation import METHODS, EvaluationContext, equalization_plan
from cnbi_v2.synthetic.pareto.hypervolume import FixedHypervolume, exact_small_union, orthant_hits
from cnbi_v2.synthetic.pareto.metrics import evaluate_metrics
from cnbi_v2.synthetic.pareto.normalization import analytic_normalization

A = np.array([[0.5, 0], [-0.5, 0], [0, 0.5], [0, -0.5]])
CELL = Scenario(2, 1, 0.25)


def test_p1_distance_and_local_density_oracles():
    hv = FixedHypervolume(2)
    result = evaluate_metrics([[0, 0], [1, 0], [3, 0]], [[0, 0], [2, 0]], hv)
    assert_allclose([result["GD"], result["IGD"]], [2 / 3, 0.5], atol=1e-15, rtol=0)
    assert_allclose(
        [result["Spacing"], result["Sparsity"]], [np.sqrt(1 / 3), 4 / 3], atol=1e-15, rtol=0
    )
    separated = evaluate_metrics([[0, 0], [1, 0]], [[0, 1], [1, 1]], hv)
    assert separated["GD"] == separated["IGD"] == 1
    own = evaluate_metrics([[0, 0], [1, 0]], [[0, 0], [1, 0]], hv)
    assert own["GD"] == own["IGD"] == 0
    for values in ([[0.2, 0.2]], [[0.2, 0.2], [0.2, 0.2]]):
        one = evaluate_metrics(values, [[0, 0]], hv)
        assert one["Spacing"] is None and one["Sparsity"] is None
    with pytest.raises(ValueError):
        evaluate_metrics([[0, 0]], [[0, 0, 0]], hv)


@pytest.mark.parametrize("m", range(4, 12))
def test_exact_hv_known_boxes_and_tiny_volume(m):
    hv = FixedHypervolume(m)
    single = np.full((1, m), 0.2)
    assert_allclose(hv.estimate(single)["HV"], 0.9**m, atol=0, rtol=3e-15)
    tiny = np.full((1, m), 0.8)
    assert_allclose(hv.estimate(tiny)["HV"], 0.3**m, atol=0, rtol=5e-15)
    boxes = np.full((2, m), 0.15)
    boxes[0, 0], boxes[1, 1] = 0.45, 0.45
    expected = 2 * 0.65 * 0.95 ** (m - 1) - 0.65**2 * 0.95 ** (m - 2)
    result = hv.estimate(boxes)
    assert result["HV_status"] == "EXACT_UP_TO_FLOAT64"
    assert_allclose(result["HV"], expected, atol=0, rtol=6e-15)
    assert hv.estimate(boxes[:1])["HV"] <= result["HV"]
    none = hv.estimate(np.full((2, m), 1.2))
    assert none["HV"] == 0 and none["HV_status"] == "ZERO_CONTRIBUTION_CERTIFIED"


def test_orthant_acceleration_matches_every_original_indicator():
    rng = np.random.Generator(np.random.PCG64(17))
    a = rng.uniform(0.05, 1, size=(100, 4))
    u = rng.uniform(0, 1.1, size=(512, 4))
    expected = np.any(np.all(a[:, None, :] <= u[None, :, :], axis=2), axis=0)
    assert_array_equal(orthant_hits(a, u), expected)
    assert_array_equal(orthant_hits(a[::-1], u), expected)
    assert_array_equal(orthant_hits(np.repeat(a[:1], 100, axis=0), u), np.all(a[0] <= u, axis=1))
    with pytest.raises(ValueError):
        orthant_hits(a, [[0, 0]])
    grid = HVGrid(np.zeros(4), np.full(4, 1.1), 13, (11, 12, 13, 14))
    samples = grid.samples()
    mask = np.bitwise_or.reduce(grid.masks(a[:3], samples), axis=0)
    assert_array_equal(np.packbits(orthant_hits(a[:3], samples), bitorder="little"), mask)


def test_qmc_prefix_study_precision_and_common_samples():
    points = np.column_stack((np.linspace(0.1, 0.9, 9), np.linspace(0.9, 0.1, 9)))
    hv = FixedHypervolume(2)
    rows = hv.study(points)
    assert [r["power"] for r in rows] == [13, 14, 15, 16]
    assert rows[-1]["qmc_status"] == "PRECISION_CRITERIA_PASSED"
    assert hv.estimate(points)["HV_method"] == "scrambled Sobol indicator estimate"
    assert_array_equal(hv.grid.samples(), FixedHypervolume(2).grid.samples())
    larger = hv.study(np.vstack((points, [0.1, 0.1])))
    assert all(b["HV_QMC"] >= a["HV_QMC"] for a, b in zip(rows, larger, strict=True))
    assert hv.study([[1.2, 0]])[-1]["qmc_status"] == "ZERO_CONTRIBUTION_CERTIFIED"


def test_artificial_zero_is_pending_not_a_false_precision_claim(monkeypatch):
    monkeypatch.setattr(HVGrid, "samples", lambda g: np.zeros((4 * 2**g.power, len(g.lower))))
    points = np.column_stack((np.linspace(0.1, 0.9, 9), np.linspace(0.9, 0.1, 9)))
    result = FixedHypervolume(2).estimate(points)
    assert result["HV"] == 0 and result["HV_status"] == "UNRESOLVED_ZERO_HITS"


@pytest.mark.parametrize("m,power", [(True, 16), (1, 16), (4, 12), (4, True), (4, 21)])
def test_invalid_hv_configuration(m, power):
    with pytest.raises(ValueError):
        FixedHypervolume(m, power=power)


def test_invalid_hv_points():
    for a in ([[-1, 0]], [[0, 0, 0]]):
        with pytest.raises(ValueError):
            FixedHypervolume(2).estimate(a)
        with pytest.raises(ValueError):
            FixedHypervolume(2).study(a)
    with pytest.raises(ValueError):
        exact_small_union(np.ones((9, 2)))


def context():
    normalization = analytic_normalization(A)
    reference = normalization.transform(evaluate(np.vstack((A, [[0, 0]])), A))
    return EvaluationContext(CELL, A, normalization, reference, FixedHypervolume(4))


def test_raw_feasible_unique_full_space_nd_counts_and_replica_normalization():
    ctx = context()
    x = np.array([[0.5, 0], [0.5, 0], [0, 0], [1, 0], [2, 0]])
    original = x.copy()
    results = [
        ctx.evaluate(CELL.scenario_id, r, "C-NBI", x, {"fixture": True}, seconds=0.5, nfe=5)
        for r in range(1, 6)
    ]
    for result in results:
        assert_array_equal(result.raw_decisions, original)
        assert_array_equal(x, original)
        assert result.diagnostics["raw_count"] == 5
        assert result.diagnostics["feasible_count"] == 4
        assert result.diagnostics["unique_count"] == 3
        assert result.diagnostics["nondominated_count"] == 2
        assert_array_equal(result.nondominated_indices, [0, 2])
        assert np.any(result.normalized_responses > 1)
        assert_array_equal(result.normalized_responses, results[0].normalized_responses)
        assert not result.diagnostics["raw_decisions_modified"]
        assert not result.diagnostics["oracle_feedback_to_search"]
    singleton = ctx.evaluate(CELL.scenario_id, 1, "MOEA/D", [[0.5, 0]], {})
    assert singleton.metrics["Spacing"] is None
    empty = ctx.evaluate(CELL.scenario_id, 1, "NSGA-III", np.empty((0, 2)), {})
    assert all(empty.metrics[k] is None for k in ("GD", "IGD", "HV", "Spacing", "Sparsity"))
    infeasible = ctx.evaluate(CELL.scenario_id, 1, "VRF-NBI", [[3, 0]], {})
    assert infeasible.diagnostics["feasible_count"] == 0 and infeasible.metrics["GD"] is None


def test_invalid_evaluation_and_equalization_is_only_a_plan():
    ctx = context()
    for sid, replica, method in (
        ("missing", 1, "C-NBI"),
        (CELL.scenario_id, 0, "C-NBI"),
        (CELL.scenario_id, True, "C-NBI"),
        (CELL.scenario_id, 1, "unknown"),
    ):
        with pytest.raises(ValueError):
            ctx.evaluate(sid, replica, method, [[0, 0]], {})
    for x in ([[np.nan, 0]], [[np.inf, 0]], [[0, 0, 0]]):
        with pytest.raises(ValueError):
            ctx.evaluate(CELL.scenario_id, 1, "C-NBI", x, {})
    for kwargs in ({"seconds": -1}, {"nfe": True}, {"nfe": -1}):
        with pytest.raises(ValueError):
            ctx.evaluate(CELL.scenario_id, 1, "C-NBI", [[0, 0]], {}, **kwargs)
    with pytest.raises(ValueError):
        ctx.evaluate(CELL.scenario_id, 1, "C-NBI", [[0, 0]], {"x": np.nan})
    plan = equalization_plan(CELL.scenario_id, 1, dict(zip(METHODS, (10, 20, 30, 40), strict=True)))
    assert plan["target_count"] == 10 and plan["status"] == "PLAN_ONLY_NOT_EXECUTED"
    with pytest.raises(ValueError):
        equalization_plan(CELL.scenario_id, 1, {"C-NBI": 5})


def test_offline_nd_uses_the_last_objectives_as_well_as_the_first():
    a = np.array([[0.5, 0], [-0.5, 0], [0.1, 0.5], [-0.1, 0.5]])
    norm = analytic_normalization(a)
    reference = norm.transform(evaluate(a, a))
    ctx = EvaluationContext(CELL, a, norm, reference, FixedHypervolume(4))
    x = np.array([[0, -0.25], [0, 0.25]])
    responses = evaluate(x, a)
    assert_array_equal(responses[0, :2], responses[1, :2])
    assert np.all(responses[1, 2:] < responses[0, 2:])
    result = ctx.evaluate(CELL.scenario_id, 1, "C-NBI", x, {"fixture": True})
    assert_array_equal(result.nondominated_indices, [1])
