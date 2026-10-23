# Raw — evidência original imutável

Guardar exatamente os bytes recebidos: .xlsx, .xls, .csv ou saída de instrumento.
Nunca modificar in-place, sobrescrever, recalcular/salvar Excel, excluir linhas,
corrigir unidades ou substituir silenciosamente. Preservar hash e proveniência.

Erro no original deve ser documentado; correção é transformação versionada em
outra camada ou nova versão recebida da fonte, preservando a anterior.
O inspetor desta fase suporta somente .xlsx; outros formatos continuam aceitos
como raw, sem conversão automática.

Não há arquivo experimental nesta pasta. A política de imutabilidade não é uma
permissão de publicação: payloads ficam ignorados até classificação/aprovação.
