"""Independent stratified candidates, nested references and numerical certificates."""

from dataclasses import dataclass
from itertools import combinations

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import cKDTree  # type: ignore[import-untyped]

from cnbi_v2.benchmark.metrics import gd_igd, nearest_distances
from cnbi_v2.reference.indicators import distances

from ..design import Scenario
from ..domain import radius
from ..model import FloatArray, evaluate, frozen
from .geometry import HullGeometry, hull_geometry, sample_hull_weights, seed_for
from .normalization import AnalyticalNormalization, analytic_normalization
from .selection import partial_fps, unique_indices

ORIGINS = (
    "individual_anchor",
    "interior",
    "boundary_or_subsimplex",
    "anchor_neighborhood",
    "anchor_pair_segment",
)


@dataclass(frozen=True, slots=True)
class Candidates:
    weights: FloatArray
    decisions: FloatArray
    origins: NDArray[np.int64]
    original_ids: NDArray[np.int64]
    before_identity_count: int


def candidates(cell: Scenario, geometry: HullGeometry, master: int) -> Candidates:
    m = cell.m

    def sample(role: str, power: int, boundary: bool = False) -> FloatArray:
        return sample_hull_weights(
            geometry, power, seed_for(master, cell.scenario_id, role), boundary=boundary
        )

    interior = sample("candidate_interior", 13)
    boundary = sample("candidate_boundary", 12, True)
    near = 0.02 * sample("candidate_anchor_neighborhood", 11)
    near[np.arange(len(near)), np.arange(len(near)) % m] += 0.98
    segments = []
    for left, right in combinations(range(m), 2):
        for k in range(1, 18):
            w = np.zeros(m)
            w[left], w[right] = 1 - k / 18, k / 18
            segments.append(w)
    blocks = (np.eye(m), interior, boundary, near, np.array(segments))
    weights = np.vstack(blocks)
    x = weights @ geometry.anchors
    origin = np.concatenate([np.full(len(b), i, dtype=np.int64) for i, b in enumerate(blocks)])
    ids = unique_indices(x, 1e-12 * radius(cell.nx))
    if not np.array_equal(ids[:m], np.arange(m)):
        raise ValueError("identity tolerance merges distinct frozen anchors")
    return Candidates(frozen(weights[ids]), frozen(x[ids]), origin[ids], ids, len(x))


@dataclass(frozen=True, slots=True)
class ParetoReference:
    scenario: Scenario
    geometry: HullGeometry
    normalization: AnalyticalNormalization
    decisions: FloatArray
    responses: FloatArray
    normalized: FloatArray
    weights: FloatArray
    candidate_ids: NDArray[np.int64]
    origins: NDArray[np.int64]
    pool: Candidates
    certificate: dict[str, object]


def certify_reference(
    cell: Scenario, anchors: FloatArray, x: FloatArray, weights: FloatArray, z: FloatArray
) -> dict[str, object]:
    alpha = radius(cell.nx)
    if (
        x.shape != (10000, cell.nx)
        or weights.shape != (10000, cell.m)
        or z.shape != (10000, cell.m)
        or not np.isfinite(x).all()
        or not np.isfinite(z).all()
        or np.any(z < 0)
        or np.any(weights < 0)
    ):
        raise ValueError("reference arrays are incomplete, nonfinite or invalid")
    reconstruction = float(np.max(np.linalg.norm(x - weights @ anchors, axis=1)))
    weight_sum_error = float(np.max(abs(weights.sum(axis=1) - 1)))
    if reconstruction > 1e-12 * alpha or weight_sum_error > 1e-12:
        raise ValueError("invalid convex-combination membership certificate")
    if np.max(np.linalg.norm(x, axis=1)) > alpha:
        raise ValueError("reference point outside the feasible sphere")
    if not np.array_equal(x[: cell.m], anchors) or not np.array_equal(z, evaluate(x, anchors)):
        raise ValueError("individual extremes or direct analytic responses not preserved")
    nearest = cKDTree(x).query(x, k=2, eps=0, workers=1)[0][:, 1]
    if np.any(nearest <= 1e-12 * alpha):
        raise ValueError("reference contains decision duplicates")
    # A soft dominator must lie in this small decision-space ball: weighted
    # quadratic gap = ||y-x||² + 2(y-x).(x-lambda A), within evaluation roundoff.
    nadir = analytic_normalization(anchors).nadir
    evaluation_bound = 64 * np.finfo(float).eps * max(1.0, float(z.max()))
    tau = float(nadir.max()) * 1e-12
    delta_bound = (
        reconstruction
        + alpha * weight_sum_error
        + 16 * np.finfo(float).eps * cell.m * max(1.0, alpha)
    ) / (1 - weight_sum_error)
    query_radius = float(
        np.nextafter(
            (delta_bound + np.sqrt(delta_bound**2 + tau + 2 * evaluation_bound))
            * (1 + 16 * np.finfo(float).eps),
            np.inf,
        )
    )
    pairs = cKDTree(x).query_pairs(query_radius, eps=0, output_type="ndarray")
    apparent = 0
    normalized = z / nadir
    for left, right in pairs:
        diff = normalized[left] - normalized[right]
        apparent += int(
            (np.all(diff <= 1e-12) and np.any(diff < -1e-12))
            or (np.all(diff >= -1e-12) and np.any(diff > 1e-12))
        )
    # Preserve analytically efficient points even if a float/tolerance diagnostic is ambiguous.
    return dict(
        status="CERTIFIED" if apparent == 0 else "CERTIFIED_WITH_NUMERICAL_DIAGNOSTICS",
        count=10000,
        primary_count=5000,
        barycentric_reconstruction_max=reconstruction,
        weight_sum_error_max=weight_sum_error,
        maximum_norm=float(np.linalg.norm(x, axis=1).max()),
        minimum_decision_separation=float(nearest.min()),
        individual_extremes_preserved=cell.m,
        analytic_pareto_membership=True,
        numerical_dominance_query_radius=float(query_radius),
        potential_dominance_pairs=len(pairs),
        apparent_tolerance_dominance_pairs=apparent,
        evaluation_roundoff_bound=evaluation_bound,
        barycentric_roundoff_adjusted_error_bound=float(delta_bound),
        no_points_discarded_for_apparent_dominance=True,
    )


def generate_reference(cell: Scenario, anchors: FloatArray, master: int) -> ParetoReference:
    if anchors.shape != (cell.m, cell.nx):
        raise ValueError("anchors do not match structural scenario")
    geometry = hull_geometry(anchors)
    normalization = analytic_normalization(anchors)
    pool = candidates(cell, geometry, master)
    truth = evaluate(pool.decisions, anchors)
    normalized = normalization.transform(truth)
    order = partial_fps(normalized, 10000, np.arange(cell.m))
    x, z, w = pool.decisions[order], truth[order], pool.weights[order]
    certificate = certify_reference(cell, anchors, x, w, z)
    return ParetoReference(
        cell,
        geometry,
        normalization,
        frozen(x),
        frozen(z),
        frozen(normalized[order]),
        frozen(w),
        pool.original_ids[order],
        pool.origins[order],
        pool,
        certificate,
    )


def sensitivity(
    reference: ParetoReference, master: int
) -> tuple[list[dict[str, object]], dict[str, FloatArray]]:
    cell, geometry = reference.scenario, reference.geometry
    probe_w = sample_hull_weights(
        geometry, 12, seed_for(master, cell.scenario_id, "independent_probe")
    )
    boundary_w = sample_hull_weights(
        geometry,
        10,
        seed_for(master, cell.scenario_id, "independent_boundary_probe"),
        boundary=True,
    )
    probe_x, boundary_x = probe_w @ geometry.anchors, boundary_w @ geometry.anchors
    probe = reference.normalization.transform(evaluate(probe_x, geometry.anchors))
    boundary = reference.normalization.transform(evaluate(boundary_x, geometry.anchors))
    rows = []
    for count in (2500, 5000, 10000):
        z, x = reference.normalized[:count], reference.decisions[:count]
        cover = distances(probe, z)
        boundary_cover = distances(boundary, z)
        to_dense = distances(z, reference.normalized)
        from_dense = distances(reference.normalized, z)
        nearest = nearest_distances(z)
        gd, igd = gd_igd(z, reference.normalized)
        if len(geometry.equations):
            slack = -(x @ geometry.equations[:, :-1].T + geometry.equations[:, -1])
            on_boundary = int(np.sum(slack.min(axis=1) <= 1e-10 * radius(cell.nx)))
        else:
            on_boundary = None
        row: dict[str, object] = dict(
            scenario_id=cell.scenario_id,
            nx=cell.nx,
            delta=cell.delta,
            rho_target=cell.rho_target,
            m=cell.m,
            count=count,
            probe_count=len(probe),
            boundary_probe_count=len(boundary),
            probe_mean=float(cover.mean()),
            probe_q95=float(np.quantile(cover, 0.95)),
            probe_max=float(cover.max()),
            probe_rms_coordinate_max=float(cover.max() / np.sqrt(cell.m)),
            boundary_probe_mean=float(boundary_cover.mean()),
            boundary_probe_max=float(boundary_cover.max()),
            directed_to_dense_max=float(to_dense.max()),
            directed_from_dense_max=float(from_dense.max()),
            discrete_hausdorff=float(max(to_dense.max(), from_dense.max())),
            hausdorff_rms_coordinate=float(max(to_dense.max(), from_dense.max()) / np.sqrt(cell.m)),
            gd_to_dense=gd,
            igd_from_dense=igd,
            nn_min=float(nearest.min()),
            nn_mean=float(nearest.mean()),
            nn_q95=float(np.quantile(nearest, 0.95)),
            nn_max=float(nearest.max()),
            boundary_count=on_boundary,
            geometry_condition=geometry.condition,
            geometry_method=geometry.method,
        )
        for k, name in enumerate(ORIGINS):
            row["origin_" + name] = int(np.sum(reference.origins[:count] == k))
        radial = np.linalg.norm(x - geometry.anchors.mean(axis=0), axis=1)
        radius_from_center = np.linalg.norm(
            geometry.anchors - geometry.anchors.mean(axis=0), axis=1
        ).max()
        shells = np.searchsorted([0.2, 0.4, 0.6, 0.8], radial / radius_from_center, side="right")
        for k in range(5):
            row[f"centroid_radial_shell_{k}"] = int(np.sum(shells == k))
        rows.append(row)
    return rows, dict(
        probe_decisions=probe_x,
        probe_weights=probe_w,
        boundary_probe_decisions=boundary_x,
        boundary_probe_weights=boundary_w,
    )
