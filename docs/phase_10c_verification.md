# Phase10C — analytical Pareto reference verification

Branch:feature/10c-synthetic-pareto-reference.
Phase10B input6d07d250e28730e69d481aa58dbc0d9ad0d76c73,integrated by merge
47a0e4dc55a22a7d0ad436540c1a305e4078e2ad after44 checksums,135 reloadable models,
eight archive tests and four green PR checks. Main CI40919991675 SUCCESS on
Ubuntu/Windows;merged tree identical to approved10B head. No frozen science changed.

## Stages A–B:preparation,proof and unit validation

The full prompt and supplied continuation10–17 are covered. Both inclusions of
P_X=conv(anchors),including zero scalarization weights,are proved in the math
document. Ideal0,nadir from anchor distances,strictly positive ranges. The finite
reference is distinct from the continuous analytic front. Sampling,identity,
FPS tie rules,independent probes,coverage budget and HV study tiers were defined
before official results. MDR0015 records independence and offline evaluation.

34 tests passed:projection and scalarization oracles,uniform-volume triangulation,
explicit nonuniform fallback,geometry rank,minima,normalization without clipping,
stable identity/FPS,seed/order independence,full10000-row mathematical fixture,
GD/IGD positive separated oracles,exact HV dimensions4–11,orthant equivalence,
QMC zero/precision states,ddof1/density/singletons,raw/feasible/unique/ND separation,
five-replica frame invariance,plan-only equalization,codecs and six grid-free figures.
Ruff and strict mypy69 source files passed. All1204 earlier scientific files verified
against main Git blobs. No historical test was edited. No official reference has
been selected by comparison with a method or a noisy RSM.

## Stages C–D:official references and independent coverage

Source/protocol freeze:d982c01f7753152e5961093d0e6de809362c595c,clean working
tree. Run:analytical_20261029,2026-10-29T18:42:03 UTC. **27 references ×5000
primary points=135000 solutions**,one per structural cell,shared by all five
replicas. Sensitivity references2500/5000/10000 are nested,not separately fitted
or optimized sets.398898 candidates across all cells;all candidate membership
weights,origins and stable source IDs are archived. Independent4096-point volume
and1024-point boundary probes per cell were generated only after its selection.

All27 hulls have full affine dimension nx;no fallback,no perturbed anchor,no rank
failure. Geometry condition range1.0712359988–88.3042889515. Every anchor is
present in each prefix,every response is direct squared distance,all coordinates/
responses are finite and all sphere constraints satisfied. Minimum decision
separation0.0001414916738,well above the fixed identity tolerance. Maximum weight
sum error3.3306690739e-16. No apparent tolerance-dominance pair was detected.
Barycentric witnesses plus the two-inclusion theorem certify true efficiency;
the numerical diagnostic uses its explicit roundoff-adjusted neighborhood bound.

All27 references reproduced **bitwise** in reverse cell order (X,F,weights),in
the recorded locked environment. The frozen arrays are the common evaluation
data on both operating systems;direct cross-platform recomputations use tight
float64 tolerances. No noisy model or method solution file enters generation.

The table reports the largest independent volume-probe RMS-coordinate distance
over the nine cells of each nx,and the largest discrete Hausdorff RMS distance
to R10000. Mean probe distances are raw Euclidean normalized-objective distances,
not divided by sqrt(m). Reporting precision here is rounded;CSVs retain17 digits.

| nx | N | Mean probe distance | Worst volume-probe RMS | Worst Hausdorff RMS |
|---:|---:|---:|---:|---:|
| 2 | 2500 | 0.006964130 | 0.011941179 | 0.008006430 |
| 2 | 5000 | 0.005083410 | 0.010258564 | 0.004752110 |
| 2 | 10000 | 0.004241729 | 0.010258564 | 0 |
| 3 | 2500 | 0.018983479 | 0.028378510 | 0.022329077 |
| 3 | 5000 | 0.015209800 | 0.026746432 | 0.015669921 |
| 3 | 10000 | 0.012719401 | 0.024336303 | 0 |
| 5 | 2500 | 0.032474306 | 0.043617492 | 0.034917742 |
| 5 | 5000 | 0.026678434 | 0.041120498 | 0.027314006 |
| 5 | 10000 | 0.022547310 | 0.037077496 | 0 |

For R5000,the global worst volume/boundary-probe/Hausdorff RMS values are
0.0411204980/0.0407492341/0.0273140059,all at nx5_delta5_rho025. All27 pass the
**predeclared proposed operational0.05 budget**;coverage_review_required is empty.
This finite audit does not certify asymptotic convergence or uniform error over
the continuous front. In particular,the worst nx2 probe distance plateaus between
5000 and10000,showing the finite candidate-pool limitation;nested self-distances
of zero do not resolve that limitation. No candidate count or budget was retuned.

Full sensitivity records include directed distances,GD/IGD versus the denser
sample,NN min/mean/q95/max,boundary counts,origin composition and radial-shell
counts. The mean NN distances at5000 are0.0089928765/0.0240372224/0.0397813576
for nx2/3/5. Small forced anchor separations remain represented rather than removed.

## Analytic normalization

All198 scenario–response ideals equal0. All198 nadirs/ranges are calculated from
the true anchor pair distances,not sampled maxima or RSM fits. Both extrema are
attained among the retained individual anchors. The primary normalized arrays
have exact per-response minima0 and maxima1. Every denominator is positive.

| nx | Smallest true response range | Largest true response range |
|---:|---:|---:|
| 2 | 0.926064874836399 | 7.976812235366184 |
| 3 | 2.176059073799494 | 11.234357403873485 |
| 5 | 8.063104864241163 | 22.57321240253261 |

All individual values/intervals are in pareto_ideal_nadir.csv (198 rows);the
complete individual-anchor response table is pareto_extremes.csv. No clipping.
Offline API tests preserve feasible points with normalized coordinates>1 and
infeasible raw rows,including every original row index. The frame is identical
across all five replicas of a scenario and never exposed through StoredRSM.

## Stage E:five metric definitions and HV precision

GD/IGD use arithmetic mean Euclidean distances,p1,through the validated API.
Spacing is sample SD of nearest-other Euclidean distances,ddof1;Sparsity is their
mean. Independent exact examples give GD=2/3,IGD=1/2,Spacing=sqrt(1/3),Sparsity=4/3.
Separated sets give GD=IGD=1,self-comparison gives0. No artificially zero distance
is assigned to separated sets. Full-objective ND tests detect dominance visible
only in the last response coordinates. Raw/feasible/unique/ND fixture counts
are5/4/3/2;these are API tests,not algorithm outputs or a benchmark run.

HV reference is exactly(1.1,...,1.1),lower bound0,all MIN,in the analytic frame.
No competitor-derived bound or clipping. Final large-set configuration is
**four scrambled Sobol grids ×65536 points (power16)**,262144 common quadrature
points per objective dimension. All27 primary references meet the predeclared
precision criteria at16;the predeclared18/20 escalation was unnecessary. Seeds
and exact grid hashes for dimensions4–11 are in generation_manifest. Dimension10
has analytic indicator oracles but no additional structural benchmark cell.

| m | Structural cells | Largest relative SE | Largest15→16 change |
|---:|---:|---:|---:|
| 4 | 3 | 0.027118% | 0.032691% |
| 5 | 3 | 0.032459% | 0.045473% |
| 6 | 3 | 0.023368% | 0.033097% |
| 7 | 6 | 0.073268% | 0.078833% |
| 8 | 3 | 0.088287% | 0.037440% |
| 9 | 6 | 0.285878% | 0.303057% |
| 11 | 3 | 0.148322% | 0.172360% |

Primary HV estimates range0.4780586391–1.2868368951. Values may exceed1 because
the fixed HV box has volume1.1^m. SE range0.0000886020–0.0016648910. Minimum
hits per scramble across primary references11281,far above128. The estimate is
reported as randomized quadrature,not exact HV for5000-point sets or a guaranteed
confidence interval. Reference-regime validation does not imply accuracy for an
arbitrarily tiny future method contribution.

All32 one/two-box analytic tests in dimensions4–11 pass the exact-small-set branch;
largest observed relative error2.8689154677e-15. The raw Sobol study retains24
zero-mean oracle rows among128 oracle/level rows,tiny positive volumes being
missed by finite indicator sampling. These are UNRESOLVED_ZERO_HITS,not certified
zeros. Bounded inclusion-exclusion for<=8 eligible boxes resolves those analytic
cases without fabricated precision. Larger future sets always retain individual
precision states;unresolved cases cannot be treated as reliable comparative HV.

Explicit undefined cases:empty feasible ND sets have no five metrics;fewer than
two distinct vectors have undefined Spacing/Sparsity;exact-small-set HV has no
randomized SE (a roundoff bound is supplied);large-set zero/unstable sampling has
an unresolved/pending precision flag. Points outside the positive-volume HV box
contribute exactly zero to HV and remain available for all other metrics.

The final configuration was frozen after this independent study and before any
algorithm run. Future evaluation accepts scenario/replica/method/raw X/metadata/
optional time/NFE,preserves raw arrays,reevaluates truth,normalizes,deduplicates,
filters full-space ND and returns diagnostics offline. Equalization is a plan
only:min eligible cardinality per paired block,candidate-only geometry,no
interpolation or reference-distance selection. No equalization was executed.

## Stage F:artifacts,figure QA and integrity

All19 requested artifact names are present,plus candidate/probe/nested NPZs and
12 English figure exports:34 files,approximately66.85 MB. Primary NPZs each have
exactly27 scenario keys and5000 float64 rows;extensions reconstruct10000 without
optimization,and2500 is an exact prefix. Candidate IDs/origins are int64 vectors;
all decision,response,normalized and barycentric matrices are float64. Every
array has shape,dtype and SHA256 metadata. All1204 earlier scientific files are
unchanged,including135 frozen RSMs,the original workbooks and all license files.

Six figure types are600dpi PNG/vector PDF,visually inspected,without grids.
Only actual nx2/nx3 geometry is plotted,no decorative nx5 projection. Prespecified
representatives are retained. A separate archive-only renderer at
d8ac09fb11429e9764591736044e85b77562f2a0 reduces3D tick overlap and moves an HV
legend,without sampling,FPS,HV recomputation or fitting. All14 numeric CSV/NPZ
files remained byte-identical. Prior image hashes,renderer source/commit and
elapsed time are explicit in generation_manifest.figure_layout_refinement.
Original numerical source hashes remain d982c01;no mathematical/protocol source
was edited after the results. Use refine_synthetic_pareto_layout.py after
generation to reproduce the final figure presentation.

**51 checksums verified**,including all payloads and scientific/display sources.
Checksum-manifest SHA256:e986d95704d6db2c3c8872e6c101452a25c5c7abb2b82e0cda0776150342bfbb.
Recorded generation/reverse-replay/study/export time307.765677600s;display-only
refinement2.167481200s;total309.933158800s,excluding tests/CI/human review. These
are pipeline timings,not comparisons between algorithms. Python3.12.15,
NumPy2.5.4,SciPy1.18.1,Matplotlib3.11.2;BLAS/platform and unchanged lock hash recorded.

## Stage G:quality and delivery

uv sync --locked PASSED. **854 tests passed in104.49s**,including40 new tests;
**98.92% coverage**,3595 statements/39 missed,above96.15%. Ruff PASSED;strict
mypy PASSED for69 source files. A collection-name collision was resolved by
renaming only the new test to test_pareto_archive.py;historical tests stayed intact.
Final remote Ubuntu/Windows CI is verified on the exact PR head before delivery.
The new PR remains open without automatic merge. No new anchors,CCD,noise,RSM
fit,method run,comparative significance analysis or10D execution occurred.

## Complete primary-case audit (display-rounded)

| Scenario | m | Geometry condition | Volume probe RMS max | Boundary probe RMS max | Hausdorff RMS | HV estimate | Relative SE |
|---|---:|---:|---:|---:|---:|---:|---:|
| nx2_delta1_rho025 | 4 | 1.071236 | 0.01006494 | 0.00474496 | 0.00465877 | 0.92984626 | 0.027118% |
| nx2_delta1_rho060 | 4 | 4.630548 | 0.00339686 | 0.00177928 | 0.00158463 | 1.09340586 | 0.008788% |
| nx2_delta1_rho085 | 4 | 8.516116 | 0.00208345 | 0.00139727 | 0.00103665 | 1.00070998 | 0.008854% |
| nx2_delta3_rho025 | 6 | 1.109380 | 0.01025856 | 0.00503355 | 0.00475211 | 0.72156186 | 0.023043% |
| nx2_delta3_rho060 | 6 | 1.646561 | 0.00716238 | 0.00334127 | 0.00314869 | 1.25856358 | 0.017104% |
| nx2_delta3_rho085 | 6 | 11.649646 | 0.00164779 | 0.00095998 | 0.00079894 | 1.06177153 | 0.023368% |
| nx2_delta5_rho025 | 8 | 1.695336 | 0.00761180 | 0.00403091 | 0.00365960 | 0.65649370 | 0.088287% |
| nx2_delta5_rho060 | 8 | 1.959465 | 0.00762020 | 0.00406863 | 0.00404328 | 0.90707405 | 0.055160% |
| nx2_delta5_rho085 | 8 | 5.279418 | 0.00336851 | 0.00186310 | 0.00160154 | 1.09204101 | 0.028807% |
| nx3_delta1_rho025 | 5 | 2.168089 | 0.01822699 | 0.01575812 | 0.01111011 | 1.07359551 | 0.032459% |
| nx3_delta1_rho060 | 5 | 4.237975 | 0.01014394 | 0.01041632 | 0.00677604 | 0.96285083 | 0.030909% |
| nx3_delta1_rho085 | 5 | 11.447339 | 0.00321920 | 0.00330848 | 0.00194205 | 0.90520536 | 0.021330% |
| nx3_delta3_rho025 | 7 | 1.811858 | 0.01872310 | 0.01860516 | 0.01239766 | 0.80153093 | 0.073268% |
| nx3_delta3_rho060 | 7 | 3.950197 | 0.01150429 | 0.01102515 | 0.00750527 | 0.96617397 | 0.041602% |
| nx3_delta3_rho085 | 7 | 8.764284 | 0.00392553 | 0.00679951 | 0.00193788 | 1.28683690 | 0.024588% |
| nx3_delta5_rho025 | 9 | 1.196919 | 0.02674643 | 0.02228873 | 0.01566992 | 0.47805864 | 0.285878% |
| nx3_delta5_rho060 | 9 | 6.060988 | 0.01185857 | 0.01374087 | 0.00808530 | 0.73435808 | 0.176408% |
| nx3_delta5_rho085 | 9 | 15.642286 | 0.00524344 | 0.00488307 | 0.00287289 | 0.66182356 | 0.093965% |
| nx5_delta1_rho025 | 7 | 49.310245 | 0.02727167 | 0.03056287 | 0.01625152 | 0.79560622 | 0.046141% |
| nx5_delta1_rho060 | 7 | 61.942897 | 0.01683333 | 0.01953333 | 0.00742484 | 0.84774665 | 0.046687% |
| nx5_delta1_rho085 | 7 | 33.417955 | 0.00753431 | 0.00728116 | 0.00264323 | 0.89561267 | 0.031595% |
| nx5_delta3_rho025 | 9 | 2.472607 | 0.03433030 | 0.03504846 | 0.02385647 | 0.69570718 | 0.239309% |
| nx5_delta3_rho060 | 9 | 88.304289 | 0.01797806 | 0.02362049 | 0.00939128 | 0.74485508 | 0.018114% |
| nx5_delta3_rho085 | 9 | 33.362361 | 0.00354958 | 0.00388990 | 0.00175375 | 0.70342477 | 0.064408% |
| nx5_delta5_rho025 | 11 | 2.366604 | 0.04112050 | 0.04074923 | 0.02731401 | 0.49253442 | 0.148322% |
| nx5_delta5_rho060 | 11 | 45.516965 | 0.02309444 | 0.02510067 | 0.00864381 | 0.66110235 | 0.105518% |
| nx5_delta5_rho085 | 11 | 19.828827 | 0.00840201 | 0.00686126 | 0.00378286 | 0.56419321 | 0.134742% |
