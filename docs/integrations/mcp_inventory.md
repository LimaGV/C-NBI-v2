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
Não instalamos/reconfiguramos MCPs nem obtivemos credenciais.

## Ferramentas locais
Executados: Git 2.54.0.windows.1, uv 0.12.23, rg 15.2.0, gh 2.97.0.
gh autenticado como LimaGV; criação/push/PR via CLI, sem GitHub MCP.
fd e ast-grep não encontrados no PATH nem nas pastas locais verificadas.
Não instalar substitutos ou tratar o alias sg como ast-grep.
