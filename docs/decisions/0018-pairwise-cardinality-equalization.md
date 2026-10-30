# 0018 - Independent C-NBI pairwise cardinality equalization

- Type: MDR
- Status: EXPERIMENTAL
- Date: 2026-10-30
- Responsible: project owner; implemented by Codex
- Branch: feature/10e-synthetic-statistical-analysis; existing stacked PR18
- Supersedes: only joint four-method equalization as the current Phase10E analysis
- Original record: commit784650a and statistical_20261030 remain byte-identical
- Validation gate: PASSED locally; exact-head Ubuntu/Windows CI required before PR readiness

## Authorization and definition

The user explicitly replaces the common four-method count with three independent
comparisons in order: C-NBI/VRF-NBI, C-NBI/NSGA-III, C-NBI/MOEA/D. The largest
equal count possible without new points is K=min(N_C,N_A) for that pair alone,
within each scenario and replica. A third front never constrains K. Each of the
135 blocks of one comparison finishes before the next comparison starts.

The validated FPS, objective-order extreme rule, analytical normalization,
raw-ID tie breaking and five metrics remain unchanged. There is no new search,
fit, point interpolation, projection, reference or scientific metric definition.
Every selected decision, normalized objective and original row ID is exported.
Previous metric values can be reused only for identical selected point sets.

The C-NBI subset can differ by comparator, so there is no common equalized
four-method table, ranking or Friedman test. Each pair has its own medians of
five replicas per cell. Two-sided exact conditional Wilcoxon, rank-biserial
effects and50000 paired-scenario bootstrap draws reuse the validated functions.
Holm jointly adjusts six quality hypotheses (three pairs x IGD/HV). Secondary
GD/Spacing/Sparsity uses a separate nine-hypothesis exploratory family.

Native pair baselines likewise use pair-specific complete numerical blocks,
with a separate six-hypothesis family. The previous native primary14 results
remain unchanged. HV pending in VRF-NBI cannot invalidate the other two pairs.
Existing supplementary HV is only reused after exact point-set identity, with
separate results/statuses; official pending estimates are never promoted.

## Evidence and scope

METHODOLOGICAL_DECISION: explicit user correction, received after the first
Phase10E analysis. This is a transparent requested revision, not a preregistered
comparison before observing the campaign. MATHEMATICAL_DERIVATION: pairwise
cardinality bound and unchanged conditional paired tests. INTERNAL_EVIDENCE:
independence tests, source hashes, FPS replay and complete archive audit.
No new literature claim or library API change is needed.

New artifacts are isolated in results/phase_10_synthetic_analysis/pairwise_20261030.
All previous scientific artifacts and source are protected by a new baseline
inventory. Only four current-state documents may change. The original global-K
result remains traceable; its conclusion must not be presented as the result
of this corrected pairwise procedure. Original data/licenses remain untouched.

## Validation and review

Test independent pair counts, full five-replica blocks, HV masks independent of
third methods, real point membership and exact FPS replay. Verify all inputs,
run full pytest/coverage, Ruff, mypy and exact-head Ubuntu/Windows CI. Keep the
existing PR18 in draft until checks pass. Do not merge PR17 or PR18. Passing
validation does not automatically accept this experimental methodological record.

Local validation:910 tests,98.30% coverage, Ruff and mypy84 passed. Independent
audit:810 subsets,405 blocks,268 fresh metric replays and542 identical-set cache
checks. All7795 previous files are unchanged. CI evidence is attached to the
final stacked PR18 head; neither PR17 nor PR18 is merged automatically.
