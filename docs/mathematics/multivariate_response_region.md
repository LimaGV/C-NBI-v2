# Experimental multivariate response-cloud region

## Definition and distinction

For observed canonical Y in R^(n*m), phi=mean(Y) and
S_Y=(Y-phi)^T(Y-phi)/(n-1). Define D²(v)=(v-phi)^T S_Y^-1(v-phi).
The RC constraint is D²(f(x))<=c in the full eight original responses.
This is a descriptive cloud region. No response rounding, manual scaling,
sign inversion, rotated factors or 28 pairwise ellipse intersections replace it.

S_Y measures joint experimental response variation across the DOE. It is not
the residual covariance Sigma_hat_e, and is not mean-prediction covariance
h(x)*Sigma_hat_e. Those matrices answer different questions. The requested
mean-centered cloud is an explicit experimental definition, not a theorem
that all admissible physical outcomes or confidence sets have that shape.

Mahalanobis invariance follows directly: if v'=Av+a, phi'=Aphi+a and
S'=A S A^T with nonsingular A, then D'²=D². Thus full covariance handles
different natural response scales/correlations without standardizing Y first.
This identity, including a non-diagonal linear transform, is tested.

## Numerical admissibility

`response_cloud_region` computes mean/covariance directly from unchanged Y,
using shifted centering to reduce cancellation. Record covariance, eigenvalues,
rank, spectral condition number and logdet. Numerical rank uses
eigenvalue>eps*max(n,m)*lambda_max in the supplied units; require full rank
and positive smallest eigenvalue, then Cholesky factorization. No response is
discarded and no pseudoinverse, diagonal jitter or shrinkage is allowed.
Extremely scaled singular numerical representations fail this explicit gate.

S_Y=L L^T; D²=||solve(L,v-phi)||². Computing an explicit inverse is unnecessary.
For in-sample distances a useful identity is sum_i D_i²=m*(n-1), when covariance
has full rank; derivation is trace(S_Y^-1*(n-1)S_Y). This is a numerical
consistency check, not a confidence coverage theorem. Report actual coverage,
minimum, median, maximum and quantiles (NumPy method='linear').

For this dataset, rank=8, condition≈2.17105e9 and logdet≈-36.22716 in canonical
units. The large condition reflects unequal scales and dependence, but does
not fail the stated numerical-rank/Cholesky gate; sum D²≈144 provides a separate
consistency check. No claim of exact statistical calibration follows.

## Threshold candidates and their meanings

Here n=19, m=8. The DOE intentionally varies factor settings; its responses
are not established as IID draws from one homogeneous multivariate normal
population. A model-predicted response vector at a chosen x is not automatically
a new independent observation from that population either.

| Candidate | Meaning | Exact/Approx | Suitable here? | Status |
|---|---|---|---|---|
| chi-square_m(q) | Population observation content with known mean/covariance under MVN | Exact only under those assumptions; estimated plug-in is not exact here | Legacy diagnostic comparison | EXPERIMENTAL |
| Hotelling mean ellipsoid | Confidence for one population mean, n*(mean-mu)^T S^-1*(mean-mu) | Exact under IID MVN, n>m | Different target from the response cloud/predicted vector | NOT_ADOPTED |
| Finite-sample new-observation F region | Prediction of one independent future IID MVN observation | Exact in that homogeneous setting | Fixed DOE and fitted mean do not establish its applicability | NOT_ADOPTED |
| Multivariate tolerance region | Confidence gamma that a region covers population fraction q | Requires distinct content/confidence definitions and method | Not established by plugging in q=.95 | UNVERIFIED |
| Empirical MD² quantile | Descriptive boundary of the fitted in-sample cloud | Not a confidence/prediction guarantee | Sensitivity diagnostic only | DIAGNOSTIC |
| Khuri/Conlon optimum-distance framework | Uncertainty-aware compromise relative to individual optima | Different target and covariance | Not identified with the cloud formula above | NOT_ADOPTED |

The legacy API is deliberately `legacy_chi_square_threshold(m,q=.95)`, not
`exact_confidence_threshold`. Selected primary c=chi2_8(.95)=15.50731305586545.
Its nominal 95% is not an established confidence level for this fitted cloud.
Sensitivity also evaluates the empirical MD² .95 quantile (12.2432703457) and
chi2_8(.99) (20.0902350297). No candidate is promoted to canonical by this run.

For clarity, under IID MVN the mean-ellipsoid bound on
(mean-mu)^T S^-1(mean-mu) is m*(n-1)/(n*(n-m))*F_m,n-m(q).
This is not an observation-cloud threshold. An independent future observation
minus the sample mean has covariance (1+1/n)Sigma, independent of S under those
assumptions. The corresponding prediction bound is
m*(n+1)*(n-1)/(n*(n-m))*F_m,n-m(q). This mathematical derivation exposes why a
mean confidence region and future-observation region have different sizes.
Neither formula is implemented as the current method or justified for this DOE.
NIST explicitly distinguishes hypothesis-testing Hotelling limits from control
charts and Phase I from Phase II; selecting a familiar F cutoff alone does
not resolve the inferential target. C-RC-02 remains UNVERIFIED.

## Maia/Khuri antecedent and limits of attribution

Maia's **2020** doctoral thesis (not his 2013 master's dissertation),
*Método de Interseção Normal à fronteira por escores rotacionados em espaço
elíptico de solução*, states at printed p.21 (PDF 38) that the restriction
must be considered when defining anchor points. Printed p.84 (PDF 101)
describes adding it during individual optimization and reports frontiers
inside the considered ellipses. Both pages were rendered and read directly.
This supports the antecedent at the anchor-definition stage, not proof that
the same construction/calibration transfers unchanged to eight original responses.

Printed pp.19-21 discuss Khuri/Conlon with phi as individual ideal values and
prediction-variance quantities. They do NOT directly establish our phi=mean(Y),
S_Y=response-cloud covariance. We intentionally use a different descriptive
definition requested for this experiment and record its derivation/status.
The original Khuri/Conlon (1981) article was metadata-verified in Zotero but its
full text was not obtained; no secondhand equation is attributed as directly read.

## Evidence

Primary sources and reading coverage: [phase_02_sources.md](../../references/notes/phase_02_sources.md).
NIST mean/covariance definition:
https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc341.htm.
Hotelling mean-test distribution and its stated limits of direct application:
https://www.itl.nist.gov/div898/handbook/pmc/section5/pmc543.htm.
No bootstrap, coefficient Monte Carlo, covariance shrinkage or automatic
methodological acceptance is implied by these descriptive computations.
