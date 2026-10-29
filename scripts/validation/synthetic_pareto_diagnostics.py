"""Six scientific diagnostics; no algorithm outputs or decorative projections."""

from pathlib import Path

import numpy as np
from matplotlib import rc_context
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from cnbi_v2.benchmark.metrics import nearest_distances

COLORS = ("#0072B2", "#009E73", "#CC3311")


def figure(width=9, height=4):
    fig = Figure(figsize=(width, height), layout="constrained")
    FigureCanvasAgg(fig)
    return fig


def figures(references, diagnostics, hv_rows, ideal_nadir):
    plots = {}
    fig = figure(9, 4.2)
    ax = fig.add_subplot(121)
    r = next(r for r in references if r.scenario.scenario_id == "nx2_delta3_rho060")
    a, x = r.geometry.anchors, r.decisions[:5000]
    ax.scatter(
        x[:, 0], x[:, 1], s=0.8, color=COLORS[0], alpha=0.4, label="Reference (5000)", linewidths=0
    )
    for facet in r.geometry.facets:
        edge = a[facet]
        ax.plot(edge[:, 0], edge[:, 1], color=".3", lw=0.7)
    ax.scatter(
        a[:, 0], a[:, 1], s=24, facecolors="none", edgecolors=COLORS[2], label="Frozen anchors"
    )
    ax.set(xlabel="$x_1$", ylabel="$x_2$", title="2 factors, excess 3, target 0.60")
    ax.set_aspect("equal", adjustable="datalim")
    ax.legend(frameon=False, fontsize=7)
    ax = fig.add_subplot(122, projection="3d", proj_type="ortho")
    r = next(r for r in references if r.scenario.scenario_id == "nx3_delta3_rho060")
    a, x = r.geometry.anchors, r.decisions[:5000:4]
    ax.add_collection3d(
        Poly3DCollection(
            a[r.geometry.facets], facecolors=".9", edgecolors=".4", linewidths=0.35, alpha=0.12
        )
    )
    ax.scatter(
        x[:, 0],
        x[:, 1],
        x[:, 2],
        s=2,
        color=COLORS[1],
        alpha=0.35,
        label="Reference (1 in 4 shown)",
    )
    ax.scatter(a[:, 0], a[:, 1], a[:, 2], s=20, color=COLORS[2], label="Frozen anchors")
    ax.set(xlabel="$x_1$", ylabel="$x_2$", zlabel="$x_3$", title="3 factors, excess 3, target 0.60")
    ax.set_box_aspect(np.ptp(a, axis=0))
    ax.view_init(elev=22, azim=-55)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    plots["pareto_decision_geometry"] = fig

    fig = figure(10, 3.5)
    for ax, nx, color in zip(fig.subplots(1, 3), (2, 3, 5), COLORS, strict=True):
        groups = [
            [
                float(row["probe_rms_coordinate_max"])
                for row in diagnostics
                if row["nx"] == nx and row["count"] == n
            ]
            for n in (2500, 5000, 10000)
        ]
        ax.boxplot(groups, tick_labels=["2500", "5000", "10000"], medianprops=dict(color=color))
        ax.axhline(0.05, color=".4", ls="--", lw=0.8)
        ax.set(
            xlabel="Reference cardinality",
            ylabel="Volume-probe maximum / $\\sqrt{m}$",
            title=f"{nx} factors; nine structural cells",
        )
    fig.suptitle("Independent coverage; dashed line: proposed finite-audit budget", fontsize=9)
    plots["reference_coverage"] = fig

    fig = figure(7, 4)
    ax = fig.subplots()
    groups = [
        np.concatenate(
            [
                nearest_distances(r.normalized[:5000]) / np.sqrt(r.scenario.m)
                for r in references
                if r.scenario.nx == nx
            ]
        )
        for nx in (2, 3, 5)
    ]
    ax.boxplot(
        groups,
        tick_labels=["2", "3", "5"],
        showfliers=False,
        whis=(1, 99),
        medianprops=dict(color=COLORS[0]),
    )
    ax.set(
        xlabel="Number of factors",
        ylabel="Nearest-neighbor distance / $\\sqrt{m}$",
        title="Primary references; whiskers: 1st–99th percentiles",
    )
    plots["reference_nearest_neighbors"] = fig

    fig = figure(9, 3.8)
    left, right = fig.subplots(1, 2)
    minima = np.array([float(row["sample_min"]) / float(row["denominator"]) for row in ideal_nadir])
    maxima = np.array([float(row["sample_max"]) / float(row["denominator"]) for row in ideal_nadir])
    ids = np.arange(1, len(minima) + 1)
    left.scatter(ids, minima, s=6, color=COLORS[0], label="Minimum")
    left.scatter(ids, maxima, s=6, color=COLORS[1], label="Maximum")
    left.axhline(0, color=".4", lw=0.6)
    left.axhline(1, color=".4", lw=0.6)
    left.set(
        xlabel="Canonical scenario–response index",
        ylabel="Normalized reference extrema",
        ylim=(-0.05, 1.05),
    )
    left.legend(frameon=False, fontsize=8)
    right.scatter(ids, [float(row["denominator"]) for row in ideal_nadir], s=7, color=COLORS[0])
    right.set(
        xlabel="Canonical scenario–response index", ylabel="Analytic nadir − ideal", yscale="log"
    )
    plots["ideal_nadir_normalization"] = fig

    fig = figure(10, 4)
    left, right = fig.subplots(1, 2)
    for nx, color in zip((2, 3, 5), COLORS, strict=True):
        sid = f"nx{nx}_delta3_rho060"
        rows = [
            r
            for r in hv_rows
            if r["case_type"] == "pareto_reference"
            and r["scenario_id"] == sid
            and r["n_reference"] == 5000
        ]
        left.errorbar(
            [r["power"] for r in rows],
            [r["HV_QMC"] for r in rows],
            yerr=[r["HV_QMC_SE"] for r in rows],
            fmt="o-",
            ms=3,
            color=color,
            label=f"{nx} factors",
        )
    powers = sorted({r["power"] for r in hv_rows})
    main = [r for r in hv_rows if r["case_type"] == "pareto_reference" and r["n_reference"] == 5000]
    relative = [
        max(
            (
                float(r["relative_se"])
                for r in main
                if r["power"] == p and r["relative_se"] is not None
            ),
            default=np.nan,
        )
        for p in powers
    ]
    change = [
        max(
            (
                float(r["relative_change_previous"])
                for r in main
                if r["power"] == p and r["relative_change_previous"] is not None
            ),
            default=np.nan,
        )
        for p in powers
    ]
    right.plot(powers, relative, "o-", color=COLORS[0], label="Largest relative SE")
    right.plot(powers, change, "s-", color=COLORS[1], label="Largest doubling change")
    right.axhline(0.02, color=".4", ls="--", lw=0.8, label="Predeclared 2% budget")
    left.set(
        xlabel="Sobol sample exponent (per scramble)",
        ylabel="HV estimate ± scramble SE",
        xticks=powers,
        title="Predefined cells: excess 3, target 0.60",
    )
    right.set(
        xlabel="Sobol sample exponent (per scramble)",
        ylabel="Relative quadrature diagnostic",
        xticks=powers,
        title="All 27 primary references",
    )
    left.legend(frameon=False, fontsize=8)
    right.legend(frameon=False, fontsize=8)
    plots["hypervolume_precision"] = fig

    fig = figure(7, 4)
    ax = fig.subplots()
    sizes = np.array([2500, 5000, 10000])
    for nx, color in zip((2, 3, 5), COLORS, strict=True):
        groups = [
            np.array(
                [
                    float(r["hausdorff_rms_coordinate"])
                    for r in diagnostics
                    if r["nx"] == nx and r["count"] == n
                ]
            )
            for n in sizes
        ]
        ax.plot(sizes, [g.mean() for g in groups], "o-", color=color, label=f"{nx} factors")
        ax.fill_between(
            sizes, [g.min() for g in groups], [g.max() for g in groups], color=color, alpha=0.10
        )
    ax.set(
        xlabel="Reference cardinality",
        ylabel="Discrete Hausdorff to R10000 / $\\sqrt{m}$",
        xticks=sizes,
        title="Nested sensitivity; bands show scenario ranges",
    )
    ax.legend(frameon=False, fontsize=8)
    plots["reference_cardinality_sensitivity"] = fig
    for fig in plots.values():
        for ax in fig.axes:
            ax.grid(False)
            if hasattr(ax, "zaxis"):
                ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
            else:
                ax.spines[["top", "right"]].set_visible(False)
    return plots


def save_figures(directory: Path, references, diagnostics, hv_rows, ideal_nadir):
    target = directory / "figures"
    target.mkdir()
    with rc_context(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.grid": False,
            "pdf.fonttype": 42,
            "axes.linewidth": 0.7,
        }
    ):
        for name, fig in figures(references, diagnostics, hv_rows, ideal_nadir).items():
            fig.savefig(target / (name + ".png"), dpi=600)
            fig.savefig(target / (name + ".pdf"))
