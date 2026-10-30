# Escopo atual — correção pareada da Fase 10E, autorizada em 2026-10-30

O usuário substituiu a equalização conjunta por três pares independentes, nesta
ordem: C-NBI/VRF-NBI, C-NBI/NSGA-III, C-NBI/MOEA/D. K é o menor tamanho apenas
do par em cada cenário/réplica; nenhum terceiro método entra. C-NBI pode ter
subconjuntos distintos em cada par. Sem Friedman/ranking conjunto equalizado.
Preservar byte a byte commit784650a, inclusive resultados e código10E anterior;
nova saída pairwise_20261030 e MDR0018. Política synthetic_analysis_10e_pairwise.json
congelada antes dos cálculos novos; Holm6 para IGD/HV dos três pares, bootstrap
por cenário, validade HV por par, nunca pela presença de um terceiro método.
FPS/normalização/indicadores/IDs originais intactos. Sem buscas/refits novos.
Atualizar o PR18 existente, empilhado no PR17, ambos sem merge automático.
Os registros seguintes são históricos, incluindo a conclusão da equalização conjunta.

# Escopo histórico — Fase10E inicial, autorizado em2026-10-30

Conclusão local: 904 testes, cobertura98.29%, Ruff/mypy83 PASS; auditoria540
subconjuntos/135 blocos e7156 arquivos anteriores íntegros. Inferência nativa
favorável ao C-NBI; vantagem IGD não permanece equalizada e HV equalizado é
inferior a NSGA-III/MOEA/D. Dois HV suplementares passam em2^20, sem promover
status oficial. Onze figuras PNG600/PDF vetorial sem grades. CI final no novo
PR empilhado; nenhum merge nem nova execução de busca oficial.

PR17 permanece aberto no SHA5c3829db, com CI Ubuntu/Windows aprovada; não integrar.
Branch feature/10e-synthetic-statistical-analysis dependente da branch10D;
novo PR empilhado, sem merge automático. Somente análise offline da campaign_v2:
27 células x5 réplicas x4 métodos. Nenhuma nova execução de otimizadores,
ajuste RSM, alteração de seeds/hiperparâmetros/referências/métricas oficiais.
Protocolo docs/policies/synthetic_analysis_10e.json e MDR0017 antes dos cálculos.
Medianas de cinco réplicas por cenário, IGD/HV primários, família Holm conjunta,
Friedman por permutação e Wilcoxon exato condicional, bootstrap por cenário.
Equalização FPS somente pontos ND reais, K mínimo por bloco, IDs preservados.
HV pendente e tolerância de viabilidade somente estudos suplementares separados;
nunca sobrescrever resultados10D nem projetar decisões. Fatores/interações
exploratórios, sem causalidade nem pseudorreplicação. Custo principal ciclo
completo observado; contadores distintos. Figuras EN PNG600/PDF sem grades.
Preservar ciência e resultados0–10D, raw e licenças dos materiais excluídos.
As proibições de10E abaixo eram limites históricos e foram superadas por esta tarefa.

# Escopo histórico — Fase10D, autorizado em2026-10-29

Conclusão numérica2026-10-30:540 buscas/avaliações,135 por método,zero falhas;
ordem C-NBI→VRF-NBI→NSGA-III→MOEA/D verificada por barreiras e horários originais.
Fonte numérica8f9d60f, protocolo19dff294; auditoria540/135 blocos/1262 arquivos PASS.
Preservar todos os resultados, incluindo24 pilotos anteriores e77 tentativas
iniciais(75 completas/2 falhas). Três flags Varimax500 e dois HV pendentes
permanecem explícitos. PR17 aberto; nenhuma reexecução,10E ou merge automático.
Evidência de qualidade e limites em docs/phase_10d_verification.md.

PR16 integrado por merge c0646768, árvore idêntica a df95a954; CI40941198792
verde Ubuntu/Windows. Branch feature/10d-synthetic-algorithm-benchmark.
A autorização desta tarefa permite adaptar v1 7bd4915 para VRF-NBI e os EAs,
superando a antiga restrição de somente consultar; preservar v1 e atribuições,
sem imports diretos de v1 em produção nem reutilização de seu ambiente.
C-NBI canônico v2 completo, B2000, PSD sem jitter, todos subsets elegíveis,
PA estrita q95, H5 k2–4/H2 k5–6, tolerâncias v2 intactas. VRF completo,
max(2,k90) sem clamp; CCD congelado só para ajuste auxiliar de fatores.
18 calibrações EA transferidas, pymoo0.6.2, teto por m, sem retuning.
Preservar ciência0–10C,135 modelos,27 referências e métricas. Busca sem verdade;
avaliação externa somente após terminar. Piloto12 antes da campanha540;
gates falhos bloqueiam campanha e permanecem INCOMPLETE. Sem Fase10E,
significância, equalização ou ajuste da referência. Novo PR permanece aberto.
MDR0016 e documento de migração registram o gauge constante VRF de compatibilidade,
com variância publicada corrigida explicitamente; não mudar licença dos excluídos.
As seções abaixo são históricas e não revogam esta autorização.

# Contrato permanente dos agentes — C-NBI v2

## Escopo atual — Fase10C, autorizado em2026-10-29

PR15 integrado por merge47a0e4d,árvore idêntica a6d07d25,44 hashes/135 modelos
verificados e CI main40919991675 verde Ubuntu/Windows. Branch exclusiva:
feature/10c-synthetic-pareto-reference. Preservar ciência0–10B/135 RSMs/27 anchors.
Somente referência analítica independente P_X=conv(anchors),prova das2 inclusões,
5000 pontos/célula (135000),prefixos2500/5000/10000,estratos eFPS determinísticos.
Sem Dirichlet redundante como falsa amostragem uniforme;sem QJ/perturbar anchors.
Ideal0/nadir maxdistância² entre anchors,frame externo fixo,sem clipping ou
feedback ao solver. Reusar GD/IGDp1,Spacingddof1/SparsityNN. HV ref1.1 fixo,
4 scrambles,Sobol níveis13–16;escalada global predefinida18/20 apenas se falhar
precisão nas referências;exato<=8 caixas. Congelar resolução após estudo independente.
Zeros artificiais/precisão insuficiente permanecem pendentes,sem fabricar confiança.
Oráculo somente referência/avaliação externa;busca futura usa RSMs ruidosos10B.
API preserva decisões brutas,viabilidade,identidade,ND emtodosm ecasos indefinidos.
Equalização somente plano,não executar. Subpacote synthetic/pareto separado de
RSM e do top-level10A,testes históricos intactos. Seis figuras EN,PNG600/PDF,
sem grades nem projeções decorativas nx5. MDR0015/policy10C antes da geração.
Não executar C-NBI,VRF-NBI,EAs,novascalibrações,CCD,ruído,RSM,seleção réplicas,
benchmark,significância ou10D. Novo PR fica aberto,sem merge. Escopos abaixo históricos.

## Escopo atual — Fase10B, autorizado em2026-10-29

PR14 integrado por merge d68aef7,árvore idêntica a489aa0e; CI40906784465 verde
Ubuntu/Windows. Desenvolver somente feature/10b-synthetic-rsm-generation.
Consumir27 configurações10A exatas; nunca recalibrar anchors ou editar ciência0–10A.
CCDs completos13/19/47,cinco centros independentes; manter8 fatoriais nx3 fora
da bola,sem projeção. Cinco réplicas por célula,135 RSMs/3555 corridas/990 respostas.
Um ruído Gaussiano iid:var(f no CCD completo,ddof1)/19,95% sinal em expectativa.
Seeds PCG64 por cenário/réplica/master,protocolo congelado antes da campanha.
OLS/diagnóstico somente pelas APIs existentes; sem nova OLS,seleção de termos,
clipping,reescala,convexidade imposta ou regularização. Preservar Sigma_e bruta,
inclusive singular.27 certificados sem ruído;4096 Sobol externos por cenário,
separados e compartilhados pelas cinco réplicas,sem seleção por qualidade.
Oráculo analítico só geração/validação;interface futura somente RSM ruidoso salvo.
Todos135 preservados;seis figuras EN,PNG600/PDF vetorial,sem grades. Não executar
C-NBI,VRF-NBI,EAs,Pareto/referência/métricas ou benchmark. Novo PR permanece aberto.
MDR0014 e docs/policies/synthetic_generation_10b.json definem este escopo;
licenças/dados originais permanecem inalterados. Seções seguintes são históricas.
Implementação10B no subpacote cnbi_v2.synthetic.rsm;top-level10A e teste AST
histórico permanecem intactos. Reorganização estrutural não altera o protocolo.

## Escopo atual — consolidação e Fase10A, autorizado em2026-10-29

O responsável confirmou direitos e divulgação pública dos itens/metadados
auditados; aprovou MIT apenas para código original. Ver LICENSE_SCOPE.md e
docs/data_publication_permissions.md. Sem MIT/CC implícita para outros materiais.
PR11/12 integrados por merge commit, preservando SHAs/ancestralidade e resultados0–9.
Concluir documentação/CI antes de feature/10-synthetic-scenario-generation.
Somente27 configurações estruturais: f_j=||x-a_j||², MIN, nx2/3/5,
alpha=2**(nx/4), delta1/3/5, m=nx+1+delta, mean(abs(Pearson)) .25/.60/.85,
erro<=.05. Sinal apenas observado. Calibração direta reproduzível, QMC uniforme
na bola, seeds distintas de calibração/validação, anchors distintos/viáveis e
posto geométrico completo. Correlação pode ser singular; sem regularização.
Falhas explícitas. Sem ruído,CCD,RSM,C-NBI,VRF-NBI,EAs,referência,métricas ou
estatística do benchmark,135 instâncias/540 runs. Novo PR10A sem merge automático.
Sem grades decorativas. Os escopos abaixo são registros históricos.

Prompt específico10A recebido após a consolidação:quatro tipos diagnósticos em
inglês,PNG alta resolução/PDF vetorial. CSV de correlações é o resumo por cenário;
matrizes completas em synthetic_correlation_matrices.npz. Preservar os1110
arquivos no frozen_inputs_manifest.json. Holdout nunca escolhe/reinicia âncoras.

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
Pacote de visualizações aplicado explicitamente autorizado em2026-10-25:
feature/09-applied-case-visualizations,base científica d938695 (correção Fase8).
PR11 permanece aberto; usar sua branch corrigida como base do PR visual,sem
merge automático. Somente fontes congeladas verificadas por hash/Git; baseline
H5 standalone409 ND,referência independente18503/zeroCNBI. Sem executar ciência,
refit,otimização,MC,anchors,PA,retuning ou recalcular métricas oficiais. Avaliar
coeficientes somente para desenhar a seção central; PCA,elipses e agregações
descritivas são transformações visuais explícitas,não mudanças do método.
Todas as figuras PT/EN compartilham dados,paleta,traduções e estilo centralizados.
Nome de exibição do método: VRF-NBI, sem qualificador histórico; IDs congelados
de arquivos/tabelas permanecem preservados.
Não usar grades de eixos; referências científicas como zero/limiar/domínio/K66
não são grades. Exportar PNG600dpi e PDF vetorial; SVG quando apropriado,com
omissão explícita do grid denso D3 (PDF vetorial preservado). C1 tem oito
exports individuais solicitados,alternativos ao painel. Não usar408 como baseline,
reconstruir referência,executar VRF ou publicar fora do repositório privado.
Fontes antigas permanecem imutáveis; resultados visuais em pasta própria com
catálogo,tabelas,legendas,auditorias e checksums. Escopos seguintes históricos.

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

Fase7 autorizada após squash do PR #9 com CI verde, branch
feature/07-pareto-reference-loo. H_base5 é decisão operacional do responsável;
H20 continua auxiliar da mesma família CNBI. Construir referência empírica pooled
e leave-one-family-out, sem auto-inclusão CNBI ao avaliar H5. Reavaliar todos x
elegíveis nos RSMs atuais; respostas históricas não são canônicas. Usuário autoriza
explicitamente transferir a calibração das metaheurísticas V1, mantendo fonte,
hashes e diferenças explícitas; não importar seus módulos ou reutilizar ambiente.
Usar pymoo consolidado/pinado, orçamento comum e30 seeds fixas, esfera por
amostragem factível/repair radial explícito. Congelar protocolo antes das runs.
Preservar proveniências, reconstruir ND após exclusão de família e distinguir
métricas LOO de métricas comuns self-included. ADR0011 ACCEPTED nesse escopo.
Sem rerodar MC/anchors/PA/NBI, sem verdade Pareto, superioridade, benchmark final,
refinamento adaptativo implementado ou merge do novo PR. Escopos abaixo históricos.

Fase 6 explicitamente autorizada após squash do PR #8 com CI verde: branch
feature/06-simplex-lattice-local-nbi. Consumir somente os37 IDs de B=2000,
RSMs codificados nominais e anchors/payoff preservados, bola alpha=8**0.25,
direções originais e sem RC. NBI local com normalização por subset, normal
unitária orientada ao ideal, igualdade e Jacobianos analíticos, SLSQP e
aceitação independente. Simplex-Lattice H={2,4,5,10,20}, malha-mãe20 com
membership inteiro exato; não resolver pesos repetidos. Reavaliar8 respostas
antes de deduplicação/ND full-space e cobertura interna em normalização global
fixa da Fase5. H20 é referência interna, sem verdade Pareto ou H final aceito.
ADR0010 ACCEPTED somente nesse escopo. Sem nova PA/MC/anchors, benchmark,
NSGA/MOEA/D/VRF ou métricas externas. Sem merge do novo PR ou próxima fase.
Escopos abaixo são históricos.

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
