"""Joint matrix-normal plug-in coefficient sampling, without optimization."""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, fields
from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike
from scipy.linalg import solve_triangular  # type: ignore[import-untyped]

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real


def _immutable(values: FloatArray) -> FloatArray:
    return np.frombuffer(values.tobytes(), dtype=np.float64).reshape(values.shape)


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _names(values: Sequence[str] | None, size: int, prefix: str) -> tuple[str, ...]:
    labels = tuple(f"{prefix}_{i}" for i in range(size)) if values is None else tuple(values)
    if (len(labels) != size or any(not isinstance(v, str) or not v.strip() for v in labels)
            or len(set(labels)) != size):
        raise ValueError(f"{prefix} names must be unique nonempty strings of length {size}")
    return labels


def _residual_root(covariance: FloatArray) -> tuple[FloatArray, FloatArray, str, float, int]:
    """Return L, effective covariance, method, absolute PSD tolerance, zeroed count."""
    if not np.array_equal(covariance, covariance.T):
        raise ValueError("residual covariance must be exactly symmetric")
    scale = float(np.max(np.abs(covariance)))
    diagnostic = covariance / scale if scale else covariance.copy()
    tolerance = float(np.finfo(float).eps * len(covariance)
                      * np.linalg.norm(diagnostic, ord=np.inf))
    try:
        root = np.linalg.cholesky(covariance)
        return root, covariance.copy(), "CHOLESKY_SPD", tolerance * scale, 0
    except np.linalg.LinAlgError:
        eigenvalues, vectors = np.linalg.eigh(diagnostic)
        if eigenvalues[0] < -tolerance:
            raise np.linalg.LinAlgError(
                "residual covariance has a significantly negative eigenvalue") from None
        negative_count = int(np.count_nonzero(eigenvalues < 0))
        nonnegative = np.maximum(eigenvalues, 0)
        root = vectors * (np.sqrt(nonnegative) * np.sqrt(scale))
        effective = root @ root.T
        return root, effective, "SPECTRAL_PSD", tolerance * scale, negative_count


@dataclass(frozen=True, slots=True)
class _SamplingFactors:
    mean: FloatArray
    design_root: FloatArray
    design_covariance: FloatArray
    raw_residual_covariance: FloatArray
    effective_residual_covariance: FloatArray
    residual_root: FloatArray
    residual_method: str
    psd_tolerance: float
    zeroed_negative_eigenvalues: int
    response_names: tuple[str, ...]
    term_names: tuple[str, ...]


def _prepare(
    coefficient_mean: ArrayLike,
    design_r_factor: ArrayLike,
    residual_covariance: ArrayLike,
    response_names: Sequence[str] | None,
    term_names: Sequence[str] | None,
) -> _SamplingFactors:
    mean = _as_finite_real(coefficient_mean, "coefficient_mean")
    if mean.ndim != 2 or min(mean.shape) == 0:
        raise ValueError("coefficient_mean must have nonempty shape (p,m)")
    p, m = mean.shape
    upper = _as_finite_real(design_r_factor, "design_r_factor")
    covariance = _as_finite_real(residual_covariance, "residual_covariance")
    if upper.shape != (p, p) or not np.array_equal(upper, np.triu(upper)):
        raise ValueError("design_r_factor must be upper triangular with shape (p,p)")
    if covariance.shape != (m, m):
        raise ValueError("residual_covariance must have shape (m,m)")
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        design_root = np.asarray(solve_triangular(upper, np.eye(p), lower=False), dtype=np.float64)
        design_covariance = design_root @ design_root.T
        root, effective, method, tolerance, zeroed = _residual_root(covariance)
    if not all(np.isfinite(a).all() for a in (design_root, design_covariance, root, effective)):
        raise FloatingPointError("nonfinite computed coefficient-sampling factor")
    return _SamplingFactors(
        mean, design_root, design_covariance, covariance, effective, root,
        method, tolerance, zeroed, _names(response_names, m, "response"),
        _names(term_names, p, "term"),
    )


@dataclass(frozen=True, slots=True)
class CoefficientEnsemble:
    """samples[b,term,response]; covariance validation uses column-stacked vec.

    design_covariance_factor is C_X, while design_covariance is V_X=C_X C_X.T.
    Raw/effective residual covariance differ only for reported spectral roundoff.
    """

    samples: FloatArray
    seed: int
    n_samples: int
    coefficient_shape: tuple[int, int]
    sampling_method: str
    coefficient_mean: FloatArray
    residual_covariance: FloatArray
    effective_residual_covariance: FloatArray
    design_covariance_factor: FloatArray
    design_covariance: FloatArray
    residual_covariance_factor: FloatArray
    residual_factorization_method: str
    psd_eigenvalue_tolerance: float
    zeroed_negative_eigenvalues: int
    response_names: tuple[str, ...]
    term_names: tuple[str, ...]
    rng: str
    batch_size: int

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, np.ndarray):
                object.__setattr__(self, field.name, _immutable(value))


def _draw_batches(
    factors: _SamplingFactors, n_samples: int, seed: int, batch_size: int,
) -> Iterator[FloatArray]:
    generator = np.random.Generator(np.random.PCG64(seed))
    p, m = factors.mean.shape
    for start in range(0, n_samples, batch_size):
        count = min(batch_size, n_samples - start)
        # flat index = replica*(p*m) + term*m + response, independent of loops.
        normals = generator.standard_normal(count * p * m, dtype=np.float64).reshape(count, p, m)
        samples = np.empty((count, p, m), dtype=np.float64)
        # Fixed-size products per replica preserve arithmetic grouping across
        # prefixes and chunk sizes, unlike potentially different batched kernels.
        with np.errstate(over="raise", invalid="raise"):
            for i in range(count):
                samples[i] = (factors.mean
                              + factors.design_root @ normals[i] @ factors.residual_root.T)
        if not np.isfinite(samples).all():
            raise FloatingPointError("nonfinite coefficient sample")
        yield _immutable(samples)


def iter_coefficient_batches(
    coefficient_mean: ArrayLike,
    design_r_factor: ArrayLike,
    residual_covariance: ArrayLike,
    n_samples: int,
    *,
    seed: int = 777,
    batch_size: int = 100,
    response_names: Sequence[str] | None = None,
    term_names: Sequence[str] | None = None,
) -> Iterator[FloatArray]:
    """One explicit local PCG64 stream; immutable batches, never a global RNG.

    Validation happens at the call, before the returned iterator is consumed.
    """
    n = _integer(n_samples, "n_samples", 1)
    seed = _integer(seed, "seed", 0)
    batch_size = _integer(batch_size, "batch_size", 1)
    factors = _prepare(coefficient_mean, design_r_factor, residual_covariance,
                       response_names, term_names)
    return _draw_batches(factors, n, seed, batch_size)


def sample_coefficient_ensemble(
    coefficient_mean: ArrayLike,
    design_r_factor: ArrayLike,
    residual_covariance: ArrayLike,
    n_samples: int,
    *,
    seed: int = 777,
    batch_size: int = 100,
    response_names: Sequence[str] | None = None,
    term_names: Sequence[str] | None = None,
) -> CoefficientEnsemble:
    """Sample B_hat+C_X G L_Sigma.T jointly; no OLS, Y perturbation or anchors."""
    n = _integer(n_samples, "n_samples", 1)
    seed = _integer(seed, "seed", 0)
    batch_size = _integer(batch_size, "batch_size", 1)
    factors = _prepare(coefficient_mean, design_r_factor, residual_covariance,
                       response_names, term_names)
    samples = np.concatenate(list(_draw_batches(factors, n, seed, batch_size)), axis=0)
    return CoefficientEnsemble(
        samples, seed, n, factors.mean.shape, "MATRIX_NORMAL_PLUGIN",
        factors.mean, factors.raw_residual_covariance, factors.effective_residual_covariance,
        factors.design_root, factors.design_covariance, factors.residual_root,
        factors.residual_method, factors.psd_tolerance, factors.zeroed_negative_eigenvalues,
        factors.response_names, factors.term_names, "Generator(PCG64)", batch_size,
    )
