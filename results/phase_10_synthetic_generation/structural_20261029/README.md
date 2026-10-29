# Phase10A structural scenarios

One configuration per cell;f_j(x)=||x-a_j||²,all MIN.
No multiobjective method,noise,CCD,RSM or Pareto benchmark was executed.
rho_abs_realized/rho_signed in the tables refer to the independent holdout.
CSV values preserve17 significant digits; NPZ stores full float64 arrays.
All four diagnostics are English,PNG600dpi/PDF vector,without gridlines.
Mean signed correlation is observed and never used for selection.

Validated:27/27. See calibration_manifest.json for failures/timing.

| Scenario | nx | delta | m | Target | Realized abs | Signed | Validation error | Status |
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
