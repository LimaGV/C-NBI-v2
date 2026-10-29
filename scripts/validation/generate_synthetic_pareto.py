"""Frozen Phase10C generation: analytical reference only, no RSM fitting or search."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from synthetic_pareto_diagnostics import save_figures
from synthetic_pareto_hv_study import run_oracles

from cnbi_v2.synthetic.pareto.geometry import seed_for
from cnbi_v2.synthetic.pareto.hypervolume import FixedHypervolume
from cnbi_v2.synthetic.pareto.reference import generate_reference, sensitivity
from cnbi_v2.synthetic.pareto.serialization import (
    array_sha256,
    load_true_anchors,
    sha256_file,
    write_csv,
    write_json,
)

ROOT = Path(__file__).resolve().parents[2]
BASE = "47a0e4dc55a22a7d0ad436540c1a305e4078e2ad"
INPUT = ROOT / "results/phase_10_synthetic_generation/structural_20261029"
POLICY = ROOT / "docs/policies/synthetic_pareto_reference_10c.json"
OUTPUT = ROOT / "results/phase_10_synthetic_pareto/analytical_20261029"
MUTABLE = {
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "docs/methodology_status.md",
    "docs/reproducibility.md",
}


def freeze_inputs():
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASE], cwd=ROOT, text=True
    ).splitlines()
    result = {}
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
            content = process.stdout.read(int(header[2]))
            assert process.stdout.read(1) == b"\n"
            digest = hashlib.sha256(content).hexdigest()
            if sha256_file(ROOT / name) != digest:
                raise ValueError("frozen Phase0–10B file differs: " + name)
            result[name] = digest
        process.stdin.close()
        assert process.wait() == 0
    return result


def generate(output):
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("refusing to overwrite an existing reference campaign")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise ValueError("commit protocol/source/tests and start from a clean tree")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    frozen = freeze_inputs()
    cells = load_true_anchors(INPUT)
    master = policy["master_seed"]
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "reference_sampling_config.json", policy)
    write_json(output / "frozen_inputs_manifest.json", frozen)
    manifest = dict(
        status="RUNNING",
        run_id=output.name,
        code_commit=commit,
        scientific_base_commit=BASE,
        phase10a_commit=policy["phase10a_commit"],
        phase10b_commit=policy["phase10b_commit"],
        generated_at_utc=datetime.now(UTC).isoformat(),
        working_tree_dirty_at_start=False,
        official_run=True,
        failures={},
    )
    write_json(output / "generation_manifest.json", manifest)
    started = time.perf_counter()
    try:
        references = []
        diagnostics, coverage, certificates, ideal_nadir, extremes, index, sampling_rows = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
        decisions, objectives, normalized, nested, probes, candidate_arrays = {}, {}, {}, {}, {}, {}
        candidate_hashes = {}
        for cell, anchors in cells:
            before = time.perf_counter()
            reference = generate_reference(cell, anchors, master)
            references.append(reference)
            sid = cell.scenario_id
            decisions[sid] = reference.decisions[:5000]
            objectives[sid] = reference.responses[:5000]
            normalized[sid] = reference.normalized[:5000]
            for suffix, array in (
                ("decisions_extension", reference.decisions[5000:]),
                ("objectives_extension", reference.responses[5000:]),
                ("normalized_extension", reference.normalized[5000:]),
                ("weights", reference.weights),
                ("candidate_ids", reference.candidate_ids),
                ("origins", reference.origins),
            ):
                nested[sid + "__" + suffix] = array
            rows, samples = sensitivity(reference, master)
            diagnostics.extend(rows)
            for suffix, array in samples.items():
                probes[sid + "__" + suffix] = array
            main = rows[1]
            budget_passed = all(
                main[k] <= 0.05 for k in ("probe_rms_coordinate_max", "hausdorff_rms_coordinate")
            ) and (main["boundary_probe_max"] / np.sqrt(cell.m) <= 0.05)
            status = "FINITE_AUDIT_BUDGET_PASSED" if budget_passed else "REVIEW_REQUIRED"
            if reference.geometry.volume is None:
                status = "GEOMETRY_FALLBACK_REVIEW_REQUIRED"
            coverage.append(
                dict(
                    scenario_id=sid,
                    nx=cell.nx,
                    m=cell.m,
                    primary_n=5000,
                    coordinate_rms_budget=0.05,
                    volume_probe_rms_max=main["probe_rms_coordinate_max"],
                    boundary_probe_rms_max=main["boundary_probe_max"] / np.sqrt(cell.m),
                    dense_hausdorff_rms=main["hausdorff_rms_coordinate"],
                    status=status,
                )
            )
            certificates.append(
                dict(
                    scenario_id=sid,
                    nx=cell.nx,
                    m=cell.m,
                    affine_dimension=int(np.linalg.matrix_rank(anchors - anchors.mean(axis=0))),
                    geometry_condition=reference.geometry.condition,
                    hull_volume=reference.geometry.volume,
                    geometry_method=reference.geometry.method,
                    geometry_limitation=reference.geometry.limitation,
                    **reference.certificate,
                )
            )
            for j in range(cell.m):
                ideal_nadir.append(
                    dict(
                        scenario_id=sid,
                        response_id=f"y{j + 1}",
                        ideal=0.0,
                        nadir=float(reference.normalization.nadir[j]),
                        denominator=float(reference.normalization.nadir[j]),
                        sample_min=float(reference.responses[:5000, j].min()),
                        sample_max=float(reference.responses[:5000, j].max()),
                    )
                )
                for k in range(cell.m):
                    extremes.append(
                        dict(
                            scenario_id=sid,
                            anchor_id=k + 1,
                            response_id=f"y{j + 1}",
                            value=float(reference.responses[k, j]),
                        )
                    )
            candidate_hashes[sid] = dict(
                decisions=array_sha256(reference.pool.decisions),
                weights=array_sha256(reference.pool.weights),
                before_identity=reference.pool.before_identity_count,
                after_identity=len(reference.pool.decisions),
            )
            candidate_arrays[sid + "__weights"] = reference.pool.weights
            candidate_arrays[sid + "__origins"] = reference.pool.origins
            candidate_arrays[sid + "__original_ids"] = reference.pool.original_ids
            for origin, label, role in (
                (0, "individual_anchor", None),
                (1, "interior", "candidate_interior"),
                (2, "boundary_or_subsimplex", "candidate_boundary"),
                (3, "anchor_neighborhood", "candidate_anchor_neighborhood"),
                (4, "anchor_pair_segment", None),
            ):
                sampling_rows.append(
                    dict(
                        scenario_id=sid,
                        origin_id=origin,
                        origin=label,
                        seed=str(seed_for(master, sid, role)) if role else "not_random",
                        candidate_count=int(np.sum(reference.pool.origins == origin)),
                        selected_2500=int(np.sum(reference.origins[:2500] == origin)),
                        selected_5000=int(np.sum(reference.origins[:5000] == origin)),
                        selected_10000=int(np.sum(reference.origins == origin)),
                        geometry_method=reference.geometry.method,
                        geometry_condition=reference.geometry.condition,
                        selection_metric="normalized true-objective Euclidean",
                        tie_rule="smallest original candidate ID for exact numeric tie",
                    )
                )
            for n in (2500, 5000, 10000):
                index.append(
                    dict(
                        scenario_id=sid,
                        nx=cell.nx,
                        m=cell.m,
                        n_reference=n,
                        primary=n == 5000,
                        shared_replicas="1;2;3;4;5",
                        source="Phase10A frozen anchors only",
                        decision_array=sid,
                        extension_prefix=sid + "__decisions_extension" if n == 10000 else "",
                        selection="nested normalized-objective FPS",
                        candidate_count=len(reference.pool.decisions),
                        count_before_identity=reference.pool.before_identity_count,
                        candidate_decisions_sha256=candidate_hashes[sid]["decisions"],
                        reference_decisions_sha256=array_sha256(reference.decisions[:n]),
                        reference_objectives_sha256=array_sha256(reference.responses[:n]),
                        reference_normalized_sha256=array_sha256(reference.normalized[:n]),
                    )
                )
            print(
                f"REFERENCE {sid}:5000 primary /10000 dense; "
                f"candidates={len(reference.pool.decisions)}; "
                f"{status}; {time.perf_counter() - before:.3f}s",
                flush=True,
            )
        # Reverse processing uses the same frozen protocol; no reselection by quality.
        for reference in reversed(references):
            cell = reference.scenario
            replay = generate_reference(cell, reference.geometry.anchors, master)
            for original, again in (
                (reference.decisions, replay.decisions),
                (reference.responses, replay.responses),
                (reference.weights, replay.weights),
            ):
                if not np.array_equal(original, again):
                    raise ValueError("reverse-order reproducibility failed: " + cell.scenario_id)
            print("REPRODUCED " + cell.scenario_id, flush=True)
        hv_rows = []
        for final_power in policy["hypervolume_study"]["maximum_power_tiers"]:
            for reference in references:
                cell = reference.scenario
                for n in (2500, 5000, 10000):
                    for row in FixedHypervolume(cell.m, master, final_power).study(
                        reference.normalized[:n]
                    ):
                        hv_rows.append(
                            dict(
                                case_type="pareto_reference",
                                scenario_id=cell.scenario_id,
                                n_reference=n,
                                tier_max_power=final_power,
                                **row,
                                exact_oracle=None,
                                absolute_error=None,
                                relative_error=None,
                            )
                        )
                print(f"HV STUDIED {cell.scenario_id},tier={final_power}", flush=True)
            final_hv_rows = [
                r
                for r in hv_rows
                if r["case_type"] == "pareto_reference"
                and r["n_reference"] == 5000
                and r["power"] == final_power
                and r["tier_max_power"] == final_power
            ]
            hv_pass = all(r["qmc_status"] == "PRECISION_CRITERIA_PASSED" for r in final_hv_rows)
            if hv_pass:
                break
        oracle_rows, oracles = run_oracles(master, final_power)
        hv_rows = oracle_rows + hv_rows
        hv_config = dict(
            status="VALIDATED_REFERENCE_REGIME" if hv_pass else "HV_PRECISION_PENDING",
            master_seed=master,
            final_power=final_power,
            samples_per_scramble=2**final_power,
            scrambles=4,
            reference_point=1.1,
            lower_bound=0,
            small_set_exact_limit=8,
            small_set_method="inclusion-exclusion with explicit cancellation bound",
            large_set_method="common Sobol estimate; per-set precision status required",
            normalization="analytic ideal/nadir, never candidate-derived",
            reference_cases_passed=sum(
                r["qmc_status"] == "PRECISION_CRITERIA_PASSED" for r in final_hv_rows
            ),
            reference_cases_total=27,
            raw_qmc_tiny_oracle_failures_preserved=True,
            resolution_frozen_after_validation=True,
            algorithms_observed=False,
        )
        metric_protocol = dict(
            phase="10C",
            status="FROZEN",
            GD="mean Euclidean A to R,p1",
            IGD="mean Euclidean R to A,p1",
            Spacing="sample nearest-other SD,ddof1",
            Sparsity="mean Euclidean nearest-other distance",
            HV=hv_config,
            undefined="empty ND:all;singleton:Spacing/Sparsity;HV unresolved:precision flag",
            primary_reference_count=5000,
            normalization="fixed true ideal/nadir per scenario",
            primary_cardinality="native",
            secondary_equalization="plan only,not executed",
            oracle_feedback_to_search=False,
        )
        for name, arrays in (
            ("decisions", decisions),
            ("objectives", objectives),
            ("normalized", normalized),
        ):
            np.savez_compressed(
                output / f"pareto_reference_{name}.npz", allow_pickle=False, **arrays
            )
        np.savez_compressed(output / "pareto_reference_nested.npz", allow_pickle=False, **nested)
        np.savez_compressed(
            output / "reference_independent_probes.npz", allow_pickle=False, **probes
        )
        np.savez_compressed(
            output / "pareto_candidates.npz", allow_pickle=False, **candidate_arrays
        )
        for name, rows in (
            ("pareto_reference_index.csv", index),
            ("pareto_geometry_certificates.csv", certificates),
            ("pareto_extremes.csv", extremes),
            ("pareto_ideal_nadir.csv", ideal_nadir),
            ("pareto_sampling_diagnostics.csv", sampling_rows),
            ("reference_cardinality_sensitivity.csv", diagnostics),
            ("reference_coverage_diagnostics.csv", coverage),
            ("hypervolume_precision_diagnostics.csv", hv_rows),
        ):
            write_csv(output / name, rows)
        write_json(output / "benchmark_metrics_protocol.json", metric_protocol)
        write_json(output / "hypervolume_integration_config.json", hv_config)
        write_json(
            output / "metric_validation_oracles.json",
            dict(
                hypervolume=oracles,
                distance_oracles="tests/synthetic/pareto/test_metrics_evaluation.py",
                spacing="nearest distances[1,1,2],SD=sqrt(1/3),mean=4/3",
                all_analytic_HV_oracles_passed=True,
            ),
        )
        save_figures(
            output,
            references,
            diagnostics,
            [r for r in hv_rows if r["tier_max_power"] == final_power],
            ideal_nadir,
        )
        for name, digest in frozen.items():
            if sha256_file(ROOT / name) != digest:
                raise ValueError("frozen file changed during generation: " + name)
        source_names = sorted(
            [
                p.relative_to(ROOT).as_posix()
                for p in (ROOT / "src/cnbi_v2/synthetic/pareto").glob("*.py")
            ]
            + [
                "scripts/validation/generate_synthetic_pareto.py",
                "scripts/validation/verify_synthetic_pareto.py",
                "scripts/validation/synthetic_pareto_diagnostics.py",
                "scripts/validation/synthetic_pareto_hv_study.py",
                "docs/policies/synthetic_pareto_reference_10c.json",
                "docs/mathematics/synthetic_pareto_reference.md",
                "docs/mathematics/synthetic_benchmark_metrics.md",
                "docs/decisions/0015-synthetic-analytical-pareto-reference.md",
            ]
        )
        arrays = {}
        for path in sorted(output.glob("*.npz")):
            with np.load(path, allow_pickle=False) as values:
                arrays[path.name] = {
                    k: dict(
                        shape=list(values[k].shape),
                        dtype=str(values[k].dtype),
                        sha256=array_sha256(values[k]),
                    )
                    for k in values.files
                }
        integration = {}
        for m in range(4, 12):
            grid = FixedHypervolume(m, master, final_power).grid
            integration[str(m)] = dict(
                seeds=list(grid.seeds), samples_sha256=array_sha256(grid.samples())
            )
        manifest.update(
            status="COMPLETE",
            scenarios=27,
            primary_points_per_scenario=5000,
            primary_points_total=135000,
            sensitivity_counts=[2500, 5000, 10000],
            references_per_scenario=1,
            shared_by_all_five_replicas=True,
            reverse_order_reproduced=27,
            geometry_fallbacks=sum(r.geometry.volume is None for r in references),
            coverage_budget_passed=sum(
                r["status"] == "FINITE_AUDIT_BUDGET_PASSED" for r in coverage
            ),
            coverage_review_required=[
                r["scenario_id"] for r in coverage if r["status"] != "FINITE_AUDIT_BUDGET_PASSED"
            ],
            hypervolume_status=hv_config["status"],
            hypervolume_reference_cases_passed=hv_config["reference_cases_passed"],
            source_sha256={n: sha256_file(ROOT / n) for n in source_names},
            frozen_inputs_verified=len(frozen),
            frozen_inputs_unchanged=True,
            candidate_hashes=candidate_hashes,
            array_manifest=arrays,
            hypervolume_integration_samples=integration,
            lock_sha256=sha256_file(ROOT / "uv.lock"),
            python=platform.python_version(),
            platform=platform.platform(),
            libraries={p: importlib.metadata.version(p) for p in ("numpy", "scipy", "matplotlib")},
            computational_parameters=dict(workers=1, blas=str(np.show_config(mode="dicts"))),
            multiobjective_methods_executed=False,
            new_CCD_noise_RSM_generated=False,
            equalization_executed=False,
            total_generation_seconds=time.perf_counter() - started,
        )
        write_json(output / "generation_manifest.json", manifest)
        (output / "README.md").write_bytes(
            (
                "# Frozen Phase10C analytical reference\n\n"
                "27 scenarios,5000 primary points each,135000 total.\n"
                "Each reference is shared by five RSM replicas. This finite sample\n"
                "is not the continuous front.\n\n"
                "Primary NPZs have exactly27 scenario keys and5000 rows each.\n"
                "The nested NPZ stores5000-row extensions and10000-row witnesses.\n"
                "R2500 is the primary prefix;R10000 concatenates primary+extension.\n"
                "Coordinates/responses are float64;ID vectors are int64.\n"
                "Independent probes and every candidate's weights/source are archived.\n\n"
                "load_reference verifies hashes and loads without optimization,\n"
                "recalibration or RSM fitting. load_evaluation_context is offline only.\n"
                "No oracle is returned to search. Precision limitations are explicit.\n\n"
                "Source commit:" + commit + ". Main integration:" + BASE + ".\n\n"
                "No algorithm results or noisy RSMs are reference inputs.\n"
                "No search or equalization occurred. Existing data/science/licenses\n"
                "are unchanged. See LICENSE_SCOPE.md;original-code MIT does not\n"
                "automatically license scientific artifacts.\n"
            ).encode("utf-8")
        )
        paths = sorted(p for p in output.rglob("*") if p.is_file()) + [
            ROOT / n for n in source_names
        ]
        (output / "checksums.sha256").write_bytes(
            "".join(
                sha256_file(p) + "  " + Path(os.path.relpath(p, output)).as_posix() + "\n"
                for p in paths
            ).encode("utf-8")
        )
        print(
            json.dumps(
                {
                    k: v
                    for k, v in manifest.items()
                    if k
                    not in (
                        "source_sha256",
                        "candidate_hashes",
                        "array_manifest",
                        "hypervolume_integration_samples",
                        "computational_parameters",
                    )
                },
                indent=2,
            ),
            flush=True,
        )
    except Exception as exc:
        manifest.update(status="FAILED", failures={"campaign": repr(exc)})
        write_json(output / "generation_manifest.json", manifest)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    generate(parser.parse_args().output)
