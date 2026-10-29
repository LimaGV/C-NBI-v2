# Consolidação das Fases0–9 em2026-10-29

## Publicação e licença

Auditoria: docs/audits/public_repository_audit.md e inventário adjacente.
O responsável confirmou direitos e autorizou divulgação dos dados,derivados e
metadados identificados. Confirmou titularidade/autorização e MIT apenas para
código próprio. Registro: docs/data_publication_permissions.md e LICENSE_SCOPE.md.
Não foi aplicada CC BY/MIT aos dados,figuras e documentos, nem feita sanitização
silenciosa de raw/logs. Não houve mudança de visibilidade,reescrita de histórico
ou alteração de proteções GitHub. Recomendações de segurança permanecem na auditoria.

## Integrações verificadas

PR11: merge39069f3f9abb51af94f9044c1d3c668264590638, HEAD científico d938695.
Árvore exatamente igual à aprovada. Local:631 testes em72,43s,cobertura99,39%.
CI Ubuntu/Windows [40884548845](https://github.com/LimaGV/C-NBI-v2/actions/runs/40884548845):SUCCESS.

PR12 foi retargetado para main após essa validação e recebeu merge comum de
main,HEAD bd3ab2209dfac83c037ab0c95ba3b8f78777ab5a,sem force-push. Árvore
exatamente c6e97db,diff apenas343 arquivos da Fase9. Local:686 testes em87,55s,
cobertura99,39%,Ruff/mypy aprovados. CI4/4:
[40885152285](https://github.com/LimaGV/C-NBI-v2/actions/runs/40885152285) e
[40885162173](https://github.com/LimaGV/C-NBI-v2/actions/runs/40885162173):SUCCESS.

PR12 integrado embb5d6f215c6465777dd395bb8448329327f49c3b. A árvore consolidada
é byte a byte c6e97db,com ancestralidade d938695/c6e97db preservada. CI pós-merge
[40885779207](https://github.com/LimaGV/C-NBI-v2/actions/runs/40885779207):SUCCESS em Ubuntu/Windows.
Merge commit foi escolhido entre as opções habilitadas para preservar SHAs de
manifests/proveniências e evitar squash/rebase da stack. Nenhuma ciência foi alterada.

## Estado científico/documental

H5 standalone:492 subproblemas/aceitos,411 decisões únicas,409 ND,zero falhas.
Referência independente18503/zeroCNBI; métricas GD,IGD,HV,Spacing,Sparsity.
Os408 pontos extraídos de H20 são histórico substituído. NBI implementado desde
a Fase6. Fases8/9 concluídas e integradas. Figuras preservadas:46 entradas,
21 principais/25 suplementares,92 PT/EN,92 PNG600dpi,92 PDF vetoriais,90 SVG,
galeria,captions e331 hashes. Nome VRF-NBI; sem grades decorativas.

Atualizados:licença/escopo,permissões,CITATION,README,ROADMAP,CHANGELOG,estado
metodológico,reprodutibilidade,política de dados,comentários de ignore e AGENTS.
Relatórios/captions hashados permanecem históricos e intactos. Nenhum DOI,
release ou fonte foi inventado. Gate3 encerra após PR documental e CI.

## Limite da próxima etapa

Fase10A:uma configuração por célula3×3×3,funções isotrópicas,correlação absoluta
.25/.60/.85 com validação independente. Sinal observado, não fator. Sem ruído,
CCD,RSM,C-NBI,VRF-NBI,EAs,referência,métricas/estatística do benchmark sintético.

## Verificação documental

uv sync --locked,Ruff e mypy aprovados. Build wheel/sdist verificado: metadata
License-Expression: MIT e LICENSE_SCOPE.md incluído. Nenhum dado/resultado foi
empacotado como código. Quatro scripts de validação tiveram apenas a cópia de
trabalho normalizada CRLF→LF pelo checkout Git; seus blobs Git continuam iguais.
Todos os payloads científicos e os demais hashes protegidos permanecem intactos.

Suíte documental:686 testes passaram em88,23s,cobertura99,39%.
