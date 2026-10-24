# 0005 — Individual anchors and experimental response-cloud restriction

- Status: EXPERIMENTAL
- Date: 2026-10-24
- Branch: feature/02-individual-anchors-response-region
- Parent: Phase 1, PR #4, squash 64b09f9 (all local/remote checks passed).
- Scope: nominal individual anchors and two separate payoff matrices only.

## Decision and definitions

Compare optimization of each complete quadratic over ||x||<=8^(1/4) with the
same problem plus (f(x)-mean(Y))^T S_Y^-1(f(x)-mean(Y))<=c, where S_Y is the
observed response-cloud sample covariance with denominator n-1. All original
responses retain their natural units and directions. This is an experimental
descriptive region; c=chi2.ppf(.95,m) is explicitly a legacy diagnostic cutoff,
not an exact confidence threshold for the current fixed DOE.

The ball problem uses a spectral secular-equation solver, including PSD
interior solutions and indefinite/singular hard cases, with global KKT/PSD
certificates. The response restriction is generally quartic/nonconvex; analytic
gradients and deterministic feasible multistart SLSQP provide best feasible
converged solutions found, not a global certificate unless the classical global
anchor already satisfies the response constraint. No pseudoinverse, response
selection, jitter or shrinkage of S_Y is allowed. Cholesky solves evaluate D².

## Coding evidence and explicit deviation from the original equivalence gate

Original local NBI Revisão.xlsm, SHA256
7792a25a8c88d29206665d8797587dc6a11e932e1a8bba0a1ac8b539385f7d4e,
Original Data!B4:H22, contains IDs, literal original coded coordinates C:E and
physical coordinates F:H. IDs and physical coordinates match the incorporated
CCD exactly. Original axial codes are +/-1.682, not reconstructed from Table 3
or replaced with theoretical alpha. Factorial codes are +/-1 and centers zero.

Refitting unchanged Y at those codes is not an equivalent reparameterization
of the physical quadratic: maximum fitted discrepancy reaches 2.5658% of a
response range. The equivalence gate therefore FAILED and is never relabelled
PASSED. After this was reported, the owner clarified: "a planilha esta correta
o artigo esta errado". This phase prioritizes verified original spreadsheet
codes, explicitly as a DISTINCT coded-input case. Prior physical fits and their
results remain untouched. There is no verified continuous physical/coded map;
new anchor physical coordinates are undefined and no factor_coding API is made.
The sphere radius remains the requested theoretical 8^(1/4), separately from
the original spreadsheet's rounded axial coordinates. Factorial corners have
norm sqrt(3)>alpha; this ball does not contain every CCD point.

## Evidence, alternatives and limits

Maia (2020), *Método de Interseção Normal à fronteira por escores rotacionados
em espaço elíptico de solução*, local Tese_2021012.pdf: pp.19-21 and 84
directly inspected. The stage at which the constraint is applied is antecedent;
his ideal-centered/prediction-covariance discussion is NOT identified with our
mean-centered response-cloud covariance. The cloud formulation is explicitly
defined/derived here, not attributed to Khuri/Conlon without direct evidence.
Threshold candidates and source limits are documented in multivariate_response_region.md.

Promotion to ACCEPTED requires separate review of coding, cutoff sensitivity,
statistical interpretation and observed tradeoffs. No automatic adoption of RC,
NBI/C-NBI, CHIM, uncertainty simulation, PA, shrinkage or later stage is implied.
Confining complete response vectors at individual anchors does not guarantee
that the diagonal Utopia assembled from different anchors is in that region.
A synthetic counterexample and a real Utopia distance diagnostic make this
logical limitation explicit; no new Utopia/Nadir optimization is added.
