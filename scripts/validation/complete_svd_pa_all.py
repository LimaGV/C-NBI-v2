"""Audit every historical local cache, then solve only missing ALL subsets."""

import os

for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[key] = "1"
# ruff: noqa: E402 -- set numerical thread limits before imports
import argparse
import ast
import hashlib
import json
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from importlib.metadata import version
from time import perf_counter

import numpy as np
import run_phase10f_focused_ablation as old

from cnbi_v2.nbi.geometry import local_nbi_geometry
from cnbi_v2.nbi.solver import DEFAULT_OPTIONS, LocalNBIProblem
from cnbi_v2.optimization import Direction
from cnbi_v2.optimization.quadratic import quadratic_responses_from_coefficients
from cnbi_v2.simplex import simplex_lattice
from cnbi_v2.synthetic.ablation import solve_subset
from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, write_json
from cnbi_v2.synthetic.benchmark.configuration import lattice_resolution
from cnbi_v2.synthetic.benchmark.contracts import array_hash
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs

ROOT = old.ROOT
PREVIOUS = ROOT / "results/phase_10_synthetic_ablation/focused_20261031"
OUT = ROOT / "results/phase_10_synthetic_ablation/svd_pa_definitive_20261031"
PLAN = read_json(PREVIOUS / "ablation_protocol.json")
INPUTS = {}


def identity(instance):
    p = PLAN["plans"][instance]
    body = dict(
        coefficients=array_hash(INPUTS[instance].model.coefficients),
        payoff=array_hash(np.array(p["payoff"])),
        anchors=array_hash(np.array(p["anchors"])),
        alpha=INPUTS[instance].alpha,
        solver=asdict(DEFAULT_OPTIONS),
        resolution={k: lattice_resolution(k) for k in range(2, INPUTS[instance].nx + 2)},
    )
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def cache(instance, sid):
    historical = PREVIOUS / "subset_cache" / instance / sid
    return (
        historical
        if (historical / "record.json").exists()
        else OUT / "subset_cache" / instance / sid
    )


def validate(instance, sid, path):
    p = PLAN["plans"][instance]
    data = INPUTS[instance]
    ids = np.array(p["universe"][sid])
    r = read_json(path / "record.json")
    x = np.load(path / "decisions.npz")["decisions"]
    assert x.dtype == np.float64 and x.shape == (len(r["weights"]), data.nx)
    if r.get("decisions_sha256"):
        assert file_hash(path / "decisions.npz") == r["decisions_sha256"]
    if r.get("identity"):
        assert r["identity"] == identity(instance)
    g = local_nbi_geometry(np.array(p["payoff"])[np.ix_(ids, ids)], (Direction.MIN,) * len(ids))
    models = quadratic_responses_from_coefficients(data.model.coefficients, data.nx)
    problem = LocalNBIProblem(
        tuple(models[j] for j in ids), g, np.array(p["anchors"])[ids], data.alpha
    )
    lattice = simplex_lattice(len(ids), lattice_resolution(len(ids)))
    assert len(r["subproblems"]) == len(lattice.weights)
    assert r["weights"] == [s["weight_id"] for s in r["subproblems"] if s["accepted"]]
    for point, w in zip(x, r["weights"], strict=True):
        trials = [t for t in r["trials"] if t["weight_id"] == w and t["accepted"]]
        assert len(trials) == 1
        t = trials[0]
        assert np.array_equal(point, t["point"]) and t["solver_success"]
        v = np.r_[point, t["t"]]
        assert (
            np.linalg.norm(problem.residual(v, lattice.weights[w]))
            <= DEFAULT_OPTIONS.equality_tolerance
        )
        assert problem.sphere_margin(v) >= -DEFAULT_OPTIONS.sphere_tolerance
    return r, x


def initialize():
    global INPUTS
    INPUTS = load_search_inputs(old.SOURCE / old.RSM)


def audit():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = subprocess.check_output(["git", "ls-tree", "-r", "-z", "eb936474"], cwd=ROOT)
    old.BLOBS.update(
        {
            p.split(b"\t")[1].decode(): p.split(b"\t")[0].split()[2].decode()
            for p in entries.split(b"\0")
            if p
        }
    )
    for rel, sha in PLAN["input_sha256"].items():
        assert file_hash(old.protect(rel)) == sha
    assert PLAN["solver"] == asdict(DEFAULT_OPTIONS)
    for package in ("numpy", "scipy"):
        assert PLAN["versions"][package] == version(package)
    before = ast.parse((PREVIOUS / "execution_source/ablation.py").read_text())
    after = ast.parse((ROOT / "src/cnbi_v2/synthetic/ablation/core.py").read_text())

    def funcs(tree):
        return {n.name: ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef)}

    assert funcs(before)["solve_subset"] == funcs(after)["solve_subset"]
    kernels = {}
    for rel in (
        "src/cnbi_v2/nbi/solver.py",
        "src/cnbi_v2/nbi/geometry.py",
        "src/cnbi_v2/chim/normalization.py",
        "src/cnbi_v2/optimization/quadratic.py",
        "src/cnbi_v2/optimization/anchors.py",
        "src/cnbi_v2/simplex/lattice.py",
        "src/cnbi_v2/synthetic/benchmark/configuration.py",
    ):
        frozen = subprocess.check_output(["git", "show", "eb936474:" + rel], cwd=ROOT)
        assert frozen == (ROOT / rel).read_bytes()
        kernels[rel] = file_hash(ROOT / rel)
    inventory = []
    missing = []
    universes = 0
    for instance, p in PLAN["plans"].items():
        a0, x0 = old.metadata(instance, "A0")
        a1, x1 = old.metadata(instance, "A1")
        for doc in (a0, a1):
            assert doc["coefficients_sha256"] == array_hash(INPUTS[instance].model.coefficients)
            assert np.array_equal(doc["diagnostics"]["nominal_payoff"], p["payoff"])
            assert np.array_equal(doc["diagnostics"]["nominal_anchors"], p["anchors"])
        for sid, ids in p["universe"].items():
            universes += 1
            path = PREVIOUS / "subset_cache" / instance / sid
            n = len(simplex_lattice(len(ids), lattice_resolution(len(ids))).weights)
            if not (path / "record.json").exists():
                missing.append(
                    dict(instance=instance, subset_id=sid, nx=INPUTS[instance].nx, subproblems=n)
                )
                continue
            r, x = validate(instance, sid, path)
            if r["source"] in ("A0", "A1"):
                d, raw = (a0, x0) if r["source"] == "A0" else (a1, x1)
                expected = old.extract(d, raw, sid, r["source"])
                assert np.array_equal(x, expected["X"]) and r["weights"] == expected["weights"]
            inventory.append(
                dict(
                    instance=instance,
                    subset_id=sid,
                    identity=identity(instance),
                    record_sha256=file_hash(path / "record.json"),
                    decisions_sha256=file_hash(path / "decisions.npz"),
                )
            )
    assert len(inventory) == 477 and universes == 855
    assert len(missing) == 378 and sum(s["subproblems"] for s in missing) == 13208
    write_json(
        OUT / "cache_compatibility_audit.json",
        dict(
            status="PASS",
            historical_caches=inventory,
            universe_count=universes,
            missing=missing,
            kernel_sha256=kernels,
            models_anchors_payoff_H_solver_tolerances_verified=True,
            solve_subset_AST_unchanged=True,
            input_sha256=old.INPUT_HASHES,
        ),
    )
    print("AUDIT PASS:477 caches;378 missing;13208 NBI subproblems", flush=True)


def work(task):
    instance, sid = task["instance"], task["subset_id"]
    path = OUT / "subset_cache" / instance / sid
    if (path / "record.json").exists():
        validate(instance, sid, path)
        return
    p = PLAN["plans"][instance]
    r = solve_subset(
        INPUTS[instance], np.array(p["payoff"]), np.array(p["anchors"]), tuple(p["universe"][sid])
    )
    assert not r["counters"].get("quadratic_ball_solves", 0)
    path.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path / "decisions.npz", decisions=r.pop("X"))
    r.update(
        source="NEW_ALL",
        identity=identity(instance),
        decisions_sha256=file_hash(path / "decisions.npz"),
    )
    write_json(path / "record.json", r)
    validate(instance, sid, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nx", type=int, choices=[2, 3], required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    initialize()
    if not (OUT / "cache_compatibility_audit.json").exists():
        audit()
    verified = read_json(OUT / "cache_compatibility_audit.json")
    for relative, sha in verified["kernel_sha256"].items():
        assert file_hash(ROOT / relative) == sha
    for relative, sha in verified["input_sha256"].items():
        assert file_hash(old.SOURCE / relative) == sha
    assert PLAN["solver"] == asdict(DEFAULT_OPTIONS)
    for package in ("numpy", "scipy"):
        assert PLAN["versions"][package] == version(package)
    for item in verified["historical_caches"]:
        path = PREVIOUS / "subset_cache" / item["instance"] / item["subset_id"]
        assert file_hash(path / "record.json") == item["record_sha256"]
        assert file_hash(path / "decisions.npz") == item["decisions_sha256"]
    if args.nx == 3:
        assert read_json(OUT / "nx2_gate.json")["status"] == "PASS"
    tasks = [t for t in verified["missing"] if t["nx"] == args.nx]
    pending = [
        t
        for t in tasks
        if not (OUT / "subset_cache" / t["instance"] / t["subset_id"] / "record.json").exists()
    ]
    gate = OUT / f"nx{args.nx}_gate.json"
    if gate.exists() and not pending:
        for t in tasks:
            validate(t["instance"], t["subset_id"], cache(t["instance"], t["subset_id"]))
        print("ALREADY COMPLETE: verified caches; no solves or timing overwrite", flush=True)
        return
    begun = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize) as pool:
        futures = [pool.submit(work, t) for t in pending]
        for count, f in enumerate(as_completed(futures), 1):
            f.result()
            if count % 25 == 0:
                print("nx", args.nx, "new completed", count, "/", len(pending), flush=True)
    rows = []
    for instance, p in PLAN["plans"].items():
        if INPUTS[instance].nx != args.nx:
            continue
        new = []
        n = 0
        for sid in p["universe"]:
            r, x = validate(instance, sid, cache(instance, sid))
            n += len(r["subproblems"])
            if r["source"] == "NEW_ALL":
                new.append(r)
        row = dict(
            instance=instance,
            status="PASS",
            B=p["B"],
            subsets=len(p["universe"]),
            subproblems=n,
            added_subsets=len(new),
            added_solver_seconds_observed=sum(r["solver_seconds"] for r in new),
            added_value_calls=sum(r["counters"].get("scalar_quadratic_values", 0) for r in new),
            added_gradients=sum(r["counters"].get("scalar_quadratic_gradients", 0) for r in new),
            new_MC_or_anchor_solves=0,
        )
        write_json(OUT / "instances" / instance / "execution_cost.json", row)
        rows.append(row)
    write_json(
        OUT / f"nx{args.nx}_gate.json",
        dict(
            status="PASS",
            instances=rows,
            newly_completed_this_invocation=len(pending),
            wall_seconds_this_invocation=perf_counter() - begun,
            integrity_and_measured_cost_verified=True,
        ),
    )
    print("STAGE COMPLETE nx", args.nx, "new subset solves", len(pending), flush=True)


if __name__ == "__main__":
    main()
