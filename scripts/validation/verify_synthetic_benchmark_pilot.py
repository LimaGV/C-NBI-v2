"""Gate12 pilot runs with full-budget replay, external certificates and projection."""

import argparse
import json
import os
import subprocess
import sys
from math import comb
from pathlib import Path

import numpy as np
from execute_synthetic_benchmark import (
    OUTPUT,
    ROOT,
    RSM,
    report_runs,
    run_id,
    verify_protocol,
    write_csv,
)

from cnbi_v2.synthetic.benchmark.archive import read_json, verify_payload, write_json
from cnbi_v2.synthetic.benchmark.configuration import ea_ceiling, load_ea_configuration
from cnbi_v2.synthetic.benchmark.contracts import METHODS, PILOT_SCENARIOS, array_hash
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs


def replay_worker(directory: Path, task: dict) -> None:
    from cnbi_v2.synthetic.benchmark.runner import run_method
    data = load_search_inputs(RSM)[task["instance_id"]]
    config = (load_ea_configuration(directory/"v1_ea_calibration.json", task["method"],
                                    data.nx, data.m) if task["method"] in METHODS[2:] else None)
    output = run_method(data, task["method"], int(task["seed"]), config)
    name = run_id(task)
    with np.load(directory/f"raw_decisions/{name}.npz", allow_pickle=False) as original:
        x_match = np.array_equal(original["decisions"], output.decisions)
    with np.load(directory/f"raw_rsm_responses/{name}.npz", allow_pickle=False) as original:
        y_match = np.array_equal(original["rsm_responses"], output.rsm_responses)
    previous = read_json(directory/f"algorithm_diagnostics/{name}.json")
    counters_match = previous["counters"] == output.counters
    passed = (x_match and y_match and counters_match
              and output.status == previous["algorithm_status"])
    write_json(directory/f"pilot_replay/{name}.json", dict(
        status="PASS" if passed else "FAIL", decisions_bitwise=x_match,
        rsm_responses_bitwise=y_match, counters_equal=counters_match,
        output_sha256=array_hash(output.decisions), same_seed=str(task["seed"]),
    ))


def verify(directory: Path, replay: bool) -> None:
    verify_protocol(directory)
    rows = report_runs(directory, "pilot")
    diagnostics, projections, problems = [], [], []
    migration = read_json(directory/"migration/verification.json")
    if migration["status"] != "PASS":
        problems.append("MIGRATION_GATE_FAILED")
    tasks = [task for task in read_json(directory/"seed_manifest.json")["tasks"]
             if task["stage"] == "pilot"]
    if len(tasks) != 12 or any(row["state"] != "COMPLETED" for row in rows):
        problems.append("PILOT_NOT_TWELVE_COMPLETED_RUNS")
    inputs = load_search_inputs(RSM)
    for task in tasks:
        name = run_id(task)
        cp = directory/f"campaign_checkpoints/{name}.json"
        if not cp.exists():
            continue
        checkpoint = read_json(cp)
        if "payload_checksums" not in checkpoint:
            continue
        verify_payload(directory, checkpoint["payload_checksums"])
        meta = read_json(directory/f"algorithm_diagnostics/{name}.json")
        data = inputs[task["instance_id"]]
        with np.load(directory/f"raw_decisions/{name}.npz", allow_pickle=False) as arrays:
            x = arrays["decisions"]
        violation = float(np.max(np.maximum(np.linalg.norm(x, axis=1)-data.alpha, 0), initial=0))
        if violation > 1e-8 or meta["coefficients_sha256"] != array_hash(data.model.coefficients):
            problems.append(name+":FEASIBILITY_OR_MODEL_MISMATCH")
        if not (directory/f"external_evaluation/{name}.json").exists():
            problems.append(name+":EXTERNAL_EVALUATION_PENDING")
        specific = meta["diagnostics"]
        diagnostics.append(dict(
            run_id=name, method=task["method"], nx=data.nx, m=data.m,
            maximum_raw_sphere_violation=violation,
            preparation_seconds=meta["timings"].get("preparation"),
            solver_seconds=meta["timings"].get("solver"), total_seconds=meta["timings"]["total"],
            selected_subsets=specific.get("selected_subsets"),
            candidate_subsets=specific.get("candidate_subsets"),
            mc_anchor_seconds=specific.get("mc_anchor_seconds"),
            nbi_subproblems=meta["counters"].get("nbi_subproblems"),
            k_vrf=specific.get("n_factors"), retained_variance=specific.get("retained_variance"),
            nfe=meta["counters"].get("original_rsm_point_evaluations"),
            peak_process_memory_bytes=meta["peak_process_memory_bytes"],
        ))
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    for task in tasks:
        if task["scenario_id"] != PILOT_SCENARIOS[0]:
            continue
        name = run_id(task)
        path = directory/f"pilot_replay/{name}.json"
        if replay and not path.exists():
            log = directory/f"logs/replay__{name}.log"
            with log.open("wb") as stream:
                result = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                         "--directory", str(directory), "--replay-worker",
                                         json.dumps(task)], cwd=ROOT, env=env,
                                        stdout=stream, stderr=subprocess.STDOUT)
            if result.returncode:
                problems.append(name+":REPLAY_PROCESS_FAILURE")
        if not path.exists() or read_json(path)["status"] != "PASS":
            problems.append(name+":REPRODUCIBILITY_PENDING_OR_FAILED")
    for data in inputs.values():
        if data.replica_id != 1:
            continue
        for method in METHODS:
            pilot = next((d for d in diagnostics if d["nx"] == data.nx and d["method"] == method),
                         None)
            if pilot is None:
                continue
            if method in METHODS[2:]:
                scale = ea_ceiling(data.m)/ea_ceiling(int(pilot["m"]))
                estimate = float(pilot["total_seconds"])*scale
                upper = estimate*2
                basis = "dimension_specific_pilot_time_per_NFE; factor2_scheduling_range"
            elif method == "C-NBI":
                candidates = sum(comb(data.m, k) for k in range(2, data.nx+2))
                scale = candidates/max(1, int(pilot["candidate_subsets"]))
                prep = float(pilot["preparation_seconds"])*max(scale, data.m/int(pilot["m"]))
                estimate = prep+float(pilot["solver_seconds"])*scale
                possible = sum(comb(data.m, k)*comb((5 if k <= 4 else 2)+k-1, k-1)
                               for k in range(2, data.nx+2))
                upper = prep+float(pilot["solver_seconds"])*possible/max(
                    1, int(pilot["nbi_subproblems"]))
                basis = ("nx_specific_preparation_and_subset_counts; "
                         "upper_all_eligible_lattice_points")
            else:
                estimate = float(pilot["total_seconds"])*data.m/int(pilot["m"])
                upper = estimate*max(2., comb(5+data.nx, data.nx)/max(
                    1, int(pilot["nbi_subproblems"])))
                basis = "nx_specific_factor_analysis_and_lattice_upper; k_unknown_until_execution"
            projections.append(dict(scenario_id=data.scenario_id, nx=data.nx, m=data.m,
                                    method=method, replicas=5, projected_total_seconds=5*estimate,
                                    conservative_scheduling_seconds=5*upper,
                                    basis=basis, rho_extrapolation="no_quality_based_retuning"))
    write_csv(directory/"pilot_diagnostics.csv", diagnostics)
    write_csv(directory/"pilot_runtime_projection.csv", projections)
    write_json(directory/"pilot_verification.json", dict(
        status="PASS" if not problems else "FAIL", planned=12,
        completed=sum(row["state"] == "COMPLETED" for row in rows), problems=problems,
        migration_status=migration["status"], replay_methods=4,
        official_campaign_authorized=not problems, workers=1, cpu_threads=1,
        projection_total_seconds=sum(row["projected_total_seconds"] for row in projections),
        conservative_scheduling_seconds=sum(row["conservative_scheduling_seconds"]
                                             for row in projections),
        projection_is_resource_planning_not_quality_tuning=True,
    ))
    print((directory/"pilot_verification.json").read_text())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--replay-worker")
    args = parser.parse_args()
    if args.replay_worker:
        replay_worker(args.directory, json.loads(args.replay_worker))
    else:
        verify(args.directory, args.replay)
