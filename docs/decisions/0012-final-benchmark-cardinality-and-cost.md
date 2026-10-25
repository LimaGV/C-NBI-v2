# ADR0012 — Reference sensitivity, cardinality control and computational cost

Status: **ACCEPTED — standalone operational-resolution correction authorized 2026-10-25**.

The official C-NBI H=5 baseline is obtained from a standalone H=5 execution.
Lower-resolution grids are not inferred from a parent H=20 execution for final
method evaluation, because continuation/warm-start trajectories can alter local
SLSQP solutions. H20 is high-resolution sensitivity only. The earlier408-point
baseline and pending-cost decision below are **SUPERSEDED historical decisions**.

Use the unchanged37 subsets, models, local/global normalization, SLSQP, analytic
Jacobians, standalone warm-start policy and acceptance(eq<=1e-4,margin>=-1e-9).
Run H2/H4/H5/H10/H20 independently, five H5 runtime repetitions and one at every
other H. The first H5 execution defines the baseline regardless of quality;
repeats quantify runtime noise only and must match at absolute1e-12,relative0.
Preserve all previous artifacts byte-for-byte, including Phase6 parent analysis.
The correction has its own archive within Phase8; it is not a new method/phase.

Freeze the independent18503-point reference and saved512 reference lineages,
subsampling indices and FPS reference ordering. Reevaluate only CNBI-dependent
sensitivities. Keep the old common target explicitly as a historical H20 pooled
target for continuity, with no claim that it self-includes the new H5. Official
independent assessment uses R_minus_CNBI; historical-target comparisons retain
other methods' values exactly. Do not rebuild the independent target or rerun
EAs/VRF. Preserve EA timing and pair each new CNBI runtime with its own output.

The historical failure remains evidence of path dependence; it is no longer an
acceptance gate requiring standalone to reproduce the parent-derived result.
The protocol is docs/policies/cnbi_standalone_correction.json. Acceptance follows
the owner's explicit baseline definition; execution validation is recorded in
the updated Phase8 verification/report.

## Superseded pre-correction decision (audit history)

Freeze H5's408 official Phase7 points, the current originally coded nominal RSMs,
37 subsets, normalization, solver/options/acceptance and all earlier artifacts.
Use GD, IGD, HV, Spacing and Sparsity as the five primary metrics. Audit V1
definitions before implementation; corrected applied outputs use sample SD
(ddof1) of Euclidean nearest-neighbor distances for Spacing, their mean for
Sparsity. Earlier notebook04 uses ddof0; this divergence is recorded, not hidden.

Phase8A uses100 paired distinct seed subsets per r5/10/15/20/25, all30 once,
fixed PCG64(20261024), composition sensitivity and reference K sensitivity.
No new EA reference runs. Exclude all CNBI before reconstructing references.
Freeze R30 as a finite empirical quality target if its reconstruction validates;
stability is assessed quantitatively without inventing a saturation threshold.

Preserve the corrected V1 common HV reference rule, recomputed once from complete
canonical Phase7 candidates: lower=min(0,minimum), r=max(1.1,w+.05*max(w-lower,1)).
Four common scrambled Sobol grids (power16, explicit PCG64 streams20260..20263)
estimate the same dominated-box integral. This is a quadrature estimate, not exact
HV; report scramble SE and nested14/15/16 precision diagnostics. It does not rerun
coefficient-uncertainty Monte Carlo. Cached numerical masks do not change metrics.

Phase8B quality compares native sets, equal K66 and nested maximin K curves.
Initialize with unique objective-extreme indices, then greedy Euclidean maximin;
stable archived row ID breaks exact ties. Full complete common/LOO references
remain fixed while candidate cardinality changes. Report common self-inclusion,
different LOO targets, native counts and deterministic-vs-stochastic distinctions.

Processing end-to-end time is the primary cost, not false NFE equivalence.
Controlled EA timing remains authorized:10 seeds1001..1010, frozen Phase7 config,
read-only checkpoints50/100/200/300/400, warm-up, one numerical thread and sequential
execution, with no other scientific campaign overlapping. Quality metrics are
computed outside the timing interval; checkpoint observer overhead is recorded.

**Required H5 direct-equivalence gate failed before any benchmark timing.**
Direct H5 with the unchanged solver differs at24/492 weights above predeclared
x/z1e-5 bounds; maximum x difference3.118120710729887, z.5942667067502265.
Identical geometries and tiny equality residuals identify different feasible local
branches under the different continuation/warm-start paths, not rounding error.
The owner explicitly chose to preserve408, complete Phase8B quality and mark CNBI
cost **PENDING_H5_DIRECT_EQUIVALENCE_FAILED**. Do not execute25 CNBI timing repeats
or attribute a direct-H5/H20 runtime to this official membership-derived baseline.
No solver/start/tolerance/baseline change is authorized by that choice.

The owner also explicitly forbids VRF execution. Use only the66 historical
reevaluated Phase7 points; no optimization or timing VRF. Missing comparable
runtime is explicit. Cost curves/efficiency analysis can characterize the EAs;
they cannot establish CNBI or VRF quality–cost competitiveness.

No adaptive refinement, new synthetic scenarios, retuning, pseudo-replication,
ground-truth claim or automatic merge. Full frozen configuration and visual mapping
are in `docs/policies/benchmark_cardinality_cost.json`.
