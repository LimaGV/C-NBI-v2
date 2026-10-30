"""The released campaign must contain every paired task and preserved history."""

from collections import Counter
from pathlib import Path

import numpy as np

from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, verify_payload
from cnbi_v2.synthetic.benchmark.contracts import METHODS

ROOT = Path(__file__).resolve().parents[3]
CASE = ROOT/"results/phase_10_synthetic_benchmark/benchmark_20261029"
DIRECTORY = CASE/"campaign_v2"


def test_all_540_tasks_have_traceable_terminal_payloads():
    manifest = read_json(DIRECTORY/"seed_manifest.json")
    official = [task for task in manifest["tasks"] if task["stage"] == "official"]
    assert len(official) == 540
    assert Counter(task["method"] for task in official) == dict.fromkeys(METHODS, 135)
    paired = {}
    for task in official:
        name = f"official__{task['instance_id']}__{task['method'].replace('/', '_')}"
        checkpoint = read_json(DIRECTORY/f"campaign_checkpoints/{name}.json")
        assert checkpoint["identity"] == task
        assert checkpoint["state"] in {"COMPLETED", "FAILED", "INCOMPLETE"}
        if "payload_checksums" not in checkpoint:
            assert checkpoint["state"] != "COMPLETED" and checkpoint.get("error")
            continue
        verify_payload(DIRECTORY, checkpoint["payload_checksums"])
        payload = checkpoint.get("payload_run_id", name)
        metadata = read_json(DIRECTORY/f"algorithm_diagnostics/{payload}.json")
        assert metadata["task"] == task
        paired.setdefault(task["instance_id"], {})[task["method"]] = metadata[
            "coefficients_sha256"]
        with np.load(DIRECTORY/f"raw_decisions/{payload}.npz", allow_pickle=False) as arrays:
            assert arrays["decisions"].dtype == np.float64
            assert arrays["decisions"].shape[0] == checkpoint["output_count"]
        record = read_json(DIRECTORY/f"external_evaluation/{name}.json")
        assert not record["oracle_feedback_to_search"]
        assert record["reference_count"] == 5000
        assert record["diagnostics"]["cardinality_mode"] == "native"
    assert len(paired) == 135
    assert all(len(set(methods.values())) == 1 for methods in paired.values())
    audit = read_json(DIRECTORY/"artifact_audit_official.json")
    assert audit["status"] == "PASS" and audit["audited_runs"] == 540
    assert audit["preserved_previous_file_hashes"] and audit["frozen_previous_files"] == 1262


def test_release_hashes_and_method_barriers():
    for line in (DIRECTORY/"checksums.sha256").read_text().splitlines():
        expected, name = line.split("  ", 1)
        assert file_hash(DIRECTORY/name) == expected
    barrier = read_json(DIRECTORY/"method_execution_barriers.json")
    assert barrier["order"] == list(METHODS)
    assert [row["method"] for row in barrier["barriers"]] == list(METHODS)
    assert all(row["processed"] == row["planned"] == 135 and row["all_tasks_finished"]
               for row in barrier["barriers"])
    chronology = read_json(DIRECTORY/"execution_chronology.json")
    assert chronology["status"] == "PASS" and chronology["method_order"] == list(METHODS)
    assert chronology["all_previous_checkpoints_finished_before_next_method_started"]
    assert all(left["last_checkpoint_epoch"] <= right["first_checkpoint_epoch"]
               for left, right in zip(chronology["windows"], chronology["windows"][1:],
                                      strict=False))


def test_initial_failures_and_all_predecessor_pilots_remain_archived():
    inventory = read_json(CASE/"archive_inventory.json")
    assert inventory["history"]["sequential_pilot"]["states"]["pilot"] == {"COMPLETED": 12}
    earlier = inventory["history"]["initial_campaign"]
    assert earlier["states"] == dict(pilot={"COMPLETED": 12},
                                     official={"COMPLETED": 75, "FAILED": 2})
    assert len(earlier["failures"]) == 2
    for record in earlier["failures"]:
        task = record["identity"]
        name = f"official__{task['instance_id']}__VRF-NBI"
        old = read_json(CASE/f"campaign_v1/campaign_checkpoints/{name}.json")
        assert old["state"] == "FAILED" and old["error"] == record["error"]
        assert (CASE/f"campaign_v1/logs/{name}.log").exists()
    assert (CASE/"campaign_v1/STOP_REQUESTED.json").exists()
