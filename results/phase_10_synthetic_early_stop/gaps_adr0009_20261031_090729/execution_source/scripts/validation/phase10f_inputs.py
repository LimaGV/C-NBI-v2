"""Isolated adaptive campaign inputs and preservation of the complete prior tree."""

import subprocess

from phase10e_inputs import (
    CURRENT_DOCS,
    INPUT,
    PARETO,
    ROOT,
    STRUCTURAL,
    digest,
    read,
    table,
    write,
)

BASE = "87362da1c17c0ffd838d3b5ca46e195f3e6065aa"
OUTPUT = ROOT / "results/phase_10_synthetic_early_stop/adaptive_20261030"
RSM = ROOT / "results/phase_10_synthetic_rsm/rsm_20261029"
POLICY = ROOT / "docs/policies/synthetic_analysis_10f.json"


def old_run(instance):
    return f"official__{instance}__C-NBI"


def tasks():
    result = [
        t
        for t in read(INPUT / "seed_manifest.json")["tasks"]
        if t["stage"] == "official" and t["method"] == "C-NBI"
    ]
    if len(result) != 135 or len({t["instance_id"] for t in result}) != 135:
        raise ValueError("exactly135 frozen C-NBI instances required")
    return result


def snapshot():
    path = OUTPUT / "frozen_inputs_manifest.json"
    if path.exists():
        raise FileExistsError("early-stop input snapshot already exists")
    names = (
        subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "-z", BASE], cwd=ROOT)
        .decode()
        .split("\0")
    )
    files = {p: digest(ROOT / p) for p in names if p and p not in CURRENT_DOCS}
    write(path, dict(input_commit=BASE, files=files, current_docs=sorted(CURRENT_DOCS)))
    write(
        OUTPUT / "seed_manifest.json",
        dict(
            seeds="exact original official C-NBI PCG64 seeds; no new seed selection", tasks=tasks()
        ),
    )
    print(f"Protected {len(files)} earlier files", flush=True)


def verify_inputs():
    manifest = read(OUTPUT / "frozen_inputs_manifest.json")
    for path, expected in manifest["files"].items():
        if digest(ROOT / path) != expected:
            raise ValueError("earlier source/data/result changed: " + path)
    return len(manifest["files"])


__all__ = [
    "BASE",
    "INPUT",
    "OUTPUT",
    "PARETO",
    "POLICY",
    "ROOT",
    "RSM",
    "STRUCTURAL",
    "digest",
    "old_run",
    "read",
    "table",
    "tasks",
    "verify_inputs",
    "write",
]


if __name__ == "__main__":
    snapshot()
