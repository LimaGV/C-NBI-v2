# Phase8 — standalone operational resolution correction

Official archive: `turning_standalone_correction_20261025`.
C-NBI(H=5) means standalone H5:492 accepted,411 unique,409 ND.
H2/H4/H10/H20 are independent resolution-sensitivity runs, never parent-grid
sources for H5. Five H5 timing repetitions have identical scientific arrays.
The direct pipeline consumes only upstream Phase2/5 inputs and explicit protocol;
Phase6/7 result directories were physically unavailable during every solve.

`turning_reference_sensitivity_20261024` is immutable
**historical_parent_grid_analysis**. Its408-point set must be read as
CNBI_H5_extracted_from_H20_parent_grid, not the official baseline. Old labels
inside that immutable archive retain their original execution meaning and are
superseded for current interpretation by this README and the corrected report.
The independent18503-point reference, saved subset indices/lineages/FPS and
all EA/VRF results/EA timings remain unchanged and are reused by hash.
The old common target is historical only, not a new self-included pooled target.

Reproduction (empty destination, single numerical thread, clean source commit):
`uv run python -m scripts.validation.turning_cnbi_standalone --output <directory>`.
It temporarily renames Phase6/7 result roots, restores them even on failure and
never rewrites old payloads. No EA/VRF is executed. Analyses and figures are in
turning_standalone_analysis and turning_standalone_report; their archived input
paths identify the preserved official run. Do not rerun historical campaign
entrypoints to define the official H5.

Read docs/mathematics/turning_final_benchmark.md and docs/phase_8_verification.md.
No automatic merge,adaptive refinement or new scenarios.
