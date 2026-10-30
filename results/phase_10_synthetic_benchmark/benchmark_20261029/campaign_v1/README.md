# Phase10D — archived initial campaign

Status: ARCHIVED_IMPLEMENTATION_ERROR / INCOMPLETE. Twelve pilot runs completed
and passed the original gate. Of540 planned official runs,77 were attempted:
75 COMPLETED and two FAILED. The retained failures identify VRF-NBI on
nx2_delta1_rho085, replicas4 and5. All checkpoints, logs and numerical outputs
are preserved. STOP_REQUESTED.json permanently identifies this stopped queue.

The adapter raised at500 Varimax iterations, while factor-analyzer0.5.1/v1
returns the last iterate. The corrected implementation preserves500 and1e-5
and records nonconvergence explicitly. Its two boundary-case regressions match
the legacy library. A separate, complete new campaign lives in ../campaign_v2/;
these77 attempts are not mixed with it. Do not resume this archived scheduler.

Scientific source77c8e12 and protocol
93193c91852710591b7062ac64732f5cb403fa79af399bb168a3c1b33281e7df
are frozen before this pilot and the official campaign. The generation manifest
records full source hashes, configurations and the source commit. The hardware
execution plan identifies six physical-core masks with one numeric thread per
independent process. FIFO scheduling never influences task seeds or objectives.

Search receives only the frozen noisy RSM and permitted CCD observations and
estimated uncertainty quantities. Original RSMs are never refitted. The true
Phase10C evaluator runs in a separate process after optimization completes.
All previous-phase scientific files, original raw datasets and excluded-material
licenses remain unchanged.

Raw outputs and attempts are immutable. Completed checkpoint payloads reload
only after checksum validation. Operational retries require a recorded reason
and cannot replace a retained scientific outcome. The540-task manifest keeps
failures and pending tasks. Native true full-objective ND cardinality is primary;
no cardinality equalization, tuning, inference or Phase10E is performed.

The command sequence below documents the original workflow. It must not be
executed against this archived directory. The default now selects campaign_v2.
The dedicated v2 uv environment is used:

```powershell
uv run python scripts/validation/run_phase10d_campaign.py --pilot
uv run python scripts/validation/compare_phase10d_pilots.py
uv run python scripts/validation/execute_synthetic_benchmark.py evaluate --stage pilot
uv run python scripts/validation/verify_synthetic_benchmark_pilot.py
uv run python scripts/validation/run_phase10d_campaign.py
uv run python scripts/validation/execute_synthetic_benchmark.py evaluate --stage official
uv run python scripts/validation/postprocess_phase10d.py --figures
```

Do not rerun completed tasks to improve outcomes. For reproducibility, preserve
the recorded code/protocol/hardware plan and the complete attempt history.
