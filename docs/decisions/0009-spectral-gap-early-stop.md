# 0009 — Normalized q95 spectral gaps for proposed PA stopping

- Status: PROPOSED. Policy v2 status: PROPOSED_REVISED; no methodological promotion.
- Date: 2026-10-24.
- Branch: feature/05-chim-svd-local-pa; same PR #8, no merge.
- Explicit revision of the stopping policy only; ADR 0008 is preserved unchanged.
- Post hoc on the turning case: defined after inspecting its first sensitivity
  trajectory. This application is not external validation of the tolerance.

## Context and proposed decision

V1 monitored the maximum individual relative q95 change over all 357 thresholds,
including rejected subsets. An isolated small or irrelevant threshold could
block stopping. Preserve the original JSON byte-for-byte in
`docs/policies/history/pa_early_stop_policy_v1.json`, SHA-256
`e738a49b7df5aca0beaca8ed7a4229dbbfeed2aecd5160de0a4414eda73b43db`.
The historical runner explicitly consumes that archive. Its results and metadata
remain immutable records of the source commit at which they were generated.

For descending nonnegative q95 reference spectrum q_r(B), define
d_r=q_r-q_(r+1) and g_r=d_r/max(q_r,epsilon_q). Monitor absolute changes
abs(g_r(B)-g_r(B-100)), with no further division by the gap. The operational
strict tolerance is 0.05: five percentage points of normalized-gap change,
not 5% statistical error, confidence, or a universal limit. Positive common
scaling leaves nondegenerate gaps invariant.

Use epsilon_q=float64.tiny, exactly 2.2250738585072014e-308. If both adjacent
q95 values are <=epsilon_q, return gap zero and DEGENERATE_Q95_SPECTRUM.
No statistical regularization. Reject descending-order violations exceeding
8*eps64*max(q_1,epsilon_q); smaller negative differences become zero gaps
without modifying q95. Scale invariance presumes values remain nondegenerate
and representable under the common rescaling.

Keep q=.95, linear interpolation, all 20 prefixes 100:100:2000, B_min=500,
and B=2000 as the complete scientific reference. Require three checkpoints
already >=500; the first complete eligible window is 500/600/700, ending at700.
Require exact equal global dimension and selected ID sets at all three points.
Monitor all six global gaps and all gaps from selected local k>=3 spectra,
using the same monitored set in both transitions. Both maximum absolute gap
changes must be strictly <.05. Pairs have one singular value and no gap;
their stability is covered by exact selection identity.

For diagnostic rows whose full selections differ, local monitors are the
intersection of selected k>=3 IDs across the current window. Such rows can
never stop, regardless of their gaps. Before three checkpoints are available,
the available-prefix intersection is diagnostic only. Do not substitute each
transition's own candidate set when checking a three-point window.

Select the first eligible joint success programmatically, without assuming
a target B. Continue retrospectively through2000. Compare every later global
dimension and selected set to the stop decision; any divergence, even if the
final decision later returns, is PREMATURE_STOP_DETECTED. Otherwise report
EARLY_STOP_RETROSPECTIVELY_DECISION_STABLE when later checkpoints exist.
At a reference-only stop there is no later evidence. Report later gap changes
separately using the monitor set frozen at the stop window; gap fluctuation
alone does not imply a premature scientific decision.

## Boundaries, validation and consequences

Observed singular values and margins are fixed/decision diagnostics, not gap
convergence inputs. Gaps never filter subsets or define global dimension.
Every historical threshold, margin, PASS/FAIL, dimension and selected ID must
match exactly when recomputed from the saved noise arrays. All 154 candidates
and the 19 pairs/18 triples/0 quadruples at2000 remain unchanged.

Only q95 prefix quantiles, gaps and stopping diagnostics are recomputed. No
coefficient Monte Carlo, anchor optimization, payoff, normalization, CHIM or
SVD is run by the revision. Test the new workflow with all upstream operations
forbidden. Synthetic oracles cover known/equal/zero spectra, scale invariance,
gap counts, exact identities, eligibility, both transitions, strict equality
rejection, selected versus rejected spectra, and retrospective decision changes.

Freeze policy v2 before its archived application. Future work must test the
unchanged rule on independent synthetic cases and other applications. Passing
implementation tests or a stable post-hoc turning trajectory does not establish
universal validity or justify automatic promotion. No lattice H, NBI/C-NBI,
new phase, new dependencies or merge is included.
