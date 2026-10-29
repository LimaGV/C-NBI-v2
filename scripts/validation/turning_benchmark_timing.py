"""Isolated sequential timing of frozen EAs; CNBI pending, VRF never executed."""

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter, process_time

import numpy as np

from cnbi_v2.benchmark.observation import PopulationObserver
from cnbi_v2.data import sha256_file
from cnbi_v2.reference import EAConfig, run_evolutionary

from . import turning_benchmark_inputs as data
from . import turning_reference_campaign as phase7
from .turning_reference import ROOT, write_json


def configuration(family):
    p = json.loads(phase7.PROTOCOL.read_text())
    s = p[family]
    return EAConfig(
        family,
        n_partitions=p["n_partitions"],
        generations=p["generations"],
        sbx_probability=s["sbx_probability"],
        sbx_eta=s["sbx_eta"],
        pm_eta=s["pm_eta"],
        n_neighbors=p["MOEAD"]["n_neighbors"],
        prob_neighbor_mating=p["MOEAD"]["prob_neighbor_mating"],
    )


def hardware_and_isolation():
    info = dict(
        platform=platform.platform(),
        python=platform.python_version(),
        logical_processors=os.cpu_count(),
        process_id=os.getpid(),
    )
    if os.name != "nt":
        raise RuntimeError("this dedicated campaign is defined for the audited Windows host")
    command = r"""
    [Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
    $before=@{}; Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
        $before[$_.Id]=$_.CPU
    }
    Start-Sleep -Milliseconds 1500
    $active=@(Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.Id -ne PARENT_PID -and $before.ContainsKey($_.Id) -and ($_.CPU-$before[$_.Id]) -gt .10
    } | ForEach-Object { @{pid=$_.Id;cpu_delta_seconds=$_.CPU-$before[$_.Id]} })
    $cpus=@(Get-CimInstance Win32_Processor |
        Select-Object Name,NumberOfCores,NumberOfLogicalProcessors)
    @{cpus=$cpus;memory_bytes=(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory;
      external_active_python=$active;observation_seconds=1.5} | ConvertTo-Json -Depth 5 -Compress
    """.replace("PARENT_PID", str(os.getpid()))
    raw = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", command], encoding="utf-8"
    ).strip()
    info.update(json.loads(raw))
    if info["external_active_python"]:
        raise RuntimeError("other active Python jobs detected; timing isolation not established")
    return info


def campaign(output):
    if not (output / "phase8a_completion.json").exists():
        raise ValueError("complete and inspect Phase8A before the timing block")
    if (output / "timing_completion.json").exists():
        raise ValueError("completed timing campaign is immutable")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise ValueError("controlled timing must launch from a clean committed checkout")
    policy = json.loads(data.POLICY.read_text())
    timing_dir = output / "controlled_timing"
    timing_dir.mkdir(exist_ok=True)
    inputs = [
        Path(__file__),
        Path(data.__file__),
        data.POLICY,
        phase7.PROTOCOL,
        ROOT / "uv.lock",
        ROOT / "src/cnbi_v2/reference/evolutionary.py",
        ROOT / "src/cnbi_v2/reference/problem.py",
        ROOT / "src/cnbi_v2/benchmark/observation.py",
    ]
    hashes = phase7.hashes(inputs)
    thread_vars = (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    )
    if any(os.environ.get(v) != "1" for v in thread_vars):
        raise ValueError("set all documented numerical thread variables to1 before Python starts")
    launch = dict(
        git_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        working_tree_dirty_at_launch=False,
        started_utc=datetime.now(UTC).isoformat(),
        hardware=hardware_and_isolation(),
        code_config_sha256=hashes,
        versions={n: importlib.metadata.version(n) for n in ("numpy", "scipy", "pymoo")},
        thread_environment={v: os.environ[v] for v in thread_vars},
        no_parallel_methods=True,
        source_reference_runs_added=0,
        CNBI_executions=0,
        VRF_executions=0,
        user_scope="preserve408; CNBI cost pending; VRF execution forbidden",
    )
    try:
        from threadpoolctl import threadpool_info

        launch["loaded_threadpools"] = threadpool_info()
    except ImportError:
        launch["loaded_threadpools"] = "unavailable; environment controls recorded"
    write_json(output / "timing_launch.json", launch)
    data.table(
        output / "timing_cnbi.csv",
        [
            dict(
                method="CNBI",
                H=h,
                repetitions_executed=0,
                T_total=None,
                status="PENDING_H5_DIRECT_EQUIVALENCE_FAILED",
            )
            for h in (2, 4, 5, 10, 20)
        ],
    )
    data.table(
        output / "timing_vrf.csv",
        [
            dict(
                method="VRF",
                retained_points=66,
                repetitions_executed=0,
                T_total=None,
                status="NOT_MEASURED_USER_FORBIDS_EXECUTION",
            )
        ],
    )
    summary = []
    started = perf_counter()
    for family in ("NSGA3", "MOEAD"):
        config = configuration(family)
        problem, _, _ = phase7.load_problem()
        print(f"{family} warm-up seed1000, excluded from reported timing", flush=True)
        run_evolutionary(problem, config, 1000)
        for seed in policy["timing"]["seeds"]:
            if phase7.hashes(inputs) != hashes:
                raise RuntimeError("timing code/config changed during the campaign")
            start, cpu = perf_counter(), process_time()
            problem, xtol, tau = phase7.load_problem()
            observer = PopulationObserver(
                tuple(policy["timing"]["generations"]), xtol, tau, start, cpu
            )
            result = run_evolutionary(problem, config, seed, callback=observer)
            total, cpu_seconds = perf_counter() - start, process_time() - cpu
            if [r["generation"] for r in observer.records] != policy["timing"]["generations"]:
                raise RuntimeError("a requested checkpoint was not observed")
            # Validation/serialization below are outside the processing-time interval.
            archive = phase7.OUTPUT / "runs" / f"{family.lower()}_seed{seed}.npz"
            with np.load(archive, allow_pickle=False) as stored:
                exact = bool(np.array_equal(result["x"], stored["final_population_x"]))
                max_error = float(np.max(np.abs(result["x"] - stored["final_population_x"])))
                if not np.allclose(result["x"], stored["final_population_x"], atol=1e-11, rtol=0):
                    raise RuntimeError(
                        "controlled final population differs from frozen Phase7 seed"
                    )
            arrays = {
                "final_population_x": result["x"],
                "final_population_f": result["natural_f"],
                "final_population_z": result["optimizer_f"],
            }
            checkpoint_metadata = []
            for row in observer.records:
                generation = row["generation"]
                for key in ("x", "natural_f", "z", "population_indices"):
                    arrays[f"g{generation}_{key}"] = row[key]
                checkpoint_metadata.append(
                    {
                        k: v
                        for k, v in row.items()
                        if k not in {"x", "natural_f", "z", "population_indices"}
                    }
                )
            target = timing_dir / f"{family.lower()}_seed{seed}"
            np.savez_compressed(target.with_suffix(".npz"), **arrays)
            record = dict(
                method=family,
                seed=seed,
                NFE=result["nfe"],
                T_total=total,
                optimizer_seconds_excluding_observer=max(
                    0.0, result["runtime"] - observer.observation_seconds
                ),
                observer_seconds=observer.observation_seconds,
                cpu_seconds=cpu_seconds,
                N_returned=result["population"],
                N_unique_ND=observer.records[-1]["N_unique_ND"],
                phase7_final_exact=exact,
                phase7_final_max_x_error=max_error,
                config_hash=phase7.fingerprint(asdict(config)),
                git_commit=launch["git_commit"],
                archive_sha256=sha256_file(target.with_suffix(".npz")),
            )
            write_json(
                target.with_suffix(".json"),
                dict(**record, checkpoints=checkpoint_metadata, configuration=asdict(config)),
            )
            summary.append(record)
            print(
                f"{family} seed{seed} T_total={total:.6f}s NFE={result['nfe']} "
                f"frozen_final_exact={exact}",
                flush=True,
            )
        data.table(
            output / f"timing_{family.lower()}.csv", [r for r in summary if r["method"] == family]
        )
    write_json(
        output / "timing_completion.json",
        dict(
            status="CONTROLLED_EA_TIMING_COMPLETE",
            runs=len(summary),
            warmups=2,
            measured_optimizer_NFE=sum(r["NFE"] for r in summary),
            wall_seconds=perf_counter() - started,
            code_config_unchanged=phase7.hashes(inputs) == hashes,
            git_commit=launch["git_commit"],
            CNBI_executions=0,
            VRF_executions=0,
            CNBI_cost="PENDING_EQUIVALENCE",
            VRF_cost="USER_FORBIDS_EXECUTION",
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=data.OUTPUT)
    args = parser.parse_args()
    campaign(args.output)
