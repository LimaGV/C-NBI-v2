# Phase 6 verification gate

Preflight2026-10-24: branch feature/05-chim-svd-local-pa at4942cfe093918d4b27acb08f847ca51bf7921697
clean/synchronized. PR #8 reviewed, OPEN/MERGEABLE/CLEAN, all4 Ubuntu/Windows
push/PR checks SUCCESS. Locked sync,502 pytest, Ruff and strict mypy passed.
Authorized squash merged as1053f297ad9263d3219532c14f7dfc19fb42c29a; local main
updated/clean before feature/06-simplex-lattice-local-nbi was created.

Before canonical execution:50 new tests passed, full552-test regression passed,
coverage99.52% (1879/1888 statements), nbi100%, lattice.py97.44% (unreached internal
count guard), only8 old workbook lines otherwise uncovered. Ruff and strict
mypy32 source files pass. Source and central options are committed before the
real archive execution; actual clean source commit is recorded by metadata.

Oracles cover lattice counts and rational nesting; normal rank/unit/sign,
permutation and MIN/MAX, exact anchor feasibility, analytic Jacobians,
closed-form linear NBI, separate60-digit quadratic reference, retry/failure
handling, independent success/finite/equality/sphere gates, numerical dedup
provenance, strict full-space dominance and known directed distances. Frozen
real selection/models and37 local geometries verified; nine small real solves
pass with fitter/RNG/anchor optimization/PA entry points forbidden. Inputs'
bytes and mtimes are unchanged. No generic100%-success assertion is used.

Final real results, independent archive checks and delivered-head CI are
recorded after execution below and in the application report/PR. All data,
previous results, models/solvers/sampler/Phase5 selection/policies remain
unchanged. No dependency/lock change, external benchmark or next phase.

## Canonical result and completed local gate

Source d8d3de5f89efcca9d3c52eeac5a2d1d57dac09af was clean at execution.
All21 input hashes match that source's Git blobs; all12 output checksums passed.
4557 distinct H20 subproblems,4557 accepted,0 final failures,4559 attempts.
Two status8 nearest-weight attempts were independently rejected and recovered
by the predefined convex start. No tolerance changed. Maximum eq_norm
9.195331178012219e-12, minimum sphere margin-9.64650581636306e-12 (inside1e-9).
Parent solves7.4831227995455265s, total workflow10.283399499952793s before
metadata serialization. H20 gives4476 unique decisions/4417 full8-space ND;
H10 directed coverage mean.0288245400363719,q95.09794950457410848,max.19877931793790762.
H20 retained as internal validation resolution; no final H accepted.

Final commands: uv sync --locked PASS; uv run pytest -v556 passed in26.03s;
uv run pytest --cov=cnbi_v2 --cov-report=term-missing -q556 passed in41.85s;
coverage99.52% (1879/1888); NBI100%, lattice.py97.44% (only internal count guard
unreached). Ruff PASS; strict mypy PASS on32 source files; git diff --check PASS.
Four new archived-case tests independently validate all4557 x/eight-response
values, ray/sphere/normal properties, exact memberships/provenance, full-space
ND and both distance directions without re-solving the parent. Total54 new tests.

No diff to original data, prior results, RSM/optimizer/sampler/CHIM/PA modules,
policies, dependencies or uv.lock from1053f29. One reviewed5.05MB archive,
one parent NPZ, no LFS. Complete12-output manifest SHA-256:
fb332fe017dd40a29344892da63907b0bf8f782c29a5695f2c376844c0b83b72.

Delivered-head CI and final commit/PR are recorded in the PR and final delivery
report after push. No automatic merge or next phase.
