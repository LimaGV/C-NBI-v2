"""Canonical identity and small real NBI checks without upstream recomputation."""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from scripts.validation import turning_local_nbi as workflow

from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import LocalNBIProblem, local_nbi_geometry, solve_nbi_lattice
from cnbi_v2.simplex import simplex_lattice


def test_frozen_selection_models_and_all_local_geometries():
    models, anchors, payoff, _, amplitudes, _, tolerance, catalog = workflow.verified_inputs()
    assert len(models) == 8 and len(catalog) == 37
    assert [sum(len(c) == k for _, c in catalog) for k in (2, 3, 4)] == [19, 18, 0]
    different_local_scale = False
    for _, indices in catalog:
        geometry = local_nbi_geometry(
            payoff[np.ix_(indices, indices)],
            [workflow.DIRECTIONS[j] for j in indices],
            optimality_tolerance=tolerance[list(indices)],
        )
        problem = LocalNBIProblem(
            tuple(models[j] for j in indices), geometry, anchors[list(indices)], workflow.ALPHA
        )
        assert geometry.orientation_dot < 0 and np.all(geometry.normalization.amplitudes > 0)
        assert geometry.orthogonality_residual < 1e-13
        different_local_scale |= not np.array_equal(
            geometry.normalization.amplitudes, amplitudes[list(indices)]
        )
        for j, point in enumerate(problem.anchors):
            assert_allclose(
                problem.residual(np.r_[point, 0.0], np.eye(len(indices))[j]), 0, atol=2e-13
            )
    assert different_local_scale


def test_small_real_nbi_does_not_draw_fit_reoptimize_or_repeat_pa(monkeypatch):
    import cnbi_v2.chim as chim
    import cnbi_v2.model as model
    import cnbi_v2.optimization as optimization
    import cnbi_v2.uncertainty.coefficient_sampling as sampling

    def forbidden(*args, **kwargs):
        pytest.fail("upstream scientific computation attempted in local NBI")

    for name in ["compute_chim_spectra", "evaluate_pa_prefixes"]:
        monkeypatch.setattr(chim, name, forbidden)
    monkeypatch.setattr(np.random, "Generator", forbidden)
    monkeypatch.setattr(model, "fit_multivariate_rsm", forbidden)
    monkeypatch.setattr(optimization, "solve_quadratic_ball", forbidden)
    monkeypatch.setattr(sampling, "sample_coefficient_ensemble", forbidden)
    before = {p: (sha256_file(p), p.stat().st_mtime_ns) for p in workflow.INPUT_HASHES}
    models, anchors, payoff, _, _, _, tolerance, catalog = workflow.verified_inputs()
    for _, indices in (catalog[0], catalog[19]):
        geometry = local_nbi_geometry(
            payoff[np.ix_(indices, indices)],
            [workflow.DIRECTIONS[j] for j in indices],
            optimality_tolerance=tolerance[list(indices)],
        )
        problem = LocalNBIProblem(
            tuple(models[j] for j in indices), geometry, anchors[list(indices)], workflow.ALPHA
        )
        result = solve_nbi_lattice(problem, simplex_lattice(len(indices), 2))
        assert all(s.accepted for s in result.solutions)  # Specific nine-point regression case.
    assert before == {p: (sha256_file(p), p.stat().st_mtime_ns) for p in workflow.INPUT_HASHES}


def test_bad_input_hash_invalid_run_id_and_nonempty_output_fail(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="run_id"):
        workflow.run_local_nbi(tmp_path, run_id="../invalid")
    (tmp_path / "existing.txt").write_text("existing")
    with pytest.raises(FileExistsError):
        workflow.run_local_nbi(tmp_path, run_id="existing")
    monkeypatch.setitem(workflow.INPUT_HASHES, workflow.SELECTED, "0" * 64)
    with pytest.raises(ValueError, match="SHA-256"):
        workflow.verified_inputs()
