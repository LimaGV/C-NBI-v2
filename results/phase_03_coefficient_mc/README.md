# Original-coded coefficient Monte Carlo

Reviewed run: turning_original_codes_mc_777_20261024, seed 777,
Generator(PCG64), one float64 samples array (2000,10,8). Prefixes 100:100:2000
refer to that same coefficient_samples.npz, not separate ensembles.
Theoretical/empirical covariance is column-vec (80,80). Formula is joint
matrix-normal plug-in with raw Sigma_e. No anchors/payoffs are recomputed.

Source commit, clean-tree flag, input/object/artifact SHA-256, lock/environment,
orders, factorization and unapplied future policy are recorded in metadata.json.
checksums.sha256 covers every other file. Total payload is approximately 1.43 MB,
including one 1.24 MB compressed ensemble; no LFS or duplicate ensembles.
The requested private-repository outputs were inspected, hashed and reviewed
before adding the exact run exception. Other runs remain ignored.

See [applied report](../../docs/mathematics/turning_coefficient_mc.md) and
[derivation/API](../../docs/mathematics/coefficient_monte_carlo.md).
Use a fresh output/run ID to reproduce; archived output is never overwritten.
