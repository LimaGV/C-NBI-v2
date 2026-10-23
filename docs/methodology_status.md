# Estado metodológico

## Fase 1 — fundação RSM e incerteza analítica

Primeira implementação científica: base quadrática completa, OLS multivariado,
equivalência com OLS univariado, resíduos/MSE, Sigma_hat_e, V_X por QR/solve,
covariâncias dos coeficientes e das médias preditas, cruzadas e de diferenças.
Aceitação do escopo por solicitação explícita na ADR 0003. Validação algébrica
e sintética, sem comprovação de adequação ao dataset real ou validação empírica
do restante do C-NBI. Ver [matemática](mathematics/multivariate_rsm.md),
[incerteza](mathematics/rsm_uncertainty.md) e [claims](../references/notes/claims_matrix.md).

Covariância dos coeficientes usa vec de B_hat por colunas: Sigma_hat_e⊗V_X.
Incerteza da média é h Sigma_hat_e, sem adicionar erro de observação.
Diferenças usam o contraste z_a-z_b e preservam covariâncias cruzadas.
Não há sampling, Monte Carlo, shrinkage ou otimização; NBI/CNBI não implementados.
A próxima fase exige nova solicitação.

## Fase 0.6 — evidência experimental e golden reference preservadas
PR #3 integrado por squash na preparação da Fase 1, com CI verde e sem conflito.
Dataset turning_application_ccd_19run incorporado como RAW_NOT_SELF_CONTAINED:
19 corridas, três fatores, oito respostas e 152 fórmulas externas.
SNAPSHOT_PENDING_EXTERNAL_SOURCE: caches existem, mas não foram certificados.
Golden reference da Table 3 criada com 80 valores, fonte FULLTEXT_VERIFIED.
CODING_SCHEME_PENDING_VERIFICATION; interpretação de escalas permanece pendente.
Reprodução numérica dos coeficientes continua PROPOSED/UNVERIFIED.
Nenhum dado experimental foi ajustado ou reconstruído. Ver data/metadata/turning_application/ e
tests/reference_cases/turning_8responses/; nenhuma resposta foi reconstruída.

Dimensões estruturais: n=19,n_x=3,m=8,p=10; nu=9 se rank(X)=10.
B:10×8; Sigma_hat_e:8×8. Isso não decide adoção futura de shrinkage.

## Propostas posteriores
C001 agora tem suporte analítico delimitado por C-RSM-01 a 06.
Isso não aceita automaticamente propostas de sampling/otimização.

| ID | Contexto/proposta | Categoria | Status |
| --- | --- | --- | --- |
| C002 | Coeficientes serão perturbados conjuntamente | PROPOSED | UNVERIFIED |
| C003 | Âncoras deverão ser reotimizadas a cada réplica | PROPOSED | UNVERIFIED |
| C004 | PA local está em estudo | PROPOSED | UNVERIFIED |
| C005 | q_C não deve virar automaticamente hard cutoff | PROPOSED | UNVERIFIED |
| C006 | B=2000 não é constante normativa | PROPOSED | UNVERIFIED |
| C007 | Simplex-Lattice com H inteiro e Delta=1/H | PROPOSED | UNVERIFIED |
| C008 | Regra adaptativa para H ainda não definida | PROPOSED | UNVERIFIED |

A proteção contra decisões implícitas já é regra de governança. As hipóteses
acima continuam sem validação científica; ver references/notes/claims_matrix.md.
