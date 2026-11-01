# Applied PA versus PA + anisotropy (postprocessing ablation)

Status: EXPERIMENTAL

The owner requested an isolated retrospective comparison on the applied turning
case. This does not modify the accepted C-NBI selection or any frozen result.

Read the Phase5 centered CHIM spectra for the 37 PA-approved subsets. Retain
subsets with q_S = sigma_(k-1)/sigma_1 >= global sigma_2/sigma_1; the fixed cutoff
is 0.3129205407188535 and the global PA dimension is two. No metric is used to
select or tune the cutoff. The selected catalog has 19 pairs and eight trios,
requiring 282 H5 weights instead of 492 (37 subsets).

Subset identity filters the complete standalone H5 raw candidate archive before
the unchanged Phase8 decision deduplication and eight-objective dominance.
The independent 18,503-point empirical reference, global normalization, numerical
tolerances, HV bounds, Sobol seeds/nodes and metric definitions remain frozen.
Pairwise K=min(ND sizes) and the official K66 use the existing extreme-preserving
FPS, including stable source-row tie handling. No optimizer, Monte Carlo,
RSM fitting, anchor calculation or Pareto-reference generation is authorized.

The ten removed trios are assessed for exclusive ND support and marginal HV.
Requested work reduction is theoretical. A counterfactual filtered runtime is
undefined because this task executes postprocessing only. Timing repetitions
of the original run are not independent quality replicates. No statistical
inference or change of the principal method follows from this ablation.

Outputs and the evidence-based conclusion are recorded separately under
`results/phase_08_pa_anisotropy/turning_pa_anisotropy_20261101/`. Source hashes,
input hashes, row memberships, metric deltas, coverage, contribution tables,
English figures and integrity tests preserve traceability.
