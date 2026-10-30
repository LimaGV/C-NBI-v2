# Phase10E independent pairwise correction

Current equalization: C-NBI versus VRF-NBI, then NSGA-III, then MOEA/D.
K=min(two native ND counts) independently per scenario-replica. No other method
constrains a pair. There are405 paired blocks and810 real float64 subsets.
The previous statistical_20261030 archive is preserved as the superseded
four-method cardinality analysis. Native primary results/costs are unchanged.

Use the locked environment with OPENBLAS_NUM_THREADS/OMP_NUM_THREADS/MKL_NUM_THREADS=1.
Run scripts/validation/phase10e_pairwise_{derive,statistics,audit,figures,report,finalize}.py
in that order. The input snapshot is already frozen; do not recreate it.
Finalize with --verify to check every output and protected prior file.

replica_metrics.csv:1620 rows (native/equalized, two methods per each of405 blocks).
selection_diagnostics.csv and subsets/:810 retained-index/point sets.
statistical_tests.csv: pairwise Wilcoxon/Holm/effects/CIs and bootstrap seeds.
scenario_metric_summary.csv and paired_scenario_differences.csv: full cell tables.
Factor/covariate files are recalculated for the independent pair contrasts.
HV pending is excluded by the two-method cohort only; supplementary numerical
values require exact set identity and never promote official flags.
No equalized four-method Friedman or rank is mathematically formed.

See docs/phase_10e_pairwise_verification.md for current conclusions and limitations.
Six English PNG600/vector-PDF figures, no decorative grids. Hashes, source,
versions and verification observations are recorded in the manifests. No official
optimizer or original RSM is rerun. Original data and license scope are unchanged.
