"""Prepare Phase10D provenance using committed v1 blobs, never its dirty checkout."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from cnbi_v2.synthetic.benchmark.archive import file_hash, write_json
from cnbi_v2.synthetic.benchmark.configuration import INTEGRATION_COMMIT, V1_COMMIT, ea_ceiling
from cnbi_v2.synthetic.benchmark.contracts import METHODS, PILOT_SCENARIOS, stream_seed
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/"results/phase_10_synthetic_benchmark/benchmark_20261029"
MUTABLE = {".gitignore", "AGENTS.md", "CHANGELOG.md", "README.md", "ROADMAP.md",
           "docs/methodology_status.md", "docs/reproducibility.md"}
V1_FILES = (
    "cnbi_experiments/comparators.py", "cnbi_experiments/solver.py",
    "cnbi_experiments/ea_calibration.json", "cnbi_experiments/calibrate_eas.py",
    "cnbi_experiments/BUDGET_POLICY.md", "VRF_ARTICLE_AUDIT.md",
    "cnbi_experiments/revise_vrf_faithful.py", "cnbi_experiments/revise_doe_vrf_faithful.py",
    "experimental_results/VRF_FAITHFUL_SUMMARY.json", "cnbi_experiments/tests/test_extension.py",
    "ORIGINAL_LICENSE.txt",
)


def git(*args: str, cwd: Path = ROOT) -> bytes:
    return subprocess.check_output(["git", *args], cwd=cwd)


def prepare(legacy: Path) -> None:
    if OUTPUT.exists():
        raise FileExistsError("preserve the prepared protocol; do not overwrite")
    remote = git("ls-remote", "https://github.com/LimaGV/C-NBI.git",
                 "refs/heads/cnbi-v1.0").decode().split()[0]
    if remote != V1_COMMIT or git("rev-parse", V1_COMMIT, cwd=legacy).decode().strip() != V1_COMMIT:
        raise ValueError("legacy commit does not match the explicitly pinned reference")
    OUTPUT.mkdir(parents=True)
    provenance = {}
    for name in V1_FILES:
        blob = git("show", f"{V1_COMMIT}:{name}", cwd=legacy)
        provenance[name] = hashlib.sha256(blob).hexdigest()
        if name.endswith("ea_calibration.json"):
            (OUTPUT/"v1_ea_calibration.json").write_bytes(blob)
    rows = json.loads((OUTPUT/"v1_ea_calibration.json").read_text(encoding="utf-8"))
    if len(rows) != 18 or any(v["status"] != "COMPLETED" for v in rows.values()):
        raise ValueError("exactly 18 completed calibration records required")
    frozen = {}
    for name in git("ls-tree", "-r", "--name-only", INTEGRATION_COMMIT).decode().splitlines():
        if name in MUTABLE:
            continue
        expected = hashlib.sha256(git("show", f"{INTEGRATION_COMMIT}:{name}")).hexdigest()
        if file_hash(ROOT/name) != expected:
            raise ValueError("previous scientific file changed: "+name)
        frozen[name] = expected
    write_json(OUTPUT/"frozen_inputs_manifest.json", dict(
        integration_commit=INTEGRATION_COMMIT, files=frozen, mutable_current_state=sorted(MUTABLE),
    ))
    write_json(OUTPUT/"algorithm_provenance.json", dict(
        v1_repository="https://github.com/LimaGV/C-NBI", v1_branch="cnbi-v1.0",
        v1_commit=V1_COMMIT, v1_blob_sha256=provenance, v1_checkout_modified=False,
        paper_doi="10.1016/j.engappai.2025.112510", zotero_key="SMMX47JT",
        paper_status="FULLTEXT_VERIFIED_RELEVANT_PAGES_6_7", attachment_in_zotero=False,
        article_variance="sum_i L_ij^2; radius rho is a separate domain definition",
        legacy_variance="rho * sum_i L_ij^2",
        variance_adaptation="constant correction cancels algebraically in Eq25; raw values differ",
        optimization_gauge="legacy constant translation retained internally; shift archived",
        license_notices=["references/software/phase10d_cnbi_v1_MIT.txt",
                         "references/software/phase10d_third_party.txt"],
    ))
    configurations = dict(
        C_NBI=dict(B=2000, MC="joint_matrix_normal_plugin", covariance="validated_PSD_no_jitter",
                   screening="all_local_components_strictly_above_q95_linear_quantile",
                   subsets="all_2_to_min_m_nxplus1", NBI="unchanged_v2_defaults"),
        VRF_NBI=dict(factor_rule="max(2,k90)", factor_admissibility="2<=k<=nx+1",
                     varimax=dict(normalize=True, iterations=500, tolerance=1e-5),
                     pinv_rcond=1e-15, variance="sum_squared_loadings",
                     extreme_ftol=1e-12, extreme_maxiter=100,
                     nbi_ftol=1e-10, nbi_maxiter=100, nbi_eq_inf_tolerance=1e-5,
                     nbi_sphere_norm_tolerance=1e-8, max_rescues=2),
        lattice_H={str(k): 5 if k <= 4 else 2 for k in range(2, 7)},
        evolutionary=rows, evolutionary_version="pymoo==0.6.2",
        initialization="uniform_ball; no_true_anchors", radial_repair="one_ulp_inward",
        evaluation="offline_Phase10C_unchanged_native_cardinality",
        cpu_threads=1, workers=1,
    )
    write_json(OUTPUT/"algorithm_configurations.json", configurations)
    write_json(OUTPUT/"budget_policy.json", dict(
        cnbi_vrf="finish_full_method_no_NFE_ceiling", ea_rule="max(50000,400*comb(m+3,4))",
        ceilings={str(m): ea_ceiling(m) for m in range(4, 12)},
        last_generation="floor(budget/population)_complete_generations_as_v1",
        unspent_remainder="reported; no_overshoot; no_silent_partial_population",
        costs="end_to_end_preparation_solver_postprocessing; external_evaluation_separate",
        nfe="original_full_vector_points; scalar_kernel_evaluations_and_gradients_separate",
    ))
    inputs = load_search_inputs(ROOT/"results/phase_10_synthetic_rsm/rsm_20261029")
    tasks = []
    for stage in ("pilot", "official"):
        for key, item in sorted(inputs.items()):
            if stage == "pilot" and (
                item.scenario_id not in PILOT_SCENARIOS or item.replica_id != 1
            ):
                continue
            for method in METHODS:
                tasks.append(dict(stage=stage, instance_id=key, scenario_id=item.scenario_id,
                                  replica_id=item.replica_id, method=method,
                                  seed=str(stream_seed(item.scenario_id, item.replica_id, method,
                                                       stage+"_search"))))
    write_json(OUTPUT/"seed_manifest.json", dict(
        rule="SHA256_first128bits_little_PCG64", tasks=tasks,
    ))
    source_files = list((ROOT/"src/cnbi_v2/synthetic/benchmark").glob("*.py"))
    source_files += list((ROOT/"scripts/validation").glob("*synthetic_benchmark*.py"))
    source_files += [ROOT/"docs/decisions/0016-synthetic-algorithm-benchmark.md",
                     ROOT/"docs/mathematics/synthetic_algorithm_benchmark.md"]
    source = {p.relative_to(ROOT).as_posix(): file_hash(p) for p in source_files}
    configuration = {p.name: file_hash(p) for p in OUTPUT.glob("*.json")}
    digest = hashlib.sha256(json.dumps(dict(source=source, configuration=configuration),
                                      sort_keys=True).encode()).hexdigest()
    write_json(OUTPUT/"generation_manifest.json", dict(
        scientific_source=source, configuration=configuration, protocol_hash=digest,
        code_commit=git("rev-parse", "HEAD").decode().strip(), campaign_status="INCOMPLETE",
        planned_pilot_runs=12, planned_official_runs=540,
    ))
    write_json(OUTPUT/"campaign_manifest.json", dict(
        status="INCOMPLETE", pilot_gate="PENDING", planned_runs=540, executed_runs=0,
        tasks=[dict(**task, state="PENDING") for task in tasks if task["stage"] == "official"],
    ))
    print(json.dumps(dict(protocol_hash=digest, frozen_files=len(frozen), tasks=len(tasks))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", type=Path, required=True)
    prepare(parser.parse_args().legacy)
