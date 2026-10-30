# Phase10D — synthetic benchmark verification

Current status: **INCOMPLETE**. The corrected pilot passed. The official ordered
campaign is running; no claim of540 completed searches or final evaluation is
made until the remaining gates and artifact audit finish.

## Repository and numerical provenance

Repository:LimaGV/C-NBI-v2. Branch:feature/10d-synthetic-algorithm-benchmark.
PR:[17](https://github.com/LimaGV/C-NBI-v2/pull/17), open as draft during execution.
Phase10C PR16 was integrated by merge commit
c06467688187b6a2234a583a538b2b7131088172; the merged tree equals its approved
head df95a954. Main CI40941198792 passed on Ubuntu and Windows.

Frozen numerical source:8f9d60f89fc06814a78d1a1cd9c42ea3ac37fbee. Protocol hash:
19dff29411ad39293f4e429f8f77babd424213a5da61baf7e69855c0ea7209cf.
The corrected pilot gate was committed in4dcb166 before the official campaign.
The final reporting commit is separate from the numerical-source commit.
Source/configuration digests and1262 protected earlier-phase file digests are
checked before every search. Seven identified current-state documents may be
updated; no earlier scientific result, original dataset or excluded license may.

Final campaign directory:
results/phase_10_synthetic_benchmark/benchmark_20261029/campaign_v2/.
It contains27 structural cells ×5 frozen noisy RSM replicas ×4 methods.
Each paired block uses exactly the same coefficient matrix and input hashes.
The original135 multivariate RSMs are never refitted or selected by quality.

## V1 migration and primary evidence

Authorized v1 source:7bd4915a9aea94b9dca1d70014ba5186b4b4e44d, branch cnbi-v1.0,
LimaGV/C-NBI. Local and remote committed SHAs matched. The already-dirty local
v1 working tree was left untouched; only committed blobs were consulted. No v1
environment or direct production import is reused. Exact source files, blob
digests and notices are in algorithm_provenance.json,
references/software/phase10d_cnbi_v1_MIT.txt and phase10d_third_party.txt.

The migration uses comparators.py factor-count, rotation/score transform,
full-VRF and EA routines; solver.py/combinations.py VRF lattice conventions;
ea_calibration.json/calibrate_eas.py/BUDGET_POLICY.md; the v1 article audit,
faithful-VRF revisions, prior validation summary and isolated regression tests.
The18 preselected EA records cover nine(nx,m) pairs per method. No calibration
is executed. Full details:synthetic_benchmark_v1_migration.md.

Pereira et al.(2025), *A hybrid multivariate normal boundary intersection
approach with post-optimization assisted by mixture design of experiments*,
DOI10.1016/j.engappai.2025.112510, was found in Zotero SMMX47JT. It has no child
attachment; the supplied verified local PDF was inspected directly on pp6–7:
Eq11, Eqs17–20 and Eqs21–26. Relevant-page status:FULLTEXT_VERIFIED. No PDF is
published in this PR. The source distinguishes factor-score auxiliary RSMs from
the full quartic VRF objective; the incorrect direct-score optimization is absent.

Registered adaptations:general radius2^(nx/4), frozen v2 data, existing v2 OLS
only for auxiliary factor-score fits, uniform-ball initialization, one-ULP inward
radial repair, explicit pymoo0.6.2 operator defaults and legacy complete-generation
floor. Paper Eq21 uses sum of squared loadings; v1 multiplies by the radius.
Correct published V/U/N are exported, with the internal v1 constant gauge
disclosed to retain numerical tie selection at flat quartic minima. The constant
translation cancels in the normalized VRF objective; it is not a tuned parameter.

Migration PASS:loadings, weights, targets, normalized payoff and NBI decisions
matched exactly in the full preselected nx3 comparison. Corrected variance and
normalization-amplitude differences were4.44e-16 and1.78e-15. The original failed
intermediate comparisons remain archived. The isolated relevant v1 regression
passed. No migration bound was relaxed to make these outcomes pass.

## Version correction and preserved history

The parent directory preserves12 sequential pilot executions, source4f051d5.
campaign_v1 preserves another12 pilot executions, source77c8e12, followed by77
official attempts:75 COMPLETED and two FAILED. The failed tasks are VRF-NBI,
nx2_delta1_rho085, replicas4 and5. The initial adapter incorrectly raised on the
500-iteration Varimax cap. The pinned v1 dependency returns its final iterate;
this behavior is visible in the [primary Rotator source](https://factor-analyzer.readthedocs.io/en/latest/_modules/factor_analyzer/rotator.html).
Its constructor uses500, although the prose description inconsistently says1000.
Installed factor-analyzer0.5.1 was inspected. Context7 did not index the library;
the unrelated result was rejected and the primary software source used.

The correction returns the last iterate and records varimax_converged=false.
The cap500 and tolerance1e-5 are unchanged. Both actual boundary instances have
independent library fixtures and passing loadings/weights/full-VRF regressions.
The old queue was stopped after active searches finished. No old payload is
overwritten, deleted, selectively rerun or mixed into the corrected whole540.
campaign_v1 remains ARCHIVED_IMPLEMENTATION_ERROR / INCOMPLETE.

The corrected campaign has a separate protocol, complete new pilot and all540
predeclared tasks. Thus the report distinguishes12 final pilot executions,
24 preserved earlier pilot executions and77 preserved earlier official attempts
(including two failures) from the final540 official attempts.

## Pilot and resource plan

Three preselected structural cases:nx2_delta1_rho025, nx3_delta3_rho060 and
nx5_delta5_rho085, replica1, all four methods. Planned12; completed12; failed0.
Migration, feasibility, raw coefficient hashes, external metrics and reproducibility
gates passed. All12 X/Y pairs match the original sequential pilot bitwise;
common counters and scientific statuses match. Counter schema2 adds separate
kernel/gradient/point-event counters, rather than changing the objective or seed.

| Method | Pilot runs | Summed kernel wall time(s) | Peak process memory(MiB) |
|---|---:|---:|---:|
| C-NBI | 3 | 76.61 | 212.75 |
| VRF-NBI | 3 | 9.79 | 122.67 |
| NSGA-III | 3 | 191.79 | 137.22 |
| MOEA/D | 3 | 676.29 | 123.35 |

These sums are process-time planning quantities, not elapsed campaign time or
equal computational work. C-NBI Monte Carlo/subsets, repeated VRF extremes and
MOEA/D scalar calls are separately instrumented. Pilot extrapolation:33511s
summed kernel wall time, conservative planning78908s. Those estimates are not
parameter tuning or a guarantee; actual time includes process/input/validation
and disclosed concurrency. Primary per-run timing is input_load_plus_search_seconds;
the kernel timer includes validation and full-objective ND postprocessing.
The primary timer excludes process startup, pre-run protocol/hash verification
and artifact serialization/disk persistence. Those exclusions are explicit;
the separate campaign wall-clock observation includes scheduler/worker lifecycle
and persistence, and offline evaluation time is reported separately.

Hardware:i5-12400F, six physical cores/twelve logical. At most six independent
processes use masks1,4,16,64,256,1024; no sibling threads, one BLAS/OpenMP thread
per search. Strict barriers run all135 C-NBI, then all135 VRF-NBI, then all135
NSGA-III, finally all135 MOEA/D. Task seeds do not depend on lane/order.
Timers measure the archived concurrent environment, not isolated idle-host time.

## Method and evaluation contracts

C-NBI:B2000, raw PSD covariance without jitter, complete sampled-anchor
reoptimization, every eligible subset2≤k≤min(m,nx+1), strict observed>q95 for
all local CHIM components, no early stop. H5 for k2–4; H2 for k5–6. Existing
v2 normalization/geometry/SLSQP/retry kernels are unchanged. All coefficient
samples, MC anchors/payoffs, selected/rejected subsets and trials are retained.

VRF-NBI:ddof0 standardization, correlation eigenstructure, Kaiser-normalized
Varimax, k=max(2,k90), never clamped to the admissible count. If k>nx+1, the
structural failure remains visible. W=L pinv(L' L), rcond1e-15. Auxiliary factor
models use frozen noisy observations; full VRF=(g−T)^2+V, U/N, payoff and NBI.

EAs:pymoo0.6.2, transferred dimension-specific settings, explicit SBX/PM,
MOEA/D PBItheta5/neighborhood settings, common ceiling by m:
max(50000,400*comb(m+3,4)). Full generations use floor(ceiling/population).
Actual NFE and unspent remainder are exported. Entire final populations remain
raw; optimizer objective arrays and independent RSM batch recomposition persist.

Search receives only the noisy RSM, permitted CCD observations and estimated
uncertainty. True functions/anchors/ideal/nadir/reference/metrics never enter the
search interface. The separate frozen10C evaluator runs after all searches end.
It evaluates raw decisions on true functions, applies common analytical
normalization without clipping, then selects feasible/unique/full-m ND sets.
Strict sphere feasibility is unchanged; tiny raw violations remain archived and
excluded externally, without repair or a hidden tolerance. Five replicas share
the exact5000-point reference and normalization for their structural cell.

GD/IGD are mean Euclidean nearest-reference distances (p1); Spacing uses sample
SD(ddof1), Sparsity mean nearest-neighbor distance. HV uses fixed ref1.1 and
four common2^16 Sobol scrambles, exact inclusion-exclusion for up to eight
eligible boxes. Preserve SE/roundoff/status, including precision-pending or
unresolved-zero states. Empty feasible ND sets have undefined metrics; fewer
than two distinct points have undefined Spacing/Sparsity. Never manufacture zero.

Counters separate original full-vector points, quadratic/factor vector events,
scalar values/gradients, NBI attempts/iterations and EA search/export/validation.
NFE alone does not establish cost equivalence. Primary analysis uses native
cardinality. Summaries first aggregate the five nested replicas within each
structural cell; no claim of statistical superiority, inference or equalization.

## Official campaign, indicators and final integrity

Pending final execution/evaluation:a method table with135 planned searches per
method, all540 terminal states, GD/IGD/HV/Spacing/Sparsity, native cardinality,
runtime/NFE accounting and HV precision diagnostics will be recorded here.
The read-only auditor validates raw float64 reload/recomposition, pairing,
MC ensembles/subsets, VRF policy, EA records/budgets, external truth/normalization,
metric replay, method barriers, hashes and all1262 frozen previous files.
HV sampling is not recalibrated or rerun simply to improve a precision flag.

Final gates still required:artifact checksums and staged-Git byte integrity;
uv sync --locked; full pytest coverage; Ruff; strict mypy; exact-head CI on
Ubuntu/Windows; nine English PNG600/vector-PDF scientific figure types without
decorative grids. The final PR remains open and is not merged automatically.
No Phase10E, new noise/CCDs/anchors/RSM fits, retuning or reference modification.
