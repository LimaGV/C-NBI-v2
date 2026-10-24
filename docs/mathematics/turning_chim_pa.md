# Turning: fixed-normalization centered CHIM and local spectral screening

Date: 2026-10-24. Run: turning_fixed_nominal_chim_pa_777_20261024.
Branch: feature/05-chim-svd-local-pa. Actual numerical source commit:
**257d1942b452c427b5f8ef7924fddf31975c3ad3**, working tree clean.
The artifact-delivery commit adds this report/results afterwards; metadata
continues to identify the actual source of the scientific computation.

## Frozen canonical inputs and validity

Nominal: Phase 2 **sphere-only payoff_sphere.csv**, not RC, a Monte Carlo mean,
a publication reconstruction or fixed-anchor reevaluation. SHA-256:
`2e410a2d3e222047442d75d526166c6af5e5d6787c2c93dcbe2b184003e124c2`.
Phase 4 payoff_samples.npz SHA-256:
`98a12097a25cf2178e8ffce79499ad627cfb8345fd00a31b3b1521d88c6407d1`;
scientific source ac9eb72af9f91de2b860df4b17ba8ab417e94e07, metadata hash
6c5a81c75e2ca759f1daa54235b270f30527ed21fafe0d932c3e9bfc7b13250d.
Finite float64 (2000,8,8), all validity masks, source metadata/order and diagonal
equality against archived Phase 4 optimal values were verified before analysis.
Phase 3 seed remains 777; no new draws, OLS, reoptimization or RC.

Dataset SHA: 7f905b7a2f7bb8b6735ab96900cba7356401df2d26c961dcb12faa2683c6c71e.
All **21** Phase 5 input hashes were checked against current files and their
committed source blobs. All ten output checksums passed. Replaying every
nominal/noise spectral computation from the frozen payoff arrays reproduced
all global/pair/triple/quadruple noise arrays bitwise in the same environment.
No prior scientific module, data, artifact, policy byte or uv.lock was altered.

## Orientation and one fixed normalization

Rows/responses and columns/anchors share order T,MTTF,WR,Ra,Rt,Kp,ROI,OEE.
MIN signs are (-1,-1,+1,+1,+1,+1,-1,-1), G=D_s A.
For nominal only: u_i=G_ii, a_i=max_j G_ij-u_i. Every replica uses
Z=(D_s A-u)/a with these same u/a. No clipping or per-replica normalization.
The diagonal-optimality and strictly positive/nondegenerate amplitude gates
passed with only the documented certificate/float64 allowances. Display values
are rounded to nine significant digits; artifacts retain full float64 precision.

| Response | Direction | Sign | Oriented Utopia u | Fixed amplitude a |
|---|---|---|---|---|
| T | MAX | -1 | -66.1444764 | 37.8316359 |
| MTTF | MAX | -1 | -68.8976706 | 38.1473199 |
| WR | MIN | 1 | 0.00421457666 | 0.00790169819 |
| Ra | MIN | 1 | 0.280668816 | 2.04198237 |
| Rt | MIN | 1 | 1.84046438 | 6.22808079 |
| Kp | MIN | 1 | 1.65000077 | 3.43944963 |
| ROI | MAX | -1 | -0.306345653 | 0.269476585 |
| OEE | MAX | -1 | -0.576892134 | 0.348822763 |


## Centered geometry and global screening

For every C use exactly matching response/anchor submatrix Z[C,C], then right
multiply by H_k=I-ones/k. Observed spectrum is SVD(Z_nom[C,C] H_k); uncertainty
reference is SVD(Delta[C,C] H_k), Delta=D_a^-1 D_s(A_b-A_nom), retaining k-1
components. No across-replica mean is subtracted from Delta. Nominal normalized
diagonal is zero, row maxima one; centered maximum absolute vertex sum is
**3.3306690738754696e-16**. Numerical centered rank and reference-difference rank
are both **7**, distinct from the uncertainty-screened leading dimension below.

q=.95, explicit linear quantiles, strict observed>q95, no added PA margin.

| r | Observed sigma | q95 B2000 | Margin | Pass |
|---|---|---|---|---|
| 1 | 2.91681179 | 1.1037221 | 1.81308969 | True |
| 2 | 0.912730323 | 0.57655301 | 0.336177313 | True |
| 3 | 0.165287374 | 0.300779067 | -0.135491693 | False |
| 4 | 0.0729834106 | 0.139830748 | -0.0668473372 | False |
| 5 | 0.0280071543 | 0.0583302952 | -0.030323141 | False |
| 6 | 0.00943317067 | 0.018330886 | -0.00889771532 | False |
| 7 | 0.000180591098 | 0.00229799285 | -0.00211740175 | False |


Global supported leading dimension: **2**. Pattern PASS,PASS,FAIL,FAIL,FAIL,FAIL,FAIL.
No NON_MONOTONE_PA_PATTERN occurred at any of the 20 checkpoints. This is a
conditional uncertainty-calibrated spectral screening result, not a classical
Horn factor test, physical-model validation or a reduction of algebraic rank to two.

## Local selection at B=2000

All candidates were assessed: **28 pairs, 56 triples, 70 quadruples =154**.
The global result did not prefilter any candidate. Selected: **19 pairs,
18 triples, 0 quadruples =37**, using every k-1 strict component comparison.
Exact selected identities follow (response labels are separated by pipes in CSV).


### Pairs (19)


| Subset ID | Responses |
|---|---|
| C_1_4 | T / Ra |
| C_1_5 | T / Rt |
| C_1_6 | T / Kp |
| C_1_7 | T / ROI |
| C_2_4 | MTTF / Ra |
| C_2_5 | MTTF / Rt |
| C_2_6 | MTTF / Kp |
| C_2_7 | MTTF / ROI |
| C_3_4 | WR / Ra |
| C_3_5 | WR / Rt |
| C_3_6 | WR / Kp |
| C_3_7 | WR / ROI |
| C_4_6 | Ra / Kp |
| C_4_7 | Ra / ROI |
| C_5_6 | Rt / Kp |
| C_5_7 | Rt / ROI |
| C_6_7 | Kp / ROI |
| C_6_8 | Kp / OEE |
| C_7_8 | ROI / OEE |


### Triples (18)


| Subset ID | Responses |
|---|---|
| C_1_4_6 | T / Ra / Kp |
| C_1_4_7 | T / Ra / ROI |
| C_1_5_6 | T / Rt / Kp |
| C_1_5_7 | T / Rt / ROI |
| C_1_7_8 | T / ROI / OEE |
| C_2_4_6 | MTTF / Ra / Kp |
| C_2_4_7 | MTTF / Ra / ROI |
| C_2_5_6 | MTTF / Rt / Kp |
| C_2_5_7 | MTTF / Rt / ROI |
| C_2_7_8 | MTTF / ROI / OEE |
| C_3_4_6 | WR / Ra / Kp |
| C_3_4_7 | WR / Ra / ROI |
| C_3_5_6 | WR / Rt / Kp |
| C_3_5_7 | WR / Rt / ROI |
| C_3_7_8 | WR / ROI / OEE |
| C_4_7_8 | Ra / ROI / OEE |
| C_5_7_8 | Rt / ROI / OEE |
| C_6_7_8 | Kp / ROI / OEE |


### Quadruples (0)


None selected. All 70 candidates were evaluated.


Every candidate's observed singular values, thresholds, margins, component
passes and selected flag are in local_pa_B2000.csv, including the 117 rejected
subsets. selected_subsets_B2000.csv contains exactly the 37 rows above.
No qmax, condition/ratio, volume/determinant, global-dimension, sampler-error or
anchor-displacement filter was used. No legacy count was a target/test oracle.

## Complete B trajectory and original early-stop policy

All 357 decision quantiles (7 global +350 local) were tracked for each of the
same 20 prefixes. The following maximum changes are relative ratios, not percent.
First-checkpoint NA has no predecessor. Eligibility starts at B=500 versus400.

| B | Global d | Pairs | Triples | Quadruples | Total | IDs changed | Max relative q change | Stop met |
|---|---|---|---|---|---|---|---|---|
| 100 | 2 | 19 | 22 | 1 | 42 | NA | NA | False |
| 200 | 2 | 20 | 18 | 0 | 38 | True | 0.293589949 | False |
| 300 | 2 | 20 | 18 | 0 | 38 | False | 0.171028836 | False |
| 400 | 2 | 20 | 17 | 0 | 37 | True | 0.242727921 | False |
| 500 | 2 | 19 | 17 | 0 | 36 | True | 0.158649044 | False |
| 600 | 2 | 19 | 18 | 0 | 37 | True | 0.0790531007 | False |
| 700 | 2 | 19 | 18 | 0 | 37 | False | 0.122934811 | False |
| 800 | 2 | 19 | 18 | 0 | 37 | True | 0.106544981 | False |
| 900 | 2 | 19 | 19 | 0 | 38 | True | 0.056544986 | False |
| 1000 | 2 | 19 | 19 | 0 | 38 | False | 0.0606104589 | False |
| 1100 | 2 | 19 | 18 | 0 | 37 | True | 0.062961792 | False |
| 1200 | 2 | 19 | 18 | 0 | 37 | False | 0.0580175496 | False |
| 1300 | 2 | 19 | 18 | 0 | 37 | False | 0.0427456553 | False |
| 1400 | 2 | 19 | 18 | 0 | 37 | False | 0.0512071828 | False |
| 1500 | 2 | 19 | 18 | 0 | 37 | False | 0.0664679638 | False |
| 1600 | 2 | 19 | 18 | 0 | 37 | False | 0.0391579517 | False |
| 1700 | 2 | 19 | 18 | 0 | 37 | False | 0.0586858668 | False |
| 1800 | 2 | 19 | 18 | 0 | 37 | False | 0.0299026388 | False |
| 1900 | 2 | 19 | 18 | 0 | 37 | False | 0.0383665882 | False |
| 2000 | 2 | 19 | 18 | 0 | 37 | False | 0.044577589 | False |


A concrete identity check matters: between B=700 and800, counts stay 19 pairs,
18 triples, 0 quadruples, yet C_5_7_8 (Rt,ROI,OEE) is replaced by C_3_6_8
(WR,Kp,OEE). The identity change is recorded as True. Selected identities are
unchanged from B=1100 through2000, but this does not by itself satisfy the policy.

Original policy SHA: **e738a49b7df5aca0beaca8ed7a4229dbbfeed2aecd5160de0a4414eda73b43db**.
Its bytes and PROPOSED status were preserved. The exact epsilon_q is
2.2250738585072014e-308; every global/local decision threshold, including those
of rejected candidates, enters the strict <1% maximum-change condition.

**B_stop=None; EARLY_STOP_NOT_REACHED.** No checkpoint met all three criteria.
The smallest observed maximum relative change was about 2.99026% at B=1800;
at B=2000 it was 4.45776%, both above 1%. Thus retrospective stop stability is
**NOT_APPLICABLE_NO_EARLY_STOP**, not a fabricated stable-stop claim.
This is not an execution error. All checkpoints, 7140 threshold/decision rows,
and B=2000 reference results were retained. Policy promotion: **false**.

## Archive, reproducibility and quality

[Reviewed run](../../results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/)
contains nominal_normalization.csv, global_pa_B2000.csv, local_pa_B2000.csv,
selected_subsets_B2000.csv, prefix_pa_sensitivity.csv, pa_quantile_trajectories.csv,
pa_noise_singular_values.npz, nominal_chim.npz, early_stop_validation.json,
metadata.json and checksums.sha256. Payload: **6096674 bytes**, about 6.10 MB.
No thousands of files or LFS. NPZ arrays are numeric, allow_pickle=False:

- global (2000,7);
- pairs (2000,28,1), indices (28,2);
- triples (2000,56,2), indices (56,3);
- quadruples (2000,70,3), indices (70,4).

The serial measured workflow before metadata serialization took
**1.0827732000034302 s**. No multiprocessing, GPU, reoptimization or random draw.


| Output | SHA-256 |
|---|---|
| early_stop_validation.json | f00bd2e0b871813e08ea7a5a7380c9f2103b1ea17c5980e01045dac225ec96ec |
| global_pa_B2000.csv | 694a1243917ae9b6c29a96e9ccb0ac311bcc61a7910e433dfe361967c9781b6f |
| local_pa_B2000.csv | 244d77ef82a6d5fa7b8bb60984641248cf763ef370dc894522196087f652118e |
| metadata.json | 61f84b930aa8b0adb9a9bc48f2129dbcc675f73bc582d7053f500188d5f87992 |
| nominal_chim.npz | 181420d3baec324fe02df7274c7130452e562ef5974e527fe63da5c935e6eb40 |
| nominal_normalization.csv | bc19f7ef44d5ee86b10b4fb789fe55742b0dc6dc2119277d5811e7464bb76dc0 |
| pa_noise_singular_values.npz | 4496326958f35ad7a322702e43db3d99eade1497d98e0b179974d424b5e71dba |
| pa_quantile_trajectories.csv | 15df4a3c7a18674f65a04bb633ddf2fe0fb506b9d00874777aec4f9fe925d441 |
| prefix_pa_sensitivity.csv | 171b3679573b1a624628569d388ed3f6fba875e3aabcc02bdfe1d26a655f343c |
| selected_subsets_B2000.csv | 198d03f7756ba9f0633d87a6142e5ac6da014a135f78df405994cc10b6b77e46 |


Locked sync, pytest -v, pytest --cov=cnbi_v2, Ruff and strict mypy passed:
**453 tests; 99.44% (1417/1425 statements); new chim/ 100%; previous scientific
modules 100%; mypy 25 source files**. Only eight pre-existing workbook-inspector
statements remain uncovered. No dependency/lock change. CI is verified on the
delivered PR head; see [gate](../phase_5_verification.md).

ADR 0008 ACCEPTED, C-PA-01/02/03/04 recorded. Mathematical proof/API:
[chim_parallel_analysis.md](chim_parallel_analysis.md). Sources R006/Horn and
R007/Jolliffe-Cadima were checked with explicitly PARTIAL coverage; this is
PA-inspired uncertainty screening, with no claimed classical equivalence or
simultaneous testing guarantee.

## Recommendation for the next separately authorized phase

Use **B=2000 and these 37 subsets** as the present reference selection. Retain
the stopping policy as PROPOSED and do not deploy early termination from this
single trajectory. Define lattice resolution/weights and downstream NBI validation
only under a new explicit task; no H was chosen. Near-threshold margins remain
visible in the CSVs and are not altered to match legacy counts.

No RC, clipping, volume/qmax gate, new Monte Carlo, anchor reoptimization,
shrinkage, lattice H/weights, NBI/C-NBI, clustering, nondominance or Pareto metrics.
No subsequent phase was started automatically.
