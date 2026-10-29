"""Non-mutating call instrumentation for the reused mathematical kernels.

Scalar response calls, vectorized model calls and analytic gradients are separate
counters. These counts are not asserted to represent equal computational work.
"""

import sys
from collections import Counter
from types import FrameType
from typing import Any


class KernelCounter:
    def __init__(self) -> None:
        self.counts: Counter[str] = Counter()
        self.previous: Any = None

    def profile(self, frame: FrameType, event: str, argument: Any) -> None:
        if event != "call":
            return
        name = frame.f_code.co_name
        if name not in {"value", "gradient", "solve_quadratic_ball", "equality_jacobian",
                        "sphere_margin", "sphere_jacobian", "_minimize_slsqp",
                        "evaluate_responses"}:
            return
        filename = frame.f_code.co_filename.replace("\\", "/")
        mapping = {
            ("optimization/quadratic.py", "value"): "scalar_quadratic_values",
            ("optimization/quadratic.py", "gradient"): "scalar_quadratic_gradients",
            ("optimization/anchors.py", "evaluate_responses"): "quadratic_response_vector_calls",
            ("optimization/trust_region.py", "solve_quadratic_ball"): "quadratic_ball_solves",
            ("nbi/solver.py", "equality_jacobian"): "nbi_equality_jacobians",
            ("nbi/solver.py", "sphere_margin"): "sphere_constraint_calls",
            ("nbi/solver.py", "sphere_jacobian"): "sphere_constraint_jacobians",
            ("_slsqp_py.py", "_minimize_slsqp"): "slsqp_solves",
        }
        for (suffix, function), counter in mapping.items():
            if filename.endswith(suffix) and name == function:
                self.counts[counter] += 1

    def __enter__(self) -> "KernelCounter":
        self.previous = sys.getprofile()
        sys.setprofile(self.profile)
        return self

    def __exit__(self, *args: object) -> None:
        sys.setprofile(self.previous)
