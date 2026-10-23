# Integridade experimental

The agent must never silently modify experimental raw data.

Raw são bytes exatamente recebidos, nunca editados in-place. Correções,
exclusões, conversões, imputações e normalização exigem transformação explícita,
reproduzível, versionada, documentada e testável em outra camada. Preservar
original e razão. Snapshot também é imutável após criação e não substitui raw.

Never use an Excel workbook with unresolved external links as the sole computational source of truth.

Excel é aceito como fonte primária. Snapshot futuro materializa valores usados
por procedimento e validação explícitos, sem presumir correção de caches.
O inspetor não gera snapshot. Ausência de link detectado não prova independência.

Registrar origem, responsável, datas, permissões, esquema, unidades, desenho e
SHA-256 de raw/snapshot/processed. Divergência de hash bloqueia uso até
esclarecimento. Hash identifica bytes, não validade de valores.
Derivação registra entrada, código/commit, ambiente, parâmetros e saída/hashes.
Futuras linhas terão run_id explícito; linha Excel é coordenada, não ID.
Resultados pertencem a results/, nunca a raw.
Nenhum dataset foi incorporado, corrigido ou transformado nesta fase.
