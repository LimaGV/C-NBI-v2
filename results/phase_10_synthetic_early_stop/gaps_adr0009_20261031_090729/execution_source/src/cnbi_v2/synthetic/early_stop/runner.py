"""Fresh incremental C-NBI orchestration; all mathematical kernels stay frozen.

The search interface has no archived ensemble, true objective or quality metric.
Only a consumed batch is generated/reoptimized. A stop breaks the iterator before
its next draw. NBI always runs afresh, even when a selection matches PA2000.
"""

from collections.abc import Callable
from dataclasses import asdict
from time import perf_counter
from typing import Any

import numpy as np

from cnbi_v2.chim import nominal_normalization
from cnbi_v2.chim.parallel_analysis import (
    ChimSpectrum,
    PACheckpoint,
    compute_chim_spectra,
    evaluate_pa_prefixes,
)
from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.nbi.geometry import local_nbi_geometry
from cnbi_v2.nbi.sensitivity import nondominated_mask
from cnbi_v2.nbi.solver import LocalNBIProblem, solve_nbi_lattice
from cnbi_v2.optimization import Direction
from cnbi_v2.optimization.quadratic import quadratic_responses_from_coefficients
from cnbi_v2.simplex.lattice import simplex_lattice
from cnbi_v2.synthetic.benchmark.configuration import lattice_resolution
from cnbi_v2.synthetic.benchmark.contracts import RunOutput, SearchInput, array_hash
from cnbi_v2.synthetic.benchmark.instrumentation import KernelCounter
from cnbi_v2.uncertainty.anchor_reoptimization import reoptimize_coefficient_ensemble
from cnbi_v2.uncertainty.coefficient_sampling import iter_coefficient_batches

from .policy import StopPolicy, assess_stop

BatchSink = Callable[[int, dict[str, FloatArray]], None]


def _search(
    data: SearchInput,
    seed: int,
    policy: StopPolicy,
    sink: BatchSink | None,
    enable_stopping: bool,
) -> RunOutput:
    start = perf_counter()
    clocks = dict(
        nominal_anchors=0.0,
        coefficient_generation=0.0,
        mc_anchors=0.0,
        spectra=0.0,
        pa_checkpoints=0.0,
        geometry_certification=0.0,
        incremental_persistence=0.0,
    )
    directions = (Direction.MIN,) * data.m
    tick = perf_counter()
    nominal = reoptimize_coefficient_ensemble(
        data.model.coefficients[None], data.nx, directions, data.alpha
    )
    if not nominal.valid_payoffs.all():
        raise ValueError("nominal anchor certification failed; no replacement permitted")
    anchors, payoff = nominal.anchors[0], nominal.payoffs[0]
    normalization = nominal_normalization(payoff, directions)
    normalized = normalization.normalize(payoff)
    clocks["nominal_anchors"] = perf_counter() - tick
    tick = perf_counter()
    batches = iter_coefficient_batches(
        data.model.coefficients,
        data.design_r,
        data.residual_covariance,
        policy.maximum_B,
        seed=seed,
        batch_size=100,
    )
    clocks["coefficient_generation"] += perf_counter() - tick
    samples, mc_anchors, mc_payoffs = [], [], []
    noise: list[list[FloatArray]] = []
    history: list[PACheckpoint] = []
    trajectory: list[dict[str, Any]] = []
    geometries: dict[str, Any] = {}
    B = 0
    # next() is deliberately inside this loop; no prefetch/materialization exists.
    while B < policy.maximum_B:
        tick = perf_counter()
        batch = next(batches)
        clocks["coefficient_generation"] += perf_counter() - tick
        tick = perf_counter()
        ensemble = reoptimize_coefficient_ensemble(batch, data.nx, directions, data.alpha)
        clocks["mc_anchors"] += perf_counter() - tick
        if not ensemble.valid_payoffs.all():
            raise ValueError("sampled anchor certification failed; no ensemble reduction")
        samples.append(batch)
        mc_anchors.append(ensemble.anchors)
        mc_payoffs.append(ensemble.payoffs)
        B += len(batch)
        tick = perf_counter()
        if sink is not None:
            sink(
                B,
                dict(
                    coefficient_samples=batch,
                    mc_anchors=ensemble.anchors,
                    mc_payoffs=ensemble.payoffs,
                    certificates=ensemble.certificates,
                    valid_anchors=ensemble.valid_anchors.astype(float),
                    valid_payoffs=ensemble.valid_payoffs.astype(float),
                ),
            )
        clocks["incremental_persistence"] += perf_counter() - tick
        tick = perf_counter()
        latest = compute_chim_spectra(
            normalized, normalization.perturbations(ensemble.payoffs), data.nx
        )
        if not noise:
            noise = [[] for _ in latest]
        for chunks, spectrum in zip(noise, latest, strict=True):
            chunks.append(spectrum.noise)
        clocks["spectra"] += perf_counter() - tick
        if B not in policy.checkpoints:
            continue
        tick = perf_counter()
        spectra = tuple(
            ChimSpectrum(s.scope, s.subset_id, s.indices, s.observed, np.concatenate(chunks))
            for s, chunks in zip(latest, noise, strict=True)
        )
        screening = evaluate_pa_prefixes(spectra, (B,))[0]
        history.append(screening)
        observed = np.concatenate([s.observed for s in spectra])
        scales = np.concatenate([np.full(len(s.observed), s.observed[0]) for s in spectra])
        clocks["pa_checkpoints"] += perf_counter() - tick
        tick = perf_counter()
        certified = bool(screening.selected_ids)
        for spectrum in spectra[1:]:
            if spectrum.subset_id in screening.selected_ids:
                if spectrum.subset_id not in geometries:
                    ids = np.array(spectrum.indices)
                    # Geometry cannot relax or alter PA selection. A failure
                    # blocks stopping and is retained as a final solver failure.
                    try:
                        geometries[spectrum.subset_id] = local_nbi_geometry(
                            payoff[np.ix_(ids, ids)], (Direction.MIN,) * len(ids)
                        )
                    except ValueError:
                        geometries[spectrum.subset_id] = None
                certified = certified and geometries[spectrum.subset_id] is not None
        clocks["geometry_certification"] += perf_counter() - tick
        tick = perf_counter()
        guard = assess_stop(history, observed, scales, policy, certified=certified)
        trajectory.append(
            dict(
                **guard,
                global_dimension=screening.global_dimension,
                selected_ids=sorted(screening.selected_ids),
                quantile_ids=screening.quantile_ids,
                decision_quantiles=screening.decision_quantiles,
                component_passes=np.concatenate([c.passes for c in screening.components]),
            )
        )
        clocks["pa_checkpoints"] += perf_counter() - tick
        if enable_stopping and guard["stop"]:
            break
    preparation = perf_counter() - start
    solver_start = perf_counter()
    models = quadratic_responses_from_coefficients(data.model.coefficients, data.nx)
    decisions: list[FloatArray] = []
    origins: list[dict[str, Any]] = []
    subproblems: list[dict[str, Any]] = []
    trials: list[dict[str, Any]] = []
    for spectrum in spectra[1:]:
        if spectrum.subset_id not in screening.selected_ids:
            continue
        ids = np.array(spectrum.indices)
        # Reuse the exact nominal geometry already certified, never a past solve.
        geometry = geometries[spectrum.subset_id]
        if geometry is None:
            raise ValueError("selected nominal NBI geometry is not certified")
        problem = LocalNBIProblem(tuple(models[j] for j in ids), geometry, anchors[ids], data.alpha)
        lattice = simplex_lattice(len(ids), lattice_resolution(len(ids)))
        solved = solve_nbi_lattice(problem, lattice)
        for index, solution in enumerate(solved.solutions):
            raw_index = None
            if solution.accepted:
                assert solution.point is not None
                raw_index = len(decisions)
                decisions.append(solution.point)
                origins.append(dict(subset_id=spectrum.subset_id, weight_id=index))
            subproblems.append(
                dict(
                    subset_id=spectrum.subset_id,
                    weight_id=index,
                    beta=lattice.weights[index],
                    accepted=solution.accepted,
                    raw_index=raw_index,
                    attempts=len(solution.trials),
                )
            )
            trials.extend(
                dict(subset_id=spectrum.subset_id, weight_id=index, attempt=i + 1, **asdict(trial))
                for i, trial in enumerate(solution.trials)
            )
    solver_seconds = perf_counter() - solver_start
    tick = perf_counter()
    x = np.array(decisions, dtype=np.float64).reshape(-1, data.nx)
    y = data.model.predict(x) if len(x) else np.empty((0, data.m))
    sampled = np.concatenate(samples)
    payoffs = np.concatenate(mc_payoffs)
    status = "EARLY_STOP" if B < policy.maximum_B else "MAX_B_REACHED"
    subsets = [
        dict(
            subset_id=s.subset_id,
            indices=list(s.indices),
            scope=s.scope,
            observed=s.observed,
            q95=d.q95,
            margins=d.margins,
            component_passes=d.passes,
            selected=s.subset_id in screening.selected_ids,
        )
        for s, d in zip(spectra, screening.components, strict=True)
    ]
    diagnostics = dict(
        method="C-NBI-ES",
        B=B,
        B_effective=B,
        generated_samples=B,
        reoptimized_samples=B,
        seed=str(seed),
        stopping_status=status,
        enable_stopping=enable_stopping,
        policy=asdict(policy),
        checkpoints=trajectory,
        covariance_policy="unchanged iter_coefficient_batches factors; no jitter",
        coefficient_samples_sha256=array_hash(sampled),
        mc_payoffs_sha256=array_hash(payoffs),
        all_mc_payoffs_valid=True,
        nominal_anchors=anchors,
        nominal_payoff=payoff,
        normalization_utopia=normalization.utopia,
        normalization_amplitudes=normalization.amplitudes,
        global_dimension=screening.global_dimension,
        global_pattern=screening.global_pattern,
        candidate_subsets=len(spectra) - 1,
        selected_subsets=len(screening.selected_ids),
        subsets=subsets,
        subproblems=subproblems,
        trials=trials,
        raw_origins=origins,
        mc_anchor_seconds=clocks["mc_anchors"],
        stage_seconds=clocks,
        no_future_draws=True,
        fresh_nbi=True,
    )
    return RunOutput(
        x,
        y,
        "COMPLETED" if len(x) else "NO_ACCEPTED_NBI_SOLUTIONS",
        diagnostics,
        dict(
            coefficient_samples=sampled, mc_anchors=np.concatenate(mc_anchors), mc_payoffs=payoffs
        ),
        dict(
            preparation=preparation,
            solver=solver_seconds,
            postprocessing=perf_counter() - tick,
            total=perf_counter() - start,
        ),
        dict(
            original_rsm_point_evaluations=len(x),
            original_rsm_vectorized_calls=1,
            mc_anchor_solves=B * data.m,
            nominal_anchor_solves=data.m,
            nbi_subproblems=len(subproblems),
            nbi_attempts=len(trials),
            nbi_iterations=sum(t["iterations"] for t in trials),
        ),
    )


DEFAULT_POLICY = StopPolicy()


def run_adaptive(
    data: SearchInput,
    seed: int,
    policy: StopPolicy = DEFAULT_POLICY,
    *,
    sink: BatchSink | None = None,
    enable_stopping: bool = True,
) -> RunOutput:
    """Original profiler, validation and full-objective postprocessing, isolated variant."""
    started = perf_counter()
    with KernelCounter() as instrumentation:
        output = _search(data, seed, policy, sink, enable_stopping)
    output.validate(data)
    output.counters.update(instrumentation.counts)
    original_points = output.counters["original_rsm_point_evaluations"] + len(output.decisions)
    output.counters["original_full_vector_points_computed"] = original_points
    output.counters["model_vector_point_events"] = (
        original_points
        + output.counters.get("quadratic_response_vector_calls", 0)
        + output.counters.get("factor_model_vector_evaluations", 0)
    )
    indices = np.flatnonzero(np.linalg.norm(output.decisions, axis=1) <= data.alpha)
    nd = indices[nondominated_mask(output.rsm_responses[indices])] if len(indices) else indices
    output.diagnostics.update(
        frozen_coefficients_sha256=array_hash(data.model.coefficients),
        raw_decisions_preserved=True,
        original_objective_nd_indices=nd,
        original_objective_feasible_indices=indices,
        original_objective_count=data.m,
        counter_policy="full_original_RSM_points_plus_separate_scalar_kernel_calls",
        instrumentation="Python_call_events; overhead included consistently in optimization time",
        counter_schema=2,
    )
    elapsed = perf_counter() - started
    output.timings["postprocessing"] = (
        elapsed - output.timings["preparation"] - output.timings["solver"]
    )
    output.timings["total"] = elapsed
    return output
