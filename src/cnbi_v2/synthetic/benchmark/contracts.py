"""Search inputs contain observations and estimated quantities, never truth."""

import hashlib
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from cnbi_v2.model.quadratic_design import FloatArray
from cnbi_v2.synthetic.rsm.rsm_serialization import StoredRSM

METHODS = ("C-NBI", "VRF-NBI", "NSGA-III", "MOEA/D")
PILOT_SCENARIOS = ("nx2_delta1_rho025", "nx3_delta3_rho060", "nx5_delta5_rho085")


def array_hash(x: FloatArray) -> str:
    return hashlib.sha256(np.asarray(x, dtype="<f8", order="C").tobytes()).hexdigest()


def stream_seed(scenario: str, replica: int, method: str, purpose: str) -> int:
    text = f"C-NBI-v2/phase10d/v1/20261029/{scenario}/{replica}/{method}/{purpose}"
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:16], "little")


@dataclass(frozen=True)
class SearchInput:
    scenario_id: str
    replica_id: int
    model: StoredRSM
    ccd: FloatArray
    observed: FloatArray
    design_r: FloatArray
    residual_covariance: FloatArray

    def __post_init__(self) -> None:
        nx, m = self.model.nx, self.model.coefficients.shape[1]
        if (self.replica_id not in range(1, 6)
                or self.model.instance_id != f"{self.scenario_id}__replica{self.replica_id}"
                or self.ccd.ndim != 2 or self.ccd.shape[1] != nx
                or self.observed.shape != (len(self.ccd), m)
                or self.residual_covariance.shape != (m, m)
                or self.design_r.shape != (len(self.model.coefficients),)*2):
            raise ValueError("inconsistent frozen search input")
        for name in ("ccd", "observed", "design_r", "residual_covariance"):
            value = np.asarray(getattr(self, name), dtype=np.float64)
            if not np.isfinite(value).all():
                raise ValueError("nonfinite frozen input")
            object.__setattr__(self, name, np.frombuffer(value.tobytes(), dtype=np.float64)
                               .reshape(value.shape))

    @property
    def nx(self) -> int:
        return self.model.nx

    @property
    def m(self) -> int:
        return int(self.model.coefficients.shape[1])

    @property
    def alpha(self) -> float:
        return float(2**(self.nx/4))


@dataclass
class RunOutput:
    decisions: FloatArray
    rsm_responses: FloatArray
    status: str
    diagnostics: dict[str, Any] = field(default_factory=dict)
    arrays: dict[str, FloatArray] = field(default_factory=dict)
    timings: dict[str, float] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)

    def validate(self, data: SearchInput) -> None:
        if (self.decisions.ndim != 2 or self.decisions.shape[1] != data.nx
                or self.rsm_responses.shape != (len(self.decisions), data.m)
                or not np.isfinite(self.decisions).all()
                or not np.isfinite(self.rsm_responses).all()
                or (len(self.decisions) and not np.array_equal(
                    data.model.predict(self.decisions), self.rsm_responses,
                ))):
            raise ValueError("raw output is not a finite, aligned prediction of the frozen RSM")
