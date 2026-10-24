# Phase 3 verification and traceability

Date: 2026-10-24. Branch: feature/03-multivariate-coefficient-monte-carlo.

## Authorized preparation

PR #5 head 6e15beb48a238126b87da41b66260fe82e6c68a1 was OPEN,
MERGEABLE/CLEAN with four successful Windows/Ubuntu checks. Local locked sync,
300 tests, coverage 99.08%, Ruff and mypy passed again. Authorized squash merge
produced main 74d6723b9a622e9e5f8a75f3a543c52a92a318eb. Main was updated and
clean before creation of the requested branch.

## Scientific gate

The original-coded Phase 2 case is reused, including verified axial codes
plus/minus 1.682. It remains distinct from the physical fit. A single existing
RSMFit supplies B_hat, R/V_X and raw E'E/9. The archived Phase 2 coefficients
are checked numerically; no independent OLS implementation, changed response,
published-coefficient surrogate or refitted response scale is introduced.

Tests cover algebraic roots, PSD singular and zero covariance, significant
indefiniteness failures, explicit roundoff handling, full Kronecker orientation,
cross-response covariance blocks, synthetic mean/covariance moments with
justified six-SE tolerances, seed isolation, exact prefixes/chunk equality,
nonfinite and invalid inputs, immutable inputs/outputs, and all 20 checkpoints.
The integrated real-data test counts one fitter call and one 2000-replica sampler
call, while replacing every anchor/payoff entry point with a failing sentinel.
Every archived CSV metric is independently recomputed using column-vec np.cov.

ADR 0006 is ACCEPTED in the scope explicitly requested. C-MC-01 derives the
covariance; C-MC-02 records finite-seed internal evidence without a monotonicity
claim; C-MC-03 is a METHODOLOGICAL_DECISION, not an empirical optimum for B.
The future PA policy is PROPOSED and current status NOT_APPLIED_PHASE_3.

## Quality and archive

Commands: uv sync --locked; uv run pytest -v; uv run pytest --cov=cnbi_v2;
uv run ruff check .; uv run mypy src; git diff --check.
Local gate: 356 tests, 99.22% coverage (1022/1030 statements), new uncertainty/
100%, existing model/ and optimization/ 100%, mypy strict 18 source files.
Only the same eight pre-existing workbook-inspection statements are uncovered.
The final PR head will be checked in Windows and Ubuntu by the four CI jobs.

Matplotlib is a justified development dependency solely for the requested
exported PNG; no production dependency was added. Lock accompanies the change.
The runtime sampler uses only existing NumPy/SciPy. No parallel executor/GPU.

The source is committed before the canonical archive is executed, so metadata
records its actual clean source commit. Reviewed small artifacts are committed
afterwards, with an exact .gitignore run exception. Input hashes must match that
source commit's blobs; output hashes are in metadata and checksums.sha256.
The [applied report](mathematics/turning_coefficient_mc.md) records the actual
source commit, object hashes, 20 diagnostics and file checks.

Raw/processed values, earlier artifacts and existing RSM/optimization code
remain unchanged. The new PR is submitted for review, without automatic merge.
No subsequent phase is started.
