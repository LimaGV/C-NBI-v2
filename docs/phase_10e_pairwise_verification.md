# Fase 10E - correção para equalização independente por par

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

| comparator | blocks | K_min | K_median | K_max | C_NBI_retained_percent |
| --- | --- | --- | --- | --- | --- |
| VRF-NBI | 135 | 3 | 12 | 55 | 4.0495868 |
| NSGA-III | 135 | 18 | 153 | 984 | 62.84153 |
| MOEA/D | 135 | 18 | 84 | 1001 | 56.910569 |

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

| variant | comparator | metric | n_scenarios | median_difference | ci_low | ci_high | rank_biserial | wins | losses | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| native | VRF-NBI | IGD | 27 | -0.21825908 | -0.24248488 | -0.16616409 | 1 | 27 | 0 | 8.9406967e-08 |
| native | VRF-NBI | HV | 26 | 0.24495928 | 0.15842348 | 0.31485596 | 1 | 26 | 0 | 8.9406967e-08 |
| native | NSGA-III | IGD | 27 | -0.063341218 | -0.089515617 | -0.042001867 | 0.97883598 | 25 | 2 | 2.0861626e-07 |
| native | NSGA-III | HV | 27 | 0.071940863 | 0.038051274 | 0.091033896 | 0.9047619 | 22 | 5 | 3.7699938e-06 |
| native | MOEA/D | IGD | 27 | -0.27344821 | -0.30781461 | -0.21345336 | 1 | 27 | 0 | 8.9406967e-08 |
| native | MOEA/D | HV | 27 | 0.15725462 | 0.12532669 | 0.17439228 | 1 | 27 | 0 | 8.9406967e-08 |
| equalized | VRF-NBI | IGD | 27 | -0.029230149 | -0.075204814 | -0.01824523 | 0.21164021 | 19 | 8 | 0.41570807 |
| equalized | VRF-NBI | HV | 26 | -0.02270116 | -0.12449521 | 0.036460651 | -0.28774929 | 13 | 13 | 0.41570807 |
| equalized | NSGA-III | IGD | 27 | -0.038435937 | -0.054145691 | -0.026509706 | 0.97883598 | 25 | 2 | 4.1723251e-07 |
| equalized | NSGA-III | HV | 27 | 0.029028548 | 0.011627896 | 0.048683732 | 0.79365079 | 20 | 7 | 0.00032933056 |
| equalized | MOEA/D | IGD | 27 | -0.25262113 | -0.28344089 | -0.1670176 | 1 | 27 | 0 | 8.9406967e-08 |
| equalized | MOEA/D | HV | 27 | 0.12198134 | 0.10147834 | 0.13898169 | 1 | 27 | 0 | 8.9406967e-08 |

Com a equalização por par, C-NBI mantém diferenças favoráveis e significativas
após Holm em IGD e HV frente a NSGA-III e MOEA/D. Contra VRF-NBI, os dois
contrastes não são significativos. A conclusão anterior de desvantagem de HV
equalizado frente aos EAs pertence ao K global e não se aplica a esta revisão.
Isso documenta sensibilidade à definição de equalização; não prova que um dos
protocolos seja universalmente superior ou que o resultado nativo dependa
exclusivamente do número de pontos.

Medianas das medianas de cenário, sempre separadas por par:

| comparator | variant | method | HV | IGD |
| --- | --- | --- | --- | --- |
| MOEA/D | equalized | C-NBI | 0.69271547 | 0.055300398 |
| MOEA/D | equalized | MOEA/D | 0.58553543 | 0.32391259 |
| MOEA/D | native | C-NBI | 0.80296565 | 0.052934202 |
| MOEA/D | native | MOEA/D | 0.58553543 | 0.32391259 |
| NSGA-III | equalized | C-NBI | 0.75233427 | 0.066479761 |
| NSGA-III | equalized | NSGA-III | 0.67186375 | 0.13424797 |
| NSGA-III | native | C-NBI | 0.80296565 | 0.052934202 |
| NSGA-III | native | NSGA-III | 0.67186375 | 0.13402653 |
| VRF-NBI | equalized | C-NBI | 0.49672423 | 0.24016295 |
| VRF-NBI | equalized | VRF-NBI | 0.53433976 | 0.25777247 |
| VRF-NBI | native | C-NBI | 0.80455647 | 0.052934202 |
| VRF-NBI | native | VRF-NBI | 0.53433976 | 0.25777247 |

As medianas globais acima não são substitutos da mediana das diferenças
pareadas. Um intervalo pontual de mediana pode excluir zero quando o teste
Wilcoxon/Holm não rejeita; os alvos, pressupostos e multiplicidade diferem.

## Estudo suplementar do HV

Os dois resultados oficiais continuam PRECISION_PENDING. Os valores2^20
validados anteriormente só são reutilizados no estudo suplementar após
identidade exata do conjunto original de pontos, conforme HV_supplement_identity.csv.
As inferências suplementares recebem famílias separadas de três hipóteses HV.
Nenhum status oficial ou métrica principal é promovido/substituído.

| variant | comparator | metric | n_scenarios | median_difference | p_holm |
| --- | --- | --- | --- | --- | --- |
| native_HV_supplement | VRF-NBI | HV | 27 | 0.25186559 | 4.4703484e-08 |
| native_HV_supplement | NSGA-III | HV | 27 | 0.071940863 | 3.7699938e-06 |
| native_HV_supplement | MOEA/D | HV | 27 | 0.15725462 | 4.4703484e-08 |
| equalized_HV_supplement | VRF-NBI | HV | 27 | 0.0013529454 | 0.23857179 |
| equalized_HV_supplement | NSGA-III | HV | 27 | 0.029028548 | 0.00021955371 |
| equalized_HV_supplement | MOEA/D | HV | 27 | 0.12198134 | 4.4703484e-08 |

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

Derivação:43.999s; auditoria:32.302s.
Auditoria aprovada em810 subconjuntos,405 blocos, com replay exato
de FPS, métricas recalculadas e caches de conjuntos idênticos. Todos os
7795 arquivos anteriores estão preservados,
inclusive toda a primeira análise10E. Nenhum dado original ou licença excluída mudou.

Qualidade local:

| check | result |
| --- | --- |
| status | PASSED |
| pytest_passed | 910 |
| pytest_seconds | 144.19 |
| coverage_percent | 98.3 |
| uv_sync_locked | PASSED |
| Ruff | PASSED |
| mypy | PASSED (84 source files) |
| CI | Ubuntu/Windows on exact final PR18 head required before review readiness |

CI Ubuntu/Windows no SHA final é registrada no PR18 antes de marcar pronto.
Nenhuma aceitação automática de MDR, merge, nova busca, RSM ou próxima fase.
Scripts de reprodução: phase10e_pairwise_derive.py, phase10e_pairwise_statistics.py,
phase10e_pairwise_audit.py, phase10e_pairwise_figures.py, phase10e_pairwise_report.py
e phase10e_pairwise_finalize.py, em scripts/validation. Cada revisão fica em
diretório próprio; não executar o finalizador antigo sobre os artefatos históricos.

Seis figuras EN PNG600/PDF vetorial sem grades acompanham os três pares.
Arquivos completos por réplica/cenário, índices, seeds, hashes e versões no
README e manifestos de pairwise_20261030.
