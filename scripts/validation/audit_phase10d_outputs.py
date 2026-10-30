"""Read-only scientific artifact audit; no optimization or reference modification.

This helper is deliberately outside the frozen search package. Its own digest
and the exact numerical-source protocol are recorded in the audit report.
"""

import argparse
import json
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
from time import perf_counter

import numpy as np
from execute_synthetic_benchmark import OUTPUT, ROOT, RSM, run_id, verify_protocol

from cnbi_v2.benchmark.metrics import gd_igd, spacing_sparsity
from cnbi_v2.model.quadratic_design import quadratic_design
from cnbi_v2.nbi import nondominated_mask
from cnbi_v2.synthetic.benchmark.archive import (
    file_hash,
    read_json,
    verify_payload,
    write_json,
)
from cnbi_v2.synthetic.benchmark.configuration import ea_ceiling, load_ea_configuration
from cnbi_v2.synthetic.benchmark.contracts import METHODS, array_hash
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.pareto.selection import unique_indices
from cnbi_v2.synthetic.pareto.serialization import load_evaluation_context


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_float(actual, expected, message):
    """Same-environment replay: only a small float64 arithmetic allowance."""
    a, e = np.asarray(actual), np.asarray(expected)
    require(a.shape == e.shape and np.isfinite(a).all() and np.isfinite(e).all(), message)
    require(np.all(abs(a-e) <= 32*np.finfo(float).eps*np.maximum(1., abs(e))), message)


def check_recomposition(x, y, data):
    require(x.dtype == y.dtype == np.float64, "raw arrays must preserve float64")
    require(x.shape == (len(y), data.nx) and y.shape == (len(x), data.m), "raw shapes")
    require(np.isfinite(x).all() and np.isfinite(y).all(), "nonfinite raw output")
    expected = data.model.predict(x)
    bound = 8*len(data.model.coefficients)*np.finfo(float).eps*(
        abs(quadratic_design(x))@abs(data.model.coefficients))
    require(np.all(abs(y-expected) <= bound), "original frozen RSM recomposition mismatch")


def check_cnbi(data, diagnostic, arrays, count):
    require(diagnostic["B"] == 2000, "C-NBI Monte Carlo count changed")
    shapes = dict(coefficient_samples=(2000, len(data.model.coefficients), data.m),
                  mc_anchors=(2000, data.m, data.nx), mc_payoffs=(2000, data.m, data.m))
    for key, shape in shapes.items():
        value = arrays[key]
        require(value.shape == shape and value.dtype == np.float64
                and np.isfinite(value).all(), "C-NBI ensemble shape/type: "+key)
    require(array_hash(arrays["coefficient_samples"])
            == diagnostic["coefficient_samples_sha256"], "MC coefficient digest")
    require(array_hash(arrays["mc_payoffs"])
            == diagnostic["mc_payoffs_sha256"], "MC payoff digest")
    expected = {ids for k in range(2, data.nx+2) for ids in combinations(range(data.m), k)}
    local = [row for row in diagnostic["subsets"] if row["scope"] == "LOCAL"]
    require({tuple(row["indices"]) for row in local} == expected
            and len(local) == len(expected) == diagnostic["candidate_subsets"],
            "C-NBI missing or duplicated eligible subsets")
    for row in local:
        passes = np.asarray(row["observed"]) > row["q95"]
        require(np.array_equal(passes, row["component_passes"])
                and row["selected"] == bool(passes.all()), "strict local PA criterion")
    selected = [row for row in local if row["selected"]]
    require(len(selected) == diagnostic["selected_subsets"], "selected subset count")
    subproblems = diagnostic["subproblems"]
    for row in selected:
        k = len(row["indices"])
        weights = [r for r in subproblems if r["subset_id"] == row["subset_id"]]
        require(len(weights) == comb((5 if k <= 4 else 2)+k-1, k-1), "NBI lattice size")
    accepted = [r["raw_index"] for r in subproblems if r["accepted"]]
    require(accepted == list(range(count)) and len(diagnostic["raw_origins"]) == count,
            "accepted NBI solutions were lost or duplicated")
    require(diagnostic["all_mc_payoffs_valid"], "invalid MC ensemble silently reduced")


def check_vrf(data, diagnostic, arrays, status):
    cumulative = np.asarray(diagnostic["cumulative"])
    k = max(2, int(np.searchsorted(cumulative, .9)+1))
    require(diagnostic["n_factors"] == k, "VRF factor retention changed")
    if k > data.nx+1:
        require(status == "VRF_STRUCTURALLY_INVALID", "inadmissible VRF factor count hidden")
        return
    require(status == "COMPLETED", "unexpected admissible VRF status")
    loadings = np.asarray(diagnostic["loadings"])
    same_float(diagnostic["variance"], np.sum(loadings**2, axis=0), "published full VRF variance")
    same_float(diagnostic["optimization_gauge_shift"],
               np.asarray(diagnostic["variance"])*(data.alpha-1), "disclosed VRF gauge")
    weights = loadings@np.linalg.pinv(loadings.T@loadings, rcond=1e-15)
    same_float(diagnostic["weights"], weights, "VRF score weights")
    z = (data.observed-data.observed.mean(0))/data.observed.std(0, ddof=0)
    same_float(diagnostic["scores"], z@weights, "VRF observed-data scores")
    require(arrays["factor_coefficients"].shape == (len(data.model.coefficients), k)
            and arrays["factor_residuals"].shape == (len(data.ccd), k), "auxiliary factor shapes")
    if not diagnostic["varimax_converged"]:
        require(diagnostic["varimax_iterations"] == 500, "Varimax cap not disclosed")


def check_ea(directory, data, method, diagnostic, arrays, counters, x, y):
    config = load_ea_configuration(directory/"v1_ea_calibration.json", method, data.nx, data.m)
    require(diagnostic["transferred_parameters"] == config, "EA calibration record changed")
    population = comb(data.m+int(config["n_partitions"])-1, int(config["n_partitions"]))
    budget, nfe = ea_ceiling(data.m), counters["original_rsm_point_evaluations"]
    require(diagnostic["population"] == population == len(x), "full final EA population lost")
    require(diagnostic["nfe_ceiling"] == budget and nfe == (budget//population)*population
            and diagnostic["unspent_budget"] == budget-nfe, "EA floor/budget changed")
    require(diagnostic["generations"] == budget//population, "EA generations changed")
    require(diagnostic["final_population_ids"] == list(range(population)), "EA raw IDs lost")
    check_recomposition(x, arrays["optimizer_objectives"], data)
    require(diagnostic["pymoo_version"] == "0.6.2", "EA version changed")
    require(np.all(np.linalg.norm(x, axis=1) <= data.alpha), "EA ball repair failed")


def check_external(directory, name, data, x, context):
    record = read_json(directory/f"external_evaluation/{name}.json")
    metrics, diagnostics = record["metrics"], record["diagnostics"]
    with np.load(directory/f"external_evaluation/{name}.npz", allow_pickle=False) as arrays:
        truth = evaluate(x, context.anchors) if len(x) else np.empty((0, data.m))
        same_float(arrays["true_responses"], truth, "true objective replay")
        normalized = context.normalization.transform(truth)
        same_float(arrays["normalized_responses"], normalized, "fixed analytical normalization")
        feasible = np.linalg.norm(x, axis=1) <= data.alpha
        valid = np.flatnonzero(feasible)
        unique = valid[unique_indices(x[valid], 1e-12*data.alpha)] if len(valid) else valid
        nd = (unique[nondominated_mask(
            normalized[unique], equality_tolerance=np.full(data.m, 1e-12))]
              if len(unique) else unique)
        require(np.array_equal(arrays["feasible_mask"], feasible)
                and np.array_equal(arrays["unique_indices"], unique)
                and np.array_equal(arrays["nondominated_indices"], nd),
                "external raw/feasible/unique/ND")
    counts = [diagnostics[k] for k in ("raw_count", "feasible_count", "unique_count",
                                      "nondominated_count")]
    require(counts == [len(x), len(valid), len(unique), len(nd)],
            "native cardinality mismatch")
    require(record["reference_count"] == 5000 and not record["oracle_feedback_to_search"]
            and not diagnostics["raw_decisions_modified"], "oracle isolation or raw preservation")
    if len(nd):
        z = np.unique(normalized[nd], axis=0)
        gd, igd = gd_igd(z, context.reference_normalized)
        same_float([metrics["GD"], metrics["IGD"]], [gd, igd], "GD/IGD replay")
        if len(z) >= 2:
            same_float([metrics["Spacing"], metrics["Sparsity"]], spacing_sparsity(z),
                       "Spacing/Sparsity replay")
        else:
            require(metrics["Spacing"] is metrics["Sparsity"] is None, "singleton metrics hidden")
        exact = metrics["HV_method"] == "exact small-set inclusion-exclusion"
        require((metrics["HV_SE"] is None if exact else metrics["HV_SE"] >= 0)
                and metrics["HV_status"] and metrics["HV_method"], "HV precision not preserved")
        if exact:
            require(metrics["HV_roundoff_bound"] >= 0, "exact HV roundoff not preserved")
    else:
        require(all(metrics[k] is None for k in ("GD", "IGD", "HV", "Spacing", "Sparsity")),
                "empty feasible ND set has fabricated metric")
    return dict(raw=len(x), feasible=len(valid), unique=len(unique), nd=len(nd),
                hv_status=metrics.get("HV_status", metrics.get("status")),
                above_one=diagnostics["above_normalized_one"])


def audit(directory, stage="official", *, external=True):
    started = perf_counter()
    require(not (directory/"scheduler.lock").exists(), "audit must wait for search workers")
    manifest = verify_protocol(directory)
    frozen = read_json(directory/"frozen_inputs_manifest.json")
    tasks = [task for task in read_json(directory/"seed_manifest.json")["tasks"]
             if task["stage"] == stage]
    require(len(tasks) == (540 if stage == "official" else 12), "planned task count")
    require(len({run_id(task) for task in tasks}) == len(tasks), "duplicate task identity")
    inputs, contexts, pairing = load_search_inputs(RSM), {}, {}
    rows = []
    for task in tasks:
        name = run_id(task)
        cp = read_json(directory/f"campaign_checkpoints/{name}.json")
        require(cp["identity"] == task and cp["protocol_hash"] == manifest["protocol_hash"],
                "run identity or protocol changed: "+name)
        require(cp["state"] in {"COMPLETED", "FAILED", "INCOMPLETE"}, "unfinished task: "+name)
        base = dict(run_id=name, method=task["method"], state=cp["state"],
                    instance_id=task["instance_id"])
        if "payload_checksums" not in cp:
            require(cp["state"] != "COMPLETED" and cp.get("error"), "unrecorded run failure")
            rows.append(dict(**base, error=cp["error"]))
            continue
        verify_payload(directory, cp["payload_checksums"])
        payload = cp.get("payload_run_id", name)
        metadata = read_json(directory/f"algorithm_diagnostics/{payload}.json")
        data = inputs[task["instance_id"]]
        require(metadata["task"] == task and metadata["code_commit"] == manifest["code_commit"],
                "scientific source/identity mismatch")
        digest = array_hash(data.model.coefficients)
        require(metadata["coefficients_sha256"] == digest
                == metadata["diagnostics"]["frozen_coefficients_sha256"], "frozen model mismatch")
        pairing.setdefault(task["instance_id"], {})[task["method"]] = digest
        with np.load(directory/f"raw_decisions/{payload}.npz", allow_pickle=False) as raw:
            x = raw["decisions"]
        with np.load(directory/f"raw_rsm_responses/{payload}.npz", allow_pickle=False) as raw:
            y = raw["rsm_responses"]
        check_recomposition(x, y, data)
        diagnostic, counters = metadata["diagnostics"], metadata["counters"]
        require(diagnostic["raw_decisions_preserved"] and diagnostic["counter_schema"] == 2,
                "raw/counter policy missing")
        with np.load(directory/f"algorithm_diagnostics/{payload}.npz", allow_pickle=False) as raw:
            if task["method"] == "C-NBI":
                check_cnbi(data, diagnostic, raw, len(x))
            elif task["method"] == "VRF-NBI":
                check_vrf(data, diagnostic, raw, metadata["algorithm_status"])
            else:
                check_ea(directory, data, task["method"], diagnostic, raw, counters, x, y)
        events = (counters["original_full_vector_points_computed"]
                  + counters.get("quadratic_response_vector_calls", 0)
                  + counters.get("factor_model_vector_evaluations", 0))
        require(counters["model_vector_point_events"] == events, "counter accounting mismatch")
        require(all(metadata["environment"]["thread_environment"][k] == "1" for k in
                    ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")),
                "unexpected numeric threading")
        if external:
            sid = task["scenario_id"]
            if sid not in contexts:
                contexts[sid] = load_evaluation_context(
                    ROOT/"results/phase_10_synthetic_pareto/analytical_20261029", sid,
                    ROOT/"results/phase_10_synthetic_generation/structural_20261029")
            base.update(check_external(directory, name, data, x, contexts[sid]))
        base.update(varimax_nonconverged=diagnostic.get("varimax_converged") is False,
                    candidate_subsets=diagnostic.get("candidate_subsets"),
                    selected_subsets=diagnostic.get("selected_subsets"))
        rows.append(base)
    for methods in pairing.values():
        require(len(set(methods.values())) == 1, "paired methods saw different coefficients")
    barriers = read_json(directory/"method_execution_barriers.json")
    require(barriers["order"] == list(METHODS), "execution order changed")
    if stage == "official":
        require([r["method"] for r in barriers["barriers"]] == list(METHODS)
                and all(r["planned"] == r["processed"] == 135 and r["all_tasks_finished"]
                        for r in barriers["barriers"]), "method barriers not completed")
    result = dict(
        status="PASS", stage=stage, planned_runs=len(tasks), audited_runs=len(rows),
        states={m: dict(Counter(r["state"] for r in rows if r["method"] == m)) for m in METHODS},
        model_pairing_blocks=len(pairing), frozen_previous_files=len(frozen["files"]),
        preserved_previous_file_hashes=True, frozen_scientific_source=manifest["code_commit"],
        protocol_hash=manifest["protocol_hash"], auditor_sha256=file_hash(Path(__file__)),
        external_metrics_replayed=external,
        hv_estimator_rerun=False, hv_policy="frozen estimates and precision flags preserved",
        wall_seconds=perf_counter()-started, runs=rows,
    )
    write_json(directory/f"artifact_audit_{stage}.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    parser.add_argument("--stage", choices=("pilot", "official"), default="official")
    parser.add_argument("--search-only", action="store_true")
    args = parser.parse_args()
    result = audit(args.directory, args.stage, external=not args.search_only)
    print(json.dumps({k: v for k, v in result.items() if k != "runs"}))
