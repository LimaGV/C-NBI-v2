"""One palette, translation registry and export policy for the whole package."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RESPONSES = ("T", "MTTF", "WR", "Ra", "Rt", "Kp", "ROI", "OEE")
DIRECTIONS = ("MAX", "MAX", "MIN", "MIN", "MIN", "MIN", "MAX", "MAX")
TERMS = ("1", "x₁", "x₂", "x₃", "x₁²", "x₂²", "x₃²", "x₁x₂", "x₁x₃", "x₂x₃")
FACTORS = ("x₁ — Vc (cs)", "x₂ — f", "x₃ — ap (md)")
PALETTE = {
    "Reference": "#D0D0D0",
    "CNBI5": "#E69F00",
    "VRF": "#0072B2",
    "NSGA3": "#009E73",
    "MOEAD": "#CC3311",
    "OriginalNBI": "#AA3377",
    "Anchor": "#AA4499",
    "Ink": "#333333",
}
METHODS = {
    "Reference": ("Referência empírica independente", "Independent empirical reference"),
    "CNBI5": ("C-NBI H5 standalone", "C-NBI H5 standalone"),
    "VRF": ("VRF-NBI histórico", "Historical VRF-NBI"),
    "NSGA3": ("NSGA-III", "NSGA-III"),
    "MOEAD": ("MOEA/D", "MOEA/D"),
}
MARKERS = {"CNBI5": "o", "VRF": "s", "NSGA3": "^", "MOEAD": "D"}
LINESTYLES = {"CNBI5": "-", "VRF": ":", "NSGA3": "--", "MOEAD": "-."}
SVG_OMISSIONS = {
    "D3": "Dense16-panel reference clouds: full-vector PDF and PNG600dpi supplied; "
    "an extra SVG would repeat hundreds of thousands of marker objects."
}

# ID -> Portuguese title, English title, recommended tier. Individual C1 exports
# are requested presentation alternatives to its composite, not new evidence.
FIGURES = {
    "A1": (
        "Mapas de contorno das superfícies de resposta",
        "Response-surface contour maps",
        "main",
    ),
    "A2": (
        "Matriz payoff normalizada das otimizações individuais",
        "Normalized payoff matrix from individual optimizations",
        "main",
    ),
    "A3": (
        "Assimetria dos custos cruzados normalizados",
        "Asymmetry of normalized cross costs",
        "supplementary",
    ),
    "B1": (
        "Ótimos individuais no espaço codificado dos fatores",
        "Individual optima in the coded factor space",
        "supplementary",
    ),
    "B2": (
        "Projeção dos ótimos individuais no espaço normalizado das respostas",
        "Projection of individual optima in the normalized response space",
        "supplementary",
    ),
    "B3": (
        "Estrutura dos subconjuntos selecionados",
        "Structure of the selected response subsets",
        "main",
    ),
    "B4": (
        "Rede de coocorrência das respostas nos subconjuntos selecionados",
        "Response co-occurrence network in the selected subsets",
        "supplementary",
    ),
    "B5": (
        "Espectro singular e limiar de incerteza da análise paralela",
        "Singular spectrum and uncertainty threshold from parallel analysis",
        "main",
    ),
    "B6": (
        "Geometria local do CHIM e direções NBI",
        "Local CHIM geometry and NBI directions",
        "main",
    ),
    "C1": (
        "Estimativas e intervalos de confiança dos coeficientes RSM",
        "RSM coefficient estimates and confidence intervals",
        "supplementary",
    ),
    "C2": (
        "Coeficientes RSM divididos pelo erro padrão",
        "RSM coefficients divided by standard error",
        "supplementary",
    ),
    "C3": (
        "Propagação da incerteza das âncoras no espaço de decisão",
        "Propagation of anchor uncertainty in the decision space",
        "supplementary",
    ),
    "C4": (
        "Incerteza Monte Carlo dos ótimos individuais",
        "Monte Carlo uncertainty of the individual optima",
        "main",
    ),
    "C5": (
        "Incerteza das âncoras e geometria local do CHIM",
        "Anchor uncertainty and local CHIM geometry",
        "main",
    ),
    "C6": (
        "Propagação da incerteza na matriz payoff",
        "Uncertainty propagation in the payoff matrix",
        "main",
    ),
    "C7": ("Estabilização da propagação Monte Carlo", "Monte Carlo propagation stability", "main"),
    "D1a": (
        "Coordenadas paralelas: referência e C-NBI",
        "Parallel coordinates: reference and C-NBI",
        "main",
    ),
    "D1b": (
        "Coordenadas paralelas das soluções não dominadas",
        "Parallel coordinates of the nondominated solutions",
        "main",
    ),
    "D2": (
        "Projeções bidimensionais da fronteira empírica",
        "Two-dimensional projections of the empirical front",
        "main",
    ),
    "D3": (
        "Comparação por método e projeção",
        "Comparison by method and projection",
        "supplementary",
    ),
    "D4": (
        "Projeção PCA da fronteira em oito objetivos",
        "PCA projection of the eight-objective front",
        "supplementary",
    ),
    "D5": (
        "Contribuição exclusiva ao envelope empírico histórico",
        "Exclusive contribution to the historical empirical envelope",
        "supplementary",
    ),
    "E1": (
        "IGD em função da cardinalidade da aproximação",
        "IGD as a function of approximation cardinality",
        "main",
    ),
    "E2": (
        "Hipervolume em função da cardinalidade da aproximação",
        "Hypervolume as a function of approximation cardinality",
        "main",
    ),
    "E3": (
        "Efeito da cardinalidade sobre as métricas de distribuição",
        "Effect of cardinality on distribution metrics",
        "supplementary",
    ),
    "F1": (
        "Qualidade da aproximação em função do tempo computacional",
        "Approximation quality as a function of computational time",
        "main",
    ),
    "F2": ("Tempo total de processamento", "Total processing time", "main"),
    "F3": (
        "Ganho marginal de qualidade por custo computacional",
        "Marginal quality gain per computational cost",
        "supplementary",
    ),
    "G1": (
        "Sensibilidade do IGD ao número de execuções usadas na referência",
        "Sensitivity of IGD to the number of runs used in the reference",
        "main",
    ),
    "G2": (
        "Sensibilidade do GD ao número de execuções usadas na referência",
        "Sensitivity of GD to the number of runs used in the reference",
        "supplementary",
    ),
    "G3": ("Crescimento da referência empírica", "Growth of the empirical reference", "main"),
    "G4": (
        "Sensibilidade à cardinalidade da referência empírica",
        "Sensitivity to empirical-reference cardinality",
        "main",
    ),
    "G5": (
        "Sensibilidade à composição da referência empírica",
        "Sensitivity to empirical-reference composition",
        "supplementary",
    ),
    "H1": (
        "Distribuição das distâncias ao vizinho mais próximo",
        "Nearest-neighbor distance distribution",
        "supplementary",
    ),
    "H2": (
        "Densidade local na projeção PCA da referência",
        "Local density in the reference PCA projection",
        "supplementary",
    ),
    "H3": (
        "Distribuição das soluções no espaço de decisão",
        "Distribution of solutions in the decision space",
        "supplementary",
    ),
    "I1": ("Fluxo metodológico do caso aplicado", "Applied-case methodological workflow", "main"),
    "J1": ("Síntese visual do caso aplicado", "Visual summary of the applied case", "main"),
}
for response in RESPONSES:
    FIGURES[f"C1_{response}"] = (
        f"Coeficientes e intervalos Wald de 95% — {response}",
        f"Coefficients and 95% Wald intervals — {response}",
        "supplementary",
    )

TEXT = {
    "anchor": ("Âncora", "Anchor"),
    "payoff": ("Matriz payoff", "Payoff matrix"),
    "uncertainty": ("Incerteza", "Uncertainty"),
    "propagation": ("Propagação de incerteza", "Uncertainty propagation"),
    "nondominated": ("Fronteira não dominada", "Nondominated front"),
    "decision_space": ("Espaço de decisão", "Decision space"),
    "response_space": ("Espaço de respostas", "Response space"),
    "optimum": ("Ótimo individual", "Individual optimum"),
    "weight": ("Posição do peso β", "Weight β position"),
    "solution": ("Solução NBI H5", "H5 NBI solution"),
    "response": ("Resposta", "Response"),
    "individual": ("Otimização individual", "Individual optimization"),
    "loss": ("Resposta normalizada (menor é melhor)", "Normalized response (lower is better)"),
    "level": ("Nível da resposta", "Response level"),
    "coded": ("Fatores codificados", "Coded factors"),
    "frequency": ("Frequência", "Frequency"),
    "subset": ("Subconjunto", "Subset"),
    "observed": ("Observado", "Observed"),
    "threshold": ("Limiar MC q95", "MC q95 threshold"),
    "singular": ("Valor singular", "Singular value"),
    "component": ("Componente", "Component"),
    "estimate": ("Estimativa e IC Wald 95%", "Estimate and 95% Wald CI"),
    "nominal": ("Âncora nominal", "Nominal anchor"),
    "mc_center": ("Centro MC", "MC center"),
    "ellipse": ("Elipse de incerteza MC de 95%", "95% MC uncertainty ellipse"),
    "mean": ("Média", "Mean"),
    "width": ("Amplitude q95 − q05", "q95 − q05 width"),
    "relative_error": ("Erro relativo de Frobenius", "Relative Frobenius error"),
    "mean_error": ("Média dos coeficientes", "Coefficient mean"),
    "cov_error": ("Covariância dos coeficientes", "Coefficient covariance"),
    "dimension": ("Dimensão global", "Global dimension"),
    "gap": ("Gap normalizado", "Normalized gap"),
    "window": ("Máxima variação na janela", "Maximum change in window"),
    "performance": ("Desempenho visual (0=pior, 1=melhor)", "Visual performance (0=worst, 1=best)"),
    "historical_target": ("Alvo comum histórico", "Historical common target"),
    "cardinality": ("Cardinalidade K", "Cardinality K"),
    "time": ("Tempo total (s)", "Total time (s)"),
    "runs": ("Execuções por família EA", "Runs per EA family"),
    "ref_size": ("Cardinalidade da referência", "Reference cardinality"),
    "ref_hv": ("HV estimado da referência", "Estimated reference HV"),
    "nn": ("Distância ao vizinho mais próximo", "Nearest-neighbor distance"),
    "density": ("log(1 + densidade kNN, k=15)", "log(1 + kNN density, k=15)"),
    "normal_out": ("Normal perpendicular ao plano", "Normal perpendicular to plane"),
    "intrinsic1": ("Coordenada intrínseca 1", "Intrinsic coordinate 1"),
    "intrinsic2": ("Coordenada intrínseca 2", "Intrinsic coordinate 2"),
    "t": ("Distância normal t", "Normal distance t"),
    "contrast": ("Assimetria de custo relativo", "Relative-cost asymmetry"),
    "count": ("Pontos exclusivos", "Exclusive points"),
    "historical": ("Histórico Fase 7 — C-NBI H20", "Historical Phase 7 — C-NBI H20"),
    "gain_igd": ("Redução de IGD / Δtempo", "IGD reduction / Δtime"),
    "gain_hv": ("Ganho de HV / Δtempo", "HV gain / Δtime"),
    "center": ("Ponto central", "Center point"),
}


def tr(key, language):
    return TEXT[key][0 if language == "pt" else 1]


def method_label(method, language):
    return METHODS[method][0 if language == "pt" else 1]


def configure():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 9,
            "legend.fontsize": 7,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.25,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "cnbi-applied-visuals-v1",
            "savefig.facecolor": "white",
            "text.usetex": False,
        }
    )


def clean_axes(fig):
    for ax in fig.axes:
        ax.grid(False, which="both")
        for collection in ax.collections:
            collection.set_rasterized(False)
        ax.tick_params(direction="out", length=3, width=0.6)
        if ax.get_label() != "<colorbar>":
            ax.spines[["top", "right"]].set_visible(False)


def points(ax, frame, x, y, language, reference=True, legend=False, size=9):
    methods = (["Reference"] if reference else []) + ["CNBI5", "VRF", "NSGA3", "MOEAD"]
    for method in methods:
        data = frame[frame.method == method]
        ax.scatter(
            data[x],
            data[y],
            s=2 if method == "Reference" else size,
            c=PALETTE[method],
            marker="." if method == "Reference" else MARKERS[method],
            alpha=0.5 if method == "Reference" else 0.65,
            linewidths=0,
            label=method_label(method, language),
            zorder=1 if method == "Reference" else 3,
        )
    if legend:
        ax.legend(frameon=False, markerscale=1.3, loc="best")


def band(ax, frame, x, y, method, language):
    data = frame[frame.method == method]
    groups = data.groupby(x, sort=True)[y]
    q = groups.quantile([0.25, 0.5, 0.75]).unstack()
    ax.plot(
        q.index,
        q[0.5],
        color=PALETTE[method],
        marker=MARKERS[method],
        markersize=3,
        linestyle=LINESTYLES[method],
        label=method_label(method, language),
    )
    if method in ("NSGA3", "MOEAD"):
        ax.fill_between(
            np.asarray(q.index, dtype=float), q[0.25], q[0.75], color=PALETTE[method], alpha=0.14
        )
