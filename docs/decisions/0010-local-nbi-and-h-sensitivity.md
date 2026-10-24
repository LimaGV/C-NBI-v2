# 0010 — Local NBI and internal Simplex-Lattice resolution sensitivity

- Status: ACCEPTED in the explicitly requested Phase 6 scope.
- Date: 2026-10-24.
- Branch: feature/06-simplex-lattice-local-nbi.
- Parent: PR #8 squash1053f297ad9263d3219532c14f7dfc19fb42c29a after four
  successful CI checks, review and local502-test/Ruff/mypy/locked-sync gate.
- No final H is accepted; the five-level sensitivity is evidence for later choice.

## Decision

Freeze the37 B=2000 subset identities (19 pairs,18 trios,0 quadruples), all eight
nominal originally coded RSMs, nominal sphere anchors/payoff, directions and
radius alpha=8**.25. Pin hashes and metadata. No coefficient mean/draws, new PA,
anchor optimization, RC or legacy selection. Do not modify earlier artifacts.

For each subset use its own nominal payoff A[C,C]. Orient rows to MIN and
normalize by its oriented diagonal u and row maximum minus u. Every amplitude
must be positive/nondegenerate. This is a local deterministic normalization;
the fixed global Phase 5 normalization remains unchanged for full-space diagnostics.

Compute the unique unit left null vector of centered local vertices V H_k.
Require affine rank k-1, orthogonality, unit length and unambiguous n'centroid<0.
The sign is selected geometrically, never by SVD vector order. Solve max t
subject to f_tilde(x)=V beta+t n and alpha^2-x'x>=0 using SLSQP with analytic
objective/equality/sphere Jacobians. t is unrestricted; no t>=0 filter is added.
Use ftol1e-11, maxiter1000, equality norm tolerance1e-4 and sphere margin
tolerance1e-9. Independently recompute finite values, equality norm and sphere
margin; require solver success too. Never relax tolerances to increase success.

Generate ascending lexicographic weak integer compositions of H. Preserve h,H
and beta=h/H; stars-and-bars gives binomial(H+k-1,k-1) weights. Use H_parent20,
solve each distinct parent weight once and derive H2,4,5,10,20 by exact integer
membership. Expected counts165,365,492,1397,4557. Solver processing visits vertices
first and other weights lexicographically; stored weight order stays canonical.
Vertices start at their exact anchor with t0. Other weights prefer the accepted
nearest parent weight; squared integer distance gives exact beta-distance ties,
broken by canonical parent index. On failure retry convex combination with t0,
anchors, and up to three nearest accepted weights, deduplicating starts exactly.
Record every attempt and stop at the first independently accepted result.

SLSQP acceptance is local convergence plus feasibility, not a global-optimality
certificate. Failure remains an explicit missing accepted point/mask, with all
attempts logged and no fabricated substitute. The real application is investigated
if failures occur; generic code never requires100% acceptance for arbitrary data.

Re-evaluate all eight natural RSM responses at every accepted x before full-space
deduplication/ND. Preserve natural, oriented and fixed-global-normalized values.
Use first representative within64*eps64*max(1,alpha) in decision L-infinity;
no transitive cluster expansion or solver-accuracy/statistical distance is used.
Keep every (subset,parent weight,H) origin. Nondominance uses common MIN orientation
with coordinate equality only inside64*eps64*max(1,max_abs_parent_z_i), frozen
across H. This bound addresses floating-point equality; there is no scientific
epsilon-dominance parameter. Distinct decision points with equal response vectors
remain separate nondominated decisions.

Measure directed Euclidean coverage ND20→NDH (mean,median,q95,max) and reverse
NDH→ND20 (mean,q95,max) in the same eight-response normalization. Report ND counts,
marginal changes and cost without an automatic H threshold. H4 and H5 are not
nested in one another, although both are subsets of H20; no monotonic theorem
is claimed for consecutive reported levels or their nondominated sets. H20 is
only the finest internal resolution evaluated, never a true Pareto reference.

## Validation and limits

Use exact lattice/nesting oracles, synthetic normal/orientation/permutation/
MIN-MAX tests, exact vertex starts and analytical Jacobian checks. Validate a
linear NBI ball intersection analytically and a quadratic case against a separate
60-digit Decimal derivation. Test failure and independent acceptance gates.
Validate real archived residuals/all-eight-response evaluations independently,
membership, provenance, counts, hashes and immutable input boundaries.

Claims C-NBI-01/02/03/04 distinguish derivation, method definitions and the
explicit internal-sensitivity decision. Literature metadata supplies context,
not an invented full-text proof of this exact normalization/normal/solver policy.
No external front, NSGA-III, MOEA/D, VRF-NBI, GD/IGD/hypervolume, new PA/MC,
parallelism, next phase or automatic merge is included.
