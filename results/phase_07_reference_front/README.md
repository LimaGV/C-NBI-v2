# Phase7 — finite empirical multi-family reference

Only the explicitly requested `turning_multifamily_loo_20261024` campaign is
versioned. It uses frozen current nominal RSMs and fixed Phase5 normalization.
Do not call the combined envelope a true Pareto front.

Reproduce search (explicitly launches60 real runs,132000 optimizer NFE each):
`uv run python -m scripts.validation.turning_reference_campaign --output <new-empty-directory>`
from a clean committed checkout. Existing compatible per-run checkpoints are
hash-checked; the runner writes launch/materialization/completion files, so always
use a separate output directory to keep the archived campaign immutable.
Run directories require the protocol/input/engine identities to match.

Assemble references/diagnostics without optimizing:
`uv run python -m scripts.validation.turning_pareto_reference --output <campaign-directory>`.
For reanalysis copy the finite campaign first, retaining the original archive.

Per-run NPZ: final population x/natural f/normalized z, final ND x/f/z and
population indices. JSON: configuration/hash, seed, NFE, runtime, repair operations,
source commit and independent scalar-validation evaluation count. No intermediate
generation/archive contributes. Pooled/reference NPZ files contain x, natural_f,
z and origins_json (Unicode JSON, allow_pickle=False).

CNBI decision files preserve exact Phase6 membership/all origins; pool files are
deduplicated ND. H5 is evaluation only; H20 alone represents the CNBI family.
Historical VRF decisions are reevaluated, never historical response values.
LOO excludes whole families before rebuilding ND. In particular,
`reference_minus_cnbi.npz` is the independent target for H5; it has no CNBI origin.

Read `docs/mathematics/turning_pareto_reference.md` for measured results and
limitations. `checksums.sha256` covers every run artifact including metadata;
metadata also stores input/code/output hashes (excluding its own recursive hash).
