# Phase10D computational execution plan

This supplements MDR0016 without changing any algorithm, scientific setting,
seed, noise realization, fitted model, reference or evaluation rule. The frozen
search worker uses one CPU worker and one BLAS/OpenMP thread per run. Its code
commit and algorithm protocol hash remain unchanged.

The pilot first runs sequentially to measure complete-pipeline costs. The audited
workstation is an Intel Core i5-12400F, six physical cores, twelve logical threads.
The scheduler queries Windows core topology and selects only one logical thread
per physical core (affinity masks1,4,16,64,256,1024). It can run six independent
processes concurrently, each pinned before importing the frozen worker. Sibling
hardware threads are not allocated as separate workers. Task shards and seeds
are deterministic, and processes share no mutable random-number generator.

Before the official campaign, the four methods on the first pilot cell are
replayed concurrently with their original pilot seeds, complete budgets and
unchanged scientific worker. Decisions, RSM predictions and counters must match
bitwise/exactly. Failure blocks the campaign. The other eight pilot runs still
have to pass numerical, structural and integrity gates. No reference-based
algorithm tuning is involved in this resource decision.

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
