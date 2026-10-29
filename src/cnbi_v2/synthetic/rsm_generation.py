"""Synthetic experiments fitted only through the validated Phase1 RSM APIs."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.model import (
    RSMDiagnostics,
    RSMFit,
    diagnose_rsm,
    fit_multivariate_rsm,
    quadratic_design,
    quadratic_term_names,
)

from .ccd import CCD, full_ccd
from .design import Scenario
from .model import FloatArray, evaluate, frozen, real_array
from .noise import experimental_noise, noise_variance, stream_seed


def true_coefficients(anchors: ArrayLike) -> FloatArray:
    """Independent analytic expansion, not an OLS fit or reconstruction of Y."""
    a = real_array(anchors, "anchors")
    if a.ndim != 2 or min(a.shape) < 1:
        raise ValueError("anchors must be a nonempty matrix")
    m, nx = a.shape
    result = np.zeros((len(quadratic_term_names(nx)), m))
    result[0] = np.sum(a * a, axis=1)
    result[1 : 1 + nx] = -2 * a.T
    result[1 + nx : 1 + 2 * nx] = 1.0
    return result


def certify_noiseless(scenario: Scenario, anchors: ArrayLike) -> dict[str, object]:
    a = _anchors(scenario, anchors)
    x = full_ccd(scenario.nx).points
    truth = evaluate(x, a)
    expected = true_coefficients(a)
    fit = fit_multivariate_rsm(x, truth)
    # Forward-error certification, frozen before noise draws; not a fit-quality gate.
    tolerance = (
        100
        * np.finfo(float).eps
        * fit.design_condition_number
        * max(1.0, float(np.max(abs(expected))))
    )
    error = float(np.max(abs(fit.coefficients - expected)))
    prediction_error = float(np.max(abs(quadratic_design(x) @ expected - truth)))
    if max(error, prediction_error) > tolerance:
        raise ValueError(f"noise-free certification failed for {scenario.scenario_id}")
    return dict(
        scenario_id=scenario.scenario_id,
        max_coefficient_error=error,
        max_prediction_error=prediction_error,
        tolerance=tolerance,
        status="CERTIFIED",
    )


def _anchors(scenario: Scenario, anchors: ArrayLike) -> FloatArray:
    a = real_array(anchors, "anchors")
    if a.shape != (scenario.m, scenario.nx):
        raise ValueError("anchors shape does not match the structural scenario")
    return a


@dataclass(frozen=True, slots=True)
class RSMInstance:
    scenario: Scenario
    replica_id: int
    seed: int
    ccd: CCD
    truth: FloatArray
    noise: FloatArray
    observed: FloatArray
    sigma_squared: FloatArray
    fit: RSMFit
    diagnostics: RSMDiagnostics

    @property
    def instance_id(self) -> str:
        return f"{self.scenario.scenario_id}__replica{self.replica_id}"


def generate_instance(
    scenario: Scenario, anchors: ArrayLike, replica_id: int, master_seed: int
) -> RSMInstance:
    if replica_id not in (1, 2, 3, 4, 5) or isinstance(replica_id, bool):
        raise ValueError("experimental replica must be 1..5")
    seed = stream_seed(master_seed, scenario.scenario_id, replica_id)
    a = _anchors(scenario, anchors)
    ccd = full_ccd(scenario.nx)
    truth = evaluate(ccd.points, a)
    noise = experimental_noise(truth, seed)
    observed = truth + noise
    fit = fit_multivariate_rsm(ccd.points, observed)
    diagnostics = diagnose_rsm(fit, ccd.points, [f"y{j + 1}" for j in range(scenario.m)])
    return RSMInstance(
        scenario,
        int(replica_id),
        seed,
        ccd,
        frozen(truth),
        frozen(noise),
        frozen(observed),
        frozen(noise_variance(truth)),
        fit,
        diagnostics,
    )


def validate_instances(instances: tuple[RSMInstance, ...]) -> None:
    ids = [i.instance_id for i in instances]
    seeds = [i.seed for i in instances]
    if not instances or len(set(ids)) != len(ids) or len(set(seeds)) != len(seeds):
        raise ValueError("nonempty instances with unique identifiers and seeds required")
