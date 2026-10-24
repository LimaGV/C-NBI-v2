# Phase 6 verification gate

Preflight2026-10-24: branch feature/05-chim-svd-local-pa at4942cfe093918d4b27acb08f847ca51bf7921697
clean/synchronized. PR #8 reviewed, OPEN/MERGEABLE/CLEAN, all4 Ubuntu/Windows
push/PR checks SUCCESS. Locked sync,502 pytest, Ruff and strict mypy passed.
Authorized squash merged as1053f297ad9263d3219532c14f7dfc19fb42c29a; local main
updated/clean before feature/06-simplex-lattice-local-nbi was created.

Before canonical execution:50 new tests passed, full552-test regression passed,
coverage99.52% (1879/1888 statements), nbi100%, simplex97.44% (unreached internal
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
