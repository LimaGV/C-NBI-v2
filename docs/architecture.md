# Arquitetura — fundação RSM da Fase 1

Layout src com distribuição c-nbi-v2 e import cnbi_v2. A versão permanece
0.1.0.dev0. Nenhum código ou ambiente da v1 é reutilizado.

- `data/hashing.py`: SHA-256 somente leitura.
- `data/workbooks.py`: inspeção de XLSX por openpyxl e OOXML, sem recálculo/save.
- `scripts/data/verify_workbook.py`: relatório JSON, sem materialização de respostas.
- `model/quadratic_design.py`: base completa e ordem dos termos, sem coding implícito.
- `model/multivariate_rsm.py`: OLS via lstsq, QR/solve para V_X, resíduos,
  estimativa residual bruta e resultado imutável RSMFit com predict.
- `model/uncertainty.py`: covariâncias analíticas plug-in de coeficientes,
  médias, pontos cruzados e diferenças; não contém sampling ou otimização.
- `references/`: notas selecionadas e claims; PDFs ficam fora do Git.
- `data/`: raw autorizado e imutável, metadata/provenance, snapshot real pendente.
- `tests/model/`: fixtures sintéticas e oráculos analíticos independentes.
- `tests/reference_cases/`: expected outputs publicados, sem import pela produção.

Runtime: numpy, scipy, pandas, scikit-learn, openpyxl. A Fase 1 usa somente
NumPy entre as dependências numéricas existentes; não adiciona statsmodels ou
novas dependências. NumPy 2.5.4 conforme lock, Python 3.12, uv_build==0.12.23.
mypy strict preservado; exceção de stubs continua limitada a openpyxl.

[ADR 0003](decisions/0003-multivariate-rsm-and-uncertainty-foundation.md) e
[matemática](mathematics/multivariate_rsm.md) definem convenções e pressupostos.
Não há Monte Carlo, shrinkage, âncoras, payoff, CHIM, PA, Simplex-Lattice,
escolha de H, Pareto, NBI/CNBI ou módulos de otimização.
