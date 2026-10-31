# Synthetic C-NBI: ES as the primary variant

By explicit owner decision, ADR0009 spectral-gap ES (minimum B300, first stop500, cap2000) is the primary synthetic variant; B2000 remains the fixed-sampling control. The applied case and historical10D/10E records are unchanged.

Native indicators are reused. Missing objective coordinates/ND membership were reconstructed only for FPS; indicators were computed only for new selected objective sets. Each comparator has its own K=min(two ND counts), frozen FPS/ties and normalization.

Inference reuses10E exactly: medians of all five replicas in27 structural cells; conditional paired Wilcoxon, Holm6 for IGD/HV and Holm9 for other indicators separately per analysis, existing effect sizes and50000 scenario bootstrap draws/seeds. Intervals are pointwise; analyses remain exploratory.

|Analysis|Comparator|Metric|Cells|Median ES−comparator|Rank-biserial benefit|Holm p|
|---|---|---|---|---|---|---|
|native|VRF-NBI|IGD|27|-0.218259|1.0000|8.9407e-08|
|native|VRF-NBI|HV|26|0.244959|1.0000|8.9407e-08|
|native|NSGA-III|IGD|27|-0.0633412|0.9788|2.08616e-07|
|native|NSGA-III|HV|27|0.0719409|0.9101|3.08454e-06|
|native|MOEA/D|IGD|27|-0.273448|1.0000|8.9407e-08|
|native|MOEA/D|HV|27|0.15952|1.0000|8.9407e-08|
|equalized|VRF-NBI|IGD|27|-0.0329187|0.2116|0.415708|
|equalized|VRF-NBI|HV|26|-0.0216881|-0.2877|0.415708|
|equalized|NSGA-III|IGD|27|-0.0378936|0.9788|4.17233e-07|
|equalized|NSGA-III|HV|27|0.0281377|0.7989|0.00028789|
|equalized|MOEA/D|IGD|27|-0.252407|1.0000|8.9407e-08|
|equalized|MOEA/D|HV|27|0.124576|1.0000|8.9407e-08|

nx=all: MC anchor solves 49.14% fewer; kernel sum 1.06182× control; median per-run ratio 0.79412; ΔND=120; ΔNBI subproblems=698.

nx=2: MC anchor solves 64.74% fewer; kernel sum 0.63220× control; median per-run ratio 0.50861; ΔND=-5; ΔNBI subproblems=120.

nx=3: MC anchor solves 63.59% fewer; kernel sum 0.95315× control; median per-run ratio 0.83413; ΔND=76; ΔNBI subproblems=203.

nx=5: MC anchor solves 27.51% fewer; kernel sum 1.11758× control; median per-run ratio 1.04211; ΔND=49; ΔNBI subproblems=375.

Cost interpretation: fewer Monte Carlo solves do not imply lower total cost. Timings come from distinct historical campaigns with different scheduling/cache conditions; ES kernel includes incremental persistence. No global controlled speedup is established. ND, subproblem counts and NBI stage times are paired in the cost CSV; worker elapsed boundaries are not conflated with kernel time.

Integrity:135 input cases,405 independent native pairs and405 equalized pairs. Metric/scenario exclusions: 2; original HV precision flags are retained. No equalized joint ranking, new hypotheses, reference changes, optimizers, fits or figures.

Stage sums (ES / control; seconds): preparation 1358.005 / 1258.195; MC_seconds 552.385 / 1057.025; NBI 15117.519 / 14283.205; total 17040.190 / 16048.056.
