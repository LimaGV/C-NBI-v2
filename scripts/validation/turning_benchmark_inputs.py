"""Historical parent-grid lineage/audit; never the official standalone H5 loader.

Official Phase8 correction: turning_cnbi_standalone + turning_standalone_analysis.
The preserved408-point archive is historical_parent_grid_analysis.
"""

import csv
import json
import re
from time import perf_counter

import numpy as np

from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import LocalNBIProblem, NBIOptions, local_nbi_geometry, solve_nbi_lattice
from cnbi_v2.optimization import evaluate_responses
from cnbi_v2.simplex import simplex_lattice

from . import turning_local_nbi as frozen
from . import turning_reference_campaign as phase7
from .turning_reference import ROOT, write_csv, write_json

RUN_ID = "turning_reference_sensitivity_20261024"
OUTPUT = ROOT / "results/phase_08_final_benchmark" / RUN_ID
POLICY = ROOT / "docs/policies/benchmark_cardinality_cost.json"
X_EQUIVALENCE = 1e-5
Z_EQUIVALENCE = 1e-5


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def table(path, records):
    keys = list(records[0])
    write_csv(path, keys, [[r[k] for k in keys] for r in records])


def load_historical_parent_grid_inputs():
    folder = phase7.OUTPUT
    for line in (folder / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        if sha256_file(folder / name) != digest:
            raise ValueError(f"frozen Phase7 checksum mismatch: {name}")
    meta = json.loads((folder / "metadata.json").read_text())
    for name, digest in meta["input_sha256"].items():
        if sha256_file(ROOT / name) != digest:
            raise ValueError(f"frozen canonical input mismatch: {name}")
    problem, xtol, tau = phase7.load_problem()
    xs, fs, zs, sources, runs = [], [], [], [], {}
    returned = {}
    offset = 0
    for family in ("NSGA3", "MOEAD"):
        for seed in range(1001, 1031):
            with np.load(
                folder / "runs" / f"{family.lower()}_seed{seed}.npz", allow_pickle=False
            ) as d:
                x, f, z = d["nd_x"], d["nd_f"], d["nd_z"]
                returned[(family, seed)] = len(d["final_population_x"])
                sources.extend(
                    (family, f"{family}_seed{seed}", int(seed), f"final_{int(j)}")
                    for j in d["nd_population_indices"]
                )
            xs.append(x)
            fs.append(f)
            zs.append(z)
            runs[(family, seed)] = np.arange(offset, offset + len(x), dtype=np.int64)
            offset += len(x)
    vrf = phase7.load_pool(folder / "vrf_decisions.npz")
    vrf_ids = np.arange(offset, offset + len(vrf.x), dtype=np.int64)
    xs.append(vrf.x)
    fs.append(vrf.f)
    zs.append(vrf.z)
    sources.extend(("VRF", "historical_vrf", 0, g[0].source_id) for g in vrf.origins)
    offset += len(vrf.x)
    independent_count = offset
    cnbi = phase7.load_pool(folder / "cnbi20_decisions.npz")
    xs.append(cnbi.x)
    fs.append(cnbi.f)
    zs.append(cnbi.z)
    sources.extend(("CNBI", "CNBI_H20", 0, g[0].source_id) for g in cnbi.origins)
    h5 = phase7.load_pool(folder / "cnbi5_pool.npz")
    h5_ids = np.array(
        [offset + int(re.match(r"solution_(\d+)_", g[0].source_id)[1]) for g in h5.origins],
        dtype=np.int64,
    )
    resolution = {}
    origins = rows(phase7.PHASE6 / "provenance.csv")
    for h in (2, 4, 5, 10, 20):
        resolution[h] = np.array(
            sorted(
                {
                    offset + int(r["canonical_solution_id"])
                    for r in origins
                    if int(r["H"]) == h and r["canonical_point_nondominated"] == "True"
                }
            ),
            dtype=np.int64,
        )
    x, f, z = (np.concatenate(a) for a in (xs, fs, zs))
    if (
        not np.array_equal(x[h5_ids], h5.x)
        or len(h5_ids) != 408
        or not np.array_equal(x[resolution[5]], h5.x)
        or not problem.feasible(x).all()
    ):
        raise ValueError("frozen H5 lineage or complete candidate feasibility changed")
    return dict(
        x=x,
        f=f,
        z=z,
        sources=sources,
        runs=runs,
        returned=returned,
        h5=h5_ids,
        vrf=vrf_ids,
        resolution=resolution,
        independent_count=independent_count,
        cnbi_offset=offset,
        problem=problem,
        xtol=xtol,
        tau=tau,
        phase7_metadata=meta,
    )


def direct_cnbi(h):
    """Same solver/options/starts/geometry as Phase6, lattice H solved directly."""
    started = perf_counter()
    models, anchors, payoff, u, amps, signs, opt, catalog = frozen.verified_inputs()
    metadata = json.loads((phase7.PHASE6 / "metadata.json").read_text())
    options = NBIOptions(**metadata["solver_options"])
    points, values, subset, compositions, times, accepted, equalities = [], [], [], [], [], [], []
    core = 0.0
    for j, (_, indices) in enumerate(catalog):
        geometry = local_nbi_geometry(
            payoff[np.ix_(indices, indices)],
            [frozen.DIRECTIONS[k] for k in indices],
            optimality_tolerance=opt[list(indices)],
        )
        problem = LocalNBIProblem(
            tuple(models[k] for k in indices), geometry, anchors[list(indices)], frozen.ALPHA
        )
        lattice = simplex_lattice(len(indices), h)
        tick = perf_counter()
        result = solve_nbi_lattice(problem, lattice, options=options)
        core += perf_counter() - tick
        for solution, composition in zip(result.solutions, lattice.compositions, strict=True):
            accepted.append(solution.accepted)
            points.append(solution.point if solution.accepted else np.full(3, np.nan))
            values.append(
                evaluate_responses(models, solution.point)
                if solution.accepted
                else np.full(8, np.nan)
            )
            subset.append(j)
            padded = np.zeros(3, dtype=np.int64)
            padded[: len(indices)] = composition
            compositions.append(padded)
            times.append(solution.t)
            equalities.append(solution.trials[-1].eq_norm)
    x, f = np.array(points), np.array(values)
    return dict(
        x=x,
        f=f,
        z=(f * signs - u) / amps,
        subsets=np.array(subset),
        compositions=np.array(compositions),
        t=np.array(times),
        accepted=np.array(accepted),
        eq=np.array(equalities),
        solver_seconds=core,
        end_to_end_before_ND_seconds=perf_counter() - started,
    )


def equivalence_audit(output):
    direct = direct_cnbi(5)
    with np.load(phase7.PHASE6 / "local_nbi_solutions_H20.npz", allow_pickle=False) as d:
        lookup = {
            (int(s), tuple(c)): i
            for i, (s, c) in enumerate(
                zip(d["subset_indices"], d["integer_compositions"], strict=True)
            )
        }
        parent = np.array(
            [
                lookup[(int(s), tuple(c * 4))]
                for s, c in zip(direct["subsets"], direct["compositions"], strict=True)
            ]
        )
        dx = np.max(np.abs(direct["x"] - d["x"][parent]), axis=1)
        dz = np.max(np.abs(direct["z"] - d["normalized_responses"][parent]), axis=1)
        records = [
            dict(
                row=i,
                parent_solution_id=int(p),
                subset=int(direct["subsets"][i]),
                H5_composition=json.dumps(direct["compositions"][i].tolist()),
                x_Linf=float(dx[i]),
                z_Linf=float(dz[i]),
                t_direct=float(direct["t"][i]),
                t_archived=float(d["t"][p]),
                eq_direct=float(direct["eq"][i]),
                accepted=bool(direct["accepted"][i]),
            )
            for i, p in enumerate(parent)
        ]
    passed = bool(
        direct["accepted"].all() and dx.max() <= X_EQUIVALENCE and dz.max() <= Z_EQUIVALENCE
    )
    table(output / "h5_direct_equivalence.csv", records)
    np.savez_compressed(
        output / "h5_direct_equivalence.npz",
        x_direct=direct["x"],
        z_direct=direct["z"],
        parent_solution_ids=parent,
        compositions=direct["compositions"],
        subsets=direct["subsets"],
    )
    result = dict(
        status="PASS" if passed else "H5_DIRECT_EQUIVALENCE_FAILED",
        accepted=int(direct["accepted"].sum()),
        subproblems=len(parent),
        max_x_Linf=float(dx.max()),
        max_z_Linf=float(dz.max()),
        x_tolerance_predeclared=X_EQUIVALENCE,
        z_tolerance_predeclared=Z_EQUIVALENCE,
        x_disagreements=int((dx > X_EQUIVALENCE).sum()),
        timing_usable_for_official_H5=passed,
        timing_reported=False,
        solver_or_warm_starts_changed=False,
        archived_baseline_modified=False,
        explanation="Direct H5 continuation can reach different feasible local branches "
        "than H5 membership in the parent H20 continuation; no relaxed gate",
    )
    write_json(output / "h5_direct_equivalence.json", result)
    return result
