# Matriz de afirmações metodológicas

Evidence class: LITERATURE, INTERNAL_EVIDENCE, MATHEMATICAL_DERIVATION, PROPOSED.
Status: SUPPORTED, PARTIALLY_SUPPORTED, EXPERIMENTAL, UNVERIFIED, REJECTED,
SUPERSEDED. SUPPORTED exige evidência direta, pressupostos e limites explícitos.
Nunca escrever "a literatura mostra" sem fonte diretamente verificável.
C001–C008 foram preservados da Fase 0 como propostas do responsável,
sem referências científicas adotadas ou preenchidas por inferência.

| Claim ID | Claim | Evidence class | Evidence | Status | Related ADR | Notes |
|---|---|---|---|---|---|---|
| C001 | Incerteza RSM multivariada | PROPOSED | Diretriz do responsável; fonte pendente | UNVERIFIED | MDR pendente | Não implementado |
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

Evidência interna não é literatura; derivação exige passos e revisão reais.
Experimento implementado não aceita hipótese. Vincular fontes, passagens,
decisões, commits e resultados afetados ao atualizar.
