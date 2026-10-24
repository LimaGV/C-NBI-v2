"""Operational v2 rule oracles, not external validation of a post-hoc tolerance."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.chim import (
    PACheckpoint,
    checkpoint_spectral_gaps,
    evaluate_gap_early_stop,
    gap_policy_from_mapping,
    normalized_adjacent_gaps,
)

POLICY = Path(__file__).resolve().parents[2] / "docs/policies/pa_early_stop_policy.json"
IDS = (
    "GLOBAL:1",
    "GLOBAL:2",
    "GLOBAL:3",
    "C_1_2:1",
    "C_1_2_3:1",
    "C_1_2_3:2",
    "C_1_2_4:1",
    "C_1_2_4:2",
    "C_1_2_3_4:1",
    "C_1_2_3_4:2",
    "C_1_2_3_4:3",
)


def policy():
    return gap_policy_from_mapping(json.loads(POLICY.read_text(encoding="utf-8")))


def records():
    return [
        PACheckpoint(
            b,
            2,
            "MONOTONE_PA_PATTERN",
            (),
            frozenset({"C_1_2", "C_1_2_3"}),
            IDS,
            np.array([10.0, 8.0, 4.0, 1.0, 5.0, 2.0, 5.0, 2.0, 9.0, 6.0, 3.0]),
            (1, 1, 0),
        )
        for b in range(100, 2001, 100)
    ]


def set_q(row, values, offset=0):
    q = row.decision_quantiles.copy()
    q[offset : offset + len(values)] = values
    return replace(row, decision_quantiles=q)


def test_known_equal_and_degenerate_gap_oracles_and_immutable_results():
    known = normalized_adjacent_gaps([10, 8, 4])
    assert_array_equal(known.absolute, [2, 4])
    assert_array_equal(known.normalized, [0.2, 0.5])
    assert_array_equal(normalized_adjacent_gaps([1, 1, 1]).normalized, [0, 0])
    zero = normalized_adjacent_gaps([0, 0])
    assert_array_equal(zero.normalized, [0])
    assert_array_equal(zero.degenerate, [True])
    assert np.isfinite(zero.normalized).all()
    assert normalized_adjacent_gaps([np.finfo(float).tiny, 0]).normalized[0] == 0
    for array in (known.absolute, known.normalized, known.degenerate):
        with pytest.raises(ValueError):
            array[0] = 0
        with pytest.raises(ValueError):
            array.setflags(write=True)


@pytest.mark.parametrize("scale", [1e-100, 0.001, 7.0, 1e100])
def test_common_positive_spectral_scale_invariance(scale):
    q = np.array([10.0, 8.0, 4.0])
    assert_allclose(
        normalized_adjacent_gaps(scale * q).normalized,
        normalized_adjacent_gaps(q).normalized,
        rtol=3e-16,
        atol=0,
    )


def test_pairs_have_zero_triples_one_and_quadruples_two_gaps():
    spectra = checkpoint_spectral_gaps(records()[0])
    assert [len(s.gaps.normalized) for s in spectra] == [2, 0, 1, 1, 2]
    with pytest.raises(ValueError):
        spectra[0].q95[0] = 1
    # A tolerated machine ordering reversal is explicitly treated as zero gap.
    assert normalized_adjacent_gaps([1.0, np.nextafter(1.0, 2.0)]).normalized[0] == 0


@pytest.mark.parametrize(
    "q,epsilon",
    [
        ([], 1e-300),
        ([[-1]], 1e-300),
        ([-1.0, 0], 1e-300),
        ([1.0, 2.0], 1e-300),
        ([np.inf, 0], 1e-300),
        ([np.nan, 0], 1e-300),
        ([1, 0], 0),
        ([1, 0], np.inf),
        ([1, 0], True),
    ],
)
def test_invalid_spectrum_or_numeric_zero_protection_rejected(q, epsilon):
    with pytest.raises(ValueError):
        normalized_adjacent_gaps(q, epsilon=epsilon)


def test_earliest_eligible_window_is_500_600_700_and_first_stop_700():
    result = evaluate_gap_early_stop(records(), policy())
    assert result.first_B_stop == 700
    assert not any(r.eligible for r in result.trajectory[:6])
    assert result.trajectory[6].eligible and result.trajectory[6].early_stop_condition_met
    assert result.trajectory[6].monitored_subset_ids == ("C_1_2_3",)
    assert result.trajectory[6].monitored_gap_count == 3  # 2 global + 1 selected trio.
    assert result.retrospective_status == "EARLY_STOP_RETROSPECTIVELY_DECISION_STABLE"
    assert result.same_final_selection is result.same_final_dimension is True
    assert result.replicate_reduction_fraction == 0.65
    assert result.post_stop_max_gap_change == 0
    assert result.trajectory[0].overall_monitored_gap_max_change is None


def test_same_counts_different_id_in_window_prevents_stop():
    rows = records()
    rows[5] = replace(rows[5], selected_ids=frozenset({"C_1_2", "C_1_2_4"}))
    result = evaluate_gap_early_stop(rows, policy())
    assert result.first_B_stop == 900
    assert not result.trajectory[6].three_checkpoint_selection_stable
    assert not result.trajectory[6].monitored_spectra_consistent
    assert result.trajectory[6].monitored_subset_ids == ()
    assert not result.trajectory[6].early_stop_condition_met


def test_a_changed_global_dimension_in_window_prevents_stop():
    rows = records()
    rows[5] = replace(rows[5], global_dimension=1)
    result = evaluate_gap_early_stop(rows, policy())
    assert not result.trajectory[6].three_checkpoint_dimension_stable
    assert result.first_B_stop == 900


def test_both_transitions_must_be_stable_not_only_the_latest():
    rows = records()
    for i in range(5, 20):
        rows[i] = set_q(rows[i], [10.0, 5.0, 4.0])
    result = evaluate_gap_early_stop(rows, policy())
    assert result.first_B_stop == 800
    at_700 = result.trajectory[6]
    assert at_700.overall_monitored_gap_max_change == 0
    assert at_700.previous_transition_monitored_gap_max_change > 0.05
    assert not at_700.spectral_gap_stable


def test_exact_five_percentage_points_is_rejected_without_relative_gap_division():
    rows = records()
    for i, row in enumerate(rows):
        rows[i] = set_q(row, [20.0, 20.0 if i < 5 else 19.0, 10.0])
    result = evaluate_gap_early_stop(rows, policy())
    assert result.trajectory[5].global_gap_max_change == 0.05
    assert result.trajectory[6].window_monitored_gap_max_change == 0.05
    assert not result.trajectory[6].early_stop_condition_met
    assert result.first_B_stop == 800


def test_only_selected_stable_local_spectra_affect_gap_condition():
    rows = records()
    for i, row in enumerate(rows):
        # Large changes for a rejected trio and a pair threshold do not block.
        rows[i] = set_q(
            set_q(row, [5.0, 0.0 if i % 2 else 5.0], 6), [1000.0 if i % 2 else 0.001], 3
        )
    assert evaluate_gap_early_stop(rows, policy()).first_B_stop == 700
    rows = records()
    for i, row in enumerate(rows):
        rows[i] = set_q(row, [5.0, 0.0 if i % 2 else 5.0], 4)  # Selected trio.
    assert evaluate_gap_early_stop(rows, policy()).first_B_stop is None


def test_selected_quartet_monitors_both_gaps():
    rows = [replace(r, selected_ids=r.selected_ids | {"C_1_2_3_4"}) for r in records()]
    result = evaluate_gap_early_stop(rows, policy())
    assert result.trajectory[6].monitored_subset_ids == ("C_1_2_3", "C_1_2_3_4")
    assert result.trajectory[6].monitored_gap_count == 5
    for i, row in enumerate(rows):
        rows[i] = set_q(row, [9.0, 6.0, 0.0 if i % 2 else 6.0], 8)
    assert evaluate_gap_early_stop(rows, policy()).first_B_stop is None


def test_individual_q95_change_is_no_longer_a_stopping_condition():
    rows = [
        replace(r, decision_quantiles=r.decision_quantiles * (1 if i % 2 else 10))
        for i, r in enumerate(records())
    ]
    result = evaluate_gap_early_stop(rows, policy())
    assert result.first_B_stop == 700  # 90% individual q changes, identical gaps.
    assert result.trajectory[6].window_monitored_gap_max_change < 1e-15


@pytest.mark.parametrize("change_dimension", [False, True])
def test_retrospective_detects_every_later_decision_even_if_final_returns(change_dimension):
    rows = records()
    rows[9] = (
        replace(rows[9], global_dimension=1)
        if change_dimension
        else replace(rows[9], selected_ids=frozenset({"C_1_2", "C_1_2_4"}))
    )
    result = evaluate_gap_early_stop(rows, policy())
    assert result.first_B_stop == 700
    assert result.changed_later_checkpoints == (1000,)
    assert result.retrospective_status == "PREMATURE_STOP_DETECTED"
    assert result.same_final_selection is result.same_final_dimension is True


def test_later_gap_fluctuation_alone_is_not_premature():
    rows = records()
    rows[8] = set_q(rows[8], [10.0, 4.0, 1.0])
    result = evaluate_gap_early_stop(rows, policy())
    assert result.first_B_stop == 700
    assert result.retrospective_status == "EARLY_STOP_RETROSPECTIVELY_DECISION_STABLE"
    assert result.post_stop_max_gap_change > 0.05
    assert result.post_stop_gap_tolerance_exceeded_at == (900, 1000)
    assert result.changed_later_checkpoints == ()


def test_empty_local_monitor_and_degenerate_spectra_are_finite_and_flagged():
    rows = [
        replace(r, selected_ids=frozenset(), decision_quantiles=np.zeros(len(IDS)))
        for r in records()
    ]
    result = evaluate_gap_early_stop(rows, policy())
    assert result.first_B_stop == 700
    assert result.trajectory[6].selected_local_gap_max_change is None
    assert result.trajectory[6].degenerate_gap_ids == (
        "GLOBAL:1",
        "GLOBAL:2",
        "C_1_2_3:1",
        "C_1_2_4:1",
        "C_1_2_3_4:1",
        "C_1_2_3_4:2",
    )


def test_no_stop_and_only_reference_stop_have_no_external_retrospective_evidence():
    rows = [replace(r, global_dimension=i % 2) for i, r in enumerate(records())]
    result = evaluate_gap_early_stop(rows, policy())
    assert result.first_B_stop is None and result.stop_status == "EARLY_STOP_NOT_REACHED"
    assert result.same_final_selection is result.replicate_reduction_fraction is None
    rows[-3:] = [replace(r, global_dimension=3) for r in rows[-3:]]
    result = evaluate_gap_early_stop(rows, policy())
    assert result.first_B_stop == 2000
    assert result.retrospective_status == "NOT_APPLICABLE_STOP_AT_REFERENCE"
    assert result.post_stop_max_gap_change is None


def test_missing_checkpoints_changed_quantile_identity_and_bad_grouping_fail():
    with pytest.raises(ValueError, match="every policy"):
        evaluate_gap_early_stop(records()[:-1], policy())
    rows = records()
    rows[1] = replace(rows[1], quantile_ids=tuple(reversed(IDS)))
    with pytest.raises(ValueError, match="identities/order"):
        evaluate_gap_early_stop(rows, policy())
    for ids, selected, values in [
        ((), frozenset(), []),
        (("GLOBAL:1", "GLOBAL:1"), frozenset(), [1.0, 1.0]),
        (("GLOBAL:2",), frozenset(), [1.0]),
        (("C_1_2:1", "GLOBAL:1"), frozenset(), [1.0, 1.0]),
        (("GLOBAL:1", "C_2_1:1"), frozenset(), [1.0, 1.0]),
        (("GLOBAL:1", "C_1_2:1"), frozenset({"C_1_3"}), [1.0, 1.0]),
    ]:
        bad = replace(
            records()[0],
            quantile_ids=ids,
            selected_ids=selected,
            decision_quantiles=np.array(values),
        )
        with pytest.raises(ValueError):
            checkpoint_spectral_gaps(bad)


@pytest.mark.parametrize(
    "key,value",
    [
        ("version", 1),
        ("version", True),
        ("status", "ACCEPTED"),
        ("post_hoc_on_turning_case", False),
        ("gap_tolerance", 0.01),
        ("epsilon_q", 1e-8),
        ("quantile", 0.9),
        ("quantile_method", "nearest"),
        ("checkpoints", (100, 200)),
        ("checkpoints", []),
        ("checkpoint_step", 200),
        ("minimum_B", 400),
        ("stability_window", 2),
        ("earliest_full_window_B", 500),
        ("maximum_B", 2100),
    ],
)
def test_policy_parameter_drift_is_rejected(key, value):
    data = json.loads(POLICY.read_text(encoding="utf-8"))
    data[key] = value
    with pytest.raises(ValueError):
        gap_policy_from_mapping(data)
