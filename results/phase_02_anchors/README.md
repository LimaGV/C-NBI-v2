# Phase 2 nominal anchors and experimental response-cloud ablation

Reviewed run: turning_original_codes_20261024, executed from clean source commit
03ff09ee79a588e9c461c4b9db5d1e89d4bcbf88. Its metadata records original coded
inputs, unchanged canonical responses, code/input hashes, environment and options.
Each output is included in checksums.sha256. No original XLSM/PDF/notebook is
published. The original-coded fit is distinct from the physical model, not an
equivalent reparameterization; physical anchor coordinates remain undefined.

Both payoff matrices are stored separately, rows responses/columns anchors.
All eight classical anchors are response-feasible under the three cutoffs
evaluated; therefore the RC optima reuse global classical certificates exactly.
No SLSQP search is needed for those real optima; restrictive/nonconvex cases
exercise deterministic multistart in tests. Every proposal and diagnostic is
recorded. The assembled Utopia is still outside this descriptive region.

See docs/mathematics/turning_individual_anchors.md for the complete report and
docs/phase_2_verification.md for reproduction in a fresh output directory.
ADR 0005 remains EXPERIMENTAL. Do not overwrite a recorded run or infer an exact
finite-sample confidence statement from these nominal cloud constraints.
