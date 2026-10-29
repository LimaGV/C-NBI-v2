"""Lossless archives and an oracle-free prediction interface requiring no refit."""

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.model import quadratic_design, quadratic_term_names

from ..correlation import summaries
from ..model import FloatArray, frozen, real_array
from .rsm_generation import RSMInstance, true_coefficients, validate_instances
from .rsm_inputs import array_sha256, sha256_file
from .rsm_validation import (
    ExternalSample,
    covariance_diagnostics,
    external_metrics,
    hessian_eigenvalues,
)


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot export an empty table")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: format(v, ".17g") if isinstance(v, float) else v for k, v in row.items()}
            )


@dataclass(frozen=True, slots=True)
class StoredRSM:
    """Only the noisy fitted polynomial is exposed to future optimizers."""

    instance_id: str
    nx: int
    coefficients: FloatArray

    def predict(self, points: ArrayLike) -> FloatArray:
        x = real_array(points, "prediction points")
        if x.ndim != 2 or x.shape[1] != self.nx:
            raise ValueError("prediction points must have shape (n,nx)")
        return quadratic_design(x) @ self.coefficients


def write_models(directory: Path, instances: tuple[RSMInstance, ...]) -> None:
    validate_instances(instances)
    arrays = {}
    index = []
    for item in instances:
        key = item.instance_id
        arrays[key + "__coefficients"] = item.fit.coefficients
        arrays[key + "__xtx_covariance_factor"] = item.fit.xtx_covariance_factor
        arrays[key + "__design_r_factor"] = item.fit.design_r_factor
        index.append(
            dict(
                instance_id=key,
                scenario_id=item.scenario.scenario_id,
                replica_id=item.replica_id,
                nx=item.scenario.nx,
                m=item.scenario.m,
                term_names=list(item.fit.term_names),
                coefficients_sha256=array_sha256(item.fit.coefficients),
            )
        )
    target = directory / "synthetic_rsm_models.npz"
    np.savez_compressed(target, allow_pickle=False, **arrays)
    write_json(
        directory / "models_index.json",
        dict(
            schema_version=1,
            models_sha256=sha256_file(target),
            models=index,
            interface="noisy RSM only; no truth oracle; no refit; all directions MIN",
        ),
    )


def load_models(directory: Path) -> dict[str, StoredRSM]:
    """Validate identifiers, metadata, shapes and bytes; never call OLS or oracle."""
    index = json.loads((directory / "models_index.json").read_text(encoding="utf-8"))
    target = directory / "synthetic_rsm_models.npz"
    if index["schema_version"] != 1 or index["models_sha256"] != sha256_file(target):
        raise ValueError("model archive schema or checksum mismatch")
    models = {}
    expected_keys: set[str] = set()
    with np.load(target, allow_pickle=False) as arrays:
        for row in index["models"]:
            key = row["instance_id"]
            nx, m = row["nx"], row["m"]
            if (
                not key
                or key in models
                or nx not in (2, 3, 5)
                or m < 1
                or row["replica_id"] not in (1, 2, 3, 4, 5)
                or key != f"{row['scenario_id']}__replica{row['replica_id']}"
                or row["term_names"] != list(quadratic_term_names(nx))
            ):
                raise ValueError("missing, duplicate or invalid model identification")
            coefficients = frozen(arrays[key + "__coefficients"])
            p = len(quadratic_term_names(nx))
            if (
                coefficients.shape != (p, m)
                or array_sha256(coefficients) != row["coefficients_sha256"]
                or arrays[key + "__xtx_covariance_factor"].shape != (p, p)
                or arrays[key + "__design_r_factor"].shape != (p, p)
            ):
                raise ValueError("invalid model shape or coefficient checksum")
            models[key] = StoredRSM(key, nx, coefficients)
            expected_keys.update(
                key + suffix
                for suffix in ("__coefficients", "__xtx_covariance_factor", "__design_r_factor")
            )
        if not models or set(arrays.files) != expected_keys:
            raise ValueError("empty or incomplete model archive")
    return models


def export_tables(
    directory: Path,
    instances: tuple[RSMInstance, ...],
    anchors: dict[str, FloatArray],
    external: dict[str, ExternalSample],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Export every replica and response, including unfavorable diagnostics."""
    validate_instances(instances)
    tables: dict[str, list[dict[str, object]]] = {
        k: []
        for k in (
            "ccd_designs",
            "rsm_instances",
            "observations",
            "noise_parameters",
            "rsm_coefficients",
            "true_coefficients",
            "coefficient_errors",
            "rsm_diagnostics",
            "external_validation",
        )
    }
    experimental: dict[str, FloatArray] = {}
    covariances: dict[str, FloatArray] = {}
    holdout: dict[str, FloatArray] = {}
    seen_dimensions = set()
    seen_cases = set()
    for item in instances:
        cell, key = item.scenario, item.instance_id
        sid, nx, m = cell.scenario_id, cell.nx, cell.m
        base = dict(
            scenario_id=sid,
            replica_id=item.replica_id,
            instance_id=key,
            nx=nx,
            delta=cell.delta,
            rho_target=cell.rho_target,
        )
        ccd, fit = item.ccd, item.fit
        expected = true_coefficients(anchors[sid])
        difference = fit.coefficients - expected
        eig = hessian_eigenvalues(fit.coefficients, nx)
        sample = external[sid]
        metrics = external_metrics(fit.predict(sample.points), sample.truth)
        true_corr, noisy_corr = (
            np.corrcoef(item.truth, rowvar=False),
            np.corrcoef(item.observed, rowvar=False),
        )
        tables["rsm_instances"].append(
            dict(
                **base,
                m=m,
                n=len(ccd.points),
                p=fit.n_terms,
                seed=str(item.seed),
                external_seed=str(sample.seed),
                design_rank=fit.rank,
                design_condition=fit.design_condition_number,
                residual_df=fit.residual_degrees_of_freedom,
                negative_observations=int(np.sum(item.observed < 0)),
                true_ccd_rho_abs=summaries(true_corr)[0],
                noisy_ccd_rho_abs=summaries(noisy_corr)[0],
                true_ccd_rho_signed=summaries(true_corr)[1],
                noisy_ccd_rho_signed=summaries(noisy_corr)[1],
                **covariance_diagnostics(item),
                noise_sha256=array_sha256(item.noise),
                observations_sha256=array_sha256(item.observed),
                coefficients_sha256=array_sha256(fit.coefficients),
                status="FITTED_RETAINED",
            )
        )
        for suffix, values in {
            "truth": item.truth,
            "noise": item.noise,
            "observed": item.observed,
            "fitted": fit.fitted_values,
            "residuals": fit.residuals,
            "hat_diagonal": item.diagnostics.hat_diagonal,
            "true_correlation": true_corr,
            "noisy_correlation": noisy_corr,
        }.items():
            experimental[key + "__" + suffix] = np.asarray(values, dtype=np.float64)
        if item.diagnostics.press_residuals is not None:
            experimental[key + "__press_residuals"] = item.diagnostics.press_residuals
        covariances[key + "__covariance"] = fit.residual_covariance
        covariances[key + "__eigenvalues"] = np.linalg.eigvalsh(fit.residual_covariance)
        if nx not in seen_dimensions:
            experimental[f"nx{nx}__ccd"] = ccd.points
            for i, point in enumerate(ccd.points):
                tables["ccd_designs"].append(
                    dict(
                        nx=nx,
                        design_point_id=i + 1,
                        point_type=ccd.kinds[i],
                        alpha=ccd.alpha,
                        inside_optimization_ball=ccd.inside_ball[i],
                        **{f"x{k + 1}": float(point[k]) if k < nx else None for k in range(5)},
                    )
                )
            seen_dimensions.add(nx)
        if sid not in seen_cases:
            holdout[sid + "__points"], holdout[sid + "__truth"] = sample.points, sample.truth
            for t, term in enumerate(fit.term_names):
                for j in range(m):
                    tables["true_coefficients"].append(
                        dict(
                            scenario_id=sid,
                            response_id=f"y{j + 1}",
                            term_id=t,
                            term=term,
                            coefficient=float(expected[t, j]),
                        )
                    )
            seen_cases.add(sid)
        for j, diagnostic in enumerate(item.diagnostics.responses):
            response = dict(**base, response_id=f"y{j + 1}")
            tables["noise_parameters"].append(
                dict(
                    **response,
                    signal_variance=float(np.var(item.truth[:, j], ddof=1)),
                    noise_variance=float(item.sigma_squared[j]),
                    sigma=float(np.sqrt(item.sigma_squared[j])),
                    expected_signal_fraction=0.95,
                    seed=str(item.seed),
                    realized_noise_mean=float(item.noise[:, j].mean()),
                    realized_noise_variance=float(np.var(item.noise[:, j], ddof=1)),
                    observed_response_variance=float(np.var(item.observed[:, j], ddof=1)),
                )
            )
            norm_error = float(np.linalg.norm(difference[:, j]))
            norm_true = float(np.linalg.norm(expected[:, j]))
            tables["rsm_diagnostics"].append(
                dict(
                    **base,
                    **asdict(diagnostic),
                    response_id=f"y{j + 1}",
                    design_rank=fit.rank,
                    design_condition=fit.design_condition_number,
                    coefficient_error_l2=norm_error,
                    coefficient_error_relative_l2=norm_error / norm_true,
                    zero_true_coefficient_abs_max=float(
                        np.max(abs(difference[expected[:, j] == 0, j]))
                    ),
                    hessian_min_eigenvalue=float(eig[j, 0]),
                    hessian_classification="STRICTLY_CONVEX"
                    if eig[j, 0] > 0
                    else "NOT_STRICTLY_CONVEX",
                )
            )
            tables["external_validation"].append(
                dict(
                    **response,
                    n_test=len(sample.points),
                    external_seed=str(sample.seed),
                    rmse=float(metrics[j, 0]),
                    mae=float(metrics[j, 1]),
                    r_squared_external=float(metrics[j, 2]),
                    max_absolute_error=float(metrics[j, 3]),
                    sample_sha256=array_sha256(sample.points),
                )
            )
            for i in range(fit.n_observations):
                tables["observations"].append(
                    dict(
                        **response,
                        design_point_id=i + 1,
                        truth=float(item.truth[i, j]),
                        noise=float(item.noise[i, j]),
                        observed=float(item.observed[i, j]),
                    )
                )
            for t, term in enumerate(fit.term_names):
                b, e, d = (
                    float(expected[t, j]),
                    float(fit.coefficients[t, j]),
                    float(difference[t, j]),
                )
                tables["rsm_coefficients"].append(
                    dict(**response, term_id=t, term=term, coefficient=e)
                )
                tables["coefficient_errors"].append(
                    dict(
                        **response,
                        term_id=t,
                        term=term,
                        true_coefficient=b,
                        estimated_coefficient=e,
                        difference=d,
                        absolute_error=abs(d),
                        relative_error=d / abs(b) if abs(b) > 1e-12 * norm_true else None,
                        relative_error_status="DEFINED_NONZERO_TRUE"
                        if abs(b) > 1e-12 * norm_true
                        else "ZERO_OR_NEAR_ZERO_TRUE_COEFFICIENT",
                    )
                )
    for name, rows in tables.items():
        write_csv(directory / f"synthetic_{name}.csv", rows)
    np.savez_compressed(
        directory / "synthetic_experimental_arrays.npz", allow_pickle=False, **experimental
    )
    np.savez_compressed(
        directory / "synthetic_residual_covariance.npz", allow_pickle=False, **covariances
    )
    np.savez_compressed(directory / "synthetic_external_sample.npz", allow_pickle=False, **holdout)
    write_models(directory, instances)
    return tables["rsm_diagnostics"], tables["external_validation"]
