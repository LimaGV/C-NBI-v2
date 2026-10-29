"""Actual frozen cases reaching500 iterations must retain v1's last iterate."""

from pathlib import Path

import numpy as np
import pytest

from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs
from cnbi_v2.synthetic.benchmark.vrf_runner import factor_analysis, run_vrf

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("replica", [4, 5])
def test_iteration_limit_matches_factor_analyzer_v1_oracle(replica):
    key = f"nx2_delta1_rho085__replica{replica}"
    data = load_search_inputs(ROOT/"results/phase_10_synthetic_rsm/rsm_20261029")[key]
    result = factor_analysis(data.observed, 2)
    assert result["varimax_iterations"] == 500
    assert not result["varimax_converged"]
    with np.load(Path(__file__).parent/"fixtures/varimax_v1_iteration_limit.npz") as expected:
        np.testing.assert_allclose(result["loadings"], expected[key+"__loadings"],
                                   atol=2e-14, rtol=2e-14)
        np.testing.assert_allclose(result["weights"], expected[key+"__weights"],
                                   atol=2e-14, rtol=2e-14)
    output = run_vrf(data, 517+replica)
    output.validate(data)
    assert output.status == "COMPLETED"
    assert not output.diagnostics["varimax_converged"]
    assert len(output.decisions) > 0
