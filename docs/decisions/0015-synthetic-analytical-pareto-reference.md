# MDR0015 — independent analytic reference and synthetic evaluation protocol

- Type:MDR; explicit owner-defined Phase10C scope and new finite-reference protocol.
- Status:ACCEPTED within this task; coverage budget is a proposed operational audit
  convention,not a theorem or approval of the later campaign.
- Date:2026-10-29;responsible:project owner;implementation:Codex.
- Branch:feature/10c-synthetic-pareto-reference.
- Input:27 frozen10A cells and135 unchanged10B RSMs;integration47a0e4d by merge
  commit after PR15 checks,44 checksums and eight archive tests. main CI40919991675
  SUCCESS Ubuntu/Windows. No historical scientific file or test may change.
- Validation gate:analytic oracles,all27 geometry certificates,independent coverage
  and HV studies,integrity/quality checks;final evidence in phase_10c_verification.md.

For common isotropic squared distances with all anchors inside the original ball,
the exact efficient decision set is the convex hull of anchors. Its objective
image is continuous;the5000-point reference is a finite independent approximation.
Prove both inclusions,including zero scalarization weights,without generalizing to
arbitrary quadratic Hessians. Ideal0,nadir from all pairwise anchor distances.

Use unperturbed coned hull triangulation and stratified interior/boundary/near-anchor/
pair-segment candidates. FPS in normalized true objective space preserves every
individual extreme and stable source-ID ties;prefixes2500/5000/10000. One common
reference per structural cell,shared by all5 replicas. Independent probes do not
select/restart points. Failure of the precommitted coverage budget is review-required,
never a reason to change5000 or anchors. Numerical dominance ambiguity is retained
and documented,not used to delete an analytically efficient point.

Reuse validated p1 Euclidean GD/IGD and ddof1 Spacing/mean-NN Sparsity. Fix external
HV box[0,1.1]^m. Study nested four-scramble Sobol levels13..16,with predeclared
global escalation to18/20 only if reference precision fails,and analytic boxes
in dimensions4..11. An exact<=8-box inclusion-exclusion branch avoids artificial
small-set zeros;large-set estimates retain precision status. Freeze final settings
only after validation;unresolved HV regimes remain pending before10D. Never adapt
the HV reference to competitors or clip coordinates.

Reference generation accepts only the approved source and frozen sampling protocol,
never noisy RSMs,method decisions,external fronts or observed performance. The
evaluation API separately accepts actual method decisions,retains raw outputs,
then computes true responses,analytic normalization,feasibility,stable identity,
full-space ND and metrics offline. Search objects expose only frozen noisy RSMs.
There is no feedback channel from the evaluator to a solver. Equalization is only
a future paired-block plan;no actual algorithm runs or subset equalization now.

Definitions:synthetic_pareto_reference.md and synthetic_benchmark_metrics.md.
Machine policy:docs/policies/synthetic_pareto_reference_10c.json.
Alternatives rejected:redundant Dirichlet as purported uniform volume,anchor
joggling,reference pooling from methods,RSM-derived truth,posthoc sampling/threshold
selection,clipping,competitor-derived HV bounds and fabricated singleton statistics.
Excluded-material licensing remains unchanged;original-code MIT scope is preserved.
