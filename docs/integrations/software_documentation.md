# Documentação de software consultada

Consulta: 2026-10-23. Context7 não exposto; links oficiais abertos via web.
Isto não é validação científica nem teste do MCP Context7.

| Fonte | Uso |
| --- | --- |
| https://docs.astral.sh/uv/concepts/projects/init/ | Layout de projeto |
| https://docs.astral.sh/uv/concepts/build-backend/ | uv_build e module-name |
| https://docs.astral.sh/uv/guides/integration/github/ | CI, lock e Python pinado |
| https://docs.pytest.org/en/stable/reference/customize.html | Configuração pytest |
| https://docs.astral.sh/ruff/configuration/ | Lint |
| https://mypy.readthedocs.io/en/stable/config_file.html | Tipagem estrita |
| https://cli.github.com/manual/gh_repo_create | Repositório privado |
| https://cli.github.com/manual/gh_pr_create | PR e corpo em arquivo |
| https://docs.github.com/en/rest/branches/branch-protection | Proteção quando suportada |
| https://learn.chatgpt.com/docs/agent-configuration/agents-md | Contrato de agentes |
| https://learn.chatgpt.com/docs/extend/mcp?surface=cli | Configuração MCP e privacidade |

Páginas OpenAI acessadas pelos redirecionamentos oficiais de developers.openai.com.
openaiDeveloperDocs MCP não foi chamado. SHAs da CI conferidos com git ls-remote:
actions/checkout v7.0.1 e astral-sh/setup-uv v9.0.0.
uv e backend mantidos em 0.12.23, sem upgrade global.
