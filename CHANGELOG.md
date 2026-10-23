# Changelog

## Unreleased — Fase 0.5 (infraestrutura)
- Camadas de dados, templates de metadados e dicionário de variáveis.
- SHA-256 e inspeção somente leitura de .xlsx, sem recálculo ou transformação.
- openpyxl: única dependência direta nova, necessária para ler células, fórmulas
  e estrutura de workbooks; não é motor de cálculo ou método científico.
- Políticas de raw imutável, snapshots, publicação seletiva e documentos locais.
- Templates bibliográficos completos e distinção de derivação matemática.
- Nenhuma alteração metodológica ou incorporação de dataset real.

## 0.1.0.dev0 — não lançado
- Base independente com Python 3.12, uv e pacote cnbi_v2.
- Governança, ADR/MDR, rastreabilidade, referências e políticas de dados.
- Testes de infraestrutura, Ruff, mypy e CI Windows/Ubuntu.
- Inventário distingue estado informado, exposição e teste real de MCPs.
- Nenhum algoritmo científico; Fase 1 permanece pendente.
