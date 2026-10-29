from time import perf_counter, process_time

import numpy as np
from numpy.testing import assert_array_equal

from cnbi_v2.benchmark.observation import PopulationObserver
from cnbi_v2.reference import CanonicalProblem, EAConfig, run_evolutionary


def test_callback_does_not_change_seeded_final_populations_for_either_family():
    rng = np.random.default_rng(44)
    problem = CanonicalProblem(rng.normal(size=(10, 8)), np.ones(8), np.zeros(8), np.ones(8), 2.0)
    for family in ("NSGA3", "MOEAD"):
        config = EAConfig(family, n_partitions=1, generations=4)
        without = run_evolutionary(problem, config, 1001)
        observer = PopulationObserver(
            (2, 4), 1e-14, np.full(8, 1e-14), perf_counter(), process_time()
        )
        with_logging = run_evolutionary(problem, config, 1001, callback=observer)
        for key in ("x", "natural_f", "optimizer_f"):
            assert_array_equal(without[key], with_logging[key])
        assert without["nfe"] == with_logging["nfe"] == 32
        assert [r["generation"] for r in observer.records] == [2, 4]
        assert [r["nfe"] for r in observer.records] == [16, 32]
        assert observer.observation_seconds > 0
        assert observer.records[-1]["T_total"] >= observer.observation_seconds
        for row in observer.records:
            assert len(set(row["population_indices"])) == len(row["x"])
            assert row["N_unique_ND"] <= row["N_ND_before_dedup"] <= row["N_returned"]
            assert row["cpu_seconds"] >= 0
