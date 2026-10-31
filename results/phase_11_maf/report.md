# Phase 11: direct MaF8/MaF9 C-NBI V2

Completed: 100/100. Wall time: 594.77 s; summed optimizer time: 2075.68 s.


|Problem|m|Runs|IGD median|HV median|V1 IGD|V1 HV|ND median|
|---|---:|---:|---:|---:|---:|---:|---:|
|MaF8|4|10|0.07798792|0.3232208|0.07798792|0.3232208|38|
|MaF8|6|10|0.06854262|0.1511622|0.06854262|0.1511622|112|
|MaF8|8|10|0.06467325|0.06594048|0.06468339|0.06594048|214|
|MaF8|10|10|0.05738772|0.02817909|0.05742054|0.02817909|330|
|MaF8|15|10|0.05959969|0.003059508|0.05959969|0.003059508|489|
|MaF9|4|10|0.1256686|0.393459|0.1288075|0.3900633|38|
|MaF9|6|10|0.1167406|0.1973327|0.09299154|0.2105242|83|
|MaF9|8|10|0.1010518|0.09066815|0.1002758|0.09132233|158|
|MaF9|10|10|0.08053193|0.04369342|0.0805319|0.04369342|293|
|MaF9|15|10|0.0689349|0.005609098|0.06986678|0.005864057|751|

## Protocol and limitations

Direct distance objectives, nx=2, box [-10000,10000]^2; MaF9 forbidden regions are enforced without repair. All anchors are optimized, including the V1 minimum-norm tie rule for its nonunique line minima.

500 independent known-Pareto samples per seed are used only for correlation Horn PA (ddof=1, 1000 column permutations, linear q95, sequential strict rank). The V1 difference-SVD window is preserved using the V2 vertex-difference helper. RSM uncertainty screening/early stopping is inapplicable and unused.

Subsets k=2,3; H=5; local CHIM/normalization, lattice traversal, SLSQP and full-objective dominance are V2. No V1 solver imports. Necessary implementation differences: V2 warm starts/retries, centered CHIM normal, analytic piecewise domain Jacobian, and L2 equality acceptance <=1e-5 (V1 used infinity norm). V2 uses the payoff diagonal ideal; V1 used row minima (differences are limited to anchor floating-point roundoff in this campaign). MaF settings retain maxiter=100 and ftol=1e-10, t in [-10,10]. This is protocol replication, not an assertion of identical fronts.

External reference: 5000 area-uniform polygon points, seed404, independent of the diagnostic. Scaling is zero ideal and vertex-objective maximum, without clipping. GD/IGD and Sparsity reuse V2 Euclidean nearest distances; MaF Spacing uses population SD (ddof=0) as V1, unlike the corrected RSM study.

HV follows V1 exactly: one scrambled Sobol net of8192, seed2026+run_seed, fixed [0,1.1]^m. HV_se is the historical binomial proxy, not a calibrated QMC confidence interval. Precision is especially limited at m=15; no escalation or cross-study statistical test was added.

The V1 figures above are verified local saved summary values, hashed in the manifest, not independently verified published table entries. The manuscript confirms MaF stress-test scope. V1 recorded identical optimizer fronts across seeds within each configuration; HV variability includes integration seeds and must not be interpreted as optimizer variability.

V2 also returned one numerically identical front across all ten seeds in each configuration. MaF8 medians closely match V1. MaF9 is not numerically equivalent: at m=6, V2 IGD is about25.5% higher and HV about6.3% lower. The retained V2 solver produces a different valid front; no tuning or replacement of points was performed to match V1.

Rejected local subproblems: 0; maximum accepted L2 equality residual: 8.6819e-11. Failures are retained in each case diagnostic, never replaced with fabricated points.

Pilot MaF8/m4 and MaF9/m4/seed101 passed before remaining jobs. Completed checkpoints are hash-verified and never rerun. Earlier science/results and the applied case remain unchanged.
