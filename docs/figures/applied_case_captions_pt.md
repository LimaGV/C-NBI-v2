# Legendas — caso aplicado C-NBI v2

## A1 — Mapas de contorno das superfícies de resposta

Avaliação visual dos coeficientes quadráticos congelados no plano x₃=0, dentro da seção circular da esfera. Cada resposta usa sua própria escala em valores naturais; cores entre respostas não são quantitativamente comparáveis. A linha tracejada delimita a seção e a cruz marca o centro. Não houve novo ajuste RSM.

## A2 — Matriz payoff normalizada das otimizações individuais

Linhas: âncoras nominais; colunas: respostas atingidas. A payoff armazenada foi transposta apenas para apresentação. Normalização global nominal fixa, orientação MIN: zero é o ideal individual e um é o pior valor entre âncoras para aquela resposta. Não é a normalização de desempenho visual das coordenadas paralelas.

## A3 — Assimetria dos custos cruzados normalizados

Diagnóstico visual suplementar de assimetria: Cᵢⱼ=Zⱼᵢ−Zᵢⱼ, em que a payoff Z tem respostas nas linhas e âncoras nas colunas. A diagonal é zero. O sinal compara custos cruzados nas amplitudes nominais; não representa correlação, dominância ou nova métrica de benchmark.

## B1 — Ótimos individuais no espaço codificado dos fatores

Oito ótimos nominais em três projeções do espaço codificado. A circunferência tracejada é a projeção da esfera, não uma transformação para unidades físicas. x₁=Vc (cs), x₂=f e x₃=ap (md) conforme a auditoria canônica; não existe inversa contínua física verificada.

## B2 — Projeção dos ótimos individuais no espaço normalizado das respostas

Projeção linear dos oito vetores de resposta das âncoras. A PCA foi ajustada uma única vez à referência independente de 18.503 pontos no espaço MIN global fixo, sem padronização adicional. Os percentuais são da referência; distâncias e dominância em oito dimensões não se preservam integralmente em duas.

## B3 — Estrutura dos subconjuntos selecionados

Matriz binária dos 37 subconjuntos congelados: 19 pares seguidos de 18 trios em ordem lexicográfica. A separação horizontal distingue as dimensões; as barras mostram frequências marginais, não importância causal ou desempenho.

## B4 — Rede de coocorrência das respostas nos subconjuntos selecionados

Layout circular determinístico na ordem canônica. A largura das arestas representa o número de subconjuntos em que duas respostas coexistem; a área dos nós cresce com a frequência marginal. A rede resume seleção, não associação estatística entre respostas.

## B5 — Espectro singular e limiar de incerteza da análise paralela

Espectro global nominal e limiares q95 de incerteza já armazenados para B=2000. Dois componentes excedem os limiares. Terminologia: PA calibrada pela incerteza/inspirada em análise paralela; não é uma nova execução MC nem uma análise de Horn.

## B6 — Geometria local do CHIM e direções NBI

Primeiro e último par e trio em ordem lexicográfica, selecionados sem usar desempenho. Estrelas: âncoras; segmento/triângulo: CHIM; cruzes: pesos H5; círculos laranja: soluções locais aceitas do H5 standalone. Pares usam respostas locais normalizadas; trios usam coordenadas SVD intrínsecas. Nos trios a normal é perpendicular ao plano e sua projeção é nula: ⊙ indica essa direção, e o painel t mostra o deslocamento que a projeção omite. A geometria nominal histórica é usada sem soluções ou trajetória H20.

## C1 — Estimativas e intervalos de confiança dos coeficientes RSM

Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

## C2 — Coeficientes RSM divididos pelo erro padrão

Quantidade visual adimensional β̂/SE, preservando o sinal. Não são coeficientes padronizados por uma escala física comum e não se infere significância por magnitude da cor. A covariância é a mesma usada no painel Wald. O intercepto foi omitido deste heatmap para tornar visíveis os efeitos dos nove termos de fatores; permanece nos forest plots e tabelas. Valores com sinal nas células são β/SE arredondados a uma casa decimal; os valores completos permanecem na tabela de desenho.

## C3 — Propagação da incerteza das âncoras no espaço de decisão

As 2.000 reotimizações já armazenadas de cada âncora são mostradas nas três projeções codificadas. Estrela escura: ótimo nominal; nuvem magenta: MC. O contorno tracejado é a esfera projetada. As nuvens são propagação do ensemble congelado, não nova amostragem ou intervalos frequencistas exatos.

## C4 — Incerteza Monte Carlo dos ótimos individuais

Cada par de respostas mostra as 2.000 avaliações da payoff própria de cada reotimização, nuvens transparentes, âncoras nominais escuras e centros MC (+). Elipses de incerteza de 95% baseadas na covariância da amostra MC: média aritmética, covariância com divisor n−1 e χ²₂(0,95). São resumos descritivos sob aproximação elíptica; não são regiões de confiança exatas, nem intervalos de confiança para a média.

## C5 — Incerteza das âncoras e geometria local do CHIM

Os mesmos subconjuntos determinísticos de B6, combinados com as projeções das payoff MC das respectivas âncoras. Normalização local nominal e base geométrica fixas; não se refaz normalização por réplica. Elipses: média e covariância amostral das 2.000 projeções, nível 95%, χ²₂, interpretação descritiva. A projeção intrínseca dos trios omite a componente normal, indicada por ⊙.

## C6 — Propagação da incerteza na matriz payoff

Média e amplitude interquantil q95−q05 das 2.000 payoff MC armazenadas, normalizadas pelo mesmo ideal/amplitude nominal fixo da Fase 5. Linhas: âncoras; colunas: respostas. Escalas de cor distintas, sem clipping. A amplitude interquantil não é um intervalo de confiança exato.

## C7 — Estabilização da propagação Monte Carlo

Checkpoints armazenados B=100,…,2000. Erros de Frobenius da média/covariância dos coeficientes, dimensão global, gaps g1/g2 e máxima variação monitorada na janela. Linha pontilhada em 1300 e janela 1100–1300: primeiro stop retrospectivo da política revisada no caso aplicado; linha horizontal 0,05: tolerância congelada. B_stop=1300 é resultado deste caso, não constante universal nem validação externa da política. Os erros comparam a média MC com β nominal e a covariância MC com Σ̂e ⊗ Vx analítica, como nos checkpoints originais.

## D1a — Coordenadas paralelas: referência e C-NBI

Referência independente de 18.503 pontos, sem CNBI, e os 409 ND do H5 standalone. Transformação visual comum pᵢ=(hiᵢ−zᵢ)/(hiᵢ−loᵢ), com limites dos candidatos canônicos completos mais o H5 atual; zero é pior e um é melhor no conjunto desses limites. Essa transformação não substitui a normalização oficial das métricas. Transparências não codificam probabilidades.

## D1b — Coordenadas paralelas das soluções não dominadas

Desempenho visual na mesma transformação de D1a, com H5 standalone, VRF-NBI e uma run arquivada por EA. A seleção visual dos EAs minimiza o IGD nativo já registrado no alvo comum histórico, com desempate pela seed. Não representa as 30 runs, sua mediana ou uma nova execução.

## D2 — Projeções bidimensionais da fronteira empírica

Projeções em valores naturais das respostas canônicas, sem rescalagem pela nota da Tabela 3. Cinza: referência independente; laranja: H5 standalone; azul: VRF-NBI; verde/vermelho: runs EA selecionadas somente pelo IGD congelado. Uma projeção bidimensional não certifica dominância em oito respostas. ROI/OEE permanecem como razões, sem conversão silenciosa para porcentagem.

## D3 — Comparação por método e projeção

As mesmas soluções representativas e pares de D2, separadas por método sobre a referência independente cinza. Evita sobreposição entre métodos. As cardinalidades nativas diferem; esta figura ilustra regiões, não é comparação com cardinalidade controlada.

## D4 — Projeção PCA da fronteira em oito objetivos

Uma única PCA centrada na referência independente, no espaço global MIN, aplicada sem refit a todos os métodos. Percentuais nos eixos: variância da referência. Métodos usam os mesmos representantes de D2; a projeção não substitui métricas nem preserva integralmente a ordem de Pareto.

## D5 — Contribuição exclusiva ao envelope empírico histórico

Proveniência histórica da Fase 7 no envelope comum de 22.523 pontos. A barra CNBI corresponde à família H20 histórica, não aos 409 pontos do baseline atual. Contagens e percentuais exclusivos são copiados dos artefatos congelados; contribuição não é qualidade absoluta ou atribuição causal.

## E1 — IGD em função da cardinalidade da aproximação

IGD congelado contra o mesmo alvo comum histórico completo de 22.523 pontos. Curvas EA: mediana e IQR de 30 runs; CNBI: H5 standalone; VRF-NBI: frente única até K=66. Reduções FPS são aninhadas e preservam extremos, sem duplicar pontos. Linha vertical em K=66. O alvo histórico contém famílias avaliadas; não é a referência independente do CNBI ou uma frente verdadeira.

## E2 — Hipervolume em função da cardinalidade da aproximação

Mesmo controle de cardinalidade de E1. HV estimado com o ponto de referência e as quatro redes Sobol comuns congeladas, sem novo cálculo científico da métrica. EAs: mediana/IQR de 30 runs. O alvo GD/IGD não entra na definição de HV; o estimador tem resolução finita.

## E3 — Efeito da cardinalidade sobre as métricas de distribuição

Spacing e Sparsity congelados em função de K. Spacing é o desvio padrão amostral das distâncias Euclidianas ao vizinho mais próximo (ddof1); Sparsity é sua média. EAs: mediana/IQR de 30 runs. Ambas dependem da densidade; valores baixos não demonstram cobertura ou convergência.

## F1 — Qualidade da aproximação em função do tempo computacional

Qualidade e tempo da mesma configuração científica: cada H é standalone, H5 destacado por estrela, cinco repetições H5 idênticas e uma observação nos demais H. EAs: medianas/IQR de dez seeds da campanha controlada, checkpoints 50/100/200/300/400. IGD usa o alvo comum histórico; HV usa o ponto/estimador comum. Campanhas têm datas próprias, mesma máquina/ambiente; não são p-valores ou equivalência por NFE. VRF-NBI não tem tempo reproduzível.

## F2 — Tempo total de processamento

Tempos end-to-end congelados, sem equivalência artificial por NFE. Pontos: medições; traço: mediana; barra: IQR quando há repetições. H5 n=5, outros H n=1, EAs n=10. Não se inventa variabilidade para n=1, e VRF-NBI não é incluído por ausência de timing reproduzível.

## F3 — Ganho marginal de qualidade por custo computacional

Diagnóstico visual suplementar entre H consecutivos: (IGD_Ha−IGD_Hb)/(t_Hb−t_Ha) e (HV_Hb−HV_Ha)/(t_Hb−t_Ha). IGD usa a referência independente sem CNBI; tempos são os já medidos, com mediana em H5 e observação única nos demais. Não são novas métricas principais ou estimativas causais de eficiência.

## G1 — Sensibilidade do IGD ao número de execuções usadas na referência

IGD do mesmo H5 standalone contra referências sem CNBI, reutilizando as 100 subamostras pareadas existentes em r=5/10/15/20/25 e uma referência completa em r=30. Curva: mediana; faixa: q05–q95; pontos: subamostras armazenadas, sem jitter. A faixa é dispersão de subconjuntos, não intervalo de confiança.

## G2 — Sensibilidade do GD ao número de execuções usadas na referência

Mesmas referências e distribuições de G1, mostrando GD do H5 standalone. Nenhuma subamostra foi gerada novamente. Redução de GD com mais runs não certifica convergência à frente verdadeira.

## G3 — Crescimento da referência empírica

Cardinalidade e HV da referência sem CNBI nas mesmas subamostras existentes. Mediana e q05–q95, com referência única em r=30. O crescimento do número de pontos e a mudança do envelope geométrico são fenômenos distintos; não se declara saturação certificada.

## G4 — Sensibilidade à cardinalidade da referência empírica

Sete prefixos FPS já congelados da referência independente; H5 avaliado é fixo. GD/IGD são dependentes do alvo e HV pertence à referência reduzida. A redução é análise de sensibilidade; as comparações de métodos mantêm o alvo completo.

## G5 — Sensibilidade à composição da referência empírica

Referências N, M, NM e NMV já armazenadas, sempre sem CNBI. Painéis: IGD/GD do H5 standalone e HV da própria referência. A composição e densidade mudam o alvo; não se interpretam contribuições marginais como importância universal de um método.

## H1 — Distribuição das distâncias ao vizinho mais próximo

Distâncias ao vizinho mais próximo no espaço global MIN, calculadas apenas para diagnóstico visual. CNBI e VRF-NBI são frentes únicas; EAs agregam distâncias calculadas dentro de cada uma das 30 runs genuínas. Violinos resumem pontos, não 30 observações independentes de qualidade; barras internas mostram mediana/IQR. Cardinalidades nativas diferem.

## H2 — Densidade local na projeção PCA da referência

Densidade kNN (k=15) na projeção PCA bidimensional da referência, exibida como log(1+k/(πr_k²)); pontos laranja são o H5 standalone. A base PCA é a mesma dos demais painéis. Densidade projetada não é densidade em oito dimensões, cobertura de Pareto ou nova métrica principal.

## H3 — Distribuição das soluções no espaço de decisão

Projeções das decisões codificadas das mesmas frentes representativas de D2. Contorno tracejado: esfera projetada. Os nomes dos fatores seguem a ordem auditada, sem inferir coordenadas físicas para novas soluções. Diferentes regiões projetadas não demonstram, isoladamente, melhor qualidade multiobjetivo.

## I1 — Fluxo metodológico do caso aplicado

Fluxograma vetorial do pipeline já executado: dados, oito RSMs, covariância, ensemble de coeficientes, reotimizações/ payoff MC, CHIM/SVD/PA, 37 subsets, H5 standalone e benchmark. O gráfico descreve etapas concluídas; não as executa novamente e não inclui refinamento adaptativo.

## J1 — Síntese visual do caso aplicado

Síntese dos dados já apresentados: payoff global normalizada, um CHIM local representativo, projeção T×Kp das frentes e IGD×tempo no alvo comum histórico. Mesmas transformações e representantes dos painéis individuais. A síntese não substitui as figuras completas ou suas limitações.

## C1_T — Coeficientes e intervalos Wald de 95% — T

Painel individual para T; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

## C1_MTTF — Coeficientes e intervalos Wald de 95% — MTTF

Painel individual para MTTF; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

## C1_WR — Coeficientes e intervalos Wald de 95% — WR

Painel individual para WR; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

## C1_Ra — Coeficientes e intervalos Wald de 95% — Ra

Painel individual para Ra; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

## C1_Rt — Coeficientes e intervalos Wald de 95% — Rt

Painel individual para Rt; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

## C1_Kp — Coeficientes e intervalos Wald de 95% — Kp

Painel individual para Kp; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

## C1_ROI — Coeficientes e intervalos Wald de 95% — ROI

Painel individual para ROI; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

## C1_OEE — Coeficientes e intervalos Wald de 95% — OEE

Painel individual para OEE; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.

