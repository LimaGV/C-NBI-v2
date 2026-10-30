"""Scenario-level inference with explicit ties, multiplicity and finite oracles."""

import hashlib
from itertools import permutations

import numpy as np
from numpy.typing import ArrayLike
from scipy.stats import chi2, rankdata  # type: ignore[import-untyped]

from ..model import FloatArray, real_array


def role_seed(role: str, master: int = 20261030) -> int:
    text = f"C-NBI-v2/phase10e/v1/{master}/{role}"
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:16], "big")


def vector(values: ArrayLike) -> FloatArray:
    a = real_array(values, "scenario values")
    if a.ndim != 1 or not len(a):
        raise ValueError("nonempty finite scenario vector required")
    return a


def holm(pvalues: ArrayLike) -> FloatArray:
    p = vector(pvalues)
    if np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must be in [0,1]")
    order = np.argsort(p, kind="stable")
    adjusted = np.empty_like(p)
    adjusted[order] = np.minimum(1, np.maximum.accumulate(p[order] * np.arange(len(p), 0, -1)))
    return adjusted


def signed_rank(differences: ArrayLike) -> dict[str, float | int]:
    """Exact conditional Wilcoxon, including ties, with Wilcox zero removal.

    Doubled average ranks are integers. Coefficients of product(1+t**rank2)
    count sign assignments. Each assignment has probability 2**(-n_nonzero).
    This avoids claiming SciPy's untied exact distribution is exact with ties.
    """
    raw = vector(differences)
    d = raw[raw != 0]
    if len(d) > 50:
        raise ValueError("exact int64 rank distribution is restricted to <=50 nonzero cells")
    if not len(d):
        return dict(statistic=0.0, pvalue=1.0, rank_biserial=0.0, nonzero=0, zeros=len(raw))
    ranks = np.asarray(rankdata(abs(d), method="average"), dtype=float)
    weights = np.rint(2 * ranks).astype(np.int64)
    total = int(weights.sum())
    positive = int(weights[d > 0].sum())
    tail = min(positive, total - positive)
    distribution = np.zeros(total + 1, dtype=np.int64)
    distribution[0] = 1
    for weight in weights:
        distribution[weight:] += distribution[:-weight].copy()
    probability = min(1.0, 2 * int(distribution[: tail + 1].sum()) / 2 ** len(d))
    return dict(
        statistic=tail / 2,
        pvalue=probability,
        rank_biserial=(2 * positive - total) / total,
        nonzero=len(d),
        zeros=len(raw) - len(d),
    )


def paired_effect(
    first: ArrayLike,
    second: ArrayLike,
    *,
    maximize: bool = False,
    seed: int,
    resamples: int = 50000,
) -> dict[str, float | int]:
    a, b = vector(first), vector(second)
    if a.shape != b.shape or len(a) < 2 or resamples < 2:
        raise ValueError("at least two paired scenarios and bootstrap draws required")
    difference = a - b
    benefit = difference if maximize else -difference
    test = signed_rank(benefit)
    rng = np.random.Generator(np.random.PCG64(seed))
    # Entire paired scenario differences are resampled; method pairing is intact.
    indices = rng.integers(0, len(a), size=(resamples, len(a)))
    bootstrap = np.median(difference[indices], axis=1)
    low, high = np.quantile(bootstrap, [0.025, 0.975])
    return dict(
        n_scenarios=len(a),
        median_difference=float(np.median(difference)),
        mean_difference=float(difference.mean()),
        ci_low=float(low),
        ci_high=float(high),
        wins=int(np.sum(benefit > 0)),
        ties=int(np.sum(benefit == 0)),
        losses=int(np.sum(benefit < 0)),
        **test,
    )


def rank_summary(values: ArrayLike, *, maximize: bool = False) -> dict[str, FloatArray]:
    a = real_array(values, "scenario-method values")
    if a.ndim != 2 or a.shape[0] < 2 or a.shape[1] < 2:
        raise ValueError("at least two scenarios and methods required")
    oriented = -a if maximize else a
    ranks = np.asarray(rankdata(oriented, axis=1, method="average"), dtype=float)
    winners = oriented == oriented.min(axis=1, keepdims=True)
    return dict(
        ranks=ranks,
        mean_rank=ranks.mean(axis=0),
        best_count=winners.sum(axis=0).astype(float),
        fractional_best=(winners / winners.sum(axis=1, keepdims=True)).sum(axis=0),
    )


def friedman_permutation(
    values: ArrayLike, *, seed: int, resamples: int = 199999
) -> dict[str, float | int]:
    a = real_array(values, "paired scenario-method values")
    if a.ndim != 2 or a.shape[0] < 2 or not 3 <= a.shape[1] <= 6 or resamples < 1:
        raise ValueError("at least two scenarios, 3..6 methods and positive permutations required")
    n, k = a.shape
    ranks = np.asarray(rankdata(a, axis=1, method="average"), dtype=float)
    tie_sum = 0
    for row in a:
        _, counts = np.unique(row, return_counts=True)
        tie_sum += int(np.sum(counts**3 - counts))
    correction = 1 - tie_sum / (n * (k**3 - k))
    if correction == 0:
        return dict(statistic=0.0, pvalue=1.0, asymptotic_p=1.0, permutations=resamples)

    def statistic(sums: FloatArray) -> FloatArray:
        centered = sums - n * (k + 1) / 2
        return np.asarray(12 * np.sum(centered**2, axis=-1) / (n * k * (k + 1) * correction))

    observed = float(statistic(ranks.sum(axis=0)))
    # Doubled-rank integer score avoids numerical equality ambiguity in the tail.
    rank2 = np.rint(2 * ranks).astype(np.int64)
    observed_score = int(np.sum((rank2.sum(axis=0) - n * (k + 1)) ** 2))
    choices = np.asarray(list(permutations(range(k))), dtype=np.int64)
    rng = np.random.Generator(np.random.PCG64(seed))
    extreme = 0
    for start in range(0, resamples, 2048):
        ids = rng.integers(0, len(choices), size=(min(2048, resamples - start), n))
        permuted = np.take_along_axis(rank2[None, :, :], choices[ids], axis=2)
        scores = np.sum((permuted.sum(axis=1) - n * (k + 1)) ** 2, axis=1)
        extreme += int(np.sum(scores >= observed_score))
    return dict(
        statistic=observed,
        pvalue=(extreme + 1) / (resamples + 1),
        asymptotic_p=float(chi2.sf(observed, k - 1)),
        permutations=resamples,
    )
