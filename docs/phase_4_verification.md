# Phase 4 verification and traceability

Date: 2026-10-24. Branch: feature/04-monte-carlo-anchor-reoptimization.

## Authorized preparation

PR #6 head a3e33ae2d0bb6e3ec4c5fd80958477dca3e6a667 was OPEN,
MERGEABLE/CLEAN with four successful Windows/Ubuntu checks. Locked sync,
356 local tests, Ruff and strict mypy passed again. Authorized squash merge
produced main 3ea6c6e6a3503ccf3eb7ea99d658c9e906677755. Main was updated and
clean before creating the requested branch.

Before edits, Phase 3 scientific commit 5a102dd337a5c9b7108fac6997b612c7d02a8684
and all 20 historical input hashes were verified against their Git blobs.
The canonical ensemble was verified finite float64 (2000,10,8), and its pinned
NPZ/metadata hashes, seed, source commit and orders are checked by the real loader.
The new source is not assumed byte-identical to all old implementation files;
the archived scientific inputs themselves remain unchanged.

## Scientific gate

The existing coefficient transform is exposed for arrays and shared with its
RSMFit wrapper. Its numeric extraction and interaction halves are unchanged.
The trust-region solver file and defaults are unchanged. Every returned anchor
is independently checked for finite fields, feasibility, normalized KKT/PSD,
scale/tolerance consistency and objective equality before payoff construction.
MIN/MAX directions, radius and payoff axes are explicit. No normalization/RC.

Tests cover single-replica manual MIN/MAX/payoff oracles, all interactions,
hard/flat/interior/boundary cases, forged certificates, solver/payoff failures,
no substitutions or dropped indices, immutable results/inputs, bitwise repeats,
isolated/reordered replicas, response permutation on both payoff axes, 2000
identical nominal coefficient matrices with **16000 actual solver calls**,
archived nominal recovery, frozen real-input validation, full export shapes,
diagonal identity, exact prefix-summary definitions and incomplete-run refusal.
The integrated real run blocks new draws/OLS/RC entry points. Failure injection
also exercises header-only distribution outputs, per-response failure counts,
preserved replica IDs and nonzero incomplete CLI exit.

## Quality and source provenance

Required commands: uv sync --locked; uv run pytest -v;
uv run pytest --cov=cnbi_v2; uv run ruff check .; uv run mypy src; git diff --check.
Final local outcomes are recorded with the reviewed real archive and PR head.
Local gate: 409 tests; coverage 99.31% (1149/1157 statements), new anchor module,
existing model/optimization and other uncertainty modules 100%; Ruff clean and
strict mypy on 19 source files. Only the same eight pre-existing inspector
statements remain uncovered. No dependency or uv.lock change.

Commit source before generating the canonical reviewed archive. Its metadata
records that actual clean commit and input hashes; the later delivery commit
adds outputs/report. Verify input hashes against those source blobs and every
output checksum before publication. One anchor NPZ and one payoff NPZ, not
2000 CSVs; fixed-width Unicode and allow_pickle=False, no object arrays.

Canonical archive: turning_original_codes_anchor_mc_777_20261024, source
ac9eb72af9f91de2b860df4b17ba8ab417e94e07, dirty=false. All 26 input hashes
match that commit's Git blobs; all nine artifact checksums passed. Actual
16000 attempted, 16000 certified, zero failures, 2000 valid payoffs and exact
diagonal equality. Compute 4.436183499987237 s; measured workflow 4.640420899959281 s.
An additional complete serial replay produced bitwise equal arrays/certificates/
cases/payoffs in the same environment, with no new draws or changes to inputs.
Ra: 420 interior and 1580 boundary. Full tables and all 20 prefixes in the report.

See [mathematics](mathematics/anchor_monte_carlo.md),
[applied report](mathematics/turning_anchor_mc.md), ADR 0007 ACCEPTED and claims
C-MC-04/05/06. Timing is serial and descriptive. The future PA early-stop policy
remains PROPOSED, not applied. No Phase 5, CHIM, dimensional SVD/PA, subset
selection, NBI/C-NBI, shrinkage or bootstrap is executed.
