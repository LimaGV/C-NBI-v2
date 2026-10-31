"""Single-entrypoint, real incremental C-NBI using ADR0009 gaps; no evaluation study."""

import os

for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
import csv
import importlib.util
import json
import multiprocessing
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path

import numpy as np
from phase10f_inputs import INPUT, ROOT, RSM, tasks
from run_phase10d_campaign import physical_masks

from cnbi_v2.chim.parallel_analysis import PACheckpoint
from cnbi_v2.chim.spectral_gap_stop import SpectralGapStopPolicy, evaluate_gap_early_stop
from cnbi_v2.synthetic.benchmark.archive import file_hash, save_output, write_json
from cnbi_v2.synthetic.benchmark.contracts import array_hash
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs
from cnbi_v2.synthetic.early_stop import runner as original_runner

POLICY = SpectralGapStopPolicy(
    tuple(range(100, 2001, 100)), 100, 300, 3, 500, 0.05, float(np.finfo(float).tiny), 2000
)
_INPUTS = None
_RUNNER = None


def gap_guard(history, observed, numerical_scales, policy, *, certified=True):
    """Reuse ADR0009 exactly on the consumed prefix; no observed/margin guard."""
    if tuple(r.B for r in history) != policy.checkpoints[: len(history)]:
        raise ValueError("checkpoints must be the consumed100:100 prefix")
    prefix_policy = replace(
        policy, checkpoints=tuple(r.B for r in history), maximum_B=history[-1].B
    )
    assessment = evaluate_gap_early_stop(history, prefix_policy)
    last = assessment.trajectory[-1]
    stop = last.early_stop_condition_met and last.B < policy.maximum_B
    return dict(
        **asdict(last),
        stop=stop,
        status="EARLY_STOP"
        if stop
        else ("MAX_B_REACHED" if last.B == policy.maximum_B else "CONTINUE"),
    )


def isolated_runner():
    # A private module instance changes only the policy callback. Original
    # source/module/globals and previous campaign fingerprints stay untouched.
    name = "cnbi_v2.synthetic.early_stop._adr0009_execution"
    spec = importlib.util.spec_from_file_location(name, original_runner.__file__)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    module.assess_stop = gap_guard
    return module


def initialize(masks):
    global _INPUTS, _RUNNER
    if sys.platform == "win32":
        import ctypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        pin = kernel.SetProcessAffinityMask
        pin.argtypes, pin.restype = [ctypes.c_void_p, ctypes.c_size_t], ctypes.c_int
        assert pin(kernel.GetCurrentProcess(), masks.get()), ctypes.get_last_error()
    _INPUTS = load_search_inputs(RSM)
    _RUNNER = isolated_runner()


def run_case(task, directory):
    output_dir = Path(directory)
    instance = task["instance_id"]
    checkpoint = output_dir / f"checkpoints/{instance}.json"
    started = time.perf_counter()
    record = dict(instance_id=instance, seed=task["seed"], state="RUNNING", attempt=1)
    write_json(checkpoint, record)
    batch_hashes = {}

    def sink(B, arrays):
        target = output_dir / f"batches/{instance}/B{B:04d}.npz"
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            np.savez_compressed(stream, **arrays)
        batch_hashes[target.relative_to(output_dir).as_posix()] = file_hash(target)
        write_json(output_dir / f"progress/{instance}.json", dict(B_generated=B, B_reoptimized=B))

    try:
        data = _INPUTS[instance]
        coefficient_hash = array_hash(data.model.coefficients)
        result = _RUNNER.run_adaptive(data, int(task["seed"]), POLICY, sink=sink)
        B = result.diagnostics["B"]
        assert (
            B
            == result.diagnostics["generated_samples"]
            == result.diagnostics["reoptimized_samples"]
        )
        assert result.counters["quadratic_ball_solves"] == (B + 1) * data.m
        assert len(batch_hashes) == B // 100
        assert array_hash(data.model.coefficients) == coefficient_hash
        # Keep compact stopping records; final thresholds, NBI trials and raw
        # samples remain available in the reused complete output format.
        for row in result.diagnostics["checkpoints"]:
            for key in ("quantile_ids", "decision_quantiles", "component_passes"):
                row.pop(key, None)
        result.diagnostics["method"] = "C-NBI-ES-ADR0009"
        hashes = save_output(
            output_dir,
            instance,
            result,
            dict(task=task, policy=asdict(POLICY), coefficients_sha256=coefficient_hash),
        )
        hashes.update(batch_hashes)
        record.update(
            state="COMPLETED" if result.status == "COMPLETED" else "FAILED",
            algorithm_status=result.status,
            B_effective=B,
            stopping_status=result.diagnostics["stopping_status"],
            output_count=len(result.decisions),
            selected_subsets=result.diagnostics["selected_subsets"],
            kernel_seconds=result.timings["total"],
            payload_checksums=hashes,
        )
    except Exception as error:
        record.update(
            state="FAILED",
            error=f"{type(error).__name__}: {error}",
            traceback=traceback.format_exc(),
            partial_batch_checksums=batch_hashes,
        )
    record["worker_seconds"] = time.perf_counter() - started
    write_json(checkpoint, record)
    return {
        k: v
        for k, v in record.items()
        if k not in {"payload_checksums", "partial_batch_checksums", "traceback"}
    }


def self_test(directory):
    ids = ("GLOBAL:1", "GLOBAL:2", "C_1_2:1", "C_1_2_3:1", "C_1_2_3:2")
    history = [
        PACheckpoint(
            B,
            2,
            "MONOTONE_PA_PATTERN",
            (),
            frozenset({"C_1_2", "C_1_2_3"}),
            ids,
            np.array([10.0, 8.0, 1.0, 5.0, 2.0]),
            (1, 1),
        )
        for B in POLICY.checkpoints[:5]
    ]
    assert not gap_guard(history[:4], None, None, POLICY)["stop"]
    assert gap_guard(history, None, None, POLICY)["stop"]
    changed = list(history)
    changed[2] = replace(changed[2], decision_quantiles=np.array([10.0, 8.0, 1.0, 5.0, 4.0]))
    assert not gap_guard(changed, None, None, POLICY)["stop"]  # First transition matters.
    changed[2] = replace(history[2], global_dimension=1)
    assert not gap_guard(changed, None, None, POLICY)["stop"]
    changed[2] = replace(history[2], selected_ids=frozenset({"C_1_2"}))
    assert not gap_guard(changed, None, None, POLICY)["stop"]
    item = tasks()[0]
    data = load_search_inputs(RSM)[item["instance_id"]]
    module = isolated_runner()
    sampler = module.iter_coefficient_batches
    consumed = []

    def counted(*args, **kwargs):
        for batch in sampler(*args, **kwargs):
            consumed.append(len(batch))
            yield batch

    module.iter_coefficient_batches = counted
    first = module.run_adaptive(data, int(item["seed"]), POLICY)
    assert sum(consumed) == first.diagnostics["B"]
    module.iter_coefficient_batches = sampler
    second = module.run_adaptive(data, int(item["seed"]), POLICY)
    assert first.diagnostics["B"] == second.diagnostics["B"] >= 500
    for key in first.arrays:
        assert np.array_equal(first.arrays[key], second.arrays[key])
    assert np.array_equal(first.decisions, second.decisions)
    assert first.counters["mc_anchor_solves"] == first.diagnostics["B"] * data.m
    write_json(
        directory / "self_test.json",
        dict(
            status="PASS",
            full_kernel_runs=2,
            B=first.diagnostics["B"],
            deterministic=True,
            no_future_batches=True,
            eligibility_and_both_transitions=True,
            dimension_and_ids=True,
        ),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    directory = args.output or ROOT / (
        "results/phase_10_synthetic_early_stop/gaps_adr0009_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    directory.mkdir(parents=True, exist_ok=False)
    (directory / ".gitattributes").write_bytes(b"*.log -text\n")
    source_paths = [
        Path(__file__),
        Path(original_runner.__file__),
        ROOT / "src/cnbi_v2/chim/spectral_gap_stop.py",
        ROOT / "docs/decisions/0009-pa-early-stopping-policy.md",
    ]
    source_paths = [p for p in source_paths if p.exists()]
    source_paths.extend(RSM.glob("*.npz"))
    source_hashes = {str(p.relative_to(ROOT)): file_hash(p) for p in source_paths}
    write_json(
        directory / "manifest.json",
        dict(
            policy=asdict(POLICY),
            tasks=tasks(),
            monitor="all GLOBAL gaps and all gaps of selected local subsets; pairs have no gap",
            reused_runner=str(Path(original_runner.__file__).relative_to(ROOT)),
            isolated_callback=True,
            source_sha256=source_hashes,
            original_seed_manifest_sha256=file_hash(INPUT / "seed_manifest.json"),
        ),
    )
    self_test(directory)
    print(
        json.dumps(dict(state="STARTED", cases=135, output=str(directory), self_test="PASS")),
        flush=True,
    )
    masks = physical_masks()[:6] if sys.platform == "win32" else [1] * 6
    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    for mask in masks:
        queue.put(mask)
    started = time.perf_counter()
    rows = []
    with (directory / "campaign.log").open("x", encoding="utf-8", newline="\n") as log:
        with ProcessPoolExecutor(
            max_workers=len(masks), mp_context=context, initializer=initialize, initargs=(queue,)
        ) as pool:
            futures = [pool.submit(run_case, task, str(directory)) for task in tasks()]
            for future in as_completed(futures):
                row = future.result()
                rows.append(row)
                log.write(json.dumps(row) + "\n")
                log.flush()
                write_json(
                    directory / "campaign_checkpoint.json",
                    dict(
                        completed=sum(r["state"] == "COMPLETED" for r in rows),
                        failed=sum(r["state"] == "FAILED" for r in rows),
                        planned=135,
                    ),
                )
    seconds = time.perf_counter() - started
    for path, expected in source_hashes.items():
        assert file_hash(ROOT / path) == expected, "input/source modified: " + path
    rows.sort(key=lambda r: r["instance_id"])
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (directory / "runs.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    good = [r for r in rows if r["state"] == "COMPLETED"]
    values = [r["B_effective"] for r in good]
    summary = dict(
        completed=len(good),
        planned=135,
        B_median=float(np.median(values)) if values else None,
        B_distribution=dict(sorted(Counter(values).items())),
        early_stops=sum(B < 2000 for B in values),
        total_seconds=seconds,
        summed_kernel_seconds=sum(r.get("kernel_seconds", 0) for r in rows),
        failures=[r for r in rows if r["state"] != "COMPLETED"],
        output=str(directory),
    )
    write_json(directory / "summary.json", summary)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
