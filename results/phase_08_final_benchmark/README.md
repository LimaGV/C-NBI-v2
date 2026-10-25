# Phase8 — frozen-reference sensitivity and cardinality-controlled benchmark

The only published campaign is `turning_reference_sensitivity_20261024` (request/
protocol identifier; actual execution timestamps are UTC metadata). It consumes
immutable Phase7 artifacts and current nominal RSMs, with no refitting.

Use a separate empty output directory to reproduce. Phase8A:
`uv run python -m scripts.validation.turning_reference_sensitivity --output <directory>`.
It launches no new EA reference runs or VRF. The regenerable point-attainment
cache under ignored `experiments/runs/` is not a versioned experimental dataset.

The H5 direct-equivalence diagnostic failed. By explicit owner decision, the
official408-point front is preserved and CNBI processing cost remains pending.
VRF uses only66 Phase7 historical points; the owner forbids VRF optimization
and timing. These omissions cannot be replaced by historical parallel wall-time
or parent-H20 time. Quality benchmarking continues within the revised scope.

Read `docs/mathematics/turning_final_benchmark.md` for measured results, limits,
common/LOO distinctions, numerical HV precision and dedicated EA timing status.
