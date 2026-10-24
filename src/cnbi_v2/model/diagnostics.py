"""Per-response diagnostics for full quadratic OLS models including an intercept.

See docs/mathematics/rsm_diagnostics.md for hypotheses and undefined cases.
Inputs and fitted models are preserved; no term selection is performed.
"""

from collections.abc import Sequence
from dataclasses import dataclass, fields
from enum import StrEnum

import numpy as np
from numpy.typing import ArrayLike
from scipy.stats import f as f_distribution  # type: ignore[import-untyped]

from .multivariate_rsm import RSMFit
from .quadratic_design import FloatArray, _as_finite_real, quadratic_design


class DiagnosticStatus(StrEnum):
    """Reason a statistic is available or explicitly undefined."""

    OK = "OK"
    CONSTANT_RESPONSE = "CONSTANT_RESPONSE"
    PRESS_LEVERAGE_NEAR_ONE = "PRESS_LEVERAGE_NEAR_ONE"
    ZERO_ERROR_MEAN_SQUARE = "ZERO_ERROR_MEAN_SQUARE"
    NEGATIVE_MODEL_SS = "NEGATIVE_MODEL_SS"
    NO_REPLICATES = "NO_REPLICATES"
    NO_LACK_OF_FIT_DF = "NO_LACK_OF_FIT_DF"
    ZERO_PURE_ERROR = "ZERO_PURE_ERROR"


@dataclass(frozen=True, slots=True)
class ResponseDiagnostics:
    """Scalar diagnostics in canonical response units; R-squared is a fraction."""

    response_name: str
    sse: float
    sst: float
    ssr: float
    mse: float
    s: float
    r_squared: float | None
    adjusted_r_squared: float | None
    press: float | None
    predicted_r_squared: float | None
    model_df: int
    error_df: int
    model_ms: float
    error_ms: float
    model_f: float | None
    model_p_value: float | None
    pure_error_ss: float
    pure_error_df: int
    lack_of_fit_ss: float
    lack_of_fit_df: int
    lack_of_fit_ms: float | None
    pure_error_ms: float | None
    lack_of_fit_f: float | None
    lack_of_fit_p_value: float | None
    r_squared_status: DiagnosticStatus
    press_status: DiagnosticStatus
    model_status: DiagnosticStatus
    lack_of_fit_status: DiagnosticStatus

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, float) and not np.isfinite(value):
                raise FloatingPointError(f"nonfinite computed diagnostic: {field.name}")


def _immutable(values: FloatArray) -> FloatArray:
    return np.frombuffer(values.tobytes(), dtype=np.float64).reshape(values.shape)


@dataclass(frozen=True, slots=True)
class RSMDiagnostics:
    """Diagnostics share leverages and exact factor groups across responses.

    Group and undefined-row indices are zero-based in the original fit order.
    press_residuals is (n,m), or None if any training leverage is near one.
    """

    responses: tuple[ResponseDiagnostics, ...]
    hat_diagonal: FloatArray
    press_residuals: FloatArray | None
    factor_groups: tuple[tuple[int, ...], ...]
    press_undefined_rows: tuple[int, ...]
    leverage_tolerance: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "hat_diagonal", _immutable(self.hat_diagonal))
        if self.press_residuals is not None:
            object.__setattr__(self, "press_residuals", _immutable(self.press_residuals))

    @property
    def replicate_groups(self) -> tuple[tuple[int, ...], ...]:
        return tuple(group for group in self.factor_groups if len(group) > 1)


def factor_configuration_groups(factors: ArrayLike) -> tuple[tuple[int, ...], ...]:
    """Group exactly equal float64 factor rows, in first-occurrence order.

    No tolerance, rounding, coding, or scaling is applied. Signed zeros compare
    equal; finite near-neighbours remain distinct. Includes singleton groups.
    """
    values = _as_finite_real(factors, "factors")
    if values.ndim != 2 or min(values.shape) == 0:
        raise ValueError("factors must have nonempty shape (n_observations, n_factors)")
    groups: dict[tuple[float, ...], list[int]] = {}
    for i, row in enumerate(values):
        groups.setdefault(tuple(float(v) for v in row), []).append(i)
    return tuple(tuple(group) for group in groups.values())


def _training_leverages(design: FloatArray, rank: int) -> tuple[FloatArray, float]:
    # H=QQ.T: only the squared row norms are needed, not the n*n matrix.
    q, _ = np.linalg.qr(design, mode="reduced")
    diagonal = np.sum(q * q, axis=1)
    tolerance = float(np.finfo(float).eps * max(design.shape))
    if (
        not np.isfinite(diagonal).all()
        or np.any(diagonal < -tolerance)
        or np.any(diagonal > 1 + tolerance)
        or abs(float(np.sum(diagonal)) - rank) > rank * tolerance
    ):
        raise np.linalg.LinAlgError("training leverages violate OLS bounds or trace identity")
    return diagonal, tolerance


def _f_test(numerator_ms: float, denominator_ms: float, df1: int, df2: int) -> tuple[float, float]:
    statistic = numerator_ms / denominator_ms
    p_value = float(f_distribution.sf(statistic, df1, df2))
    if not np.isfinite(statistic) or not np.isfinite(p_value):
        raise FloatingPointError("F statistic or survival probability is nonfinite")
    return statistic, p_value


def _response_diagnostics(
    result: RSMFit,
    j: int,
    name: str,
    groups: tuple[tuple[int, ...], ...],
    press_residuals: FloatArray | None,
) -> ResponseDiagnostics:
    observed = result.observed_responses[:, j]
    residuals = result.residuals[:, j]
    # Shifting before centering avoids cancellation for large offsets and makes
    # exactly constant stored observations yield exactly SST=0 (even for 0.1).
    shifted = observed - observed[0]
    centered = shifted - np.mean(shifted)
    sse = float(residuals @ residuals)
    sst = float(centered @ centered)
    ssr = sst - sse
    nu = result.residual_degrees_of_freedom
    mse = float(result.mse_by_response[j])
    model_df = result.rank - 1
    model_ms = ssr / model_df
    r_squared = adjusted = predicted = None
    r_status = DiagnosticStatus.CONSTANT_RESPONSE
    press = (
        None if press_residuals is None
        else float(press_residuals[:, j] @ press_residuals[:, j])
    )
    press_status = (
        DiagnosticStatus.PRESS_LEVERAGE_NEAR_ONE
        if press is None else DiagnosticStatus.OK
    )
    if sst > 0:
        r_status = DiagnosticStatus.OK
        r_squared = 1 - sse / sst
        adjusted = 1 - mse / (sst / (result.n_observations - 1))
        if press is not None:
            predicted = 1 - press / sst

    model_f = model_p = None
    if sst == 0:
        model_status = DiagnosticStatus.CONSTANT_RESPONSE
    elif mse == 0:
        model_status = DiagnosticStatus.ZERO_ERROR_MEAN_SQUARE
    elif ssr < 0:
        model_status = DiagnosticStatus.NEGATIVE_MODEL_SS
    else:
        model_status = DiagnosticStatus.OK
        model_f, model_p = _f_test(model_ms, mse, model_df, nu)

    pure_error_ss = lack_of_fit_ss = 0.0
    for group in groups:
        indices = list(group)
        values = observed[indices]
        offsets = values - values[0]
        mean_offset = float(np.mean(offsets))
        deviations = offsets - mean_offset
        pure_error_ss += float(deviations @ deviations)
        # Algebraically SSE-SS_PE, without subtracting two nearly equal sums.
        mean_residual = float(values[0] - result.fitted_values[group[0], j]) + mean_offset
        lack_of_fit_ss += len(group) * mean_residual**2
    pure_error_df = result.n_observations - len(groups)
    lof_df = nu - pure_error_df
    pure_error_ms = pure_error_ss / pure_error_df if pure_error_df > 0 else None
    lof_ms = lack_of_fit_ss / lof_df if lof_df > 0 else None
    lof_f = lof_p = None
    if pure_error_df == 0:
        lof_status = DiagnosticStatus.NO_REPLICATES
    elif lof_df == 0:
        lof_status = DiagnosticStatus.NO_LACK_OF_FIT_DF
    elif pure_error_ss == 0:
        lof_status = DiagnosticStatus.ZERO_PURE_ERROR
    else:
        lof_status = DiagnosticStatus.OK
        # Both MS are defined and the denominator is positive in this branch.
        assert lof_ms is not None and pure_error_ms is not None
        lof_f, lof_p = _f_test(lof_ms, pure_error_ms, lof_df, pure_error_df)

    return ResponseDiagnostics(
        response_name=name, sse=sse, sst=sst, ssr=ssr, mse=mse, s=float(np.sqrt(mse)),
        r_squared=r_squared, adjusted_r_squared=adjusted, press=press,
        predicted_r_squared=predicted, model_df=model_df, error_df=nu,
        model_ms=model_ms, error_ms=mse, model_f=model_f, model_p_value=model_p,
        pure_error_ss=pure_error_ss, pure_error_df=pure_error_df,
        lack_of_fit_ss=lack_of_fit_ss, lack_of_fit_df=lof_df,
        lack_of_fit_ms=lof_ms, pure_error_ms=pure_error_ms,
        lack_of_fit_f=lof_f, lack_of_fit_p_value=lof_p,
        r_squared_status=r_status, press_status=press_status,
        model_status=model_status, lack_of_fit_status=lof_status,
    )


def diagnose_rsm(
    result: RSMFit,
    factors: ArrayLike,
    response_names: Sequence[str] | None = None,
) -> RSMDiagnostics:
    """Diagnose each response, using the exact factors/row order of the fit.

    RSMFit includes an intercept, full column rank and positive error df.
    No automatic recoding is allowed. Undefined statistics are None with a
    DiagnosticStatus; computed nonfinite numbers raise FloatingPointError.
    """
    values = _as_finite_real(factors, "factors")
    if not np.array_equal(values, result.experimental_factors):
        raise ValueError("diagnostic factors must equal the fitted factors in the same row order")
    names = (
        tuple(f"response_{j}" for j in range(result.n_responses))
        if response_names is None else tuple(response_names)
    )
    if (
        len(names) != result.n_responses
        or any(not isinstance(name, str) or not name.strip() for name in names)
        or len(set(names)) != len(names)
    ):
        raise ValueError("response_names must contain one unique nonempty string per response")
    groups = factor_configuration_groups(values)
    diagonal, tolerance = _training_leverages(quadratic_design(values), result.rank)
    undefined_rows = tuple(int(i) for i in np.flatnonzero(1 - diagonal <= tolerance))
    with np.errstate(over="raise", invalid="raise", divide="raise", under="ignore"):
        press_residuals = None if undefined_rows else result.residuals / (1 - diagonal[:, None])
        responses = tuple(
            _response_diagnostics(result, j, name, groups, press_residuals)
            for j, name in enumerate(names)
        )
    return RSMDiagnostics(responses, diagonal, press_residuals, groups, undefined_rows, tolerance)
