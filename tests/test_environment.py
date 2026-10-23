"""Check isolation, package provenance and absence of legacy coupling."""

import ast
import importlib
import importlib.metadata
import importlib.util
import re
import sys
import tomllib
from pathlib import Path

import pytest

import cnbi_v2

ROOT = Path(__file__).resolve().parents[1]


def test_python_312() -> None:
    assert sys.version_info[:2] == (3, 12)


def test_project_virtual_environment() -> None:
    assert Path(sys.prefix).resolve() == (ROOT / ".venv").resolve()
    assert Path(sys.executable).absolute().is_relative_to(ROOT / ".venv")
    assert sys.prefix != sys.base_prefix


def test_editable_package_origin() -> None:
    assert cnbi_v2.__file__ is not None
    assert Path(cnbi_v2.__file__).resolve() == ROOT / "src" / "cnbi_v2" / "__init__.py"


def test_version_matches_distribution_and_project() -> None:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    assert cnbi_v2.__version__ == "0.1.0.dev0"
    assert cnbi_v2.__version__ == project["version"]
    assert cnbi_v2.__version__ == importlib.metadata.version("c-nbi-v2")


@pytest.mark.parametrize("module_name", ["numpy", "scipy", "pandas", "sklearn"])
def test_runtime_dependency_imports(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module.__file__ is not None
    assert Path(module.__file__).resolve().is_relative_to((ROOT / ".venv").resolve())


def test_runtime_dependencies_are_only_the_requested_libraries() -> None:
    requirements = importlib.metadata.requires("c-nbi-v2") or []
    names = {re.split(r"[\s<>=!~;\[]", item, maxsplit=1)[0].lower() for item in requirements}
    assert names == {"numpy", "scipy", "pandas", "scikit-learn"}


def test_legacy_package_is_unavailable_and_not_loaded() -> None:
    assert importlib.util.find_spec("cnbi") is None
    assert not any(name == "cnbi" or name.startswith("cnbi.") for name in sys.modules)


def test_no_legacy_checkout_on_import_path() -> None:
    for entry in sys.path:
        path = Path(entry or ".").resolve()
        assert not (path / "cnbi").exists(), f"Legacy package directory on sys.path: {path}"
        assert not (path / "cnbi.py").exists(), f"Legacy module on sys.path: {path}"
        legacy_names = {"c-nbi-v1", "cnbi-v1.0", "c-nbi"}
        assert not any(part.lower() in legacy_names for part in path.parts)


def test_source_does_not_import_legacy_package() -> None:
    for source in (ROOT / "src" / "cnbi_v2").rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name.split(".")[0] != "cnbi" for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] != "cnbi"
