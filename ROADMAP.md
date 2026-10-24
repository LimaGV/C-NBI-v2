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

## Posteriormente — sem compromisso metodológico
Experimentos/validação após nova tarefa. Nenhum solver de otimização, seed do
C-NBI, H adaptativo, NBI/CNBI, Monte Carlo, Pareto ou cutoff definido nesta fase.
