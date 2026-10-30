"""Lossless run artifacts and append-only attempt history, without oracle imports."""

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .contracts import RunOutput


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return json_value(value.tolist())
    if isinstance(value, np.generic):
        return json_value(value.item())
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_value(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return {"nonfinite_diagnostic": str(value)}
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(json_value(value), indent=2, allow_nan=False)+"\n").encode())


def read_json(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return result


def verify_payload(directory: Path, checksums: dict[str, str]) -> None:
    for name, expected in checksums.items():
        if file_hash(directory/name) != expected:
            raise ValueError("run payload checksum mismatch: "+name)


def save_output(directory: Path, run_id: str, output: RunOutput,
                metadata: dict[str, Any]) -> dict[str, str]:
    names = {
        "x": f"raw_decisions/{run_id}.npz",
        "y": f"raw_rsm_responses/{run_id}.npz",
        "extra": f"algorithm_diagnostics/{run_id}.npz",
        "metadata": f"algorithm_diagnostics/{run_id}.json",
    }
    for name in names.values():
        target = directory/name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError("immutable run output already exists: "+name)
    np.savez_compressed(directory/names["x"], decisions=output.decisions)
    np.savez_compressed(directory/names["y"], rsm_responses=output.rsm_responses)
    np.savez_compressed(directory/names["extra"], allow_pickle=False, **output.arrays)
    write_json(directory/names["metadata"], dict(
        **metadata, algorithm_status=output.status, diagnostics=output.diagnostics,
        timings=output.timings, counters=output.counters,
    ))
    return {name: file_hash(directory/name) for name in names.values()}


def begin_attempt(
    path: Path, identity: dict[str, Any], protocol_hash: str,
) -> dict[str, Any] | None:
    """Completed runs reload; failures need an explicit separately documented retry."""
    if path.exists():
        checkpoint = read_json(path)
        if checkpoint["identity"] != identity or checkpoint["protocol_hash"] != protocol_hash:
            raise ValueError("checkpoint from incompatible identity or scientific version")
        if checkpoint["state"] in {"COMPLETED", "FAILED", "INCOMPLETE"}:
            return None
        if checkpoint["state"] == "PENDING":
            checkpoint["state"] = "RUNNING"
            checkpoint["history"].append(dict(attempt=checkpoint["attempt"], state="RUNNING"))
            write_json(path, checkpoint)
            return checkpoint
        if checkpoint["state"] == "RUNNING":
            raise ValueError("interrupted RUNNING attempt needs an operational recovery record")
        raise ValueError("unsupported checkpoint state")
    checkpoint = dict(identity=identity, protocol_hash=protocol_hash, state="RUNNING", attempt=1,
                      history=[dict(attempt=1, state="RUNNING")])
    write_json(path, checkpoint)
    return checkpoint


def recover_attempt(path: Path, reason: str) -> None:
    """Explicit operational retry; retain prior checkpoint and immutable payloads."""
    if not reason.strip():
        raise ValueError("operational recovery requires a reason")
    checkpoint = read_json(path)
    if checkpoint["state"] not in {"FAILED", "INCOMPLETE", "RUNNING"}:
        raise ValueError("completed or pending tasks cannot be replaced")
    if "payload_checksums" in checkpoint:
        raise ValueError("a retained scientific outcome cannot be replaced by an operational retry")
    archive = path.parent/"attempt_history"/f"{path.stem}.attempt{checkpoint['attempt']}.json"
    if archive.exists():
        raise FileExistsError("previous attempt archive already exists")
    write_json(archive, checkpoint)
    checkpoint["attempt"] += 1
    checkpoint["state"] = "PENDING"
    checkpoint["history"].append(dict(
        attempt=checkpoint["attempt"], state="PENDING", reason=reason,
    ))
    write_json(path, checkpoint)
