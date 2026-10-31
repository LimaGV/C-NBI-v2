"""Focused ablation: quality-blind subset sampling and unchanged local V2 NBI.

Only cached nominal payoffs enter these helpers. No true anchors, references,
metric, coefficient sampling or anchor optimizer is available to selection.
"""

from collections import Counter
from dataclasses import asdict
from time import perf_counter
from typing import Any

import numpy as np

from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.nbi.geometry import local_nbi_geometry
from cnbi_v2.nbi.solver import LocalNBIProblem, solve_nbi_lattice
from cnbi_v2.optimization import Direction
from cnbi_v2.optimization.quadratic import quadratic_responses_from_coefficients
from cnbi_v2.simplex import simplex_lattice
from cnbi_v2.synthetic.benchmark.configuration import lattice_resolution
from cnbi_v2.synthetic.benchmark.contracts import SearchInput, stream_seed
from cnbi_v2.synthetic.benchmark.instrumentation import KernelCounter


def select_scenarios(cost_ranking: list[dict[str, Any]]) -> tuple[str, ...]:
    """Cost-only rule: three cheapest, then cheapest new nx when required."""
    ordered = sorted(cost_ranking, key=lambda r: (r["total_seconds"], r["scenario_id"]))
    if len(ordered) < 4:
        raise ValueError("at least four scenarios required")
    first = ordered[:3]
    dimensions = {r["nx"] for r in first}
    fourth = (
        ordered[3]
        if len(dimensions) >= 2
        else next(r for r in ordered[3:] if r["nx"] not in dimensions)
    )
    return tuple(str(r["scenario_id"]) for r in [*first, fourth])


def random_subsets(
    universe: dict[str, tuple[int, ...]],
    targets: dict[int, int],
    scenario: str,
    replica: int,
    seed: int,
) -> tuple[list[str], dict[int, int]]:
    """Uniform samples without replacement, independently for each k/instance/seed."""
    chosen: list[str] = []
    deficits: dict[int, int] = {}
    for k, count in sorted(targets.items()):
        candidates = sorted(s for s, ids in universe.items() if len(ids) == k)
        if count < 0:
            raise ValueError("subset budget must be nonnegative")
        take = min(count, len(candidates))
        rng = np.random.default_rng(stream_seed(scenario, replica, "A2", f"{seed}/k{k}"))
        positions = rng.choice(len(candidates), take, replace=False)
        chosen.extend(candidates[int(j)] for j in positions)
        if take < count:
            deficits[k] = count - take
    return sorted(chosen, key=lambda s: (len(universe[s]), universe[s])), deficits


def subset_counts(names: list[str], universe: dict[str, tuple[int, ...]]) -> dict[int, int]:
    return dict(Counter(len(universe[s]) for s in names))


def solve_subset(
    data: SearchInput,
    payoff: FloatArray,
    anchors: FloatArray,
    indices: tuple[int, ...],
) -> dict[str, Any]:
    """No new model, MC draw or anchor solve; exact default solver and local frame."""
    started = perf_counter()
    ids = np.array(indices)
    with KernelCounter() as instrument:
        models = quadratic_responses_from_coefficients(data.model.coefficients, data.nx)
        geometry = local_nbi_geometry(payoff[np.ix_(ids, ids)], (Direction.MIN,) * len(ids))
        problem = LocalNBIProblem(tuple(models[j] for j in ids), geometry, anchors[ids], data.alpha)
        lattice = simplex_lattice(len(ids), lattice_resolution(len(ids)))
        prepared = perf_counter() - started
        tick = perf_counter()
        solved = solve_nbi_lattice(problem, lattice)
        solver_seconds = perf_counter() - tick
    points, weights, records = [], [], []
    trials: list[dict[str, Any]] = []
    for j, solution in enumerate(solved.solutions):
        if solution.accepted:
            points.append(solution.point)
            weights.append(j)
        records.append(dict(weight_id=j, accepted=solution.accepted, attempts=len(solution.trials)))
        trials.extend(dict(weight_id=j, **asdict(t)) for t in solution.trials)
    return dict(
        X=np.array(points).reshape(-1, data.nx),
        weights=weights,
        subproblems=records,
        trials=trials,
        iterations=sum(t["iterations"] for t in trials),
        attempts=sum(s["attempts"] for s in records),
        counters=dict(instrument.counts),
        geometry_seconds=prepared,
        solver_seconds=solver_seconds,
        elapsed_seconds=perf_counter() - started,
    )
