"""Read-only Phase10D source inventory and narrowly scoped Phase10E outputs."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "5c3829dbd1bdd41ee828cfaf919c551d4f869d32"
INPUT = ROOT / "results/phase_10_synthetic_benchmark/benchmark_20261029/campaign_v2"
OUTPUT = ROOT / "results/phase_10_synthetic_analysis/statistical_20261030"
STRUCTURAL = ROOT / "results/phase_10_synthetic_generation/structural_20261029"
PARETO = ROOT / "results/phase_10_synthetic_pareto/analytical_20261029"
METHODS = ("C-NBI", "VRF-NBI", "NSGA-III", "MOEA/D")
CURRENT_DOCS = {"AGENTS.md", "README.md", "CHANGELOG.md", "ROADMAP.md"}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, allow_nan=False) + "\n").encode())


def table(path, rows):
    if not rows:
        raise ValueError("cannot silently omit an empty analysis table")
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def name(task):
    return f"official__{task['instance_id']}__{task['method'].replace('/', '_')}"


def snapshot():
    target = OUTPUT / "frozen_inputs_manifest.json"
    if target.exists():
        raise FileExistsError("input snapshot is immutable")
    paths = (
        subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "-z", BASE], cwd=ROOT)
        .decode()
        .split("\0")
    )
    files = {p: digest(ROOT / p) for p in paths if p and p not in CURRENT_DOCS}
    write(target, dict(input_commit=BASE, files=files, permitted_current_docs=sorted(CURRENT_DOCS)))
    print(json.dumps(dict(frozen_files=len(files), output=str(target))), flush=True)


def verify():
    manifest = read(OUTPUT / "frozen_inputs_manifest.json")
    if manifest["input_commit"] != BASE:
        raise ValueError("wrong Phase10D baseline")
    for path, expected in manifest["files"].items():
        if digest(ROOT / path) != expected:
            raise ValueError("protected source changed: " + path)
    return len(manifest["files"])


if __name__ == "__main__":
    snapshot()
