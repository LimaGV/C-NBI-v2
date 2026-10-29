"""Publication figures from preserved CSV values; no optimization or fitting."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import NullFormatter

from cnbi_v2.data import sha256_file

from . import turning_benchmark_inputs as data
from .turning_final_benchmark import COMMON, LOO, finalize_archive

LABELS = {"CNBI5": "C-NBI H5", "VRF": "VRF historical", "NSGA3": "NSGA-III", "MOEAD": "MOEA/D"}
MARKERS = {"CNBI5": "o", "VRF": "s", "NSGA3": "v", "MOEAD": "D"}
LINES = {"CNBI5": "-", "VRF": "-", "NSGA3": "--", "MOEAD": "-."}


def numeric_rows(path):
    return data.rows(path)


def bands(rows, xkey, metric):
    levels = sorted({float(r[xkey]) for r in rows})
    q = np.array(
        [
            np.quantile(
                [float(r[metric]) for r in rows if float(r[xkey]) == x],
                [0.25, 0.5, 0.75],
                method="linear",
            )
            for x in levels
        ]
    )
    return np.array(levels), q[:, 0], q[:, 1], q[:, 2]


def figures(output):
    if not (output / "phase8b_quality_completion.json").exists():
        raise ValueError("complete scientific metrics before plotting")
    policy = json.loads(data.POLICY.read_text())
    folder = output / "figures"
    folder.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "legend.fontsize": 7.5,
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.4,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "cnbi-v2-phase8",
            "savefig.facecolor": "white",
        }
    )
    visual = dict(
        colors=policy["colors"],
        markers=MARKERS,
        linestyles=LINES,
        reference_color="#444444",
        font="DejaVu Serif",
        formats=["pdf", "svg", "png"],
        png_dpi=600,
        uncertainty="IQR across EA runs; q05-q95 across reference subsets",
        renderer_source=Path(__file__).relative_to(data.ROOT).as_posix(),
        renderer_sha256=sha256_file(Path(__file__)),
    )
    (folder / "visual_mapping.json").write_text(
        json.dumps(visual, indent=2) + "\n", encoding="utf-8"
    )
    captions = []

    def save(fig, name, caption):
        for suffix in ("pdf", "svg", "png"):
            metadata = (
                {"CreationDate": None, "ModDate": None}
                if suffix == "pdf"
                else {"Date": None}
                if suffix == "svg"
                else None
            )
            fig.savefig(folder / f"{name}.{suffix}", dpi=600, metadata=metadata)
        (folder / f"{name}_caption.md").write_text(caption + "\n", encoding="utf-8")
        captions.append(dict(figure=name, caption=caption))
        plt.close(fig)

    sensitivity = numeric_rows(output / "reference_run_sensitivity.csv")
    for metric, name, ylabel, color in (
        ("GD_CNBI5", "gd_vs_reference_runs", "GD of fixed C-NBI H5", policy["colors"]["CNBI5"]),
        ("IGD_CNBI5", "igd_vs_reference_runs", "IGD of fixed C-NBI H5", policy["colors"]["CNBI5"]),
        ("HV_reference", "hv_reference_vs_runs", "Estimated HV of reference", "#444444"),
        ("reference_size", "reference_cardinality_vs_runs", "Reference ND cardinality", "#444444"),
    ):
        records = [r for r in sensitivity if r["metric"] == metric]
        records.sort(key=lambda r: int(r["r"]))
        x = np.array([int(r["r"]) for r in records])
        median = np.array([float(r["median"]) for r in records])
        low, high = (np.array([float(r[q]) for r in records]) for q in ("q05", "q95"))
        fig, ax = plt.subplots(figsize=(7.08, 3.05), layout="constrained")
        ax.fill_between(x, low, high, color=color, alpha=0.17, label="q05–q95 subset range")
        ax.plot(x, median, color=color, marker="o", label="Median; full set at30")
        ax.set(xlabel="Selected runs per EA family", ylabel=ylabel, xticks=x)
        ax.grid(alpha=0.15)
        ax.legend()
        save(
            fig,
            name,
            "Fixed408-point H5; paired100 distinct seed subsets for each r<30, "
            "one full reference at30. Shading is the q05–q95 subset distribution, not a "
            "confidence interval. All references exclude CNBI. HV is common-node Sobol quadrature.",
        )

    ref_k = numeric_rows(output / "reference_cardinality_sensitivity.csv")
    for metric in ("GD_CNBI5", "IGD_CNBI5", "HV"):
        fig, ax = plt.subplots(figsize=(7.08, 3.05), layout="constrained")
        x = [int(r["K_R"]) for r in ref_k]
        ax.plot(x, [float(r[metric]) for r in ref_k], marker="o", color="#444444")
        ax.set_xscale("log")
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xticks(x, [str(v) for v in x], rotation=25)
        ax.set(
            xlabel="Reference cardinality K_R (log scale)",
            ylabel=metric.replace("_CNBI5", " of H5"),
        )
        ax.grid(alpha=0.15)
        save(
            fig,
            f"{metric.lower()}_vs_reference_cardinality",
            "Nested extreme-preserving farthest-point prefixes of R30, sensitivity only. "
            "The evaluated H5 set is fixed. "
            "The benchmark itself always retains the full reference.",
        )

    curves = numeric_rows(output / "cardinality_curve_metrics.csv")
    for metric in ("GD", "IGD", "HV", "Spacing", "Sparsity"):
        dependent = metric in {"GD", "IGD"}
        labels = (COMMON, LOO) if dependent else (COMMON,)
        fig, axes = plt.subplots(
            1, len(labels), figsize=(7.08, 3.35), layout="constrained", squeeze=False
        )
        for ax, label in zip(axes[0], labels, strict=True):
            for method in ("CNBI5", "NSGA3", "MOEAD", "VRF"):
                records = [r for r in curves if r["method"] == method and r["label"] == label]
                x, low, median, high = bands(records, "K", metric)
                color = policy["colors"][method]
                ax.plot(
                    x,
                    median,
                    label=LABELS[method],
                    color=color,
                    marker=MARKERS[method],
                    markersize=3.2,
                    linestyle=LINES[method],
                )
                if method in {"NSGA3", "MOEAD"}:
                    ax.fill_between(x, low, high, color=color, alpha=0.14)
            ax.axvline(66, color="#888888", linewidth=0.7, linestyle=":")
            ax.set_xscale("log")
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.set_xticks(
                [20, 40, 66, 100, 200, 303], ["20", "40", "66", "100", "200", "303"], rotation=30
            )
            ax.set(xlabel="Candidate cardinality K (log scale)", ylabel=metric)
            if dependent:
                ax.set_title(
                    "Common, self-included" if label == COMMON else "Family LOO, targets differ"
                )
            ax.grid(alpha=0.15)
        axes[0, 0].legend(loc="best")
        save(
            fig,
            f"{metric.lower()}_vs_candidate_cardinality",
            "One nested farthest-point ordering per native front; extremes preserved. "
            "EA lines show medians/IQR of30 runs; CNBI/VRF are fixed fronts. K66 is marked. "
            "Complete common/LOO targets remain fixed; LOO targets differ. HV uses one shared "
            "point/grid; Spacing/Sparsity use corrected V1 definitions and depend on density.",
        )

    cost = numeric_rows(output / "cost_quality_metrics.csv")
    for metric in ("IGD", "HV"):
        labels = (COMMON, LOO) if metric == "IGD" else (COMMON,)
        fig, axes = plt.subplots(
            1, len(labels), figsize=(7.08, 3.35), layout="constrained", squeeze=False
        )
        for ax, label in zip(axes[0], labels, strict=True):
            for method in ("NSGA3", "MOEAD"):
                records = [r for r in cost if r["method"] == method and r["label"] == label]
                gens, low, median, high = bands(records, "generation", metric)
                _, tlo, time, thi = bands(records, "generation", "T_total")
                color = policy["colors"][method]
                ax.plot(
                    time,
                    median,
                    color=color,
                    marker=MARKERS[method],
                    markersize=3.5,
                    linestyle=LINES[method],
                    label=LABELS[method],
                )
                ax.fill_between(time, low, high, color=color, alpha=0.14)
                ax.errorbar(
                    time,
                    median,
                    xerr=[time - tlo, thi - time],
                    fmt="none",
                    color=color,
                    linewidth=0.6,
                    capsize=2,
                )
                for g, t, y in zip(gens, time, median, strict=True):
                    if g in (50, 400):
                        ax.annotate(
                            str(int(g)),
                            (t, y),
                            xytext=(3, 4),
                            textcoords="offset points",
                            fontsize=7,
                        )
            ax.set_xscale("log")
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.set_xticks([2, 5, 10, 20, 50, 100], ["2", "5", "10", "20", "50", "100"])
            ax.set(xlabel="End-to-end processing time /s (log scale)", ylabel=metric)
            ax.set_title(
                "Fixed common HV reference point"
                if metric == "HV"
                else "Common, self-included"
                if label == COMMON
                else "Family LOO, targets differ"
            )
            ax.grid(alpha=0.15)
        axes[0, 0].legend()
        save(
            fig,
            f"{metric.lower()}_vs_processing_time",
            "Sequential controlled10-seed EA campaign, checkpoints50/100/200/300/400. "
            "Median/IQR quality and horizontal processing-time IQR. Only EAs have comparable "
            "timing: CNBI remains pending the failed H5 equivalence gate; VRF execution was "
            "forbidden. LOO targets differ; it is not a cross-family ranking.",
        )
    data.table(output / "figure_captions.csv", captions)
    finalize_archive(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=data.OUTPUT)
    args = parser.parse_args()
    figures(args.output)
