"""Prespecified paired inference and descriptive fixed-factor associations."""

from itertools import combinations, product

import numpy as np
import pandas as pd
from phase10e_inputs import METHODS, OUTPUT, ROOT, STRUCTURAL, read, table, write
from scipy.stats import spearmanr

from cnbi_v2.synthetic.analysis.factors import factorial_decomposition
from cnbi_v2.synthetic.analysis.inference import (
    friedman_permutation,
    holm,
    paired_effect,
    rank_summary,
    role_seed,
)

VALID = {"PRECISION_CRITERIA_PASSED", "EXACT_UP_TO_FLOAT64", "ZERO_CONTRIBUTION_CERTIFIED"}
METRICS = ("GD", "IGD", "HV", "Spacing", "Sparsity")
KEYS = ["scenario_id", "replica_id", "method"]


def medians(frame, metric, strict_hv=True):
    retained, excluded = [], []
    for sid, cell in frame.groupby("scenario_id", sort=True):
        if len(cell) != 20 or cell.duplicated(KEYS).any() or set(cell.method) != set(METHODS):
            raise ValueError("five complete paired replicas per cell required")
        bad = cell[metric].isna() | ~np.isfinite(cell[metric])
        if metric == "HV" and strict_hv:
            bad |= ~cell.HV_status.isin(VALID)
        if bad.any():
            excluded.append(
                dict(
                    scenario_id=sid,
                    metric=metric,
                    excluded_runs=int(bad.sum()),
                    identities=";".join(
                        f"{r.method}:r{r.replica_id}" for r in cell[bad].itertuples()
                    ),
                    reason="nonfinite or insufficient numerical precision",
                )
            )
            continue
        for method in METHODS:
            group = cell[cell.method == method]
            if set(group.replica_id) != set(range(1, 6)):
                raise ValueError("missing or incorrect replica IDs")
            values = group[metric].to_numpy()
            retained.append(
                dict(
                    scenario_id=sid,
                    method=method,
                    metric=metric,
                    median=float(np.median(values)),
                    q25=float(np.quantile(values, 0.25)),
                    q75=float(np.quantile(values, 0.75)),
                    replicas=5,
                )
            )
    summary = pd.DataFrame(retained)
    wide = (
        (
            summary.pivot(index="scenario_id", columns="method", values="median")
            .reindex(columns=METHODS)
            .sort_index()
        )
        if len(summary)
        else pd.DataFrame(columns=METHODS)
    )
    return summary, wide, excluded


def compare(analysis, frame, metrics, strict_hv=True):
    tests, rankings, cell_rows, exclusions, differences = [], [], [], [], []
    for metric in metrics:
        summary, wide, excluded = medians(frame, metric, strict_hv)
        exclusions.extend(dict(analysis=analysis, **r) for r in excluded)
        cell_rows.extend(dict(analysis=analysis, **r) for r in summary.to_dict("records"))
        if len(wide) < 2:
            continue
        values = wide.to_numpy(dtype=float)
        maximize = metric in {"HV", "N_ND", "N_feasible"}
        omnibus = friedman_permutation(values, seed=role_seed(f"{analysis}/{metric}/friedman"))
        tests.append(
            dict(
                analysis=analysis,
                metric=metric,
                test="Friedman_permutation",
                method_a="all",
                method_b="all",
                n_scenarios=len(wide),
                **omnibus,
            )
        )
        ranks = rank_summary(values, maximize=maximize)
        for j, method in enumerate(METHODS):
            rankings.append(
                dict(
                    analysis=analysis,
                    metric=metric,
                    method=method,
                    n_scenarios=len(wide),
                    mean_rank=float(ranks["mean_rank"][j]),
                    best_count=int(ranks["best_count"][j]),
                    fractional_best=float(ranks["fractional_best"][j]),
                    median_of_cell_medians=float(np.median(values[:, j])),
                )
            )
        for i, j in combinations(range(4), 2):
            first, second = METHODS[i], METHODS[j]
            effect = paired_effect(
                values[:, i],
                values[:, j],
                maximize=maximize,
                seed=role_seed(f"{analysis}/{metric}/{first}/{second}"),
            )
            tests.append(
                dict(
                    analysis=analysis,
                    metric=metric,
                    test="Wilcoxon_exact_conditional",
                    method_a=first,
                    method_b=second,
                    **effect,
                )
            )
            for sid, difference in zip(wide.index, values[:, i] - values[:, j], strict=True):
                differences.append(
                    dict(
                        analysis=analysis,
                        metric=metric,
                        scenario_id=sid,
                        method_a=first,
                        method_b=second,
                        difference=float(difference),
                    )
                )
    adjusted = holm([r["pvalue"] for r in tests]) if tests else []
    for row, p in zip(tests, adjusted, strict=True):
        row.update(
            p_holm=float(p),
            reject_holm_005=bool(p <= 0.05),
            family_size=len(tests),
            inference_role="confirmatory_in_observed_design"
            if analysis == "native_primary"
            else "exploratory_secondary",
            ci_role="pointwise_scenario_stability_only",
        )
    return tests, rankings, cell_rows, exclusions, differences


def factor_associations(contrasts, metadata):
    decomposition, associations, marginals, covariates = [], [], [], []
    frame = pd.DataFrame(contrasts).merge(metadata, on="scenario_id", validate="many_to_one")
    for key, group in frame.groupby(["analysis", "metric", "method_a", "method_b"]):
        if key[0] not in {"native_primary", "equalized_secondary", "hv_supplement_validated"}:
            continue
        base = dict(zip(("analysis", "metric", "method_a", "method_b"), key, strict=True))
        for variable in ("nx", "delta", "rho_target", "m"):
            for level, cell in group.groupby(variable):
                marginals.append(
                    dict(
                        **base,
                        factor=variable,
                        level=float(level),
                        n_cells=len(cell),
                        median_difference=float(cell.difference.median()),
                        mean_difference=float(cell.difference.mean()),
                    )
                )
        for variable in ("rho_abs_realized", "rho_signed"):
            statistic = float(spearmanr(group.difference, group[variable]).statistic)
            associations.append(
                dict(
                    **base,
                    covariate=variable,
                    n_cells=len(group),
                    spearman_rho=statistic,
                    role="exploratory_not_causal",
                )
            )
        if len(group) != 27:
            continue
        ordered = group.set_index(["nx", "delta", "rho_target"]).reindex(
            pd.MultiIndex.from_tuples(
                list(product((2, 3, 5), (1, 3, 5), (0.25, 0.60, 0.85))),
                names=["nx", "delta", "rho_target"],
            )
        )
        cube = ordered.difference.to_numpy().reshape(3, 3, 3)
        decomposition.extend(dict(**base, **r) for r in factorial_decomposition(cube))
        # Prespecified partial association: main-factor dummy columns plus each
        # observed correlation, separately. No significance-driven term selection.
        main = pd.get_dummies(
            ordered.reset_index()[["nx", "delta", "rho_target"]].astype(str),
            drop_first=True,
            dtype=float,
        ).to_numpy()
        baseline = np.column_stack((np.ones(27), main))
        for variable in ("rho_abs_realized", "rho_signed"):
            c = ordered[variable].to_numpy()
            residual_c = c - baseline @ np.linalg.lstsq(baseline, c, rcond=None)[0]
            y = ordered.difference.to_numpy()
            residual_y = y - baseline @ np.linalg.lstsq(baseline, y, rcond=None)[0]
            denominator = float(residual_c @ residual_c)
            covariates.append(
                dict(
                    **base,
                    covariate=variable,
                    n_cells=27,
                    adjusted_for="prespecified categorical main effects nx,delta,rho_target",
                    partial_slope=float(residual_c @ residual_y / denominator)
                    if denominator > 0
                    else None,
                    residual_covariate_sum_squares=denominator,
                    interpretation="descriptive_partial_association; geometry confounded; no p value",
                )
            )
    return decomposition, associations, marginals, covariates


def run():
    native = pd.read_csv(OUTPUT / "native_replica_metrics.csv", float_precision="round_trip")
    native["N_ND"] = native.nondominated_count
    equalized = pd.read_csv(OUTPUT / "equalized_replica_metrics.csv", float_precision="round_trip")
    equalized["N_ND"] = equalized.K
    feasibility = pd.read_csv(
        OUTPUT / "feasibility_replica_metrics.csv", float_precision="round_trip"
    )
    supplementary = pd.read_csv(
        OUTPUT / "hv_supplement_precision.csv", float_precision="round_trip"
    )
    corrected = native.copy(deep=True)
    supplement_valid = True
    replacements = []
    for key, group in supplementary.groupby(KEYS):
        row = group[(group.supplementary_max_power == 20) & (group.power == 20)].iloc[0]
        accepted = row.qmc_status in VALID
        replacements.append(
            dict(
                zip(KEYS, key, strict=True),
                accepted=bool(accepted),
                supplementary_HV=row.HV_QMC,
                supplementary_status=row.qmc_status,
            )
        )
        supplement_valid &= accepted
        mask = (
            (corrected.scenario_id == key[0])
            & (corrected.replica_id == key[1])
            & (corrected.method == key[2])
        )
        if accepted:
            corrected.loc[mask, "HV"] = row.HV_QMC
            corrected.loc[mask, "HV_status"] = row.qmc_status
    plans = [
        ("native_primary", native, ["IGD", "HV"], True),
        (
            "native_secondary",
            native,
            ["GD", "Spacing", "Sparsity", "N_ND", "observed_lifecycle_seconds"],
            True,
        ),
        ("equalized_secondary", equalized, ["IGD", "HV"], True),
        ("equalized_density", equalized, ["GD", "Spacing", "Sparsity"], True),
        ("hv_pending_provisional", native, ["HV"], False),
    ]
    if supplement_valid and len(replacements) == 2:
        plans.append(("hv_supplement_validated", corrected, ["HV"], True))
    for epsilon, frame in feasibility.groupby("epsilon", sort=True):
        plans.append(
            (
                f"feasibility_eps_{epsilon:.0e}",
                frame,
                ["GD", "IGD", "HV", "N_feasible", "N_ND"],
                True,
            )
        )
    all_outputs = [[], [], [], [], []]
    for analysis, frame, metrics, strict in plans:
        result = compare(analysis, frame, metrics, strict)
        for collected, rows in zip(all_outputs, result, strict=True):
            collected.extend(rows)
        print(analysis, "completed", flush=True)
    tests, rankings, cell_rows, exclusions, differences = all_outputs
    metadata = pd.read_csv(STRUCTURAL / "synthetic_correlations.csv", float_precision="round_trip")
    decomposition, associations, marginals, covariates = factor_associations(differences, metadata)
    for filename, rows in (
        ("statistical_tests.csv", tests),
        ("method_rankings.csv", rankings),
        ("scenario_metric_summary.csv", cell_rows),
        ("inference_exclusions.csv", exclusions),
        ("paired_scenario_differences.csv", differences),
        ("factorial_contrast_decomposition.csv", decomposition),
        ("correlation_associations.csv", associations),
        ("factor_marginal_contrasts.csv", marginals),
        ("partial_covariate_associations.csv", covariates),
        ("hv_supplement_replacements.csv", replacements),
    ):
        table(OUTPUT / filename, rows)
    # Full, uncollapsed cost counters stay paired at the replica level.
    columns = KEYS + [
        c
        for c in native.columns
        if c
        in {
            "IGD",
            "HV",
            "HV_status",
            "N_ND",
            "observed_lifecycle_seconds",
            "end_to_end_seconds",
            "model_vector_point_events",
            "scalar_quadratic_values",
            "scalar_quadratic_gradients",
            "nbi_subproblems",
            "nbi_attempts",
            "nbi_iterations",
            "mc_anchor_solves",
            "original_rsm_point_evaluations",
            "factor_model_vector_evaluations",
        }
    ]
    native[columns].to_csv(OUTPUT / "quality_cost_replica.csv", index=False, lineterminator="\n")
    costs, cost_differences = [], []
    time = native.groupby(["scenario_id", "method"]).observed_lifecycle_seconds.median().unstack()
    for first, second in combinations(METHODS, 2):
        ratios = time[first] / time[second]
        effect = paired_effect(
            np.log(ratios), np.zeros(len(ratios)), seed=role_seed(f"cost_ratio/{first}/{second}")
        )
        costs.append(
            dict(
                method_a=first,
                method_b=second,
                n_scenarios=len(ratios),
                median_time_ratio=float(np.exp(effect["median_difference"])),
                ratio_ci_low=float(np.exp(effect["ci_low"])),
                ratio_ci_high=float(np.exp(effect["ci_high"])),
                ratio_role="pointwise paired scenario stability; concurrent archived hardware",
            )
        )
        for sid, ratio in ratios.items():
            cost_differences.append(
                dict(scenario_id=sid, method_a=first, method_b=second, lifecycle_ratio=float(ratio))
            )
    table(OUTPUT / "paired_quality_cost.csv", costs)
    table(OUTPUT / "scenario_cost_ratios.csv", cost_differences)
    write(
        OUTPUT / "inference_manifest.json",
        dict(
            primary_family_hypotheses=14,
            primary_metrics=["IGD", "HV"],
            statistical_unit="scenario median of five paired nested replicas",
            families=[p[0] for p in plans],
            pending_official_values_preserved=True,
            hv_supplement_all_passed=bool(supplement_valid),
            generated_tests=len(tests),
            protocol=read(ROOT / "docs/policies/synthetic_analysis_10e.json"),
        ),
    )


if __name__ == "__main__":
    run()
