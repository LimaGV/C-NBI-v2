"""Complete v2 C-NBI orchestration for an arbitrary frozen synthetic RSM."""

from dataclasses import asdict
from time import perf_counter
from typing import Any

import numpy as np

from cnbi_v2.chim import nominal_normalization
from cnbi_v2.chim.parallel_analysis import compute_chim_spectra, evaluate_pa_prefixes
from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.nbi.geometry import local_nbi_geometry
from cnbi_v2.nbi.solver import LocalNBIProblem, solve_nbi_lattice
from cnbi_v2.optimization import Direction
from cnbi_v2.optimization.quadratic import quadratic_responses_from_coefficients
from cnbi_v2.simplex.lattice import simplex_lattice
from cnbi_v2.uncertainty.anchor_reoptimization import reoptimize_coefficient_ensemble
from cnbi_v2.uncertainty.coefficient_sampling import sample_coefficient_ensemble

from .configuration import MC_SAMPLES, lattice_resolution
from .contracts import RunOutput, SearchInput, array_hash


def run_cnbi(data: SearchInput, seed: int) -> RunOutput:
    start = perf_counter()
    direction = (Direction.MIN,)*data.m
    nominal = reoptimize_coefficient_ensemble(
        data.model.coefficients[None], data.nx, direction, data.alpha,
    )
    if not nominal.valid_payoffs.all():
        raise ValueError("nominal anchor certification failed; no replacement permitted")
    anchors, payoff = nominal.anchors[0], nominal.payoffs[0]
    normalization = nominal_normalization(payoff, direction)
    sampled = sample_coefficient_ensemble(
        data.model.coefficients, data.design_r, data.residual_covariance, MC_SAMPLES, seed=seed,
    )
    mc_start = perf_counter()
    ensemble = reoptimize_coefficient_ensemble(sampled.samples, data.nx, direction, data.alpha)
    if not ensemble.valid_payoffs.all():
        raise ValueError("sampled anchor certification failed; ensemble cannot be silently reduced")
    mc_seconds = perf_counter()-mc_start
    spectra = compute_chim_spectra(
        normalization.normalize(payoff), normalization.perturbations(ensemble.payoffs), data.nx,
    )
    screening = evaluate_pa_prefixes(spectra, (MC_SAMPLES,))[0]
    subsets: list[dict[str, Any]] = []
    for spectrum, decision in zip(spectra, screening.components, strict=True):
        subsets.append(dict(
            subset_id=spectrum.subset_id, indices=list(spectrum.indices), scope=spectrum.scope,
            observed=spectrum.observed, q95=decision.q95, margins=decision.margins,
            component_passes=decision.passes,
            selected=spectrum.subset_id in screening.selected_ids,
            reason="ALL_COMPONENTS_STRICTLY_ABOVE_Q95" if decision.passes.all()
            else "AT_LEAST_ONE_COMPONENT_NOT_ABOVE_Q95",
        ))
    preparation = perf_counter()-start
    solver_start = perf_counter()
    models = quadratic_responses_from_coefficients(data.model.coefficients, data.nx)
    decisions: list[FloatArray] = []
    origins = []
    subproblems: list[dict[str, Any]] = []
    trials: list[dict[str, Any]] = []
    for spectrum in spectra[1:]:
        if spectrum.subset_id not in screening.selected_ids:
            continue
        ids = np.array(spectrum.indices)
        local = payoff[np.ix_(ids, ids)]
        geometry = local_nbi_geometry(local, (Direction.MIN,)*len(ids))
        problem = LocalNBIProblem(tuple(models[j] for j in ids), geometry,
                                  anchors[ids], data.alpha)
        lattice = simplex_lattice(len(ids), lattice_resolution(len(ids)))
        solved = solve_nbi_lattice(problem, lattice)
        for index, solution in enumerate(solved.solutions):
            raw_index = None
            if solution.accepted:
                assert solution.point is not None
                raw_index = len(decisions)
                decisions.append(solution.point)
                origins.append(dict(subset_id=spectrum.subset_id, weight_id=index))
            subproblems.append(dict(
                subset_id=spectrum.subset_id, weight_id=index, beta=lattice.weights[index],
                accepted=solution.accepted, raw_index=raw_index, attempts=len(solution.trials),
            ))
            trials.extend(dict(subset_id=spectrum.subset_id, weight_id=index,
                               attempt=i+1, **asdict(trial))
                          for i, trial in enumerate(solution.trials))
    solver_seconds = perf_counter()-solver_start
    post_start = perf_counter()
    x = np.array(decisions, dtype=np.float64).reshape(-1, data.nx)
    y = data.model.predict(x) if len(x) else np.empty((0, data.m))
    diagnostics = dict(
        method="C-NBI", B=MC_SAMPLES, seed=str(seed),
        covariance_method=sampled.residual_factorization_method,
        covariance_psd_tolerance=sampled.psd_eigenvalue_tolerance,
        covariance_zeroed_negative_eigenvalues=sampled.zeroed_negative_eigenvalues,
        coefficient_samples_sha256=array_hash(sampled.samples),
        mc_payoffs_sha256=array_hash(ensemble.payoffs), all_mc_payoffs_valid=True,
        nominal_anchors=anchors, nominal_payoff=payoff,
        normalization_utopia=normalization.utopia,
        normalization_amplitudes=normalization.amplitudes,
        global_dimension=screening.global_dimension, global_pattern=screening.global_pattern,
        candidate_subsets=len(spectra)-1, selected_subsets=len(screening.selected_ids),
        subsets=subsets, subproblems=subproblems, trials=trials, raw_origins=origins,
        mc_anchor_seconds=mc_seconds,
    )
    return RunOutput(
        x, y, "COMPLETED" if len(x) else "NO_ACCEPTED_NBI_SOLUTIONS", diagnostics,
        dict(coefficient_samples=sampled.samples, mc_anchors=ensemble.anchors,
             mc_payoffs=ensemble.payoffs),
        dict(preparation=preparation, solver=solver_seconds,
             postprocessing=perf_counter()-post_start, total=perf_counter()-start),
        dict(original_rsm_point_evaluations=len(x), original_rsm_vectorized_calls=1,
             mc_anchor_solves=MC_SAMPLES*data.m, nominal_anchor_solves=data.m,
             nbi_subproblems=len(subproblems),
             nbi_attempts=len(trials), nbi_iterations=sum(t["iterations"] for t in trials)),
    )
