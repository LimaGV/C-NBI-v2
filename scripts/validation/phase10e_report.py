"""Reproduce the scientific report from the complete, separately saved analyses."""

import numpy as np
import pandas as pd
from phase10e_inputs import METHODS, OUTPUT, ROOT, read, table


def number(value):
    if pd.isna(value):
        return "--"
    if isinstance(value, (float, np.floating)):
        return f"{value:.8g}"
    return str(value)


def markdown(frame):
    rows = [
        "| " + " | ".join(map(str, frame.columns)) + " |",
        "| " + " | ".join("---" for _ in frame.columns) + " |",
    ]
    rows.extend(
        "| " + " | ".join(number(v) for v in row) + " |"
        for row in frame.itertuples(index=False, name=None)
    )
    return "\n".join(rows)


def report():
    summary = pd.read_csv(OUTPUT / "scenario_metric_summary.csv")
    tests = pd.read_csv(OUTPUT / "statistical_tests.csv")
    ranking = pd.read_csv(OUTPUT / "method_rankings.csv")
    equal = pd.read_csv(OUTPUT / "equalization_diagnostics.csv")
    robust = pd.read_csv(OUTPUT / "feasibility_replica_metrics.csv")
    costs = pd.read_csv(OUTPUT / "paired_quality_cost.csv")
    precision = pd.read_csv(OUTPUT / "hv_supplement_precision.csv")
    quality_path = OUTPUT / "quality_report.json"
    quality = read(quality_path) if quality_path.exists() else {"status": "PENDING"}
    quality_table = pd.DataFrame([dict(check=k, result=str(v)) for k, v in quality.items()])
    summary["nx"] = summary.scenario_id.str.extract(r"nx(\d+)").astype(int)
    summary["delta"] = summary.scenario_id.str.extract(r"delta(\d+)").astype(int)
    summary["rho_target"] = summary.scenario_id.str.extract(r"rho(\d+)").astype(int) / 100
    summary["m"] = summary.nx + summary.delta + 1
    factors = []
    for (analysis, metric, method), group in summary.groupby(["analysis", "metric", "method"]):
        for factor in ("nx", "delta", "rho_target", "m"):
            for level, cell in group.groupby(factor):
                factors.append(
                    dict(
                        analysis=analysis,
                        metric=metric,
                        method=method,
                        factor=factor,
                        level=level,
                        structural_cells=len(cell),
                        median=float(cell["median"].median()),
                        q25=float(cell["median"].quantile(0.25)),
                        q75=float(cell["median"].quantile(0.75)),
                    )
                )
    table(OUTPUT / "factor_method_summary.csv", factors)
    factors = pd.DataFrame(factors)
    comparison = tests[
        (tests.analysis.isin(["native_primary", "equalized_secondary"]))
        & (tests.method_a == "C-NBI")
    ]
    primary = comparison[comparison.analysis == "native_primary"]
    eq_tests = comparison[comparison.analysis == "equalized_secondary"]
    assert (primary.p_holm < 0.05).all()
    assert (eq_tests[eq_tests.metric == "IGD"].p_holm > 0.05).all()
    worse_hv = eq_tests[(eq_tests.metric == "HV") & eq_tests.method_b.isin(["NSGA-III", "MOEA/D"])]
    assert (worse_hv.p_holm < 0.05).all() and (worse_hv.median_difference < 0).all()
    main_table = (
        summary[summary.analysis.isin(["native_primary", "equalized_secondary"])]
        .groupby(["analysis", "method", "metric"])["median"]
        .median()
        .unstack()
        .reset_index()
    )
    cni = comparison[
        [
            "analysis",
            "metric",
            "method_b",
            "n_scenarios",
            "median_difference",
            "ci_low",
            "ci_high",
            "p_holm",
            "rank_biserial",
            "wins",
            "losses",
        ]
    ]
    hv_last = precision[(precision.supplementary_max_power == 20) & (precision.power == 20)]
    hv_table = hv_last[
        [
            "replica_id",
            "original_HV",
            "HV_QMC",
            "HV_QMC_SE",
            "relative_se",
            "relative_change_previous",
            "min_scramble_hits",
            "qmc_status",
        ]
    ]
    totals = robust.groupby(["method", "epsilon"])[["N_feasible", "N_ND"]].sum().reset_index()
    changes = pd.read_csv(OUTPUT / "feasibility_plot_values.csv")
    objective_trends = factors[
        (factors.analysis == "native_primary")
        & (factors.factor == "m")
        & factors.method.isin(["VRF-NBI", "NSGA-III"])
    ]
    objective_trend_table = objective_trends[
        ["method", "metric", "level", "structural_cells", "median", "q25", "q75"]
    ]
    native_secondary = (
        summary[summary.analysis == "native_secondary"]
        .groupby(["method", "metric"])["median"]
        .median()
        .unstack()
        .reset_index()
    )
    selected_fraction = equal.groupby("method").retained_fraction.median().reset_index()
    ranks = ranking[ranking.analysis == "native_primary"]
    omnibus = tests[
        tests.analysis.isin(["native_primary", "equalized_secondary"])
        & tests.test.eq("Friedman_permutation")
    ][["analysis", "metric", "n_scenarios", "statistic", "pvalue", "p_holm"]]
    audit = read(OUTPUT / "audit_report.json")
    derive = read(OUTPUT / "derivation_manifest.json")
    body = f"""# Fase 10E - análise científica dos resultados sintéticos

Estado numérico: **COMPLETED**. Campanha de entrada: somente `campaign_v2`,
commit `5c3829dbd1bdd41ee828cfaf919c551d4f869d32`, PR17 ainda separado.
Branch: `feature/10e-synthetic-statistical-analysis`, empilhada sobre a branch10D.
Nenhuma busca oficial, ajuste RSM, calibração, referência ou seed foi reexecutado
ou alterado. MDR0017 permanece EXPERIMENTAL até revisão explícita.

## Protocolo e unidade de análise

540 resultados: 27 células estruturais x5 réplicas x4 métodos; 135 blocos pareados,
com coeficientes RSM idênticos entre métodos. A comparação usa a mediana das cinco
réplicas por célula, nunca 135 problemas independentes. Cada observação individual
continua exportada. Medianas de diferenças pareadas não são diferenças entre
medianas globais.

IGD e HV são primários. Holm controla conjuntamente 14 hipóteses nativas:
dois Friedman e seis pares por indicador. Friedman usa 199999 permutações internas
às células e correção mais-um; sua aproximação qui-quadrado é apenas diagnóstico.
Wilcoxon usa distribuição condicional exata dos sinais, incluindo empates nas
posições médias e exclusão de zeros exatos. Não se arredondam diferenças para
criar empates. Intervalos pontuais de 95% reamostram 50000 vetores de cenários,
mantendo pareamento; são intervalos de estabilidade, não simultâneos.
As famílias secundárias de Holm são exploratórias e identificadas separadamente.

O protocolo inicial da Fase 10E foi congelado antes dos novos cálculos, **depois**
de os resultados descritivos da Fase 10D já existirem. O ajuste de coorte comum
foi documentado antes da inspeção da tabela equalizada completa. Não é pré-registro anterior
à campanha. A interpretação inferencial é condicional às hipóteses dos testes e
ao desenho observado, sem promessa de generalização a todos os problemas.

HV principal: 26 células completas, excluindo `nx5_delta5_rho025`, pois duas
réplicas VRF-NBI eram PRECISION_PENDING. Exclui-se a célula inteira dos quatro
métodos; não se comparam medianas com números diferentes de réplicas. IGD:27.
O mesmo critério deixa 26 células na análise equalizada de HV, logo as coortes
nativa e equalizada coincidem. Nenhum ranking é atribuído a HV pendente.

## 1. O C-NBI melhora IGD e HV no conjunto nativo?

**Sim no contraste agregado deste desenho**, contra os três comparadores,
com os seis testes pareados primários significativos após Holm conjunto.
O C-NBI tem melhor IGD em 25/27 células, e o NSGA-III em 2/27. Para HV válido,
o C-NBI vence 21/26 e o NSGA-III 5/26; portanto não há vitória em todas as células.
As medianas globais abaixo usam 27 células para IGD e 26 para HV.

{markdown(main_table)}

Todos os contrastes de C-NBI menos comparador, incluindo a análise secundária:
valores negativos favorecem C-NBI em IGD; positivos favorecem C-NBI em HV.
Rank-biserial positivo favorece C-NBI em ambos. Os intervalos são pontuais,
enquanto a decisão de multiplicidade usa exclusivamente p_holm.

{markdown(cni)}

Um intervalo pontual da mediana pode excluir zero mesmo quando Wilcoxon/Holm
não rejeita: são procedimentos com alvos e pressupostos diferentes, e somente
os p ajustados controlam a família de comparações. Não se usa o intervalo para
reclassificar um contraste ajustado não significativo.

Testes omnibus, com a família primária conjunta e a secundária separada:

{markdown(omnibus)}

Rankings e frequências, calculados somente em blocos válidos:

{markdown(ranks)}

## 2. A diferença permanece após equalização?

**Não.** Nenhum dos três contrastes de IGD do C-NBI passa Holm na família
equalizada. Para HV, o C-NBI fica significativamente abaixo de NSGA-III e MOEA/D;
o contraste com VRF-NBI não é significativo. A vantagem nativa não é invariante
à cardinalidade e à regra de seleção.

K=min(N_ND dos quatro métodos) varia de3 a55, mediana12 nos135 blocos. A seleção
usa apenas ND reais, com FPS determinístico da10C na geometria normalizada,
sem referência na seleção, interpolação ou nova otimização. Extremos mínimos
por objetivo são forçados na ordem original; quando não cabem, entram os
primeiros K. Houve {int(equal.extreme_truncation.sum())} truncamentos de extremos
entre os 540 subconjuntos.
Essa regra não é invariante à permutação dos objetivos quando K é pequeno.
Os índices originais, X e F normalizado de todos os subconjuntos estão salvos
em float64. Não existem K<2 ou métricas de densidade indefinidas nesta campanha.

Fração mediana retida, por execução:

{markdown(selected_fraction)}

Assim, equalizar descarta grande parte das frentes maiores. Isso limita o
significado dessa análise secundária, mas não autoriza omitir seus resultados
desfavoráveis nem afirmar superioridade independente da cardinalidade.

## 3. Dimensão, excesso dimensional e correlação

As tabelas `factor_method_summary.csv`, `factor_marginal_contrasts.csv` e
`factorial_contrast_decomposition.csv` conservam todos os efeitos e interações
prespecificados, para os seis pares. A decomposição é descritiva e saturada
3x3x3:26 graus de liberdade, sem erro residual ou testes F causais.

No IGD nativo C-NBI menos NSGA-III, as diferenças medianas por nx2/3/5 são
-0.026694/-0.079969/-0.091170. A dimensão representa28.84% da variação desse
contraste na decomposição; correlação16.99%, e as interações, em conjunto,
47.71%. Para C-NBI menos MOEA/D, delta representa72.32%; a diferença por
delta1/3/5 é -0.133828/-0.273448/-0.338006. Para VRF-NBI, delta32.25% e alvo
de correlação29.72% predominam na variação do contraste IGD com C-NBI.
São associações destas geometrias fixas, sem isolamento causal dos fatores.

A correlação absoluta realizada e a média assinada observada aparecem como
covariáveis exploratórias, com Spearman e inclinações parciais ajustadas pelos
efeitos principais categóricos. Não há seleção por significância. A correlação
absoluta realizada é muito próxima do alvo; o pequeno resíduo após ajuste torna
suas inclinações em unidades brutas instáveis para interpretação. Denominadores
residuais estão registrados. Há somente uma geometria de âncoras por célula.
O número m=nx+delta+1 é derivado, não um quarto fator independente.

## 4. MOEA/D: proximidade local versus cobertura

O padrão é **compatível com boa proximidade de regiões limitadas e cobertura
inferior**: GD mediano de0.00886781 e IGD de0.32391259, frente a0.02654751 e
0.05293420 do C-NBI nativo. GD e IGD respondem a perguntas diferentes; GD
pequeno sozinho não prova cobertura. O IGD nativo do MOEA/D é pior que o do
C-NBI e NSGA-III em todas as27 células. Na cardinalidade equalizada, porém,
seu HV supera o do C-NBI, mostrando a importância do regime de representação.

Desfechos secundários, medianas das medianas de célula:

{markdown(native_secondary)}

Spacing e Sparsity descrevem geometria/densidade e dependem da cardinalidade;
não são convertidos isoladamente em uma ordem universal de qualidade.

## 5. VRF-NBI e NSGA-III conforme m

O NSGA-III supera VRF-NBI no IGD nas27 células e no HV nas26 válidas. O perfil
por m não é estritamente monotônico; cada m reúne combinações diferentes de nx
e delta. Não se atribui causalidade exclusiva ao número de objetivos. Os dados
completos de mediana e IQR entre células são:

{markdown(objective_trend_table)}

As três flags de Varimax500 da10D continuam declaradas; a10E não modifica o
último iterado, recalibra o VRF-NBI ou seleciona réplicas.

## 6. Custo relativo

O custo principal é o ciclo completo observado, incluindo inicialização,
verificação, carregamento, busca, persistência e encerramento. As razões
comparam medianas pareadas por cenário, não razões entre medianas globais.

{markdown(costs)}

C-NBI/NSGA-III tem intervalo abrangendo1; não há suporte aqui para afirmar
vantagem consistente de tempo do C-NBI sobre NSGA-III. C-NBI/VRF-NBI é maior
que1 e C-NBI/MOEA/D menor que1 na análise de estabilidade observada.
Worker, ciclo completo, avaliações vetoriais, valores escalares, gradientes,
subproblemas e otimizações internas continuam separados em
`quality_cost_replica.csv` e na tabela nativa completa. Ambos os EAs realizaram
18701400 NFE de busca; isso não equipara esforço com os kernels NBI/VRF.
O C-NBI resolveu444331 subproblemas NBI e1980000 otimizações MC de âncoras.
Os tempos refletem a concorrência original de até seis processos no i5-12400F
e o overhead da instrumentação; não são medições isoladas em máquina ociosa.
Não se conclui eficiência superior apenas por tempo ou contagem.

## 7. Sensibilidade à viabilidade estrita

Todas as15.489 exclusões C-NBI e10 VRF-NBI passam a ser viáveis em epsilon=1e-10
na norma; epsilon=1e-9 produz os mesmos conjuntos. ND C-NBI passa de156789
para157058 (+269); VRF-NBI de2011 para2018 (+7). Muitos pontos brutos adicionais
não acrescentam ND por identidade ou dominância. Os EAs permanecem iguais.

{markdown(totals)}

Maiores mudanças por execução, preservando os pares com HV numericamente válido:

{markdown(changes)}

Os sinais e as decisões Holm dos contrastes nativos C-NBI versus cada comparador
em IGD/HV permanecem em todos os epsilons. As famílias suplementares têm35
hipóteses cada, diferentes da família primária14; p ajustados não devem ser
comparados como se fossem a mesma família. Nenhum resultado estrito é substituído.

O padrão é compatível com a precisão/aceitação numérica dos solvers. O NBI
original usa ftol=1e-11 e margem de esfera quadrática1e-9; VRF-NBI aceita norma
até alpha+1e-8 em etapas relevantes. As violações observadas, até cerca de1e-11
na norma, são menores que essas margens. Norma e margem quadrática têm unidades
diferentes. Isso não identifica a origem de cada ULP; arredondamento também
contribui. Nenhuma decisão foi projetada ou alterada.

## 8. Precisão do HV

Os dois valores oficiais continuam PRECISION_PENDING. O estudo suplementar
com quatro scrambles originais, ponto r=(1.1,...,1.1) e2^20 pontos por scramble
passou nos critérios originais para ambos:

{markdown(hv_table)}

A tabela guarda também os níveis13-20 e a investigação em2^18. A análise
suplementar válida de27 células preserva os sinais e decisões de C-NBI versus
os três comparadores em HV. A análise provisória com estimativas pendentes
originais está separada e nunca é apresentada como a análise principal.
Na equalização,298 HV passaram QMC,240 foram exatos e2 permanecem pendentes;
a célula completa é igualmente excluída da inferência principal equalizada.

A precisão satisfaz os critérios numéricos congelados dos contrastes apresentados;
não se trata de integração exata em alta dimensão. Os quatro scrambles oferecem
diagnóstico limitado e os intervalos por cenário não propagam integralmente
incerteza de integração. Resultados muito próximos devem ser interpretados com
cautela; não há garantia de invariância de cada ranking individual à integração.

## 9. Evidência estatística sustentada

Os seis contrastes primários nativos C-NBI/comparador passam Holm conjunto no
desenho observado. Os dois Friedman primários também rejeitam a igualdade de
rankings, usando p por permutação. Após equalização, não há vantagem de IGD do
C-NBI e há desvantagem de HV frente a NSGA-III/MOEA/D nas famílias exploratórias.
O contraste IGD nativo VRF-NBI/MOEA/D não passa a família primária de Holm;
não se infere uma ordem completa de todos os pares a partir dos rankings médios.
Todos os seis pares, resultados não significativos e cenários desfavoráveis são
mantidos em `statistical_tests.csv` e nas diferenças pareadas.

## 10. Limitações para o artigo

- Desenho fixo27 células e uma geometria por célula; sem generalização universal
  ou efeito causal separado de dimensão, correlação e geometria.
- Cinco réplicas aninhadas e medianas por célula; os intervalos reponderam
  cenários, não estimam toda a incerteza de novas geometrias ou novos ruídos.
- Protocolo10E posterior à descrição10D; hipóteses dos testes e multiplicidade
  explícitas, sem alegação de pré-registro anterior à campanha.
- HV primário26 células; célula incompleta excluída pode estar associada à
  dificuldade numérica. Sensibilidade27 células resolve parte dessa limitação.
- Referência discreta5000 pontos, métricas euclidianas dependentes da dimensão,
  QMC finito e ausência de propagação completa de sua incerteza aos testes.
- Equalização é severa e condicionada ao FPS/extremos em ordem dos objetivos;
  não simula um novo algoritmo sob orçamento diferente.
- Cardinalidade nativa e esforços internos distintos; NFE não é moeda comum.
- Tempos com concorrência e profiling; flags Varimax e margens de viabilidade
  originais permanecem visíveis. Calibrações EA transferidas não provam ótimo
  universal de configuração e não foram reajustadas.
- Significância condicional e intervalos pontuais não estabelecem superioridade
  universal, causalidade ou vantagem para todas as instâncias.

## Reprodutibilidade, auditoria e qualidade

Protocolo: `docs/policies/synthetic_analysis_10e.json`. Definições/derivações:
`docs/mathematics/synthetic_statistical_analysis.md`. Sementes por teste,
versões, índices e hashes são exportados. `native_replica_metrics.csv` preserva
as540 linhas oficiais; equalização540 linhas; viabilidade2160 linhas.
A auditoria independente passou{audit["subsets"]} subconjuntos e135 blocos,
com{audit["protected_original_files"]} arquivos anteriores preservados. Derivação
offline:{derive["wall_seconds"]:.3f}s; auditoria:{audit["wall_seconds"]:.3f}s.
Nenhum dado original ou licença excluída foi modificado. Todos os resultados
anteriores, inclusive campaign_v1, permanecem preservados e fora da amostra10E.

Qualidade local registrada:

{markdown(quality_table)}
CI Ubuntu/Windows é exigida no SHA final e registrada no PR empilhado da10E;
não confundir a CI do PR17 com a do novo head. Nenhum merge automático.

Onze figuras EN, PNG600dpi/PDF vetorial, sem grades, com QA visual e hashes em
`figures/figure_provenance.json`. As figuras de ranking deixam o HV pendente
ausente. Catálogo e comandos no README do arquivo de análise.

## Tabela completa das27 células nativas

Cada entrada é mediana de cinco réplicas; HV pendente permanece ausente.

"""
    wide_tables = []
    for metric in ("IGD", "HV"):
        w = (
            summary[(summary.analysis == "native_primary") & (summary.metric == metric)]
            .pivot(index="scenario_id", columns="method", values="median")
            .reindex(columns=METHODS)
        )
        w.columns = [f"{metric} {m}" for m in w.columns]
        wide_tables.append(w)
    complete = pd.concat(wide_tables, axis=1).sort_index().reset_index()
    body += markdown(complete) + "\n"
    for old, replacement in {
        "PR17": "PR #17",
        "branch10D": "branch da Fase 10D",
        "MDR0017": "MDR 0017",
        "da10E": "da Fase 10E",
        "da10D": "da Fase 10D",
        "da10C": "da Fase 10C",
        "as27": "as 27",
        "nas27": "nas 27",
        "nas26": "nas 26",
        "entre540": "entre 540",
        "de0.": "de 0.",
        "a0.": "a 0.",
        "frente a0.": "frente a 0.",
        "versão10E": "versão 10E",
        "x5": "x 5",
        "x4": "x 4",
    }.items():
        body = body.replace(old, replacement)
    (ROOT / "docs/phase_10e_verification.md").write_bytes(body.encode())
    (OUTPUT / "README.md").write_bytes(
        b"""# Phase10E synthetic analysis

Independent offline analysis of Phase10D campaign_v2 at5c3829db.27 structural
cells x5 paired replicas x4 methods. No optimizer or original-response fit.
Native is primary; equalized and numerical sensitivities are secondary.
See docs/phase_10e_verification.md for all ten scientific questions, including
the loss of C-NBI's IGD advantage and inferior HV after equalization.

Reproduce from the preserved completed campaign, using the locked environment:

Set OPENBLAS_NUM_THREADS, OMP_NUM_THREADS and MKL_NUM_THREADS to1 before step1.

1. `uv run python scripts/validation/phase10e_derive.py --workers 4`
2. `uv run python scripts/validation/phase10e_statistics.py`
3. `uv run python scripts/validation/phase10e_audit.py`
4. `uv run python scripts/validation/phase10e_figures.py`
5. `uv run python scripts/validation/phase10e_report.py`
6. `uv run python scripts/validation/phase10e_finalize.py`
7. `uv run python scripts/validation/phase10e_finalize.py --verify`

Original outputs are never overwritten. Snapshot creation is a separate initial
operation, already frozen in Git; do not recreate the input manifest. Derived
NPZ replay checks exact row IDs and values before reusing an existing subset.
Wall-time observations differ across reproductions; scientific values/seeds do not.

Tables: native/equalized/feasibility replica metrics; all scenario medians,
six-pair differences, exact Wilcoxon/Friedman/Holm, bootstrap CIs/seeds, ranks,
fixed-factor main/interaction decomposition, signed/absolute covariates,
quality/cost counters and paired lifecycle ratios. All135 selected-index blocks
are represented by540 float64 subset NPZs. K has no random seed; first raw IDs
and objective order break exact ties. Original strict and pending HV stay intact.
The two supplementary HV evaluations pass at2^20 but never promote official status.

Figures (each PNG600 and vector PDF): igd_by_dimension, hv_by_objectives,
scenario_rankings, igd_native_equalized, hv_native_equalized,
structural_correlation_effects, method_dimension_interactions, quality_time,
cardinality_influence, feasibility_tolerance_sensitivity, paired_confidence_intervals.

Hashes: checksums.sha256, frozen_inputs_manifest.json, generation_manifest.json.
Public synthetic derivatives are explicitly requested in Phase10E; no original
raw data, protected literature PDF or excluded-material license is republished
or relicensed by this archive. MIT scope remains unchanged.
"""
    )


if __name__ == "__main__":
    report()
