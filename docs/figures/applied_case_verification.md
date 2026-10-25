# Verificação do pacote de visualizações do caso aplicado

Branch: `feature/09-applied-case-visualizations`.
Base científica: `d938695b7fdaf9c871d331a42ff277e0c3fbd2d1`.
Commit do código de renderização: `d4db09332b81bd6a11aa0750125670dd8d53541f`.
Run: `results/applied_case_visualizations/turning_visuals_20261025`.
O SHA de entrega e o PR são os da branch remota; o relatório final fornece os
identificadores verificados depois do commit/push. Nenhum merge automático.

O PR visual tem como base `feature/08-reference-sensitivity-final-benchmark`,
que contém a correção científica da Fase 8. O PR #11 permaneceu aberto:
foi verificado como MERGEABLE, com quatro checks verdes, sem integrá-lo
automaticamente a main. O novo PR mostra somente a apresentação científica.

## Entrega e integridade

São 46 entradas no catálogo: 38 famílias de figuras e oito alternativas
individuais de C1. Há 21 MAIN e 25 SUPPLEMENTARY, cada uma em PT e EN:
92 variantes, 92 PNG600dpi, 92 PDF totalmente vetoriais e 90 SVG.
Somente D3 omite SVG; seu PDF vetorial e PNG continuam disponíveis.

As 34 entradas científicas são verificadas contra seus blobs no commit-base,
antes e depois da leitura. As 33 tabelas CSV de desenho são comuns aos dois
idiomas e preservam números com 17 dígitos significativos. Não há mudança
nos dados, em src/ ou nos resultados científicos anteriores. As tabelas de
métricas existentes são lidas sem recalcular as métricas oficiais.

O baseline continua standalone H5: 492 subproblemas aceitos, 411 decisões
únicas, 409 pontos ND. A referência independente continua com 18.503 pontos,
zero origens CNBI. Os 37 subsets são 19 pares e 18 trios. As oito respostas
e suas direções mantêm a ordem canônica. A auditoria de nomenclatura confirma
x1=Vc (cabeçalho cs), x2=f, x3=ap (cabeçalho md).

O nome apresentado é **VRF-NBI**, em ambos os idiomas. Identificadores internos
congelados de fontes e famílias permanecem intactos. Não foi executado VRF-NBI.
A alteração dos rótulos não altera nenhuma das 33 tabelas numéricas de desenho.

O lançamento oficial exige working tree limpo e registra o commit de plotting.
Há um único PCA compartilhado; as 42 elipses registram amostra MC, n=2000,
projeção, média, covariância ddof1, nível .95 e quantil qui-quadrado. Não são
regiões de confiança exatas. Nenhuma otimização, refit, campanha MC, nova PA,
retuning ou reconstrução de dados foi executada por este pipeline visual.

## Revisão editorial e limites

As variantes PT/EN foram inspecionadas em pranchas de revisão; as figuras
densas e as anotações de âncoras também foram examinadas ampliadas. As
anotações de B1/B6/C4/C5/J1 usam posições determinísticas com linhas-guia
para separar nomes próximos. Curvas comparativas também usam marcadores e
estilos de linha. D2, E1, J1 e o heatmap C2 foram examinados em cinza. C2
inclui os valores com sinal, a uma casa decimal, para preservar a leitura
do sinal sem depender de cor. Valores integrais continuam no CSV.

Não há grades de coordenadas em nenhuma variante. Zero dos Wald, limites do
domínio, contornos, limiar PA, divisor pares/trios, K=66 e janela/limiar de
early stop são referências científicas descritas nas captions.

Cada pergunta, eixo, normalização, fonte, transformação, observação, limite
de interpretação e uso recomendado consta no catálogo/relatório. A revisão
por figura fica em `quality_review.csv`, no diretório do run. Não se deve
encolher painéis de oito respostas/37 subsets para uma única coluna: usar
largura dupla ou página completa. C3 e D3 são pranchas suplementares densas,
indicadas para leitura ampliada; C1 tem alternativas individuais de coluna.
Essa indicação evita prometer legibilidade idêntica sob qualquer redução.

As projeções não certificam dominância em oito dimensões. A1 avalia somente
o modelo congelado na seção central x3=0, com escalas próprias por resposta.
A2 transpõe a orientação armazenada para âncora×resposta. A3 é um diagnóstico
suplementar de assimetria dos custos cruzados, definido explicitamente.
O intercepto permanece nos dados e em C1; somente C2 o omite da exibição.
Nos trios, a normal é perpendicular ao plano CHIM: o símbolo ⊙ e o painel t
explicam a dimensão omitida, sem desenhar uma normal falsa no plano.

Os representantes visuais são NSGA-III seed1002 e MOEA/D seed1025, escolhidos
apenas por mínimo IGD nativo já registrado, com desempate pela menor seed.
Não são a mediana de 30 runs; as curvas quantitativas usam as agregações
previstas. Os tempos têm cinco repetições em H5, uma nos demais H e dez seeds
por EA; qualidade usa 30 runs EA. Não existe runtime reproduzível VRF-NBI.
D5 descreve a proveniência da Fase7/CNBI-H20. O alvo comum de 22.523 pontos
das comparações E/F é explicitamente distinto da referência independente
de 18.503 pontos usada no bloco G. Não há ranking cruzado de métricas LOO.
As limitações científicas da Fase8, inclusive a divergência H20 em 1/4557,
continuam documentadas; o pacote visual não tenta resolvê-las.

## Validação automatizada

`uv sync --locked`: aprovado, 131 pacotes resolvidos/128 instalados conferidos.
`uv run pytest -v --cov=cnbi_v2 --cov-report=term-missing`: **686 passaram**,
85,46s no Windows/Python3.12.15; cobertura **99,39%** (gate96,15%).
`uv run ruff check .`: aprovado. `uv run mypy src`: aprovado, 44 arquivos.
São 55 testes novos de visualização, incluindo os 46 contratos PT/EN.
O run final registra COMPLETE, zero warnings e working tree limpo no lançamento.

Foram conferidas as 331 entradas do manifesto contra os bytes dos blobs
efetivamente preparados no índice Git, incluindo nove scripts e três documentos
de captions/relatório. Todos os hashes SHA-256 coincidem. Os 584 links locais
da galeria apontam para arquivos existentes; há 46 cards. O pacote tem 320
arquivos e aproximadamente205,10MiB; o maior arquivo tem11,16MiB. Não foi
configurado LFS nem incluída outra pasta de resultados.

A comparação com a renderização revisada anterior preserva integralmente
as 33 tabelas e todas as geometrias científicas. Dos 274 exports, 267 são
byte-identical; seis mudaram somente pelas novas anotações com sinal em C2.
O PNG B6_en difere em quatro pixels de antialiasing, no máximo1/255 por canal;
seus PDF/SVG são byte-identical. Essa diferença raster mínima foi registrada
em integrity_review.json, sem alegar determinismo bitwise universal. O teste
de exportação repetida A2 é exato nos três formatos, e os hashes finais
preservam os bytes entregues. Nenhuma diferença foi ocultada nos dados.

O workflow existente executa os gates em Ubuntu e Windows no push desta
branch. Seu gatilho de pull_request cobre somente main; como este PR usa
a branch corrigida da Fase8, a evidência remota é o workflow do push no SHA
de entrega. O status e os links da execução são informados no PR e no
relatório final após conclusão. Nenhuma configuração de CI foi alterada.

Os contratos cobrem traduções, nome VRF-NBI, paleta, ordens/direções,
âncoras/subsets, baseline/referência, PCA compartilhado, fórmula das elipses,
valores de métricas congeladas, transposição payoff, precisão CSV, mesma
geometria PT/EN, determinismo de exportação PNG/PDF/SVG, ausência de grades,
ausência de chamadas a campanhas científicas, existência de todos os exports,
PDF sem imagens raster e hashes de fontes, código, captions e figuras.

Reprodução em uma saída nova, após instalar o ambiente travado:

```powershell
uv sync --locked
uv run python -m scripts.visualization.generate_applied_case_figures --language both --set all --output experiments/runs/visual_reproduction --dpi 600
uv run pytest -v --cov=cnbi_v2 --cov-report=term-missing
uv run ruff check .
uv run mypy src
```

O gerador recusa sobrescrever um run completo. A reprodutibilidade de bytes
é condicionada ao mesmo ambiente/fontes/backend; versões e hashes ficam no
metadata. O teste automatizado repete a exportação nos três formatos.

## Mapa dos 42 itens solicitados

Todos os caminhos da tabela pertencem ao run, salvo indicação docs/.

| Item | Entrega | Localização/evidência |
|---|---|---|
| 1 | Branch | feature/09-applied-case-visualizations |
| 2 | Commit | plotting d4db093; SHA de entrega no relatório final/HEAD do PR |
| 3 | PR | PR remoto desta branch, com base na branch corrigida da Fase8 |
| 4 | Total | 46 entradas; 38 famílias + 8 alternativas C1 |
| 5 | Main | 21 |
| 6 | Supplementary | 25 |
| 7 | Catálogo | figure_catalog.csv |
| 8 | Versões PT | figures/main/pt/ e figures/supplementary/pt/ |
| 9 | Versões EN | figures/main/en/ e figures/supplementary/en/ |
| 10 | PDF | 92, totalmente vetoriais |
| 11 | PNG | 92, 600dpi |
| 12 | SVG | 90; D3 preserva PDF vetorial e PNG |
| 13 | Captions PT | captions_pt.md e docs/figures/applied_case_captions_pt.md |
| 14 | Captions EN | captions_en.md e docs/figures/applied_case_captions_en.md |
| 15 | Tabelas-fonte | data/plot_data_*.csv, 33 tabelas |
| 16 | Workflow | I1; plot_data_workflow.csv |
| 17 | Contornos | A1; plot_data_contours.csv |
| 18 | Payoff | A2; plot_data_payoff.csv; A3 suplementar |
| 19 | Subsets | B3; plot_data_subsets.csv; B4 coocorrência |
| 20 | Espectro PA | B5; plot_data_pa.csv |
| 21 | Exemplos CHIM | B6; plot_data_local_geometry.csv |
| 22 | IC beta | C1 e C1_T/MTTF/WR/Ra/Rt/Kp/ROI/OEE; plot_data_coefficients.csv |
| 23 | Nuvens MC | C3; plot_data_mc_decision.csv |
| 24 | Elipses das âncoras | C4; plot_data_mc_responses.csv e plot_data_ellipses.csv |
| 25 | Incerteza/CHIM | C5; plot_data_local_mc.csv e tabelas geométricas/elipses |
| 26 | Incerteza payoff | C6; plot_data_payoff_uncertainty.csv |
| 27 | Estabilidade MC | C7; plot_data_coefficient_stability/spectral_gaps/early_stop.csv |
| 28 | Coordenadas paralelas | D1a/D1b; plot_data_fronts.csv |
| 29 | Projeções físicas | D2; plot_data_fronts.csv |
| 30 | Grid de métodos | D3; plot_data_fronts.csv; sem grades de eixos |
| 31 | PCA | B2/D4/H2; visual_transform_audit.json e tabelas PCA |
| 32 | Cardinalidade | E1/E2/E3; plot_data_cardinality.csv |
| 33 | Qualidade/tempo | F1; plot_data_cost_cnbi/cost_ea.csv |
| 34 | Runtime | F2; plot_data_timing_cnbi/nsga3/moead.csv |
| 35 | Sensibilidade da referência | G1/G2/G3; plot_data_reference_replicates.csv |
| 36 | Cardinalidade da referência | G4; plot_data_reference_cardinality.csv |
| 37 | Composição da referência | G5; plot_data_reference_composition.csv |
| 38 | Vizinhos/densidade | H1/H2; plot_data_nearest_neighbor/pca_density.csv |
| 39 | Graphical summary | J1; reutiliza as mesmas tabelas/fontes |
| 40 | Testes | tests/visualization/test_applied_figures.py; resultado acima |
| 41 | Checksums | checksums.sha256; source_artifacts.json; metadata.json |
| 42 | Git status | conferido após commit/push e informado no relatório final |

F3 acrescenta somente a visualização descritiva do ganho marginal já
armazenado. H3 mostra as decisões arquivadas. I1/J1 são as duas sínteses
explicitamente solicitadas, sem criar novos resultados independentes.
