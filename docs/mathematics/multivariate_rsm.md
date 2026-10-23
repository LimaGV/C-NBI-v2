# Fundação do RSM multivariado

Escopo aceito na [ADR 0003](../decisions/0003-multivariate-rsm-and-uncertainty-foundation.md).
Esta fase implementa estimação e identidades analíticas, com validação sintética.
Não valida ainda o experimento real nem implementa otimização.

## Base e dimensões

Sejam os fatores `x` de dimensão n × n_x. A função `quadratic_design(x)`
constrói X de dimensão n × p, com p = (n_x+1)(n_x+2)/2. A ordem é:
intercepto, lineares, quadráticos puros e interações i<j em ordem lexicográfica.
Para três fatores:

```text
intercept, x1, x2, x3, x1^2, x2^2, x3^2, x1*x2, x1*x3, x2*x3
```

Não há centralização, codificação, padronização ou conversão de unidades implícita.
Quem chama a API fornece a escala dos fatores e das respostas explicitamente.
Entradas são arrays numéricos reais finitos; fatores de ajuste têm shape (n,n_x),
com n_x>=1. Y pode ter shape (n,m) ou (n,), promovido para (n,1).

O modelo é Y = XB + E, com Y e E de dimensão n × m e B de dimensão p × m.
B e Sigma são parâmetros populacionais desconhecidos. `coefficients` contém
B_hat; `residual_covariance` contém Sigma_hat_e, nunca a matriz populacional.
As linhas do erro têm média zero, covariância comum Sigma e não têm covariância
entre observações; X é tratado como fixo e de posto completo. Normalidade não é
necessária para as identidades de segundo momento. Para a distribuição
matrix-normal, exige-se adicionalmente erro conjuntamente normal.

## Ajuste e estimativas

Matematicamente, B_hat = (X^T X)^(-1) X^T Y. O critério Frobenius é a soma
dos critérios OLS por coluna; portanto o ajuste conjunto é equivalente a m
regressões univariadas com o mesmo X. A covariância entre respostas acrescenta
informação de incerteza, sem alterar esses coeficientes OLS.

A implementação usa `numpy.linalg.lstsq(X,Y,rcond=eps*max(n,p))`, em float64.
A tolerância relativa de posto é explícita e registrada no resultado, junto
ao número de condição de X. Posto menor que p causa ValueError: não se retorna
uma solução de norma mínima para um modelo não identificável.

Definem-se fitted_values = X B_hat e residuals = E_hat = Y-X B_hat.
Graus de liberdade: nu = n-rank(X). Exige-se nu>0, inclusive para um ajuste
sem ruído. A API não elimina termos e não aplica regularização.

\[
MSE_j = \frac{\hat e_j^T\hat e_j}{\nu},\qquad
\hat\Sigma_e = \frac{\hat E^T\hat E}{\nu}.
\]

A implementação calcula o Gram residual completo e copia sua diagonal para
`mse_by_response`; cada entrada coincide com a definição univariada acima.
Os elementos fora da diagonal são covariâncias dos resíduos após o ajuste,
não a covariância ou correlação bruta entre colunas de Y.
Sigma_hat_e pode ser singular, por exemplo com respostas redundantes ou ajuste
sem ruído. Isso não autoriza clipping, jitter ou shrinkage.

Para ver a ausência de viés, seja A=(X^TX)^(-1)X^T e P=XA. Então
E_hat=(I-P)E e (I-P) é simétrica idempotente com traço nu. Para respostas j,k,
E[E_hat_j^T E_hat_k] = tr(I-P) Sigma_jk = nu Sigma_jk.
Logo E[Sigma_hat_e]=Sigma e diag(Sigma_hat_e)_j=MSE_j.
Esta é uma derivação matemática sob as hipóteses indicadas, não evidência empírica
de que os erros do torneamento satisfaçam essas hipóteses.

## Fator de covariância do projeto e qualidade numérica

Com QR reduzida X=QR, resolve-se R W=I e calcula-se V_X=W W^T.
Assim V_X=(X^TX)^(-1), sem formar/inverter as equações normais.
`xtx_covariance_factor` contém V_X e `design_r_factor` contém R.
Leverages usam soluções com R^T, evitando cancelamento em formas quadráticas.

Valores derivados não finitos causam falha. A verificação de simetria/PSD usa
apenas a escala de arredondamento eps*d*||M||_inf para matriz d×d. Violação
maior causa LinAlgError. A matriz não é simetrizada ou corrigida. Essa tolerância
numérica não é uma tolerância de comparação com coeficientes publicados.
A checagem usa uma cópia dividida por max(abs(M)) para evitar overflow na norma;
a matriz retornada permanece exatamente a calculada. Matriz zero é PSD.
Fatores mal escalados podem produzir problemas de condição: a API diagnostica
o número de condição e rejeita deficiência numérica de posto, sem recodificar.

O resultado é uma dataclass frozen com arrays próprios sobre buffers imutáveis.
Os inputs não são modificados. `predict` aceita ponto (n_x,) e retorna (m,), ou
matriz (q,n_x) e retorna (q,m). Todas as APIs de incerteza de ponto exigem (n_x,).

## API pública em cnbi_v2.model

| API | Resultado |
|---|---|
| quadratic_term_names(n_factors) | Nomes canônicos em tuple |
| quadratic_design(factors) | Base (n,p) |
| fit_multivariate_rsm(factors,responses) | RSMFit, com estimativas e diagnósticos |
| RSMFit.predict(factors) | Média estimada em um ou vários pontos |
| coefficient_covariance(result) | (pm,pm), vec por colunas |
| coefficient_covariance_by_response(result,j) | Bloco (p,p), resposta j iniciando em 0 |
| prediction_leverage(result,point) | h(x) escalar |
| mean_prediction_covariance(result,point) | (m,m), estimativa h Sigma_hat_e |
| mean_prediction_variance(result,point) | (m,), estimativa h MSE_j |
| cross_prediction_leverage(result,a,b) | h_cross_ab escalar, pode ser negativo |
| cross_prediction_covariance(result,a,b) | (m,m), estimativa cruzada |
| difference_prediction_leverage(result,a,b) | h_ab escalar não negativo |
| difference_prediction_covariance(result,a,b) | (m,m), estimativa da diferença |

## Conexão com o caso de torneamento

Atualização aplicada: o usuário forneceu revisão literal autocontida do CCD.
Ver [validação real e limites](turning_real_validation.md): oito RSMs ajustados
sem mudar a precisão das células; reprodução publicada parcial, com escalas e
WR não reconciliados. O parágrafo seguinte descreve o estado inicial da Fase 1.

Somente as dimensões verificadas são usadas: n=19, n_x=3, m=8, p=10.
Se rank(X)=10, nu=9, B tem dimensão 10×8 e Sigma_hat_e teria dimensão 8×8.
Isso é um fato estrutural condicionado ao posto, sem conclusão sobre shrinkage.
O raw continua RAW_NOT_SELF_CONTAINED, sem snapshot certificado.
Não foi ajustado, não houve comparação numérica com a Table 3 e C011 permanece
UNVERIFIED. Não há acesso ao raw ou à golden reference pelo código de produção.

## Evidências e software

- [R003: preprint de Díaz-García e Bashiri](../../references/notes/rsm_foundation_sources.md),
  seção 2, pp.2-3: modelo comum, base, OLS e estimativa residual.
- [R004: Myers, Montgomery e Anderson-Cook](../../references/notes/rsm_foundation_sources.md),
  4a ed., pp.16-17 e 22-23: OLS, resíduos, covariância e MSE.
- R001: Pereira et al. (2025), Eq.(17) p.6 e Table 3 p.13: caso publicado.
- API NumPy 2.5: [lstsq](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html),
  [QR](https://numpy.org/doc/stable/reference/generated/numpy.linalg.qr.html) e
  [solve](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html).
  Context7 não estava exposto; estas fontes oficiais sustentam software, não ciência.
