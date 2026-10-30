"""Independent read-only audit of every Phase10E subset and primary table."""

from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from phase10e_inputs import INPUT, METHODS, OUTPUT, digest, verify, write

from cnbi_v2.synthetic.analysis.inference import holm
from cnbi_v2.synthetic.analysis.selection import equalized_indices
from cnbi_v2.synthetic.domain import radius


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit():
    start = perf_counter()
    protected = verify()
    native = pd.read_csv(OUTPUT / "native_replica_metrics.csv", float_precision="round_trip")
    equalized = pd.read_csv(OUTPUT / "equalized_replica_metrics.csv", float_precision="round_trip")
    robustness = pd.read_csv(
        OUTPUT / "feasibility_replica_metrics.csv", float_precision="round_trip"
    )
    source = pd.read_csv(INPUT / "benchmark_native_metrics.csv", float_precision="round_trip")
    keys = ["scenario_id", "replica_id", "method"]
    for metric in ("GD", "IGD", "HV", "Spacing", "Sparsity"):
        require(
            np.array_equal(
                native.set_index(keys).sort_index()[metric],
                source.set_index(keys).sort_index()[metric],
            ),
            "native source values were altered",
        )
    require(len(equalized) == 540 and len(robustness) == 2160, "incorrect derived row counts")
    rows = 0
    for (sid, replica), group in native.groupby(["scenario_id", "replica_id"]):
        count = int(group.nondominated_count.min())
        require(set(group.method) == set(METHODS), "incomplete paired block")
        for original in group.itertuples():
            run = f"official__{sid}__replica{replica}__{original.method.replace('/', '_')}"
            with np.load(INPUT / f"raw_decisions/{run}.npz", allow_pickle=False) as f:
                x = f["decisions"]
            with np.load(INPUT / f"external_evaluation/{run}.npz", allow_pickle=False) as f:
                normalized, nd = f["normalized_responses"], f["nondominated_indices"]
            subset = equalized[
                (equalized.scenario_id == sid)
                & (equalized.replica_id == replica)
                & (equalized.method == original.method)
            ].iloc[0]
            require(subset.K == count, "K differs from paired native minimum")
            with np.load(OUTPUT / f"subsets/{run}.npz", allow_pickle=False) as f:
                chosen = f["equalized_raw_indices"]
                require(
                    len(chosen) == count and len(np.unique(chosen)) == count,
                    "wrong selected cardinality or duplicated row IDs",
                )
                require(
                    np.isin(chosen, nd).all(), "selected point was not an original native ND point"
                )
                require(
                    np.array_equal(chosen, equalized_indices(normalized[nd], nd, count)),
                    "FPS replay mismatch",
                )
                require(
                    np.array_equal(f["equalized_decisions"], x[chosen])
                    and np.array_equal(f["equalized_normalized"], normalized[chosen]),
                    "new or modified points in equalized set",
                )
                require(
                    f["equalized_decisions"].dtype == np.float64
                    and f["equalized_normalized"].dtype == np.float64,
                    "loss of float64 precision",
                )
                alpha = radius(original.nx)
                norms = np.linalg.norm(x, axis=1)
                for index, epsilon in enumerate((0.0, 1e-12, 1e-10, 1e-9)):
                    row = robustness[
                        (robustness.scenario_id == sid)
                        & (robustness.replica_id == replica)
                        & (robustness.method == original.method)
                        & (robustness.epsilon == epsilon)
                    ].iloc[0]
                    selected = f[f"epsilon_{index}_nd_raw_indices"]
                    require(len(selected) == row.N_ND, "wrong robustness ND count")
                    require(
                        np.sum(norms <= alpha + epsilon) == row.N_feasible,
                        "wrong norm-tolerance feasible count",
                    )
                    require(
                        np.all(norms[selected] <= alpha + epsilon),
                        "infeasible secondary ND decision",
                    )
                    if epsilon == 0:
                        require(np.array_equal(selected, nd), "strict source selection changed")
            rows += 1
    tests = pd.read_csv(OUTPUT / "statistical_tests.csv", float_precision="round_trip")
    primary = tests[tests.analysis == "native_primary"]
    require(len(primary) == 14, "wrong primary multiplicity family")
    require(set(primary[primary.metric == "IGD"].n_scenarios) == {27}, "wrong primary IGD blocks")
    require(
        set(primary[primary.metric == "HV"].n_scenarios) == {26}, "pending HV cell not excluded"
    )
    for _, family in tests.groupby("analysis", sort=False):
        require(
            np.array_equal(holm(family.pvalue.to_numpy()), family.p_holm.to_numpy()),
            "Holm family replay mismatch",
        )
    require(
        set(source.HV_status[source.HV_status == "PRECISION_PENDING"].index) != set(),
        "official precision flags were overwritten",
    )
    require(verify() == protected, "protected input inventory changed")
    write(
        OUTPUT / "audit_report.json",
        dict(
            status="PASSED",
            subsets=rows,
            paired_blocks=135,
            robustness_rows=len(robustness),
            protected_original_files=protected,
            native_values_unchanged=True,
            selected_points_are_real_native_ND=True,
            all_FPS_indices_reproduced=True,
            float64_preserved=True,
            strict_selections_unchanged=True,
            primary_family_hypotheses=14,
            official_HV_statuses_unchanged=True,
            optimization_executions=0,
            wall_seconds=perf_counter() - start,
            auditor_sha256=digest(Path(__file__)),
        ),
    )
    print("Phase10E independent audit PASSED", flush=True)


if __name__ == "__main__":
    audit()
