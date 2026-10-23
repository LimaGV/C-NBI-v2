# Contrato permanente dos agentes — C-NBI v2

## Clean implementation
C-NBI v2 is a clean reimplementation.
Legacy code is historical reference only.

A v1 em https://github.com/LimaGV/C-NBI, branch cnbi-v1.0, é somente referência.
Não modificar a v1, copiar módulos, importar cnbi, reutilizar .venv, herdar sua
arquitetura ou preservar thresholds e decisões por continuidade.
A distribuição é c-nbi-v2; o import é cnbi_v2.

## Scientific change policy
A fundação contém somente infraestrutura. Não iniciar Fase 1 sem nova tarefa.
Nenhuma mudança metodológica sem definição matemática, evidência, ADR/MDR,
testes e validação. Hipótese experimental não vira metodologia oficial.
Registrar o que mudou, por quê, branch, commit, decisão, testes, resultados
afetados e versão do código.
Não alterar silenciosamente seed, threshold, solver, normalização, número de
Monte Carlos, H, covariância, critério Pareto, tolerância ou regularização.
Mudanças, inclusive defaults, exigem decisão documentada.

Estados: PROPOSED, EXPERIMENTAL, ACCEPTED, REJECTED, SUPERSEDED.
Fluxo: PROPOSED → EXPERIMENTAL → VALIDATION → ACCEPTED.
VALIDATION é um gate, não um sexto estado persistido. Seguir o template;
validação aprovada não implica aceitação automática: revisão explícita é exigida.

## Tool policy
- Serena: preferir navegação semântica. Antes de editar ciência existente:
  localizar símbolo, referências, dependências e impacto; só então editar.
  Se indisponível, registrar e usar busca focada.
- fd / rg: localização de arquivos / busca textual. Na ausência de fd, rg --files.
- ast-grep: padrões e transformações estruturais; não usar o alias sg nem
  substituições textuais cegas quando estrutura for mais segura.
- Repomix: contexto amplo e auditorias cruzadas; evitar em tarefas pequenas.
  Não agregar secrets, dados ou PDFs.
- Zotero: fonte canônica da biblioteca pessoal; primeira consulta de literatura
  potencialmente existente. Buscar título, autor, DOI ou tópico, conferir
  metadados e localizar documentos quando permitido. Não exportar a biblioteca.
  Não inventar DOI, título, autor, ano, páginas, equações, volume ou periódico.
  METADATA_VERIFIED não equivale a FULLTEXT_VERIFIED. Este último exige inspeção
  real do texto integral, com passagens e localização registradas.
- Context7: documentação atual de bibliotecas, frameworks, SDKs, APIs, CLIs e
  cloud, inclusive setup e debugging específico. Começar por resolve-library-id
  salvo ID /org/project exato; escolher fonte relevante e query-docs por conceito.
  Se ausente, registrar e consultar docs oficiais, sem fingir consulta.
  Context7 fundamenta software, nunca validade científica.
- OpenAI Developer Docs MCP: primeira fonte oficial para OpenAI/Codex/MCP.
  Se não exposto, usar páginas oficiais e registrar fallback.
- Blender: IRRELEVANTE à infraestrutura científica atual.
- cua_repl / node_repl: suporte somente quando necessário.
- code-review / codex_app: disabled por política desta tarefa; não depender.
- GitHub: git e gh autenticado; não depender de GitHub MCP.

Distinguir estado informado, ferramenta exposta e teste real no inventário MCP.

## Desenvolvimento e qualidade
Python 3.12; .venv própria via uv. Não reutilizar ambiente da v1.
Na raiz: uv sync --locked; uv run pytest; uv run ruff check .; uv run mypy src.
Dependências novas exigem justificativa; mudanças acompanham uv.lock.
Nunca desenvolver em main. Usar feature/*, experiment/*, fix/*, docs/*, release/*.
Proibidos nomes final, final2, test, temp, new. main só recebe estados testados,
documentados, reproduzíveis e metodologicamente rastreáveis por PR.
Não fazer merge com CI falhando; não mergear esta fundação automaticamente.
main nasce com um commit vazio para permitir o primeiro PR.

## Referências e dados
Classificar claims: LITERATURE, INTERNAL_EVIDENCE, PROPOSED.
Status: SUPPORTED, PARTIALLY_SUPPORTED, EXPERIMENTAL, UNVERIFIED, REJECTED,
SUPERSEDED. Não escrever "a literatura mostra" sem fonte verificável.
Dados brutos são imutáveis. Derivações exigem origem, hashes, commit, configuração,
ambiente e resultados. Não versionar dados, anexos Zotero ou grandes resultados
automaticamente. Seguir docs/data_integrity.md e docs/data_management.md.

## External actions e secrets
Não executar ações destrutivas ou persistentes desnecessárias sem autorização
da tarefa. Esta fundação autoriza criar LimaGV/C-NBI-v2 privado, push e PR;
não autoriza modificar a v1 ou fazer merge.
Nunca registrar tokens, API keys, passwords ou credentials. Não copiar .env,
configuração global de agentes, credenciais ou conteúdo de keyring para o Git.
