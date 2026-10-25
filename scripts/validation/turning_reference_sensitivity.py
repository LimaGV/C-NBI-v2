"""Historical parent-grid Phase8A reference construction, retained for provenance.

Reevaluate corrected H5 with turning_standalone_analysis and the saved references;
do not regenerate the stored subsamplings. No VRF/EA campaign executes here.
"""

import argparse
import hashlib
import json
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import numpy as np
from numpy.testing import assert_array_equal
from scipy.spatial import cKDTree

from cnbi_v2.benchmark.dominance import DominanceIndex
from cnbi_v2.benchmark.hypervolume import HVGrid, historical_box
from cnbi_v2.benchmark.metrics import gd_igd, summary
from cnbi_v2.benchmark.selection import farthest_order, seed_subsamples
from cnbi_v2.data import sha256_file

from . import turning_benchmark_inputs as data
from . import turning_reference_campaign as phase7
from .turning_reference import ROOT, write_json


def union_mask(cache, indices):
    result = np.zeros(cache.shape[1], dtype=np.uint8)
    for start in range(0, len(indices), 512):
        result |= np.bitwise_or.reduce(cache[indices[start : start + 512]], axis=0)
    return result


def mask_worker(task):
    start, stop, points_path, samples_path, cache_path, shape, lo, ref, power = task
    points = np.load(points_path, mmap_mode="r")
    samples = np.load(samples_path, mmap_mode="r")
    cache = np.memmap(cache_path, dtype=np.uint8, mode="r+", shape=tuple(shape))
    grid = HVGrid(np.array(lo), np.array(ref), power=power)
    cache[start:stop] = grid.masks(points[start:stop], samples)
    cache.flush()
    return stop - start


def prepare_cache(inputs, output, grid, workers):
    cache_dir = ROOT / "experiments/runs" / data.RUN_ID
    cache_dir.mkdir(parents=True, exist_ok=True)
    points = cache_dir / "canonical_z.npy"
    samples = cache_dir / "hv_samples.npy"
    path = cache_dir / "point_attainment.uint8"
    identity = dict(
        z_sha256=hashlib.sha256(inputs["z"].tobytes()).hexdigest(),
        reference=grid.reference.tolist(),
        lower=grid.lower.tolist(),
        power=grid.power,
        seeds=grid.seeds,
        shape=[len(inputs["z"]), grid.bytes_per_point],
    )
    marker = cache_dir / "cache_metadata.json"
    fingerprint = phase7.fingerprint(identity)
    if marker.exists():
        meta = json.loads(marker.read_text())
        if meta["fingerprint"] == fingerprint and sha256_file(path) == meta["sha256"]:
            return np.memmap(path, dtype=np.uint8, mode="r", shape=tuple(identity["shape"])), meta
        raise ValueError("refusing incompatible/corrupted numerical cache")
    np.save(points, inputs["z"], allow_pickle=False)
    sample_values = grid.samples()
    np.save(samples, sample_values, allow_pickle=False)
    cache = np.memmap(path, dtype=np.uint8, mode="w+", shape=tuple(identity["shape"]))
    cache.flush()
    del cache
    tasks = [
        (
            i,
            min(i + 128, len(inputs["z"])),
            str(points),
            str(samples),
            str(path),
            identity["shape"],
            grid.lower.tolist(),
            grid.reference.tolist(),
            grid.power,
        )
        for i in range(0, len(inputs["z"]), 128)
    ]
    completed = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(mask_worker, task) for task in tasks]
        for future in as_completed(futures):
            completed += future.result()
            if completed % 2048 < 128 or completed == len(inputs["z"]):
                print(f"HV quadrature masks {completed}/{len(inputs['z'])}", flush=True)
    meta = dict(
        fingerprint=fingerprint,
        identity=identity,
        sha256=sha256_file(path),
        samples_sha256=hashlib.sha256(sample_values.tobytes()).hexdigest(),
        cache_in_git=False,
        cache_bytes=path.stat().st_size,
        note="regenerable packed pointwise integration cache, not an optimization archive",
    )
    write_json(marker, meta)
    write_json(output / "hv_numerical_cache.json", meta)
    return np.memmap(path, dtype=np.uint8, mode="r", shape=tuple(identity["shape"])), meta


def graph(inputs, output):
    path = output / "dominance_index.npz"
    n = inputs["independent_count"]
    if path.exists():
        with np.load(path, allow_pickle=False) as d:
            return DominanceIndex(n, d["dominators"], d["dominated"], d["duplicate_pairs"])
    tick = perf_counter()
    index = DominanceIndex.build(inputs["x"][:n], inputs["z"][:n], inputs["xtol"], inputs["tau"])
    np.savez_compressed(
        path,
        dominators=index.dominators,
        dominated=index.dominated,
        duplicate_pairs=index.duplicate_pairs,
    )
    print(
        f"Exact numerical dominance graph: {len(index.dominators)} edges, "
        f"{perf_counter() - tick:.2f}s",
        flush=True,
    )
    return index


def summarize(records):
    result = []
    for r in (5, 10, 15, 20, 25, 30):
        selected = [row for row in records if row["r"] == r and row["selection"] != "prefix"]
        for name in (
            "GD_CNBI5",
            "IGD_CNBI5",
            "HV_reference",
            "reference_size",
            "NSGA3_exclusive",
            "MOEAD_exclusive",
            "VRF_exclusive",
            "shared",
        ):
            result.append(dict(r=r, metric=name, **summary([v[name] for v in selected])))
    return result


def run(output):
    started = perf_counter()
    if output.exists() and (output / "phase8a_completion.json").exists():
        raise ValueError("completed scientific archive is immutable; choose a separate output")
    output.mkdir(parents=True, exist_ok=True)
    protocol = json.loads(data.POLICY.read_text())
    launch = dict(
        git_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        working_tree_dirty_at_launch=bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
        ),
        started_utc=datetime.now(UTC).isoformat(),
        policy_sha256=sha256_file(data.POLICY),
        code_sha256=phase7.hashes(
            [
                Path(__file__),
                Path(data.__file__),
                *sorted((ROOT / "src/cnbi_v2/benchmark").glob("*.py")),
            ]
        ),
    )
    if launch["working_tree_dirty_at_launch"]:
        raise ValueError("freeze and commit sensitivity code/config before the scientific study")
    write_json(output / "phase8a_launch.json", launch)
    inputs = data.load_historical_parent_grid_inputs()
    x, z = inputs["x"], inputs["z"]
    np.savez_compressed(output / "canonical_candidates.npz", x=x, natural_f=inputs["f"], z=z)
    data.table(
        output / "provenance.csv",
        [
            dict(point_id=i, family=f, run_id=r, seed=s, source_id=source)
            for i, (f, r, s, source) in enumerate(inputs["sources"])
        ],
    )
    gate = data.equivalence_audit(output)
    write_json(output / "h5_timing_gate.json", gate)
    lo, ref = historical_box(z)
    grid = HVGrid(lo, ref, power=protocol["hv_quadrature"]["power"])
    ref_body = dict(
        lower=lo.tolist(),
        reference=ref.tolist(),
        rule=protocol["hv_reference_rule"],
        source="complete canonical Phase7 candidates, including CNBI for common HV bounds",
        strictly_dominates_all_candidates=bool(np.all(z < ref)),
    )
    ref_body["sha256"] = phase7.fingerprint(ref_body)
    write_json(output / "hv_reference_point.json", ref_body)
    index = graph(inputs, output)
    all_ids = np.arange(inputs["independent_count"], dtype=np.int64)
    full, _ = index.front(all_ids)
    saved = phase7.load_pool(phase7.OUTPUT / "reference_minus_cnbi.npz")
    assert_array_equal(x[full], saved.x)
    assert_array_equal(z[full], saved.z)
    if len(full) != 18503:
        raise ValueError("full independent reference no longer matches Phase7")
    np.savez_compressed(output / "reference_final.npz", point_ids=full, x=x[full], z=z[full])
    # Postprocessing may be parallel; the later dedicated timing is strictly serial.
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    cache, cache_meta = prepare_cache(inputs, output, grid, protocol["postprocessing_workers"])
    h5z = z[inputs["h5"]]
    nearest_to_h5 = cKDTree(h5z).query(z, k=1, eps=0.0, workers=1)[0]
    family = np.array([v[0] for v in inputs["sources"]])
    front_sets, origin_sets, representative_sets, names = [], [], [], []

    def reference_record(ids, name):
        front, canonical = index.front(ids)
        if np.any(family[ids] == "CNBI") or np.any(family[front] == "CNBI"):
            raise ValueError("CNBI leaked into independent sensitivity reference")
        flags = np.zeros((index.n, 3), dtype=bool)
        for col, f in enumerate(("NSGA3", "MOEAD", "VRF")):
            flags[canonical[family[ids] == f], col] = True
        exclusive = flags[front].sum(axis=1) == 1
        counts = [int(np.count_nonzero(flags[front, j] & exclusive)) for j in range(3)]
        hv = grid.estimate(union_mask(cache, front))
        gd = float(cKDTree(z[front]).query(h5z, k=1, eps=0.0, workers=1)[0].mean())
        origin_keep = np.isin(canonical, front)
        front_sets.append(front)
        origin_sets.append(ids[origin_keep])
        representative_sets.append(canonical[origin_keep])
        names.append(name)
        return dict(
            reference_name=name,
            reference_size=len(front),
            GD_CNBI5=gd,
            IGD_CNBI5=float(nearest_to_h5[front].mean()),
            HV_reference=hv["HV"],
            HV_QMC_SE=hv["HV_QMC_SE"],
            NSGA3_exclusive=counts[0],
            MOEAD_exclusive=counts[1],
            VRF_exclusive=counts[2],
            shared=int((~exclusive).sum()),
        )

    rng = np.random.Generator(np.random.PCG64(20261024))
    results, selections = [], {}
    for r in (5, 10, 15, 20, 25, 30):
        subsets = (
            np.arange(30).reshape(1, 30) if r == 30 else seed_subsamples(r, count=100, rng=rng)
        )
        selections[str(r)] = subsets
        records = [
            ("full" if r == 30 else "subsample", b, selected) for b, selected in enumerate(subsets)
        ]
        if r < 30:
            records.append(("prefix", 0, np.arange(r)))
        for kind, b, selected in records:
            ids = np.sort(
                np.concatenate(
                    [
                        inputs["runs"][(f, 1001 + int(s))]
                        for f in ("NSGA3", "MOEAD")
                        for s in selected
                    ]
                    + [inputs["vrf"]]
                )
            )
            name = f"r{r}_{kind}_{b:03}"
            row = reference_record(ids, name)
            row.update(
                r=r, replicate=b, selection=kind, seeds=json.dumps((1001 + selected).tolist())
            )
            results.append(row)
            if b % 25 == 0 and kind != "prefix":
                print(f"r{r} subset{b + 1}/{len(subsets)} ND={row['reference_size']}", flush=True)
    data.table(output / "reference_run_sensitivity_replicates.csv", results)
    data.table(output / "reference_run_sensitivity.csv", summarize(results))
    np.savez_compressed(output / "reference_seed_subsamples.npz", **selections)
    composition = []
    for label, families in (
        ("N", ("NSGA3",)),
        ("M", ("MOEAD",)),
        ("NM", ("NSGA3", "MOEAD")),
        ("NMV", ("NSGA3", "MOEAD", "VRF")),
        ("MV", ("MOEAD", "VRF")),
        ("NV", ("NSGA3", "VRF")),
    ):
        selected = [
            inputs["runs"][(f, s)] for f in families if f != "VRF" for s in range(1001, 1031)
        ]
        if "VRF" in families:
            selected.append(inputs["vrf"])
        ids = np.sort(np.concatenate(selected))
        composition.append(dict(composition=label, **reference_record(ids, f"composition_{label}")))
    data.table(output / "reference_composition_sensitivity.csv", composition)
    marginal = []
    by_name = {r["composition"]: r for r in composition}
    for added, base in (("VRF", "NM"), ("NSGA3", "MV"), ("MOEAD", "NV")):
        a, b = by_name[base], by_name["NMV"]
        marginal.append(
            dict(
                added_family=added,
                base=base,
                full="NMV",
                delta_cardinality=b["reference_size"] - a["reference_size"],
                delta_HV=b["HV_reference"] - a["HV_reference"],
                delta_GD=b["GD_CNBI5"] - a["GD_CNBI5"],
                delta_IGD=b["IGD_CNBI5"] - a["IGD_CNBI5"],
            )
        )
    data.table(output / "reference_marginal_effects.csv", marginal)
    order = farthest_order(z[full])
    np.savez_compressed(output / "farthest_orderings.npz", reference_final=full[order])
    cardinality = []
    for k in protocol["reference_K"]:
        ids = full[order[:k]]
        gd, igd = gd_igd(h5z, z[ids])
        cardinality.append(
            dict(K_R=k, GD_CNBI5=gd, IGD_CNBI5=igd, **grid.estimate(union_mask(cache, ids)))
        )
    data.table(output / "reference_cardinality_sensitivity.csv", cardinality)
    # Ragged lineage uses only numeric arrays, never pickle/object arrays.
    front_offsets = np.r_[0, np.cumsum([len(v) for v in front_sets])]
    origin_offsets = np.r_[0, np.cumsum([len(v) for v in origin_sets])]
    np.savez_compressed(
        output / "reference_sensitivity_lineage.npz",
        names=np.array(names),
        front_ids=np.concatenate(front_sets),
        front_offsets=front_offsets,
        origin_ids=np.concatenate(origin_sets),
        origin_representatives=np.concatenate(representative_sets),
        origin_offsets=origin_offsets,
    )
    precision = []
    for label, ids in (("CNBI5", inputs["h5"]), ("VRF", inputs["vrf"]), ("R30", full)):
        mask = union_mask(cache, ids)
        for power in (14, 15, 16):
            values = grid.values(mask, power=power)
            precision.append(
                dict(
                    set=label,
                    power=power,
                    HV=float(values.mean()),
                    SE=float(values.std(ddof=1) / np.sqrt(4)),
                )
            )
    data.table(output / "hv_precision_diagnostics.csv", precision)
    completion = dict(
        status="PHASE8A_COMPLETE",
        source_commit=launch["git_commit"],
        wall_seconds=perf_counter() - started,
        source_candidates=len(x),
        independent_candidates=index.n,
        full_reference_size=len(full),
        references_evaluated=len(results),
        no_CNBI_in_any_reference=True,
        VRF_executions=0,
        new_EA_reference_runs=0,
        reference_final_sha256=sha256_file(output / "reference_final.npz"),
        phase7_checksums_sha256=sha256_file(phase7.OUTPUT / "checksums.sha256"),
        hv_reference_sha256=ref_body["sha256"],
        quadrature_cache=cache_meta,
        H5_timing_gate=gate["status"],
        quality_baseline_preserved=True,
        reference_status="FROZEN_EMPIRICAL_REFERENCE_FOR_QUALITY_NO_GROUND_TRUTH",
    )
    write_json(output / "phase8a_completion.json", completion)
    print(json.dumps(completion, default=str), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=data.OUTPUT)
    args = parser.parse_args()
    run(args.output)
