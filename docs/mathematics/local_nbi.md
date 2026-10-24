# Local NBI and internal lattice-resolution sensitivity

Phase6, ADR0010 ACCEPTED in the explicitly requested scope. Inputs are the exact
37 B=2000 identities, current nominal originally coded RSMs and the nominal
sphere payoff/anchors. No fit, stochastic coefficients, anchor optimization,
RC or PA selection is run. Scientific source context is separated from the
explicit definitions in [phase_06_sources.md](../../references/notes/phase_06_sources.md).

## Geometry and normalization

For subset C of size k, take A_C=A_nom[C,C]. Rows are responses, columns their
anchors in the same response order. Let s_i=+1 for MIN and -1 for MAX,
G_C=D_s A_C, u_i=G_ii and a_i=max_jG_ij-u_i>0. Define

\[
\widetilde f_i(x)=(s_i f_i(x)-u_i)/a_i,\quad
V_C=(G_C-u1^T)/a,\quad v_\beta=V_C\beta.
\]

The diagonal of V is zero and row maxima one. The existing nominal-normalization
helper is reused with the archived nominal solver numerical allowances, but on
the **local** payoff, so each subset has its own a. The global Phase5 amplitudes
are not substituted here and no previous normalization is modified.

With H_k=I-11'/k, M=V H_k and centroid c=V1/k, compute full SVD M=U S Vh.
Require affine rank k-1 at s_max*k*eps64; the last left singular vector spans
the unique normal. Choose its sign so n'c<0. Ambiguity is abs(n'c)<=
64*k*eps64*max(1,||c||). Check ||n||=1 within64*k*eps64 and ||M'n|| within
that bound times max(1,s_max). Fail explicitly on degeneracy or ambiguity.
This criterion is permutation invariant. Since the derivative at zero of
||c+t n||² is2n'c<0, the chosen ray initially moves toward the normalized ideal.
It does not require every component of n to be negative.

## NBI definition and exact derivatives

For beta>=0, sum(beta)=1, solve

\[
\max_{x,t}t,\qquad
r(x,t,\beta)=\widetilde f_C(x)-V_C\beta-tn_C=0,\qquad
\alpha^2-x^Tx\ge0,\quad\alpha=8^{1/4}.
\]

t is unrestricted. With f_i=b0_i+b_i'x+x'Q_i x and symmetric Q_i,
grad f_i=b_i+2Q_i x. The minimized objective is -t with gradient(0,...,0,-1).
The equality Jacobian is

\[
J_r=[D_a^{-1}D_s\nabla f_C(x),\ -n_C],\qquad
J_{sphere}=(-2x^T,0).
\]

The production solver supplies every Jacobian analytically; finite differences
are used only in tests. Configuration is centralized in NBIOptions:
ftol=1e-11, maxiter=1000, equality_tolerance=1e-4, sphere_tolerance=1e-9,
retry_neighbours=3. Acceptance requires solver success, all finite values,
recomputed ||r||_2<=1e-4 and alpha²-x'x>=-1e-9. Store the actual diagnostics;
do not move accepted x onto the sphere, clip responses or adjust tolerances.
SLSQP provides a local constrained solution, with no global-optimality certificate.

## Simplex-Lattice, exact nesting and continuation

Use weak integer compositions h_i>=0, sum h_i=H, beta=h/H. Represent each weight
by h and H as well as float beta. Ascending lexicographic order gives, for
k2/H2, (0,1),(.5,.5),(1,0). Stars-and-bars places k-1 separators among H+k-1
positions, giving binomial(H+k-1,k-1) weights. Pair/trio counts are H+1 and
(H+1)(H+2)/2. For19 pairs+18 trios:

| H | Weights per pair | Weights per trio | Total |
|---|---|---|---|
|2|3|6|165|
|4|5|15|365|
|5|6|21|492|
|10|11|66|1397|
|20|21|231|4557|

Every requested H divides20. Its parent composition is h_parent=(20/H)h;
membership requires every parent component divisible by20/H. No float tolerance
is needed. Solve4557 distinct parent weights once; store one parent solution
set and five membership columns, rather than five redundant solution arrays.

Process vertices first, in their canonical index order, then remaining weights
lexicographically. Vertex starts x=anchor_j,t=0 satisfy the equality exactly;
this start is not assumed optimal. For other weights prefer the nearest accepted
weight. On one common H grid, ||beta-beta'||²=||h-h'||²/H²; integer distances
and parent-index tie breaking make nearest selection deterministic. Retry only
after failure: convex anchor combination with t0, anchors and at most three
nearest accepted weights. Remove exactly identical (x,t) starts and record every
attempt. Only accepted solutions may warm-start later weights. No random start
or parallelism. Returning the first accepted local result is explicit; this is
not a multistart proof of the largest possible t across disconnected branches.

## Full-response evaluation, provenance and numerical equality

Before ND analysis evaluate all eight original nominal f_i(x), preserve natural
values, orient g=D_s f, and use the unchanged Phase5 u_nom/a_nom to obtain
z=(g-u_nom)/a_nom for every subset and H. Do not scale separately by H or clip
negative/out-of-range model predictions. Preserve rejected attempts separately;
NPZ accepted=false and NaN denote no accepted solution, never generated data.

For each H select parent members, retain every origin and identify numerical
duplicates in decision coordinates. The first canonical representative within
64*eps64*max(1,alpha) in L-infinity is used; do not expand a transitive cluster.
This is machine-roundoff equality, not an optimization-error or geometry radius.
Keep mapping from every(subset,beta,H) to its representative. Genuine distinct
x with equal eight-response vectors remain distinct ND decision points.

In exact minimization, a dominates b iff all a_i<=b_i and some a_j<b_j.
Implement only numerical coordinate equality: differences inside
tau_i=64*eps64*max(1,max_abs_parent_z_i) count as equal. Freeze this roundoff
bound across H; then require no worse coordinates and at least one strict
improvement outside equality. This introduces no substantive epsilon-dominance
policy. Source identities and points are never overwritten by the comparison.

## Internal H sensitivity and limits

For each nondominated canonical-decision set ND_H, compute Euclidean nearest
distances ND20→NDH (mean,median,q95,max) and NDH→ND20 (mean,q95,max) in the same
normalized eight-response space. The implementation uses bounded-size cdist
blocks, not a dense all-pairs archive. Report counts, delta_ND and coverage changes
between reported H levels, with measured solver costs and iteration distributions.

H20 is the finest evaluated internal resolution, not a true Pareto front.
H4 and H5 are not mutually nested; increasing H and ND counts alone do not prove
better coverage. No universal monotonicity or automatic threshold for choosing H
is claimed. Only this curve informs an explicitly qualified recommendation.
Do not load P*, NSGA-III, MOEA/D, VRF-NBI, historical C-NBI fronts or external
Pareto metrics. No next phase or automatic merge is included.

Synthetic validation includes analytic linear ball intersections, equal-Hessian
quadratics with an independent60-digit Decimal reference, normal sign/rank,
permutations/MIN-MAX, exact vertex starts, analytic Jacobians, nesting, failure
handling, provenance, strict dominance and known directed-distance oracles.
