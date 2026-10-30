# Roadmap

## Fase 10E — correção pareada autorizada em 2026-10-30

Equalização atual em três pares C-NBI/comparador, K independente por bloco,
na ordem VRF-NBI, NSGA-III, MOEA/D. Resultados globais anteriores são preservados
e substituídos somente para a conclusão equalizada vigente. Ver MDR0018,
docs/phase_10e_pairwise_verification.md e pairwise_20261030. Sem novas buscas,
ajustes, referências ou merge. PR18 continua dependente do PR17 aberto.

## Histórico da Fase 10E inicial — análise offline autorizada em 2026-10-30

Branch feature/10e-synthetic-statistical-analysis empilhada sobre a branch do PR17,
que permanece aberto e não é integrado automaticamente. Campanha oficial intacta.
Concluídas inferência pareada por 27 cenários (HV válido em 26), equalização FPS,
sensibilidade de viabilidade e estudo suplementar dos dois HV pendentes.
Vantagem nativa do C-NBI não é invariante à cardinalidade. Resultados completos,
limitações e qualidade: docs/phase_10e_verification.md e MDR0017 EXPERIMENTAL.
Nenhuma fase posterior ou nova busca de otimização autorizada por esta entrega.
As seções abaixo registram o escopo histórico de cada etapa.

## Fase10D — escopo histórico autorizado

PR16 integrado em c0646768, CI Ubuntu/Windows aprovada. Branch
feature/10d-synthetic-algorithm-benchmark e PR17. Piloto corrigido12/12 PASS;
540 execuções e avaliações concluídas,135 por método, com barreiras na ordem
C-NBI, VRF-NBI, NSGA-III e MOEA/D; zero falhas de execução. Auditoria540/135
blocos/1262 arquivos aprovada. Documentação e evidência de qualidade no relatório.
Não iniciar10E, inferência, retuning ou equalização.
Resultados e limites: docs/phase_10d_verification.md. Escopos abaixo históricos.

## Fase10C — escopo atual autorizado

PR15 integrado em47a0e4d,CI main40919991675 verde Ubuntu/Windows.
Concluídas nesta branch27 referências analíticas independentes ×5000 pontos,
normalização fixa,sensibilidade2500/5000/10000 e protocolo das cinco métricas.
MDR0015,sem executar métodos ou iniciar10D;PR próprio sem merge automático.

## Fase10B — escopo atual autorizado

Fase10A integrada por merge d68aef7,CI40906784465 verde em Ubuntu/Windows.
Concluídas nesta branch135 instâncias RSM sintéticas,com CCD/ruído e validação
independente,sem iniciar otimização multiobjetivo. MDR0014;novo PR sem merge.
As seções anteriores abaixo registram o escopo vigente em cada etapa histórica.

## Estado consolidado em2026-10-29

Fases0–9 concluídas e integradas. PR11:39069f3; PR12:bb5d6f2.
H5 standalone409 ND; referência empírica18503/zeroCNBI. NBI implementado desde
a Fase6;408 pontos são análise histórica. Fase10A autorizada para27 configurações
estruturais em PR separado após o gate documental. Ruído,CCD,RSM e benchmark
sintético completo são posteriores. Seções antigas registram a evolução,
não anulam autorizações posteriores ou representam o estado atual.

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
Revisão antes do merge do PR #8: política v2 PROPOSED_REVISED com gaps q95
normalizados, janela3 e tolerância estrita0.05. ADR 0009 PROPOSED, definição
post hoc; stop1300 retrospectivamente estável até2000. PA e37 IDs preservados.

## Gate histórico antes da autorização da Fase6
A autorização original da Fase5 reservava H/pesos/NBI a uma tarefa posterior.
A tarefa explícita da Fase6 abaixo delimita esse novo escopo; os resultados
e critérios estatísticos anteriores permanecem preservados.

## Fase 6 — local NBI / Simplex-Lattice and internal H sensitivity

PR #8 integrated by authorized squash1053f297ad9263d3219532c14f7dfc19fb42c29a,
with four green checks and clean tree. Branch feature/06-simplex-lattice-local-nbi.
Implement the37 frozen B2000 subsets and original nominal coded RSMs on the
unchanged ball, local payoff normalization and ideal-oriented unit CHIM normal.
Analytic-Jacobian SLSQP, independent acceptance and deterministic continuation;
H2,4,5,10,20 are exact memberships of H20. Full8-response ND and internal
coverage only support H sensitivity. ADR0010 ACCEPTED; no final H automatically
accepted, no external front/benchmark, new PA/MC/anchors or automatic next phase.

Resultado real:4557/4557 subproblemas aceitos, sem falhas finais. H20 produz4417
pontos ND full-space e permanece referência interna, sem H final aceito.

## Gate histórico ao término da Fase6 — posteriormente superado

Escolha definitiva de H e validação/comparações externas exigem autorização,
critérios e evidência próprios. Era pendente naquela etapa; Fases7–9 foram
autorizadas e concluídas posteriormente.

## Fase7 — referência empírica aplicada, concluída

PR10 integrado em f904e8d.30 runs por EA,VRF-NBI e análise por família.
O baseline408 então disponível foi substituído pelo standalone409 da Fase8.

## Fase8 — benchmark final aplicado, concluída e integrada

PR11 integrado em39069f3. H5 standalone, análise de H2/4/5/10/20, referência
independente, métricas nativas, cardinalidade, custo e sensibilidade da referência.
Dados/algoritmos anteriores e arquivos históricos preservados.

## Fase9 — visualizações científicas, concluída e integrada

PR12 integrado embb5d6f2.46 entradas,21 principais/25 suplementares,PT/EN,
PNG600dpi/PDF vetorial/SVG disponível,galeria,captions,auditoria/checksums.
Nenhuma mudança científica. Próxima etapa autorizada: apenas Fase10A estrutural.

## Fase10A — geração estrutural implementada e validada nesta branch

27 células,uma configuração de âncoras por célula,funções isotrópicas verdadeiras,
calibração e validação Sobol independentes.27/27 aprovadas dentro de0.05,sem
seleção por sinal ou holdout. Matrizes completas/diagnósticos/hashes preservados.
Ver docs/phase_10a_verification.md. Entrega em PR próprio; não integrado automaticamente.
Ruído,CCD,RSM,CHIM/PA sintética,algoritmos,referência e métricas de benchmark
não pertencem à Fase10A e ainda não foram executados.
