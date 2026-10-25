# Phase8 verification — revised scope accepted by the owner

Branch: `feature/08-reference-sensitivity-final-benchmark`.
PR10 was reviewed at c0d7dfd with four successful Windows/Ubuntu checks and no
conflict, then squash-merged to main f904e8de0810324b4456cf2ad7de59ca2c6b5ab4.
Local main was updated/clean before the new branch. The publication head/PR/live
CI are reported in the delivery and PR; a commit cannot embed its own hash.

## Scientific and publication provenance

| Stage | Source commit | Launch/source condition |
|---|---|---|
| Phase8A | 3ac57ecb9dcd9912e0ebe4576a772471c902e8e3 | committed/clean; no new reference EA runs |
| Controlled EA timing | 70883d7c8dc5954f3438b0b43e5274b07cf16e0a | committed/clean; same commit/config throughout all20 measured runs |
| Native/K/checkpoint quality | a0b38817e99cc91c8a6e244fd38ad8e6d87c4fd1 | committed/clean; postprocessing after timing completed |
| Reporting/layout | recorded source hash/commit in metadata and figures/visual_mapping.json | later presentation edits; numerical inputs and metrics unchanged |

The timing script later received a line-wrap-only change to its hardware-inventory
PowerShell text. Its recorded execution hash remains historical; no timing was
rewritten or attributed to the newer source. The callback/default algorithm path
and all scientific operators remain unchanged. Unit checks and all20 actual
controlled final populations are bitwise identical to their frozen Phase7 seeds.

Date-bearing run ID20261024 identifies the request/protocol and fixed sampling
seed; actual execution timestamps are UTC metadata on2026-10-25. The random seed
was not silently changed after the overnight continuation.

## Scope correction: H5 and VRF

The mandatory H5 direct-equivalence gate **FAILED**, not passed by relaxed bounds:
24/492 weights differ above predeclared x/z1e-5, maxΔx3.118120710729887 and
maxΔz.5942667067502265. Both paths satisfy constraints with matching geometry;
different continuation/warm-start paths reach different feasible local branches.
CSV/NPZ/JSON retain the counterexample. Software tests pass by verifying that
this scientific failure blocks cost attribution, not by asserting equivalence.

The owner explicitly replied: preserve408, conclude Phase8B quality and report
CNBI cost pending. Therefore zero CNBI timing repetitions at any H; the direct
H5 diagnostic is not a runtime benchmark. No solver/initialization/tolerance or
baseline was changed. The parent-H20 time is never presented as H5 time.
Other H values are only frozen membership-quality diagnostics, with no cost.

The owner explicitly forbids VRF execution. The benchmark reads only the66
already reevaluated Phase7 historical points. Zero VRF optimizations/timings;
no invented or historically incomparable runtime. Temporal efficiency analysis
has EAs only and cannot establish CNBI/VRF competitiveness.

## Required final-report coverage

| Requested items | Delivered evidence |
|---|---|
| 1–3 branch/head/PR | Branch above; published head and open PR in delivery/PR body |
| 4 input hashes | metadata input_sha256/phase8_input_sha256; Phase7 manifest, dataset/model/normalization/subsets, final reference and source audits |
| 5–9 exact equations | mathematics/reference_sensitivity_and_cardinality_control.md: GD/IGD p1, dominated volume, corrected V1 sampleSD Spacing and meanNN Sparsity |
| 10 HV point | hv_reference_point.json, logical config hash5170df63be007610e3d0fecb03152eaa959ccde19a6dbf33c9e283a3265e59d5; one shared point and Sobol grid |
| 11–16 runs/subsample distributions/curves | 100 distinct paired subsets at5/10/15/20/25, singleton30;506 reference rows,48 statistical-summary rows, full replicate CSV, seed arrays, four figures |
| 17–20 composition/marginals | six compositions, reference_marginal_effects.csv and paired HV precision CSV; explicit VRF, NSGA3 and MOEAD effects |
| 21–23 reference K/stability/freeze | seven nested K_R levels, three figures; R30 reproduced exactly18503 ND/zero CNBI; qualified empirical interpretation in application report |
| 24–29 native metrics/statistics/cardinalities | native_metrics.csv124 rows (62 sets x2 labels), native_metrics_summary.csv, main_table_A_native.csv; single deterministic observations/30 EA runs |
| 30–33 K66/curves/Kmax | equalized_k66_metrics.csv124 rows,1352 curve rows,62 nested candidate orderings; Kmax303 from genuine minimum, no fabricated points |
| 34–35 better-run fractions/percentiles | deterministic_percentiles.csv, common target only; oriented score and midrank ties, no p-values or naive cross-target LOO ranks |
| 36 CNBI direct timing | pending by explicit revised scope after failed gate; timing_cnbi.csv has five status rows, zero repetitions/time values |
| 37 VRF timing | user prohibits execution; timing_vrf.csv has explicit unavailable status, zero repetitions |
| 38–41 controlled EA cost/curves | 10 seeds each, same machine/env/commit, thread1, serial, warm-up;100 snapshots/200 metric-label rows, IQR figures for IGD/HV vs time |
| 42 quality-cost Pareto | quality_cost_pareto.csv of10 configuration medians in common-target(T,IGD)/(T,-HV), EAs only |
| 43 feasibility | feasibility.csv and metadata: max norm1.681792830510297, radial excess2.8679281172117044e-12, zero violations above1e-9; frozen squared-margin rule also passes |
| 44–45 artifacts/checksums | exact reviewed run directory,14 figures PDF/SVG/PNG600dpi, tables, lineage, metadata and checksums.sha256 |
| 46–49 local software quality | commands/results below |
| 50–51 CI/Git | live Windows/Ubuntu PR checks and final clean/synchronized branch in delivery; no merge |
| 52–53 ADR/claims | ADR0012 ACCEPTED revised scope; C-BENCH-01..06, with partial resolution-cost support explicitly marked |
| 54–55 limits/final scientific interpretation | application report answers reference, cardinality, cost and H5/coarse-to-fine questions; no true-front, universal-winner or temporal-CNBI claim |

## Local quality results

- `uv sync --locked`: passed,131 resolved packages/128 installed checked.
- `uv run pytest -v`: **620 passed**,47.97s.
- `uv run pytest --cov=cnbi_v2 --cov-report=term-missing`: **620 passed**,66.53s;
  **99.39%** coverage,2314 statements/14 missed, required96.15%.
- Final presentation/metadata update: archival integrity tests **5 passed**,10.85s.
- `uv run ruff check .`: passed.
- `uv run mypy src`: passed,44 source files.

Raw/processed experimental data, earlier result directories, models, normalization,
37 IDs and prior scientific modules have no diff against merged main. The only
existing scientific adapter edit is an optional observer argument; default kwargs
remain identical and noninterference is demonstrated. No RSM refit/reconstructed
observations, new uncertainty MC/anchors/PA or parent NBI scientific campaign.
The full QA suite retains earlier temporary unit/smoke validations as required;
none replaces a preserved scientific result.

Generated SVG/caption/mapping payloads retain renderer bytes via exact -text Git
attributes so checkout cannot silently invalidate their checksums by normalizing
Windows line endings. NPZ/PDF/PNG already use binary attributes. Numeric tables
and metadata use LF. The numerical800292864-byte attainment cache is regenerable
and ignored under experiments/runs; it is not published as experimental evidence.

Context7 supplied current pymoo callback documentation. Moocore was not resolved
there; official docs/installed code were inspected for bounded exact-HV probes,
but production retains the audited V1 Sobol integral and introduces no dependency.
Serena initially provided symbols/callers; after the overnight continuation its
LSP manager was unavailable, so the two-line optional-callback edit used a targeted
patch with caller review and numerical noninterference checks.

Figures were visually inspected; duplicate minor log tick labels were removed.
Colours/markers are centralized. HV approximation precision, density sensitivity,
different LOO targets, filtered historical VRF source and missing CNBI/VRF runtime
remain material limitations, not hidden warnings or completed gates.
