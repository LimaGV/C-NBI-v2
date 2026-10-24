# Joint coefficient Monte Carlo

Phase 3, ADR 0006 ACCEPTED. The random variable is the complete coefficient
matrix, conditional on the already fitted model and its plug-in residual
covariance. This is not a Bayesian posterior or an exact distribution of the
unknown true parameters. Experimental observations are preserved.

## Construction and covariance derivation

For a fixed full-rank design X (N by p), retain B_hat (p by m), reduced-QR R
(p by p), V_X=(X'X)^-1 (p by p), and raw Sigma_hat_e=E'E/nu (m by m) from
the **same existing RSMFit**, nu=N-rank(X). No second OLS implementation is used.
Let C_X=solve_triangular(R,I); then

\[
C_XC_X^T=R^{-1}R^{-T}=(X^TX)^{-1}=V_X.
\]

If L_Sigma L_Sigma'=Sigma_hat_e, draw G with p by m independent N(0,1)
entries and construct

\[
B^{(b)}=\hat B+C_XG^{(b)}L_\Sigma^T.
\]

Using column-stacked vec and vec(AGD)=(D^T tensor A)vec(G):

\[
\operatorname{vec}(B^{(b)}-\hat B)
 =(L_\Sigma\otimes C_X)\operatorname{vec}(G^{(b)}),
\]

\[
E[B^{(b)}]=\hat B,\qquad
\operatorname{Cov}[\operatorname{vec}(B^{(b)})]
 =(L_\Sigma\otimes C_X)I_{pm}(L_\Sigma^T\otimes C_X^T)
 =\hat\Sigma_e\otimes V_X.
\]

Consequently Cov(B_j)=MSE_j V_X and Cov(B_j,B_k)=Sigma_hat_e[j,k] V_X.
This preserves correlations both within a response's coefficients and across
responses. Replacing Sigma_hat_e by diagonal MSE or drawing each beta
independently does not satisfy the specified joint covariance.

For turning: N=19, p=10, m=8, nu=9; B_hat and G are 10 by 8, C_X is 10 by 10,
L_Sigma is 8 by 8, and the column-vec covariance is 80 by 80.

## Numerical factors and PSD handling

The design root uses upper-triangular solve against I, never np.linalg.inv.
Reconstruction is checked against the original fitter's V_X. Residual
Cholesky is preferred for SPD input. Input must be finite and exactly symmetric;
there is no implicit symmetrization, jitter, shrinkage or diagonal regularization.

On Cholesky failure, let s=max(abs(Sigma)), A=Sigma/s (or zero if s=0).
Compute a symmetric eigendecomposition of A. The explicit absolute eigenvalue
tolerance in original units is tau=eps64*m*||A||_inf*s, algebraically
eps64*m*||Sigma||_inf, computed after scaling to reduce overflow risk.
An eigenvalue below -tau fails. Only negative eigenvalues within that roundoff
bound are replaced by zero. Nonnegative eigenvalues are kept, including small
positive ones; this is not a statistical rank threshold. The root is
U diag(sqrt(max(lambda_A,0))*sqrt(s)). The raw covariance, effective reconstruction,
tolerance, method and count of zeroed negatives are exposed in the result.
Exactly zero covariance yields deterministic samples and an undefined relative
covariance error (None with ZERO_THEORETICAL_COVARIANCE), not NaN.

## API and deterministic stream

`cnbi_v2.uncertainty.sample_coefficient_ensemble(B_hat,R,Sigma,n_samples,...)`
returns a frozen CoefficientEnsemble with immutable bytes-backed float64 arrays.
`iter_coefficient_batches` provides immutable batches from the same algorithm.
Counts and batch sizes are positive integers; seed is a nonnegative integer,
default 777. Inputs are copied and never changed. Labels are explicit and unique.

Each call creates local Generator(PCG64(seed)); it never changes a global RNG.
Normals are a **flat** float64 stream reshaped C-order to (batch,p,m):
flat offset = replica*(p*m)+term*m+response. The response varies fastest.
Each replica uses the same two fixed-size matrix products regardless of batch
size, preventing a batch-dependent regrouping of floating-point arithmetic.
Output indexing is samples[replica,term,response]. Column vec is used only for
covariance diagnostics, equivalently sample.reshape(-1,order="F").

Same inputs/seed in the same supported numerical environment produce bitwise
identical arrays, including shorter prefixes and different chunk sizes. Tests
cover 1, 3, 100, 333 and 2000-sized chunks and 100/500-replica prefixes.
No cross-version, cross-BLAS or cross-platform bitwise guarantee is claimed;
the lock, Python/platform and object-byte hashes identify the archived run.

## B sensitivity

The real workflow generates **one** ensemble of 2,000 replicas (160,000 normal
draws), default batches of 100, then evaluates the 20 nested prefixes
B=100,200,...,2000. It does not execute 20 independent simulations or save
20 ensembles. Larger ensembles occur only in synthetic distribution tests.

For every prefix, use the arithmetic sample mean and unbiased empirical
covariance K_hat_B of its column-vec replicas (divisor B-1). Diagnostics are

\[
E_\mu(B)=\frac{\|\bar B_B-\hat B\|_F}
 {\max(\|\hat B\|_F,\epsilon)},\quad
E_K(B)=\frac{\|\hat K_B-K\|_F}{\|K\|_F},\quad
K=\hat\Sigma_e\otimes V_X,
\]

with epsilon=eps64=2.220446049250313e-16. The real target K is obtained
independently from the existing coefficient_covariance(fit), not reconstructed
from the sampler's empirical covariance. All 80 coefficients and their complete
80 by 80 covariance enter the diagnostics in native response units.
These Frobenius ratios weight numerically larger components more strongly;
tests separately verify covariance blocks and simple identity/diagonal/correlated
cases. The aggregate ratio alone does not validate every small-variance entry.

Finite-seed errors fluctuate. Neither the tests nor the analysis requires local
monotonicity, selects B by its smallest observed error, or makes moment errors
a scientific stopping rule. Synthetic mean/covariance tests use fixed seeds,
50,000 replicas and six-standard-error tolerances from Gaussian/Wishart moments
(SE(cov_ij)=sqrt((K_ii*K_jj+K_ij^2)/(B-1))).

## Future PA early stop (PROPOSED)

The machine-readable [policy](../policies/pa_early_stop_policy.json) was written
before the real results. It is **not applied in Phase 3**. In future production,
evaluate B=100:100:2000; the first eligible comparison is B=500 versus 400.
At the first eligible checkpoint satisfying all three conditions, stop:

1. Exactly the same selected subset identities, not merely counts.
2. Exactly the same global dimensional decision.
3. For the same identities of every singular-value quantile actually used in
   decisions, abs(q_B-q_previous)/max(abs(q_B),abs(q_previous),epsilon_q) <0.01.

epsilon_q=float64.tiny=2.2250738585072014e-308, the smallest positive normal
float64, protects the zero denominator without introducing a material absolute
stability threshold. Two zeros give zero change; a zero and a nonzero normal
value give relative change one. This floor differs from the mean-norm epsilon.
If no eligible checkpoint meets the joint rule, use 2000 and record
EARLY_STOP_NOT_REACHED (not an execution error). Development/validation must
still allow all 20 prefixes through 2000. No PA/subset/singular-value results
or future PA CSV columns are manufactured in this phase.

The present run is validation/sensitivity mode with status NOT_APPLIED_PHASE_3.
Future production can consume the batch iterator and prefixes when PA exists;
no generic PA framework or stopping comparator is implemented prematurely.

## Reproduction and scope

`uv run python -m scripts.validation.turning_coefficient_mc --run-id <fresh_id>`
creates results/phase_03_coefficient_mc/<fresh_id>; --output selects a fresh
directory and --seed changes the explicit configuration. Nonempty directories
are refused. All artifacts and scientific/code inputs have SHA-256 manifests.
See the [applied report](turning_coefficient_mc.md) and
[verification gate](../phase_3_verification.md).

The original-coded Phase 2 coefficients are checked against its archived CSV
with rtol=1e-12, atol=1e-13 to permit platform-level floating-point differences.
The raw literal workbook is checked by hash and modification timestamp before
and after. Published coefficients are not used in this workflow.
No anchor reoptimization, per-replica payoff, response perturbation, bootstrap,
shrinkage, NBI/C-NBI, CHIM, PA or Phase 4 is executed.

Software documentation checked in this phase: [NumPy PCG64](https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html),
[standard_normal](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.standard_normal.html),
[SciPy triangular solve](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_triangular.html)
and [Matplotlib direct Figure usage](https://matplotlib.org/stable/users/faq.html).
These substantiate API usage; the covariance result is the derivation above,
not a literature claim inferred from software documentation.
