# Phase10E synthetic analysis

Independent offline analysis of Phase10D campaign_v2 at5c3829db.27 structural
cells x5 paired replicas x4 methods. No optimizer or original-response fit.
Native is primary; equalized and numerical sensitivities are secondary.
See docs/phase_10e_verification.md for all ten scientific questions, including
the loss of C-NBI's IGD advantage and inferior HV after equalization.

Reproduce from the preserved completed campaign, using the locked environment:

Set OPENBLAS_NUM_THREADS, OMP_NUM_THREADS and MKL_NUM_THREADS to1 before step1.

1. `uv run python scripts/validation/phase10e_derive.py --workers 4`
2. `uv run python scripts/validation/phase10e_statistics.py`
3. `uv run python scripts/validation/phase10e_audit.py`
4. `uv run python scripts/validation/phase10e_figures.py`
5. `uv run python scripts/validation/phase10e_report.py`
6. `uv run python scripts/validation/phase10e_finalize.py`
7. `uv run python scripts/validation/phase10e_finalize.py --verify`

Original outputs are never overwritten. Snapshot creation is a separate initial
operation, already frozen in Git; do not recreate the input manifest. Derived
NPZ replay checks exact row IDs and values before reusing an existing subset.
Wall-time observations differ across reproductions; scientific values/seeds do not.

Tables: native/equalized/feasibility replica metrics; all scenario medians,
six-pair differences, exact Wilcoxon/Friedman/Holm, bootstrap CIs/seeds, ranks,
fixed-factor main/interaction decomposition, signed/absolute covariates,
quality/cost counters and paired lifecycle ratios. All135 selected-index blocks
are represented by540 float64 subset NPZs. K has no random seed; first raw IDs
and objective order break exact ties. Original strict and pending HV stay intact.
The two supplementary HV evaluations pass at2^20 but never promote official status.

Figures (each PNG600 and vector PDF): igd_by_dimension, hv_by_objectives,
scenario_rankings, igd_native_equalized, hv_native_equalized,
structural_correlation_effects, method_dimension_interactions, quality_time,
cardinality_influence, feasibility_tolerance_sensitivity, paired_confidence_intervals.

Hashes: checksums.sha256, frozen_inputs_manifest.json, generation_manifest.json.
Public synthetic derivatives are explicitly requested in Phase10E; no original
raw data, protected literature PDF or excluded-material license is republished
or relicensed by this archive. MIT scope remains unchanged.
