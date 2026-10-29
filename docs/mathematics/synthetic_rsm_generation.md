# Phase10B — synthetic CCD, noise and full quadratic RSM

## Scope and provenance

This is a synthetic experiment-generation protocol, not a multiobjective campaign.
Its specification is the owner's Phase10B task (2026-10-29). Mathematical
derivations below are internal definitions, not claims attributed to literature.
The 27 approved Phase10A configurations are consumed byte-for-byte from
`results/phase_10_synthetic_generation/structural_20261029/`, commit
`489aa0e2b4703c0e39b0bff2623209e5a177a94b`. PR14 was integrated by merge commit
`d68aef72532ed0e39bd256b3e9dcb75f30c6a76b`; main CI40906784465 passed on Ubuntu
and Windows. No anchor calibration or signed-correlation selection is performed.

The source/protocol/tests are committed before official noise generation.
`docs/policies/synthetic_generation_10b.json` is the machine-readable protocol.
The frozen-input manifest protects every tracked main file except the seven
explicit current-state documentation/ignore files. Previous source, tests,
datasets, results, figures, licenses and Phase10A inputs remain unchanged.

## True functions and conventional training CCD

For each frozen row-oriented anchor matrix A (m,nx),

\[
 f_j(x)=\|x-a_j\|^2,\quad f_j(a_j)=0,\quad \text{all directions MIN}.
\]

These functions are defined on all real factor coordinates. Training uses the
full rotatable CCD: lexicographic {-1,+1} factorial rows, then negative/positive
axial rows in increasing factor order, then five separate all-zero center rows.
The axial radius is alpha=2^(nx/4). No projection, row deletion or factor recoding.

| nx | Factorial | Axial | Center | n | p | Residual df | Pure-error df | LOF df |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 4 | 4 | 5 | 13 | 6 | 7 | 4 | 3 |
| 3 | 8 | 6 | 5 | 19 | 10 | 9 | 4 | 5 |
| 5 | 32 | 10 | 5 | 47 | 21 | 26 | 4 | 22 |

The future optimization region is the ball ||x||<=alpha. At nx=3, all eight
factorial rows have norm sqrt(3)>8^(1/4); they remain unchanged and are marked
outside. nx=2 factorial rows are on the boundary; nx=5 factorial rows are inside.
Outside training rows are valid oracle evaluations, not domain failures.

The canonical full quadratic terms are the existing `quadratic_term_names(nx)`:
intercept, x1..xnx, x1^2..xnx^2, then xk*xl in lexicographic k<l order.
p=(nx+1)(nx+2)/2. Full column rank is required by the existing fit API.

## Five independent replicas and one noise level

For each structural cell and r=1..5, Y^(r)=F_CCD+epsilon^(r), with independent
zero-mean Gaussian errors across rows, responses and replicas. Including all five
center rows, let S_fj²=var(F_CCD[:,j],ddof=1). Freeze

\[
 \sigma_j^2=S_{f_j}^2/19,\qquad
 S_{f_j}^2/(S_{f_j}^2+\sigma_j^2)=0.95.
\]

This is a variance proportion in expectation. It does not constrain realized
noise variance, training R², LOOCV R² or external R². The source search across
docs/src/scripts/tests at d68aef7 found no previously validated conflicting 95%
signal protocol. Phase10A explicitly excluded noise. No retuning occurs.

Every center row receives its own random error. Negative noisy measurements,
extreme values and nonzero sample noise means remain unchanged. There is no
clipping, rounding, log transform, recentering, correlation induction or rescaling.
The CCD, anchors, true responses and sigma vector are identical across replicas.

Master seed:20261029. Derive a 128-bit seed as the first16 bytes of SHA256 of
ASCII `C-NBI-v2/phase10b/v1/{master}/{scenario_id}/{replica_id}`, big endian.
Use `Generator(PCG64(seed))`, with its normal draw of shape (n,m). Replica0 denotes
only the external Sobol stream; replicas1..5 denote noise. The namespace is
separate from Phase10A. No native Python hash, mutable spawn counter, global RNG,
worker ID or execution-order seed is involved. Versions and byte hashes are saved.
Statistical independence is a property of the specified PRNG streams and iid
generation, not an assertion that finite-sample correlations are exactly zero.

27 cells ×5 replicas give135 joint RSMs,3555 experiment rows and990 response
models. Long-form observations contain28530 scalar response values; these are
not28530 independent experimental runs. All135 instances will be shared by future
methods; no algorithm-specific experiment or model is generated.

## Fitting and independent analytic certification

Only `cnbi_v2.model.fit_multivariate_rsm(X_factors,Y_noisy)` fits a model.
`diagnose_rsm` supplies the existing training/LOOCV/ANOVA diagnostics. Neither API
is modified. No new OLS implementation, term selection or convexity constraint.

Independently expanding the distance function gives intercept ||a_j||²,
linears -2*a_j, pure squares1 and interactions0. Each of27 noiseless CCD fits must
recover these coefficients and direct-distance predictions within
100*float64_eps*condition(X)*max(1,max(abs(B_true))). This is a forward-error
implementation certificate, not a sixth experimental replica or noisy-fit filter.

For noisy models, preserve B_hat and B_hat-B_true, per-term absolute error,
per-response L2/relative-L2 error. A per-term relative error is defined only when
abs(beta_true)>1e-12*L2(B_true_response). Zero/near-zero denominators are explicitly
undefined; exactly-zero true interaction errors are diagnosed separately. No
coefficient is corrected toward its true value.

The fitted Hessian has diagonal2*beta_kk and off-diagonal beta_kl. Record its
eigenvalues and strict convexity when the smallest eigenvalue>0. This is an
observation about the estimated polynomial, never an imposed condition.

## Diagnostics and covariance

Retain all statistics returned by `diagnose_rsm`, including their explicit status:
SSE,SSR,SST,MSE,S,R²,adjusted R²,PRESS,LOOCV predicted R²,global F/p,pure-error and
lack-of-fit SS/MS/df/F/p. Exact factor grouping identifies the five centers;
u=2^nx+2*nx+1 unique factor configurations, PE df=4,LOF df=u-p. No new statistical
formula replaces the validated API. LOF p<0.05 is reported without rejection of
the experimental instance or retuning; nominal false positives are possible.

Residual covariance is the unaltered API result E.T@E/(n-p). Save its rank,
eigenvalues and condition only when full rank. A singular covariance is legitimate
(nx2,m8 has rank at most7). No jitter, shrinkage, symmetrization, eigenvalue
clipping or positive-definiteness enforcement is performed. Small negative
computed eigenvalues attributable to floating-point rounding are recorded as is.

The structural correlation targets describe true responses over the ball, not
responses on the CCD. Record true-CCD and noisy-CCD Pearson matrices and their
mean absolute/signed off-diagonal correlations; never require agreement with a
structural target or recalibrate anchors.

## External validation and replica variability

After all135 fits, generate4096 independent uniform-volume Sobol ball points per
structural cell with stream0, reusing the unchanged Phase10A `sample_ball` transform
(12-bit sample exponent, scrambled32-bit Sobol coordinates, open-cell midpoint,
normal-quantile directions and radial inverse CDF). All five replicas share the
same points and direct-distance truths. Save points/truth and hashes separately
from the prediction-only model interface. They do not affect noise, fits or
replica selection. This is independent external validation, distinct from LOOCV.

For prediction error d=prediction-truth, export responsewise RMSE=sqrt(mean(d²)),
MAE=mean(abs(d)),R²external=1-sum(d²)/sum((truth-mean(truth))²),max(abs(d)).
These external-oracle metrics are new validation measures, not duplicate training
statistics. Record mean/maximum pointwise sample SD of predictions across all five
replicas, with ddof=1; no best replica is retained in place of another.

Summaries give equal weight to each response model, grouped by nx,delta,target,
structural cell and overall. Quantiles use NumPy's linear rule. These descriptive
aggregations do not establish benchmark performance or causal target effects.
Different structural cells change anchors and m as designed; no inferential
comparison or hyperparameter tuning is conducted.

## Storage, figures and interpretation limits

CSV values use17 significant digits for float64 round trips. NPZ arrays are
float64, allow_pickle=False, with dtype/shape/C-order little-endian byte hashes.
The separate model index validates identity, term order, shape and coefficient
hash. `load_models` returns an oracle-free polynomial prediction interface and
never refits; future optimizers receive only these noisy RSMs.

Six English diagnostics use PNG600dpi and vector PDF, consistent typography and
no grids. Prediction examples are predefined as nx2/3/5,delta3,rho060,replica1,y1,
external indices0:4096:16. Residual scatter/QQ use fixed stride17; pooled residuals
are divided by known sigma, not studentized. Identity/zero/0.95 lines are scientific
references. The observed signal/noise variance ratio is not training R².

Reproducibility requires pinned numerical libraries/BLAS; exact experimental
noise arrays are reproduced in reverse order locally. Cross-platform fit results
are verified with numerical tolerances, not promised bitwise identical BLAS.
The archive is frozen; diagnostic weaknesses, negative measurements, LOF rejections
and singular covariance are retained. No multiobjective optimization, Pareto
reference/metrics, algorithm comparison, new structural cell or later phase runs.
Original raw data and excluded-material licenses are unchanged.

Software API documentation consulted through Context7: official NumPy
[parallel RNG](https://github.com/numpy/numpy/blob/main/doc/source/reference/random/parallel.rst)
and Matplotlib [figure export](https://github.com/matplotlib/matplotlib/blob/main/galleries/users_explain/figure/figure_intro.rst).
These document software behavior, not scientific validity.
