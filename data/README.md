# Dados experimentais — Fase 0.5

Excel (.xlsx) é aceito como registro primário de laboratório. Pesquisadores não
precisam coletar diretamente em CSV. Código computacional deve consumir entradas
rastreadas e transformações versionadas, sem depender de edição manual.

~~~text
Experimental workbook
        ↓
       raw
        ↓
validation + hashing
        ↓
snapshot if necessary
        ↓
scripted transformation
        ↓
processed
        ↓
scientific model
        ↓
results
~~~

| Camada | Papel |
| --- | --- |
| raw/ | Bytes exatamente recebidos, nunca editados in-place |
| snapshots/ | Cópias autocontidas e imutáveis, quando necessárias e explicitamente criadas |
| interim/ | Conversões e limpeza regeneráveis |
| processed/ | Tabelas reproduzíveis a partir de raw/snapshot e script versionado |
| external/ | Fontes externas com origem, licença e versão verificadas |
| metadata/ | Proveniência, desenho, variáveis, unidades, hashes e transformações |

**Never use an Excel workbook with unresolved external links as the sole computational source of truth.**

O raw permanece intacto. Snapshot com valores materializados exige procedimento
futuro explícito e validação; o inspetor não calcula fórmulas nem cria snapshots.
Resultados computacionais pertencem a results/, nunca retornam a raw/.

## Identidade e publicação
Cada linha experimental deverá ter identificador explícito, por exemplo run_id.
Número da linha do Excel é coordenada de origem, não identificador científico.
Não renumerar ou alterar datasets existentes agora.

Classificar cada dataset com evidência: PUBLIC_SMALL, PUBLIC_LARGE ou RESTRICTED.
Não inferir categoria. Por padrão, payloads de todas as camadas ficam fora do
Git; READMEs, metadata e schemas podem ser versionados. PUBLIC_SMALL aprovado
pode receber exceção estreita e revisada no .gitignore, inclusive processed.
PUBLIC_LARGE requer solução futura; não configuramos LFS.
RESTRICTED mantém no Git somente metadados permitidos, hashes esperados,
proveniência e código. Revisar metadados também quanto à confidencialidade.

Nenhum dataset real foi incorporado. O contexto conceitual informado sobre CCD,
19 ensaios, 3 fatores, 8 respostas e 5 pontos centrais não foi convertido em dados,
nem usado para preencher metadados por inferência.

Inspeção: [scripts/data/README.md](../scripts/data/README.md).
Políticas: [gestão](../docs/data_management.md) e [integridade](../docs/data_integrity.md).
