"""Checkpointed Phase10D execution; each search has its own oracle-free process."""

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np

from cnbi_v2.synthetic.benchmark.archive import (
    begin_attempt,
    file_hash,
    read_json,
    recover_attempt,
    save_output,
    verify_payload,
    write_json,
)
from cnbi_v2.synthetic.benchmark.configuration import load_ea_configuration
from cnbi_v2.synthetic.benchmark.contracts import METHODS, array_hash
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/"results/phase_10_synthetic_benchmark/benchmark_20261029/campaign_v1"
RSM = ROOT/"results/phase_10_synthetic_rsm/rsm_20261029"


def run_id(task: dict[str, Any]) -> str:
    return f"{task['stage']}__{task['instance_id']}__{task['method'].replace('/', '_')}"


def verify_protocol(directory: Path) -> dict[str, Any]:
    manifest = read_json(directory/"generation_manifest.json")
    for name, digest in manifest["scientific_source"].items():
        if file_hash(ROOT/name) != digest:
            raise ValueError("scientific code changed since protocol freeze: "+name)
    for name, digest in manifest["configuration"].items():
        if file_hash(directory/name) != digest:
            raise ValueError("configuration changed since freeze: "+name)
    frozen = read_json(directory/"frozen_inputs_manifest.json")
    for name, digest in frozen["files"].items():
        if file_hash(ROOT/name) != digest:
            raise ValueError("previous phase file changed: "+name)
    return manifest


def environment() -> dict[str, Any]:
    import contextlib
    import importlib.metadata
    import io

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        np.show_config()
    return dict(python=sys.version, platform=platform.platform(), processor=platform.processor(),
                packages={name: importlib.metadata.version(name)
                          for name in ("numpy", "scipy", "pymoo")},
                thread_environment={name: os.environ.get(name) for name in (
                    "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
                workers=1, numpy_configuration=output.getvalue())


def peak_memory_bytes() -> int:
    if sys.platform != "win32":
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    import ctypes
    from ctypes import wintypes

    class Memory(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)]+[
            (name, ctypes.c_size_t) for name in (
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
                "PagefileUsage", "PeakPagefileUsage")]

    memory = Memory()
    memory.cb = ctypes.sizeof(memory)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    query = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
    query.argtypes = [wintypes.HANDLE, ctypes.POINTER(Memory), wintypes.DWORD]
    query.restype = wintypes.BOOL
    if not query(kernel.GetCurrentProcess(), ctypes.byref(memory), memory.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(memory.PeakWorkingSetSize)


def worker(directory: Path, task: dict[str, Any]) -> None:
    # No import of Phase10A truth / Phase10C evaluation in the search worker.
    from cnbi_v2.synthetic.benchmark.runner import run_method

    manifest = verify_protocol(directory)
    name = run_id(task)
    checkpoint_path = directory/f"campaign_checkpoints/{name}.json"
    checkpoint = begin_attempt(checkpoint_path, task, manifest["protocol_hash"])
    if checkpoint is None:
        old = read_json(checkpoint_path)
        if old["state"] == "COMPLETED":
            verify_payload(directory, old["payload_checksums"])
        return
    payload_name = name if checkpoint["attempt"] == 1 else f"{name}__attempt{checkpoint['attempt']}"
    started = time.perf_counter()
    try:
        inputs = load_search_inputs(RSM)
        item = inputs[task["instance_id"]]
        cfg = (load_ea_configuration(directory/"v1_ea_calibration.json", task["method"],
                                      item.nx, item.m) if task["method"] in METHODS[2:] else None)
        output = run_method(item, task["method"], int(task["seed"]), cfg)
        metadata = dict(task=task, protocol_hash=manifest["protocol_hash"],
                        code_commit=manifest["code_commit"], environment=environment(),
                        coefficients_sha256=array_hash(item.model.coefficients),
                        peak_process_memory_bytes=peak_memory_bytes(),
                        input_load_plus_search_seconds=time.perf_counter()-started)
        hashes = save_output(directory, payload_name, output, metadata)
        state = "COMPLETED" if output.status == "COMPLETED" else "FAILED"
        checkpoint.update(state=state, algorithm_status=output.status, payload_checksums=hashes,
                          payload_run_id=payload_name,
                          output_count=len(output.decisions), timings=output.timings,
                          counters=output.counters, nx=item.nx, m=item.m,
                          peak_process_memory_bytes=metadata["peak_process_memory_bytes"])
    except Exception as error:
        checkpoint.update(state="FAILED", error=f"{type(error).__name__}: {error}",
                          traceback=traceback.format_exc(), elapsed=time.perf_counter()-started)
    checkpoint["history"].append(dict(attempt=checkpoint["attempt"], state=checkpoint["state"]))
    write_json(checkpoint_path, checkpoint)
    print(json.dumps(dict(run_id=name, state=checkpoint["state"],
                          seconds=time.perf_counter()-started)), flush=True)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def report_runs(directory: Path, stage: str) -> list[dict[str, Any]]:
    tasks = [task for task in read_json(directory/"seed_manifest.json")["tasks"]
             if task["stage"] == stage]
    rows = []
    for task in tasks:
        path = directory/f"campaign_checkpoints/{run_id(task)}.json"
        record = read_json(path) if path.exists() else dict(state="PENDING")
        rows.append(dict(**task, state=record["state"], nx=record.get("nx"), m=record.get("m"),
                         output_count=record.get("output_count"),
                         total_seconds=record.get("timings", {}).get("total"),
                         peak_memory_bytes=record.get("peak_process_memory_bytes"),
                         error=record.get("error"),
                         algorithm_status=record.get("algorithm_status")))
    write_csv(directory/("pilot_runs.csv" if stage == "pilot" else "campaign_runs.csv"), rows)
    return rows


def execute(directory: Path, stage: str) -> None:
    verify_protocol(directory)
    if stage == "official":
        gate = read_json(directory/"pilot_verification.json")
        if gate["status"] != "PASS":
            raise ValueError("official campaign prohibited: pilot gate not passed")
    tasks = [task for task in read_json(directory/"seed_manifest.json")["tasks"]
             if task["stage"] == stage]
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    for task in tasks:
        log_path = directory/f"logs/{run_id(task)}.log"
        log_path.parent.mkdir(exist_ok=True)
        with log_path.open("ab") as log:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "worker",
                                     "--directory", str(directory), "--task", json.dumps(task)],
                                    env=env, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
        rows = report_runs(directory, stage)
        print(json.dumps(dict(run_id=run_id(task), exit_code=result.returncode,
                              completed=sum(row["state"] == "COMPLETED" for row in rows),
                              failed=sum(row["state"] == "FAILED" for row in rows),
                              planned=len(tasks))), flush=True)
        # Retain all pilot outcomes; structural failures block the official gate.
        if result.returncode:
            raise RuntimeError("worker process failed; inspect retained log and checkpoint")
    if stage == "pilot":
        passed = all(row["state"] == "COMPLETED" for row in rows) and len(rows) == 12
        write_json(directory/"pilot_verification.json", dict(
            status="NUMERICAL_RUNS_COMPLETE_AUDIT_PENDING" if passed else "FAIL",
            planned=12, completed=sum(row["state"] == "COMPLETED" for row in rows),
            failed=sum(row["state"] == "FAILED" for row in rows),
            official_campaign_authorized=False,
            remaining=["migration_equivalence", "reproducibility", "external_evaluation",
                       "checkpoint_integrity", "runtime_projection"],
        ))
    else:
        complete = all(row["state"] == "COMPLETED" for row in rows) and len(rows) == 540
        manifest = read_json(directory/"campaign_manifest.json")
        manifest.update(status="COMPLETED" if complete else "INCOMPLETE",
                        executed_runs=sum(row["state"] != "PENDING" for row in rows), tasks=rows)
        write_json(directory/"campaign_manifest.json", manifest)


def evaluate(directory: Path, stage: str) -> None:
    # Runs only in the parent evaluation process after search has terminated.
    from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context

    verify_protocol(directory)
    contexts = {}
    rows = []
    for task in read_json(directory/"seed_manifest.json")["tasks"]:
        if task["stage"] != stage:
            continue
        name = run_id(task)
        path = directory/f"campaign_checkpoints/{name}.json"
        if not path.exists():
            continue
        checkpoint = read_json(path)
        if "payload_checksums" not in checkpoint:
            rows.append(dict(**task, state=checkpoint["state"], status="UNDEFINED_FAILED_RUN"))
            continue
        verify_payload(directory, checkpoint["payload_checksums"])
        payload_name = checkpoint.get("payload_run_id", name)
        sid = task["scenario_id"]
        if sid not in contexts:
            contexts[sid] = load_evaluation_context(
                ROOT/"results/phase_10_synthetic_pareto/analytical_20261029", sid,
                ROOT/"results/phase_10_synthetic_generation/structural_20261029")
        with np.load(directory/f"raw_decisions/{payload_name}.npz", allow_pickle=False) as arrays:
            decisions = arrays["decisions"]
        started = time.perf_counter()
        evaluated = contexts[sid].evaluate(
            sid, int(task["replica_id"]), task["method"], decisions,
            dict(protocol_hash=checkpoint["protocol_hash"], run_id=name,
                 algorithm_status=checkpoint.get("algorithm_status")),
            seconds=checkpoint.get("timings", {}).get("total"),
            nfe=checkpoint.get("counters", {}).get("original_rsm_point_evaluations"),
        )
        external_seconds = time.perf_counter()-started
        target = directory/f"external_evaluation/{name}.npz"
        target.parent.mkdir(exist_ok=True)
        np.savez_compressed(target, true_responses=evaluated.true_responses,
                            normalized_responses=evaluated.normalized_responses,
                            feasible_mask=evaluated.feasible_mask,
                            unique_indices=evaluated.unique_indices,
                            nondominated_indices=evaluated.nondominated_indices)
        write_json(target.with_suffix(".json"), dict(
            metrics=evaluated.metrics, diagnostics=evaluated.diagnostics,
            external_evaluation_seconds=external_seconds,
        ))
        rows.append(dict(**task, state=checkpoint["state"], **evaluated.metrics,
                         **evaluated.diagnostics, external_evaluation_seconds=external_seconds))
    write_csv(directory/("pilot_native_metrics.csv" if stage == "pilot"
                         else "benchmark_native_metrics.csv"), rows)
    print(json.dumps(dict(external_evaluations=len(rows), stage=stage)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("pilot", "official", "worker", "evaluate", "verify",
                                          "recover"))
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    parser.add_argument("--stage", choices=("pilot", "official"), default="pilot")
    parser.add_argument("--task")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--reason", default="")
    args = parser.parse_args()
    if args.action == "worker":
        worker(args.directory, json.loads(args.task))
    elif args.action in {"pilot", "official"}:
        execute(args.directory, args.action)
    elif args.action == "evaluate":
        evaluate(args.directory, args.stage)
    elif args.action == "recover":
        verify_protocol(args.directory)
        if args.checkpoint is None:
            raise ValueError("--checkpoint is required for operational recovery")
        target = args.checkpoint.resolve()
        if not target.is_relative_to((args.directory/"campaign_checkpoints").resolve()):
            raise ValueError("recovery target must be inside this campaign's checkpoints")
        recover_attempt(target, args.reason)
    else:
        print(json.dumps(dict(status="VERIFIED", **verify_protocol(args.directory))))
