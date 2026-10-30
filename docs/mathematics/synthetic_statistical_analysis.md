# Phase10E: paired analysis of the fixed synthetic factorial experiment

The sole campaign input is Phase10D `campaign_v2` at
`5c3829dbd1bdd41ee828cfaf919c551d4f869d32`. Its 540 searches and official external
evaluations remain immutable. All computations here are offline transformations
of those preserved outputs. There is no optimizer or model-fitting interface.

## Units, estimands and scope

Let q[s,r,a] be one indicator for structural cell s, nested noise replica
r=1,...,5 and method a. The primary observation is

    Q[s,a] = median_r q[s,r,a].

All four methods must have the same five replica identities. A native HV cell
is complete only when all twenty official HV values have a valid precision
status. The two pending values therefore remove one complete cell from the
primary HV contrast, leaving 26 cells; IGD uses all 27. We do not compute a
three-replica median for one method and compare it with five-replica medians.
The individual 135 observations per method remain available in replica tables.

For methods A,B the untransformed paired contrast is D[s]=Q[s,A]-Q[s,B].
Negative D favors A for IGD; positive D favors A for HV. We report the median
and mean of D, wins/ties/losses and matched rank-biserial correlation, oriented
so that positive rank-biserial values favor A. An indicator's median across
cells is distinct from the median of paired differences and is not substituted
for it. Larger ND cardinality is described as larger, never intrinsically better.

The design is fixed: nx in {2,3,5}, delta in {1,3,5}, target mean absolute
correlation in {.25,.60,.85}, one anchor geometry per cell. The number of
objectives m=nx+delta+1 is derived, not a fourth independent experimental factor.
Cells are the comparative units; replicas are not 135 independent problems.

## Friedman, exact conditional Wilcoxon and multiplicity

Within each cell, average ranks R[s,a] treat exact floating-point ties equally.
The Friedman statistic is

    T = 12/(n*k*(k+1)*C) * sum_a (sum_s R[s,a]-n*(k+1)/2)^2,
    C = 1 - sum_t (t^3-t)/(n*(k^3-k)),

where the tie counts t run over tied groups within rows. If C=0 all methods
tie: T=0 and p=1. With four methods, the default chi-square approximation is
retained only as a diagnostic. The primary p-value uses 199999 independently
sampled within-cell method-label permutations, with (extreme+1)/(B+1), including
the observed statistic in the finite Monte Carlo test. The smallest attainable
p-value is 1/200000. Integer doubled-rank scores avoid ambiguous numeric tail
equality. The public SciPy guidance identifies limitations of the asymptotic
approximation for this method count; see the
[official Friedman documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html).

For each pair we remove exact zero D, rank |D| with average ties, and let
w_i=2*rank(|D_i|). The coefficients c_j of

    product_i (1 + t^(w_i))

count every sign assignment. The two-sided conditional signed-rank probability
is min(1, 2*sum_{j<=min(Wplus,Wminus)} c_j / 2^n_nonzero). Dynamic programming
computes this distribution exactly with integer counts (n_nonzero<=50). An
all-zero contrast has p=1 and effect=0. Unlike applying the untied exact
distribution to tied observations, this construction includes the tied ranks
in the conditional distribution. The independent oracle enumerates all signs
for small examples and also agrees with SciPy on untied examples. Differences
are computed once in float64; no arbitrary rounding or tolerance creates ties.
The [Wilcoxon documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html)
describes the symmetry assumption and the limits of untied exact calculations.

The native primary family contains fourteen prespecified hypotheses: two
omnibus tests and six method pairs for each of IGD and HV. Every test is
reported; no pair is selected according to a favorable omnibus outcome. For
ordered raw probabilities p_(i), Holm gives

    adjusted_p_(i) = min(1, max_{j<=i} (M-j+1)*p_(j)).

All primary decisions use this one family at alpha=.05. Each named secondary
analysis has a separately labelled exploratory Holm family. Secondary tests do
not increase the confirmatory evidence by being counted as new primary tests.

These tests condition on exchangeability/symmetric independent signs of the
observed scenario contrasts. The 27 cells are not a probability sample of all
multiobjective problems. Neither p-values nor ranks prove universal superiority.

## Effect uncertainty

For each contrast, resample the complete paired scenario index vector 50000
times with replacement and calculate the median D in each draw. The 2.5/97.5
percentiles form pointwise 95% stability intervals. Pairing is preserved because
the same cell indices select both methods; individual nested replicas are not
resampled as independent cells. Constant contrasts give degenerate, valid
stability intervals. Intervals are not simultaneous, are not a replacement for
Holm decisions, and do not assert random-population coverage for the fixed design.
The [bootstrap API documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)
was checked for paired resampling semantics; the implementation explicitly
records its chosen percentile convention instead of inheriting a library default.

RNGs are independent PCG64 streams keyed by analysis, indicator and method pair,
using the first 128 big-endian bits of SHA256 of the documented role string.
Canonical scenario order is recorded by sorted IDs. Exact signed-rank tests
and FPS have no random seed. Per-test bootstrap/permutation seeds are exported.

## Equalized cardinality

For each (s,r), K is the minimum native ND count over the four methods.
Candidate rows are sorted by original raw ID. Objective-wise minima in original
objective order form a unique forced list. If it exceeds K, its first K entries
are retained; K is never enlarged. The unchanged Phase10C partial FPS fills the
remaining positions by maximizing minimum squared Euclidean distance in the
analytical-normalized true objective space. Exact numeric ties choose the first
original raw ID. The reference set is not an argument to selection.

Exports retain every selected original raw index, decision and normalized
objective in float64, plus extreme-truncation and retained-fraction diagnostics.
No point is interpolated or optimized. K=0 produces undefined metrics; K=1
leaves density measures undefined. All five frozen metrics are recalculated.
Equalization can discard most of a large front; it is a secondary description
of equal-sized candidate subsets, not an estimate of how the optimizer would
perform under a different search budget.

## Numerical sensitivity

Only the two officially pending HV sets receive supplementary 2^18 and 2^20
Sobol studies. The same four original scramble seeds, lower bound zero,
reference (1.1,...,1.1) and Phase10C precision criteria apply. Original statuses
and values never change. Only if both pass can the separate supplementary
27-cell analysis replace their values in its own copied table. A provisional
analysis retaining the two original pending estimates remains explicitly labelled.

Feasibility sensitivity uses norm(x)<=alpha+epsilon at epsilon=0,1e-12,1e-10,1e-9
in norm units. No decision is projected. Identity and full-m nondominance use
the original Phase10C tolerances. Identical selected row sets reuse the same
metric evaluation, preventing redundant numerical integration; changed sets
are evaluated with the unchanged metric code. Strict epsilon=0 is compared
with the original masks and indices. Every variant is reported, including any
pending new HV status, rather than choosing a favorable tolerance.

## Fixed-factor associations and computational cost

For complete 3x3x3 paired-contrast tables, functional ANOVA decomposes the
centered table into orthogonal main effects, all two-way interactions and the
three-way component. Each component is its marginal mean minus the grand mean
and all contained lower-order components. Its sum of squares is the squared
norm of the expanded component over 27 cells; component sums reconstruct total
contrast variation. This saturated descriptive decomposition has 26 degrees
of freedom and no residual error degrees of freedom. No F-test or causal claim
is attached. Incomplete tables receive marginal summaries only, without imputation.

Observed mean absolute and signed correlations are separate prespecified
exploratory covariates. We report Spearman association and partial slopes after
categorical main-factor adjustment; there is no significance-driven selection.
With only one geometry per cell, residual geometric confounding remains.

The main cost is the archived observed complete process lifecycle. Worker time,
NFE, scalar quadratic values, gradients, internal optimizations, NBI subproblems
and native front sizes remain separate. Time ratios compare paired cell medians
and bootstrap median log ratios; the exponential interval is pointwise.
All runtime interpretations retain the original six-process shared-host
environment and profiling overhead. Search effort cannot be equated by NFE
across heterogeneous methods. No optimizer is executed by Phase10E.
