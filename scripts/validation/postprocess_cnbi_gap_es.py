"""Minimal offline paired evaluation; frozen10C API, no optimizer or inference."""

import csv
import hashlib
import json
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from evaluate_phase10d import load_evaluation_context

from cnbi_v2.synthetic.benchmark.archive import read_json, verify_payload

ROOT = Path(__file__).resolve().parents[2]
ES = ROOT / "results/phase_10_synthetic_early_stop/gaps_adr0009_20261031_090729"
OLD = ROOT / "results/phase_10_synthetic_benchmark/benchmark_20261029/campaign_v2"
OUT = ES / "postprocess_20261031"
BRANCH = "feature/10f-adr0009-gap-results"
METRICS = ("GD", "IGD", "HV", "Spacing", "Sparsity", "ND")
HV_VALID = {"PRECISION_CRITERIA_PASSED", "EXACT_UP_TO_FLOAT64", "ZERO_CONTRIBUTION_CERTIFIED"}
GIT_BLOBS = {}


def checked(path):
    data = path.read_bytes()
    name = path.relative_to(ROOT).as_posix()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if GIT_BLOBS.get(name) != blob:
        raise ValueError("input differs from published branch: " + name)
    return data, hashlib.sha256(data).hexdigest()


def setup():
    global GIT_BLOBS
    entries = subprocess.check_output(["git", "ls-tree", "-r", "-z", BRANCH], cwd=ROOT)
    GIT_BLOBS = {
        part.split(b"\t", 1)[1].decode(): part.split(b"\t", 1)[0].split()[2].decode()
        for part in entries.split(b"\0")
        if part
    }
    for path in [
        ROOT / "scripts/validation/evaluate_phase10d.py",
        *ROOT.glob("src/cnbi_v2/synthetic/pareto/*.py"),
    ]:
        checked(path)


def number(value):
    return (
        float(value) if isinstance(value, (float, int, np.number)) and np.isfinite(value) else None
    )


def cell(tasks):
    setup()
    sid = tasks[0]["scenario_id"]
    context = load_evaluation_context(
        ROOT / "results/phase_10_synthetic_pareto/analytical_20261029",
        sid,
        ROOT / "results/phase_10_synthetic_generation/structural_20261029",
    )
    rows = []
    for task in tasks:
        instance = task["instance_id"]
        oldname = f"official__{instance}__C-NBI"
        row = dict(
            instance_id=instance,
            scenario_id=sid,
            replica_id=task["replica_id"],
            nx=context.scenario.nx,
            B_original=2000,
            integrity="FAIL",
            error="",
        )
        for metric in METRICS:
            row.update({f"{metric}_{suffix}": None for suffix in ("original", "ES", "delta")})
        try:
            cp_bytes, row["ES_checkpoint_sha256"] = checked(ES / f"checkpoints/{instance}.json")
            cp = json.loads(cp_bytes)
            assert cp["state"] == "COMPLETED" and cp["seed"] == task["seed"]
            verify_payload(ES, cp["payload_checksums"])
            _, row["ES_decisions_sha256"] = checked(ES / f"raw_decisions/{instance}.npz")
            old_bytes, row["original_metrics_sha256"] = checked(
                OLD / f"external_evaluation/{oldname}.json"
            )
            original = json.loads(old_bytes)
            row.update(
                B_effective=cp["B_effective"],
                kernel_seconds_ES=cp["kernel_seconds"],
                kernel_seconds_original=original["diagnostics"]["seconds"],
                worker_seconds_ES=cp["worker_seconds"],
            )
            row["kernel_seconds_delta"] = row["kernel_seconds_ES"] - row["kernel_seconds_original"]
            row["kernel_ratio"] = row["kernel_seconds_ES"] / row["kernel_seconds_original"]
            with np.load(ES / f"raw_decisions/{instance}.npz", allow_pickle=False) as arrays:
                decisions = arrays["decisions"]
            assert decisions.dtype == np.float64 and len(decisions) == cp["output_count"]
            # Name alias only satisfies the unchanged API; no optimizer dispatch.
            result = context.evaluate(
                sid,
                int(task["replica_id"]),
                "C-NBI",
                decisions,
                dict(variant="C-NBI-ES-ADR0009", run_id=instance),
                seconds=cp["kernel_seconds"],
            )
            for metric in METRICS:
                before = (
                    original["diagnostics"]["nondominated_count"]
                    if metric == "ND"
                    else original["metrics"].get(metric)
                )
                after = (
                    result.diagnostics["nondominated_count"]
                    if metric == "ND"
                    else result.metrics.get(metric)
                )
                a, b = number(before), number(after)
                row.update(
                    {
                        f"{metric}_original": a,
                        f"{metric}_ES": b,
                        f"{metric}_delta": b - a if a is not None and b is not None else None,
                    }
                )
            row.update(
                HV_status_original=original["metrics"].get("HV_status"),
                HV_status_ES=result.metrics.get("HV_status"),
                integrity="PASS",
            )
            row["HV_pair_valid"] = (
                row["HV_status_original"] in HV_VALID and row["HV_status_ES"] in HV_VALID
            )
            row["undefined_metrics"] = ";".join(
                m for m in METRICS if row[f"{m}_original"] is None or row[f"{m}_ES"] is None
            )
            assert (
                checked(OLD / f"external_evaluation/{oldname}.json")[1]
                == row["original_metrics_sha256"]
            )
        except Exception as error:
            row.update(integrity="FAIL", error=f"{type(error).__name__}: {error}")
        rows.append(row)
    return rows


def table(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def outcomes(rows, metric):
    values = [
        r[f"{metric}_delta_medians"] for r in rows if r[f"{metric}_delta_medians"] is not None
    ]
    benefit = np.array(values) * (1 if metric == "HV" else -1)
    return (
        (
            f"n={len(values)}, mediana Δ={np.median(values):.8g}, "
            f"V/D/E={sum(benefit > 0)}/{sum(benefit < 0)}/{sum(benefit == 0)}"
        )
        if values
        else "indefinido"
    )


def main():
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    setup()
    tasks = json.loads(checked(ES / "manifest.json")[0])["tasks"]
    original_tasks = [
        t
        for t in read_json(OLD / "seed_manifest.json")["tasks"]
        if t["stage"] == "official" and t["method"] == "C-NBI"
    ]
    assert tasks == original_tasks and len({t["instance_id"] for t in tasks}) == 135
    groups = [
        [t for t in tasks if t["scenario_id"] == sid]
        for sid in sorted({t["scenario_id"] for t in tasks})
    ]
    assert len(groups) == 27 and all(len(g) == 5 for g in groups)
    OUT.mkdir(exist_ok=False)
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows = [r for group in pool.map(cell, groups) for r in group]
    assert len(rows) == 135
    table(OUT / "paired_135.csv", rows)
    scenarios = []
    for group in groups:
        cases = [r for r in rows if r["scenario_id"] == group[0]["scenario_id"]]
        row = dict(
            scenario_id=group[0]["scenario_id"],
            nx=cases[0]["nx"],
            replicas=5,
            integrity_failures=sum(r["integrity"] != "PASS" for r in cases),
        )
        for metric in METRICS:
            valid = [
                r
                for r in cases
                if r["integrity"] == "PASS"
                and r[f"{metric}_delta"] is not None
                and (metric != "HV" or r["HV_pair_valid"])
            ]
            row[f"{metric}_valid_pairs"] = len(valid)
            for suffix in ("original", "ES", "delta"):
                row[f"{metric}_median_{suffix}"] = (
                    float(np.median([r[f"{metric}_{suffix}"] for r in valid]))
                    if len(valid) == 5
                    else None
                )
            a, b = row[f"{metric}_median_original"], row[f"{metric}_median_ES"]
            row[f"{metric}_delta_medians"] = b - a if a is not None and b is not None else None
        for field in (
            "B_effective",
            "kernel_seconds_original",
            "kernel_seconds_ES",
            "kernel_ratio",
        ):
            row[f"{field}_median"] = (
                float(np.median([r[field] for r in cases]))
                if not row["integrity_failures"]
                else None
            )
        scenarios.append(row)
    assert len(scenarios) == 27
    table(OUT / "scenarios_27.csv", scenarios)
    good = [r for r in rows if r["integrity"] == "PASS"]
    before = sum(r["kernel_seconds_original"] for r in good)
    after = sum(r["kernel_seconds_ES"] for r in good)
    changed = sum(r["ND_delta"] != 0 for r in good)
    lines = [
        "# C-NBI-ES versus B=2000 — resumo descritivo",
        f"Integridade: {len(good)}/135 PASS; falhas: {135 - len(good)}. "
        "API10C congelada; alias C-NBI apenas na validação do nome.",
        "27 cenários com cinco réplicas; Δ=ES−original; sinais estritos, "
        "sem tolerância nova, inferência ou equivalência formal.",
        "IGD: " + outcomes(scenarios, "IGD"),
        "HV: " + outcomes(scenarios, "HV"),
        f"Cardinalidade ND: {changed}/135 casos mudaram; "
        f"total {sum(r['ND_original'] for r in good):g}→{sum(r['ND_ES'] for r in good):g}.",
        f"Kernels: {before:.3f}→{after:.3f}s ({100 * (after / before - 1):+.3f}%); "
        f"mediana das razões por caso={np.median([r['kernel_ratio'] for r in good]):.5f}.",
        "Tempos históricos, não controlados; kernel inclui I/O incremental ES; "
        "worker ES inclui persistência final.",
        f"Valores indefinidos: {sum(bool(r.get('undefined_metrics')) for r in good)} casos; "
        f"HV sem precisão válida: {sum(not r['HV_pair_valid'] for r in good)} casos "
        "(excluídos apenas do resumo HV).",
    ]
    for nx in (2, 3, 5):
        subset = [r for r in good if r["nx"] == nx]
        cells = [r for r in scenarios if r["nx"] == nx]
        ratio = sum(r["kernel_seconds_ES"] for r in subset) / sum(
            r["kernel_seconds_original"] for r in subset
        )
        lines.append(
            f"nx={nx}: IGD [{outcomes(cells, 'IGD')}]; HV [{outcomes(cells, 'HV')}]; "
            f"tempo {100 * (ratio - 1):+.2f}%; ΔND={sum(r['ND_delta'] for r in subset):g}."
        )
    lines += [
        "IGD/HV: medianas globais preservadas descritivamente; houve perdas em alguns "
        "cenários. Não há demonstração de equivalência.",
        "Custo: "
        + (
            "não reduziu o tempo agregado dos kernels."
            if after >= before
            else "reduziu o tempo agregado histórico dos kernels, sem prova de speedup controlado."
        ),
        "Adoção: manter experimental; não adotar como padrão por economia de tempo neste resultado."
        if after >= before
        else "Adoção: apenas experimental, considerando perdas individuais e tempos históricos.",
        "Falhas/indefinições estão identificadas no CSV; nenhuma métrica original foi recalculada.",
    ]
    markdown = lines[0] + "\n\n" + "\n".join("- " + line for line in lines[1:]) + "\n"
    (OUT / "summary.md").write_bytes(markdown.encode())
    print(
        json.dumps(
            dict(evaluated=len(good), failures=135 - len(good), scenarios=27, output=str(OUT))
        )
    )


if __name__ == "__main__":
    main()
