"""Scientific interpretation/limitations are localized with the plotting labels."""

NOTES = {
    "A1": (
        (
            "Avaliação visual dos coeficientes quadráticos congelados no plano x₃=0, "
            "dentro da seção circular da esfera. Cada resposta usa sua própria escala em "
            "valores naturais; cores entre respostas não são quantitativamente "
            "comparáveis. A linha tracejada delimita a seção e a cruz marca o centro. Não "
            "houve novo ajuste RSM."
        ),
        (
            "Visual evaluation of the frozen quadratic coefficients on the x₃=0 plane "
            "within the circular sphere section. Each response uses its own natural-value "
            "scale; colors across responses are not quantitatively comparable. The dashed "
            "curve delimits the section and the cross marks its center. No RSM was "
            "refitted."
        ),
    ),
    "A2": (
        (
            "Linhas: âncoras nominais; colunas: respostas atingidas. A payoff armazenada "
            "foi transposta apenas para apresentação. Normalização global nominal fixa, "
            "orientação MIN: zero é o ideal individual e um é o pior valor entre âncoras "
            "para aquela resposta. Não é a normalização de desempenho visual das "
            "coordenadas paralelas."
        ),
        (
            "Rows: nominal anchors; columns: attained responses. The stored payoff was "
            "transposed only for presentation. Fixed nominal global normalization, MIN "
            "orientation: zero is the individual ideal and one is the worst anchor value "
            "for that response. This is not the visual-performance normalization used in "
            "parallel coordinates."
        ),
    ),
    "A3": (
        (
            "Diagnóstico visual suplementar de assimetria: Cᵢⱼ=Zⱼᵢ−Zᵢⱼ, em que a payoff Z "
            "tem respostas nas linhas e âncoras nas colunas. A diagonal é zero. O sinal "
            "compara custos cruzados nas amplitudes nominais; não representa correlação, "
            "dominância ou nova métrica de benchmark."
        ),
        (
            "Supplementary visual asymmetry diagnostic: Cᵢⱼ=Zⱼᵢ−Zᵢⱼ, where payoff Z has "
            "responses in rows and anchors in columns. The diagonal is zero. The sign "
            "compares cross costs on nominal ranges; it does not represent correlation, "
            "dominance, or a new benchmark metric."
        ),
    ),
    "B1": (
        (
            "Oito ótimos nominais em três projeções do espaço codificado. A circunferência"
            " tracejada é a projeção da esfera, não uma transformação para unidades "
            "físicas. x₁=Vc/cs, x₂=f e x₃=ap/md conforme a auditoria canônica; não existe "
            "inversa contínua física verificada."
        ),
        (
            "Eight nominal optima in three coded-space projections. The dashed circle is "
            "the sphere projection, not a conversion to physical units. x₁=Vc/cs, x₂=f, "
            "and x₃=ap/md follow the canonical audit; no verified continuous physical "
            "inverse is available."
        ),
    ),
    "B2": (
        (
            "Projeção linear dos oito vetores de resposta das âncoras. A PCA foi ajustada "
            "uma única vez à referência independente de 18.503 pontos no espaço MIN global"
            " fixo, sem padronização adicional. Os percentuais são da referência; "
            "distâncias e dominância em oito dimensões não se preservam integralmente em "
            "duas."
        ),
        (
            "Linear projection of the eight anchor response vectors. PCA was fitted once "
            "to the independent 18,503-point reference in the fixed global MIN space, with"
            " no additional standardization. Percentages refer to that reference; "
            "eight-dimensional distances and dominance are not fully preserved in two "
            "dimensions."
        ),
    ),
    "B3": (
        (
            "Matriz binária dos 37 subconjuntos congelados: 19 pares seguidos de 18 trios "
            "em ordem lexicográfica. A separação horizontal distingue as dimensões; as "
            "barras mostram frequências marginais, não importância causal ou desempenho."
        ),
        (
            "Binary matrix of the 37 frozen subsets: 19 pairs followed by 18 triples in "
            "lexicographic order. The horizontal divider separates dimensions; bars show "
            "marginal frequencies, not causal importance or performance."
        ),
    ),
    "B4": (
        (
            "Layout circular determinístico na ordem canônica. A largura das arestas "
            "representa o número de subconjuntos em que duas respostas coexistem; a área "
            "dos nós cresce com a frequência marginal. A rede resume seleção, não "
            "associação estatística entre respostas."
        ),
        (
            "Deterministic circular layout in canonical order. Edge width represents the "
            "number of subsets containing both responses; node area grows with marginal "
            "frequency. The network summarizes selection, not statistical association "
            "between responses."
        ),
    ),
    "B5": (
        (
            "Espectro global nominal e limiares q95 de incerteza já armazenados para "
            "B=2000. Dois componentes excedem os limiares. Terminologia: PA calibrada pela"
            " incerteza/inspirada em análise paralela; não é uma nova execução MC nem uma "
            "análise de Horn."
        ),
        (
            "Stored nominal global spectrum and uncertainty q95 thresholds for B=2000. Two"
            " components exceed their thresholds. Terminology: "
            "uncertainty-calibrated/parallel-analysis-inspired PA; this is neither a new "
            "MC execution nor a Horn analysis."
        ),
    ),
    "B6": (
        (
            "Primeiro e último par e trio em ordem lexicográfica, selecionados sem usar "
            "desempenho. Estrelas: âncoras; segmento/triângulo: CHIM; cruzes: pesos H5; "
            "círculos laranja: soluções locais aceitas do H5 standalone. Pares usam "
            "respostas locais normalizadas; trios usam coordenadas SVD intrínsecas. Nos "
            "trios a normal é perpendicular ao plano e sua projeção é nula: ⊙ indica essa "
            "direção, e o painel t mostra o deslocamento que a projeção omite. A geometria"
            " nominal histórica é usada sem soluções ou trajetória H20."
        ),
        (
            "First and last lexicographic pair and triple, selected without performance "
            "information. Stars: anchors; segment/triangle: CHIM; crosses: H5 weights; "
            "orange circles: accepted local standalone H5 solutions. Pairs use locally "
            "normalized responses; triples use intrinsic SVD coordinates. In triples the "
            "normal is perpendicular to the plane and projects to zero: ⊙ denotes this "
            "direction, and the t panel shows the displacement omitted by projection. "
            "Historical nominal geometry is used without H20 solutions or trajectory."
        ),
    ),
    "C1": (
        (
            "Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE."
            " Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem"
            " vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in,"
            " sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais"
            " variam por resposta."
        ),
        (
            "Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard "
            "errors come from the frozen analytic covariance diagonal, using column-wise "
            "vectorization. Intervals are approximate, conditional on the plug-in model, "
            "and not simultaneously adjusted; no model was fitted. Horizontal scales vary "
            "by response."
        ),
    ),
    "C2": (
        (
            "Quantidade visual adimensional β̂/SE, preservando o sinal. Não são "
            "coeficientes padronizados por uma escala física comum e não se infere "
            "significância por magnitude da cor. A covariância é a mesma usada no painel "
            "Wald."
        ),
        (
            "Dimensionless visual quantity β̂/SE, retaining the sign. These are not "
            "coefficients standardized to a shared physical scale, and significance is not"
            " inferred from color magnitude. The covariance is the same as in the Wald "
            "panel."
        ),
    ),
    "C3": (
        (
            "As 2.000 reotimizações já armazenadas de cada âncora são mostradas nas três "
            "projeções codificadas. Estrela escura: ótimo nominal; nuvem magenta: MC. O "
            "contorno tracejado é a esfera projetada. As nuvens são propagação do ensemble"
            " congelado, não nova amostragem ou intervalos frequencistas exatos."
        ),
        (
            "The 2,000 stored reoptimizations of each anchor are shown in three coded "
            "projections. Dark star: nominal optimum; magenta cloud: MC. The dashed "
            "contour is the projected sphere. Clouds propagate the frozen ensemble; they "
            "are neither new sampling nor exact frequentist intervals."
        ),
    ),
    "C4": (
        (
            "Cada par de respostas mostra as 2.000 avaliações da payoff própria de cada "
            "reotimização, nuvens transparentes, âncoras nominais escuras e centros MC "
            "(+). Elipses de incerteza de 95% baseadas na covariância da amostra MC: média"
            " aritmética, covariância com divisor n−1 e χ²₂(0,95). São resumos descritivos"
            " sob aproximação elíptica; não são regiões de confiança exatas, nem "
            "intervalos de confiança para a média."
        ),
        (
            "Each response pair shows the 2,000 own-payoff evaluations of each "
            "reoptimization, transparent clouds, dark nominal anchors, and MC centers (+)."
            " The 95% covariance-based uncertainty ellipses use the arithmetic mean, "
            "sample covariance with divisor n−1, and χ²₂(0.95). They are descriptive "
            "summaries under an elliptical approximation, not exact confidence regions or "
            "confidence intervals for the mean."
        ),
    ),
    "C5": (
        (
            "Os mesmos subconjuntos determinísticos de B6, combinados com as projeções das"
            " payoff MC das respectivas âncoras. Normalização local nominal e base "
            "geométrica fixas; não se refaz normalização por réplica. Elipses: média e "
            "covariância amostral das 2.000 projeções, nível 95%, χ²₂, interpretação "
            "descritiva. A projeção intrínseca dos trios omite a componente normal, "
            "indicada por ⊙."
        ),
        (
            "The same deterministic subsets as B6, combined with projections of the "
            "corresponding MC anchor payoffs. Local nominal normalization and geometric "
            "basis remain fixed; no per-replicate normalization is refitted. Ellipses use "
            "the mean and sample covariance of the 2,000 projections, 95% level, and χ²₂, "
            "with descriptive interpretation. Triple intrinsic projections omit the normal"
            " component, denoted by ⊙."
        ),
    ),
    "C6": (
        (
            "Média e amplitude interquantil q95−q05 das 2.000 payoff MC armazenadas, "
            "normalizadas pelo mesmo ideal/amplitude nominal fixo da Fase 5. Linhas: "
            "âncoras; colunas: respostas. Escalas de cor distintas, sem clipping. A "
            "amplitude interquantil não é um intervalo de confiança exato."
        ),
        (
            "Mean and q95−q05 interquantile width of the 2,000 stored MC payoffs, "
            "normalized by the same fixed Phase 5 nominal ideal/range. Rows: anchors; "
            "columns: responses. Separate color scales, no clipping. The interquantile "
            "width is not an exact confidence interval."
        ),
    ),
    "C7": (
        (
            "Checkpoints armazenados B=100,…,2000. Erros de Frobenius da média/covariância"
            " dos coeficientes, dimensão global, gaps g1/g2 e máxima variação monitorada "
            "na janela. Linha pontilhada em 1300 e janela 1100–1300: primeiro stop "
            "retrospectivo da política revisada no caso aplicado; linha horizontal 0,05: "
            "tolerância congelada. B_stop=1300 é resultado deste caso, não constante "
            "universal nem validação externa da política."
        ),
        (
            "Stored checkpoints B=100,…,2000. Coefficient mean/covariance Frobenius "
            "errors, global dimension, g1/g2 gaps, and maximum monitored window change. "
            "Dotted line at 1300 and 1100–1300 window: first retrospective stop under the "
            "revised policy in this applied case; horizontal line at 0.05: frozen "
            "tolerance. B_stop=1300 is a case result, not a universal constant or external"
            " policy validation."
        ),
    ),
    "D1a": (
        (
            "Referência independente de 18.503 pontos, sem CNBI, e os 409 ND do H5 "
            "standalone. Transformação visual comum pᵢ=(hiᵢ−zᵢ)/(hiᵢ−loᵢ), com limites dos"
            " candidatos canônicos completos mais o H5 atual; zero é pior e um é melhor no"
            " conjunto desses limites. Essa transformação não substitui a normalização "
            "oficial das métricas. Transparências não codificam probabilidades."
        ),
        (
            "Independent 18,503-point zero-CNBI reference and the 409 standalone H5 ND "
            "points. Shared visual transform pᵢ=(hiᵢ−zᵢ)/(hiᵢ−loᵢ), with bounds from all "
            "canonical candidates plus current H5; zero is worst and one best within those"
            " bounds. This transform does not replace official metric normalization. "
            "Opacity does not encode probabilities."
        ),
    ),
    "D1b": (
        (
            "Desempenho visual na mesma transformação de D1a, com H5 standalone, VRF-NBI "
            "e uma run arquivada por EA. A seleção visual dos EAs minimiza o IGD"
            " nativo já registrado no alvo comum histórico, com desempate pela seed. Não "
            "representa as 30 runs, sua mediana ou uma nova execução."
        ),
        (
            "Visual performance using the same transform as D1a, with standalone H5, "
            "VRF-NBI, and one archived run per EA. Display representatives minimize"
            " the already recorded native IGD on the historical common target, breaking "
            "ties by seed. They do not represent all 30 runs, their median, or a new "
            "execution."
        ),
    ),
    "D2": (
        (
            "Projeções em valores naturais das respostas canônicas, sem rescalagem pela "
            "nota da Tabela 3. Cinza: referência independente; laranja: H5 standalone; "
            "azul: VRF-NBI; verde/vermelho: runs EA selecionadas somente pelo IGD "
            "congelado. Uma projeção bidimensional não certifica dominância em oito "
            "respostas. ROI/OEE permanecem como razões, sem conversão silenciosa para "
            "porcentagem."
        ),
        (
            "Projections in natural values of the canonical responses, without applying "
            "the Table 3 scaling note. Gray: independent reference; orange: standalone H5;"
            " blue: VRF-NBI; green/red: EA runs selected only by frozen IGD. A "
            "two-dimensional projection does not certify eight-response dominance. ROI/OEE"
            " remain ratios, with no silent percentage conversion."
        ),
    ),
    "D3": (
        (
            "As mesmas soluções representativas e pares de D2, separadas por método sobre "
            "a referência independente cinza. Evita sobreposição entre métodos. As "
            "cardinalidades nativas diferem; esta figura ilustra regiões, não é comparação"
            " com cardinalidade controlada."
        ),
        (
            "The same representative solutions and pairs as D2, separated by method over "
            "the gray independent reference. This avoids inter-method overlap. Native "
            "cardinalities differ; the figure illustrates regions rather than a "
            "cardinality-controlled comparison."
        ),
    ),
    "D4": (
        (
            "Uma única PCA centrada na referência independente, no espaço global MIN, "
            "aplicada sem refit a todos os métodos. Percentuais nos eixos: variância da "
            "referência. Métodos usam os mesmos representantes de D2; a projeção não "
            "substitui métricas nem preserva integralmente a ordem de Pareto."
        ),
        (
            "One PCA centered on the independent reference in the global MIN space, "
            "applied to every method without refitting. Axis percentages: reference "
            "variance. Methods use the same representatives as D2; projection does not "
            "replace metrics or fully preserve Pareto order."
        ),
    ),
    "D5": (
        (
            "Proveniência histórica da Fase 7 no envelope comum de 22.523 pontos. A barra "
            "CNBI corresponde à família H20 histórica, não aos 409 pontos do baseline "
            "atual. Contagens e percentuais exclusivos são copiados dos artefatos "
            "congelados; contribuição não é qualidade absoluta ou atribuição causal."
        ),
        (
            "Historical Phase 7 provenance in the 22,523-point common envelope. The CNBI "
            "bar refers to the historical H20 family, not the current 409-point baseline. "
            "Exclusive counts and percentages are copied from frozen artifacts; "
            "contribution is neither absolute quality nor causal attribution."
        ),
    ),
    "E1": (
        (
            "IGD congelado contra o mesmo alvo comum histórico completo de 22.523 pontos. "
            "Curvas EA: mediana e IQR de 30 runs; CNBI: H5 standalone; VRF-NBI: frente "
            "única até K=66. Reduções FPS são aninhadas e preservam extremos, "
            "sem duplicar pontos. Linha vertical em K=66. O alvo histórico contém famílias"
            " avaliadas; não é a referência independente do CNBI ou uma frente verdadeira."
        ),
        (
            "Frozen IGD against the same complete historical 22,523-point common target. "
            "EA curves: median and IQR of 30 runs; CNBI: standalone H5; VRF-NBI: one "
            "front up to K=66. Nested FPS reductions preserve extremes without "
            "duplicate points. Vertical line at K=66. The historical target includes "
            "evaluated families; it is neither the independent CNBI reference nor a true "
            "front."
        ),
    ),
    "E2": (
        (
            "Mesmo controle de cardinalidade de E1. HV estimado com o ponto de referência "
            "e as quatro redes Sobol comuns congeladas, sem novo cálculo científico da "
            "métrica. EAs: mediana/IQR de 30 runs. O alvo GD/IGD não entra na definição de"
            " HV; o estimador tem resolução finita."
        ),
        (
            "Same cardinality control as E1. HV is estimated with the frozen reference "
            "point and four shared Sobol grids, with no new scientific metric calculation."
            " EAs: median/IQR of 30 runs. The GD/IGD target is not part of the HV "
            "definition; estimator resolution is finite."
        ),
    ),
    "E3": (
        (
            "Spacing e Sparsity congelados em função de K. Spacing é o desvio padrão "
            "amostral das distâncias Euclidianas ao vizinho mais próximo (ddof1); Sparsity"
            " é sua média. EAs: mediana/IQR de 30 runs. Ambas dependem da densidade; "
            "valores baixos não demonstram cobertura ou convergência."
        ),
        (
            "Frozen Spacing and Sparsity versus K. Spacing is the sample standard "
            "deviation of Euclidean nearest-neighbor distances (ddof1); Sparsity is their "
            "mean. EAs: median/IQR of 30 runs. Both depend on density; low values do not "
            "establish coverage or convergence."
        ),
    ),
    "F1": (
        (
            "Qualidade e tempo da mesma configuração científica: cada H é standalone, H5 "
            "destacado por estrela, cinco repetições H5 idênticas e uma observação nos "
            "demais H. EAs: medianas/IQR de dez seeds da campanha controlada, checkpoints "
            "50/100/200/300/400. IGD usa o alvo comum histórico; HV usa o ponto/estimador "
            "comum. Campanhas têm datas próprias, mesma máquina/ambiente; não são "
            "p-valores ou equivalência por NFE. VRF-NBI não tem tempo reproduzível."
        ),
        (
            "Quality and time belong to the same scientific configuration: each H is "
            "standalone, H5 is starred, with five identical-output H5 repetitions and one "
            "observation at each other H. EAs: medians/IQR of ten controlled seeds, "
            "checkpoints 50/100/200/300/400. IGD uses the historical common target; HV "
            "uses the shared point/estimator. Campaign dates differ on the same "
            "machine/environment; these are neither p-values nor NFE equivalences. VRF-NBI "
            "lacks reproducible timing."
        ),
    ),
    "F2": (
        (
            "Tempos end-to-end congelados, sem equivalência artificial por NFE. Pontos: "
            "medições; traço: mediana; barra: IQR quando há repetições. H5 n=5, outros H "
            "n=1, EAs n=10. Não se inventa variabilidade para n=1, e VRF-NBI não é incluído "
            "por ausência de timing reproduzível."
        ),
        (
            "Frozen end-to-end times, without artificial NFE equivalence. Points: "
            "measurements; tick: median; bar: IQR when repetitions exist. H5 n=5, other H "
            "n=1, EAs n=10. No variability is invented for n=1, and VRF-NBI is omitted because"
            " reproducible timing is unavailable."
        ),
    ),
    "F3": (
        (
            "Diagnóstico visual suplementar entre H consecutivos: "
            "(IGD_Ha−IGD_Hb)/(t_Hb−t_Ha) e (HV_Hb−HV_Ha)/(t_Hb−t_Ha). IGD usa a referência"
            " independente sem CNBI; tempos são os já medidos, com mediana em H5 e "
            "observação única nos demais. Não são novas métricas principais ou estimativas"
            " causais de eficiência."
        ),
        (
            "Supplementary visual diagnostic between consecutive H values: "
            "(IGD_Ha−IGD_Hb)/(t_Hb−t_Ha) and (HV_Hb−HV_Ha)/(t_Hb−t_Ha). IGD uses the "
            "independent zero-CNBI reference; times are stored measurements, using the H5 "
            "median and single observations elsewhere. These are neither new primary "
            "metrics nor causal efficiency estimates."
        ),
    ),
    "G1": (
        (
            "IGD do mesmo H5 standalone contra referências sem CNBI, reutilizando as 100 "
            "subamostras pareadas existentes em r=5/10/15/20/25 e uma referência completa "
            "em r=30. Curva: mediana; faixa: q05–q95; pontos: subamostras armazenadas, sem"
            " jitter. A faixa é dispersão de subconjuntos, não intervalo de confiança."
        ),
        (
            "IGD of the same standalone H5 against zero-CNBI references, reusing the 100 "
            "existing paired subsets at r=5/10/15/20/25 and one complete reference at "
            "r=30. Curve: median; band: q05–q95; points: stored subsets without jitter. "
            "The band is subset dispersion, not a confidence interval."
        ),
    ),
    "G2": (
        (
            "Mesmas referências e distribuições de G1, mostrando GD do H5 standalone. "
            "Nenhuma subamostra foi gerada novamente. Redução de GD com mais runs não "
            "certifica convergência à frente verdadeira."
        ),
        (
            "Same references and distributions as G1, showing standalone H5 GD. No subsets"
            " were generated again. Decreasing GD with more runs does not certify "
            "convergence to the true front."
        ),
    ),
    "G3": (
        (
            "Cardinalidade e HV da referência sem CNBI nas mesmas subamostras existentes. "
            "Mediana e q05–q95, com referência única em r=30. O crescimento do número de "
            "pontos e a mudança do envelope geométrico são fenômenos distintos; não se "
            "declara saturação certificada."
        ),
        (
            "Cardinality and HV of the zero-CNBI reference in the same existing subsets. "
            "Median and q05–q95, with one reference at r=30. Point-count growth and "
            "geometric-envelope change are distinct phenomena; certified saturation is not"
            " claimed."
        ),
    ),
    "G4": (
        (
            "Sete prefixos FPS já congelados da referência independente; H5 avaliado é "
            "fixo. GD/IGD são dependentes do alvo e HV pertence à referência reduzida. A "
            "redução é análise de sensibilidade; as comparações de métodos mantêm o alvo "
            "completo."
        ),
        (
            "Seven already frozen FPS prefixes of the independent reference; evaluated H5 "
            "is fixed. GD/IGD depend on the target, while HV belongs to the reduced "
            "reference. Reduction is a sensitivity analysis; method comparisons retain the"
            " complete target."
        ),
    ),
    "G5": (
        (
            "Referências N, M, NM e NMV já armazenadas, sempre sem CNBI. Painéis: IGD/GD "
            "do H5 standalone e HV da própria referência. A composição e densidade mudam o"
            " alvo; não se interpretam contribuições marginais como importância universal "
            "de um método."
        ),
        (
            "Stored N, M, NM, and NMV references, always excluding CNBI. Panels: "
            "standalone H5 IGD/GD and reference HV. Composition and density change the "
            "target; marginal contributions are not interpreted as universal method "
            "importance."
        ),
    ),
    "H1": (
        (
            "Distâncias ao vizinho mais próximo no espaço global MIN, calculadas apenas "
            "para diagnóstico visual. CNBI e VRF-NBI são frentes únicas; EAs agregam "
            "distâncias calculadas dentro de cada uma das 30 runs genuínas. Violinos "
            "resumem pontos, não 30 observações independentes de qualidade; barras "
            "internas mostram mediana/IQR. Cardinalidades nativas diferem."
        ),
        (
            "Nearest-neighbor distances in the global MIN space, calculated only as a "
            "visual diagnostic. CNBI and VRF-NBI are single fronts; EAs pool distances "
            "computed within each of the 30 genuine runs. Violins summarize points rather "
            "than 30 independent quality observations; inner bars show median/IQR. Native "
            "cardinalities differ."
        ),
    ),
    "H2": (
        (
            "Densidade kNN (k=15) na projeção PCA bidimensional da referência, exibida "
            "como log(1+k/(πr_k²)); pontos laranja são o H5 standalone. A base PCA é a "
            "mesma dos demais painéis. Densidade projetada não é densidade em oito "
            "dimensões, cobertura de Pareto ou nova métrica principal."
        ),
        (
            "kNN density (k=15) in the two-dimensional reference PCA projection, shown as "
            "log(1+k/(πr_k²)); orange points are standalone H5. The PCA basis is the same "
            "as in the other panels. Projected density is neither eight-dimensional "
            "density, Pareto coverage, nor a new primary metric."
        ),
    ),
    "H3": (
        (
            "Projeções das decisões codificadas das mesmas frentes representativas de D2. "
            "Contorno tracejado: esfera projetada. Os nomes dos fatores seguem a ordem "
            "auditada, sem inferir coordenadas físicas para novas soluções. Diferentes "
            "regiões projetadas não demonstram, isoladamente, melhor qualidade "
            "multiobjetivo."
        ),
        (
            "Coded-decision projections of the same representative fronts as D2. Dashed "
            "contour: projected sphere. Factor names follow the audited order, without "
            "inferring physical coordinates for new solutions. Different projected regions"
            " alone do not establish better multiobjective quality."
        ),
    ),
    "I1": (
        (
            "Fluxograma vetorial do pipeline já executado: dados, oito RSMs, covariância, "
            "ensemble de coeficientes, reotimizações/ payoff MC, CHIM/SVD/PA, 37 subsets, "
            "H5 standalone e benchmark. O gráfico descreve etapas concluídas; não as "
            "executa novamente e não inclui refinamento adaptativo."
        ),
        (
            "Vector workflow of the already executed pipeline: data, eight RSMs, "
            "covariance, coefficient ensemble, MC reoptimizations/payoff, CHIM/SVD/PA, 37 "
            "subsets, standalone H5, and benchmark. The diagram describes completed "
            "stages; it does not rerun them or include adaptive refinement."
        ),
    ),
    "J1": (
        (
            "Síntese dos dados já apresentados: payoff global normalizada, um CHIM local "
            "representativo, projeção T×Kp das frentes e IGD×tempo no alvo comum "
            "histórico. Mesmas transformações e representantes dos painéis individuais. A "
            "síntese não substitui as figuras completas ou suas limitações."
        ),
        (
            "Summary of the already presented data: globally normalized payoff, one "
            "representative local CHIM, T×Kp front projection, and IGD×time on the "
            "historical common target. Same transforms and representatives as in "
            "individual panels. The summary does not replace the full figures or their "
            "limitations."
        ),
    ),
}


def caption(identifier, language):
    key = "C1" if identifier.startswith("C1_") else identifier
    text = NOTES[key][0 if language == "pt" else 1]
    text = text.replace("Vc/cs", "Vc (cs)").replace("ap/md", "ap (md)")
    if key == "C2":
        text += (
            " O intercepto foi omitido deste heatmap para tornar visíveis os efeitos "
            "dos nove termos de fatores; permanece nos forest plots e tabelas."
            if language == "pt"
            else " The intercept is omitted from this heatmap to reveal the nine "
            "factor-term effects; it remains in forest plots and tables."
        )
    if key == "C7":
        text += (
            " Os erros comparam a média MC com β nominal e a covariância MC com "
            "Σ̂e ⊗ Vx analítica, como nos checkpoints originais."
            if language == "pt"
            else " Errors compare the MC mean with nominal β and MC covariance "
            "with analytic Σ̂e ⊗ Vx, as in the original checkpoints."
        )
    if identifier.startswith("C1_"):
        text = (
            f"Painel individual para {identifier[3:]}; alternativa de apresentação de C1. "
            if language == "pt"
            else f"Individual panel for {identifier[3:]}; presentation alternative to C1. "
        ) + text
    return text


QUESTIONS = {
    "A1": "Como cada resposta varia na seção central permitida do domínio codificado?",
    "A2": "Qual custo nas oito respostas acompanha cada ótimo individual?",
    "A3": "Os custos cruzados relativos entre duas otimizações são simétricos?",
    "B1": "Onde estão os oito ótimos individuais no espaço de decisão?",
    "B2": "Como os vetores das âncoras se posicionam na mesma projeção de respostas?",
    "B3": "Quais respostas compõem os 19 pares e 18 trios selecionados?",
    "B4": "Quais respostas aparecem juntas com maior frequência nos subsets selecionados?",
    "B5": "Quantos componentes singulares excedem os limiares de incerteza congelados?",
    "B6": "Como pesos,CHIM,normal e soluções standalone se relacionam localmente?",
    "C1": "Quais estimativas e amplitudes Wald têm os coeficientes congelados?",
    "C2": "Como variam os efeitos dos fatores em relação aos respectivos erros padrão?",
    "C3": "Como o ensemble congelado dispersa as decisões de cada ótimo individual?",
    "C4": "Qual dispersão das respostas acompanha as reotimizações MC de cada âncora?",
    "C5": "Como a incerteza das âncoras aparece na mesma geometria local nominal?",
    "C6": "Quais células payoff apresentam maior dispersão interquantil no ensemble?",
    "C7": "Como evoluem os diagnósticos existentes e a decisão retrospectiva de stop?",
    "D1a": "Quais perfis de resposta do H5 aparecem dentro do envelope empírico independente?",
    "D1b": "Como diferem os perfis visuais dos representantes arquivados dos métodos?",
    "D2": "Quais regiões das respostas naturais aparecem nas projeções de cada método?",
    "D3": "Como separar a sobreposição dos métodos preservando os mesmos eixos e dados?",
    "D4": "Como os mesmos conjuntos aparecem em uma única projeção linear compartilhada?",
    "D5": "Qual foi a contribuição exclusiva das famílias ao envelope histórico da Fase7?",
    "E1": "Como muda o IGD congelado quando a aproximação possui menos soluções genuínas?",
    "E2": "Como muda o HV congelado sob o mesmo controle de cardinalidade?",
    "E3": "Como a cardinalidade afeta os indicadores de regularidade e densidade?",
    "F1": "Que compromissos de qualidade e tempo são observados nas configurações medidas?",
    "F2": "Qual foi o runtime observado e sua dispersão quando existem repetições?",
    "F3": "Qual ganho incremental de qualidade acompanha o custo entre resoluções medidas?",
    "G1": "Quanto o IGD do mesmo H5 varia entre referências com diferentes números de runs?",
    "G2": "Quanto o GD do mesmo H5 varia entre as mesmas referências congeladas?",
    "G3": "Como crescem o número de pontos e o volume empírico da referência?",
    "G4": "Como a redução da referência altera as distâncias do mesmo H5?",
    "G5": "Quanto a composição de famílias altera o alvo usado para avaliar o H5?",
    "H1": "Como diferem as distribuições de vizinhança no espaço normalizado original?",
    "H2": "Onde a projeção bidimensional da referência tem maior densidade local?",
    "H3": "Quais regiões codificadas das decisões são representadas pelas soluções exibidas?",
    "I1": "Quais etapas científicas já executadas ligam o CCD ao benchmark aplicado?",
    "J1": "Como resumir problema,geometria,fronteira e custo sem novos resultados?",
}


def question(identifier):
    return QUESTIONS["C1" if identifier.startswith("C1_") else identifier]


def observation(identifier, tables, audit):
    root = "C1" if identifier.startswith("C1_") else identifier
    ev = audit["pca"]["explained_variance_ratio"]
    if root == "A1":
        return "O plano exibido fixa x3=0; cada escala mostra valores do modelo nominal congelado."
    if root == "A2":
        return (
            "A diagonal normalizada é zero; as64 células são explicitamente "
            "transpostas para âncora×resposta."
        )
    if root == "A3":
        return (
            "A transformação é antissimétrica e a diagonal é zero por definição; "
            "não há nova otimização."
        )
    if root in ("B2", "D4", "H2"):
        return (
            f"PC1={ev[0]:.2%},PC2={ev[1]:.2%} da variância na referência independente; "
            "mesma base para todos."
        )
    if root == "B1":
        return "Oito pontos nominais arquivados,na bola de raio8**0.25,sem inversa física inferida."
    if root in ("B3", "B4"):
        return (
            "37 subconjuntos preservados:19 pares e18 trios; frequências calculadas"
            " apenas dessa matriz binária."
        )
    if root == "B5":
        return "Apenas os componentes1 e2 excedem o q95; dimensão global suportada d=2."
    if root in ("B6", "C5"):
        return "Subconjuntos de exibição:" + ",".join(audit["selected_local_subsets"]) + "."
    if root == "C1":
        return (
            "80 coeficientes de oito respostas,10 termos por modelo; não foram "
            "recalculados ajustes ou coeficientes."
        )
    if root == "C2":
        return (
            "São exibidos os nove termos de fatores por resposta; o intercepto "
            "continua nas demais fontes."
        )
    if root in ("C3", "C4", "C6"):
        return "Todos os2000 índices MC de cada uma das oito âncoras são preservados."
    if root == "C7":
        return (
            "O primeiro stop retrospectivo armazenado é1300; o ensemble final "
            "de2000 permanece a fonte."
        )
    if root in ("D1a", "D1b", "D2", "D3", "H3"):
        data = tables["fronts"]
        if root == "D1a":
            data = data[data.method.isin(["Reference", "CNBI5"])]
        if root in ("D1b", "H3"):
            data = data[data.method != "Reference"]
        from .style import method_label

        counts = {
            method_label(method, "pt"): count
            for method, count in data.groupby("method").size().items()
        }
        return (
            f"Cardinalidades das nuvens exibidas:{counts}. "
            "Representantes EA auditados separadamente."
        )
    if root == "D5":
        return (
            "Contagens exclusivas históricas:NSGA=8449,MOEA=9743,CNBI-H20=4267,VRF-NBI=64; "
            "não são contribuições do H5 atual."
        )
    if root in ("E1", "E2", "E3"):
        r = tables["cardinality"]
        r = r[
            (r.method == "CNBI5") & (r.label == "HISTORICAL_COMMON_H20_TARGET") & (r.K == 66)
        ].iloc[0]
        return (
            f"No K66 do H5:IGD={r.IGD:.9g},HV={r.HV:.9g},Spacing={r.Spacing:.9g},"
            f"Sparsity={r.Sparsity:.9g}; valores congelados."
        )
    if root in ("F1", "F2", "F3"):
        return (
            "H5 tem cinco medições com saída idêntica;H2/H4/H10/H20 têm uma;EAs têm"
            " dez seeds de timing,sem runtime VRF-NBI."
        )
    if root in ("G1", "G2", "G3", "G4", "G5"):
        return (
            "As referências são as mesmas já congeladas;nenhum índice,run,FPS ou "
            "referência foi reconstruído."
        )
    if root == "H1":
        return (
            "Distâncias são calculadas dentro das frentes genuínas,nunca entre runs"
            " diferentes; não se introduz métrica primária."
        )
    if root == "I1":
        return (
            "São14 etapas descritivas do pipeline concluído,sem executar qualquer etapa científica."
        )
    return (
        "Os quatro painéis reutilizam as mesmas tabelas,transformações e "
        "representantes das figuras individuais."
    )
