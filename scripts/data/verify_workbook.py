"""Inspect a local XLSX and print JSON to stdout; never write to the source."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from cnbi_v2.data import inspect_workbook


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, help="Path to a .xlsx workbook")
    parser.add_argument("--header-row", type=int, default=1)
    parser.add_argument("--max-cells", type=int, default=1_000_000)
    parser.add_argument("--detail-limit", type=int, default=100)
    args = parser.parse_args(argv)
    try:
        report = inspect_workbook(
            args.workbook,
            header_row=args.header_row,
            max_cells=args.max_cells,
            detail_limit=args.detail_limit,
        )
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(asdict(report), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
