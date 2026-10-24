"""Uncertainty-calibrated spectral screening, not an equivalence claim to Horn PA."""

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real

from ._validation import frozen, integer
from .geometry import chim_singular_values


@dataclass(frozen=True, slots=True)
class ChimSpectrum:
    scope: str
    subset_id: str
    indices: tuple[int, ...]
    observed: FloatArray
    noise: FloatArray

    def __post_init__(self) -> None:
        object.__setattr__(self, "observed", frozen(self.observed))
        object.__setattr__(self, "noise", frozen(self.noise))


def compute_chim_spectra(
    nominal_normalized: ArrayLike, perturbations: ArrayLike, n_factors: int,
) -> tuple[ChimSpectrum, ...]:
    """All local candidates are evaluated, independently of global PA dimension."""
    n = integer(n_factors, "n_factors", 1)
    nominal = _as_finite_real(nominal_normalized, "nominal_normalized")
    delta = _as_finite_real(perturbations, "perturbations")
    if (nominal.ndim != 2 or nominal.shape[0] != nominal.shape[1] or len(nominal) < 2
            or delta.ndim != 3 or delta.shape[0] < 2 or delta.shape[1:] != nominal.shape):
        raise ValueError("need square nominal geometry and at least two matching perturbations")
    m = len(nominal)
    candidates = [("GLOBAL", "GLOBAL", tuple(range(m)))]
    candidates += [("LOCAL", "C_" + "_".join(str(j+1) for j in subset), subset)
                   for k in range(2, min(n+1, m)+1) for subset in combinations(range(m), k)]
    spectra = []
    for scope, identifier, subset in candidates:
        nominal_local = nominal[np.ix_(subset, subset)]
        delta_local = delta[:, subset, :][:, :, subset]
        spectra.append(ChimSpectrum(scope, identifier, subset,
                                    chim_singular_values(nominal_local),
                                    chim_singular_values(delta_local)))
    return tuple(spectra)


@dataclass(frozen=True, slots=True)
class PAComponents:
    q95: FloatArray
    margins: FloatArray
    passes: NDArray[np.bool_]

    def __post_init__(self) -> None:
        object.__setattr__(self, "q95", frozen(self.q95))
        object.__setattr__(self, "margins", frozen(self.margins))
        object.__setattr__(self, "passes", frozen(self.passes))


def component_pa(observed: ArrayLike, noise: ArrayLike) -> PAComponents:
    actual = _as_finite_real(observed, "observed")
    samples = _as_finite_real(noise, "noise singular values")
    if (actual.ndim != 1 or len(actual) == 0 or samples.ndim != 2
            or samples.shape[0] < 2 or samples.shape[1:] != actual.shape
            or np.any(actual < 0) or np.any(samples < 0)):
        raise ValueError("observed/noise must be nonnegative matching component spectra")
    q95 = np.quantile(samples, .95, axis=0, method="linear")
    margins = actual - q95
    return PAComponents(q95, margins, actual > q95)  # Strict comparison, no added margin.


def leading_dimension(passes: ArrayLike) -> tuple[int, str]:
    flags = np.asarray(passes)
    if flags.ndim != 1 or flags.dtype != np.bool_ or not len(flags):
        raise ValueError("passes must be a nonempty Boolean component vector")
    failing = np.flatnonzero(~flags)
    dimension = int(failing[0]) if len(failing) else len(flags)
    pattern = ("NON_MONOTONE_PA_PATTERN" if flags[dimension:].any()
               else "MONOTONE_PA_PATTERN")
    return dimension, pattern


@dataclass(frozen=True, slots=True)
class PACheckpoint:
    B: int
    global_dimension: int
    global_pattern: str
    components: tuple[PAComponents, ...]  # Global then canonical local candidate order.
    selected_ids: frozenset[str]
    quantile_ids: tuple[str, ...]
    decision_quantiles: FloatArray
    selected_counts: tuple[int, ...]  # k=2,...,max candidate k.

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision_quantiles", frozen(self.decision_quantiles))


def evaluate_pa_prefixes(
    spectra: Sequence[ChimSpectrum], checkpoints: Sequence[int],
) -> tuple[PACheckpoint, ...]:
    if (not spectra or spectra[0].scope != "GLOBAL"
            or any(s.scope != "LOCAL" for s in spectra[1:])):
        raise ValueError("spectra order must be global followed by all local candidates")
    points = tuple(integer(b, "checkpoint", 2) for b in checkpoints)
    if (not points or tuple(sorted(set(points))) != points
            or any(s.noise.shape[0] < points[-1] for s in spectra)
            or len({s.subset_id for s in spectra}) != len(spectra)):
        raise ValueError("checkpoints must be increasing, unique and within every spectrum")
    max_k = max((len(s.indices) for s in spectra[1:]), default=1)
    quantile_ids = tuple(f"{s.subset_id}:{r+1}" for s in spectra
                         for r in range(len(s.observed)))
    records = []
    for b in points:
        decisions = tuple(component_pa(s.observed, s.noise[:b]) for s in spectra)
        dimension, pattern = leading_dimension(decisions[0].passes)
        selected = frozenset(s.subset_id for s, d in zip(spectra[1:], decisions[1:], strict=True)
                             if d.passes.all())
        counts = tuple(sum(len(s.indices) == k and s.subset_id in selected for s in spectra[1:])
                       for k in range(2, max_k+1))
        records.append(PACheckpoint(b, dimension, pattern, decisions, selected, quantile_ids,
                                    np.concatenate([d.q95 for d in decisions]), counts))
    return tuple(records)
