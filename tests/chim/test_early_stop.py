"""Pre-registered policy, exact identities, strict 1% and retrospective failure oracles."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from cnbi_v2.chim import PACheckpoint, evaluate_early_stop, policy_from_mapping

POLICY = Path(__file__).resolve().parents[2] / "docs/policies/pa_early_stop_policy.json"


def records(*, premature=False, unstable_quantiles=False):
    rows = []
    for b in range(100, 2001, 100):
        selected = frozenset({"old" if b < 500 else "new"})
        if premature and b >= 800:
            selected = frozenset({"different_same_count"})
        q = float(1 + (b//100)%2) if unstable_quantiles else 1.
        rows.append(PACheckpoint(b, 1, "MONOTONE_PA_PATTERN", (), selected,
                                 ("GLOBAL:1", "C_1_2:1"), np.array([q, 0.]), (1,)))
    return rows


def policy():
    return policy_from_mapping(json.loads(POLICY.read_text()))


def test_first_eligible_500_changes_and_first_actual_stop_is_600():
    result = evaluate_early_stop(records(), policy())
    assert result.first_B_stop == 600
    assert result.stop_status == "EARLY_STOP_CONDITION_MET"
    assert result.retrospective_status == "EARLY_STOP_RETROSPECTIVELY_STABLE"
    assert result.trajectory[4].selection_changed_from_previous is True
    assert result.trajectory[4].early_stop_condition_met is False
    assert result.trajectory[5].early_stop_condition_met is True
    assert result.trajectory[0].max_decision_quantile_relative_change is None
    assert not any(row.early_stop_condition_met for row in result.trajectory[:4])
    assert len(result.trajectory) == 20 and result.reference_B == 2000
    assert policy().epsilon_q == np.finfo(float).tiny


def test_premature_stop_detects_later_identity_change_despite_same_count():
    result = evaluate_early_stop(records(premature=True), policy())
    assert result.first_B_stop == 600
    assert result.retrospective_status == "PREMATURE_STOP_DETECTED"
    assert result.changed_later_checkpoints == tuple(range(800, 2001, 100))


def test_not_reached_is_not_an_execution_error_and_global_dimension_matters():
    result = evaluate_early_stop(records(unstable_quantiles=True), policy())
    assert result.first_B_stop is None and result.stop_status == "EARLY_STOP_NOT_REACHED"
    rows = [replace(r, global_dimension=r.B//100%2) for r in records()]
    assert evaluate_early_stop(rows, policy()).first_B_stop is None


def test_exact_one_percent_is_not_stable_and_zero_protection():
    rows = records()
    rows[4] = replace(rows[4], selected_ids=rows[3].selected_ids,
                      decision_quantiles=np.array([100., 0.]))
    rows[3] = replace(rows[3], decision_quantiles=np.array([99., 0.]))
    result = evaluate_early_stop(rows, policy())
    assert result.trajectory[4].max_decision_quantile_relative_change == .01
    assert result.trajectory[4].early_stop_condition_met is False
    zero = [replace(r, selected_ids=frozenset(), decision_quantiles=np.zeros(2)) for r in records()]
    assert evaluate_early_stop(zero, policy()).first_B_stop == 500
    result = evaluate_early_stop(zero, policy())
    assert result.trajectory[4].max_decision_quantile_relative_change == 0


def test_only_at_reference_has_no_later_retrospective_evidence():
    rows = [replace(r, global_dimension=r.B//100) for r in records()]
    rows[-1] = replace(rows[-1], global_dimension=rows[-2].global_dimension)
    result = evaluate_early_stop(rows, policy())
    assert result.first_B_stop == 2000
    assert result.retrospective_status == "NOT_APPLICABLE_STOP_AT_REFERENCE"


def test_bad_trajectory_identifiers_and_nonfinite_quantiles_fail():
    with pytest.raises(ValueError, match="every policy"):
        evaluate_early_stop(records()[:-1], policy())
    rows = records()
    rows[1] = replace(rows[1], quantile_ids=("DIFFERENT:1", "C_1_2:1"))
    with pytest.raises(ValueError, match="identities"):
        evaluate_early_stop(rows, policy())
    for values in [np.array([np.nan, 0]), np.array([-1., 0]), np.ones(3)]:
        rows = records()
        rows[0] = replace(rows[0], decision_quantiles=values)
        with pytest.raises(ValueError, match="every checkpoint"):
            evaluate_early_stop(rows, policy())


@pytest.mark.parametrize("key,value", [
    ("checkpoints", (100, 200)), ("checkpoints", []), ("checkpoints", [100, 100]),
    ("minimum_eligible_B", 99), ("maximum_B", 2100), ("comparison_lag", 200),
    ("epsilon_q", 0), ("epsilon_q", "bad"), ("epsilon_q", True),
    ("quantile_relative_tolerance", 1.), ("policy_id", "different"), ("status", "ACCEPTED"),
])
def test_invalid_or_silently_replaced_policy_is_rejected(key, value):
    data = json.loads(POLICY.read_text())
    data[key] = value
    with pytest.raises(ValueError):
        policy_from_mapping(data)
