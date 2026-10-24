# 0006 — Joint multivariate coefficient Monte Carlo

- Status: ACCEPTED for the explicitly requested Phase 3 scope.
- Date: 2026-10-24.
- Branch: feature/03-multivariate-coefficient-monte-carlo.
- Parent: PR #5, merged by authorized squash after green checks.
- Separate future PA early-stop policy: PROPOSED, not applied in Phase 3.

## Decision

Use the exact original-coded Phase 2 model identity, preserving its complete
quadratic coefficients and raw residual covariance. Do not mix physical,
published or other coded fits. Obtain B_hat, R/V_X and Sigma_hat_e together
from the existing RSM fitter, without implementing another OLS routine.

Draw B_sample=B_hat+C_X G L_Sigma^T, with C_X=solve_triangular(R,I),
V_X=C_X C_X^T, iid standard-normal G and L_Sigma L_Sigma^T=Sigma_hat_e.
Column-stacked covariance is Sigma_hat_e tensor V_X. This is a matrix-normal
plug-in ensemble, not a posterior or an exact distribution of true parameters.
No independent-beta or response-noise surrogate is substituted.

Prefer Cholesky for SPD Sigma_hat_e. On failure, use a symmetric spectral PSD
root with tolerance eps*m*||Sigma||_inf. Negative eigenvalues below minus this
roundoff tolerance fail; negatives within tolerance alone are set to zero,
explicitly counted, with raw/effective covariance and reconstruction recorded.
No jitter, shrinkage, response removal or bootstrap. Input covariance must be
finite and exactly symmetric; it is never silently symmetrized.

Use explicit Generator(PCG64(seed)), default seed=777. Draw a flat float64
standard-normal stream, reshape C-order (batch,p,m), response index fastest.
Transform each replica with the same two fixed-size matrix products so changing
B/chunk size cannot change arithmetic grouping. Same-environment prefix and
chunk reproducibility are exact test contracts. Returned arrays are immutable.

One real ensemble of B_max=2000, evaluated at 100,200,...,2000, uses
validation/sensitivity mode. Do not choose B by the smallest moment error.
The moment table uses relative Frobenius errors for the mean and full unbiased
empirical covariance under column vec. These are sampler diagnostics only.

## Future PA rule, recorded before PA results exist

At the first B>=500, compare B against B-100. Stop only if subset identities
are exactly unchanged, global dimension unchanged, and every decision-relevant
singular-value quantile changes by strictly less than 1% relative to
max(abs(q_new),abs(q_old),epsilon_q). Use epsilon_q=float64.tiny solely as
zero protection. If no qualifying comparison through B=2000, use B=2000 and
EARLY_STOP_NOT_REACHED. Validation mode still evaluates every prefix to 2000.
No PA, singular values, subsets or actual early-stop decisions are fabricated
now. Actual Phase 3 status is NOT_APPLIED_PHASE_3.

## Evidence, software and validation

The covariance identity is derived directly in coefficient_monte_carlo.md;
existing Phase 1 conventions/uncertainty are reused. Exact factor reconstruction,
manual iid/diagonal/correlated cases, fixed-seed empirical moments/blocks,
PSD/indefinite failures, immutability and bitwise prefix/chunk tests validate
implementation. Finite Monte Carlo error is not required to be monotone.

Matplotlib is added only to development dependencies to produce the explicitly
requested PNG; it is not part of production sampling or a numerical method.
NumPy/SciPy runtime versions remain locked. No parallel/GPU dependency is added.
No anchor optimization, per-replica payoff, NBI/C-NBI, PA or Phase 4 is included.
Acceptance here is the user's explicit scope decision, not automatic promotion
of the separate proposed early-stop policy or later methodology.
