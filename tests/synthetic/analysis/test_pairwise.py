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


def test_pairwise_archive_has_independent_counts_and_six_quality_tests(monkeypatch):
    from pathlib import Path

    import pandas as pd

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3] / "scripts/validation"))
    from phase10e_pairwise_inputs import INPUT, OUTPUT, read

    native = pd.read_csv(INPUT / "benchmark_native_metrics.csv").set_index(
        ["scenario_id", "replica_id", "method"]
    )
    diag = pd.read_csv(OUTPUT / "selection_diagnostics.csv")
    assert len(diag) == 810
    for row in diag.itertuples():
        expected = min(
            native.loc[row.scenario_id, row.replica_id, "C-NBI"].nondominated_count,
            native.loc[row.scenario_id, row.replica_id, row.comparator].nondominated_count,
        )
        assert row.K == expected
    example = diag[
        (diag.scenario_id == "nx2_delta1_rho025")
        & (diag.replica_id == 1)
        & (diag.method == "C-NBI")
    ].set_index("comparator")
    assert list(example.loc[["VRF-NBI", "NSGA-III", "MOEA/D"], "K"]) == [9, 32, 35]
    tests = pd.read_csv(OUTPUT / "statistical_tests.csv")
    for variant in ("native", "equalized"):
        quality = tests[(tests.variant == variant) & tests.metric.isin(["IGD", "HV"])]
        assert len(quality) == 6 and quality.family_size.eq(6).all()
        assert quality[quality.metric == "IGD"].n_scenarios.eq(27).all()
        hv = quality[quality.metric == "HV"].set_index("comparator")
        assert hv.loc["VRF-NBI", "n_scenarios"] == 26
        assert (hv.loc[["NSGA-III", "MOEA/D"], "n_scenarios"] == 27).all()
    assert not tests.test.str.contains("Friedman").any()
    assert read(OUTPUT / "audit_report.json")["sets"] == 810


def test_pairwise_protected_inputs_and_complete_output_hashes(monkeypatch):
    from pathlib import Path

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3] / "scripts/validation"))
    from phase10e_pairwise_finalize import verify_outputs
    from phase10e_pairwise_inputs import OUTPUT, read

    assert read(OUTPUT / "generation_manifest.json")["optimization_executions"] == 0
    verify_outputs()


def test_six_pairwise_figures_have_no_grids_or_joint_ranking(monkeypatch):
    from pathlib import Path

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3] / "scripts/validation"))
    import matplotlib.pyplot as plt
    import phase10e_pairwise_figures as module

    stems = []

    def check(fig, stem):
        stems.append(stem)
        for ax in fig.axes:
            assert not any(g.get_visible() for g in ax.get_xgridlines() + ax.get_ygridlines())
        plt.close(fig)

    monkeypatch.setattr(module, "finish", check)
    monkeypatch.setattr(module, "write", lambda *args: None)
    module.figures()
    assert len(stems) == len(set(stems)) == 6
    assert not any("rank" in stem for stem in stems)
