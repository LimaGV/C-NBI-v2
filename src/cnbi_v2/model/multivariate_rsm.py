"""Full-rank quadratic OLS and raw residual covariance estimates."""

from dataclasses import dataclass, fields

import numpy as np
from numpy.typing import ArrayLike

from .quadratic_design import (
    FloatArray,
    _as_finite_real,
    quadratic_design,
    quadratic_term_names,
)


def _check_symmetric_psd(matrix: FloatArray, name: str) -> None:
    """Diagnose violations beyond roundoff; never modify or regularize a matrix."""
    if not np.isfinite(matrix).all():
        raise FloatingPointError(f"{name} contains nonfinite computed values")
    scale = float(np.max(np.abs(matrix)))
    if scale == 0:
        return
    # Scale only the diagnostic copy, so the norm and eigenvalue check cannot
    # overflow for a finite covariance with very large response units.
    diagnostic = matrix / scale
    tolerance = np.finfo(np.float64).eps * matrix.shape[0] * np.linalg.norm(diagnostic, ord=np.inf)
    if np.max(np.abs(diagnostic - diagnostic.T)) > tolerance:
        raise np.linalg.LinAlgError(f"{name} is not numerically symmetric")
    if np.linalg.eigvalsh(diagnostic)[0] < -tolerance:
        raise np.linalg.LinAlgError(f"{name} is not numerically positive semidefinite")


@dataclass(frozen=True, slots=True)
class RSMFit:
    """Estimated quantities from fit_multivariate_rsm, with immutable arrays.

    Response axes are retained for m=1. V_X is xtx_covariance_factor;
    design_r_factor is the reduced-QR upper triangular R used for leverage.
    """

    coefficients: FloatArray
    fitted_values: FloatArray
    residuals: FloatArray
    mse_by_response: FloatArray
    residual_covariance: FloatArray
    xtx_covariance_factor: FloatArray
    design_r_factor: FloatArray
    rank: int
    residual_degrees_of_freedom: int
    n_observations: int
    n_factors: int
    n_responses: int
    n_terms: int
    term_names: tuple[str, ...]
    rank_relative_tolerance: float
    design_condition_number: float

    def __post_init__(self) -> None:
        # Bytes-backed copies cannot be made writeable again via setflags.
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, np.ndarray):
                immutable = np.frombuffer(value.tobytes(), dtype=np.float64).reshape(value.shape)
                object.__setattr__(self, field.name, immutable)

    def predict(self, factors: ArrayLike) -> FloatArray:
        """Predict a mean for one point (n_x,) or many points (q,n_x)."""
        values = _as_finite_real(factors, "prediction factors")
        single_point = values.ndim == 1
        if single_point:
            values = values.reshape(1, -1)
        design = quadratic_design(values)
        if values.shape[1] != self.n_factors:
            raise ValueError(f"prediction factors must have {self.n_factors} columns")
        with np.errstate(over="raise", invalid="raise"):
            predicted = design @ self.coefficients
        return predicted[0] if single_point else predicted


def fit_multivariate_rsm(factors: ArrayLike, responses: ArrayLike) -> RSMFit:
    """Fit Y=XB+E by stable least squares, rejecting nonidentifiable models.

    A vector Y is promoted to (n,1); other results retain their response axis.
    Raw residual covariance is E_hat.T @ E_hat / (n-rank(X)).
    No raw-file access, implicit factor coding, or coefficient sampling occurs.
    """
    design = quadratic_design(factors)
    observed = _as_finite_real(responses, "responses")
    if observed.ndim == 1:
        observed = observed.reshape(-1, 1)
    if observed.ndim != 2 or observed.shape[0] != design.shape[0] or observed.shape[1] == 0:
        raise ValueError("responses must have shape (n_observations, n_responses) or (n,)")
    n_observations, n_terms = design.shape
    n_factors = np.asarray(factors).shape[1]
    rank_relative_tolerance = float(np.finfo(np.float64).eps * max(design.shape))
    coefficients, _, rank, singular_values = np.linalg.lstsq(
        design, observed, rcond=rank_relative_tolerance
    )
    if rank < n_terms:
        raise ValueError(f"rank deficient quadratic design: rank={rank}, terms={n_terms}")
    residual_df = n_observations - int(rank)
    if residual_df <= 0:
        raise ValueError("positive residual degrees of freedom are required to estimate covariance")

    _, upper = np.linalg.qr(design, mode="reduced")
    solved_identity = np.linalg.solve(upper, np.eye(n_terms))
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        fitted_values = design @ coefficients
        residuals = observed - fitted_values
        residual_covariance = (residuals.T @ residuals) / residual_df
        xtx_covariance_factor = solved_identity @ solved_identity.T
    _check_symmetric_psd(residual_covariance, "residual_covariance")
    _check_symmetric_psd(xtx_covariance_factor, "xtx_covariance_factor")
    return RSMFit(
        coefficients=coefficients,
        fitted_values=fitted_values,
        residuals=residuals,
        mse_by_response=np.diag(residual_covariance).copy(),
        residual_covariance=residual_covariance,
        xtx_covariance_factor=xtx_covariance_factor,
        design_r_factor=upper,
        rank=int(rank),
        residual_degrees_of_freedom=residual_df,
        n_observations=n_observations,
        n_factors=n_factors,
        n_responses=observed.shape[1],
        n_terms=n_terms,
        term_names=quadratic_term_names(n_factors),
        rank_relative_tolerance=rank_relative_tolerance,
        design_condition_number=float(singular_values[0] / singular_values[-1]),
    )
