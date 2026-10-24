# Changelog

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
