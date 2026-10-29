"""Direct coordinate calibration, followed by one untouched holdout assessment."""

from dataclasses import asdict, dataclass
from numbers import Integral
from time import perf_counter
from types import SimpleNamespace

import numpy as np
from scipy.optimize import minimize  # type: ignore[import-untyped]

from .anchors import constraint_jacobian, constraints, initial_positions
from .correlation import (
    calibration_loss_gradient,
    feature_covariance,
    from_feature_covariance,
    population_correlation,
    summaries,
)
from .design import Scenario
from .domain import radius, sample_ball
from .model import FloatArray, evaluate, frozen
from .validation import certify_anchors, certify_correlation


@dataclass(frozen=True, slots=True)
class CalibrationConfig:
    master_seed: int = 20261029
    calibration_power: int = 14
    validation_power: int = 16
    n_starts: int = 8
    maxiter: int = 400
    ftol: float = 1e-10
    acceptance_tolerance: float = 0.05
    separation_ratio: float = 1e-4
    rank_rtol: float = 1e-10
    matrix_tolerance: float = 1e-10
    sampling_precision_budget: float = 0.005

    def __post_init__(self) -> None:
        integers = (
            self.master_seed,
            self.calibration_power,
            self.validation_power,
            self.n_starts,
            self.maxiter,
        )
        if any(isinstance(x, bool) or not isinstance(x, Integral) or x < 1 for x in integers):
            raise ValueError("seed,powers,starts,maxiter must be positive integers")
        if not (4 <= self.calibration_power <= 24 and 4 <= self.validation_power <= 24):
            raise ValueError("sample powers must be4..24")
        if not 0 < self.acceptance_tolerance <= 0.05:
            raise ValueError("acceptance tolerance may never exceed0.05")
        for value in (
            self.ftol,
            self.separation_ratio,
            self.rank_rtol,
            self.matrix_tolerance,
            self.sampling_precision_budget,
        ):
            if not np.isfinite(value) or value <= 0:
                raise ValueError("numerical tolerances must be finite and positive")
        if self.sampling_precision_budget > self.acceptance_tolerance / 2:
            raise ValueError(
                "sampling precision budget must be at most half the acceptance tolerance"
            )
        if self.separation_ratio >= 1 or self.rank_rtol >= 1 or self.matrix_tolerance >= 1e-4:
            raise ValueError("separation/rank/matrix tolerances are not numerically meaningful")


@dataclass(frozen=True, slots=True)
class CalibrationTrial:
    start: int
    seed: int
    strategy: str
    solver_success: bool
    solver_status: int
    message: str
    iterations: int
    evaluations: int
    gradient_evaluations: int
    elapsed_seconds: float
    calibration_rho_abs: float
    calibration_error: float
    final_solver_error: float
    anchor_rank: int
    minimum_separation: float
    maximum_norm: float
    structurally_valid: bool
    anchors: FloatArray

    def row(self) -> dict[str, object]:
        result: dict[str, object] = asdict(self)
        result.pop("anchors")
        return result


@dataclass(frozen=True, slots=True)
class CalibratedScenario:
    scenario: Scenario
    config: CalibrationConfig
    anchors: FloatArray
    calibration_matrix: FloatArray
    validation_matrix: FloatArray
    population_matrix: FloatArray
    trials: tuple[CalibrationTrial, ...]
    selected_start: int
    calibration_seed: int
    validation_seed: int
    calibration_sample_sha256: str
    validation_sample_sha256: str
    elapsed_seconds: float
    valid: bool
    failures: tuple[str, ...]


def _trial(
    scenario: Scenario,
    config: CalibrationConfig,
    covariance: FloatArray,
    start: int,
    seed: int,
) -> CalibrationTrial:
    begin = perf_counter()
    m, nx, alpha = scenario.m, scenario.nx, radius(scenario.nx)
    initial = initial_positions(scenario, start, seed).ravel()
    best = initial.copy()
    best_loss = float("inf")
    evaluations = 0

    def loss_gradient(coordinates: FloatArray) -> tuple[float, FloatArray]:
        return calibration_loss_gradient(coordinates, m, nx, alpha, covariance, scenario.rho_target)

    def objective(coordinates: FloatArray) -> float:
        nonlocal best, best_loss, evaluations
        evaluations += 1
        loss = loss_gradient(coordinates)[0]
        certificate = certify_anchors(
            coordinates.reshape(m, nx) * alpha, alpha, config.separation_ratio, config.rank_rtol
        )
        if certificate.valid and loss < best_loss:
            best, best_loss = coordinates.copy(), loss
        return loss

    objective(initial)
    try:
        result = minimize(
            objective,
            initial,
            method="SLSQP",
            jac=lambda u: loss_gradient(u)[1],
            constraints={
                "type": "ineq",
                "fun": lambda u: constraints(u, m, nx, config.separation_ratio),
                "jac": lambda u: constraint_jacobian(u, m, nx),
            },
            options={"ftol": config.ftol, "maxiter": config.maxiter, "disp": False},
        )
    except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
        result = SimpleNamespace(
            x=best,
            success=False,
            status=-1,
            message=f"{type(error).__name__}: {error}",
            nit=0,
            nfev=evaluations,
            njev=0,
        )
    final = np.asarray(result.x, dtype=np.float64)
    if np.isfinite(final).all():
        objective(final)
        final_error = float(np.sqrt(loss_gradient(final)[0]))
    else:
        final_error = float("inf")
    a = best.reshape(m, nx) * alpha
    certificate = certify_anchors(a, alpha, config.separation_ratio, config.rank_rtol)
    rho_abs = summaries(from_feature_covariance(a, covariance))[0]
    return CalibrationTrial(
        start,
        seed,
        "balanced_simplex_jitter" if start == 0 else "uniform_ball",
        bool(result.success),
        int(result.status),
        str(result.message),
        int(result.nit),
        int(result.nfev),
        int(result.njev),
        perf_counter() - begin,
        rho_abs,
        abs(rho_abs - scenario.rho_target),
        final_error,
        certificate.rank,
        certificate.minimum_separation,
        certificate.maximum_norm,
        certificate.valid,
        frozen(a),
    )


def select_trial(trials: tuple[CalibrationTrial, ...]) -> CalibrationTrial:
    """Selection has no signed-correlation or validation arguments."""
    if not trials:
        raise ValueError("at least one trial required")
    qualified = [t for t in trials if t.solver_success and t.structurally_valid]
    feasible_trials = [t for t in trials if t.structurally_valid]
    return min(
        qualified or feasible_trials or list(trials), key=lambda t: (t.calibration_error, t.start)
    )


def calibrate(scenario: Scenario, config: CalibrationConfig | None = None) -> CalibratedScenario:
    import hashlib

    config = CalibrationConfig() if config is None else config
    begin = perf_counter()
    seed_init, seed_cal, seed_val = scenario.seeds(config.master_seed)
    calibration_points = sample_ball(scenario.nx, config.calibration_power, seed_cal)
    covariance = feature_covariance(calibration_points)
    trials = tuple(
        _trial(scenario, config, covariance, start, seed_init + 100000 * start)
        for start in range(config.n_starts)
    )
    chosen = select_trial(trials)
    # Holdout is not even generated until the final candidate has been selected.
    validation_points = sample_ball(scenario.nx, config.validation_power, seed_val)
    calibration_matrix = from_feature_covariance(chosen.anchors, covariance)
    validation_matrix = np.asarray(
        np.corrcoef(evaluate(validation_points, chosen.anchors), rowvar=False), dtype=np.float64
    )
    population_matrix = population_correlation(chosen.anchors, radius(scenario.nx))
    failures = []
    if not chosen.solver_success:
        failures.append("NO_CONVERGED_CALIBRATION_TRIAL")
    if not chosen.structurally_valid:
        failures.append("INVALID_ANCHOR_CONFIGURATION")
    for label, matrix in (("CALIBRATION", calibration_matrix), ("VALIDATION", validation_matrix)):
        if abs(summaries(matrix)[0] - scenario.rho_target) > config.acceptance_tolerance:
            failures.append(label + "_TARGET_TOLERANCE_FAILED")
        if not certify_correlation(matrix, scenario.nx, config.matrix_tolerance).valid:
            failures.append(label + "_CORRELATION_MATRIX_INVALID")
        if np.max(np.abs(matrix - population_matrix)) > config.sampling_precision_budget:
            failures.append(label + "_SAMPLING_PRECISION_FAILED")
    minima = np.diag(evaluate(chosen.anchors, chosen.anchors))
    if not np.array_equal(minima, np.zeros(scenario.m)):
        failures.append("ANALYTIC_MINIMA_FAILED")
    return CalibratedScenario(
        scenario,
        config,
        chosen.anchors,
        frozen(calibration_matrix),
        frozen(validation_matrix),
        frozen(population_matrix),
        trials,
        chosen.start,
        seed_cal,
        seed_val,
        hashlib.sha256(calibration_points.tobytes()).hexdigest(),
        hashlib.sha256(validation_points.tobytes()).hexdigest(),
        perf_counter() - begin,
        not failures,
        tuple(failures),
    )
