"""The only controlled factors are nx,delta and mean absolute correlation."""

from dataclasses import dataclass
from itertools import product
from numbers import Integral

DIMENSIONS = (2, 3, 5)
EXCESSES = (1, 3, 5)
TARGETS = (0.25, 0.60, 0.85)


@dataclass(frozen=True, slots=True)
class Scenario:
    nx: int
    delta: int
    rho_target: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.nx, bool)
            or isinstance(self.delta, bool)
            or not isinstance(self.nx, Integral)
            or not isinstance(self.delta, Integral)
            or self.nx not in DIMENSIONS
            or self.delta not in EXCESSES
            or self.rho_target not in TARGETS
        ):
            raise ValueError("scenario factors must belong to the frozen 3x3x3 design")

    @property
    def m(self) -> int:
        return self.nx + 1 + self.delta

    @property
    def scenario_id(self) -> str:
        return f"nx{self.nx}_delta{self.delta}_rho{round(100 * self.rho_target):03d}"

    @property
    def ordinal(self) -> int:
        return (
            9 * DIMENSIONS.index(self.nx)
            + 3 * EXCESSES.index(self.delta)
            + TARGETS.index(self.rho_target)
        )

    def seeds(self, master: int) -> tuple[int, int, int]:
        """Fixed cell-keyed streams, independent of iteration order."""
        base = master + 10 * self.ordinal
        return base + 1, base + 2, base + 3


def factorial_design() -> tuple[Scenario, ...]:
    return tuple(Scenario(n, d, r) for n, d, r in product(DIMENSIONS, EXCESSES, TARGETS))
