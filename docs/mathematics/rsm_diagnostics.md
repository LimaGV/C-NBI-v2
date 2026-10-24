# Qualidade e predição dos RSMs completos

## Escopo, API e hipóteses

`diagnose_rsm(fit, factors, response_names=None)` retorna `RSMDiagnostics`, com
uma tupla de `ResponseDiagnostics`, diagonal de H, resíduos PRESS e grupos de
fatores. Todas as estruturas/arrays são imutáveis. Nomes omitidos tornam-se
`response_0`, `response_1`, ...; índices de observações são zero-based.
As métricas são por resposta, em unidades canônicas, e R² é uma fração.

O ajuste é OLS de posto completo, com intercepto e nu=n-rank(X)>0, como na API
RSM atual. Fatores fornecidos devem coincidir exatamente com os usados no ajuste,
na mesma ordem. `RSMFit` passa a preservar duas propriedades fundamentais:
`experimental_factors` e `observed_responses`, cópias float64 imutáveis. Isso evita
reconstruir Y por fitted+residual e impede associar réplicas/leverages às linhas
erradas. Não contém uma coleção de métricas diagnósticas nem altera o OLS.

Os testes F pressupõem erros independentes, normais e de variância constante
por resposta; correlação entre respostas não impede o cálculo marginal, mas não
se cria teste conjunto ou ajuste de multiplicidade. Os pressupostos não são
certificados por calcular p-values. Replicação de fatores deve representar
experimentos independentes, não apenas leituras repetidas da mesma amostra.

## Somas de quadrados, erro e R²

Para cada coluna j, e=y-y_hat, SSE=e^T e, SST=sum((y-y_bar)^2), SSR=SST-SSE.
Logo SST=SSR+SSE. Calcula-se SST centrando primeiro y-y[0], para reduzir perda
por cancelamento e preservar SST=0 para observações exatamente constantes.

MSE=SSE/nu=diag(Sigma_hat_e); S=sqrt(MSE). A API reutiliza MSE do ajuste.
R²=1-SSE/SST e R²_adj=1-(SSE/nu)/(SST/(n-1)), equivalente a
1-(1-R²)*(n-1)/nu. Com intercepto, R²_adj<=R², salvo precisão numérica.

SST=0 torna R², R²_adj e R²_pred indefinidos (`None`, CONSTANT_RESPONSE).
Não se substituem por 0 ou 1. SSE residual de arredondamento permanece visível.

## Leverage, PRESS e equivalência LOOCV

De X=QR reduzida, H=QQ^T e h_ii=sum_k Q_ik². Calculam-se apenas n diagonais,
sem construir H. Verificam-se 0<=h<=1 e sum(h)=rank(X), com tolerância
eps_float64*max(n,p) nos limites e rank(X) vezes essa margem no traço.
É verificação numérica, sem clipping de h ou alteração do desenho.

Para excluir a linha z_i^T, a identidade de atualização de posto um dá
beta_(-i)=beta-(X^T X)^(-1) z_i e_i/(1-h_ii), desde que 1-h_ii não seja zero.
Portanto y_i-z_i^T beta_(-i)=e_i/(1-h_ii). A identidade é usada no cálculo;
não se usa a inversa explícita na implementação. Testes refazem, independentemente,
n ajustes e comparam cada predição omitida e sua soma de quadrados.

PRESS_residual_i=e_i/(1-h_ii), PRESS=sum(PRESS_residual_i²) e
R²_pred=1-PRESS/SST. Um R²_pred negativo é preservado. Esses resíduos não são
standardized ou studentized residuals. Se qualquer 1-h<=tolerância acima,
PRESS, toda a matriz de resíduos PRESS e R²_pred são `None` com
PRESS_LEVERAGE_NEAR_ONE e índices das linhas afetadas: remover tal linha pode
destruir a identificabilidade. Não se fabrica uma predição leave-one-out.

## ANOVA global com intercepto

| Fonte | SS | df | MS |
|---|---|---|---|
| Modelo | SSR | rank(X)-1 | SSR/(rank(X)-1) |
| Erro | SSE | nu=n-rank(X) | SSE/nu |
| Total corrigido | SST | n-1 | — |

F_model=MS_model/MSE; p=scipy.stats.f.sf(F_model,df_model,nu).
É o teste global de todos os termos não constantes iguais a zero.
Sem p-values de betas, seleção, redução ou mudança de hierarquia.
MSE=0 produz F/p `None`, ZERO_ERROR_MEAN_SQUARE; SSR negativo produz
NEGATIVE_MODEL_SS, sem truncar a soma reportada. SST=0 tem precedência.
Resultados não finitos falham explicitamente, sem nan/inf silencioso.

## Replicação, pure error e lack of fit

`factor_configuration_groups` agrupa linhas float64 por igualdade numérica exata,
em ordem da primeira ocorrência. Não aplica tolerância nem recodificação. +0 e
-0 são iguais; vizinhos `nextafter` continuam diferentes. Não agrupa por Y.
Se existirem u configurações, grupos g de tamanho n_g:

- SS_PE=sum_g sum_i_in_g (y_i-y_bar_g)²; df_PE=sum_g(n_g-1)=n-u.
- SS_LOF=SSE-SS_PE=sum_g n_g*(y_bar_g-y_hat_g)²; df_LOF=nu-df_PE=u-rank(X).
- MS_PE=SS_PE/df_PE; MS_LOF=SS_LOF/df_LOF.
- F_LOF=MS_LOF/MS_PE; p=scipy.stats.f.sf(F_LOF,df_LOF,df_PE).

Implementa-se a soma ponderada não negativa de SS_LOF, equivalente à subtração,
para evitar cancelamento quando SSE≈SS_PE. As médias dentro dos grupos usam
offsets a partir do primeiro valor. A identidade decorre de
y_i-y_hat_g=(y_i-y_bar_g)+(y_bar_g-y_hat_g); o termo cruzado soma zero em cada
grupo. Testa-se SSE=SS_PE+SS_LOF com precisão numérica, sem clipping.

| Condição | F_LOF/p | Status |
|---|---|---|
| Sem réplicas, df_PE=0 | None | NO_REPLICATES |
| df_LOF=0 | None | NO_LACK_OF_FIT_DF |
| SS_PE=0, df positivos | None | ZERO_PURE_ERROR |
| df_PE>0, df_LOF>0, SS_PE>0 | Calculados | OK |

SS/df são reportados mesmo quando o teste não é estimável; MS com df zero é
`None`. Sem réplicas, a soma formal LOF=SSE não fornece teste de adequação.
LOF não significativo não comprova adequação, normalidade ou predição externa.

## Escalas e limites

Multiplicar Y por c!=0 mantém R²/R²_adj/R²_pred/F e seus p-values;
S multiplica por abs(c), SS/MSE/PRESS por c². Nada é reescalado no diagnóstico.
Operações são float64; overflow/invalid/divisão por zero falham, e estatísticas
não finitas são rejeitadas. Valores subnormais estão sujeitos ao underflow da
representação. Não há tolerância científica oculta para aceitar a publicação.

## Evidência e verificação

[R004](../../references/notes/rsm_foundation_sources.md): Myers, Montgomery e
Anderson-Cook (2016), pp.24-26 Eqs.(2.20)-(2.26); pp.38-42 Eqs.(2.44)-(2.54)
e traço de H; pp.44-46 Eqs.(2.60)-(2.65). Passagens lidas diretamente,
PRESS e LOF conferidos em páginas renderizadas. O livro permanece PARTIAL.
O [NIST, seção 4.4.4.6](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd446.htm)
também explicita a exigência de réplicas, graus de liberdade e teste LOF.
A [documentação oficial do SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f.html)
define `sf(x,dfn,dfd)` como probabilidade de cauda superior; nenhuma CDF foi
reimplementada. Context7 estava indisponível na implementação; na finalização
de 2026-10-24, a consulta /scipy/scipy reconfirmou sf como survival function
(1-CDF), sem alterar a API ou os resultados.

Oráculos manuais, polinômio exato, R²_pred negativo, LOOCV explícito,
invariância de escala, permutações, limites de leverage, estados degenerados,
PE/LOF conhecidos e equivalências de Sigma_e estão nos testes. A Table 3 é
referência secundária do caso aplicado; não é oráculo que produz observações.
