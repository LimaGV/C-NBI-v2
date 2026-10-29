"""Frozen fronts, benchmark curves, diagnostic projections and workflow D–J."""

import textwrap

import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.ticker import NullFormatter

from .problem_panels import DECISION_PAIRS, PAIRS, figure, heatmap, local_panel, response_axis
from .style import (
    DIRECTIONS,
    FACTORS,
    LINESTYLES,
    MARKERS,
    PALETTE,
    RESPONSES,
    band,
    method_label,
    points,
    tr,
)

COMMON = "HISTORICAL_COMMON_H20_TARGET"


def legend_below(fig, ax, language, *, columns=3):
    handles, labels = ax.get_legend_handles_labels()
    legend = fig.legend(handles, labels, loc="outside lower center", ncol=columns, frameon=False)
    for handle in legend.legend_handles:
        handle.set_alpha(1.0)


def quality_time(ax, tables, metric, language, *, legend=True):
    cnbi = tables["cost_cnbi"]
    cnbi = cnbi[cnbi.label == COMMON]
    grouped = cnbi.groupby("H", sort=True)
    xx = grouped.T_total.median()
    yy = grouped[metric].first()
    ax.plot(xx, yy, "o-", c=PALETTE["CNBI5"], ms=3, label="C-NBI standalone")
    for h, t in xx.items():
        if h == 5:
            ax.scatter(
                t,
                yy[h],
                marker="*",
                s=95,
                c=PALETTE["CNBI5"],
                edgecolor="#333333",
                lw=0.5,
                zorder=7,
            )
        ax.annotate(f"H{int(h)}", (t, yy[h]), xytext=(3, 5), textcoords="offset points", fontsize=6)
    for method in ("NSGA3", "MOEAD"):
        data = tables["cost_ea"]
        data = data[(data.label == COMMON) & (data.method == method)]
        group = data.groupby("generation", sort=True)
        time = group.T_total.median()
        q = group[metric].quantile([0.25, 0.5, 0.75]).unstack()
        ax.plot(
            time,
            q[0.5],
            color=PALETTE[method],
            marker=MARKERS[method],
            markersize=3,
            linestyle=LINESTYLES[method],
            label=method_label(method, language),
        )
        ax.fill_between(time.to_numpy(), q[0.25], q[0.75], color=PALETTE[method], alpha=0.13)
        tlow, thigh = group.T_total.quantile(0.25), group.T_total.quantile(0.75)
        ax.errorbar(
            time,
            q[0.5],
            xerr=[time - tlow, thigh - time],
            fmt="none",
            ecolor=PALETTE[method],
            lw=0.5,
        )
    ax.set(xscale="log", xlabel=tr("time", language), ylabel=metric)
    ax.xaxis.set_minor_formatter(NullFormatter())
    if legend:
        ax.legend(frameon=False, loc="best")


def curve(ax, tables, metric, language):
    data = tables["cardinality"]
    data = data[data.label == COMMON]
    for method in ("CNBI5", "NSGA3", "MOEAD", "VRF"):
        band(ax, data, "K", metric, method, language)
    ax.axvline(66, color="#555555", ls=":", lw=0.7)
    ax.set(xlabel=tr("cardinality", language), ylabel=metric)


def sensitivity(ax, tables, metric, language):
    data = tables["reference_replicates"]
    data = data[data.selection != "prefix"]
    grouped = data.groupby("r", sort=True)[metric]
    q = grouped.quantile([0.05, 0.5, 0.95]).unstack()
    ax.scatter(data.r, data[metric], s=2, c="#777777", alpha=0.07, linewidths=0, zorder=1)
    ax.fill_between(q.index.to_numpy(), q[0.05], q[0.95], color=PALETTE["CNBI5"], alpha=0.17)
    ax.plot(q.index, q[0.5], "o-", c=PALETTE["CNBI5"], ms=3)
    ax.set(
        xlabel=tr("runs", language),
        ylabel=metric.replace("_CNBI5", ""),
        xticks=[5, 10, 15, 20, 25, 30],
    )


def plot(identifier, tables, audit, language):
    fronts = tables["fronts"]
    if identifier in ("D1a", "D1b"):
        fig, axes = figure(height=4.2)
        ax = axes[0, 0]
        methods = (
            ("Reference", "CNBI5") if identifier == "D1a" else ("CNBI5", "NSGA3", "MOEAD", "VRF")
        )
        for method in methods:
            data = fronts[fronts.method == method]
            yy = data[[f"performance_{r}" for r in RESPONSES]].to_numpy()
            vertices = np.stack((np.broadcast_to(np.arange(8), yy.shape), yy), axis=2)
            collection = LineCollection(
                vertices,
                colors=PALETTE[method],
                linewidths=0.35 if method == "Reference" else 0.6,
                alpha=0.025 if method == "Reference" else 0.16,
                linestyles="-" if method == "Reference" else LINESTYLES[method],
                label=method_label(method, language),
            )
            ax.add_collection(collection)
        ax.set(
            xlim=(-0.1, 7.1),
            ylim=(-0.02, 1.02),
            xticks=range(8),
            xticklabels=[
                r + (" ↑" if d == "MAX" else " ↓")
                for r, d in zip(RESPONSES, DIRECTIONS, strict=True)
            ],
            ylabel=tr("performance", language),
        )
        handles = [
            Line2D(
                [],
                [],
                color=PALETTE[m],
                lw=1.3,
                ls="-" if m == "Reference" else LINESTYLES[m],
                label=method_label(m, language),
            )
            for m in methods
        ]
        fig.legend(handles=handles, loc="outside lower center", ncol=2, frameon=False)
        return fig, ["fronts"]
    if identifier == "D2":
        fig, axes = figure(2, 2, height=6)
        for ax, (r1, r2) in zip(axes.flat, PAIRS, strict=True):
            points(ax, fronts, r1, r2, language)
            ax.set(xlabel=response_axis(r1), ylabel=response_axis(r2))
        legend_below(fig, axes[0, 0], language, columns=3)
        return fig, ["fronts"]
    if identifier == "D3":
        fig, axes = figure(4, 4, height=9, width=9.6)
        ref = fronts[fronts.method == "Reference"]
        for row, method in enumerate(("CNBI5", "VRF", "NSGA3", "MOEAD")):
            data = fronts[fronts.method == method]
            for ax, (r1, r2) in zip(axes[row], PAIRS, strict=True):
                ax.scatter(ref[r1], ref[r2], s=1, c=PALETTE["Reference"], alpha=0.5, linewidths=0)
                ax.scatter(
                    data[r1],
                    data[r2],
                    s=6,
                    c=PALETTE[method],
                    marker=MARKERS[method],
                    alpha=0.6,
                    linewidths=0,
                )
                ax.set(xlabel=response_axis(r1), ylabel=response_axis(r2))
                if row == 0:
                    ax.set_title(f"{r1} × {r2}", fontsize=8)
            axes[row, 0].text(
                -0.36,
                0.5,
                method_label(method, language),
                transform=axes[row, 0].transAxes,
                rotation=90,
                ha="center",
                va="center",
                fontsize=8,
            )
        return fig, ["fronts"]
    if identifier == "D4":
        fig, axes = figure(height=4.5)
        ax = axes[0, 0]
        points(ax, fronts, "PC1", "PC2", language, size=10)
        ev = audit["pca"]["explained_variance_ratio"]
        ax.set(xlabel=f"PC1 ({ev[0]:.1%})", ylabel=f"PC2 ({ev[1]:.1%})")
        legend_below(fig, ax, language, columns=3)
        return fig, ["fronts"]
    if identifier == "D5":
        fig, axes = figure(height=3.8)
        ax = axes[0, 0]
        data = tables["contributions"]
        names = ["NSGA-III", "MOEA/D", "C-NBI H20 (hist.)", "VRF-NBI"]
        colors = [PALETTE[m] for m in ("NSGA3", "MOEAD", "CNBI5", "VRF")]
        ax.bar(names, data.exclusive_points, color=colors, width=0.58)
        for i, row in data.iterrows():
            ax.text(
                i,
                row.exclusive_points + 150,
                f"{int(row.exclusive_points):,}\n{row.exclusive_fraction:.1%}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        ax.set(ylabel=tr("count", language), ylim=(0, data.exclusive_points.max() * 1.22))
        ax.set_title(tr("historical", language), fontsize=8)
        return fig, ["contributions"]
    if identifier in ("E1", "E2", "E3"):
        metrics = {"E1": ["IGD"], "E2": ["HV"], "E3": ["Spacing", "Sparsity"]}[identifier]
        fig, axes = figure(1, len(metrics), height=3.5)
        for ax, metric in zip(axes.flat, metrics, strict=True):
            curve(ax, tables, metric, language)
        legend_below(fig, axes[0, 0], language, columns=2)
        return fig, ["cardinality"]
    if identifier == "F1":
        fig, axes = figure(1, 2, height=3.8)
        for ax, metric in zip(axes.flat, ("IGD", "HV"), strict=True):
            quality_time(ax, tables, metric, language, legend=False)
        legend_below(fig, axes[0, 0], language, columns=3)
        return fig, ["cost_cnbi", "cost_ea"]
    if identifier == "F2":
        fig, axes = figure(height=4)
        ax = axes[0, 0]
        values = []
        labels = []
        colors = []
        for h in (2, 4, 5, 10, 20):
            values.append(tables["timing_cnbi"].query("H==@h").T_total.to_numpy())
            labels.append(f"C-NBI\nH{h}")
            colors.append(PALETTE["CNBI5"])
        for family in ("NSGA3", "MOEAD"):
            values.append(tables["timing_" + family.lower()].T_total.to_numpy())
            labels.append(method_label(family, language))
            colors.append(PALETTE[family])
        for j, (v, color) in enumerate(zip(values, colors, strict=True)):
            spread = np.linspace(-0.08, 0.08, len(v)) if len(v) > 1 else np.zeros(1)
            ax.scatter(j + spread, v, c=color, s=14, alpha=0.7)
            q = np.quantile(v, [0.25, 0.5, 0.75])
            ax.plot([j - 0.2, j + 0.2], [q[1], q[1]], color="#111111", lw=1.2)
            if len(v) > 1:
                ax.plot([j, j], [q[0], q[2]], color="#111111", lw=2)
        ax.set(xticks=range(7), xticklabels=labels, yscale="log", ylabel=tr("time", language))
        ax.yaxis.set_minor_formatter(NullFormatter())
        return fig, ["timing_cnbi", "timing_nsga3", "timing_moead"]
    if identifier == "F3":
        fig, axes = figure(1, 2, height=3.4)
        data = tables["marginal_gain"]
        xx = [f"H{int(a)}→H{int(b)}" for a, b in zip(data.H_from, data.H_to, strict=True)]
        for ax, key, label in zip(
            axes.flat,
            ("IGD_reduction_per_second", "HV_gain_per_second"),
            ("gain_igd", "gain_hv"),
            strict=True,
        ):
            ax.bar(xx, data[key], color=PALETTE["CNBI5"], width=0.6)
            ax.set(ylabel=tr(label, language))
            ax.tick_params(axis="x", rotation=30)
        return fig, ["marginal_gain"]
    if identifier in ("G1", "G2", "G3"):
        metrics = {
            "G1": ["IGD_CNBI5"],
            "G2": ["GD_CNBI5"],
            "G3": ["reference_size", "HV_reference"],
        }[identifier]
        fig, axes = figure(1, len(metrics), height=3.5)
        for ax, metric in zip(axes.flat, metrics, strict=True):
            sensitivity(ax, tables, metric, language)
            if metric == "reference_size":
                ax.set_ylabel(tr("ref_size", language))
            if metric == "HV_reference":
                ax.set_ylabel(tr("ref_hv", language))
        return fig, ["reference_replicates"]
    if identifier == "G4":
        fig, axes = figure(1, 3, height=3.5, width=9)
        data = tables["reference_cardinality"]
        for ax, metric in zip(axes.flat, ("IGD_CNBI5", "GD_CNBI5", "HV"), strict=True):
            ax.plot(data.K_R, data[metric], "o-", ms=3, c=PALETTE["CNBI5"])
            ax.set(
                xscale="log", xlabel=tr("ref_size", language), ylabel=metric.replace("_CNBI5", "")
            )
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.set_xticks(data.K_R, [str(int(k)) for k in data.K_R], rotation=45)
        return fig, ["reference_cardinality"]
    if identifier == "G5":
        fig, axes = figure(1, 3, height=3.5, width=9)
        data = tables["reference_composition"].set_index("composition").loc[["N", "M", "NM", "NMV"]]
        for ax, metric in zip(axes.flat, ("IGD_CNBI5", "GD_CNBI5", "HV_reference"), strict=True):
            ax.plot(range(4), data[metric], "o", ms=5, c=PALETTE["CNBI5"])
            ax.set(
                xticks=range(4),
                xticklabels=["NSGA", "MOEA/D", "N+M", "N+M+V"],
                ylabel=metric.replace("_CNBI5", ""),
            )
            ax.tick_params(axis="x", rotation=30)
        return fig, ["reference_composition"]
    if identifier == "H1":
        fig, axes = figure(height=3.8)
        ax = axes[0, 0]
        data = tables["nearest_neighbor"]
        methods = ("CNBI5", "VRF", "NSGA3", "MOEAD")
        values = [data[data.method == m].distance.to_numpy() for m in methods]
        violins = ax.violinplot(
            values, positions=range(4), showmeans=False, showmedians=False, showextrema=False
        )
        for body, method in zip(violins["bodies"], methods, strict=True):
            body.set_facecolor(PALETTE[method])
            body.set_edgecolor("none")
            body.set_alpha(0.4)
        for j, v in enumerate(values):
            q = np.quantile(v, [0.25, 0.5, 0.75])
            ax.plot([j, j], [q[0], q[2]], color="#333333", lw=4)
            ax.plot(j, q[1], "o", color="white", ms=3)
        ax.set(
            xticks=range(4),
            xticklabels=[method_label(m, language) for m in methods],
            ylabel=tr("nn", language),
        )
        return fig, ["nearest_neighbor"]
    if identifier == "H2":
        fig, axes = figure(height=4.6)
        ax = axes[0, 0]
        data = tables["pca_density"]
        image = ax.scatter(
            data.PC1, data.PC2, c=data.log1p_density, s=3, cmap="cividis", linewidths=0
        )
        cnbi = fronts[fronts.method == "CNBI5"]
        ax.scatter(cnbi.PC1, cnbi.PC2, s=4, c=PALETTE["CNBI5"], alpha=0.7)
        ev = audit["pca"]["explained_variance_ratio"]
        ax.set(xlabel=f"PC1 ({ev[0]:.1%})", ylabel=f"PC2 ({ev[1]:.1%})")
        fig.colorbar(image, ax=ax, label=tr("density", language))
        return fig, ["pca_density", "fronts"]
    if identifier == "H3":
        fig, axes = figure(1, 3, height=3.2)
        radius = audit["coding"]["sphere_radius"]
        for ax, (i, j) in zip(axes.flat, DECISION_PAIRS, strict=True):
            points(ax, fronts, f"x{i + 1}", f"x{j + 1}", language, reference=False, size=5)
            ax.add_patch(Circle((0, 0), radius, fill=False, ls="--", lw=0.7, color="#777777"))
            ax.set(
                xlabel=FACTORS[i],
                ylabel=FACTORS[j],
                aspect="equal",
                xlim=(-1.9, 1.9),
                ylim=(-1.9, 1.9),
            )
        legend_below(fig, axes[0, 0], language, columns=2)
        return fig, ["fronts"]
    if identifier == "I1":
        fig, axes = figure(height=8, width=7.2)
        ax = axes[0, 0]
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis("off")
        data = tables["workflow"]
        centers = []
        for i, row in data.iterrows():
            column = i // 7
            position = i % 7
            x = 0.23 + 0.54 * column
            y = 0.94 - position * 0.14
            centers.append((x, y))
            box = FancyBboxPatch(
                (x - 0.2, y - 0.043),
                0.4,
                0.086,
                boxstyle="round,pad=.01",
                edgecolor="#777777",
                facecolor="#FAFAFA",
                lw=0.75,
            )
            ax.add_patch(box)
            ax.text(
                x,
                y,
                textwrap.fill(f"{i + 1}. " + row[language], 31),
                ha="center",
                va="center",
                fontsize=8,
            )
        for i in range(13):
            start = np.array(centers[i])
            end = np.array(centers[i + 1])
            if i == 6:
                ax.plot(
                    [start[0] + 0.21, 0.5, 0.5],
                    [start[1], start[1], end[1]],
                    color="#555555",
                    lw=0.8,
                )
                ax.annotate(
                    "",
                    end - np.array([0.21, 0]),
                    xytext=(0.5, end[1]),
                    arrowprops=dict(arrowstyle="->", lw=0.8, color="#555555"),
                )
            else:
                ax.annotate(
                    "",
                    end + np.array([0, 0.055]),
                    xytext=start - np.array([0, 0.055]),
                    arrowprops=dict(arrowstyle="->", lw=0.8, color="#555555"),
                )
        return fig, ["workflow"]
    if identifier == "J1":
        fig, axes = figure(2, 2, height=6.8, width=9)
        heatmap(axes[0, 0], tables["payoff"], "loss", language, annotate=False)
        subset = audit["selected_local_subsets"][2]
        local_panel(axes[0, 1], tables["local_geometry"], subset, audit, language)
        points(axes[1, 0], fronts, "T", "Kp", language, size=5)
        axes[1, 0].set(xlabel=response_axis("T"), ylabel=response_axis("Kp"))
        quality_time(axes[1, 1], tables, "IGD", language, legend=False)
        labels = (
            ("A — Payoff", "B — CHIM / NBI", "C — Fronteira empírica", "D — Qualidade × tempo")
            if language == "pt"
            else ("A — Payoff", "B — CHIM / NBI", "C — Empirical front", "D — Quality × time")
        )
        for ax, label in zip(axes.flat, labels, strict=True):
            ax.set_title(label, fontsize=9)
        legend_below(fig, axes[1, 0], language, columns=3)
        return fig, ["payoff", "local_geometry", "fronts", "cost_cnbi", "cost_ea"]
    raise KeyError(identifier)
