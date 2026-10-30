"""Scientific Phase10E figures from saved analyses, without decorative grids."""

import hashlib
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from phase10e_inputs import METHODS, OUTPUT, ROOT, digest, table, write

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

COLORS = dict(zip(METHODS, ("#0072B2", "#D55E00", "#009E73", "#CC79A7"), strict=True))
DELIVERED = []


def finish(fig, stem):
    for ax in fig.axes:
        ax.grid(False)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    target = OUTPUT / "figures"
    target.mkdir(exist_ok=True)
    for suffix in ("png", "pdf"):
        path = target / f"{stem}.{suffix}"
        kwargs = dict(metadata={"CreationDate": None, "ModDate": None}) if suffix == "pdf" else {}
        fig.savefig(path, dpi=600, bbox_inches="tight", **kwargs)
        DELIVERED.append(dict(path=str(path.relative_to(OUTPUT)), sha256=digest(path)))
    plt.close(fig)


def attach(summary):
    s = summary.copy()
    s["nx"] = s.scenario_id.str.extract(r"nx(\d+)").astype(int)
    s["delta"] = s.scenario_id.str.extract(r"delta(\d+)").astype(int)
    s["rho"] = s.scenario_id.str.extract(r"rho(\d+)").astype(int) / 100
    s["m"] = s.nx + s.delta + 1
    return s


def legend(ax):
    ax.legend(
        handles=[
            Line2D([], [], color=COLORS[m], marker="o", linestyle="", label=m) for m in METHODS
        ],
        frameon=False,
        fontsize=8,
    )


def figures():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "axes.grid": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    summary = attach(pd.read_csv(OUTPUT / "scenario_metric_summary.csv"))
    native = summary[summary.analysis == "native_primary"]
    equal = summary[summary.analysis == "equalized_secondary"]
    tests = pd.read_csv(OUTPUT / "statistical_tests.csv")
    raw = pd.read_csv(OUTPUT / "native_replica_metrics.csv")
    igd = native[native.metric == "IGD"]
    hv = native[native.metric == "HV"]

    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.3), sharey=True)
    for ax, nx in zip(axes, (2, 3, 5), strict=True):
        for j, method in enumerate(METHODS):
            values = igd[(igd.nx == nx) & (igd.method == method)]["median"].to_numpy()
            box = ax.boxplot(
                values,
                positions=[j],
                widths=0.55,
                patch_artist=True,
                showfliers=False,
                medianprops={"color": "black"},
            )
            box["boxes"][0].set_facecolor(COLORS[method])
            ax.scatter(
                j + np.linspace(-0.13, 0.13, len(values)),
                values,
                color=COLORS[method],
                edgecolor="white",
                linewidth=0.35,
                s=14,
                zorder=3,
            )
        ax.set_xticks(range(4), METHODS, rotation=30, ha="right")
        ax.set_title(f"$n_x={nx}$; 9 structural cells")
    axes[0].set_ylabel("Native IGD (scenario median)")
    finish(fig, "igd_by_dimension")

    fig, ax = plt.subplots(figsize=(7.3, 3.7))
    for method in METHODS:
        rows = []
        for m, group in hv[hv.method == method].groupby("m"):
            rows.append(
                (
                    m,
                    group["median"].median(),
                    group["median"].quantile(0.25),
                    group["median"].quantile(0.75),
                )
            )
        a = np.array(rows)
        ax.plot(a[:, 0], a[:, 1], "o-", color=COLORS[method], label=method)
        ax.fill_between(a[:, 0], a[:, 2], a[:, 3], color=COLORS[method], alpha=0.12)
    ax.set(
        xlabel="Number of objectives, m",
        ylabel="Native HV (median and cell IQR)",
        title="Official numerically valid cells only (26 of 27)",
    )
    ax.set_xticks(sorted(hv.m.unique()))
    ax.legend(frameon=False, ncol=2)
    finish(fig, "hv_by_objectives")

    from cnbi_v2.synthetic.analysis.inference import rank_summary

    scenarios = sorted(igd.scenario_id.unique())
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 7.8), sharey=True)
    for ax, metric in zip(axes, ("IGD", "HV"), strict=True):
        frame = (
            native[native.metric == metric]
            .pivot(index="scenario_id", columns="method", values="median")
            .reindex(columns=METHODS)
        )
        ranks = pd.DataFrame(
            rank_summary(frame.to_numpy(), maximize=metric == "HV")["ranks"],
            index=frame.index,
            columns=METHODS,
        ).reindex(scenarios)
        cmap = plt.get_cmap("viridis_r").with_extremes(bad="#e5e5e5")
        image = ax.pcolormesh(
            np.arange(5) - 0.5,
            np.arange(28) - 0.5,
            ranks.to_numpy(),
            cmap=cmap,
            vmin=1,
            vmax=4,
            shading="flat",
            edgecolors="none",
            rasterized=False,
        )
        ax.set_ylim(26.5, -0.5)
        ax.set_xlim(-0.5, 3.5)
        for i in range(27):
            for j in range(4):
                value = ranks.iloc[i, j]
                ax.text(
                    j,
                    i,
                    f"{value:g}" if np.isfinite(value) else "--",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="black" if not np.isfinite(value) or value <= 2 else "white",
                )
        ax.set_xticks(range(4), METHODS, rotation=30, ha="right")
        ax.set_title(f"{metric}: scenario ranks")
    axes[0].set_yticks(range(27), [s.replace("nx", "n").replace("delta", "d") for s in scenarios])
    colorbar = fig.colorbar(image, ax=axes[-1], fraction=0.025, pad=0.02, label="Rank (1 = best)")
    if colorbar.solids is not None:
        colorbar.solids.set_rasterized(False)
    finish(fig, "scenario_rankings")

    for metric, stem in (("IGD", "igd_native_equalized"), ("HV", "hv_native_equalized")):
        merged = native[native.metric == metric].merge(
            equal[equal.metric == metric],
            on=["scenario_id", "method", "metric"],
            suffixes=("_native", "_equalized"),
        )
        fig, axes = plt.subplots(1, 4, figsize=(10.2, 3.1), sharex=True, sharey=True)
        limits = [
            merged[["median_native", "median_equalized"]].min().min(),
            merged[["median_native", "median_equalized"]].max().max(),
        ]
        for ax, method in zip(axes, METHODS, strict=True):
            g = merged[merged.method == method]
            ax.scatter(g.median_native, g.median_equalized, color=COLORS[method], s=20, alpha=0.8)
            ax.plot(limits, limits, "--", color=".55", linewidth=0.8)
            ax.set_title(f"{method}\n{len(g)} common valid cells")
            ax.set_xlabel(f"Native {metric}")
        axes[0].set_ylabel(f"Equalized {metric}")
        finish(fig, stem)

    contrasts = attach(pd.read_csv(OUTPUT / "paired_scenario_differences.csv"))
    g = contrasts[
        (contrasts.analysis == "native_primary")
        & (contrasts.metric == "IGD")
        & (contrasts.method_a == "C-NBI")
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.3), sharey=True)
    for ax, nx in zip(axes, (2, 3, 5), strict=True):
        for other in METHODS[1:]:
            cell = g[(g.nx == nx) & (g.method_b == other)]
            ax.scatter(cell.rho, cell.difference, color=COLORS[other], s=17, alpha=0.65)
            trend = cell.groupby("rho").difference.median()
            ax.plot(trend.index, trend.values, color=COLORS[other], marker="o", label=other)
        ax.axhline(0, color=".5", linewidth=0.7)
        ax.set_xticks([0.25, 0.60, 0.85])
        ax.set(xlabel="Target mean absolute correlation", title=f"$n_x={nx}$")
    axes[0].set_ylabel("IGD difference: C-NBI minus comparator")
    axes[1].legend(frameon=False, fontsize=7)
    finish(fig, "structural_correlation_effects")

    fig, ax = plt.subplots(figsize=(6.5, 3.7))
    for method in METHODS:
        g = igd[igd.method == method].groupby("nx")["median"]
        mids, low, high = g.median(), g.quantile(0.25), g.quantile(0.75)
        ax.plot(mids.index, mids, "o-", color=COLORS[method], label=method)
        ax.fill_between(mids.index, low, high, color=COLORS[method], alpha=0.12)
    ax.set_xticks([2, 3, 5])
    ax.set(
        xlabel="Decision-space dimension",
        ylabel="Native IGD (median and cell IQR)",
        title="Method-by-dimension association; fixed anchor geometry",
    )
    ax.legend(frameon=False)
    finish(fig, "method_dimension_interactions")

    costs = (
        raw.groupby(["scenario_id", "method"])[["observed_lifecycle_seconds", "nondominated_count"]]
        .median()
        .reset_index()
    )
    merged = igd.merge(costs, on=["scenario_id", "method"], validate="one_to_one")
    for variable, label, stem in (
        ("observed_lifecycle_seconds", "Observed full lifecycle (s)", "quality_time"),
        ("nondominated_count", "Native ND cardinality", "cardinality_influence"),
    ):
        fig, ax = plt.subplots(figsize=(6.5, 3.9))
        for method in METHODS:
            g = merged[merged.method == method]
            ax.scatter(
                g[variable], g["median"], color=COLORS[method], label=method, s=23, alpha=0.75
            )
        ax.set_xscale("log")
        ax.set(xlabel=label, ylabel="Native IGD (scenario median)")
        ax.legend(frameon=False)
        finish(fig, stem)

    feasibility = pd.read_csv(OUTPUT / "feasibility_replica_metrics.csv")
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.2))
    display = []
    for method in METHODS:
        g = feasibility[feasibility.method == method]
        totals, shifts, hv_shifts = [], [], []
        baseline = g[g.epsilon == 0].set_index(["scenario_id", "replica_id"])
        for epsilon in sorted(g.epsilon.unique()):
            rows = g[g.epsilon == epsilon].set_index(["scenario_id", "replica_id"])
            totals.append(int(rows.N_feasible.sum() - baseline.N_feasible.sum()))
            shifts.append(float(np.max(np.abs(rows.IGD - baseline.IGD))))
            valid = rows.HV_status.isin({"PRECISION_CRITERIA_PASSED", "EXACT_UP_TO_FLOAT64"}) & (
                baseline.HV_status.isin({"PRECISION_CRITERIA_PASSED", "EXACT_UP_TO_FLOAT64"})
            )
            hv_shifts.append(
                float(np.max(np.abs(rows.loc[valid, "HV"] - baseline.loc[valid, "HV"])))
            )
            display.append(
                dict(
                    method=method,
                    epsilon=epsilon,
                    added_feasible=totals[-1],
                    max_absolute_IGD_change=shifts[-1],
                    max_absolute_HV_change_valid_pairs=hv_shifts[-1],
                )
            )
        for ax, values in zip(axes, (totals, shifts, hv_shifts), strict=True):
            ax.plot(range(4), values, "o-", color=COLORS[method], label=method)
    for ax, label in zip(
        axes,
        (
            "Additional feasible decisions",
            "Maximum absolute IGD change",
            "Maximum absolute HV change\n(common valid run pairs)",
        ),
        strict=True,
    ):
        ax.set_xticks(range(4), ["0", "$10^{-12}$", "$10^{-10}$", "$10^{-9}$"])
        ax.set(xlabel="Norm tolerance epsilon", ylabel=label)
    axes[0].legend(frameon=False, fontsize=7)
    finish(fig, "feasibility_tolerance_sensitivity")
    table(OUTPUT / "feasibility_plot_values.csv", display)

    fig, axes = plt.subplots(1, 2, figsize=(9.3, 4.3))
    for ax, metric in zip(axes, ("IGD", "HV"), strict=True):
        labels = []
        for row_index, (other, analysis) in enumerate(product_pairs()):
            row = tests[
                (tests.analysis == analysis)
                & (tests.metric == metric)
                & (tests.method_a == "C-NBI")
                & (tests.method_b == other)
            ].iloc[0]
            color = "#0072B2" if analysis == "native_primary" else "#D55E00"
            ax.plot([row.ci_low, row.ci_high], [row_index] * 2, color=color, linewidth=1.5)
            ax.scatter(row.median_difference, row_index, color=color, s=25)
            labels.append(
                f"vs {other}: {'native' if analysis == 'native_primary' else 'equalized'}"
            )
        ax.axvline(0, color=".45", linewidth=0.8)
        ax.set_yticks(range(6), labels)
        ax.set_xlabel(f"C-NBI minus comparator: {metric}")
        ax.set_title("Pointwise 95% scenario-bootstrap intervals")
        ax.invert_yaxis()
    finish(fig, "paired_confidence_intervals")
    sources = [
        OUTPUT / f
        for f in (
            "scenario_metric_summary.csv",
            "statistical_tests.csv",
            "paired_scenario_differences.csv",
            "native_replica_metrics.csv",
            "feasibility_replica_metrics.csv",
        )
    ]
    write(
        OUTPUT / "figures/figure_provenance.json",
        dict(
            source_sha256={str(p.relative_to(ROOT)): digest(p) for p in sources},
            script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            outputs=DELIVERED,
            grid=False,
            language="English",
            png_dpi=600,
            pdf_vector=True,
            ranks="official pending HV cell remains missing, never assigned a rank",
        ),
    )


def product_pairs():
    return [
        (other, analysis)
        for other in METHODS[1:]
        for analysis in ("native_primary", "equalized_secondary")
    ]


if __name__ == "__main__":
    figures()
