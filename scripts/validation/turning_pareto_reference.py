"""Assemble empirical common/LOO references from the frozen completed campaign."""

import argparse
import importlib.metadata
import json
import shutil
import subprocess
from pathlib import Path
from time import perf_counter

import numpy as np
from numpy.testing import assert_allclose

from cnbi_v2.data import sha256_file
from cnbi_v2.reference.indicators import additive_epsilon, diagnostics, distances
from cnbi_v2.reference.leave_one_out import reference
from cnbi_v2.reference.pools import Origin, PointPool, front

from . import turning_reference_campaign as campaign
from .turning_reference import ROOT, write_csv, write_json


def ea_runs(output, family, problem):
    protocol = json.loads(campaign.PROTOCOL.read_text())
    runs = []
    for seed in protocol["seeds"]:
        path = output / "runs" / f"{family.lower()}_seed{seed}"
        meta = json.loads(path.with_suffix(".json").read_text())
        if (meta["seed"] != seed or meta["family"] != family
                or meta["nfe"] > protocol["nfe_max"]
                or sha256_file(path.with_suffix(".npz")) != meta["archive_sha256"]):
            raise ValueError("incompatible evolutionary archive")
        with np.load(path.with_suffix(".npz"), allow_pickle=False) as d:
            x, f = d["nd_x"], d["nd_f"]
            if not problem.feasible(x).all():
                raise ValueError("archived EA decision is infeasible")
            assert_allclose(f, problem.natural(x, scalar_check=True), atol=5e-14, rtol=2e-14)
            runs.append(PointPool(x, f, problem.normalize(f), tuple(
                (Origin(family, f"{family}_seed{seed}", f"final_population_{int(i)}"),)
                for i in d["nd_population_indices"])))
    return runs


def table(path, records):
    keys = list(records[0])
    write_csv(path, keys, [[record[k] for k in keys] for record in records])


def assemble(output):
    start = perf_counter()
    dirty_at_launch = bool(subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    launch = json.loads((output / "campaign_launch.json").read_text())
    complete = json.loads((output / "campaign_completion.json").read_text())
    if (complete["runs"] != 60 or not complete["engine_still_identical"]
            or not complete["input_still_identical"]
            or campaign.hashes(campaign.input_paths()) != launch["input_sha256"]
            or campaign.hashes(campaign.ENGINE) != launch["engine_sha256"]):
        raise ValueError("campaign completion/input/code integrity gate failed")
    problem, xtol, tau = campaign.load_problem()
    pools = {}
    saturation = []
    timings = {}
    assembly_validation_counts = {}
    for family in ("NSGA3", "MOEAD"):
        t = perf_counter()
        runs = ea_runs(output, family, problem)
        assembly_validation_counts[family] = sum(len(p.x) for p in runs)
        pool = front(runs, xtol, tau)
        pools[family] = pool
        campaign.save_pool(output / f"{family.lower()}_pool.npz", pool)
        timings[f"{family}_pool_union_ND_seconds"] = perf_counter()-t
        # Rebuild each prefix from final-run pools, not a lossy common envelope.
        for r in range(1, 31):
            prefix = pool if r == 30 else front(runs[:r], xtol, tau)
            saturation.append({"family": family, "runs": r, "ND": len(prefix.x),
                               "hausdorff_pool30_to_prefix": float(distances(pool.z,
                                                                            prefix.z).max()),
                               "epsilon_plus_prefix_pool30": additive_epsilon(prefix.z, pool.z),
                               "interpretation": "INTERNAL_POOL_SATURATION_NOT_TRUTH"})
            print(f"{family} pool prefix{r}/30 ND={len(prefix.x)}", flush=True)
        timings[f"{family}_pool_and_saturation_seconds"] = perf_counter()-t
    pools["CNBI"] = campaign.load_pool(output / "cnbi20_pool.npz")
    pools["VRF"] = campaign.load_pool(output / "vrf_pool.npz")
    h5 = campaign.load_pool(output / "cnbi5_pool.npz")
    t = perf_counter()
    settings = dict(x_tolerance=xtol, dominance_tolerance=tau)
    common = reference(pools, **settings)
    campaign.save_pool(output / "reference_all.npz", common)
    timings["reference_all_union_ND_seconds"] = perf_counter()-t
    print(f"P_all={len(common.x)}", flush=True)
    references = {"all": common}
    removal, contribution, metrics = [], [], []
    family_sets = [{o.family for o in g} for g in common.origins]
    for family in pools:
        t = perf_counter()
        minus = reference(pools, excluded=family, **settings)
        references[f"minus_{family.lower()}"] = minus
        campaign.save_pool(output / f"reference_minus_{family.lower()}.npz", minus)
        timings[f"minus_{family}_union_ND_seconds"] = perf_counter()-t
        count = sum(g == {family} for g in family_sets)
        contribution.append({"family": family, "pool_ND": len(pools[family].x),
                             "exclusive_points": count, "exclusive_fraction": count/len(common.x),
                             "shared_points_with_family": sum(family in g and len(g) > 1
                                                              for g in family_sets),
                             "all_points_with_family": sum(family in g for g in family_sets)})
        removal.append({"excluded_family": family, "common_ND": len(common.x),
                        "minus_ND": len(minus.x),
                        "hausdorff_all_to_minus": float(distances(common.z, minus.z).max()),
                        "epsilon_plus_minus_all": additive_epsilon(minus.z, common.z)})
        for label, target in (("COMMON_REFERENCE_SELF_INCLUDED", common),
                              ("LEAVE_ONE_FAMILY_OUT", minus)):
            metrics.append({"evaluated_set": family, "label": label,
                            "target": "all" if target is common else f"minus_{family.lower()}",
                            **diagnostics(pools[family].z, target.z)})
        print(f"minus{family}={len(minus.x)} exclusive={count}", flush=True)
    for label, target in (("COMMON_REFERENCE_SELF_INCLUDED", common),
                          ("LEAVE_ONE_FAMILY_OUT", references["minus_cnbi"])):
        metrics.append({"evaluated_set": "CNBI_H5_SANITY_ONLY", "label": label,
                        "target": "all" if target is common else "minus_cnbi",
                        **diagnostics(h5.z, target.z)})
    provenance = []
    for name, pool in {**{f"pool_{k}": v for k, v in pools.items()},
                       "baseline_cnbi5": h5, **references}.items():
        for i, group in enumerate(pool.origins):
            for origin in group:
                provenance.append({"set": name, "point_id": i, "family": origin.family,
                                   "run_id": origin.run_id, "source_id": origin.source_id})
    table(output / "provenance.csv", provenance)
    table(output / "reference_contributions.csv", contribution)
    table(output / "loo_reference_diagnostics.csv", removal)
    table(output / "pool_saturation.csv", saturation)
    table(output / "geometric_diagnostics.csv", metrics)
    shutil.copyfile(ROOT / "references/metadata/phase_07_v1/reference_source_audit.csv",
                    output / "reference_source_audit.csv")
    shutil.copyfile(ROOT / "references/metadata/phase_07_v1/historical_decision_audit.json",
                    output / "historical_decision_audit.json")
    no_cnbi = all(o.family != "CNBI" for g in references["minus_cnbi"].origins for o in g)
    versions = {k: importlib.metadata.version(k) for k in ("numpy", "scipy", "pymoo", "moocore")}
    code = [Path(__file__), *sorted((ROOT / "src/cnbi_v2/reference").glob("*.py"))]
    metadata = {"run_id": campaign.RUN_ID, "status": "EMPIRICAL_REFERENCE_CONSTRUCTED",
                "construction_git_commit": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "construction_working_tree_dirty_at_launch": dirty_at_launch,
                "engine_git_commit": launch["git_commit"],
                "input_sha256": launch["input_sha256"], "engine_sha256": launch["engine_sha256"],
                "assembly_sha256": campaign.hashes(code), "versions": versions,
                "alpha": problem.alpha, "sphere_tolerance": problem.sphere_tolerance,
                "responses": list(campaign.frozen.RESPONSES),
                "directions": [d.value for d in campaign.frozen.DIRECTIONS],
                "utopia": problem.utopia.tolist(), "amplitudes": problem.amplitudes.tolist(),
                "signs": problem.signs.tolist(), "deduplication_x_Linf": xtol,
                "dominance_coordinate_equality_tolerance": tau.tolist(),
                "config": json.loads(campaign.PROTOCOL.read_text()),
                "campaign_completion": complete, "VRF_eligibility": "ELIGIBLE_REEVALUATED_66_X",
                "evaluation_accounting": {
                    "optimizer_NFE": complete["total_optimizer_NFE"],
                    "per_run_independent_scalar_validation": complete[
                        "total_validation_evaluations"],
                    "per_run_validation_scope": "330 final-population points per run; not search",
                    "canonical_materialization_scalar_CNBI20_CNBI5_VRF": 4557+492+66,
                    "materialization_additional_fast_scalar_cross_checks_CNBI": 4557+492,
                    "assembly_additional_scalar_validation": assembly_validation_counts,
                    "optimizer_evaluations_added_by_assembly": 0},
                "VRF_limit": "historically sanitized/ND-filtered export, not original full run",
                "historical_EA_outputs_in_principal_pools": False,
                "pool_counts": {k: len(v.x) for k, v in pools.items()},
                "reference_counts": {k: len(v.x) for k, v in references.items()},
                "CNBI5_ND": len(h5.x), "CNBI5_in_common_inputs": False,
                "CNBI20_only_family_contribution": True,
                "no_CNBI_origin_in_reference_for_CNBI5": no_cnbi,
                "shared_common_points": sum(len(g) > 1 for g in family_sets),
                "construction_rule": "exclude family before union, numerical deduplication and ND",
                "reference_for_CNBI5": "reference_minus_cnbi.npz",
                "LOO_targets_differ_no_automatic_ranking": True,
                "common_reference_self_included": True, "pareto_ground_truth": False,
                "prior_scientific_pipelines_reexecuted": [], "new_VRF_optimization": False,
                "HV": "DEFERRED", "adaptive_H": "FUTURE_NOT_IMPLEMENTED",
                "final_benchmark": "NOT_STARTED", "timings_seconds": timings,
                "assembly_wall_seconds": perf_counter()-start}
    metadata["output_sha256"] = {
        p.relative_to(output).as_posix(): sha256_file(p)
        for p in sorted(output.rglob("*")) if p.is_file()
        and p.name not in {"metadata.json", "checksums.sha256"}}
    write_json(output / "metadata.json", metadata)
    checksum_files = [p for p in sorted(output.rglob("*"))
                      if p.is_file() and p.name != "checksums.sha256"]
    (output / "checksums.sha256").write_text("".join(
        f"{sha256_file(p)}  {p.relative_to(output).as_posix()}\n" for p in checksum_files),
        encoding="utf-8", newline="\n")
    print(json.dumps({"pools": metadata["pool_counts"],
                      "references": metadata["reference_counts"],
                      "no_CNBI_leak": no_cnbi,
                      "seconds": metadata["assembly_wall_seconds"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=campaign.OUTPUT)
    args = parser.parse_args()
    assemble(args.output)
