# Phase10D — preserved pilots and versioned campaigns

This directory preserves the initial twelve sequential pilot runs, produced
by source4f051d51a39c62172aa1030684a21c607ff8e179. All twelve completed.
Its original protocol, intermediate migration failures, corrected migration
validation, raw decisions, raw RSM predictions and complete diagnostics are
retained without replacement.

`campaign_v1/` preserves twelve additional pilot runs and the first77 official
attempts (75 completed, two failed). Its status is ARCHIVED_IMPLEMENTATION_ERROR.
The VRF adapter incorrectly raised at the Varimax iteration limit, whereas the
legacy library returns the final iterate. No earlier output has been deleted,
replaced or promoted selectively into the corrected campaign.

The corrected frozen protocol, twelve-run pilot and complete new540-task
campaign are in `campaign_v2/`. Its method barriers follow the user's order:
all135 C-NBI, then all135 VRF-NBI, then all135 NSGA-III, then all135 MOEA/D.
All twelve corrected pilot X/Y arrays match this initial sequential pilot
bitwise; common counters match. The original twenty-four pilot executions and
the77 initial official attempts remain separate from the corrected results.

See `campaign_v2/README.md` and `docs/phase_10d_verification.md` in the repository
for the current campaign status. Execution completion and artifact validation
must both be checked before calling the benchmark complete.

No results in this directory justify any recalibration or modification of the
true references. Data and scientific results are outside the original-code MIT
grant; no additional material license is assigned here.
