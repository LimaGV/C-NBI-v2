# Phase 7 source audit — completed before new evolutionary runs

Scope: local V1 `CNBI` at `7bd4915a9aea94b9dca1d70014ba5186b4b4e44d`,
its `CNBI-Synthetic-Benchmarks` checkout at
`bdd64313b55e275c3e2cec321ea5d86012917a1a`, and frozen V2 Phase6.
No legacy module is imported, modified, or executed. Some historical result
files are local/ignored artifacts: their checkout commit is context, **not proof
that those artifact bytes were tracked by Git**. File hashes and sizes are in
`references/metadata/phase_07_v1/source_provenance.json`.

| method | artifact | decision_vectors_available | canonical_reevaluation_possible | historical_config_available | usable_for_reference | reason |
|---|---|---|---|---|---|---|
| NSGA3 | applied_8d_equal_budget/final_fronts/nsga3_seed001.csv, other saved seeds | yes, cs/f/md | yes | yes | not selected for principal pool | historical final fronts exist; principal pool uses 30 new equal-budget canonical runs |
| MOEAD | applied_8d_equal_budget/final_fronts/moead_seed001.csv, other saved seeds | yes, cs/f/md | yes | yes | not selected for principal pool | same decision as NSGA3; no old objective values enter canonical union |
| VRF | derived_amm_20261020/provenance/vrf_final_objectives_from_saved_coefficients.csv | yes, 66 literal cs/f/md rows | yes, all within sphere | partial, source/export script and workbook identified | yes after current-RSM reevaluation | coordinates preserved; old response columns discarded |
| CNBI | Phase6 local_nbi_solutions_H20.npz and provenance.csv | yes | yes | yes, frozen Phase6 metadata | H20 only contributes; H5 evaluation only | recover exact integer memberships, no new NBI solve |
| synthetic V1 EAs | DOE/MaF archives | yes in inspected examples | no as turning evidence | yes | no | different problem/variable dimension; not experimental turning decisions |

## Calibration transfer authorized by the owner

The initially located general V1 calibration concerned synthetic 8-objective,
2-variable problems. A deeper audit located the more specific **applied turning
3-variable/8-response** calibration. The latter is the operator source:
`CNBI-Synthetic-Benchmarks/results/applied/applied_8d_equal_budget/tuning/selected_parameters.json`.
The 365-byte file is copied byte-identically to
`references/metadata/phase_07_v1/applied_ea_calibration.json`, SHA256
`0417657aa8847c3bef551eaaa259adf4f149b0e44e9063be5709d0b0eed7ff5b`.
No new hyperparameter tuning is performed.

Both use Das–Dennis partitions4, hence C(11,7)=330 directions/population.
NSGA3: SBX probability .9, eta10; polynomial mutation eta15.
MOEAD: SBX probability1, eta10; mutation eta30; neighborhood fraction .2
(66 neighbors), neighborhood mating probability .9. Historical notebook
`12_cenario_aplicado_EAs_orcamento_igual_corrigido.ipynb`, `make_alg`, directly
confirms PM individual probability1/3, SBX/PM repairs and the configured operators.
The notebook is read as JSON only, never executed.

Historical calibration seeds1010/2110/3070; final seeds1..10. Applied run manifest
cap19830 gives60 complete generations, actual19800 search evaluations/run.
Those settings were selected on historical models/reference; their transfer is
a configuration reuse decision, **not fresh validation of optimal tuning**.

For reference construction, freeze **132000 NFE/run =400*330**. This follows
the separately identified V1 general `BUDGET_POLICY.md` rule
max(50000,400*C(m+3,4)) at m8. It is deliberately larger than historical
applied19800; it is not the old applied budget or a mathematical constant.
Both current algorithms receive the same cap and30 seeds1001..1030.

## Explicit library and representation differences

V2 adds pinned `pymoo==0.6.2` rather than implementing either EA. Classes:
`pymoo.algorithms.moo.nsga3.NSGA3`, `pymoo.algorithms.moo.moead.MOEAD`.
Version and transitive resolution are in uv.lock. Context7 pymoo documentation
was consulted for algorithms/operators/repair, then installed source inspected
for signatures/defaults. A SciPy Context7 query failed; KDTree API is checked
against the installed implementation and independent distance oracles.

Explicit preserved operator defaults: SBX prob_var=.5, prob_exch=1,
prob_bin=.5, two offspring; PM individual probability1/3 and per-variable1/3,
at_least_once=False. NSGA3 uses330 offspring/generation and duplicate elimination.
MOEAD uses PBI theta5, standard strict scalar improvement replacing every improved
neighbor, one evaluated offspring per individual, seeded random population order.
Pymoo's MOEAD does not accept general inequality constraints; feasible uniform
ball sampling plus deterministic radial repair and an evaluation guard impose
the sphere explicitly. Repair counts are archived, not silently discarded.

Current fitness is globally normalized, MIN-oriented current nominal f, identical
for both methods. The old applied notebook evaluated unnormalized MIN f; this
representation difference matters particularly for decomposition. Current
fixed normalization, no clipping, ball sampler and numerical-only deduplication
are explicit Phase7 decisions, not hidden inherited V1 behavior. Old V1 rounding
to10 decimals and old model-dependent sanitization are not reapplied.

## Historical VRF eligibility

The source export has66 decision vectors; norm range
0.14128277478389079 to1.6660848515194757, below alpha=8**.25.
`applied_data.py` identifies columns cs/f/md, coded cutting speed/feed/depth in
that order. Literal strings map to x1/x2/x3 without inverse coding, rounding,
projection or reconstruction. Only these coordinates/source row IDs are copied
into `data/external/turning_reference/vrf_historical_decisions.csv`.
Original export hash `e1bea7d1ac4e7bfc5fafa87a1c0da6e958c9c3604ec4fe107d21a49b585e2e29`;
extracted coordinates hash
`f41b338c8927c635d18e60ab363c900116e9a7894177b9d740a433581fd2661a`.

The export was already historically sanitized, deduplicated and ND-filtered under
old models (`common.py::sanitize` called by `applied_data.py`); it is not an
unfiltered original search log. The identified underlying workbook is
`data/applied/VRF_Pareto.xlsx` (hash in source metadata). No new VRF optimization
or claim of exact published VRF algorithm reproduction is made. All66 retained
x must be reevaluated under current nominal RSMs before current ND filtering.
Historical T/MTTF/etc values never enter canonical construction.

## Frozen prior results

Phase6 H5:492 subproblems,411 unique decisions,408 ND. H20:4557 subproblems,
4476 unique,4417 ND. Recover H5 by archived exact membership and all original
provenance; compare reevaluated responses with archived ones using
atol5e-14, rtol2e-14. Current-RSM vectorized and existing scalar evaluator are
independently cross-checked. H20 alone contributes the CNBI pool; H5 is baseline
evaluation only. No MC, anchors, PA or NBI scientific run is repeated.

The Phase6 integrity test retains the archived **historical uv.lock digest**
instead of requiring that historical dependency environment to equal the newly
extended environment. All other Phase6 inputs/results remain byte checked.
No saved scientific artifact or previous test result is rewritten.
