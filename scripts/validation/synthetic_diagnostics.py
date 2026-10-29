"""Exactly four English scientific diagnostics; no multiobjective benchmark data."""

from pathlib import Path

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from cnbi_v2.synthetic.calibration import CalibratedScenario
from cnbi_v2.synthetic.correlation import summaries


def figures(results: tuple[CalibratedScenario, ...]) -> dict[str, Figure]:
    ids = [r.scenario.scenario_id for r in results]
    targets = np.array([r.scenario.rho_target for r in results])
    cal = np.array([summaries(r.calibration_matrix)[0] for r in results])
    val = np.array([summaries(r.validation_matrix)[0] for r in results])
    signed = np.array([summaries(r.validation_matrix)[1] for r in results])
    plots = {}

    fig = Figure(figsize=(6.8, 4.4), layout="constrained")
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    ax.plot([0.15, 0.95], [0.15, 0.95], color="0.55", lw=0.8, label="Target")
    for nx, marker, color in ((2, "o", "#0072B2"), (3, "s", "#009E73"), (5, "^", "#CC3311")):
        mask = np.array([r.scenario.nx == nx for r in results])
        ax.scatter(
            targets[mask],
            val[mask],
            marker=marker,
            facecolors="none",
            edgecolors=color,
            s=48,
            label=f"Independent validation, nx={nx}",
        )
    ax.set(
        xlabel="Target mean absolute Pearson correlation",
        ylabel="Realized mean absolute Pearson correlation",
        xlim=(0.15, 0.95),
        ylim=(0.15, 0.95),
    )
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    plots["target_vs_realized"] = fig

    fig = Figure(figsize=(8, 8), layout="constrained")
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    y = np.arange(len(results))
    ax.barh(y - 0.15, abs(cal - targets), height=0.28, color="#0072B2", label="Calibration")
    ax.barh(
        y + 0.15, abs(val - targets), height=0.28, color="#E69F00", label="Independent validation"
    )
    ax.axvline(0.05, color="#CC3311", ls="--", lw=1, label="Acceptance tolerance 0.05")
    ax.set(yticks=y, yticklabels=ids, xlabel="Absolute error from target", xlim=(0, 0.055))
    ax.invert_yaxis()
    ax.tick_params(axis="y", labelsize=7)
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    plots["calibration_errors"] = fig

    fig = Figure(figsize=(6.8, 4.4), layout="constrained")
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    ax.hist(signed, bins=np.linspace(-1, 1, 17), color="#0072B2", edgecolor="white")
    ax.set(
        xlabel="Observed mean signed Pearson correlation",
        ylabel="Number of structural scenarios",
        xlim=(-1, 1),
        title="Observed covariate; no signed-correlation target",
    )
    plots["signed_correlation_distribution"] = fig

    fig = Figure(figsize=(11, 3.8), layout="constrained")
    FigureCanvasAgg(fig)
    axes = fig.subplots(1, 3)
    # Fixed first/middle/last factorial cells, without inspecting quality/sign.
    for ax, index in zip(axes, (0, len(results) // 2, len(results) - 1), strict=True):
        result = results[index]
        r = result.validation_matrix
        m = result.scenario.m
        image = ax.pcolormesh(
            np.arange(m + 1) - 0.5,
            np.arange(m + 1) - 0.5,
            r,
            cmap="RdBu_r",
            vmin=-1,
            vmax=1,
            rasterized=False,
        )
        ax.set(
            aspect="equal",
            ylim=(m - 0.5, -0.5),
            title=result.scenario.scenario_id,
            xticks=range(m),
            yticks=range(m),
            xticklabels=range(1, m + 1),
            yticklabels=range(1, m + 1),
            xlabel="Response",
            ylabel="Response",
        )
        ax.tick_params(labelsize=7)
        for i in range(m):
            for j in range(m):
                rgba = image.cmap(image.norm(r[i, j]))
                light = np.dot(rgba[:3], [0.2126, 0.7152, 0.0722])
                ax.text(
                    j,
                    i,
                    f"{r[i, j]:+.1f}",
                    ha="center",
                    va="center",
                    fontsize=5,
                    color="white" if light < 0.48 else "#111111",
                )
    fig.colorbar(image, ax=list(axes), label="Pearson correlation")
    plots["representative_correlation_matrices"] = fig
    for figure in plots.values():
        for ax in figure.axes:
            ax.grid(False)
            ax.spines[["top", "right"]].set_visible(False)
            for collection in ax.collections:
                collection.set_rasterized(False)
    return plots


def export_diagnostics(results: tuple[CalibratedScenario, ...], output: Path) -> None:
    from matplotlib import rc_context

    output.mkdir(parents=True, exist_ok=True)
    with rc_context({"font.family": "DejaVu Sans", "font.size": 9, "axes.grid": False}):
        for identifier, fig in figures(results).items():
            fig.savefig(
                output / (identifier + ".png"),
                dpi=600,
                bbox_inches="tight",
                metadata={"Software": "C-NBI v2 synthetic structural diagnostics"},
            )
            fig.savefig(
                output / (identifier + ".pdf"),
                bbox_inches="tight",
                metadata={"CreationDate": None, "ModDate": None},
            )
            fig.clear()
