# Fase 0.6 — verificação documental e de integridade

Data: 2026-10-23. Projeto C-NBI-v2.
Branch: feature/00-6-turning-reference-dataset. Versão: 0.1.0.dev0.

## Preparação
PR #2 encontrado OPEN, CLEAN, MERGEABLE, head e009f6bc0470a26c78d9813a1b23f43df4d9cc3e,
com quatro checks SUCCESS (push/PR em Windows/Ubuntu).
Não havia aprovação formal de review registrada no GitHub; a integração seguiu
a autorização explícita do responsável nesta tarefa e a política sem review obrigatório.
Squash permitido pelo repositório e executado com head esperado.
main atualizada por fast-forward, limpa, árvore idêntica à revisão aprovada:
5bc81a39294d14ac5154af672381f580fde76cc3.
Nova branch criada a partir desse estado; nenhum desenvolvimento em main.

## Fonte e cópia
Arquivo CCD.xlsx fornecido por caminho exato pelo responsável, sem seleção
ambígua de candidatos ou busca indiscriminada em disco.
Fonte e raw de 15427 bytes têm o mesmo SHA-256:
fd9c463efdcd62ff3d7eaa7eec18d9e112543675c30b1f36838beeb38deebf4a.
Cópia via Copy-Item sem abrir/salvar Excel. O responsável autorizou explicitamente
envio deste workbook ao repositório privado; exceção de ignore limitada a um arquivo.
Atributo Git binary garante que não haja normalização de linhas no raw.

provenance.yaml registra origem relativa a Documents, operador, data, método,
hashes e commit efetivo de incorporação. O commit é registrado em atualização
posterior para evitar inventar um hash autorreferente antes de existir.

## Inspeção
CLI somente leitura, --detail-limit 1000: Plan1, A1:L20, 19 corridas, três fatores,
oito respostas, 152 fórmulas de resposta externas, nenhum vazio no retângulo.
Refs para NBI Revisão.xlsm, Data!linhas 4–22, sem resolução automática.
152 caches numéricos presentes, mas versão/frescor não comprovados.
RAW_NOT_SELF_CONTAINED, SNAPSHOT_PENDING_EXTERNAL_SOURCE; processed não criado.
O relatório omite apenas o segmento de diretório pessoal de um target externo,
com redaction explícita. Não se alterou o raw.

O primeiro uso real revelou UnicodeEncodeError sob stdout cp1252 no Windows.
A CLI agora usa JSON ASCII escaped, sem perda após JSON decode. Regressão
verifica nomes Unicode sob PYTHONIOENCODING=ascii, inclusive caractere combinante.
Nenhum cálculo científico foi acrescentado.

## Referência publicada
Zotero consultado primeiro: SMMX47JT, metadados completos correspondentes ao DOI.
Sem anexo Zotero. PDF local fornecido, 32 páginas, SHA-256
5717f7a90195157830e42e038782f43b2976c77813ccc11f2b3c01e3cc2be70a.
Texto integral inspecionado, com conferência visual de Table 3 p.13,
Eq. (17)/(19) p.6, Table 1 p.11 e Table 6 p.18.
Metadados e texto integral verificados; prioridade CRITICAL_SOURCE.
O PDF e seu texto integral não foram incorporados ao Git.

80 coeficientes (10×8) conferidos visualmente e por extração textual posicionada
independente; sinais e três casas decimais coincidiram integralmente.
VRF1/2/3 excluídos. Resumo secundário preservado, sem recálculo.
Nota da Table 3: WR/ROI/OEE e S em 10^-2, metadados separados e sem rescaling.
Table 2 usa outra nota para WR. Níveis físicos da Table 1 divergem do raw;
coding e associação exata de beta/fator permanecem pendentes.
C011 (reproduzir coeficientes a partir deste raw) continua PROPOSED/UNVERIFIED.

## Verificação local
uv sync --locked: aprovado. Nenhuma dependência adicionada.
uv run pytest -v: 73 passed.
uv run ruff check .: All checks passed.
uv run mypy src: Success, no issues found in 5 source files.
Testes cobrem forma/ordem/precisão dos arquivos, DOI, hashes, imutabilidade,
inspeção, publicação do raw autorizado e independência da produção em relação
a expected outputs. Nenhum teste ajusta modelo.
checksums.sha256 cobre sete artefatos explicitamente enumerados.
Auditoria de 84 arquivos rastreados/preparados: um único binário autorizado
(raw XLSX), nenhum PDF ou texto integral publicado e nenhum padrão de secret
detectado, inclusive no OOXML do raw. YAML e links locais conferidos.
Original, raw e PDF mantiveram seus hashes; pacote src/ não foi alterado.

## Limites e próximos passos
Fase 0.6 documental concluída; entrada computacional validada ainda não está pronta.
Antes da Fase 1: fonte externa/versionamento, snapshot validado, reconciliação de
níveis físicos, coding/ordem beta e escala/rounding. Tolerância ainda não definida.
Nenhuma resposta reconstruída, OLS/RSM/CNBI/NBI/Monte Carlo implementado ou Fase 1 iniciada.
Novo PR para main, sem merge automático. CI remota vinculada ao SHA na aba Actions/PR.
