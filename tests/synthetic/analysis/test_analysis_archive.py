import hashlib
import json
from pathlib import Path

import pandas as pd
from numpy.testing import assert_array_equal

ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "results/phase_10_synthetic_analysis/statistical_20261030"


def test_540_equalized_results_135_common_minimum_cardinalities_and_2160_sensitivities():
    native = pd.read_csv(RESULT / "native_replica_metrics.csv")
    equal = pd.read_csv(RESULT / "equalized_replica_metrics.csv")
    sensitivity = pd.read_csv(RESULT / "feasibility_replica_metrics.csv")
    assert len(native) == len(equal) == 540
    assert len(sensitivity) == 2160
    assert not equal.duplicated(["scenario_id", "replica_id", "method"]).any()
    counts = native.groupby(["scenario_id", "replica_id"]).nondominated_count.min()
    for key, group in equal.groupby(["scenario_id", "replica_id"]):
        assert len(group) == 4 and group.K.eq(counts.loc[key]).all()
    assert set(sensitivity.epsilon) == {0.0, 1e-12, 1e-10, 1e-9}
    keys = ["scenario_id", "replica_id", "method"]
    strict = sensitivity[sensitivity.epsilon == 0].set_index(keys).sort_index()
    source = native.set_index(keys).sort_index()
    assert_array_equal(strict.N_ND, source.nondominated_count)
    for metric in ("GD", "IGD", "HV", "Spacing", "Sparsity"):
        assert_array_equal(strict[metric], source[metric])


def test_primary_family_no_pending_hv_rank_and_full_supplementary_provenance():
    tests = pd.read_csv(
        RESULT / "statistical_tests.csv", dtype={"bootstrap_seed": str, "permutation_seed": str}
    )
    primary = tests[tests.analysis == "native_primary"]
    assert len(primary) == 14 and primary.family_size.eq(14).all()
    assert primary[primary.metric == "IGD"].n_scenarios.eq(27).all()
    assert primary[primary.metric == "HV"].n_scenarios.eq(26).all()
    assert primary.p_holm.ge(primary.pvalue).all()
    assert (primary.reject_holm_005 == primary.p_holm.le(0.05)).all()
    pairs = primary[primary.test == "Wilcoxon_exact_conditional"]
    assert len(pairs) == 12 and pairs.bootstrap_seed.notna().all()
    ranking = pd.read_csv(RESULT / "method_rankings.csv")
    assert (
        ranking[(ranking.analysis == "native_primary") & (ranking.metric == "HV")]
        .n_scenarios.eq(26)
        .all()
    )
    exclusions = pd.read_csv(RESULT / "inference_exclusions.csv")
    main_hv = exclusions[(exclusions.analysis == "native_primary") & (exclusions.metric == "HV")]
    assert list(main_hv.scenario_id) == ["nx5_delta5_rho025"]
    assert main_hv.excluded_runs.iloc[0] == 2
    study = pd.read_csv(RESULT / "hv_supplement_precision.csv")
    assert set(study.supplementary_max_power) == {18, 20}
    assert set(study.replica_id) == {2, 3}
    assert study.method.eq("VRF-NBI").all() and study.original_status.eq("PRECISION_PENDING").all()


def test_derived_artifact_hashes_and_completed_independent_audit():
    manifest = json.loads((RESULT / "generation_manifest.json").read_text())
    assert manifest["optimization_executions"] == 0
    assert manifest["status"] == "COMPLETED"
    audit = json.loads((RESULT / "audit_report.json").read_text())
    assert audit["status"] == "PASSED" and audit["subsets"] == 540
    assert audit["protected_original_files"] == 7156
    for line in (RESULT / "checksums.sha256").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        with (RESULT / relative).open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == expected, relative


def test_eleven_figures_are_gridless_and_do_not_rank_pending_values(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/validation"))
    import matplotlib.pyplot as plt
    import phase10e_figures as module

    stems = []

    def inspect(fig, stem):
        stems.append(stem)
        for ax in fig.axes:
            assert not any(line.get_visible() for line in ax.get_xgridlines() + ax.get_ygridlines())
        plt.close(fig)

    monkeypatch.setattr(module, "finish", inspect)
    monkeypatch.setattr(module, "write", lambda *args: None)
    monkeypatch.setattr(module, "table", lambda *args: None)
    module.figures()
    assert len(stems) == len(set(stems)) == 11
