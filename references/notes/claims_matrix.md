# Matriz de afirmações metodológicas

Evidence class: LITERATURE, INTERNAL_EVIDENCE, MATHEMATICAL_DERIVATION,
METHODOLOGICAL_DECISION, METHOD_DEFINITION, PROPOSED.
Status: SUPPORTED, PARTIALLY_SUPPORTED, EXPERIMENTAL, UNVERIFIED, REJECTED,
SUPERSEDED. SUPPORTED exige evidência direta, pressupostos e limites explícitos.
Nunca escrever "a literatura mostra" sem fonte diretamente verificável.
C001–C008 nasceram como propostas do responsável na Fase 0. C001 recebe
suporte analítico delimitado na Fase 1. C002 é especificada pela ADR 0006;
C006 é delimitada pela decisão C-MC-03. C003 é especificada na Fase 4;
as propostas restantes continuam pendentes.

| Claim ID | Claim | Evidence class | Evidence | Status | Related ADR | Notes |
|---|---|---|---|---|---|---|
| C001 | Incerteza analítica RSM multivariada sob projeto fixo e erros de covariância comum | LITERATURE + MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | C-RSM-01 a 06; R003/R004; tests/model | SUPPORTED | ADR 0003 | Escopo analítico; não valida sampling, ótimos ou dataset real |
| C002 | Perturbação conjunta dos coeficientes | MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | C-MC-01/02 | SUPPORTED | ADR 0006 | Matrix-normal plug-in implementada; não valida ótimos por réplica ou PA |
| C003 | Reotimizar âncoras por réplica | METHODOLOGICAL_DECISION | C-MC-04, solicitação explícita da Fase 4 | SUPPORTED | ADR 0007 | Implementação/certificados na esfera principal; sem PA ou RC |
| C004 | PA local em estudo | PROPOSED | Contexto do responsável; evidência pendente | UNVERIFIED | MDR pendente | Não implementado |
| C005 | q_C sem hard cutoff automático | PROPOSED | Salvaguarda do responsável; validade pendente | UNVERIFIED | MDR pendente | Sem cutoff definido |
| C006 | B=2000 não é teorema ou valor universal ótimo | METHODOLOGICAL_DECISION | C-MC-03, diretriz explícita da Fase 3 | SUPPORTED | ADR 0006 | Máximo 2000 adotado para sensibilidade, não escolhido por menor erro observado |
| C007 | Simplex-Lattice, H inteiro, Delta=1/H | PROPOSED | Diretriz do responsável; derivação pendente | UNVERIFIED | MDR pendente | Não implementado |
| C008 | H adaptativo indefinido | PROPOSED | Questão em aberto do responsável | UNVERIFIED | MDR pendente | Nenhuma regra escolhida |
| C009 | The turning application uses full quadratic response surface models for eight original responses. | LITERATURE | R001, Eq. (17) p.6, seção 3 p.12 e Table 3 p.13 | SUPPORTED | docs/decisions/0002-turning-reference-case.md | Descrição publicada; não implementação v2 |
| C010 | The experimental application contains 19 CCD runs, three factors, eight responses and five center points. | LITERATURE + INTERNAL_EVIDENCE | R001 seção 3 p.11/Table 2 p.12; DATASET_METADATA e Plan1!A1:L20 | SUPPORTED | docs/decisions/0002-turning-reference-case.md | Estrutura/layout verificados; respostas vinculadas externamente |
| C011 | The published coefficients can be reproduced numerically from the incorporated experimental dataset. | INTERNAL_EVIDENCE | Validação literal em docs/mathematics/turning_real_validation.md; 50/80 nota literal, 70/80 escala diagnóstica sob CCD nominal | PARTIALLY_SUPPORTED | ADR 0004 | Não reproduz 80/80 preservando precisão; WR diverge; coding físico e nota de escala pendentes |
| C012 | The incorporated raw workbook has unresolved external response dependencies. | INTERNAL_EVIDENCE | workbook_inspection.json, 152 fórmulas E2:L20 e relação OOXML | SUPPORTED | docs/decisions/0002-turning-reference-case.md | RAW_NOT_SELF_CONTAINED; caches não certificados |
| C-DATA-01 | A revisão CCD_values_20261023 possui 19×11 entradas numéricas literais, além de 19 IDs | INTERNAL_EVIDENCE | Inspeção e extração OOXML da nova revisão, SHA 7f905b7a... | SUPPORTED | ADR 0004 | Nova revisão não sobrescreve o raw histórico C012 |
| C-PUB-WR-01 | Uma cópia de WR arredondada a três casas antes do OLS reproduz os dez coeficientes sob desenho nominal e escala diagnóstica | INTERNAL_EVIDENCE | wr_rounding_hypothesis.json e teste reprodutível | SUPPORTED | ADR 0004 | Diagnóstico altera 19 valores da cópia, não entra nos modelos reais; não prova preprocessing dos autores |
| C-RSM-01 | Y=XB+E com projeto comum e base quadrática completa | LITERATURE | R003 seção 2 pp.2-3 Eq.(3); R004 pp.16-17 Eqs.(2.12)-(2.15) | SUPPORTED | ADR 0003 | X fixo, posto completo; respostas compartilham o projeto |
| C-RSM-02 | Sigma_hat_e=E_hat^T E_hat/nu, nu=n-rank(X), é estimador não viesado de Sigma | LITERATURE + MATHEMATICAL_DERIVATION | R003 p.3; R004 pp.22-23 Eqs.(2.17)-(2.18); derivação por projetor em docs/mathematics/multivariate_rsm.md | SUPPORTED | ADR 0003 | Média zero, observações não correlacionadas e covariância comum; nu>0 |
| C-RSM-03 | diag(Sigma_hat_e)_j=MSE_j | MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | Produto de cada coluna residual; tests/model/test_multivariate_rsm.py | SUPPORTED | ADR 0003 | Caso manual e equivalência univariada, sem validação experimental |
| C-RSM-04 | Cov(vec(B_hat))=Sigma⊗V_X; estimativa plug-in Sigma_hat_e⊗V_X | LITERATURE + MATHEMATICAL_DERIVATION | R003 p.3 escreve vec(B_hat^T); conversão explícita em docs/mathematics/rsm_uncertainty.md | SUPPORTED | ADR 0003 | vec por colunas de B_hat; normalidade adicional para matrix-normal |
| C-RSM-05 | Cov(mu_hat(x))=h(x)Sigma; estimativa h(x)Sigma_hat_e | LITERATURE + MATHEMATICAL_DERIVATION | R003 p.3 Eqs.(5)-(6); R004 p.33 Eq.(2.40); propagação linear em rsm_uncertainty.md | SUPPORTED | ADR 0003 | Média estimada sem 1+h; não é erro de nova observação |
| C-RSM-06 | Cov(mu_hat(x_a)-mu_hat(x_b))=[(z_a-z_b)^T V_X(z_a-z_b)]Sigma | MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | Derivação em rsm_uncertainty.md; tests/model/test_uncertainty.py | SUPPORTED | ADR 0003 | Inclui ambos os termos cruzados; zero se a=b; simetria a/b |
| C-RSM-07 | R²=1-SSE/SST | LITERATURE + INTERNAL_EVIDENCE | R004 p.26 Eq.(2.25), PDF 44 lido; tests/model/test_diagnostics.py, oráculo manual | SUPPORTED | ADR 0003, fechamento | SST>0; resposta constante explicitamente indefinida |
| C-RSM-08 | PRESS=sum_i(e_i/(1-h_ii))² | LITERATURE + INTERNAL_EVIDENCE | R004 p.40 Eqs.(2.51)-(2.52), PDF 58 lido/renderizado; oráculo manual | SUPPORTED | ADR 0003, fechamento | OLS identificável após excluir cada ponto; h próximo de um diagnosticado |
| C-RSM-09 | PRESS analítico equivale ao squared LOOCV prediction error | LITERATURE + MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | R004 pp.39-40 Eqs.(2.50)-(2.52); derivação em rsm_diagnostics.md; refits explícitos em testes | SUPPORTED | ADR 0003, fechamento | Mesma base/OLS, exclusões de posto completo; não atribui esse método à Table 3 |
| C-RSM-10 | SSE=SS_LOF+SS_PE | LITERATURE + MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | R004 p.45 Eqs.(2.60)-(2.64), PDF 63 lido/renderizado; oráculos com replicação | SUPPORTED | ADR 0003, fechamento | Fitted constante em cada configuração; soma ponderada evita cancelamento |
| C-RSM-11 | Réplicas nas mesmas condições permitem separar pure error e lack of fit | LITERATURE + INTERNAL_EVIDENCE | R004 pp.44-46; NIST seção 4.4.4.6; 15 configurações e grupo Exp 15-19 detectados | SUPPORTED | ADR 0003, fechamento | F_LOF requer df_PE>0, df_LOF>0 e SS_PE>0; independência das réplicas é pressuposto experimental |

O diagnóstico histórico C-PUB-WR-01 tem classe de uso
`PUBLICATION_RECONCILIATION_NOTE`, fora do pipeline oficial de diagnósticos.
Não autoriza arredondamento dos dados ou atribuição de preprocessing aos autores.

Evidência interna não é literatura; derivação exige passos e revisão reais.

## Fase 2 — anchors e região de respostas (ADR 0005 EXPERIMENTAL)

| Claim ID | Claim | Evidence class | Evidence | Status | Limits |
|---|---|---|---|---|---|
| C-ANCHOR-01 | Anchors individuais são obtidos otimizando cada objetivo separadamente na região admissível | LITERATURE + INTERNAL_EVIDENCE | R001 seção 4.1/Table 4 pp.13-14; tests/optimization | SUPPORTED | Suporte à definição; nenhum NBI implementado |
| C-ANCHOR-02 | Quadrática completa sobre bola Euclidiana é um quadratic trust-region problem com caracterização global KKT/PSD | MATHEMATICAL_DERIVATION + LITERATURE + INTERNAL_EVIDENCE | individual_anchors.md; Moré 1993 PDF p.3 diretamente lido; oráculos interiores/fronteira/hard case | SUPPORTED | Precisão numérica/certificado explicitados; não se transfere globalidade ao problema RC geral |
| C-RC-01 | Uma restrição de distância quadrática pode limitar os vetores previstos a uma região multivariada especificada durante a definição dos anchors | LITERATURE + MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | Maia 2020 pp.21/84 lidas/renderizadas; formulação e geometria em multivariate_response_region.md | SUPPORTED | Antecedente do estágio, não identidade entre a fórmula Khuri e a nuvem centrada na média escolhida aqui |
| C-RC-02 | O cutoff finite-sample apropriado ao caso n=19,m=8 está estabelecido | PROPOSED | Revisão focada distingue conteúdo populacional, média, predição, tolerância e quantil empírico | UNVERIFIED | Chi-square .95 é EXPERIMENTAL; nenhuma adoção automática |
| C-CODING-01 | Códigos e fatores físicos originais foram verificados por IDs, mas seus ajustes quadráticos não são equivalentes | INTERNAL_EVIDENCE | Original Data!B4:H22, hash fonte e phase_02_coding.json; teste de fitted discrepancy | SUPPORTED | Clarificação do responsável prioriza planilha; sem transformação contínua/inversa certificada |
| C-RC-03 | Nesta formulação 8-D, os oito anchors clássicos estão dentro dos três cutoffs avaliados | INTERNAL_EVIDENCE | Run turning_original_codes_20261024, comparação e sensibilidade | EXPERIMENTAL | Resultado do modelo codificado distinto; não prova adequação estatística ou inutilidade universal de RC |
| C-RC-04 | Admissibilidade dos vetores completos nos anchors não implica admissibilidade do Utopia montado pela diagonal da payoff | MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | Contraexemplo 2-D em individual_anchors.md/testes; utopia_diagnostic.json no caso real | SUPPORTED | Não é nova formulação; nenhuma garantia de atingibilidade conjunta da diagonal |
Experimento implementado não aceita hipótese. Vincular fontes, passagens,
decisões, commits e resultados afetados ao atualizar.

## Fase 3 — joint coefficient Monte Carlo (ADR 0006 ACCEPTED)

| Claim ID | Claim | Evidence class | Evidence | Status | Limits |
|---|---|---|---|---|---|
| C-MC-01 | For DeltaB=C_X G L_Sigma^T with iid standard-normal G, Cov(vec(DeltaB))=Sigma tensor V_X | MATHEMATICAL_DERIVATION | docs/mathematics/coefficient_monte_carlo.md; root identities and column-vec tests | SUPPORTED | Conditional plug-in law, C_X C_X^T=V_X and L_Sigma L_Sigma^T=Sigma; not a posterior |
| C-MC-02 | Empirical Monte Carlo moments approach the plug-in theoretical moments as B increases | INTERNAL_EVIDENCE | Synthetic six-SE tests; run turning_original_codes_mc_777_20261024: E_mu .00948444 to .00216433, E_K .285882 to .0615535, all 20 prefixes archived | SUPPORTED | Finite-seed evidence consistent with convergence, not a monotonic theorem or universal B; covariance blocks tested separately |
| C-MC-03 | B=100:100:2000 is a sensitivity schedule, not a universal optimum | METHODOLOGICAL_DECISION | Explicit Phase 3 instruction, ADR 0006, coefficient_checkpoints() | SUPPORTED | Final B not selected by minimum observed error; future PA early stop PROPOSED and not applied |

## Fase 4 — anchor reoptimization (ADR 0007 ACCEPTED)

| Claim ID | Claim | Evidence class | Evidence | Status | Limits |
|---|---|---|---|---|---|
| C-MC-04 | For each sampled coefficient matrix, individual anchors are recomputed before constructing its payoff | METHODOLOGICAL_DECISION | Explicit Phase 4 instruction; anchor_reoptimization.py; nominal repeated-2000 control counts 16000 calls | SUPPORTED | Main sphere only, unchanged solver; nominal anchors are diagnostic references |
| C-MC-05 | Fixed nominal anchors do not propagate coefficient uncertainty into optimizer location | MATHEMATICAL_DERIVATION | anchor_monte_carlo.md: f_theta=-(x-theta)^2, x_star=theta versus fixed zero; direct oracle test | SUPPORTED | Response uncertainty at a fixed point is a different object; no unverified attribution to prior work |
| C-MC-06 | Phase 4 payoffs are A[b,i,j]=f_i[b](x_j_star[b]) | METHOD_DEFINITION | Explicit definition, ADR 0007, payoff orientation/permutation/diagonal tests | SUPPORTED | Native units, same replica on both axes; does not define normalization, CHIM, PA or Nadir |
