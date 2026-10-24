"""Print an infrastructure inventory without reading credentials."""

import importlib.metadata
import importlib.util
import json
import platform
import sys
from pathlib import Path

import cnbi_v2

root = Path(__file__).resolve().parents[1]
report = {
    "python": platform.python_version(),
    "executable": sys.executable,
    "prefix": sys.prefix,
    "package": cnbi_v2.__file__,
    "version": cnbi_v2.__version__,
    "project_venv": str(root / ".venv"),
    "legacy_cnbi_discoverable": importlib.util.find_spec("cnbi") is not None,
    "legacy_cnbi_loaded": "cnbi" in sys.modules,
    "sys_path": sys.path,
    "dependencies": {
        name: importlib.metadata.version(name)
        for name in [
            "numpy",
            "scipy",
            "pandas",
            "scikit-learn",
            "openpyxl",
            "pymoo",
            "pytest",
            "pytest-cov",
            "ruff",
            "mypy",
            "ipykernel",
            "jupyterlab",
        ]
    },
}
print(json.dumps(report, indent=2, ensure_ascii=False))
