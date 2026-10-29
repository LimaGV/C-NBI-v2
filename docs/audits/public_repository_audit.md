# Auditoria do repositório público C-NBI v2

Data da verificação: **2026-10-29**, America/Sao_Paulo.
Repositório: [LimaGV/C-NBI-v2](https://github.com/LimaGV/C-NBI-v2).
Snapshot local auditado: `c6e97db8cf18b1927821b386231fb64a8342b431`.
Branch local deste relatório: `docs/public-repository-audit-20261029`.

**GATE 0: LIBERADO por declaração e autorização explícitas do responsável em 2026-10-29.**

Atualização após a auditoria inicial: o responsável confirmou os direitos e
autorizou a divulgação pública de todos os itens/metadados identificados;
aprovou também MIT exclusivamente para o código original. O registro completo
está em [permissões](../data_publication_permissions.md) e LICENSE_SCOPE.md.
As classificações PUBLIC_PENDING_AUTHORIZATION abaixo descrevem o diagnóstico
anterior a essa resposta. Para os itens identificados, a classificação atual
é PUBLIC_APPROVED para divulgação; isso não aplica uma licença aberta a dados,
figuras ou documentos. Riscos técnicos/recomendações continuam registrados.
Nenhuma configuração de segurança ou visibilidade foi alterada.

## Diagnóstico inicial preservado para rastreabilidade
O repositório não está declarado regularizado. Nenhum merge, alteração de
visibilidade, aplicação de licença ou reescrita de histórico foi executado.
A consolidação e a Fase 10A ainda não começaram.

A condição vem da Etapa 0.1 e do Gate 0 do pedido de consolidação: havendo
autorização incerta, "Não continuar automaticamente para os merges".
Este relatório é o resultado concreto para a decisão do responsável.

## Estado real do Git e do GitHub

GitHub CLI/API confirmaram visibilidade **PUBLIC**, `main` como branch padrão,
um colaborador com papel admin e nenhuma regra de proteção/ruleset configurada.
Os três HEADs conhecidos permanecem atuais após `git fetch origin`:

| Referência | HEAD remoto verificado | Estado |
|---|---|---|
| main | `f904e8de0810324b4456cf2ad7de59ca2c6b5ab4` | Fase 7 integrada; Fases 8/9 ainda não integradas |
| PR #11 | `d938695b7fdaf9c871d331a42ff277e0c3fbd2d1` | OPEN, MERGEABLE, base main |
| PR #12 | `c6e97db8cf18b1927821b386231fb64a8342b431` | OPEN, MERGEABLE, base branch do PR #11 |

As três branches locais correspondentes tinham divergência local/remota
`0/0`; o working tree estava limpo antes desta auditoria. O PR #12 continua
empilhado sobre `feature/08-reference-sensitivity-final-benchmark`.
As opções de merge commit, squash e rebase estão habilitadas, mas nenhuma
foi usada. O problema de exposição já existe na main e não depende do merge
dos PRs #11/#12.

| Evidência remota | CI verificada em 29/10/2026 |
|---|---|
| [main / run 40140306356](https://github.com/LimaGV/C-NBI-v2/actions/runs/40140306356) | SUCCESS, Ubuntu e Windows |
| [PR #11 / run 40203802291](https://github.com/LimaGV/C-NBI-v2/actions/runs/40203802291) | SUCCESS, Ubuntu e Windows |
| [PR #11 / run 40203806547](https://github.com/LimaGV/C-NBI-v2/actions/runs/40203806547) | SUCCESS, Ubuntu e Windows |
| [PR #12 / run 40220670761](https://github.com/LimaGV/C-NBI-v2/actions/runs/40220670761) | SUCCESS, Ubuntu e Windows |

São execuções anteriores, novamente consultadas; não foram apresentadas como
novas execuções em 29/10. CI verde não comprova titularidade ou permissão de
divulgação. As etapas 1/2 do pedido continuam suspensas pelo Gate 0.

## Escopo e método

Foram inventariados 1.111 arquivos no snapshot da Fase 9: 31 em data/, 23 em
references/, 849 em results/ e os demais em código/documentação/configuração.
A main contém 494 arquivos, o HEAD do PR #11 contém 774. As duas planilhas,
as extrações e os vetores externos abaixo estão nas três referências.
O fixture de métricas do legado também está nos HEADs dos PRs #11/#12.

A inspeção das planilhas leu somente ZIP/OOXML e propriedades dos arquivos.
Não abriu Excel, resolveu links, calculou fórmulas, materializou caches,
exportou planilhas nem salvou os originais. Os hashes anteriores e posteriores
coincidem. Nenhuma observação experimental é reproduzida neste relatório.

Foi realizada uma varredura heurística dos objetos Git alcançáveis pelas refs
locais, após o fetch: 1.904 objetos, incluindo 1.020 blobs de texto
(127.764.411 bytes) e 357 blobs binários. Foram procurados padrões de tokens
GitHub, AWS, Google, Slack, OpenAI, chaves privadas e atribuições literais de
segredos. Não houve candidatos reconhecidos nem arquivos com nomes típicos de
credenciais entre os objetos examinados. Gitleaks/TruffleHog não estavam
disponíveis; não se atribui a esta varredura a cobertura desses produtos.

Também foram lidos os logs disponíveis das quatro execuções CI citadas:
16 membros de arquivo, 350.258 bytes, sem candidatos aos padrões de tokens
e chaves privadas examinados. Os logs contêm caminhos de ambiente de runner.
Esses achados não constituem certificação de ausência de segredos. Objetos
binários, todos os logs antigos, artifacts, caches, forks e objetos remotos
inacessíveis não foram examinados exaustivamente. Não foram persistidos ou
reproduzidos valores de tokens, identidades pessoais ou alvos completos de links.

## Critérios de classificação

- **PUBLIC_APPROVED:** evidência suficiente de permissão pública para o item
  e seu conteúdo, sem estender automaticamente essa permissão a derivados.
- **PUBLIC_PENDING_AUTHORIZATION:** permissão pública ou titularidade ainda
  não comprovada. Publicação já existente não é evidência de autorização.
- **RESTRICTED:** material cuja divulgação não foi autorizada e que deve
  permanecer fora da publicação, como obras integrais de terceiros e credenciais.

Nenhum conjunto de dados experimentais foi promovido a PUBLIC_APPROVED.
A classificação abaixo é uma avaliação para divulgação; não altera os campos
históricos de metadata, os bytes científicos ou a política de armazenamento.

| Artefato/grupo | Classificação | Evidência e decisão necessária |
|---|---|---|
| data/raw/turning_application/CCD_original.xlsx | PUBLIC_PENDING_AUTHORIZATION | provenance.yaml autoriza somente o repositório privado; dataset.yaml registra public_redistribution_authorized: false |
| data/raw/turning_application/CCD_values_20261023.xlsx | PUBLIC_PENDING_AUTHORIZATION | values_20261023/provenance.json restringe o escopo a private repository only |
| data/processed/turning_application/CCD_values_20261023.csv | PUBLIC_PENDING_AUTHORIZATION | Extração literal do workbook atualizado; remover apenas o XLSX não retira estas observações |
| data/processed/turning_application/original_coded_factors.csv | PUBLIC_PENDING_AUTHORIZATION | Dados do mesmo experimento, não um exemplo sintético independente |
| data/external/turning_reference/vrf_historical_decisions.csv | PUBLIC_PENDING_AUTHORIZATION | 66 decisões VRF-NBI reutilizadas do legado; autorização de reutilização científica não documenta por si só a redistribuição pública |
| tests/reference_cases/legacy_metrics/spacing_oracle.npz | PUBLIC_PENDING_AUTHORIZATION | Fixture de dados do legado, com proveniência registrada; verificar escopo de redistribuição |
| results/phase_02_anchors/ até results/phase_08_final_benchmark/ | PUBLIC_PENDING_AUTHORIZATION | Resultados derivados do caso aplicado; confirmar autoria, restrições dos dados de origem e divulgação dos artefatos/logs |
| results/applied_case_visualizations/turning_visuals_20261025/ | PUBLIC_PENDING_AUTHORIZATION | Figuras/tabelas do mesmo caso; confirmar direitos de publicação separadamente da licença de código |
| data/metadata/turning_application/ e metadados de execução | PUBLIC_PENDING_AUTHORIZATION | Revisar exposição de autoria/caminhos e alinhar permissões; hashes não concedem direitos |
| tests/reference_cases/turning_8responses/ e notas científicas | PUBLIC_PENDING_AUTHORIZATION | Referência numérica transcrita da publicação; manter atribuição e revisar escopo, sem usar MIT como autorização sobre o artigo |
| src/, scripts/, testes de código e configuração própria | PUBLIC_PENDING_AUTHORIZATION quanto à licença proposta | Confirmar titularidade e aprovação MIT; a ausência de licença continua explícita |
| PDFs integrais de artigos/livros, biblioteca Zotero e credenciais | RESTRICTED | Não encontrados como payloads de obras integrais no HEAD auditado; não incorporar ou relicenciar |

As referências bibliográficas factuais já publicadas (DOI, título, autores)
não equivalem a uma cópia do artigo. Não foi encontrada obra integral em
references/ ou em outra pasta do HEAD; os 118 PDFs do HEAD da Fase 9 estão
em results/, com finalidade de exportação gráfica. Isso não é aprovação
automática das permissões dos dados usados nas figuras.

## Riscos e ações recomendadas

| ID | Risco/localização | Evidência | Ação recomendada |
|---|---|---|---|
| P01 | Divulgação dos dois CCD e extrações, já na main pública | Autorizações limitadas ao privado; campo público explicitamente false | Obter confirmação dos titulares para os itens e derivados, ou conter a exposição enquanto se decide |
| P02 | Vínculos e identidade no CCD_original.xlsx | 152 fórmulas externas; duas relações externalLinkPath, uma file URI com diretório de usuário e outra relativa; creator/lastModifiedBy preenchidos | Revisar consentimento de divulgação; preservar raw original; eventual cópia sanitizada seria um artefato novo com hash/proveniência próprios e exige decisão |
| P03 | Identidade em CCD_values_20261023.xlsx | Sem fórmulas ou relações externas detectadas; creator/lastModifiedBy preenchidos | Revisar publicação desses metadados sem editar o raw silenciosamente |
| P04 | Caminhos locais em documentação/logs versionados | Localizações abaixo | Decidir se a divulgação é necessária; correção editorial futura não remove versões anteriores |
| P05 | Dados reaproveitados do legado e derivados | Vetores VRF-NBI, fixture de métricas e source_provenance.json | Confirmar licença/permissão específica aplicável; não herdar autorização global da V1 |
| P06 | Licença inexistente para o código novo | LICENSE_DECISION_PENDING.md; pyproject sem license | Confirmar titularidade, responsável/copyright e aprovação MIT com exclusões expressas |
| P07 | Ausência de proteção da main | Endpoint de branch protection retorna Branch not protected; lista de rulesets vazia | Após a decisão, exigir PR e CI Ubuntu/Windows, impedir force-push/exclusão e rever bypass admin |
| P08 | Alertas/prevenção de segredos desativados | security_and_analysis; secret scanning API informa disabled | Habilitar recursos apropriados por decisão do responsável e repetir auditoria com ferramenta dedicada |
| P09 | Dependabot indisponível | Updates disabled; endpoint de alerts responde disabled/403 e informa escopo insuficiente | Revisar configuração/escopo por decisão; não interpretar falta de acesso como zero vulnerabilidades |
| P10 | Direitos de dependências e fontes das figuras | Inventário de pacotes/licenças; fonte DejaVu usada nas figuras | Preservar termos/avisos de terceiros; revisar redistribuição de wheels/fontes antes de release |

P04 foi localizado, sem reproduzir os valores pessoais, em:

- docs/environment_verification.md: linhas 4, 28, 29;
- docs/legacy_reference.md: linha 8;
- docs/mathematics/coefficient_monte_carlo.md: linha 164;
- docs/phase_0_5_verification.md: linha 3;
- results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/timing_launch.json:
  linhas 54, 64.

Esses números referem-se ao snapshot c6e97db. O scanner também marcou dois
trechos de código como e-mails; a revisão mostrou operações matriciais com
`@`, falsos positivos. Não foram relatados como endereços pessoais.
Metadados de autoria Git e identificadores bibliográficos/Zotero também são
superfícies públicas a revisar; seus valores não foram copiados para este relatório.

As permissões padrão de Actions são read; o workflow declara contents: read,
não autoriza aprovação de PR pelo bot e fixa as duas actions por SHA. Actions
está habilitado com allowed_actions=all. Estes controles observados não
substituem proteção da branch, revisão das permissões de dados ou secret scanning.
Nenhuma dessas configurações foi alterada durante a auditoria.

### Contenção e histórico

Recomenda-se **tornar temporariamente o repositório privado** enquanto a
autorização de P01–P05 é esclarecida. A mudança não foi executada: este pedido
autoriza a auditoria e recomendações, sem transformar a mudança anterior para
público em permissão sobre os dados.

Retirar um arquivo no HEAD, acrescentar .gitignore ou mudar a visibilidade não
apaga os blobs antigos nem recolhe cópias/forks já feitos. As duas planilhas e
suas extrações estão também no histórico da main. Uma eventual limpeza precisa
considerar branches, tags, refs de PR, caches e cópias externas, preservando uma
cópia restrita de evidência. Não foi usado filter-repo, BFG ou force-push.
Uma reescrita ampla mudaria SHAs usados pela proveniência/testes e necessita
autorização específica e plano próprio. [GitHub: remoção de dados](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository),
[visibilidade e forks](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility).

## Licença: recomendação, sem aplicação

A API do GitHub identifica LICENSE_DECISION_PENDING.md como Other/NOASSERTION;
isso não equivale a MIT. Não existe LICENSE aprovado. A V1 está pública e
identificada como MIT, mas esse fato não escolhe a licença do código novo nem
resolve direitos de dados experimentais ou de terceiros.

A proposta para revisão é **MIT exclusivamente para código original**, após
confirmação de titularidade e aprovação explícita do responsável. Antes de
aplicar, confirmar o nome do titular: CITATION.cff/Git identificam autores,
mas não substituem prova ou declaração de titularidade.

Escopo proposto: código próprio em src/, scripts/, arquivos de teste de código
e configurações próprias. Excluir expressamente data/, payloads de fixtures,
results/, figuras, documentos científicos, bibliografia/obras e materiais de
terceiros. Depois da aprovação, acrescentar LICENSE com o texto MIT e uma
política de escopo/exclusões no README e na documentação de dados. Não aplicar
MIT indiscriminadamente a todo arquivo do repositório. A licença de dados,
documentos e figuras permanece uma decisão separada; CC BY 4.0 é apenas opção
para material cujos titulares autorizem esse licenciamento, não um default.
[Texto MIT/OSI](https://opensource.org/license/mit),
[GitHub: licenciar um repositório](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

Inventário preliminar do ambiente instalado, sem redistribuir as dependências:

| Pacote | Versão observada | Evidência de licença |
|---|---|---|
| NumPy | 2.5.4 | License-Expression: BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0; inclui avisos adicionais |
| SciPy | 1.18.1 | Texto instalado com condições BSD de três cláusulas; componentes incluídos têm avisos próprios |
| pandas | 3.1.0 | BSD-3-Clause |
| scikit-learn | 1.9.1 | BSD-3-Clause |
| openpyxl | 3.1.5 | MIT |
| pymoo | 0.6.2 | Apache-2.0 |
| Matplotlib | 3.11.2 | Acordo próprio, classificado PSF; não substituí-lo por MIT |
| pytest / pytest-cov | 9.1.1 / 7.1.0 | MIT |
| Ruff / mypy | 0.17.2 / 2.4.0 | MIT, com avisos de componentes incluídos |
| ipykernel / JupyterLab | 7.4.0 / 4.6.4 | BSD-3-Clause / texto BSD do Project Jupyter |
| uv_build | pin0.12.23 no pyproject | Backend de build isolado; não instalado na venv examinada, licença não validada por esse inventário |

Importar essas bibliotecas não lhes aplica a futura MIT do projeto. Não foi
identificado nesses metadados um motivo para rejeitar a proposta MIT para
código original independente; isso não certifica compatibilidade de todos os
componentes transitivos, wheels nativos ou futuras formas de distribuição.
BSD/MIT/Apache e os termos próprios continuam exigindo os avisos aplicáveis
quando seus materiais forem redistribuídos. O arquivo LICENSE_DEJAVU instalado
contém condições de copyright/permissão para fontes; verificar os avisos
aplicáveis ao empacotamento dos PDFs/fontes. Nenhum aviso de terceiro foi removido.

CITATION.cff continua em 0.1.0.dev0, sem campo de licença, e seu abstract diz
que ainda não há algoritmos científicos. Esse texto está desatualizado para
o estado atual. Deve ser corrigido na etapa de documentação, sem inventar
DOI, release, coautores ou uma licença ainda não aprovada.

## Integridade científica e verificação realizada

O teste de integridade já existente
`uv run pytest tests/visualization/test_applied_figures.py::test_published_visual_archive -q`
passou: **1 teste**, 8,73s. Ele confere os 331 hashes do manifesto, fontes,
presença dos exports e PDFs sem imagens raster. Não é uma nova execução da
suíte completa nem uma calibração da Fase 10A.

O pacote mantém 46 entradas (21 MAIN/25 SUPPLEMENTARY), 92 variantes PT/EN e
274 exports; nome VRF-NBI, zero grades de eixos, baseline H5 standalone409 ND,
referência18503/zeroCNBI. O metadata preserva a base d938695 e o plotting
d4db093. As 37 combinações e todos os resultados permanecem congelados.
As duas planilhas mantêm os hashes:

```text
fd9c463efdcd62ff3d7eaa7eec18d9e112543675c30b1f36838beeb38deebf4a  CCD_original.xlsx
7f905b7a2f7bb8b6735ab96900cba7356401df2d26c961dcb12faa2683c6c71e  CCD_values_20261023.xlsx
```

O inventário complementar `public_repository_inventory.json` registra a
fotografia redigida da auditoria e hashes selecionados. Evidências operacionais
locais, sem payloads de segredos, ficaram em experiments/runs/, ignorado pelo
Git. O relatório não incorpora planilhas, artigo integral, observações ou
log bruto. Arquivos científicos preexistentes não foram modificados.

## Decisões necessárias e sequência restante

1. Confirmar autorização dos titulares para divulgação dos dois CCD, extrações,
   dados do legado e resultados/figuras publicados, ou aprovar contenção temporária
   em repositório privado enquanto essa autorização é obtida. Resolver também a
   publicação de metadados de autoria e caminhos nos arquivos identificados.
2. Confirmar titularidade e aprovação MIT somente para o código original, ou
   manter a decisão de licença pendente. Não presumir CC BY para os demais itens.
3. Se alguma remoção permanente for necessária, definir um procedimento próprio;
   esta auditoria não autoriza reescrever o histórico.

Sem resolver o Gate 0, PR #11 e PR #12 permanecem abertos nos SHAs acima,
main continua em f904e8d, e não foi criada a branch da Fase 10A. Nenhum dos
27 cenários foi gerado ou validado nesta execução; correlações, erros, tempos
de calibração e métricas sintéticas permanecem não executados, sem números
fabricados. Os gates de consolidação/documentação ainda precisam ser satisfeitos
antes de abrir feature/10-synthetic-scenario-generation.

As fontes oficiais de software foram consultadas via Context7 (/github/docs)
e páginas oficiais GitHub/OSI. Elas fundamentam o funcionamento do serviço e
os termos citados; não foram tratadas como prova de autorização dos titulares.

## Verificação posterior à autorização

uv sync --locked, Ruff e mypy foram aprovados. Todos os1.111 arquivos
preexistentes tinham os mesmos hashes ao encerrar a coleta inicial; apenas
documentação/licença recebem alterações posteriores autorizadas. As planilhas,
código científico e resultados congelados permanecem intactos.

As etapas de integração e Fase10A podem prosseguir sequencialmente. O estado
de integração será registrado no documento de consolidação, sem apresentar
o diagnóstico inicial acima como o estado final do projeto.
