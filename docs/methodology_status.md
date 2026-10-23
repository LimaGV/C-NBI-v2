# Estado metodológico inicial

## Fase 0.6 — incorporação documental concluída nesta branch
PR #2 da Fase 0.5 integrado por squash após CI verde.
Dataset turning_application_ccd_19run incorporado como RAW_NOT_SELF_CONTAINED:
19 corridas, três fatores, oito respostas e 152 fórmulas externas.
SNAPSHOT_PENDING_EXTERNAL_SOURCE: caches existem, mas não foram certificados.
Golden reference da Table 3 criada com 80 valores, fonte FULLTEXT_VERIFIED.
CODING_SCHEME_PENDING_VERIFICATION; interpretação de escalas permanece pendente.
Reprodução numérica dos coeficientes continua PROPOSED/UNVERIFIED.
RSM, OLS, design matrix, Monte Carlo e NBI/CNBI continuam não implementados.
Fase 1 não iniciada. Ver data/metadata/turning_application/ e
tests/reference_cases/turning_8responses/; nenhuma resposta foi reconstruída.

Nenhuma metodologia científica está implementada ou validada.
Os itens abaixo são contexto fornecido pelo responsável e propostas de trabalho,
não conclusões da literatura. Não há resultados científicos nesta fundação.

| ID | Contexto/proposta | Categoria | Status |
| --- | --- | --- | --- |
| C001 | Incerteza RSM será multivariada | PROPOSED | UNVERIFIED |
| C002 | Coeficientes serão perturbados conjuntamente | PROPOSED | UNVERIFIED |
| C003 | Âncoras deverão ser reotimizadas a cada réplica | PROPOSED | UNVERIFIED |
| C004 | PA local está em estudo | PROPOSED | UNVERIFIED |
| C005 | q_C não deve virar automaticamente hard cutoff | PROPOSED | UNVERIFIED |
| C006 | B=2000 não é constante normativa | PROPOSED | UNVERIFIED |
| C007 | Simplex-Lattice com H inteiro e Delta=1/H | PROPOSED | UNVERIFIED |
| C008 | Regra adaptativa para H ainda não definida | PROPOSED | UNVERIFIED |

A proteção contra decisões implícitas já é regra de governança. As hipóteses
acima continuam sem validação científica; ver references/notes/claims_matrix.md.
