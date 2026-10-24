# Revisão literal do CCD fornecida em 2026-10-23

O responsável informou que o CCD agora contém os valores necessários e pediu
o ajuste preservando os valores reais das células. A nova revisão é copiada
byte a byte; o raw histórico da Fase 0.6 permanece intacto.

- `dataset.json`: 19 corridas × (3 fatores + 8 respostas) = 209 números,
  além de 19 IDs; zero fórmulas, vazios e dependências externas detectadas.
- `provenance.json`: origem, hashes, cópia, operador e commit de incorporação.
- `workbook_inspection.json`: CLI read-only, sem recalcular ou salvar o XLSX.
- `coding_and_scaling.json`: quatro desenhos e duas interpretações de escala,
  explicitamente separados. Y sempre mantém os valores reais nas oito regressões.

O CSV processed mantém exatamente os tokens numéricos do XML do Excel,
inclusive as casas que a interface pode não exibir. Nenhuma imputação, truncamento,
arredondamento ou alteração de unidades é aplicado aos dados extraídos.
Como o novo raw já é literal e autocontido, não é necessário fabricar outro snapshot.

Ver [relatório científico](../../../../docs/mathematics/turning_real_validation.md).
Reprodução completa da Table 3 não foi estabelecida; escala e WR divergem.
