# MDR0014 — synthetic CCD, noise and RSM generation

- Type:MDR; Phase10B owner-defined experimental protocol, not a C-NBI method change.
- Status:ACCEPTED within the explicit Phase10B task; new PR remains open for review.
- Responsible:project owner; implementation by Codex.
- Date:2026-10-29.
- Branch:feature/10b-synthetic-rsm-generation.
- Input:27 frozen Phase10A cells at489aa0e,integrated by merge d68aef7.
- Validation gate:PASSED,814 tests/99.25% coverage,135/135 fits and27 noiseless
  certificates;all1150 historical files intact. Final evidence
  in docs/phase_10b_verification.md and the PR's Ubuntu/Windows CI.

Use conventional full rotatable CCDs (13,19,47 rows),five separate centers and
all nx3 factorial rows unchanged outside the future feasible ball. Five noisy
replicas per frozen structural cell; one Gaussian iid intensity sigma_j²=S_fj²/19,
complete-CCD sample variance ddof1,95% signal in expectation. No conflicting
validated protocol was found in prior source/documentation. Freeze seeds/code
before the official campaign; deterministic cell/replica-keyed PCG64 streams.

Fit the full quadratic exclusively through existing Phase1 APIs. Preserve all
noisy observations,all coefficients,all135 replicas,all diagnostics and raw
residual covariance,including singular matrices. Certify noiseless recovery on
all27 cells. Independent4096-point uniform-volume Sobol holdout per cell is
shared by its five replicas and cannot select or modify fits.

Analytic functions/true coefficients are generation/validation oracles; future
optimizers receive only the frozen noisy polynomial model interface. Export
float64 arrays,metadata,seeds,hashes and full diagnostics. Predetermined diagnostic
representatives and all-replica descriptive summaries prevent quality selection.

Alternatives rejected by the explicit task:CCD projection/fractionation,center
collapse,posthoc noise scaling,clipping,response transforms,term selection,
convexity constraints,covariance regularization,anchor recalibration,replica
discarding and a new OLS/statistical implementation. Published excluded materials
retain their existing license scope. No multiobjective campaign is authorized.

Definition:docs/mathematics/synthetic_rsm_generation.md.
Frozen policy:docs/policies/synthetic_generation_10b.json.
