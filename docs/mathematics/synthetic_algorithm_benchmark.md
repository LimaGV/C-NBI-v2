# Synthetic algorithm benchmark — Phase10D

The paired unit is a frozen Phase10B RSM instance; five replicas are nested within
one structural cell, not five independent structural scenarios. There are 135
instances and four methods, for 540 planned official runs. Methodology and fixed
parameters are specified in MDR0016 and the archived algorithm configurations.

The optimization domain is ||x||<=alpha=2^(nx/4), nx in {2,3,5}; all original
objectives are minimized. The search interface carries only noisy coefficients,
noisy CCD observations and estimated uncertainty quantities. No original model
is refitted; VRF auxiliary factor-score fitting is a separate permitted step.
True anchors, analytical objectives, reference sets, true ideals/nadires and
quality indicators never enter the search interface. Search subprocesses exit
before offline true-function evaluation.

C-NBI: optimize nominal quadratics; A_ij=fhat_i(xstar_j); normalize using the
estimated nominal payoff. Sample Bhat+C_X G L_Sigma.T jointly 2000 times with the
validated PSD factorization, optimize all sampled quadratics and build A_b.
Use D_a^-1(A_b-A_nom), centered CHIM spectra and strict observed>q95 comparisons
for every nonzero local singular component, over all eligible subsets. Approved
subsets receive their own payoff normalization and unchanged local v2 NBI.
Candidate, rejected and selected subsets, component thresholds, all NBI attempts
and complete MC coefficient/anchor/payoff arrays are archived. No ensemble
failures are silently removed. No applied-case list of subsets is reused.

VRF-NBI: let Z be standardized noisy observations and L the rotated retained
correlation loadings. W=L(L.T L)^+, scores=ZW, and fitted factors g_j(x) are full
quadratics. T_j=min_{ball}g_j, V_j=sum_i L_ij^2, q_j(x)=(g_j(x)-T_j)^2+V_j.
The analytic derivative is 2(g_j-T_j) grad(g_j). U_j=min q_j, N_j=max q_j and
qnorm_j=(q_j-U_j)/(N_j-U_j). Construct the normalized payoff and orient its
unit affine normal toward the ideal. Full VRF objectives, never signed factor
scores directly, enter NBI. k=max(2,k90)>nx+1 is structurally invalid, not clamped.
All fitted-factor diagnostics, loadings, rotations/signs, score weights, targets,
variance, extremes, payoff, NBI attempts and failures are retained.

The v1 variance correction is a constant per factor, whose cancellation in
utopia/nadir normalization is proved in MDR0016. See the separate migration
provenance and numerical comparisons; do not claim bitwise identity across
different numerical environments or in nonunique local optima.
The compatibility adapter evaluates optimization in the v1 constant gauge and
exports published constants after subtracting that explicitly archived gauge.
This avoids changing quartic-flat payoff tie choices through constant-subtraction
rounding. Its normalized objective is algebraically the same complete VRF.

EAs operate on unnormalized original noisy RSM objective vectors, consistent
with the transferred v1 synthetic comparator. NSGA-III performs its own internal
normalization. MOEA/D uses PBI(theta=5). Initial populations sample the feasible
ball uniformly; crossover/mutation have explicit settings and radial repair
occurs inside the algorithm. Full final populations are preserved, including
duplicates and dominated individuals. Original optimizer F values and replayed
batch RSM predictions are both retained. Their difference is bounded using the
float64 dot-product forward-error bound, 8*p*eps*|design|@|B|; no scientific
coefficient or data tolerance is relaxed to force bitwise BLAS equivalence.

An internally accepted NBI point may lie just outside the exact float64 sphere
under its established solver tolerance. It is kept raw. Offline Phase10C uses
its unchanged strict feasibility test; no post-hoc projection occurs. Both
certification and strict external counts must be reported.

The run lifecycle is PENDING -> RUNNING -> COMPLETED/FAILED/INCOMPLETE. A completed
payload is checksum-validated before reuse. Incompatible protocol hashes cannot
be mixed. Failed attempts are not automatically rerun or replaced. Interrupted
RUNNING tasks require an explicit operational recovery record and preserved
attempt-specific payloads; automatic recovery without such a record is refused.

Official streams hash namespace C-NBI-v2/phase10d/v1/20261029, scenario, replica,
method and purpose, taking the first128 SHA256 bits little-endian for PCG64.
Task order does not influence seeds. Pilot and official purposes are distinct.

The fixed Phase10C reference and normalization are shared across all five
replicas of a cell. Evaluate raw X on true functions only offline; retain raw,
feasible, unique and ND counts. Metrics use native full-objective true ND sets.
No clipping of normalized objectives, no repair, no selective replica exclusion,
no reconstruction of truth from noisy models, and no reference adaptation.

Report GD, IGD, HV with its precision status/SE, Spacing and Sparsity, end-to-end
cost, failures and cardinalities descriptively by cell/replica and structural
factors. Undefined quantities remain undefined. Replicas must be nested in
structural-cell aggregation. No significance tests or performance claims are
supported by arithmetic mean rankings alone.
