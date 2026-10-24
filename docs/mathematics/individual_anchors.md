# Individual quadratic anchors and payoff orientation

## Model and directions

Each unchanged full quadratic is f_j(x)=beta0_j+b_j^T x+x^T Q_j x.
The canonical coefficient order is intercept, linears, pure squares, then
lexicographic interactions i<j. Q_ii=beta_ii, Q_ij=Q_ji=beta_ij/2.
`quadratic_responses(RSMFit)` extracts these quantities without refitting or
changing terms. `QuadraticResponse.value/gradient` evaluate f and b+2Qx.
Natural responses are retained. `Direction.MIN/MAX` is explicit metadata;
only the solver objective uses sign +1/-1. The response cloud is never sign-flipped.

For the application: T/MTTF/ROI/OEE MAX; WR/Ra/Rt/Kp MIN.
The requested decision region is ||x||<=r, r=8^(1/4)=1.681792830507429 in
original coded coordinates. It is not a ball in physical units. This ball
excludes the eight factorial corners with norm sqrt(3); the original axial codes
1.682 are also slightly outside r. This is the requested region, not a claim
that the entire CCD lies inside it.

## Classical global quadratic-ball solver

`solve_quadratic_ball(model,radius,direction)` solves a quadratic trust-region
problem. Put x=r z and minimize g^T z+0.5 z^T H z over ||z||<=1, with
H=2*s*r²*Q, g=s*r*b, s=+1 for MIN and -1 for MAX. Divide H,g by the same
positive scale max(||H||_2,||g||_2), or 1 for a constant objective. This numerical
normalization does not change any optimizer or the natural response returned.

Global necessary/sufficient conditions: there exists lambda>=0 with
(H+lambda I)z=-g, H+lambda I PSD, ||z||<=1 and
lambda*(1-||z||²)=0. For a feasible PSD stationary solution, return the
minimum-norm interior solution, including flat directions. For an indefinite
H, a stationary saddle is never accepted as the solution solely for stationarity.

Diagonalize H=V diag(d) V^T, c=V^T g. The multiplier lower bound is
lambda0=max(0,-d_min). If the gradient has no significant component in the
nullspace of H+lambda0 I and the remaining minimum-norm solution fits in the
ball, either it is the PSD interior solution (lambda0=0), or add the necessary
minimum-eigenvalue nullspace component to reach the boundary (hard case).
The sign of that null vector is fixed by its largest-magnitude coordinate.
Ties describe nonunique optima; the selected representative can depend on the
eigenbasis, while objective and certificate are invariant.

Otherwise solve sum_k(c_k/(d_k+lambda))²=1 for lambda>lambda0. The implementation
uses the shifted scalar delta=lambda-lambda0, a monotone norm equation, and
Brent's bracketed scalar root finder. At the singular endpoint its mathematical
limit may be +infinity; no nonfinite final optimizer is accepted. The upper
delta=||c|| bounds the root. No generic nonlinear local solver defines the
classical answer. No normal-equation or covariance inverse is formed.

Numerical choices are explicit: spectral zero margin 16*n_x*eps_float64 after
normalization; secular xtol=float64.tiny, rtol=8*eps, maxiter=256. Validate the
normalized stationarity, complementarity and squared-ball margin with 1e-10;
shifted minimum eigenvalue >= -16*n_x*eps. Failure raises an exception. Store
point, objective, norm, sphere margin, case, iterations, original multiplier,
objective scale and the normalized global certificate. Array results are immutable.
This nullspace handling solves the TRS hard case; it does not authorize a
pseudoinverse or regularization of the response-cloud covariance.

## Response-restricted problem

The second problem adds D_Y²(f(x))<=c as defined in
[multivariate_response_region.md](multivariate_response_region.md). Composing a
quadratic response vector with a quadratic distance is generally quartic and
nonconvex, so its solution is not a trust-region certificate problem.

`solve_response_region_anchor` uses SLSQP with exact objective and constraint
Jacobians. grad_x D²=J_f^T * 2*S_Y^-1(f(x)-phi), computed by two Cholesky solves.
The objective is divided by max(|beta0|,r||b||,r²||Q||), or 1; constraints are
divided by r² and c respectively. Returned values/margins remain unscaled.
Defaults: ftol=1e-11, maxiter=1000; feasibility margins independently checked
with sphere tolerance 1e-9 and response-distance tolerance 1e-8. Active-constraint
reporting uses 1e-6, and is distinct from acceptance feasibility.

Start proposals are deterministic: origin, nonzero {-1,0,1} directions at r/2
and r, the 19 original coded settings, and the eight classical anchors.
Exact duplicates and infeasible proposals are rejected with recorded indices;
all unique feasible starts are used when SLSQP is needed. Every start, terminal
point, objective, margins, success/status/message/iteration count is recorded.
Accept a trial only when solver success AND both true margins satisfy tolerances.
No feasible start is not proof of global infeasibility. No accepted trial raises
an error rather than fabricating an anchor. Select the best accepted natural
objective for its explicit MIN/MAX direction, with no general global claim.

An important exact shortcut: if the globally certified classical anchor is
already response-feasible without tolerance relaxation, it is also a global
optimum on the restricted subset. Reuse it byte-for-byte, record a
SPHERE_GLOBAL_CERTIFICATE trial and the evaluated start proposals. Running a
local optimizer cannot improve a feasible global bound. This occurs for all
eight actual anchors at the cutoffs evaluated here. Synthetic restrictive
regions independently exercise SLSQP multistart and infeasible-success rejection.

## Payoff, Utopia and comparison

`payoff_matrix(models,anchor_points)` returns A_ij=f_i(x_j): rows responses,
columns anchors, both in response order. U_j=A_jj. The complete vector of
responses is evaluated at every anchor; the diagonal is not separately fitted.
Keep payoff_sphere and payoff_response_region independent even when identical.
No additional Nadir estimator or NBI/CHIM construction is implemented.

Anchor membership does not imply that the assembled diagonal U belongs to the
region: each component is optimized at a different x. Counterexample with
S=I, phi=0, c=1/4: anchors (1/2,0) and (0,1/2) both satisfy the region, but
their assembled U=(1/2,1/2) has D²=1/2>c. The real run records this diagnostic
without asserting joint attainability or adding a new constraint on Utopia.

Signed change is f_RC-f_sphere. Deterioration is s*(f_RC-f_sphere), positive
for loss in either direction. Relative deterioration divides by |f_sphere|,
and is undefined if that denominator is exactly zero. Code displacement is
||x_RC-x_sphere||. Reporting "moved" uses displacement>1e-6; this does not change
any optimizer. A response-boundary classification uses D² and cutoff with the
explicit response tolerance. Being outside is not mathematical incorrectness.

## Evidence and validation

Moré (1993), *Generalizations of the trust region problem*, author preprint
MCS-P349-0193, PDF p.3, states global stationarity/PSD/complementarity without
assuming convexity. The spectral/secular implementation is derived above.
Primary source: https://ftp.mcs.anl.gov/pub/tech_reports/reports/P349.pdf.
Bindel's [Cornell course notes](https://www.cs.cornell.edu/courses/cs4220/2026sp/lec/2026-04-20.html)
also distinguish the interior, boundary and singular hard cases. No code from
these sources or the v1 is copied. Sources and reading limits are in
[phase_02_sources.md](../../references/notes/phase_02_sources.md).

Tests cover manual 1/2/3-factor convex MIN/concave MAX, linear boundary,
indefinite and repeated-eigenvalue hard cases, PSD flat directions, constant
response, canonical interactions, finite-difference gradient checks, independent
SciPy multistart comparison, response geometry/scaling, MIN/MAX payoff orientation,
immutable arrays and failure contracts. Earlier RSM/uncertainty tests are retained.
