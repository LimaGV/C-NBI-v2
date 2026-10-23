"""Synthetic fixtures only; seed is not a future C-NBI algorithm parameter."""

from itertools import product

import numpy as np
import pytest

from cnbi_v2.model import fit_multivariate_rsm, quadratic_design


@pytest.fixture
def ccd_factors():
    corners = np.array(list(product([-1.0, 1.0], repeat=3)))
    axes = np.vstack([1.7 * np.eye(3), -1.7 * np.eye(3)])
    return np.vstack([corners, axes, np.zeros((5, 3))])


@pytest.fixture
def correlated_case(ccd_factors):
    design = quadratic_design(ccd_factors)
    coefficients = np.arange(30, dtype=float).reshape(10, 3) / 10 - 1
    rng = np.random.default_rng(20261023)
    mixing = np.array([[1.0, 0.5, -0.3], [0.0, 0.7, 0.4], [0.2, 0.0, 0.9]])
    # One controlled error realization, not an empirical covariance convergence test.
    experimental_error = rng.normal(size=(19, 3)) @ mixing
    responses = design @ coefficients + experimental_error
    return ccd_factors, responses, fit_multivariate_rsm(ccd_factors, responses)


@pytest.fixture
def hand_case():
    factors = np.arange(-2.0, 3.0).reshape(-1, 1)
    design = quadratic_design(factors)
    coefficients = np.array([[2.0, -1.0], [3.0, 2.0], [0.5, -2.0]])
    # Both vectors are orthogonal to 1, x, x^2, verifiable by integer arithmetic.
    residual_1 = np.array([1.0, -4.0, 6.0, -4.0, 1.0])
    residual_2 = np.array([-1.0, 2.0, 0.0, -2.0, 1.0])
    residuals = np.column_stack([residual_1, 2 * residual_1 + residual_2])
    responses = design @ coefficients + residuals
    # r1'r1=70, r2'r2=10, r1'r2=0; df=2, known nonzero cross covariance.
    residual_covariance = np.array([[35.0, 70.0], [70.0, 145.0]])
    vx = np.array([[17 / 35, 0, -1 / 7], [0, 1 / 10, 0], [-1 / 7, 0, 1 / 14]])
    return factors, coefficients, residuals, residual_covariance, vx, responses
