# Extração literal do CCD atualizado

CCD_values_20261023.csv contém os tokens numéricos originais das células
Plan1!A2:L20 da revisão literal autocontida CCD_values_20261023.xlsx.
Mantém os cabeçalhos originais e os 19 IDs. Não há arredondamento, troca de
valores, rescaling, imputação ou reconstrução por coeficientes publicados.

Regerar: uv run python -m scripts.validation.turning_reference --extract-only.
Hashes, fonte, parâmetros de codificação e resultados ficam em metadata/revisão
e results/turning_8responses_validation/. O raw histórico com links permanece
inelegível; seus caches não são inputs do script.
