"""Actual platform memory instrumentation must work before running a campaign."""

import importlib.util
from pathlib import Path


def test_process_memory_instrumentation():
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "phase10d_execution", root/"scripts/validation/execute_synthetic_benchmark.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.peak_memory_bytes() > 0
