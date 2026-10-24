"""Validate the published finite campaign without rerunning real optimizers."""

import csv
import json

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scripts.validation import turning_reference_campaign as workflow

from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import nondominated_mask


@pytest.fixture(scope="module")
def archive():
    path = workflow.OUTPUT
    return path, json.loads((path / "metadata.json").read_text()), workflow.load_problem()


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_all_hashes_frozen_inputs_and_campaign_accounting(archive):
    path, meta, (problem, _, _) = archive
    for line in (path / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(path / name) == digest
    for name, digest in meta["output_sha256"].items():
        assert sha256_file(path / name) == digest
    for name, digest in meta["input_sha256"].items():
        assert sha256_file(workflow.ROOT / name) == digest
    assert meta["alpha"] == 8**.25 == problem.alpha
    assert meta["campaign_completion"]["runs"] == 60
    assert meta["campaign_completion"]["total_optimizer_NFE"] == 60*132000
    assert meta["campaign_completion"]["engine_still_identical"]
    assert meta["campaign_completion"]["input_still_identical"]
    assert meta["prior_scientific_pipelines_reexecuted"] == []
    assert meta["pareto_ground_truth"] is False
    assert meta["final_benchmark"] == "NOT_STARTED"
    assert meta["construction_working_tree_dirty_at_launch"] is False
    launch = json.loads((path / "campaign_launch.json").read_text())
    assert launch["git_working_tree_dirty_at_launch"] is False
    assert len(set(launch["seeds"])) == 30
    assert launch["seeds"] == list(range(1001, 1031))
    assert launch["historical_audit_completed_before_runs"]


@pytest.mark.parametrize("family", ["NSGA3", "MOEAD"])
def test_sixty_final_populations_nfe_response_integration_and_nd(archive, family):
    path, _, (problem, _, tau) = archive
    summaries = csv_rows(path / f"{family.lower()}_runs_summary.csv")
    assert len(summaries) == 30
    assert [int(r["seed"]) for r in summaries] == list(range(1001, 1031))
    for seed in range(1001, 1031):
        stem = path / "runs" / f"{family.lower()}_seed{seed}"
        run = json.loads(stem.with_suffix(".json").read_text())
        assert run["seed"] == seed and run["family"] == family
        assert run["nfe"] == run["nfe_max"] == 132000
        assert run["population"] == 330 and run["generations"] == 400
        assert run["config_hash"] == workflow.fingerprint(run["identity"])
        assert sha256_file(stem.with_suffix(".npz")) == run["archive_sha256"]
        with np.load(stem.with_suffix(".npz"), allow_pickle=False) as data:
            x, f, z = (data[k] for k in ("final_population_x", "final_population_f",
                                        "final_population_z"))
            assert x.shape == (330, 3) and f.shape == z.shape == (330, 8)
            assert problem.feasible(x).all()
            assert_allclose(f, problem.natural(x), atol=5e-14, rtol=2e-14)
            assert_allclose(z, problem.normalize(f), atol=0, rtol=0)
            ids = np.flatnonzero(nondominated_mask(z, equality_tolerance=tau))
            assert_array_equal(ids, data["nd_population_indices"])
            assert_array_equal(x[ids], data["nd_x"])
            assert_array_equal(f[ids], data["nd_f"])
            assert_array_equal(z[ids], data["nd_z"])
            assert run["ND"] == len(ids)


def test_references_preserve_only_independent_retained_origins(archive):
    path, meta, (problem, xtol, _) = archive
    files = {"NSGA3": "nsga3", "MOEAD": "moead", "CNBI": "cnbi20", "VRF": "vrf"}
    originals = {}
    for family, name in files.items():
        pool = workflow.load_pool(path / f"{name}_pool.npz")
        assert len(pool.x) == meta["pool_counts"][family]
        assert problem.feasible(pool.x).all()
        assert_allclose(pool.f, problem.natural(pool.x), atol=5e-14, rtol=2e-14)
        for i, group in enumerate(pool.origins):
            for origin in group:
                assert origin.family == family
                originals[origin] = (pool.x[i], pool.f[i], pool.z[i])
    provenance_rows = csv_rows(path / "provenance.csv")
    for name in ("all", "minus_nsga3", "minus_moead", "minus_cnbi", "minus_vrf"):
        pool = workflow.load_pool(path / f"reference_{name}.npz")
        assert len(pool.x) == meta["reference_counts"][name]
        excluded = name.removeprefix("minus_").upper() if name != "all" else None
        for i, group in enumerate(pool.origins):
            for origin in group:
                assert origin.family != excluded
                x, f, z = originals[origin]
                assert_allclose(pool.x[i], x, atol=xtol, rtol=0)
                assert_allclose(pool.f[i], f, atol=1e-10, rtol=2e-14)
                assert_allclose(pool.z[i], z, atol=1e-12, rtol=2e-14)
        rows = [r for r in provenance_rows if r["set"] == name]
        assert len(rows) == sum(len(g) for g in pool.origins)
        assert {r["family"] for r in rows} == {
            o.family for group in pool.origins for o in group}
    assert meta["no_CNBI_origin_in_reference_for_CNBI5"] is True
    assert meta["reference_for_CNBI5"] == "reference_minus_cnbi.npz"
    assert meta["CNBI5_in_common_inputs"] is False
    assert meta["CNBI20_only_family_contribution"] is True
    assert meta["CNBI5_ND"] == 408 and meta["pool_counts"]["CNBI"] == 4417


def test_saturation_metric_labels_contribution_and_directions(archive):
    path, meta, _ = archive
    saturation = csv_rows(path / "pool_saturation.csv")
    assert len(saturation) == 60
    for family in ("NSGA3", "MOEAD"):
        rows = [r for r in saturation if r["family"] == family]
        assert [int(r["runs"]) for r in rows] == list(range(1, 31))
        assert float(rows[-1]["hausdorff_pool30_to_prefix"]) == 0
        assert float(rows[-1]["epsilon_plus_prefix_pool30"]) == 0
        assert int(rows[-1]["ND"]) == meta["pool_counts"][family]
    contributions = csv_rows(path / "reference_contributions.csv")
    assert sum(int(r["exclusive_points"]) for r in contributions) + meta[
        "shared_common_points"] == meta["reference_counts"]["all"]
    metrics = csv_rows(path / "geometric_diagnostics.csv")
    assert len(metrics) == 10
    assert {r["label"] for r in metrics} == {
        "COMMON_REFERENCE_SELF_INCLUDED", "LEAVE_ONE_FAMILY_OUT"}
    h5 = [r for r in metrics if r["evaluated_set"] == "CNBI_H5_SANITY_ONLY"
          and r["label"] == "LEAVE_ONE_FAMILY_OUT"]
    assert len(h5) == 1 and h5[0]["target"] == "minus_cnbi"
    assert meta["directions"] == ["MAX", "MAX", "MIN", "MIN", "MIN", "MIN", "MAX", "MAX"]
