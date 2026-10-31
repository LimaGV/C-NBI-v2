# Definitive SVD + PA filter ablation

Only FILTER, RANDOM and ALL are compared. FILTER is the existing C-NBI-ES A0; RANDOM reuses all three existing A2 draws with the same per-k subset counts. ALL uses every admissible subset. The four cost-selected scenarios and all five original replicas are unchanged. This is a focused exploratory study; it does not support27-cell inference.


|Arm|IGD change vs FILTER (%)|HV change (%)|ND median|Subsets median|NBI subproblems median|
|---|---:|---:|---:|---:|---:|
|FILTER|0.000|0.000|70.0|12.0|133.5|
|RANDOM|13.191|-3.089|68.0|12.0|133.5|
|ALL|-24.640|2.426|282.0|35.0|510.0|

At the same per-k budgets, RANDOM changes focused IGD by 13.191% and HV by -3.089%. ALL changes IGD by -24.640% and HV by 2.426%. FILTER requests 3087 versus 19805 NBI subproblems (84.41% fewer). This is an exact effort comparison, not measured runtime savings.


Quality entries are medians of scenario medians of paired changes. RANDOM first averages the three draws within each scenario/replica. Its three seed-level rows remain separate in ablation_results.csv, and within-replica SD/range summaries remain in ablation_summary.csv. No seed is treated as another structural scenario.


## Design, compatibility and complete ALL reconstruction

All three arms share the exact model, nominal payoff/anchors, consumed uncertainty prefix and effective B of FILTER. No ES-versus-fixed-B comparison is performed. The stopping time is matched, not re-adapted to the random draw or ALL membership.

The477 previous local caches were checked before reuse: frozen coefficient hashes, payoff/anchors, local geometry, H, objective directions, solver defaults/tolerances, library versions and mathematical kernel bytes/AST. Historical cache points match their source records; accepted weights satisfy the unchanged NBI residual/ball checks. The original source and a byte-identical historical result copy remain available.

The universe has855 admissible instance/subset pairs. Only378 missing subsets (13208 NBI subproblems) were solved: nx=2 first (50/975), then nx=3 (328/12233) after the nx=2 integrity and measured-cost gate. Per-subset and per-instance checkpoints permit resumption without repeating completed solves.

ALL_candidates.npz contains the complete concatenation of accepted local candidates with subset/weight origins. ALL nondominance is rebuilt from that raw union via the unchanged10C evaluator, never from another arm's ND front. FILTER/RANDOM metrics are reused. The same5000-point references, normalization, strict feasibility, duplicate/dominance tolerances, indicators and HV precision rules are retained.


## Cost and interpretation limits

New solver times and function/gradient/internal-solve counters are observed for the missing complement and reported per instance. Cached component times retain their source campaign; known counters are explicitly partial when older local instrumentation did not record them. Shared cached work is nonadditive across random seeds. A full fresh RANDOM/ALL pipeline runtime was not observed.

No allocation-model time saving is claimed. Exact subset, NBI-attempt and candidate counts describe effort; they do not prove wall-clock speedup. FILTER versus RANDOM isolates selection at matched per-k budgets. FILTER versus ALL also changes candidate/ND cardinality, so it cannot isolate geometry from the benefit of more candidates. Solver rejections remain recorded rather than replaced with points.

The previous A1/A3 analyses are historical only; their caches remain available. No CCD, noise, RSM fit, MC sample, anchor/payoff optimization, reference, applied-case or MaF experiment was generated or changed.


## Scenario results

|Scenario|Arm|IGD|HV|IGD change (%)|HV change (%)|
|---|---|---:|---:|---:|---:|
|nx2_delta1_rho025|ALL|0.0832837|0.833922|-6.438|0.883|
|nx2_delta3_rho025|ALL|0.0658633|0.650941|-13.880|1.954|
|nx2_delta3_rho060|ALL|0.0561645|1.22241|-35.401|2.898|
|nx3_delta3_rho085|ALL|0.0295811|1.23468|-40.828|6.033|
|nx2_delta1_rho025|FILTER|0.0893151|0.824645|0.000|0.000|
|nx2_delta3_rho025|FILTER|0.0792708|0.638466|0.000|0.000|
|nx2_delta3_rho060|FILTER|0.0735576|1.1811|0.000|0.000|
|nx3_delta3_rho085|FILTER|0.0539849|1.16832|0.000|0.000|
|nx2_delta1_rho025|RANDOM|0.106014|0.791088|18.123|-4.069|
|nx2_delta3_rho025|RANDOM|0.0791982|0.626274|8.260|-2.110|
|nx2_delta3_rho060|RANDOM|0.0839129|1.17679|2.814|-0.142|
|nx3_delta3_rho085|RANDOM|0.0874037|1.0807|61.904|-7.500|

## Observed execution ledger

|Stage|Added subsets|Observed stage wall (s)|Sum of observed added solver times (s)|
|---|---:|---:|---:|
|nx=2|50|3.7547|2.5456|
|nx=3|328|555.4168|1829.8469|

Four numerical workers (one BLAS thread each) completed 378 added subsets. 176 local weights were rejected and retained in diagnostics. The profiled local routines recorded 56728801 scalar quadratic value calls, 5737870 analytic gradient calls and 14840 internal SLSQP solves. Counts include local geometry preparation where instrumented. The timing ledger measures only the missing complement and validation, not a fresh full ALL pipeline.
