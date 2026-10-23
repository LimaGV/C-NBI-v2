# Fontes verificadas para a fundação RSM da Fase 1

Verificação em 2026-10-23, Zotero primeiro, somente leitura.
Escopo: referências diretamente pertinentes à regressão e seus segundos momentos.
Nenhum PDF ou texto integral é incorporado ao Git. PARTIAL não significa
FULLTEXT_VERIFIED; somente passagens efetivamente lidas são usadas nas claims.

## R002 — artigo de Díaz-García e Bashiri (2014)

- Título: Multiple response optimisation: An approach from multiobjective stochastic programming.
- Autores: José A. Díaz-García; Mahdi Bashiri.
- Applied Mathematical Modelling, 38(7-8), 2015-2027, 2014.
- DOI: 10.1016/j.apm.2013.10.010.
- Zotero: AXXUEWGY, My Library; sem child attachment.
- Status: METADATA_VERIFIED, por registro Zotero. Artigo final não inspecionado.
- Não atribuir páginas/equações do preprint à versão publicada.

## R003 — preprint dos mesmos autores, versão explicitamente identificada

- Título: Multiple response optimisation: Multiobjective stochastic programming methods.
- Autores: José A. Díaz-García; Mahdi Bashiri.
- Ano: 2011, arXiv:1105.2911v1, submetido em 14/05/2011, 17 páginas.
- Fonte primária: https://arxiv.org/abs/1105.2911v1 e https://arxiv.org/pdf/1105.2911v1.
- Não existe Zotero key verificada para esta versão; AXXUEWGY identifica o artigo de 2014.
- PDF temporário baixado da fonte primária, não incorporado.
- SHA-256: bc254539c8b4bb416b454291374aa6a93d710b2ed9ef803b503ac48ec9e980dc.
- Status: PARTIAL; seção 2 pp.2-3 lida diretamente, p.3 renderizada e conferida.
- pp.2-3 Eq.(3): Y=XB+E com projeto comum; p.3: OLS conjunto/por coluna,
  base quadrática, estimativa residual e covariância dos coeficientes.
- p.3 Eqs.(5)-(6): covariância populacional e estimada da média predita.
- A fonte escreve Cov(vec(B_hat^T))=V_X⊗Sigma. A implementação empilha B_hat
  por colunas, logo usa Sigma⊗V_X; a permutação está derivada e testada.
- Não alegar identidade textual ou igualdade integral entre preprint e artigo final.

## R004 — Myers, Montgomery e Anderson-Cook (2016)

- Título: Response Surface Methodology: Process and Product Optimization Using Designed Experiments.
- Autores: Raymond H. Myers; Douglas C. Montgomery; Christine M. Anderson-Cook.
- 4a edição, John Wiley & Sons, Hoboken, 2016.
- ISBN verificado na folha de copyright: 978-1-118-91601-8.
- Zotero: Z8Z2JEDC, My Library, sem PDF anexado; duplicata 677LYFGP também sem anexo.
- Cópia local identificada relativamente a Documents:
  `Dissertação/02_REFERENCIAS/artigos_pdf/Response_surface_methodology_process_z_library_sk,_1lib_sk,.pdf`.
- 855 páginas PDF; SHA-256: d1a4ea0659f9679ce2efe779643ac67cfc68b53f81a30329da2076eb8ce70644.
- Status: PARTIAL, metadados conferidos no Zotero e folhas iniciais do PDF.
- pp.16-17 (PDF 34-35), Eqs.(2.12)-(2.15): OLS e resíduos.
- pp.22-23 (PDF 40-41), Eqs.(2.16)-(2.18): covariância dos coeficientes,
  residual sum of squares, graus de liberdade e MSE.
- p.33 (PDF 51), Eqs.(2.39)-(2.40): média predita e sua variância.
- Passagens lidas diretamente; PDF 40 e 51 renderizadas para conferência visual.
- Não se implementam os intervalos que também aparecem nas páginas consultadas.

## R005 — Johnson e Wichern (2007)

- Applied Multivariate Statistical Analysis, Richard A. Johnson; Dean W. Wichern.
- 6a edição, Pearson Prentice Hall, 2007; Zotero ITYZMBYG.
- Status: METADATA_VERIFIED, não FULLTEXT_VERIFIED.
- Attachment Q9TB6VTG é linked_url, não arquivo local:
  `http://staff.ustc.edu.cn/~ynyang/vector/books/Johnson-Wichern-ENG.pdf`.
- Tentativa HTTPS falhou por timeout; nenhuma passagem usada como evidência.
- Busca Khuri retornou Khuri/Conlon (1981), sem consulta de texto; não se inventa
  uma cópia de Khuri/Cornell nem se acrescenta revisão ampla fora do escopo.

## R001 e fronteira das evidências

[Pereira et al. (2025)](pereira_2025_hybrid_vrf_nbi.md), já FULLTEXT_VERIFIED,
sustenta o caso quadrático publicado, não as hipóteses estatísticas do raw.
As derivações de covariância cruzada e de diferenças estão em
[rsm_uncertainty.md](../../docs/mathematics/rsm_uncertainty.md).
Os testes sintéticos são INTERNAL_EVIDENCE das implementações e identidades,
sem provar adequação do modelo ao torneamento ou reprodução da Table 3.
