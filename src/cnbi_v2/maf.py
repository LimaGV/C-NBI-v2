"""Direct MaF8/9 adapter; Phase 11 uses the pinned V1 MaF protocol, not RSM PA.

Equations/protocol: LimaGV/C-NBI@7bd4915, benchmarks.py/parallel_analysis.py.
No V1 solver or runtime imports. The NBI solver and CHIM geometry are V2.
"""

from itertools import combinations
from time import perf_counter
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize  # type: ignore[import-untyped]
from scipy.stats import qmc  # type: ignore[import-untyped]

from cnbi_v2.benchmark.metrics import gd_igd, nearest_distances
from cnbi_v2.chim import nominal_normalization
from cnbi_v2.chim.geometry import vertex_differences
from cnbi_v2.chim.parallel_analysis import leading_dimension
from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.nbi import nondominated_mask
from cnbi_v2.nbi.geometry import LocalNBIGeometry, local_nbi_geometry
from cnbi_v2.nbi.solver import LocalNBIProblem, NBIOptions, solve_nbi_lattice
from cnbi_v2.optimization import Direction
from cnbi_v2.simplex import simplex_lattice

OPTIONS = NBIOptions(ftol=1e-10, maxiter=100, equality_tolerance=1e-5,
                     sphere_tolerance=1e-12, retry_neighbours=2)


def contains(points: Any, polygon: FloatArray) -> NDArray[np.bool_]:
    """V1 ray crossing, including boundary with its established 1e-12 guard."""
    x = np.atleast_2d(points)
    inside = np.zeros(len(x), dtype=bool)
    boundary = inside.copy()
    for a, b in zip(polygon, np.roll(polygon, -1, axis=0), strict=True):
        e, v = b-a, x-a
        cross, dot = e[0]*v[:, 1]-e[1]*v[:, 0], v@e
        boundary |= ((np.abs(cross) <= 1e-12*max(1., np.linalg.norm(e)))
                     & (dot >= -1e-12) & (dot <= e@e+1e-12))
        if e[1] != 0:
            crossing = (a[1] > x[:, 1]) != (b[1] > x[:, 1])
            inside ^= crossing & (x[:, 0] < a[0]+(x[:, 1]-a[1])*e[0]/e[1])
    return inside | boundary


def polygon_margin(point: FloatArray, polygon: FloatArray) -> tuple[float, FloatArray]:
    """Signed inside margin and active affine derivative of a convex polygon."""
    edges = np.roll(polygon, -1, axis=0)-polygon
    following = np.roll(polygon, -1, axis=0)
    orientation = np.sign(np.sum(polygon[:, 0]*following[:, 1]-polygon[:, 1]*following[:, 0]))
    gradients = orientation*np.column_stack([-edges[:, 1], edges[:, 0]])
    gradients /= np.linalg.norm(edges, axis=1)[:, None]
    margins = np.einsum('ij,ij->i', gradients, point-polygon)
    j = int(np.argmin(margins))
    return float(margins[j]), gradients[j]


class MaF:
    def __init__(self, number: int, m: int) -> None:
        if number not in (8, 9) or m not in (4, 6, 8, 10, 15):
            raise ValueError('Phase 11 supports only MaF8/9 and frozen objective counts')
        self.number, self.m = number, m
        theta = np.pi/2-np.arange(1, m+1)*2*np.pi/m
        self.vertices = np.column_stack([np.cos(theta), np.sin(theta)])
        self.polygons = []
        if number == 9:
            for gap in range(1, int(np.ceil(m/2-2))+1):
                for head in range(m):
                    tail = head+gap
                    a, b, c, d = self.vertices[np.array([head-1, head, tail, tail+1]) % m]
                    t = np.linalg.solve(np.column_stack([b-a, c-d]), c-a)[0]
                    origin = a+t*(b-a)
                    arc = self.vertices[np.arange(head, tail+1) % m]
                    self.polygons.append(np.vstack([arc, 2*origin-arc]))
        self.evaluations, self.gradient_calls = 0, 0

    def values(self, points: Any) -> Any:
        x = np.asarray(points, dtype=float)
        if x.ndim not in (1, 2) or x.shape[-1] != 2 or not np.isfinite(x).all():
            raise ValueError('finite two-dimensional decisions required')
        delta = x[..., None, :]-self.vertices
        if self.number == 8:
            return np.linalg.norm(delta, axis=-1)
        edges = np.roll(self.vertices, -1, axis=0)-self.vertices
        return np.abs(edges[:, 0]*delta[..., 1]-edges[:, 1]*delta[..., 0])/np.linalg.norm(
            edges, axis=1)

    def evaluate(self, point: Any) -> Any:
        self.evaluations += 1
        return self.values(point)

    def jacobian(self, point: FloatArray) -> Any:
        self.gradient_calls += 1
        delta = np.asarray(point)-self.vertices
        if self.number == 8:
            d = np.linalg.norm(delta, axis=1)
            return np.divide(delta, d[:, None], out=np.zeros_like(delta), where=d[:, None]>1e-15)
        edges = np.roll(self.vertices, -1, axis=0)-self.vertices
        cross = edges[:, 0]*delta[:, 1]-edges[:, 1]*delta[:, 0]
        return np.sign(cross)[:, None]*np.column_stack([-edges[:, 1], edges[:, 0]])/(
            np.linalg.norm(edges, axis=1)[:, None])

    def feasible(self, points: Any) -> NDArray[np.bool_]:
        x = np.atleast_2d(points)
        valid = np.isfinite(x).all(axis=1) & (np.abs(x) <= 10000).all(axis=1)
        if self.polygons:
            forbidden = np.zeros(len(x), dtype=bool)
            for polygon in self.polygons:
                forbidden |= contains(x, polygon)
            valid &= ~forbidden | contains(x, self.vertices)
        return cast(NDArray[np.bool_], valid)

    def margin(self, point: FloatArray) -> tuple[float, FloatArray]:
        x = np.asarray(point)
        margins = np.r_[10000+x, 10000-x]
        gradients = np.vstack([np.eye(2), -np.eye(2)])
        j = int(np.argmin(margins))
        bound = float(margins[j]), gradients[j]
        if not self.polygons:
            return bound
        central = polygon_margin(x, self.vertices)
        outside = [(-v, -g) for v, g in (polygon_margin(x, p) for p in self.polygons)]
        exterior = min(outside, key=lambda a: a[0])
        region = max((central, exterior), key=lambda a: a[0])
        return min((bound, region), key=lambda a: a[0])

    def sample(self, n: int, seed: int) -> tuple[FloatArray, FloatArray]:
        rng = np.random.default_rng(seed)
        ids = rng.integers(self.m, size=n)
        u, v = np.sqrt(rng.random(n))[:, None], rng.random(n)[:, None]
        x = u*((1-v)*self.vertices[ids]+v*self.vertices[(ids+1) % self.m])
        return x, self.values(x)


def anchors(problem: MaF, seed: int) -> tuple[FloatArray, FloatArray, list[dict[str, Any]]]:
    """Optimize all anchors; retain V1's minimum-norm tie rule for MaF9."""
    starts = [np.zeros(2), *problem.vertices,
              *np.random.default_rng(seed).uniform(-10000, 10000, (4, 2))]
    midpoints = (problem.vertices+np.roll(problem.vertices, -1, axis=0))/2
    xs, diagnostics = [], []
    for j in range(problem.m):
        initial = starts if problem.number == 8 else [
            midpoints[j], problem.vertices[j], problem.vertices[(j+1) % problem.m],
            np.zeros(2), *midpoints[np.arange(problem.m) != j]]
        valid = []
        for x0 in initial:
            if not problem.feasible(x0)[0]:
                continue
            r = minimize(lambda x, j=j: problem.evaluate(x)[j], x0,
                         jac=lambda x, j=j: problem.jacobian(x)[j], method='SLSQP',
                         bounds=[(-10000, 10000)]*2,
                         constraints=[dict(type='ineq', fun=lambda x: problem.margin(x)[0],
                                           jac=lambda x: problem.margin(x)[1])],
                         options=dict(ftol=1e-11, maxiter=100))
            diagnostics.append(dict(objective=j, success=bool(r.success), value=float(r.fun),
                                    feasible=bool(problem.feasible(r.x)[0]), iterations=int(r.nit)))
            if r.success and problem.feasible(r.x)[0] and np.isfinite(r.fun):
                valid.append(r)
        if not valid:
            raise ValueError(f'No valid individual anchor: objective {j}')
        key = ((lambda r: (0 if r.fun <= 1e-10 else 1, float(r.x@r.x), float(r.fun)))
               if problem.number == 9 else (lambda r: (float(r.fun),)))
        xs.append(min(valid, key=key).x)
    x = np.array(xs)
    return x, np.column_stack([problem.evaluate(p) for p in x]), diagnostics


def spectral_screen(problem: MaF, payoff: FloatArray, seed: int) -> dict[str, Any]:
    """V1 correlation PA and payoff difference-SVD bridge, not RSM noise PA."""
    sample_x, f = problem.sample(500, seed)
    problem.evaluations += 500
    z = (f-f.mean(axis=0))/f.std(axis=0, ddof=1)
    observed = np.linalg.eigvalsh(z.T@z/499)[::-1]
    rng = np.random.default_rng(seed)
    null = np.empty((1000, problem.m))
    for b in range(1000):
        permuted = np.column_stack([rng.permutation(z[:, j]) for j in range(problem.m)])
        null[b] = np.linalg.eigvalsh(permuted.T@permuted/499)[::-1]
    q95 = np.quantile(null, .95, axis=0, method='linear')
    rank, pattern = leading_dimension(observed > q95)
    norm = nominal_normalization(payoff, (Direction.MIN,)*problem.m)
    scaled = norm.normalize(payoff)
    singular = np.linalg.svd(vertex_differences(scaled).T, compute_uv=False)
    if not 1 <= rank <= len(singular) or singular[rank-1] <= 1e-12:
        raise ValueError('Horn rank incompatible with payoff geometry; no clamp')
    floor = singular[rank] if rank < len(singular) else 0.
    ceiling = singular[0]/singular[rank-1]
    subsets = []
    for k in (2, 3):
        for combo in combinations(range(problem.m), k):
            s = np.linalg.svd(vertex_differences(scaled[np.ix_(combo, combo)]).T,
                              compute_uv=False)
            condition = float(s[0]/s[-1]) if s[-1] > 1e-12 else None
            selected = bool(s[-1] > floor and condition is not None and condition <= ceiling)
            subsets.append(dict(indices=combo, selected=selected, singular=s,
                                condition=condition))
    return dict(rank=rank, pattern=pattern, observed=observed, q95=q95, null=null,
                sample_x=sample_x, sample_f=f, singular=singular,
                floor=float(floor), ceiling=float(ceiling), subsets=subsets)


class DirectNBIProblem:
    """Structural V2 solver adapter. Legacy sphere_* names encode MaF domain here.

    No quadratic-response stand-ins. Original RSM classes remain unchanged.
    """
    n_factors = 2
    beta = LocalNBIProblem.beta

    def __init__(self, problem: MaF, indices: Any, geometry: LocalNBIGeometry,
                 anchor_points: FloatArray) -> None:
        self.problem, self.indices, self.geometry = problem, np.array(indices), geometry
        self.anchors, self.models = anchor_points, tuple(indices)

    def normalized_values(self, point: FloatArray) -> Any:
        n = self.geometry.normalization
        return (self.problem.evaluate(point)[self.indices]-n.utopia)/n.amplitudes

    def residual(self, variables: FloatArray, weights: FloatArray) -> Any:
        return (self.normalized_values(variables[:-1])-self.geometry.vertices@weights
                -variables[-1]*self.geometry.normal)

    def equality_jacobian(self, variables: FloatArray) -> FloatArray:
        gradients = self.problem.jacobian(variables[:-1])[self.indices]
        return np.column_stack([gradients/self.geometry.normalization.amplitudes[:, None],
                                -self.geometry.normal])

    def domain(self, variables: FloatArray) -> tuple[float, FloatArray]:
        margin, gradient = self.problem.margin(variables[:-1])
        candidates = [(margin, np.r_[gradient, 0.]),
                      (10-variables[-1], np.array([0., 0., -1.])),
                      (10+variables[-1], np.array([0., 0., 1.]))]
        return min(candidates, key=lambda a: a[0])

    def sphere_margin(self, variables: FloatArray) -> float:
        return float(self.domain(variables)[0])

    def sphere_jacobian(self, variables: FloatArray) -> FloatArray:
        return self.domain(variables)[1]


def front_indices(x: FloatArray, f: FloatArray) -> NDArray[np.int64]:
    """V1 quantized decision deduplication, then V2 full-objective dominance."""
    order = np.lexsort((np.arange(len(x)), f.sum(axis=1)))
    keys, chosen = set(), []
    for i in order:
        key = tuple(np.round(x[i]/1e-5))
        if key not in keys:
            keys.add(key)
            chosen.append(int(i))
    ids = np.array(sorted(chosen), dtype=int)
    return ids[nondominated_mask(f[ids], equality_tolerance=np.full(f.shape[1], 1e-10))]


def run(number: int, m: int, seed: int) -> dict[str, Any]:
    start = perf_counter()
    problem = MaF(number, m)
    xstar, payoff, anchor_trials = anchors(problem, seed)
    pa_start = perf_counter()
    screen = spectral_screen(problem, payoff, seed)
    diagnostic_seconds = perf_counter()-pa_start
    nbi_start = perf_counter()
    xs, origins, records = [], [], []
    geometry_failures = []
    for subset in screen['subsets']:
        if not subset['selected']:
            continue
        ids = np.array(subset['indices'])
        try:
            geometry = local_nbi_geometry(payoff[np.ix_(ids, ids)], (Direction.MIN,)*len(ids))
        except ValueError as error:
            geometry_failures.append(dict(indices=ids, error=str(error)))
            continue
        adapter = DirectNBIProblem(problem, ids, geometry, xstar[ids])
        lattice = simplex_lattice(len(ids), 5)
        solved = solve_nbi_lattice(cast(LocalNBIProblem, adapter), lattice, options=OPTIONS)
        for weight, solution in enumerate(solved.solutions):
            accepted = solution.accepted and bool(problem.feasible(solution.point)[0])
            trial = solution.trials[-1]
            records.append(dict(indices=ids, weight=weight, accepted=accepted,
                                eq_l2=trial.eq_norm, margin=trial.sphere_margin,
                                attempts=len(solution.trials),
                                iterations=sum(t.iterations for t in solution.trials),
                                solver_status=trial.status))
            if accepted:
                xs.append(solution.point)
                origins.append((tuple(ids), weight))
    x = np.array(xs, dtype=float).reshape(-1, 2)
    f = problem.values(x)
    if not len(x):
        raise ValueError('No accepted feasible NBI solutions; campaign blocked')
    nd = front_indices(x, f)
    if not problem.feasible(x).all():
        raise ValueError('Infeasible candidate retained')
    return dict(X=x, F=f, nd=nd, anchors=xstar, payoff=payoff, screen=screen,
                anchor_trials=anchor_trials, subproblems=records, origins=origins,
                geometry_failures=geometry_failures, evaluations=problem.evaluations,
                gradient_calls=problem.gradient_calls, diagnostic_seconds=diagnostic_seconds,
                nbi_seconds=perf_counter()-nbi_start, seconds=perf_counter()-start)


def metrics(f: FloatArray, reference: FloatArray, seed: int) -> dict[str, float | None]:
    """Exact V1 MaF metric definitions, including population SD and one Sobol net."""
    gd, igd = gd_igd(f, reference)
    d = nearest_distances(f) if len(f) > 1 else None
    samples = qmc.Sobol(f.shape[1], scramble=True, seed=2026+seed).random_base2(13)*1.1
    hit = np.zeros(len(samples), dtype=bool)
    for i in range(0, len(samples), 1000):
        hit[i:i+1000] = np.any(np.all(samples[i:i+1000, None] >= f[None], axis=2), axis=1)
    p, volume = hit.mean(), 1.1**f.shape[1]
    return dict(GD=gd, IGD=igd, HV=float(p*volume),
                HV_se=float(volume*np.sqrt(p*(1-p)/8192)),
                Spacing=float(d.std(ddof=0)) if d is not None else None,
                Sparsity=float(d.mean()) if d is not None else None)
