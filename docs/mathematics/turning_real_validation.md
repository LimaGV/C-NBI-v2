# CCD real e comparação dos 80 coeficientes publicados

## Resultado

As 19 corridas e as oito respostas foram ajustadas com o módulo RSM existente,
preservando a precisão armazenada nas células. A reprodução integral de 80/80
coeficientes **não foi estabelecida**. Há concordância parcial forte sob hipóteses
explícitas de desenho nominal e escala; WR apresenta uma assinatura de
arredondamento prévio incompatível com a exigência de manter os dados reais.

## Entrada experimental

Nova revisão recebida em 2026-10-23: CCD_values_20261023.xlsx, Plan1!A1:L20.
SHA-256: 7f905b7a2f7bb8b6735ab96900cba7356401df2d26c961dcb12faa2683c6c71e.
11283 bytes, 19 IDs em A2:A20 e **209 números em B2:L20 = 19×(3+8)**.
Todos os 228 valores de dados, incluindo IDs, são literais; zero fórmulas,
vazios ou dependências externas detectadas na inspeção completa.
Não houve recálculo, save do Excel, correção de célula ou imputação.

O raw anterior CCD_original.xlsx e seu hash fd9c463e... permanecem intactos.
Como auditoria, os números literais da revisão atual coincidem com os números
anteriormente presentes nos caches. O ajuste atual lê apenas o novo raw literal;
não utiliza esses caches históricos como fonte computacional.

O CSV em data/processed/turning_application/CCD_values_20261023.csv preserva
os tokens numéricos originais do OOXML, não o texto formatado pela interface.
Exemplos: F2 é `68.306215222565058`, G2 é `4.4924127802190104E-3`.
Os tokens são convertidos diretamente a float64 para o ajuste; não são
arredondados antes do OLS. A cópia XLSX byte-identical preserva a evidência integral.
Não é necessário produzir um snapshot adicional a partir de fórmulas.

## Ajustes e desenhos explicitamente separados

Y é sempre a mesma matriz 19×8, na ordem T,MTTF,WR,Ra,Rt,Kp,ROI,OEE, em unidades
das células. A ordem dos fatores é cs/f/md, com aliases contextuais Vc/f/ap.
Cada caso usa a base completa canônica do módulo, dez termos e rank=10, nu=9.
Todos os ajustes têm equivalência com oito regressões OLS separadas.

| Caso | Fatores efetivamente usados | Interpretação |
|---|---|---|
| physical_cells | Os números B2:D20, inalterados | Ajuste real nas coordenadas físicas das células |
| affine_from_cells | (x-centro)/meia_amplitude_fatorial | Recodificação explícita dos próprios fatores observados |
| table6_rounded_alpha | Ordem e sinais da Table 6, alpha=1.682 | Desenho nominal com precisão impressa; quadrados recalculados pela base |
| rotatable_alpha_hypothesis | Mesmo desenho nominal, alpha=8^(1/4) | Hipótese CCD rotacional, sem otimização de alpha |

No caso afim, centro=[162.5,0.16,0.24] e meia amplitude=[62.5,0.06,0.09],
obtidos dos cinco centros e dos oito pontos fatoriais do arquivo.
Os pontos axiais físicos não se convertem exatamente em ±1.682 por essa regra.
O caso nominal é alinhado por Exp e pela ordem da Table 6; não é apresentado
como uma transformação afim exata dos valores físicos das células.

A Table 6, p.18, imprime alpha=1.682 e quadrados=2.828. A hipótese rotacional
usa alpha=1.681792830507429 e alpha²=2.828427124746..., ambos compatíveis com
o arredondamento impresso. A fórmula alpha=(número de pontos fatoriais)^(1/4)
tem apoio independente no [NIST/SEMATECH, seção 5.3.3.6.1](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3361.htm).
Isso não prova a precisão interna usada pelos autores; sua concordância numérica
é evidência condicional. Não se escolheu alpha por busca numérica ou otimização.

O número de condição de X físico é aproximadamente 1.1185e7, contra 3.9114 no
desenho rotacional nominal. Portanto os coeficientes físicos e codificados não
podem ser comparados diretamente como se fossem a mesma parametrização.
As divergências da Table 1 com os níveis físicos do workbook permanecem abertas.

## Comparação e escalas

Os 80 valores da golden reference permanecem como impressos, sem alteração.
Comparação por intervalo de arredondamento: meia unidade na última casa impressa,
portanto ±0.0005 para três casas, incluindo empates. Só se acrescenta uma margem
numérica de 16*eps*max(1,abs(calculado),abs(publicado)) para fronteiras float64.
Nenhum limite foi ajustado para aceitar divergências experimentais.

A nota da Table 3, p.13, declara WR/ROI/OEE em 10^-2. Sua interpretação literal
aplica multiplicador de apresentação 100 aos coeficientes calculados.
O multiplicador 1000 é registrado como **diagnóstico conflitante com essa nota**,
nunca como correção silenciosa. T/MTTF/Ra/Rt/Kp têm multiplicador 1.
Os multiplicadores são aplicados somente depois do OLS, sem alterar Y.

| Desenho | Nota literal ×100 | Diagnóstico ×1000 |
|---|---:|---:|
| Coordenadas físicas das células | 0/80 | 0/80 |
| Transformação afim dos próprios fatores | 22/80 | 31/80 |
| Table 6 com alpha arredondado | 45/80 | 54/80 |
| Hipótese nominal rotacional exata | **50/80** | **70/80** |

No último caso, a comparação por resposta é:

| Resposta | Nota literal | Escala diagnóstica | S calculado em unidades das células | R² calculado (%) |
|---|---:|---:|---:|---:|
| T | 10/10 | 10/10 | 3.044461103 | 96.473381 |
| MTTF | 10/10 | 10/10 | 3.034021568 | 96.561790 |
| WR | 0/10 | 0/10 | 0.000519034 | 97.622580 |
| Ra | 10/10 | 10/10 | 0.274577911 | 91.361843 |
| Rt | 10/10 | 10/10 | 0.871754587 | 90.163692 |
| Kp | 10/10 | 10/10 | 0.193534089 | 98.289072 |
| ROI | 0/10 | 10/10 | 0.007244015 | 99.491273 |
| OEE | 0/10 | 10/10 | 0.007162154 | 99.697462 |

S=sqrt(MSE); R²=1-SSE/SST, com SST centrado por resposta. Nenhum teste de
normalidade, significância, convexidade ou direção de otimização foi inferido.

## Diagnóstico de WR, sem substituir o modelo real

Classificação: `PUBLICATION_RECONCILIATION_NOTE`. Esse experimento histórico
é excluído do pipeline oficial de diagnósticos do fechamento da Fase 1.

Com dados completos e desenho nominal rotacional, os coeficientes de WR,
apresentados somente aqui com ×1000, são:

| Termo | Calculado com valores reais | Table 3 |
|---|---:|---:|
| beta0 | 6.643905899 | 6.785 |
| beta1 | 2.468323811 | 2.573 |
| beta2 | 0.701061247 | 0.709 |
| beta3 | -0.004307533 | 0.146 |
| beta11 | 0.712880407 | 0.683 |
| beta22 | 0.436733681 | 0.329 |
| beta33 | -0.132535501 | -0.201 |
| beta12 | +0.042135680 | -0.250 |
| beta13 | -0.055980242 | 0.000 |
| beta23 | -0.044156814 | 0.000 |

Até o sinal de beta12 difere; não se trata apenas da última casa decimal.
O R² publicado para WR é 96.63%, enquanto o ajuste completo dá 97.622580%.

Uma hipótese exploratória posterior, motivada pela estrutura das interações,
foi testada em cópia: arredondar **WR em unidades das células a três casas antes
do OLS**. Isso altera 19/19 observações e reproduz 10/10 coeficientes de WR,
com o mesmo desenho nominal e multiplicador diagnóstico 1000.
É consistente com pré-arredondamento na cadeia publicada, mas não comprova
o procedimento dos autores. Não é validação com os valores reais das células.
Esse diagnóstico é opcional, explicitamente nomeado e excluído dos totais 50/70;
nenhum dado arredondado é salvo como observação ou usado nos quatro ajustes reais.

## Reexecução e artefatos

```powershell
uv sync --locked
uv run python -m scripts.validation.turning_reference --investigate-wr-rounding
uv run pytest -v
uv run pytest --cov=cnbi_v2
uv run ruff check .
uv run mypy src
```

Resultados em results/turning_8responses_validation/: quatro pastas com fatores
usados, coeficientes nas unidades reais, fitted values, resíduos, Sigma_hat_e e
resumo; comparação de todos os 80 termos em cada um dos oito cenários (640 linhas);
summary.json, manifest.json, checksums.sha256 e diagnóstico opcional de WR.
O manifesto registra commit real de execução, estado Git, ambiente e hashes de
entradas, código, lock e saídas. Dados experimentais não derivam da golden reference.

ADR 0004 registra esta evidência como EXPERIMENTAL/PARTIAL. A CI passar atesta
integridade e reprodutibilidade dos resultados, incluindo as divergências;
não equivale a afirmar que 80 coeficientes publicados foram reproduzidos.
Antes de aceitar o caso inteiro: confirmar codificação física versus nominal,
precisão de alpha, discrepância da nota de escala e tratamento original de WR.
Sem Monte Carlo, shrinkage, otimização ou início de outra fase.

## Qualidade e integridade

193 testes passam, incluindo a comparação real, preservação da revisão antiga,
extração sem arredondamento e diagnóstico que não altera os totais reais.
Cobertura de produção: 97.78%, com 100% no módulo model. Ruff e mypy aprovados.
O módulo em src/ e uv.lock não foram alterados nesta validação aplicada;
os dois CSVs de expected outputs publicados também permanecem inalterados.
