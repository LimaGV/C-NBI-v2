# MDR 0016 — Synthetic algorithm benchmark

Status: EXPERIMENTAL (protocol frozen before pilot; campaign requires all gates).
Date: 2026-10-29.
Evidence: METHOD_DEFINITION, METHODOLOGICAL_DECISION, INTERNAL_EVIDENCE,
MATHEMATICAL_DERIVATION; literature only where directly verified.

The authorized experiment pairs four methods on each of the 135 frozen noisy
multivariate RSMs, across 27 structural cells and five experimental replicas.
Neither truth, analytical anchors, analytical normalization nor reference quality
is supplied to search. The Phase10C evaluator operates only after search exits.
Previous scientific files and all data are immutable. PR16 was integrated by
merge c06467688187b6a2234a583a538b2b7131088172, identical tree to df95a954,
with main CI40941198792 passing Ubuntu and Windows.

C-NBI reuses v2 joint coefficient sampling, PSD handling, B=2000 certified anchor
reoptimizations, nominal-payoff normalization, centered CHIM SVD, strict q95
component screening of every eligible subset, local normalization, analytic NBI
Jacobians and the unchanged v2 SLSQP acceptance/retry policy. No early stopping.
All k=2..min(m,nx+1) candidates are screened. H=5 for k=2,3,4; H=2 for k=5,6,
transferred from v1 before seeing the synthetic benchmark outcomes.

VRF-NBI transfers the corrected v1 pipeline, never its direct-score predecessor.
It standardizes the supplied noisy observations (ddof=0), retains max(2,k90),
checks k<=nx+1 without truncation, rotates correlation loadings with normalized
Varimax and uses W=L pinv(L.T L), rcond=1e-15. Only auxiliary factor RSMs are
fitted. Targets minimize those RSMs. The optimized functions are squared target
deviations plus constant loading variances, with independent VRF utopia/nadir
normalization, payoff and NBI. Multistart SLSQP options and deterministic rescue
starts follow the pinned v1. Retention is an experimental transfer, not a literal
factor-selection rule established by the article.

Direct visual reading of Pereira et al. (2025), p.7 Eqs21–22, establishes
V_j=sum_i L_ij^2. The adjacent rho=2^(nx/4) defines the constraint radius; it does
not multiply the variance. The pinned v1 instead multiplies V by rho. The v2
adapter corrects the raw constant to the published definition. For a constant c_j,
VRF_j'=VRF_j+c_j implies U_j'=U_j+c_j, N_j'=N_j+c_j, hence Eq25 is invariant.
The migration audit compares raw values with this explicitly registered shift
and normalized intermediate quantities directly. Floating point trajectories
may differ; independent residual/domain certificates are retained.

Migration implementation correction: initial payoff comparisons failed despite
matching factors/targets. Quartic-flat individual minima amplified differences
in summation and constant-subtraction rounding into different payoff tie choices.
The adapter therefore preserves v1's design/Jacobian arithmetic order and uses
its constant translation (optimization gauge) internally. Published variance,
utopia and nadir are exported with that shift removed. For every point the
normalized mathematical VRF and its analytic derivative are unchanged. The
gauge shift and both sets of constants are archived; a direct oracle checks
this identity. This is a numerical compatibility correction validated before
pilot, not a change to H/B/tolerances or any parameter chosen by quality.

NSGA-III/MOEA/D use pymoo0.6.2 and the 18 previously calibrated v1 records, with
all operator parameters explicit. No retuning. Both use the same ceiling by m:
max(50000,400*C(m+3,4)). As in v1, floor(ceiling/population) complete generations
are executed; actual NFE and the unspent remainder are recorded. No overshoot.
PBI theta=5 applies to these m>=4 cases. Initialization is uniform in the current
dimension's ball. Radial repair uses one representable step inward to avoid
rounding an internally repaired individual outside the ball. This necessary
generalization is not a transfer of the old fixed three-variable domain.

One CPU worker and one BLAS/OpenMP thread are fixed. Main cost is end-to-end
preparation+solver+postprocessing. Original full-vector RSM points, vectorized
calls, scalar quadratic evaluations, analytic gradients and solver iterations
are separate counters; different counters do not imply equal computational work.
Call-instrumentation overhead is included for all methods. External true-function
and metric computation is timed separately. No equal-time or equal-NFE claim.

Twelve pilot runs (three preselected cells, replica1, all methods) precede the
540 official tasks, using distinct SHA256/PCG64 streams. Migration, repeatability,
integrity, checkpoints, feasibility and a stratified runtime projection must pass.
A structural/scientific failure blocks the main campaign; status stays INCOMPLETE.
No parameter, threshold, tolerance, H, B or retention rule is tuned to an outcome.
Implementation corrections require recorded evidence and pilot revalidation.

Raw outputs are preserved; internal ND is assessed in all original noisy RSM
objectives, and external ND/normalization/metrics use the frozen Phase10C API.
GD/IGD p1, HV r=1.1 with four 2^16 Sobol scrambles plus the exact small-box branch,
Spacing ddof1 and mean-NN Sparsity remain unchanged. Undefined states and HV
precision flags remain explicit. Native cardinality is primary. No inferential
algorithm comparison, retuning, cardinality equalization or Phase10E occurs here.
