# 0008 — Fixed-normalization centered CHIM and local spectral screening

- Status: ACCEPTED for the explicitly requested Phase 5 scope.
- Date: 2026-10-24.
- Branch: feature/05-chim-svd-local-pa.
- Parent: PR #7, authorized squash after four green checks and clean tree.
- Existing PA early-stop policy: PROPOSED; no automatic promotion or revision.

## Decision

Use only the Phase 2 classical sphere payoff as the nominal object, and the
exact frozen Phase 4 payoff ensemble. Verify file hashes, orders, float64 shape,
metadata/source commit, all validity masks and the recorded diagonal identity.
No draws, reoptimization, coefficient fitting, RC or modification of old artifacts.

Orient rows to MIN: G=D_s A, signs +1 for MIN/-1 for MAX. Define u=diag(G_nom)
and a=row_max(G_nom)-u once. Fail on material nominal diagonal optimality
violations or numerically degenerate amplitudes. Real nominal optimality check
uses 4*c_i*1e-10 plus eps64*16*m*max_abs_row, translating the archived Phase 2
normalized certificate/objective scale into natural units and allowing stored
float64 roundoff. Amplitude degeneracy uses only the latter roundoff bound.
These are numerical validity gates, not PA statistical margins.

Every replica uses the same nominal u and a, Z=(D_s A-u)/a. Do not clip normalized
values or renormalize a replica. Delta=D_a^-1 D_s(A_b-A_nom), without subtracting
the Monte Carlo mean. Preserve variation/bias of the realized optimum geometry.

For each subset C use exactly Z[C,C] H_k, H_k=I-ones/k, with columns=vertices.
Use the first k-1 descending singular values. Apply the same SVD to Delta[C,C] H_k
for the uncertainty reference, rather than using spectra of full perturbed Z.
The global set uses seven components. All k=2,3,4 local combinations are assessed
regardless of global dimension: 28 pairs, 56 triples, 70 quadruples, 154 in all.
Their deterministic IDs use one-based original response indices.

Use q95 with explicit linear quantiles for every nested prefix 100:100:2000.
Global dimension counts consecutive leading strict passes; flag later passes
after a failure as NON_MONOTONE_PA_PATTERN. Local selection requires every k-1
component to satisfy observed>q95. No qmax, condition ratio, determinant/volume,
global-dimension, sampler-moment or anchor-displacement filter.

Consume the original pre-registered PA policy and epsilon_q byte-for-byte.
Retrospectively identify its first eligible joint success (starting at 500 vs
400), using exact subset identities, global dimension, and all 357 global/local
decision quantiles. Always continue through 2000 and use B=2000 as the scientific
reference. Verify identities/dimension against every later checkpoint; report
premature stop without changing the policy. A stop only at 2000 has no later
validation evidence. No stop is EARLY_STOP_NOT_REACHED, not an execution error.

## Evidence and limits

The affine-rank proof, centering/translation/permutation invariance and fixed
normalization derivation are in chim_parallel_analysis.md. C-PA-01 is mathematical
derivation; C-PA-02/04 are methodological decisions; C-PA-03 is a method definition.
Verified source notes separate classical PA/PCA context from this explicitly
defined uncertainty-calibrated, PA-inspired spectral screening. No equivalence
to Horn's original method, nominal type-I error or multiplicity guarantee is claimed.

Analytic rank oracles, invariance tests, strict/all-component PA cases, global
non-monotone patterns, prefix quantiles, exact identities and stable/premature/
not-reached stopping trajectories validate the implementation. Archive spectra,
all thresholds/decisions, selected identities, hashes and full prefix trajectory.
No new dependencies, H resolution, lattice weights, NBI/C-NBI, clustering or
Pareto metrics. H_k here is only the centering matrix, not a chosen lattice H.
