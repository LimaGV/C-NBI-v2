# Phase10D computational execution plan

This supplements MDR0016 without changing any algorithm, scientific setting,
seed, noise realization, fitted model, reference or evaluation rule. The frozen
search worker uses one CPU worker and one BLAS/OpenMP thread per run. Its code
commit and algorithm protocol hash are frozen separately for each revision.

The pilot first runs sequentially to measure complete-pipeline costs. The audited
workstation is an Intel Core i5-12400F, six physical cores, twelve logical threads.
The scheduler queries Windows core topology and selects only one logical thread
per physical core (affinity masks1,4,16,64,256,1024). It can run six independent
processes concurrently, each pinned before importing the frozen worker. Sibling
hardware threads are not allocated as separate workers. Task shards and seeds
use a deterministic FIFO task list within each method, and processes share no mutable random-number
generator. The next free core takes the next queued task; core assignment can
depend on completion times, while task identity, seed and numerical outputs
cannot. A hard barrier enforces the owner's requested order: all135 C-NBI,
then all135 VRF-NBI, then all135 NSGA-III, then all135 MOEA/D. Each method may
use the six physical cores concurrently. No task of the next method starts
until every task of the current method has finished or has a retained terminal
failure. Completed and failed outcomes are preserved during resumption.

Before the official campaign, the four methods on the first pilot cell are
replayed concurrently with their original pilot seeds, complete budgets and
unchanged scientific worker. Decisions, RSM predictions and counters must match
bitwise/exactly. Failure blocks the campaign. The other eight pilot runs still
have to pass numerical, structural and integrity gates. No reference-based
algorithm tuning is involved in this resource decision.

The finalized protocol repeats all twelve pilot tasks under the actual six-core
scheduler. The initial sequential pilot is preserved in the parent directory;
the first scheduled pilot and incomplete initial campaign live in campaign_v1/.
The corrected final pilot and540-run campaign live separately in campaign_v2/.
The initial campaign was stopped at77 attempts:75 completed and2 Varimax-cap
failures caused by a migration bug. The correction restores v1's return-last
behavior at the unchanged500-iteration cap; its explicit nonconvergence flag
remains available. All original payloads and failures are retained. The whole
final campaign restarts under one corrected version, without selectively
replacing unfavorable cases. Additional counter
schema2 records all quadratic-response vector events, original full-vector
recomposition/validation and auxiliary factor-model calls separately. Runner
end-to-end timers include validation and full-objective ND postprocessing. These
observability corrections do not change objectives, solver settings or decisions.
Operational recovery now refuses to replace any retained scientific outcome,
even if its state is FAILED. Only interrupted/failed operational attempts without
a scientific payload can be retried with a recorded reason. An exclusive
scheduler lock prevents accidental concurrent launch of the same campaign.
Every final pilot is compared with its sequential counterpart; common counters
and numerical outputs must agree, while the added counters remain separately
audited. No source code or scientific configuration is modified after this
revalidation for the official campaign.

The hardware execution plan and scheduler source hash are stored separately
in execution_plan.json; receipts identify each task's physical CPU mask and
the common plan hash. Benchmark time is per-run wall time under the disclosed
concurrency. It must not be described as isolated idle-host time. Concurrent
resource contention and CPU-frequency effects are limitations for interpretation
of small timing differences. No equal-time or equal-NFE fairness claim is made.
Sequential pilot projections are resource estimates, not replacements for
actual official per-run times. Primary end-to-end time uses the worker's
input_load_plus_search_seconds, which also includes output validation and
environment capture; kernel preparation, solver and postprocessing subtimers
are reported separately, with the remaining measured overhead explicit.

Only a complete validated payload can be skipped during resumption. Earlier
attempts and failures are retained; retries require an operational reason.
No run can be replaced because its quality is unfavorable. Official tasks remain
540 regardless of outcomes. The final report distinguishes completed, failed,
incomplete and pending tasks and keeps all paired experimental blocks.
