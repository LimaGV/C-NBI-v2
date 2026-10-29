# Phase10C — analytic Pareto set and independent finite reference

## Assumptions and two-inclusion proof

This is a mathematical derivation for the owner's explicitly specified class,
not a claim about arbitrary quadratic multiobjective problems. Fix the unchanged
Phase10A anchors a_j in the Euclidean ball Omega={x:||x||<=alpha},alpha=2^(nx/4).
All objectives are MIN and f_j(x)=||x-a_j||². Let C=conv{a_1,...,a_m}.
C is compact,convex and contained in Omega by convexity of the ball.

**Outside C implies inefficiency.** For any feasible x outside C,its Euclidean
projection p onto C exists and is unique. For a_j in C,the first-order projection
inequality is <x-p,a_j-p><=0. Expanding the square gives

\[
 ||x-a_j||^2=||x-p||^2+||p-a_j||^2+2\langle x-p,p-a_j\rangle
 \ge ||p-a_j||^2+||x-p||^2>||p-a_j||^2.
\]

The feasible p strictly improves every objective. Thus P_X is contained in C.
For completeness,the projection inequality follows by differentiating
||x-[p+t(a_j-p)]||² at t=0+;a negative derivative would contradict minimality.

**Membership in C implies efficiency.** Write x=sum_j lambda_j*a_j,lambda_j>=0,
sum lambda_j=1. Completing the square in the scalarized function gives

\[
 g_\lambda(z)=\sum_j\lambda_j||z-a_j||^2
 =||z-x||^2+\sum_j\lambda_j||a_j||^2-||x||^2.
\]

Its Hessian is2I and its unique global minimizer is x,which is feasible. If a
different y dominated x,componentwise inequalities imply g_lambda(y)<=g_lambda(x),
contradicting unique minimality. This argument remains valid when some lambda_j
are zero:uniqueness,not positivity of every individual weight,excludes another
decision with equal weighted objective. Consequently C is contained in P_X.

Therefore **P_X=C** and **P_F={F(x):x in C}**. This conclusion depends on the
common isotropic quadratic Hessian and feasibility of the entire hull. It is not
asserted for arbitrary Hessians,restricted nonconvex feasible sets or general MOO.

The true decision set and true front are continuous. A finite reference R5000 is
an approximation for indicator evaluation;it is never called the complete/exact
front. Full affine anchor rank nx,already certified in10A,also makes F injective:
subtracting response differences between objectives eliminates ||x||² and leaves
the full-rank anchor-difference system. The Pareto image has intrinsic dimension
nx,not m-1,despite m objective coordinates.

## Exact ideal and nadir,independent of sampling density

Each ideal component is0,attained at its corresponding anchor. By convexity,
f_j(sum lambda_k*a_k)<=sum lambda_k*f_j(a_k)<=max_k f_j(a_k),and the last maximum
is attained at an anchor in C. Therefore nadir_j=max_k||a_k-a_j||² exactly.
Distinct frozen anchors imply every denominator is positive. Evaluation uses
(f_j-0)/nadir_j without clipping. Points in C lie in[0,1]^m;feasible decisions
outside C may exceed1 and retain those values. The normalization belongs only to
the offline evaluation API and is not passed to noisy-RSM search objects.

## Independent candidates and uniform-volume justification

The machine protocol is docs/policies/synthetic_pareto_reference_10c.json.
Only27 anchors from the hash-verified Phase10A archive are admissible official
inputs. No noisy RSM or method solution file is read by reference generation.

Use unperturbed Qhull ConvexHull (Qc Qx,Qt always enabled,no QJ). Cone each
triangulated boundary facet to the mean of all anchors,an interior point because
all convex weights are positive and the hull has full affine rank. These nx-
simplexes cover C with disjoint interiors. Their volumes are
abs(det(v_1-c,...,v_nx-c))/nx!. The sum must agree with the hull volume within
relative1e-8,with no zero-volume cones. Select cones proportionally to volume,
then use sorted uniform spacings for Dirichlet(1,...,1) weights over that
**nx+1-vertex nonredundant simplex**. Constant density on each selected simplex
gives constant volume density on C. Convert its centroid weight into equal
weights over all m anchors to store an explicit membership witness.

This does not identify Dirichlet(1,...,1) over all redundant m anchor weights
with uniform hull volume. Those two distributions generally differ.
Boundary strata select triangulated facets proportionally to their Gram/SVD
surface areas,then uniformly sample each facet. No anchor is joggled or changed.

If Qhull fails or the cone-volume audit fails,record the exact limitation. The
declared fallback samples positive redundant-anchor exponential/Dirichlet weights
and all nx-anchor subsimplex strata. It preserves C but is **not** claimed uniform
volume/surface sampling. Such a case requires explicit geometry/coverage review.
Rank deficiency is a certified error,never corrected by perturbing anchors.

Candidate strata per cell:all m anchors;8192 volume-interior points;4096 facet
points;2048 near-anchor points (0.98*anchor+0.02*independent interior draw,cyclic
anchor assignment);17 equally spaced internal points on every anchor-pair
segment. Some pair segments are interior rather than polytope edges;actual edges
are included among them. All true individual extrema are retained.

Duplicate identity uses L-infinity distance<=1e-12*alpha,stable original row ID,
first representative without transitive clustering. Distinct anchors cannot be
merged. FPS selects10000 points in normalized true objective Euclidean distance,
starting with every anchor in published order. Exact numeric ties use the first
remaining original candidate ID. This is objective-coverage oriented selection,
not uniform-volume sampling. Store weights,source IDs,origins,counts and hashes.

R2500,R5000,R10000 are prefixes of the same order. Main arrays contain exactly
5000 rows per scenario,total135000. The last5000 rows and witnesses are separate
lossless sensitivity extensions. All five noisy replicas share one reference.

## Membership,non-dominance and precision certificates

Store float64 coordinates/responses and convex-combination witnesses. Verify
lambda>=0,sum(lambda)=1 within1e-12,decision reconstruction<=1e-12*alpha,
strict ball feasibility,all individual anchors,nonnegative finite responses and
direct distance evaluation. Identity tolerance is not a statistical parameter.

Barycentric membership plus the theorem certifies mathematical non-dominance.
For a floating-point diagnostic,soft dominance uses normalized tolerance1e-12.
Let delta bound reconstruction error,including the weight-sum normalization error
and a conservative16*m*eps*max(1,alpha) dot-product allowance,and epsilon bound direct evaluation
roundoff by64*float64_eps*max(1,max(F)). Inflate the search radius outward for
floating-point square-root/query rounding. A possible soft dominator must have
decision separation at most delta+sqrt(delta²+max(nadir)*1e-12+2*epsilon),from
the weighted quadratic gap. Query all pairs in that radius and inspect both
directions. Apparent tolerance dominance is recorded and does not delete an
analytically efficient reference point. Tests also verify brute-force dominance
and projection examples independently on small fixtures.

## Cardinality sensitivity and predeclared coverage review

An independent4096-point volume probe and1024-point boundary probe use separate
streams,are generated only after selection,and never select or modify R5000.
Report directed Euclidean distances,RMS-per-coordinate distances,discrete
Hausdorff distances,nearest-neighbor distributions,source composition,boundary
counts and centroid radial-shell counts for2500/5000/10000. Nested directed
zeros are expected and are not evidence of asymptotic convergence;independent
probe coverage supplies the nontrivial diagnostic. Geometric conditioning and
any fallback are explicit.

Before inspecting outputs,set an operational review budget of1/20 of the true
Pareto response range in coordinate RMS units:0.05 for maximum independent
volume/boundary-probe distance and for R5000-versus-R10000 discrete Hausdorff.
This is a **new proposed finite-reference audit convention**,not an inherited
threshold or theorem about convergence. Euclidean distances are divided by
sqrt(m) only for this budget;GD/IGD themselves remain unscaled Euclidean p1.
Any failure is REVIEW_REQUIRED before10D;never change5000,anchors,samples or
the budget to make a scenario pass. Even a passing finite audit is not a proof
of uniform approximation or asymptotic convergence of the continuous front.

Source math is an internal derivation (MATHEMATICAL_DERIVATION);protocol choices
are METHODOLOGICAL_DECISION. No unverified literature attribution is made.
Software documentation consulted via Context7:official SciPy1.18.1 spatial
tutorial and ConvexHull/Qhull documentation;QJ random perturbations are excluded.
