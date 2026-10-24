# Monte Carlo anchors and natural payoff ensemble

Reviewed run: turning_original_codes_anchor_mc_777_20261024, consuming the exact
versioned Phase 3 coefficients (seed 777 already frozen, no new random draws).
16000 certified global sphere solves, 0 failures, 2000 complete payoffs.
Anchors (2000,8,3); optimal_values/norms/cases (2000,8); payoffs (2000,8,8),
rows=evaluated responses, columns=anchors, diagonal=optimal_values.

NPZs include masks, fixed-width Unicode cases/locations, displacement/delta_f
and independently checked certificates, loaded with allow_pickle=False.
Six CSVs contain displacement/optimum/solver summaries, failure log and all
20 prefix diagnostics. Empty failure log retains its header. No prefix reruns
optimization, no early stop, response normalization or RC.

Actual clean source commit and all 26 input hashes are recorded in metadata;
all nine output hashes are in checksums.sha256, including metadata. Files were
checked against source Git blobs and reviewed before the exact run exception.
Approximately 2.18 MB total; one anchor NPZ and one payoff NPZ, no LFS/CSV flood.
Other runs remain ignored. Never overwrite a reviewed run.

See [applied report](../../docs/mathematics/turning_anchor_mc.md),
[math/API](../../docs/mathematics/anchor_monte_carlo.md) and
[gate](../../docs/phase_4_verification.md). No Phase 5 execution.
