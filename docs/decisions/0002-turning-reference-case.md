# 0002 — Turning reference case

- Tipo: ADR de seleção de evidência para validação futura.
- Status: ACCEPTED.
- Data: 2026-10-23.
- Branch: feature/00-6-turning-reference-dataset.
- Versão: 0.1.0.dev0.
- Commit: rastreado no histórico; incorporação raw registrada em provenance.yaml.
- Validation gate: NOT_APPLICABLE à escolha documental; testes de integridade obrigatórios.

## Identificação
O nome deste arquivo foi solicitado explicitamente na tarefa. Já existe
0002-data-reference-foundation.md; ele não foi removido, renumerado ou substituído.
Para evitar ambiguidade, citar esta decisão pelo caminho completo
docs/decisions/0002-turning-reference-case.md, não apenas pelo ordinal 0002.

## Decisão
Usar o experimento de torneamento e a Table 3 de Pereira et al. (2025),
DOI 10.1016/j.engappai.2025.112510, como caso independente de validação futura.

- experimental data = input: CCD_original.xlsx, preservado byte a byte;
- published coefficients = expected reference output: CSV de Table 3;
- no reverse reconstruction.

A autorização explícita do responsável permite versionar somente este raw no
repositório privado. É uma exceção estreita de armazenamento, sem inferir
PUBLIC_SMALL ou direito de redistribuição pública. O PDF permanece fora do Git.

## Evidência e limites
Zotero SMMX47JT confirmou metadados; não há anexo Zotero. PDF local com hash
verificado, texto completo lido e tabela/equações relevantes conferidas visualmente.
80 valores preservados, sem rescaling, ajuste ou precisão adicional.

Raw contém 152 fórmulas externas para NBI Revisão.xlsm. Caches existem, mas não
estão validados; RAW_NOT_SELF_CONTAINED e SNAPSHOT_PENDING_EXTERNAL_SOURCE.
Níveis físicos divergem entre workbook e Table 1; convenção de Table 3 permanece
CODING_SCHEME_PENDING_VERIFICATION. beta1/beta2/beta3 não são associados
silenciosamente a fatores sem confirmação explícita.

## Consequências
Não há design matrix, OLS, RSM, NBI/CNBI ou Monte Carlo implementado.
Não gerar Y, imputar respostas, corrigir raw ou otimizar dados para reproduzir tabela.
A reprodutibilidade numérica continua PROPOSED/UNVERIFIED até Fase 1 autorizada.
Arredondamento, compatibilidade dos dados, coding e scaling devem ser separados
de erro numérico. Tolerância ainda não definida.
