# Phase10D — final frozen protocol

Status: INCOMPLETE until the required pilot gate and all official tasks have
been executed and audited. Planned:27 structural cells ×5 frozen noisy RSM
replicas ×4 methods =540 official runs. Final pilot:12 preselected tasks.

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

Commands from the repository root use the dedicated v2 uv environment:

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
