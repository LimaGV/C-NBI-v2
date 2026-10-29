"""VRF-NBI adapted from LimaGV/C-NBI 7bd4915 (MIT; see migration notice).

Original observations -> rotated scores -> auxiliary quadratic models -> full
VRF objectives. The legacy direct-score variant is deliberately absent.
"""

from dataclasses import asdict
from itertools import combinations
from time import perf_counter
from typing import Any

import numpy as np
from scipy.linalg import null_space  # type: ignore[import-untyped]
from scipy.optimize import minimize  # type: ignore[import-untyped]

from cnbi_v2.model import diagnose_rsm, fit_multivariate_rsm
from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.optimization import QuadraticResponse, evaluate_responses
from cnbi_v2.simplex.lattice import simplex_lattice

from .configuration import lattice_resolution
from .contracts import RunOutput, SearchInput


def factor_count(cumulative: FloatArray) -> int:
    if (cumulative.ndim != 1 or len(cumulative) < 2 or not np.isfinite(cumulative).all()
            or np.any(np.diff(cumulative) < -1e-12) or cumulative[-1] < .9):
        raise ValueError("invalid cumulative factor variance")
    return max(2, int(np.searchsorted(cumulative, .9)+1))


def varimax(loadings: FloatArray) -> tuple[FloatArray, FloatArray, int]:
    """Kaiser-normalized orthogonal SVD iteration; 500 iterations, tolerance 1e-5.

    Same mathematical iteration as factor-analyzer 0.5.1 Rotator defaults.
    Its MIT notice is preserved in references/software/phase10d_third_party.txt.
    """
    norms = np.sqrt(np.sum(loadings**2, axis=1))
    if np.any(norms == 0):
        raise ValueError("zero communality in retained loadings")
    normalized = loadings/norms[:, None]
    rotation = np.eye(loadings.shape[1])
    criterion = 0.
    for iteration in range(1, 501):
        previous = criterion
        basis = normalized@rotation
        diagonal = np.diag(np.ones(len(basis)).dot(basis**2))
        transformed = normalized.T@(basis**3-basis@diagonal/len(basis))
        u, singular, vt = np.linalg.svd(transformed)
        rotation = u@vt
        criterion = float(singular.sum())
        if criterion < previous*(1+1e-5):
            return (normalized@rotation)*norms[:, None], rotation, iteration
    raise ValueError("Varimax did not converge within the legacy iteration limit")


def factor_analysis(y: FloatArray, k: int) -> dict[str, Any]:
    mean, scale = y.mean(axis=0), y.std(axis=0, ddof=0)
    if np.any(scale <= 1e-14):
        raise ValueError("constant response cannot be standardized")
    z = (y-mean)/scale
    eigenvalues, eigenvectors = np.linalg.eigh(np.corrcoef(z, rowvar=False))
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.maximum(eigenvalues[order], 0.)
    initial = eigenvectors[:, order[:k]]*np.sqrt(eigenvalues[:k])
    loadings, rotation, iterations = varimax(initial)
    signs = np.where(loadings[np.argmax(np.abs(loadings), axis=0), np.arange(k)] >= 0, 1., -1.)
    loadings *= signs
    gram = loadings.T@loadings
    weights = loadings@np.linalg.pinv(gram, rcond=1e-15)
    return dict(mean=mean, scale=scale, loadings=loadings, rotation=rotation, signs=signs,
                weights=weights, scores=z@weights, eigenvalues=eigenvalues,
                cumulative=np.cumsum(eigenvalues)/eigenvalues.sum(),
                rank=int(np.linalg.matrix_rank(gram)), condition=float(np.linalg.cond(gram)),
                varimax_iterations=iterations, pinv_rcond=1e-15)


def vrf_values(models: tuple[QuadraticResponse, ...], targets: FloatArray,
               variance: FloatArray, point: FloatArray) -> FloatArray:
    return np.asarray((evaluate_responses(models, point)-targets)**2+variance, dtype=np.float64)


def vrf_jacobian(models: tuple[QuadraticResponse, ...], targets: FloatArray,
                 point: FloatArray) -> FloatArray:
    delta = evaluate_responses(models, point)-targets
    return np.asarray(2*delta[:, None]*np.array([model.gradient(point) for model in models]),
                      dtype=np.float64)


def factor_design_jacobian(point: FloatArray) -> FloatArray:
    """Canonical term derivatives in the v1 arithmetic order, for migration fidelity."""
    n = len(point)
    cross = []
    for i, j in combinations(range(n), 2):
        row = np.zeros(n)
        row[i], row[j] = point[j], point[i]
        cross.append(row)
    return np.vstack([np.zeros(n), np.eye(n), 2*np.diag(point), cross])


def run_vrf(data: SearchInput, seed: int) -> RunOutput:
    started = perf_counter()
    z = (data.observed-data.observed.mean(0))/data.observed.std(0, ddof=0)
    eigenvalues = np.maximum(np.linalg.eigvalsh(np.corrcoef(z, rowvar=False))[::-1], 0.)
    cumulative = np.cumsum(eigenvalues)/eigenvalues.sum()
    k = factor_count(cumulative)
    diagnostics: dict[str, Any] = dict(
        method="VRF-NBI", factor_rule="max(2,k90)", n_factors=k,
        retained_variance=float(cumulative[k-1]), cumulative=cumulative,
        implementation="Pereira_2025_Eqs11_17_to28_with_documented_v1_transfer",
    )
    if k > data.nx+1:
        return RunOutput(np.empty((0, data.nx)), np.empty((0, data.m)),
                         "VRF_STRUCTURALLY_INVALID", diagnostics,
                         timings=dict(total=perf_counter()-started))
    analysis = factor_analysis(data.observed, k)
    fit = fit_multivariate_rsm(data.ccd, analysis["scores"])
    summary = diagnose_rsm(fit, data.ccd)
    counters = dict(vrf_vector_evaluations=0, vrf_jacobian_calls=0, extreme_solves=0,
                    extreme_iterations=0, nbi_subproblems=0, nbi_attempts=0, nbi_iterations=0)
    radius, nx = data.alpha, data.nx
    rng = np.random.Generator(np.random.PCG64(910003+seed))
    starts = [np.zeros(nx), *list(.99*radius*np.eye(nx)), *list(-.99*radius*np.eye(nx))]
    for _ in range(2):
        direction = rng.normal(size=nx)
        starts.append(radius*rng.random()**(1/nx)*direction/np.linalg.norm(direction))
    sphere: dict[str, Any] = dict(
        type="ineq", fun=lambda x: radius**2-float(x@x), jac=lambda x: -2*x,
    )
    extreme_trials: list[dict[str, Any]] = []

    def extreme(fun: Any, jac: Any, maximize: bool = False,
                proposals: list[FloatArray] | None = None) -> Any:
        sign = -1. if maximize else 1.
        results = []
        for x0 in starts if proposals is None else proposals:
            result = minimize(lambda x: sign*float(fun(x)), x0,
                              jac=lambda x: sign*jac(x), method="SLSQP",
                              bounds=[(-radius, radius)]*nx, constraints=[sphere],
                              options=dict(ftol=1e-12, maxiter=100))
            counters["extreme_solves"] += 1
            counters["extreme_iterations"] += int(result.nit)
            feasible = bool(np.isfinite(result.fun) and sphere["fun"](result.x) >= -1e-7)
            extreme_trials.append(dict(x=result.x, success=bool(result.success),
                                       feasible=feasible, value=float(result.fun),
                                       iterations=int(result.nit), maximize=maximize))
            if feasible:
                results.append(result)
        if not results:
            raise ValueError("no feasible VRF extreme; no inferred replacement")
        return min(results, key=lambda result: sign*float(fun(result.x)))

    def factor_value(point: FloatArray) -> FloatArray:
        return fit.predict(point)

    def factor_jac(point: FloatArray) -> FloatArray:
        return np.asarray((factor_design_jacobian(point).T@fit.coefficients).T, dtype=np.float64)

    targets = np.array([extreme(lambda x, j=j: factor_value(x)[j],
                                lambda x, j=j: factor_jac(x)[j]).fun for j in range(k)])
    # Eq21: sum of squared loadings. The adjacent rho defines the domain radius;
    # it is not a multiplicative factor (unlike v1 7bd4915). See migration audit.
    variance = np.sum(analysis["loadings"]**2, axis=0)
    # A constant objective translation leaves Eq25 unchanged. Retain the v1
    # arithmetic gauge inside SLSQP so quartic-flat payoff tie selection is not
    # changed by subtractive rounding. Published raw constants are corrected
    # on export; the shift is explicit and independently checked in the audit.
    optimization_variance = variance*radius
    gauge_shift = optimization_variance-variance

    def raw(point: FloatArray) -> FloatArray:
        counters["vrf_vector_evaluations"] += 1
        delta = factor_value(point)-targets
        return np.asarray(delta*delta+optimization_variance, dtype=np.float64)

    def raw_jac(point: FloatArray) -> FloatArray:
        counters["vrf_jacobian_calls"] += 1
        return np.asarray(2*(factor_value(point)-targets)[:, None]*factor_jac(point),
                          dtype=np.float64)

    utopia, nadir, xu, xn = [], [], [], []
    for j in range(k):
        lo = extreme(lambda x, j=j: raw(x)[j], lambda x, j=j: raw_jac(x)[j])
        hi = extreme(lambda x, j=j: raw(x)[j], lambda x, j=j: raw_jac(x)[j], True)
        utopia.append(raw(lo.x)[j])
        nadir.append(raw(hi.x)[j])
        xu.append(lo.x)
        xn.append(hi.x)
    ideal = np.array(utopia)
    amplitude = np.array(nadir)-ideal
    if np.any(amplitude <= 1e-12):
        raise ValueError("VRF utopia/nadir amplitude is degenerate")

    def value(point: FloatArray) -> FloatArray:
        return np.asarray((raw(point)-ideal)/amplitude, dtype=np.float64)

    def jacobian(point: FloatArray) -> FloatArray:
        return np.asarray(raw_jac(point)/amplitude[:, None], dtype=np.float64)

    payoff_anchors = []
    for j in range(k):
        proposals = [*xu, *xn, np.zeros(nx), *starts[1:1+2*nx]]
        candidates = []
        for x0 in proposals:
            if np.linalg.norm(x0) <= radius+1e-8:
                result = minimize(lambda x, j=j: value(x)[j], x0,
                                  jac=lambda x, j=j: jacobian(x)[j], method="SLSQP",
                                  bounds=[(-radius, radius)]*nx, constraints=[sphere],
                                  options=dict(ftol=1e-11, maxiter=100))
                counters["extreme_solves"] += 1
                counters["extreme_iterations"] += int(result.nit)
                if np.linalg.norm(result.x) <= radius+1e-8 and np.isfinite(result.fun):
                    candidates.append(result)
        if not candidates:
            raise ValueError("no feasible VRF payoff optimum")
        chosen = min(candidates, key=lambda result: (
            round(float(value(result.x)[j]), 9), -float(np.delete(value(result.x), j).sum()),
        ))
        payoff_anchors.append(chosen.x)
    anchors = np.array(payoff_anchors)
    payoff = np.column_stack([value(x) for x in anchors])
    null = null_space(payoff[:, 1:].T-payoff[:, :1].T)
    if null.shape[1] != 1:
        raise ValueError("VRF CHIM does not have a unique normal")
    normal = null[:, 0]
    if normal@(-payoff.mean(1)) < 0:
        normal = -normal
    preparation = perf_counter()-started
    solve_start = perf_counter()
    lattice = simplex_lattice(k, lattice_resolution(k))
    weights = lattice.weights
    remaining = set(range(len(weights)))
    order = []
    previous = None
    while remaining:
        index = min(remaining) if previous is None else min(
            remaining, key=lambda i: (float(np.linalg.norm(weights[i]-weights[previous])), i))
        remaining.remove(index)
        order.append(index)
        previous = index
    raw_x, rows, trials = [], [], []
    warm = None
    for index in order:
        beta, phi = weights[index], payoff@weights[index]
        counters["nbi_subproblems"] += 1
        vertex = np.flatnonzero(np.isclose(beta, 1., atol=1e-12))
        if len(vertex) == 1:
            point = anchors[vertex[0]].copy()
            residual = float(np.max(abs(value(point)-phi)))
            accepted = residual <= 1e-5 and np.linalg.norm(point) <= radius+1e-8
            warm = np.r_[point, 0.]
            rows.append(dict(weight_id=index, beta=beta, x=point, accepted=accepted,
                             eq_inf=residual, attempts=0))
            if accepted:
                raw_x.append(point)
            continue
        proposals = [] if warm is None else [warm[:-1]]
        proposals.extend([beta@anchors, *anchors[np.argsort(-beta)], np.zeros(nx)])
        rescue = np.random.Generator(np.random.PCG64(1000003+index))
        for _ in range(2):
            direction = rescue.normal(size=nx)
            proposals.append(radius*rescue.random()**(1/nx)*direction/np.linalg.norm(direction))
        candidates, seen = [], set()
        for point in proposals:
            key = tuple(np.round(point, 12))
            if np.linalg.norm(point) > radius+1e-8 or key in seen:
                continue
            seen.add(key)

            def equality(v: FloatArray, phi: FloatArray = phi) -> FloatArray:
                return np.asarray(value(v[:-1])-phi-v[-1]*normal, dtype=np.float64)

            t0 = np.clip((value(point)-phi)@normal, -10, 10)
            result = minimize(lambda v: -float(v[-1]), np.r_[point, t0],
                              jac=lambda v: np.r_[np.zeros(nx), -1.], method="SLSQP",
                              bounds=[(-radius, radius)]*nx+[(-10, 10)],
                              constraints=[dict(type="eq", fun=equality,
                                                jac=lambda v: np.column_stack(
                                                    [jacobian(v[:-1]), -normal])),
                                           dict(type="ineq", fun=lambda v: sphere["fun"](v[:-1]),
                                                jac=lambda v: np.r_[-2*v[:-1], 0.])],
                              options=dict(ftol=1e-10, maxiter=100))
            residual = float(np.max(abs(equality(result.x))))
            accepted = bool(residual <= 1e-5 and np.linalg.norm(result.x[:-1]) <= radius+1e-8
                            and np.isfinite(result.x).all())
            counters["nbi_attempts"] += 1
            counters["nbi_iterations"] += int(result.nit)
            trials.append(dict(weight_id=index, x=result.x, accepted=accepted,
                               solver_success=bool(result.success), eq_inf=residual,
                               status=int(result.status), iterations=int(result.nit)))
            candidates.append((accepted, residual, result))
            if accepted:
                break
        if not candidates:
            rows.append(dict(weight_id=index, beta=beta, accepted=False,
                             status="NO_FEASIBLE_START", attempts=0))
            warm = None
            continue
        ok, residual, result = min(candidates, key=lambda item: (
            not item[0], -float(item[2].x[-1]) if item[0] else item[1]))
        if ok:
            raw_x.append(result.x[:-1])
        rows.append(dict(weight_id=index, beta=beta, x=result.x[:-1], accepted=ok,
                         eq_inf=residual, attempts=len(candidates)))
        warm = result.x if ok else None
    solver_seconds = perf_counter()-solve_start
    post = perf_counter()
    x = np.array(raw_x, dtype=np.float64).reshape(-1, nx)
    y = data.model.predict(x)
    diagnostics.update(analysis, targets=targets, variance=variance, utopia=ideal-gauge_shift,
                       nadir=np.array(nadir)-gauge_shift,
                       optimization_gauge_shift=gauge_shift,
                       optimization_gauge_utopia=ideal, optimization_gauge_nadir=np.array(nadir),
                       optimization_gauge_variance=optimization_variance,
                       payoff=payoff, payoff_anchors=anchors,
                       normal=normal, subproblems=rows, trials=trials,
                       extreme_trials=extreme_trials, factor_diagnostics=asdict(summary))
    return RunOutput(x, y, "COMPLETED", diagnostics,
                     dict(factor_coefficients=fit.coefficients, factor_residuals=fit.residuals),
                     dict(preparation=preparation, solver=solver_seconds,
                          postprocessing=perf_counter()-post, total=perf_counter()-started),
                     dict(**counters, original_rsm_point_evaluations=len(x),
                          original_rsm_vectorized_calls=1))
