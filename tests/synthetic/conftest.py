import pytest

from cnbi_v2.synthetic import CalibrationConfig, Scenario, calibrate


@pytest.fixture(scope="module")
def small_config():
    return CalibrationConfig(calibration_power=11, validation_power=12, n_starts=2)


@pytest.fixture(scope="module")
def small_results(small_config):
    return tuple(
        calibrate(cell, small_config)
        for cell in (
            Scenario(2, 1, 0.60),
            Scenario(2, 5, 0.25),
            Scenario(3, 1, 0.85),
        )
    )
