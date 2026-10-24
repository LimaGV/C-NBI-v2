# 0003 — Fundação RSM multivariada e incerteza analítica

- Tipo: ADR com definição metodológica explícita
- Status: ACCEPTED
- Responsável: solicitação explícita do responsável pelo C-NBI v2; implementação pelo agente
- Data: 2026-10-23
- Branch: feature/01-multivariate-rsm-foundation
- Commit/PR: registrar no PR após criação; não inventar SHA autorreferente
- Versão: 0.1.0.dev0
- Substitui: restrição de não iniciar Fase 1 nas fases anteriores, somente para este escopo
- Validation gate: PASSED (validação analítica e sintética local; CI vinculada ao PR)

## Contexto e definição

Primeira implementação científica independente da v1. A autorização atual pede
explicitamente esta decisão como ACCEPTED. O estado não é uma aceitação
automática derivada de testes, nem aprova as fases futuras ou valida o caso real.
Definições, pressupostos e derivações estão em
[RSM](../mathematics/multivariate_rsm.md) e
[incerteza](../mathematics/rsm_uncertainty.md).

## Decisão

- Base quadrática completa, sem eliminar termos. Ordem: intercepto, lineares,
  quadráticos puros e interações i<j lexicográficas.
- OLS multivariado por numpy.linalg.lstsq, equivalente a ajustes por coluna.
  float64, rcond=eps*max(n,p), posto reportado e condição de X registrada.
- Posto menor que p ou nu=n-rank(X)<=0 causa falha explícita.
- V_X por QR reduzida: solve(R,I) solve(R,I)^T, sem inversa explícita/normal equations.
- Covariância residual bruta E_hat^T E_hat/nu; sua diagonal é MSE por resposta.
- vec por colunas de B_hat: covariância estimada Sigma_hat_e⊗V_X e estrutura
  matrix-normal sob normalidade, distinguindo parâmetros e estimativas.
- Incerteza da média h Sigma_hat_e, covariância cruzada entre pontos e incerteza
  da diferença por contraste z_a-z_b. Não adicionar erro de nova observação.
- Leverages calculados com solve(R^T,z), e diferenças com solve(R^T,z_a-z_b).
- Checagem de simetria/PSD com eps*d*||M||_inf; falhar em violação significativa,
  sem correção, clipping, jitter, shrinkage ou regularização.
  Para evitar overflow, somente a cópia diagnóstica é dividida por max(abs(M)).
- Resultado imutável, inputs preservados; sem normalização/codificação implícita.
- Sem Monte Carlo, sampling, Cholesky de amostragem, otimização, âncoras, payoff,
  CHIM, PA, NBI/CNBI, Pareto, seleção de subconjuntos ou H.

## Evidência e alternativas

[Nota das fontes R002-R005](../../references/notes/rsm_foundation_sources.md):
Zotero consultado primeiro. R003 (preprint dos autores) e R004 (livro local)
têm passagens diretamente verificadas; os limites de acesso e de cobertura
estão explícitos. R001 sustenta apenas o caso aplicado já documentado.
C-RSM-01/02/04/05 têm apoio de literatura; C-RSM-03/06 e extensões de
covariância têm derivação e testes analíticos independentes.

Inverter X^TX no ajuste piora a estabilidade e não foi adotado. Ridge,
pseudoinversa em deficiência de posto e ajuste parcial mudariam o problema.
Uma simulação repetida seria menos direta para estas identidades e foi dispensada.
Seed de fixture sintética não é parâmetro do futuro C-NBI.

## Validação e consequências

Critérios: ordem determinística da base, recuperação sem ruído, equivalência
uni/multivariada, resíduos, MSE, simetria/PSD, blocos e orientação da covariância,
leverage, predição, covariâncias cruzadas/diferenças, permutações e falhas de input.
Testes não usam dados reais nem os coeficientes publicados como observações.
Cobertura de base medida antes das mudanças: 200/208 statements, 96.15%.
O novo código deve preservar essa cobertura e a imutabilidade do raw.

O raw real continua não autocontido; não houve ajuste nem reprodução da Table 3.
nu=9 para o caso real é apenas dimensional, condicionado a rank(X)=10;
não implica adoção de shrinkage. A próxima fase exige nova tarefa.

## Revisão e histórico

### Fechamento autorizado da Fase 1 — diagnósticos (2026-10-23)

Estende o escopo aceito, por solicitação explícita do responsável, com as
definições de [rsm_diagnostics.md](../mathematics/rsm_diagnostics.md).
Mantém a mesma base e OLS, sem remoção de termos por significância.
PRESS é analítico e validado por LOOCV explícito; pure error usa igualdade exata
dos fatores e LOF só é testado quando seus graus de liberdade e denominador
permitem. Ausências têm representação tipada e razão explícita.
H diagonal é obtida das normas de linhas de Q, com verificação de limites/traço.
Dois inputs imutáveis fundamentais são preservados em RSMFit: fatores e Y;
as métricas ficam no módulo separado. Isso conserva os valores reais e a
associação entre observações, evitando reconstrução de dados por soma numérica.

A revisão literal do raw é a entrada canônica e não é arredondada. Os quatro
desenhos já registrados recebem diagnósticos separados; a tabela principal
usa physical_cells, e a comparação secundária usa também a hipótese nominal
rotacional explicitamente identificada. Não se altera codificação para coincidir
com a publicação. Table 3 permanece secundária; seu R²_pred não tem método
PRESS/LOOCV explicitamente identificado no artigo inspecionado.
O diagnóstico histórico de WR arredondado é PUBLICATION_RECONCILIATION_NOTE,
fora do pipeline oficial. As inconsistências de WR/escala ROI/OEE não são
tratadas como defeitos da implementação. ADR 0004 existente não é sobrescrita.
Claims C-RSM-07 a 11 ligam literatura, derivação e testes; gate e execução
aplicada são registrados no relatório de diagnósticos e no PR #4, sem merge.

Decisão aceita no escopo solicitado pelo responsável em 2026-10-23.
Resultados efetivos do gate estão na [verificação da Fase 1](../phase_1_verification.md);
CI remota vinculada ao SHA no PR. A aceitação não certifica o dataset real.
