# Oito RSMs reais e comparação publicada

Input literal e imutável: CCD_values_20261023.xlsx, SHA 7f905b7a...;
19 corridas, 3 fatores, 8 respostas. Os valores reais de Y não são arredondados.
O manifesto registra a execução em commit limpo e os hashes de código/inputs.

Cada pasta tem fatores efetivos, os 80 coeficientes nas unidades das células,
fitted values, resíduos, covariância residual e MSE/S/R² por resposta.
`physical_cells` preserva os próprios fatores físicos; as outras pastas são
recodificação afim ou desenhos nominais explicitamente separados.

`all_80_coefficient_comparisons.csv` compara 80 números em cada combinação
de quatro desenhos e duas escalas (640 linhas). `summary.json` resume contagens.
Nota literal ×100: até 50/80; escala diagnóstica ×1000: até 70/80, ambos no
CCD nominal rotacional. WR com precisão integral não reproduz os dez coeficientes.

`wr_rounding_hypothesis.json` é diagnóstico opcional a posteriori: arredondar
somente uma cópia de WR a três casas antes do OLS reproduz 10/10, mas muda
19 valores da cópia. Não entra nos modelos reais ou nos totais de validação.
Não prova o preprocessing dos autores e não foi adotado para o dataset.

Ver [relatório e limites](../../docs/mathematics/turning_real_validation.md).
Reexecução: `uv run python -m scripts.validation.turning_reference --investigate-wr-rounding`.
Checksums cobrem os artefatos calculados; README não interfere na computação.
