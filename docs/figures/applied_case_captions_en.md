# Captions — C-NBI v2 applied case

## A1 — Response-surface contour maps

Visual evaluation of the frozen quadratic coefficients on the x₃=0 plane within the circular sphere section. Each response uses its own natural-value scale; colors across responses are not quantitatively comparable. The dashed curve delimits the section and the cross marks its center. No RSM was refitted.

## A2 — Normalized payoff matrix from individual optimizations

Rows: nominal anchors; columns: attained responses. The stored payoff was transposed only for presentation. Fixed nominal global normalization, MIN orientation: zero is the individual ideal and one is the worst anchor value for that response. This is not the visual-performance normalization used in parallel coordinates.

## A3 — Asymmetry of normalized cross costs

Supplementary visual asymmetry diagnostic: Cᵢⱼ=Zⱼᵢ−Zᵢⱼ, where payoff Z has responses in rows and anchors in columns. The diagonal is zero. The sign compares cross costs on nominal ranges; it does not represent correlation, dominance, or a new benchmark metric.

## B1 — Individual optima in the coded factor space

Eight nominal optima in three coded-space projections. The dashed circle is the sphere projection, not a conversion to physical units. x₁=Vc (cs), x₂=f, and x₃=ap (md) follow the canonical audit; no verified continuous physical inverse is available.

## B2 — Projection of individual optima in the normalized response space

Linear projection of the eight anchor response vectors. PCA was fitted once to the independent 18,503-point reference in the fixed global MIN space, with no additional standardization. Percentages refer to that reference; eight-dimensional distances and dominance are not fully preserved in two dimensions.

## B3 — Structure of the selected response subsets

Binary matrix of the 37 frozen subsets: 19 pairs followed by 18 triples in lexicographic order. The horizontal divider separates dimensions; bars show marginal frequencies, not causal importance or performance.

## B4 — Response co-occurrence network in the selected subsets

Deterministic circular layout in canonical order. Edge width represents the number of subsets containing both responses; node area grows with marginal frequency. The network summarizes selection, not statistical association between responses.

## B5 — Singular spectrum and uncertainty threshold from parallel analysis

Stored nominal global spectrum and uncertainty q95 thresholds for B=2000. Two components exceed their thresholds. Terminology: uncertainty-calibrated/parallel-analysis-inspired PA; this is neither a new MC execution nor a Horn analysis.

## B6 — Local CHIM geometry and NBI directions

First and last lexicographic pair and triple, selected without performance information. Stars: anchors; segment/triangle: CHIM; crosses: H5 weights; orange circles: accepted local standalone H5 solutions. Pairs use locally normalized responses; triples use intrinsic SVD coordinates. In triples the normal is perpendicular to the plane and projects to zero: ⊙ denotes this direction, and the t panel shows the displacement omitted by projection. Historical nominal geometry is used without H20 solutions or trajectory.

## C1 — RSM coefficient estimates and confidence intervals

Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

## C2 — RSM coefficients divided by standard error

Dimensionless visual quantity β̂/SE, retaining the sign. These are not coefficients standardized to a shared physical scale, and significance is not inferred from color magnitude. The covariance is the same as in the Wald panel. The intercept is omitted from this heatmap to reveal the nine factor-term effects; it remains in forest plots and tables. Signed cell values are β/SE rounded to one decimal place; full values remain in the plot-data table.

## C3 — Propagation of anchor uncertainty in the decision space

The 2,000 stored reoptimizations of each anchor are shown in three coded projections. Dark star: nominal optimum; magenta cloud: MC. The dashed contour is the projected sphere. Clouds propagate the frozen ensemble; they are neither new sampling nor exact frequentist intervals.

## C4 — Monte Carlo uncertainty of the individual optima

Each response pair shows the 2,000 own-payoff evaluations of each reoptimization, transparent clouds, dark nominal anchors, and MC centers (+). The 95% covariance-based uncertainty ellipses use the arithmetic mean, sample covariance with divisor n−1, and χ²₂(0.95). They are descriptive summaries under an elliptical approximation, not exact confidence regions or confidence intervals for the mean.

## C5 — Anchor uncertainty and local CHIM geometry

The same deterministic subsets as B6, combined with projections of the corresponding MC anchor payoffs. Local nominal normalization and geometric basis remain fixed; no per-replicate normalization is refitted. Ellipses use the mean and sample covariance of the 2,000 projections, 95% level, and χ²₂, with descriptive interpretation. Triple intrinsic projections omit the normal component, denoted by ⊙.

## C6 — Uncertainty propagation in the payoff matrix

Mean and q95−q05 interquantile width of the 2,000 stored MC payoffs, normalized by the same fixed Phase 5 nominal ideal/range. Rows: anchors; columns: responses. Separate color scales, no clipping. The interquantile width is not an exact confidence interval.

## C7 — Monte Carlo propagation stability

Stored checkpoints B=100,…,2000. Coefficient mean/covariance Frobenius errors, global dimension, g1/g2 gaps, and maximum monitored window change. Dotted line at 1300 and 1100–1300 window: first retrospective stop under the revised policy in this applied case; horizontal line at 0.05: frozen tolerance. B_stop=1300 is a case result, not a universal constant or external policy validation. Errors compare the MC mean with nominal β and MC covariance with analytic Σ̂e ⊗ Vx, as in the original checkpoints.

## D1a — Parallel coordinates: reference and C-NBI

Independent 18,503-point zero-CNBI reference and the 409 standalone H5 ND points. Shared visual transform pᵢ=(hiᵢ−zᵢ)/(hiᵢ−loᵢ), with bounds from all canonical candidates plus current H5; zero is worst and one best within those bounds. This transform does not replace official metric normalization. Opacity does not encode probabilities.

## D1b — Parallel coordinates of the nondominated solutions

Visual performance using the same transform as D1a, with standalone H5, VRF-NBI, and one archived run per EA. Display representatives minimize the already recorded native IGD on the historical common target, breaking ties by seed. They do not represent all 30 runs, their median, or a new execution.

## D2 — Two-dimensional projections of the empirical front

Projections in natural values of the canonical responses, without applying the Table 3 scaling note. Gray: independent reference; orange: standalone H5; blue: VRF-NBI; green/red: EA runs selected only by frozen IGD. A two-dimensional projection does not certify eight-response dominance. ROI/OEE remain ratios, with no silent percentage conversion.

## D3 — Comparison by method and projection

The same representative solutions and pairs as D2, separated by method over the gray independent reference. This avoids inter-method overlap. Native cardinalities differ; the figure illustrates regions rather than a cardinality-controlled comparison.

## D4 — PCA projection of the eight-objective front

One PCA centered on the independent reference in the global MIN space, applied to every method without refitting. Axis percentages: reference variance. Methods use the same representatives as D2; projection does not replace metrics or fully preserve Pareto order.

## D5 — Exclusive contribution to the historical empirical envelope

Historical Phase 7 provenance in the 22,523-point common envelope. The CNBI bar refers to the historical H20 family, not the current 409-point baseline. Exclusive counts and percentages are copied from frozen artifacts; contribution is neither absolute quality nor causal attribution.

## E1 — IGD as a function of approximation cardinality

Frozen IGD against the same complete historical 22,523-point common target. EA curves: median and IQR of 30 runs; CNBI: standalone H5; VRF-NBI: one front up to K=66. Nested FPS reductions preserve extremes without duplicate points. Vertical line at K=66. The historical target includes evaluated families; it is neither the independent CNBI reference nor a true front.

## E2 — Hypervolume as a function of approximation cardinality

Same cardinality control as E1. HV is estimated with the frozen reference point and four shared Sobol grids, with no new scientific metric calculation. EAs: median/IQR of 30 runs. The GD/IGD target is not part of the HV definition; estimator resolution is finite.

## E3 — Effect of cardinality on distribution metrics

Frozen Spacing and Sparsity versus K. Spacing is the sample standard deviation of Euclidean nearest-neighbor distances (ddof1); Sparsity is their mean. EAs: median/IQR of 30 runs. Both depend on density; low values do not establish coverage or convergence.

## F1 — Approximation quality as a function of computational time

Quality and time belong to the same scientific configuration: each H is standalone, H5 is starred, with five identical-output H5 repetitions and one observation at each other H. EAs: medians/IQR of ten controlled seeds, checkpoints 50/100/200/300/400. IGD uses the historical common target; HV uses the shared point/estimator. Campaign dates differ on the same machine/environment; these are neither p-values nor NFE equivalences. VRF-NBI lacks reproducible timing.

## F2 — Total processing time

Frozen end-to-end times, without artificial NFE equivalence. Points: measurements; tick: median; bar: IQR when repetitions exist. H5 n=5, other H n=1, EAs n=10. No variability is invented for n=1, and VRF-NBI is omitted because reproducible timing is unavailable.

## F3 — Marginal quality gain per computational cost

Supplementary visual diagnostic between consecutive H values: (IGD_Ha−IGD_Hb)/(t_Hb−t_Ha) and (HV_Hb−HV_Ha)/(t_Hb−t_Ha). IGD uses the independent zero-CNBI reference; times are stored measurements, using the H5 median and single observations elsewhere. These are neither new primary metrics nor causal efficiency estimates.

## G1 — Sensitivity of IGD to the number of runs used in the reference

IGD of the same standalone H5 against zero-CNBI references, reusing the 100 existing paired subsets at r=5/10/15/20/25 and one complete reference at r=30. Curve: median; band: q05–q95; points: stored subsets without jitter. The band is subset dispersion, not a confidence interval.

## G2 — Sensitivity of GD to the number of runs used in the reference

Same references and distributions as G1, showing standalone H5 GD. No subsets were generated again. Decreasing GD with more runs does not certify convergence to the true front.

## G3 — Growth of the empirical reference

Cardinality and HV of the zero-CNBI reference in the same existing subsets. Median and q05–q95, with one reference at r=30. Point-count growth and geometric-envelope change are distinct phenomena; certified saturation is not claimed.

## G4 — Sensitivity to empirical-reference cardinality

Seven already frozen FPS prefixes of the independent reference; evaluated H5 is fixed. GD/IGD depend on the target, while HV belongs to the reduced reference. Reduction is a sensitivity analysis; method comparisons retain the complete target.

## G5 — Sensitivity to empirical-reference composition

Stored N, M, NM, and NMV references, always excluding CNBI. Panels: standalone H5 IGD/GD and reference HV. Composition and density change the target; marginal contributions are not interpreted as universal method importance.

## H1 — Nearest-neighbor distance distribution

Nearest-neighbor distances in the global MIN space, calculated only as a visual diagnostic. CNBI and VRF-NBI are single fronts; EAs pool distances computed within each of the 30 genuine runs. Violins summarize points rather than 30 independent quality observations; inner bars show median/IQR. Native cardinalities differ.

## H2 — Local density in the reference PCA projection

kNN density (k=15) in the two-dimensional reference PCA projection, shown as log(1+k/(πr_k²)); orange points are standalone H5. The PCA basis is the same as in the other panels. Projected density is neither eight-dimensional density, Pareto coverage, nor a new primary metric.

## H3 — Distribution of solutions in the decision space

Coded-decision projections of the same representative fronts as D2. Dashed contour: projected sphere. Factor names follow the audited order, without inferring physical coordinates for new solutions. Different projected regions alone do not establish better multiobjective quality.

## I1 — Applied-case methodological workflow

Vector workflow of the already executed pipeline: data, eight RSMs, covariance, coefficient ensemble, MC reoptimizations/payoff, CHIM/SVD/PA, 37 subsets, standalone H5, and benchmark. The diagram describes completed stages; it does not rerun them or include adaptive refinement.

## J1 — Visual summary of the applied case

Summary of the already presented data: globally normalized payoff, one representative local CHIM, T×Kp front projection, and IGD×time on the historical common target. Same transforms and representatives as in individual panels. The summary does not replace the full figures or their limitations.

## C1_T — Coefficients and 95% Wald intervals — T

Individual panel for T; presentation alternative to C1. Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

## C1_MTTF — Coefficients and 95% Wald intervals — MTTF

Individual panel for MTTF; presentation alternative to C1. Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

## C1_WR — Coefficients and 95% Wald intervals — WR

Individual panel for WR; presentation alternative to C1. Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

## C1_Ra — Coefficients and 95% Wald intervals — Ra

Individual panel for Ra; presentation alternative to C1. Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

## C1_Rt — Coefficients and 95% Wald intervals — Rt

Individual panel for Rt; presentation alternative to C1. Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

## C1_Kp — Coefficients and 95% Wald intervals — Kp

Individual panel for Kp; presentation alternative to C1. Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

## C1_ROI — Coefficients and 95% Wald intervals — ROI

Individual panel for ROI; presentation alternative to C1. Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

## C1_OEE — Coefficients and 95% Wald intervals — OEE

Individual panel for OEE; presentation alternative to C1. Frozen estimates with normal 95% Wald intervals: β̂ ± Φ⁻¹(0.975)SE. Standard errors come from the frozen analytic covariance diagonal, using column-wise vectorization. Intervals are approximate, conditional on the plug-in model, and not simultaneously adjusted; no model was fitted. Horizontal scales vary by response.

