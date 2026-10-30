"""Immutable baseline and isolated outputs for the requested pairwise revision."""

import subprocess

from phase10e_inputs import (
    CURRENT_DOCS,
    INPUT,
    PARETO,
    ROOT,
    STRUCTURAL,
    digest,
    name,
    read,
    table,
    write,
)
from phase10e_inputs import OUTPUT as PREVIOUS

BASE = "784650a13afc496dab8b1cfab4a2c100a9c5539e"
OUTPUT = ROOT / "results/phase_10_synthetic_analysis/pairwise_20261030"
COMPARATORS = ("VRF-NBI", "NSGA-III", "MOEA/D")


def pair_id(comparator):
    return "CNBI_vs_" + comparator.replace("-", "_").replace("/", "_")


def snapshot():
    target = OUTPUT / "frozen_inputs_manifest.json"
    if target.exists():
        raise FileExistsError("pairwise input snapshot already frozen")
    paths = (
        subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "-z", BASE], cwd=ROOT)
        .decode()
        .split("\0")
    )
    files = {p: digest(ROOT / p) for p in paths if p and p not in CURRENT_DOCS}
    write(target, dict(input_commit=BASE, files=files, current_docs=sorted(CURRENT_DOCS)))
    print(f"Frozen {len(files)} previous files", flush=True)


def verify():
    manifest = read(OUTPUT / "frozen_inputs_manifest.json")
    if manifest["input_commit"] != BASE:
        raise ValueError("wrong baseline for pairwise correction")
    for path, expected in manifest["files"].items():
        if digest(ROOT / path) != expected:
            raise ValueError("previous result/source changed: " + path)
    return len(manifest["files"])


__all__ = [
    "BASE",
    "COMPARATORS",
    "INPUT",
    "OUTPUT",
    "PARETO",
    "PREVIOUS",
    "ROOT",
    "STRUCTURAL",
    "digest",
    "name",
    "pair_id",
    "read",
    "table",
    "verify",
    "write",
]


if __name__ == "__main__":
    snapshot()
