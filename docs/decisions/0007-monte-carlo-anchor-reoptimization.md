# 0007 — Monte Carlo anchor reoptimization

- Status: ACCEPTED in the explicitly requested Phase 4 scope.
- Date: 2026-10-24.
- Branch: feature/04-monte-carlo-anchor-reoptimization.
- Parent: PR #6, authorized squash after four successful checks and clean tree.

## Decision

Consume the exact versioned Phase 3 coefficient_samples.npz (2000,10,8), pinned
by SHA-256, scientific source commit and metadata. No draws, OLS or covariance
changes. Recompute all eight individual anchors for each realization, then
A[b,i,j]=f_i[b](x_j_star[b]) with the same replica's models and anchors.
Natural response units, explicit MIN/MAX directions, radius alpha=8**0.25.
Nominal anchors are diagnostic references only, never optimizer substitutes.

Reuse the unchanged Phase 2 spectral global quadratic-ball solver and its
default tolerances. Expose the same existing coefficient extraction for arrays,
with the old fitted-model entry point delegating to it; no duplicate transform.
Recheck finite values, feasibility, stationarity, complementarity and shifted
PSD independently for every returned solution. Radial reporting tolerance is
alpha times the solver's dimensionless certificate tolerance, derived from
the existing normalized squared-norm constraint, not a scientific threshold.

Log failures with original one-based replica IDs, response, stage/type/message.
Keep their array positions as NaN with explicit validity masks. Do not replace,
drop, retry with nominal/previous/zero points, or switch solver. A replica's
payoff requires all its anchors. If any result is incomplete, archive counts,
masks and logs and refuse distribution summaries rather than silently averaging
a reduced ensemble. The CLI reports an incomplete scientific run as failure.

RC remains the earlier EXPERIMENTAL/ABLATION ONLY case. No RC constraints,
normalization, Nadir estimator, CHIM, edge matrices, explicit SVD/PA, subset
selection, NBI/C-NBI, parallelism or later phase is included. Existing solver
linear algebra is retained unchanged; no dimensional-analysis SVD is added.

## Diagnostics and evidence

Store immutable anchors (B,m,n_x), optimal values (B,m), raw payoffs (B,m,m),
norms, original solver cases, radial locations, masks and independently checked
certificates. Diagonal payoff identity is exact in the same environment.
Summarize displacements and optimal-value distributions using linear quantiles,
sample std (ddof=1); differences in sampled optima are not deterioration since
the response models differ. Twenty prefix diagnostics use one frozen input;
payoff mean error targets its full-2000 mean only as a descriptive diagnostic.
No early stop; the future PA policy remains PROPOSED.

Derivation and fixed-anchor counterexample: docs/mathematics/anchor_monte_carlo.md.
C-MC-04: METHODOLOGICAL_DECISION; C-MC-05: MATHEMATICAL_DERIVATION;
C-MC-06: METHOD_DEFINITION. Deterministic analytic oracles, nominal-ensemble
recovery, permutation/replica independence, certificates/failures/immutability,
prefix summaries and the pinned real-input contract validate the implementation.
Report actual attempted/success/failed counts and serial timing, never assume
16000 valid outcomes. No new dependency or solver tolerance is introduced.
