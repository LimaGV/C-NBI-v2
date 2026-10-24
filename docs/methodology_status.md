# Estado metodológico

## Fase 2 — comparação experimental de anchors nominais

PR #4 integrado por squash após todos os checks verdes; main limpa, branch
feature/02-individual-anchors-response-region. ADR 0005 EXPERIMENTAL.
Implementados anchors clássicos quadráticos sobre bola codificada e payoff,
mais região 8-D de respostas observadas e anchors RC por multistart SLSQP,
com atalho exato quando o anchor clássico global já é admissível.

Codificação original verificada em NBI Revisão.xlsm!Original Data!C4:E22,
axiais +/-1.682. Fonte prioritária por clarificação explícita do responsável.
O gate de equivalência física/codificada FALHOU; o caso codificado é distinto,
sem inventar decodificação contínua nem coordenadas físicas dos novos anchors.
Respostas canônicas e resultados anteriores permanecem intactos.

Na formulação cloud escolhida: phi=mean(Y), S_Y=cov(Y,ddof=1), posto 8.
Cutoff chi-square_8(.95) é legado/EXPERIMENTAL, não confiança exata.
Os oito anchors estão dentro; ambas as payoffs coincidem e não há deslocamento
ou custo de objetivo. Quantil empírico .95 e chi-square .99 também não alteram
os anchors. Recomendação: manter RC como ablação/candidato experimental, sem
torná-lo obrigatório; C-RC-02 continua UNVERIFIED.
O Utopia diagonal permanece fora da região descritiva (D²≈70560.14), embora
os oito anchors estejam dentro. Restringir anchors individualmente não garante
admissibilidade da diagonal; C-RC-04 registra a não implicação e contraexemplo.

Ver [anchors](mathematics/individual_anchors.md),
[região](mathematics/multivariate_response_region.md),
[fontes](../references/notes/phase_02_sources.md) e
[relatório aplicado](mathematics/turning_individual_anchors.md).
Nenhum NBI/C-NBI, CHIM, Monte Carlo, PA, seleção de subconjuntos ou shrinkage.

## Fechamento da Fase 1 — qualidade e capacidade preditiva

Implementados diagnósticos por resposta: SS, R²/R²_adj, MSE/S,
leverages de treino, PRESS analítico/R²_pred, ANOVA global e pure error/LOF.
Oráculos manuais, equivalência PRESS/LOOCV por refits e estados degenerados
estão testados; derivação e fontes verificadas em
[rsm_diagnostics.md](mathematics/rsm_diagnostics.md). ADR 0003 estendida;
claims C-RSM-07 a 11 SUPPORTED nos pressupostos documentados.

Os quatro ajustes anteriores são preservados, com a mesma Y integral e dez
termos. Tabela principal em coordenadas físicas e comparação nominal condicional
estão no [relatório aplicado](mathematics/turning_rsm_diagnostics.md).
Foram detectadas 15 configurações e cinco corridas centrais idênticas (Exp 15-19),
df_PE=4, df_LOF=5. A 5%, testes individuais indicam significância global das oito
respostas e falta de ajuste em sete; WR não rejeita LOF nesse limiar.
Não há declaração de adequação global só por R² elevado.

Table 3 é secundária: método de R²_pred não especificado por PRESS/LOOCV;
Ra/Rt divergem fortemente nesse indicador. WR e notas ROI/OEE continuam
inconsistências de referência/publicação, sem alterações experimentais.
WR arredondado é PUBLICATION_RECONCILIATION_NOTE, fora do pipeline oficial.
Fase 1 concluída no escopo autorizado; nenhuma otimização ou fase seguinte
iniciada. O PR #4 permanece para revisão, sem merge automático.

## Complemento aplicado — CCD literal ajustado
O usuário forneceu revisão atualizada, com 19×11 entradas numéricas reais,
sem fórmulas/dependências externas detectadas. O novo raw foi preservado e os
oito modelos ajustados com a precisão integral das células; rank=10, nu=9.
Relatório: [validação real](mathematics/turning_real_validation.md), ADR 0004 EXPERIMENTAL.
Com desenho nominal rotacional: 50/80 pela nota literal de escala e 70/80 sob
escala diagnóstica 10^-3, em conflito com a nota impressa 10^-2.
WR diverge em 10/10 com precisão integral. Arredondar uma cópia de WR a três
casas explica os coeficientes publicados, mas é diagnóstico a posteriori,
excluído dos ajustes reais. C011 é PARTIALLY_SUPPORTED, sem validação integral.
O raw histórico continua não autocontido; não foi sobrescrito nem ajustado.
Nenhum Monte Carlo, shrinkage ou otimização foi iniciado.

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
Na Fase 0.6, reprodução numérica ficou PROPOSED/UNVERIFIED; o complemento
aplicado acima registra a evidência posterior. Não houve reconstrução de dados.
Ver data/metadata/turning_application/ e
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
