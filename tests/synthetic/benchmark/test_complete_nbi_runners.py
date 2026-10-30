"""Exercise complete scientific kernels on frozen inputs, without truth feedback."""

from dataclasses import replace
from math import comb
from pathlib import Path

import numpy as np

from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs
from cnbi_v2.synthetic.benchmark.runner import run_method

ROOT = Path(__file__).resolve().parents[3]


def test_complete_cnbi_uses_joint_2000_and_all_candidates():
    data = load_search_inputs(ROOT/"results/phase_10_synthetic_rsm/rsm_20261029")[
        "nx2_delta1_rho025__replica1"]
    before = data.model.coefficients.copy()
    output = run_method(data, "C-NBI", 90211)
    output.validate(data)
    np.testing.assert_array_equal(before, data.model.coefficients)
    d = output.diagnostics
    assert d["B"] == 2000 and d["candidate_subsets"] == comb(4, 2)+comb(4, 3)
    assert d["all_mc_payoffs_valid"]
    assert output.arrays["coefficient_samples"].shape == (2000, 6, 4)
    assert output.counters["quadratic_ball_solves"] == 2001*4
    assert d["selected_subsets"] >= 1 and len(output.decisions) >= 1
    for subset in d["subsets"][1:]:
        assert subset["selected"] == bool(np.all(subset["component_passes"]))
        assert subset["selected"] == bool(np.all(subset["observed"] > subset["q95"]))
    assert d["original_objective_count"] == 4
    assert output.counters["nbi_subproblems"] == len(d["subproblems"])
    assert output.counters["scalar_quadratic_values"] > len(output.decisions)
    assert output.counters["quadratic_response_vector_calls"] > 2000*data.m
    assert output.counters["model_vector_point_events"] > 2000*data.m
    assert output.counters["original_full_vector_points_computed"] == 2*len(output.decisions)
    assert abs(output.timings["total"]-sum(output.timings[k] for k in
                                          ("preparation", "solver", "postprocessing"))) < 1e-12


def test_vrf_complete_and_deterministic_without_original_refit():
    data = load_search_inputs(ROOT/"results/phase_10_synthetic_rsm/rsm_20261029")[
        "nx3_delta3_rho060__replica1"]
    first = run_method(data, "VRF-NBI", 317)
    second = run_method(data, "VRF-NBI", 317)
    first.validate(data)
    np.testing.assert_array_equal(first.decisions, second.decisions)
    assert first.diagnostics["retained_variance"] >= .9
    k = first.diagnostics["n_factors"]
    assert first.arrays["factor_coefficients"].shape == (10, k)
    assert first.arrays["factor_residuals"].shape == (19, k)
    assert first.counters["vrf_jacobian_calls"] > 0
    assert first.counters["extreme_solves"] > k
    np.testing.assert_allclose(first.diagnostics["variance"],
                               np.sum(first.diagnostics["loadings"]**2, axis=0), rtol=0, atol=0)
    assert len(first.diagnostics["factor_diagnostics"]["responses"]) == k
    from cnbi_v2.model import quadratic_design
    factors = quadratic_design(first.decisions)@first.arrays["factor_coefficients"]
    published = (factors-first.diagnostics["targets"])**2+first.diagnostics["variance"]
    published_z = ((published-first.diagnostics["utopia"])
                   /(first.diagnostics["nadir"]-first.diagnostics["utopia"]))
    internal = published+first.diagnostics["optimization_gauge_shift"]
    internal_z = ((internal-first.diagnostics["optimization_gauge_utopia"])
                  /(first.diagnostics["optimization_gauge_nadir"]
                    -first.diagnostics["optimization_gauge_utopia"]))
    np.testing.assert_allclose(published_z, internal_z, rtol=2e-14, atol=2e-14)


def test_vrf_structural_invalid_is_not_clamped():
    original = load_search_inputs(ROOT/"results/phase_10_synthetic_rsm/rsm_20261029")[
        "nx2_delta1_rho025__replica1"]
    rng = np.random.default_rng(7)
    matrix = rng.normal(size=original.observed.shape)
    orthogonal, _ = np.linalg.qr(matrix-matrix.mean(0))
    data = replace(original, observed=orthogonal)
    result = run_method(data, "VRF-NBI", 1)
    assert result.status == "VRF_STRUCTURALLY_INVALID"
    assert result.diagnostics["n_factors"] == 4
    assert result.decisions.shape == (0, 2)
