import ast
import hashlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from cnbi_v2.synthetic.domain import radius
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.pareto.geometry import hull_geometry, sample_hull_weights
from cnbi_v2.synthetic.pareto.normalization import analytic_normalization
from cnbi_v2.synthetic.pareto.serialization import (
    array_sha256,
    load_reference,
    load_true_anchors,
    verify_checksums,
    write_csv,
    write_json,
)

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "results/phase_10_synthetic_generation/structural_20261029"


def test_all27_frozen_anchor_sources_affine_dimensions_and_minima():
    cases = load_true_anchors(SOURCE)
    assert len(cases) == 27
    for cell, a in cases:
        assert a.shape == (cell.m, cell.nx) and a.dtype == np.float64
        assert np.linalg.matrix_rank(a - a.mean(axis=0)) == cell.nx
        assert np.all(np.linalg.norm(a, axis=1) <= radius(cell.nx))
        assert_array_equal(np.diag(evaluate(a, a)), np.zeros(cell.m))


def test_codec_exact_floats_canonical_lf_and_corrupt_files(tmp_path):
    path = tmp_path / "data.json"
    write_json(path, {"a": 0.1})
    assert b"\r\n" not in path.read_bytes()
    write_csv(tmp_path / "a.csv", [{"value": float(np.nextafter(1, 2))}])
    assert float((tmp_path / "a.csv").read_text().splitlines()[1]) == np.nextafter(1, 2)
    with pytest.raises(ValueError):
        write_csv(tmp_path / "empty.csv", [])
    with pytest.raises(ValueError):
        write_json(path, {"a": np.nan})
    a = np.array([[0.1, 0.2]], dtype=np.float64)
    assert array_sha256(a) == hashlib.sha256(a.astype("<f8").tobytes()).hexdigest()
    with pytest.raises(FileNotFoundError):
        verify_checksums(tmp_path)
    checks = tmp_path / "checksums.sha256"
    checks.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        verify_checksums(tmp_path)
    path.write_bytes(b"payload")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    checks.write_text(digest + "  data.json\n", encoding="utf-8")
    assert verify_checksums(tmp_path) == {"data.json": digest}
    with pytest.raises(ValueError):
        load_true_anchors(tmp_path)
    checks.write_text((digest + "  data.json\n") * 2, encoding="utf-8")
    with pytest.raises(ValueError):
        verify_checksums(tmp_path)
    checks.write_text("0" * 64 + "  data.json\n", encoding="utf-8")
    with pytest.raises(ValueError):
        verify_checksums(tmp_path)
    for sid, n in (("missing", 5000), ("nx2_delta1_rho025", 3)):
        with pytest.raises(ValueError):
            load_reference(tmp_path, sid, n)


def test_reference_and_rsm_import_isolation_no_algorithm_input_channel():
    forbidden_calls = {
        "fit_multivariate_rsm",
        "solve_nbi_lattice",
        "run_evolutionary",
        "solve_quadratic_ball",
        "sample_coefficient_ensemble",
        "calibrate",
        "generate_instance",
        "full_ccd",
        "experimental_noise",
    }
    paths = [
        *(ROOT / "src/cnbi_v2/synthetic/pareto").glob("*.py"),
        ROOT / "scripts/validation/generate_synthetic_pareto.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = (
                    node.func.id
                    if isinstance(node.func, ast.Name)
                    else getattr(node.func, "attr", "")
                )
                assert name not in forbidden_calls, (path, name)
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(
                    (
                        "cnbi_v2.synthetic.rsm",
                        "cnbi_v2.model",
                        "cnbi_v2.optimization",
                        "cnbi_v2.reference.evolutionary",
                    )
                )
    script = (ROOT / "scripts/validation/generate_synthetic_pareto.py").read_text(encoding="utf-8")
    assert 'parser.add_argument("--output"' in script
    assert "phase_10_synthetic_generation/structural_20261029" in script
    for forbidden in ("--method-solutions", "--rsm", "--external-front"):
        assert forbidden not in script


def test_all_six_diagnostic_figure_types_and_no_grids(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/validation"))
    from synthetic_pareto_diagnostics import figures

    # Small,explicit layout fixtures; no official reference or result is produced.
    references, rows, hv, extrema = [], [], [], []
    for cell, a in load_true_anchors(SOURCE):
        geometry = hull_geometry(a)
        x = np.vstack((a, sample_hull_weights(geometry, 7, cell.ordinal + 1) @ a))
        z = evaluate(x, a)
        norm = analytic_normalization(a)
        references.append(
            SimpleNamespace(
                scenario=cell,
                geometry=geometry,
                decisions=x,
                responses=z,
                normalized=norm.transform(z),
            )
        )
        for n in (2500, 5000, 10000):
            rows.append(
                dict(
                    nx=cell.nx,
                    count=n,
                    probe_rms_coordinate_max=1 / np.sqrt(n),
                    hausdorff_rms_coordinate=1 / n,
                )
            )
        for j in range(cell.m):
            extrema.append(
                dict(
                    sample_min=float(z[:, j].min()),
                    sample_max=float(z[:, j].max()),
                    denominator=float(norm.nadir[j]),
                )
            )
        for p in (13, 14, 15, 16):
            hv.append(
                dict(
                    case_type="pareto_reference",
                    scenario_id=cell.scenario_id,
                    n_reference=5000,
                    power=p,
                    HV_QMC=0.5 + p / 100,
                    HV_QMC_SE=0.001,
                    relative_se=0.002,
                    relative_change_previous=None if p == 13 else 0.003,
                )
            )
    plots = figures(references, rows, hv, extrema)
    assert len(plots) == 6
    for fig in plots.values():
        for ax in fig.axes:
            assert not any(line.get_visible() for line in ax.get_xgridlines())
            assert not any(line.get_visible() for line in ax.get_ygridlines())
            if hasattr(ax, "zaxis"):
                assert ax._draw_grid is False
