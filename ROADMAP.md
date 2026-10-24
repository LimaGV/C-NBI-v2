# Roadmap

## Fase 0 — infraestrutura concluída
PR #1 integrado por squash após árvore limpa, ausência de conflitos e CI verde.
Commit em main: 777a8fd07d6edf901acb46fcec6f97f2a0d1e7a4.
Branch histórica: feature/00-project-foundation.

## Phase 0.5 — Experimental data and scientific reference foundation
Branch: feature/00-5-data-reference-foundation, criada da main atualizada e limpa.
Camadas de dados, templates vazios, hashes, inspeção read-only .xlsx e integridade
bibliográfica. PR #2 integrado por squash na Fase 0.6, após CI verde e autorização.
Nenhum dataset real incorporado ou algoritmo científico implementado.

## Fase 0.6 — Turning reference dataset and published golden reference
Raw real incorporado byte a byte, com autorização de armazenamento no GitHub
privado. Golden reference documental: 80 coeficientes de Table 3 e resumo.
RAW_NOT_SELF_CONTAINED; snapshot pendente de fonte/versão externa validada.
Coding/scaling e divergências físicas ficam explícitos. Nenhum modelo ajustado.
Branch histórica: feature/00-6-turning-reference-dataset. PR #3 integrado por
squash na preparação da Fase 1, após CI verde e ausência de conflito.

## Fase 1 — fundação matemática RSM multivariada
Base quadrática completa, OLS conjunto e univariado equivalente, resíduos/MSE,
covariância residual bruta, covariância dos coeficientes e incerteza analítica
das médias e diferenças. Fontes consultadas antes de implementação;
ADR 0003, derivações e testes sintéticos. Branch feature/01-multivariate-rsm-foundation.
Complemento: CCD literal real ajustado; reprodução parcial de Table 3, 50/80
pela nota literal ou 70/80 sob escala diagnóstica, com desenho nominal rotacional.
WR e divergências de escala/coding continuam pendentes. Não iniciar próxima fase.

## Fase 2 — anchors e payoff, comparação experimental da região de respostas
PR #4 integrado por squash 64b09f9, com checks verdes e autorização explícita.
Branch feature/02-individual-anchors-response-region, ADR 0005 EXPERIMENTAL.
TRS global sobre bola codificada, payoff clássica e restrição de nuvem 8-D,
cutoff legado explícito e multistart determinístico para os casos RC necessários.
Original coded inputs verificados; equivalência ao modelo físico falhou e é
registrada como caso distinto após priorização da planilha pelo responsável.
Nenhum anchor afetado pelos três cutoffs avaliados. Não adotar RC automaticamente.

## Fase 3 — coefficient Monte Carlo conjunto
PR #5 integrado por squash 74d6723 com autorização e CI verde. Mesmo modelo
codificado, covariância residual bruta, matrix-normal plug-in conjunta,
seed PCG64 777 e um ensemble 2000×10×8. Vinte prefixos 100:100:2000,
diagnósticos/figura/manifests. ADR 0006 ACCEPTED neste escopo.
Política futura de early stop da PA PROPOSED, não aplicada.

## Fase 4 — reotimização por réplica e payoff ensemble
PR #6 integrado por squash 3ea6c6e com quatro checks verdes e autorização.
Branch feature/04-monte-carlo-anchor-reoptimization. Ensemble exato da Fase 3,
2000 réplicas × 8 objetivos, solver global quadrático inalterado sobre bola,
certificados independentes e falhas explícitas. Payoffs naturais por réplica,
distribuições dos anchors/ótimos e todos os prefixos 100:100:2000.
ADR 0007 ACCEPTED no escopo solicitado; sem RC ou early stop.

## Fase 5 — centered CHIM / uncertainty-calibrated local PA
PR #7 integrado por squash ccf951a após quatro checks verdes e autorização.
Branch feature/05-chim-svd-local-pa. Payoff nominal sphere da Fase 2 e ensemble
exato da Fase 4; orientação MIN, normalização fixa e CHIM centralizado.
Todos 154 subsets avaliados por q95 espectral da perturbação, sem filtros legados.
Vinte prefixos e validação retrospectiva da política PA original; B=2000 referência.
ADR 0008 ACCEPTED, política de early stop PROPOSED, sem promoção automática.

## Posteriormente — nova tarefa necessária
Decisões sobre H da malha, pesos e NBI exigem escopo/validação próprios após
revisão dos resultados PA e da estabilidade da política. Nada disso foi iniciado;
não há clustering, fronteira Pareto ou métricas de desempenho multiobjetivo.
