# Fase 2 — anchors individuais e ablação da região de respostas

## Resultado e decisão delimitada

No caso codificado original verificado, **zero dos oito anchors clássicos**
ficam fora da região 8-D com cutoff legado chi-square_8(.95). A restrição RC
não desloca nenhum anchor nem deteriora qualquer objetivo: mediana/máximo de
Delta x e de perda relativa são zero. As duas payoff matrices são numericamente
idênticas e foram preservadas separadamente. Todos os oito anchors RC herdam o
certificado global clássico porque já pertencem ao subconjunto admissível.

**O Utopia diagonal, porém, fica fora dessa região.** D²(U)=70560.1448517,
contra c=15.5073131. Admissibilidade dos vetores completos em cada anchor não
implica admissibilidade da diagonal montada com componentes de pontos diferentes.
Isso é uma limitação lógica da proposta, ilustrada também por contraexemplo
2-D nos testes; não é um novo teste de confiança ou uma formulação adicional.
Nenhum Nadir adicional foi estimado e nenhum NBI foi implementado.

Recomendação: **continuar RC como ablação/candidato experimental**, sem adoção
obrigatória. Não houve benefício nesse caso nominal e nos três cutoffs avaliados;
além disso, restringir anchors isoladamente não resolve a admissibilidade do
Utopia montado. A inferência finita n=19,m=8 continua pendente. O resultado não
prova desnecessidade universal da restrição e não certifica adequação dos RSMs.
ADR 0005 permanece EXPERIMENTAL; C-RC-02 UNVERIFIED.

## Fonte, codificação e limite de interpretação

PR #4 foi integrado por squash 64b09f9bc413778efe47cfce9b586fe2ce2a2630,
após todos os checks e autorização explícita. Desenvolvimento em
feature/02-individual-anchors-response-region, nunca main.

Y é a revisão literal CCD_values_20261023.xlsx, inalterada, 19×8 respostas,
SHA256 7f905b7a2f7bb8b6735ab96900cba7356401df2d26c961dcb12faa2683c6c71e.
Não se arredondou WR ou reescalaram ROI/OEE. Não se reconstruíram respostas.

A planilha original NBI Revisão.xlsm (SHA256
7792a25a8c88d29206665d8797587dc6a11e932e1a8bba0a1ac8b539385f7d4e)
contém Original Data!B4:H22: IDs em B, códigos em C:E e físicos em F:H.
IDs e físicos coincidem exatamente com o CCD incorporado. Os códigos axiais
são **+/-1.682**, fatoriais +/-1 e cinco centros zero; ordem Vc,f,ap.
O extrator lê somente células numéricas literais, sem recálculo/save/macros ou
caches de fórmulas. Apenas o CSV literal de coordenadas e metadados são versionados.

O gate de equivalência física/codificada **FALHOU**: diferenças máximas de fitted
values chegam a 2.5658% da amplitude de uma resposta. Não se reclassifica isso
como tolerância de arredondamento. Após informado, o responsável esclareceu
"a planilha esta correta o artigo esta errado". A entrega prioriza os códigos
originais como **um caso de entrada codificada distinto**, mantendo os ajustes
físicos anteriores intactos. Não se presume uma transformação afim ou inversa.
Por isso as coordenadas físicas dos novos anchors ficam explicitamente
indefinidas, e não se criou API factor_coding/round-trip sem mapa verificado.

A esfera usa o alpha teórico solicitado 8^(1/4)=1.681792830507429, separado da
precisão literal 1.682 do arquivo. Os oito cantos fatoriais têm norma sqrt(3),
maior que alpha; os seis axiais 1.682 também ficam ligeiramente fora. A esfera
especificada não contém todos os pontos do CCD. Nada foi excluído do ajuste ou
nuvem de respostas por esse fato.

## Solvers e garantias

Clássico: solução espectral da quadrática sobre bola, equação secular por
Brent e caso singular/hard case explícito. A caracterização global verifica
viabilidade, estacionariedade, complementaridade e PSD do Hessiano deslocado.
Ra é um ótimo interior; os outros sete anchors ativam a esfera. Nenhum saddle
foi aceito apenas por ter gradiente zero. Tolerâncias e escalas estão em
[individual_anchors.md](individual_anchors.md) e no diagnóstico serializado.

RC geral: SLSQP com Jacobianos analíticos e multistart determinístico factível.
Aqui os oito ótimos globais clássicos já são factíveis, de modo que são
reutilizados exatamente; não se executa um otimizador local desnecessário nem
se apresenta resultado local como prova global. O solver RC está exercitado
em testes restritivos, quarticos, não convexos e com regiões desconectadas.
Há 80 propostas registradas: origem/direções determinísticas, 19 corridas e oito
anchors. Duplicatas/inviáveis são identificadas, sem random multistart.

## Oito anchors clássicos e RC

Coordenadas e objetivos abaixo são os mesmos em ambos os casos. MIN/MAX
permanece metadata explícita, e a escala é a natural das células.
Formatação numérica é apenas apresentação posterior ao cálculo.

| Resposta | Direção | x1 sphere=RC | x2 sphere=RC | x3 sphere=RC | Objetivo sphere=RC | D² sphere=RC | Esfera ativa | Delta x | Perda relativa |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| T | MAX | -1.53719111 | -0.525905413 | -0.434619494 | 66.1444764 | 6.28049303 | Sim | 0 | 0 |
| MTTF | MAX | -1.53649705 | -0.620505752 | -0.287361383 | 68.8976706 | 7.0541016 | Sim | 0 | 0 |
| WR | MIN | -1.37554995 | -0.539215823 | -0.803452391 | 0.00421457666 | 6.00121471 | Sim | 0 | 0 |
| Ra | MIN | -0.0778840625 | -1.53343206 | 0.276256839 | 0.280668816 | 5.63407771 | Não | 0 | 0 |
| Rt | MIN | -0.00512706475 | -1.63266922 | 0.403474991 | 1.84046438 | 7.14377657 | Sim | 0 | 0 |
| Kp | MIN | 1.36847743 | 0.789240201 | 0.576885219 | 1.65000077 | 6.52007425 | Sim | 0 | 0 |
| ROI | MAX | 1.11366638 | 1.26001112 | -0.0233731887 | 0.306345653 | 9.69254787 | Sim | 0 | 0 |
| OEE | MAX | -1.20695368 | -1.17118986 | -0.00206190729 | 0.576892134 | 9.4713686 | Sim | 0 | 0 |

Todos classificados INSIDE_RESPONSE_REGION (tolerância D²=1e-8).
Nenhuma fronteira RC ativa. Objetivo change assinado=f_RC-f_sphere;
deterioração positiva é +change para MIN e -change para MAX. Perda relativa
divide por abs(f_sphere), indefinida quando esse denominador é zero.
A tolerância 1e-6 define apenas a classificação descritiva de deslocamento.
Nenhuma resposta foi afetada; não há "mais afetada" entre oito perdas zero.

## Payoff clássica e payoff RC

Linhas=respostas; colunas=anchor otimizado para a resposta do cabeçalho.
A_ij=f_i(x_j). Utopia é a diagonal. A tabela aplica-se a ambas; os dois CSVs
existem separadamente e coincidem byte a byte, sem sobrescrita entre formulações.

| Resposta / anchor | T | MTTF | WR | Ra | Rt | Kp | ROI | OEE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| T | 66.144476 | 66.04439 | 65.718769 | 44.997372 | 43.714055 | 28.312841 | 29.553642 | 62.461665 |
| MTTF | 68.781944 | 68.897671 | 67.996428 | 47.244669 | 46.0482 | 30.750351 | 32.545846 | 65.883491 |
| WR | 0.0042495399 | 0.0042652324 | 0.0042145767 | 0.006421485 | 0.0066569974 | 0.012116275 | 0.011915109 | 0.0045404744 |
| Ra | 0.75709977 | 0.69290873 | 0.80993755 | 0.28066882 | 0.28533118 | 1.9181754 | 2.3226512 | 0.44903689 |
| Rt | 3.294417 | 3.1100011 | 3.4564506 | 1.8650227 | 1.8404644 | 6.8953721 | 8.0685452 | 2.4041607 |
| Kp | 4.8689014 | 5.0442779 | 4.2809717 | 4.2336639 | 4.2681892 | 1.6500008 | 1.8345321 | 5.0894504 |
| ROI | 0.058308662 | 0.051740822 | 0.072412591 | 0.075953741 | 0.069377451 | 0.29415267 | 0.30634565 | 0.036869068 |
| OEE | 0.5530272 | 0.56113484 | 0.53544446 | 0.51464843 | 0.52082807 | 0.23938283 | 0.22806937 | 0.57689213 |

D²(Utopia)=70560.1448517 em ambas as formulações: a diagonal está fora da
região descritiva embora cada coluna esteja dentro. Não se declara que U é
uma combinação conjuntamente atingível de respostas em um único ponto x.

## Região de respostas e cobertura empírica

phi é a média aritmética de Y; S_Y=(Y-phi)^T(Y-phi)/(n-1), não Sigma_e ou
h(x)Sigma_e. Posto=8; condition number≈2.17105e9; logdet≈-36.22716264.
Autovalores e matriz completa são preservados em response_region.json.
O gate de posto numérico/Cholesky foi aprovado sem pseudoinversa, jitter,
shrinkage, exclusão de respostas ou padronização manual.

| Resposta | phi |
|---|---:|
| T | 44.5921052632 |
| MTTF | 45.9940654592 |
| WR | 0.00737496347926 |
| Ra | 1.12789473684 |
| Rt | 4.43421052632 |
| Kp | 3.33947368421 |
| ROI | 0.184949548311 |
| OEE | 0.384716015859 |

D² dos 19 vetores observados: mínimo≈2.95753646, mediana≈6.71168432,
máximo≈12.56200471. Soma≈144=m*(n-1), verificação algébrica independente.
Cada distância e os quantis (method=linear) estão versionados.

| Cutoff | c | Observações dentro/fora | Anchors fora | Anchors deslocados |
|---|---:|---|---:|---:|
| Legacy chi-square 95% | 15.5073130559 | 19 / 0 | 0 | 0 |
| Quantil empírico MD² 95% | 12.2432703457 | 18 / 1 | 0 | 0 |
| Legacy chi-square 99% | 20.0902350297 | 19 / 0 | 0 | 0 |

Não há sensibilidade dos anchors nesse intervalo avaliado. O quantil empírico
não é uma confidence region; as distâncias in-sample dependem da própria média
e covariância estimadas. Nenhum dos três cutoffs fornece garantia de confiança
finita para esta nuvem proveniente de DOE fixo. A menor margem entre os anchors
e a região principal ainda é cerca de 5.81 unidades de D²; não há classificação
ambígua por erro de ponto flutuante.

## Antecedente bibliográfico e interpretação

A tese de Maia (2020), pp.21 e 84 (PDF 38 e 101), foi lida/renderizada e
sustenta o uso de uma restrição multivariada na definição dos anchors. Sua
formulação discutida em pp.19-21 usa ótimos ideais e covariâncias de predição;
não se atribui a ela, nem diretamente a Khuri/Conlon sem full text, a escolha
phi=mean(Y), S_Y=cov(Y). A nuvem 8-D aqui é uma definição experimental explícita.
Ver [fontes e limites](../../references/notes/phase_02_sources.md) e
[revisão dos cutoffs](multivariate_response_region.md).

O NIST distingue Hotelling para média, controle e inferência sobre observações;
regiões de tolerância ainda exigem definir conteúdo e confiança separadamente.
A aplicação de chi-square estimado com n=19,m=8 não está estabelecida como exata.
Restrições nos anchors não bastam para garantir Utopia admissível, como mostram
a derivação, o contraexemplo e o diagnóstico real. Adoção futura requer revisão
explícita; nenhum parâmetro ou decisão do C-NBI posterior foi adotado.

Os diagnósticos da Fase 1 já registram limitações de ajuste/predição dos modelos.
Encontrar um ótimo global da superfície não certifica que ele seja um ótimo
experimental ou que o modelo seja adequado. Isso não é corrigido por um cutoff
descritivo de Mahalanobis.

## Artefatos, reexecução e qualidade

Run: results/phase_02_anchors/turning_original_codes_20261024/.
Contém metadata, coded_models/coded_factors, response_region,
experimental_mahalanobis, anchors_sphere, anchors_response_region,
anchor_comparison, payoff_sphere, payoff_response_region, cutoff_coverage,
cutoff_sensitivity, utopia_diagnostic, todos os solver trials, summary e checksums.
Inputs/código/lock têm hashes; metadata registra commit efetivo de execução e
estado Git, n/alpha/direções, parâmetros/tolerâncias, propostas determinísticas,
ambiente e hash dos coeficientes. CSVs preservam float64 sem arredondamento prévio.
Novas execuções exigem um diretório vazio, impedindo sobrescrita silenciosa.

Validação: 300 testes, cobertura 99.08% (861/869), novo optimization/ e model/
com 100%; uv sync --locked, pytest -v, pytest --cov=cnbi_v2, Ruff e mypy src
(15 arquivos) aprovados. Oito statements antigos não cobertos no inspetor
permanecem; não houve perda de cobertura. CI será vinculada ao head do novo PR.
Ver [gate](../phase_2_verification.md).

ADR 0005 EXPERIMENTAL e claims C-ANCHOR-01/02, C-RC-01/02/03/04,
C-CODING-01 registradas. Raw, respostas integrais, golden reference, módulos
RSM anteriores e uv.lock preservados. Nenhum Monte Carlo, NBI/C-NBI, CHIM
combinatorial, PA, seleção de subconjuntos, shrinkage ou fase seguinte iniciado.
