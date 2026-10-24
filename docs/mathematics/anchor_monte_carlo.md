# Coefficient uncertainty propagated to anchors and payoffs

Phase 4, ADR 0007 ACCEPTED for the explicitly requested scope. Consume the exact
Phase 3 coefficient ensemble; no draws, fit, covariance estimation or response
rescaling occurs here. No response-region (RC) constraint is applied.

## Model, optimization and payoff definition

For b=1,...,2000 and j=1,...,8, extract the existing full quadratic representation:

\[
f_j^{(b)}(x)=\beta_{0j}^{(b)}+b_j^{(b)T}x+x^TQ_j^{(b)}x.
\]

Canonical terms: intercept,x1,x2,x3,x1^2,x2^2,x3^2,x1*x2,x1*x3,x2*x3.
The unchanged extraction puts beta_ij/2 in both symmetric off-diagonal entries
of Q, so x'Qx includes the full beta_ij*x_i*x_j. The fitted-model entry point
now delegates to the same extraction exposed for coefficient arrays; no fake
RSMFit or duplicate coefficient mapping is created.

With alpha=8^(1/4)=1.681792830507429, independently solve every objective over
||x||_2<=alpha in the same original-coded space used by Phases 2 and 3:

\[
x_j^{*(b)}\in\arg\operatorname{opt}_{\|x\|\le\alpha}f_j^{(b)}(x),
\quad F_{bj}^*=f_j^{(b)}(x_j^{*(b)}),\quad
A_{ij}^{(b)}=f_i^{(b)}(x_j^{*(b)}).
\]

Directions in order T,MTTF,WR,Ra,Rt,Kp,ROI,OEE:
MAX,MAX,MIN,MIN,MIN,MIN,MAX,MAX. They are explicit, never inferred from signs.
The chain is B[b] -> models[b] -> optimized anchors[b] -> raw payoff[b].
Rows of payoff are evaluated responses; columns are the corresponding anchors.
Every entry uses the same replica's coefficients and anchor points.
Its diagonal equals F_star exactly in the supported same numerical environment;
it is already the allowed Utopia diagnostic, not a multivariately feasible claim.

Shapes: coefficients (2000,10,8), anchors (2000,8,3), optimal values (2000,8),
norms/cases/locations (2000,8), payoffs (2000,8,8). Response axes are permuted
together in tests, including both payoff axes. Natural objective orientation
and scales are retained; the solver's internal MIN conversion does not flip
saved objectives or payoffs. No min-max, Utopia/Nadir, amplitude or z-score scaling.

## Why nominal fixed points do not propagate optimizer location

In general x_j_star[b] differs from x_j_star[nominal]. A procedure evaluating
perturbed models at a fixed nominal anchor captures variation in the response
at that point, while its optimizer coordinate remains a deterministic constant.
It therefore does not propagate coefficient uncertainty into that location.

For an explicit example, maximize f_theta(x)=-(x-theta)^2 on |x|<=1 with |theta|<1.
Its coefficients are (-theta^2,2*theta,-1), x_star(theta)=theta and optimum zero.
Holding x_nominal=0 fixed instead gives location zero for every theta and value
-theta^2. These are different random objects. The example is tested directly;
it describes the distinction without attributing unverified behavior to a paper.

Reoptimization for every coefficient realization is an explicit characteristic
of v2 (C-MC-04). It is not evidence that a sampled RSM optimum is a true physical
optimum. Prior model-quality, coding and plug-in approximation caveats persist.

## Solver and independent acceptance checks

Use the unchanged solve_quadratic_ball spectral global trust-region solver:
secular equation, singular hard case, shifted PSD condition and KKT certificate.
See [individual_anchors.md](individual_anchors.md). No SLSQP/multistart/fallback
or new tolerance is introduced. The Phase 4 layer always invokes it with its
existing default certificate_tolerance=1e-10.

For sign s=+1 for MIN or -1 for MAX, z=x/alpha, use the solver's positive scale c:
H=2*s*Q*alpha^2/c, g=s*b*alpha/c and lambda=mu*alpha^2/c. Independently recompute
and require the same existing certificate bounds:

- Finite point, objective, norm and certificate fields; correct dimensions,
  direction/radius, declared convergence, and original tolerance.
- The reported c agrees with max(||2*s*Q*alpha^2||_2,||s*b*alpha||), or one for a
  flat function, within the existing eps64*16*n_x numerical bound. The verifier
  obtains the symmetric operator norm from eigenvalues.
- z'z<=1+1e-10, lambda>=0, ||Hz+g+lambda*z||<=1e-10,
  |lambda*(1-z'z)|<=1e-10 and lambda_min(H)+lambda>=-eps64*16*n_x.
- Stored diagnostics also pass their bounds, point norm is consistent, and
  re-evaluating the same model at the point exactly reproduces its saved value.

Stationarity, complementarity, shifted minimum eigenvalue, normalized multiplier,
normalized squared norm and tolerance are archived per anchor (2000,8,6).
The existing solver uses numerical linear algebra internally unchanged; this
phase adds no CHIM/edge/singular-value analysis or dimensional SVD workflow.

For radial reporting, tau=alpha*certificate_tolerance is derived conservatively
from the existing normalized squared-norm bound. Label BOUNDARY when
abs(||x||-alpha)<=tau and INTERIOR when ||x||<alpha-tau. A certified point's
allowed roundoff overshoot lies within tau. This is a unit conversion of the
solver tolerance, not a separately fitted scientific cutoff.

Original solver cases are retained: INTERIOR_OR_PSD_MINIMUM_NORM,
BOUNDARY_SECULAR, BOUNDARY_HARD_CASE. Flat/PSD minimum-norm optima belong to the
first case. The solver-case table counts secular boundary separately from hard
cases, with other/failure counts; its categories sum to B for each response.
Radial interior/boundary fractions are separate geometric diagnostics, since a
zero-multiplier PSD optimum can itself lie on the boundary.

## Failures and immutable results

The serial public API reoptimize_coefficient_ensemble(samples,n_factors,directions,
radius,response_names=...) returns a frozen AnchorEnsemble with bytes-backed
immutable numeric, Boolean and fixed-width Unicode arrays. Input arrays and
nominal reference objects are never modified. No RNG or inter-replica solver
state is used. Same inputs in the same supported environment yield bitwise
equal numeric results; deterministic permutation/prefix/isolation tests cover
this. Cross-platform equality to archived nominal values uses the documented
rtol=1e-12/atol=1e-12-level comparison, not a cross-BLAS bitwise promise.

Every solve and certificate failure is logged with one-based replicate_id,
response, failure stage/type and message. Its original position stays NaN and
its validity mask false; no nominal, previous, zero, skipped-index or alternative
solver substitute is used. Other valid anchors retain their indices. A payoff
requires all that replica's certified anchors, finite entries and the exact
diagonal identity. Payoff failures are logged separately from solve counts.

If any solve/payoff is incomplete, save arrays, masks, logs and actual counts,
including per-response solver cases. Refuse distribution/prefix summaries over
a silently reduced ensemble; their CSVs remain header-only and metadata marks
INCOMPLETE_FAILURE_NO_DISTRIBUTION_SUMMARIES. CLI exits nonzero. The desired
16000/16000 is an expectation, not a hard-coded success result.

## Descriptive statistics and prefix sensitivity

Nominal Phase 2 anchors/optima are loaded from the pinned archived CSV solely
as diagnostic references. For each response compute d_bj=||x_star[b,j]-x_nom[j]||
and delta_f_bj=F_star[b,j]-F_nom[j]. Displacement summary: mean, median, sample
std, q05,q25,q75,q95,max; also radial interior/boundary fractions. Optimal-value
summary: mean,median,sample std,q05,q25,q75,q95,min,max, plus selected delta_f
statistics. Full delta_x and delta_f arrays are archived. Signed delta_f is
variation of an estimated optimum across different models, not deterioration.

Use unweighted NumPy linear quantiles and std(ddof=1). These describe the frozen
plug-in ensemble, not confidence/credible intervals or a new inference method.

Analyze all 20 prefixes B=100,200,...,2000 without rerunning any optimizer:
per-response mean/median/q95 displacement and boundary fraction. Payoff prefix
diagnostic is E_A(B)=||mean(A[:B])-mean(A[:2000])||_F /
max(||mean(A[:2000])||_F,eps64), with eps64=2.220446049250313e-16.
The full-ensemble mean is a descriptive target; E_A(2000)=0 by definition,
not proof of Monte Carlo convergence to a known population mean. Native-scale
Frobenius weighting emphasizes larger components. No monotonicity is required.

No early stop is applied. The Phase 3 PA policy remains PROPOSED, pending actual
PA/quantiles/dimensional/subset outputs in a separately authorized phase.

## Canonical evidence and reproduction

The real loader pins both Phase 3 NPZ and metadata SHA-256, the original clean
scientific commit 5a102dd337a5c9b7108fac6997b612c7d02a8684, raw dataset hash,
seed 777, orders, dimensions, checkpoint schedule and sample-array byte hash.
It validates the single samples key, finite float64 (2000,10,8) and fails on any
inconsistency. The historical source commit and all 20 input Git blobs were
also checked during Phase 4 preflight. Updated Phase 4 source files are not
misrepresented as byte-identical to every historical Phase 3 implementation file.

Run `uv run python -m scripts.validation.turning_anchor_mc --run-id <fresh_id>`;
--output selects a fresh directory. Nonempty output directories are refused.
No source XLSM/PDF/Excel session is required. The raw, nominal anchor CSV and
coefficient ensemble are checked unchanged after propagation. Manifest records
actual source commit/dirty, inputs, configuration, outputs and serial timing.
NPZ strings are fixed-width Unicode, loaded/saved with allow_pickle=False.

See [applied report](turning_anchor_mc.md) and [verification](../phase_4_verification.md).
No new dependency, parallel executor, shrinkage, bootstrap, RC, CHIM, edge matrix,
PA, subset decomposition, Nadir estimator, NBI/C-NBI or Phase 5 is introduced.

API documentation checked via Context7: [NumPy quantile](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html),
[std](https://numpy.org/doc/stable/reference/generated/numpy.std.html),
[savez_compressed](https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html)
and [Unicode types](https://numpy.org/doc/stable/user/basics.types.html).
Software documentation supports API use; C-MC-05 is the explicit derivation above.
