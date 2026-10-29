"""Phase10B official immutable campaign; requires committed code and a clean tree."""

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from synthetic_rsm_diagnostics import save_figures

from cnbi_v2.synthetic.rsm.noise import experimental_noise
from cnbi_v2.synthetic.rsm.rsm_generation import (
    certify_noiseless,
    generate_instance,
    validate_instances,
)
from cnbi_v2.synthetic.rsm.rsm_inputs import array_sha256, load_structural_cases, sha256_file
from cnbi_v2.synthetic.rsm.rsm_serialization import (
    export_tables,
    load_models,
    write_csv,
    write_json,
)
from cnbi_v2.synthetic.rsm.rsm_validation import external_sample, replica_prediction_spread

ROOT = Path(__file__).resolve().parents[2]
BASE = "d68aef72532ed0e39bd256b3e9dcb75f30c6a76b"
PHASE10A = "489aa0e2b4703c0e39b0bff2623209e5a177a94b"
INPUT = ROOT / "results/phase_10_synthetic_generation/structural_20261029"
POLICY = ROOT / "docs/policies/synthetic_generation_10b.json"
OUTPUT = ROOT / "results/phase_10_synthetic_rsm/rsm_20261029"
MUTABLE = {
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "docs/methodology_status.md",
    "docs/reproducibility.md",
}


def frozen_inputs():
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASE], cwd=ROOT, text=True
    ).splitlines()
    hashes = {}
    with subprocess.Popen(
        ["git", "cat-file", "--batch"], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as process:
        for name in names:
            if name in MUTABLE:
                continue
            process.stdin.write((BASE + ":" + name + "\n").encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            assert header[1] == b"blob", name
            import hashlib

            payload = process.stdout.read(int(header[2]))
            assert process.stdout.read(1) == b"\n"
            digest = hashlib.sha256(payload).hexdigest()
            if sha256_file(ROOT / name) != digest:
                raise ValueError("frozen Phase0–10A input changed: " + name)
            hashes[name] = digest
        process.stdin.close()
        assert process.wait() == 0
    return hashes


def aggregate(diagnostics, external):
    merged = [
        dict(d, **{k: e[k] for k in ("rmse", "mae", "r_squared_external", "max_absolute_error")})
        for d, e in zip(diagnostics, external, strict=True)
    ]
    groups = [("all", "all", merged)]
    for field in ("nx", "delta", "rho_target", "scenario_id"):
        for level in sorted({row[field] for row in merged}):
            groups.append((field, str(level), [r for r in merged if r[field] == level]))
    rows = []
    for field, level, group in groups:
        row = dict(
            group_by=field,
            level=level,
            n_response_models=len(group),
            lof_rejections_p05=sum(
                r["lack_of_fit_p_value"] is not None and r["lack_of_fit_p_value"] < 0.05
                for r in group
            ),
            not_strictly_convex=sum(
                r["hessian_classification"] != "STRICTLY_CONVEX" for r in group
            ),
        )
        for metric in (
            "r_squared",
            "adjusted_r_squared",
            "predicted_r_squared",
            "press",
            "coefficient_error_l2",
            "coefficient_error_relative_l2",
            "rmse",
            "mae",
            "r_squared_external",
            "max_absolute_error",
        ):
            values = np.array([r[metric] for r in group if r[metric] is not None], dtype=float)
            for label, value in zip(
                ("min", "q1", "median", "q3", "max"),
                np.quantile(values, [0, 0.25, 0.5, 0.75, 1]),
                strict=True,
            ):
                row[metric + "_" + label] = float(value)
            row[metric + "_mean"] = float(values.mean())
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("refusing to overwrite an existing campaign")
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    if dirty.strip():
        raise ValueError("commit implementation, tests and protocol before official generation")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    protocol = json.loads(POLICY.read_text(encoding="utf-8"))
    cases = load_structural_cases(INPUT)
    frozen = frozen_inputs()
    master = protocol["master_seed"]
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "generation_config.json", protocol)
    write_json(output / "frozen_inputs_manifest.json", frozen)
    started = time.perf_counter()
    manifest = dict(
        status="RUNNING",
        run_id=output.name,
        code_commit=commit,
        scientific_base_commit=BASE,
        phase10a_commit=PHASE10A,
        working_tree_dirty_at_start=False,
        official_run=True,
        generated_at_utc=datetime.now(UTC).isoformat(),
        failures={},
    )
    write_json(output / "generation_manifest.json", manifest)
    try:
        certificates = [certify_noiseless(c, a) for c, a in cases]
        write_csv(output / "noiseless_certification.csv", certificates)
        instances = tuple(generate_instance(c, a, r, master) for c, a in cases for r in range(1, 6))
        validate_instances(instances)
        if (
            len(instances),
            sum(i.fit.n_observations for i in instances),
            sum(i.fit.n_responses for i in instances),
        ) != (135, 3555, 990):
            raise ValueError("incomplete experimental campaign")
        # Holdout is generated after every noisy RSM has been frozen in memory.
        samples = {c.scenario_id: external_sample(c, a, master) for c, a in cases}
        anchors = {c.scenario_id: a for c, a in cases}
        diagnostics, external = export_tables(output, instances, anchors, samples)
        summary = aggregate(diagnostics, external)
        write_csv(output / "synthetic_rsm_summary.csv", summary)
        spreads = []
        for cell, _ in cases:
            group = [i for i in instances if i.scenario == cell]
            prediction = np.stack([i.fit.predict(samples[cell.scenario_id].points) for i in group])
            spreads.append(
                dict(scenario_id=cell.scenario_id, **replica_prediction_spread(prediction))
            )
        write_csv(output / "synthetic_replica_variation.csv", spreads)
        reverse_verified = 0
        for item in reversed(instances):
            noise = experimental_noise(item.truth, item.seed)
            if not np.array_equal(noise, item.noise) or not np.array_equal(
                item.truth + noise, item.observed
            ):
                raise ValueError("reverse-order reproducibility failure")
            reverse_verified += 1
        loaded = load_models(output)
        for item in instances:
            if not np.array_equal(
                loaded[item.instance_id].predict(item.ccd.points), item.fit.fitted_values
            ):
                raise ValueError("lossless reload failed")
        save_figures(output, instances, anchors, samples, diagnostics, external)
        for name, digest in frozen.items():
            if sha256_file(ROOT / name) != digest:
                raise ValueError("frozen input changed during generation: " + name)
        source_names = sorted(
            [
                str(p.relative_to(ROOT)).replace("\\", "/")
                for p in (ROOT / "src/cnbi_v2/synthetic/rsm").glob("*.py")
            ]
            + [
                "scripts/validation/generate_synthetic_rsm.py",
                "scripts/validation/verify_synthetic_rsm.py",
                "scripts/validation/synthetic_rsm_diagnostics.py",
                "docs/policies/synthetic_generation_10b.json",
            ]
        )
        arrays = {}
        for path in sorted(output.glob("*.npz")):
            with np.load(path, allow_pickle=False) as data:
                arrays[path.name] = {
                    k: dict(
                        shape=list(data[k].shape),
                        dtype=str(data[k].dtype),
                        sha256=array_sha256(data[k]),
                    )
                    for k in data.files
                }
        manifest.update(
            status="COMPLETE",
            scenarios=27,
            replicas_per_scenario=5,
            instances=135,
            experimental_rows=3555,
            scalar_response_observations=28530,
            response_models=990,
            coefficient_values=13275,
            noise_free_certifications=27,
            maximum_noise_free_coefficient_error=max(
                c["max_coefficient_error"] for c in certificates
            ),
            reverse_order_reproduced=reverse_verified,
            models_reloaded_without_refit=len(loaded),
            failed_models=0,
            all_replicas_retained=True,
            raw_residual_covariance=True,
            holdout_points_per_scenario=4096,
            external_validation_used_for_selection=False,
            multiobjective_methods_executed=False,
            Pareto_reference_or_metrics_generated=False,
            master_seed=master,
            bit_generator="PCG64",
            seed_protocol=protocol["seed_protocol"],
            frozen_inputs_verified=len(frozen),
            frozen_inputs_unchanged=True,
            source_sha256={n: sha256_file(ROOT / n) for n in source_names},
            phase10a_checksums_sha256=sha256_file(INPUT / "checksums.sha256"),
            lock_sha256=sha256_file(ROOT / "uv.lock"),
            array_manifest=arrays,
            python=platform.python_version(),
            platform=platform.platform(),
            libraries={p: importlib.metadata.version(p) for p in ("numpy", "scipy", "matplotlib")},
            computational_parameters=dict(
                workers=1,
                float_dtype="float64",
                numpy_blas=str(np.show_config(mode="dicts")),
                cpu=platform.processor(),
            ),
            total_generation_seconds=time.perf_counter() - started,
        )
        write_json(output / "generation_manifest.json", manifest)
        (output / "README.md").write_text(
            "# Frozen Phase10B synthetic experiments\n\n"
            "27 structural cases × 5 replicas = 135 joint RSMs; 3555 experiment rows; "
            "990 response models. All retained. No multiobjective run.\n\n"
            "Observations CSV is long-form: 28530 scalar response values; unique "
            "(instance_id,design_point_id) count is 3555. CCD x columns beyond nx "
            "are structurally inapplicable, not missing observations.\n\n"
            "models_index.json + synthetic_rsm_models.npz expose noisy polynomial "
            "predictions without OLS or oracle. Separate experimental/external NPZs "
            "preserve truth/noise, points, residuals and raw covariance. Term IDs are "
            "zero-based; response/design/replica IDs start at 1.\n\n"
            "CSV floats round-trip float64 (.17g); NPZ float64. Empty relative errors "
            "mean zero/near-zero true denominator; singular covariance condition is "
            "explicitly undefined. See mathematical definition and verification report.\n\n"
            "Source commit: " + commit + ". Input Phase10A: " + PHASE10A + ".\n\n"
            "Code-only MIT scope does not grant a license to these scientific artifacts; "
            "see LICENSE_SCOPE.md. No excluded material license changed.\n",
            encoding="utf-8",
        )
        paths = sorted(p for p in output.rglob("*") if p.is_file())
        paths += [ROOT / n for n in source_names]
        (output / "checksums.sha256").write_text(
            "".join(
                sha256_file(p) + "  " + Path(os.path.relpath(p, output)).as_posix() + "\n"
                for p in paths
            ),
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    k: v
                    for k, v in manifest.items()
                    if k not in ("array_manifest", "source_sha256", "computational_parameters")
                },
                indent=2,
            )
        )
        print(json.dumps(summary[:10], indent=2))
    except Exception as exc:
        manifest.update(status="FAILED", failures={"campaign": repr(exc)})
        write_json(output / "generation_manifest.json", manifest)
        raise


if __name__ == "__main__":
    main()
