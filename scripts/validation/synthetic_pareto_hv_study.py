"""Analytic HV oracles and fixed-grid precision audit; no optimizer results."""

import numpy as np

from cnbi_v2.synthetic.pareto.hypervolume import FixedHypervolume


def run_oracles(master, power=16):
    rows, certificates = [], []
    for m in range(4, 12):
        broad = np.full((1, m), 0.2)
        overlap = np.full((2, m), 0.15)
        overlap[0, 0], overlap[1, 1] = 0.45, 0.45
        tiny = np.full((1, m), 0.8)
        tiny_overlap = np.full((2, m), 0.8)
        tiny_overlap[0, 0], tiny_overlap[1, 1] = 0.95, 0.95
        fixtures = (
            ("single_broad_box", broad, 0.9**m),
            (
                "two_overlapping_boxes",
                overlap,
                2 * 0.65 * 0.95 ** (m - 1) - 0.65**2 * 0.95 ** (m - 2),
            ),
            ("tiny_single_box", tiny, 0.3**m),
            (
                "tiny_two_box_union",
                tiny_overlap,
                2 * 0.15 * 0.3 ** (m - 1) - 0.15**2 * 0.3 ** (m - 2),
            ),
        )
        hv = FixedHypervolume(m, master, power)
        for label, points, expected in fixtures:
            estimate = hv.estimate(points)
            error = abs(estimate["HV"] - expected)
            relative_error = error / expected
            if relative_error > 1e-12 or estimate["HV_status"] != "EXACT_UP_TO_FLOAT64":
                raise ValueError("analytic HV oracle failed: " + label + f",m={m}")
            certificates.append(
                dict(
                    oracle=label,
                    m=m,
                    expected=expected,
                    hybrid_value=estimate["HV"],
                    absolute_error=error,
                    relative_error=relative_error,
                    status=estimate["HV_status"],
                    method=estimate["HV_method"],
                )
            )
            for row in hv.study(points):
                rows.append(
                    dict(
                        case_type="analytic_oracle",
                        scenario_id=label,
                        n_reference=None,
                        tier_max_power=power,
                        **row,
                        exact_oracle=expected,
                        absolute_error=abs(row["HV_QMC"] - expected),
                        relative_error=abs(row["HV_QMC"] - expected) / expected,
                    )
                )
    return rows, certificates
