# Fase 10E - análise científica dos resultados sintéticos

Estado numérico: **COMPLETED**. Campanha de entrada: somente `campaign_v2`,
commit `5c3829dbd1bdd41ee828cfaf919c551d4f869d32`, PR #17 ainda separado.
Branch: `feature/10e-synthetic-statistical-analysis`, empilhada sobre a branch da Fase 10D.
Nenhuma busca oficial, ajuste RSM, calibração, referência ou seed foi reexecutado
ou alterado. MDR 0017 permanece EXPERIMENTAL até revisão explícita.

## Protocolo e unidade de análise

540 resultados: 27 células estruturais x 5 réplicas x 4 métodos; 135 blocos pareados,
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

HV principal: 26 células completas, excluindo `nx 5_delta5_rho025`, pois duas
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

| analysis | method | HV | IGD |
| --- | --- | --- | --- |
| equalized_secondary | C-NBI | 0.49672423 | 0.24016295 |
| equalized_secondary | MOEA/D | 0.59651745 | 0.33352652 |
| equalized_secondary | NSGA-III | 0.56783819 | 0.21842539 |
| equalized_secondary | VRF-NBI | 0.53433976 | 0.25777247 |
| native_primary | C-NBI | 0.80455647 | 0.052934202 |
| native_primary | MOEA/D | 0.61031589 | 0.32391259 |
| native_primary | NSGA-III | 0.71295018 | 0.13402653 |
| native_primary | VRF-NBI | 0.53433976 | 0.25777247 |

Todos os contrastes de C-NBI menos comparador, incluindo a análise secundária:
valores negativos favorecem C-NBI em IGD; positivos favorecem C-NBI em HV.
Rank-biserial positivo favorece C-NBI em ambos. Os intervalos são pontuais,
enquanto a decisão de multiplicidade usa exclusivamente p_holm.

| analysis | metric | method_b | n_scenarios | median_difference | ci_low | ci_high | p_holm | rank_biserial | wins | losses |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| native_primary | IGD | VRF-NBI | 27 | -0.21825908 | -0.24248488 | -0.16616409 | 2.0861626e-07 | 1 | 27 | 0 |
| native_primary | IGD | NSGA-III | 27 | -0.063341218 | -0.089515617 | -0.042001867 | 6.2584877e-07 | 0.97883598 | 25 | 2 |
| native_primary | IGD | MOEA/D | 27 | -0.27344821 | -0.30781461 | -0.21345336 | 2.0861626e-07 | 1 | 27 | 0 |
| native_primary | HV | VRF-NBI | 26 | 0.24495928 | 0.15842348 | 0.31485596 | 2.9802322e-07 | 1 | 26 | 0 |
| native_primary | HV | NSGA-III | 26 | 0.062025781 | 0.03629976 | 0.09010895 | 2e-05 | 0.8974359 | 21 | 5 |
| native_primary | HV | MOEA/D | 26 | 0.15559751 | 0.12091155 | 0.17154991 | 2.9802322e-07 | 1 | 26 | 0 |
| equalized_secondary | IGD | VRF-NBI | 27 | -0.029230149 | -0.075204814 | -0.01824523 | 0.69665521 | 0.21164021 | 19 | 8 |
| equalized_secondary | IGD | NSGA-III | 27 | 0.01169443 | -0.0052031617 | 0.029520433 | 0.4153617 | -0.38624339 | 11 | 16 |
| equalized_secondary | IGD | MOEA/D | 27 | -0.058651461 | -0.098477072 | -0.031744358 | 0.59260988 | 0.32275132 | 20 | 7 |
| equalized_secondary | HV | VRF-NBI | 26 | -0.02270116 | -0.12449521 | 0.036460651 | 0.6235621 | -0.28774929 | 13 | 13 |
| equalized_secondary | HV | NSGA-III | 26 | -0.050313246 | -0.070182369 | -0.028099611 | 0.00038230419 | -0.85185185 | 3 | 23 |
| equalized_secondary | HV | MOEA/D | 26 | -0.11876541 | -0.18293915 | -0.09690704 | 4.1723251e-06 | -0.97150997 | 2 | 24 |

Um intervalo pontual da mediana pode excluir zero mesmo quando Wilcoxon/Holm
não rejeita: são procedimentos com alvos e pressupostos diferentes, e somente
os p ajustados controlam a família de comparações. Não se usa o intervalo para
reclassificar um contraste ajustado não significativo.

Testes omnibus, com a família primária conjunta e a secundária separada:

| analysis | metric | n_scenarios | statistic | pvalue | p_holm |
| --- | --- | --- | --- | --- | --- |
| native_primary | IGD | 27 | 72.022222 | 5e-06 | 2e-05 |
| native_primary | HV | 26 | 67.523077 | 5e-06 | 2e-05 |
| equalized_secondary | IGD | 27 | 21.533333 | 6.5e-05 | 0.000715 |
| equalized_secondary | HV | 26 | 25.523077 | 5e-06 | 6.5e-05 |

Rankings e frequências, calculados somente em blocos válidos:

| analysis | metric | method | n_scenarios | mean_rank | best_count | fractional_best | median_of_cell_medians |
| --- | --- | --- | --- | --- | --- | --- | --- |
| native_primary | IGD | C-NBI | 27 | 1.0740741 | 25 | 25 | 0.052934202 |
| native_primary | IGD | VRF-NBI | 27 | 3.2962963 | 0 | 0 | 0.25777247 |
| native_primary | IGD | NSGA-III | 27 | 1.9259259 | 2 | 2 | 0.13402653 |
| native_primary | IGD | MOEA/D | 27 | 3.7037037 | 0 | 0 | 0.32391259 |
| native_primary | HV | C-NBI | 26 | 1.1923077 | 21 | 21 | 0.80455647 |
| native_primary | HV | VRF-NBI | 26 | 3.8461538 | 0 | 0 | 0.53433976 |
| native_primary | HV | NSGA-III | 26 | 1.8461538 | 5 | 5 | 0.71295018 |
| native_primary | HV | MOEA/D | 26 | 3.1153846 | 0 | 0 | 0.61031589 |

## 2. A diferença permanece após equalização?

**Não.** Nenhum dos três contrastes de IGD do C-NBI passa Holm na família
equalizada. Para HV, o C-NBI fica significativamente abaixo de NSGA-III e MOEA/D;
o contraste com VRF-NBI não é significativo. A vantagem nativa não é invariante
à cardinalidade e à regra de seleção.

K=min(N_ND dos quatro métodos) varia de3 a55, mediana12 nos135 blocos. A seleção
usa apenas ND reais, com FPS determinístico da Fase 10C na geometria normalizada,
sem referência na seleção, interpolação ou nova otimização. Extremos mínimos
por objetivo são forçados na ordem original; quando não cabem, entram os
primeiros K. Houve 37 truncamentos de extremos
entre os 540 subconjuntos.
Essa regra não é invariante à permutação dos objetivos quando K é pequeno.
Os índices originais, X e F normalizado de todos os subconjuntos estão salvos
em float64. Não existem K<2 ou métricas de densidade indefinidas nesta campanha.

Fração mediana retida, por execução:

| method | retained_fraction |
| --- | --- |
| C-NBI | 0.040495868 |
| MOEA/D | 0.071428571 |
| NSGA-III | 0.067961165 |
| VRF-NBI | 1 |

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
inferior**: GD mediano de 0.00886781 e IGD de 0.32391259, frente a 0.02654751 e
0.05293420 do C-NBI nativo. GD e IGD respondem a perguntas diferentes; GD
pequeno sozinho não prova cobertura. O IGD nativo do MOEA/D é pior que o do
C-NBI e NSGA-III em todas as 27 células. Na cardinalidade equalizada, porém,
seu HV supera o do C-NBI, mostrando a importância do regime de representação.

Desfechos secundários, medianas das medianas de célula:

| method | GD | N_ND | Spacing | Sparsity | observed_lifecycle_seconds |
| --- | --- | --- | --- | --- | --- |
| C-NBI | 0.026547514 | 261 | 0.033807677 | 0.045069794 | 21.189254 |
| MOEA/D | 0.0088678107 | 84 | 0.026897635 | 0.015603713 | 109.39485 |
| NSGA-III | 0.030765842 | 186 | 0.045358218 | 0.034897496 | 16.971099 |
| VRF-NBI | 0.040074591 | 11 | 0.10106689 | 0.2154445 | 5.7015445 |

Spacing e Sparsity descrevem geometria/densidade e dependem da cardinalidade;
não são convertidos isoladamente em uma ordem universal de qualidade.

## 5. VRF-NBI e NSGA-III conforme m

O NSGA-III supera VRF-NBI no IGD nas 27 células e no HV nas 26 válidas. O perfil
por m não é estritamente monotônico; cada m reúne combinações diferentes de nx
e delta. Não se atribui causalidade exclusiva ao número de objetivos. Os dados
completos de mediana e IQR entre células são:

| method | metric | level | structural_cells | median | q25 | q75 |
| --- | --- | --- | --- | --- | --- | --- |
| NSGA-III | HV | 4 | 3 | 0.89497849 | 0.83386913 | 0.94225634 |
| NSGA-III | HV | 5 | 3 | 0.82826281 | 0.81870029 | 0.85315057 |
| NSGA-III | HV | 6 | 3 | 1.0243729 | 0.81520365 | 1.1086617 |
| NSGA-III | HV | 7 | 6 | 0.71295018 | 0.65557823 | 0.80056268 |
| NSGA-III | HV | 8 | 3 | 0.84809232 | 0.72239738 | 0.93326135 |
| NSGA-III | HV | 9 | 6 | 0.54742697 | 0.52812401 | 0.55470831 |
| NSGA-III | HV | 11 | 2 | 0.45359771 | 0.44598179 | 0.46121363 |
| VRF-NBI | HV | 4 | 3 | 0.86747338 | 0.72012657 | 0.90003071 |
| VRF-NBI | HV | 5 | 3 | 0.70660094 | 0.67094651 | 0.72194926 |
| VRF-NBI | HV | 6 | 3 | 0.53231845 | 0.40460741 | 0.71084755 |
| VRF-NBI | HV | 7 | 6 | 0.59082084 | 0.52859464 | 0.65536212 |
| VRF-NBI | HV | 8 | 3 | 0.63683585 | 0.37169196 | 0.73248776 |
| VRF-NBI | HV | 9 | 6 | 0.36472345 | 0.162211 | 0.46376733 |
| VRF-NBI | HV | 11 | 2 | 0.31844119 | 0.28005228 | 0.35683009 |
| NSGA-III | IGD | 4 | 3 | 0.095356365 | 0.088675574 | 0.1150151 |
| NSGA-III | IGD | 5 | 3 | 0.11330339 | 0.083983991 | 0.13604136 |
| NSGA-III | IGD | 6 | 3 | 0.0884742 | 0.07705196 | 0.1077898 |
| NSGA-III | IGD | 7 | 6 | 0.14777175 | 0.094784823 | 0.16032449 |
| NSGA-III | IGD | 8 | 3 | 0.068187876 | 0.057106248 | 0.083787941 |
| NSGA-III | IGD | 9 | 6 | 0.16919226 | 0.15322743 | 0.19457022 |
| NSGA-III | IGD | 11 | 3 | 0.13717133 | 0.13559893 | 0.15701383 |
| VRF-NBI | IGD | 4 | 3 | 0.2088603 | 0.16611563 | 0.23216974 |
| VRF-NBI | IGD | 5 | 3 | 0.1625477 | 0.16040463 | 0.21529086 |
| VRF-NBI | IGD | 6 | 3 | 0.29838716 | 0.26063726 | 0.32112275 |
| VRF-NBI | IGD | 7 | 6 | 0.22115545 | 0.20617113 | 0.2374143 |
| VRF-NBI | IGD | 8 | 3 | 0.25629069 | 0.24496015 | 0.36930808 |
| VRF-NBI | IGD | 9 | 6 | 0.31287033 | 0.28136015 | 0.40674038 |
| VRF-NBI | IGD | 11 | 3 | 0.28958412 | 0.27774946 | 0.45213974 |

As três flags de Varimax 500 da Fase 10D continuam declaradas; a10E não modifica o
último iterado, recalibra o VRF-NBI ou seleciona réplicas.

## 6. Custo relativo

O custo principal é o ciclo completo observado, incluindo inicialização,
verificação, carregamento, busca, persistência e encerramento. As razões
comparam medianas pareadas por cenário, não razões entre medianas globais.

| method_a | method_b | n_scenarios | median_time_ratio | ratio_ci_low | ratio_ci_high | ratio_role |
| --- | --- | --- | --- | --- | --- | --- |
| C-NBI | VRF-NBI | 27 | 3.1299091 | 2.2845646 | 4.6631931 | pointwise paired scenario stability; concurrent archived hardware |
| C-NBI | NSGA-III | 27 | 0.94966094 | 0.67079703 | 1.4900464 | pointwise paired scenario stability; concurrent archived hardware |
| C-NBI | MOEA/D | 27 | 0.17715786 | 0.14018553 | 0.26329608 | pointwise paired scenario stability; concurrent archived hardware |
| VRF-NBI | NSGA-III | 27 | 0.30047817 | 0.16346703 | 0.38784465 | pointwise paired scenario stability; concurrent archived hardware |
| VRF-NBI | MOEA/D | 27 | 0.057387739 | 0.032112205 | 0.077967265 | pointwise paired scenario stability; concurrent archived hardware |
| NSGA-III | MOEA/D | 27 | 0.19098804 | 0.17834517 | 0.20762811 | pointwise paired scenario stability; concurrent archived hardware |

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

| method | epsilon | N_feasible | N_ND |
| --- | --- | --- | --- |
| C-NBI | 0 | 427608 | 156789 |
| C-NBI | 1e-12 | 442586 | 157050 |
| C-NBI | 1e-10 | 443097 | 157058 |
| C-NBI | 1e-09 | 443097 | 157058 |
| MOEA/D | 0 | 39750 | 39671 |
| MOEA/D | 1e-12 | 39750 | 39671 |
| MOEA/D | 1e-10 | 39750 | 39671 |
| MOEA/D | 1e-09 | 39750 | 39671 |
| NSGA-III | 0 | 39630 | 35335 |
| NSGA-III | 1e-12 | 39630 | 35335 |
| NSGA-III | 1e-10 | 39630 | 35335 |
| NSGA-III | 1e-09 | 39630 | 35335 |
| VRF-NBI | 0 | 2617 | 2011 |
| VRF-NBI | 1e-12 | 2622 | 2015 |
| VRF-NBI | 1e-10 | 2627 | 2018 |
| VRF-NBI | 1e-09 | 2627 | 2018 |

Maiores mudanças por execução, preservando os pares com HV numericamente válido:

| method | epsilon | added_feasible | max_absolute_IGD_change | max_absolute_HV_change_valid_pairs |
| --- | --- | --- | --- | --- |
| C-NBI | 0 | 0 | 0 | 0 |
| C-NBI | 1e-12 | 14978 | 0.0056423549 | 0.0085488307 |
| C-NBI | 1e-10 | 15489 | 0.0056423549 | 0.0085488307 |
| C-NBI | 1e-09 | 15489 | 0.0056423549 | 0.0085488307 |
| VRF-NBI | 0 | 0 | 0 | 0 |
| VRF-NBI | 1e-12 | 5 | 0.00052913367 | 0.0002068817 |
| VRF-NBI | 1e-10 | 10 | 0.00052913367 | 0.0002068817 |
| VRF-NBI | 1e-09 | 10 | 0.00052913367 | 0.0002068817 |
| NSGA-III | 0 | 0 | 0 | 0 |
| NSGA-III | 1e-12 | 0 | 0 | 0 |
| NSGA-III | 1e-10 | 0 | 0 | 0 |
| NSGA-III | 1e-09 | 0 | 0 | 0 |
| MOEA/D | 0 | 0 | 0 | 0 |
| MOEA/D | 1e-12 | 0 | 0 | 0 |
| MOEA/D | 1e-10 | 0 | 0 | 0 |
| MOEA/D | 1e-09 | 0 | 0 | 0 |

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

| replica_id | original_HV | HV_QMC | HV_QMC_SE | relative_se | relative_change_previous | min_scramble_hits | qmc_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 0.010306936 | 0.010368838 | 4.0880242e-05 | 0.003942606 | 0.0012464738 | 3780 | PRECISION_CRITERIA_PASSED |
| 3 | 0.018796282 | 0.019339791 | 3.4226532e-05 | 0.0017697468 | 0.0025676199 | 7073 | PRECISION_CRITERIA_PASSED |

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
A auditoria independente passou540 subconjuntos e135 blocos,
com7156 arquivos anteriores preservados. Derivação
offline:1036.141s; auditoria:10.130s.
Nenhum dado original ou licença excluída foi modificado. Todos os resultados
anteriores, inclusive campaign_v1, permanecem preservados e fora da amostra10E.

Qualidade local registrada:

| check | result |
| --- | --- |
| status | PASSED |
| uv_sync_locked | PASSED (131 resolved /128 checked) |
| pytest_passed | 904 |
| pytest_seconds | 143.66 |
| coverage_percent | 98.29 |
| ruff | PASSED |
| mypy | PASSED (83 source files) |
| CI | Ubuntu/Windows required on the exact final Phase10E PR head |
CI Ubuntu/Windows é exigida no SHA final e registrada no PR empilhado da Fase 10E;
não confundir a CI do PR #17 com a do novo head. Nenhum merge automático.

Onze figuras EN, PNG600dpi/PDF vetorial, sem grades, com QA visual e hashes em
`figures/figure_provenance.json`. As figuras de ranking deixam o HV pendente
ausente. Catálogo e comandos no README do arquivo de análise.

## Tabela completa das 27 células nativas

Cada entrada é mediana de cinco réplicas; HV pendente permanece ausente.

| scenario_id | IGD C-NBI | IGD VRF-NBI | IGD NSGA-III | IGD MOEA/D | HV C-NBI | HV VRF-NBI | HV NSGA-III | HV MOEA/D |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nx2_delta1_rho025 | 0.089315094 | 0.25547919 | 0.13467384 | 0.20349838 | 0.82464534 | 0.57277975 | 0.77275978 | 0.76642628 |
| nx2_delta1_rho060 | 0.055300398 | 0.12337097 | 0.081994783 | 0.18912874 | 1.0275855 | 0.93258803 | 0.9895342 | 0.96381482 |
| nx2_delta1_rho085 | 0.045597994 | 0.2088603 | 0.095356365 | 0.16804783 | 0.93514651 | 0.86747338 | 0.89497849 | 0.88475217 |
| nx2_delta3_rho025 | 0.079270792 | 0.34385835 | 0.12710541 | 0.37206598 | 0.63846587 | 0.27689636 | 0.60603438 | 0.4760516 |
| nx2_delta3_rho060 | 0.073557627 | 0.29838716 | 0.0884742 | 0.2990656 | 1.1811037 | 0.53231845 | 1.1929505 | 1.0346586 |
| nx2_delta3_rho085 | 0.041048457 | 0.22288736 | 0.065629721 | 0.41444869 | 1.0101744 | 0.88937666 | 1.0243729 | 0.88211768 |
| nx2_delta5_rho025 | 0.052934202 | 0.48232547 | 0.068187876 | 0.33637318 | 0.59490346 | 0.10654807 | 0.59670243 | 0.43764884 |
| nx2_delta5_rho060 | 0.036046789 | 0.25629069 | 0.099388007 | 0.36305627 | 0.87488882 | 0.63683585 | 0.84809232 | 0.7062925 |
| nx2_delta5_rho085 | 0.052000768 | 0.23362961 | 0.04602462 | 0.45737949 | 1.0151432 | 0.82813968 | 1.0184304 | 0.86837163 |
| nx3_delta1_rho025 | 0.078810594 | 0.26803402 | 0.15877933 | 0.18535004 | 1.0024525 | 0.63529208 | 0.87803833 | 0.84851214 |
| nx3_delta1_rho060 | 0.07130152 | 0.15826156 | 0.11330339 | 0.17349322 | 0.87602322 | 0.70660094 | 0.82826281 | 0.77281675 |
| nx3_delta1_rho085 | 0.047008272 | 0.1625477 | 0.054664596 | 0.21746229 | 0.82696651 | 0.73729759 | 0.80913776 | 0.77493015 |
| nx3_delta3_rho025 | 0.072338842 | 0.23260895 | 0.15960437 | 0.32391259 | 0.74118362 | 0.52600583 | 0.65014972 | 0.50491624 |
| nx3_delta3_rho060 | 0.057333889 | 0.20970194 | 0.1782627 | 0.3307821 | 0.90526913 | 0.64528061 | 0.81607137 | 0.69067118 |
| nx3_delta3_rho085 | 0.053984914 | 0.13141158 | 0.040359614 | 0.21522754 | 1.1719852 | 1.0064043 | 1.2058758 | 1.0582189 |
| nx3_delta5_rho025 | 0.075484916 | 0.4396029 | 0.20300078 | 0.4550553 | 0.42844301 | 0.11358705 | 0.34018548 | 0.25973548 |
| nx3_delta5_rho060 | 0.042242687 | 0.28355749 | 0.23412038 | 0.35845705 | 0.70461209 | 0.43647542 | 0.55501863 | 0.53021981 |
| nx3_delta5_rho085 | 0.038142826 | 0.28062771 | 0.084742324 | 0.34595744 | 0.61301747 | 0.47286463 | 0.5410766 | 0.49956534 |
| nx 5_delta1_rho025 | 0.080961826 | 0.34630513 | 0.16056453 | 0.25195631 | 0.72811506 | 0.2893296 | 0.58281467 | 0.44505956 |
| nx 5_delta1_rho060 | 0.043562151 | 0.2049942 | 0.13593914 | 0.25701551 | 0.80296565 | 0.53636107 | 0.67186375 | 0.58553543 |
| nx 5_delta1_rho085 | 0.048332118 | 0.23901608 | 0.081066719 | 0.30410785 | 0.8061473 | 0.65872262 | 0.7540366 | 0.63509635 |
| nx 5_delta3_rho025 | 0.081915375 | 0.42825945 | 0.16910599 | 0.31378393 | 0.67208669 | 0.11862417 | 0.52380648 | 0.37509452 |
| nx 5_delta3_rho060 | 0.046370383 | 0.34218317 | 0.16927852 | 0.33557979 | 0.70579042 | 0.29297147 | 0.57297237 | 0.4947351 |
| nx 5_delta3_rho085 | 0.031596622 | 0.25777247 | 0.14793457 | 0.30829613 | 0.64296135 | 0.53091831 | 0.55377734 | 0.56307802 |
| nx 5_delta5_rho025 | 0.085686446 | 0.61469537 | 0.17685633 | 0.42369208 | -- | -- | -- | -- |
| nx 5_delta5_rho060 | 0.047655716 | 0.2659148 | 0.13717133 | 0.43470911 | 0.62855986 | 0.24166337 | 0.46882956 | 0.4178826 |
| nx 5_delta5_rho085 | 0.036167429 | 0.28958412 | 0.13402653 | 0.4518717 | 0.514487 | 0.395219 | 0.43836587 | 0.38916031 |
