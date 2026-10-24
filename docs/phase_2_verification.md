# Phase 2 verification and traceability

Date: 2026-10-24. Branch: feature/02-individual-anchors-response-region.

## Authorized preparation

PR #4 head 233d17fdf4d6a2ea9838bc6fd133a1e74080f1ee was OPEN,
MERGEABLE/CLEAN, with four successful Ubuntu/Windows checks. Local
uv sync --locked, 237 tests, coverage 98.47%, Ruff and mypy passed again.
Explicitly authorized squash merge produced main commit
64b09f9bc413778efe47cfce9b586fe2ce2a2630;
main was fast-forwarded and clean before creating the requested Phase 2 branch.

## Scientific and data gates

- Existing RSM, diagnostics and uncertainty implementation unchanged.
- Source XLSM SHA and all literal coordinates checked read-only. No macros,
  links, formulas or cached responses evaluated as scientific input.
- Nineteen original coded/physical pairs join exactly to canonical CCD IDs.
  Physical/coded fitted equivalence FAILED, up to 2.5658% response-range error.
  Owner clarification prioritizes the spreadsheet; the case is explicitly
  distinct, with no asserted continuous inverse/physical anchor coordinates.
- Theoretical ball alpha=8^(1/4), separate from source axial code 1.682.
- Cloud covariance rank 8, numerical SPD/Cholesky gate passed; no correction.
- Legacy chi-square .95 cutoff is EXPERIMENTAL, not an exact confidence claim.
- Eight anchors pass global classical KKT/PSD certificates and are already
  response-region feasible. Both separately stored payoffs therefore coincide.
- Empirical .95 and chi-square .99 cutoff sensitivity leaves all anchors unchanged.

## Checks

Commands: uv sync --locked; uv run pytest -v; uv run pytest --cov=cnbi_v2;
uv run ruff check .; uv run mypy src; git diff --check.
Local gate PASSED: 300 tests; coverage 99.08% (861/869 statements),
new optimization package 100%, model/ still 100%; mypy 15 source files.
Actual command outcomes and CI are linked to the delivered PR head.

Tests include analytic one/two/three-factor MIN/MAX optima, hard cases,
independent SciPy validation, exact interaction extraction, Mahalanobis geometry
and invariance, singular covariance failures, quartic/disconnected RC constraints,
nonconvex-objective multistart, independent feasibility checks, payoff orientation,
immutable arrays, source joins/hashes, raw preservation, all eight real anchors,
both payoff matrices and cutoff sensitivity. No published numbers generate data.

## Reproduction and review

Source commit is recorded by metadata.json during the archived run, from a clean
working tree before the output directory is created. Reviewed small outputs
are subsequently versioned with an exact .gitignore exception for the run.
Every output has SHA256 in checksums.sha256; code/data/lock input hashes,
model coefficient hash, solver options, complete start proposals and decisions
are versioned. Existing output directories cannot be overwritten by the runner.

Run in a fresh output directory:

```powershell
uv sync --locked
uv run python -m scripts.validation.turning_anchors --run-id turning_original_codes_reproduction --output "$env:TEMP/cnbi-phase02-reproduction"
```

The original coding extract is versioned and hashed, so execution does not need
access to the source XLSM. Re-extraction, if separately desired, requires that
original exact source hash and is explicitly selected by --extract-coding-source.
No original XLSM/PDF/notebook is published. Raw XLSX/CSV and all Phase 1 outputs
remain unchanged. ADR 0005 is EXPERIMENTAL; no RC adoption, Monte Carlo,
NBI/C-NBI or subsequent phase is authorized by this gate.
