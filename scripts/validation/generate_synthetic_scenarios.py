"""Generate only Phase10A structural scenarios from the committed protocol.

uv run python -m scripts.validation.generate_synthetic_scenarios
"""

import argparse
import hashlib
import json
import os
import platform
import subprocess
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

from cnbi_v2.data import sha256_file
from cnbi_v2.synthetic import CalibrationConfig, calibrate, factorial_design
from cnbi_v2.synthetic.serialization import correlation_row, export_scenarios

from .synthetic_diagnostics import export_diagnostics

ROOT = Path(__file__).resolve().parents[2]
BASE = "4432e333b75fe9427c7e5340bf952a05858ad19e"
PROTOCOL = ROOT / "docs/policies/synthetic_generation_10a.json"
OUTPUT = ROOT / "results/phase_10_synthetic_generation/structural_20261029"


def write_json(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def frozen_scientific_inputs():
    names = subprocess.check_output(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            BASE,
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    # Only the current-state documentation and the exact new-result ignore
    # exception may change; every other preexisting tracked file is protected.
    mutable = {
        ".gitignore",
        "AGENTS.md",
        "README.md",
        "ROADMAP.md",
        "CHANGELOG.md",
        "docs/methodology_status.md",
        "docs/reproducibility.md",
    }
    names = [name for name in names if name not in mutable]
    result = {}
    with subprocess.Popen(
        ["git", "cat-file", "--batch"], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as process:
        for name in names:
            process.stdin.write((BASE + ":" + name + "\n").encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            assert header[1] == b"blob", name
            payload = process.stdout.read(int(header[2]))
            assert process.stdout.read(1) == b"\n"
            expected = hashlib.sha256(payload).hexdigest()
            if sha256_file(ROOT / name) != expected:
                raise ValueError("frozen input differs from consolidated main: " + name)
            result[name] = expected
        process.stdin.close()
        assert process.wait() == 0
    return result


def verify_unchanged(hashes):
    for name, digest in hashes.items():
        if sha256_file(ROOT / name) != digest:
            raise ValueError("scientific input changed during generation: " + name)


def source_files():
    return sorted((ROOT / "src/cnbi_v2/synthetic").glob("*.py")) + [
        Path(__file__),
        ROOT / "scripts/validation/synthetic_diagnostics.py",
        PROTOCOL,
    ]


def generate(output=OUTPUT, protocol_path=PROTOCOL):
    begin = perf_counter()
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(
            "output must be new and empty; completed/failed evidence is not overwritten"
        )
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    official = output.resolve() == OUTPUT.resolve()
    if official and dirty:
        raise ValueError("commit code/tests/protocol before official27-cell generation")
    if official and Path(protocol_path).resolve() != PROTOCOL.resolve():
        raise ValueError("official generation requires the committed protocol path")
    protocol = json.loads(Path(protocol_path).read_text(encoding="utf-8"))
    config = CalibrationConfig(**protocol["calibration_parameters"])
    if protocol["scientific_base_commit"] != BASE:
        raise ValueError("unexpected scientific baseline")
    inputs = frozen_scientific_inputs()
    code = {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in source_files()}
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "calibration_config.json", protocol)
    write_json(output / "frozen_inputs_manifest.json", inputs)
    results = []
    for number, cell in enumerate(factorial_design(), 1):
        result = calibrate(cell, config)
        results.append(result)
        row = correlation_row(result)
        print(
            f"{number}/27 {cell.scenario_id}: {row['status']}; cal={row['error_calibration']:.8g}; "
            f"val={row['error_validation']:.8g}; {result.elapsed_seconds:.2f}s",
            flush=True,
        )
    results = tuple(results)
    export_scenarios(results, output)
    export_diagnostics(results, output / "figures")
    verify_unchanged(inputs)
    if any(sha256_file(ROOT / name) != digest for name, digest in code.items()):
        raise ValueError("generation source changed during execution")
    rows = [correlation_row(r) for r in results]
    signed = [r["rho_signed"] for r in rows]
    manifest = dict(
        run_id=output.name,
        status="COMPLETE" if all(r.valid for r in results) else "NOT_FULLY_VALIDATED",
        generated_at_utc=datetime.now(UTC).isoformat(),
        scientific_base_commit=BASE,
        code_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        working_tree_dirty_at_start=dirty,
        official_run=official,
        scenarios=27,
        validated=sum(r.valid for r in results),
        configurations_per_cell=1,
        maximum_calibration_error=max(r["error_calibration"] for r in rows),
        maximum_validation_error=max(r["error_validation"] for r in rows),
        maximum_entry_error_calibration=max(r["maximum_entry_error_calibration"] for r in rows),
        maximum_entry_error_validation=max(r["maximum_entry_error_validation"] for r in rows),
        signed_correlation_min=min(signed),
        signed_correlation_max=max(signed),
        calibration_seconds=sum(r.elapsed_seconds for r in results),
        total_generation_seconds=perf_counter() - begin,
        starts_total=sum(len(r.trials) for r in results),
        solver_failures=sum(not t.solver_success for r in results for t in r.trials),
        failed_scenarios={r.scenario.scenario_id: list(r.failures) for r in results if not r.valid},
        frozen_inputs_verified=len(inputs),
        frozen_inputs_unchanged=True,
        lock_sha256=sha256_file(ROOT / "uv.lock"),
        source_sha256=code,
        python=platform.python_version(),
        platform=platform.system(),
        libraries={n: version(n) for n in ("numpy", "scipy", "matplotlib")},
        selected_seeds={
            r.scenario.scenario_id: dict(
                initialization=r.trials[r.selected_start].seed,
                calibration=r.calibration_seed,
                validation=r.validation_seed,
            )
            for r in results
        },
        figure_language="English",
        diagnostic_figure_types=4,
        png_dpi=600,
        pdf_vector=True,
        coordinate_gridlines=False,
        multiobjective_methods_executed=False,
        noise_CCD_RSM_generated=False,
        Pareto_reference_or_metrics_generated=False,
        data_publication=(
            "Explicitly requested generated structural results; no open data/figure license applied"
        ),
    )
    write_json(output / "calibration_manifest.json", manifest)
    text = (
        "# Phase10A structural scenarios\n\n"
        "One configuration per cell;f_j(x)=||x-a_j||²,all MIN.\n"
        "No multiobjective method,noise,CCD,RSM or Pareto benchmark was executed.\n"
        "rho_abs_realized/rho_signed in the tables refer to the independent holdout.\n"
        "CSV values preserve17 significant digits; NPZ stores full float64 arrays.\n"
        "All four diagnostics are English,PNG600dpi/PDF vector,without gridlines.\n"
        "Mean signed correlation is observed and never used for selection.\n\n"
        f"Validated:{manifest['validated']}/27. "
        "See calibration_manifest.json for failures/timing.\n\n"
        "| Scenario | nx | delta | m | Target | Realized abs | Signed | "
        "Validation error | Status |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|---|\n"
    )
    for r in rows:
        text += (
            f"| {r['scenario_id']} | {r['nx']} | {r['delta']} | {r['m']} | {r['rho_target']:.2f} "
            f"| {r['rho_abs_realized']:.8f} | {r['rho_signed']:.8f} "
            f"| {r['error_validation']:.8f} | {r['status']} |\n"
        )
    (output / "README.md").write_text(text, encoding="utf-8", newline="\n")
    payloads = sorted(p for p in output.rglob("*") if p.is_file() and p.name != "checksums.sha256")
    lines = [f"{sha256_file(p)}  {p.relative_to(output).as_posix()}\n" for p in payloads]
    lines += [
        f"{digest}  {Path(os.path.relpath(ROOT / name, output)).as_posix()}\n"
        for name, digest in code.items()
    ]
    (output / "checksums.sha256").write_text("".join(lines), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                k: manifest[k]
                for k in (
                    "status",
                    "validated",
                    "maximum_calibration_error",
                    "maximum_validation_error",
                    "solver_failures",
                    "total_generation_seconds",
                )
            }
        ),
        flush=True,
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--config", type=Path, default=PROTOCOL)
    args = parser.parse_args()
    manifest = generate(args.output, args.config)
    return 0 if manifest["validated"] == 27 else 1


if __name__ == "__main__":
    raise SystemExit(main())
