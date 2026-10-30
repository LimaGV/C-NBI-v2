from itertools import product

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from scipy.stats import friedmanchisquare, wilcoxon

from cnbi_v2.synthetic.analysis.factors import factorial_decomposition
from cnbi_v2.synthetic.analysis.inference import (
    friedman_permutation,
    holm,
    paired_effect,
    rank_summary,
    role_seed,
    signed_rank,
    vector,
)


def test_holm_hand_oracle_and_original_order():
    assert_allclose(holm([0.03, 0.001, 0.04, 0.01]), [0.06, 0.004, 0.06, 0.03])
    assert_array_equal(holm([1, 1, 1]), [1, 1, 1])
    assert_array_equal(holm([0, 0]), [0, 0])
    for bad in ([], [[1]], [np.nan], [-0.1], [1.1]):
        with pytest.raises(ValueError):
            holm(bad)
    with pytest.raises(ValueError):
        vector([[1]])


@pytest.mark.parametrize("d", [[1, 2, -3, 4], [1, -1, 2, 0, -2], [0, 0], [1, 1, 1]])
def test_conditional_signed_rank_against_exhaustive_sign_oracle(d):
    from scipy.stats import rankdata

    d = np.asarray(d, dtype=float)
    nz = d[d != 0]
    result = signed_rank(d)
    if not len(nz):
        assert result["pvalue"] == 1 and result["rank_biserial"] == 0
        return
    ranks = rankdata(abs(nz))
    observed = min(ranks[nz > 0].sum(), ranks[nz < 0].sum())
    null = [
        min(np.dot(bits, ranks), np.dot(1 - np.array(bits), ranks))
        for bits in product((0, 1), repeat=len(nz))
    ]
    expected = np.mean(np.asarray(null) <= observed)
    assert result["pvalue"] == expected
    assert result["statistic"] == observed
    assert result["zeros"] == np.sum(d == 0)


def test_signed_rank_untied_scipy_and_effect_direction():
    d = np.array([1.0, -2.0, 3.0, -4.0, 5.0, 6.0])
    assert signed_rank(d)["pvalue"] == wilcoxon(d, method="exact").pvalue
    assert signed_rank(-d)["pvalue"] == signed_rank(d)["pvalue"]
    assert signed_rank(-d)["rank_biserial"] == -signed_rank(d)["rank_biserial"]
    with pytest.raises(ValueError):
        signed_rank(np.arange(1, 52))


def test_cluster_bootstrap_pairing_seed_and_constant_oracle():
    a, b = np.arange(27.0), np.arange(27.0) + 3
    result = paired_effect(a, b, seed=role_seed("oracle"), resamples=1000)
    assert result["median_difference"] == result["ci_low"] == result["ci_high"] == -3
    assert result["wins"] == 27 and result["rank_biserial"] == 1
    assert result == paired_effect(a, b, seed=role_seed("oracle"), resamples=1000)
    maximum = paired_effect(a, b, seed=2, maximize=True, resamples=1000)
    assert maximum["losses"] == 27 and maximum["rank_biserial"] == -1
    assert role_seed("a") != role_seed("b")
    for x, y, draws in (([1], [2], 100), ([1, 2], [3], 100), ([1, 2], [2, 3], 1)):
        with pytest.raises(ValueError):
            paired_effect(x, y, seed=1, resamples=draws)


def test_friedman_statistic_ties_against_scipy_and_permutation_replay():
    a = np.array([[1.0, 2, 3, 4], [2, 2, 5, 6], [4, 1, 1, 3], [1, 2, 4, 3]])
    result = friedman_permutation(a, seed=42, resamples=999)
    assert_allclose(result["statistic"], friedmanchisquare(*a.T).statistic, atol=1e-14)
    assert_allclose(result["asymptotic_p"], friedmanchisquare(*a.T).pvalue, atol=1e-14)
    assert result == friedman_permutation(a, seed=42, resamples=999)
    assert 1 / 1000 <= result["pvalue"] <= 1
    tied = friedman_permutation(np.ones((4, 3)), seed=0, resamples=99)
    assert tied["statistic"] == 0 and tied["pvalue"] == 1
    for bad in ([1, 2, 3], [[1, 2, 3]], np.ones((3, 2)), np.ones((3, 7))):
        with pytest.raises(ValueError):
            friedman_permutation(bad, seed=1, resamples=1)
    with pytest.raises(ValueError):
        friedman_permutation(a, seed=1, resamples=0)


def test_ranking_exact_ties_and_maximization_no_artificial_ranking():
    result = rank_summary([[1, 1, 3], [3, 2, 1]])
    assert_array_equal(result["ranks"], [[1.5, 1.5, 3], [3, 2, 1]])
    assert_array_equal(result["best_count"], [1, 1, 1])
    assert_array_equal(result["fractional_best"], [0.5, 0.5, 1])
    assert_array_equal(rank_summary([[1, 2], [2, 1]], maximize=True)["mean_rank"], [1.5, 1.5])
    for bad in ([[1]], [1, 2], [[1, np.nan], [2, 3]]):
        with pytest.raises(ValueError):
            rank_summary(bad)


def test_factorial_decomposition_orthogonal_known_main_interaction():
    i, j, k = np.indices((3, 3, 3))
    y = (i - 1) * (j - 1) + 2 * (k - 1)
    rows = factorial_decomposition(y)
    ss = {r["effect"]: r["sum_squares"] for r in rows}
    assert_allclose(ss["nx:delta"], 12)
    assert_allclose(ss["rho_target"], 72)
    assert_allclose(sum(ss.values()), np.sum((y - y.mean()) ** 2), atol=1e-12)
    assert sum(r["degrees_of_freedom"] for r in rows) == 26
    rng = np.random.default_rng(123)
    random_cube = rng.normal(size=(3, 3, 3))
    result = factorial_decomposition(random_cube)
    assert_allclose(
        sum(r["sum_squares"] for r in result),
        np.sum((random_cube - random_cube.mean()) ** 2),
        rtol=1e-14,
    )
    assert all(
        r["fraction_of_contrast_variation"] is None
        for r in factorial_decomposition(np.ones((3, 3, 3)))
    )
    with pytest.raises(ValueError):
        factorial_decomposition(np.ones((2, 3, 3)))
