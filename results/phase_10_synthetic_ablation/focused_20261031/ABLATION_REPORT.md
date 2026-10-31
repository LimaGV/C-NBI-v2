# Focused C-NBI V2 ablation

Exploratory evidence from four cost-selected cells, five frozen replicas each. C-NBI-ES (ADR0009, minimum300 / first500 / maximum2000) is the principal method. No conclusion is extrapolated to the27-cell benchmark.


## Selection and frozen protocol

The three cheapest B2000 cells were selected by the sum of recorded kernel timings.total across five replicas. The cheapest remaining nx=3 cell adds a decision dimension. No quality indicator entered selection. Cost ranking, exact subset plans, seeds and hashes were frozen before external evaluation.


|Scenario|nx|Five-replica B2000 cost (s)|
|---|---:|---:|
|nx2_delta1_rho025|2|15.6183|
|nx2_delta3_rho025|2|27.3583|
|nx2_delta3_rho060|2|32.0785|
|nx3_delta3_rho085|3|43.6501|

## Article-ready focused comparison

Values below are medians of four scenario medians of paired relative changes against A0. A2 first averages its three random draws within each replica. Negative IGD/GD/Spacing/Sparsity changes and positive HV changes favor the variant. Spacing/Sparsity also depend on cardinality; no equalization or inference is used.


|Variant|IGD change (%)|HV change (%)|ND change|NBI subproblems|Pipeline cost change (%)|Cost basis|
|---|---:|---:|---:|---:|---:|---|
|A0|0.000|0.000|0.0|133.5|0.00|Historical observed|
|A1|0.000|0.000|0.0|133.5|215.90|Historical observed|
|A2|13.191|-3.089|-9.0|133.5|0.53|Estimated reuse|
|A3|57.336|-11.888|-42.0|45.0|-7.65|Estimated reuse|

## Interpretation

Disabling ES (A1) changes focused IGD by 0.000% and HV by 0.000%. Its historical pipeline cost change is 215.90%; this is not a controlled speedup experiment.

Replacing PA selection with random matched per-k budgets (A2) changes IGD by 13.191% and HV by -3.089%. This isolates subset choice at the retained budget, not the computational removal of the PA diagnostic: the original ES uncertainty/stability history is retained.

A2 and A3 keep the paired A0 stopping decision fixed, including its monitored PA-selected IDs. Random subsets are not used to re-adapt the stopping time. The experiment therefore isolates subset choice/composition at matched uncertainty prefixes, not alternative ES dynamics for each random draw.

Retaining pairs only (A3) changes IGD by 57.336% and HV by -11.888%, at -7.65% estimated pipeline cost change. This measures the marginal contribution of higher-k solutions in the archived complete run, not a newly tuned pair-only method.


## Reuse, costs and limits

A0/A1 metrics are reused without reevaluation. A3 filters A0 raw pair candidates and repeats only frozen feasibility/uniqueness/ND recomposition and evaluation. A2 uniformly samples eligible nominally certified subsets without replacement within each k, using seeds181001/181002/181003 and independent per-instance hashed streams. It matches A0 counts at the same saved ES stopping prefix. Degenerate subsets and any budget deficit are explicitly recorded.

Nominal/MC anchors and models are read-only cached inputs. Local NBI caches from A0/A1 are reusable only for identical anchors, payoff and kernels; shared decisions are checked bitwise. A pilot reproduces one local solution set bitwise before solving only missing subset caches. No new MC, coefficient draw, anchor optimization, RSM fit, reference, comparator or MaF run occurs.

A0/A1 times are historical observed kernel times. A2/A3 full-pipeline costs are explicitly modeled: inherited A0 preparation plus cached subset solver time allocated proportionally to recorded SLSQP iterations, using the same paired A0 time per iteration for every subset, plus inherited postprocessing time. Actual new solver times are reported separately and never mixed into that model. Allocation is not measured local runtime and ignores fixed and retry-dependent overhead. It can understate costly line searches in random subsets, so estimated A2 costs cannot establish a processing-time benefit or equivalence. No total function/gradient counts are invented for cached subsets. The actual new execution cost is separately recorded; shared cache work must not be summed repeatedly across random draws.

Screening, nominal/MC optimization, NBI and postprocessing fields remain separate where originally observed. A1 preparation was not historically split into every screening component; missing components remain unavailable. Timing comparisons across historical and current campaigns have hardware/load and profiler limitations. No claim of global speedup is made.

All metrics use the unchanged analytical10C reference, normalization, strict feasibility and duplicate/ND tolerances and frozen HV precision rules. Undefined HV remains undefined; no precision escalation or clipping is added. Objective coverage counts distinct objective IDs in selected subsets, not an invented front-coverage indicator. Only nx=2 and nx=3 are represented.

Rows: 120 (A0/A1/A3:20 each; A2:60). Undefined metric entries: 0.

Existing27-cell principal analyses and pairwise10E equalization remain unchanged.

The zero focused median does not imply identical results in every replica. B2000 and ES have identical IGD/HV in15/20 paired cases. B2000 improves both in four cases and worsens both in one. Its IGD change ranges from -7.925% to 13.936%; HV ranges from -2.088% to 0.724%.

## Scenario sensitivity and measured added work

|Scenario|Variant|IGD change (%)|HV change (%)|Cost change (%)|
|---|---|---:|---:|---:|
|nx2_delta1_rho025|A1|0.000|0.000|243.28|
|nx2_delta3_rho025|A1|0.000|0.000|196.47|
|nx2_delta3_rho060|A1|0.000|0.000|96.61|
|nx3_delta3_rho085|A1|0.000|0.000|235.34|
|nx2_delta1_rho025|A2|18.123|-4.069|0.00|
|nx2_delta3_rho025|A2|8.260|-2.110|1.05|
|nx2_delta3_rho060|A2|2.814|-0.142|-0.16|
|nx3_delta3_rho085|A2|61.904|-7.500|1.21|
|nx2_delta1_rho025|A3|68.895|-17.626|-6.00|
|nx2_delta3_rho025|A3|108.773|-32.261|-13.92|
|nx2_delta3_rho060|A3|45.776|-6.149|-5.27|
|nx3_delta3_rho085|A3|4.979|-0.618|-9.30|

|Variant|B median|NBI subproblems (sum)|Pipeline time sum (s)|Basis|
|---|---:|---:|---:|---|
|A0|500|3087.0|73.5472|Historical observed|
|A1|2000|3064.0|118.7051|Historical observed|
|A2|500|3087.0|127.7141|Iteration model|
|A3|500|966.0|39.0827|Iteration model|

Actual added search: 215 unique subset solves, 3435 NBI subproblems, 280.134 s in the solver and 45 rejected local weights, plus 0.0107 s for the mandatory cached-subset pilot. Exact function/gradient/internal-optimization counts are in execution_costs.json. A2 full-pipeline time was not observed; the sum above is an allocation model and must not be compared as a measured speedup.
