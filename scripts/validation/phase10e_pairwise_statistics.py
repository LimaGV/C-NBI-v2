"""Independent two-method cohorts and jointly adjusted C-NBI pair contrasts."""

import numpy as np
import pandas as pd
from phase10e_pairwise_inputs import (
    COMPARATORS,
    INPUT,
    OUTPUT,
    PREVIOUS,
    ROOT,
    STRUCTURAL,
    name,
    pair_id,
    read,
    table,
    write,
)
from phase10e_statistics import VALID, factor_associations

from cnbi_v2.synthetic.analysis.inference import holm, paired_effect, role_seed


def pair_medians(frame, metric, comparator):
    rows, excluded = [], []
    for sid, group in frame.groupby("scenario_id", sort=True):
        if (
            len(group) != 10
            or set(group.method) != {"C-NBI", comparator}
            or group.duplicated(["replica_id", "method"]).any()
            or set(group.replica_id) != set(range(1, 6))
        ):
            raise ValueError("exactly five complete replicas of the specified pair required")
        bad = group[metric].isna() | ~np.isfinite(group[metric])
        if metric == "HV":
            bad |= ~group.HV_status.isin(VALID)
        if bad.any():
            excluded.append(
                dict(
                    scenario_id=sid,
                    comparator=comparator,
                    metric=metric,
                    excluded_runs=int(bad.sum()),
                    identities=";".join(
                        f"{r.method}:r{r.replica_id}" for r in group[bad].itertuples()
                    ),
                )
            )
            continue
        for method in ("C-NBI", comparator):
            v = group[group.method == method][metric].to_numpy(dtype=float)
            rows.append(
                dict(
                    scenario_id=sid,
                    comparator=comparator,
                    method=method,
                    metric=metric,
                    median=float(np.median(v)),
                    q25=float(np.quantile(v, 0.25)),
                    q75=float(np.quantile(v, 0.75)),
                    replicas=5,
                )
            )
    wide = (
        (
            pd.DataFrame(rows)
            .pivot(index="scenario_id", columns="method", values="median")
            .reindex(columns=["C-NBI", comparator])
            .sort_index()
        )
        if rows
        else pd.DataFrame()
    )
    return rows, wide, excluded


def compare(frame, variant, metrics):
    tests, cells, differences, exclusions = [], [], [], []
    for comparator in COMPARATORS:
        pair = frame[(frame.variant == variant) & (frame.comparator == comparator)]
        for metric in metrics:
            rows, wide, omitted = pair_medians(pair, metric, comparator)
            cells.extend(dict(variant=variant, **r) for r in rows)
            exclusions.extend(dict(variant=variant, **r) for r in omitted)
            if len(wide) < 2:
                raise ValueError("insufficient complete paired scenarios; no fabricated test")
            seed = role_seed(f"pairwise_v2/{variant}/{comparator}/{metric}")
            effect = paired_effect(
                wide["C-NBI"], wide[comparator], maximize=metric == "HV", seed=seed
            )
            tests.append(
                dict(
                    variant=variant,
                    pair_id=pair_id(comparator),
                    comparator=comparator,
                    metric=metric,
                    test="Wilcoxon_exact_conditional",
                    method_a="C-NBI",
                    method_b=comparator,
                    bootstrap_seed=str(seed),
                    bootstrap_resamples=50000,
                    **effect,
                )
            )
            for sid, difference in (wide["C-NBI"] - wide[comparator]).items():
                differences.append(
                    dict(
                        variant=variant,
                        scenario_id=sid,
                        metric=metric,
                        method_a="C-NBI",
                        method_b=comparator,
                        difference=float(difference),
                    )
                )
    for row, adjusted in zip(tests, holm([r["pvalue"] for r in tests]), strict=True):
        row.update(
            p_holm=float(adjusted),
            reject_holm_005=bool(adjusted <= 0.05),
            family_size=len(tests),
            family=f"pairwise_v2/{variant}/{'_'.join(metrics)}",
            role="requested_secondary_revision_fixed_observed_design",
            ci_role="pointwise scenario-bootstrap stability, not simultaneous",
        )
    return tests, cells, differences, exclusions


def supplemented(frame):
    result = frame.copy(deep=True)
    accepted = pd.read_csv(PREVIOUS / "hv_supplement_replacements.csv")
    checks = []
    for original in accepted.itertuples():
        if not original.accepted:
            continue
        rows = result[
            (result.scenario_id == original.scenario_id)
            & (result.replica_id == original.replica_id)
            & (result.method == original.method)
        ]
        for row in rows.itertuples():
            task = dict(
                instance_id=f"{row.scenario_id}__replica{row.replica_id}", method=row.method
            )
            run = name(task)
            with np.load(INPUT / f"external_evaluation/{run}.npz", allow_pickle=False) as f:
                nd = f["nondominated_indices"]
            if row.variant == "native":
                identity = True
            else:
                with np.load(OUTPUT / f"subsets/{row.pair_id}/{run}.npz", allow_pickle=False) as f:
                    identity = np.array_equal(np.sort(f["selected_raw_indices"]), np.sort(nd))
            checks.append(
                dict(
                    comparator=row.comparator,
                    variant=row.variant,
                    scenario_id=row.scenario_id,
                    replica_id=row.replica_id,
                    exact_original_point_set=bool(identity),
                )
            )
            if identity:
                result.loc[row.Index, "HV"] = original.supplementary_HV
                result.loc[row.Index, "HV_status"] = original.supplementary_status
    result["variant"] += "_HV_supplement"
    return result, checks


def statistics():
    frame = pd.read_csv(OUTPUT / "replica_metrics.csv")
    more, checks = supplemented(frame)
    combined = pd.concat([frame, more], ignore_index=True)
    plans = [
        ("native", ["IGD", "HV"]),
        ("equalized", ["IGD", "HV"]),
        ("native", ["GD", "Spacing", "Sparsity"]),
        ("equalized", ["GD", "Spacing", "Sparsity"]),
        ("native_HV_supplement", ["HV"]),
        ("equalized_HV_supplement", ["HV"]),
    ]
    collected = [[], [], [], []]
    for variant, metrics in plans:
        for destination, rows in zip(collected, compare(combined, variant, metrics), strict=True):
            destination.extend(rows)
    tests, cells, differences, exclusions = collected
    table(OUTPUT / "statistical_tests.csv", tests)
    # A metric appears once in quality or density plans; no duplicate scenario rows.
    table(OUTPUT / "scenario_metric_summary.csv", cells)
    table(OUTPUT / "paired_scenario_differences.csv", differences)
    table(OUTPUT / "inference_exclusions.csv", exclusions)
    table(OUTPUT / "HV_supplement_identity.csv", checks)
    factors_input = [
        dict(
            analysis="native_primary" if r["variant"] == "native" else "equalized_secondary",
            **{k: v for k, v in r.items() if k != "variant"},
        )
        for r in differences
        if r["variant"] in {"native", "equalized"}
    ]
    metadata = pd.read_csv(STRUCTURAL / "synthetic_correlations.csv")
    for filename, rows in zip(
        (
            "factorial_contrast_decomposition.csv",
            "correlation_associations.csv",
            "factor_marginal_contrasts.csv",
            "partial_covariate_associations.csv",
        ),
        factor_associations(factors_input, metadata),
        strict=True,
    ):
        for row in rows:
            row["analysis"] = {
                "native_primary": "native_pair",
                "equalized_secondary": "equalized_pair",
            }[row["analysis"]]
        table(OUTPUT / filename, rows)
    write(
        OUTPUT / "inference_manifest.json",
        dict(
            status="COMPLETED",
            quality_family_size=6,
            density_family_size=9,
            omnibus_equalized_Friedman=False,
            joint_ranking=False,
            statistical_unit="structural_scenario",
            replicas_per_scenario=5,
            independent_comparators=list(COMPARATORS),
            supplementary_values_only_after_point_set_identity=True,
            protocol=read(ROOT / "docs/policies/synthetic_analysis_10e_pairwise.json"),
        ),
    )


if __name__ == "__main__":
    statistics()
