# Contrato permanente dos agentes â€” C-NBI v2

## Clean implementation
C-NBI v2 is a clean reimplementation.
Legacy code is historical reference only.

A v1 em https://github.com/LimaGV/C-NBI, branch cnbi-v1.0, Ã© somente referÃªncia.
NÃ£o modificar a v1, copiar mÃ³dulos, importar cnbi, reutilizar .venv, herdar sua
arquitetura ou preservar thresholds e decisÃµes por continuidade.
A distribuiÃ§Ã£o Ã© c-nbi-v2; o import Ã© cnbi_v2.

## Scientific change policy
A Fase 1 foi autorizada explicitamente: base quadrÃ¡tica, OLS multivariado e
incerteza analÃ­tica, com validaÃ§Ã£o sintÃ©tica e ADR 0003. Fases posteriores exigem nova tarefa.
Nenhuma mudanÃ§a metodolÃ³gica sem definiÃ§Ã£o matemÃ¡tica, evidÃªncia, ADR/MDR,
testes e validaÃ§Ã£o. HipÃ³tese experimental nÃ£o vira metodologia oficial.
Registrar o que mudou, por quÃª, branch, commit, decisÃ£o, testes, resultados
afetados e versÃ£o do cÃ³digo.
NÃ£o alterar silenciosamente seed, threshold, solver, normalizaÃ§Ã£o, nÃºmero de
Monte Carlos, H, covariÃ¢ncia, critÃ©rio Pareto, tolerÃ¢ncia ou regularizaÃ§Ã£o.
MudanÃ§as, inclusive defaults, exigem decisÃ£o documentada.

Estados: PROPOSED, EXPERIMENTAL, ACCEPTED, REJECTED, SUPERSEDED.
Fluxo: PROPOSED â†’ EXPERIMENTAL â†’ VALIDATION â†’ ACCEPTED.
VALIDATION Ã© um gate, nÃ£o um sexto estado persistido. Seguir o template;
validaÃ§Ã£o aprovada nÃ£o implica aceitaÃ§Ã£o automÃ¡tica: revisÃ£o explÃ­cita Ã© exigida.

## Tool policy
- Serena: preferir navegaÃ§Ã£o semÃ¢ntica. Antes de editar ciÃªncia existente:
  localizar sÃ­mbolo, referÃªncias, dependÃªncias e impacto; sÃ³ entÃ£o editar.
  Se indisponÃ­vel, registrar e usar busca focada.
- fd / rg: localizaÃ§Ã£o de arquivos / busca textual. Na ausÃªncia de fd, rg --files.
- ast-grep: padrÃµes e transformaÃ§Ãµes estruturais; nÃ£o usar o alias sg nem
  substituiÃ§Ãµes textuais cegas quando estrutura for mais segura.
- Repomix: contexto amplo e auditorias cruzadas; evitar em tarefas pequenas.
  NÃ£o agregar secrets, dados ou PDFs.
- Zotero: fonte canÃ´nica da biblioteca pessoal; primeira consulta de literatura
  potencialmente existente. Buscar tÃ­tulo, autor, DOI ou tÃ³pico, conferir
  metadados e localizar documentos quando permitido. NÃ£o exportar a biblioteca.
  NÃ£o inventar DOI, tÃ­tulo, autor, ano, pÃ¡ginas, equaÃ§Ãµes, volume ou periÃ³dico.
  METADATA_VERIFIED nÃ£o equivale a FULLTEXT_VERIFIED. Este Ãºltimo exige inspeÃ§Ã£o
  real do texto integral, com passagens e localizaÃ§Ã£o registradas.
- Context7: documentaÃ§Ã£o atual de bibliotecas, frameworks, SDKs, APIs, CLIs e
  cloud, inclusive setup e debugging especÃ­fico. ComeÃ§ar por resolve-library-id
  salvo ID /org/project exato; escolher fonte relevante e query-docs por conceito.
  Se ausente, registrar e consultar docs oficiais, sem fingir consulta.
  Context7 fundamenta software, nunca validade cientÃ­fica.
- OpenAI Developer Docs MCP: primeira fonte oficial para OpenAI/Codex/MCP.
  Se nÃ£o exposto, usar pÃ¡ginas oficiais e registrar fallback.
- Blender: IRRELEVANTE Ã  infraestrutura cientÃ­fica atual.
- cua_repl / node_repl: suporte somente quando necessÃ¡rio.
- code-review / codex_app: disabled por polÃ­tica desta tarefa; nÃ£o depender.
- GitHub: git e gh autenticado; nÃ£o depender de GitHub MCP.

Distinguir estado informado, ferramenta exposta e teste real no inventÃ¡rio MCP.

## Desenvolvimento e qualidade
Python 3.12; .venv prÃ³pria via uv. NÃ£o reutilizar ambiente da v1.
Na raiz: uv sync --locked; uv run pytest; uv run ruff check .; uv run mypy src.
DependÃªncias novas exigem justificativa; mudanÃ§as acompanham uv.lock.
Nunca desenvolver em main. Usar feature/*, experiment/*, fix/*, docs/*, release/*.
Proibidos nomes final, final2, test, temp, new. main sÃ³ recebe estados testados,
documentados, reproduzÃ­veis e metodologicamente rastreÃ¡veis por PR.
NÃ£o fazer merge com CI falhando ou conflito; novos PRs nÃ£o tÃªm merge automÃ¡tico.
O PR #1 da Fase 0 foi integrado por autorizaÃ§Ã£o explÃ­cita na tarefa da Fase 0.5.
main nasce com um commit vazio para permitir o primeiro PR.

## ReferÃªncias e dados
Correção da Fase8 explicitamente autorizada em2026-10-25, no PR11 e mesma
branch feature/08-reference-sensitivity-final-benchmark: baseline oficial é H5
standalone (492 subproblemas), nunca membership H20. Preservar37 subsets,
RSMs/anchors/normalizações, SLSQP/Jacobianos/starts/aceitação. Executar cada H
2/4/5/10/20 independentemente; H5 cinco repetições para ruído de runtime,
outros H uma medição cada. Congelar protocolo/source antes das execuções.
Reavaliar8 respostas, dedup/ND, cinco métricas, K66/curvas e dependências CNBI
na sensibilidade usando a linhagem/subamostras já salvas. Referência independente
18503/zeroCNBI, dados/runs/timing EAs e VRF histórico permanecem preservados.
Arquivo anterior da Fase8 é histórico (H5 extraído da malha-mãe H20); manter
byte-identical e publicar correção separada na mesma fase, com documentação
principal corrigida. Referência comum antiga é apenas target histórico,
explicitamente sem alegar auto-inclusão do novo H5. Sem VRF/EA novos, refit,
MC/anchors/PA, novos subsets, mudança de solver/tolerância, adaptação ou merge.
A decisão anterior de preservar408/custo pendente é SUPERSEDED por este pedido.
Escopos abaixo são históricos.

Fase7 autorizada apÃ³s squash do PR #9 com CI verde, branch
feature/07-pareto-reference-loo. H_base5 Ã© decisÃ£o operacional do responsÃ¡vel;
H20 continua auxiliar da mesma famÃ­lia CNBI. Construir referÃªncia empÃ­rica pooled
e leave-one-family-out, sem auto-inclusÃ£o CNBI ao avaliar H5. Reavaliar todos x
elegÃ­veis nos RSMs atuais; respostas histÃ³ricas nÃ£o sÃ£o canÃ´nicas. UsuÃ¡rio autoriza
explicitamente transferir a calibraÃ§Ã£o das metaheurÃ­sticas V1, mantendo fonte,
hashes e diferenÃ§as explÃ­citas; nÃ£o importar seus mÃ³dulos ou reutilizar ambiente.
Usar pymoo consolidado/pinado, orÃ§amento comum e30 seeds fixas, esfera por
amostragem factÃ­vel/repair radial explÃ­cito. Congelar protocolo antes das runs.
Preservar proveniÃªncias, reconstruir ND apÃ³s exclusÃ£o de famÃ­lia e distinguir
mÃ©tricas LOO de mÃ©tricas comuns self-included. ADR0011 ACCEPTED nesse escopo.
Sem rerodar MC/anchors/PA/NBI, sem verdade Pareto, superioridade, benchmark final,
refinamento adaptativo implementado ou merge do novo PR. Escopos abaixo histÃ³ricos.

Fase 6 explicitamente autorizada apÃ³s squash do PR #8 com CI verde: branch
feature/06-simplex-lattice-local-nbi. Consumir somente os37 IDs de B=2000,
RSMs codificados nominais e anchors/payoff preservados, bola alpha=8**0.25,
direÃ§Ãµes originais e sem RC. NBI local com normalizaÃ§Ã£o por subset, normal
unitÃ¡ria orientada ao ideal, igualdade e Jacobianos analÃ­ticos, SLSQP e
aceitaÃ§Ã£o independente. Simplex-Lattice H={2,4,5,10,20}, malha-mÃ£e20 com
membership inteiro exato; nÃ£o resolver pesos repetidos. Reavaliar8 respostas
antes de deduplicaÃ§Ã£o/ND full-space e cobertura interna em normalizaÃ§Ã£o global
fixa da Fase5. H20 Ã© referÃªncia interna, sem verdade Pareto ou H final aceito.
ADR0010 ACCEPTED somente nesse escopo. Sem nova PA/MC/anchors, benchmark,
NSGA/MOEA/D/VRF ou mÃ©tricas externas. Sem merge do novo PR ou prÃ³xima fase.
Escopos abaixo sÃ£o histÃ³ricos.

RevisÃ£o explicitamente autorizada antes do merge do PR #8: alterar somente a
polÃ­tica de early stop e sua sensibilidade, na mesma branch. Preservar a v1 e
todos os artefatos anteriores. V2 PROPOSED_REVISED, post hoc no caso turning:
gaps adjacentes normalizados do q95, tolerÃ¢ncia estrita 0.05 (pontos percentuais),
janela de trÃªs checkpoints elegÃ­veis (primeira 500/600/700), dimensÃ£o e IDs
exatamente estÃ¡veis. Monitorar global e trios/quartetos selecionados estÃ¡veis;
pares apenas pela identidade. Reusar espectros salvos, sem MC/anchors/payoffs/
normalizaÃ§Ã£o/CHIM/SVD novos. PA e seleÃ§Ã£o B=2000 permanecem inalteradas.
ADR 0009 PROPOSED; regra congelada para validaÃ§Ã£o externa futura. Sem merge,
H, NBI/C-NBI ou fase nova. O escopo original abaixo Ã© histÃ³rico.

Esta tarefa autoriza a Fase 5 em feature/05-chim-svd-local-pa apÃ³s squash do PR #7
com CI verde. Consumir payoff sphere nominal da Fase 2 e ensemble exato da Fase 4.
OrientaÃ§Ã£o comum MIN e normalizaÃ§Ã£o fixa nominal, CHIM centralizado Z_C H_k,
SVD da perturbaÃ§Ã£o e PA local q95 linear com comparaÃ§Ã£o estrita em todos k-1
componentes. Avaliar todos 28/56/70 subsets, sem filtro pela dimensÃ£o global,
qmax, volume, deslocamento de anchors ou mÃ©tricas do sampler. B=2000 referÃªncia;
20 prefixos e avaliaÃ§Ã£o retrospectiva da polÃ­tica PA original, sem promovÃª-la.
ADR 0008 ACCEPTED neste escopo. Sem novos draws, reotimizaÃ§Ã£o, RC, clipping,
H/Simplex-Lattice, NBI/C-NBI, clustering ou mÃ©tricas Pareto. Novo PR sem merge
automÃ¡tico; nenhuma fase posterior iniciada. Escopos anteriores sÃ£o histÃ³ricos.

Esta tarefa autoriza a Fase 4 em feature/04-monte-carlo-anchor-reoptimization,
apÃ³s squash do PR #6 com CI verde. Consumir exatamente o ensemble versionado da
Fase 3, sem novos draws ou alteraÃ§Ã£o de seed/Sigma_e. Reotimizar cada rÃ©plica e
resposta com solve_quadratic_ball inalterado, na bola alpha=8**0.25, sem RC.
Certificar soluÃ§Ãµes, preservar Ã­ndices e registrar falhas sem substitutos;
payoff natural prÃ³pria de cada rÃ©plica. ADR 0007 ACCEPTED no escopo solicitado;
METHOD_DEFINITION Ã© classe adicional explÃ­cita para C-MC-06.
Sem normalizaÃ§Ã£o, CHIM, edge matrix, SVD/PA, subsets, NBI/C-NBI ou Fase 5.
Novo PR sem merge automÃ¡tico. PolÃ­ticas das fases anteriores sÃ£o histÃ³ricas.

Esta tarefa autoriza a Fase 3 em feature/03-multivariate-coefficient-monte-carlo,
apÃ³s squash do PR #5 com checks verdes. Usar o mesmo ajuste codificado da Fase 2,
matrix-normal plug-in conjunta, Sigma_e bruta, seed 777 explÃ­cita e um ensemble
2000Ã—10Ã—8. Sensibilidade em 100:100:2000 por prefixos do mesmo ensemble.
ADR 0006 ACCEPTED no escopo solicitado; early stop futuro da PA PROPOSED,
registrado antes dos resultados e nÃ£o aplicado agora. Sem reotimizar anchors,
payoff por rÃ©plica, bootstrap, shrinkage, NBI/C-NBI/PA ou inÃ­cio da Fase 4.
O novo PR nÃ£o tem merge automÃ¡tico. METHODOLOGICAL_DECISION Ã© classe explÃ­cita
adicional de evidÃªncia para o calendÃ¡rio B/seed decidido pelo responsÃ¡vel.

Esta tarefa autoriza a Fase 2 em feature/02-individual-anchors-response-region,
apÃ³s squash do PR #4 com checks verdes: anchors individuais, payoff clÃ¡ssica e
ablaÃ§Ã£o experimental de regiÃ£o de respostas. ADR 0005 permanece EXPERIMENTAL.
A clarificaÃ§Ã£o do responsÃ¡vel prioriza a planilha sobre o artigo; os cÃ³digos
originais verificados sÃ£o um caso distinto do modelo fÃ­sico, sem afirmar
equivalÃªncia que falhou. NÃ£o inventar inverse coding ou coordenadas fÃ­sicas.
Dados continuam integrais. O novo PR nÃ£o tem merge automÃ¡tico. Monte Carlo,
NBI/C-NBI, CHIM combinatorial, PA, shrinkage e etapas posteriores seguem fora.

Classificar claims: LITERATURE, INTERNAL_EVIDENCE, MATHEMATICAL_DERIVATION,
METHODOLOGICAL_DECISION, METHOD_DEFINITION, PROPOSED.
Status: SUPPORTED, PARTIALLY_SUPPORTED, EXPERIMENTAL, UNVERIFIED, REJECTED,
SUPERSEDED. NÃ£o escrever "a literatura mostra" sem fonte verificÃ¡vel.
Dados brutos sÃ£o imutÃ¡veis. DerivaÃ§Ãµes exigem origem, hashes, commit, configuraÃ§Ã£o,
ambiente e resultados. NÃ£o versionar dados, anexos Zotero ou grandes resultados
automaticamente. Seguir docs/data_integrity.md e docs/data_management.md.

## External actions e secrets
NÃ£o executar aÃ§Ãµes destrutivas ou persistentes desnecessÃ¡rias sem autorizaÃ§Ã£o
da tarefa. A Fase 0.5 autoriza merge do PR #1 apÃ³s checks e ausÃªncia de conflito,
e criaÃ§Ã£o/push/PR da nova branch. NÃ£o autoriza merge do novo PR ou alteraÃ§Ã£o da v1.
A Fase 0.6 autoriza integrar o PR #2 apÃ³s CI verde e ausÃªncia de conflito,
incorporar o CCD.xlsx fornecido e enviar seu raw byte-identical ao repositÃ³rio
privado por autorizaÃ§Ã£o explÃ­cita adicional do responsÃ¡vel. A exceÃ§Ã£o cobre
somente CCD_original.xlsx. O novo PR da Fase 0.6 nÃ£o tem merge automÃ¡tico.
A tarefa da Fase 1 autoriza squash merge do PR #3 apÃ³s CI verde e ausÃªncia
de conflito, desenvolvimento/push/PR em feature/01-multivariate-rsm-foundation.
O novo PR da Fase 1 nÃ£o tem merge automÃ¡tico. NÃ£o acrescentar ferramentas de
sampling, shrinkage, otimizaÃ§Ã£o, NBI/CNBI ou dependÃªncias sem justificativa.
A tarefa posterior autoriza ajustar o CCD atualizado, preservar sua revisÃ£o
literal separadamente e comparar os 80 coeficientes. A autorizaÃ§Ã£o privada
do mesmo workbook Ã© estendida somente a CCD_values_20261023.xlsx e Ã  extraÃ§Ã£o
literal correspondente. NÃ£o sobrescrever CCD_original.xlsx; atualizar o PR #4,
sem fazer merge ou iniciar outra fase.
Nunca registrar tokens, API keys, passwords ou credentials. NÃ£o copiar .env,
configuraÃ§Ã£o global de agentes, credenciais ou conteÃºdo de keyring para o Git.

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
Raw e snapshots sÃ£o imutÃ¡veis; snapshot nÃ£o substitui o original.
Never use an Excel workbook with unresolved external links as the sole computational source of truth.
Excel Ã© formato primÃ¡rio aceito, mas cÃ³digo nÃ£o depende de ediÃ§Ã£o manual.
Cada linha experimental deverÃ¡ ter run_id explÃ­cito; linha Excel nÃ£o Ã© ID cientÃ­fico.
NÃ£o incorporar dataset real ou criar snapshot sem operaÃ§Ã£o explÃ­cita posterior.
Na Fase 0.6 o dataset turning_application_ccd_19run Ã© incorporado como evidÃªncia
raw com links externos, sem certificaÃ§Ã£o dos caches, snapshot ou processed.
Table 3 de Pereira et al. (2025) Ã© expected output, nunca observaÃ§Ã£o experimental.
Proibido reconstruir Y, imputar respostas ou ajustar dados para reproduzir
coeficientes publicados. OLS/RSM e incerteza analÃ­tica estÃ£o autorizados na
Fase 1 com dados sintÃ©ticos; nÃ£o ajustar o raw experimental nÃ£o autocontido.
A revisÃ£o literal fornecida em 2026-10-23 pode ser ajustada com precisÃ£o integral.
Coding nominal, escala de apresentaÃ§Ã£o e hipÃ³teses diagnÃ³sticas devem ser
explÃ­citos. Arredondamento de cÃ³pia de WR Ã© diagnÃ³stico opcional, excluÃ­do dos
modelos reais e dos totais de validaÃ§Ã£o; nunca alterar os valores experimentais.
Monte Carlo e NBI/CNBI continuam fora do escopo autorizado.
ClassificaÃ§Ã£o PUBLIC_SMALL/PUBLIC_LARGE/RESTRICTED exige evidÃªncia; nÃ£o escolher
por inferÃªncia, nÃ£o configurar LFS automaticamente e nÃ£o alterar .gitignore sÃ³
para ocultar dados existentes. Processed exige raw/snapshot + script versionado.
Resultados pertencem a results/, nunca a data/raw/.

## Bibliographic integrity
Ã‰ proibido inventar ou inferir sem verificaÃ§Ã£o DOI, tÃ­tulo, autores, ano, journal,
volume, issue, pÃ¡ginas, equaÃ§Ãµes ou pÃ¡ginas que supostamente sustentem uma claim.
Se desconhecido, deixar vazio ou marcar UNVERIFIED_METADATA.
Toda decisÃ£o cientÃ­fica futura exige uma combinaÃ§Ã£o pertinente de literatura
verificada, derivaÃ§Ã£o matemÃ¡tica documentada ou experimento reproduzÃ­vel.
EvidÃªncia interna nÃ£o Ã© literatura; hipÃ³tese proposta nÃ£o Ã© fato.
Status de fonte: UNREAD, METADATA_VERIFIED, PARTIAL, FULLTEXT_VERIFIED, CRITICAL_SOURCE.
CRITICAL_SOURCE expressa importÃ¢ncia, nÃ£o substitui evidÃªncia de leitura integral.
NÃ£o enviar PDF/EPUB/DJVU ou outros documentos protegidos ao Git por padrÃ£o.
Zotero continua canÃ´nico e somente leitura nesta fase; Git guarda seleÃ§Ãµes
verificadas de BibTeX, notas, IDs, claims, DOI conhecido, proveniÃªncia e decisÃµes.
