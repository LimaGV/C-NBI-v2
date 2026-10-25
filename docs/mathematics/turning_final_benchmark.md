# Fase8 — correção do baseline operacional standalone

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

| Variant | N | GD | IGD | HV estimate | Spacing | Sparsity |
|---|---|---|---|---|---|---|
| Native | 409 | 0.0394917342 | 0.141143732 | 0.739028525 | 0.0321274244 | 0.0387891739 |
| K66 | 66 | 0.0432970632 | 0.160237687 | 0.673161931 | 0.056733601 | 0.223549913 |

## Comparação nativa com alvo histórico fixo

| Method | N ND | GD | IGD | HV estimate | Spacing | Sparsity |
|---|---|---|---|---|---|---|
| CNBI5 | 409 | 0.00210207344 | 0.126956844 | 0.739028525 | 0.0321274244 | 0.0387891739 |
| VRF | 66 | 0.00108794394 | 0.274519431 | 0.491567866 | 0.00665316046 | 0.0930686674 |
| NSGA3 | 330 | 0.00597183765 | 0.0788034094 | 0.769570317 | 0.0492510857 | 0.0530612513 |
| MOEAD | 327 | 0 | 0.184477648 | 0.661578496 | 0.0429353379 | 0.016129703 |

## K66 com alvo histórico fixo

| Method | N ND | GD | IGD | HV estimate | Spacing | Sparsity |
|---|---|---|---|---|---|---|
| CNBI5 | 66 | 0.00414168426 | 0.152271779 | 0.673161931 | 0.056733601 | 0.223549913 |
| VRF | 66 | 0.00108794394 | 0.274519431 | 0.491567866 | 0.00665316046 | 0.0930686674 |
| NSGA3 | 66 | 0.0109365035 | 0.115292358 | 0.682173497 | 0.0450413322 | 0.216513574 |
| MOEAD | 66 | 0 | 0.190452919 | 0.655900341 | 0.0773720407 | 0.086600576 |

EAs:medianas de30 runs; distribuições/IQR estão nos CSVs. CNBI e VRF são
observações únicas. GD zero MOEAD é consequência de auto-inclusão no alvo
histórico, não prova de convergência independente. Ordenações dos outros
métodos não mudaram. FPS novo usa409 pontos genuínos, extremos e desempate
determinístico já definidos. K=20/30/40/50/66/100/150/200/250/300/303;
Kmax comum303 continua o mínimo real; VRF encerra em66. Todos os alvos são
completos nas curvas. ReduçãoK não recebe artificialmente o tempo do solve.

## Impacto antigo versus standalone — alvo independente

| Metric | Old H5-from-H20 | Standalone H5 | Delta |
|---|---|---|---|
| N_unique_ND | 408 | 409 | 1 |
| GD | 0.0395671528 | 0.0394917342 | -7.54185833e-05 |
| IGD | 0.167646775 | 0.141143732 | -0.0265030432 |
| HV | 0.667336813 | 0.739028525 | 0.0716917123 |
| Spacing | 0.0318252849 | 0.0321274244 | 0.000302139518 |
| Sparsity | 0.0373044091 | 0.0387891739 | 0.00148476483 |

Os492 pares são listados em parent_vs_standalone_all492.csv e os24 divergentes
em historical_24_divergent_cases_named.csv:subset,beta,composição,parent row,distâncias
Linf/L2 em x e oito z,delta t e dominância nos dois sentidos com a tolerância
congelada.468 coincidentes/24 divergentes; máximoΔx3.1181207107 e
máximoΔz0.5942667068. Trajetórias de continuação distintas atingem branches
locais factíveis. O diagnóstico explica a correção; não seleciona o baseline.

## Resoluções independentes e custo

| H | Subproblems | Accepted | Unique | ND | GD | IGD | HV | Spacing | Sparsity |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 165 | 165 | 84 | 83 | 0.0430041168 | 0.216970517 | 0.548162367 | 0.0675401232 | 0.0573622067 |
| 4 | 365 | 365 | 284 | 282 | 0.0407298962 | 0.159862855 | 0.702087119 | 0.0320658297 | 0.0408850493 |
| 5 | 492 | 492 | 411 | 409 | 0.0394917342 | 0.141143732 | 0.739028525 | 0.0321274244 | 0.0387891739 |
| 10 | 1397 | 1397 | 1316 | 1310 | 0.0392704674 | 0.0989103818 | 0.765148036 | 0.0199956801 | 0.0259587614 |
| 20 | 4557 | 4557 | 4476 | 4417 | 0.0391708757 | 0.0654449733 | 0.83102799 | 0.0125130503 | 0.0169743058 |

GD/IGD da tabela acima usam R_minus_CNBI,18503 pontos. Zero falhas em todo H.

| H | Time/s | n | Median | IQR | Min | Max |
|---|---|---|---|---|---|---|
| 2 | T_solver | 1 | 0.1278705 | not estimated | 0.1278705 | 0.1278705 |
| 2 | T_total | 1 | 0.1619907 | not estimated | 0.1619907 | 0.1619907 |
| 4 | T_solver | 1 | 0.5157723 | not estimated | 0.5157723 | 0.5157723 |
| 4 | T_total | 1 | 0.577301 | not estimated | 0.577301 | 0.577301 |
| 5 | T_solver | 5 | 1.2371551 | 0.0108254997 | 1.2327023 | 1.275901 |
| 5 | T_total | 5 | 1.3138283 | 0.0130340999 | 1.3120026 | 1.3543456 |
| 10 | T_solver | 1 | 1.9273538 | not estimated | 1.9273538 | 1.9273538 |
| 10 | T_total | 1 | 2.2143211 | not estimated | 2.2143211 | 2.2143211 |
| 20 | T_solver | 1 | 7.6987894 | not estimated | 7.6987894 | 7.6987894 |
| 20 | T_total | 1 | 9.6730097 | not estimated | 9.6730097 | 9.6730097 |

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

| r | Reference N median | GD H5 median | IGD H5 median | HV reference median |
|---|---|---|---|---|
| 5 | 3265.5 | 0.0672978676 | 0.139564683 | 0.858784146 |
| 10 | 6380.5 | 0.0546076529 | 0.140237098 | 0.876740475 |
| 15 | 9448 | 0.0488386917 | 0.140537196 | 0.885578356 |
| 20 | 12490 | 0.0446702693 | 0.140745468 | 0.891810966 |
| 25 | 15502 | 0.041537991 | 0.14095986 | 0.896453692 |
| 30 | 18503 | 0.0394917342 | 0.141143732 | 0.899406333 |

| Composition | Reference N | GD H5 | IGD H5 | HV reference |
|---|---|---|---|---|
| N | 8754 | 0.0403662247 | 0.107790282 | 0.8945298 |
| M | 9743 | 0.373089203 | 0.171262438 | 0.703503318 |
| NM | 18440 | 0.0399734952 | 0.141244763 | 0.899379612 |
| NMV | 18503 | 0.0394917342 | 0.141143732 | 0.899406333 |
| MV | 9809 | 0.267597289 | 0.170846547 | 0.745922473 |
| NV | 8817 | 0.0398844637 | 0.107817303 | 0.89455652 |

| Reference K | GD H5 | IGD H5 |
|---|---|---|
| 250 | 0.080009514 | 0.113108816 |
| 500 | 0.0675770292 | 0.113438597 |
| 1000 | 0.0523572619 | 0.111424565 |
| 2500 | 0.0431439656 | 0.109078949 |
| 5000 | 0.0402761072 | 0.108327739 |
| 10000 | 0.0395310458 | 0.116469489 |
| 18503 | 0.0394917342 | 0.141143732 |

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
