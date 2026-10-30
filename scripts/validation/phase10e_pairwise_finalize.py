"""Hash the current pairwise revision without touching the archived joint analysis."""

import argparse
import importlib.metadata
import subprocess
import sys

from phase10e_pairwise_inputs import BASE, OUTPUT, ROOT, digest, read, verify, write


def finalize():
    paths = [
        p
        for p in sorted(OUTPUT.rglob("*"))
        if p.is_file() and p.name not in {"checksums.sha256", "generation_manifest.json"}
    ]
    sources = list(sorted((ROOT / "scripts/validation").glob("phase10e_pairwise_*.py")))
    sources += [
        ROOT / "src/cnbi_v2/synthetic/analysis/pairwise.py",
        ROOT / "docs/policies/synthetic_analysis_10e_pairwise.json",
        ROOT / "docs/decisions/0018-pairwise-cardinality-equalization.md",
    ]
    write(
        OUTPUT / "generation_manifest.json",
        dict(
            phase="10E",
            revision="independent_pairwise_v2",
            status="COMPLETED",
            baseline_commit=BASE,
            initial_freeze_commit=subprocess.check_output(
                ["git", "rev-parse", "edd1a81"], cwd=ROOT, text=True
            ).strip(),
            reporting_commit="exact final head recorded in PR18; no circular self-SHA",
            protected_previous_files=verify(),
            optimization_executions=0,
            original_refits=0,
            previous_joint_analysis="preserved; superseded for current equalized conclusions",
            source_sha256={str(p.relative_to(ROOT)): digest(p) for p in sources},
            artifacts_sha256={str(p.relative_to(OUTPUT)): digest(p) for p in paths},
            artifact_bytes=sum(p.stat().st_size for p in paths),
            policy=read(ROOT / "docs/policies/synthetic_analysis_10e_pairwise.json"),
            python=sys.version,
            packages={
                p: importlib.metadata.version(p)
                for p in ("numpy", "scipy", "pandas", "matplotlib", "pytest", "pytest-cov")
            },
            original_data_and_excluded_license_scope_unchanged=True,
        ),
    )
    checked = sorted([*paths, OUTPUT / "generation_manifest.json"])
    (OUTPUT / "checksums.sha256").write_bytes(
        "".join(f"{digest(p)}  {p.relative_to(OUTPUT).as_posix()}\n" for p in checked).encode()
    )
    print(f"Hashed {len(checked)} pairwise artifacts; previous files unchanged", flush=True)


def verify_outputs():
    records = (OUTPUT / "checksums.sha256").read_text().splitlines()
    names = set()
    for line in records:
        expected, relative = line.split("  ", 1)
        if digest(OUTPUT / relative) != expected:
            raise ValueError("pairwise artifact changed: " + relative)
        names.add(relative)
    actual = {
        p.relative_to(OUTPUT).as_posix()
        for p in OUTPUT.rglob("*")
        if p.is_file() and p.name != "checksums.sha256"
    }
    if actual != names:
        raise ValueError("missing or unlisted pairwise artifacts")
    print(f"Verified {len(records)} artifacts and {verify()} protected files", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    if parser.parse_args().verify:
        verify_outputs()
    else:
        finalize()
