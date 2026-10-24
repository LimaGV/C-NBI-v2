# Turning: Monte Carlo anchors and payoffs, Phase 4

Date: 2026-10-24. Run: turning_original_codes_anchor_mc_777_20261024.
Branch: feature/04-monte-carlo-anchor-reoptimization.
Numerical source commit: **ac9eb72af9f91de2b860df4b17ba8ab417e94e07**, dirty=false.
The later delivery revision adds this report and reviewed artifacts; metadata
identifies the actual numerical source commit separately from that descendant.

## Canonical frozen input and execution

Phase 3 run turning_original_codes_mc_777_20261024, coefficient_samples.npz SHA:
`5df42af4ef36fe6e2ce1948897d12a0d90a4a9f3449b1180898cf6adc9d84674`.
Its clean scientific source is 5a102dd337a5c9b7108fac6997b612c7d02a8684;
metadata SHA is 000888b8b35e88e22c4c42a62d8a8033254c78c4896cfa41925858569eaf7bcb.
The loader checked the pinned files, sample byte hash, finite float64 (2000,10,8),
term/response order, original seed 777 and metadata identity. No new draws,
OLS or residual covariance changes. Original-coded factors and full response
precision/scales remain those of Phase 2; the physical/publication fit is not used.

Raw dataset SHA: 7f905b7a2f7bb8b6735ab96900cba7356401df2d26c961dcb12faa2683c6c71e.
Nominal sphere-anchor SHA: 462b6b18002c2ae784758a26ebe500bf95de3a8ff1c504aab6986924d9d5bafd.
All **26** Phase 4 input hashes match both their source-commit Git blobs and
current files. All nine output checksums passed. Raw, prior nominal anchors,
Phase 3 ensemble/artifacts, model fitter, global solver and uv.lock remain intact.

Serial solve_quadratic_ball, unchanged defaults, alpha=8**0.25=1.681792830507429.
Directions T/MTTF/ROI/OEE MAX; WR/Ra/Rt/Kp MIN. No RC or response normalization.

- Attempted **16000**, certified successful **16000**, failed **0**.
- All **2000** payoffs available; failure_log.csv has header and zero data rows.
- Anchors **(2000,8,3)**, optimum/norm/cases **(2000,8)**, payoffs **(2000,8,8)**.
- Exact diagonal identity for all 16000 values: diag(A[b])=F_star[b].
- Maximum independently checked normalized stationarity approximately 1.7173e-15;
  complementarity 2.8088e-15; minimum shifted eigenvalue 8.1700e-06.
- Unchanged certificate tolerance 1e-10; spectral bound eps64*16*3;
  radial reporting tau=alpha*1e-10. No tolerance was loosened.
- Compute time **4.436183499987237 s**; total measured workflow time
  **4.640420899959281 s** (through payload writes, before metadata serialization).
- Mean per optimization **0.0002772614687492023 s** (0.277261 ms);
  mean per replica **0.0022180917499936186 s** (2.218092 ms).
  Compute timing includes extraction, solves, independent certificates and payoffs.

An additional full serial replay of the same frozen input (16000 verification
solves) reproduced anchors, optimal values, norms, cases, locations, masks,
certificates and payoffs **bitwise** in the same environment. Reported attempt
counts/times above refer to the canonical archived run, not this replay/tests.
The repeated-2000 nominal control separately confirmed 16000 actual calls and
recovered the archived nominal anchors/payoffs; there is no nominal substitution.

## Nominal references

Display tables round to nine significant digits; CSV/NPZ retain full float64.
All coordinates/displacements are in the original coded space. No physical
inverse transform is asserted.

| Response | x1 nominal | x2 nominal | x3 nominal | Nominal optimum |
|---|---|---|---|---|
| T | -1.53719111 | -0.525905413 | -0.434619494 | 66.1444764 |
| MTTF | -1.53649705 | -0.620505752 | -0.287361383 | 68.8976706 |
| WR | -1.37554995 | -0.539215823 | -0.803452391 | 0.00421457666 |
| Ra | -0.0778840625 | -1.53343206 | 0.276256839 | 0.280668816 |
| Rt | -0.00512706475 | -1.63266922 | 0.403474991 | 1.84046438 |
| Kp | 1.36847743 | 0.789240201 | 0.576885219 | 1.65000077 |
| ROI | 1.11366638 | 1.26001112 | -0.0233731887 | 0.306345653 |
| OEE | -1.20695368 | -1.17118986 | -0.00206190729 | 0.576892134 |


## Displacement distributions

Delta_x=||x_star[b,j]-x_nom[j]||. Sample std uses ddof=1; quantiles use linear
interpolation. Every statistic uses all 2000 certified realizations.

| Response | mean | median | std | q05 | q25 | q75 | q95 | max |
|---|---|---|---|---|---|---|---|---|
| T | 0.411098728 | 0.351218145 | 0.274436584 | 0.0840191335 | 0.214660574 | 0.541229721 | 0.94746698 | 1.9164968 |
| MTTF | 0.331706805 | 0.296239009 | 0.205479815 | 0.0736011082 | 0.179280325 | 0.441348652 | 0.707568981 | 1.60412913 |
| WR | 0.894104753 | 0.557789489 | 0.679063443 | 0.130593864 | 0.336900924 | 1.63064567 | 2.01108816 | 2.36875304 |
| Ra | 0.806864142 | 0.777786645 | 0.359753965 | 0.265095129 | 0.537379149 | 1.05726556 | 1.44083283 | 1.97993095 |
| Rt | 0.856716834 | 0.820460243 | 0.410121575 | 0.234196024 | 0.55278571 | 1.13393092 | 1.57479491 | 2.18024864 |
| Kp | 0.342086752 | 0.216996709 | 0.471225786 | 0.0553038928 | 0.134087918 | 0.316363396 | 1.86459306 | 2.61666992 |
| ROI | 0.189234637 | 0.167408635 | 0.117204763 | 0.0372646743 | 0.0993010132 | 0.256560147 | 0.416595122 | 0.753692755 |
| OEE | 0.0820030761 | 0.0765030153 | 0.0431909165 | 0.0219217753 | 0.0497009936 | 0.107170976 | 0.160506213 | 0.256195769 |


## Locations and solver cases

Fractions are between zero and one. Secular and hard boundary cases are counted
separately; geometric fractions use the radial tolerance, distinct from the
solver's case name. Counts sum to 2000 per response.

| Response | Interior fraction | Boundary fraction | Interior case | Secular boundary | Hard | Other | Failed |
|---|---|---|---|---|---|---|---|
| T | 0 | 1 | 0 | 2000 | 0 | 0 | 0 |
| MTTF | 0 | 1 | 0 | 2000 | 0 | 0 | 0 |
| WR | 0.0075 | 0.9925 | 15 | 1985 | 0 | 0 | 0 |
| Ra | 0.21 | 0.79 | 420 | 1580 | 0 | 0 | 0 |
| Rt | 0.126 | 0.874 | 252 | 1748 | 0 | 0 | 0 |
| Kp | 0 | 1 | 0 | 2000 | 0 | 0 | 0 |
| ROI | 0 | 1 | 0 | 2000 | 0 | 0 | 0 |
| OEE | 0 | 1 | 0 | 2000 | 0 | 0 | 0 |


Ra is nominally interior: **420/2000 (21%)** remain interior and **1580/2000
(79%)** are on the boundary. WR has 15 interior realizations (0.75%); Rt has
252 (12.6%). T, MTTF, Kp, ROI and OEE are on the boundary in every realization.
There were no hard cases in this real ensemble; synthetic hard/flat cases are
covered explicitly. No surface class is used to reject a coefficient realization.

## Estimated optimum distributions

These are distributions of optima of different sampled models, in native units.
They are not physical observations, deterioration measures or confidence intervals.

| Response | mean | median | std | q05 | q25 | q75 | q95 | min | max |
|---|---|---|---|---|---|---|---|---|---|
| T | 66.5574446 | 66.5274533 | 2.33510208 | 62.6895317 | 64.9382325 | 68.1630225 | 70.5060437 | 59.6989477 | 73.2651897 |
| MTTF | 69.2059424 | 69.202484 | 2.36858697 | 65.3204241 | 67.5917598 | 70.7829652 | 73.2231561 | 62.0490446 | 76.1283622 |
| WR | 0.00399427803 | 0.00400396689 | 0.000344088892 | 0.00342088249 | 0.00376633496 | 0.00422752389 | 0.00454983483 | 0.00294521639 | 0.0050269165 |
| Ra | 0.143648608 | 0.154005537 | 0.175063975 | -0.168048745 | 0.0306657222 | 0.26674433 | 0.409128594 | -0.482238839 | 0.634413346 |
| Rt | 1.41288601 | 1.4563336 | 0.569563062 | 0.433098648 | 1.05258115 | 1.81409929 | 2.29200224 | -0.875479184 | 2.97040096 |
| Kp | 1.62606948 | 1.62596092 | 0.139612446 | 1.39588144 | 1.52990808 | 1.72393989 | 1.84873396 | 1.09688995 | 2.06765406 |
| ROI | 0.307078495 | 0.307139709 | 0.00558470367 | 0.298010441 | 0.303302993 | 0.310754103 | 0.316299958 | 0.28740989 | 0.325753887 |
| OEE | 0.577534399 | 0.577490026 | 0.00571887722 | 0.56822201 | 0.573855375 | 0.581545735 | 0.587262009 | 0.558076813 | 0.594936273 |


Signed delta_f=F_star[b,j]-F_nom[j] is stored in the NPZ; mean/q05/q95 delta_f
also appear in optimal_value_summary.csv. Ra and Rt include negative predicted
optima; these realized quadratic predictions were preserved, without clipping,
rejection or adding a new response constraint. Solver certification establishes
an optimum of each sampled surface, not physical admissibility/model adequacy.
Previous model-quality and plug-in approximation limitations remain relevant.

## Prefix sensitivity

Each row refers to the same archived outputs; no prefix reruns optimization.
E_A(B)=||mean(A[:B])-mean(A[:2000])||_F/max(||mean(A[:2000])||_F,eps64).
The target is the complete-ensemble mean, so E_A(2000)=0 **by definition**,
not a convergence certificate against a known population expectation.
Ra diagnostics illustrate the location sensitivity. All eight responses'
mean/median/q95 displacements and boundary fractions are in the 160-row
prefix_anchor_sensitivity.csv; the payoff CSV has exactly 20 rows.

| B | E_A | Ra median delta_x | Ra q95 delta_x | Ra boundary fraction |
|---|---|---|---|---|
| 100 | 0.0103094031 | 0.795112662 | 1.48863109 | 0.79 |
| 200 | 0.00587982892 | 0.747428887 | 1.43767527 | 0.765 |
| 300 | 0.00338963115 | 0.748446947 | 1.41712438 | 0.763333333 |
| 400 | 0.00285021174 | 0.741263758 | 1.38960861 | 0.765 |
| 500 | 0.0038617608 | 0.751218029 | 1.39712504 | 0.776 |
| 600 | 0.00451488074 | 0.750516453 | 1.42703172 | 0.775 |
| 700 | 0.0034822319 | 0.757459019 | 1.4773765 | 0.781428571 |
| 800 | 0.00227512956 | 0.756698567 | 1.46306338 | 0.785 |
| 900 | 0.00211824468 | 0.760836402 | 1.47564339 | 0.783333333 |
| 1000 | 0.00100730768 | 0.771556852 | 1.46668204 | 0.782 |
| 1100 | 0.000992877276 | 0.772514463 | 1.46668204 | 0.781818182 |
| 1200 | 0.000890783226 | 0.772083626 | 1.47681077 | 0.783333333 |
| 1300 | 0.00092938862 | 0.772514463 | 1.47564339 | 0.785384615 |
| 1400 | 0.000861565931 | 0.777786645 | 1.46668204 | 0.784285714 |
| 1500 | 0.000642079559 | 0.779198742 | 1.46256799 | 0.786666667 |
| 1600 | 0.000770272985 | 0.778740628 | 1.46256799 | 0.79 |
| 1700 | 0.000564091223 | 0.776835681 | 1.46152485 | 0.787647059 |
| 1800 | 0.000427283166 | 0.777786645 | 1.44083283 | 0.79 |
| 1900 | 0.000203266757 | 0.780542915 | 1.44226206 | 0.788947368 |
| 2000 | 0 | 0.777786645 | 1.44083283 | 0.79 |


No monotonicity is required and no B was selected by these errors. All prefixes
100:100:2000 were evaluated. Early stop is **NOT_APPLIED_PHASE_4**;
the future PA policy remains **PROPOSED**, with no fabricated PA/quantile/subset
outputs or stopping decisions.

## Archive, hashes and checks

[Reviewed run](../../results/phase_04_anchor_mc/turning_original_codes_anchor_mc_777_20261024/)
contains anchor_samples.npz, payoff_samples.npz, metadata.json, six CSV files
and checksums.sha256. Total payload **2178410 bytes**, approximately 2.18 MB.
Arrays, masks, original solver cases and certificate fields are preserved;
Unicode strings use fixed-width dtype and allow_pickle=False. No 2000 CSVs.

Array-byte SHA-256 (C-order, float64, little-endian in this run):
anchors=5ef6e37cbb1bc4bc1bbd46ad432b905f728971224b7f32deec6c80eb608dfcf3;
payoffs=336590ca4213cd9c9d6469ac71665d2db6e83b3e8eb9162f7dc3b5367fa1b850.
NPZ file hashes differ from array-byte hashes because they include container data.

| Output | SHA-256 |
|---|---|
| anchor_samples.npz | 0ece76217c22fb9c8a606b50aa8e8a787f9a7828083bc1f7e3bd5c74c5e28dba |
| anchor_summary.csv | 9c27abeb5283afc5ff16a0654308f6b4438498a3457e375dcba1c4340e311491 |
| failure_log.csv | bd9ac92d1619553321efe726b9eb0268e49ece7bfb8d17520df49eb9f4e2d3a5 |
| metadata.json | 6c5a81c75e2ca759f1daa54235b270f30527ed21fafe0d932c3e9bfc7b13250d |
| optimal_value_summary.csv | b964a2a6dd6ef6411afbd0cbe704cc41747cccd57b07a738dffb019497b29a78 |
| payoff_samples.npz | 98a12097a25cf2178e8ffce79499ad627cfb8345fd00a31b3b1521d88c6407d1 |
| prefix_anchor_sensitivity.csv | 29ff82746b3f67b48cfb9e53327b04d295433c5d8268fd51f7e90667b0440171 |
| prefix_payoff_sensitivity.csv | aa86b9d941879fcdf052880031b01d623504b6a47d798b6ae49c2d96d3c382dd |
| solver_case_summary.csv | 236ecc7f4678ec1adf054b8510b3ab23a7b00f58c0ea28ff6ba25332889c18e0 |


Locked sync, pytest -v, pytest --cov=cnbi_v2, Ruff and strict mypy passed:
**409 tests; 99.31% coverage (1149/1157); new anchor module and existing
scientific modules 100%; mypy 19 source files.** Only the same eight older
workbook-inspection statements remain uncovered. No new dependency/lock change.
CI is checked on the delivered PR head; see [verification](../phase_4_verification.md).

ADR 0007 ACCEPTED. C-MC-04 METHODOLOGICAL_DECISION, C-MC-05
MATHEMATICAL_DERIVATION, C-MC-06 METHOD_DEFINITION. Full chain and fixed-anchor
counterexample: [anchor_monte_carlo.md](anchor_monte_carlo.md).

All replicas reoptimized, no nominal fallback, RC, shrinkage, bootstrap, new
randomness, response normalization, CHIM/edge, dimensional SVD/PA, subset
selection, Nadir estimator or NBI/C-NBI. The global solver's internal linear
algebra is unchanged. No Phase 5 started.

Before Phase 5: review this PR; explicitly define normalization, CHIM/edge
orientation and dimensional-analysis validation, keeping frozen sample identity
and payoff conventions. The proposed PA stopping policy still needs actual PA
outputs and separate validation; present descriptive sensitivity does not apply it.
