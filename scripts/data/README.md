# Inspeção de workbooks

Uso na raiz do projeto:

~~~sh
uv run python scripts/data/verify_workbook.py "caminho/arquivo.xlsx"
uv run python scripts/data/verify_workbook.py "caminho/arquivo.xlsx" --header-row 3
~~~

verify_workbook.py usa cnbi_v2.data.inspect_workbook e imprime JSON em stdout.
Não escreve arquivos, não transforma dados, não cria snapshot, não recalcula
Excel, não resolve links, não incorpora datasets e não envia conteúdo à rede.
Para guardar um relatório, escolher explicitamente destino fora de raw e revisar
informações sensíveis antes de versionar.

## Conteúdo e interpretação
Relata nome, SHA-256, tamanho, abas, dimensão declarada aproximada, extensão
observada, colunas/cabeçalhos, duplicações aparentes, tipos e vazios, fórmulas
e sinais de dependências externas. Todas as abas são listadas; estatísticas de
células cobrem worksheets, não abas de gráfico (non_worksheet_names).
O hash é conferido novamente no fim;
mudança dos bytes durante a leitura invalida a inspeção.

A primeira linha é posição inicial de cabeçalho, não inferência científica.
--header-row escolhe outra linha explicitamente. Duplicatas usam strip/casefold;
não são renomeadas. Vazios e tipos cobrem o retângulo inspecionado, incluindo
cabeçalhos e posições ausentes entre células, não a grade inteira do Excel.

Dimensões declaradas podem estar erradas: são relatadas, mas a leitura ignora
seus limites usando reset_dimensions em memória. Isso não altera o arquivo.
--max-cells (padrão 1000000 por aba) limita células materializadas na varredura;
uma linha que ultrapassaria o orçamento não é inspecionada. O relatório marca
inspection_complete=false. --detail-limit (padrão 100) limita detalhes de fórmulas;
a contagem e a detecção continuam em toda a parte inspecionada. Estes são
controles de recursos/relatório, não thresholds científicos.

## Fórmulas e dependências
data_only=False preserva expressões. Valores calculados/caches ficam NOT_VERIFIED.
Detecta referências diretas a workbook em operandos de fórmula, nomes definidos,
partes OOXML externalLinks/connections/queryTables e relações externas.
Hiperlinks são relatados separadamente de dependências de dados.
Fórmulas não interpretáveis e varredura parcial impedem concluir ausência.

- DETECTED_UNRESOLVED: sinais encontrados; dependências não foram resolvidas.
- INDETERMINATE: ausência não avaliável por limite ou expressão não interpretada.
- NOT_DETECTED: nenhum sinal detectado; não certifica workbook autocontido.

Referências dinâmicas, funções indiretas, conexões proprietárias e caches
obsoletos podem escapar à análise. Inspeção não é validação de valores.
Never use an Excel workbook with unresolved external links as the sole computational source of truth.

Somente .xlsx é suportado. .xls e .xlsm não são convertidos silenciosamente.
Código 0 significa inspeção concluída com relatório, não aprovação científica;
2 indica erro de entrada/leitura, com mensagem JSON em stderr.
