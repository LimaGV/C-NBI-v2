"""Reproduce per-response diagnostics of the four previously recorded CCD fits.

uv run python -m scripts.validation.turning_diagnostics
No rounded-WR experiment is called. Table 3 is read only after fitting real Y.
"""

import argparse
import csv
import json
import platform
import subprocess
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from cnbi_v2.data import sha256_file
from cnbi_v2.model import diagnose_rsm, fit_multivariate_rsm

from .turning_reference import (
    PROCESSED,
    RAW,
    RESPONSES,
    ROOT,
    design_cases,
    read_literal_values,
    rounding_comparison,
    write_csv,
    write_json,
)

OUTPUT = ROOT / "results/validation/turning_rsm"
SUMMARY_REFERENCE = ROOT / "tests/reference_cases/turning_8responses/expected_model_summary.csv"
PRIMARY_CASE = "physical_cells"
PUBLICATION_CASE = "rotatable_alpha_hypothesis"
PRIMARY_HEADER = (
    "Response", "S", "R2", "R2_adj", "PRESS", "R2_pred",
    "Model_F", "Model_p", "LOF_F", "LOF_p",
)


def run_diagnostics(output: Path = OUTPUT) -> dict:
    """Write small auditable artifacts; keep response values/coding unchanged."""
    before = sha256_file(RAW)
    values, _ = read_literal_values()
    outputs = {}
    all_metrics, anova, lof, press_rows = [], [], [], []
    groups_by_case = {}
    for case, factors in design_cases(values[:, 1:4]).items():
        fit = fit_multivariate_rsm(factors, values[:, 4:])
        diagnostics = diagnose_rsm(fit, factors, RESPONSES)
        groups_by_case[case] = {
            "unique_configurations": len(diagnostics.factor_groups),
            "replicate_run_ids": [
                [int(values[i, 0]) for i in group] for group in diagnostics.replicate_groups
            ],
            "leverage_sum": float(diagnostics.hat_diagonal.sum()),
            "leverage_min": float(diagnostics.hat_diagonal.min()),
            "leverage_max": float(diagnostics.hat_diagonal.max()),
            "leverage_tolerance": diagnostics.leverage_tolerance,
            "press_undefined_run_ids": [
                int(values[i, 0]) for i in diagnostics.press_undefined_rows
            ],
            "rank": fit.rank,
            "n": fit.n_observations,
            "p": fit.n_terms,
            "condition_number": fit.design_condition_number,
        }
        outputs[case] = diagnostics
        for d in diagnostics.responses:
            all_metrics.append([case, *asdict(d).values()])
            anova.extend([
                [case, d.response_name, "model", d.ssr, d.model_df, d.model_ms,
                 d.model_f, d.model_p_value, d.model_status],
                [case, d.response_name, "error", d.sse, d.error_df, d.error_ms, None, None, "OK"],
                [case, d.response_name, "total_corrected", d.sst, len(values) - 1,
                 None, None, None, d.r_squared_status],
            ])
            lof.append([
                case, d.response_name, d.sse, d.error_df, d.pure_error_ss,
                d.pure_error_df, d.pure_error_ms, d.lack_of_fit_ss, d.lack_of_fit_df,
                d.lack_of_fit_ms, d.lack_of_fit_f, d.lack_of_fit_p_value,
                d.sse - d.pure_error_ss - d.lack_of_fit_ss, d.lack_of_fit_status,
            ])
        for i, run_id in enumerate(values[:, 0]):
            press_rows.append([
                case, int(run_id), diagnostics.hat_diagonal[i],
                *([None] * len(RESPONSES) if diagnostics.press_residuals is None
                  else diagnostics.press_residuals[i].tolist()),
            ])

    # Expected outputs are never inputs to OLS or to the diagnostics API.
    with SUMMARY_REFERENCE.open(encoding="utf-8", newline="") as stream:
        published = {row["response"]: row for row in csv.DictReader(stream)}
    comparison, compatibility = [], {}
    for case, diagnostics in outputs.items():
        counts = Counter()
        for d in diagnostics.responses:
            metrics = {"S": d.s, "R2": d.r_squared,
                       "R2_adj": d.adjusted_r_squared, "R2_pred": d.predicted_r_squared}
            for metric, canonical in metrics.items():
                text = published[d.response_name][metric]
                # S is printed in 10^-2; R-squared quantities are percentages.
                display = canonical * 100 if canonical is not None else None
                if display is None:
                    half_width = margin = match = difference = None
                else:
                    half_width, margin, match = rounding_comparison(display, text)
                    difference = display - float(text)
                    counts[metric] += int(match)
                comparison.append([
                    case, d.response_name, metric, canonical, text,
                    "1e-2" if metric == "S" else "percent",
                    display, difference, half_width, margin, match,
                    "PUBLISHED_R2_PRED_METHOD_UNSPECIFIED" if metric == "R2_pred"
                    else "SECONDARY_PUBLICATION_REFERENCE",
                ])
        compatibility[case] = dict(counts)

    output.mkdir(parents=True, exist_ok=True)
    primary = outputs[PRIMARY_CASE]
    write_csv(output / "model_diagnostics.csv", PRIMARY_HEADER, [
        [d.response_name, d.s, d.r_squared, d.adjusted_r_squared, d.press,
         d.predicted_r_squared, d.model_f, d.model_p_value,
         d.lack_of_fit_f, d.lack_of_fit_p_value] for d in primary.responses
    ])
    write_csv(output / "all_cases_model_diagnostics.csv",
              ["Case", *asdict(primary.responses[0]).keys()], all_metrics)
    write_csv(output / "anova.csv",
              ["Case", "Response", "Source", "SS", "df", "MS", "F", "p", "Status"], anova)
    write_csv(output / "lack_of_fit.csv", [
        "Case", "Response", "SSE", "error_df", "SS_PE", "df_PE", "MS_PE",
        "SS_LOF", "df_LOF", "MS_LOF", "F_LOF", "p_LOF", "decomposition_error", "Status",
    ], lof)
    write_csv(output / "press_residuals.csv", ["Case", "Exp", "h_ii", *RESPONSES], press_rows)
    write_csv(output / "published_summary_comparison.csv", [
        "Case", "Response", "Metric", "Canonical_value", "Published_text",
        "Published_scale", "Calculated_display", "Difference_display_units",
        "Published_rounding_half_width", "Float64_boundary_allowance",
        "Rounding_compatible", "Comparability_status",
    ], comparison)
    after = sha256_file(RAW)
    if after != before:
        raise RuntimeError("Raw changed during read-only diagnostics")
    summary = {
        "primary_case": PRIMARY_CASE,
        "secondary_publication_case": PUBLICATION_CASE,
        "data_status": "FULL_PRECISION_LITERAL_VALUES_UNCHANGED",
        "response_order": RESPONSES,
        "r_squared_units": "fraction",
        "diagnostics_by_case": groups_by_case,
        "publication_rounding_compatible_out_of_8": compatibility,
        "published_predicted_r_squared_method": "PUBLISHED_R2_PRED_METHOD_UNSPECIFIED",
        "publication_source": {
            "doi": "10.1016/j.engappai.2025.112510", "zotero_key": "SMMX47JT",
            "table": "Table 3", "pdf_page": 13, "status": "FULLTEXT_VERIFIED",
            "S_printed_unit": "1e-2", "R2_printed_unit": "percent",
            "coefficient_published_scaling": {"WR": "1e-2", "ROI": "1e-2", "OEE": "1e-2"},
            "method_audit": "No explicit PRESS/LOOCV definition for Table 3 found; "
                            "ML cross-validation on pp.22-23 does not define that statistic.",
        },
        "wr_rounding_status": "PUBLICATION_RECONCILIATION_NOTE_OUTSIDE_OFFICIAL_PIPELINE",
        "interpretation_alpha": 0.05,
        "individual_tests_no_multiplicity_adjustment": True,
        "physical_case_model_p_below_alpha": [
            d.response_name for d in primary.responses
            if d.model_p_value is not None and d.model_p_value < 0.05
        ],
        "physical_case_lof_p_below_alpha": [
            d.response_name for d in primary.responses
            if d.lack_of_fit_p_value is not None and d.lack_of_fit_p_value < 0.05
        ],
    }
    write_json(output / "summary.json", summary)
    (output / "README.md").write_text(
        "# Full-precision turning RSM diagnostics\n\n"
        "Reproduce: `uv run python -m scripts.validation.turning_diagnostics`.\n"
        "model_diagnostics.csv: eight responses, physical_cells; R2 values are fractions.\n"
        "all_cases_model_diagnostics.csv, anova.csv, lack_of_fit.csv and press_residuals.csv: "
        "all four previously recorded fits; Case is explicit.\n"
        "published_summary_comparison.csv: secondary comparison, all four cases; "
        "S*100, R2*100, differences in printed units, half last printed unit.\n"
        "R2_pred method in the article is unspecified; "
        "numeric agreement does not prove equivalence.\n"
        "No rounded WR, changed observations, selected terms or later optimization.\n"
        "See docs/mathematics/turning_rsm_diagnostics.md for scientific interpretation.\n"
        "manifest.json binds actual execution commit, code/input hashes and environment; "
        "checksums.sha256 covers every artifact except itself.\n",
        encoding="utf-8", newline="\n",
    )
    files = [RAW, PROCESSED, SUMMARY_REFERENCE, ROOT / "uv.lock", Path(__file__),
             ROOT / "scripts/validation/turning_reference.py",
             *sorted((ROOT / "src/cnbi_v2/model").glob("*.py"))]
    artifact_files = sorted(p for p in output.iterdir()
                            if p.is_file() and p.name not in {"manifest.json", "checksums.sha256"})
    manifest = {
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "git_working_tree_dirty": bool(subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "command": "uv run python -m scripts.validation.turning_diagnostics",
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {name: version(name) for name in ["numpy", "scipy", "openpyxl"]},
        "input_sha256": {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in files},
        "raw_before_sha256": before, "raw_after_sha256": after,
        "output_sha256": {p.name: sha256_file(p) for p in artifact_files},
        "canonical_data_rounded": False, "wr_rounding_experiment_executed": False,
        "models_or_coding_changed": False,
    }
    write_json(output / "manifest.json", manifest)
    (output / "checksums.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.name}\n" for p in sorted(output.iterdir())
                if p.is_file() and p.name != "checksums.sha256"),
        encoding="utf-8", newline="\n",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    summary = run_diagnostics(args.output)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
