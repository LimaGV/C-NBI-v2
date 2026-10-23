# C-NBI v2

Reimplementação limpa e independente do Combinatorial Normal Boundary
Intersection. Versão **0.1.0.dev0**. Estado: fundação de infraestrutura.
Fase 0 integrada em main; Fase 0.5 adiciona infraestrutura de dados/referências.
Nenhum algoritmo científico implementado; Fase 1 não iniciada.

A [v1](https://github.com/LimaGV/C-NBI/tree/cnbi-v1.0) é referência histórica.
Não foram herdados módulos, arquitetura, ambiente ou parâmetros.

## Ambiente
Python **3.12.15** e uv **0.12.23**. Na raiz:

~~~sh
uv sync --locked
uv run python -c "import sys, cnbi_v2; print(sys.executable); print(cnbi_v2.__file__)"
uv run pytest
uv run ruff check .
uv run mypy src
uv run python scripts/verify_environment.py
~~~

.venv é local; o pacote editável vem de src/cnbi_v2. Importar cnbi_v2,
nunca cnbi. Não apontar PYTHONPATH para a v1. O lock acompanha o projeto;
a CI repete os quatro checks obrigatórios em Windows e Ubuntu.

## Dados experimentais e referências
Excel é registro primário aceito. Seguir [data/README.md](data/README.md):
raw imutável → validação/hash → snapshot se necessário → transformação
versionada → processed. Resultados computacionais ficam em results/.

~~~sh
uv run python scripts/data/verify_workbook.py "caminho/arquivo.xlsx"
~~~

Inspeção não recalcula fórmulas, resolve links ou certifica caches.
Ver [opções e limites](scripts/data/README.md). Não incorpora dataset ou snapshot.
Zotero/local documents → verificação → notas/BibTeX → claims → ADR/MDR.
Documentos locais protegidos ficam fora do Git por padrão.

## Governança
Usar feature/*, experiment/*, fix/*, docs/* ou release/*.
main é destino de PR aprovado. A Fase 0 entrou pelo PR #1 após CI verde;
a Fase 0.5 usa feature/00-5-data-reference-foundation, sem merge automático.

- [Contrato dos agentes](AGENTS.md)
- [Arquitetura](docs/architecture.md) e [roadmap](ROADMAP.md)
- [Decisões](docs/decisions/) e [estado metodológico](docs/methodology_status.md)
- [Reprodutibilidade](docs/reproducibility.md)
- [Integridade](docs/data_integrity.md) e [gestão dos dados](docs/data_management.md)
- [Verificação do ambiente](docs/environment_verification.md)
- [Inventário MCP](docs/integrations/mcp_inventory.md)
- [Referências](references/README.md)

Licença pendente: LICENSE_DECISION_PENDING.md. CITATION.cff descreve software
em desenvolvimento, sem DOI ou publicação inventados.
