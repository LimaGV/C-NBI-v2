"""Explicit visual transforms, never scientific optimizers or model fitting."""

import numpy as np
from scipy.stats import chi2


def pca_projection(points):
    mean = points.mean(axis=0)
    _, singular, vt = np.linalg.svd(points - mean, full_matrices=False)
    # Resolve arbitrary SVD signs by the largest absolute loading, first tie.
    for row in vt:
        if row[np.argmax(np.abs(row))] < 0:
            row *= -1
    variance = singular**2 / (len(points) - 1)
    return dict(
        mean=mean.tolist(),
        components=vt[:2].T.tolist(),
        explained_variance_ratio=(variance / variance.sum()).tolist(),
        n=len(points),
        scaling="none beyond frozen global MIN normalization",
        sign_rule="largest absolute loading positive; first index breaks ties",
    )


def project(points, definition):
    return (points - np.array(definition["mean"])) @ np.array(definition["components"])


def ellipse_parameters(points):
    center = points.mean(axis=0)
    covariance = np.cov(points, rowvar=False, ddof=1)
    values, vectors = np.linalg.eigh(covariance)
    if values.min() < -1e-12 * max(1.0, values.max()):
        raise ValueError("unexpected non-PSD visual covariance")
    order = np.argsort(-values, kind="stable")
    values, vectors = np.maximum(values[order], 0), vectors[:, order]
    quantile = float(chi2.ppf(0.95, 2))
    return dict(
        n=len(points),
        center_x=float(center[0]),
        center_y=float(center[1]),
        covariance_xx=float(covariance[0, 0]),
        covariance_xy=float(covariance[0, 1]),
        covariance_yy=float(covariance[1, 1]),
        width=float(2 * np.sqrt(quantile * values[0])),
        height=float(2 * np.sqrt(quantile * values[1])),
        angle=float(np.degrees(np.arctan2(vectors[1, 0], vectors[0, 0]))),
        probability=0.95,
        chi2_df=2,
        chi2_quantile=quantile,
        covariance_estimator="sample covariance ddof1",
        center_definition="arithmetic MC mean",
    )


def evaluate_visual_slice(coefficients, radius, grid_size=101):
    """Evaluate frozen coefficients on x3=0 solely to draw the requested slice."""
    axis = np.linspace(-radius, radius, grid_size)
    x1, x2 = np.meshgrid(axis, axis)
    inside = x1 * x1 + x2 * x2 <= radius * radius
    terms = np.array(
        [
            np.ones_like(x1),
            x1,
            x2,
            np.zeros_like(x1),
            x1 * x1,
            x2 * x2,
            np.zeros_like(x1),
            x1 * x2,
            np.zeros_like(x1),
            np.zeros_like(x1),
        ]
    )
    values = np.einsum("tij,tr->ijr", terms, coefficients)
    values[~inside] = np.nan
    return x1, x2, inside, values
