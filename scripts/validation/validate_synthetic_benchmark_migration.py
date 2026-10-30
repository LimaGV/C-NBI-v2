"""Isolated v1 regression and intermediate-stage migration checks (not calibration)."""

import argparse
import os
import subprocess
from pathlib import Path

import numpy as np

from cnbi_v2.synthetic.benchmark.archive import write_json
from cnbi_v2.synthetic.benchmark.configuration import V1_COMMIT
from cnbi_v2.synthetic.benchmark.inputs import load_search_inputs
from cnbi_v2.synthetic.benchmark.vrf_runner import run_vrf

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT/"tmp/phase10d_migration"

ORACLE = '''
import json
import numpy as np
from cnbi_experiments.doe import RSM
from cnbi_experiments.comparators import run_vrf, rotated_factor_scores
from cnbi_experiments.solver import Config
from cnbi.config import ALPHA
from factor_analyzer.rotator import Rotator
from pathlib import Path
data=np.load('migration_input.npz')
p=object.__new__(RSM)
p.nx=3;p.m=data['Y'].shape[1];p.Xobs=data['X'];p.Yobs=data['Y'];p.B=data['B']
p.lower=np.full(3,-ALPHA);p.upper=np.full(3,ALPHA)
r=run_vrf(p,Config(budget=None,seed=317))
d=r['diagnostics']
np.savez_compressed('migration_oracle.npz',loadings=d['loadings'],weights=d['score_weights'],
 targets=d['factor_targets'],variance=d['factor_variance'],utopia=d['vrf_utopia'],
 nadir=d['vrf_nadir'],payoff=d['payoff'],anchors=d['Xstar'],
 x=np.array([row['x'] for row in r['rows'] if row.get('accepted')]))
Path('legacy_status.json').write_text(json.dumps(dict(status=r['status'],rows=len(r['rows']))))
'''


def validate(legacy: Path) -> None:
    snapshot = WORK/"v1_snapshot"
    snapshot.mkdir(parents=True, exist_ok=True)
    paths = subprocess.check_output(
        ["git", "-C", str(legacy), "ls-tree", "-r", "--name-only", V1_COMMIT],
    ).decode().splitlines()
    for name in paths:
        if (name.startswith(("cnbi/", "cnbi_experiments/"))
                and (name.endswith(".py") or name.endswith("ea_calibration.json"))):
            target = snapshot/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.check_output(
                ["git", "-C", str(legacy), "show", f"{V1_COMMIT}:{name}"],
            ))
    data = load_search_inputs(ROOT/"results/phase_10_synthetic_rsm/rsm_20261029")[
        "nx3_delta3_rho060__replica1"]
    np.savez_compressed(snapshot/"migration_input.npz", X=data.ccd, Y=data.observed,
                        B=data.model.coefficients)
    (snapshot/"migration_oracle.py").write_bytes(ORACLE.encode())
    env = dict(os.environ, PYTHONPATH=str(snapshot), OPENBLAS_NUM_THREADS="1",
               OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    command = ["uv", "run", "--project", str(ROOT), "--with", "factor-analyzer", "python"]
    with (WORK/"legacy_regression.log").open("wb") as log:
        tests = subprocess.run(command+[
            "-m", "pytest", "cnbi_experiments/tests/test_extension.py::Extension::"
            "test_vrf_minimum_two_and_retention", "-q", "-o", "filterwarnings="],
            cwd=snapshot, env=env, stdout=log, stderr=subprocess.STDOUT)
    with (WORK/"legacy_oracle.log").open("wb") as log:
        oracle = subprocess.run(command+["migration_oracle.py"], cwd=snapshot, env=env,
                                stdout=log, stderr=subprocess.STDOUT)
    if tests.returncode or oracle.returncode:
        write_json(WORK/"verification.json", dict(status="FAIL", tests_exit=tests.returncode,
                                                  oracle_exit=oracle.returncode))
        raise ValueError("legacy migration regression failed; inspect retained logs")
    new = run_vrf(data, 317)
    d = new.diagnostics
    differences = {}
    with np.load(snapshot/"migration_oracle.npz", allow_pickle=False) as old:
        for key, newkey in (("loadings", "loadings"), ("weights", "weights"),
                            ("targets", "targets"), ("payoff", "payoff")):
            delta = float(np.max(abs(old[key]-d[newkey])))
            differences[key] = delta
        differences["variance_after_registered_constant_correction"] = float(np.max(
            abs(old["variance"]/data.alpha-d["variance"])))
        # Targets have the same mathematical minimum. Raw utopia/nadir differ
        # by the documented constant; compare the invariant Eq25 amplitudes.
        differences["normalization_amplitude"] = float(np.max(abs(
            (old["nadir"]-old["utopia"])-(d["nadir"]-d["utopia"])) ))
        from scipy.spatial.distance import cdist
        if len(new.decisions) and len(old["x"]):
            distances = cdist(new.decisions, old["x"])
            differences["decision_hausdorff_diagnostic"] = float(max(
                distances.min(0).max(), distances.min(1).max()))
    thresholds = dict(loadings=2e-12, weights=2e-12, targets=2e-8, payoff=2e-5,
                      variance_after_registered_constant_correction=2e-12,
                      normalization_amplitude=2e-7)
    passed = all(differences[name] <= tolerance for name, tolerance in thresholds.items())
    write_json(WORK/"verification.json", dict(
        status="PASS" if passed else "FAIL", v1_commit=V1_COMMIT,
        legacy_regression_exit=tests.returncode, legacy_oracle_exit=oracle.returncode,
        comparisons=differences, technical_absolute_bounds=thresholds,
        decision_comparison=("diagnostic; nonunique local solver outputs require "
                             "independent certificates"),
        variance_difference="published sum_squared_loadings; legacy rho factor removed",
        parameters_retuned=False, scope="migration_only_no_legacy_calibration_or_campaign",
    ))
    print((WORK/"verification.json").read_text())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", type=Path, required=True)
    validate(parser.parse_args().legacy)
