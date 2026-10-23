# Gestão dos dados e artefatos

| Artefato | Política inicial |
| --- | --- |
| Código/governança | Git e revisão por PR |
| Dados brutos/derivados | Fora do Git por padrão; acesso/backup definidos antes da coleta |
| Manifestos pequenos | Git após revisão de conteúdo/permissões |
| Resultados | results/ local ignorado; evidências pequenas só por decisão explícita |
| Experimentos | Protocolos no Git; runs/ ignorado |
| Notebooks | Remover saídas, dados e credenciais antes de commitar |
| PDFs/anexos | Zotero canônico; inclusão seletiva com permissão |
| BibTeX/notas | Metadados verificados e rastreáveis a Zotero |
| Ambientes/secrets/caches | Nunca versionar |

Planejar nomes, retenção, responsável, controle de acesso e restauração antes
de produzir dados. Não adotar armazenamento externo, LFS ou cloud automaticamente.
Registrar transferências e conferir hashes. Não copiar a biblioteca Zotero inteira.
Somente leitura Zotero autorizada nesta fundação; não modificar/excluir itens.
