# Phase10D — corrected ordered synthetic benchmark

Status: COMPLETED. All540 official searches and540 external evaluations finished;
135 searches per method, zero execution failures. The540-run artifact audit and
all135 pairing blocks passed. Pilot:12/12 COMPLETED, no failures, migration and
external validation PASS; X/Y match the preserved sequential pilot bitwise.
Final software-quality/CI evidence is in docs/phase_10d_verification.md.

Numerical source:8f9d60f89fc06814a78d1a1cd9c42ea3ac37fbee. Protocol SHA-256:
19dff29411ad39293f4e429f8f77babd424213a5da61baf7e69855c0ea7209cf.
The generation manifest freezes each source/configuration file and all1262
protected files from Phases0–10C. Seven explicitly listed current-state
documents are mutable; original data and excluded-material licenses are not.
generation_manifest_at_freeze.json preserves the byte-identical pre-execution
manifest. The current generation manifest adds completion metadata while its
source/configuration maps and protocol hash remain unchanged.

Official order is fixed by hard method barriers:135 C-NBI →135 VRF-NBI
→135 NSGA-III →135 MOEA/D. Within a block, at most six independent processes
run on separate physical cores, each with one numerical thread. The execution
plan, per-task receipts and completed barriers are archived. Per-run timings
describe this disclosed concurrent environment, rather than an idle host.

The corrected Varimax adapter returns the last iterate at500, matching the v1
library, and records varimax_converged=false. Its tolerance remains1e-5.
The earlier24 pilot executions and77 official attempts (including two failures)
remain in the parent/campaign_v1 directories. This is a whole new scientific
version of the campaign; there is no selective replacement of failed cases.

Inputs are the same135 frozen multivariate RSMs. C-NBI uses B=2000 and every
eligible local subset with strict PA q95. VRF-NBI uses full quartic VRF
objectives and only permitted auxiliary factor fits. EAs use the18 pinned v1
calibration records and complete-generation floor within their common ceiling.
No true response, anchor or reference is passed into any search interface.

Search wall time:9029.539s(2h30m29.539s); external evaluation:299.964s;
read-only audit:359.386s. Release tables preserve27 structural cells with five
nested replicas, native cardinality, original worker timers and additional
full lifecycle observations. All540 lifecycle event windows were verified.
Three Varimax rotations reached500 iterations; two VRF HV estimates remain
PRECISION_PENDING. These flags and tiny raw sphere violations remain explicit.
See release_summary.json/release_tables.md and the full verification report.

The unchanged Phase10C API evaluates raw decisions only after all searches
terminate. Original-objective ND cardinality is native, with fixed analytical
normalization and no clipping. Infeasible raw decisions, undefined metrics and
HV precision flags remain visible. No inference, equalization, tuning or10E.

Reproduction from the repository root:

```powershell
uv sync --locked
uv run python scripts/validation/run_phase10d_campaign.py --pilot
uv run python scripts/validation/compare_phase10d_pilots.py
uv run python scripts/validation/evaluate_phase10d.py --stage pilot
uv run python scripts/validation/verify_synthetic_benchmark_pilot.py
uv run python scripts/validation/run_phase10d_campaign.py
uv run python scripts/validation/evaluate_phase10d.py --stage official
uv run python scripts/validation/postprocess_phase10d.py --figures
uv run python scripts/validation/audit_phase10d_outputs.py
```

Use a separate output directory for an independent reproduction. Retained
scientific payloads are immutable; completed checkpoints verify and reload.
For a clean numerical reproduction, the8f9d60f source checkout precedes the
creation of this directory. In a separate worktree, run synthetic_benchmark_audit.py
and validate_synthetic_benchmark_migration.py with --legacy <pinned_v1_repo>
before the pilot sequence above. See docs/reproducibility.md for the workflow.
Never resume campaign_v1 or overwrite a retained outcome to improve quality.
The final verification document reports exact counts, metrics, costs, checks,
hashes and limitations. Data/results are outside the original-code MIT grant;
no new license for excluded materials is assigned.
