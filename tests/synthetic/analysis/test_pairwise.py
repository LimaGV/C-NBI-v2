import numpy as np
import pytest
from numpy.testing import assert_array_equal

from cnbi_v2.synthetic.analysis.pairwise import equalized_pair_indices


def test_pairwise_count_not_limited_by_a_third_front():
    c = np.column_stack((np.arange(56), -np.arange(56)))
    vrf = np.column_stack((np.arange(9), -np.arange(9)))
    nsga = np.column_stack((np.arange(32), -np.arange(32)))
    moea = np.column_stack((np.arange(35), -np.arange(35)))
    for comparator, expected in ((vrf, 9), (nsga, 32), (moea, 35)):
        k, ci, ai = equalized_pair_indices(c, np.arange(56), comparator, np.arange(len(comparator)))
        assert k == expected and len(ci) == len(ai) == expected
        assert set(ai) == set(range(expected))
    # Changing VRF has no argument/channel into the other two comparisons.
    assert equalized_pair_indices(c, np.arange(56), vrf[:3], np.arange(3))[0] == 3
    assert equalized_pair_indices(c, np.arange(56), nsga, np.arange(32))[0] == 32


def test_pairwise_smaller_cnbi_empty_front_and_stable_real_ids():
    a, b = np.array([[0.0, 1], [1, 0]]), np.array([[0.0, 2], [1, 1], [2, 0]])
    k, ci, ai = equalized_pair_indices(a, [4, 9], b, [10, 20, 30])
    assert k == 2
    assert_array_equal(ci, [4, 9])
    assert_array_equal(ai, [10, 30])
    assert equalized_pair_indices(a[:0], np.array([], dtype=int), b, [10, 20, 30])[0] == 0
    with pytest.raises(ValueError):
        equalized_pair_indices([1, 2], [0, 1], b, [10, 20, 30])
    with pytest.raises(ValueError):
        equalized_pair_indices(a, [4, 9], np.ones((3, 3)), [10, 20, 30])


def test_pair_specific_complete_replicas_and_HV_validity(monkeypatch):
    from pathlib import Path

    import pandas as pd

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3] / "scripts/validation"))
    from phase10e_pairwise_statistics import pair_medians

    frame = pd.DataFrame(
        [
            dict(
                scenario_id=s,
                replica_id=r,
                method=m,
                HV=float(r),
                HV_status="PRECISION_CRITERIA_PASSED",
            )
            for s in ("a", "b")
            for r in range(1, 6)
            for m in ("C-NBI", "NSGA-III")
        ]
    )
    rows, wide, excluded = pair_medians(frame, "HV", "NSGA-III")
    assert len(wide) == 2 and not excluded and len(rows) == 4
    assert (wide == 3).all().all()
    frame.loc[0, "HV_status"] = "PRECISION_PENDING"
    rows, wide, excluded = pair_medians(frame, "HV", "NSGA-III")
    assert list(wide.index) == ["b"] and excluded[0]["excluded_runs"] == 1
    with pytest.raises(ValueError):
        pair_medians(frame.iloc[:-1], "HV", "NSGA-III")
    with pytest.raises(ValueError):
        pair_medians(frame, "HV", "VRF-NBI")
