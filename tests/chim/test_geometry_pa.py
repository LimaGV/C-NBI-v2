"""Manual geometry, invariance and selection oracles independent of the real case."""

from dataclasses import FrozenInstanceError, replace

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.chim import (
    ChimSpectrum,
    centered_chim,
    centering_matrix,
    chim_singular_values,
    component_pa,
    compute_chim_spectra,
    evaluate_pa_prefixes,
    leading_dimension,
    nominal_normalization,
    vertex_differences,
)
from cnbi_v2.optimization import Direction


def test_fixed_normalization_orientation_delta_and_no_per_replica_rescaling():
    nominal = np.array([[10., 4., 5.], [7., 2., 4.], [1., 3., 8.]])
    directions = [Direction.MAX, Direction.MIN, Direction.MAX]
    normalization = nominal_normalization(nominal, directions)
    assert_array_equal(normalization.signs, [-1, 1, -1])
    assert_array_equal(normalization.utopia, [-10, 2, -8])
    assert_array_equal(normalization.amplitudes, [6, 5, 7])
    normalized = normalization.normalize(nominal)
    assert_array_equal(np.diag(normalized), [0, 0, 0])
    assert_array_equal(normalized.max(axis=1), [1, 1, 1])
    samples = np.stack([nominal*1.1, nominal*.9, nominal + 2])
    delta = normalization.perturbations(samples)
    assert_allclose(delta, normalization.normalize(samples)-normalized, atol=1e-15)
    expected = (samples-nominal)*normalization.signs[:, None]/normalization.amplitudes[:, None]
    assert_array_equal(delta, expected)
    assert not np.all(np.diagonal(normalization.normalize(samples), axis1=1, axis2=2) == 0)
    assert_allclose(normalization.normalize(samples[-1])-normalized,
                    np.broadcast_to(2*normalization.signs[:, None]
                                    / normalization.amplitudes[:, None], (3, 3)))
    assert_array_equal(samples[-1], nominal+2)
    for array in [normalization.nominal_payoff, normalization.amplitudes, normalized, delta]:
        with pytest.raises(ValueError):
            array.setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        normalization.utopia = np.zeros(3)


def test_units_translation_and_equivalent_direction_preserve_spectra_and_decisions():
    nominal = np.ones((4, 4))-np.eye(4)
    t = np.arange(40*16, dtype=float).reshape(40, 4, 4)/10000
    samples = nominal[None]+t
    original = nominal_normalization(nominal, [Direction.MIN]*4)
    scale = np.array([1e-3, 5., 100., .1])[:, None]
    shift = np.array([3., -1., 8., 2.])[:, None]
    changed = nominal_normalization(nominal*scale+shift, [Direction.MIN]*4)
    equivalent = nominal_normalization(-nominal, [Direction.MAX]*4)
    a = compute_chim_spectra(original.normalize(nominal), original.perturbations(samples), 3)
    b = compute_chim_spectra(changed.normalize(nominal*scale+shift),
                             changed.perturbations(samples*scale+shift), 3)
    c = compute_chim_spectra(equivalent.normalize(-nominal),
                             equivalent.perturbations(-samples), 3)
    for x, y, z in zip(a, b, c, strict=True):
        assert_allclose(x.observed, y.observed, atol=1e-12)
        assert_allclose(x.noise, y.noise, atol=1e-12)
        assert_array_equal(x.observed, z.observed)
        assert_array_equal(x.noise, z.noise)
    decisions = [evaluate_pa_prefixes(s, [20, 40]) for s in (a, b, c)]
    assert decisions[0][-1].selected_ids == decisions[1][-1].selected_ids
    assert decisions[0][-1].selected_ids == decisions[2][-1].selected_ids


@pytest.mark.parametrize("k", [2, 3, 4, 8])
def test_centering_properties_vertex_translation_and_permutation(k):
    h = centering_matrix(k)
    assert_array_equal(h, h.T)
    assert_allclose(h@h, h, atol=2e-16)
    assert_allclose(h@np.ones(k), 0, atol=2e-16)
    vertices = np.arange(k*k, dtype=float).reshape(k, k) + np.eye(k)
    vector = np.arange(k)[:, None]*3.
    assert_allclose(centered_chim(vertices+vector), centered_chim(vertices), atol=1e-13)
    permutation = np.arange(k)[::-1]
    assert_allclose(chim_singular_values(vertices[np.ix_(permutation, permutation)]),
                    chim_singular_values(vertices), atol=1e-13)


@pytest.mark.parametrize("vertices,rank", [
    ([[0, 1], [0, 0]], 1),
    ([[0, 1, 2], [0, 0, 0], [0, 0, 0]], 1),
    ([[0, 1, 0], [0, 0, 1], [0, 0, 0]], 2),
    ([[0, 1, 0, 1], [0, 0, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]], 2),
    ([[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]], 3),
])
def test_known_affine_ranks_equal_every_vertex_difference_reference(vertices, rank):
    assert np.linalg.matrix_rank(centered_chim(vertices)) == rank
    for reference in range(len(vertices)):
        assert np.linalg.matrix_rank(vertex_differences(vertices, reference)) == rank
    singular = chim_singular_values(vertices)
    assert np.count_nonzero(singular > 1e-12) == rank
    assert len(singular) == len(vertices)-1
    assert np.all(singular[:-1] >= singular[1:])


def test_local_subset_slicing_uses_only_matching_rows_and_anchors_and_candidate_counts():
    nominal = np.arange(64, dtype=float).reshape(8, 8)+np.eye(8)
    noise = np.stack([nominal/10, nominal/20])
    before = nominal.copy(), noise.copy()
    spectra = compute_chim_spectra(nominal, noise, 3)
    assert len(spectra) == 155
    assert [sum(s.scope == "LOCAL" and len(s.indices) == k for s in spectra)
            for k in (2, 3, 4)] == [28, 56, 70]
    assert spectra[1].subset_id == "C_1_2" and spectra[-1].subset_id == "C_5_6_7_8"
    subset = next(s for s in spectra if s.indices == (1, 3, 5) and s.scope == "LOCAL")
    ix = np.ix_([1, 3, 5], [1, 3, 5])
    assert_array_equal(subset.observed, chim_singular_values(nominal[ix]))
    assert_allclose(subset.noise[0], chim_singular_values(noise[0][ix]))
    assert_array_equal(nominal, before[0])
    assert_array_equal(noise, before[1])


def test_component_selection_requires_all_strict_passes_and_nonmonotone_global_pattern():
    yes = component_pa([3, 1], np.tile([.5, .1], (100, 1)))
    no = component_pa([3, 1], np.tile([2, 2], (100, 1)))
    equal = component_pa([3, 1], np.tile([3, 1], (100, 1)))
    assert yes.passes.all() and not no.passes.all() and not equal.passes.any()
    assert_array_equal(no.passes, [True, False])
    mixed = component_pa([3, 2, 1], np.tile([2.5, 2.1, .9], (100, 1)))
    assert leading_dimension(mixed.passes) == (1, "NON_MONOTONE_PA_PATTERN")
    assert leading_dimension([False, False]) == (0, "MONOTONE_PA_PATTERN")
    assert leading_dimension([True, True]) == (2, "MONOTONE_PA_PATTERN")


def test_quantile_prefixes_are_linear_nested_and_global_dimension_does_not_filter_locals():
    noise = np.arange(200, dtype=float)[:, None]
    global_s = ChimSpectrum("GLOBAL", "GLOBAL", (0, 1, 2), np.array([100., 1.]),
                            np.column_stack([noise[:, 0], noise[:, 0]/2]))
    local = ChimSpectrum("LOCAL", "C_1_2_3", (0, 1, 2), np.array([5., 4.]),
                         np.tile([.5, .1], (200, 1)))
    records = evaluate_pa_prefixes([global_s, local], [100, 200])
    assert records[0].components[0].q95[0] == pytest.approx(94.05)
    assert records[1].components[0].q95[0] == pytest.approx(189.05)
    assert records[1].global_dimension == 0
    assert records[1].selected_ids == frozenset({"C_1_2_3"})
    assert records[1].quantile_ids == ("GLOBAL:1", "GLOBAL:2", "C_1_2_3:1", "C_1_2_3:2")
    for array in [global_s.noise, records[0].decision_quantiles, records[0].components[0].passes]:
        with pytest.raises(ValueError):
            array.setflags(write=True)


@pytest.mark.parametrize("nominal,directions,kwargs", [
    (np.ones((2, 3)), [Direction.MIN]*2, {}),
    (np.ones((2, 2)), [Direction.MIN]*2, {}),
    ([[2, 1], [2, 0]], [Direction.MIN]*2, {}),
    ([[0, 1], [1, 0]], [Direction.MIN], {}),
    ([[0, 1], [1, 0]], [Direction.MIN]*2, {"optimality_tolerance": [-1, 0]}),
    ([[0, 1], [1, 0]], [Direction.MIN]*2, {"optimality_tolerance": [0]}),
])
def test_invalid_normalization(nominal, directions, kwargs):
    with pytest.raises(ValueError):
        nominal_normalization(nominal, directions, **kwargs)


def test_invalid_geometry_spectrum_and_prefix_inputs():
    for k in [1, True, 2.5]:
        with pytest.raises(ValueError):
            centering_matrix(k)
    for vertices in [[], [1, 2], [[1]], np.empty((0, 2))]:
        with pytest.raises(ValueError):
            centered_chim(vertices)
    with pytest.raises(ValueError):
        chim_singular_values(np.ones((2, 3)))
    for reference in [-1, 2]:
        with pytest.raises(ValueError):
            vertex_differences(np.eye(2), reference)
    with pytest.raises(ValueError):
        compute_chim_spectra(np.eye(2), np.ones((1, 2, 2)), 1)
    with pytest.raises(ValueError):
        component_pa([1], [[-1], [0]])
    with pytest.raises(ValueError):
        leading_dimension([1, 0])
    with pytest.raises(ValueError):
        evaluate_pa_prefixes([], [100])
    spectra = compute_chim_spectra(np.eye(2), np.ones((20, 2, 2)), 1)
    for checkpoints in [[], [10, 10], [20, 10], [21]]:
        with pytest.raises(ValueError):
            evaluate_pa_prefixes(spectra, checkpoints)
    normalization = nominal_normalization([[0, 1], [1, 0]], [Direction.MIN]*2)
    with pytest.raises(ValueError):
        normalization.normalize(np.eye(3))


def test_nonfinite_numerical_results_fail_instead_of_entering_pa(monkeypatch):
    import cnbi_v2.chim.geometry as geometry
    normalization = nominal_normalization([[0, 1], [1, 0]], [Direction.MIN]*2)
    corrupt = replace(normalization, amplitudes=np.full(2, np.nan))
    with pytest.raises(FloatingPointError, match="normalized payoff"):
        corrupt.normalize(np.eye(2))
    with pytest.raises(FloatingPointError, match="normalized perturbation"):
        corrupt.perturbations(np.eye(2))
    with monkeypatch.context() as patch:
        patch.setattr(geometry, "centering_matrix", lambda k: np.full((k, k), np.nan))
        with pytest.raises(FloatingPointError, match="centered geometry"):
            centered_chim(np.eye(2))
    monkeypatch.setattr(geometry.np.linalg, "svd", lambda *a, **k: np.array([np.nan, 0.]))
    with pytest.raises(FloatingPointError, match="singular values"):
        chim_singular_values(np.eye(2))
