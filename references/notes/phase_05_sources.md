# Phase 5 sources and attribution limits

Date checked: 2026-10-24. Zotero searched first, read-only. No attached PDFs were
available for the four matched items; no documents or Zotero writes were made.

## PA context — R006

John L. Horn (1965), *A Rationale and Test for the Number of Factors in Factor
Analysis*, Psychometrika 30(2),179-185, DOI 10.1007/BF02289447.
Zotero RCPDPDRD. Metadata and abstract verified against
[the publisher](https://www.cambridge.org/core/journals/psychometrika/article/abs/rationale-and-test-for-the-number-of-factors-in-factor-analysis/54A5318A9F0548C2EC9606C278FCAE15).
Status: PARTIAL (publisher abstract); not FULLTEXT_VERIFIED.

The abstract motivates separating sampling-related latent-root contributions
using generated random variables in factor analysis. This establishes historical
context, not identity with the CHIM procedure. The v2 reference distribution is
the SVD of propagated payoff perturbations after anchor reoptimization, under a
fixed nominal normalization; q95, strict local decisions and their domain are
the responsible researcher's explicit Phase 5 definition.

## Centering/SVD spectral context — R007

Ian T. Jolliffe and Jorge Cadima (2016), *Principal component analysis: a review
and recent developments*, Philosophical Transactions of the Royal Society A
374(2065),20150202, DOI 10.1098/rsta.2015.0202. Zotero A7EM5INX.
Metadata matched Zotero and the [author article in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4792409/).
Status: PARTIAL, section 2(a), discussion surrounding Eqs.(2.2)-(2.5), directly
read in HTML; not a claim of reading the whole paper.

The inspected passage relates centered data, SVD, nonnegative ordered singular
values and low-dimensional geometry. Here vertices are columns, so the centering
operator acts on the right. The specific proof that centered vertex rank equals
affine CHIM dimension is supplied independently in the mathematical note; this
paper is contextual spectral support, not a source for the new PA threshold law.

## CHIM context and uninspected items

Das and Dennis (1998), *Normal-Boundary Intersection: A New Method for Generating
the Pareto Surface in Nonlinear Multicriteria Optimization Problems*, SIAM Journal
on Optimization 8(3),631-657, DOI 10.1137/S1052623496307510, Zotero 5R3KLTFK:
metadata reconfirmed, no attachment. METADATA_VERIFIED only; earlier access
limitations remain. No invented page/equation attribution. R001/Pereira's earlier
verified payoff/anchor context remains available in the existing source notes.

Xia/Zhou (2025), Zotero LPLWLE39, DOI 10.1177/00131644241268073, metadata found
for a PA sampling-variability study but no attachment. Not used to justify any
algorithmic step or claim of equivalence; no content claim inferred from its title.

Terminology throughout v2: **Monte Carlo uncertainty-calibrated Parallel Analysis /
PA-inspired spectral screening**. It does not establish a classical Horn test,
a universal dimensional estimator, physical model adequacy, simultaneous error
control or downstream NBI validity.

## API verification

Context7 resolved NumPy /websites/numpy_doc_stable; checked stacked
np.linalg.svd(compute_uv=False), descending singular values, matrix_rank's
roundoff default and np.quantile(...,.95,axis=0,method="linear").
API documentation supports implementation, not scientific equivalence.
