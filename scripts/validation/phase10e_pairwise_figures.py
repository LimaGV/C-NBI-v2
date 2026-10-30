"""Pair-specific displays: C-NBI can have a different subset in each comparison."""

from pathlib import Path

import matplotlib
import pandas as pd
from phase10e_pairwise_inputs import COMPARATORS, OUTPUT, digest, write

matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORS = {"C-NBI": "#0072B2", "VRF-NBI": "#D55E00", "NSGA-III": "#009E73", "MOEA/D": "#CC79A7"}
DELIVERED = []


def finish(fig, stem):
    for ax in fig.axes:
        ax.grid(False)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    folder = OUTPUT / "figures"
    folder.mkdir(exist_ok=True)
    for suffix in ("png", "pdf"):
        path = folder / f"{stem}.{suffix}"
        metadata = {"CreationDate": None, "ModDate": None} if suffix == "pdf" else {}
        fig.savefig(path, dpi=600, bbox_inches="tight", metadata=metadata)
        DELIVERED.append(dict(path=str(path.relative_to(OUTPUT)), sha256=digest(path)))
    plt.close(fig)


def figures():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.grid": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    summary = pd.read_csv(OUTPUT / "scenario_metric_summary.csv")
    tests = pd.read_csv(OUTPUT / "statistical_tests.csv")
    diagnostic = pd.read_csv(OUTPUT / "selection_diagnostics.csv")
    main = summary[summary.variant.isin(["native", "equalized"])].copy()
    main["nx"] = main.scenario_id.str.extract(r"nx(\d+)").astype(int)
    main["delta"] = main.scenario_id.str.extract(r"delta(\d+)").astype(int)
    main["m"] = main.nx + main.delta + 1
    for metric, stem in (
        ("IGD", "pairwise_native_equalized_igd"),
        ("HV", "pairwise_native_equalized_hv"),
    ):
        fig, axes = plt.subplots(1, 3, figsize=(10, 3.4))
        for ax, comparator in zip(axes, COMPARATORS, strict=True):
            pair = main[(main.comparator == comparator) & (main.metric == metric)]
            wide = pair.pivot(
                index=["scenario_id", "method"], columns="variant", values="median"
            ).dropna()
            limits = (float(wide.min().min()), float(wide.max().max()))
            for method, marker in (("C-NBI", "o"), (comparator, "^")):
                g = wide.xs(method, level="method")
                ax.scatter(
                    g.native,
                    g.equalized,
                    color=COLORS[method],
                    label=method,
                    s=22,
                    alpha=0.8,
                    marker=marker,
                )
            ax.plot(limits, limits, "--", color=".55", linewidth=0.8)
            ax.set(
                xlabel=f"Native {metric}",
                ylabel=f"Pairwise equalized {metric}",
                title=f"C-NBI vs {comparator}\n{len(wide) // 2} common valid cells",
            )
            ax.legend(frameon=False, fontsize=7)
        finish(fig, stem)
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.5))
    for ax, metric in zip(axes, ("IGD", "HV"), strict=True):
        labels = []
        for index, (comparator, variant) in enumerate(
            (c, v) for c in COMPARATORS for v in ("native", "equalized")
        ):
            r = tests[
                (tests.comparator == comparator)
                & (tests.variant == variant)
                & (tests.metric == metric)
            ].iloc[0]
            color = ".5" if variant == "native" else COLORS["C-NBI"]
            ax.plot([r.ci_low, r.ci_high], [index, index], color=color, linewidth=1.5)
            ax.scatter(r.median_difference, index, color=color, s=24)
            labels.append(f"vs {comparator}: {variant}")
        ax.set_yticks(range(6), labels)
        ax.invert_yaxis()
        ax.axvline(0, color=".5", linewidth=0.7)
        ax.set(
            xlabel=f"C-NBI minus comparator: {metric}",
            title="Pointwise 95% scenario-bootstrap intervals",
        )
    finish(fig, "pairwise_confidence_intervals")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9))
    for i, comparator in enumerate(COMPARATORS):
        pair = diagnostic[diagnostic.comparator == comparator]
        boxes = axes[0].boxplot(
            pair[pair.method == "C-NBI"].K, positions=[i], widths=0.6, patch_artist=True
        )
        boxes["boxes"][0].set_facecolor(COLORS[comparator])
        for j, method in enumerate(("C-NBI", comparator)):
            values = pair[pair.method == method].retained_fraction * 100
            boxes = axes[1].boxplot(values, positions=[3 * i + j], widths=0.6, patch_artist=True)
            boxes["boxes"][0].set_facecolor(COLORS[method])
    axes[0].set_xticks(range(3), COMPARATORS)
    axes[0].set_yscale("log")
    axes[0].set(xlabel="C-NBI comparator", ylabel="Pair-specific K (135 paired replicas)")
    axes[1].set_xticks([3 * i + 0.5 for i in range(3)], [f"C-NBI /\n{c}" for c in COMPARATORS])
    axes[1].set_ylabel("Native ND points retained (%)")
    axes[1].set_ylim(-3, 105)
    finish(fig, "pairwise_cardinality_retention")
    for metric, variable, stem, xlabel in (
        ("IGD", "nx", "pairwise_igd_by_dimension", "Decision-space dimension"),
        ("HV", "m", "pairwise_hv_by_objectives", "Number of objectives"),
    ):
        fig, axes = plt.subplots(1, 3, figsize=(10, 3.5), sharey=True)
        for ax, comparator in zip(axes, COMPARATORS, strict=True):
            pair = main[(main.comparator == comparator) & (main.metric == metric)]
            common = set(pair[pair.variant == "native"].scenario_id) & set(
                pair[pair.variant == "equalized"].scenario_id
            )
            pair = pair[pair.scenario_id.isin(common)]
            for method in ("C-NBI", comparator):
                for variant, style in (("native", "--"), ("equalized", "-")):
                    g = (
                        pair[(pair.method == method) & (pair.variant == variant)]
                        .groupby(variable)["median"]
                        .median()
                    )
                    ax.plot(
                        g.index,
                        g,
                        marker="o",
                        linestyle=style,
                        color=COLORS[method],
                        label=f"{method} {variant}",
                        markersize=3,
                    )
            ax.set_xticks(sorted(pair[variable].unique()))
            ax.set(xlabel=xlabel, title=f"C-NBI vs {comparator}")
            ax.legend(frameon=False, fontsize=6.5)
        axes[0].set_ylabel(f"{metric}: median of scenario medians")
        finish(fig, stem)
    write(
        OUTPUT / "figures/figure_provenance.json",
        dict(
            outputs=DELIVERED,
            language="English",
            grid=False,
            PNG_DPI=600,
            PDF_vector=True,
            script_sha256=digest(Path(__file__)),
            sources_sha256={
                p: digest(OUTPUT / p)
                for p in (
                    "scenario_metric_summary.csv",
                    "statistical_tests.csv",
                    "selection_diagnostics.csv",
                )
            },
            interpretation="independent paired C-NBI subsets; no four-method equalized ranking",
        ),
    )


if __name__ == "__main__":
    figures()
