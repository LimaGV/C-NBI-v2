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
- `model/diagnostics.py`: SS/R²/S, PRESS, ANOVA e pure error/LOF por resposta.
- `optimization/quadratic.py`: f=beta0+b'x+x'Qx, direções explícitas e arrays imutáveis.
- `optimization/trust_region.py`: solução global sobre bola com certificado KKT/PSD.
- `optimization/response_region.py`: nuvem observada, Mahalanobis por Cholesky,
  cutoff legado experimental, sem confundir S_Y com Sigma_e/h*Sigma_e.
- `optimization/anchors.py`: RC multistart, margens verificadas, atalho global
  para anchor clássico já admissível e payoff orientada respostas×anchors.
- `scripts/validation/turning_anchors.py`: extração de códigos originais por opção
  explícita, execução nominal e artefatos separados; não depende de PDFs ou v1.
- `uncertainty/coefficient_sampling.py`: matrix-normal conjunta plug-in,
  QR/solve e Cholesky/PSD, Generator(PCG64), arrays imutáveis e streaming de lotes.
- `uncertainty/mc_sensitivity.py`: prefixos e erros agregados de momentos,
  sem early stop ou dependência de optimization/.
- `scripts/validation/turning_coefficient_mc.py`: carrega o caso codificado
  verificado da Fase 2, ajusta uma vez pelo fitter existente e arquiva um ensemble.
  Importar o loader não executa o fluxo de anchors; sentinelas testam esse limite.
- `references/`: notas selecionadas e claims; PDFs ficam fora do Git.
- `data/`: raw autorizado e imutável, metadata/provenance, snapshot real pendente.
- `tests/model/`: fixtures sintéticas e oráculos analíticos independentes.
- `tests/reference_cases/`: expected outputs publicados, sem import pela produção.

Runtime: numpy, scipy, pandas, scikit-learn, openpyxl. RSM usa NumPy e os
diagnósticos/otimização usam SciPy já disponível; não adiciona statsmodels ou
novas dependências de runtime. Fase 3 adiciona Matplotlib apenas a dev para o PNG
solicitado, sem pyplot/GUI. NumPy 2.5.4 conforme lock, Python 3.12, uv_build==0.12.23.
mypy strict preservado; exceção global de stubs para openpyxl e ignores locais
de import-untyped nas APIs SciPy utilizadas.

[ADR 0003](decisions/0003-multivariate-rsm-and-uncertainty-foundation.md) e
[matemática](mathematics/multivariate_rsm.md) definem convenções e pressupostos.
ADR 0005 EXPERIMENTAL acrescenta anchors nominais e duas payoffs; ADR 0006
ACCEPTED acrescenta somente propagação conjunta de coeficientes e sensibilidade.
Não há reotimização por réplica, shrinkage, CHIM, PA, Simplex-Lattice, escolha de H,
Pareto ou NBI/CNBI. A futura política PA é especificação PROPOSED, sem execução.
