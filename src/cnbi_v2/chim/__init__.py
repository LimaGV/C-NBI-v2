"""Fixed nominal normalization, centered CHIM and uncertainty-calibrated PA screening."""

from .early_stop import (
    EarlyStopValidation,
    PAStopPolicy,
    StopCheckpoint,
    evaluate_early_stop,
    policy_from_mapping,
)
from .geometry import centered_chim, centering_matrix, chim_singular_values, vertex_differences
from .normalization import PayoffNormalization, nominal_normalization
from .parallel_analysis import (
    ChimSpectrum,
    PACheckpoint,
    PAComponents,
    component_pa,
    compute_chim_spectra,
    evaluate_pa_prefixes,
    leading_dimension,
)
from .spectral_gap_stop import (
    AdjacentSpectralGaps,
    GapEarlyStopValidation,
    GapStopCheckpoint,
    Q95GapSpectrum,
    SpectralGapStopPolicy,
    checkpoint_spectral_gaps,
    evaluate_gap_early_stop,
    gap_policy_from_mapping,
    normalized_adjacent_gaps,
)

__all__ = [
    "AdjacentSpectralGaps", "GapEarlyStopValidation", "GapStopCheckpoint", "Q95GapSpectrum",
    "SpectralGapStopPolicy", "checkpoint_spectral_gaps", "evaluate_gap_early_stop",
    "gap_policy_from_mapping", "normalized_adjacent_gaps",
    "ChimSpectrum", "EarlyStopValidation", "PACheckpoint", "PAComponents", "PAStopPolicy",
    "PayoffNormalization", "StopCheckpoint", "centering_matrix", "centered_chim",
    "chim_singular_values", "component_pa", "compute_chim_spectra", "evaluate_early_stop",
    "evaluate_pa_prefixes", "leading_dimension", "nominal_normalization", "policy_from_mapping",
    "vertex_differences",
]
