"""Dimension-independent pymoo adapters with the 18 pinned v1 calibrations.

LimaGV/C-NBI 7bd4915 transfer; attribution in the migration notice. The domain
sampling is explicitly generalized to the Phase10D radius; there is no truth
oracle or analytic normalization in this module.
"""

from math import comb
from time import perf_counter
from typing import Any

import numpy as np
from pymoo.algorithms.moo.moead import MOEAD  # type: ignore[import-untyped]
from pymoo.algorithms.moo.nsga3 import NSGA3  # type: ignore[import-untyped]
from pymoo.core.problem import Problem  # type: ignore[import-untyped]
from pymoo.core.repair import Repair  # type: ignore[import-untyped]
from pymoo.core.sampling import Sampling  # type: ignore[import-untyped]
from pymoo.decomposition.pbi import PBI  # type: ignore[import-untyped]
from pymoo.operators.crossover.sbx import SBX  # type: ignore[import-untyped]
from pymoo.operators.mutation.pm import PM  # type: ignore[import-untyped]
from pymoo.util.ref_dirs import get_reference_directions  # type: ignore[import-untyped]

from cnbi_v2.model import quadratic_design
from cnbi_v2.model.quadratic_design import FloatArray

from .configuration import ea_ceiling
from .contracts import RunOutput, SearchInput


def radial_repair(x: FloatArray, alpha: float) -> FloatArray:
    result = np.array(x, dtype=np.float64, copy=True)
    norms = np.linalg.norm(result, axis=1)
    outside = norms > alpha
    # One representable step inward ensures strict feasibility after float64
    # normalization; this is a registered numerical repair, never offline repair.
    result[outside] *= (np.nextafter(alpha, 0.)/norms[outside])[:, None]
    again = np.linalg.norm(result, axis=1) > alpha
    result[again] *= np.nextafter(1., 0.)
    return result


class BallSampling(Sampling):  # type: ignore[misc]
    def _do(self, problem: Any, n_samples: int, *, random_state: Any, **kwargs: Any) -> FloatArray:
        direction = random_state.normal(size=(n_samples, problem.n_var))
        norm = np.linalg.norm(direction, axis=1)
        if np.any(norm == 0):
            raise FloatingPointError("zero sampling direction")
        radii = problem.data.alpha*random_state.random(n_samples)**(1/problem.n_var)
        return radial_repair(direction/norm[:, None]*radii[:, None], problem.data.alpha)


class SphereRepair(Repair):  # type: ignore[misc]
    def __init__(self, alpha: float) -> None:
        super().__init__()
        self.alpha = alpha
        self.calls = 0
        self.candidates = 0
        self.max_before = 0.

    def _do(self, problem: Any, x: FloatArray, **kwargs: Any) -> FloatArray:
        norms = np.linalg.norm(x, axis=1)
        self.calls += 1
        self.candidates += int(np.count_nonzero(norms > self.alpha))
        self.max_before = max(self.max_before, float(np.max(norms-self.alpha, initial=0.)))
        return radial_repair(x, self.alpha)


class RSMProblem(Problem):  # type: ignore[misc]
    def __init__(self, data: SearchInput, ceiling: int) -> None:
        super().__init__(n_var=data.nx, n_obj=data.m, n_ieq_constr=0,
                         xl=-data.alpha, xu=data.alpha)
        self.data = data
        self.ceiling = ceiling
        self.nfe = 0
        self.vectorized_calls = 0

    def _evaluate(self, x: FloatArray, out: dict[str, Any], **kwargs: Any) -> None:
        if self.nfe+len(x) > self.ceiling:
            raise RuntimeError("hard evaluation ceiling would be exceeded")
        if not np.all(np.linalg.norm(x, axis=1) <= self.data.alpha):
            raise ValueError("repair failed to enforce the ball before evaluation")
        out["F"] = self.data.model.predict(x)
        self.nfe += len(x)
        self.vectorized_calls += 1


def run_ea(data: SearchInput, method: str, config: dict[str, Any], seed: int,
           *, budget: int | None = None) -> RunOutput:
    """budget override is for infrastructure tests only; official runner omits it.

    Legacy termination uses floor(budget/population) complete generations. It
    can finish below the ceiling; the unspent remainder is explicitly exported.
    """
    started = perf_counter()
    if method not in ("NSGA-III", "MOEA/D"):
        raise ValueError("unsupported evolutionary method")
    ceiling = ea_ceiling(data.m) if budget is None else budget
    partitions = int(config["n_partitions"])
    population = comb(data.m+partitions-1, partitions)
    if ceiling < population:
        raise ValueError("budget cannot initialize the full population")
    generations = max(1, ceiling//population)
    ref_dirs = get_reference_directions("das-dennis", data.m, n_partitions=partitions)
    repair = SphereRepair(data.alpha)
    neighbors = max(2, min(population-1, round(float(config["neighbor_fraction"])*population)))
    shared = dict(
        ref_dirs=ref_dirs, sampling=BallSampling(), repair=repair,
        crossover=SBX(prob=float(config["sbx_probability"]), eta=float(config["sbx_eta"]),
                      prob_var=.5, prob_exch=1., prob_bin=.5, n_offsprings=2, repair=repair),
        mutation=PM(prob=1/data.nx, prob_var=min(.5, 1/data.nx), eta=float(config["pm_eta"]),
                    at_least_once=False, repair=repair),
    )
    algorithm = (NSGA3(pop_size=population, eliminate_duplicates=True, **shared)
                 if method == "NSGA-III" else MOEAD(
                     n_neighbors=neighbors,
                     prob_neighbor_mating=float(config["prob_neighbor_mating"]),
                     decomposition=PBI(theta=5.), **shared))
    adapter = RSMProblem(data, ceiling)
    algorithm.setup(adapter, termination=("n_gen", generations), seed=seed, verbose=False)
    preparation = perf_counter()-started
    optimization = perf_counter()
    while algorithm.has_next():
        algorithm.next()
    solver_seconds = perf_counter()-optimization
    post = perf_counter()
    x = np.asarray(algorithm.pop.get("X"), dtype=np.float64).copy()
    f = data.model.predict(x)
    optimizer_f = np.asarray(algorithm.pop.get("F"), dtype=np.float64).copy()
    p = len(data.model.coefficients)
    roundoff = 8*p*np.finfo(float).eps*(abs(quadratic_design(x))@abs(data.model.coefficients))
    if np.any(abs(f-optimizer_f) > roundoff):
        raise ValueError("final population predictions no longer match the frozen RSM")
    if len(x) != population or adapter.nfe > ceiling:
        raise ValueError("incomplete population or exceeded budget")
    return RunOutput(
        x, f, "COMPLETED",
        dict(method=method, transferred_parameters=config, population=population,
             final_population_ids=list(range(population)), nfe_ceiling=ceiling,
             generations=generations, unspent_budget=ceiling-adapter.nfe,
             termination="legacy_floor_complete_generations_no_partial_generation",
             n_neighbors=neighbors, decomposition="PBI(theta=5)",
             pm_individual_probability=1/data.nx,
             pm_variable_probability=min(.5, 1/data.nx), repair_calls=repair.calls,
             repaired_candidates=repair.candidates, max_violation_before_repair=repair.max_before,
             max_violation_after_repair=float(np.max(np.linalg.norm(x, axis=1)-data.alpha)),
             batch_replay_max_difference=float(np.max(abs(f-optimizer_f))),
             pymoo_version="0.6.2", initialization="uniform_ball_PCG64"),
        arrays=dict(optimizer_objectives=optimizer_f),
        timings=dict(preparation=preparation, solver=solver_seconds,
                     postprocessing=perf_counter()-post, total=perf_counter()-started),
        counters=dict(original_rsm_point_evaluations=adapter.nfe,
                      original_rsm_vectorized_calls=adapter.vectorized_calls,
                      original_rsm_export_point_evaluations=len(x), gradient_calls=0,
                      repair_calls=repair.calls, repaired_candidates=repair.candidates),
    )
