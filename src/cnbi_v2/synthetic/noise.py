"""One frozen signal fraction and task-keyed independent PCG64 streams."""

import hashlib
from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike

from .design import factorial_design
from .model import FloatArray, real_array


def stream_seed(master: int, scenario_id: str, replica_id: int) -> int:
    """Replica 0 is exclusively the external Sobol stream; 1..5 are noise.

    SHA-256's first 128 bits (big endian) identify a PCG64 SeedSequence input.
    No worker/order counter, Python hash, global RNG or Phase10A seed is used.
    """
    if (
        isinstance(master, bool)
        or not isinstance(master, Integral)
        or master < 0
        or scenario_id not in {c.scenario_id for c in factorial_design()}
        or isinstance(replica_id, bool)
        or not isinstance(replica_id, Integral)
        or not 0 <= replica_id <= 5
    ):
        raise ValueError("valid master, structural scenario ID and replica 0..5 required")
    key = f"C-NBI-v2/phase10b/v1/{master}/{scenario_id}/{replica_id}".encode("ascii")
    return int.from_bytes(hashlib.sha256(key).digest()[:16], "big")


def noise_variance(truth: ArrayLike) -> FloatArray:
    values = real_array(truth, "CCD truth")
    if values.ndim != 2 or values.shape[0] < 2 or values.shape[1] < 1:
        raise ValueError("CCD truth must be a matrix with at least two rows")
    with np.errstate(over="raise", invalid="raise"):
        signal = np.var(values, axis=0, ddof=1)
    if np.any(signal <= 0):
        raise ValueError("every response must have strictly positive signal variance")
    return signal / 19.0


def experimental_noise(truth: ArrayLike, seed: int) -> FloatArray:
    values = real_array(truth, "CCD truth")
    variance = noise_variance(values)
    if isinstance(seed, bool) or not isinstance(seed, Integral) or seed < 0:
        raise ValueError("noise seed must be a nonnegative integer")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    return rng.normal(0.0, np.sqrt(variance), size=values.shape)
