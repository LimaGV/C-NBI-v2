"""Scientific settings fixed before pilot, independent of observed performance."""

import json
from math import comb
from pathlib import Path
from typing import Any

from .contracts import METHODS

MC_SAMPLES = 2000
V1_COMMIT = "7bd4915a9aea94b9dca1d70014ba5186b4b4e44d"
INTEGRATION_COMMIT = "c06467688187b6a2234a583a538b2b7131088172"


def lattice_resolution(k: int) -> int:
    if not 2 <= k <= 6:
        raise ValueError("eligible simplex dimension must be 2..6")
    return 5 if k <= 4 else 2


def ea_ceiling(m: int) -> int:
    return max(50000, 400*comb(m+3, 4))


def load_ea_configuration(path: Path, method: str, nx: int, m: int) -> dict[str, Any]:
    if method not in METHODS[2:]:
        raise ValueError("unknown evolutionary method")
    records = json.loads(path.read_text(encoding="utf-8"))
    record: dict[str, Any] = records[f"{method}_nx{nx}_m{m}"]
    if record["status"] != "COMPLETED":
        raise ValueError("unvalidated legacy calibration")
    return record
