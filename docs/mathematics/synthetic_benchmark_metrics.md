# Phase10C — frozen synthetic benchmark evaluation protocol

All values are evaluated offline in the same analytic ideal/nadir MIN frame per
structural scenario,shared across replicas and methods. The noisy RSM prediction
objects remain the only objective API during future search. No reference,oracle,
ideal/nadir or evaluation result is fed back into an optimizer. Historical applied
metric files and definitions remain unchanged.

## Five definitions

For finite normalized candidate set A and main reference R5000:

- GD=mean_a min_r ||a-r||_2.
- IGD=mean_r min_a ||r-a||_2.
- HV=volume of union_{a in A} product_j[a_j,1.1],all MIN.
- Spacing=sample SD (ddof1) of Euclidean nearest-other distances in A.
- Sparsity=mean of those nearest-other distances.

GD/IGD are p1 arithmetic means of Euclidean distances,not squared conventions
or IGD+. The validated repository distance/GD/IGD/Spacing/Sparsity APIs are reused.
Local density statistics require at least two distinct objective vectors;empty
or singleton cases are explicitly undefined,not artificial zeros. Empty eligible
ND sets produce undefined metrics. Self-comparison GD/IGD is zero;separated
different sets must have positive distances. These metrics characterize distinct
aspects;lower spacing/sparsity is not universal superiority. GD on a finite
reference need not vanish for an efficient decision absent from that sample.

## Hypervolume integration and precision study

The common box is analytically fixed:[0,1.1]^m. Never call the historical
competitor-derived box constructor. Points with any coordinate>=1.1 have zero
positive-volume contribution and remain eligible for other metrics. No clipping.
Identical objective boxes have no repeated contribution.

The initial study uses four independent PCG64/Sobol scrambles,8192 samples each,
then nested levels2^14,2^15,2^16. The validated HVGrid supplies samples,prefix
counting and between-scramble estimates. Seeds depend only on master20261029,
objective dimension and scramble ID;all scenarios with the same m,all replicas
and all future methods share the same quadrature. Exact array hashes identify
the grids. The same integrand is evaluated using an axis-aligned bounding tree:
node minima prune impossible dominators,node maxima certify hits,and leaf checks
use exact componentwise comparison. This is an acceleration of the existing
finite-set indicator,not a different HV integral;tests compare every hit.

For each level report mean HV,SE=sample_SD(four estimates)/sqrt(4),hit counts,
volume quantum=(1.1)^m/2^power,relative SE and change from the previous doubling.
SE is an estimate of randomized quadrature variation,not a guaranteed confidence
bound. Before the study,define a diagnostic pass as every scramble>=128 hits,
relative SE<=2%,quantum/mean<=1%,and successive-doubling change<=2%. Zero observed
hits with eligible boxes is UNRESOLVED_ZERO_HITS,not certified exact zero or
proof of precision. Missing precision is reported,never fabricated.

An exact small-set branch uses inclusion-exclusion for at most8 distinct eligible
boxes (at most255 intersections). Products of side lengths and signed subset
intersections give the independent analytic formula. Accumulate in extended
precision when available,export float64,and report conservative roundoff bound
64*float64_eps*sum(abs(terms)). If cancellation prevents relative bound<=1e-10,
report pending with the raw result rather than clipping or claiming exactness.
This branch prevents artificial QMC zeros for analytically resolvable tiny boxes.
Its cutoff is computationally bounded before any performance comparison.

Study exact one/two-box examples in every m4..11,including tiny-volume stress
cases and dimension10 (an indicator test,not a new structural scenario). Preserve
raw Sobol diagnostics even when the exact branch resolves a small-set zero.
The final large-set resolution is frozen only after the reference/oracle study.
The predeclared global maximum-power tiers are16,18,20. Begin at16;if any primary
reference fails,repeat the reference study at18,then20. Choose the first global
tier satisfying every primary reference,the same level for every future method.
Only independent reference precision controls escalation;earlier rows are retained.
If20 still fails,record HV_PRECISION_PENDING before any algorithm campaign.
Future large-set estimates always carry their own precision status;reference
accuracy is not a guarantee for arbitrarily small volumes returned by a method.

## Raw,feasible,unique and ND processing

Evaluation accepts scenario ID,replica1..5,method name,raw decision matrix,JSON
metadata and optional nonnegative runtime/NFE. Validate shape/finitude,copy and
preserve raw decisions. Compute true responses independently,then fixed analytic
normalization with no clipping. Strict norm<=alpha determines feasibility;there
is no repair or projection. Exclude infeasible rows only from metrics and preserve
their responses,violations and IDs for audit.

Within feasible rows,use stable first-representative L-infinity identity tolerance
1e-12*alpha,no transitive clustering. Identify ND in all m normalized coordinates
using the validated repository dominance function with fixed1e-12 coordinate
tolerance. Preserve indices/counts at every step. Exact duplicate objective rows
are set duplicates for local metric computation. Apparent tolerance effects are
diagnostic,not an alteration of raw outputs or of the mathematical reference.

The primary analysis uses native ND cardinality. The secondary equalization
plan takes the minimum eligible size in each paired scenario/replica block of
all four methods,selects only actual returned rows by deterministic candidate-
only geometric FPS with stable raw IDs,preserves extremes,and never uses reference
distances/interpolation. This phase creates a plan only;no algorithm equalization
or search is executed. Undefined cases remain explicit.

Protocol choices and numerical budgets are recorded in MDR0015 and the frozen
JSON. They cannot be adapted after algorithm results. No superiority claim,
significance test,benchmark campaign or10D execution is part of this phase.
