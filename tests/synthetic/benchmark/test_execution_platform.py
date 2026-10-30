"""Actual platform memory instrumentation must work before running a campaign."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_process_memory_instrumentation():
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "phase10d_execution", root/"scripts/validation/execute_synthetic_benchmark.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.peak_memory_bytes() > 0


def test_physical_core_affinity_is_set_before_worker_import(tmp_path, monkeypatch):
    if sys.platform != "win32":
        pytest.skip("audited Windows scheduler topology API")
    root = Path(__file__).resolve().parents[3]
    monkeypatch.syspath_prepend(str(root/"scripts/validation"))
    from run_phase10d_campaign import PIN_AND_RUN, physical_masks
    masks = physical_masks()
    assert len(masks) == len(set(masks)) and all(mask.bit_count() == 1 for mask in masks)
    probe = tmp_path/"affinity_probe.py"
    probe.write_text(
        "import ctypes\n"
        "k=ctypes.WinDLL('kernel32');k.GetCurrentProcess.restype=ctypes.c_void_p\n"
        "f=k.GetProcessAffinityMask\n"
        "f.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),"
        "ctypes.POINTER(ctypes.c_size_t)]\n"
        "a=ctypes.c_size_t();b=ctypes.c_size_t()\n"
        "assert f(k.GetCurrentProcess(),ctypes.byref(a),ctypes.byref(b))\n"
        "print(a.value)\n",
    )
    actual = subprocess.check_output([sys.executable, "-c", PIN_AND_RUN, str(probe)],
                                     env=dict(os.environ, PHASE10D_CPU_MASK=str(masks[0])))
    assert int(actual) == masks[0]
