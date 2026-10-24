# Turning: empirical pooled reference and family LOO

Phase7 consumes the frozen nominal originally coded eight-RSM case. The owner
defines **H_base=5**:492 subproblems,411 unique decisions,408 ND. This updates
the operational recommendation after Phase6 without changing its results.
H20 is a finer auxiliary member of the same CNBI family,4417 ND, never truth.
H5→H20 adaptive refinement is future work, not implemented here.

PR9 was reviewed, conflict-free with four successful Windows/Ubuntu checks,
squash-merged to main `b94be85d039ca6ce8e7aff435dd00b055c11caf9`. Local main was
updated and clean before branch `feature/07-pareto-reference-loo`.
The campaign launched from clean engine/protocol/audit commit
`8d77bc99596e8b01eff4d2829ada48b5ed5c8c07`. The archive records the separate
committed assembly version and all source/input/output SHA256 values.

## Historical evidence and canonical problem

See [pre-run source audit](reference_source_audit.md). Historical NSGA3 and MOEAD
x exist in10 final-front CSVs each; a supplementary20-file hash/sphere check
confirms availability. They are not principal-pool contributions: current EA
pools use30 new runs each under the same current problem and budget.

Historical VRF has66 literal cs/f/md decision vectors, in verified coded
cutting-speed/feed/depth order. Coordinates are preserved without rounding,
projection, inverse coding or reconstruction, and all satisfy the sphere.
All eight responses are reevaluated under current RSMs; old response columns
are discarded. The historical export was already sanitized and ND-filtered
under old models, so it does not recover the complete original VRF population.
This is **historical VRF reevaluated**, not a new VRF run or proof of exact
published VRF algorithm reproduction. Its source/extraction hashes are recorded.

The current canonical decision order is x1=Vc,x2=f,x3=ap. Domain norm(x)<=8**.25,
with frozen numerical squared-margin tolerance1e-9, not the CCD axial literal1.682.
Responses T/MTTF/WR/Ra/Rt/Kp/ROI/OEE have directions
MAX/MAX/MIN/MIN/MIN/MIN/MAX/MAX. Fitness and all geometry use the same fixed
Phase5 global nominal MIN normalization, with no clipping or per-family rescaling.
The earlier physical/coded mismatch and published-table discrepancies are not
reopened or corrected by this reference construction.

Reevaluating Phase6 decisions verifies archived responses with atol5e-14,
rtol2e-14. All4557 H20 origins cover4476 unique decisions and4417 ND; exact H5
membership recovers492/411/408. No NBI solve or projection of archived x. Scalar
and vectorized current-RSM evaluators agree within the declared numerical bound
(largest CNBI20 scalar/vector absolute difference4.263256414560601e-14).

## Evolutionary configuration, frozen before execution

Consolidated **pymoo0.6.2**, locked in the V2 environment; no V1 module/environment
is imported. The owner explicitly authorized applied V1 calibration transfer.
The applied3-variable/8-response calibration supplies operators; a separately
identified general V1 budget policy supplies132000. No fresh tuning is done.

| Setting | NSGA3 | MOEAD |
|---|---|---|
| Class | pymoo.algorithms.moo.nsga3.NSGA3 | pymoo.algorithms.moo.moead.MOEAD |
| Das–Dennis partitions/directions | 4 /330 | 4 /330 |
| Population | 330 | 330 |
| Search NFE/run | 132000 | 132000 |
| Generation count | 400 including initial population | 400 including initial population |
| Seeds | 1001..1030 | 1001..1030 |
| SBX probability /eta | .9 /10 | 1 /10 |
| Polynomial mutation eta | 15 | 30 |
| PM individual/per-variable probability | 1/3 each | 1/3 each |
| Neighborhood/mating probability | not applicable | 66 /.9 |
| Decomposition/replacement | reference-direction survival | PBI theta5; all strictly improving neighbors |

SBX per-variable .5, exchange1, bin .5, two offspring; PM at_least_once=False.
NSGA3 uses330 offspring/cycle and duplicate elimination. The generation count
means330 initial evaluations plus399 cycles of330. Initial x is uniform in the
3-ball (Gaussian direction and radius alpha*U^(1/3)); out-of-ball offspring
receive deterministic radial repair, with only inward representational nextafter
correction. Every evaluation is checked for feasibility and a hard search cap.
Repair operations, not rejection counts, are archived per run.

Differences from old applied calibration runs: those had cap19830, actual19800,
seeds1..10 and raw MIN fitness. Current runs use a larger reference-construction
budget, fixed-global normalized fitness and uniform-ball initial sampling.
Transfer does not establish optimal tuning under the current problem.
Six separate seeded processes, one numerical-library thread each; runtime sums
overlap and must not be confused with campaign wall time.

All60 runs completed without failure, **7920000 optimizer NFE**. Each independently
checks330 final-population points with the existing scalar evaluator:19800
additional validation evaluations, outside search. Materialization and assembly
checks are separately counted in metadata; they add no search evaluations.
There is no intermediate-generation archive in the reference.

## Construction and interpretation

See [mathematical definitions](pareto_reference_leave_one_out.md) and ADR0011.
Each EA pool is the ND union of final ND populations from its30 seeds. H20 alone
represents CNBI in the common union; H5 is not a reference contributor.
Only numerical decision duplicates are merged, retaining every origin. MIN
dominance uses the explicit Phase6 coordinate roundoff vector, not a statistical
epsilon-dominance rule. Each LOO is rebuilt from original family pools **after
excluding the entire family and before deduplication/ND**. Independent shared
coordinates can remain through retained origins.

The independent target for H5 is `reference_minus_cnbi.npz`; no CNBI origin,
including H20 or any other resolution, is allowed. Contract tests cover this
and retained points reappearing after a dominating family is excluded.

LOO targets differ, so their metrics do not automatically rank methods. Common
metrics are labeled `COMMON_REFERENCE_SELF_INCLUDED`; LOO metrics are labeled
`LEAVE_ONE_FAMILY_OUT`. H5 metrics are sanity checks only. Contribution and ND
cardinality do not establish superiority. HV, final benchmarking/statistical
comparison, new VRF optimization and adaptive H are deferred.

## Measured finite-campaign results

The following tables report the preserved archive; rounded display values are
secondary to the full-precision CSV/NPZ/JSON files.

### Pools, common envelope and LOO

| Family | Pool ND | Exclusive in common | Exclusive fraction | Shared | LOO ND | Retained points revived after removal |
|---|---|---|---|---|---|---|
| NSGA3 | 8754 | 8449 | 37.512765% | 0 | 14202 | 128 |
| MOEAD | 9743 | 9743 | 43.258003% | 0 | 12836 | 56 |
| CNBI | 4417 | 4267 | 18.945078% | 0 | 18503 | 247 |
| VRF | 66 | 64 | 0.284154% | 0 | 22460 | 1 |


P_all has **22523 ND**; no numerically shared cross-family points were found (shared=0).
The LOO cardinalities exceed common-minus-exclusive because retained points
previously dominated by the excluded family revive. This is why exclusion must
precede ND. The eligible VRF pool retains66 current ND points,64 in the common
envelope. These are finite contributions, not a ranking.


### Removal diagnostics

H is directed **P_all→P_minus_M**; epsilon is **Iepsilon+(P_minus_M,P_all)**.

| Excluded family | H(all→minus) | epsilon(minus,all) |
|---|---|---|
| NSGA3 | 0.279510115 | 0.0674644798 |
| MOEAD | 0.0823844705 | 0.0413518352 |
| CNBI | 0.20578226 | 0.0772181987 |
| VRF | 0.0654957598 | 0.0209015189 |


### Pool saturation

H is **pool30→prefix(r)**; epsilon is **Iepsilon+(prefix(r),pool30)**.

| Family | r | ND | H(pool30→prefix) | epsilon(prefix,pool30) |
|---|---|---|---|---|
| NSGA3 | 1 | 330 | 0.574905264 | 0.104619343 |
| NSGA3 | 5 | 1582 | 0.523532232 | 0.0853375155 |
| NSGA3 | 10 | 3099 | 0.467527948 | 0.0542936373 |
| NSGA3 | 20 | 5994 | 0.283826518 | 0.0427550698 |
| NSGA3 | 25 | 7431 | 0.143588677 | 0.039943428 |
| NSGA3 | 29 | 8511 | 0.0747588874 | 0.0303113518 |
| NSGA3 | 30 | 8754 | 0 | 0 |
| MOEAD | 1 | 327 | 0.229726205 | 0.0555022913 |
| MOEAD | 5 | 1631 | 0.214107097 | 0.0523349232 |
| MOEAD | 10 | 3270 | 0.0679037772 | 0.0346534926 |
| MOEAD | 20 | 6482 | 0.0382870712 | 0.0204270293 |
| MOEAD | 25 | 8124 | 0.0316329026 | 0.0194612381 |
| MOEAD | 29 | 9417 | 0.0268423924 | 0.0132018617 |
| MOEAD | 30 | 9743 | 0 | 0 |


The endpoint30 necessarily has zero distance to itself. At29, NSGA3 still has
H0.0747588874/epsilon0.0303113518 and MOEAD H0.0268423924/epsilon0.0132018617
to their respective30-run pools; the last runs add243 and326 ND points.
Thus **30 runs are a finite reproducible reference protocol, not a certified
saturation/completeness result**. No preregistered sufficiency threshold was
provided; do not declare full saturation from the trivial zero endpoint.


### Family LOO and H5 sanity

Label: `LEAVE_ONE_FAMILY_OUT`. A is the evaluated set, B its named target.

| A | B | GD_p1 | IGD_p1 | H(A→B) | H(B→A) | epsilon(A,B) |
|---|---|---|---|---|---|---|
| NSGA3 | minus_nsga3 | 0.0492713774 | 0.0249509377 | 0.279510115 | 0.20578226 | 0.0772181987 |
| MOEAD | minus_moead | 0.0175319091 | 0.294206917 | 0.0823844705 | 1.48220174 | 0.447773642 |
| CNBI | minus_cnbi | 0.0391376007 | 0.0654449733 | 0.20578226 | 0.279510115 | 0.070494247 |
| VRF | minus_vrf | 0.0282722108 | 0.275293688 | 0.0654957598 | 1.24441067 | 0.30647829 |
| CNBI_H5_SANITY_ONLY | minus_cnbi | 0.0395671528 | 0.167646775 | 0.163503231 | 0.33809673 | 0.18640077 |


### Common-reference exploratory diagnostics

Label: `COMMON_REFERENCE_SELF_INCLUDED`. A is the evaluated set, B its named target.

| A | B | GD_p1 | IGD_p1 | H(A→B) | H(B→A) | epsilon(A,B) |
|---|---|---|---|---|---|---|
| NSGA3 | all | 0.000848689979 | 0.0154337358 | 0.122164047 | 0.20578226 | 0.0772181987 |
| MOEAD | all | 0 | 0.167190283 | 0 | 1.48220174 | 0.447773642 |
| CNBI | all | 0.00120350182 | 0.0531952474 | 0.0900974405 | 0.279510115 | 0.070494247 |
| VRF | all | 0.00108794394 | 0.274519431 | 0.0412673816 | 1.24441067 | 0.30647829 |
| CNBI_H5_SANITY_ONLY | all | 0.0011093721 | 0.148711735 | 0.0650850237 | 0.33809673 | 0.18640077 |


H5's independent target contains18503 ND points and **zero CNBI origins**.
Common and LOO labels must remain distinct. In particular, a self-included zero
GD does not imply coverage of the combined envelope. LOO targets vary by family.


### Runtime and accounting

| Family | Sum run seconds | Median | Minimum | Maximum | Repair operations |
|---|---|---|---|---|---|
| NSGA3 | 697.014912 | 23.3596194 | 22.2711191 | 24.4358934 | 1198068 |
| MOEAD | 3262.38482 | 108.600194 | 107.975554 | 110.240252 | 3958647 |


Campaign wall time: **667.808878 s** with6 workers;
assembly wall time: **322.145311 s**. Run sums overlap.

| Union/ND operation | Seconds |
|---|---|
| NSGA3_pool_union_ND_seconds | 9.1778143 |
| NSGA3_pool_and_saturation_seconds | 91.5039482 |
| MOEAD_pool_union_ND_seconds | 8.5797992 |
| MOEAD_pool_and_saturation_seconds | 82.8249295 |
| reference_all_union_ND_seconds | 43.1614725 |
| minus_NSGA3_union_ND_seconds | 16.4244545 |
| minus_MOEAD_union_ND_seconds | 14.8015216 |
| minus_CNBI_union_ND_seconds | 28.3701202 |
| minus_VRF_union_ND_seconds | 43.0049527 |


Repair counts include operator-stage outside-ball candidates (including generated
offspring not selected for evaluation); they are not rejected-search counts or
percentages of NFE. The archive separates7920000 optimizer evaluations from19800
per-run scalar validation calls,5115 scalar materialization checks,5049 additional
CNBI fast/scalar cross-checks and19800 assembly scalar validations. Test-suite
checks are outside this scientific-search accounting.


The observed common normalized range is [0,1.18609316]; values above1
are preserved. No clipping, separate normalization, refitting, reconstruction or
reoptimization of prior anchors/NBI results. The QA suite exercises historical
modules on temporary synthetic cases; it does not replace preserved real runs.


### Artifact identities

Assembly commit: `2f51fda483ad37525f7ac72cb2467cd063284513`; working tree clean at launch.
Engine commit: `8d77bc99596e8b01eff4d2829ada48b5ed5c8c07`; engine and inputs unchanged at campaign completion.


Directory: `results/phase_07_reference_front/turning_multifamily_loo_20261024/`.
Per-run NPZ/JSON60 pairs, five references, four family pools, H5 baseline, complete
origin CSV, contributions/removal/saturation/geometry CSVs, launch/completion,
source audits and metadata/checksums. NPZ files load with allow_pickle=False.

| Artifact/input | SHA256 |
|---|---|
| metadata.json | 0f0b308ad7b87949a3edc6cf040d7be6185cb1f58fffa0bb941cfc14fba76b1a |
| checksums.sha256 | 271d2ccaed63e1d6951888453dac69e5a945be4e0f8d230e6203d3cdbec4f3c9 |
| reference_all.npz | 120fb4ad9692704d8ff5d7e1276f5541c1f9d939cc5af2b34b51da2aeda92b67 |
| reference_minus_nsga3.npz | 3b90129c98c16e63dadeeec0e4bbe2de232d7cbb5d32f152315f199ef6f36b40 |
| reference_minus_moead.npz | 7cb59d5d0d4945d273a398f74ea448cd78059fa093943ad15f7683fd54e5b719 |
| reference_minus_cnbi.npz | 156342db42fca932bcbfa715a4e58dec85e375873a0fe2c57edc12f78dbfe0d2 |
| reference_minus_vrf.npz | a70a2485e2d6186fd60a3f0889e5192bfbaeb606513074131f853ce84655ede4 |
| data/raw/turning_application/CCD_values_20261023.xlsx | 7f905b7a2f7bb8b6735ab96900cba7356401df2d26c961dcb12faa2683c6c71e |
| results/phase_02_anchors/turning_original_codes_20261024/coded_models.csv | 9d5590b5f2ba43592fa13753cd86afaa583fadbbd4f0d180acb1b5eef0b3e3e9 |
| results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/nominal_normalization.csv | bc19f7ef44d5ee86b10b4fb789fe55742b0dc6dc2119277d5811e7464bb76dc0 |
| data/external/turning_reference/vrf_historical_decisions.csv | f41b338c8927c635d18e60ab363c900116e9a7894177b9d740a433581fd2661a |
| references/metadata/phase_07_v1/applied_ea_calibration.json | 0417657aa8847c3bef551eaaa259adf4f149b0e44e9063be5709d0b0eed7ff5b |


### Limits and next authorized step

The empirical reference reflects finite budgets, transferred tuning, current coded
RSMs and a filtered historical VRF export. No independent true front or complete
original VRF search population is available. Cardinality, exclusive contribution
and common self-inclusion cannot establish superiority. Different LOO targets
preclude an automatic direct ranking.30 seeds do not certify saturation.

Recommendation: preserve this versioned finite envelope and use
`reference_minus_cnbi.npz` for a separately authorized H5 benchmark. Predefine
common/LOO reporting and statistical protocol, and assess reference sensitivity
before claiming stable coverage or comparative performance. Broader seeds/NFE
may be examined in a separate reference-sensitivity study if needed. HV and
H5→H20 adaptive refinement remain future work. No final benchmark is started,
and this PR must not be automatically merged. ADR0011 and claims C-REF-01..04
record definitions/decisions, not superiority.
