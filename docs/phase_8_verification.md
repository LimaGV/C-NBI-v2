# Phase8 verification — standalone baseline correction

Official definition: C-NBI(H=5)=standalone H5. H20=high-resolution sensitivity
only. The owner explicitly authorized this pre-merge correction on PR11 in the
same feature/08-reference-sensitivity-final-benchmark branch. The earlier408 /
cost-pending decision is SUPERSEDED, not silently rewritten.

## Provenance and integrity

- Baseline9 measured runs: source/protocol committed clean at3e23701 (full hash
  in correction launch.json), sequential/one numerical thread. H5 five runs;
  H2/H4/H10/H20 one run each. One unreported H2 warm-up.
- Actual filesystem isolation: all Phase6/7 result roots temporarily renamed
  during every solve,restored in finally. No parent artifact is a scientific input.
- Official runner needs only upstream Phase2/5 files and the explicit frozen
  correction protocol. The earlier Phase6 acceptance/dedup/dominance settings
  were transcribed verbatim into that protocol,verified before execution.
- Runner was formatted after timing; the historical execution source is checked
  against its Git blob at launch commit,not a later formatting-only revision.
- Analysis source committed clean at30cbb3c; no optimizer/reference resampling
  or reference FPS is called by targeted postprocessing. Reference lineage512
  arrays and seed subsets are reused by recorded hash.
- Old Phase6/7 and Phase8 parent-derived result directories remain byte-identical.
  Old Phase8 manifest SHA256:
  c0e8ab1ccd8d4b8d42ca03dffec22afb86200d4dc371da5993276001bf3b3988.
- New archive:results/phase_08_final_benchmark/turning_standalone_correction_20261025.
  Each payload is hashed in checksums.sha256. Original archive labels retain
  historical execution meaning; the results-root README explicitly supersedes
  them as official baseline labels. Frozen old protocol JSON is also historical.

## Scientific acceptance

492 expected/492 accepted/0 failures,411 unique decisions,409 ND. Five H5 runs
have bitwise-identical scientific arrays and match predeclared atol1e-12,rtol0.
No tolerance or warm-start/solver change. eq_norm<=1e-4,margin>=-1e-9 unchanged.
Full x,z,t,subsets/compositions and starts/trials/status/iterations/solve times
are archived. The first H5 defines the baseline regardless of metric changes.

All standalone resolutions satisfy the sphere: maximum norm1.681792830510297,
maximum positive radial excess2.8679281172117044e-12,zero violations above1e-9
and zero under the frozen squared-margin rule. No RSM/data/MC/anchors/PA/subsets
or earlier algorithm changed. No EA/VRF campaign repeated.

Independent target remains18503/zeroCNBI. Historical common target22523 is only
HISTORICAL_COMMON_H20_TARGET,not a new self-included pooled target. This retains
all other-method metric numbers exactly. Family LOO targets differ; no naive
cross-family LOO ranking. New CNBI independent assessment uses the complete
frozen reference; all K curves keep complete targets. H5 FPS/K66 uses409 ND.

## Forty requested delivery items

| Items | Evidence |
|---|---|
|1–4 branch,commit,PR,CI|Same branch/PR11; published head,CI URLs and status in PR and final delivery|
|5–9 H5 counts|H5_rep1.npz,official_cnbi5.npz,records and metadata;492/492/0/411/409|
|10–14 five native metrics|native_metrics.csv,two explicit target labels; independent results in main report|
|15–16 K66/cardinality|new409-point FPS ordering,K66,complete grid20..303; other method entries unchanged|
|17–19 reference sensitivity|506 rows/512 saved references,100 stored subsets reused; GD/IGD recalculated,structural fields/hash preserved|
|20–24 each standalone H|H2/H4/H5/H10/H20 NPZ/records/trials; independent mesh/solve,not membership|
|25–27 runtime|timing_cnbi.csv,timing_summary.csv;solver,total,H5 median/IQR/min/max,n1 explicit for other H|
|28–29 IGD/HV vs time|new figures and cost tables; original controlled EA timing retained; no VRF runtime|
|30–31 old/new and24 cases|old_vs_new_metrics.csv,parent_vs_standalone_all492.csv,historical_24_divergent_cases_named.csv|
|32–34 docs/ADR/claims|updated mathematical report/definition,ADR0012,C-BENCH-06/07,methodology_status,README/CHANGELOG|
|35–38 software|final check results below; new tests cover counts,mesh,5 repetitions,blocked parent access,own runtime,official source,K66,preservation|
|39 checksums|new checksums.sha256 plus unchanged historical manifest; verify actual Git blob payloads before push|
|40 Git status|clean/synchronized head reported at delivery; no automatic merge|

## Software validation

- uv sync --locked:passed,131 resolved/128 installed packages checked.
- uv run pytest -v:**631 passed**,46.94s.
- uv run pytest --cov=cnbi_v2 --cov-report=term-missing:**631 passed**,67.30s.
- Coverage:**99.39%**,2314 statements/14 missed;threshold96.15% passed.
- uv run ruff check .:passed.
- uv run mypy src:passed,44 source files.
- CI is verified at the published correction head and linked in the PR/delivery.

The historical loader was renamed semantically with Serena to
load_historical_parent_grid_inputs and all callers updated. Official entrypoints
are standalone; no generic loader can silently return the old408 baseline.
execution_source_audit.json confirms identical runner AST after formatting and
hashes ancillary executed sources at their actual historical commit.
baseline_registry.json maps every old H5 source to its explicit historical role.
No new dependencies. Context7 SciPy cKDTree docs consulted for exact nearest
queries; no change to frozen metric definitions. Context7 actions/checkout
confirms fetch-depth:0; CI fetches history to verify executed source bytes at
recorded commits, instead of assuming a later formatted source is identical.
Serena symbols/callers inspected
before work; the existing NBI solver was left unchanged. Twelve new scientific
figures(PDF/SVG/PNG600dpi) are visually verified,with captions.

No adaptive refinement,new synthetic campaigns,new metaheuristics or automatic
merge. Historical gate failure remains24/492 path-dependence evidence; the
standalone correction removes the invalid scientific baseline definition rather
than changing the solver to make the gate pass.
