"""Compare final scheduled pilot with preserved sequential pilot, without truth."""

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from execute_synthetic_benchmark import OUTPUT, ROOT, run_id, verify_protocol

from cnbi_v2.synthetic.benchmark.archive import read_json, verify_payload, write_json


def compare(directory: Path = OUTPUT) -> None:
    current = verify_protocol(directory)
    previous = directory.parent
    original = read_json(previous/"generation_manifest.json")
    # Old source is versioned evidence; it is verified against its own Git
    # commit, not silently declared identical to the currently working source.
    for name, expected in original["scientific_source"].items():
        blob = subprocess.check_output(["git", "show", f"{original['code_commit']}:{name}"],
                                       cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError("original pilot source does not match its declared commit")
    rows = []
    for task in read_json(directory/"seed_manifest.json")["tasks"]:
        if task["stage"] != "pilot":
            continue
        name = run_id(task)
        old = read_json(previous/f"campaign_checkpoints/{name}.json")
        new = read_json(directory/f"campaign_checkpoints/{name}.json")
        verify_payload(previous, old["payload_checksums"])
        verify_payload(directory, new["payload_checksums"])
        oldmeta = read_json(previous/f"algorithm_diagnostics/{name}.json")
        newmeta = read_json(directory/f"algorithm_diagnostics/{name}.json")
        matches = {}
        for folder, key in (("raw_decisions", "decisions"),
                            ("raw_rsm_responses", "rsm_responses")):
            with (np.load(previous/f"{folder}/{name}.npz", allow_pickle=False) as a,
                  np.load(directory/f"{folder}/{name}.npz", allow_pickle=False) as b):
                matches[key] = bool(np.array_equal(a[key], b[key]))
        counters_match = all(newmeta["counters"].get(key) == value
                             for key, value in oldmeta["counters"].items())
        identity_match = oldmeta["coefficients_sha256"] == newmeta["coefficients_sha256"]
        passed = (all(matches.values()) and counters_match and identity_match
                  and old["state"] == new["state"] == "COMPLETED")
        row = dict(task=task, status="PASS" if passed else "FAIL", **matches,
                   common_counters_equal=counters_match, frozen_model_equal=identity_match,
                   previous_protocol_hash=original["protocol_hash"],
                   current_protocol_hash=current["protocol_hash"],
                   replay_source="complete_final_pilot_vs_preserved_sequential_pilot",
                   added_counter_schema=2, scientific_parameters_changed=False)
        rows.append(row)
        write_json(directory/f"pilot_replay/{name}.json", row)
    if len(rows) != 12:
        raise ValueError("exactly twelve cross-schedule pilot comparisons required")
    result = dict(status="PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
                  scenarios=3, methods=4, compared_runs=12, records=rows)
    write_json(directory/"pilot_reproducibility.json", result)
    print(json.dumps({key: value for key, value in result.items() if key != "records"}))


if __name__ == "__main__":
    compare()
