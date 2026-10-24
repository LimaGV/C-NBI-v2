"""Exclude a whole family before union, deduplication and nondominance."""

from cnbi_v2.model.quadratic_design import FloatArray

from .pools import PointPool, front


def reference(pools: dict[str, PointPool], *, excluded: str | None = None,
              x_tolerance: float, dominance_tolerance: FloatArray) -> PointPool:
    # Require the independent original pools, never a previously merged envelope.
    for family, pool in pools.items():
        if any(origin.family != family for group in pool.origins for origin in group):
            raise ValueError("LOO input must contain homogeneous original family pools")
    if excluded is not None and excluded not in pools:
        raise ValueError("excluded family is absent")
    result = front([p for name, p in pools.items() if name != excluded],
                   x_tolerance, dominance_tolerance)
    if any(o.family == excluded for group in result.origins for o in group):
        raise RuntimeError("excluded family leaked into reference provenance")
    return result
