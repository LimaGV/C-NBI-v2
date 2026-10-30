"""No method may start before the preceding method's tasks have terminated."""

import json
import threading
import time
from pathlib import Path
from types import SimpleNamespace

from cnbi_v2.synthetic.benchmark.archive import read_json, write_json
from cnbi_v2.synthetic.benchmark.contracts import METHODS


def test_strict_method_barriers_and_preserved_terminal_outcomes(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[3]
    monkeypatch.syspath_prepend(str(root/"scripts/validation"))
    import run_phase10d_campaign as scheduler
    tasks = [dict(stage="official", instance_id=f"toy{replica}__replica1",
                  scenario_id=f"toy{replica}", replica_id=1, method=method, seed="1")
             for replica in (1, 2) for method in METHODS]
    write_json(tmp_path/"seed_manifest.json", dict(tasks=tasks))
    write_json(tmp_path/"pilot_verification.json", dict(status="PASS"))
    write_json(tmp_path/"campaign_manifest.json", dict(status="INCOMPLETE"))
    monkeypatch.setattr(scheduler, "verify_protocol", lambda p: dict(
        protocol_hash="unit_protocol", code_commit="unit_source"))
    monkeypatch.setattr(scheduler, "physical_masks", lambda: [1, 2])
    finished = {method: 0 for method in METHODS}
    lock = threading.Lock()
    calls = []
    preserved = tasks[0]
    path = tmp_path/f"campaign_checkpoints/{scheduler.run_id(preserved)}.json"
    write_json(path, dict(state="COMPLETED", preserved=True))
    original_bytes = path.read_bytes()
    finished["C-NBI"] = 1

    def process(command, **kwargs):
        task = json.loads(command[-1])
        method = task["method"]
        with lock:
            for earlier in METHODS[:METHODS.index(method)]:
                assert finished[earlier] == 2
            calls.append(method)
        time.sleep(.002)
        write_json(tmp_path/f"campaign_checkpoints/{scheduler.run_id(task)}.json",
                   dict(state="COMPLETED", timings=dict(total=.002)))
        with lock:
            finished[method] += 1
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(scheduler.subprocess, "run", process)
    monkeypatch.setattr(scheduler, "report_runs", lambda p, stage: [dict(
        **task, state=read_json(p/f"campaign_checkpoints/{scheduler.run_id(task)}.json")["state"])
        for task in tasks])
    scheduler.execute(tmp_path, False)
    assert path.read_bytes() == original_bytes
    assert len(calls) == 7
    assert [METHODS.index(method) for method in calls] == sorted(METHODS.index(m) for m in calls)
    barriers = read_json(tmp_path/"method_execution_barriers.json")["barriers"]
    assert [row["method"] for row in barriers] == list(METHODS)
    assert all(row["all_tasks_finished"] for row in barriers)
