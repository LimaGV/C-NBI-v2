# Changelog

## Unreleased — revisão proposta da política de early stop da Fase 5
- V1 preservada com hash original; política v2 PROPOSED_REVISED, explicitamente post hoc.
- Gaps adjacentes normalizados do q95, tolerância operacional estrita0.05 e janela3.
- Monitores globais e locais selecionados estáveis, identidades completas e retrospectiva.
- Reuso exclusivo dos espectros salvos; nenhum threshold, PASS/FAIL ou ID anterior muda.
- Stop retrospectivo1300; mesma decisão até2000, redução potencial35% de réplicas.
- ADR 0009 PROPOSED, C-PA-05/06/07 e validação externa futura necessária.
- Sem MC/anchors/payoffs/normalização/CHIM/SVD novos na análise, H, NBI/C-NBI ou merge.

## Unreleased — Fase 5 centered CHIM / local PA
- Orientação MIN e normalização fixa definida somente pela payoff sphere nominal.
- Geometria Z[C,C] H_k e SVD da perturbação Monte Carlo; arrays naturais preservados.
- Avaliação de todos 28 pares, 56 trios e 70 quartetos, seleção estrita por todos k-1 componentes.
- Quantis q95 linear, dimensão global por passes líderes e padrões não monotônicos explícitos.
- Vinte prefixos, trajetória de todos 357 quantis e avaliação retrospectiva da política original.
- B=2000 referência científica; política de early stop permanece PROPOSED, sem promoção automática.
- ADR 0008, claims C-PA-01/02/03/04 e fontes verificadas com cobertura delimitada.
- Sem novos draws, reotimização, clipping, RC, qmax/volume filter, H da malha ou NBI/C-NBI.

## Unreleased — Fase 4 anchor/payoff Monte Carlo
- Consumo rastreável do ensemble exato da Fase 3, sem novos draws ou ajustes.
- Reotimização por réplica/resposta com solver global sobre bola inalterado.
- Extração coeficientes → quadráticas compartilhada com o caminho nominal.
- Certificados independentes, índices/máscaras imutáveis e logs sem substituição em falha.
- Ensembles de anchors/valores ótimos/payoffs naturais e diagnósticos dos 20 prefixos.
- ADR 0007 ACCEPTED e claims C-MC-04/05/06, com política PA ainda PROPOSED e não aplicada.
- Sem RC, normalização, shrinkage, CHIM/SVD/PA, subsets ou NBI/C-NBI; dependências preservadas.

## Unreleased — Fase 3 coefficient Monte Carlo
- Sampler matrix-normal plug-in conjunto, Sigma_e bruta, QR/solve e Cholesky/PSD explícito.
- Resultado imutável, seed PCG64 explícita, igualdade de prefixos e chunks testada.
- Ensemble real único 2000×10×8, seed 777, 20 diagnósticos de momentos e figura PNG.
- Metadata, hashes de objetos/inputs/artefatos, ADR 0006 e claims C-MC-01 a 03.
- Política futura de early stop da PA PROPOSED, registrada e não aplicada.
- Matplotlib no grupo dev para a figura solicitada; runtime sem dependência nova.
- Sem reotimizar anchors, payoff por réplica, shrinkage, bootstrap ou NBI/C-NBI/PA.

## Unreleased — Fase 2 experimental
- Quadráticas naturais com b/Q e extração correta de interações beta_ij/2.
- Solver global do problema quadrático sobre bola, com caso singular e certificado KKT/PSD.
- Região 8-D da nuvem de respostas observadas, Cholesky e cutoff legado explícito.
- Anchors RC por multistart determinístico e verificação independente de margens;
  reutilização exata do anchor global clássico quando já admissível.
- Duas payoff matrices separadas, Utopia diagonal, comparação e sensibilidade de cutoff.
- Códigos originais literais extraídos com proveniência; gate de equivalência física
  falhou, registrado como caso distinto após priorização da planilha pelo responsável.
- ADR 0005 EXPERIMENTAL e claims/fontes delimitadas; nenhuma adoção definitiva de RC.
- Sem Monte Carlo, NBI/C-NBI ou fase posterior.

## Unreleased — fechamento científico da Fase 1
- Diagnósticos imutáveis por resposta: SS, R²/ajustado, S, PRESS/LOOCV,
  R² predito, ANOVA global, pure error e lack of fit com estados indefinidos.
- Inputs originais float64 preservados no ajuste para integridade e alinhamento.
- Oráculos manuais, refits leave-one-out, replicação exata e invariância de escala.
- Relatório e artefatos rastreáveis dos quatro ajustes reais já registrados;
  Table 3 secundária, método R²_pred não especificado e divergências preservadas.
- ADR 0003 e claims C-RSM-07 a 11 com fontes diretamente verificadas.
- WR arredondado classificado PUBLICATION_RECONCILIATION_NOTE, fora do pipeline.
- Dados integrais e todos os termos mantidos; sem otimização ou NBI/CNBI.

## Unreleased — validação aplicada da Fase 1
- Nova revisão literal e autocontida do CCD, preservada junto ao raw histórico.
- Extração dos tokens numéricos completos, oito RSMs reais e comparação dos
  80 coeficientes sob quatro desenhos explícitos e duas escalas de apresentação.
- Reprodução parcial: 50/80 pela nota literal; 70/80 sob escala diagnóstica,
  ambos com desenho nominal rotacional. WR completo diverge nos dez termos.
- Diagnóstico opcional de pré-arredondamento de WR reproduz 10/10, mas altera
  19 observações da cópia e fica excluído dos modelos/validação reais.
- Sem alteração da implementação matemática RSM ou dos coeficientes publicados.

## Unreleased — Fase 1 (fundação científica)
- Base quadrática canônica e OLS multivariado estável, com equivalência univariada.
- Resíduos, MSE, covariância residual bruta e fator V_X por QR/solve.
- Covariância dos coeficientes por vec de colunas; leverage, covariância da média,
  covariância cruzada e de diferenças com coeficientes compartilhados.
- Resultado imutável, validação de posto/df/inputs e diagnóstico de simetria/PSD.
- Derivações, fontes verificadas, claims C-RSM-01 a 06, ADR 0003 e testes analíticos.
- Cobertura em CI com mínimo 96.15%, preservando a cobertura medida antes da fase.
- Sem ajuste do dataset real, sampling, shrinkage, otimização ou NBI/CNBI.

## Unreleased — Fase 0.6 (dados e referências)
- Turning reference dataset infrastructure: cópia raw byte-identical do CCD.xlsx,
  autorizada pelo usuário no repositório privado, com inspeção e proveniência.
- Published golden reference: 80 coeficientes e resumo secundário da Table 3,
  extraídos do PDF local verificado, ligados ao Zotero SMMX47JT.
- Metadata/provenance: links externos, caches não certificados, snapshot pendente,
  coding/scaling e divergências de níveis físicos documentados sem reconciliação.
- Correção de portabilidade JSON: escape Unicode preserva texto mesmo em stdout
  ASCII/Windows cp1252; teste de regressão com caracteres não ASCII.
- Nenhum método científico alterado ou algoritmo RSM/OLS/CNBI/NBI implementado.

## Unreleased — Fase 0.5 (infraestrutura)
- Camadas de dados, templates de metadados e dicionário de variáveis.
- SHA-256 e inspeção somente leitura de .xlsx, sem recálculo ou transformação.
- openpyxl: única dependência direta nova, necessária para ler células, fórmulas
  e estrutura de workbooks; não é motor de cálculo ou método científico.
- Políticas de raw imutável, snapshots, publicação seletiva e documentos locais.
- Templates bibliográficos completos e distinção de derivação matemática.
- Nenhuma alteração metodológica ou incorporação de dataset real.

## 0.1.0.dev0 — não lançado
- Base independente com Python 3.12, uv e pacote cnbi_v2.
- Governança, ADR/MDR, rastreabilidade, referências e políticas de dados.
- Testes de infraestrutura, Ruff, mypy e CI Windows/Ubuntu.
- Inventário distingue estado informado, exposição e teste real de MCPs.
- Nenhum algoritmo científico; Fase 1 permanece pendente.
