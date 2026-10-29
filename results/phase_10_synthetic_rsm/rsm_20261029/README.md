# Frozen Phase10B synthetic experiments

27 structural cases × 5 replicas = 135 joint RSMs; 3555 experiment rows; 990 response models. All retained. No multiobjective run.

Observations CSV is long-form: 28530 scalar response values; unique (instance_id,design_point_id) count is 3555. CCD x columns beyond nx are structurally inapplicable, not missing observations.

models_index.json + synthetic_rsm_models.npz expose noisy polynomial predictions without OLS or oracle. Separate experimental/external NPZs preserve truth/noise, points, residuals and raw covariance. Term IDs are zero-based; response/design/replica IDs start at 1.

CSV floats round-trip float64 (.17g); NPZ float64. Empty relative errors mean zero/near-zero true denominator; singular covariance condition is explicitly undefined. See mathematical definition and verification report.

Source commit: 800076f4c5cac3f651cdb875cf01135f1eddb561. Input Phase10A: 489aa0e2b4703c0e39b0bff2623209e5a177a94b.

Code-only MIT scope does not grant a license to these scientific artifacts; see LICENSE_SCOPE.md. No excluded material license changed.
