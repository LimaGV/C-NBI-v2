# Phase 5 — stopping-policy-only revision gate

## Preflight and immutable boundary

On 2026-10-24 the existing feature/05-chim-svd-local-pa branch was clean and
up to date after fetch/ff-only pull. Local and PR #8 HEAD matched
fc57b05c96a72a8cc6128f49ef270a689cc9bac0. PR OPEN, MERGEABLE/CLEAN;
all four Ubuntu/Windows push/pull-request checks SUCCESS. No merge performed.

The original 10 Phase 5 artifacts and their checksum manifest remain unchanged.
The revised workflow pins each artifact's SHA-256 and validates the manifest,
array keys/shapes/dtypes/order and canonical subset indices. It recalculates
only q95 prefixes and stopping diagnostics. All 7140 q95/observed/margin/PASS
rows are exactly equal to history; all 20 dimensions, counts and selected ID
sets are checked. B=2000 stays dimension2, 19 pairs+18 triples+0 quadruples.

V1 is preserved byte-identical in docs/policies/history/pa_early_stop_policy_v1.json,
hash e738a49b7df5aca0beaca8ed7a4229dbbfeed2aecd5160de0a4414eda73b43db.
The active JSON is version2, PROPOSED_REVISED, explicitly post hoc. Historical
Phase 3/4/5 scripts now reference the v1 archive instead of reading future
revisions from the same active path. Their science is unchanged. One regression
test caught the initial Phase 3 path dependency; pinning v1 resolved it.
Original archived metadata remains a record of its recorded source Git commit.

## Verification contracts

Known q=(10,8,4) gives gaps(.2,.5); equal/zero spectra are finite and explicit;
positive common scaling preserves representable nondegenerate gaps. Pair/trio/
quartet gap counts are0/1/2, and immutable outputs are tested. Policy drift,
nonfinite/negative/unordered spectra and inconsistent threshold IDs fail.
Synthetic windows test first eligibility700, exact IDs despite equal counts,
global dimension, strict .05 equality rejection, both transitions, selected
versus rejected local spectra, and all selected quartet gaps. Large individual
q95 changes with unchanged spectral shape no longer block stopping.

Retrospective oracles detect any later decision change even if the final state
returns; gap fluctuation alone is not premature. No-stop and reference-only
cases record the absence of later evidence. A dedicated real-workflow test
forbids SVD, RNG, fitting, optimization, normalization/CHIM and all old pipeline
runners, verifies source hashes and mtimes unchanged, and independently checks
all4040 saved gap rows against the historical q95 table.

Locked sync, pytest with coverage, Ruff, strict mypy and diff whitespace checks
are required. Full regression tests may exercise historical modules in isolated
temporary directories; the revised scientific analysis itself never reexecutes
the upstream pipelines. No archived experiment is replaced. Final results and
delivered-head CI are recorded below after verification.

No data/model/solver/sampler/normalization/geometry/PA-selection change, no new
dependency or lock change, and ADR 0008 remains byte-identical. ADR 0009 is
PROPOSED; C-PA-05/06/07 are decision/definition claims, not statistical validity
claims. Freeze v2 for future independent synthetic/application validation.

## Completed local gate and canonical application

Source commit5a2b6cdb8595c5524af5cdfe2af076a2125366b8 was clean at the canonical
revision run. All17 input hashes match Git blobs at that commit; all7 output
checksums passed. The original archive is unchanged. The revised run is
turning_spectral_gap_policy_v2_20261024, B_stop_gap1300, same dimension2 and37
IDs through2000. Retrospective status EARLY_STOP_RETROSPECTIVELY_DECISION_STABLE;
post-stop maximum gap change1.1791584724 pp; potential replica reduction35%.

uv sync --locked PASS; pytest502 passed in34.70s; coverage99.50%
(1577/1585), new module159/159 and chim/100%; Ruff PASS; strict mypy PASS
on26 source files; git diff --check PASS. Eight old workbook-inspection lines
remain uncovered. No dependency change. All historical production scientific
modules/artifacts, raw/processed data and ADR0008 have zero diff from fc57b05.

Delivered-head Ubuntu/Windows push/pull-request CI results and final commit are
recorded in the updated PR #8 and final delivery report, after the push. No merge.
