"""Common MIN orientation and one fixed normalization from the nominal payoff."""

from collections.abc import Sequence
from dataclasses import dataclass, fields

import numpy as np
from numpy.typing import ArrayLike

from cnbi_v2.model.quadratic_design import FloatArray, _as_finite_real
from cnbi_v2.optimization.quadratic import Direction

from ._validation import frozen


@dataclass(frozen=True, slots=True)
class PayoffNormalization:
    nominal_payoff: FloatArray
    signs: FloatArray
    utopia: FloatArray
    payoff_worst: FloatArray
    amplitudes: FloatArray
    optimality_tolerance: FloatArray
    degeneracy_tolerance: FloatArray

    def __post_init__(self) -> None:
        for field in fields(self):
            object.__setattr__(self, field.name, frozen(getattr(self, field.name)))

    def _payoffs(self, payoffs: ArrayLike) -> FloatArray:
        values = _as_finite_real(payoffs, "payoffs")
        if values.ndim < 2 or values.shape[-2:] != self.nominal_payoff.shape:
            raise ValueError("payoffs must end in the nominal (response,anchor) shape")
        return values

    def normalize(self, payoffs: ArrayLike) -> FloatArray:
        values = self._payoffs(payoffs)
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            result = (values*self.signs[:, None] - self.utopia[:, None]) / self.amplitudes[:, None]
        if not np.isfinite(result).all():
            raise FloatingPointError("nonfinite normalized payoff")
        return frozen(result)

    def perturbations(self, payoffs: ArrayLike) -> FloatArray:
        """Delta=D_a^-1 D_s (A_b-A_nom); never recenter/rescale per replica."""
        values = self._payoffs(payoffs)
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            result = ((values-self.nominal_payoff) * self.signs[:, None]
                      / self.amplitudes[:, None])
        if not np.isfinite(result).all():
            raise FloatingPointError("nonfinite normalized perturbation")
        return frozen(result)


def nominal_normalization(
    nominal_payoff: ArrayLike,
    directions: Sequence[Direction],
    *,
    optimality_tolerance: ArrayLike | None = None,
) -> PayoffNormalization:
    payoff = _as_finite_real(nominal_payoff, "nominal_payoff")
    if payoff.ndim != 2 or payoff.shape[0] != payoff.shape[1] or len(payoff) < 2:
        raise ValueError("nominal payoff must be square with at least two responses")
    signs = np.asarray([Direction(d).minimization_sign for d in directions], dtype=np.float64)
    if signs.shape != (len(payoff),):
        raise ValueError("directions must match nominal response order")
    oriented = signs[:, None]*payoff
    utopia = np.diag(oriented).copy()
    worst = oriented.max(axis=1)
    # This bound addresses float64 subtraction/representation only. Real-data
    # optimality tolerances are supplied from archived Phase 2 certificates.
    roundoff = np.finfo(float).eps*16*len(payoff)*np.max(np.abs(oriented), axis=1)
    tolerance = (roundoff.copy() if optimality_tolerance is None
                 else _as_finite_real(optimality_tolerance, "optimality_tolerance"))
    if tolerance.shape != utopia.shape or np.any(tolerance < 0):
        raise ValueError("optimality_tolerance must be a nonnegative response vector")
    with np.errstate(over="raise", invalid="raise"):
        if np.any(oriented - utopia[:, None] < -tolerance[:, None]):
            raise ValueError("nominal diagonal violates individual MIN optimality")
        amplitude = worst - utopia
    if np.any(amplitude <= roundoff):
        raise ValueError("nominal payoff amplitude is nonpositive or numerically degenerate")
    return PayoffNormalization(payoff, signs, utopia, worst, amplitude, tolerance, roundoff)
