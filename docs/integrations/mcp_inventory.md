# Inventário MCP

Data: 2026-10-23. Estado informado vem das instruções do responsável.
TESTED exige chamada real bem-sucedida; metadados de ferramentas não bastam.

| Integração | Estado informado | Evidência nesta sessão | Finalidade / relevância | Leitura/escrita |
| --- | --- | --- | --- | --- |
| zotero | habilitado e previamente verificado | TESTED: zotero_get_collections(limit=1) respondeu com sucesso | Biblioteca científica pessoal canônica; relevante | Leitura testada; escrita exposta, não executada |
| serena | habilitado e previamente verificado | NOT_TESTED: ferramentas não expostas ao agente | Navegação semântica; relevante com código | Não confirmado |
| repomix | habilitado e previamente verificado | NOT_TESTED: ferramentas não expostas; contexto amplo desnecessário nesta base nova | Contexto agregado sob demanda | Não confirmado |
| context7 | habilitado e previamente verificado | NOT_TESTED: resolve-library-id/query-docs não expostos; fallback oficial web | Documentação de software; relevante | Não confirmado |
| openaiDeveloperDocs | habilitado e previamente verificado | NOT_TESTED: MCP não exposto; páginas oficiais OpenAI abertas via web | OpenAI/Codex/MCP; governança | Leitura web realizada, não teste MCP |
| blender | habilitado e previamente verificado | NOT_TESTED: não chamado | IRRELEVANTE à infraestrutura científica atual | Não testado |
| cua_repl | habilitado e previamente verificado | NOT_TESTED: não necessário | Suporte eventual | Não testado |
| node_repl | habilitado e previamente verificado | NOT_TESTED: não necessário | Suporte eventual | Não testado |
| code-review | disabled | DISABLED_BY_POLICY: não usado | Não depender | Não testado |
| codex_app | disabled para infraestrutura | Sem dependência no projeto; attach_artifact foi usado apenas para associar o PR ao chat, por exigência da interface do ambiente | Metadado de interface, fora do fluxo científico | Somente associação do PR; nenhuma operação de código/ambiente |

Teste Zotero somente de leitura de uma coleção; nenhum item/PDF/nota foi
copiado, adicionado, alterado ou excluído. Conectividade não valida ciência.
Fase 0.5: zotero_get_collections(limit=1) retestado com sucesso em 2026-10-23,
somente leitura. Serena/Repomix/Context7/OpenAI Docs MCP continuam sem exposição.
Fase 0.6: Zotero consultado em leitura para busca, metadados e anexos de SMMX47JT;
nenhum anexo encontrado. PDF local verificado separadamente, sem alterar Zotero.
O locator de dependências do ambiente e o vínculo de PR na interface foram
usados como suporte externo; o projeto continua executado por uv, sem dependência
de codex_app para sua infraestrutura ou execução científica.
Revalidar Serena, Context7 e OpenAI Docs MCP quando estiverem expostos.
Fase 1: Zotero search/metadata/children usados para Díaz-García/Bashiri,
Myers/Montgomery/Anderson-Cook, Johnson/Wichern e busca Khuri, somente leitura.
Preprint arXiv primário e livro RSM local inspecionados por passagens; linked_url
de Johnson/Wichern indisponível por timeout. Context7/Serena/Repomix continuam
sem exposição; NumPy 2.5 consultado em documentação oficial via web.
Busca focada rg e AST do Python foram usadas para navegação/auditoria.
Validação aplicada: Zotero buscou NIST, sem item pertinente (fallback textual
retornou itens não relacionados, que não foram usados). Fórmula de CCD rotacional
conferida diretamente no handbook oficial do NIST; nenhum metadado de item foi inventado.
Não instalamos/reconfiguramos MCPs nem obtivemos credenciais.
Fechamento da Fase 1: metadados Zotero Z8Z2JEDC reconferidos em leitura;
passagens de ANOVA/R²/PRESS/LOF verificadas no livro local e NIST oficial.
Context7 segue não exposto; `scipy.stats.f.sf` conferido na documentação
oficial estável (1.18.0; runtime locked 1.18.1). URL 1.18.1 indisponível via web.
Não se usou Context7 como fonte de validade científica.

Retomada de finalização em 2026-10-24: Context7 e Serena passaram a estar
expostos. Context7 resolve_library_id(SciPy) selecionou /scipy/scipy e query_docs
reconferiu a survival function (1-CDF); a assinatura F já havia sido verificada
na documentação oficial específica. Não houve mudança de API ou cálculo.
O manual inicial Serena respondeu; a sessão apontou para o diretório de contexto,
sem language servers, diferente do repositório C-NBI-v2. Não se fez onboarding,
migração ou edição semântica: código já estava implementado e esta retomada
se limitou ao gate, documentação e entrega Git. Os registros anteriores de
indisponibilidade permanecem como histórico, não como estado atual.

## Ferramentas locais

Fase 2: Serena ativada no repositório C-NBI-v2 com LSP Python; RSMFit, ordem
canônica e referências inspecionados antes de acrescentar módulos separados.
Context7 testado para SciPy SLSQP/brentq e NumPy quantile(method=linear).
Zotero consultado em leitura para Maia, Khuri/Conlon e Das/Dennis. Sem item Maia;
tese local 2020 identificada pelo título e repositório institucional, passagens
renderizadas. Originais do autor consultados via gh e planilha local, somente
leitura. Nenhuma escrita Zotero, cópia de PDF ou dependência nova.
Executados: Git 2.54.0.windows.1, uv 0.12.23, rg 15.2.0, gh 2.97.0.
gh autenticado como LimaGV; criação/push/PR via CLI, sem GitHub MCP.
fd e ast-grep não encontrados no PATH nem nas pastas locais verificadas.
Não instalar substitutos ou tratar o alias sg como ast-grep.

## Fase 3 — uso efetivo

Serena: manual inicial lido, sessão b3010349 no projeto C-NBI-v2/LSP Python;
RSMFit, fit_multivariate_rsm, coefficient_covariance e loader codificado
inspecionados semanticamente antes de criar os módulos independentes.
Nenhum módulo científico anterior foi alterado.
Context7: resolve/query para NumPy Generator/PCG64/standard_normal, SciPy
solve_triangular e Matplotlib Figure/Agg. A busca SciPy retornou material
insuficiente; assinatura e comportamento foram conferidos na documentação
oficial de solve_triangular. Referências de APIs na documentação matemática.
Zotero não foi necessário para novas claims de literatura: a covariância é
derivada diretamente, e resultados novos são evidência interna/decisão explícita.
Nenhum item bibliográfico ou documento protegido foi escrito/exportado.
Git/gh autenticado para preflight, squash autorizado e entrega do PR.
Matplotlib no grupo dev justificado pelo PNG solicitado; runtime preservado.
