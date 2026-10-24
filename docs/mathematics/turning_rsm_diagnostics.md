# Diagnósticos do CCD real — fechamento da Fase 1

## Resultado e entrada preservada

Os oito RSMs completos foram diagnosticados com os 209 valores literais
19×(3+8) da revisão autocontida, sem arredondamento ou reconstrução de respostas.
Raw: `data/raw/turning_application/CCD_values_20261023.xlsx`, Plan1!A1:L20.
SHA-256: `7f905b7a2f7bb8b6735ab96900cba7356401df2d26c961dcb12faa2683c6c71e`.
O raw histórico, a extração literal, a golden reference e uv.lock permanecem
inalterados. As definições/API/fontes estão em [rsm_diagnostics.md](rsm_diagnostics.md).

Foram preservados os quatro ajustes anteriores: physical_cells,
affine_from_cells, table6_rounded_alpha e rotatable_alpha_hypothesis.
Os dois primeiros usam os fatores das células ou sua transformação afim;
os dois últimos são desenhos nominais publicados/hipotéticos já identificados.
Não há nova codificação ou seleção para obter concordância. A tabela principal
abaixo usa **physical_cells**, os fatores efetivamente armazenados. A comparação
secundária destaca o caso nominal rotacional; ele não é uma transformação afim
exata das coordenadas físicas. Isso continua sendo uma limitação de referência.

Todos os casos: N=19, n_x=3, m=8, p=rank=10, df_model=9, df_error=9.
A API preserva fatores e observações imutáveis, em float64, além dos resultados
já existentes. Testes conferem os coeficientes contra os artefatos anteriores.

## Tabela principal — fatores físicos das células

R²/R²_adj/R²_pred abaixo são percentuais; os CSVs da API guardam frações.
S e PRESS mantêm as unidades das células (PRESS em unidades ao quadrado).
A formatação desta tabela é apenas apresentação posterior ao cálculo.

| Resposta | S | R² (%) | R²_adj (%) | PRESS | R²_pred (%) | F_model | p_model | F_LOF | p_LOF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| T | 3.0003595 | 96.574813 | 93.149626 | 622.00687 | 73.70396 | 28.195487 | 1.5273793e-05 | 27.380667 | 0.0034262264 |
| MTTF | 3.0279502 | 96.575537 | 93.151073 | 633.20309 | 73.721802 | 28.201655 | 1.5259605e-05 | 27.918969 | 0.0033007764 |
| WR | 0.00050637108 | 97.737168 | 95.474336 | 1.625548e-05 | 84.060606 | 43.192411 | 2.4466524e-06 | 5.5710692 | 0.060527252 |
| Ra | 0.27012536 | 91.639724 | 83.279448 | 4.8507938 | 38.246692 | 10.961327 | 0.00073057454 | 1312.6187 | 1.6221352e-06 |
| Rt | 0.86064013 | 90.412909 | 80.825819 | 46.031683 | 33.799999 | 9.4306931 | 0.0013029199 | 8.6010899 | 0.029028757 |
| Kp | 0.18602628 | 98.419242 | 96.838483 | 2.4477747 | 87.576447 | 62.260778 | 4.9674987e-07 | 14.137745 | 0.011883149 |
| ROI | 0.0057844915 | 99.675619 | 99.351237 | 0.0022522489 | 97.573951 | 307.27903 | 4.1374475e-10 | 67.680037 | 0.00059011672 |
| OEE | 0.005340404 | 99.831794 | 99.663589 | 0.0019032017 | 98.752804 | 593.51007 | 2.1637636e-11 | 32.543421 | 0.002458323 |

A 5%, como leitura descritiva de testes individuais sem correção de
multiplicidade, as oito respostas rejeitam o modelo de intercepto apenas.
Há evidência de falta de ajuste para T, MTTF, Ra, Rt, Kp, ROI e OEE.
WR tem p_LOF≈0.06053 no caso físico e ≈0.05519 no nominal rotacional,
portanto não rejeita nesse limiar. Isso não certifica adequação de WR.
R² elevado e significância global coexistem com falta de ajuste; a ANOVA global
não é teste de que a superfície representa toda a estrutura experimental.
A inferência F pressupõe independência, normalidade e variância constante por
resposta, não comprovadas somente por esses números.

## Réplicas, pure error e LOF

O agrupamento por igualdade exata de fatores detectou **15 configurações únicas**
e **um grupo de cinco corridas**, Exp 15,16,17,18,19, em todos os quatro casos.
Logo df_PE=19-15=4 e df_LOF=15-10=5. Não há `5` hard-coded na rotina genérica.
Os cinco resultados centrais são tratados como réplicas experimentais conforme
identificados no caso; sua independência física continua sendo pressuposto.

`lack_of_fit.csv` contém SS_PE, MS_PE, SS_LOF, MS_LOF, F/p e erro numérico da
identidade SSE=SS_PE+SS_LOF, por resposta/caso. Todos os testes LOF reais são
estimáveis: SS_PE>0 e ambos os graus de liberdade positivos.
`anova.csv` registra modelo/erro/total corrigido. Os grupos e leverages estão
em summary.json; press_residuals.csv preserva Exp e os erros leave-one-out.
Não se constrói H inteiro; sum(h)=10 dentro da margem numérica documentada.

## Table 3 — comparação secundária sob hipótese nominal rotacional

Fonte primária: Pereira et al. (2025), *A hybrid multivariate normal boundary
intersection approach with post-optimization assisted by mixture design of
experiments*, Engineering Applications of Artificial Intelligence,
[DOI 10.1016/j.engappai.2025.112510](https://doi.org/10.1016/j.engappai.2025.112510),
Zotero SMMX47JT, PDF local verificado, Table 3 p.13, FULLTEXT_VERIFIED.
A [nota de leitura](../../references/notes/pereira_2025_hybrid_vrf_nbi.md)
registra a auditoria: não foi encontrada definição PRESS/LOOCV do R²_pred da
tabela. A discussão de machine learning/cross-validation em cinco folds nas
pp.22-23 não determina esse método. Classificação:
`PUBLISHED_R2_PRED_METHOD_UNSPECIFIED`; não se presume equivalência metodológica.

Na tabela abaixo S é apresentado em 10^-2 (calculado×100), como na nota própria
de S; os três R² são percentuais. Diferença=calculado-publicado nessas unidades.
O texto publicado foi preservado no CSV, sem precisão inventada.
Compatibilidade usa meia unidade da última casa impressa (±0.005 para estas
estatísticas), mais apenas margem de fronteira float64. Não se alarga intervalo
para aceitar divergências. Compatibilidade numérica de R²_pred não prova método.

| Resposta | Métrica | C-NBI v2 (display) | Publicado | Diferença | No intervalo de arredondamento? |
|---|---|---:|---:|---:|---|
| T | S | 304.44611 | 304.44 | +0.006110303 | Não |
| T | R2 | 96.4733811 | 96.47 | +0.003381066 | Sim |
| T | R2_adj | 92.9467621 | 92.95 | -0.003237868 | Sim |
| T | R2_pred | 73.7858047 | 73.79 | -0.004195316 | Sim |
| MTTF | S | 303.402157 | 303.40 | +0.002156782 | Sim |
| MTTF | R2 | 96.56179 | 96.56 | +0.001789995 | Sim |
| MTTF | R2_adj | 93.12358 | 93.12 | +0.00357999 | Sim |
| MTTF | R2_pred | 74.4437992 | 74.44 | +0.003799185 | Sim |
| WR | S | 0.0519033821 | 0.06 | -0.008096618 | Não |
| WR | R2 | 97.6225805 | 96.63 | +0.9925805 | Não |
| WR | R2_adj | 95.245161 | 93.27 | +1.975161 | Não |
| WR | R2_pred | 82.8858327 | 78.11 | +4.775833 | Não |
| Ra | S | 27.4577911 | 27.46 | -0.002208904 | Sim |
| Ra | R2 | 91.3618426 | 91.36 | +0.00184264 | Sim |
| Ra | R2_adj | 82.7236853 | 82.72 | +0.003685281 | Sim |
| Ra | R2_pred | 34.0288814 | 75.95 | -41.92112 | Não |
| Rt | S | 87.1754587 | 87.18 | -0.004541269 | Sim |
| Rt | R2 | 90.1636916 | 90.16 | +0.003691634 | Sim |
| Rt | R2_adj | 80.3273833 | 80.33 | -0.002616733 | Sim |
| Rt | R2_pred | 29.8238397 | 73.60 | -43.77616 | Não |
| Kp | S | 19.3534089 | 19.35 | +0.003408864 | Sim |
| Kp | R2 | 98.2890716 | 98.29 | -0.0009283562 | Sim |
| Kp | R2_adj | 96.5781433 | 96.58 | -0.001856712 | Sim |
| Kp | R2_pred | 87.0788539 | 87.08 | -0.001146063 | Sim |
| ROI | S | 0.724401534 | 0.72 | +0.004401534 | Sim |
| ROI | R2 | 99.4912735 | 99.49 | +0.001273494 | Sim |
| ROI | R2_adj | 98.982547 | 98.98 | +0.002546987 | Sim |
| ROI | R2_pred | 96.1533152 | 96.15 | +0.00331523 | Sim |
| OEE | S | 0.716215435 | 0.72 | -0.003784565 | Sim |
| OEE | R2 | 99.697462 | 99.70 | -0.002537993 | Sim |
| OEE | R2_adj | 99.394924 | 99.39 | +0.004924013 | Sim |
| OEE | R2_pred | 97.7265795 | 97.73 | -0.003420516 | Sim |

Sob esse mesmo desenho já registrado, coincidem **6/8 S**, **7/8 R²**,
**7/8 R²_adj** e **5/8 R²_pred** no intervalo impresso. A comparação completa dos
quatro casos, com diferenças e intervalos por célula, é
`published_summary_comparison.csv`. Os fatores físicos/afins não coincidem com
Table 3; isso acompanha a distinção de desenhos documentada antes desta tarefa.

Divergências relevantes:

- WR integral: R²≈97.62258%, R²_adj≈95.24516%, R²_pred≈82.88583%, contra
  96.63%, 93.27%, 78.11%. S≈0.05190338 em unidades impressas, contra 0.06.
  É inconsistência da publicação/reference case já identificada. Nenhum valor
  foi arredondado no ajuste. O experimento histórico em cópia arredondada recebe
  `PUBLICATION_RECONCILIATION_NOTE`, fora deste pipeline e não reexecutado aqui.
- Ra: PRESS/LOOCV dá R²_pred≈34.02888%, publicado 75.95%; Rt: ≈29.82384%,
  publicado 73.60%. Os R²/R²_adj coincidem, mas a predição não. A causa não está
  confirmada; método publicado não especificado impede atribuir a divergência
  a erro do novo módulo. Não se tenta reconciliar por ajuste de dados/modelos.
- T: S×100≈304.44611, publicado 304.44, diferença ≈0.00611 > 0.005.
  Fica fora do intervalo de arredondamento convencional. Não se presume que
  tenha sido truncado nem se altera a tolerância para aceitar esse valor.
- ROI/OEE: métricas invariantes de escala coincidem no caso nominal, inclusive
  R²_pred. A inconsistência de escala dos coeficientes (nota 10^-2 versus
  evidência numérica condicional 10^-3) permanece na referência publicada.
  Não se aplicou multiplicador ao Y. A nota própria de S é tratada separadamente;
  nenhuma escala adicional WR/ROI/OEE foi empilhada sobre S.

Multiplicar Y por c!=0 preserva R²/R²_adj/R²_pred/F/p; S muda por abs(c) e
SSE/MSE/PRESS por c². Essas identidades foram verificadas com dados sintéticos.
Diferenças de R²_pred de Ra/Rt não são explicáveis por um multiplicador de Y.

## Execução, testes e rastreabilidade

```powershell
uv sync --locked
uv run python -m scripts.validation.turning_diagnostics
uv run pytest -v
uv run pytest --cov=cnbi_v2
uv run ruff check .
uv run mypy src
```

Artefatos pequenos explicitamente autorizados em `results/validation/turning_rsm/`:
model_diagnostics.csv (oito respostas físicas), all_cases_model_diagnostics.csv
(32 linhas), anova.csv (96), lack_of_fit.csv (32), press_residuals.csv (76),
published_summary_comparison.csv (128), summary.json, manifest.json e checksums.
O manifesto registra commit efetivo de execução, branch, estado Git, comando,
ambiente, versões e hashes de código/inputs/saídas, além dos hashes raw antes e
depois. A execução original ocorreu sobre HEAD 384bb97 com alterações pendentes,
explicitamente registradas como git_working_tree_dirty=true. Os hashes do código
efetivamente executado preservam a identidade dessa versão. O fechamento registra
separadamente o commit que contém esse código e o gate aprovado, evitando SHA
autorreferente. Não se regravam os arquivos numéricos para mudar a proveniência.
PDFs e bibliotecas pessoais não são incorporados.
O [registro do gate](../phase_1_diagnostics_validation.json) vincula os hashes
executados ao commit ac6e7a98842e1f1c32fd2240e2a266738264fcd9, confirma
identidade dos blobs versionados e preserva os hashes de todos os CSVs numéricos.

Validação: 237 testes passam, cobertura total 98.47% (516/524 statements),
novo diagnostics.py 100% (160/160), model/ 100%. Oráculos manuais de SS/R²/F e
PRESS, LOOCV explícito uni/multirresposta, polinômio exato, R²_pred negativo,
replicação exata, cenários PE/LOF e todos os casos degenerados passam.
As identidades anteriores de covariância e incerteza permanecem verificadas.
O primeiro gate remoto revelou diferença LAPACK Windows/Ubuntu de até
7.10542736e-12 nos coeficientes físicos, com erro relativo máximo 2.77976713e-12;
o limite fixo 2e-14 do novo teste de preservação era excessivamente estrito.
Somente esse teste passou a comparar erros por norma máxima de cada coluna B,
com margem eps*max(n,p)*condition(X), derivada da escala de erro de primeira
ordem e do rcond já existente. Isso distingue arredondamento de plataforma,
sobretudo com condition(X_fisico)≈1.1e7, sem alterar qualquer coeficiente, solver,
tolerância de posto, intervalo de arredondamento publicado ou arquivo numérico.
Gate final de 2026-10-24: uv sync --locked, pytest -v, pytest --cov=cnbi_v2,
Ruff e mypy src aprovados (10 arquivos de produção no mypy). CI remota
vinculada ao head no PR #4. A retomada preservou metodologia e números já obtidos.

ADR 0003 atualizada, sem colidir com a ADR 0004 aplicada existente.
Claims C-RSM-07 a 11 possuem evidência diretamente verificada e limites.
Nenhum termo removido, beta t-test individual, otimização, Monte Carlo ou
NBI/CNBI implementado. Dados não foram reconstruídos ou alterados.
A Fase 1 está concluída no escopo solicitado; a discrepância com a publicação
não equivale a aceitar o caso inteiro como reproduzido ou adequado para otimizar.
Não se inicia a fase seguinte automaticamente.
