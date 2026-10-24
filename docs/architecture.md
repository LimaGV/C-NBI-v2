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
- `optimization/quadratic.py`: extração única de coeficientes para quadráticas,
  exposta para arrays e compartilhada pelo antigo caminho RSMFit.
- `uncertainty/anchor_reoptimization.py`: usa extração e solve_quadratic_ball
  existentes em cada réplica, verifica certificados e constrói payoff natural;
  resultado imutável com máscaras, casos e falhas identificadas, sem RNG/RC.
- `scripts/validation/turning_anchor_mc.py`: verifica o NPZ/metadata da Fase 3,
  carrega nominal da Fase 2 apenas como referência, executa e arquiva o ensemble,
  resumos completos e prefixos; bloqueia resumos em caso de falha.
- `scripts/validation/turning_coefficient_mc.py`: carrega o caso codificado
  verificado da Fase 2, ajusta uma vez pelo fitter existente e arquiva um ensemble.
  Importar o loader não executa o fluxo de anchors; sentinelas testam esse limite.
- `references/`: notas selecionadas e claims; PDFs ficam fora do Git.
- `chim/normalization.py`: orientação comum, Utopia/amplitudes fixas nominais,
  validação de ótimo/amplitude, Z/Delta imutáveis sem clipping.
- `chim/geometry.py`: centralização H_k, SVD e diferença de vértices como diagnóstico de rank.
- `chim/parallel_analysis.py`: candidatos programáticos, espectros da perturbação,
  quantis q95 por prefixo, seleção local completa e dimensão global com flags.
- `chim/early_stop.py`: conserva o avaliador histórico v1, compara identidades e
  todos os quantis, avalia retrospectivamente sem truncar a trajetória.
- `chim/spectral_gap_stop.py`: gaps adjacentes q95 e política v2 proposta;
  janelas de três checkpoints, IDs exatos, mesmas transições/monitores e
  validação de decisões posteriores. Sem dependência de SVD ou optimizer.
- `scripts/validation/turning_spectral_gap_stop.py`: lê apenas os espectros
  arquivados da Fase 5, recalcula quantis, verifica decisões históricas,
  produz gaps/política/figura; mantém o arquivo original imutável.
- `scripts/validation/turning_chim_pa.py`: valida os artefatos congelados,
  executa screening determinístico, exporta thresholds/decisões/spectra/hashes.
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
ACCEPTED acrescenta propagação conjunta de coeficientes e sensibilidade.
ADR 0007 ACCEPTED acrescenta reotimização por réplica e payoff natural, sem
alterar o solver global ou adicionar dependências. ADR 0008 ACCEPTED acrescenta
CHIM centralizado e screening espectral PA inspirado, sem alterar módulos anteriores.
A política original é avaliada retrospectivamente e permanece PROPOSED.
A revisão v2 é PROPOSED_REVISED, post hoc no caso real, ADR 0009 PROPOSED;
somente a análise de stopping muda. Os runners históricos usam a v1 arquivada.
Sem shrinkage, Simplex-Lattice, escolha de H da malha, Pareto ou NBI/CNBI.

## Phase 6 — local NBI and internal resolution sensitivity

simplex/lattice.py generates immutable lexicographic weak compositions, beta
and exact integer parent membership. nbi/geometry.py constructs a local nominal
normalization and unique unit ideal-oriented left-null normal. nbi/solver.py
provides analytic equality/sphere derivatives, SLSQP options, independently
checked trials, deterministic retries and nearest-weight continuation.
nbi/sensitivity.py preserves decision-origin mappings, roundoff-only equality,
full-space nondominance and blocked Euclidean directed distances.

scripts/validation/turning_local_nbi.py pins the37 B=2000 identities, nominal
coded model/anchor/payoff and Phase5 global normalization hashes. It solves the
H20 parent once per subset, re-evaluates all8 responses before diagnostics and
exports one parent NPZ plus membership/provenance, attempt logs and H summaries.
No fitter, anchor optimizer, PA or Monte Carlo dependency is executed by this
workflow. The existing shared quadratic evaluators and normalization helpers
are consumed unchanged. No new dependency or parallelism; strict mypy retained.
