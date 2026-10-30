# Phase10D — synthetic benchmark verification

Numerical status: **COMPLETED**. All540 official searches completed without
execution failures, followed by540 independent evaluations and a passing
artifact audit. Final software-quality and exact-head CI evidence is recorded
below. The PR remains open; MDR0016 remains EXPERIMENTAL pending review.

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

| Method | Pilot runs | Summed kernel wall time(s) | Peak before archive(MiB) |
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
Search runtimes include the Python call-event profiling overhead used for the
archived counters; they describe these instrumented implementations.
The primary timer excludes process startup, pre-run protocol/hash verification
and artifact serialization/disk persistence. Those exclusions are explicit;
the separate campaign wall-clock observation includes scheduler/worker lifecycle
and persistence, and offline evaluation time is reported separately.
Additional per-task lifecycle windows use the original log's creation before
process launch and the receipt's creation after child exit. They include startup,
protocol checks, loading, optimization, validation, persistence and shutdown.
The original wall-clock observations and event-order checks are preserved in
runtime_observations.json before Git checkout can change filesystem timestamps.
These are additional lifecycle diagnostics; the predeclared worker timer remains
unchanged. Missing or contradictory event windows remain explicitly unavailable.
The Windows peak-working-set query occurs before artifact persistence; memory
allocated by later serialization is outside that observation window. It is not
a measurement of the full worker lifecycle's peak or total host memory usage.

Hardware:i5-12400F, six physical cores/twelve logical. At most six independent
processes use masks1,4,16,64,256,1024; no sibling threads, one BLAS/OpenMP thread
per search. Strict barriers run all135 C-NBI, then all135 VRF-NBI, then all135
NSGA-III, finally all135 MOEA/D. Task seeds do not depend on lane/order.
Timers measure the archived concurrent environment, not isolated idle-host time.
The completed C-NBI case nx5_delta3_rho060/replica3 illustrates the NBI cost:
241 of456 candidate subsets,6991 lattice subproblems,8342 trials and829505
iterations. Its solver took1250.18s out of1267.44s kernel wall time; sampled
anchor reoptimization took12.15s. This is an observed cost example, not a
quality-based selection or an upper runtime bound for other instances.

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

## Official campaign and verified execution order

| Method | Planned | Completed | Failed | Incomplete/pending |
|---|---:|---:|---:|---:|
| C-NBI | 135 | 135 | 0 | 0 |
| VRF-NBI | 135 | 135 | 0 | 0 |
| NSGA-III | 135 | 135 | 0 | 0 |
| MOEA/D | 135 | 135 | 0 | 0 |
| Total | 540 | 540 | 0 | 0 |

Original checkpoint creation/final-write observations independently confirm
that every preceding method finished before the next method started. The
following windows are local UTC−03 on2026-10-30; they describe checkpoint
activity, rather than the complete lifecycle of the first/last process.

| Method | First checkpoint | Last checkpoint | Window(s) |
|---|---|---|---:|
| C-NBI | 08:20:12.311 | 09:18:25.612 | 3493.301 |
| VRF-NBI | 09:18:27.823 | 09:21:08.204 | 160.382 |
| NSGA-III | 09:21:10.391 | 09:37:56.198 | 1005.807 |
| MOEA/D | 09:37:58.337 | 10:50:36.026 | 4357.690 |

The complete scheduler/worker lifecycle lasted9029.539s (**2h30m29.539s**),
08:20:06.779–10:50:36.317. Offline evaluation of27 cells/540 runs took299.964s.
The additional read-only scientific artifact audit took359.386s. These wall
times are separate from sums of concurrent per-process durations.

## Descriptive indicators and native cardinality

Each entry below is the median across27 structural-cell medians, each cell
containing its five nested replicas. Allfive indicators were defined in all540
runs. Per-replica paired rows, defined counts, quartiles, extrema and summaries
by nx/m/delta/rho remain in the CSV/JSON artifacts. HV values include the two
explicit precision-pending estimates described below.

| Method | GD | IGD | HV | Spacing | Sparsity | Native ND |
|---|---:|---:|---:|---:|---:|---:|
| C-NBI | 0.026547514 | 0.052934202 | 0.80296565 | 0.033807677 | 0.045069794 | 261 |
| VRF-NBI | 0.040074591 | 0.25777247 | 0.53231845 | 0.10106689 | 0.21544450 | 11 |
| NSGA-III | 0.030765842 | 0.13402653 | 0.67186375 | 0.045358218 | 0.034897496 | 186 |
| MOEA/D | 0.008867811 | 0.32391259 | 0.58553543 | 0.026897635 | 0.015603713 | 84 |

These are descriptive summaries, not a statistical superiority claim. Native
cardinality differs substantially. GD/IGD also include the fixed finite-reference
approximation; the analytical continuous front is distinct from its5000-point
sample. No reference, normalization, metric or method configuration was adapted
after seeing these results. Equalization and inferential comparisons remain10E.

| Method | Returned | Feasible | Unique | True full-m ND |
|---|---:|---:|---:|---:|
| C-NBI | 443097 | 427608 | 373113 | 156789 |
| VRF-NBI | 2627 | 2617 | 2617 | 2011 |
| NSGA-III | 39630 | 39630 | 39630 | 35335 |
| MOEA/D | 39750 | 39750 | 39700 | 39671 |

The unchanged strict sphere test excludes15489 C-NBI raw points in94 runs and
10 VRF-NBI points in6 runs. Maximum raw norm excess was1.0962342145e-11 and
1.7779111516e-11, respectively. Both EAs had zero raw sphere violations. These
small boundary excesses remain in the raw artifacts and affect native counts;
no external projection, repair or hidden feasibility tolerance was introduced.
Raw points with any true normalized objective above1 were76914/594/1035/0 for
C-NBI/VRF-NBI/NSGA-III/MOEA/D. Values outside[0,1] remain unchanged.

## Computational cost and observed lifecycle windows

Time columns use the same median-of-cell-medians convention. The additional
lifecycle observations include startup/protocol checks/persistence and were
verified in all540 tasks; the original primary worker timer is preserved.

| Method | Worker(s) | Observed lifecycle(s) | Sum worker(s) | Maximum worker(s) | Peak before archive(MiB) |
|---|---:|---:|---:|---:|---:|
| C-NBI | 19.019930 | 21.189254 | 16066.997 | 1752.574 | 906.562 |
| VRF-NBI | 3.606188 | 5.701545 | 675.714 | 16.669 | 123.227 |
| NSGA-III | 14.882193 | 16.971099 | 5314.689 | 193.313 | 138.855 |
| MOEA/D | 106.460395 | 109.394854 | 24591.786 | 596.706 | 123.766 |

| Method | Original-RSM point evaluations | Model-vector point events | Additional work |
|---|---:|---:|---|
| C-NBI | 443097 | 96843149 | 502581993 scalar values;68980209 scalar gradients |
| VRF-NBI | 2627 | 6061943 | 6056689 auxiliary factor-vector evaluations |
| NSGA-III | 18701400 | 18780660 | Full final populations/export/validation counted separately |
| MOEA/D | 18701400 | 18780900 | Full final populations/export/validation counted separately |

For NBI methods, original-RSM point counts chiefly describe original-objective
recomposition; they exclude the separately recorded scalar/factor work. These
categories cannot be treated as equal computational effort. Both EAs used the
predeclared ceiling and full-generation floor, with no overshoot or retuning.

C-NBI screened all38100 eligible local subsets, selected16532, solved444331 NBI
subproblems in459476 trials and14458055 iterations, and retained all1,980,000 MC
anchor optimizations(B2000 across990 original responses). No global-only NBI
substitution or early stopping was used. The largest worker runtime was the
nx5_delta5_rho060/replica3 C-NBI task. Raw trials and selected/rejected subsets
are preserved for every run. Run environment:Windows, Python3.12.15, NumPy2.5.4,
SciPy1.18.1, pymoo0.6.2; plotting Matplotlib3.11.2. CI tests both operating systems.

## Precision and migration limitations retained

Of540 HV results,470 passed the frozen QMC precision criteria and68 used the
exact small-set branch. Two VRF-NBI estimates remain PRECISION_PENDING, both
nx5_delta5_rho025; no unresolved-zero estimate or fabricated zero occurred.

| Replica | HV estimate | HV SE | Status |
|---:|---:|---:|---|
| 2 | 0.01030693634294957 | 0.00017806426035488158 | PRECISION_PENDING |
| 3 | 0.018796282010848903 | 0.00013579301396345143 | PRECISION_PENDING |

Maximum relative SE for QMC estimates was0.2302%/1.7276%/0.3776%/0.3269% by
C-NBI/VRF-NBI/NSGA-III/MOEA/D. A small SE alone does not imply every precision
criterion passed. The two flags remain pending; resolution/scrambles/reference
were not changed to improve them. Exact roundoff/raw inclusion-exclusion values,
SE and status remain in benchmark_hv_precision.csv and the primary records.

Three VRF-NBI rotations reached500 iterations with varimax_converged=false:
nx2_delta1_rho085 replicas4/5 and nx3_delta5_rho085 replica3. The final iterate
is retained exactly as the pinned v1 dependency specifies. Neither the cap nor
the tolerance was changed. All135 VRF runs remain admissible and completed;
these convergence diagnostics are distinct from execution failures.

## Artifact integrity, figures and final quality

The read-only audit passed all540 runs and135 pairing blocks. It verifies raw
float64 reload/recomposition, coefficient identity, MC ensembles/subsets,
VRF policy/weights/full variance, EA records/budgets/populations, external true
responses/normalization, all-m ND/cardinality and GD/IGD/density replay. It also
verifies all1262 protected previous files. HV estimates were not rerun or
recalibrated for this audit; original precision flags remain intact.

Nine English scientific figure types are present as PNG600 and vector PDF,
with consistent method colors, integer dimension/objective ticks and no grids.
Representative PNGs and rendered PDFs were visually inspected; DPI metadata
is599.9988, the PNG pixels-per-metre representation of600dpi. Source/data and
all18 output digests are in figures/figure_provenance.json. The parallel plots
show every native ND line for the three preselected replica1 cases.

Final local quality:uv sync --locked passed(131 resolved/128 checked packages);
**885 tests passed in133.59s,98.24% coverage**, above the96.15% gate. Ruff passed;
strict mypy passed all79 source files. The five targeted audit tests also passed,
including dtype/tampering/PA/clipping checks and preservation of original runtime
observations after checkout. No historical test or numerical source was edited.

The release inventory verifies all24 prior pilot executions and77 initial
official attempts, including their two failures and source blobs at their own
recorded commits. The inventory counts5848 files/1155355542 bytes across versions,
5074 files/1103002068 bytes in the corrected campaign, excluding its own record,
checksum files and the separate Git-index observation. Largest payload:41882448
bytes. Direct versioning of the requested synthetic results follows the explicit
Phase10D preserve/version/push instruction; no LFS or material-license change.

Final-case checksums SHA-256:
31f970ea06024c4e992d039c3c98f28d71f3b45f99694d131241ad49d6c5f537.
All-version checksums SHA-256:
77d4edab80c8c385d72070a1ef1111d215598733c9f9c2eae411b619b3d6f820.
The Git-index byte observation is stored separately in staged_git_integrity.json
to avoid a circular self-digest:5851 staged blobs/1156889826 bytes matched their
working files exactly, with no omitted artifacts. Final Ubuntu/Windows CI evidence is attached to
the exact latest PR head in [PR17 checks](https://github.com/LimaGV/C-NBI-v2/pull/17/checks);
both operating-system checks are required before marking the PR ready for review.

The final PR remains open and is not merged automatically. No Phase10E, new
noise/CCDs/anchors/original-response RSM fits, retuning or reference modification.
The specified VRF auxiliary factor fits remain permitted.
