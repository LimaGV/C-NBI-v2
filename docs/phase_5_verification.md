# Phase 5 verification and traceability

Date: 2026-10-24. Branch: feature/05-chim-svd-local-pa.

## Authorized preparation

PR #7 head 64c0a84b430c30a93f712d674baab7019c10aa4d was OPEN,
MERGEABLE/CLEAN with four successful Windows/Ubuntu checks. Locked sync,
409 local tests, Ruff and strict mypy passed again. Authorized squash merge
produced main ccf951a7ff333e147088c084b6e67c71025a2a33; main was updated
and clean before creating the requested branch.

## Input and scientific gates

Pinned nominal sphere payoff from Phase 2; exact Phase 4 payoff/anchor NPZ and
metadata, source commit, canonical axes/directions, finite float64 (2000,8,8),
all validity masks and diagonal equality against archived optima are checked.
The Phase 2 nominal diagonal/certificates are also checked. The original PA
policy SHA is pinned and its bytes/status are unchanged. No old artifact,
experimental value, fitter, sampler, optimizer or dependency/lock is altered.

New tests: nominal diagonal/row maxima, fixed normalization/Delta identity,
positive amplitudes, unit/shift/direction invariance, H_k symmetry/idempotence/
null vector, vertex translation/permutation, known 1/2/3-dimensional geometries,
rank equivalence for every reference vertex, local row/anchor slicing and all
candidate counts, strict/all-component decisions, non-monotone global passes,
nested linear quantiles, exact subset identities, 1% equality rejection, zero
protection, first stop 600 synthetic oracle, stable/premature/not-reached cases,
immutable/finite outputs and pinned real archives. Integrated tests block RNG,
fitter and optimizer entry points, recheck all 7140 thresholds directly from
archived noise arrays, and verify retrospective identities/dimension independently.

## Quality and archive

Required commands: uv sync --locked; uv run pytest -v;
uv run pytest --cov=cnbi_v2; uv run ruff check .; uv run mypy src; git diff --check.
Local gate: 453 tests; coverage 99.44% (1417/1425 statements); new chim/ 100%;
prior scientific modules remain 100%. Ruff and strict mypy on 25 source files pass.
Only the same eight older workbook-inspection statements remain uncovered.
Final CI results are linked to the delivered revision.
No new dependencies, runtime or dev, and no uv.lock change.

Source is committed before canonical archive execution; metadata records its
actual clean source commit. All input hashes are compared to its committed blobs
and artifact checksums are verified before publication. One compact grouped
noise-spectrum NPZ, one nominal-geometry NPZ and text tables preserve every
decision and all 20 prefixes. Nonempty run directories cannot be overwritten.

Canonical archive turning_fixed_nominal_chim_pa_777_20261024, actual source
257d1942b452c427b5f8ef7924fddf31975c3ad3, dirty=false. All 21 input hashes
match committed source blobs and all ten artifact checksums passed. A separate
deterministic replay reproduced every noise spectrum bitwise. Global leading
dimension 2, 19 pairs/18 triples/0 quadruples selected at B=2000, numerical rank 7.
EARLY_STOP_NOT_REACHED; max decision-quantile relative changes never fell below
1%, so no retrospective early-stop stability claim or policy promotion.

ADR 0008 ACCEPTED. C-PA-01/02/03/04 recorded with explicit derivation/decision/
definition evidence. Literature coverage remains PARTIAL where only abstract or
selected HTML passages were inspected; no claim of Horn equivalence.
Early-stop policy is evaluated retrospectively but stays PROPOSED; B=2000 is
always the scientific reference, including if a premature stop is detected.
No H resolution, lattice, NBI/C-NBI, clustering, Pareto metrics or later phase.
