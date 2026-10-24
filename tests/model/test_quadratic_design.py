from itertools import product

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from cnbi_v2.model import quadratic_design, quadratic_term_names


def test_three_factor_basis_has_exact_canonical_order():
    factors = np.array([[2, 3, 5], [-1, 4, 0]])
    original = factors.copy()
    assert quadratic_term_names(3) == (
        "intercept",
        "x1",
        "x2",
        "x3",
        "x1^2",
        "x2^2",
        "x3^2",
        "x1*x2",
        "x1*x3",
        "x2*x3",
    )
    assert_array_equal(
        quadratic_design(factors),
        [
            [1, 2, 3, 5, 4, 9, 25, 6, 10, 15],
            [1, -1, 4, 0, 1, 16, 0, -4, 0, 0],
        ],
    )
    assert_array_equal(factors, original)


@pytest.mark.parametrize("n_factors", [1, 2, 3, 4, 5])
def test_number_of_terms_and_general_interaction_order(n_factors):
    factors = np.arange(2, n_factors + 2, dtype=float).reshape(1, -1)
    names = quadratic_term_names(n_factors)
    p = (n_factors + 1) * (n_factors + 2) // 2
    assert len(names) == len(set(names)) == p
    result = quadratic_design(factors)
    assert result.shape == (1, p)
    # Evaluate named monomials independently of production column assembly.
    coordinates = dict(zip([f"x{i + 1}" for i in range(n_factors)], factors[0], strict=True))
    for name, actual in zip(names, result[0], strict=True):
        if name == "intercept":
            expected = 1
        elif name.endswith("^2"):
            expected = coordinates[name[:-2]] ** 2
        else:
            expected = np.prod([coordinates[part] for part in name.split("*")])
        assert actual == expected
    if n_factors == 4:
        assert names[-6:] == ("x1*x2", "x1*x3", "x1*x4", "x2*x3", "x2*x4", "x3*x4")


@pytest.mark.parametrize("invalid", [0, -1, True, 1.5, "3"])
def test_term_count_rejects_invalid_factor_count(invalid):
    with pytest.raises(ValueError, match="positive integer"):
        quadratic_term_names(invalid)


@pytest.mark.parametrize(
    "invalid", [[], [1, 2], 2, np.empty((3, 0)), np.empty((0, 2)), np.ones((2, 2, 2))]
)
def test_design_requires_nonempty_matrix(invalid):
    with pytest.raises(ValueError, match="shape"):
        quadratic_design(invalid)


@pytest.mark.parametrize("invalid", [np.nan, np.inf, -np.inf])
def test_nonfinite_factors_rejected(invalid):
    with pytest.raises(ValueError, match="finite"):
        quadratic_design([[invalid]])


@pytest.mark.parametrize("invalid", [[[1j]], [["1"]], [[True]], [[None]]])
def test_no_silent_coercion_of_nonnumeric_or_complex_factors(invalid):
    with pytest.raises(ValueError, match="real numeric"):
        quadratic_design(invalid)


def test_polynomial_overflow_is_explicit():
    with pytest.raises(FloatingPointError, match="overflow"):
        quadratic_design([[1e200]])


def test_full_factorial_three_level_design_has_full_quadratic_rank():
    design = quadratic_design(list(product([-1, 0, 1], repeat=3)))
    assert design.shape == (27, 10)
    assert np.linalg.matrix_rank(design) == 10
