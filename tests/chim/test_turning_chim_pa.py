"""Real artifact contract, direct independent spectral checks and frozen policy."""

import csv
import json

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation import turning_chim_pa as workflow

from cnbi_v2.data import sha256_file


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


@pytest.fixture(scope="module")
def real_pa(tmp_path_factory):
    output = tmp_path_factory.mktemp("chim_pa")
    before = {p: (sha256_file(p), p.stat().st_mtime_ns) for p in workflow.INPUT_HASHES}
    with pytest.MonkeyPatch.context() as patch:
        import cnbi_v2.model as model
        import cnbi_v2.optimization as optimization
        import cnbi_v2.uncertainty as uncertainty
        import cnbi_v2.uncertainty.anchor_reoptimization as anchor_mc
        import cnbi_v2.uncertainty.coefficient_sampling as coefficient_mc
        def forbidden(*args, **kwargs):
            pytest.fail("new draws, reoptimization or OLS attempted in Phase 5")
        patch.setattr(np.random, "Generator", forbidden)
        patch.setattr(model, "fit_multivariate_rsm", forbidden)
        patch.setattr(optimization, "solve_quadratic_ball", forbidden)
        patch.setattr(optimization, "solve_response_region_anchor", forbidden)
        patch.setattr(uncertainty, "reoptimize_coefficient_ensemble", forbidden)
        patch.setattr(anchor_mc, "reoptimize_coefficient_ensemble", forbidden)
        patch.setattr(coefficient_mc, "sample_coefficient_ensemble", forbidden)
        metadata = workflow.run_chim_pa(output, run_id="integration_chim_pa")
    assert before == {p: (sha256_file(p), p.stat().st_mtime_ns) for p in workflow.INPUT_HASHES}
    return output, metadata


def test_real_artifact_shapes_indexing_and_every_quantile_against_saved_noise(real_pa):
    output, metadata = real_pa
    assert metadata["candidate_counts"] == {2: 28, 3: 56, 4: 70}
    assert metadata["decision_quantile_count"] == 357
    assert metadata["reference_B"] == metadata["validation_continued_to_B"] == 2000
    assert metadata["normalization"] == "FIXED_NOMINAL_PAYOFF"
    assert metadata["new_random_draws"] == 0 and metadata["anchors_reoptimized"] is False
    assert metadata["policy_promoted"] is False
    assert metadata["qmax_filter"] is metadata["volume_filter"] is metadata["clipping"] is False
    assert metadata["early_stop_policy_sha256"] == workflow.INPUT_HASHES[workflow.POLICY]
    with np.load(output / "pa_noise_singular_values.npz", allow_pickle=False) as archive:
        assert archive["global"].shape == (2000, 7)
        lookup = {("GLOBAL", "GLOBAL"): archive["global"]}
        for name, k, count in [("pairs", 2, 28), ("triples", 3, 56), ("quadruples", 4, 70)]:
            samples = archive[name]
            indices = archive[f"{name}_indices"]
            assert samples.shape == (2000, count, k-1)
            assert indices.shape == (count, k) and indices.dtype == np.int64
            assert np.isfinite(samples).all() and np.all(samples >= 0)
            assert np.all(samples[:, :, :-1] >= samples[:, :, 1:])
            for j, subset in enumerate(indices):
                identifier = "C_" + "_".join(str(i+1) for i in subset)
                lookup[("LOCAL", identifier)] = samples[:, j]
        trajectories = read_rows(output / "pa_quantile_trajectories.csv")
        assert len(trajectories) == 7140
        for row in trajectories:
            noise = lookup[(row["scope"], row["subset_id"])][:int(row["B"])]
            rank = int(row["singular_index"])-1
            expected = np.quantile(noise[:, rank], .95, method="linear")
            assert float(row["q95"]) == expected
            assert (row["pass"] == "True") == (float(row["observed_singular"]) > expected)
    local = read_rows(output / "local_pa_B2000.csv")
    selected = read_rows(output / "selected_subsets_B2000.csv")
    assert len(local) == 154
    assert {row["subset_id"] for row in selected} == set(metadata["selected_ids_B2000"])
    for row in local:
        passes = json.loads(row["component_passes"])
        assert len(passes) == int(row["k"])-1
        assert (row["selected"] == "True") == all(passes)
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(output / name) == digest
    assert len(read_rows(output / "prefix_pa_sensitivity.csv")) == 20
    with pytest.raises(FileExistsError):
        workflow.run_chim_pa(output, run_id="existing_case")


def test_independent_normalization_centering_and_perturbation_svd(real_pa):
    output, metadata = real_pa
    nominal, samples, _, _, _ = workflow.load_canonical_inputs()
    signs = np.array([-1, -1, 1, 1, 1, 1, -1, -1])
    g = signs[:, None]*nominal
    u = np.diag(g)
    amplitude = g.max(axis=1)-u
    z = (g-u[:, None])/amplitude[:, None]
    assert_array_equal(np.diag(z), np.zeros(8))
    assert_array_equal(z.max(axis=1), np.ones(8))
    assert_array_equal(amplitude, metadata["nominal_amplitudes"])
    h = np.eye(8)-np.ones((8, 8))/8
    with np.load(output / "nominal_chim.npz", allow_pickle=False) as archive:
        assert_array_equal(archive["normalized"], z)
        assert_array_equal(archive["centered"], z@h)
    observed = np.linalg.svd(z@h, compute_uv=False)[:7]
    rows = read_rows(output / "global_pa_B2000.csv")
    assert_allclose([float(r["observed_singular"]) for r in rows], observed)
    with np.load(output / "pa_noise_singular_values.npz", allow_pickle=False) as archive:
        for b in [0, 99, 499, 1999]:
            delta = signs[:, None]*(samples[b]-nominal)/amplitude[:, None]
            expected = np.linalg.svd(delta@h, compute_uv=False)[:7]
            assert_array_equal(archive["global"][b], expected)
    assert metadata["centered_rank_diagnostic"] == metadata["vertex_difference_rank_diagnostic"]


def test_real_early_stop_is_checked_against_every_later_selection_and_dimension(real_pa):
    output, metadata = real_pa
    validation = json.loads((output / "early_stop_validation.json").read_text())
    sensitivity = read_rows(output / "prefix_pa_sensitivity.csv")
    quantiles = read_rows(output / "pa_quantile_trajectories.csv")
    first = next((int(r["B"]) for r in sensitivity
                  if r["early_stop_condition_met"] == "True"), None)
    assert first == metadata["B_stop"] == validation["first_B_stop"]
    selections = {}
    for b in range(100, 2001, 100):
        decisions = {}
        for row in quantiles:
            if int(row["B"]) == b and row["scope"] == "LOCAL":
                decisions.setdefault(row["subset_id"], []).append(row["pass"] == "True")
        selections[b] = {identifier for identifier, flags in decisions.items() if all(flags)}
    for index in range(1, 20):
        now, previous = sensitivity[index], sensitivity[index-1]
        changed = selections[int(now["B"])] != selections[int(previous["B"])]
        assert (now["selection_changed_from_previous"] == "True") == changed
    if first is not None and first < 2000:
        stopped = next(r for r in sensitivity if int(r["B"]) == first)
        stable = all(selections[int(r["B"])] == selections[first]
                     and r["global_dimension"] == stopped["global_dimension"]
                     for r in sensitivity if int(r["B"]) > first)
        assert (validation["retrospective_status"] == "EARLY_STOP_RETROSPECTIVELY_STABLE") == stable


def test_corrupt_input_hash_and_invalid_run_id_fail(tmp_path, monkeypatch):
    bad = tmp_path / "wrong.npz"
    bad.write_bytes(b"not the frozen input")
    monkeypatch.setitem(workflow.INPUT_HASHES, bad, "0"*64)
    with pytest.raises(ValueError, match="SHA-256"):
        workflow.load_canonical_inputs()
    with pytest.raises(ValueError, match="run_id"):
        workflow.run_chim_pa(tmp_path, run_id="../invalid")
