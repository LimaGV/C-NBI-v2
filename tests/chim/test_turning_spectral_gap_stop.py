"""Revised real analysis consumes frozen spectra; forbid every upstream operation."""

import json
from dataclasses import replace

import numpy as np
import pytest
from scripts.validation import turning_spectral_gap_stop as workflow

from cnbi_v2.data import sha256_file


@pytest.fixture(scope="module")
def revision(tmp_path_factory):
    output = tmp_path_factory.mktemp("gap_stop_revision")
    inputs = [workflow.SOURCE / name for name in workflow.ARCHIVE_HASHES]
    inputs += [workflow.SOURCE / "checksums.sha256", workflow.POLICY]
    before = {p: (sha256_file(p), p.stat().st_mtime_ns) for p in inputs}
    with pytest.MonkeyPatch.context() as patch:
        from scripts.validation import turning_anchor_mc, turning_chim_pa, turning_coefficient_mc

        import cnbi_v2.chim as chim
        import cnbi_v2.model as model
        import cnbi_v2.optimization as optimization
        import cnbi_v2.uncertainty.coefficient_sampling as sampling

        def forbidden(*args, **kwargs):
            pytest.fail("spectral-gap revision attempted upstream scientific computation")

        patch.setattr(np.linalg, "svd", forbidden)
        patch.setattr(np.random, "Generator", forbidden)
        patch.setattr(np.random, "default_rng", forbidden)
        patch.setattr(model, "fit_multivariate_rsm", forbidden)
        patch.setattr(optimization, "solve_quadratic_ball", forbidden)
        patch.setattr(sampling, "sample_coefficient_ensemble", forbidden)
        for name in ["nominal_normalization", "centered_chim", "compute_chim_spectra"]:
            patch.setattr(chim, name, forbidden)
        patch.setattr(turning_coefficient_mc, "run_coefficient_mc", forbidden)
        patch.setattr(turning_anchor_mc, "run_anchor_mc", forbidden)
        patch.setattr(turning_chim_pa, "run_chim_pa", forbidden)
        metadata = workflow.run_gap_revision(output, run_id="spectral_gap_integration")
    assert before == {p: (sha256_file(p), p.stat().st_mtime_ns) for p in inputs}
    return output, metadata


def test_revision_keeps_all_historical_decisions_and_uses_no_new_upstream_work(revision):
    output, metadata = revision
    assert metadata["all_historical_thresholds_and_decisions_identical"] is True
    assert metadata["selected_counts_B2000"] == [19, 18, 0]
    assert metadata["global_dimension_B2000"] == 2
    assert metadata["new_random_draws"] == 0
    for key in ["anchors_reoptimized", "payoffs_recalculated", "normalization_recalculated",
                "chim_recalculated", "svd_recalculated", "gap_filter_applied_to_pa",
                "external_validation", "policy_promoted"]:
        assert metadata[key] is False
    assert metadata["policy_status"] == "PROPOSED_REVISED"
    assert metadata["degenerate_q95_status"] == "NOT_DETECTED"
    for line in (output / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(output / name) == digest
    assert (output / "global_q95_spectral_gaps.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    with pytest.raises(FileExistsError):
        workflow.run_gap_revision(output, run_id="duplicate")


def test_every_saved_gap_independently_matches_archived_q95_and_monitor_ids(revision):
    output, _ = revision
    q_rows = workflow.read_rows(workflow.SOURCE / "pa_quantile_trajectories.csv")
    quantiles = {(int(r["B"]), r["subset_id"], int(r["singular_index"])): float(r["q95"])
                 for r in q_rows}
    windows = {int(r["B"]): json.loads(r["monitored_local_subset_ids"])
               for r in workflow.read_rows(output / "window_monitoring.csv")}
    rows = workflow.read_rows(output / "spectral_gap_trajectories.csv")
    assert len(rows) == 4040  # 20*(6 global + 56 trios + 2*70 quartets), no pairs.
    gaps = {}
    for row in rows:
        b, index, identifier = int(row["B"]), int(row["gap_index"]), row["subset_id"]
        q1, q2 = quantiles[b, identifier, index], quantiles[b, identifier, index+1]
        expected = (q1-q2)/q1
        assert float(row["q_r"]) == q1 and float(row["q_r_plus_1"]) == q2
        assert float(row["absolute_gap"]) == q1-q2
        assert float(row["normalized_gap"]) == expected
        assert 0 <= expected <= 1
        assert (row["monitored_for_early_stop"] == "True") == (
            identifier == "GLOBAL" or identifier in windows[b])
        if b > 100:
            assert float(row["normalized_gap_change_from_previous"]) == abs(
                expected-gaps[b-100, identifier, index])
        gaps[b, identifier, index] = expected
    global_rows = workflow.read_rows(output / "global_spectral_gap_trajectory.csv")
    assert len(global_rows) == 20
    for row in global_rows:
        assert float(row["critical_global_gap"]) == float(row["g2"])
        assert [float(row[f"g{j}"]) for j in range(1, 7)] == [
            gaps[int(row["B"]), "GLOBAL", j] for j in range(1, 7)]


def test_real_stop_uses_both_transitions_and_every_later_decision(revision):
    output, metadata = revision
    validation = json.loads((output / "early_stop_validation.json").read_text())
    rows = workflow.read_rows(output / "prefix_pa_sensitivity.csv")
    first = next(int(r["B"]) for r in rows if r["early_stop_condition_met"] == "True")
    assert first == 1300 == metadata["B_stop_gap"] == validation["first_B_stop"]
    assert validation["global_dimension_at_stop"] == 2
    assert validation["selected_counts_at_stop"] == [19, 18, 0]
    assert validation["selected_ids_at_stop"] == validation["selected_ids_at_reference"]
    assert validation["same_final_selection"] is validation["same_final_dimension"] is True
    assert validation["replicate_reduction_fraction"] == .35
    assert validation["retrospective_status"] == "EARLY_STOP_RETROSPECTIVELY_DECISION_STABLE"
    assert validation["changed_later_checkpoints"] == []
    windows = workflow.read_rows(output / "window_monitoring.csv")
    stopped_ids = next(r["selected_subset_ids"] for r in windows if int(r["B"]) == first)
    assert all(r["selected_subset_ids"] == stopped_ids for r in windows if int(r["B"]) > first)
    for row in rows:
        if row["early_stop_condition_met"] == "True":
            assert int(row["B"]) >= 700
            assert row["three_checkpoint_dimension_stable"] == "True"
            assert row["three_checkpoint_selection_stable"] == "True"
            assert float(row["overall_monitored_gap_max_change"]) < .05
            assert float(row["previous_transition_monitored_gap_max_change"]) < .05
    assert len(rows) == 20


def test_corrupt_history_or_recomputed_decision_fails_and_invalid_run_id(tmp_path, monkeypatch):
    monkeypatch.setitem(workflow.ARCHIVE_HASHES, "global_pa_B2000.csv", "0"*64)
    with pytest.raises(ValueError, match="SHA-256"):
        workflow.load_saved_spectra()
    with pytest.raises(ValueError, match="run_id"):
        workflow.run_gap_revision(tmp_path, run_id="../invalid")


def test_changed_quantile_or_selection_cannot_be_silently_accepted():
    spectra = workflow.load_saved_spectra()
    records = list(workflow.evaluate_pa_prefixes(spectra, range(100, 2001, 100)))
    q = records[0].decision_quantiles.copy()
    q[0] += .01
    altered = [replace(records[0], decision_quantiles=q), *records[1:]]
    with pytest.raises(ValueError, match="quantile vector"):
        workflow.verify_historical_decisions(altered, spectra)
    # Components are the authoritative PA outputs checked against every historical row.
    altered[0] = replace(altered[0], components=(
        replace(records[0].components[0], q95=records[0].components[0].q95+.01),
        *records[0].components[1:]))
    altered[0] = replace(altered[0], decision_quantiles=np.concatenate([
        d.q95 for d in altered[0].components]))
    with pytest.raises(ValueError, match="historical q95"):
        workflow.verify_historical_decisions(altered, spectra)
    altered = [replace(records[0], selected_ids=frozenset()), *records[1:]]
    with pytest.raises(ValueError, match="selection identities"):
        workflow.verify_historical_decisions(altered, spectra)
