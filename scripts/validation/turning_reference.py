"""Fit the literal CCD revision and report, rather than conceal, publication mismatches.

Run from the repository: uv run python -m scripts.validation.turning_reference
No workbook is saved or recalculated. Published outputs never generate observations.
"""

import argparse
import csv
import json
import platform
import subprocess
import zipfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import openpyxl

from cnbi_v2.data import inspect_workbook, sha256_file
from cnbi_v2.model import fit_multivariate_rsm

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/turning_application/CCD_values_20261023.xlsx"
PROCESSED = ROOT / "data/processed/turning_application/CCD_values_20261023.csv"
REFERENCE = ROOT / "tests/reference_cases/turning_8responses/expected_coefficients.csv"
RAW_SHA256 = "7f905b7a2f7bb8b6735ab96900cba7356401df2d26c961dcb12faa2683c6c71e"
RESPONSES = ("T", "MTTF", "WR", "Ra", "Rt", "Kp", "ROI", "OEE")
HEADERS = ("Exp", "cs", "f", "md", *RESPONSES)
TERMS = (
    "beta0",
    "beta1",
    "beta2",
    "beta3",
    "beta11",
    "beta22",
    "beta33",
    "beta12",
    "beta13",
    "beta23",
)


def read_literal_values(path: Path = RAW) -> tuple[np.ndarray, list[list[str]]]:
    """Return float64 input and original OOXML numeric lexemes, without caches."""
    if sha256_file(path) != RAW_SHA256:
        raise ValueError("Unexpected CCD revision hash; review a new revision explicitly")
    report = inspect_workbook(path, detail_limit=1000)
    if (
        not report.inspection_complete
        or not report.source_unchanged
        or report.external_reference_assessment != "NOT_DETECTED"
        or len(report.sheets) != 1
        or report.sheets[0].formula_count != 0
    ):
        raise ValueError("The supplied CCD must be completely inspected and literal/self-contained")
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=False, keep_links=False)
    try:
        rows = list(workbook["Plan1"].iter_rows(values_only=True))
    finally:
        workbook.close()
    if len(rows) != 20 or tuple(rows[0]) != HEADERS or any(len(row) != 12 for row in rows):
        raise ValueError("CCD must have 19 runs and the verified 12 columns including Exp")
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    cells = {cell.attrib["r"]: cell for cell in sheet.findall(".//s:sheetData/s:row/s:c", ns)}
    lexemes = []
    for row_number in range(2, 21):
        record = []
        for column in "ABCDEFGHIJKL":
            cell = cells[f"{column}{row_number}"]
            value = cell.findtext("s:v", namespaces=ns)
            if (
                cell.find("s:f", ns) is not None
                or cell.attrib.get("t", "n") != "n"
                or value is None
                or not Decimal(value).is_finite()
            ):
                raise ValueError("All 228 stored data cells must be finite numeric literals")
            record.append(value)
        lexemes.append(record)
    values = np.asarray(lexemes, dtype=np.float64)
    if not np.isfinite(values).all() or not np.array_equal(values[:, 0], np.arange(1, 20)):
        raise ValueError("Invalid finite values or experiment identifiers")
    if not np.array_equal(values, np.asarray(rows[1:], dtype=np.float64)):
        raise ValueError("OOXML literal values and read-only workbook values disagree")
    return values, lexemes


def design_cases(physical: np.ndarray) -> dict[str, np.ndarray]:
    """Keep actual cell coordinates separate from explicitly labelled nominal DOE hypotheses."""
    center = physical[14:19].mean(axis=0)
    if not np.array_equal(physical[14:19], np.tile(center, (5, 1))):
        raise ValueError("Expected five identical physical center settings")
    half_range = (physical[:8].max(axis=0) - physical[:8].min(axis=0)) / 2
    cases = {
        "physical_cells": physical.copy(),
        "affine_from_cells": (physical - center) / half_range,
    }
    for label, alpha in [("table6_rounded_alpha", 1.682), ("rotatable_alpha_hypothesis", 8**0.25)]:
        coded = np.zeros((19, 3))
        # Exact factorial row order from the publication's Table 6, joined by Exp.
        coded[:8] = [
            [-1, -1, -1],
            [1, -1, -1],
            [-1, 1, -1],
            [1, 1, -1],
            [-1, -1, 1],
            [1, -1, 1],
            [-1, 1, 1],
            [1, 1, 1],
        ]
        for j in range(3):
            coded[8 + 2 * j, j], coded[9 + 2 * j, j] = -alpha, alpha
        cases[label] = coded
    return cases


def rounding_comparison(calculated: float, printed: str) -> tuple[float, float, bool]:
    """Printed rounding interval, with only a float64 boundary allowance (ties included)."""
    expected = Decimal(printed)
    half_width = float(Decimal("0.5") * Decimal(10) ** expected.as_tuple().exponent)
    numerical_allowance = 16 * np.finfo(float).eps * max(1, abs(calculated), abs(float(expected)))
    matches = abs(calculated - float(expected)) <= half_width + numerical_allowance
    return half_width, numerical_allowance, bool(matches)


def write_csv(path: Path, header, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def wr_rounding_diagnostic(values: np.ndarray) -> dict:
    """Test an explicitly lossy hypothesis on a copy, never the actual CCD fits."""
    original = values[:, 6].copy()
    rounded_copy = np.round(original, 3)
    factors = design_cases(values[:, 1:4])["rotatable_alpha_hypothesis"]
    hypothetical_fit = fit_multivariate_rsm(factors, rounded_copy)
    with REFERENCE.open(encoding="utf-8", newline="") as stream:
        published = list(csv.DictReader(stream))
    entries = []
    for term, coefficient, reference in zip(
        TERMS, hypothetical_fit.coefficients[:, 0], published, strict=True
    ):
        _, _, matches = rounding_comparison(float(coefficient) * 1000, reference["WR"])
        entries.append(
            {
                "coefficient": term,
                "hypothetical_raw_units": float(coefficient),
                "hypothetical_display_times1000": float(coefficient) * 1000,
                "published_exact_text": reference["WR"],
                "within_rounding": matches,
            }
        )
    return {
        "status": "POST_HOC_DIAGNOSTIC_ONLY_NOT_FULL_PRECISION_VALIDATION",
        "operation": "round a separate copy of WR to 3 decimal places before OLS",
        "original_observations_modified": False,
        "used_in_main_fits_or_match_totals": False,
        "changed_values_in_hypothetical_copy": int(np.count_nonzero(original != rounded_copy)),
        "max_absolute_loss_in_hypothetical_copy": float(np.max(np.abs(original - rounded_copy))),
        "display_multiplier": 1000,
        "matches": sum(entry["within_rounding"] for entry in entries),
        "coefficients": entries,
        "interpretation": (
            "Consistent with prior WR rounding; does not prove the authors' workflow "
            "or authorize changing experimental data"
        ),
    }


def run_validation(
    output: Path, processed: Path = PROCESSED, investigate_wr_rounding: bool = False
) -> dict:
    """Fit unchanged responses; response display multipliers apply only after fitting."""
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
    before = RAW.read_bytes()
    before_mtime = RAW.stat().st_mtime_ns
    values, lexemes = read_literal_values()
    write_csv(processed, HEADERS, lexemes)
    with REFERENCE.open(encoding="utf-8", newline="") as stream:
        expected = list(csv.DictReader(stream))
    if [row["coefficient"] for row in expected] != list(TERMS):
        raise ValueError("Unexpected published coefficient ordering")
    output.mkdir(parents=True, exist_ok=True)
    comparisons = []
    summary = {
        "raw_sha256": RAW_SHA256,
        "n_runs": 19,
        "n_factors": 3,
        "n_responses": 8,
        "cases": {},
    }
    multipliers = {
        "table3_footnote_1e-2": [1, 1, 100, 1, 1, 1, 100, 100],
        "diagnostic_1e-3_NOT_FOOTNOTE": [1, 1, 1000, 1, 1, 1, 1000, 1000],
    }
    for label, factors in design_cases(values[:, 1:4]).items():
        fit = fit_multivariate_rsm(factors, values[:, 4:])
        folder = output / label
        write_csv(
            folder / "factors_used.csv",
            ["Exp", "x1", "x2", "x3"],
            zip(values[:, 0].astype(int), *factors.T, strict=True),
        )
        write_csv(
            folder / "coefficients_raw_units.csv",
            ["coefficient", *RESPONSES],
            [[term, *row] for term, row in zip(TERMS, fit.coefficients, strict=True)],
        )
        for name, matrix in [("fitted_values", fit.fitted_values), ("residuals", fit.residuals)]:
            write_csv(
                folder / f"{name}.csv",
                ["Exp", *RESPONSES],
                zip(values[:, 0].astype(int), *matrix.T, strict=True),
            )
        write_csv(
            folder / "residual_covariance.csv",
            ["response", *RESPONSES],
            [[name, *row] for name, row in zip(RESPONSES, fit.residual_covariance, strict=True)],
        )
        rss = (fit.residuals**2).sum(axis=0)
        tss = ((values[:, 4:] - values[:, 4:].mean(axis=0)) ** 2).sum(axis=0)
        r2 = 1 - rss / tss
        write_csv(
            folder / "model_summary_raw_units.csv",
            ["response", "MSE", "S", "R2_percent"],
            zip(
                RESPONSES, fit.mse_by_response, np.sqrt(fit.mse_by_response), 100 * r2, strict=True
            ),
        )
        case_summary = {
            "rank": fit.rank,
            "residual_df": fit.residual_degrees_of_freedom,
            "condition_number": fit.design_condition_number,
            "comparisons": {},
        }
        for scale_label, display_multipliers in multipliers.items():
            counts = dict.fromkeys(RESPONSES, 0)
            for i, term in enumerate(TERMS):
                for j, response in enumerate(RESPONSES):
                    raw_coefficient = float(fit.coefficients[i, j])
                    display = raw_coefficient * display_multipliers[j]
                    printed = expected[i][response]
                    half_width, numerical_allowance, matches = rounding_comparison(display, printed)
                    counts[response] += int(matches)
                    comparisons.append(
                        [
                            label,
                            scale_label,
                            term,
                            response,
                            raw_coefficient,
                            display_multipliers[j],
                            display,
                            printed,
                            display - float(printed),
                            half_width,
                            numerical_allowance,
                            matches,
                        ]
                    )
            case_summary["comparisons"][scale_label] = {
                "matched_by_response": counts,
                "matched_total": sum(counts.values()),
            }
        summary["cases"][label] = case_summary
    write_csv(
        output / "all_80_coefficient_comparisons.csv",
        [
            "design_case",
            "scaling_case",
            "coefficient",
            "response",
            "calculated_raw_units",
            "display_multiplier",
            "calculated_display_units",
            "published_exact_text",
            "difference_display_units",
            "rounding_half_width",
            "numerical_allowance",
            "within_rounding",
        ],
        comparisons,
    )
    summary["full_80_coefficient_reproduction"] = any(
        comparison["matched_total"] == 80
        for case in summary["cases"].values()
        for comparison in case["comparisons"].values()
    )
    if investigate_wr_rounding:
        diagnostic = wr_rounding_diagnostic(values)
        write_json(output / "wr_rounding_hypothesis.json", diagnostic)
        summary["wr_rounding_diagnostic_matches_excluded_from_totals"] = diagnostic["matches"]
    write_json(output / "summary.json", summary)
    source_files = [
        RAW,
        processed,
        REFERENCE,
        Path(__file__),
        ROOT / "uv.lock",
        *sorted((ROOT / "src/cnbi_v2").rglob("*.py")),
    ]
    if RAW.read_bytes() != before or RAW.stat().st_mtime_ns != before_mtime:
        raise RuntimeError("Immutable input changed during validation")
    source_hashes = {
        str(p.relative_to(ROOT)).replace("\\", "/"): sha256_file(p)
        for p in source_files
        if p.is_relative_to(ROOT)
    }
    artifacts = {
        str(p.relative_to(output)).replace("\\", "/"): sha256_file(p)
        for p in sorted(output.rglob("*.csv"))
    }
    artifacts["summary.json"] = sha256_file(output / "summary.json")
    if investigate_wr_rounding:
        artifacts["wr_rounding_hypothesis.json"] = sha256_file(
            output / "wr_rounding_hypothesis.json"
        )
    write_json(
        output / "manifest.json",
        {
            "run_id": "turning_values_20261023",
            "git_execution_commit": commit,
            "working_tree_dirty_at_start": dirty,
            "executed_at_utc": datetime.now(UTC).isoformat(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "openpyxl": openpyxl.__version__,
            "input_hashes": source_hashes,
            "artifact_hashes": artifacts,
            "raw_unchanged": True,
            "responses_changed_or_rounded": False,
            "display_scaling_applied_to_Y": False,
            "nominal_doe_designs_are_separate_hypotheses": True,
            "full_80_coefficient_reproduction": summary["full_80_coefficient_reproduction"],
            "wr_rounding_diagnostic_requested": investigate_wr_rounding,
        },
    )
    entries = [
        f"{sha256_file(output / name)}  {name}" for name in [*sorted(artifacts), "manifest.json"]
    ]
    (output / "checksums.sha256").write_text(
        "\n".join(entries) + "\n", encoding="utf-8", newline="\n"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results/turning_8responses_validation"
    )
    parser.add_argument("--extract-only", action="store_true")
    parser.add_argument(
        "--investigate-wr-rounding",
        action="store_true",
        help="Explicit post-hoc lossy-copy diagnostic, excluded from real validation",
    )
    args = parser.parse_args()
    if args.extract_only:
        _, lexemes = read_literal_values()
        write_csv(PROCESSED, HEADERS, lexemes)
    else:
        summary = run_validation(args.output, investigate_wr_rounding=args.investigate_wr_rounding)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
