"""Release checksums and Git-index byte audit for preserved Phase10D artifacts.

No algorithm is run. Hash creation excludes only the checksum files themselves
and the separate Git-index observation, preventing a circular self-digest.
"""

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from execute_synthetic_benchmark import OUTPUT, ROOT, verify_protocol

from cnbi_v2.synthetic.benchmark.archive import file_hash, read_json, verify_payload, write_json

CASE = OUTPUT.parent
EXCLUDED = {"checksums.sha256", "campaign_v2/checksums.sha256", "staged_git_integrity.json"}


def archived_history():
    result = {}
    for label, directory in (("sequential_pilot", CASE), ("initial_campaign", CASE/"campaign_v1")):
        source = read_json(directory/"generation_manifest.json")
        # Historical source differs intentionally from the corrected working tree.
        for name, expected in source["scientific_source"].items():
            blob = subprocess.run(["git", "show", source["code_commit"]+":"+name],
                                  cwd=ROOT, check=True, capture_output=True).stdout
            if hashlib.sha256(blob).hexdigest() != expected:
                raise ValueError("historical source blob mismatch: "+name)
        states = {"pilot": Counter(), "official": Counter()}
        failures = []
        for path in sorted((directory/"campaign_checkpoints").glob("*.json")):
            record = read_json(path)
            stage = record["identity"]["stage"]
            states[stage][record["state"]] += 1
            if "payload_checksums" in record:
                verify_payload(directory, record["payload_checksums"])
            if record["state"] == "FAILED":
                failures.append(dict(identity=record["identity"], error=record.get("error")))
        result[label] = dict(source_commit=source["code_commit"],
                             protocol_hash=source["protocol_hash"],
                             states={k: dict(v) for k, v in states.items()}, failures=failures,
                             all_payloads_preserved=True,
                             source_verified_against_own_git_commit=True)
    if result["sequential_pilot"]["states"]["pilot"] != {"COMPLETED": 12}:
        raise ValueError("sequential pilot history changed")
    initial = result["initial_campaign"]["states"]
    if initial["pilot"] != {"COMPLETED": 12} or initial["official"] != {
            "COMPLETED": 75, "FAILED": 2}:
        raise ValueError("initial campaign attempts omitted or replaced")
    return result


def create_checksums():
    if (OUTPUT/"scheduler.lock").exists():
        raise ValueError("wait for all search workers before finalizing artifacts")
    frozen = verify_protocol(OUTPUT)
    audit = read_json(OUTPUT/"artifact_audit_official.json")
    if audit["status"] != "PASS" or audit["audited_runs"] != 540:
        raise ValueError("official artifact audit must pass first")
    history = archived_history()
    files = sorted(path for path in CASE.rglob("*") if path.is_file()
                   and path.relative_to(CASE).as_posix() not in EXCLUDED
                   and path.name != "archive_inventory.json")
    groups = {}
    for label, paths in (("all_versions", files),
                         ("corrected_campaign", [p for p in files if OUTPUT in p.parents])):
        groups[label] = dict(files=len(paths), bytes=sum(p.stat().st_size for p in paths),
                             largest_file_bytes=max(p.stat().st_size for p in paths),
                             largest_file=str(max(paths, key=lambda p: p.stat().st_size)
                                              .relative_to(CASE)))
    write_json(CASE/"archive_inventory.json", dict(
        status="VERIFIED", numerical_source=frozen["code_commit"],
        protocol_hash=frozen["protocol_hash"], history=history,
        file_sizes_exclude_inventory_self_and_checksum_observation=True, sizes=groups,
        publication_basis="explicit Phase10D task: preserve raw outputs, version and push PR",
        original_data_modified=False, excluded_material_licenses_changed=False,
        lfs_automatically_enabled=False, source_sha256=file_hash(Path(__file__)),
    ))
    files.append(CASE/"archive_inventory.json")
    for directory in (CASE, OUTPUT):
        lines = [f"{file_hash(path)}  {path.relative_to(directory).as_posix()}\n"
                 for path in sorted(files) if directory in path.parents]
        (directory/"checksums.sha256").write_bytes("".join(lines).encode())
    return dict(status="PASS", **groups, historical_attempts_verified=77,
                final_checksum_sha256=file_hash(OUTPUT/"checksums.sha256"),
                all_versions_checksum_sha256=file_hash(CASE/"checksums.sha256"))


def verify_checksums():
    count = 0
    for directory in (CASE, OUTPUT):
        for line in (directory/"checksums.sha256").read_text(encoding="utf-8").splitlines():
            expected, name = line.split("  ", 1)
            if file_hash(directory/name) != expected:
                raise ValueError("release checksum mismatch: "+name)
            count += 1
    verify_protocol(OUTPUT)
    return dict(status="PASS", checksum_entries_verified=count)


def verify_staged():
    """Read every staged blob through one binary pipe; never print payload bytes."""
    verify_checksums()
    listing = subprocess.run(["git", "ls-files", "--stage", "-z", "--", str(CASE)],
                             cwd=ROOT, check=True, capture_output=True).stdout
    entries = [row.split(b"\t", 1) for row in listing.split(b"\0") if row]
    changed, compared, total = [], 0, 0
    with subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        assert process.stdin is not None and process.stdout is not None
        for metadata, raw_name in entries:
            blob_id = metadata.split()[1]
            name = raw_name.decode("utf-8")
            if name == str((CASE/"staged_git_integrity.json").relative_to(ROOT)).replace("\\", "/"):
                continue  # This observation is written only after checking the other blobs.
            process.stdin.write(blob_id+b"\n")
            process.stdin.flush()
            header = process.stdout.readline().split()
            size = int(header[2])
            content = process.stdout.read(size)
            if len(content) != size or process.stdout.read(1) != b"\n":
                raise ValueError("truncated Git object stream")
            if hashlib.sha256(content).hexdigest() != file_hash(ROOT/name):
                changed.append(name)
            compared += 1
            total += size
        process.stdin.close()
        process.wait()
        if process.returncode:
            raise ValueError("Git cat-file failed")
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "-z",
                                "--", str(CASE)], cwd=ROOT, check=True, capture_output=True).stdout
    staged_names = {name.decode("utf-8") for _, name in entries}
    omitted = sorted({p.decode("utf-8") for p in untracked.split(b"\0") if p
                      and not p.endswith(b"/staged_git_integrity.json")} | {
                          p.relative_to(ROOT).as_posix() for p in CASE.rglob("*")
                          if p.is_file() and p.name != "staged_git_integrity.json"
                          and p.relative_to(ROOT).as_posix() not in staged_names})
    if changed or omitted or not compared:
        raise ValueError(f"Git artifact bytes differ or are omitted: {changed}; {omitted}")
    result = dict(status="PASS", staged_blobs_compared=compared, bytes_compared=total,
                  byte_identical_to_working_files=True, omitted_artifacts=omitted,
                  excludes_only_own_observation=True, source_sha256=file_hash(Path(__file__)))
    write_json(CASE/"staged_git_integrity.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify_staged() if args.staged else verify_checksums() if args.verify
                     else create_checksums()))
