# 0017 - Paired synthetic analysis and secondary cardinality equalization

- Type: MDR
- Status: EXPERIMENTAL
- Responsible: project owner; implemented by Codex
- Date: 2026-10-30
- Branch: feature/10e-synthetic-statistical-analysis
- Commit/PR: recorded in the generation manifest and PR after validation
- Version: 1
- Supersedes: no previous scientific result; explicitly authorizes Phase10E
- Validation gate: IN_PROGRESS

## Context and definition

Phase10D contains 27 fixed structural cells, five noisy replicas per cell and
four methods per replica. The 540 runs are not 540 independent problems.
The primary comparative observation is a method's median of five replicas in
one cell. IGD and numerically valid HV are primary quality outcomes. The
protocol in `docs/policies/synthetic_analysis_10e.json` is frozen before new
analyses. Phase10D outputs, configurations and code remain byte-identical.

Holm controls the single family of 14 native primary hypotheses (two omnibus
and twelve paired tests). We use tie-corrected Friedman statistics with method
labels permuted within cells, because the usual chi-square approximation has
limitations with four methods. Pairwise Wilcoxon uses an exact conditional
sign distribution, including tied average ranks, with exact zeros removed.
The signed-rank interpretation assumes symmetric independent cell differences;
the fixed factorial experiment does not establish a population of all problems.
Bootstrap intervals resample whole paired cells, not individual runs. They are
pointwise stability descriptions, not simultaneous inferential guarantees.

HV retains a cell only when every official replicate and method is numerically
valid. Supplementary 2^18/2^20 Sobol estimates of the two pending results use
the original four scrambles, reference 1.1 and original precision budgets.
They never overwrite an official value or promote its status. Analyses with
pending estimates and with supplementary values are separately labelled.

Secondary equalization uses K=min(native ND counts) in every paired replicate.
Only original ND points can be selected. Objective minima in objective order
are forced, truncating that deterministic list if K is too small; unchanged
Phase10C FPS fills the rest in normalized objective geometry. Exact ties use
first original raw IDs. No reference distance, random draw or interpolation.

Supplementary feasibility uses norm(x)<=alpha+epsilon for epsilon in
{0,1e-12,1e-10,1e-9}, with unchanged identity/dominance conventions and no
projection. It does not replace the official strict evaluation.

For fixed-factor associations we decompose the 3x3x3 table of paired contrasts
into orthogonal marginal and interaction components. This is descriptive:
there is one anchor configuration per cell, no residual degrees of freedom in
the saturated decomposition and no causal interpretation. Observed absolute
and signed correlations are prespecified exploratory covariates.

## Evidence and alternatives

- METHODOLOGICAL_DECISION: the explicit Phase10E request and its restrictions.
- MATHEMATICAL_DERIVATION: within-cell pairing, exact rank-sum sign distribution,
  Holm's ordered step-down adjustment and orthogonal balanced-table decomposition.
- INTERNAL_EVIDENCE: frozen Phase10D inputs and independent validation oracles.
- SOFTWARE_DOCUMENTATION: SciPy 1.18.1 queried through Context7; official
  `wilcoxon`, `friedmanchisquare` and `bootstrap` documentation read directly.
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
  Software documentation supports API/assumption checks, not new scientific claims.
- Zotero query for Demsar returned no item; no invented bibliography or full-text
  verification status is assigned. No new article is required for a user-defined
  protocol validated by mathematical derivations and independent computational tests.

We reject treating replicas as independent problems, post-result metric tuning,
reference-guided point selection, hidden feasibility repair and unlabelled use
of uncertain HV. All secondary analyses remain exploratory.

## Validation and consequences

Tests cover exact small rank oracles, ties/zeros, permutations, Holm, paired
bootstrap reproducibility, balanced factorial reconstruction, FPS indices and
extreme truncation, feasibility masks and archive integrity. Full pytest,
coverage, Ruff, mypy and Ubuntu/Windows CI are required. All original artifacts
are hashed before and after processing. No optimizer entry point is invoked.
Validation does not automatically accept this methodological decision; review
remains required. The PR is stacked on the still-open Phase10D branch.

## History

2026-10-30: PROPOSED -> EXPERIMENTAL for implementation/validation under the
explicit Phase10E request. No earlier result is superseded.
