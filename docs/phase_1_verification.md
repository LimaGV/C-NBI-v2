# Fase 1 — verificação da fundação RSM e incerteza

Data: 2026-10-23. Versão 0.1.0.dev0.
Branch: feature/01-multivariate-rsm-foundation.
Commit/PR: SHA efetivo e CI vinculados no PR após commit, sem hash autorreferente.

## Fechamento científico posterior — diagnósticos

O registro abaixo descreve o gate inicial e preserva seu estado histórico.
Após a incorporação literal autorizada, o fechamento acrescenta SS/R²/S,
PRESS/LOOCV, ANOVA global e PE/LOF, com
[definição matemática](mathematics/rsm_diagnostics.md) e
[resultados reais](mathematics/turning_rsm_diagnostics.md).
237 testes; cobertura 98.47% (516/524), novo módulo 160/160, model/ 100%.
Sem dependência nova, alteração de raw, remoção de termos ou algoritmo posterior.
ADR 0003 estendida e claims C-RSM-07 a 11; PR #4 mantido sem merge.
Gate final reconferido em 2026-10-24: uv sync --locked, pytest -v,
pytest --cov=cnbi_v2, Ruff e mypy src aprovados (10 source files).
Raw histórico/literal, CSV literal, golden reference e lock preservados.

## Preparação Git

Working tree estava limpo. PR #3 aberto com head
afc9acd10d8615b3028e8c59252699f2e0592469, MERGEABLE/CLEAN e quatro checks SUCCESS
(push/PR, Windows/Ubuntu). Integração explicitamente autorizada nesta tarefa.
Squash merge em main: 6d3b5e2a59a3b4a7f0f132a1f0c940af6f42755b.
main atualizada por fast-forward e limpa antes de criar a nova branch.
Nenhum desenvolvimento diretamente em main; novo PR sem merge automático.

## Verificação científica anterior à implementação

Zotero primeiro: AXXUEWGY (Díaz-García/Bashiri 2014), Z8Z2JEDC/677LYFGP
(Myers/Montgomery/Anderson-Cook), ITYZMBYG (Johnson/Wichern) e busca Khuri.
Ausência de anexo no artigo final e no livro RSM foi verificada.
Usados diretamente R003, preprint primário arXiv:1105.2911v1 pp.2-3, e
R004, livro RSM 4a ed. local pp.16-17,22-23,33. PARTIAL explícito, sem
atribuir páginas do preprint à publicação final ou alegar leitura integral.
Johnson/Wichern ficou somente METADATA_VERIFIED após timeout do linked_url.
R001, já FULLTEXT_VERIFIED, continua evidência do caso aplicado.
Ver [fontes e hashes](../references/notes/rsm_foundation_sources.md).

Matemática documentada antes da implementação: projeto fixo, erro de média
zero, covariância comum e ausência de covariância entre observações.
Normalidade adicional somente para a distribuição matrix-normal.
Sigma e B populacionais são distintos de suas estimativas no código/documentação.

## Implementação e decisões numéricas

Quatro arquivos em src/cnbi_v2/model: __init__, quadratic_design,
multivariate_rsm e uncertainty. Base completa determinística; OLS por lstsq
com rcond=eps*max(n,p), rejeição de posto deficiente/df<=0; V_X por QR/solve.
Estimativa residual bruta, sem padronização, correção de autovalores ou jitter.
Buffers imutáveis no resultado, inputs preservados e diagnósticos de condição.

vec(B_hat) empilha colunas, Cov estimada=Sigma_hat_e⊗V_X.
O preprint escreve vec(B_hat^T); conversão/permutação derivada e testada.
h calculado por solve(R^T,z), nunca por 1+h. Contrastes usam solve(R^T,z_a-z_b),
incluindo covariâncias cruzadas e evitando cancelamento de marginais próximas.
As checagens de PSD/simetria usam apenas tolerância de arredondamento
eps*d*||M||_inf; escala interna da cópia diagnóstica evita overflow, sem alterar
a covariância armazenada. Matriz residual singular/zero é aceita como PSD.

## Testes analíticos e dados sintéticos

105 testes novos, 73 testes anteriores preservados. Sem simulação repetida.
Fixture correlacionada usa uma realização sintética e seed 20261023;
permutação de observações usa seed 42. Ambas pertencem somente aos testes.
Não são seeds/defaults do futuro C-NBI.

- Base de 1 a 5 fatores, ordem explícita e rank de projeto fatorial sintético.
- Recuperação sem ruído para 1,3,8 respostas; dimensões sintéticas 19×10/19×8.
- Caso manual unifatorial com resíduos ortogonais à base: MSE=[35,145],
  Sigma_hat_e=[[35,70],[70,145]] e V_X calculado por frações exatas.
- Equivalência de coeficientes, fitted values, resíduos e MSE uni/multivariados.
- Gram residual, diag(Sigma_hat_e)=MSE, ortogonalidade, simetria e PSD.
- Todos os blocos/indexações vec, permutação de vec(B_hat^T) e propagação
  determinística da covariância das observações até os coeficientes.
- h manual, diagonal do projetor e soma dos leverages igual ao rank.
- Covariância média/variância univariada, sem erro adicional de observação.
- Covariância cruzada via mapa linear de coeficientes, incluindo valor negativo.
- Diferença com os dois termos cruzados, zero exato para pontos iguais,
  simetria a/b e pontos muito próximos sem cancelamento de marginais.
- Permutações de respostas/observações, imutabilidade, NaN/Inf/complexos,
  shape, posto, df, overflow e diagnóstico PSD em escalas extremas.

Tolerâncias explícitas de precisão float64 em projetos sintéticos bem
condicionados: relativas em geral 1e-13/1e-14, absolutas por identidade e
escala (até 2e-13 para ortogonalidade de X^T E). Não são tolerâncias de
reprodução de números publicados. Nenhuma tolerância da Table 3 foi escolhida.

## Resultados locais

- uv sync --locked: passou; 115 pacotes resolvidos, sem dependência nova.
- uv run pytest -v: 178 passed.
- uv run pytest --cov=cnbi_v2: 178 passed; 352/360 statements, 97.78%.
- Novo model/: 152/152 statements, 100%.
- Antes: 200/208 statements, 96.15%; os mesmos oito statements antigos
  não cobertos permanecem no inspector, sem redução na cobertura anterior.
- CI Windows/Ubuntu passa a executar cobertura com mínimo 96.15%.
- uv run ruff check .: All checks passed.
- uv run mypy src: Success, no issues found in 9 source files.
- git diff --check: passou. data/, golden reference e uv.lock sem mudanças.
- Produção não importa fixtures/golden reference; teste de fronteira preservado.

## Escopo e pendências

ADR 0003 ACCEPTED por solicitação explícita; validation gate local PASSED.
Claims C-RSM-01 a 06 documentadas com tipo de evidência, pressupostos e limites.
As covariâncias cruzadas/diferenças são derivações, não citações inventadas.

Não há Monte Carlo, perturbação/sampling, Cholesky de amostragem, shrinkage,
OAS/LW, bootstrap, otimização, âncoras, payoff, CHIM, PA, NBI/CNBI, Pareto,
subconjuntos, Simplex-Lattice ou escolha de H. statsmodels não foi adicionado.
Nenhum dado experimental foi ajustado ou reconstruído. O raw permanece com
SHA-256 fd9c463efdcd62ff3d7eaa7eec18d9e112543675c30b1f36838beeb38deebf4a.

Antes da validação aplicada: fonte externa e versão do workbook, snapshot
certificado, fatores codificados/físicos e ordem beta/fator, divergências dos
níveis físicos, interpretação de escalas e tolerância de arredondamento justificada.
C011 permanece UNVERIFIED. nu=9 é condicionado a rank(X)=10 e não decide
shrinkage. A próxima fase não é iniciada automaticamente.
