# Matriz de afirmações metodológicas

Evidence class: LITERATURE, INTERNAL_EVIDENCE, MATHEMATICAL_DERIVATION, PROPOSED.
Status: SUPPORTED, PARTIALLY_SUPPORTED, EXPERIMENTAL, UNVERIFIED, REJECTED,
SUPERSEDED. SUPPORTED exige evidência direta, pressupostos e limites explícitos.
Nunca escrever "a literatura mostra" sem fonte diretamente verificável.
C001–C008 nasceram como propostas do responsável na Fase 0. C001 recebe
suporte analítico delimitado na Fase 1; C002–C008 continuam sem aceitação.

| Claim ID | Claim | Evidence class | Evidence | Status | Related ADR | Notes |
|---|---|---|---|---|---|---|
| C001 | Incerteza analítica RSM multivariada sob projeto fixo e erros de covariância comum | LITERATURE + MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | C-RSM-01 a 06; R003/R004; tests/model | SUPPORTED | ADR 0003 | Escopo analítico; não valida sampling, ótimos ou dataset real |
| C002 | Perturbação conjunta dos coeficientes | PROPOSED | Diretriz do responsável; fonte pendente | UNVERIFIED | MDR pendente | Não implementado |
| C003 | Reotimizar âncoras por réplica | PROPOSED | Diretriz do responsável; fonte pendente | UNVERIFIED | MDR pendente | Não implementado |
| C004 | PA local em estudo | PROPOSED | Contexto do responsável; evidência pendente | UNVERIFIED | MDR pendente | Não implementado |
| C005 | q_C sem hard cutoff automático | PROPOSED | Salvaguarda do responsável; validade pendente | UNVERIFIED | MDR pendente | Sem cutoff definido |
| C006 | B=2000 não normativo | PROPOSED | Salvaguarda do responsável; validade pendente | UNVERIFIED | MDR pendente | Sem B adotado |
| C007 | Simplex-Lattice, H inteiro, Delta=1/H | PROPOSED | Diretriz do responsável; derivação pendente | UNVERIFIED | MDR pendente | Não implementado |
| C008 | H adaptativo indefinido | PROPOSED | Questão em aberto do responsável | UNVERIFIED | MDR pendente | Nenhuma regra escolhida |
| C009 | The turning application uses full quadratic response surface models for eight original responses. | LITERATURE | R001, Eq. (17) p.6, seção 3 p.12 e Table 3 p.13 | SUPPORTED | docs/decisions/0002-turning-reference-case.md | Descrição publicada; não implementação v2 |
| C010 | The experimental application contains 19 CCD runs, three factors, eight responses and five center points. | LITERATURE + INTERNAL_EVIDENCE | R001 seção 3 p.11/Table 2 p.12; DATASET_METADATA e Plan1!A1:L20 | SUPPORTED | docs/decisions/0002-turning-reference-case.md | Estrutura/layout verificados; respostas vinculadas externamente |
| C011 | The published coefficients can be reproduced numerically from the incorporated experimental dataset. | PROPOSED | Golden reference registrada; experimento computacional ainda não realizado | UNVERIFIED | docs/decisions/0002-turning-reference-case.md | Depende de fonte experimental validada, coding/scaling e arredondamento |
| C012 | The incorporated raw workbook has unresolved external response dependencies. | INTERNAL_EVIDENCE | workbook_inspection.json, 152 fórmulas E2:L20 e relação OOXML | SUPPORTED | docs/decisions/0002-turning-reference-case.md | RAW_NOT_SELF_CONTAINED; caches não certificados |
| C-RSM-01 | Y=XB+E com projeto comum e base quadrática completa | LITERATURE | R003 seção 2 pp.2-3 Eq.(3); R004 pp.16-17 Eqs.(2.12)-(2.15) | SUPPORTED | ADR 0003 | X fixo, posto completo; respostas compartilham o projeto |
| C-RSM-02 | Sigma_hat_e=E_hat^T E_hat/nu, nu=n-rank(X), é estimador não viesado de Sigma | LITERATURE + MATHEMATICAL_DERIVATION | R003 p.3; R004 pp.22-23 Eqs.(2.17)-(2.18); derivação por projetor em docs/mathematics/multivariate_rsm.md | SUPPORTED | ADR 0003 | Média zero, observações não correlacionadas e covariância comum; nu>0 |
| C-RSM-03 | diag(Sigma_hat_e)_j=MSE_j | MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | Produto de cada coluna residual; tests/model/test_multivariate_rsm.py | SUPPORTED | ADR 0003 | Caso manual e equivalência univariada, sem validação experimental |
| C-RSM-04 | Cov(vec(B_hat))=Sigma⊗V_X; estimativa plug-in Sigma_hat_e⊗V_X | LITERATURE + MATHEMATICAL_DERIVATION | R003 p.3 escreve vec(B_hat^T); conversão explícita em docs/mathematics/rsm_uncertainty.md | SUPPORTED | ADR 0003 | vec por colunas de B_hat; normalidade adicional para matrix-normal |
| C-RSM-05 | Cov(mu_hat(x))=h(x)Sigma; estimativa h(x)Sigma_hat_e | LITERATURE + MATHEMATICAL_DERIVATION | R003 p.3 Eqs.(5)-(6); R004 p.33 Eq.(2.40); propagação linear em rsm_uncertainty.md | SUPPORTED | ADR 0003 | Média estimada sem 1+h; não é erro de nova observação |
| C-RSM-06 | Cov(mu_hat(x_a)-mu_hat(x_b))=[(z_a-z_b)^T V_X(z_a-z_b)]Sigma | MATHEMATICAL_DERIVATION + INTERNAL_EVIDENCE | Derivação em rsm_uncertainty.md; tests/model/test_uncertainty.py | SUPPORTED | ADR 0003 | Inclui ambos os termos cruzados; zero se a=b; simetria a/b |

Evidência interna não é literatura; derivação exige passos e revisão reais.
Experimento implementado não aceita hipótese. Vincular fontes, passagens,
decisões, commits e resultados afetados ao atualizar.
