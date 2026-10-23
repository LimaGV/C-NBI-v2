## Problema e comportamento resultante
Descrever o que muda e por quê.

## Rastreabilidade
- Branch e commit:
- Versão:
- ADR/MDR e claims (ou justificar infraestrutura):
- Dados, configurações e resultados afetados:
- Evidências e limitações:

## Validação
- [ ] uv sync --locked
- [ ] uv run pytest
- [ ] uv run ruff check .
- [ ] uv run mypy src
- [ ] CI Windows/Ubuntu aprovada
- [ ] Sem secrets e sem alterações não autorizadas na v1
- [ ] Mudanças científicas têm matemática, evidência, decisão, testes e validação

Não promover experimento a metodologia automaticamente nem mergear com CI falhando.
