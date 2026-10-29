"""Deterministic starting positions and constraints, never objective transformations."""

import numpy as np

from .design import Scenario
from .model import FloatArray


def initial_positions(scenario: Scenario, start: int, seed: int) -> FloatArray:
    rng = np.random.Generator(np.random.PCG64(seed))
    m, nx = scenario.m, scenario.nx
    if start == 0:
        # Balanced perturbed regular simplex: a solver initialization only.
        basis = np.zeros((nx + 1, nx))
        for k in range(nx):
            denominator = np.sqrt((k + 1) * (k + 2))
            basis[: k + 1, k] = 1 / denominator
            basis[k + 1, k] = -(k + 1) / denominator
        vertices = basis * np.sqrt((nx + 1) / nx) * nx / np.sqrt((nx + 4) * (nx + 2))
        result = vertices[np.arange(m) % (nx + 1)] + rng.normal(0, 0.01, (m, nx))
    else:
        direction = rng.normal(size=(m, nx))
        result = direction / np.linalg.norm(direction, axis=1)[:, None]
        result *= rng.uniform(size=m)[:, None] ** (1 / nx)
    return np.asarray(result, dtype=np.float64)


def constraints(coordinates: FloatArray, m: int, nx: int, separation: float) -> FloatArray:
    u = coordinates.reshape(m, nx)
    i, j = np.triu_indices(m, 1)
    return np.concatenate(
        (1 - np.sum(u * u, axis=1), np.sum((u[i] - u[j]) ** 2, axis=1) - separation**2)
    )


def constraint_jacobian(coordinates: FloatArray, m: int, nx: int) -> FloatArray:
    u = coordinates.reshape(m, nx)
    i, j = np.triu_indices(m, 1)
    result = np.zeros((m + len(i), m * nx))
    for k in range(m):
        result[k, k * nx : (k + 1) * nx] = -2 * u[k]
    for k, (left, right) in enumerate(zip(i, j, strict=True), m):
        difference = 2 * (u[left] - u[right])
        result[k, left * nx : (left + 1) * nx] = difference
        result[k, right * nx : (right + 1) * nx] = -difference
    return result
