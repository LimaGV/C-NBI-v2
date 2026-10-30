"""Record source/environment provenance and hash the separate analysis archive."""

import argparse
import importlib.metadata
import platform
import subprocess
import sys

from phase10e_inputs import BASE, OUTPUT, ROOT, digest, read, verify, write


def finalize():
    files = [
        p
        for p in sorted(OUTPUT.rglob("*"))
        if p.is_file() and p.name not in {"checksums.sha256", "generation_manifest.json"}
    ]
    sources = sorted((ROOT / "src/cnbi_v2/synthetic/analysis").glob("*.py")) + sorted(
        (ROOT / "scripts/validation").glob("phase10e_*.py")
    )
    sources += [
        ROOT / "docs/policies/synthetic_analysis_10e.json",
        ROOT / "docs/decisions/0017-synthetic-statistical-analysis.md",
        ROOT / "docs/mathematics/synthetic_statistical_analysis.md",
    ]
    manifest = dict(
        phase="10E",
        status="COMPLETED",
        input_commit=BASE,
        stacked_base_branch="feature/10d-synthetic-algorithm-benchmark",
        initial_protocol_commit=subprocess.check_output(
            ["git", "rev-parse", "d520e43"], cwd=ROOT, text=True
        ).strip(),
        derivation_code_commit=subprocess.check_output(
            ["git", "rev-parse", "3d7f5bd"], cwd=ROOT, text=True
        ).strip(),
        inference_code_commit=subprocess.check_output(
            ["git", "rev-parse", "f2d9e77"], cwd=ROOT, text=True
        ).strip(),
        reporting_commit="exact final head recorded in Phase10E PR; no circular self-SHA",
        optimizer_execution_count=0,
        optimization_executions=0,
        original_rsm_refits=0,
        protected_original_files=verify(),
        source_sha256={str(p.relative_to(ROOT)): digest(p) for p in sources},
        artifacts_sha256={str(p.relative_to(OUTPUT)): digest(p) for p in files},
        artifact_bytes=sum(p.stat().st_size for p in files),
        python=sys.version,
        platform=platform.platform(),
        packages={
            k: importlib.metadata.version(k)
            for k in ("numpy", "scipy", "pandas", "matplotlib", "pytest", "pytest-cov")
        },
        policy=read(ROOT / "docs/policies/synthetic_analysis_10e.json"),
        official_HV_pending_statuses_preserved=True,
        publication_scope=(
            "requested synthetic derived analyses; original data and excluded licenses unchanged"
        ),
        numerical_status_does_not_imply_MDR_acceptance=True,
    )
    write(OUTPUT / "generation_manifest.json", manifest)
    checked = sorted([*files, OUTPUT / "generation_manifest.json"])
    (OUTPUT / "checksums.sha256").write_bytes(
        "".join(f"{digest(p)}  {p.relative_to(OUTPUT).as_posix()}\n" for p in checked).encode()
    )
    print(f"Hashed {len(checked)} analysis files; protected originals unchanged", flush=True)


def verify_outputs():
    count = 0
    for line in (OUTPUT / "checksums.sha256").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        if digest(OUTPUT / relative) != expected:
            raise ValueError("analysis artifact changed: " + relative)
        count += 1
    print(f"Verified {count} analysis artifacts and {verify()} protected input files", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        verify_outputs()
    else:
        finalize()
