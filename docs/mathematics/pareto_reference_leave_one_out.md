# Empirical Pareto reference and family leave-one-out

For each stochastic family M, retain final populations from30 seeds. Evaluate
all feasible decisions with the same current nominal RSM function f(x), orient
to minimization g_i=s_i f_i, and apply the frozen nominal normalization
z_i=(g_i-u_i)/a_i from Phase5. No clipping or method-specific normalization.
The domain is norm(x)<=8**.25; feasibility uses the frozen1e-9 squared-margin
roundoff tolerance. Variation outside the ball receives deterministic radial
repair x←alpha*x/norm(x), with only representational inward nextafter correction.

Define P_M=ND(union_r FinalND(M,r)), using classical MIN dominance with the
explicit machine-roundoff equality vector frozen in Phase6. Deduplicate only
decisions within the frozen L-infinity tolerance64*eps*max(1,alpha), first
representative, retaining every (family,run,source_id) origin. No clustering,
statistical epsilon-dominance, decimal rounding or intermediate archive.

P_all=ND(union_M P_M). For each M, reconstruct
P_minus_M=ND(union_{K != M} P_K) from **original independent family pools**.
Exclude before deduplication/ND. A shared coordinate may survive only through a
retained independent origin. Removing rows from P_all would lose retained points
previously dominated by M and can leak shared provenance; it is not this rule.

Families are NSGA3, MOEAD, CNBI, VRF. H5/H20 both belong to CNBI. Only H20
contributes to the common reference. H5 is evaluated against P_minus_CNBI,
which contains no CNBI origin at any resolution. Its coordinates may coincide
with another family's independent result without constituting origin leakage.

## Indicators and orientation

All distances use Euclidean norm in the same fixed eight-dimensional z space.
GD_p1(A,B)=mean_{a in A} min_{b in B} norm(a-b).
IGD_p1(A,B)=mean_{b in B} min_{a in A} norm(b-a).
Directed Hausdorff H(A→B)=max_{a in A} min_{b in B} norm(a-b).
The archive names both orientations explicitly.

The signed additive MIN indicator is
Iepsilon+(A,B)=max_{b in B} min_{a in A} max_i(a_i-b_i).
Negative values are preserved; it is not an absolute-distance metric and must
not be clipped at zero. KDTree nearest-neighbor queries are exact (eps0).
An exact epsilon acceleration uses a nearest Euclidean candidate to upper-bound
each target's minimum, skipping it only if that upper bound cannot raise the
running maximum; remaining minima scan all candidates. Brute-force oracles test
this equivalence, including negative epsilon cases.

Removal diagnostics use H(P_all→P_minus_M) and
Iepsilon+(candidate=P_minus_M,target=P_all), plus exclusive/shared counts.
Pool saturation uses H(P_pool30→P_poolr) and
Iepsilon+(candidate=P_poolr,target=P_pool30), r1..30 in seed order. Pool30 is an
internal endpoint, not an external convergence certificate or true Pareto set.

## Interpretation

LOO diagnostics use label `LEAVE_ONE_FAMILY_OUT`. Family targets differ; these
numbers are not automatically comparable for ranking. The common target permits
exploratory comparison but contains each contributor's own points and is labeled
`COMMON_REFERENCE_SELF_INCLUDED`. Contribution measures which regions a family
adds to the known envelope, not algorithm superiority. H5 diagnostics are a
sanity check only, not the final benchmark. Thirty finite runs do not establish
Pareto completeness. HV, final benchmarking and H5→H20 adaptation are deferred.
