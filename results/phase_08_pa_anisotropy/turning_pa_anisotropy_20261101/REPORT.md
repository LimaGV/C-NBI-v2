# Applied PA versus PA + anisotropy ablation

Experimental post-hoc analysis; the principal C-NBI method is unchanged.

## Frozen design and integrity

q_S = sigma_(k-1)/sigma_1; retain q_S >= 0.3129205407188535. The cutoff is the global second/first singular-value ratio (d=2), specified before evaluation. All 37 PA-approved centered spectra are read from Phase5; 27 survive (19 pairs, 8 trios). All pairs have q=1; ten trios are removed.

The full standalone H5 archive (492 accepted rows) is filtered by subset identity BEFORE decision deduplication and full eight-objective dominance. PA recomposition reproduces 411 unique / 409 ND; the combined filter gives 228 unique / 228 ND. All five archived timing repetitions are bitwise identical scientifically.

## Quality

Independent empirical reference: 18,503 archived points, excluding the entire C-NBI family. Fixed Phase5 global MIN normalization and Phase8 coordinate tolerances are unchanged. GD/IGD use mean Euclidean nearest distances; Spacing uses ddof=1; Sparsity is mean nearest-neighbor distance. HV reuses the official bounds and exact quadrature nodes: four PCG64 scrambled Sobol nets, 2^16 nodes each, seeds 20260–20263. Native PA and K66 metrics reproduce their official saved values. HV is an estimate, with the original across-scramble QMC SE.

|Comparison|Metric|PA|PA + anisotropy|Change (%)|
|---|---|---:|---:|---:|
|native|GD|0.039491734|0.040148262|+1.6624|
|native|IGD|0.14114373|0.18035923|+27.7841|
|native|HV|0.73902853|0.61320062|-17.0261|
|native|Spacing|0.032127424|0.044710193|+39.1652|
|native|Sparsity|0.038789174|0.039516568|+1.8753|
|equalized_pairwise|GD|0.040183437|0.040148262|-0.0875|
|equalized_pairwise|IGD|0.14461658|0.18035923|+24.7155|
|equalized_pairwise|HV|0.7262961|0.61320062|-15.5715|
|equalized_pairwise|Spacing|0.04154758|0.044710193|+7.6120|
|equalized_pairwise|Sparsity|0.086805672|0.039516568|-54.4770|
|equalized_K66|GD|0.043297063|0.041432044|-4.3075|
|equalized_K66|IGD|0.16023769|0.18514624|+15.5448|
|equalized_K66|HV|0.67316193|0.58872443|-12.5434|
|equalized_K66|Spacing|0.056733601|0.060402858|+6.4675|
|equalized_K66|Sparsity|0.22354991|0.18563383|-16.9609|

Lower GD/IGD is better; higher HV is better. Lower Spacing describes regularity; lower Sparsity describes density and is not a universal quality ranking. Equalization uses the unchanged Phase8 extreme-preserving FPS and archived-row tie rule: K=228 for this pair and K=66 for the official Phase8 cardinality control.

## Coverage and eliminated subsets

The combined front retains 228 of 409 PA ND decisions (55.7457%), loses 181, and introduces 0 formerly non-ND decisions. Decision correspondence uses the frozen L-infinity deduplication tolerance, rather than requiring identical representative row IDs. All eight objectives remain represented by retained subsets. Per-objective extrema, range ratios and subset counts are in objective_coverage.csv. The reference coverage table and ECDF show nearest-front distances across all 18,503 reference points. Geometric/objective coverage is not certified Pareto coverage.

Removed-subset contributions below are leave-one-subset-out, holding the rest of PA fixed. Exclusive ND support accounts for duplicate decisions across subsets. Exclusive HV uses the same common quadrature nodes; these marginal contributions are not additive when several subsets are removed together.

|Removed subset|q|Exclusively supported PA ND|Exclusive HV (%)|
|---|---:|---:|---:|
|C_1_7_8|0.0734915|19|0.11751|
|C_2_7_8|0.0551379|19|0.04158|
|C_3_4_6|0.245203|18|0.20248|
|C_3_4_7|0.222629|18|0.21152|
|C_3_5_6|0.259277|18|0.12836|
|C_3_5_7|0.235975|18|0.11028|
|C_3_7_8|0.0725486|19|1.81325|
|C_4_7_8|0.108599|18|0.90934|
|C_5_7_8|0.102195|16|0.87499|
|C_6_7_8|0.0388559|18|0.14282|

## Cost and practical conclusion

The filter removes 10/37 subsets (27.0270%) and 210/492 NBI subproblems (42.6829%). These are theoretical reductions in requested work, not measured runtime savings. No filtered optimization campaign was run. The original PA runtime is historical evidence only; filtered end-to-end runtime is left undefined. Postprocessing time is recorded separately in protocol.json. No proportional speedup is claimed.

Native IGD changes by +27.7841% and native HV by -17.0261%. Equalized IGD and HV also deteriorate, so the loss is not explained solely by different front cardinalities. The geometric cutoff removes useful trade-off regions despite preserving all individual-objective minima. It does not meet the stated goal of reducing cost without compromising quality. No practical advantage is demonstrated for this cutoff; retain PA as the principal applied-case configuration. A quality-sacrificing alternative would require an explicit acceptance criterion and measured runtime, neither inferred here.

## Reproducibility and limits

No optimizer, new subproblem, Monte Carlo, RSM fit, anchor or reference construction is executed. Frozen inputs are checked against their published Git blobs and rehashed after analysis. Source rows and all evaluated front memberships are exported. No old result is overwritten. Figures are in English, PNG 600 dpi and vector PDF, without axis grids. This is one deterministic applied case; timing repetitions are not independent quality replicates, and no inferential statistics are used.

Reproduce: `uv run python -m scripts.validation.turning_pa_anisotropy` from a full checkout (or pass `--input-root` for an immutable source checkout). The output path must not already exist; use `--output` for a separate reproduction.
