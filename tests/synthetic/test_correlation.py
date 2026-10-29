import numpy as np
import pytest
from numpy.testing import assert_allclose

from cnbi_v2.synthetic import evaluate, radius, sample_ball
from cnbi_v2.synthetic.anchors import constraint_jacobian, constraints
from cnbi_v2.synthetic.correlation import (
    calibration_loss_gradient,
    feature_covariance,
    from_feature_covariance,
    population_correlation,
    summaries,
)
from cnbi_v2.synthetic.validation import certify_anchors, certify_correlation


def test_absolute_and_signed_upper_triangle_means_are_distinct():
    r = np.array([[1, -0.5, 0.25], [-0.5, 1, -0.75], [0.25, -0.75, 1.0]])
    assert summaries(r) == (0.5, -1 / 3)


def test_feature_covariance_identity_and_population_precision():
    x = sample_ball(3, 14, 190318)
    a = np.array(
        [[0, 0, 0], [0.2, -0.1, 0.4], [-0.6, 0.4, 0.1], [0.9, -0.1, -0.3], [-0.1, -0.8, 0.2]]
    )
    c = feature_covariance(x)
    correlation = from_feature_covariance(a, c)
    assert_allclose(correlation, np.corrcoef(evaluate(x, a), rowvar=False), atol=1e-14, rtol=0)
    population = population_correlation(a, radius(3))
    assert_allclose(correlation, population, atol=0.003, rtol=0)
    certificate = certify_correlation(correlation, 3)
    assert certificate.valid and certificate.rank == 4
    assert abs(certificate.minimum_eigenvalue) < 1e-12


def test_loss_and_inequality_jacobians_against_independent_finite_differences():
    m, nx = 4, 2
    u = np.array([[-0.2, 0.1], [0.3, -0.1], [0.1, 0.4], [-0.3, -0.4]]).ravel()
    cov = feature_covariance(sample_ball(nx, 11, 773))

    def fun(z):
        return calibration_loss_gradient(z, m, nx, radius(nx), cov, 0.6)

    value, grad = fun(u)
    rho = summaries(from_feature_covariance(u.reshape(m, nx) * radius(nx), cov))[0]
    assert_allclose(value, (rho - 0.6) ** 2, atol=1e-16)
    eps = 1e-6
    basis = np.eye(len(u)) * eps
    numeric = np.array([(fun(u + h)[0] - fun(u - h)[0]) / (2 * eps) for h in basis])
    assert_allclose(grad, numeric, atol=3e-9, rtol=1e-6)
    numeric_g = np.column_stack(
        [
            (constraints(u + h, m, nx, 1e-4) - constraints(u - h, m, nx, 1e-4)) / (2 * eps)
            for h in basis
        ]
    )
    assert_allclose(constraint_jacobian(u, m, nx), numeric_g, atol=2e-10, rtol=0)


def test_singular_psd_is_accepted_but_indefinite_or_malformed_is_not():
    assert certify_correlation(np.ones((4, 4)), 2).valid
    bad = np.eye(4)
    bad[0, 1] = bad[1, 0] = 2
    assert not certify_correlation(bad, 2).valid
    bad = np.eye(4)
    bad[0, 1] = 0.4
    assert not certify_correlation(bad, 2).valid
    assert not certify_correlation(np.eye(4) * 0.9, 2).valid
    assert not certify_correlation(np.eye(4), 2).valid  # impossible rank for these functions
    assert not certify_anchors(np.zeros((4, 2)), radius(2)).valid
    assert not certify_anchors(np.array([[0, 0], [0.1, 0], [0.2, 0], [0.3, 0]]), radius(2)).valid
    assert not certify_anchors(np.array([[0, 0], [3, 0], [0, 3], [0.3, 0.3]]), radius(2)).valid


@pytest.mark.parametrize(
    "call",
    [
        lambda: summaries([1, 2]),
        lambda: summaries([[1]]),
        lambda: feature_covariance([[0, 0]]),
        lambda: from_feature_covariance([[0, 0]], np.eye(3)),
        lambda: population_correlation([0, 1], 1),
        lambda: population_correlation([[0, 0]], 0),
        lambda: certify_correlation(np.eye(3), 2),
        lambda: certify_anchors([[0, 0]], 1),
        lambda: certify_anchors(np.zeros((4, 2)), 1, separation_ratio=0),
    ],
)
def test_invalid_correlation_inputs(call):
    with pytest.raises(ValueError):
        call()
