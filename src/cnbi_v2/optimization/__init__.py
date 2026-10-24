"""Nominal individual optimization and experimental response-region ablations."""

from .anchors import (
    RCOptions,
    RCTrial,
    ResponseRegionAnchor,
    classify_response_distance,
    deterministic_ball_starts,
    evaluate_responses,
    payoff_matrix,
    solve_response_region_anchor,
)
from .quadratic import Direction, QuadraticResponse, quadratic_responses
from .response_region import ResponseRegion, legacy_chi_square_threshold, response_cloud_region
from .trust_region import SphereAnchor, solve_quadratic_ball

__all__ = [
    "Direction", "QuadraticResponse", "RCOptions", "RCTrial", "ResponseRegion",
    "ResponseRegionAnchor", "SphereAnchor", "classify_response_distance",
    "deterministic_ball_starts", "evaluate_responses", "legacy_chi_square_threshold",
    "payoff_matrix", "quadratic_responses", "response_cloud_region",
    "solve_quadratic_ball", "solve_response_region_anchor",
]
