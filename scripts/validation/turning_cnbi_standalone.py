"""Official Phase8 standalone resolutions; no parent-grid artifact is an input.

Run with single numerical threads, after committing this protocol/source:
uv run python -m scripts.validation.turning_cnbi_standalone
"""

import argparse
import json
import os
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import numpy as np

from cnbi_v2.data import sha256_file
from cnbi_v2.nbi import (
    LocalNBIProblem,
    NBIOptions,
    canonical_decision_points,
    local_nbi_geometry,
    nondominated_mask,
    solve_nbi_lattice,
)
from cnbi_v2.optimization import evaluate_responses
from cnbi_v2.simplex import simplex_lattice

from . import turning_local_nbi as frozen
from .turning_benchmark_timing import hardware_and_isolation
from .turning_reference import ROOT, write_csv, write_json

POLICY = ROOT / "docs/policies/cnbi_standalone_correction.json"
OUTPUT = ROOT / "results/phase_08_final_benchmark/turning_standalone_correction_20261025"


def table(path, rows):
    keys = list(rows[0])
    write_csv(path, keys, [[r[k] for k in keys] for r in rows])


def execute(h, policy):
    """Same Phase6 solver, geometry, lattice order and starts, resolved at this H."""
    started = perf_counter()
    models, anchors, payoff, u, amps, signs, opt, catalog = frozen.verified_inputs()
    options = NBIOptions(**policy["solver_options"])
    points, responses, records, trial_records, subsets, compositions = [], [], [], [], [], []
    solver_seconds = 0.0
    for subset_index, (name, indices) in enumerate(catalog):
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
        solver_seconds += perf_counter() - tick
        ranks = {index: rank for rank, index in enumerate(result.processing_order)}
        for j, solution in enumerate(result.solutions):
            row_id = len(points)
            last = solution.trials[-1]
            point = solution.point if solution.accepted else np.full(3, np.nan)
            points.append(point)
            responses.append(
                evaluate_responses(models, point) if solution.accepted else np.full(8, np.nan)
            )
            subsets.append(subset_index)
            compositions.append(np.pad(lattice.compositions[j], (0, 3 - len(indices))))
            records.append(
                dict(
                    row_id=row_id,
                    subset=name,
                    subset_index=subset_index,
                    H=h,
                    lattice_index=j,
                    processing_rank=ranks[j],
                    composition=json.dumps(lattice.compositions[j].tolist()),
                    beta=json.dumps(lattice.weights[j].tolist()),
                    initial_start_kind=solution.trials[0].start.kind,
                    initial_start_x=json.dumps(solution.trials[0].start.point.tolist()),
                    initial_start_t=solution.trials[0].start.t,
                    used_start_kind=last.start.kind,
                    used_start_x=json.dumps(last.start.point.tolist()),
                    used_start_t=last.start.t,
                    solver_status=last.status,
                    solver_success=last.solver_success,
                    iterations=last.iterations,
                    t=last.t,
                    x1=float(point[0]),
                    x2=float(point[1]),
                    x3=float(point[2]),
                    eq_norm=last.eq_norm,
                    sphere_margin=last.sphere_margin,
                    solve_seconds=float(result.elapsed_seconds[j]),
                    accepted=solution.accepted,
                    trials=len(solution.trials),
                )
            )
            for attempt, trial in enumerate(solution.trials):
                trial_records.append(
                    dict(
                        row_id=row_id,
                        attempt=attempt,
                        start_kind=trial.start.kind,
                        start_x=json.dumps(trial.start.point.tolist()),
                        start_t=trial.start.t,
                        point=json.dumps(trial.point.tolist()),
                        t=trial.t,
                        status=trial.status,
                        message=trial.message,
                        iterations=trial.iterations,
                        accepted=trial.accepted,
                        eq_norm=trial.eq_norm,
                        sphere_margin=trial.sphere_margin,
                    )
                )
    x, f = np.array(points), np.array(responses)
    z = (f * signs - u) / amps
    accepted = np.array([r["accepted"] for r in records])
    accepted_ids = np.flatnonzero(accepted)
    reps, _ = canonical_decision_points(x[accepted], tolerance=policy["x_tolerance"])
    unique_ids = accepted_ids[reps]
    nd = nondominated_mask(z[unique_ids], equality_tolerance=policy["z_tolerance"])
    nd_ids = unique_ids[nd]
    elapsed = perf_counter() - started
    arrays = dict(
        x=x,
        natural_f=f,
        z=z,
        accepted=accepted,
        unique_ids=unique_ids,
        nd_ids=nd_ids,
        subsets=np.array(subsets),
        compositions=np.array(compositions),
        t=np.array([r["t"] for r in records]),
    )
    stats = dict(
        H=h,
        subproblems=len(x),
        accepted=int(accepted.sum()),
        failures=int((~accepted).sum()),
        unique=len(unique_ids),
        ND=len(nd_ids),
        T_solver=solver_seconds,
        T_total=elapsed,
        max_eq_norm=max(r["eq_norm"] for r in records),
        min_sphere_margin=min(r["sphere_margin"] for r in records),
    )
    return arrays, stats, records, trial_records


def campaign(output):
    if output.exists():
        raise ValueError("standalone archive already exists; never overwrite scientific runs")
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    if dirty.strip():
        raise ValueError("commit protocol and source before the controlled campaign")
    if any(
        os.environ.get(k) != "1"
        for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
    ):
        raise ValueError("launch with one numerical thread")
    policy = json.loads(POLICY.read_text())
    if asdict(NBIOptions(**policy["solver_options"])) != asdict(NBIOptions()):
        raise ValueError("Phase6 options changed")
    hardware = hardware_and_isolation()
    paths = [
        *frozen.INPUT_HASHES,
        POLICY,
        Path(__file__),
        ROOT / "uv.lock",
        *sorted((ROOT / "src/cnbi_v2/nbi").glob("*.py")),
        *sorted((ROOT / "src/cnbi_v2/simplex").glob("*.py")),
    ]
    launch = dict(
        executed_at_utc=datetime.now(UTC).isoformat(),
        git_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        working_tree_dirty_at_launch=False,
        hardware=hardware,
        input_sha256={p.relative_to(ROOT).as_posix(): sha256_file(p) for p in paths},
        policy=policy,
        methods_sequential=True,
        EA_executions=0,
        VRF_executions=0,
        independence="Phase6 and Phase7 result directories temporarily unavailable for all solves",
    )
    output.mkdir(parents=True)
    write_json(output / "launch.json", launch)
    # Actual filesystem isolation, restored even on failure. Explicit roots are
    # checked before renaming; no deletion and no data are reconstructed.
    hidden = []
    timings, repeats = [], []
    reference = None
    try:
        for name in ("phase_06_local_nbi", "phase_07_reference_front"):
            original = (ROOT / "results" / name).resolve()
            target = original.with_name(name + ".unavailable_for_standalone")
            if original.parent != (ROOT / "results").resolve() or target.exists():
                raise ValueError("unsafe or occupied isolation path")
            original.rename(target)
            hidden.append((original, target))
        # One unreported H2 warm-up; H5 repetitions are runtime noise only.
        execute(2, policy)
        for h in policy["H_values"]:
            for repetition in range(1, policy["repetitions"][str(h)] + 1):
                arrays, stats, records, trials = execute(h, policy)
                stats["repetition"] = repetition
                timings.append(stats)
                stem = output / f"H{h}_rep{repetition}"
                np.savez_compressed(stem.with_suffix(".npz"), **arrays)
                table(stem.with_name(stem.name + "_records.csv"), records)
                table(stem.with_name(stem.name + "_trials.csv"), trials)
                if h == 5:
                    if reference is None:
                        reference = arrays
                    deltas = {
                        k: float(np.max(np.abs(arrays[k] - reference[k]))) for k in ("x", "z", "t")
                    }
                    same = all(np.array_equal(arrays[k], reference[k]) for k in arrays)
                    if (
                        not np.array_equal(arrays["accepted"], reference["accepted"])
                        or not np.array_equal(arrays["nd_ids"], reference["nd_ids"])
                        or max(deltas.values()) > policy["repeat_atol"]
                    ):
                        raise ValueError("H5 scientific results differ across timing repetitions")
                    repeats.append(dict(repetition=repetition, bitwise_same=same, **deltas))
                print(json.dumps(stats), flush=True)
    finally:
        for original, target in reversed(hidden):
            target.rename(original)
    table(output / "timing_cnbi.csv", timings)
    table(output / "h5_repeat_equivalence.csv", repeats)
    write_json(
        output / "completion.json",
        dict(
            completed_at_utc=datetime.now(UTC).isoformat(),
            measured_runs=len(timings),
            H5_repetitions=5,
            H5_same_scientific_baseline=True,
            parent_artifacts_unavailable_during_every_solve=True,
            parent_artifacts_restored=all(a.exists() and not b.exists() for a, b in hidden),
            timing_interval=(
                "input verification through mesh/NBI/8-response/dedup/ND; "
                "excludes artifact serialization; includes start/trial observation"
            ),
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    campaign(parser.parse_args().output)
