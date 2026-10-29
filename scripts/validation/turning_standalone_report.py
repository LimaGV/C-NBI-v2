"""Figures/report from the corrected archive; no scientific optimization."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import NullFormatter
from scipy.spatial import cKDTree

from cnbi_v2.data import sha256_file

from . import turning_standalone_analysis as a
from .turning_benchmark_figures import bands
from .turning_cnbi_standalone import OUTPUT, table
from .turning_reference import ROOT, write_json


def markdown(headers, rows):
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "|" + "---|" * len(headers),
            *["| " + " | ".join(str(v) for v in r) + " |" for r in rows],
        ]
    )


def fmt(v):
    return f"{float(v):.9g}"


def report():
    output = OUTPUT
    folder = output / "figures"
    folder.mkdir(exist_ok=True)
    policy = json.loads((ROOT / "docs/policies/benchmark_cardinality_cost.json").read_text())
    colors = policy["colors"]
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 9,
            "axes.titlesize": 9,
            "legend.fontsize": 7,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "cnbi-phase8-standalone",
        }
    )
    captions = []

    def save(fig, name, caption):
        for suffix in ("png", "pdf", "svg"):
            kwargs = (
                {"metadata": {"CreationDate": None, "ModDate": None}} if suffix == "pdf" else {}
            )
            fig.savefig(folder / f"{name}.{suffix}", dpi=600, **kwargs)
        captions.append(dict(figure=name, caption=caption))
        plt.close(fig)

    sensitivity = a.numeric_rows(output / "reference_run_sensitivity.csv")
    for metric in ("GD_CNBI5", "IGD_CNBI5"):
        records = sorted([r for r in sensitivity if r["metric"] == metric], key=lambda r: r["r"])
        fig, ax = plt.subplots(figsize=(7.08, 3.1), layout="constrained")
        xx = np.array([r["r"] for r in records])
        ax.fill_between(
            xx,
            [r["q05"] for r in records],
            [r["q95"] for r in records],
            color=colors["CNBI5"],
            alpha=0.18,
            label="q05–q95 stored subsets",
        )
        ax.plot(xx, [r["median"] for r in records], "o-", color=colors["CNBI5"], label="Median")
        ax.set(xlabel="Runs per EA family", ylabel=metric.replace("_CNBI5", ""), xticks=xx)
        ax.grid(alpha=0.15)
        ax.legend()
        save(
            fig,
            metric.lower() + "_vs_runs",
            "Standalone H5 fixed409 ND; same100 stored subsets "
            "at each r<30, singleton30. Range is a subset distribution, not confidence interval.",
        )
    composition = a.numeric_rows(output / "reference_composition_sensitivity.csv")
    card = a.numeric_rows(output / "reference_cardinality_sensitivity.csv")
    for name, records, key in (
        ("composition_sensitivity", composition, "composition"),
        ("reference_cardinality", card, "K_R"),
    ):
        fig, axes = plt.subplots(1, 2, figsize=(7.08, 3.1), layout="constrained")
        for ax, metric in zip(axes, ("GD_CNBI5", "IGD_CNBI5"), strict=True):
            ax.plot(
                [r[key] for r in records], [r[metric] for r in records], "o-", color=colors["CNBI5"]
            )
            ax.set(xlabel=key, ylabel=metric.replace("_CNBI5", ""))
            ax.grid(alpha=0.15)
            if key == "K_R":
                ax.set_xscale("log")
                ax.xaxis.set_minor_formatter(NullFormatter())
                ax.set_xticks(
                    [r[key] for r in records], [str(int(r[key])) for r in records], rotation=35
                )
        save(
            fig,
            name,
            "Same frozen independent reference lineages/orderings; only GD/IGD of "
            "the corrected standalone H5 reevaluated. Targets never include CNBI.",
        )
    curves = a.numeric_rows(output / "cardinality_curve_metrics.csv")
    for metric in a.PRIMARY:
        labels = (a.COMMON, a.LOO) if metric in ("GD", "IGD") else (a.COMMON,)
        fig, axes = plt.subplots(
            1, len(labels), figsize=(7.08, 3.25), layout="constrained", squeeze=False
        )
        for ax, label in zip(axes[0], labels, strict=True):
            for method in ("CNBI5", "NSGA3", "MOEAD", "VRF"):
                rows = [r for r in curves if r["method"] == method and r["label"] == label]
                xx, low, mid, high = bands(rows, "K", metric)
                ax.plot(xx, mid, marker="o", markersize=3, color=colors[method], label=method)
                if method in ("NSGA3", "MOEAD"):
                    ax.fill_between(xx, low, high, color=colors[method], alpha=0.15)
            ax.axvline(66, color="gray", linestyle=":", linewidth=0.7)
            ax.set(xlabel="Candidate cardinality K", ylabel=metric)
            if metric in ("GD", "IGD"):
                ax.set_title(
                    "Historical pooled H20 target"
                    if label == a.COMMON
                    else "Family LOO: targets differ"
                )
            ax.grid(alpha=0.15)
        axes[0, 0].legend()
        save(
            fig,
            metric.lower() + "_vs_K",
            "Only CNBI curve changed: nested FPS of409 genuine "
            "standalone ND points. Other method numbers/orderings preserved. Full targets. "
            "Historical common target is not a new self-included reference; LOO targets differ.",
        )
    resolution = a.numeric_rows(output / "standalone_resolution_metrics.csv")
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.2), layout="constrained")
    selected = [r for r in resolution if r["label"] == a.LOO and r["repetition"] == 1]
    for ax, metric in zip(axes, ("GD", "IGD", "HV"), strict=True):
        ax.plot(
            [r["H"] for r in selected], [r[metric] for r in selected], "o-", color=colors["CNBI5"]
        )
        ax.set(xlabel="Standalone resolution H", ylabel=metric, xticks=[2, 4, 5, 10, 20])
        ax.tick_params(axis="x", labelrotation=35)
        ax.grid(alpha=0.15)
    save(
        fig,
        "quality_vs_resolution",
        "Every H independently solved on the same37 subsets. "
        "GD/IGD use frozen18503-point zero-CNBI target. H20 is sensitivity only; H5 baseline.",
    )
    cost = a.numeric_rows(output / "cost_quality_ea_preserved.csv")
    for metric in ("IGD", "HV"):
        fig, ax = plt.subplots(figsize=(7.08, 3.3), layout="constrained")
        for method in ("NSGA3", "MOEAD"):
            rows = [r for r in cost if r["method"] == method and r["label"] == a.COMMON]
            _, low, mid, high = bands(rows, "generation", metric)
            _, tlow, time, thigh = bands(rows, "generation", "T_total")
            ax.plot(time, mid, "o--", color=colors[method], label=method)
            ax.fill_between(time, low, high, color=colors[method], alpha=0.15)
            ax.errorbar(
                time, mid, xerr=[time - tlow, thigh - time], fmt="none", color=colors[method]
            )
        for h_value in (2, 4, 5, 10, 20):
            rows = [r for r in resolution if r["label"] == a.COMMON and r["H"] == h_value]
            times = np.array([r["T_total"] for r in rows])
            time = np.median(times)
            ax.plot(
                time,
                rows[0][metric],
                "s",
                color=colors["CNBI5"],
                label="CNBI standalone" if h_value == 2 else None,
            )
            if h_value == 5:
                ax.errorbar(
                    [time],
                    [rows[0][metric]],
                    xerr=[[time - np.quantile(times, 0.25)], [np.quantile(times, 0.75) - time]],
                    fmt="none",
                    color=colors["CNBI5"],
                )
            ax.annotate(
                f"H{h_value}",
                (time, rows[0][metric]),
                xytext=(3, 5),
                textcoords="offset points",
                fontsize=7,
            )
        ax.set_xscale("log")
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set(
            xlabel="End-to-end time /s (log)",
            ylabel=metric,
            title="Fixed historical pooled H20 target"
            if metric == "IGD"
            else "Shared HV point/grid",
        )
        ax.grid(alpha=0.15)
        ax.legend()
        save(
            fig,
            metric.lower() + "_vs_time",
            "New standalone CNBI quality paired with own runtime. "
            "H5 median/IQR of five identical-output runs; other H single measured observations. "
            "EA10-seed checkpoint timing/quality preserved. No VRF timing. "
            "Different campaign dates.",
        )
    table(output / "figure_captions.csv", captions)
    # Updated geometric gap diagnostics, with no physical-coordinate inference.
    ref = a.load(a.OLD / "reference_final.npz")
    front = a.load(output / "official_cnbi5.npz")
    distance, nearest = cKDTree(front["z"]).query(ref["z"], k=1, eps=0.0, workers=1)
    table(
        output / "cnbi5_coverage_gaps.csv",
        [
            dict(
                rank=i + 1,
                reference_row=int(j),
                nearest_official_row=int(nearest[j]),
                distance=float(distance[j]),
                **{f"x{k + 1}": float(v) for k, v in enumerate(ref["x"][j])},
            )
            for i, j in enumerate(np.argsort(-distance, kind="stable")[:50])
        ],
    )

    def metric_table(filename, label):
        rows = a.numeric_rows(output / filename)
        result = []
        for method in ("CNBI5", "VRF", "NSGA3", "MOEAD"):
            group = [r for r in rows if r["method"] == method and r["label"] == label]
            result.append(
                [
                    method,
                    str(int(np.median([r["N_unique_ND"] for r in group]))),
                    *[fmt(np.median([r[k] for r in group])) for k in a.PRIMARY],
                ]
            )
        return markdown(
            ["Method", "N ND", "GD", "IGD", "HV estimate", "Spacing", "Sparsity"], result
        )

    official = next(
        r
        for r in a.numeric_rows(output / "native_metrics.csv")
        if r["method"] == "CNBI5" and r["label"] == a.LOO
    )
    equal = next(
        r
        for r in a.numeric_rows(output / "equalized_k66_metrics.csv")
        if r["method"] == "CNBI5" and r["label"] == a.LOO
    )
    impacts = a.numeric_rows(output / "old_vs_new_metrics.csv")
    # Named audit supplement for direct inspection; no solver result is changed.
    named_records = a.numeric_rows(output / "H5_rep1_records.csv")
    cases = a.numeric_rows(output / "historical_24_divergent_cases.csv")
    table(
        output / "historical_24_divergent_cases_named.csv",
        [
            dict(
                subset_id=named_records[int(r["row"])]["subset"],
                beta=named_records[int(r["row"])]["beta"],
                **r,
            )
            for r in cases
        ],
    )
    # A separate historical comparison does not alter/select any standalone run.
    parent_h20 = a.load(
        ROOT / "results/phase_06_local_nbi/turning_local_nbi_h20_20261024/"
        "local_nbi_solutions_H20.npz"
    )
    direct_h20 = a.load(output / "H20_rep1.npz")
    dx20 = np.max(np.abs(parent_h20["x"] - direct_h20["x"]), axis=1)
    h20_records = a.numeric_rows(output / "H20_rep1_records.csv")
    write_json(
        output / "historical_h20_reproduction_audit.json",
        dict(
            purpose="historical diagnostic only; no solution selection or changed solver",
            diagnostic_x_atol=1e-5,
            disagreements=int((dx20 > 1e-5).sum()),
            max_x_Linf=float(dx20.max()),
            exact_cause="UNDETERMINED",
            H5_five_repeats_bitwise_identical=True,
            cases=[
                dict(
                    row=int(j),
                    subset=h20_records[j]["subset"],
                    composition=h20_records[j]["composition"],
                    old_x=parent_h20["x"][j].tolist(),
                    new_x=direct_h20["x"][j].tolist(),
                    old_t=float(parent_h20["t"][j]),
                    new_t=float(direct_h20["t"][j]),
                    old_accepted=bool(parent_h20["accepted"][j]),
                    new_accepted=bool(direct_h20["accepted"][j]),
                )
                for j in np.flatnonzero(dx20 > 1e-5)
            ],
        ),
    )
    text = """# Fase8 — correção do baseline operacional standalone

C-NBI(H=5) significa **execução standalone H5**. H20 é somente sensibilidade
de alta resolução. Esta correção foi explicitamente solicitada antes do merge
do PR11, na mesma branch feature/08-reference-sensitivity-final-benchmark.
Não é uma nova fase ou método. A escolha anterior de408/custo pendente está
SUPERSEDED. O conjunto antigo chama-se CNBI_H5_extracted_from_H20_parent_grid.

## Execução e independência

Protocolo e fonte foram commitados em3e23701 (hash completo em launch.json).
37 subsets congelados, modelos/anchors/payoff locais e normalização global
Fase5, SLSQP/Jacobianos e warm starts originais. Aceitação: solver success,
finitude, eq_norm<=1e-4 e sphere_margin>=-1e-9; nenhuma tolerância relaxada.
Fonte do runner recebeu depois apenas formatação; o hash da execução continua
preservado no commit/launch, sem reescrever o resultado histórico.

Todos os nove solves medidos e o warm-up H2 ocorreram com os diretórios de
resultados das Fases6/7 fisicamente renomeados e indisponíveis. Foram restaurados
em finally; completion.json registra a operação. O pipeline oficial recebe
apenas evidências upstream das Fases2/5 e protocolo congelado; nenhum arquivo
H20 define H5. Cada resolução constrói sua própria malha e trajetória.

H5:492 subproblemas/492 aceitos/0 falhas/411 decisões únicas/**409 ND**.
As cinco repetições têm x,z,t e demais arrays científicos bitwise idênticos
(tolerância pré-declarada absoluta1e-12,relativa0). Repetições quantificam ruído
de runtime, não replicações de qualidade. O baseline é a primeira execução,
sem escolha de solução por melhoria de métricas.

## Referências e preservação

O alvo independente R_minus_CNBI permanece byte-identical:18503 ND, zero CNBI.
Não houve nova amostragem:506 referências de runs e seis composições foram
reavaliadas pela mesma linhagem salva; FPS da referência foi reutilizado.
Modelos/raw, MC/anchors/PA e37 subsets,30 runs por EA,66 pontos VRF e todo timing
EA permanecem preservados. Nenhuma execução VRF ou EA nova.

O alvo comum22523 da Fase7 é retido **somente como alvo histórico congelado**:
HISTORICAL_COMMON_H20_TARGET. Ele contém a família CNBI antiga/H20 e não é uma
nova referência comum auto-incluindo H5 standalone. Assim, a análise principal
independente do CNBI usa R_minus_CNBI. Tabelas comparativas históricas abaixo
servem para continuidade, preservando cada número dos demais métodos. Não se
reconstrói um pooled novo nem se alegam novas propriedades de auto-inclusão.
LOO dos outros métodos conserva seus próprios alvos; não permite ranking direto
entre famílias por GD/IGD. HV/Spacing/Sparsity não dependem desses alvos.

## Baseline oficial, alvo independente

"""
    text += markdown(
        ["Variant", "N", "GD", "IGD", "HV estimate", "Spacing", "Sparsity"],
        [
            [name, int(r["N_unique_ND"]), *[fmt(r[k]) for k in a.PRIMARY]]
            for name, r in (("Native", official), ("K66", equal))
        ],
    )
    text += "\n\n## Comparação nativa com alvo histórico fixo\n\n"
    text += metric_table("native_metrics.csv", a.COMMON)
    text += "\n\n## K66 com alvo histórico fixo\n\n"
    text += metric_table("equalized_k66_metrics.csv", a.COMMON)
    text += """

EAs:medianas de30 runs; distribuições/IQR estão nos CSVs. CNBI e VRF são
observações únicas. GD zero MOEAD é consequência de auto-inclusão no alvo
histórico, não prova de convergência independente. Ordenações dos outros
métodos não mudaram. FPS novo usa409 pontos genuínos, extremos e desempate
determinístico já definidos. K=20/30/40/50/66/100/150/200/250/300/303;
Kmax comum303 continua o mínimo real; VRF encerra em66. Todos os alvos são
completos nas curvas. ReduçãoK não recebe artificialmente o tempo do solve.

## Impacto antigo versus standalone — alvo independente

"""
    text += markdown(
        ["Metric", "Old H5-from-H20", "Standalone H5", "Delta"],
        [
            [r["metric"], fmt(r["old_H5_from_H20"]), fmt(r["new_standalone_H5"]), fmt(r["delta"])]
            for r in impacts
            if r["label"] == a.LOO
        ],
    )
    text += """

Os492 pares são listados em parent_vs_standalone_all492.csv e os24 divergentes
em historical_24_divergent_cases_named.csv:subset,beta,composição,parent row,distâncias
Linf/L2 em x e oito z,delta t e dominância nos dois sentidos com a tolerância
congelada.468 coincidentes/24 divergentes; máximoΔx3.1181207107 e
máximoΔz0.5942667068. Trajetórias de continuação distintas atingem branches
locais factíveis. O diagnóstico explica a correção; não seleciona o baseline.

Auditoria adicional:H20 standalone difere do H20 histórico em1/4557 subproblemas
acima do mesmo limite diagnóstico x1e-5:linha4552,C_6_7_8,composição[18,1,1],
máximoΔx1.3274507752,t histórico.007262385 e novo-.010981157. Ambas soluções
foram aceitas; a causa exata da diferença entre essas execuções não foi
determinada. A geometria desse subset foi verificada como igual. O arquivo
historical_h20_reproduction_audit.json preserva o caso. Não se alterou solver,
start ou saída para recuperar a solução histórica; H20 continua observação
auxiliar própria,não garantia de repetição do arquivo anterior. Isso não muda
a identidade bitwise das cinco execuções H5 nem sua definição oficial.

## Resoluções independentes e custo

"""
    timing = a.numeric_rows(output / "timing_cnbi.csv")
    timing_rows = []
    res_rows = []
    for h_value in (2, 4, 5, 10, 20):
        runs = [r for r in timing if r["H"] == h_value]
        row = next(r for r in selected if r["H"] == h_value)
        res_rows.append(
            [
                h_value,
                int(row["subproblems"]),
                int(row["accepted"]),
                int(row["unique"]),
                int(row["ND"]),
                *[fmt(row[k]) for k in a.PRIMARY],
            ]
        )
        for key in ("T_solver", "T_total"):
            vals = np.array([r[key] for r in runs])
            q = np.quantile(vals, [0.25, 0.75])
            timing_rows.append(
                [
                    h_value,
                    key,
                    len(vals),
                    fmt(np.median(vals)),
                    fmt(q[1] - q[0]) if len(vals) > 1 else "not estimated",
                    fmt(vals.min()),
                    fmt(vals.max()),
                ]
            )
    text += markdown(["H", "Subproblems", "Accepted", "Unique", "ND", *a.PRIMARY], res_rows)
    text += "\n\nGD/IGD da tabela acima usam R_minus_CNBI,18503 pontos. Zero falhas em todo H.\n\n"
    text += markdown(["H", "Time/s", "n", "Median", "IQR", "Min", "Max"], timing_rows)
    text += """

T_solver soma chamadas solve_nbi_lattice; T_total inclui verificação/leitura de
inputs,malha,geometrias,NBI,reavaliação8respostas,dedup e ND, além da coleta de
starts/trials. Exclui serialização em disco e métricas externas, realizadas
depois. Um warm-up H2 não medido foi descartado; H5 tem cinco medições, demais
H uma observação cada, sem estimativa de dispersão. Arrays de cada run estão
ligados às suas medidas em standalone_resolution_metrics.csv.

Mesma máquina Intel i5-12400F/Windows11, Python3.12.15 e ambiente travado,
uma thread numérica e execução sequencial; hardware/isolamento em launch.json.
Timing EA preservado:10 seeds,NSGA17.4856s[IQR.090247],MOEAD82.9816s[IQR.263237].
As campanhas têm datas/commits próprios, registrados sem atribuir-lhes um commit
comum fictício. Hardware/ambiente são iguais; ruído de carga/frequência permanece
uma limitação. A diferença de custo não é uma equivalência por NFE.

## Sensibilidade atualizada e interpretação

"""
    run_table = []
    for r_value in (5, 10, 15, 20, 25, 30):
        rows = [r for r in sensitivity if r["r"] == r_value]

        def med(metric, rows=rows):
            return fmt(next(r["median"] for r in rows if r["metric"] == metric))

        run_table.append(
            [r_value, med("reference_size"), med("GD_CNBI5"), med("IGD_CNBI5"), med("HV_reference")]
        )
    text += markdown(
        ["r", "Reference N median", "GD H5 median", "IGD H5 median", "HV reference median"],
        run_table,
    )
    text += "\n\n"
    text += markdown(
        ["Composition", "Reference N", "GD H5", "IGD H5", "HV reference"],
        [
            [
                r["composition"],
                int(r["reference_size"]),
                fmt(r["GD_CNBI5"]),
                fmt(r["IGD_CNBI5"]),
                fmt(r["HV_reference"]),
            ]
            for r in composition
        ],
    )
    text += "\n\n"
    text += markdown(
        ["Reference K", "GD H5", "IGD H5"],
        [[int(r["K_R"]), fmt(r["GD_CNBI5"]), fmt(r["IGD_CNBI5"])] for r in card],
    )
    text += """

Medianas/IQR/q05/q95 e506 linhas por subamostra foram atualizadas somente em
GD/IGD de H5. Cardinalidades/HV/composição de origens/índices/lineages permanecem
os originais. A referência não tem saturação certificada:25→30 ainda reduz GD
em cerca de4.9%; IGD permanece sensível à densidade do alvo. Composição depende
fortemente do NSGA; contribuição marginal de VRF/MOEA em HV é condicional e
permanece idêntica ao arquivo anterior, inclusive SE pareado da quadratura.

O novo H5 melhora IGD independente em15.81% e HV em10.74% sobre o subconjunto
histórico,mas GD muda pouco e Spacing/Sparsity aumentam. A correção não é uma
melhoria geral do solver nem prova global. Ao igualar66 soluções, NSGA mantém
IGD/HV melhores no alvo histórico, e H5 mantém HV maior que MOEA tanto nativo
como K66. A reversão H5/MOEA por HV registrada antes deixa de ocorrer; não
transportar aquela conclusão para o novo baseline.

No plano do alvo histórico,H5 oferece uma alternativa rápida com qualidade
inferior ao NSGA nos indicadores de cobertura, sem um vencedor universal.
H10 é dominado por NSGA geração50 nos pares(T,IGD)/(T,-HV) de medianas; H20
oferece maior HV e menor IGD que essas configurações EA,com custo9.673s, e
aparece na envoltória qualidade-custo. Isso é comparação descritiva condicionada
ao alvo histórico/medianas,preservando auto-inclusão dos EAs e antigos CNBI;
não é teste estatístico ou certificado da frente verdadeira. H5→H10 reduz IGD
independente29.92% e aumenta HV3.53% por1.69x tempo; H5→H20 reduz IGD53.63%
e aumenta HV12.45% por7.36x tempo. Não há razão escalar universal para chamar
esses ganhos proporcionais ao custo; a escolha depende da qualidade desejada.

GD independente~.0395 indica proximidade ao alvo amostrado,sem prova de
convergência global. A redução IGD com H mostra lacuna de cobertura/resolução,
mas o diagnóstico24/492 impede atribuir tudo apenas à densidade da malha.
cnbi5_coverage_gaps.csv localiza as50 maiores lacunas em códigos originais,
sem inferir unidades físicas. A geometria e o baixo custo standalone sustentam
H5 como malha exploratória para possível investigação coarse-to-fine; nenhum
refinamento foi iniciado e a política adaptativa não foi validada.

HV usa os mesmos bounds/seeds/power16/quatro scrambles,sem clipping ou novo
reference point. É estimativa de quadratura com SE, não volume exato.
Spacing=SD amostral(ddof1) dos vizinhos Euclidianos e Sparsity=média,com
dependência de densidade. Nenhuma mudança nas cinco definições congeladas.

## Artefatos, rastreabilidade e verificação

Arquivo oficial:results/phase_08_final_benchmark/turning_standalone_correction_20261025.
O anterior turning_reference_sensitivity_20261024 permanece byte-identical,
classificado historical_parent_grid_analysis. Seu manifesto continua
c0e8ab1ccd8d4b8d42ca03dffec22afb86200d4dc371da5993276001bf3b3988.
Phase6 também permanece íntegra:nenhum artefato anterior foi apagado/reescrito.

launch.json identifica commit/config/hardware/inputs antes dos solves;
metadata.json identifica execução da análise e hashes das referências reusadas;
checksums.sha256 cobre todos os payloads novos,menos o próprio manifesto.
As doze figuras novas têm PDF/SVG/PNG600dpi e captions; os gráficos estruturais
de cardinalidade/HV da referência anteriores permanecem válidos e preservados.
Validação de software,40 itens de entrega,ADR0012 e claims C-BENCH-01..07 em
docs/phase_8_verification.md. PR11 permanece aberto,sem merge automático.

Nenhum raw/modelo alterado,dado reconstruído,refit,MC,PA,anchor,VRF,EA,retuning,
novo subset ou mudança de SLSQP/starts/tolerância. Sem refinamento adaptativo,
novos cenários sintéticos ou novas metaheurísticas.
"""
    (ROOT / "docs/mathematics/turning_final_benchmark.md").write_text(
        text, encoding="utf-8", newline="\n"
    )
    write_json(
        output / "report_provenance.json",
        dict(
            source=str(Path(__file__).relative_to(ROOT)),
            source_sha256=sha256_file(Path(__file__)),
            figures=len(captions),
            official_baseline_sha256=sha256_file(output / "official_cnbi5.npz"),
        ),
    )
    files = sorted(p for p in output.rglob("*") if p.is_file() and p.name != "checksums.sha256")
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.relative_to(output).as_posix()}\n" for p in files),
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    report()
