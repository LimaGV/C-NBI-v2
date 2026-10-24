"""Frozen-input Phase7 campaign. No fitting, anchors, MC, PA or NBI solving."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import numpy as np
from numpy.testing import assert_allclose

from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import canonical_decision_points, nondominated_mask
from cnbi_v2.reference import CanonicalProblem, EAConfig, run_evolutionary
from cnbi_v2.reference.pools import Origin, PointPool, front

from . import turning_local_nbi as frozen
from .turning_reference import RAW, ROOT, write_csv, write_json

RUN_ID = "turning_multifamily_loo_20261024"
OUTPUT = ROOT / "results/phase_07_reference_front" / RUN_ID
PHASE6 = ROOT / "results/phase_06_local_nbi" / frozen.RUN_ID
PROTOCOL = ROOT / "docs/policies/pareto_reference_protocol.json"
VRF = ROOT / "data/external/turning_reference/vrf_historical_decisions.csv"
ENGINE = [ROOT / "src/cnbi_v2/reference" / name for name in
          ("__init__.py", "problem.py", "evolutionary.py", "pools.py")]
ENGINE += [Path(__file__), PROTOCOL, ROOT / "uv.lock"]


def input_paths():
    return [RAW, frozen.MODELS, frozen.PHASE2 / "anchors_sphere.csv",
            frozen.PHASE2 / "payoff_sphere.csv", frozen.PHASE2 / "metadata.json",
            frozen.PHASE5 / "nominal_normalization.csv",
            frozen.PHASE5 / "selected_subsets_B2000.csv", frozen.PHASE5 / "metadata.json",
            PHASE6 / "metadata.json", PHASE6 / "local_nbi_solutions_H20.npz",
            PHASE6 / "provenance.csv", VRF,
            ROOT / "references/metadata/phase_07_v1/applied_ea_calibration.json",
            ROOT / "references/metadata/phase_07_v1/source_provenance.json"]


def hashes(paths):
    return {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in paths}


def load_problem():
    _, _, _, u, a, signs, _, _ = frozen.verified_inputs()
    b = np.array([[float(row[k]) for k in frozen.RESPONSES]
                  for row in frozen.read_rows(frozen.MODELS)])
    problem = CanonicalProblem(b, signs, u, a, frozen.ALPHA)
    meta = json.loads((PHASE6 / "metadata.json").read_text())
    return problem, float(meta["deduplication_tolerance_x_Linf"]), np.array(
        meta["dominance_coordinate_equality_tolerance"])


def save_pool(path, pool):
    np.savez_compressed(path, x=pool.x, natural_f=pool.f, z=pool.z,
                        origins_json=np.array([
                            json.dumps([asdict(o) for o in group], sort_keys=True)
                            for group in pool.origins]))


def load_pool(path):
    with np.load(path, allow_pickle=False) as data:
        return PointPool(data["x"], data["natural_f"], data["z"],
                         tuple(tuple(Origin(**o) for o in json.loads(str(s)))
                               for s in data["origins_json"]))


def materialize_h(problem, h):
    """Recover exact H membership and all origins without solving anything."""
    _, xtol, tau = load_problem()
    with np.load(PHASE6 / "local_nbi_solutions_H20.npz", allow_pickle=False) as d:
        column = int(np.flatnonzero(d["H_values"] == h)[0])
        ids = np.flatnonzero(d["H_membership"][:, column] & d["accepted"])
        x = d["x"][ids]
        f = problem.natural(x, scalar_check=True)
        assert_allclose(f, d["natural_responses"][ids], atol=5e-14, rtol=2e-14)
    if not problem.feasible(x).all():
        raise ValueError("saved CNBI point violates frozen sphere tolerance")
    groups = {int(i): [] for i in ids}
    with (PHASE6 / "provenance.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if int(row["H"]) == h:
                i = int(row["solution_id"])
                groups[i].append(Origin("CNBI", f"CNBI_H{h}",
                                        f"solution_{i}_{row['subset_id']}_{row['beta']}"))
    raw = PointPool(x, f, problem.normalize(f), tuple(tuple(groups[int(i)]) for i in ids))
    reps, _ = canonical_decision_points(x, tolerance=xtol)
    pool = front([raw], xtol, tau)
    expected = {5: (492, 411, 408), 20: (4557, 4476, 4417)}[h]
    if (len(x), len(reps), len(pool.x)) != expected:
        raise RuntimeError("exact saved H recovery changed")
    return raw, pool, {"subproblems": len(x), "unique": len(reps), "ND": len(pool.x),
                       "max_absolute_response_check": float(np.max(np.abs(
                           f-problem.natural(x))))}


def materialize_vrf(problem):
    provenance = json.loads((ROOT / "references/metadata/phase_07_v1/source_provenance.json"
                            ).read_text())
    if sha256_file(VRF) != provenance["extracted_decisions_sha256"]:
        raise ValueError("historical VRF decision digest changed")
    with VRF.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    x = np.array([[float(r[k]) for k in ("x1", "x2", "x3")] for r in rows])
    if len(x) != 66 or not problem.feasible(x).all():
        raise ValueError("historical VRF decisions unavailable or infeasible")
    f = problem.natural(x, scalar_check=True)
    return PointPool(x, f, problem.normalize(f),
                     tuple((Origin("VRF", "historical_vrf_reevaluated", r["source_id"]),)
                           for r in rows))


def prepare(output):
    problem, xtol, tau = load_problem()
    output.mkdir(parents=True, exist_ok=True)
    checks = {}
    for h in (20, 5):
        raw, pool, checks[str(h)] = materialize_h(problem, h)
        save_pool(output / f"cnbi{h}_decisions.npz", raw)
        save_pool(output / f"cnbi{h}_pool.npz", pool)
    vrf = materialize_vrf(problem)
    save_pool(output / "vrf_decisions.npz", vrf)
    save_pool(output / "vrf_pool.npz", front([vrf], xtol, tau))
    write_json(output / "canonical_integration_checks.json", checks)
    return checks


def fingerprint(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True, allow_nan=False).encode()).hexdigest()


def run_one(task):
    output, family, seed, launch = task
    problem, xtol, tau = load_problem()
    protocol = json.loads(PROTOCOL.read_text())
    settings = protocol[family]
    config = EAConfig(family, n_partitions=protocol["n_partitions"],
                      generations=protocol["generations"],
                      sbx_probability=settings["sbx_probability"], sbx_eta=settings["sbx_eta"],
                      pm_eta=settings["pm_eta"],
                      n_neighbors=protocol["MOEAD"]["n_neighbors"],
                      prob_neighbor_mating=protocol["MOEAD"]["prob_neighbor_mating"])
    identity = {"config": asdict(config), "protocol_sha256": sha256_file(PROTOCOL),
                "input_sha256": launch["input_sha256"], "engine_sha256": launch["engine_sha256"]}
    config_hash = fingerprint(identity)
    path = Path(output) / "runs" / f"{family.lower()}_seed{seed}"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.with_suffix(".json").exists():
        meta = json.loads(path.with_suffix(".json").read_text())
        if (meta["config_hash"] != config_hash or meta["seed"] != seed
                or sha256_file(path.with_suffix(".npz")) != meta["archive_sha256"]):
            raise ValueError("refusing incompatible or corrupted run checkpoint")
        return meta
    if hashes(ENGINE) != launch["engine_sha256"]:
        raise RuntimeError("frozen campaign engine changed after launch")
    result = run_evolutionary(problem, config, seed)
    x, f, z = (result.pop(k) for k in ("x", "natural_f", "optimizer_f"))
    # Independent scalar implementation, additional validation calls, outside search NFE.
    checked = problem.natural(x, scalar_check=True)
    assert_allclose(checked, f, atol=5e-14, rtol=2e-14)
    assert_allclose(problem.normalize(checked), z, atol=5e-14, rtol=2e-14)
    ids = nondominated_mask(z, equality_tolerance=tau)
    np.savez_compressed(path.with_suffix(".npz"), final_population_x=x, final_population_f=f,
                        final_population_z=z, nd_x=x[ids], nd_f=f[ids], nd_z=z[ids],
                        nd_population_indices=np.flatnonzero(ids))
    result.update(config_hash=config_hash, identity=identity, ND=int(ids.sum()),
                  validation_evaluations=len(x),
                  validation_max_absolute_error=float(np.max(np.abs(checked-f))),
                  archive_sha256=sha256_file(path.with_suffix(".npz")),
                  git_commit=launch["git_commit"], versions=launch["versions"])
    write_json(path.with_suffix(".json"), result)
    return result


def campaign(output):
    protocol = json.loads(PROTOCOL.read_text())
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    if dirty:
        raise RuntimeError("campaign must launch from a committed clean engine/config/audit")
    thread_vars = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                   "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")
    for key in thread_vars:
        os.environ[key] = "1"
    output.mkdir(parents=True, exist_ok=True)
    launch = {"git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                    text=True).strip(),
              "git_working_tree_dirty_at_launch": False,
              "started_utc": datetime.now(UTC).isoformat(),
              "input_sha256": hashes(input_paths()), "engine_sha256": hashes(ENGINE),
              "versions": {k: importlib.metadata.version(k) for k in ("numpy", "scipy", "pymoo")},
              "python": platform.python_version(), "platform": platform.platform(),
              "workers": protocol["workers"], "thread_environment": {k: "1" for k in thread_vars},
              "seeds": protocol["seeds"], "nfe_max": protocol["nfe_max"],
              "historical_audit_completed_before_runs": True}
    write_json(output / "campaign_launch.json", launch)
    start = perf_counter()
    checks = prepare(output)
    print(f"CNBI checks {checks}; VRF66 re-evaluated; starting60 EA runs", flush=True)
    tasks = [(str(output), method, seed, launch) for method in ("NSGA3", "MOEAD")
             for seed in protocol["seeds"]]
    summaries = []
    with ProcessPoolExecutor(max_workers=protocol["workers"]) as executor:
        futures = [executor.submit(run_one, task) for task in tasks]
        for future in as_completed(futures):
            meta = future.result()
            summaries.append(meta)
            print(f"{len(summaries)}/60 {meta['family']} seed{meta['seed']} "
                  f"NFE={meta['nfe']} ND={meta['ND']} seconds={meta['runtime']:.2f}", flush=True)
    for method in ("NSGA3", "MOEAD"):
        rows = sorted((r for r in summaries if r["family"] == method), key=lambda r: r["seed"])
        keys = ["family", "seed", "config_hash", "nfe", "nfe_max", "population", "generations",
                "ND", "runtime", "repair_operations", "validation_evaluations"]
        write_csv(output / f"{method.lower()}_runs_summary.csv", keys,
                  [[row[k] for k in keys] for row in rows])
    write_json(output / "campaign_completion.json",
               {"wall_seconds": perf_counter()-start, "runs": len(summaries),
                "total_optimizer_NFE": sum(r["nfe"] for r in summaries),
                "total_validation_evaluations": sum(r["validation_evaluations"] for r in summaries),
                "engine_still_identical": hashes(ENGINE) == launch["engine_sha256"],
                "input_still_identical": hashes(input_paths()) == launch["input_sha256"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    campaign(args.output)
