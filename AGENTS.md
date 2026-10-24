# Contrato permanente dos agentes — C-NBI v2

## Clean implementation
C-NBI v2 is a clean reimplementation.
Legacy code is historical reference only.

A v1 em https://github.com/LimaGV/C-NBI, branch cnbi-v1.0, é somente referência.
Não modificar a v1, copiar módulos, importar cnbi, reutilizar .venv, herdar sua
arquitetura ou preservar thresholds e decisões por continuidade.
A distribuição é c-nbi-v2; o import é cnbi_v2.

## Scientific change policy
A Fase 1 foi autorizada explicitamente: base quadrática, OLS multivariado e
incerteza analítica, com validação sintética e ADR 0003. Fases posteriores exigem nova tarefa.
Nenhuma mudança metodológica sem definição matemática, evidência, ADR/MDR,
testes e validação. Hipótese experimental não vira metodologia oficial.
Registrar o que mudou, por quê, branch, commit, decisão, testes, resultados
afetados e versão do código.
Não alterar silenciosamente seed, threshold, solver, normalização, número de
Monte Carlos, H, covariância, critério Pareto, tolerância ou regularização.
Mudanças, inclusive defaults, exigem decisão documentada.

Estados: PROPOSED, EXPERIMENTAL, ACCEPTED, REJECTED, SUPERSEDED.
Fluxo: PROPOSED → EXPERIMENTAL → VALIDATION → ACCEPTED.
VALIDATION é um gate, não um sexto estado persistido. Seguir o template;
validação aprovada não implica aceitação automática: revisão explícita é exigida.

## Tool policy
- Serena: preferir navegação semântica. Antes de editar ciência existente:
  localizar símbolo, referências, dependências e impacto; só então editar.
  Se indisponível, registrar e usar busca focada.
- fd / rg: localização de arquivos / busca textual. Na ausência de fd, rg --files.
- ast-grep: padrões e transformações estruturais; não usar o alias sg nem
  substituições textuais cegas quando estrutura for mais segura.
- Repomix: contexto amplo e auditorias cruzadas; evitar em tarefas pequenas.
  Não agregar secrets, dados ou PDFs.
- Zotero: fonte canônica da biblioteca pessoal; primeira consulta de literatura
  potencialmente existente. Buscar título, autor, DOI ou tópico, conferir
  metadados e localizar documentos quando permitido. Não exportar a biblioteca.
  Não inventar DOI, título, autor, ano, páginas, equações, volume ou periódico.
  METADATA_VERIFIED não equivale a FULLTEXT_VERIFIED. Este último exige inspeção
  real do texto integral, com passagens e localização registradas.
- Context7: documentação atual de bibliotecas, frameworks, SDKs, APIs, CLIs e
  cloud, inclusive setup e debugging específico. Começar por resolve-library-id
  salvo ID /org/project exato; escolher fonte relevante e query-docs por conceito.
  Se ausente, registrar e consultar docs oficiais, sem fingir consulta.
  Context7 fundamenta software, nunca validade científica.
- OpenAI Developer Docs MCP: primeira fonte oficial para OpenAI/Codex/MCP.
  Se não exposto, usar páginas oficiais e registrar fallback.
- Blender: IRRELEVANTE à infraestrutura científica atual.
- cua_repl / node_repl: suporte somente quando necessário.
- code-review / codex_app: disabled por política desta tarefa; não depender.
- GitHub: git e gh autenticado; não depender de GitHub MCP.

Distinguir estado informado, ferramenta exposta e teste real no inventário MCP.

## Desenvolvimento e qualidade
Python 3.12; .venv própria via uv. Não reutilizar ambiente da v1.
Na raiz: uv sync --locked; uv run pytest; uv run ruff check .; uv run mypy src.
Dependências novas exigem justificativa; mudanças acompanham uv.lock.
Nunca desenvolver em main. Usar feature/*, experiment/*, fix/*, docs/*, release/*.
Proibidos nomes final, final2, test, temp, new. main só recebe estados testados,
documentados, reproduzíveis e metodologicamente rastreáveis por PR.
Não fazer merge com CI falhando ou conflito; novos PRs não têm merge automático.
O PR #1 da Fase 0 foi integrado por autorização explícita na tarefa da Fase 0.5.
main nasce com um commit vazio para permitir o primeiro PR.

## Referências e dados
Revisão explicitamente autorizada antes do merge do PR #8: alterar somente a
política de early stop e sua sensibilidade, na mesma branch. Preservar a v1 e
todos os artefatos anteriores. V2 PROPOSED_REVISED, post hoc no caso turning:
gaps adjacentes normalizados do q95, tolerância estrita 0.05 (pontos percentuais),
janela de três checkpoints elegíveis (primeira 500/600/700), dimensão e IDs
exatamente estáveis. Monitorar global e trios/quartetos selecionados estáveis;
pares apenas pela identidade. Reusar espectros salvos, sem MC/anchors/payoffs/
normalização/CHIM/SVD novos. PA e seleção B=2000 permanecem inalteradas.
ADR 0009 PROPOSED; regra congelada para validação externa futura. Sem merge,
H, NBI/C-NBI ou fase nova. O escopo original abaixo é histórico.

Esta tarefa autoriza a Fase 5 em feature/05-chim-svd-local-pa após squash do PR #7
com CI verde. Consumir payoff sphere nominal da Fase 2 e ensemble exato da Fase 4.
Orientação comum MIN e normalização fixa nominal, CHIM centralizado Z_C H_k,
SVD da perturbação e PA local q95 linear com comparação estrita em todos k-1
componentes. Avaliar todos 28/56/70 subsets, sem filtro pela dimensão global,
qmax, volume, deslocamento de anchors ou métricas do sampler. B=2000 referência;
20 prefixos e avaliação retrospectiva da política PA original, sem promovê-la.
ADR 0008 ACCEPTED neste escopo. Sem novos draws, reotimização, RC, clipping,
H/Simplex-Lattice, NBI/C-NBI, clustering ou métricas Pareto. Novo PR sem merge
automático; nenhuma fase posterior iniciada. Escopos anteriores são históricos.

Esta tarefa autoriza a Fase 4 em feature/04-monte-carlo-anchor-reoptimization,
após squash do PR #6 com CI verde. Consumir exatamente o ensemble versionado da
Fase 3, sem novos draws ou alteração de seed/Sigma_e. Reotimizar cada réplica e
resposta com solve_quadratic_ball inalterado, na bola alpha=8**0.25, sem RC.
Certificar soluções, preservar índices e registrar falhas sem substitutos;
payoff natural própria de cada réplica. ADR 0007 ACCEPTED no escopo solicitado;
METHOD_DEFINITION é classe adicional explícita para C-MC-06.
Sem normalização, CHIM, edge matrix, SVD/PA, subsets, NBI/C-NBI ou Fase 5.
Novo PR sem merge automático. Políticas das fases anteriores são históricas.

Esta tarefa autoriza a Fase 3 em feature/03-multivariate-coefficient-monte-carlo,
após squash do PR #5 com checks verdes. Usar o mesmo ajuste codificado da Fase 2,
matrix-normal plug-in conjunta, Sigma_e bruta, seed 777 explícita e um ensemble
2000×10×8. Sensibilidade em 100:100:2000 por prefixos do mesmo ensemble.
ADR 0006 ACCEPTED no escopo solicitado; early stop futuro da PA PROPOSED,
registrado antes dos resultados e não aplicado agora. Sem reotimizar anchors,
payoff por réplica, bootstrap, shrinkage, NBI/C-NBI/PA ou início da Fase 4.
O novo PR não tem merge automático. METHODOLOGICAL_DECISION é classe explícita
adicional de evidência para o calendário B/seed decidido pelo responsável.

Esta tarefa autoriza a Fase 2 em feature/02-individual-anchors-response-region,
após squash do PR #4 com checks verdes: anchors individuais, payoff clássica e
ablação experimental de região de respostas. ADR 0005 permanece EXPERIMENTAL.
A clarificação do responsável prioriza a planilha sobre o artigo; os códigos
originais verificados são um caso distinto do modelo físico, sem afirmar
equivalência que falhou. Não inventar inverse coding ou coordenadas físicas.
Dados continuam integrais. O novo PR não tem merge automático. Monte Carlo,
NBI/C-NBI, CHIM combinatorial, PA, shrinkage e etapas posteriores seguem fora.

Classificar claims: LITERATURE, INTERNAL_EVIDENCE, MATHEMATICAL_DERIVATION,
METHODOLOGICAL_DECISION, METHOD_DEFINITION, PROPOSED.
Status: SUPPORTED, PARTIALLY_SUPPORTED, EXPERIMENTAL, UNVERIFIED, REJECTED,
SUPERSEDED. Não escrever "a literatura mostra" sem fonte verificável.
Dados brutos são imutáveis. Derivações exigem origem, hashes, commit, configuração,
ambiente e resultados. Não versionar dados, anexos Zotero ou grandes resultados
automaticamente. Seguir docs/data_integrity.md e docs/data_management.md.

## External actions e secrets
Não executar ações destrutivas ou persistentes desnecessárias sem autorização
da tarefa. A Fase 0.5 autoriza merge do PR #1 após checks e ausência de conflito,
e criação/push/PR da nova branch. Não autoriza merge do novo PR ou alteração da v1.
A Fase 0.6 autoriza integrar o PR #2 após CI verde e ausência de conflito,
incorporar o CCD.xlsx fornecido e enviar seu raw byte-identical ao repositório
privado por autorização explícita adicional do responsável. A exceção cobre
somente CCD_original.xlsx. O novo PR da Fase 0.6 não tem merge automático.
A tarefa da Fase 1 autoriza squash merge do PR #3 após CI verde e ausência
de conflito, desenvolvimento/push/PR em feature/01-multivariate-rsm-foundation.
O novo PR da Fase 1 não tem merge automático. Não acrescentar ferramentas de
sampling, shrinkage, otimização, NBI/CNBI ou dependências sem justificativa.
A tarefa posterior autoriza ajustar o CCD atualizado, preservar sua revisão
literal separadamente e comparar os 80 coeficientes. A autorização privada
do mesmo workbook é estendida somente a CCD_values_20261023.xlsx e à extração
literal correspondente. Não sobrescrever CCD_original.xlsx; atualizar o PR #4,
sem fazer merge ou iniciar outra fase.
Nunca registrar tokens, API keys, passwords ou credentials. Não copiar .env,
configuração global de agentes, credenciais ou conteúdo de keyring para o Git.

## Experimental data integrity
The agent must never silently modify experimental raw data.

All corrections, transformations, exclusions, unit conversions or imputations must be:
- explicit;
- reproducible;
- version controlled;
- documented;
- testable.

If an experimental value must be corrected, raw remains unchanged.
The correction must occur in a documented transformation step.
Raw e snapshots são imutáveis; snapshot não substitui o original.
Never use an Excel workbook with unresolved external links as the sole computational source of truth.
Excel é formato primário aceito, mas código não depende de edição manual.
Cada linha experimental deverá ter run_id explícito; linha Excel não é ID científico.
Não incorporar dataset real ou criar snapshot sem operação explícita posterior.
Na Fase 0.6 o dataset turning_application_ccd_19run é incorporado como evidência
raw com links externos, sem certificação dos caches, snapshot ou processed.
Table 3 de Pereira et al. (2025) é expected output, nunca observação experimental.
Proibido reconstruir Y, imputar respostas ou ajustar dados para reproduzir
coeficientes publicados. OLS/RSM e incerteza analítica estão autorizados na
Fase 1 com dados sintéticos; não ajustar o raw experimental não autocontido.
A revisão literal fornecida em 2026-10-23 pode ser ajustada com precisão integral.
Coding nominal, escala de apresentação e hipóteses diagnósticas devem ser
explícitos. Arredondamento de cópia de WR é diagnóstico opcional, excluído dos
modelos reais e dos totais de validação; nunca alterar os valores experimentais.
Monte Carlo e NBI/CNBI continuam fora do escopo autorizado.
Classificação PUBLIC_SMALL/PUBLIC_LARGE/RESTRICTED exige evidência; não escolher
por inferência, não configurar LFS automaticamente e não alterar .gitignore só
para ocultar dados existentes. Processed exige raw/snapshot + script versionado.
Resultados pertencem a results/, nunca a data/raw/.

## Bibliographic integrity
É proibido inventar ou inferir sem verificação DOI, título, autores, ano, journal,
volume, issue, páginas, equações ou páginas que supostamente sustentem uma claim.
Se desconhecido, deixar vazio ou marcar UNVERIFIED_METADATA.
Toda decisão científica futura exige uma combinação pertinente de literatura
verificada, derivação matemática documentada ou experimento reproduzível.
Evidência interna não é literatura; hipótese proposta não é fato.
Status de fonte: UNREAD, METADATA_VERIFIED, PARTIAL, FULLTEXT_VERIFIED, CRITICAL_SOURCE.
CRITICAL_SOURCE expressa importância, não substitui evidência de leitura integral.
Não enviar PDF/EPUB/DJVU ou outros documentos protegidos ao Git por padrão.
Zotero continua canônico e somente leitura nesta fase; Git guarda seleções
verificadas de BibTeX, notas, IDs, claims, DOI conhecido, proveniência e decisões.
