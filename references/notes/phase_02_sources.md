# Phase 2 source audit — 2026-10-24

Zotero was searched first, read-only; no items, notes or attachments were added.
No PDF, notebook or original XLSM was copied into Git. PARTIAL describes direct
reading of identified passages, not an invented full-text verification.

## Maia (2020) — verified antecedent at anchor-definition stage

- Paulo Roberto Maia, *Método de Interseção Normal à fronteira por escores
  rotacionados em espaço elíptico de solução*, doctoral thesis, Universidade
  Federal de Itajubá, October 2020. No DOI or Zotero key verified.
- Zotero query Maia returned no item. Local title pages directly inspected;
  source: Documents/Dissertação/02_REFERENCIAS/dissertacoes_modelo/Tese_2021012.pdf.
- Primary institutional identity:
  https://repositorio.unifei.edu.br/jspui/bitstream/123456789/2309/1/Tese_2021012.pdf.
  Institutional defense catalog records 16/10/2020; local title page says
  submitted for examination 10/10/2020. Do not conflate these dates.
- 137 PDF pages, SHA256
  4e5e43dc01f1dd4b40929828466ffc8ba78bccba821780a31927404702f3ed0a.
- Status PARTIAL: printed pp.19-21 (PDF 36-38), p.84 (PDF 101), p.107 (PDF 124)
  read directly. PDF 38 and 101 rendered and visually verified.
- p.21: considers the elliptical restriction when defining anchor points;
  p.84: describes its addition during individual optimization and reports
  resulting frontiers inside the considered ellipses.
- pp.19-21 discuss ideal-centered phi and prediction-covariance quantities.
  They do not directly justify attributing phi=mean(Y) and observed-cloud S_Y to
  Khuri/Conlon. The current cloud formula is a distinct experimental definition.
- The local 2013 master's dissertation *Método do vetor gradiente multivariado*
  is a different work (91 PDF pages, SHA f4e9e85c25f607fdc37b54467f6c1f3ca0a31f0558a0b579dc279c2367329078).
  Its title pages/method chapter were checked and it was not used as evidence
  for NBI anchors or this restriction.

## Khuri and Conlon (1981) — metadata only

- A. I. Khuri; M. Conlon, *Simultaneous Optimization of Multiple Responses
  Represented by Polynomial Regression Functions*, Technometrics 23(4),
  363-375, 1981. DOI 10.1080/00401706.1981.10487681.
- Zotero QNCQQVYI, METADATA_VERIFIED; child is a DOI note, no PDF attachment.
- No direct full-text equations attributed to this article. Maia's discussion
  remains secondary evidence with its own limitations.

## Quadratic trust-region global characterization

- Jorge J. Moré, *Generalizations of the trust region problem*, January 1993,
  Argonne author preprint MCS-P349-0193, 23 PDF pages.
- Primary PDF https://ftp.mcs.anl.gov/pub/tech_reports/reports/P349.pdf.
  Status PARTIAL: introduction, PDF p.3, directly read: stationarity with
  nonnegative multiplier, feasibility, complementarity and PSD shifted Hessian
  characterize the global minimizer for general quadratics without convexity.
- David Bindel, Cornell CS 4220 lecture *Trust regions*, 20 April 2026:
  https://www.cs.cornell.edu/courses/cs4220/2026sp/lec/2026-04-20.html.
  Sections "The trust region subproblem" and "Exact solves" read directly,
  distinguishing interior, boundary and hard case. Code is independently derived;
  no source algorithm is copied.

## Anchors and payoff literature

- Pereira et al. (2025), R001/SMMX47JT, already FULLTEXT_VERIFIED: section 4.1
  and Table 4, PDF pp.13-14, describe individual optimization/payoff storage.
  This supports the individual-anchor definition, not adoption of a later NBI step.
- Das and Dennis (1998), Zotero 5R3KLTFK, metadata reconfirmed:
  *Normal-Boundary Intersection: A New Method for Generating the Pareto Surface
  in Nonlinear Multicriteria Optimization Problems*, SIAM Journal on Optimization
  8(3),631-657, DOI 10.1137/S1052623496307510.
  No Zotero PDF. Author preprint TR96-19 (July 1996) identified at Rice but web
  access returned 403; do not invent passages or identify preprint with journal
  pagination. No NBI implementation is imported or implemented in Phase 2.

## Threshold and covariance meanings

- NIST/SEMATECH, sections 6.3.4.1 and 6.5.4.3, directly read:
  https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc341.htm and
  https://www.itl.nist.gov/div898/handbook/pmc/section5/pmc543.htm.
  Explicit sample mean/covariance, IID MVN assumptions and Hotelling mean-test
  F distribution. The text warns that mean-test limits do not apply directly
  to control charts; Phase I/II differ. No automatic threshold transfer.
- A finite-sample independent-new-observation bound is mathematically derived
  in multivariate_response_region.md from the IID MVN premise. It is not
  asserted as applicable to this fixed DOE or chosen as its canonical cutoff.
- Population chi-square content, mean confidence, future prediction, tolerance
  content/confidence and empirical in-sample quantiles are distinct targets.
  C-RC-02 remains UNVERIFIED after this focused review.

## Original computational sources and coding

- Local NBI Revisão.xlsm: SHA256
  7792a25a8c88d29206665d8797587dc6a11e932e1a8bba0a1ac8b539385f7d4e.
  Original Data!B4:H22 literal IDs/coded/physical values read without caches,
  recalculation, save or modification. Physical factors and IDs match CCD exactly.
  Coded axial values are +/-1.682; no continuous decoding is certified.
- Literal extraction/provenance:
  data/processed/turning_application/original_coded_factors.csv and
  data/metadata/turning_application/phase_02_coding.json. No responses extracted
  from the linked/formula areas of the original XLSM are used as observations.
- Author repository https://github.com/Matheuscp98/VrfNbiPython, commit
  ce0fe1637c6398b56e0f7d1e7cd4cab1591635a6, inspected read-only via GitHub CLI.
  Current responses.xlsx (SHA256 81f0ab9ca271653e32bf54664b105c72d8c7d656bfb6ccd20622a659a46e1a9d)
  contains 24 CFD runs with eight different headers, not this 19-run turning case.
  The notebook constructs four factors/alpha=2 and excludes a factorial row.
  The local VRF-NBI(Matheus).ipynb has that same four-factor setup. Neither is
  used as the source of turning factors or responses.
- VrfNbiVba README/tree inspected; publicly listed files include VBA code,
  illustrations and an MCDM CSV, not a matching literal 19-run turning workbook.
  No VBA routine, v1 package or its architecture is copied into C-NBI v2.

## Software documentation

Context7 resolved SciPy -> /scipy/scipy and read current docs for SLSQP analytic
objective/constraint Jacobians, c(x)>=0, ftol/maxiter/result status, and brentq
bracketing/xtol/rtol. NumPy official stable docs (Context7
/websites/numpy_doc_stable) verified method='linear' for empirical quantiles.
These are API references, not scientific validity evidence. Runtime stays
locked NumPy 2.5.4/SciPy 1.18.1, with no new dependency.
Serena was activated on C-NBI-v2 with Python LSP; RSMFit, canonical term order
and dependencies were inspected semantically before adding separate modules.
