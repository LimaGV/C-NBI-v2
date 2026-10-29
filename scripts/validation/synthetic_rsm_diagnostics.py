"""Six English diagnostics, fixed representatives, no grid or quality selection."""

from pathlib import Path
from statistics import NormalDist

import numpy as np
from matplotlib import rc_context
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from cnbi_v2.synthetic.rsm.rsm_generation import true_coefficients

COLORS = ("#0072B2", "#009E73", "#CC3311")


def new_figure(width=9, height=3.8):
    fig = Figure(figsize=(width, height), layout="constrained")
    FigureCanvasAgg(fig)
    return fig


def figures(instances, anchors, samples, diagnostics, external):
    plots = {}
    fig = new_figure(10, 3.6)
    for ax, metric, label in zip(
        fig.subplots(1, 3),
        ("r_squared", "adjusted_r_squared", "predicted_r_squared"),
        ("Training $R^2$", "Adjusted $R^2$", "LOOCV predicted $R^2$"),
        strict=True,
    ):
        ax.boxplot(
            [[r[metric] for r in diagnostics if r["nx"] == nx] for nx in (2, 3, 5)],
            tick_labels=["2", "3", "5"],
            showfliers=True,
            medianprops=dict(color=COLORS[0]),
        )
        ax.set(xlabel="Number of factors", ylabel=label)
    plots["r_squared_distributions"] = fig

    fig = new_figure(10, 3.6)
    for ax, nx in zip(fig.subplots(1, 3), (2, 3, 5), strict=True):
        ax.boxplot(
            [
                [r["rmse"] for r in external if r["nx"] == nx and r["rho_target"] == rho]
                for rho in (0.25, 0.60, 0.85)
            ],
            tick_labels=["0.25", "0.60", "0.85"],
            medianprops=dict(color=COLORS[0]),
        )
        ax.set(
            xlabel="Structural absolute-correlation target",
            ylabel="External RMSE",
            title=f"{nx} factors",
        )
        ax.xaxis.label.set_fontsize(8)
    fig.suptitle("All excess levels and replicas", fontsize=9)
    plots["external_rmse"] = fig

    fig = new_figure(6.4, 4.8)
    ax = fig.subplots()
    for nx, color in zip((2, 3, 5), COLORS, strict=True):
        group = [i for i in instances if i.scenario.nx == nx]
        true = np.concatenate(
            [true_coefficients(anchors[i.scenario.scenario_id]).ravel() for i in group]
        )
        estimated = np.concatenate([i.fit.coefficients.ravel() for i in group])
        ax.scatter(
            true, estimated, s=5, alpha=0.25, color=color, label=f"{nx} factors", linewidths=0
        )
    limits = ax.get_xlim()
    ax.plot(limits, limits, color=".35", lw=0.8, label="Identity")
    ax.set(xlabel="True coefficient", ylabel="Estimated coefficient")
    ax.legend(frameon=False, fontsize=8)
    plots["estimated_vs_true_coefficients"] = fig

    fig = new_figure(10, 3.6)
    for ax, nx, color in zip(fig.subplots(1, 3), (2, 3, 5), COLORS, strict=True):
        sid = f"nx{nx}_delta3_rho060"
        item = next(i for i in instances if i.scenario.scenario_id == sid and i.replica_id == 1)
        sample = samples[sid]
        # Fixed every-sixteenth Sobol row; never chosen by residual or quality.
        truth = sample.truth[::16, 0]
        predicted = item.fit.predict(sample.points[::16])[:, 0]
        ax.scatter(truth, predicted, s=8, color=color, alpha=0.6, linewidths=0)
        lo, hi = min(truth.min(), predicted.min()), max(truth.max(), predicted.max())
        ax.plot([lo, hi], [lo, hi], color=".35", lw=0.8)
        ax.set(
            xlabel="True response",
            ylabel="RSM prediction",
            title=f"{nx} factors, excess 3, target 0.60\nReplica 1, response 1",
        )
    plots["true_vs_rsm_predictions"] = fig

    residual = np.concatenate(
        [(i.fit.residuals / np.sqrt(i.sigma_squared)).ravel() for i in instances]
    )
    fitted = np.concatenate(
        [(i.fit.fitted_values / np.sqrt(i.sigma_squared)).ravel() for i in instances]
    )
    fig = new_figure(10, 4)
    left, right = fig.subplots(1, 2)
    left.scatter(fitted[::17], residual[::17], s=4, color=COLORS[0], alpha=0.35, linewidths=0)
    left.axhline(0, color=".35", lw=0.8)
    left.set(xlabel="Fitted response / known noise SD", ylabel="Residual / known noise SD")
    ordered = np.sort(residual)
    # Fixed rank stride for a lean vector export; all residuals determine ranks.
    ranks = np.arange(0, len(ordered), 17)
    quantiles = np.array([NormalDist().inv_cdf((k + 0.5) / len(ordered)) for k in ranks])
    right.scatter(quantiles, ordered[ranks], s=5, color=COLORS[1], linewidths=0)
    right.plot([-4, 4], [-4, 4], color=".35", lw=0.8, label="Standard normal identity")
    right.set(
        xlabel="Standard normal quantile",
        ylabel="Residual / known noise SD",
        title="Pooled residuals; not studentized",
    )
    right.legend(frameon=False, fontsize=8)
    plots["residual_diagnostics"] = fig

    fig = new_figure(9, 3.8)
    left, right = fig.subplots(1, 2)
    for nx, color in zip((2, 3, 5), COLORS, strict=True):
        group = [i for i in instances if i.scenario.nx == nx]
        expected = np.concatenate([i.sigma_squared for i in group])
        realized = np.concatenate([np.var(i.noise, axis=0, ddof=1) for i in group])
        left.scatter(
            expected, realized, s=7, color=color, alpha=0.4, label=f"{nx} factors", linewidths=0
        )
    limits = left.get_xlim()
    left.plot(limits, limits, color=".35", lw=0.8)
    left.set(xlabel="Expected noise variance", ylabel="Realized sample noise variance")
    left.legend(frameon=False, fontsize=8)
    right.boxplot(
        [
            np.concatenate(
                [
                    19 * i.sigma_squared / (19 * i.sigma_squared + np.var(i.noise, axis=0, ddof=1))
                    for i in instances
                    if i.scenario.nx == nx
                ]
            )
            for nx in (2, 3, 5)
        ],
        tick_labels=["2", "3", "5"],
        medianprops=dict(color=COLORS[0]),
    )
    right.axhline(0.95, color=".35", lw=0.8, ls="--", label="Expected signal fraction 0.95")
    right.set(
        xlabel="Number of factors",
        ylabel="$S_f^2/(S_f^2+s^2_{noise})$",
        title="Realized variance ratio; not training $R^2$",
    )
    right.legend(frameon=False, fontsize=8)
    plots["signal_and_noise_variance"] = fig
    for fig in plots.values():
        for ax in fig.axes:
            ax.grid(False)
            ax.spines[["top", "right"]].set_visible(False)
    return plots


def save_figures(directory: Path, instances, anchors, samples, diagnostics, external):
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
        for name, fig in figures(instances, anchors, samples, diagnostics, external).items():
            fig.savefig(target / (name + ".png"), dpi=600)
            fig.savefig(target / (name + ".pdf"))
