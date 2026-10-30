"""Hardware scheduler only: independent frozen searches on separate physical cores.

No algorithm, seed, scientific parameter or frozen worker code is changed.
This scheduler has its own source hash and execution plan; one worker and one
numeric thread per run, with up to six simultaneous single-core runs.
"""

import argparse
import ctypes
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Empty, Queue
from threading import Event

from execute_synthetic_benchmark import OUTPUT, ROOT, report_runs, run_id, verify_protocol

from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, write_json
from cnbi_v2.synthetic.benchmark.contracts import METHODS

PIN_AND_RUN = (
    "import ctypes,os,runpy,sys;"
    "k=ctypes.WinDLL('kernel32',use_last_error=True);"
    "k.GetCurrentProcess.restype=ctypes.c_void_p;"
    "f=k.SetProcessAffinityMask;f.argtypes=[ctypes.c_void_p,ctypes.c_size_t];f.restype=ctypes.c_int;"
    "assert f(k.GetCurrentProcess(),int(os.environ['PHASE10D_CPU_MASK'])),ctypes.get_last_error();"
    "sys.argv=sys.argv[1:];sys.path.insert(0,os.path.dirname(sys.argv[0]));"
    "runpy.run_path(sys.argv[0],run_name='__main__')"
)


def physical_masks() -> list[int]:
    """Read Windows core topology; never assign sibling threads as separate cores."""
    if sys.platform != "win32":
        raise ValueError("this explicit hardware plan is for the audited Windows workstation")
    from ctypes import wintypes

    class ProcessorInfo(ctypes.Structure):
        _fields_ = [("mask", ctypes.c_size_t), ("relationship", ctypes.c_int),
                    ("union", ctypes.c_ulonglong*2)]

    query = ctypes.WinDLL("kernel32", use_last_error=True).GetLogicalProcessorInformation
    query.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
    query.restype = wintypes.BOOL
    length = wintypes.DWORD(0)
    query(None, ctypes.byref(length))
    buffer = ctypes.create_string_buffer(length.value)
    if not query(buffer, ctypes.byref(length)):
        raise ctypes.WinError(ctypes.get_last_error())
    size = ctypes.sizeof(ProcessorInfo)
    if length.value % size:
        raise ValueError("unsupported Windows processor information layout")
    result = []
    for offset in range(0, length.value, size):
        info = ProcessorInfo.from_buffer_copy(buffer.raw[offset:offset+size])
        if info.relationship == 0:
            mask = int(info.mask)
            result.append(mask & -mask)
    if not result or len(set(result)) != len(result):
        raise ValueError("physical CPU topology could not be certified")
    return sorted(result)


def execute(directory: Path, replay: bool, pilot: bool = False) -> None:
    manifest = verify_protocol(directory)
    if (not replay and not pilot
            and read_json(directory/"pilot_verification.json")["status"] != "PASS"):
        raise ValueError("official campaign blocked by pilot gate")
    masks = physical_masks()[:6]
    source_hash = file_hash(Path(__file__))
    plan = dict(
        scheduler_source=Path(__file__).relative_to(ROOT).as_posix(),
        scheduler_sha256=source_hash, algorithm_protocol_hash=manifest["protocol_hash"],
        max_concurrent_runs=len(masks), workers_per_run=1, BLAS_OpenMP_threads_per_run=1,
        physical_core_affinity_masks=masks, sibling_threads_used=False,
        semantics="independent_processes; no_change_to_frozen_algorithm_or_seed",
        timing="per_run_wall_time_under_archived_concurrency; not_isolated_idle_host_time",
        resource_decision="use_available_physical_cores; no_quality_or_parameter_tuning",
        method_order=list(METHODS), barrier_between_methods=True,
    )
    plan["plan_sha256"] = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()
    plan_path = directory/"execution_plan.json"
    if plan_path.exists() and read_json(plan_path) != plan:
        raise ValueError("refuse to mix execution hardware plans")
    write_json(plan_path, plan)
    tasks = [task for task in read_json(directory/"seed_manifest.json")["tasks"]
             if task["stage"] == ("pilot" if replay or pilot else "official")]
    if replay:
        tasks = [task for task in tasks if task["scenario_id"] == "nx2_delta1_rho025"]
    queue = Queue()
    abort = Event()

    def shard(index: int) -> int:
        completed = 0
        while True:
            if (directory/"STOP_REQUESTED.json").exists() or abort.is_set():
                break
            try:
                task = queue.get_nowait()
            except Empty:
                break
            name = run_id(task)
            if replay:
                command = [str(ROOT/"scripts/validation/verify_synthetic_benchmark_pilot.py"),
                           "--directory", str(directory), "--replay-worker", json.dumps(task)]
                receipt = directory/f"scheduler_receipts/replay__{name}.json"
            else:
                command = [str(ROOT/"scripts/validation/execute_synthetic_benchmark.py"),
                           "worker", "--directory", str(directory), "--task", json.dumps(task)]
                receipt = directory/f"scheduler_receipts/{name}.json"
                checkpoint = directory/f"campaign_checkpoints/{name}.json"
                if (checkpoint.exists()
                        and read_json(checkpoint)["state"] in {
                            "COMPLETED", "FAILED", "INCOMPLETE",
                        }):
                    from cnbi_v2.synthetic.benchmark.archive import verify_payload
                    retained = read_json(checkpoint)
                    if "payload_checksums" in retained:
                        verify_payload(directory, retained["payload_checksums"])
                    completed += 1
                    continue
            env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
                       MKL_NUM_THREADS="1", PHASE10D_CPU_MASK=str(masks[index]))
            log_path = directory/f"logs/{'replay__' if replay else ''}{name}.log"
            log_path.parent.mkdir(exist_ok=True)
            with log_path.open("ab") as stream:
                result = subprocess.run([sys.executable, "-c", PIN_AND_RUN, *command],
                                        cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
            write_json(receipt, dict(task=task, plan_sha256=plan["plan_sha256"],
                                     cpu_mask=masks[index], exit_code=result.returncode,
                                     shard=index, scientific_code_commit=manifest["code_commit"]))
            if result.returncode:
                abort.set()
                raise RuntimeError("worker failed; inspect preserved log: "+name)
            completed += 1
            if not replay:
                checkpoint = read_json(directory/f"campaign_checkpoints/{name}.json")
                print(json.dumps(dict(
                    run_id=name, state=checkpoint["state"], shard=index,
                    seconds=checkpoint.get("timings", {}).get("total"),
                )), flush=True)
        return completed

    total = 0
    barriers = []
    for method in METHODS:
        stage_tasks = [task for task in tasks if task["method"] == method]
        queue = Queue()
        for task in stage_tasks:
            queue.put(task)
        with ThreadPoolExecutor(max_workers=len(masks)) as pool:
            processed = sum(future.result() for future in as_completed(
                [pool.submit(shard, index) for index in range(len(masks))]))
        total += processed
        barrier = dict(method=method, planned=len(stage_tasks), processed=processed,
                       all_tasks_finished=processed == len(stage_tasks))
        barriers.append(barrier)
        write_json(directory/"method_execution_barriers.json", dict(
            order=list(METHODS), barriers=barriers,
            next_method_allowed=barrier["all_tasks_finished"],
        ))
        print(json.dumps(dict(method_barrier=barrier)), flush=True)
        if processed != len(stage_tasks):
            break
    if not replay and pilot:
        rows = report_runs(directory, "pilot")
        write_json(directory/"pilot_verification.json", dict(
            status="NUMERICAL_RUNS_COMPLETE_AUDIT_PENDING", planned=12,
            completed=sum(r["state"] == "COMPLETED" for r in rows),
            official_campaign_authorized=False,
        ))
    elif not replay:
        rows = report_runs(directory, "official")
        campaign = read_json(directory/"campaign_manifest.json")
        campaign.update(
            status="COMPLETED" if all(r["state"] == "COMPLETED" for r in rows) else "INCOMPLETE",
            executed_runs=sum(r["state"] != "PENDING" for r in rows), tasks=rows,
            execution_plan_sha256=plan["plan_sha256"],
        )
        write_json(directory/"campaign_manifest.json", campaign)
    print(json.dumps(dict(tasks_processed=total, replay=replay)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    parser.add_argument("--pilot-replay", action="store_true")
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    lock = args.directory/"scheduler.lock"
    with lock.open("x", encoding="utf-8") as stream:
        json.dump(dict(pid=os.getpid(), pilot=args.pilot, replay=args.pilot_replay), stream)
    try:
        execute(args.directory, args.pilot_replay, args.pilot)
    finally:
        lock.unlink()
