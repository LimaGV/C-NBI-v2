# Pacote oficial de visualizações — caso aplicado

Este pacote apresenta exclusivamente evidências científicas congeladas no
commit d938695b7fdaf9c871d331a42ff277e0c3fbd2d1. O baseline é H5 standalone,
492 aceitos/411 únicos/409 ND. A referência independente tem18503 pontos e
zero proveniência CNBI. Nenhuma otimização,amostragem,refit ou métrica oficial
foi executada novamente. As tabelas oficiais de métricas são copiadas como
fontes; estatísticas de exibição e diagnósticos visuais são identificados.

Não há linhas de grade. Linhas de contorno,limites do domínio,zero dos Wald,
limiar PA,divisor pares/trios,K66 e janela/limiar de stop são referências
científicas explícitas,distintas de grades dos eixos.

## Base e nomenclatura

PR11 contém a correção e permaneceu aberto ao iniciar esta tarefa. A branch
feature/09-applied-case-visualizations parte de d938695 na branch corrigida,
sem fazer merge automático do PR11. O PR de visualizações usa essa base.
Fatores:x1=Vc(cabeçalho cs),x2=f,x3=ap(cabeçalho md),confirmados no metadata
de coding da Fase2. Não usar md como alias de Vc. Não existe inversa contínua
codificado→físico verificada. Respostas naturais não recebem a escala da
Tabela3; ROI/OEE não são convertidos para porcentagens.

## Transformações e limites

Auditáveis em data/visual_transform_audit.json. PCA única centrada na referência
18503,sem padronização extra,aplicada a todas as frentes e âncoras. Componentes,
média,variância e convenção de sinais estão salvos. As projeções não preservam
dominância em8D. O diagnóstico kNN mede densidade em2D,sem nova métrica principal.

As elipses descrevem a amostra MC já reotimizada:2000 payoff próprias,média
aritmética,covariância ddof1,nível.95,chi2df2. Os42 conjuntos de parâmetros,
variáveis de projeção e fonte estão nas tabelas de elipses e auditoria. Não são
regiões de confiança exatas nem intervalos para a média. Wald usa a covariância
analítica congelada e aproximação normal,sem multiplicidade. Nenhuma incerteza
foi reamostrada. A1 apenas avalia os coeficientes congelados no plano x3=0 para
desenhar o contorno; não estima coeficientes ou altera valores experimentais.

B6/C5 usam geometria nominal congelada e soluções H5 standalone; nunca usam
soluções H20 como baseline. Para trios,a normal é perpendicular ao plano CHIM
intrínseco e desaparece na projeção. O símbolo⊙ e o painel t tornam essa perda
de dimensão explícita. A projeção de um peso e de sua solução NBI pode coincidir.

E/F usam,quando comparativos,o alvo comum histórico22523 e deixam claro que
não é o alvo independente do CNBI. G usa as referências sem CNBI. D5 é apenas
proveniência histórica Fase7/CNBIH20,não contribuição do baseline409. Os tempos
por H são próprios standalone,n5 emH5/n1 nos demais; EAs têm10 seeds e suas
curvas de qualidade30 runs. Não existe runtime VRF-NBI reproduzível. A divergência
histórica H20 em1/4557 permanece como limitação já documentada,não é corrigida.

Representantes EA são escolhidos exclusivamente pelos IGDs já registrados,
com a menor seed em empate. Essa é uma seleção de exibição,não novo benchmark,
retuning,otimização ou alegação de run previamente nomeada como representante.
Os nomes,seeds e valores exatos estão na auditoria visual. Nenhuma legenda
apresenta uma run como mediana das30. Figuras quantitativas usam as30 quando
previsto. C1 inclui oito exports individuais solicitados,alternativas ao painel
composto,não oito resultados independentes adicionais. Não se gera radar,
UMAP,t-SNE,3D decorativo ou original NBI fora do benchmark.

## Reprodutibilidade

Entrada:scripts/visualization/generate_applied_case_figures.py. Opções:
--language pt/en/both,--set main/supplementary/all,--output,--formats,--dpi.
PNG600dpi,PDF e SVG vetoriais nas entregas oficiais. Prévia pode usar outro DPI.
SVG é omitido apenas para D3,cuja nuvem de referência é repetida em16 painéis;
o PDF totalmente vetorial e o PNG600dpi dessa figura continuam disponíveis.
Heatmaps usam células vetoriais e colorbars não são rasterizadas. O leitor CSV
preserva literais com conversão Python explícita e17 dígitos nas tabelas de
desenho,sem depender de float_precision depreciado no pandas3.1 instalado.
Context7 forneceu documentação Matplotlib,SciPy e NumPy; após o limite de
consultas,foi verificada a documentação oficial pandas e o código instalado:
https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html.
Sem LaTeX externo ou RNG. Metadados temporais de PDF/SVG são removidos e salts
SVG são fixos por figura/idioma. Reprodutibilidade bytewise é condicionada ao
mesmo ambiente/fontes/backends; as tabelas e identidades científicas permanecem
auditáveis entre plataformas. Os testes verificam exports repetidos e igualdade
dos dados/artistas entre PT/EN,integridade das fontes,paleta/ordens e baseline.
Os checksums incluem fontes de plotting,tabelas,figuras,metadata e captions.

## Catálogo e perguntas científicas

### A1 — Mapas de contorno das superfícies de resposta

- Pergunta/finalidade: Como cada resposta varia na seção central permitida do domínio codificado?
- Tabelas de desenho: ["data/plot_data_contours.csv"]
- Fontes congeladas: ["data/metadata/turning_application/phase_02_coding.json", "results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv"]
- Observação principal: O plano exibido fixa x3=0; cada escala mostra valores do modelo nominal congelado.
- Transformação,observação e limites: Avaliação visual dos coeficientes quadráticos congelados no plano x₃=0, dentro da seção circular da esfera. Cada resposta usa sua própria escala em valores naturais; cores entre respostas não são quantitativamente comparáveis. A linha tracejada delimita a seção e a cruz marca o centro. Não houve novo ajuste RSM.
- Uso recomendado: artigo,dissertação,apresentação.

### A2 — Matriz payoff normalizada das otimizações individuais

- Pergunta/finalidade: Qual custo nas oito respostas acompanha cada ótimo individual?
- Tabelas de desenho: ["data/plot_data_payoff.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/payoff_sphere.csv", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_chim.npz", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_normalization.csv"]
- Observação principal: A diagonal normalizada é zero; as64 células são explicitamente transpostas para âncora×resposta.
- Transformação,observação e limites: Linhas: âncoras nominais; colunas: respostas atingidas. A payoff armazenada foi transposta apenas para apresentação. Normalização global nominal fixa, orientação MIN: zero é o ideal individual e um é o pior valor entre âncoras para aquela resposta. Não é a normalização de desempenho visual das coordenadas paralelas.
- Uso recomendado: artigo,dissertação,apresentação.

### A3 — Assimetria dos custos cruzados normalizados

- Pergunta/finalidade: Os custos cruzados relativos entre duas otimizações são simétricos?
- Tabelas de desenho: ["data/plot_data_conflict.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/payoff_sphere.csv", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_chim.npz", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_normalization.csv"]
- Observação principal: A transformação é antissimétrica e a diagonal é zero por definição; não há nova otimização.
- Transformação,observação e limites: Diagnóstico visual suplementar de assimetria: Cᵢⱼ=Zⱼᵢ−Zᵢⱼ, em que a payoff Z tem respostas nas linhas e âncoras nas colunas. A diagonal é zero. O sinal compara custos cruzados nas amplitudes nominais; não representa correlação, dominância ou nova métrica de benchmark.
- Uso recomendado: material suplementar,dissertação,apresentação.

### B1 — Ótimos individuais no espaço codificado dos fatores

- Pergunta/finalidade: Onde estão os oito ótimos individuais no espaço de decisão?
- Tabelas de desenho: ["data/plot_data_anchors.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/anchors_sphere.csv"]
- Observação principal: Oito pontos nominais arquivados,na bola de raio8**0.25,sem inversa física inferida.
- Transformação,observação e limites: Oito ótimos nominais em três projeções do espaço codificado. A circunferência tracejada é a projeção da esfera, não uma transformação para unidades físicas. x₁=Vc (cs), x₂=f e x₃=ap (md) conforme a auditoria canônica; não existe inversa contínua física verificada.
- Uso recomendado: material suplementar,dissertação,apresentação.

### B2 — Projeção dos ótimos individuais no espaço normalizado das respostas

- Pergunta/finalidade: Como os vetores das âncoras se posicionam na mesma projeção de respostas?
- Tabelas de desenho: ["data/plot_data_anchor_pca.csv"]
- Fontes congeladas: ["results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_chim.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz"]
- Observação principal: PC1=69.16%,PC2=16.20% da variância na referência independente; mesma base para todos.
- Transformação,observação e limites: Projeção linear dos oito vetores de resposta das âncoras. A PCA foi ajustada uma única vez à referência independente de 18.503 pontos no espaço MIN global fixo, sem padronização adicional. Os percentuais são da referência; distâncias e dominância em oito dimensões não se preservam integralmente em duas.
- Uso recomendado: material suplementar,dissertação,apresentação.

### B3 — Estrutura dos subconjuntos selecionados

- Pergunta/finalidade: Quais respostas compõem os 19 pares e 18 trios selecionados?
- Tabelas de desenho: ["data/plot_data_subsets.csv"]
- Fontes congeladas: ["results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/selected_subsets_B2000.csv"]
- Observação principal: 37 subconjuntos preservados:19 pares e18 trios; frequências calculadas apenas dessa matriz binária.
- Transformação,observação e limites: Matriz binária dos 37 subconjuntos congelados: 19 pares seguidos de 18 trios em ordem lexicográfica. A separação horizontal distingue as dimensões; as barras mostram frequências marginais, não importância causal ou desempenho.
- Uso recomendado: artigo,dissertação,apresentação.

### B4 — Rede de coocorrência das respostas nos subconjuntos selecionados

- Pergunta/finalidade: Quais respostas aparecem juntas com maior frequência nos subsets selecionados?
- Tabelas de desenho: ["data/plot_data_cooccurrence.csv", "data/plot_data_subsets.csv"]
- Fontes congeladas: ["results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/selected_subsets_B2000.csv"]
- Observação principal: 37 subconjuntos preservados:19 pares e18 trios; frequências calculadas apenas dessa matriz binária.
- Transformação,observação e limites: Layout circular determinístico na ordem canônica. A largura das arestas representa o número de subconjuntos em que duas respostas coexistem; a área dos nós cresce com a frequência marginal. A rede resume seleção, não associação estatística entre respostas.
- Uso recomendado: material suplementar,dissertação,apresentação.

### B5 — Espectro singular e limiar de incerteza da análise paralela

- Pergunta/finalidade: Quantos componentes singulares excedem os limiares de incerteza congelados?
- Tabelas de desenho: ["data/plot_data_pa.csv"]
- Fontes congeladas: ["results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/global_pa_B2000.csv"]
- Observação principal: Apenas os componentes1 e2 excedem o q95; dimensão global suportada d=2.
- Transformação,observação e limites: Espectro global nominal e limiares q95 de incerteza já armazenados para B=2000. Dois componentes excedem os limiares. Terminologia: PA calibrada pela incerteza/inspirada em análise paralela; não é uma nova execução MC nem uma análise de Horn.
- Uso recomendado: artigo,dissertação,apresentação.

### B6 — Geometria local do CHIM e direções NBI

- Pergunta/finalidade: Como pesos,CHIM,normal e soluções standalone se relacionam localmente?
- Tabelas de desenho: ["data/plot_data_local_geometry.csv"]
- Fontes congeladas: ["results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/selected_subsets_B2000.csv", "results/phase_06_local_nbi/turning_local_nbi_h20_20261024/local_geometry.json", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/H5_rep1.npz"]
- Observação principal: Subconjuntos de exibição:C_1_4,C_7_8,C_1_4_6,C_6_7_8.
- Transformação,observação e limites: Primeiro e último par e trio em ordem lexicográfica, selecionados sem usar desempenho. Estrelas: âncoras; segmento/triângulo: CHIM; cruzes: pesos H5; círculos laranja: soluções locais aceitas do H5 standalone. Pares usam respostas locais normalizadas; trios usam coordenadas SVD intrínsecas. Nos trios a normal é perpendicular ao plano e sua projeção é nula: ⊙ indica essa direção, e o painel t mostra o deslocamento que a projeção omite. A geometria nominal histórica é usada sem soluções ou trajetória H20.
- Uso recomendado: artigo,dissertação,apresentação.

### C1 — Estimativas e intervalos de confiança dos coeficientes RSM

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C2 — Coeficientes RSM divididos pelo erro padrão

- Pergunta/finalidade: Como variam os efeitos dos fatores em relação aos respectivos erros padrão?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: São exibidos os nove termos de fatores por resposta; o intercepto continua nas demais fontes.
- Transformação,observação e limites: Quantidade visual adimensional β̂/SE, preservando o sinal. Não são coeficientes padronizados por uma escala física comum e não se infere significância por magnitude da cor. A covariância é a mesma usada no painel Wald. O intercepto foi omitido deste heatmap para tornar visíveis os efeitos dos nove termos de fatores; permanece nos forest plots e tabelas.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C3 — Propagação da incerteza das âncoras no espaço de decisão

- Pergunta/finalidade: Como o ensemble congelado dispersa as decisões de cada ótimo individual?
- Tabelas de desenho: ["data/plot_data_mc_decision.csv", "data/plot_data_anchors.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/anchors_sphere.csv", "results/phase_04_anchor_mc/turning_original_codes_anchor_mc_777_20261024/anchor_samples.npz"]
- Observação principal: Todos os2000 índices MC de cada uma das oito âncoras são preservados.
- Transformação,observação e limites: As 2.000 reotimizações já armazenadas de cada âncora são mostradas nas três projeções codificadas. Estrela escura: ótimo nominal; nuvem magenta: MC. O contorno tracejado é a esfera projetada. As nuvens são propagação do ensemble congelado, não nova amostragem ou intervalos frequencistas exatos.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C4 — Incerteza Monte Carlo dos ótimos individuais

- Pergunta/finalidade: Qual dispersão das respostas acompanha as reotimizações MC de cada âncora?
- Tabelas de desenho: ["data/plot_data_mc_responses.csv", "data/plot_data_ellipses.csv", "data/plot_data_payoff.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/payoff_sphere.csv", "results/phase_04_anchor_mc/turning_original_codes_anchor_mc_777_20261024/payoff_samples.npz", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_chim.npz", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_normalization.csv", "results/phase_06_local_nbi/turning_local_nbi_h20_20261024/local_geometry.json"]
- Observação principal: Todos os2000 índices MC de cada uma das oito âncoras são preservados.
- Transformação,observação e limites: Cada par de respostas mostra as 2.000 avaliações da payoff própria de cada reotimização, nuvens transparentes, âncoras nominais escuras e centros MC (+). Elipses de incerteza de 95% baseadas na covariância da amostra MC: média aritmética, covariância com divisor n−1 e χ²₂(0,95). São resumos descritivos sob aproximação elíptica; não são regiões de confiança exatas, nem intervalos de confiança para a média.
- Uso recomendado: artigo,dissertação,apresentação.

### C5 — Incerteza das âncoras e geometria local do CHIM

- Pergunta/finalidade: Como a incerteza das âncoras aparece na mesma geometria local nominal?
- Tabelas de desenho: ["data/plot_data_local_geometry.csv", "data/plot_data_local_mc.csv", "data/plot_data_ellipses.csv"]
- Fontes congeladas: ["results/phase_04_anchor_mc/turning_original_codes_anchor_mc_777_20261024/payoff_samples.npz", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/selected_subsets_B2000.csv", "results/phase_06_local_nbi/turning_local_nbi_h20_20261024/local_geometry.json", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/H5_rep1.npz"]
- Observação principal: Subconjuntos de exibição:C_1_4,C_7_8,C_1_4_6,C_6_7_8.
- Transformação,observação e limites: Os mesmos subconjuntos determinísticos de B6, combinados com as projeções das payoff MC das respectivas âncoras. Normalização local nominal e base geométrica fixas; não se refaz normalização por réplica. Elipses: média e covariância amostral das 2.000 projeções, nível 95%, χ²₂, interpretação descritiva. A projeção intrínseca dos trios omite a componente normal, indicada por ⊙.
- Uso recomendado: artigo,dissertação,apresentação.

### C6 — Propagação da incerteza na matriz payoff

- Pergunta/finalidade: Quais células payoff apresentam maior dispersão interquantil no ensemble?
- Tabelas de desenho: ["data/plot_data_payoff_uncertainty.csv"]
- Fontes congeladas: ["results/phase_04_anchor_mc/turning_original_codes_anchor_mc_777_20261024/payoff_samples.npz", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_normalization.csv"]
- Observação principal: Todos os2000 índices MC de cada uma das oito âncoras são preservados.
- Transformação,observação e limites: Média e amplitude interquantil q95−q05 das 2.000 payoff MC armazenadas, normalizadas pelo mesmo ideal/amplitude nominal fixo da Fase 5. Linhas: âncoras; colunas: respostas. Escalas de cor distintas, sem clipping. A amplitude interquantil não é um intervalo de confiança exato.
- Uso recomendado: artigo,dissertação,apresentação.

### C7 — Estabilização da propagação Monte Carlo

- Pergunta/finalidade: Como evoluem os diagnósticos existentes e a decisão retrospectiva de stop?
- Tabelas de desenho: ["data/plot_data_coefficient_stability.csv", "data/plot_data_spectral_gaps.csv", "data/plot_data_early_stop.csv"]
- Fontes congeladas: ["results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/mc_prefix_sensitivity.csv", "results/phase_05_chim_pa/turning_spectral_gap_policy_v2_20261024/early_stop_validation.json", "results/phase_05_chim_pa/turning_spectral_gap_policy_v2_20261024/global_spectral_gap_trajectory.csv"]
- Observação principal: O primeiro stop retrospectivo armazenado é1300; o ensemble final de2000 permanece a fonte.
- Transformação,observação e limites: Checkpoints armazenados B=100,…,2000. Erros de Frobenius da média/covariância dos coeficientes, dimensão global, gaps g1/g2 e máxima variação monitorada na janela. Linha pontilhada em 1300 e janela 1100–1300: primeiro stop retrospectivo da política revisada no caso aplicado; linha horizontal 0,05: tolerância congelada. B_stop=1300 é resultado deste caso, não constante universal nem validação externa da política. Os erros comparam a média MC com β nominal e a covariância MC com Σ̂e ⊗ Vx analítica, como nos checkpoints originais.
- Uso recomendado: artigo,dissertação,apresentação.

### D1a — Coordenadas paralelas: referência e C-NBI

- Pergunta/finalidade: Quais perfis de resposta do H5 aparecem dentro do envelope empírico independente?
- Tabelas de desenho: ["data/plot_data_fronts.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: Cardinalidades das nuvens exibidas:{'C-NBI H5 standalone': 409, 'Referência empírica independente': 18503}. Representantes EA auditados separadamente.
- Transformação,observação e limites: Referência independente de 18.503 pontos, sem CNBI, e os 409 ND do H5 standalone. Transformação visual comum pᵢ=(hiᵢ−zᵢ)/(hiᵢ−loᵢ), com limites dos candidatos canônicos completos mais o H5 atual; zero é pior e um é melhor no conjunto desses limites. Essa transformação não substitui a normalização oficial das métricas. Transparências não codificam probabilidades.
- Uso recomendado: artigo,dissertação,apresentação.

### D1b — Coordenadas paralelas das soluções não dominadas

- Pergunta/finalidade: Como diferem os perfis visuais dos representantes arquivados dos métodos?
- Tabelas de desenho: ["data/plot_data_fronts.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: Cardinalidades das nuvens exibidas:{'C-NBI H5 standalone': 409, 'MOEA/D': 330, 'NSGA-III': 330, 'VRF-NBI': 66}. Representantes EA auditados separadamente.
- Transformação,observação e limites: Desempenho visual na mesma transformação de D1a, com H5 standalone, VRF-NBI e uma run arquivada por EA. A seleção visual dos EAs minimiza o IGD nativo já registrado no alvo comum histórico, com desempate pela seed. Não representa as 30 runs, sua mediana ou uma nova execução.
- Uso recomendado: artigo,dissertação,apresentação.

### D2 — Projeções bidimensionais da fronteira empírica

- Pergunta/finalidade: Quais regiões das respostas naturais aparecem nas projeções de cada método?
- Tabelas de desenho: ["data/plot_data_fronts.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: Cardinalidades das nuvens exibidas:{'C-NBI H5 standalone': 409, 'MOEA/D': 330, 'NSGA-III': 330, 'Referência empírica independente': 18503, 'VRF-NBI': 66}. Representantes EA auditados separadamente.
- Transformação,observação e limites: Projeções em valores naturais das respostas canônicas, sem rescalagem pela nota da Tabela 3. Cinza: referência independente; laranja: H5 standalone; azul: VRF-NBI; verde/vermelho: runs EA selecionadas somente pelo IGD congelado. Uma projeção bidimensional não certifica dominância em oito respostas. ROI/OEE permanecem como razões, sem conversão silenciosa para porcentagem.
- Uso recomendado: artigo,dissertação,apresentação.

### D3 — Comparação por método e projeção

- Pergunta/finalidade: Como separar a sobreposição dos métodos preservando os mesmos eixos e dados?
- Tabelas de desenho: ["data/plot_data_fronts.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: Cardinalidades das nuvens exibidas:{'C-NBI H5 standalone': 409, 'MOEA/D': 330, 'NSGA-III': 330, 'Referência empírica independente': 18503, 'VRF-NBI': 66}. Representantes EA auditados separadamente.
- Transformação,observação e limites: As mesmas soluções representativas e pares de D2, separadas por método sobre a referência independente cinza. Evita sobreposição entre métodos. As cardinalidades nativas diferem; esta figura ilustra regiões, não é comparação com cardinalidade controlada.
- Uso recomendado: material suplementar,dissertação,apresentação.

### D4 — Projeção PCA da fronteira em oito objetivos

- Pergunta/finalidade: Como os mesmos conjuntos aparecem em uma única projeção linear compartilhada?
- Tabelas de desenho: ["data/plot_data_fronts.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: PC1=69.16%,PC2=16.20% da variância na referência independente; mesma base para todos.
- Transformação,observação e limites: Uma única PCA centrada na referência independente, no espaço global MIN, aplicada sem refit a todos os métodos. Percentuais nos eixos: variância da referência. Métodos usam os mesmos representantes de D2; a projeção não substitui métricas nem preserva integralmente a ordem de Pareto.
- Uso recomendado: material suplementar,dissertação,apresentação.

### D5 — Contribuição exclusiva ao envelope empírico histórico

- Pergunta/finalidade: Qual foi a contribuição exclusiva das famílias ao envelope histórico da Fase7?
- Tabelas de desenho: ["data/plot_data_contributions.csv"]
- Fontes congeladas: ["results/phase_07_reference_front/turning_multifamily_loo_20261024/reference_contributions.csv"]
- Observação principal: Contagens exclusivas históricas:NSGA=8449,MOEA=9743,CNBI-H20=4267,VRF-NBI=64; não são contribuições do H5 atual.
- Transformação,observação e limites: Proveniência histórica da Fase 7 no envelope comum de 22.523 pontos. A barra CNBI corresponde à família H20 histórica, não aos 409 pontos do baseline atual. Contagens e percentuais exclusivos são copiados dos artefatos congelados; contribuição não é qualidade absoluta ou atribuição causal.
- Uso recomendado: material suplementar,dissertação,apresentação.

### E1 — IGD em função da cardinalidade da aproximação

- Pergunta/finalidade: Como muda o IGD congelado quando a aproximação possui menos soluções genuínas?
- Tabelas de desenho: ["data/plot_data_cardinality.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/cardinality_curve_metrics.csv"]
- Observação principal: No K66 do H5:IGD=0.152271779,HV=0.673161931,Spacing=0.056733601,Sparsity=0.223549913; valores congelados.
- Transformação,observação e limites: IGD congelado contra o mesmo alvo comum histórico completo de 22.523 pontos. Curvas EA: mediana e IQR de 30 runs; CNBI: H5 standalone; VRF-NBI: frente única até K=66. Reduções FPS são aninhadas e preservam extremos, sem duplicar pontos. Linha vertical em K=66. O alvo histórico contém famílias avaliadas; não é a referência independente do CNBI ou uma frente verdadeira.
- Uso recomendado: artigo,dissertação,apresentação.

### E2 — Hipervolume em função da cardinalidade da aproximação

- Pergunta/finalidade: Como muda o HV congelado sob o mesmo controle de cardinalidade?
- Tabelas de desenho: ["data/plot_data_cardinality.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/cardinality_curve_metrics.csv"]
- Observação principal: No K66 do H5:IGD=0.152271779,HV=0.673161931,Spacing=0.056733601,Sparsity=0.223549913; valores congelados.
- Transformação,observação e limites: Mesmo controle de cardinalidade de E1. HV estimado com o ponto de referência e as quatro redes Sobol comuns congeladas, sem novo cálculo científico da métrica. EAs: mediana/IQR de 30 runs. O alvo GD/IGD não entra na definição de HV; o estimador tem resolução finita.
- Uso recomendado: artigo,dissertação,apresentação.

### E3 — Efeito da cardinalidade sobre as métricas de distribuição

- Pergunta/finalidade: Como a cardinalidade afeta os indicadores de regularidade e densidade?
- Tabelas de desenho: ["data/plot_data_cardinality.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/cardinality_curve_metrics.csv"]
- Observação principal: No K66 do H5:IGD=0.152271779,HV=0.673161931,Spacing=0.056733601,Sparsity=0.223549913; valores congelados.
- Transformação,observação e limites: Spacing e Sparsity congelados em função de K. Spacing é o desvio padrão amostral das distâncias Euclidianas ao vizinho mais próximo (ddof1); Sparsity é sua média. EAs: mediana/IQR de 30 runs. Ambas dependem da densidade; valores baixos não demonstram cobertura ou convergência.
- Uso recomendado: material suplementar,dissertação,apresentação.

### F1 — Qualidade da aproximação em função do tempo computacional

- Pergunta/finalidade: Que compromissos de qualidade e tempo são observados nas configurações medidas?
- Tabelas de desenho: ["data/plot_data_cost_cnbi.csv", "data/plot_data_cost_ea.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/cost_quality_cnbi.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/cost_quality_ea_preserved.csv"]
- Observação principal: H5 tem cinco medições com saída idêntica;H2/H4/H10/H20 têm uma;EAs têm dez seeds de timing,sem runtime VRF-NBI.
- Transformação,observação e limites: Qualidade e tempo da mesma configuração científica: cada H é standalone, H5 destacado por estrela, cinco repetições H5 idênticas e uma observação nos demais H. EAs: medianas/IQR de dez seeds da campanha controlada, checkpoints 50/100/200/300/400. IGD usa o alvo comum histórico; HV usa o ponto/estimador comum. Campanhas têm datas próprias, mesma máquina/ambiente; não são p-valores ou equivalência por NFE. VRF-NBI não tem tempo reproduzível.
- Uso recomendado: artigo,dissertação,apresentação.

### F2 — Tempo total de processamento

- Pergunta/finalidade: Qual foi o runtime observado e sua dispersão quando existem repetições?
- Tabelas de desenho: ["data/plot_data_timing_cnbi.csv", "data/plot_data_timing_nsga3.csv", "data/plot_data_timing_moead.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/timing_moead.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/timing_nsga3.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/timing_cnbi.csv"]
- Observação principal: H5 tem cinco medições com saída idêntica;H2/H4/H10/H20 têm uma;EAs têm dez seeds de timing,sem runtime VRF-NBI.
- Transformação,observação e limites: Tempos end-to-end congelados, sem equivalência artificial por NFE. Pontos: medições; traço: mediana; barra: IQR quando há repetições. H5 n=5, outros H n=1, EAs n=10. Não se inventa variabilidade para n=1, e VRF-NBI não é incluído por ausência de timing reproduzível.
- Uso recomendado: artigo,dissertação,apresentação.

### F3 — Ganho marginal de qualidade por custo computacional

- Pergunta/finalidade: Qual ganho incremental de qualidade acompanha o custo entre resoluções medidas?
- Tabelas de desenho: ["data/plot_data_marginal_gain.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/cost_quality_cnbi.csv"]
- Observação principal: H5 tem cinco medições com saída idêntica;H2/H4/H10/H20 têm uma;EAs têm dez seeds de timing,sem runtime VRF-NBI.
- Transformação,observação e limites: Diagnóstico visual suplementar entre H consecutivos: (IGD_Ha−IGD_Hb)/(t_Hb−t_Ha) e (HV_Hb−HV_Ha)/(t_Hb−t_Ha). IGD usa a referência independente sem CNBI; tempos são os já medidos, com mediana em H5 e observação única nos demais. Não são novas métricas principais ou estimativas causais de eficiência.
- Uso recomendado: material suplementar,dissertação,apresentação.

### G1 — Sensibilidade do IGD ao número de execuções usadas na referência

- Pergunta/finalidade: Quanto o IGD do mesmo H5 varia entre referências com diferentes números de runs?
- Tabelas de desenho: ["data/plot_data_reference_replicates.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/reference_run_sensitivity_replicates.csv"]
- Observação principal: As referências são as mesmas já congeladas;nenhum índice,run,FPS ou referência foi reconstruído.
- Transformação,observação e limites: IGD do mesmo H5 standalone contra referências sem CNBI, reutilizando as 100 subamostras pareadas existentes em r=5/10/15/20/25 e uma referência completa em r=30. Curva: mediana; faixa: q05–q95; pontos: subamostras armazenadas, sem jitter. A faixa é dispersão de subconjuntos, não intervalo de confiança.
- Uso recomendado: artigo,dissertação,apresentação.

### G2 — Sensibilidade do GD ao número de execuções usadas na referência

- Pergunta/finalidade: Quanto o GD do mesmo H5 varia entre as mesmas referências congeladas?
- Tabelas de desenho: ["data/plot_data_reference_replicates.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/reference_run_sensitivity_replicates.csv"]
- Observação principal: As referências são as mesmas já congeladas;nenhum índice,run,FPS ou referência foi reconstruído.
- Transformação,observação e limites: Mesmas referências e distribuições de G1, mostrando GD do H5 standalone. Nenhuma subamostra foi gerada novamente. Redução de GD com mais runs não certifica convergência à frente verdadeira.
- Uso recomendado: material suplementar,dissertação,apresentação.

### G3 — Crescimento da referência empírica

- Pergunta/finalidade: Como crescem o número de pontos e o volume empírico da referência?
- Tabelas de desenho: ["data/plot_data_reference_replicates.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/reference_run_sensitivity_replicates.csv"]
- Observação principal: As referências são as mesmas já congeladas;nenhum índice,run,FPS ou referência foi reconstruído.
- Transformação,observação e limites: Cardinalidade e HV da referência sem CNBI nas mesmas subamostras existentes. Mediana e q05–q95, com referência única em r=30. O crescimento do número de pontos e a mudança do envelope geométrico são fenômenos distintos; não se declara saturação certificada.
- Uso recomendado: artigo,dissertação,apresentação.

### G4 — Sensibilidade à cardinalidade da referência empírica

- Pergunta/finalidade: Como a redução da referência altera as distâncias do mesmo H5?
- Tabelas de desenho: ["data/plot_data_reference_cardinality.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/reference_cardinality_sensitivity.csv"]
- Observação principal: As referências são as mesmas já congeladas;nenhum índice,run,FPS ou referência foi reconstruído.
- Transformação,observação e limites: Sete prefixos FPS já congelados da referência independente; H5 avaliado é fixo. GD/IGD são dependentes do alvo e HV pertence à referência reduzida. A redução é análise de sensibilidade; as comparações de métodos mantêm o alvo completo.
- Uso recomendado: artigo,dissertação,apresentação.

### G5 — Sensibilidade à composição da referência empírica

- Pergunta/finalidade: Quanto a composição de famílias altera o alvo usado para avaliar o H5?
- Tabelas de desenho: ["data/plot_data_reference_composition.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_standalone_correction_20261025/reference_composition_sensitivity.csv"]
- Observação principal: As referências são as mesmas já congeladas;nenhum índice,run,FPS ou referência foi reconstruído.
- Transformação,observação e limites: Referências N, M, NM e NMV já armazenadas, sempre sem CNBI. Painéis: IGD/GD do H5 standalone e HV da própria referência. A composição e densidade mudam o alvo; não se interpretam contribuições marginais como importância universal de um método.
- Uso recomendado: material suplementar,dissertação,apresentação.

### H1 — Distribuição das distâncias ao vizinho mais próximo

- Pergunta/finalidade: Como diferem as distribuições de vizinhança no espaço normalizado original?
- Tabelas de desenho: ["data/plot_data_nearest_neighbor.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: Distâncias são calculadas dentro das frentes genuínas,nunca entre runs diferentes; não se introduz métrica primária.
- Transformação,observação e limites: Distâncias ao vizinho mais próximo no espaço global MIN, calculadas apenas para diagnóstico visual. CNBI e VRF-NBI são frentes únicas; EAs agregam distâncias calculadas dentro de cada uma das 30 runs genuínas. Violinos resumem pontos, não 30 observações independentes de qualidade; barras internas mostram mediana/IQR. Cardinalidades nativas diferem.
- Uso recomendado: material suplementar,dissertação,apresentação.

### H2 — Densidade local na projeção PCA da referência

- Pergunta/finalidade: Onde a projeção bidimensional da referência tem maior densidade local?
- Tabelas de desenho: ["data/plot_data_pca_density.csv", "data/plot_data_fronts.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: PC1=69.16%,PC2=16.20% da variância na referência independente; mesma base para todos.
- Transformação,observação e limites: Densidade kNN (k=15) na projeção PCA bidimensional da referência, exibida como log(1+k/(πr_k²)); pontos laranja são o H5 standalone. A base PCA é a mesma dos demais painéis. Densidade projetada não é densidade em oito dimensões, cobertura de Pareto ou nova métrica principal.
- Uso recomendado: material suplementar,dissertação,apresentação.

### H3 — Distribuição das soluções no espaço de decisão

- Pergunta/finalidade: Quais regiões codificadas das decisões são representadas pelas soluções exibidas?
- Tabelas de desenho: ["data/plot_data_fronts.csv"]
- Fontes congeladas: ["results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: Cardinalidades das nuvens exibidas:{'C-NBI H5 standalone': 409, 'MOEA/D': 330, 'NSGA-III': 330, 'VRF-NBI': 66}. Representantes EA auditados separadamente.
- Transformação,observação e limites: Projeções das decisões codificadas das mesmas frentes representativas de D2. Contorno tracejado: esfera projetada. Os nomes dos fatores seguem a ordem auditada, sem inferir coordenadas físicas para novas soluções. Diferentes regiões projetadas não demonstram, isoladamente, melhor qualidade multiobjetivo.
- Uso recomendado: material suplementar,dissertação,apresentação.

### I1 — Fluxo metodológico do caso aplicado

- Pergunta/finalidade: Quais etapas científicas já executadas ligam o CCD ao benchmark aplicado?
- Tabelas de desenho: ["data/plot_data_workflow.csv"]
- Fontes congeladas: ["docs/mathematics/turning_final_benchmark.md"]
- Observação principal: São14 etapas descritivas do pipeline concluído,sem executar qualquer etapa científica.
- Transformação,observação e limites: Fluxograma vetorial do pipeline já executado: dados, oito RSMs, covariância, ensemble de coeficientes, reotimizações/ payoff MC, CHIM/SVD/PA, 37 subsets, H5 standalone e benchmark. O gráfico descreve etapas concluídas; não as executa novamente e não inclui refinamento adaptativo.
- Uso recomendado: artigo,dissertação,apresentação.

### J1 — Síntese visual do caso aplicado

- Pergunta/finalidade: Como resumir problema,geometria,fronteira e custo sem novos resultados?
- Tabelas de desenho: ["data/plot_data_payoff.csv", "data/plot_data_local_geometry.csv", "data/plot_data_fronts.csv", "data/plot_data_cost_cnbi.csv", "data/plot_data_cost_ea.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/payoff_sphere.csv", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_chim.npz", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_normalization.csv", "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/selected_subsets_B2000.csv", "results/phase_06_local_nbi/turning_local_nbi_h20_20261024/local_geometry.json", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/candidate_farthest_orderings.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/canonical_candidates.npz", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/provenance.csv", "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/reference_final.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/H5_rep1.npz", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/cost_quality_cnbi.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/cost_quality_ea_preserved.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/native_metrics.csv", "results/phase_08_final_benchmark/turning_standalone_correction_20261025/official_cnbi5.npz"]
- Observação principal: Os quatro painéis reutilizam as mesmas tabelas,transformações e representantes das figuras individuais.
- Transformação,observação e limites: Síntese dos dados já apresentados: payoff global normalizada, um CHIM local representativo, projeção T×Kp das frentes e IGD×tempo no alvo comum histórico. Mesmas transformações e representantes dos painéis individuais. A síntese não substitui as figuras completas ou suas limitações.
- Uso recomendado: artigo,dissertação,apresentação.

### C1_T — Coeficientes e intervalos Wald de 95% — T

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Painel individual para T; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C1_MTTF — Coeficientes e intervalos Wald de 95% — MTTF

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Painel individual para MTTF; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C1_WR — Coeficientes e intervalos Wald de 95% — WR

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Painel individual para WR; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C1_Ra — Coeficientes e intervalos Wald de 95% — Ra

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Painel individual para Ra; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C1_Rt — Coeficientes e intervalos Wald de 95% — Rt

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Painel individual para Rt; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C1_Kp — Coeficientes e intervalos Wald de 95% — Kp

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Painel individual para Kp; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C1_ROI — Coeficientes e intervalos Wald de 95% — ROI

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Painel individual para ROI; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

### C1_OEE — Coeficientes e intervalos Wald de 95% — OEE

- Pergunta/finalidade: Quais estimativas e amplitudes Wald têm os coeficientes congelados?
- Tabelas de desenho: ["data/plot_data_coefficients.csv"]
- Fontes congeladas: ["results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv", "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/theoretical_covariance.npy"]
- Observação principal: 80 coeficientes de oito respostas,10 termos por modelo; não foram recalculados ajustes ou coeficientes.
- Transformação,observação e limites: Painel individual para OEE; alternativa de apresentação de C1. Estimativas congeladas com intervalos Wald normais de 95%: β̂ ± Φ⁻¹(0,975)SE. Os erros padrão vêm da diagonal da covariância analítica congelada, na ordem vec por colunas. São intervalos aproximados, condicionais ao modelo plug-in, sem correção simultânea; não foi ajustado nenhum modelo. Escalas horizontais variam por resposta.
- Uso recomendado: material suplementar,dissertação,apresentação.

## Representantes de exibição

{
  "NSGA3": {
    "seed": 1002,
    "stored_IGD": 0.06317478116100282,
    "rule": "minimum frozen native IGD on historical common target; smallest seed on exact tie",
    "use": "display representative only; no new run or metric"
  },
  "MOEAD": {
    "seed": 1025,
    "stored_IGD": 0.17773678054734138,
    "rule": "minimum frozen native IGD on historical common target; smallest seed on exact tie",
    "use": "display representative only; no new run or metric"
  }
}
