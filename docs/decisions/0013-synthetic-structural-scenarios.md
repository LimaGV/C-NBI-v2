# MDR0013 — synthetic structural scenarios

- Type: MDR, user-defined Phase10A scope and separate module architecture.
- Status: ACCEPTED within the explicit Phase10A task; no change to C-NBI methodology.
- Responsible: project owner; implementation by Codex.
- Date:2026-10-29.
- Branch:feature/10-synthetic-scenario-generation.
- Validation gate:IN_PROGRESS; numerical outcome must be recorded after execution.

Use exclusively squared Euclidean distance objectives, nx2/3/5,delta1/3/5,
m=nx+1+delta,radius2**(nx/4),absolute-correlation targets.25/.60/.85.
One final anchor configuration per cell; signed mean is observed,never controlled.
The mathematical definition and implementation parameters are frozen in
docs/mathematics/synthetic_scenario_generation.md and
docs/policies/synthetic_generation_10a.json before the official27-cell generation.

Independent validation must not select/restart candidates. Preserve failed cells,
solver diagnostics and the best available configurations. No regularization to
force positive definiteness; no numerical tolerance relaxation. Independent
analytic population correlations assess sampling precision after selection.

Acceptance of this scope follows the explicit task. Validation does not approve
new benchmark methods or change historical C-NBI decisions. No noise/CCD/RSM,
Pareto methods/reference/metrics or benchmark campaign is authorized here.
All scientific modules/results0–9 remain unchanged. No new dependency required.
