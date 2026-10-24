# Phase7 verification and publication record

Branch: `feature/07-pareto-reference-loo`. PR9 reviewed/green/conflict-free and
merged by authorized squash to `b94be85d039ca6ce8e7aff435dd00b055c11caf9`.
Clean local main and clean engine launch are recorded. New PR targets main;
no automatic merge. Publication head SHA, PR URL and live CI are in the PR and
final delivery report; they are not circularly embedded in their own commit.

Scientific engine: `8d77bc99596e8b01eff4d2829ada48b5ed5c8c07`.
Assembly: `2f51fda483ad37525f7ac72cb2467cd063284513`.
Both launched from committed clean working trees. Subsequent documentation does
not change executed code, models, inputs or results. Metadata/checksums retain
all file identities and separate engine/assembly provenance.

## Required report coverage

| Requested items | Evidence/location |
|---|---|
| 1–3 branch/head/PR | Branch above; published head and PR URL in delivery/PR |
| 4–8 historical audit/x/VRF eligibility | mathematics/reference_source_audit.md; references/metadata/phase_07_v1/; all20 old EA CSVs have x; VRF66 literal x eligible/re-evaluated |
| 9–12 libraries/configuration | pymoo0.6.2, frozen pareto_reference_protocol.json and applied calibration exact copy; mathematics/turning_pareto_reference.md |
| 13–16 NFE/seeds/runs/runtime | 132000 optimizer NFE/run, seeds1001..1030,30 per EA; campaign667.808878s, assembly322.145311s; per-run CSV/JSON |
| 17–29 pools/common/exclusive/LOO counts | Application report tables and reference_contributions.csv; pools8754/9743/4417/66, common22523, LOO14202/12836/18503/22460 |
| 30 removal H/epsilon | loo_reference_diagnostics.csv; exact orientations in mathematical/application reports |
| 31–32 saturation | pool_saturation.csv,60 prefix rows; last runs still add points; no certified saturation |
| 33–34 provenance-aware exclusion/no CNBI | Original homogeneous family pools excluded before dedup/ND; synthetic shared-coordinate/revival oracles; every archived LOO origin independently checked |
| 35 H5 sanity | geometric_diagnostics.csv, CNBI_H5_SANITY_ONLY/LEAVE_ONE_FAMILY_OUT; GD.0395671528,IGD.167646775,H(A→B).163503231,H(B→A).338096730,epsilon.186400770 |
| 36 common diagnostics | Same CSV, COMMON_REFERENCE_SELF_INCLUDED; separate application table, no independence claim |
| 37–38 artifacts/hashes | results/phase_07_reference_front/turning_multifamily_loo_20261024/; metadata.json/checksums.sha256; full selected hashes in application report |
| 39–42 local quality | Commands/results below; all required checks |
| 43 CI | Windows/Ubuntu GitHub Actions checks of the published PR head; live status in PR/delivery |
| 44 Git status | Final clean/synchronized branch check in delivery; no new PR merge |
| 45–46 ADR/claims | ADR0011 ACCEPTED; C-REF-01..04 SUPPORTED as definitions/decisions |
| 47–48 limits/recommendation | Final application-report section: finite envelope, filtered historical VRF, transferred tuning, no Pareto truth, differing LOO targets; separately authorize future benchmark/sensitivity |

## Integrity and scope

Raw dataset, processed experimental values, Phase2–6 preserved outputs and prior
scientific modules have no diff against merged main. No data reconstructed or
responses inferred; historical response columns never used as canonical values.
Current RSM coefficients are read, not fitted. No MC ensemble, anchors, PA,
early-stop, NBI or VRF scientific pipeline repeated; no final benchmark, HV or
adaptive H implementation. The full QA suite includes existing temporary
synthetic/smoke tests of historical modules, not replacement real runs.

All60 final populations are finite, feasible and current-RSM checked. NFE includes
initial populations and is identical per search; independent validation is
explicitly separate. Every output checksum and frozen input digest is checked.
All LOO origins link back to retained independent family pools. Excluded-family
origins cannot survive. H5/H20 are both CNBI; H20 is not an H5 target.

Dependency addition changes uv.lock. The historical Phase6 test preserves its
saved historical lock digest; all other Phase6 inputs still match actual bytes.
The environment test explicitly permits the newly authorized pinned pymoo.
The calibration JSON has -text Git attributes to preserve original CRLF bytes
and SHA256 across Windows/Linux, rather than silently normalizing evidence.

## Local commands

`uv sync --locked`: passed,131 resolved packages /128 installed checked.
`uv run pytest -v`: **599 passed**,37.50s, including archival tests.
`uv run pytest --cov=cnbi_v2 --cov-report=term-missing`: **599 passed**,57.28s;
**99.34%** coverage (2122 statements,14 missed; required96.15%).
`uv run ruff check .`: passed.
`uv run mypy src`: passed,38 source files.
`git diff --check`: passed. Publication/CI does not rerun the60 scientific EAs.

The checksums manifest SHA256 is
`271d2ccaed63e1d6951888453dac69e5a945be4e0f8d230e6203d3cdbec4f3c9`;
metadata SHA256 is
`0f0b308ad7b87949a3edc6cf040d7be6185cb1f58fffa0bb941cfc14fba76b1a`.
