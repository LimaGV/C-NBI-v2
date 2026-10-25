"""Consolidated pymoo algorithms; only problem adapters and sphere operators here."""

from dataclasses import dataclass
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
from pymoo.optimize import minimize  # type: ignore[import-untyped]
from pymoo.util.ref_dirs import get_reference_directions  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.simplex.lattice import positive_integer

from .problem import CanonicalProblem, radial_repair


@dataclass(frozen=True, slots=True)
class EAConfig:
    family: str
    n_partitions: int = 4
    generations: int = 400
    sbx_probability: float = .9
    sbx_eta: float = 10.
    pm_eta: float = 15.
    n_neighbors: int = 66
    prob_neighbor_mating: float = .9

    def __post_init__(self) -> None:
        if self.family not in {"NSGA3", "MOEAD"}:
            raise ValueError("reference EA family must be NSGA3 or MOEAD")
        for name in ("n_partitions", "generations", "n_neighbors"):
            positive_integer(getattr(self, name), name)
        if (not 0 < self.sbx_probability <= 1 or not 0 < self.prob_neighbor_mating <= 1
                or min(self.sbx_eta, self.pm_eta) <= 0
                or not np.isfinite([self.sbx_eta, self.pm_eta]).all()):
            raise ValueError("invalid EA probability or distribution index")

    @property
    def population(self) -> int:
        return comb(8+self.n_partitions-1, 7)

    @property
    def nfe_max(self) -> int:
        return self.population*self.generations


class BallSampling(Sampling):  # type: ignore[misc]
    def __init__(self, alpha: float) -> None:
        super().__init__()
        self.alpha = alpha

    def _do(self, problem: Any, n_samples: int, *, random_state: Any, **kwargs: Any) -> FloatArray:
        directions = random_state.normal(size=(n_samples, 3))
        norm = np.linalg.norm(directions, axis=1)
        if np.any(norm == 0):
            raise FloatingPointError("zero sampling direction")
        radius = self.alpha*random_state.random(n_samples)**(1/3)
        return radial_repair(directions/norm[:, None]*radius[:, None], self.alpha)


class SphereRepair(Repair):  # type: ignore[misc]
    def __init__(self, alpha: float) -> None:
        super().__init__()
        self.alpha = alpha
        self.repaired_candidates = 0

    def _do(self, problem: Any, x: FloatArray, **kwargs: Any) -> FloatArray:
        self.repaired_candidates += int(np.count_nonzero(np.linalg.norm(x, axis=1) > self.alpha))
        return radial_repair(x, self.alpha)


class RSMAdapter(Problem):  # type: ignore[misc]
    def __init__(self, canonical: CanonicalProblem, nfe_max: int) -> None:
        super().__init__(n_var=3, n_obj=8, n_ieq_constr=0, xl=-canonical.alpha, xu=canonical.alpha)
        self.canonical = canonical
        self.nfe_max = nfe_max
        self.evaluations = 0

    def _evaluate(self, x: FloatArray, out: dict[str, Any], **kwargs: Any) -> None:
        if self.evaluations+len(x) > self.nfe_max:
            raise RuntimeError("common hard NFE ceiling would be exceeded")
        if not self.canonical.feasible(x).all():
            raise ValueError("EA attempted an infeasible evaluation despite sphere repair")
        natural = self.canonical.natural(x)
        out["F"] = self.canonical.normalize(natural)
        out["natural_F"] = natural
        self.evaluations += len(x)


def run_evolutionary(
    problem: CanonicalProblem, config: EAConfig, seed: int, *, callback: Any | None = None
) -> dict[str, Any]:
    positive_integer(seed, "seed", 0)
    start = perf_counter()
    directions = get_reference_directions("das-dennis", 8, n_partitions=config.n_partitions)
    repair = SphereRepair(problem.alpha)
    shared = dict(ref_dirs=directions, sampling=BallSampling(problem.alpha), repair=repair,
                  crossover=SBX(prob=config.sbx_probability, eta=config.sbx_eta, prob_var=.5,
                                prob_exch=1., prob_bin=.5, n_offsprings=2, repair=repair),
                  mutation=PM(prob=1/3, prob_var=1/3, eta=config.pm_eta,
                              at_least_once=False, repair=repair))
    if config.family == "NSGA3":
        algorithm = NSGA3(pop_size=config.population, n_offsprings=config.population,
                          eliminate_duplicates=True, **shared)
    else:
        algorithm = MOEAD(n_neighbors=min(config.n_neighbors, config.population-1),
                          prob_neighbor_mating=config.prob_neighbor_mating,
                          decomposition=PBI(theta=5.), **shared)
    adapter = RSMAdapter(problem, config.nfe_max)
    result = minimize(adapter, algorithm, termination=("n_gen", config.generations), seed=seed,
                       verbose=False, save_history=False, copy_algorithm=False,
                       **({"callback": callback} if callback is not None else {}))
    x = np.asarray(result.pop.get("X"), dtype=np.float64)
    optimizer_f = np.asarray(result.pop.get("F"), dtype=np.float64)
    natural_f = np.asarray(result.pop.get("natural_F"), dtype=np.float64)
    if (x.shape != (config.population, 3) or natural_f.shape != (len(x), 8)
            or not problem.feasible(x).all() or not np.isfinite(optimizer_f).all()
            or adapter.evaluations > config.nfe_max):
        raise RuntimeError("incomplete, infeasible or nonfinite final evolutionary population")
    return {"x": x, "natural_f": natural_f, "optimizer_f": optimizer_f,
            "nfe": adapter.evaluations, "nfe_max": config.nfe_max,
            "generations": config.generations, "population": config.population,
            "seed": seed, "family": config.family,
            "repair_operations": repair.repaired_candidates, "runtime": perf_counter()-start}
