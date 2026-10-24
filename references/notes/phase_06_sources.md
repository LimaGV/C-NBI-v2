# Phase 6 source and software audit — 2026-10-24

Zotero was searched first, read-only, using Normal-Boundary. Das/Dennis item
5R3KLTFK was found and its metadata rechecked: Indraneel Das, J. E. Dennis,
1998, *Normal-Boundary Intersection: A New Method for Generating the Pareto
Surface in Nonlinear Multicriteria Optimization Problems*, SIAM Journal on
Optimization8(3),631–657, DOI10.1137/S1052623496307510. No child attachment
was available. Status METADATA_VERIFIED; no FULLTEXT_VERIFIED, equation/page
attribution, protected document export or uninspected quotation is claimed.

The exact local normalization, unit geometric normal/sign, equality formulation,
solver tolerances, continuation and H schedule here are definitions supplied by
the explicit Phase6 request and recorded in ADR0010/local_nbi.md. Stars-and-bars
and exact nesting are direct mathematical derivations. None relies on an
invented passage in the original NBI paper. Local SLSQP feasibility acceptance
is not presented as global optimality or a proof of Pareto completeness.

Context7 resolved SciPy and NumPy, then queried primary software documentation:

- SciPy optimize tutorial: SLSQP equality/inequality dictionaries, analytic jac,
  constrained minimization conventions and result diagnostics:
  https://github.com/scipy/scipy/blob/main/doc/source/tutorial/optimize.rst
- NumPy SVD: full U contains left singular vectors and singular values are
  descending; matrix-rank default roundoff threshold s_max*max(shape)*eps:
  https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html
  and https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html
- SciPy spatial docs/release notes confirm cdist Cartesian-product distances;
  used only for Euclidean nearest distances in bounded blocks:
  https://github.com/scipy/scipy/blob/main/doc/source/release/0.7.0-notes.rst

No dependency was added. Actual locked package versions and code/input hashes
are recorded in the real run metadata. Context7 validates software interfaces,
not scientific choices. No external benchmark/front or new PA/MC was used.
