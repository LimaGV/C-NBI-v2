# Pereira et al. (2025) — hybrid VRF-NBI

## Complemento empírico posterior
O CCD literal atualizado foi ajustado com precisão integral. Ver
[validação real](../../docs/mathematics/turning_real_validation.md): 50/80 pela
nota literal e 70/80 sob escala diagnóstica com desenho nominal rotacional.
WR com valores integrais diverge; uma cópia arredondada a três casas reproduz
seus dez coeficientes, sem provar o preprocessing original. Não alterar a
transcrição de Table 3 ou os valores experimentais com base nesse diagnóstico.
Table 2 p.12 foi reconferida visualmente; PDF conserva o hash registrado.
As lacunas descritas abaixo registram a investigação inicial da Fase 0.6.

Title: A hybrid multivariate normal boundary intersection approach with post-optimization assisted by mixture design of experiments
Authors: Matheus Costa Pereira; Caio Tertuliano Ribeiro; Ronã Rinston Amaury Mendes;
Paulo Henrique da Silva Campos; Anderson Paulo de Paiva.
Year: 2025.
Source type: journal article.
Journal: Engineering Applications of Artificial Intelligence.
Volume: 162. Article number: 112510. Issue: UNVERIFIED_METADATA.
DOI: 10.1016/j.engappai.2025.112510.
DOI link: https://doi.org/10.1016/j.engappai.2025.112510
BibTeX key: pereira2025hybrid (local key assigned here, not asserted as Zotero citekey).
Zotero key: SMMX47JT, My Library.
Local file relative to Documents:
Dissertação/02_REFERENCIAS/artigos_pdf/A hybrid multivariate normal boundary intersection .pdf
SHA-256: 5717f7a90195157830e42e038782f43b2976c77813ccc11f2b3c01e3cc2be70a.
Verification date: 2026-10-23.
Verification status: FULLTEXT_VERIFIED.
Metadata status: METADATA_VERIFIED.
Evidence class: LITERATURE.
Priority: CRITICAL_SOURCE.

## Verification evidence
Zotero foi consultado primeiro. Busca por título localizou SMMX47JT; metadados
JSON confirmaram título, DOI, journal, ano/volume e autores. A busca inicial por
DOI não retornou o item, mas isso não foi tratado como prova de ausência.
get_item_children não encontrou anexos: o full text foi lido na cópia local
fornecida, cujo título/DOI/journal/volume também constam no próprio PDF.

Texto completo das 32 páginas foi inspecionado, com verificação visual direta
das páginas relevantes: Eq. (17) e ordem de Eq. (19), página 6; Table 1, página 11;
Table 3, página 13; Table 6, página 18. A renderização é indispensável porque
extração textual confundiu alguns sinais negativos e caracteres.
FULLTEXT_VERIFIED atesta essa leitura da fonte, não certificação de todos os
métodos, resultados ou exatidão interna da publicação.
Os nomes completos são registrados conforme a página 1 do PDF; os campos
firstName/lastName de alguns autores no Zotero estão segmentados diferentemente.
Não foi alterado o registro Zotero.

## Why this source matters
Fornece expected reference output independente para validar uma futura
implementação, sem reconstruir observações. Table 3 é o ponto de comparação
documental; CCD.xlsx é evidência experimental preservada separadamente.

## Claims supported
- C009: oito respostas originais modeladas por quadrático completo: seção 3,
  página 12, Table 3 página 13, Eq. (17) página 6.
- C010: estrutura CCD com 19 corridas, três fatores e cinco centros: seção 3
  e Table 1 página 11; Table 2 página 12. Layout também verificado no workbook.
A matriz de claims identifica a natureza distinta da evidência documental/raw.

## Claims NOT supported na verificação histórica da Fase 0.6
- C011: reprodução numérica dos coeficientes a partir do raw incorporado.
  Continua PROPOSED/UNVERIFIED.
- Caches do Excel serem atuais/corretos ou equivalentes à fonte experimental oficial.
- Convenção exata de codificação/escalas da comparação futura estar resolvida.
- Hipóteses futuras C001–C008 ou metodologia v2 estarem validadas por esta leitura.

## Relevant equations and tables
Eq. (17), seção 2.3, página 6: quadrático completo.
Eq. (19), página 6; discussão página 15; Table 6 página 18: ordem dos termos.
Table 3, página 13: 80 coeficientes originais selecionados e estatísticas secundárias.
Table 3 footnote: WR, ROI, OEE e S apresentados em 10^-2.
Table 2 footnote, página 12: WR em 10^-3; ROI/OEE em 10^-2.
As notas não foram reconciliadas silenciosamente nem usadas para rescaling.
Table 1, página 11, níveis físicos: divergem do workbook em centros e alguns níveis.
Exemplos: Vc central 150.000 versus raw 162.5; f central 0.150 versus raw 0.16;
ap central 0.225 versus raw 0.24. Nenhuma das fontes foi corrigida.

## Methodological use
Somente caso de referência documental; sem RSM, OLS, Monte Carlo ou NBI implementado.
O CSV mantém três casas decimais e os valores impressos, sem VRF1/2/3.
Modelo esperado e dimensões são documentação, não funções executáveis.

## Related ADRs / experiments
docs/decisions/0002-turning-reference-case.md.
Dataset turning_application_ccd_19run; nenhuma execução científica realizada.

## Open questions
Identificar/validar NBI Revisão.xlsm e sua versão experimental antes de snapshot.
Confirmar convenção exata raw→Table 3 e correspondência beta/fator.
Reconciliar discrepâncias físicas da Table 1, notas de escala e precisão publicada.
A seção Data availability, página 30, identifica o repositório
https://github.com/Matheuscp98/Normal-Boundary-Intersection.git e material
suplementar. Foram apenas identificados no texto; não foram baixados ou importados.
Nenhum dado foi preenchido a partir da Table 2 ou da Table 3.

## Atualização — fechamento da Fase 1 (2026-10-23)

A nota acima preserva o estado histórico de incorporação. A revisão literal
posterior e a implementação/validação estão em turning_real_validation.md e
turning_rsm_diagnostics.md. C011 agora é PARTIALLY_SUPPORTED conforme a claims
matrix, sem reprodução integral 80/80. O raw histórico não foi ajustado.

Foi auditado novamente o texto local verificado, com busca por PRESS,
leave-one-out, R² predicted e cross-validation e leitura das passagens de
modelagem/validação nas pp.6,9-10,12-13,22-24. Table 3 p.13 apresenta R² pred.,
mas não foi encontrada definição explícita por PRESS/LOOCV para esse resumo.
Cross-validation em cinco folds e treino/teste 80/20 nas pp.22-23 refere-se
ao estudo de machine learning/dados simulados, não define o R² pred. da Table 3.
Status da comparabilidade: PUBLISHED_R2_PRED_METHOD_UNSPECIFIED; comparação
numérica é secundária, inclusive quando há coincidência de arredondamento.
S tem nota própria 10^-2, aplicada separadamente das escalas dos coeficientes.

WR com precisão integral é canônico. O diagnóstico histórico de arredondamento
tem classificação PUBLICATION_RECONCILIATION_NOTE e fica fora do pipeline
oficial. Divergências WR e escala de ROI/OEE são inconsistências da publicação/
reference case; não são classificadas como defeito da implementação.
