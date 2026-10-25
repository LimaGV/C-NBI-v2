"""Problem, frozen geometry and Monte Carlo presentation panels A–C."""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse, Polygon

from .style import FACTORS, PALETTE, RESPONSES, TERMS, tr

PAIRS = (("T", "Kp"), ("Ra", "ROI"), ("WR", "OEE"), ("MTTF", "Rt"))
DECISION_PAIRS = ((0, 1), (0, 2), (1, 2))
UNITS = {"T": "min", "MTTF": "min", "WR": "mm/min", "Ra": "µm", "Rt": "µm", "Kp": "USD"}
OFFSETS = ((-30, 15), (-42, -22), (12, -7), (-23, 18), (10, 26), (10, -18), (-32, 5), (8, 7))


def response_axis(response):
    return f"{response} ({UNITS[response]})" if response in UNITS else response


def figure(rows=1, cols=1, *, height=None, width=7.2):
    return plt.subplots(
        rows, cols, figsize=(width, height or 2.7 * rows), layout="constrained", squeeze=False
    )


def label_anchors(ax, xx, yy, labels=RESPONSES, *, perimeter=False):
    if perimeter:
        xx, yy = np.asarray(xx), np.asarray(yy)
        order = np.argsort(xx, kind="stable")
        cut = len(order) // 2
        lo, hi = ax.get_ylim()
        relative = (yy - lo) / max(hi - lo, np.finfo(float).eps)
        for side, indices in enumerate((order[:cut], order[cut:])):
            indices = indices[np.argsort(yy[indices], kind="stable")]
            slots = (
                np.linspace(0.12, 0.88, len(indices))
                if len(indices) > 1
                else np.clip(relative[indices], 0.12, 0.88)
            )
            for index, slot in zip(indices, slots, strict=True):
                near = relative[np.abs(xx - xx[index]) <= 0.15 * max(np.ptp(xx), 1e-12)]
                if len(near) and np.min(abs(near - slot)) < 0.07:
                    slot = np.clip(slot + (0.07 if slot > 0.5 else -0.07), 0.06, 0.94)
                ax.annotate(
                    str(list(labels)[index]) + "*",
                    (xx[index], yy[index]),
                    xytext=(0.015 if side == 0 else 0.985, slot),
                    textcoords="axes fraction",
                    ha="left" if side == 0 else "right",
                    va="center",
                    fontsize=6.5,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=0.3),
                    arrowprops=dict(arrowstyle="-", lw=0.4, color="#666666"),
                )
        return
    for i, (x, y, label) in enumerate(zip(xx, yy, labels, strict=True)):
        ax.annotate(
            label + "*",
            (x, y),
            xytext=OFFSETS[i % 8],
            textcoords="offset points",
            fontsize=6.5,
            arrowprops=dict(arrowstyle="-", lw=0.4, color="#666666"),
        )


def heatmap(ax, frame, value, language, *, cmap="cividis", annotate=True, symmetric=False):
    data = frame.pivot(index="anchor", columns="response", values=value).reindex(
        index=RESPONSES, columns=RESPONSES
    )
    matrix = data.to_numpy()
    lim = np.max(abs(matrix)) if symmetric else None
    image = ax.pcolormesh(
        np.arange(9) - 0.5,
        np.arange(9) - 0.5,
        matrix,
        cmap=cmap,
        vmin=-lim if symmetric else None,
        vmax=lim,
        edgecolors="none",
        rasterized=False,
    )
    ax.set(xlim=(-0.5, 7.5), ylim=(7.5, -0.5), aspect="equal")
    ax.set(
        xticks=range(8),
        yticks=range(8),
        xticklabels=RESPONSES,
        yticklabels=[r + "*" for r in RESPONSES],
        xlabel=tr("response", language),
        ylabel=tr("individual", language),
    )
    ax.tick_params(axis="x", rotation=35)
    if annotate:
        norm = image.norm
        for i in range(8):
            for j in range(8):
                rgba = image.cmap(norm(matrix[i, j]))
                luminance = np.dot(rgba[:3], [0.2126, 0.7152, 0.0722])
                color = "white" if luminance < 0.48 else "#111111"
                display = 0.0 if abs(matrix[i, j]) < 0.005 else matrix[i, j]
                ax.text(j, i, f"{display:.2f}", ha="center", va="center", fontsize=7, color=color)
    return image


def ellipse(ax, row, *, color=None):
    color = color or PALETTE["Anchor"]
    ax.add_patch(
        Ellipse(
            (row.center_x, row.center_y),
            row.width,
            row.height,
            angle=row.angle,
            fill=False,
            edgecolor=color,
            lw=1.0,
            zorder=5,
        )
    )
    ax.plot(row.center_x, row.center_y, "+", color=color, ms=5, zorder=6)


def local_panel(ax, table, subset, audit, language, *, mc=None, regions=None, normal=True):
    local = table[table.subset == subset]
    anchors = local[local.kind == "anchor"]
    xy = anchors[["u", "v"]].to_numpy()
    ax.add_patch(Polygon(xy, closed=len(xy) > 2, fill=False, edgecolor=PALETTE["Ink"], lw=1.2))
    weights = local[local.kind == "weight"]
    ax.scatter(weights.u, weights.v, s=18, c=PALETTE["Ink"], marker="x", lw=0.6, zorder=3)
    solutions = local[local.kind == "solution"]
    ax.scatter(solutions.u, solutions.v, s=15, c=PALETTE["CNBI5"], marker="o", zorder=4)
    ax.scatter(anchors.u, anchors.v, c=PALETTE["Anchor"], marker="*", s=55, zorder=7)
    label_anchors(ax, anchors.u, anchors.v, anchors.response, perimeter=True)
    if mc is not None:
        points = mc[mc.subset == subset]
        ax.scatter(points.u, points.v, s=1, c=PALETTE["Anchor"], alpha=0.05, linewidths=0, zorder=1)
        for _, row in regions[(regions.figure == "C5") & (regions.projection == subset)].iterrows():
            ellipse(ax, row)
    if int(local.k.iloc[0]) == 2:
        normal = np.array(audit["local_coordinates"][subset]["normal"])
        center = xy.mean(axis=0)
        if normal is not None:
            ax.annotate(
                "n",
                center + 0.2 * normal,
                xytext=center,
                arrowprops=dict(arrowstyle="->", color=PALETTE["Ink"]),
                fontsize=8,
            )
        names = [RESPONSES[j] for j in audit["local_coordinates"][subset]["indices"]]
        ax.set(xlabel=f"z({names[0]})", ylabel=f"z({names[1]})")
    else:
        ax.set(xlabel=tr("intrinsic1", language), ylabel=tr("intrinsic2", language))
        if normal:
            ax.text(
                0.02,
                0.98,
                r"$\odot\,n$" + "\n" + tr("normal_out", language),
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=6.3,
                color=PALETTE["Ink"],
            )
    ax.set_title(subset, fontsize=8)
    ax.margins(0.22)


def forest(ax, data, response, language):
    subset = data[data.response == response].sort_values("term_index")
    yy = np.arange(10)
    ax.errorbar(
        subset.beta,
        yy,
        xerr=[subset.beta - subset.lower, subset.upper - subset.beta],
        fmt="o",
        color=PALETTE["Ink"],
        ms=3,
        capsize=2,
        lw=1,
    )
    ax.axvline(0, color="#777777", ls=":", lw=0.7)
    ax.set(yticks=yy, yticklabels=TERMS, title=response, xlabel=tr("estimate", language))
    ax.invert_yaxis()


def plot(identifier, tables, audit, language):
    if identifier == "A1":
        fig, axes = figure(4, 2, height=10)
        data = tables["contours"]
        size = int(np.sqrt(len(data)))
        xx, yy = data.x1.to_numpy().reshape(size, size), data.x2.to_numpy().reshape(size, size)
        for i, (ax, response) in enumerate(zip(axes.flat, RESPONSES, strict=True)):
            zz = data[response].to_numpy().reshape(size, size)
            filled = ax.contourf(xx, yy, zz, levels=14, cmap="cividis")
            lines = ax.contour(xx, yy, zz, levels=5, colors="#333333", linewidths=0.4, alpha=0.7)
            ax.clabel(lines, fontsize=5.7, inline=True, fmt="%.3g")
            ax.add_patch(
                Circle(
                    (0, 0),
                    audit["coding"]["sphere_radius"],
                    fill=False,
                    ls="--",
                    lw=0.8,
                    color="#333333",
                )
            )
            ax.plot(0, 0, "+", ms=5, color="#111111")
            ax.set(
                xlabel=FACTORS[0],
                ylabel=FACTORS[1],
                title=f"({chr(97 + i)}) {response_axis(response)}",
                aspect="equal",
            )
            fig.colorbar(filled, ax=ax, pad=0.025, shrink=0.78, label=tr("level", language))
        return fig, ["contours"]
    if identifier in ("A2", "A3"):
        fig, axes = figure(height=5.5)
        source, value = ("payoff", "loss") if identifier == "A2" else ("conflict", "asymmetry")
        image = heatmap(
            axes[0, 0],
            tables[source],
            value,
            language,
            cmap="cividis" if identifier == "A2" else "RdBu_r",
            symmetric=identifier == "A3",
        )
        fig.colorbar(
            image,
            ax=axes[0, 0],
            shrink=0.85,
            label=tr("loss" if identifier == "A2" else "contrast", language),
        )
        return fig, [source]
    if identifier == "B1":
        fig, axes = figure(1, 3, height=3)
        data = tables["anchors"]
        radius = audit["coding"]["sphere_radius"]
        for ax, (i, j) in zip(axes.flat, DECISION_PAIRS, strict=True):
            ax.add_patch(Circle((0, 0), radius, fill=False, ls="--", lw=0.7, color="#555555"))
            ax.scatter(
                data[f"x{i + 1}"], data[f"x{j + 1}"], marker="*", s=40, color=PALETTE["Anchor"]
            )
            label_anchors(ax, data[f"x{i + 1}"], data[f"x{j + 1}"], perimeter=True)
            ax.set(
                xlabel=FACTORS[i],
                ylabel=FACTORS[j],
                xlim=(-radius * 1.15, radius * 1.15),
                ylim=(-radius * 1.15, radius * 1.15),
                aspect="equal",
            )
        return fig, ["anchors"]
    if identifier == "B2":
        fig, axes = figure(height=4.2)
        ax = axes[0, 0]
        data = tables["anchor_pca"]
        ax.scatter(data.PC1, data.PC2, s=60, c=PALETTE["Anchor"], marker="*")
        label_anchors(ax, data.PC1, data.PC2)
        ev = audit["pca"]["explained_variance_ratio"]
        ax.set(xlabel=f"PC1 ({ev[0]:.1%})", ylabel=f"PC2 ({ev[1]:.1%})")
        ax.margins(0.2)
        return fig, ["anchor_pca"]
    if identifier == "B3":
        data = tables["subsets"]
        fig = plt.figure(figsize=(7.2, 8.8), layout="constrained")
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 6])
        top = fig.add_subplot(gs[0])
        ax = fig.add_subplot(gs[1])
        mat = data[list(RESPONSES)].to_numpy()
        ax.pcolormesh(
            np.arange(9) - 0.5,
            np.arange(38) - 0.5,
            mat,
            cmap="Greys",
            vmin=0,
            vmax=1,
            edgecolors="none",
            rasterized=False,
        )
        ax.set(xlim=(-0.5, 7.5), ylim=(36.5, -0.5), aspect="auto")
        ax.set(
            xticks=range(8),
            xticklabels=RESPONSES,
            yticks=range(37),
            yticklabels=data.subset,
            xlabel=tr("response", language),
            ylabel=tr("subset", language),
        )
        ax.tick_params(axis="y", labelsize=6.5)
        ax.axhline(18.5, color=PALETTE["Anchor"], lw=1)
        top.bar(np.arange(8), mat.sum(axis=0), color=PALETTE["Ink"], width=0.65)
        top.set(xticks=range(8), xticklabels=RESPONSES, ylabel=tr("frequency", language))
        for j, v in enumerate(mat.sum(axis=0)):
            top.text(j, v, str(v), ha="center", va="bottom", fontsize=7)
        top.set_ylim(0, mat.sum(axis=0).max() * 1.18)
        return fig, ["subsets"]
    if identifier == "B4":
        fig, axes = figure(height=5)
        ax = axes[0, 0]
        angles = np.pi / 2 - np.arange(8) * 2 * np.pi / 8
        xy = np.column_stack((np.cos(angles), np.sin(angles)))
        frame = tables["cooccurrence"]
        freq = tables["subsets"][list(RESPONSES)].sum()
        segments = []
        widths = []
        for _, row in frame.iterrows():
            if row.cooccurrence:
                i, j = RESPONSES.index(row.response1), RESPONSES.index(row.response2)
                segments.append(xy[[i, j]])
                widths.append(0.3 + 0.23 * row.cooccurrence)
        ax.add_collection(LineCollection(segments, colors="#999999", linewidths=widths, alpha=0.55))
        ax.scatter(
            xy[:, 0],
            xy[:, 1],
            s=80 + 25 * freq.to_numpy(),
            c=PALETTE["Anchor"],
            edgecolor="white",
            zorder=3,
        )
        for i, r in enumerate(RESPONSES):
            ax.text(
                xy[i, 0] * 1.2, xy[i, 1] * 1.2, f"{r}\n{int(freq[r])}", ha="center", va="center"
            )
        ax.set(xlim=(-1.5, 1.5), ylim=(-1.4, 1.4), aspect="equal")
        ax.axis("off")
        return fig, ["cooccurrence", "subsets"]
    if identifier == "B5":
        fig, axes = figure(height=3.7)
        ax = axes[0, 0]
        data = tables["pa"]
        ax.plot(
            data.singular_index,
            data.observed_singular,
            "o-",
            color=PALETTE["Ink"],
            label=tr("observed", language),
        )
        ax.plot(
            data.singular_index,
            data.q95,
            "s--",
            color=PALETTE["Anchor"],
            label=tr("threshold", language),
        )
        ax.axvspan(0.6, 2.4, color=PALETTE["Anchor"], alpha=0.08)
        ax.text(0.03, 0.06, "d = 2", transform=ax.transAxes, fontsize=10)
        ax.set(
            yscale="log",
            xlabel=tr("component", language),
            ylabel=tr("singular", language),
            xticks=range(1, 8),
        )
        ax.legend(frameon=False)
        return fig, ["pa"]
    if identifier in ("B6", "C5"):
        fig = plt.figure(figsize=(7.2, 6.6), layout="constrained")
        gs = fig.add_gridspec(2, 2)
        for cell, subset in zip(gs, audit["selected_local_subsets"], strict=True):
            trio = len(audit["local_coordinates"][subset]["indices"]) == 3
            if trio and identifier == "B6":
                inner = cell.subgridspec(1, 2, width_ratios=[3, 1])
                ax = fig.add_subplot(inner[0])
                tax = fig.add_subplot(inner[1])
                data = tables["local_geometry"]
                data = data[(data.subset == subset) & (data.kind == "solution")]
                tax.plot(data["index"], data.t, "o-", ms=2, color=PALETTE["CNBI5"])
                tax.set(xlabel="β #", ylabel="t")
                tax.tick_params(labelsize=6)
            else:
                ax = fig.add_subplot(cell)
            local_panel(
                ax,
                tables["local_geometry"],
                subset,
                audit,
                language,
                mc=tables["local_mc"] if identifier == "C5" else None,
                regions=tables["ellipses"] if identifier == "C5" else None,
            )
        handles = [
            Line2D(
                [],
                [],
                color=PALETTE["Anchor"],
                marker="*",
                ls="none",
                label=tr("nominal", language),
            ),
            Line2D([], [], color=PALETTE["Ink"], ls="-", label="CHIM"),
            Line2D(
                [], [], color=PALETTE["Ink"], marker="x", ls="none", label=tr("weight", language)
            ),
            Line2D(
                [],
                [],
                color=PALETTE["CNBI5"],
                marker="o",
                ls="none",
                label=tr("solution", language),
            ),
        ]
        if identifier == "C5":
            handles.append(
                Line2D([], [], color=PALETTE["Anchor"], ls="-", label=tr("ellipse", language))
            )
        fig.legend(handles=handles, loc="outside lower center", ncol=3, frameon=False)
        return fig, ["local_geometry"] if identifier == "B6" else [
            "local_geometry",
            "local_mc",
            "ellipses",
        ]
    if identifier == "C1" or identifier.startswith("C1_"):
        if identifier == "C1":
            fig, axes = figure(4, 2, height=10.5)
            for ax, response in zip(axes.flat, RESPONSES, strict=True):
                forest(ax, tables["coefficients"], response, language)
        else:
            fig, axes = figure(height=3.5, width=3.6)
            forest(axes[0, 0], tables["coefficients"], identifier[3:], language)
        return fig, ["coefficients"]
    if identifier == "C2":
        fig, axes = figure(height=4.3)
        ax = axes[0, 0]
        data = tables["coefficients"]
        data = data[data.term_index > 0]
        matrix = (
            data.pivot(index="response", columns="term_index", values="beta_over_SE")
            .reindex(RESPONSES)
            .to_numpy()
        )
        limit = abs(matrix).max()
        image = ax.pcolormesh(
            np.arange(10) - 0.5,
            np.arange(9) - 0.5,
            matrix,
            cmap="RdBu_r",
            vmin=-limit,
            vmax=limit,
            edgecolors="none",
            rasterized=False,
        )
        ax.set(xlim=(-0.5, 8.5), ylim=(7.5, -0.5), aspect="auto")
        ax.set(xticks=range(9), xticklabels=TERMS[1:], yticks=range(8), yticklabels=RESPONSES)
        for i in range(8):
            for j in range(9):
                rgba = image.cmap(image.norm(matrix[i, j]))
                luminance = np.dot(rgba[:3], [0.2126, 0.7152, 0.0722])
                ax.text(
                    j,
                    i,
                    f"{matrix[i, j]:+.1f}",
                    ha="center",
                    va="center",
                    fontsize=6.5,
                    color="white" if luminance < 0.48 else "#111111",
                )
        fig.colorbar(image, ax=ax, label="β / SE")
        return fig, ["coefficients"]
    if identifier == "C3":
        fig, axes = figure(8, 3, height=13.8)
        data = tables["mc_decision"]
        nominal = tables["anchors"]
        radius = audit["coding"]["sphere_radius"]
        for row, response in enumerate(RESPONSES):
            mc = data[data.anchor == response]
            anchor = nominal[nominal.response == response].iloc[0]
            for ax, (i, j) in zip(axes[row], DECISION_PAIRS, strict=True):
                ax.scatter(
                    mc[f"x{i + 1}"],
                    mc[f"x{j + 1}"],
                    s=1,
                    color=PALETTE["Anchor"],
                    alpha=0.07,
                    linewidths=0,
                )
                ax.scatter(
                    anchor[f"x{i + 1}"],
                    anchor[f"x{j + 1}"],
                    s=35,
                    marker="*",
                    color=PALETTE["Ink"],
                    zorder=5,
                )
                ax.add_patch(Circle((0, 0), radius, fill=False, ls="--", lw=0.5, color="#777777"))
                ax.set(
                    xlabel=FACTORS[i],
                    ylabel=FACTORS[j],
                    xlim=(-1.8, 1.8),
                    ylim=(-1.8, 1.8),
                    aspect="equal",
                )
            axes[row, 0].set_title(response + "*", loc="left", fontsize=8)
        return fig, ["mc_decision", "anchors"]
    if identifier == "C4":
        fig, axes = figure(2, 2, height=6.3)
        data = tables["mc_responses"]
        nominal = tables["payoff"]
        regions = tables["ellipses"]
        for ax, (r1, r2) in zip(axes.flat, PAIRS, strict=True):
            for anchor in RESPONSES:
                cloud = data[data.anchor == anchor]
                ax.scatter(
                    cloud[r1], cloud[r2], s=1, c=PALETTE["Anchor"], alpha=0.025, linewidths=0
                )
                p = nominal[nominal.anchor == anchor].set_index("response").natural
                ax.scatter(p[r1], p[r2], marker="*", s=35, c=PALETTE["Ink"], zorder=7)
                row = regions[
                    (regions.figure == "C4")
                    & (regions.projection == f"{r1}|{r2}")
                    & (regions.anchor == anchor)
                ].iloc[0]
                ellipse(ax, row)
            pp = nominal.pivot(index="anchor", columns="response", values="natural").reindex(
                RESPONSES
            )
            label_anchors(ax, pp[r1], pp[r2], perimeter=True)
            ax.set(xlabel=response_axis(r1), ylabel=response_axis(r2))
            ax.margins(0.12)
        handles = [
            Line2D(
                [], [], color=PALETTE["Ink"], marker="*", ls="none", label=tr("nominal", language)
            ),
            Line2D(
                [],
                [],
                color=PALETTE["Anchor"],
                marker="+",
                ls="none",
                label=tr("mc_center", language),
            ),
            Line2D([], [], color=PALETTE["Anchor"], ls="-", label=tr("ellipse", language)),
        ]
        fig.legend(handles=handles, loc="outside lower center", ncol=3, frameon=False)
        return fig, ["mc_responses", "ellipses", "payoff"]
    if identifier == "C6":
        fig, axes = figure(1, 2, height=4.2)
        data = tables["payoff_uncertainty"]
        for ax, value, label in zip(axes.flat, ("mean", "q95_q05"), ("mean", "width"), strict=True):
            image = heatmap(ax, data, value, language, annotate=False)
            ax.set_title(tr(label, language))
            fig.colorbar(image, ax=ax, shrink=0.7, pad=0.02)
        return fig, ["payoff_uncertainty"]
    if identifier == "C7":
        fig, axes = figure(2, 2, height=5.8)
        coeff = tables["coefficient_stability"]
        gaps = tables["spectral_gaps"]
        stop = tables["early_stop"]
        ax = axes[0, 0]
        ax.plot(
            coeff.B,
            coeff.mean_relative_frobenius_error,
            "o-",
            ms=3,
            c=PALETTE["Ink"],
            label=tr("mean_error", language),
        )
        ax.plot(
            coeff.B,
            coeff.covariance_relative_frobenius_error,
            "s--",
            ms=3,
            c=PALETTE["Anchor"],
            label=tr("cov_error", language),
        )
        ax.set(ylabel=tr("relative_error", language), xlabel="B")
        ax.legend(frameon=False)
        axes[0, 1].step(gaps.B, gaps.global_dimension, where="mid", c=PALETTE["Ink"])
        axes[0, 1].set(xlabel="B", ylabel=tr("dimension", language), ylim=(1.5, 2.5), yticks=[2])
        axes[0, 1].text(
            1300, 2.25, "B_stop = 1300", ha="center", color=PALETTE["Anchor"], fontsize=7
        )
        for key, ls in (("g1", "-"), ("g2", "--")):
            axes[1, 0].plot(
                gaps.B,
                gaps[key],
                ls,
                ms=3,
                c=PALETTE["Ink"] if key == "g1" else PALETTE["Anchor"],
                label=key,
            )
        axes[1, 0].set(xlabel="B", ylabel=tr("gap", language))
        axes[1, 0].legend(frameon=False)
        valid = stop.dropna(subset=["window_monitored_gap_max_change"])
        axes[1, 1].plot(
            valid.B, valid.window_monitored_gap_max_change, "o-", ms=3, c=PALETTE["Ink"]
        )
        axes[1, 1].axhline(0.05, c=PALETTE["Anchor"], ls="--", lw=0.9)
        axes[1, 1].set(xlabel="B", ylabel=tr("window", language))
        for ax in axes.flat:
            ax.axvspan(1100, 1300, color=PALETTE["Anchor"], alpha=0.06)
            ax.axvline(1300, c=PALETTE["Anchor"], ls=":", lw=0.8)
        return fig, ["coefficient_stability", "spectral_gaps", "early_stop"]
    raise KeyError(identifier)
