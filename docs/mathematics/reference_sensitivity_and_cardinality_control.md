# Reference sensitivity, cardinality and processing cost

All geometry uses the frozen nominal Phase5 global MIN normalization
z_i=(s_i f_i-u_i)/a_i. Neither methods, runs nor K levels are renormalized.
Values outside[0,1] are retained. The current nominal RSMs and response directions
are unchanged. Historical VRF means only the66 already reevaluated Phase7 points;
no VRF algorithm, workbook pipeline or timing is executed in Phase8.

## Five primary indicators

For finite nonempty candidate A and empirical reference R in normalized space:

GD(A,R) = (1/|A|) sum_a min_r ||a-r||_2.

IGD(A,R) = (1/|R|) sum_r min_a ||r-a||_2.

Both are arithmetic-mean Euclidean p1 conventions; smaller is better. They are
not root-mean-square variants or IGD+. Reference composition/density can change
their interpretation even when the candidate is identical.

HV(A;r) = Lebesgue_measure(union_a product_i [a_i,r_i]), all objectives MIN.

The fixed common r strictly dominates every point used in the quality benchmark.
Larger HV is better. The corrected applied V1 rule is preserved once for the
complete canonical Phase7 candidates (including CNBI for common integration bounds):

lo_i=min(0,min z_i); w_i=max z_i;
r_i=max(1.1,w_i+.05*max(w_i-lo_i,1)).

The max(...,1) provides positive margin for constant coordinates. No r change
by method, K, subset size or run count. The rule and r hash are archived.
The earlier V1 fixed1.1 recipe alone would miss current values above1.1; the
corrected applied rule explicitly accounts for the global worst coordinates.

For d_j=min_{k != j} ||a_j-a_k||_2 and d_bar=mean_j d_j:

Spacing(A) = sqrt(sum_j(d_j-d_bar)^2/(|A|-1)).

Sparsity(A) = d_bar.

These are the **corrected applied V1** definitions. The earlier notebook04 used
Spacing denominator|A| (ddof0); notebook11 and the actual corrected applied
`metricas_por_seed.csv` use ddof1. A330-point historical oracle reproduces
Spacing0.04501054580599567 and Sparsity0.049105932312835714. Source paths/hashes,
the earlier differing value and oracle lineage are in
`references/metadata/phase_08_legacy_metrics/source_audit.json`. No claim of a
different generic textbook definition or literature verification is made.

Spacing describes nearest-neighbor regularity, not convergence. The historical
lower-Sparsity convention describes density and depends strongly on cardinality;
it is not universal solution quality. Both require at least two genuine points.
Numerical decision duplicates use the frozen Phase6 equality contract; no new
clustering or arbitrary near-duplicate removal. Additional nearest-neighbor
diagnostics use sqrt(eps64) only as a reported threshold, never a filter.

## HV quadrature and numerical reuse

HV is estimated by the same common-box indicator integral used by corrected V1:

HV_hat = volume([lo,r]) * mean_l 1{some a <= U_l componentwise}.

Four independently scrambled Sobol nets use explicit PCG64 streams20260..20263,
2^16 nodes each. The current explicit SciPy rng interface differs from historical
seed=RandomState; this is recorded along with the common sample hash. Power16
increases numerical resolution relative to old power14; nested14/15/16 estimates
are reported. This is an estimate of HV, not an exact-volume claim. Scramble SE
is sampleSD of four HV estimates divided by sqrt4. Identical nodes for every set
make changes paired; ties can reflect integration resolution, not equivalence.
This numerical integration does not repeat coefficient-uncertainty Monte Carlo.

Per-point attainment indicators are packed into bits in a regenerable ignored
cache. A selected front's mask is their bitwise OR; it is exactly the same
indicator at the same nodes, not a different estimator. Cache/source/sample
identities are recorded. Cached pairwise dominance/equality likewise changes
computation only: every subset picks its own first retained representative and
then uses the unchanged Phase6 numerical MIN dominance relation. Tests compare
cached results with the original full algorithm, including nontransitive equality
and removal of an earlier representative. All original origins are retained.

Software API evidence: Context7 pymoo callback documentation and installed source;
moocore was not found by Context7 and its official documentation/installed source
were used only for feasibility probes of exact HV (large8D sets timed out in the
bounded probe). Production HV retains the audited V1 integral, using SciPy
[Sobol](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.Sobol.html).
No new runtime dependency or V1 environment is introduced.

## Phase8A reference sensitivity

R_r,b=ND(union of final ND runs of NSGA3 and MOEAD for the same selected r seeds,
plus constant VRF), with r5/10/15/20/25/30. No CNBI at any resolution.
One PCG64(20261024) stream produces100 distinct sorted seed subsets without
replacement for each r<30, consumed in ascending r. At30 there is one full set;
prefixes are secondary diagnostics. The corrected H5 candidate is the standalone409-point front; the earlier408-point parent-derived candidate is historical.

Record GD/IGD(H5,R), HV(R), cardinality and exclusive family contributions.
Mean/median/sampleSD/IQR/q05/q95/min/max describe the100-subset distributions;
the full30 singleton has no sampleSD. Fixed-candidate HV/Spacing/Sparsity do not
depend on R and are not fabricated as reference-sensitive quantities.

Composition uses N,M,NM,NMV,MV,NV, always without CNBI. Marginal changes are
fullNMV minus the indicated reduced composition. No automatic saturation test
or extra reference runs. Validate R30 byte/numerical equality to the18503-point
Phase7 reference, then preserve it as a finite empirical quality target, never
as the true industrial Pareto front.

## Deterministic cardinality control

One complete greedy maximin ordering is computed for each genuine front.
First preserve the point attaining each objective minimum, objective order,
removing repeated extreme indices. Then select the unchosen point maximizing
its minimum squared Euclidean distance to the selected set. Exact ties use the
lowest stable archived source-row index. All K prefixes are nested; no point
is duplicated, interpolated or fabricated.

Reference reduction K_R250/500/1000/2500/5000/10000/18503 is sensitivity only.
The native/equalized benchmark and quality-versus-K curves keep their **complete**
common or family-LOO reference fixed. K66 permits all four methods to participate;
the extended grid uses the actual minimum unique-ND count over H5 and all60 EA
runs, not a mean or extrapolation. Native N_returned, N_ND_before_dedup and genuine
unique-ND cardinality are distinct and recorded.

The old common target is retained only as `HISTORICAL_COMMON_H20_TARGET`, not as a newly self-included pooled target for standalone H5. Other method numbers remain unchanged; independent CNBI assessment uses the frozen18503-point zero-CNBI target. Family LOO results are
`LEAVE_ONE_FAMILY_OUT`; their targets differ and cannot automatically rank
methods. Deterministic fronts are single observations, not fake replications.
Better-run fractions use strict comparisons; score-oriented midrank percentiles
put better deterministic performance higher. No inference against duplicated
deterministic samples or unregistered p-value tests.

## Processing time and revised scope

Primary cost is end-to-end processing time, including necessary preparation,
optimization, response evaluation and final numerical dedup/ND. Solver/core time
is separately reported where available; NFE is technical information, not an
artificial equivalence between RSM calls and SLSQP/Jacobian subproblems.

The earlier parent/direct equivalence failure (24/492) established trajectory
sensitivity and remains historical evidence. By the explicit pre-merge correction,
the official operational baseline is now standalone H5. Use the exact Phase6
solver/options/Jacobians/acceptance/starts and37 frozen subsets, construct each
lattice independently, and recompose eight responses before fixed-global-frame
deduplication/ND. No H20 result defines a lower-H output.

Each H2/H4/H5/H10/H20 is measured with its own scientific output. H5 has five
runtime repetitions with a predeclared absolute1e-12/relative0 scientific check;
the observed arrays are bitwise identical. Other H have one measured run each,
so no runtime variability estimate. One unreported H2 warm-up precedes timing.
End-to-end includes input preparation,mesh,geometry,NBI,eight-response evaluation,
start/trial observation,dedup and ND; excludes disk serialization and external
quality metrics. Solver time is the sum of lattice solver calls. Repetitions
are runtime noise only, not quality replicates. The first H5 run is official.

Actual Phase6/7 result directories were temporarily renamed during all measured
solves and restored in finally, proving computational independence from H20.
Options/numerical equality bounds are explicitly frozen in
`docs/policies/cnbi_standalone_correction.json`, so no Phase6 result is needed at
runtime. The old benchmark_cardinality_cost.json remains a byte-preserved
historical execution protocol, superseded only in baseline/cost scope.

EA controlled timing and all30-run quality arrays remain unchanged. Shared
historical-target time plots add the corrected CNBI runs, never pair old CNBI
quality with new runtime. Hardware/environment match; campaign dates/source
commits are separately recorded. VRF execution/timing remains forbidden.

Reuse the saved512 reference lineages,506 run-sensitivity rows,100-subset indices
and reference FPS ordering; reevaluate only GD/IGD for the corrected H5. Reference
cardinalities/HV/origins do not change. The entire prior Phase8 result directory
is historical_parent_grid_analysis and byte-identical. The official correction
is turning_standalone_correction_20261025, still within Phase8/PR11.
