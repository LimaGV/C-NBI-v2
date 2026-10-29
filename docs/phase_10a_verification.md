# Phase10A verification —27 structural synthetic scenarios

Branch:feature/10-synthetic-scenario-generation.
Base:4432e333b75fe9427c7e5340bf952a05858ad19e; consolidated main CI
40890066315 SUCCESS on Ubuntu/Windows. No original scientific module or result changed.

## Protocol and implementation

True objectives are only f_j(x)=||x-a_j||²,all MIN. nx2/3/5,delta1/3/5,
m=nx+1+delta,alpha=2**(nx/4),absolute-correlation targets.25/.60/.85.
Exactly one final configuration per factorial cell. Row-oriented anchor arrays
are documented as the transpose of mathematical column notation.

Code/tests/protocol were committed before the official launch.8 SLSQP starts,
maxiter400,ftol1e-10,analytic objective/constraint derivatives; deterministic
cell-keyed PCG64/Sobol seeds.16,384 fixed calibration points and65,536 holdout
points,uniform in ball volume. Holdout generated only after candidate selection.
Selection never reads the signed mean or validation results. Failed candidates
would remain archived,without relaxing0.05 or choosing by holdout.

Direct-distance evaluations certify all minima exactly zero. Every anchor is
strictly certified norm<=alpha,distinct and full affine rank nx. All correlation
matrices are symmetric,unit diagonal and PSD within1e-10; expected ranks3/4/6,
less than m,are accepted without regularization.

## Numerical outcome

**27/27 validated**,216 starts,zero solver failures/failed cells.
Maximum calibration error:4.5196132855196414e-05.
Maximum independent-validation error:0.00012444084694640534.
Maximum per-entry discrepancy against exact uniform-ball population correlation:
calibration=0.00086567669210853293,validation=0.00022145125512451624;
both below the predefined0.005 sampling budget. This is a numerical accuracy
check,not a statistical confidence interval. No sample sizes/seeds were adapted.
Minimum normalized anchor separation:0.00010004972200266893;required>=1e-4.
Maximum normalized anchor norm:0.99999999981889764;required<=1.
Observed signed correlation[min,Q1,median,Q3,max],linear quantiles:
[-0.1999100994498769, 0.00824771202431119, 0.09001956093400852, 0.15455504621803356, 0.5257948961685558]. Mean=0.10789782722334867;
5 below zero,22 above zero. These are observations,not controlled levels.
Official calibration time:4.512261s;total generation/export:
10.486788s,Windows/Python3.12.15. Timings describe this
generation only,not comparisons between multiobjective algorithms.

## Complete scenario table

Realized absolute/signed correlations and the error below refer to the independent
validation sample. Display rounded to8 decimals; CSV preserves17 significant digits.
Calibration errors are also stored separately in synthetic_correlations.csv.

| Scenario | nx | delta | m | Target | Realized abs | Signed | Error | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| nx2_delta1_rho025 | 2 | 1 | 4 | 0.25 | 0.24998189 | 0.15427410 | 0.00001811 | VALIDATED |
| nx2_delta1_rho060 | 2 | 1 | 4 | 0.60 | 0.60002110 | -0.02764637 | 0.00002110 | VALIDATED |
| nx2_delta1_rho085 | 2 | 1 | 4 | 0.85 | 0.85001048 | -0.19991010 | 0.00001048 | VALIDATED |
| nx2_delta3_rho025 | 2 | 3 | 6 | 0.25 | 0.25001618 | 0.21044234 | 0.00001618 | VALIDATED |
| nx2_delta3_rho060 | 2 | 3 | 6 | 0.60 | 0.59995932 | 0.52579490 | 0.00004068 | VALIDATED |
| nx2_delta3_rho085 | 2 | 3 | 6 | 0.85 | 0.84999772 | 0.07212159 | 0.00000228 | VALIDATED |
| nx2_delta5_rho025 | 2 | 5 | 8 | 0.25 | 0.25004652 | 0.24999579 | 0.00004652 | VALIDATED |
| nx2_delta5_rho060 | 2 | 5 | 8 | 0.60 | 0.59995063 | 0.14047550 | 0.00004937 | VALIDATED |
| nx2_delta5_rho085 | 2 | 5 | 8 | 0.85 | 0.84999104 | 0.25044939 | 0.00000896 | VALIDATED |
| nx3_delta1_rho025 | 3 | 1 | 5 | 0.25 | 0.24998282 | 0.10168305 | 0.00001718 | VALIDATED |
| nx3_delta1_rho060 | 3 | 1 | 5 | 0.60 | 0.60002593 | 0.00291773 | 0.00002593 | VALIDATED |
| nx3_delta1_rho085 | 3 | 1 | 5 | 0.85 | 0.85004865 | -0.08096948 | 0.00004865 | VALIDATED |
| nx3_delta3_rho025 | 3 | 3 | 7 | 0.25 | 0.25001089 | 0.13288433 | 0.00001089 | VALIDATED |
| nx3_delta3_rho060 | 3 | 3 | 7 | 0.60 | 0.60001075 | 0.15483600 | 0.00001075 | VALIDATED |
| nx3_delta3_rho085 | 3 | 3 | 7 | 0.85 | 0.85004405 | 0.52375140 | 0.00004405 | VALIDATED |
| nx3_delta5_rho025 | 3 | 5 | 9 | 0.25 | 0.24999435 | 0.16081657 | 0.00000565 | VALIDATED |
| nx3_delta5_rho060 | 3 | 5 | 9 | 0.60 | 0.60002480 | 0.01488537 | 0.00002480 | VALIDATED |
| nx3_delta5_rho085 | 3 | 5 | 9 | 0.85 | 0.85000314 | -0.00724443 | 0.00000314 | VALIDATED |
| nx5_delta1_rho025 | 5 | 1 | 7 | 0.25 | 0.25001165 | 0.08580528 | 0.00001165 | VALIDATED |
| nx5_delta1_rho060 | 5 | 1 | 7 | 0.60 | 0.60009888 | -0.03729886 | 0.00009888 | VALIDATED |
| nx5_delta1_rho085 | 5 | 1 | 7 | 0.85 | 0.84998748 | 0.10776708 | 0.00001252 | VALIDATED |
| nx5_delta3_rho025 | 5 | 3 | 9 | 0.25 | 0.24999839 | 0.05520251 | 0.00000161 | VALIDATED |
| nx5_delta3_rho060 | 5 | 3 | 9 | 0.60 | 0.60012444 | 0.06302999 | 0.00012444 | VALIDATED |
| nx5_delta3_rho085 | 5 | 3 | 9 | 0.85 | 0.84987749 | 0.01357769 | 0.00012251 | VALIDATED |
| nx5_delta5_rho025 | 5 | 5 | 11 | 0.25 | 0.24999037 | 0.09001956 | 0.00000963 | VALIDATED |
| nx5_delta5_rho060 | 5 | 5 | 11 | 0.60 | 0.60006953 | 0.15266281 | 0.00006953 | VALIDATED |
| nx5_delta5_rho085 | 5 | 5 | 11 | 0.85 | 0.85001531 | 0.00291760 | 0.00001531 | VALIDATED |

## Reproducibility and preservation

Final generation source commit:06323416c5934836c3879f3603c17e8d0775e8cf.
The initial27-cell generation used93ed779. After visual QA,only the error-figure
axis was refined for legibility; tolerance is stated explicitly when outside the
plotted range. A second clean official launch used the same scientific code,
seeds,parameters and sampling. Anchors/scenarios CSV and the complete NPZ are
byte-identical between launches; numerical diagnostic fields are identical,
excluding measured elapsed times. The initial output is retained in ignored
local QA storage,not as a second published structural configuration.

All27 cells were also recalibrated in reverse order; every anchor and every
calibration/validation/population matrix reproduced exactly. Receipt:
reproducibility_check.json. No global RNG state or per-order seed assignment.
The formal unit test also checks forward/reverse order on small cells.

1,110 preexisting tracked files are verified against baseline Git objects before
and after generation. Their full SHA256 inventory is frozen_inputs_manifest.json.
Only current-state documents and the exact new-run ignore exception are mutable;
all scientific code,data/results,licensing and archived figures remain protected.
The frozen inputs,source hashes,uv.lock hash,versions,seeds,solver diagnostics and
run status are recorded. No new dependency or change to the lock was needed.

## Artifact inventory and figure review

results/phase_10_synthetic_generation/structural_20261029/ contains:

- synthetic_scenarios.csv:27 unique factorial cells and certification status.
- synthetic_anchors.csv:complete long-format coordinates,scenario/response/coordinate IDs.
- synthetic_correlations.csv:27 rows,calibration/holdout/population summaries and errors.
- synthetic_correlation_matrices.npz:108 float64 arrays,anchors and three full matrices per cell.
- calibration_diagnostics.csv:216 starts,convergence,evaluations,iterations,constraints,timing.
- calibration_config.json:complete frozen protocol and seed rules.
- calibration_manifest.json:code/base/environment/hashes,outcome/failures/timings.
- frozen_inputs_manifest.json,reproducibility_check.json,README.md,checksums.sha256.
- figures/:exactly four English diagnostics,each PNG600dpi and fully vector PDF.

All four figures were visually inspected. No coordinate gridlines. Correlation
heatmaps use first/middle/last lexicographic cells,without inspecting performance
or sign. Numeric heatmap labels are rounded only for display. The error plot
shows the observed range; its title states acceptance0.05 outside that range.
Source tables/NPZ retain the full numbers. No benchmark or algorithm-performance
figure was fabricated. No CC data/figure license is applied; MIT remains code-only.

## Quality checks

Initial complete suite:750 passed,coverage99.23%,gate96.15% satisfied.
Final post-QA suite:750 passed in84.91s,coverage99.23%. Remote Ubuntu/Windows
CI is linked in the PR after completion; no automatic merge.
Ruff and mypy53 source files passed.64 new tests include the published archive,
all27 certificates,precision,roundtrip,hashes,holdout separation and no forbidden
scientific-pipeline imports/calls. Existing regression tests retain their original
API checks; no new multiobjective campaign or synthetic benchmark was run.

Reproduction to a fresh ignored directory:

```powershell
uv sync --locked
uv run python -m scripts.validation.generate_synthetic_scenarios --output experiments/runs/synthetic_reproduction
uv run pytest --cov=cnbi_v2 --cov-report=term-missing
uv run ruff check .
uv run mypy src
```

The generator refuses to overwrite prior evidence; official generation requires
committed source/protocol and a clean launch. Numerical repeatability is tested
in the pinned environment; no universal cross-platform bitwise guarantee is claimed.
No noise,CCD,RSM,coefficient MC,CHIM/PA,methods Pareto,reference,GD/IGD/HV/Spacing/
Sparsity or benchmark performance statistics were implemented in this phase.
The Phase10A PR must remain unmerged unless separately authorized.
