"""Offline parallel orchestration of the unchanged frozen Phase10C evaluator.

All search workers must have exited. No metric is returned to any algorithm.
Each process evaluates one structural cell, sharing its fixed context across
five replicas and four methods; no reference/metric recalibration occurs.
"""

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import perf_counter

import numpy as np
from execute_synthetic_benchmark import OUTPUT, ROOT, run_id, verify_protocol, write_csv
from run_phase10d_campaign import PIN_AND_RUN, physical_masks

from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, verify_payload, write_json
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context


def evaluate_cell(directory: Path, stage: str, sid: str) -> None:
    verify_protocol(directory)
    context = load_evaluation_context(
        ROOT/"results/phase_10_synthetic_pareto/analytical_20261029", sid,
        ROOT/"results/phase_10_synthetic_generation/structural_20261029")
    tasks = [task for task in read_json(directory/"seed_manifest.json")["tasks"]
             if task["stage"] == stage and task["scenario_id"] == sid]
    for task in tasks:
        name = run_id(task)
        checkpoint = directory/f"campaign_checkpoints/{name}.json"
        if not checkpoint.exists():
            raise ValueError("cannot evaluate a task that has not run")
        cp = read_json(checkpoint)
        if cp["state"] == "RUNNING":
            raise ValueError("truth evaluation cannot overlap the same task's search")
        if "payload_checksums" not in cp:
            write_json(directory/f"external_evaluation/{name}.json", dict(
                metrics=dict(GD=None, IGD=None, HV=None, Spacing=None, Sparsity=None,
                             status="UNDEFINED_FAILED_RUN_WITHOUT_PAYLOAD"),
                diagnostics=dict(algorithm_status=cp.get("algorithm_status", cp["state"])),
                external_evaluation_seconds=0., no_decision_payload=True,
            ))
            continue
        verify_payload(directory, cp["payload_checksums"])
        payload = cp.get("payload_run_id", name)
        with np.load(directory/f"raw_decisions/{payload}.npz", allow_pickle=False) as arrays:
            decisions = arrays["decisions"]
        started = perf_counter()
        evaluated = context.evaluate(
            sid, int(task["replica_id"]), task["method"], decisions,
            dict(protocol_hash=cp["protocol_hash"], run_id=name,
                 algorithm_status=cp.get("algorithm_status")),
            seconds=cp.get("timings", {}).get("total"),
            nfe=cp.get("counters", {}).get(
                "model_vector_point_events",
                cp.get("counters", {}).get("original_rsm_point_evaluations"),
            ),
        )
        seconds = perf_counter()-started
        target = directory/f"external_evaluation/{name}.npz"
        target.parent.mkdir(exist_ok=True)
        np.savez_compressed(target, true_responses=evaluated.true_responses,
                            normalized_responses=evaluated.normalized_responses,
                            feasible_mask=evaluated.feasible_mask,
                            unique_indices=evaluated.unique_indices,
                            nondominated_indices=evaluated.nondominated_indices)
        write_json(target.with_suffix(".json"), dict(
            metrics=evaluated.metrics, diagnostics=evaluated.diagnostics,
            external_evaluation_seconds=seconds, oracle_feedback_to_search=False,
            evaluator_source="frozen_Phase10C_API", reference_count=5000,
        ))
    print(json.dumps(dict(scenario_id=sid, stage=stage, evaluated=len(tasks))), flush=True)


def evaluate(directory: Path, stage: str) -> None:
    verify_protocol(directory)
    if (directory/"scheduler.lock").exists():
        raise ValueError("wait until optimization scheduler exits before evaluating truth")
    tasks = [task for task in read_json(directory/"seed_manifest.json")["tasks"]
             if task["stage"] == stage]
    for task in tasks:
        cp = directory/f"campaign_checkpoints/{run_id(task)}.json"
        if not cp.exists() or read_json(cp)["state"] in {"PENDING", "RUNNING"}:
            raise ValueError("all planned search attempts must finish before offline evaluation")
    scenarios = sorted({task["scenario_id"] for task in tasks})
    masks = physical_masks()[:6]
    started = perf_counter()
    source_hash = file_hash(Path(__file__))
    write_json(directory/f"external_evaluation_plan_{stage}.json", dict(
        source=str(Path(__file__).relative_to(ROOT)), source_sha256=source_hash,
        stage=stage, max_processes=6, threads_per_process=1, physical_core_masks=masks,
        evaluator="cnbi_v2.synthetic.pareto.serialization.load_evaluation_context",
        mathematical_protocol="unchanged_Phase10C", reference_points=5000,
        search_already_terminated=True, feedback_to_search=False,
    ))

    def worker(index: int, sid: str) -> int:
        env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                   MKL_NUM_THREADS="1", PHASE10D_CPU_MASK=str(masks[index % len(masks)]))
        log = directory/f"logs/evaluation__{stage}__{sid}.log"
        with log.open("ab") as stream:
            result = subprocess.run([
                sys.executable, "-c", PIN_AND_RUN, str(Path(__file__).resolve()),
                "--directory", str(directory), "--stage", stage, "--scenario", sid,
            ], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError("offline evaluator failed: "+sid)
        print(json.dumps(dict(scenario_id=sid, stage=stage, status="EVALUATED")), flush=True)
        return 1

    # Each lane keeps one physical core; cells are distributed before execution.
    def lane(index: int) -> int:
        return sum(worker(index, sid) for sid in scenarios[index::len(masks)])

    with ThreadPoolExecutor(max_workers=len(masks)) as pool:
        total = sum(future.result() for future in as_completed(
            [pool.submit(lane, index) for index in range(len(masks))]))
    rows = []
    for task in tasks:
        name = run_id(task)
        record = read_json(directory/f"external_evaluation/{name}.json")
        cp = read_json(directory/f"campaign_checkpoints/{name}.json")
        rows.append(dict(**task, state=cp["state"], **record["metrics"], **record["diagnostics"],
                         external_evaluation_seconds=record["external_evaluation_seconds"]))
    write_csv(directory/("pilot_native_metrics.csv" if stage == "pilot"
                         else "benchmark_native_metrics.csv"), rows)
    write_json(directory/f"external_evaluation_completion_{stage}.json", dict(
        status="COMPLETED", evaluated_scenarios=total, evaluated_runs=len(rows),
        wall_seconds=perf_counter()-started, evaluator_source_sha256=source_hash,
        metrics_and_reference_changed=False, search_feedback=False,
    ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    parser.add_argument("--stage", choices=("pilot", "official"), default="official")
    parser.add_argument("--scenario")
    args = parser.parse_args()
    if args.scenario:
        evaluate_cell(args.directory, args.stage, args.scenario)
    else:
        evaluate(args.directory, args.stage)
