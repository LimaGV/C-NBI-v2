# 0002 — Infraestrutura de dados e referências

- Tipo: ADR
- Status: ACCEPTED (diretriz de infraestrutura explicitamente solicitada)
- Data: 2026-10-23
- Branch: feature/00-5-data-reference-foundation
- Versão: 0.1.0.dev0
- Commit/PR: identificados no histórico e PR desta alteração
- Validation gate: NOT_APPLICABLE à diretriz; implementação verificada por testes
- Substitui: nenhuma decisão científica

## Decisão e limites
Aceitar Excel como registro primário. Separar raw imutável, snapshot autocontido
quando necessário, interim regenerável, processed reproduzível, external e metadata.
Não usar links externos não resolvidos como única fonte computacional.
Resultados ficam em results, não em raw. Importações futuras terão run_id explícito.

Adicionar somente openpyxl como dependência direta nova para ler estrutura/células
de .xlsx em modo read_only, com fórmulas preservadas e sem salvar/recalcular.
et-xmlfile é dependência transitiva da biblioteca. Nenhum engine Excel adicional.
SHA-256 identifica bytes de arquivos; não certifica validade científica.

O inspetor é uma ferramenta de relatório: sinaliza limites, não infere cabeçalhos
sem opção explícita nem certifica independência ou valores em cache.
Não resolve links nem materializa snapshots nesta fase.

## Publicação e bibliografia
Payloads locais ficam fora do Git até classificação PUBLIC_SMALL, PUBLIC_LARGE ou
RESTRICTED e aprovação. READMEs, metadados/schemas e código são revisáveis.
Biblioteca local tem somente formatos textuais seletivos elegíveis por padrão;
documentos protegidos não são publicados. Zotero permanece canônico e somente leitura.
Derivação matemática é classe distinta de literatura/evidência interna/proposta.

## Consequências e evidência
Testes usam apenas arquivos sintéticos temporários, nunca um experimento fabricado.
Nenhum dataset incorporado, nenhuma metodologia científica ou Fase 1 implementada.
Critérios de aceitação: inspeção sem alteração, detecção básica de fórmulas/links,
hashes determinísticos, falhas explícitas, políticas de Git e checks da CI.
Documentação oficial da biblioteca sustenta software, não ciência.
