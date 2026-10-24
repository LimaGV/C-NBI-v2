# Fixed-normalization centered CHIM uncertainty screening

Reviewed run: turning_fixed_nominal_chim_pa_777_20261024. Exact Phase 2 sphere
nominal payoff and frozen Phase 4 samples; no draws, fitting, reoptimization or RC.
Fixed nominal MIN orientation/normalization, centered vertex geometry, SVD of
payoff perturbations, q95 linear strict component tests for every candidate.

B=2000 reference: global leading dimension 2; 19 pairs +18 triples +0 quadruples
=37 selected from 28+56+70 candidates. All 20 prefixes and 7140 threshold/decision
rows retained. Original early-stop policy remains PROPOSED:
EARLY_STOP_NOT_REACHED, retrospective stability not applicable.

NPZ noise arrays: global (2000,7), pairs (2000,28,1), triples (2000,56,2),
quadruples (2000,70,3), with numeric subset indices, allow_pickle=False.
Nominal normalized/centered/H matrices are preserved in a second small NPZ.
Selected/full local/global decisions, normalizers and stopping validation are
in text tables/JSON. The ten output checksums and all 21 input hashes were verified
against the clean source commit 257d1942b452c427b5f8ef7924fddf31975c3ad3.
All noise spectra were reproduced bitwise by a separate deterministic replay.

Approximately 6.10 MB reviewed payload, one grouped noise archive, no LFS or
file-per-subset flood. Only this exact run is allowed by .gitignore; other runs
remain ignored and nonempty output directories cannot be overwritten.

See [applied report](../../docs/mathematics/turning_chim_pa.md),
[math/API](../../docs/mathematics/chim_parallel_analysis.md) and
[verification](../../docs/phase_5_verification.md). No downstream phase execution.
