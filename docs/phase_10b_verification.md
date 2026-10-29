# Phase10B — verification record

Branch:feature/10b-synthetic-rsm-generation.
Input Phase10A:489aa0e2b4703c0e39b0bff2623209e5a177a94b.
Integrated by merge d68aef72532ed0e39bd256b3e9dcb75f30c6a76b,identical tree;
main CI40906784465 SUCCESS Ubuntu/Windows.30 input checksums and three archive
tests passed before integration. No prior conflicting validated95% noise protocol
found in docs/src/scripts/tests. Current definition is explicitly owner-specified.

## Stage A — implementation and small tests

56 tests passed,including all27 noiseless certificates,full135-instance count
check under a separate test seed,CCD geometry,independent centers,reverse order,
three workers,existing OLS/LOOCV/ANOVA APIs,raw singular covariance,external
validation,predefined grid-free figures and lossless oracle-free reload.
Ruff and strict mypy passed;1150 preexisting main files verified byte-for-byte.

## Stages B–D — frozen official campaign

Initial protocol/source freeze:09d469e5a40e9567e85ea3b972315d7273c9a5de.
Final execution source:800076f4c5cac3f651cdb875cf01135f1eddb561,clean working
tree at launch. Run:rsm_20261029,2026-10-29T16:21:50 UTC. Exactly27 noise-free
certificates passed;maximum coefficient error5.329070518200751e-15,below the
predefined condition-aware float64 bounds. These are not experimental replicas.

All135 noisy joint fits succeeded;zero failures,all135 retained.3555 distinct
experimental rows,28530 scalar observed responses,990 response models,13275 noisy
coefficients and2655 independent true coefficients. Five replicas per structural
cell with the same anchors,CCD,truth and noise variances. Conventional training
CCDs are13/19/47 rows;nx3 preserves all8 outside-ball factorial rows. No old
workbook,dataset,model,anchor or structural calibration changed.

Master seed20261029;128-bit SHA256 cell/replica keyed seeds,PCG64 through NumPy2.5.4.
135 distinct noise streams plus27 separate external streams. No global RNG or
processing/worker-order dependence. All135 experimental arrays reproduced exactly
in reverse order;three-worker/order equivalence tested independently under a test
seed. All135 models reloaded and evaluated without OLS or oracle access.

Noise is Gaussian iid,mean zero in distribution,with sigma²=S_f²/19 and complete
CCD sample variance ddof1,including all five independently perturbed centers.
No sample recentering,rescaling,clipping,rounding or response transform.

| nx | Signal variance min–max | Noise variance min–max | Noise draws per joint fit |
|---:|---:|---:|---|
| 2 | 1.224098064–6.358974346 | 0.064426214–0.334682860 | 13 × m |
| 3 | 2.743507656–10.342387873 | 0.144395140–0.544336204 | 19 × m |
| 5 | 6.064276804–23.960083973 | 0.319172463–1.261057051 | 47 × m |

Full-precision variances and per-instance seeds are in noise_parameters/instances
CSVs.369 negative scalar observations were preserved. Realized sample noise
variances range0.0250257486–1.7708400318;they were not forced to expectation.

## Fit diagnostics

Every design has full rank6/10/21. Condition(X)=2.8971292992/3.9113607637/7.8726373801
for nx2/3/5. Residual df7/9/26,pure-error df4,LOF df3/5/22. Every training,
PRESS,global-model and LOF statistic is defined with status OK. All statistics
come from the existing diagnose_rsm API;see990-row diagnostics CSV for S,SS,MS,
df,F,p and status fields. No term removal or refit after inspection.

Equal weight per response model; values in this report are display-rounded.

| nx | Responses | Mean R² | Mean adjusted R² | Mean LOOCV predicted R² | Mean PRESS | LOF p<.05 |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 270 | 0.970798 | 0.949940 | 0.887655 | 4.667048 | 10 |
| 3 | 315 | 0.975103 | 0.950205 | 0.868777 | 19.279063 | 21 |
| 5 | 405 | 0.971421 | 0.949438 | 0.904210 | 89.612942 | 22 |
| All | 990 | 0.972423 | 0.949819 | 0.888421 | 44.066919 | 53 |

R² range0.9118924281–0.9989471219;adjusted R²0.8428639697–0.9978942439;
LOOCV predicted R²0.4420087858–0.9922091675;PRESS0.2654511213–178.3341623002.
S0.0958179186–1.4423392254;global F11.7278256707–948.7775984139;
global p5.8742766313e-20–0.0014166006. LOF F0.0273868768–78.7027191049;
LOF p0.0003452727–0.9996427712.53/990=5.353535% LOF rejections at nominal5%
are descriptive results under correct quadratic truth;none were used for retuning
or exclusion. Small training samples can have LOOCV predictions markedly poorer
than training R². The protocol's95% signal is not a target for these fitted R²s.

Coefficient L2 error:mean0.6436961841,range0.1119946971–2.1617260041;
relative-L2 error:mean0.1472742358,range0.0495023445–0.3690079206.
The maximum absolute error of a truly zero interaction is0.7399800495.
Termwise differences,absolute errors and explicitly undefined zero/near-zero
relative denominators are preserved in13275 coefficient-error rows.

No estimated polynomial was nonconvex:minimum Hessian eigenvalue across all990
models0.5062615487. This observed result was not enforced. Residual covariance
rank is4/6/7 for nx2 (m4/6/8),5/7/9 for nx3,and7/9/11 for nx5. Fifteen nx2,m8
matrices are singular as expected with7 residual df. Their conditions are explicitly
undefined. Full-rank covariance conditions range3.1235468344–188708.8922953.
Raw covariance,eigenvalues and any tiny negative roundoff eigenvalues are saved;
no jitter,regularization or positive-definiteness requirement was introduced.

## Independent external prediction and replica variability

4096 fresh uniform-volume Sobol ball points per cell,generated only after all135
fits and shared by its five replicas. Separate stream0 seeds;all points/truths
preserved in the external NPZ. Predictions use frozen B_hat and never train or
select models. External R² compares to the noiseless oracle,unlike LOOCV R²,
which predicts noisy experimental observations.

| nx | Mean RMSE | Mean MAE | Mean external R² |
|---:|---:|---:|---:|
| 2 | 0.226024 | 0.185483 | 0.969832 |
| 3 | 0.363560 | 0.292399 | 0.970737 |
| 5 | 0.584241 | 0.463991 | 0.977573 |
| All | 0.416329 | 0.333437 | 0.973287 |

| Structural target | Mean RMSE | Mean MAE | Mean external R² | Responses |
|---:|---:|---:|---:|---:|
| 0.25 | 0.374937 | 0.300146 | 0.971613 | 330 |
| 0.60 | 0.428513 | 0.343103 | 0.972980 | 330 |
| 0.85 | 0.445538 | 0.357060 | 0.975267 | 330 |

| Excess delta | Mean RMSE | Mean MAE | Mean external R² | Responses |
|---:|---:|---:|---:|---:|
| 1 | 0.436946 | 0.349410 | 0.973184 | 240 |
| 3 | 0.411257 | 0.329416 | 0.973471 | 330 |
| 5 | 0.408534 | 0.327468 | 0.973200 | 420 |

External RMSE range0.0528212782–0.9743214417;MAE0.0384994019–0.7873620613;
external R²0.8577964933–0.9984285803;largest pointwise absolute error3.4648175057.
Smallest RMSE:nx2_delta1_rho060,replica4,y3,RMSE0.0528212782,
MAE0.0384994019,external R²0.9984285803.
Largest RMSE:nx5_delta3_rho085,replica5,y5,RMSE0.9743214417,
MAE0.7873620613,external R²0.9495947763. These identify diagnostic extremes only;
all models remain in the archive. Lowest external R² need not identify highest
raw RMSE,because true-response variances differ.

Across five replicas,mean pointwise prediction SD per scenario ranges
0.1631157760–0.5979108029;maximum pointwise SD1.9994517500. Full per-scenario
spread is preserved. The37-row summary covers all27 cells plus nx,delta,target
and overall groups,using linear quantiles and all990 responses. Raw RMSE increases
with response scale/dimension here;these descriptive summaries do not establish
algorithm performance or isolate causal correlation effects.

## Correlation change on the training CCD

| nx | Mean true-CCD absolute correlation | Mean noisy-CCD absolute correlation |
|---:|---:|---:|
| 2 | 0.570580 | 0.554844 |
| 3 | 0.539505 | 0.510075 |
| 5 | 0.544320 | 0.518653 |

The mean noisy-minus-true absolute-correlation difference over135 instances is
-0.0236105871. Full true/noisy CCD matrices and signed summaries are archived.
The structural target is the volume-ball quantity calibrated in10A;neither true
CCD correlation nor noisy CCD correlation is constrained to match it.

## Figures,storage and integrity

Six English figure types,600dpi PNG and vector PDF,visually inspected without
grids. Predetermined true/predicted examples:nx2/3/5,delta3,rho060,replica1,y1,
fixed Sobol stride16. Residuals are pooled/known-sigma scaled,not studentized.
Identity,zero and0.95 reference lines are scientifically identified.

The initial RMSE titles were shortened with a separate archive-only renderer,
without OLS or oracle evaluation. Its receipt is preserved with the initial full
manifest in docs/phase_10b_initial_generation_receipt.json.

The first full suite exposed a directory-scope conflict:the frozen Phase10A AST
test prohibits RSM fitting in every top-level synthetic Python file,including
new files. Rather than change that historical test,the new Phase10B modules were
isolated in cnbi_v2.synthetic.rsm. Its scientific functions and validated Phase1
APIs were unchanged;only import paths and figure labels changed. The initial
noise policy remains byte-identical. Source checkout bytes were normalized to
canonical Git LF before the final clean execution so hashes also match Ubuntu.

Final re-execution at800076f produced **all16 numerical CSV/NPZ files byte-identical
to the initial09d469e generation**,including observations,coefficients,covariances,
diagnostics,holdout and summaries. An automated test protects this equivalence.
Earlier local archives were preserved in explicitly named sibling directories;
only the final official campaign is versioned. No threshold,seed,model,scientific
formula,hyperparameter or frozen historical test changed. The source SHA/byte
hashes in the final manifest refer directly to the final committed package.

34 artifacts,approximately24.03 MB,including16 mandatory outputs,lossless model
index,experimental/external NPZs,noiseless certificates,replica variability and
12 figure files.44 checksum entries include payloads and their code/protocol
sources;all verified. Every numerical array has dtype,shape and byte SHA256 in
the generation manifest. All1150 earlier tracked scientific files remain intact.
New phase-local Git attributes preserve checksummed generated JSON/README bytes
including renderer line endings across platforms;root attributes are unchanged.
The model loader exposes only noisy polynomials and never refits. Raw data and
excluded-material licenses are unchanged;no implicit MIT/CC data license.

Final official generation/fit/export/figures:8.580396000s. The initial and package
equivalence executions took7.834726200s and7.615803700s;initial display-only
refinement1.420478600s. Total recorded pipeline work25.451404500s excluding
testing,CI and human review. These are
pipeline timings,not algorithm runtime comparisons. Python3.12.15,NumPy2.5.4,
SciPy1.18.1,Matplotlib3.11.2,Windows11;BLAS/CPU/lock metadata recorded. No new
dependency or change to uv.lock. Bitwise experimental reproducibility is certified
in this locked environment;cross-platform BLAS equivalence uses tolerances.
Archive byte identity is always exact by SHA256. Cross-platform libm/BLAS
recomputations use small float64 tolerances;local reverse-order experiments and
raw covariance API tests still require exact identity. No solver/model tolerance
or scientific result was changed by these platform-portability checks.

## Stage E — quality gate and delivery

64 new tests cover the required25 categories and invalid variance/nonfinite,
incomplete/corrupt archives,duplicate/missing identity/seeds and deficient designs.
Final local checks:uv sync --locked PASSED;**814 tests passed in105.98s**,
**99.25% coverage** (3062 statements,23 missed;gate96.15%). Ruff PASSED;
strict mypy PASSED for60 source files.44 checksums also matched the actual staged
Git blobs,not only the working-copy files. Remote Ubuntu/Windows CI is verified
on the final PR head before delivery. Phase10B PR remains open;no auto-merge or later
scientific phase. No multiobjective solver,Pareto reference or benchmark metric
was executed. No original data were modified or reconstructed.
