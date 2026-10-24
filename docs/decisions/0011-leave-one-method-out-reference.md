# ADR 0011 — Empirical reference with family leave-one-out

Status: **ACCEPTED**, within the explicitly requested Phase7 scope.

Problem: a reference containing a method's own output can give optimistic
self-included diagnostics. H5 and H20 are resolutions of one CNBI family.

Decision: build the empirical nondominated union of eligible NSGA3, MOEAD,
CNBI20 and historical reevaluated VRF pools. Reconstruct each leave-one-family-out
reference from independent retained pools, excluding all origins of that family
**before** union/deduplication/nondominance. Independent shared coordinates may
survive via retained origins. Never remove a family merely from the already-ND
common envelope: previously dominated retained points may reappear.

H5 is the operational baseline by the owner's Phase7 instruction (492/411/408).
H20 is a finer auxiliary CNBI member (4417 ND), not ground truth. It alone
represents CNBI in the common pool; all CNBI resolutions are excluded for H5's
independent target. H5→H20 adaptive refinement remains future work.

Canonical inputs: current eight originally coded nominal RSMs, original response
directions, sphere alpha=8**.25, fixed global Phase5 normalization without clipping.
Historical solutions require verifiable decisions and current-RSM reevaluation;
unverifiable historical objectives are excluded. See the pre-run source audit.

Pymoo0.6.2 is added and locked to use consolidated algorithms. Authorized applied
V1 calibration supplies operators, general V1 budget policy supplies a common
132000 search evaluations/run. Thirty independent seeds1001..1030 per EA;
uniform ball sampling and explicit radial repair; final populations only.
No V1 module, environment or architecture is reused. Full frozen policy:
`docs/policies/pareto_reference_protocol.json`.

Validation: synthetic known ND/LOO/shared-provenance and signed-indicator oracles,
sphere/seed/budget tests, frozen-H recovery and immutable-input checks. Scientific
archive records all60 runs, saturation, removal diagnostics and H5 sanity metrics.
Search NFE and independent validation evaluations are accounted separately.

Consequences: LOO reduces self-inclusion but different families have different
targets; do not derive an automatic ranking. Common diagnostics are explicitly
`COMMON_REFERENCE_SELF_INCLUDED`. Cardinality/contribution is not superiority.
The envelope is an empirical approximation, not a true Pareto front. HV and final
benchmark/statistical comparison are deferred. No automatic PR merge.
