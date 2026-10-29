# Phase10D v1 migration provenance

Authorized source: https://github.com/LimaGV/C-NBI, branch cnbi-v1.0,
commit7bd4915a9aea94b9dca1d70014ba5186b4b4e44d. Local and remote committed SHAs
match. The local v1 has uncommitted work; only committed blobs are consulted.
No original v1 file, environment or result is modified. A temporary isolated
snapshot is used only to execute the required migration regression/oracles.
There are no v1 imports in the v2 production package.

| v1 source | Use in v2 |
|---|---|
| comparators.py: vrf_factor_count | max(2,k90), separate admissibility |
| comparators.py: rotated_factor_scores, factor_score_transform | correlation loadings, Varimax, loadings-based score weights |
| comparators.py: run_vrf | auxiliary factor RSMs, full VRF, targets, normalization, payoff, NBI |
| comparators.py: run_ea, ea_budget | explicit pymoo operators, dimension-specific calibration, ceiling and full-generation rule |
| ea_calibration.json, calibrate_eas.py, BUDGET_POLICY.md | 18 previously selected configurations and provenance; no new calibration |
| solver.py, cnbi/combinations.py | VRF-only affine NBI, lexicographic lattice and nearest-neighbor traversal |
| VRF_ARTICLE_AUDIT.md, revise_vrf_faithful.py, revise_doe_vrf_faithful.py | exclude the incorrect direct-score variant |
| experimental_results/VRF_FAITHFUL_SUMMARY.json | prior validation evidence only; no reused fronts |
| cnbi_experiments/tests/test_extension.py | isolated VRF retention/score/full-function regression |

Exact source blob SHA256 values are archived in algorithm_provenance.json.
The v1 ORIGINAL_LICENSE.txt is MIT, copyright(c)2026 LimaGV; its complete notice
is preserved in references/software/phase10d_cnbi_v1_MIT.txt. Varimax SVD/Kaiser
iteration is adapted from factor-analyzer0.5.1; its complete license is separately
preserved. These adapted portions are not asserted to be original v2 code.
Data, results, figures and scientific documents retain their existing separate
license scope. No excluded material's license is changed.

Pereira et al., DOI10.1016/j.engappai.2025.112510, was found in Zotero item
SMMX47JT without an attachment. The previously verified local PDF was read
directly, pp6–7: score formula Eq11, full quadratic Eqs17–20, full VRF
Eqs21–22, target Eq23, payoff/normalization Eqs24–26. Relevant-page status:
FULLTEXT_VERIFIED. The PDF itself is not copied into Git.

Registered adaptations before pilot:

- Radius generalized to2^(nx/4); the old RSM adapter uses a fixed3-variable radius.
- Canonical frozen v2 observations/coefficients replace v1-generated noisy RSMs;
  the original 135 models are never refitted.
- Paper Eq21 variance is sum of squared loadings; v1 multiplies it by rho.
  Correct raw constants, preserve the mathematical normalized objective;
  archive the discrepancy and compare normalization invariants explicitly.
  Preserve v1's optimization constant gauge internally; export the gauge shift,
  published variance/utopia/nadir and internal constants separately. A direct
  algebraic/numerical oracle verifies translation invariance. This correction
  addresses failed migration payoff comparisons caused by quartic-flat minima;
  it does not loosen the comparison limit or tune a scientific parameter.
- Existing v2 OLS/diagnostic APIs fit auxiliary factor models. Original v1 uses
  direct least squares. Technical comparisons cover scores, targets and payoff.
- Pure numerical radial repair moves boundary points one ULP inward. Initialization
  is uniform in the correct ball; no true-anchor initialization is allowed.
- Explicit operator defaults prevent silent pymoo-version changes: SBX variable
  probability.5, exchange1, binomial.5; PM individual1/nx and variablemin(.5,1/nx),
  at_least_onceFalse; MOEA/D PBItheta5 and the transferred neighbor fraction.
- v1 floors the generation count; the ceiling is not a promise to exhaust every
  evaluation. Actual NFE and remainder are exported without silently overshooting.
- Raw failures/trials are retained. Independent offline evaluation uses the strict
  unchanged Phase10C sphere test, not the legacy algorithm's feasibility tolerance.

No adaptations are selected using new benchmark quality. The exact technical
comparison outcomes and relevant legacy test log accompany the migration audit.
