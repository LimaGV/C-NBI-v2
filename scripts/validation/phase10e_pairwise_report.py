"""Current report for the explicitly requested three independent comparisons."""

import pandas as pd
from phase10e_pairwise_inputs import COMPARATORS, OUTPUT, ROOT, read
from phase10e_report import markdown


def report():
    tests = pd.read_csv(OUTPUT / "statistical_tests.csv")
    diagnostic = pd.read_csv(OUTPUT / "selection_diagnostics.csv")
    summary = pd.read_csv(OUTPUT / "scenario_metric_summary.csv")
    audit = read(OUTPUT / "audit_report.json")
    derive = read(OUTPUT / "derivation_manifest.json")
    quality_path = OUTPUT / "quality_report.json"
    quality = read(quality_path) if quality_path.exists() else {"status": "PENDING"}
    pairs = []
    for comparator in COMPARATORS:
        rows = diagnostic[(diagnostic.comparator == comparator) & (diagnostic.method == "C-NBI")]
        pairs.append(
            dict(
                comparator=comparator,
                blocks=len(rows),
                K_min=int(rows.K.min()),
                K_median=float(rows.K.median()),
                K_max=int(rows.K.max()),
                C_NBI_retained_percent=float(100 * rows.retained_fraction.median()),
            )
        )
    result = tests[tests.variant.isin(["native", "equalized"]) & tests.metric.isin(["IGD", "HV"])]
    result = result[
        [
            "variant",
            "comparator",
            "metric",
            "n_scenarios",
            "median_difference",
            "ci_low",
            "ci_high",
            "rank_biserial",
            "wins",
            "losses",
            "p_holm",
        ]
    ]
    medians = (
        summary[summary.variant.isin(["native", "equalized"]) & summary.metric.isin(["IGD", "HV"])]
        .groupby(["comparator", "variant", "method", "metric"])["median"]
        .median()
        .unstack()
        .reset_index()
    )
    supplemental = tests[tests.variant.str.endswith("HV_supplement")][
        ["variant", "comparator", "metric", "n_scenarios", "median_difference", "p_holm"]
    ]
    body = f"""# Fase 10E - correção para equalização independente por par

Estado numérico: COMPLETED. Revisão explicitamente solicitada pelo usuário após
a análise inicial. Base preservada:784650a13afc496dab8b1cfab4a2c100a9c5539e.
Branch feature/10e-synthetic-statistical-analysis; PR18 empilhado no PR17.
Nenhum PR é integrado automaticamente. MDR0018 permanece EXPERIMENTAL.

## Procedimento vigente

Para cada cenário s e réplica r, para cada comparador A separadamente:

    K[s,r,A] = min(N_ND[C-NBI,s,r], N_ND[A,s,r]).

Ordem executada e registrada: todos os135 blocos C-NBI/VRF-NBI; depois todos
os135 C-NBI/NSGA-III; finalmente todos os135 C-NBI/MOEA/D. São405 blocos e810
subconjuntos reais, provenientes das540 buscas congeladas da10D; zero buscas
novas. Os outros dois métodos não participam da definição de K de um par.

O C-NBI tem subconjuntos diferentes conforme o comparador. Portanto não há
matriz equalizada conjunta de quatro métodos, ranking conjunto ou Friedman
equalizado. O relatório/análise de K global em statistical_20261030 permanece
byte a byte como registro anterior, substituído para a conclusão equalizada atual.
Seus resultados não são apresentados como resultados do novo procedimento.

K e retenção abaixo são estatísticas dos135 blocos de cenário/réplica de cada
par. A retenção é calculada individualmente antes de sua mediana.

{markdown(pd.DataFrame(pairs))}

O exemplo nx2_delta1_rho025/réplica1 passa de K global9 para K pareados9,32,35
nos três pares, respectivamente. Nenhum terceiro método reduz o tamanho dos
subconjuntos C-NBI/NSGA-III e C-NBI/MOEA/D.

FPS e critérios anteriores são mantidos: normalização analítica congelada,
extremos mínimos únicos na ordem dos objetivos, depois máxima distância mínima
em objetivos normalizados; empate pelo primeiro índice raw. Se os extremos
excedem K, entram os primeiros K. Não se escolhem pontos pela referência,
HV ou IGD. Não há interpolação, projeção, nova otimização ou reconstrução.
Os810 subconjuntos guardam índices originais, decisões e objetivos em float64.
Valores de métricas antigos só são reutilizados com identidade exata dos pontos,
verificada por índices e arrays; os demais usam o avaliador10C inalterado.

## Unidade, multiplicidade e precisão

Cada teste usa medianas das cinco réplicas de cada cenário estrutural. Nenhuma
das135 réplicas é tratada como um problema estrutural independente. Wilcoxon
bilateral exato condicional, efeitos rank-biserial e bootstrap pareado de50000
cenários reutilizam as funções validadas. Sementes são exportadas por papel.

Os seis contrastes equalizados (três pares x IGD/HV) recebem Holm conjuntamente
a alpha=.05. GD/Spacing/Sparsity usam família exploratória separada de nove.
A linha de base nativa pareada usa outra família de seis; o resultado primário
nativo original de14 hipóteses permanece intacto, com seus próprios p ajustados.
Os intervalos de95% são pontuais e descrevem estabilidade por cenário; não
substituem o controle de multiplicidade nem provam generalização universal.

HV exige as cinco réplicas numericamente válidas de ambos os métodos do par.
Assim C-NBI/VRF-NBI usa26 cenários; C-NBI/NSGA-III e C-NBI/MOEA/D usam27.
Os dois HV pendentes do VRF-NBI não invalidam os demais pares. As coortes nativas
e equalizadas coincidem dentro de cada par nesta revisão. IGD usa27 em todos.

## Resultados pareados

Diferenças são C-NBI menos comparador: negativo favorece C-NBI para IGD;
positivo favorece C-NBI para HV. Rank-biserial positivo favorece C-NBI em ambos.

{markdown(result)}

Com a equalização por par, C-NBI mantém diferenças favoráveis e significativas
após Holm em IGD e HV frente a NSGA-III e MOEA/D. Contra VRF-NBI, os dois
contrastes não são significativos. A conclusão anterior de desvantagem de HV
equalizado frente aos EAs pertence ao K global e não se aplica a esta revisão.
Isso documenta sensibilidade à definição de equalização; não prova que um dos
protocolos seja universalmente superior ou que o resultado nativo dependa
exclusivamente do número de pontos.

Medianas das medianas de cenário, sempre separadas por par:

{markdown(medians)}

As medianas globais acima não são substitutos da mediana das diferenças
pareadas. Um intervalo pontual de mediana pode excluir zero quando o teste
Wilcoxon/Holm não rejeita; os alvos, pressupostos e multiplicidade diferem.

## Estudo suplementar do HV

Os dois resultados oficiais continuam PRECISION_PENDING. Os valores2^20
validados anteriormente só são reutilizados no estudo suplementar após
identidade exata do conjunto original de pontos, conforme HV_supplement_identity.csv.
As inferências suplementares recebem famílias separadas de três hipóteses HV.
Nenhum status oficial ou métrica principal é promovido/substituído.

{markdown(supplemental)}

## Fatores, diversidade, cobertura e custo

As novas tabelas contêm todos os cinco indicadores, diferenças por cenário,
decomposição fatorial de efeitos principais/interações, médias absolutas e
correlações assinadas observadas. A função de decomposição e as associações
exploratórias anteriores são reutilizadas nas diferenças de cada par, sem
misturar os três subconjuntos C-NBI. Apenas cubos3x3x3 completos recebem a
decomposição saturada, sem erro residual, teste F ou interpretação causal.
Há uma única geometria de âncoras por célula; m=nx+delta+1 é derivado.

O padrão nativo de MOEA/D (GD pequeno e IGD elevado) permanece compatível com
aproximação local e cobertura limitada. A revisão pareada mostra vantagem
IGD/HV do C-NBI contra esse método mesmo com cardinalidades iguais no par.
VRF-NBI e NSGA-III continuam com resultados por dimensão/m e correlação
disponíveis nas tabelas/figuras, sem alegação de causalidade exclusiva de m.
Spacing/Sparsity permanecem secundários e dependentes da representação.

Os custos originais não mudam: razões medianas pareadas de ciclo completo
C-NBI/VRF-NBI3.129909, C-NBI/NSGA-III0.949661 e C-NBI/MOEA/D0.177158.
O intervalo C-NBI/NSGA-III [.670797,1.490046] inclui1. NFE, valores escalares,
gradientes, subproblemas e otimizações internas permanecem separados no arquivo
anterior. A equalização é pós-processamento e não equipara esforço de busca.

A sensibilidade anterior de viabilidade estrita permanece íntegra e não é
reexecutada. Ela é evidência sobre frentes nativas; não foi apresentada como
uma nova análise cruzada de todos os epsilons com os K pareados. A avaliação
principal atual usa a viabilidade estrita original, sem projeção. Todos os
limites de precisão QMC, referência discreta5000, concorrência original e flags
Varimax continuam válidos. Não se fabricam novas observações ou referências.

## Integridade e reprodução

Derivação:{derive["wall_seconds"]:.3f}s; auditoria:{audit["wall_seconds"]:.3f}s.
Auditoria aprovada em{audit["sets"]} subconjuntos,405 blocos, com replay exato
de FPS, métricas recalculadas e caches de conjuntos idênticos. Todos os
{audit["protected_previous_files"]} arquivos anteriores estão preservados,
inclusive toda a primeira análise10E. Nenhum dado original ou licença excluída mudou.

Qualidade local:

{markdown(pd.DataFrame([dict(check=k, result=str(v)) for k, v in quality.items()]))}

CI Ubuntu/Windows no SHA final é registrada no PR18 antes de marcar pronto.
Nenhuma aceitação automática de MDR, merge, nova busca, RSM ou próxima fase.
Scripts de reprodução: phase10e_pairwise_derive.py, phase10e_pairwise_statistics.py,
phase10e_pairwise_audit.py, phase10e_pairwise_figures.py, phase10e_pairwise_report.py
e phase10e_pairwise_finalize.py, em scripts/validation. Cada revisão fica em
diretório próprio; não executar o finalizador antigo sobre os artefatos históricos.

Seis figuras EN PNG600/PDF vetorial sem grades acompanham os três pares.
Arquivos completos por réplica/cenário, índices, seeds, hashes e versões no
README e manifestos de pairwise_20261030.
"""
    (ROOT / "docs/phase_10e_pairwise_verification.md").write_bytes(body.encode())
    (OUTPUT / "README.md").write_bytes(b"""# Phase10E independent pairwise correction

Current equalization: C-NBI versus VRF-NBI, then NSGA-III, then MOEA/D.
K=min(two native ND counts) independently per scenario-replica. No other method
constrains a pair. There are405 paired blocks and810 real float64 subsets.
The previous statistical_20261030 archive is preserved as the superseded
four-method cardinality analysis. Native primary results/costs are unchanged.

Use the locked environment with OPENBLAS_NUM_THREADS/OMP_NUM_THREADS/MKL_NUM_THREADS=1.
Run scripts/validation/phase10e_pairwise_{derive,statistics,audit,figures,report,finalize}.py
in that order. The input snapshot is already frozen; do not recreate it.
Finalize with --verify to check every output and protected prior file.

replica_metrics.csv:1620 rows (native/equalized, two methods per each of405 blocks).
selection_diagnostics.csv and subsets/:810 retained-index/point sets.
statistical_tests.csv: pairwise Wilcoxon/Holm/effects/CIs and bootstrap seeds.
scenario_metric_summary.csv and paired_scenario_differences.csv: full cell tables.
Factor/covariate files are recalculated for the independent pair contrasts.
HV pending is excluded by the two-method cohort only; supplementary numerical
values require exact set identity and never promote official flags.
No equalized four-method Friedman or rank is mathematically formed.

See docs/phase_10e_pairwise_verification.md for current conclusions and limitations.
Six English PNG600/vector-PDF figures, no decorative grids. Hashes, source,
versions and verification observations are recorded in the manifests. No official
optimizer or original RSM is rerun. Original data and license scope are unchanged.
""")


if __name__ == "__main__":
    report()
