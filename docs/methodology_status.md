# Estado metodológico

## Fase10C — escopo atual nesta branch

PR15 integrado por merge47a0e4d,CI40919991675 aprovada Ubuntu/Windows.
Referência independente baseada somente em anchors10A e protocolo congelado.
P_X=conv(anchors),frente contínua distinta da referência discreta5000/célula.
MDR0015;27 referências/135000 pontos,reprodução reversa e27 auditorias finitas
aprovadas. HV power16 ×4,validado no regime das referências,32 oráculos analíticos.
854 testes/98.92% cobertura,51 hashes e1204 arquivos anteriores íntegros.
Fontes/protocolo d982c01 antes da geração. Sem novos RSMs ou métodos.
Escopos abaixo são registros históricos;ver phase_10c_verification.md.

## Fase10B — escopo atual nesta branch

PR14 integrado por merge d68aef7,CI40906784465 aprovada Ubuntu/Windows.
Pipeline CCD/ruído/RSM concluído nesta branch,protocolo próprio MDR0014.
27 entradas congeladas,cinco réplicas,135 instâncias/3555 corridas/990 respostas;
135/135 ajustes sem falha,27 certificados sem ruído,holdout4096/célula e44 hashes.
Fontes/protocolo congelados antes da execução,source final800076f. Evidência em
phase_10b_verification.md. Nenhuma ciência0–10A,licença ou dado original alterado.
Sem otimização multiobjetivo ou benchmark sintético. Escopos abaixo históricos.

## Estado atual consolidado —2026-10-29

Fases0–9 concluídas e integradas: PR11 em39069f3, PR12 embb5d6f2.
H5 standalone409 ND é o único baseline oficial; referência empírica18503,
zeroCNBI. NBI/Simplex-Lattice implementados. Nenhum resultado mudou nesta
consolidação. MIT cobre código original; divulgação dos itens auditados foi
autorizada sem licença CC implícita. Seções anteriores abaixo são históricas,
incluindo gates/408 pontos substituídos, não restrições atuais.
O gate documental foi concluído pelo PR13,main4432e33,CI Ubuntu/Windows verde.

## Fase10A — cenários estruturais nesta branch

27/27 células geradas/calibradas e validadas,uma configuração por célula.
Funções verdadeiras exclusivamente distâncias quadráticas isotrópicas,MIN,
bola alpha=2**(nx/4),nx2/3/5,delta1/3/5,m=nx+1+delta,alvos abs.25/.60/.85.
16.384 pontos de calibração e65.536 de validação independente,8 starts por célula;
erro máximo0.00004520/0.00012444,sem relaxar0.05. Correlação assinada observada,
não controlada. Singularidade é esperada; PSD sem regularização. Nenhum módulo
ou resultado das Fases0–9 foi alterado. Ver MDR0013 e phase_10a_verification.md.
Sem novo benchmark,ruído,CCD,ajuste RSM,MC,PA,C-NBI,VRF-NBI,EAs,referência ou métricas.

## Visualizações científicas do caso aplicado

Pacote bilíngue de apresentação dos resultados congelados no commit d938695,
na branch feature/09-applied-case-visualizations. O baseline continua H5
standalone409 ND; referência independente18503/zeroCNBI. Nenhum pipeline
científico é reexecutado. PCA, elipses MC, avaliação de malha de desenho e
agregações de exibição são transformações visuais explícitas, sem alterar
modelos, covariâncias, PA, subsets, frentes, métricas ou resultados anteriores.
Os eixos não usam grades; referências científicas são descritas nas captions.
Ver docs/figures/applied_case_visualization_report.md e a verificação do pacote.

## Fase 8 — correção standalone concluída e integrada pelo PR11

Baseline oficial: standalone H5,492 aceitos/zero falhas/411 únicos/409 ND.
H2/H4/H5/H10/H20 são execuções independentes,sem malha-mãe para avaliação final.
Cinco repetições H5 bitwise idênticas; T_total mediana1.313828s,IQR.0130341s;
T_solver mediana1.237155s. Outros H têm uma observação de runtime cada.
Os antigos408 pontos e arquivos Fase6/7/8 parent-grid são históricos imutáveis,
nomeados CNBI_H5_extracted_from_H20_parent_grid / historical_parent_grid_analysis.
A decisão preserve408/custo pendente foi SUPERSEDED pelo pedido explícito.

37 subsets,modelos,normalizações,SLSQP/Jacobianos/starts/aceitação mantidos.
Pipeline H5 funcionou com todos os resultados Fase6/7 fisicamente indisponíveis.
Reavaliadas cinco métricas,nativo/K66/curvasK e GD/IGD contra512 referências já
salvas. Alvo independente18503/zeroCNBI,subamostras/FPS da referência e resultados
EA/VRF/timing EA permanecem idênticos. Alvo comum antigo é somente histórico,
sem alegar auto-inclusão do novo H5. Nenhum refit,MC,PA,anchor,subset novo ou VRF/EA.

GD/IGD independentes H5=.0394917342/.1411437315,HV=.7390285251.
Resolução/tempo standalone agora podem ser analisados; qualidade e custo são
pareados por execução. Sem vencedor universal,saturação certificada ou frente
verdadeira. ADR0012 ACCEPTED conforme definição explícita do responsável;
C-BENCH-06/07 documentam baseline direto e independência dos demais H.
Ver [relatório](mathematics/turning_final_benchmark.md) e
[verificação](phase_8_verification.md). Sem merge/refinamento automático.

## Histórico da Fase 7 — referência empírica multi-família e family LOO

Fase7 concluída no escopo solicitado, após squash do PR9 em main b94be85.
Baseline operacional definido pelo responsável: H5 (492 subproblemas,411 decisões
únicas,408 ND); H20 preservado como resolução fina auxiliar da mesma família CNBI.
Essa decisão atualiza a recomendação operacional, sem alterar a Fase6 abaixo.
RSMs nominais codificados, esfera alpha=8**.25, direções e normalização global
fixa da Fase5 consumidos sem alteração. Nenhum MC/anchors/PA/NBI real reexecutado.

Calibração aplicada V1 transferida por autorização explícita; pymoo0.6.2 pinado.
30 seeds1001..1030 por EA,132000 NFE de busca/run,7920000 no total. Pools ND:
NSGA3=8754,MOEAD=9743,CNBI20=4417,VRF histórico reavaliado=66. VRF tem decisões
verificadas; respostas antigas não são entradas canônicas. P_all=22523 ND.
LOO reconstruído com exclusão prévia de toda a família, deduplicação numérica e
ND; P_minus_CNBI=18503 ND, zero origens CNBI. H5 não contribui ao envelope comum.
30 runs não certificam saturação; alvos LOO distintos não definem ranking.
Métricas comuns self-included e sanity H5 independentes estão separadas.

ADR0011 ACCEPTED, C-REF-01..04 como definições/decisões; sem verdade Pareto,
superioridade ou benchmark final. Refinamento adaptativo H5→H20 e HV futuros.
Ver [resultados e limites](mathematics/turning_pareto_reference.md),
[definição](mathematics/pareto_reference_leave_one_out.md),
[verificação](phase_7_verification.md). Estados abaixo são históricos.

## Fase 6 — local NBI e sensibilidade interna de H

Autorizada após squash do PR #8 com CI verde (main1053f29).37 IDs de B2000
preservados:19 pares+18 trios+0 quartetos. NBI nominal codificado na bola
alpha=8**.25, sem RC; normalização local por subset, normal unitária orientada
à origem ideal, igualdade, Jacobianos analíticos e SLSQP com aceitação independente.
Malha-mãe20, membership inteiro para H2,4,5,10,20; reavaliar8 respostas antes
de ND e cobertura interna na normalização global fixa. ADR0010 ACCEPTED nesse
escopo, C-NBI-01/02/03/04. Nenhum H final aceito ou benchmark externo.
Execução concluída:4557/4557 aceitos, zero falhas finais e duas tentativas iniciais
resolvidas por retry. H20 tem4476 decisões únicas e4417 ND full-space; H10 tem
q95 de cobertura interna0.0979495. H20 segue referência interna recomendada,
sem H final aceito. Ver [relatório](mathematics/turning_local_nbi_h_sensitivity.md).
As seções seguintes preservam os estados históricos; nenhuma nova PA/MC/anchors.

## Fase 5 — revisão exclusiva da política de early stop no PR #8

Política v1 preservada byte-identical em docs/policies/history/; resultados
anteriores imutáveis. V2 PROPOSED_REVISED: gap q95 adjacente normalizado,
tolerância estrita0.05 (cinco pontos percentuais), janela de três checkpoints
elegíveis, primeira500/600/700, dimensão e IDs exatos. Monitores: todos os gaps
globais e trios/quartetos selecionados de forma estável; nenhum gap de pares.
Definida post hoc após a primeira trajetória; não é validação externa da regra.
ADR 0009 PROPOSED; claims C-PA-05/06/07 delimitadas como decisão/definições.
Aplicação aos espectros salvos: stop1300, dimensão2 e os mesmos37 IDs até2000;
potencial redução de35% das réplicas. B=2000 continua a referência científica
com19 pares+18 trios+0 quartetos. Não houve alteração de PASS/FAIL, normalização
ou geometria; análise sem novos draws, otimização ou SVD. Sem nova fase ou merge.
As seções seguintes preservam a execução original e fases anteriores.

## Fase 5 — geometria CHIM e screening espectral local

PR #7 integrado por squash ccf951a com CI verde, main atualizada e limpa.
Nominal sphere-only da Fase 2 e ensemble exato da Fase 4, sem novos draws/anchors.
Orientação MIN, normalização nominal fixa e geometria Z[C,C] H_k. Ruído definido
por Delta[C,C] H_k, sem centralização adicional entre réplicas ou clipping.
PA-inspired uncertainty screening q95 linear, comparação estrita, todos k-1
componentes para seleção local e passes líderes para dimensão global.
Todos 28/56/70 candidatos avaliados, sem gate global, qmax, volume ou filtros
de deslocamento/erros do sampler. Vinte prefixos e B=2000 referência científica.
Política original de early stop avaliada retrospectivamente, mantida PROPOSED.
Ver [matemática](mathematics/chim_parallel_analysis.md),
[caso real](mathematics/turning_chim_pa.md), [gate](phase_5_verification.md).
ADR 0008 ACCEPTED; C-PA-01/02/03/04. Sem equivalência alegada à PA clássica de Horn.
Sem H da malha, pesos, NBI/C-NBI, clustering ou métricas Pareto; próxima fase não iniciada.
As seções seguintes são históricas e preservam o escopo de cada fase anterior.

## Fase 4 — propagação aos anchors e payoff matrices

PR #6 integrado por squash 3ea6c6e após CI verde e ausência de conflitos.
Consumo do ensemble congelado da Fase 3, sem novos draws, mudança de seed,
Sigma_e ou OLS. Cada objetivo é reotimizado em cada réplica na bola codificada
alpha=8**0.25, com o solver global e tolerâncias da Fase 2 preservados.
Payoff própria por réplica, nas escalas naturais, com identidade diagonal.
Certificados independentes, falhas com índices/máscaras e nenhum substituto.
Resumos descritivos de deslocamento/ótimos e 20 prefixos; sem early stop.
Ver [formulação](mathematics/anchor_monte_carlo.md),
[relatório aplicado](mathematics/turning_anchor_mc.md),
[gate](phase_4_verification.md). ADR 0007 ACCEPTED; C-MC-04/05/06 registradas.
RC permanece EXPERIMENTAL/ABLATION ONLY, sem aplicação neste pipeline.
Não há normalização, CHIM, edge/SVD/PA, subconjuntos, NBI/C-NBI ou início da Fase 5.
As seções seguintes são históricas e descrevem o escopo de cada fase anterior.

## Fase 3 — propagação conjunta plug-in de coeficientes

PR #5 integrado por squash 74d6723 após CI verde e ausência de conflitos.
Mesmo ajuste codificado original da Fase 2: B_hat, R/V_X e Sigma_e=E'E/9,
sem misturar modelos físicos ou publicados. Sampler matrix-normal conjunto,
seed 777 via Generator(PCG64), resultado imutável e reprodutibilidade de prefixos/lotes.
Um ensemble 2000×10×8 e 20 prefixos 100:100:2000 em validation/sensitivity mode.
Derivação e [API](mathematics/coefficient_monte_carlo.md),
[relatório aplicado](mathematics/turning_coefficient_mc.md),
[gate](phase_3_verification.md). ADR 0006 ACCEPTED no escopo solicitado.
Política futura de early stop PA PROPOSED, sem aplicação nesta fase;
erros de momentos não selecionam B. C-MC-01/02/03 delimitam a evidência.
RSM, dados integrais e anchors anteriores preservados. Sem reotimização, payoff
por réplica, shrinkage, bootstrap, CHIM, NBI/C-NBI, PA ou início da Fase 4.
As seções seguintes são registros históricos de suas respectivas fases.

## Fase 2 — comparação experimental de anchors nominais

PR #4 integrado por squash após todos os checks verdes; main limpa, branch
feature/02-individual-anchors-response-region. ADR 0005 EXPERIMENTAL.
Implementados anchors clássicos quadráticos sobre bola codificada e payoff,
mais região 8-D de respostas observadas e anchors RC por multistart SLSQP,
com atalho exato quando o anchor clássico global já é admissível.

Codificação original verificada em NBI Revisão.xlsm!Original Data!C4:E22,
axiais +/-1.682. Fonte prioritária por clarificação explícita do responsável.
O gate de equivalência física/codificada FALHOU; o caso codificado é distinto,
sem inventar decodificação contínua nem coordenadas físicas dos novos anchors.
Respostas canônicas e resultados anteriores permanecem intactos.

Na formulação cloud escolhida: phi=mean(Y), S_Y=cov(Y,ddof=1), posto 8.
Cutoff chi-square_8(.95) é legado/EXPERIMENTAL, não confiança exata.
Os oito anchors estão dentro; ambas as payoffs coincidem e não há deslocamento
ou custo de objetivo. Quantil empírico .95 e chi-square .99 também não alteram
os anchors. Recomendação: manter RC como ablação/candidato experimental, sem
torná-lo obrigatório; C-RC-02 continua UNVERIFIED.
O Utopia diagonal permanece fora da região descritiva (D²≈70560.14), embora
os oito anchors estejam dentro. Restringir anchors individualmente não garante
admissibilidade da diagonal; C-RC-04 registra a não implicação e contraexemplo.

Ver [anchors](mathematics/individual_anchors.md),
[região](mathematics/multivariate_response_region.md),
[fontes](../references/notes/phase_02_sources.md) e
[relatório aplicado](mathematics/turning_individual_anchors.md).
Nenhum NBI/C-NBI, CHIM, Monte Carlo, PA, seleção de subconjuntos ou shrinkage.

## Fechamento da Fase 1 — qualidade e capacidade preditiva

Implementados diagnósticos por resposta: SS, R²/R²_adj, MSE/S,
leverages de treino, PRESS analítico/R²_pred, ANOVA global e pure error/LOF.
Oráculos manuais, equivalência PRESS/LOOCV por refits e estados degenerados
estão testados; derivação e fontes verificadas em
[rsm_diagnostics.md](mathematics/rsm_diagnostics.md). ADR 0003 estendida;
claims C-RSM-07 a 11 SUPPORTED nos pressupostos documentados.

Os quatro ajustes anteriores são preservados, com a mesma Y integral e dez
termos. Tabela principal em coordenadas físicas e comparação nominal condicional
estão no [relatório aplicado](mathematics/turning_rsm_diagnostics.md).
Foram detectadas 15 configurações e cinco corridas centrais idênticas (Exp 15-19),
df_PE=4, df_LOF=5. A 5%, testes individuais indicam significância global das oito
respostas e falta de ajuste em sete; WR não rejeita LOF nesse limiar.
Não há declaração de adequação global só por R² elevado.

Table 3 é secundária: método de R²_pred não especificado por PRESS/LOOCV;
Ra/Rt divergem fortemente nesse indicador. WR e notas ROI/OEE continuam
inconsistências de referência/publicação, sem alterações experimentais.
WR arredondado é PUBLICATION_RECONCILIATION_NOTE, fora do pipeline oficial.
Fase 1 concluída no escopo autorizado; nenhuma otimização ou fase seguinte
iniciada. O PR #4 permanece para revisão, sem merge automático.

## Complemento aplicado — CCD literal ajustado
O usuário forneceu revisão atualizada, com 19×11 entradas numéricas reais,
sem fórmulas/dependências externas detectadas. O novo raw foi preservado e os
oito modelos ajustados com a precisão integral das células; rank=10, nu=9.
Relatório: [validação real](mathematics/turning_real_validation.md), ADR 0004 EXPERIMENTAL.
Com desenho nominal rotacional: 50/80 pela nota literal de escala e 70/80 sob
escala diagnóstica 10^-3, em conflito com a nota impressa 10^-2.
WR diverge em 10/10 com precisão integral. Arredondar uma cópia de WR a três
casas explica os coeficientes publicados, mas é diagnóstico a posteriori,
excluído dos ajustes reais. C011 é PARTIALLY_SUPPORTED, sem validação integral.
O raw histórico continua não autocontido; não foi sobrescrito nem ajustado.
Nenhum Monte Carlo, shrinkage ou otimização foi iniciado.

## Fase 1 — fundação RSM e incerteza analítica

Primeira implementação científica: base quadrática completa, OLS multivariado,
equivalência com OLS univariado, resíduos/MSE, Sigma_hat_e, V_X por QR/solve,
covariâncias dos coeficientes e das médias preditas, cruzadas e de diferenças.
Aceitação do escopo por solicitação explícita na ADR 0003. Validação algébrica
e sintética, sem comprovação de adequação ao dataset real ou validação empírica
do restante do C-NBI. Ver [matemática](mathematics/multivariate_rsm.md),
[incerteza](mathematics/rsm_uncertainty.md) e [claims](../references/notes/claims_matrix.md).

Covariância dos coeficientes usa vec de B_hat por colunas: Sigma_hat_e⊗V_X.
Incerteza da média é h Sigma_hat_e, sem adicionar erro de observação.
Diferenças usam o contraste z_a-z_b e preservam covariâncias cruzadas.
Não há sampling, Monte Carlo, shrinkage ou otimização; NBI/CNBI não implementados.
A próxima fase exige nova solicitação.

## Fase 0.6 — evidência experimental e golden reference preservadas
PR #3 integrado por squash na preparação da Fase 1, com CI verde e sem conflito.
Dataset turning_application_ccd_19run incorporado como RAW_NOT_SELF_CONTAINED:
19 corridas, três fatores, oito respostas e 152 fórmulas externas.
SNAPSHOT_PENDING_EXTERNAL_SOURCE: caches existem, mas não foram certificados.
Golden reference da Table 3 criada com 80 valores, fonte FULLTEXT_VERIFIED.
CODING_SCHEME_PENDING_VERIFICATION; interpretação de escalas permanece pendente.
Na Fase 0.6, reprodução numérica ficou PROPOSED/UNVERIFIED; o complemento
aplicado acima registra a evidência posterior. Não houve reconstrução de dados.
Ver data/metadata/turning_application/ e
tests/reference_cases/turning_8responses/; nenhuma resposta foi reconstruída.

Dimensões estruturais: n=19,n_x=3,m=8,p=10; nu=9 se rank(X)=10.
B:10×8; Sigma_hat_e:8×8. Isso não decide adoção futura de shrinkage.

## Propostas posteriores
C001 agora tem suporte analítico delimitado por C-RSM-01 a 06.
Isso não aceita automaticamente propostas de sampling/otimização.

| ID | Contexto/proposta | Categoria | Status |
| --- | --- | --- | --- |
| C002 | Coeficientes serão perturbados conjuntamente | PROPOSED | UNVERIFIED |
| C003 | Âncoras deverão ser reotimizadas a cada réplica | PROPOSED | UNVERIFIED |
| C004 | PA local está em estudo | PROPOSED | UNVERIFIED |
| C005 | q_C não deve virar automaticamente hard cutoff | PROPOSED | UNVERIFIED |
| C006 | B=2000 não é constante normativa | PROPOSED | UNVERIFIED |
| C007 | Simplex-Lattice com H inteiro e Delta=1/H | PROPOSED | UNVERIFIED |
| C008 | Regra adaptativa para H ainda não definida | PROPOSED | UNVERIFIED |

A proteção contra decisões implícitas já é regra de governança. As hipóteses
acima continuam sem validação científica; ver references/notes/claims_matrix.md.
