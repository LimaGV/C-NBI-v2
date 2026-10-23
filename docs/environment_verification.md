# Verificação do ambiente

Data: 2026-10-23 (America/Sao_Paulo). Plataforma local: Windows x86_64.
Projeto: C:/Users/gabri/Documents/C-NBI-v2.
Branch: feature/00-project-foundation. Versão: 0.1.0.dev0.
O SHA final consta no histórico e no PR; não se insere um SHA autorreferente.

## Ferramentas e ambiente
Git 2.54.0.windows.1; uv 0.12.23; rg 15.2.0; gh 2.97.0.
gh autenticado como LimaGV via keyring; nenhum conteúdo de credencial registrado.
fd e ast-grep não encontrados no PATH nem nas pastas locais verificadas.
Python 3.12.15 instalado por uv; .venv nova, sem reutilização da v1.
uv sync concluiu; uv sync --locked confirmou o lock sem alteração.
SHA256 de uv.lock: E98142352294FFD2BE9D4A30583117436569F25DB74F7837BB7E355D87F3A406.
Foram resolvidos 113 pacotes no lock multiplataforma e instalados 110 no Windows.
Os avisos iniciais do uv trataram metadados legados de dependências transitivas;
não houve falha nem ajuste de versões manual para ignorá-los.

Comando executado:

~~~sh
uv run python -c "import sys, cnbi_v2; print(sys.executable); print(cnbi_v2.__file__)"
~~~

Resultado:

~~~text
C:\Users\gabri\Documents\C-NBI-v2\.venv\Scripts\python.exe
C:\Users\gabri\Documents\C-NBI-v2\src\cnbi_v2\__init__.py
~~~

scripts/verify_environment.py também foi executado. Confirmou prefixo em .venv,
versão 0.1.0.dev0, legacy_cnbi_discoverable=false e legacy_cnbi_loaded=false.
sys.path continha apenas scripts/, src/, .venv e a biblioteca padrão do Python
gerenciado por uv; nenhum checkout da v1. Os testes verificam isso sem importar cnbi.

| Dependência direta | Versão instalada |
| --- | --- |
| numpy | 2.5.4 |
| scipy | 1.18.1 |
| pandas | 3.1.0 |
| scikit-learn | 1.9.1 |
| pytest | 9.1.1 |
| pytest-cov | 7.1.0 |
| ruff | 0.17.2 |
| mypy | 2.4.0 |
| ipykernel | 7.4.0 |
| jupyterlab | 4.6.4 |

## Verificações locais
- uv sync --locked: aprovado.
- uv run pytest: 12 passed, incluindo imports, versão, Python, origem, ambiente
  e ausência de acoplamento à v1.
- uv run ruff check .: All checks passed.
- uv run mypy src: Success, no issues found in 2 source files.
- Workflow YAML: matriz Windows/Ubuntu e quatro comandos obrigatórios conferidos.
- Metadados básicos de CITATION.cff e git diff --check conferidos.
- Auditoria dos 47 arquivos preparados: estrutura exigida e links locais válidos;
  nenhum padrão de token, chave privada ou URL com credencial detectado.
  .venv, .env e configurações privadas de agentes ficaram fora do Git.
  A verificação não acessou nem exportou credenciais do sistema.

Esses checks são de infraestrutura, sem validação matemática ou metodológica.
A CI repetiu os checks em Windows e Ubuntu para a fundação
78568c9c8a61238f615b56f94456442b16125c71. Os quatro jobs (push e PR nos dois
sistemas) concluíram com SUCCESS, incluindo sync, pytest, Ruff e mypy.
Evidências: [push](https://github.com/LimaGV/C-NBI-v2/actions/runs/40012646633),
[PR](https://github.com/LimaGV/C-NBI-v2/actions/runs/40012648564) e
[PR aberto, sem merge](https://github.com/LimaGV/C-NBI-v2/pull/1).
Este registro posterior não altera o código da fundação.

## GitHub e limitações
Repositório criado e verificado privado: https://github.com/LimaGV/C-NBI-v2.
origin: https://github.com/LimaGV/C-NBI-v2.git. main é a branch padrão e contém
inicialmente apenas o commit vazio de bootstrap. A fundação segue na feature.
Foi tentada proteção de main com PR obrigatório, checks Windows/Ubuntu,
sem force push e sem exclusão. GitHub retornou HTTP 403: o plano atual exige
upgrade para proteção em repositório privado. A visibilidade não foi alterada.
A regra de revisão/CI permanece no contrato; não há enforcement remoto ativo.

Zotero testado somente em leitura. Serena, Repomix, Context7 e OpenAI Docs MCP
não testados: não expostos nesta sessão. Fallback oficial web documentado no
inventário; nenhuma reconfiguração ou obtenção de credenciais efetuada.

A v1 não foi modificada ou copiada. Nenhum algoritmo científico implementado;
nenhuma execução científica, dado ou resultado produzido. Fase 1 não iniciada.
