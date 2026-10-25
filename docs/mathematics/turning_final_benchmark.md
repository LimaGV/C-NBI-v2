# Fase8 — sensibilidade e benchmark controlado, escopo revisado

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


## Tabela A — desempenho nativo


| Method | Unique ND | GD | IGD | HV estimate | Spacing | Sparsity | T_total/s |
|---|---|---|---|---|---|---|---|
| CNBI5 | 408 | 0.001109372 | 0.1487117 | 0.6673368 | 0.03182528 | 0.03730441 | pending |
| VRF | 66 | 0.001087944 | 0.2745194 | 0.4915679 | 0.00665316 | 0.09306867 | pending |
| NSGA3 | 330 [0] | 0.005971838 [0.002375885] | 0.07880341 [0.008891651] | 0.7695703 [0.01326684] | 0.04925109 [0.0038903] | 0.05306125 [0.005493395] | 17.4856 [0.090247] |
| MOEAD | 327 [3.75] | 0 [0] | 0.1844776 [0.00496609] | 0.6615785 [0.002778956] | 0.04293534 [0.000830451] | 0.0161297 [0.0004948644] | 82.98164 [0.2632369] |


## Tabela B — cardinalidade igualada em66


| Method | Unique ND | GD | IGD | HV estimate | Spacing | Sparsity |
|---|---|---|---|---|---|---|
| CNBI5 | 66 | 0.001664502 | 0.1705072 | 0.5977026 | 0.05366976 | 0.2145634 |
| VRF | 66 | 0.001087944 | 0.2745194 | 0.4915679 | 0.00665316 | 0.09306867 |
| NSGA3 | 66 [0] | 0.0109365 [0.005228899] | 0.1152924 [0.008598793] | 0.6821735 [0.01660693] | 0.04504133 [0.01437159] | 0.2165136 [0.01212377] |
| MOEAD | 66 [0] | 0 [0] | 0.1904529 [0.004801735] | 0.6559003 [0.003039483] | 0.07737204 [0.00254931] | 0.08660058 [0.001465055] |


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


## Tabela C — sensibilidade ao número de runs


| r | Reference size median | GD H5 median | IGD H5 median | HV reference median |
|---|---|---|---|---|
| 5 | 3265.5 | 0.06795285 | 0.165076 | 0.8587841 |
| 10 | 6380.5 | 0.05496746 | 0.1660021 | 0.8767405 |
| 15 | 9448 | 0.0491133 | 0.1665065 | 0.8855784 |
| 20 | 12490 | 0.04489724 | 0.1669434 | 0.891811 |
| 25 | 15502 | 0.04163344 | 0.1673088 | 0.8964537 |
| 30 | 18503 | 0.03956715 | 0.1676468 | 0.8994063 |


## Composição e contribuição marginal


| Reference | ND | GD H5 | IGD H5 | HV estimate |
|---|---|---|---|---|
| N | 8754 | 0.0403134 | 0.1224824 | 0.8945298 |
| M | 9743 | 0.3852789 | 0.2083976 | 0.7035033 |
| NM | 18440 | 0.04005009 | 0.1678085 | 0.8993796 |
| NMV | 18503 | 0.03956715 | 0.1676468 | 0.8994063 |
| MV | 9809 | 0.2777979 | 0.207788 | 0.7459225 |
| NV | 8817 | 0.03983046 | 0.1224669 | 0.8945565 |

| Added family | Base | Delta ND | Delta HV | Delta GD H5 | Delta IGD H5 |
|---|---|---|---|---|---|
| VRF | NM | 63 | 2.6720727655304977e-05 | -0.0004829421628501501 | -0.00016170121684708216 |
| NSGA3 | MV | 8694 | 0.15348385965249323 | -0.2382307174614943 | -0.04014122975910481 |
| MOEAD | NV | 9686 | 0.00484981206945112 | -0.00026330308663328333 | 0.04517983998615081 |


## Cardinalidade da referência


| K_R | GD H5 | IGD H5 | HV reference estimate |
|---|---|---|---|
| 250 | 0.08105401 | 0.1224036 | 0.7972664 |
| 500 | 0.06789276 | 0.1215209 | 0.8336867 |
| 1000 | 0.05283944 | 0.119816 | 0.8587641 |
| 2500 | 0.0432894 | 0.1194329 | 0.8824921 |
| 5000 | 0.04024395 | 0.1211003 | 0.8939687 |
| 10000 | 0.03960272 | 0.1363013 | 0.8989922 |
| 18503 | 0.03956715 | 0.1676468 | 0.8994063 |


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


## Robustez independente H5 e resoluções auxiliares


| H | ND | GD to R30 | IGD to R30 | HV estimate | Runtime |
|---|---|---|---|---|---|
| 2 | 82 | 0.04239855 | 0.220905 | 0.5130246 | pending |
| 4 | 281 | 0.04051362 | 0.1760363 | 0.6294335 | pending |
| 5 | 408 | 0.03956715 | 0.1676468 | 0.6673368 | pending |
| 10 | 1310 | 0.03927047 | 0.09891025 | 0.765148 | pending |
| 20 | 4417 | 0.0391376 | 0.06544497 | 0.831028 | pending |


Os cinco conjuntos acima são memberships do H20 preservado; não são novas execuções isoladas. H5 oficial continua408. Referência R30 exclui toda CNBI. Os resultados LOO das demais famílias estão nos CSVs, com alvos próprios; não devem ser ordenados como se fossem a mesma referência.


## Tabela D — custo controlado, somente EAs


| Method | Generation | T_total median/s | IGD common median | HV estimate median | ND median |
|---|---|---|---|---|---|
| NSGA3 | 50 | 2.168276 | 0.08112549 | 0.7674126 | 330 |
| NSGA3 | 100 | 4.377896 | 0.07848903 | 0.7630171 | 330 |
| NSGA3 | 200 | 8.750034 | 0.07945884 | 0.7724094 | 330 |
| NSGA3 | 300 | 13.12917 | 0.07776254 | 0.7676063 | 330 |
| NSGA3 | 400 | 17.48403 | 0.08015605 | 0.7715811 | 330 |
| MOEAD | 50 | 10.16679 | 0.197313 | 0.6495608 | 313.5 |
| MOEAD | 100 | 20.56096 | 0.1926636 | 0.6596145 | 314.5 |
| MOEAD | 200 | 41.38649 | 0.1867216 | 0.6625137 | 324 |
| MOEAD | 300 | 62.1476 | 0.1862161 | 0.6620528 | 324.5 |
| MOEAD | 400 | 82.97739 | 0.185004 | 0.6615852 | 327.5 |


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


## Proporções de runs melhores e posição percentual do H5


| Variant | EA | Metric | Fraction better than H5 | H5 percentile (higher better) |
|---|---|---|---|---|
| native | NSGA3 | GD | 0.0 | 100.0 |
| native | NSGA3 | IGD | 1.0 | 0.0 |
| native | NSGA3 | HV | 1.0 | 0.0 |
| native | NSGA3 | Spacing | 0.0 | 100.0 |
| native | NSGA3 | Sparsity | 0.0 | 100.0 |
| native | MOEAD | GD | 1.0 | 0.0 |
| native | MOEAD | IGD | 0.0 | 100.0 |
| native | MOEAD | HV | 0.0 | 100.0 |
| native | MOEAD | Spacing | 0.0 | 100.0 |
| native | MOEAD | Sparsity | 1.0 | 0.0 |
| K66 | NSGA3 | GD | 0.0 | 100.0 |
| K66 | NSGA3 | IGD | 1.0 | 0.0 |
| K66 | NSGA3 | HV | 1.0 | 0.0 |
| K66 | NSGA3 | Spacing | 0.8 | 20.0 |
| K66 | NSGA3 | Sparsity | 0.4 | 60.0 |
| K66 | MOEAD | GD | 1.0 | 0.0 |
| K66 | MOEAD | IGD | 0.0 | 100.0 |
| K66 | MOEAD | HV | 1.0 | 0.0 |
| K66 | MOEAD | Spacing | 0.0 | 100.0 |
| K66 | MOEAD | Sparsity | 1.0 | 0.0 |


As mesmas comparações com VRF, as proporções de empate, média/SD/IQR/q05/q95/mínimo/máximo de todas as métricas e todas as30 runs estão nos CSVs completos. Percentis usam score orientado (HV positivo, demais negativos), com meia massa nos empates. Não são p-values; empates de HV podem ser quantização.


## Figuras e reprodutibilidade


14 figuras em PDF/SVG e PNG600dpi, cores/markers centralizados em `figures/visual_mapping.json`, legendas e dados completos preservados. Faixas das curvas de runs são q05–q95 das100 subamostras, não IC; curvas dos EAs em K/tempo usam mediana e IQR. Figuras comuns/LOO estão identificadas.

| Artifact | SHA256 |
|---|---|
| metadata.json | d067a23760141269c69f604be9d4e4a4a2f0fab6f9bfe361c265af825f4b0c18 |
| checksums.sha256 | c0e8ab1ccd8d4b8d42ca03dffec22afb86200d4dc371da5993276001bf3b3988 |
| reference_final.npz | 9b3c727c6dc73fa304fd66f3532f36ed345014113c09bb8fd6118025e7ada041 |
| hv_reference_point.json | 95b219f84474e913dfde0b863a9799744eaafca878bed083da6f986237dd4d95 |


Input hashes completos em metadata.json; raw, modelos, normalização, IDs dos37 subsets, fases anteriores e resultados publicados não foram modificados. Otimização adaptativa, novos cenários sintéticos e merge automático não iniciados.
