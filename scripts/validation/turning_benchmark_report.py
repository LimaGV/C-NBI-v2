"""Materialize principal tables, archived-resolution diagnostics and the case report."""

import json
import subprocess
from pathlib import Path

import numpy as np

from cnbi_v2.benchmark.hypervolume import HVGrid
from cnbi_v2.benchmark.metrics import gd_igd, spacing_sparsity
from cnbi_v2.data import sha256_file

from . import turning_benchmark_inputs as data
from .turning_final_benchmark import COMMON, LOO, PRIMARY, finalize_archive, reference_arrays
from .turning_reference import ROOT, write_json
from .turning_reference_sensitivity import union_mask

METHODS = ("CNBI5", "VRF", "NSGA3", "MOEAD")


def mdtable(headers, rows):
    return (
        "\n".join(
            ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
            + ["| " + " | ".join(map(str, row)) + " |" for row in rows]
        )
        + "\n"
    )


def number(value):
    return "pending" if value is None else f"{float(value):.7g}"


def run(output=data.OUTPUT):
    report_dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    meta = json.loads((output / "metadata.json").read_text())
    inputs = data.load_inputs()
    z = inputs["z"]
    h = meta["hv_reference"]
    grid = HVGrid(np.array(h["lower"]), np.array(h["reference"]))
    cache = np.memmap(
        ROOT / "experiments/runs" / data.RUN_ID / "point_attainment.uint8",
        mode="r",
        dtype=np.uint8,
        shape=(len(z), grid.bytes_per_point),
    )
    refs = reference_arrays()
    resolution = []
    for level, ids in inputs["resolution"].items():
        spacing, sparsity = spacing_sparsity(z[ids])
        intrinsic = dict(
            **grid.estimate(union_mask(cache, ids)), Spacing=spacing, Sparsity=sparsity
        )
        for label, ref in ((COMMON, "all"), (LOO, "minus_cnbi")):
            gd, igd = gd_igd(z[ids], refs[ref])
            resolution.append(
                dict(
                    H=level,
                    N_unique_ND=len(ids),
                    label=label,
                    reference=ref,
                    GD=gd,
                    IGD=igd,
                    **intrinsic,
                    source="Phase6 parent-H20 membership, not standalone H execution",
                    T_total=None,
                    runtime_status="PENDING_H5_EQUIVALENCE",
                )
            )
    data.table(output / "cnbi_resolution_quality_historical.csv", resolution)
    tables = {}
    for variant, filename in (
        ("native", "native_metrics_summary.csv"),
        ("K66", "equalized_k66_summary.csv"),
    ):
        records = data.rows(output / filename)
        values = {(r["method"], r["label"], r["metric"]): r for r in records}
        table = []
        for method in METHODS:
            row = dict(Method=method, label=COMMON)
            for metric in (*PRIMARY, "N_unique_ND", "T_total_controlled"):
                r = values.get((method, COMMON, metric))
                row[f"{metric}_median"] = float(r["median"]) if r else None
                row[f"{metric}_IQR"] = float(r["IQR"]) if r else None
                row[f"{metric}_n"] = int(r["n"]) if r else 0
            table.append(row)
        tables[variant] = table
        data.table(
            output / f"main_table_{'A_native' if variant == 'native' else 'B_K66'}.csv", table
        )
    sensitivity = data.rows(output / "reference_run_sensitivity.csv")
    by_ref = {(int(r["r"]), r["metric"]): r for r in sensitivity}
    ref_table = []
    for r in (5, 10, 15, 20, 25, 30):
        row = dict(n_runs=r)
        for metric in ("reference_size", "GD_CNBI5", "IGD_CNBI5", "HV_reference"):
            s = by_ref[(r, metric)]
            for q in ("median", "q05", "q95"):
                row[f"{metric}_{q}"] = float(s[q])
        ref_table.append(row)
    data.table(output / "main_table_C_reference_sensitivity.csv", ref_table)
    cost_summary = data.rows(output / "cost_quality_summary.csv")
    cost_values = {
        (r["method"], int(r["generation"]), r["metric"]): r
        for r in cost_summary
        if r["label"] == COMMON
    }
    cost_table = []
    for method in ("NSGA3", "MOEAD"):
        for generation in (50, 100, 200, 300, 400):
            row = dict(method=method, generation=generation, label=COMMON)
            for metric in ("T_total", "GD", "IGD", "HV", "N_unique_ND"):
                for q in ("median", "IQR"):
                    row[f"{metric}_{q}"] = float(cost_values[(method, generation, metric)][q])
            cost_table.append(row)
    data.table(output / "main_table_D_controlled_cost.csv", cost_table)
    meta["report_postprocessing"] = dict(
        source_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        source_sha256=sha256_file(Path(__file__)),
        working_tree_dirty_at_start=report_dirty,
        archived_resolution_diagnostics=True,
        new_NBI_optimizations=0,
        CNBI_time_assigned=False,
        VRF_executions=0,
    )
    write_json(output / "metadata.json", meta)
    finalize_archive(output)
    parts = [INTRO]
    for variant, title in (
        ("native", "Tabela A — desempenho nativo"),
        ("K66", "Tabela B — cardinalidade igualada em66"),
    ):
        parts.append(f"\n## {title}\n\n")
        table_rows = []
        for row in tables[variant]:
            method = row["Method"]

            def shown(metric, row=row, method=method):
                text = number(row[f"{metric}_median"])
                return (
                    text + f" [{number(row[f'{metric}_IQR'])}]"
                    if method in {"NSGA3", "MOEAD"}
                    else text
                )

            table_rows.append(
                [
                    method,
                    shown("N_unique_ND"),
                    *[shown(m) for m in PRIMARY],
                ]
                + ([shown("T_total_controlled")] if variant == "native" else [])
            )
        parts.append(
            mdtable(
                [
                    "Method",
                    "Unique ND",
                    "GD",
                    "IGD",
                    "HV estimate",
                    "Spacing",
                    "Sparsity",
                ]
                + (["T_total/s"] if variant == "native" else []),
                table_rows,
            )
        )
    parts.append(TABLE_NOTES)
    parts.append("\n## Tabela C — sensibilidade ao número de runs\n\n")
    parts.append(
        mdtable(
            ["r", "Reference size median", "GD H5 median", "IGD H5 median", "HV reference median"],
            [
                [
                    r["n_runs"],
                    *[
                        number(r[f"{m}_median"])
                        for m in ("reference_size", "GD_CNBI5", "IGD_CNBI5", "HV_reference")
                    ],
                ]
                for r in ref_table
            ],
        )
    )
    composition = data.rows(output / "reference_composition_sensitivity.csv")
    parts.append("\n## Composição e contribuição marginal\n\n")
    parts.append(
        mdtable(
            ["Reference", "ND", "GD H5", "IGD H5", "HV estimate"],
            [
                [
                    r["composition"],
                    r["reference_size"],
                    *[number(r[k]) for k in ("GD_CNBI5", "IGD_CNBI5", "HV_reference")],
                ]
                for r in composition
            ],
        )
    )
    parts.append(
        mdtable(
            ["Added family", "Base", "Delta ND", "Delta HV", "Delta GD H5", "Delta IGD H5"],
            [
                [
                    r[k]
                    for k in (
                        "added_family",
                        "base",
                        "delta_cardinality",
                        "delta_HV",
                        "delta_GD",
                        "delta_IGD",
                    )
                ]
                for r in data.rows(output / "reference_marginal_effects.csv")
            ],
        )
    )
    parts.append("\n## Cardinalidade da referência\n\n")
    parts.append(
        mdtable(
            ["K_R", "GD H5", "IGD H5", "HV reference estimate"],
            [
                [r["K_R"], *[number(r[k]) for k in ("GD_CNBI5", "IGD_CNBI5", "HV")]]
                for r in data.rows(output / "reference_cardinality_sensitivity.csv")
            ],
        )
    )
    parts.append(REFERENCE_CONCLUSIONS)
    parts.append("\n## Robustez independente H5 e resoluções auxiliares\n\n")
    parts.append(
        mdtable(
            ["H", "ND", "GD to R30", "IGD to R30", "HV estimate", "Runtime"],
            [
                [r["H"], r["N_unique_ND"], *[number(r[k]) for k in ("GD", "IGD", "HV")], "pending"]
                for r in resolution
                if r["label"] == LOO
            ],
        )
    )
    parts.append(
        "\nOs cinco conjuntos acima são memberships do H20 preservado; não são novas "
        "execuções isoladas. H5 oficial continua408. Referência R30 exclui toda CNBI. "
        "Os resultados LOO das demais famílias estão nos CSVs, com alvos próprios; "
        "não devem ser ordenados como se fossem a mesma referência.\n"
    )
    parts.append("\n## Tabela D — custo controlado, somente EAs\n\n")
    parts.append(
        mdtable(
            [
                "Method",
                "Generation",
                "T_total median/s",
                "IGD common median",
                "HV estimate median",
                "ND median",
            ],
            [
                [
                    r["method"],
                    r["generation"],
                    *[number(r[f"{k}_median"]) for k in ("T_total", "IGD", "HV", "N_unique_ND")],
                ]
                for r in cost_table
            ],
        )
    )
    parts.append(INTEGRATED_CONCLUSIONS)
    parts.append("\n## Proporções de runs melhores e posição percentual do H5\n\n")
    fractions = [
        r
        for r in data.rows(output / "deterministic_percentiles.csv")
        if r["deterministic"] == "CNBI5"
    ]
    parts.append(
        mdtable(
            ["Variant", "EA", "Metric", "Fraction better than H5", "H5 percentile (higher better)"],
            [
                [
                    r[k]
                    for k in (
                        "variant",
                        "stochastic",
                        "metric",
                        "proportion_runs_strictly_better",
                        "deterministic_percentile_higher_is_better",
                    )
                ]
                for r in fractions
            ],
        )
    )
    parts.append(
        "\nAs mesmas comparações com VRF, as proporções de empate, média/SD/IQR/q05/q95/"
        "mínimo/máximo de todas as métricas e todas as30 runs estão nos CSVs completos. "
        "Percentis usam score orientado (HV positivo, demais negativos), com meia "
        "massa nos empates. Não são p-values; empates de HV podem ser quantização.\n"
    )
    parts.append("\n## Figuras e reprodutibilidade\n\n")
    parts.append(
        "14 figuras em PDF/SVG e PNG600dpi, cores/markers centralizados em "
        "`figures/visual_mapping.json`, legendas e dados completos preservados. "
        "Faixas das curvas de runs são q05–q95 das100 subamostras, não IC; curvas "
        "dos EAs em K/tempo usam mediana e IQR. Figuras comuns/LOO estão identificadas.\n"
    )
    parts.append(
        mdtable(
            ["Artifact", "SHA256"],
            [
                [name, sha256_file(output / name)]
                for name in (
                    "metadata.json",
                    "checksums.sha256",
                    "reference_final.npz",
                    "hv_reference_point.json",
                )
            ],
        )
    )
    parts.append(
        "\nInput hashes completos em metadata.json; raw, modelos, normalização, IDs dos37 "
        "subsets, fases anteriores e resultados publicados não foram modificados. "
        "Otimização adaptativa, novos cenários sintéticos e merge automático não iniciados.\n"
    )
    (ROOT / "docs/mathematics/turning_final_benchmark.md").write_text(
        "\n".join(parts), encoding="utf-8", newline="\n"
    )


INTRO = """# Fase8 — sensibilidade e benchmark controlado, escopo revisado

8A e qualidade8B concluídas preservando exatamente os408 pontos oficiais do H5.
Execução VRF foi explicitamente proibida: somente66 pontos históricos reavaliados
na Fase7 entram na qualidade. Após falha do gate H5 direto, o responsável escolheu
preservar408 e registrar custo CNBI como pendente. A comparação temporal tem apenas
NSGA-III/MOEA-D; não há tempo comparável de CNBI ou VRF.

Branch `feature/08-reference-sensitivity-final-benchmark`; PR10 revisado com quatro
checks verdes/sem conflitos, squash em main f904e8de0810324b4456cf2ad7de59ca2c6b5ab4.
Código8A limpo3ac57ecb9dcd9912e0ebe4576a772471c902e8e3;
timing limpo70883d7c8dc5954f3438b0b43e5274b07cf16e0a;
qualidade8B limpa a0b38817e99cc91c8a6e244fd38ad8e6d87c4fd1. Metadados registram
as versões distintas de cálculo/relatório e hashes, sem reescrever execuções.

Definições completas: [matemática](reference_sensitivity_and_cardinality_control.md),
ADR0012 e protocolo JSON. GD/IGD são médias de distância Euclidiana, p1. HV é
volume dominado estimado em quatro redes Sobol comuns,2^16 pontos cada; não exato.
Spacing é SD amostral(ddof1) de nearest-neighbor Euclidiano e Sparsity sua média,
conforme resultados aplicados corrigidos V1; a divergência ddof0 anterior foi auditada.
Nenhuma normalização por método/run/K ou clipping. Mesmo frame global nominal Fase5.
"""

TABLE_NOTES = """
Tabelas A/B usam o mesmo alvo P_all22523, rótulo COMMON_REFERENCE_SELF_INCLUDED.
GD/IGD têm self-inclusion por família; particularmente GD zero de MOEAD decorre
de seus pontos presentes no envelope e não comprova convergência independente.
Valores dos EAs são mediana[IQR] de30 runs, salvo tempo, que tem10 seeds controladas.
CNBI/VRF são observações únicas; o zero de IQR aritmético dos CSVs singleton não é
variabilidade algorítmica e não é apresentado como uma banda determinística.

Contagens nativas: CNBI492 resultados de subproblemas,489 ND antes de deduplicar,
411 decisões únicas antes de ND e408 ND genuínos. EAs retornam330 por run; NSGA3
tem330 ND genuínos, MOEAD303..330 (mediana327). VRF tem66 decisões retidas no
export histórico; o N original pré-processamento não é conhecido por esse export.
Kmax comum é303, o mínimo real de todas as frentes, nunca a média. K usa20/30/40/
50/66/100/150/200/250/300/303; VRF para em66. Uma ordenação FPS por frente conserva
extremos e produz todos os prefixos aninhados. A referência completa não é reduzida.
Tempos não são atribuídos artificialmente à redução K; ela é pós-processamento de qualidade.
"""

REFERENCE_CONCLUSIONS = """
## Conclusões da Fase8A

GD continua melhorando: mediana em25=.0416334 contra30=.0395672 (cerca de5% de
redução); não há certificado de saturação total. IGD varia pouco entre25=.167309
e30=.167647 (cerca de.20%); HV do envelope passa de.896454 a.899406 (cerca de.33%).
As distribuições100-subset, seus oito resumos e os prefixos históricos estão nos
artefatos. Aumento de ND não é, isoladamente, insuficiência da referência.

A composição importa. Remover NSGA3 reduz HV em.153484 e eleva GD_H5 a.277798;
remover MOEAD reduz HV em.00484981, mas muda IGD_H5 de.167647 para.122467 pela
mudança de distribuição do alvo. O envelope geométrico depende bastante de NSGA3;
MOEAD altera fortemente a ponderação empírica por pontos, sem ganho proporcional
de HV. Não se definiu limiar arbitrário para a palavra “excessivo”.

VRF acrescenta63 ND líquidos, melhora GD em.000482942 e IGD em.000161701 no
NM→NMV. Ganho de HV=.0000267207, SE quadratura pareada=.0000154272 (apenas poucos
nós de integração); não estabelecer significância/precisão excessiva desse pequeno
volume. Sem NSGA, porém, VRF acrescenta cerca de.04242 de HV a MOEAD: redundância
marginal depende dos demais geradores, não apenas de possuir66 pontos.

Cardinalidade do alvo altera IGD materialmente: KR10000→18503 muda IGD de.136301
para.167647 (+cerca de23%), enquanto GD melhora apenas cerca de.09% e HV cresce
cerca de.046%. FPS torna o alvo reduzido menos concentrado; IGD é média ponderada
por seus pontos. Não confundir crescimento/densificação com piora do H5 fixo.

R30 é defensável como alvo empírico finito completo deste protocolo, com essas
sensibilidades explícitas; não como referência universal ou comprovadamente
saturada. Ele foi reconstruído idêntico à Fase7:18503 ND, zero origens CNBI.
Foi congelado sem acrescentar runs. As reduções são diagnóstico, não substituto
do alvo no benchmark final. Não há erro de construção que justifique trocar R30;
a falha H5 refere-se à execução/custo do baseline, preservado pelo responsável.
"""

INTEGRATED_CONCLUSIONS = """
## Interpretação integrada e perguntas finais

**Cardinalidade:** NSGA3 oferece menor IGD e maior HV que H5 neste caso, inclusive
K66; portanto a diferença não é explicada só por N. H5 passa de HV.667337 nativo
para.597703 em66 (-cerca de10.4%) e IGD.148712→.170507. MOEAD perde menos de1%
de HV em66, mas mantém IGD pior que H5: muitos de seus pontos densificam uma
região menor. A ordem H5/MOEAD por HV se inverte: H5 ligeiramente maior nativo,
MOEAD maior em66. A ordem H5/NSGA por Spacing também muda. Nenhum único ranking
resume os cinco indicadores. Spacing muito baixo do VRF não equivale a cobertura:
seu IGD permanece.274519 e HV.491568. Sparsity menor pode significar concentração.

**Convergência/cobertura H5:** independente R30, GD=.0395672 e IGD=.167647;
common self-included, GD=.00110937. O contraste impede usar GD comum muito baixo
como prova independente. A limitação mais visível é cobertura/resolução, porém
não se pode atribuí-la exclusivamente a H: o gate revelou branches locais
dependentes do caminho de continuação. Maior lacuna de referência→H5 é.338097,
perto de x codificado(-.51136,-.19551,-1.59019); a separação mais forte é em z_Kp,
com trade-offs ROI/OEE. Os50 maiores gaps estão preservados sem inferir unidades.

**Custo:** i5-12400F,6 cores/12 lógicos, Windows11, Python3.12.15 e ambiente
travado, thread numérica1, métodos sequenciais, ausência de Python externo ativo
no gate. Cada EA tem10 seeds1001..1010 e um warm-up400 gerações excluído. Todos20
resultados finais são bitwise iguais aos arquivados da Fase7; callback não mudou
evolução. T_total inclui preparação/avaliação/dedup/ND e observer, cujo overhead
é separado; core também é registrado. Métricas foram calculadas depois do timing.

NSGA em50 gerações usa mediana2.16828s com IGD comum.0811255 e HV.767413;
MOEAD em400 usa82.9774s com IGD.185004 e HV.661585. No plano das dez configurações
medianas medidas, nenhuma MOEAD é ND em(T,IGD) ou(T,-HV). Isso caracteriza apenas
os EAs e este setup/calibração; não demonstra dominância estatística universal.
As curvas são populações correntes, não archives acumuladas, e podem ser
não monotônicas. Tempos finais de30 runs paralelas anteriores são históricos,
não usados como custo comparável. NFE não vira falsa unidade equivalente NBI.

**CNBI/VRF no custo:** indisponível por motivos distintos. H5 direto diverge em24/
492 pesos (maxΔx3.11812, maxΔz.594267), apesar de geometrias iguais/restrições
satisfeitas. O responsável manteve408 e aceitou custo CNBI pendente; zero repetições
de timing CNBI. VRF foi proibido de executar: zero otimizações/timings e nenhum
runtime inventado. Não é possível responder se H5 ocupa região competitiva no
plano qualidade×tempo nem se H5→H10/H20 compensa custo. Qualidade de memberships
mais finos pode ser descrita, mas proporcionalidade ao tempo permanece aberta.

**Coarse-to-fine:**408 pontos oferecem uma representação exploratória com extremos
e lacunas identificáveis; dados mais finos melhoram cobertura. Isso apoia somente
uma motivação geométrica para exploração/refinamento. O H5 oficial foi extraído
do H20 e não reproduziu a execução H5 isolada; os resultados não demonstram que
essa exploração seja produzida pelo algoritmo coarse isolado ou que seja barata.
Resolver formalmente inicializações/continuação e equivalência é pré-condição
de uma futura comparação temporal CNBI, sem trocar os408 nesta entrega.

Os resultados não autorizam vencedor universal, p-values contra réplicas falsas,
refinamento adaptativo automático ou novos cenários. HV é aproximação QMC com
precisão auditada, alvos LOO diferem e referência comum contém auto-inclusão.
"""


if __name__ == "__main__":
    run()
