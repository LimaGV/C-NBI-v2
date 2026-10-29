# Gestão dos dados

Atualização2026-10-29: o responsável autorizou a divulgação pública dos CCD,
extrações, legado, derivados e metadados identificados na auditoria. Ver
[permissões](data_publication_permissions.md). A divulgação não concede licença
aberta de reutilização. MIT cobre apenas código próprio (LICENSE_SCOPE.md).
Registros de autorização privada permanecem como evidência histórica.

Excel (.xlsx) pode ser registro primário. Não exigir coleta em CSV.
raw preserva bytes recebidos; snapshots preservam valores quando necessários;
interim é regenerável; processed deriva de raw/snapshot + script;
external identifica terceiros; metadata registra a cadeia.

## Classificação por dataset, sem inferência
- PUBLIC_SMALL: versionamento direto após confirmação/aprovação, com exceção
  exata revisada no .gitignore, inclusive processed público pequeno.
- PUBLIC_LARGE: solução futura apropriada; não configurar LFS automaticamente.
- RESTRICTED: payload fora do Git; versionar somente metadata permitida,
  hash esperado, provenance e código.

Categoria desconhecida fica vazia. Ignorar payload por padrão não atribui classe.
Não alterar ignore só para esconder dados reais ou limpar working tree.
data/ não é ignorada inteira: README, metadata e schemas continuam versionáveis.
Raw/snapshot são imutáveis; derivação registra entradas, hashes, commit,
configuração, ambiente e saídas. Resultados ficam em results/, nunca em raw.

local_library ignora binários, incluindo PDF/EPUB/DJVU; somente Markdown,
BibTeX, YAML, JSON e CSV seletivos são elegíveis por padrão. Direitos continuam
obrigatórios; não publicar obras integrais trocando sua extensão para texto.
Revisar confidencialidade dos metadados, retenção, acesso e restauração.
Não adotar cloud/LFS nem copiar a biblioteca Zotero automaticamente.
Zotero somente leitura nesta fase; nenhum dataset/documento incorporado.
