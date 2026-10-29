"""Phase10B: independent experiments, unchanged scientific APIs and lossless RSMs."""

import csv
import json
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from cnbi_v2.model import diagnose_rsm, fit_multivariate_rsm, quadratic_design, quadratic_term_names
from cnbi_v2.synthetic.ccd import full_ccd
from cnbi_v2.synthetic.design import factorial_design
from cnbi_v2.synthetic.model import evaluate
from cnbi_v2.synthetic.noise import experimental_noise, noise_variance, stream_seed
from cnbi_v2.synthetic.rsm_generation import (
    certify_noiseless,
    generate_instance,
    true_coefficients,
    validate_instances,
)
from cnbi_v2.synthetic.rsm_inputs import load_structural_cases, verify_checksums
from cnbi_v2.synthetic.rsm_serialization import export_tables, load_models, write_csv, write_models
from cnbi_v2.synthetic.rsm_validation import (
    covariance_diagnostics,
    external_metrics,
    external_sample,
    hessian_eigenvalues,
    replica_prediction_spread,
)

ROOT = Path(__file__).resolve().parents[2]
STRUCTURAL = ROOT / "results/phase_10_synthetic_generation/structural_20261029"


@pytest.fixture(scope="module")
def cases():
    return load_structural_cases(STRUCTURAL)


@pytest.mark.parametrize(
    "nx,n,p,lof,outside", [(2, 13, 6, 3, 0), (3, 19, 10, 5, 8), (5, 47, 21, 22, 0)]
)
def test_full_rotatable_ccd_counts_order_rank_and_domain(nx, n, p, lof, outside):
    ccd = full_ccd(nx)
    x = ccd.points
    assert x.shape == (n, nx) and ccd.alpha == 2 ** (nx / 4)
    assert ccd.kinds.count("factorial") == 2**nx
    assert ccd.kinds.count("axial") == 2 * nx
    assert ccd.kinds.count("center") == 5
    assert_array_equal(x[: 2**nx], list(product((-1, 1), repeat=nx)))
    assert_array_equal(x[-5:], np.zeros((5, nx)))
    for k in range(nx):
        assert x[2**nx + 2 * k, k] == -ccd.alpha
        assert x[2**nx + 2 * k + 1, k] == ccd.alpha
    assert sum(not v for v in ccd.inside_ball) == outside
    assert all(ccd.kinds[i] == "factorial" for i, v in enumerate(ccd.inside_ball) if not v)
    design = quadratic_design(x)
    assert np.linalg.matrix_rank(design) == p
    fit = fit_multivariate_rsm(x, np.arange(n, dtype=float))
    diag = diagnose_rsm(fit, x).responses[0]
    assert diag.error_df == n - p and diag.pure_error_df == 4 and diag.lack_of_fit_df == lof
    assert not x.flags.writeable


@pytest.mark.parametrize("index", range(27))
def test_all_27_noise_free_coefficients_oracles_and_minima(cases, index):
    cell, a = cases[index]
    b = true_coefficients(a)
    assert b.shape == (len(quadratic_term_names(cell.nx)), cell.m)
    assert_array_equal(np.diag(evaluate(a, a)), np.zeros(cell.m))
    assert_array_equal(b[0], np.sum(a * a, axis=1))
    assert_array_equal(b[1 : 1 + cell.nx], -2 * a.T)
    assert_array_equal(b[1 + cell.nx : 1 + 2 * cell.nx], np.ones((cell.nx, cell.m)))
    assert_array_equal(b[1 + 2 * cell.nx :], np.zeros((cell.nx * (cell.nx - 1) // 2, cell.m)))
    assert_allclose(hessian_eigenvalues(b, cell.nx), 2, atol=0, rtol=0)
    assert certify_noiseless(cell, a)["status"] == "CERTIFIED"


def test_experimental_totals_seeds_and_all_replicas_retained(cases):
    instances = tuple(generate_instance(c, a, r, 42) for c, a in cases for r in range(1, 6))
    validate_instances(instances)
    assert len(instances) == 135
    assert sum(i.fit.n_observations for i in instances) == 3555
    assert sum(i.fit.n_responses for i in instances) == 990
    seeds = {stream_seed(42, c.scenario_id, r) for c, _ in cases for r in range(6)}
    assert len(seeds) == 162
    assert all(i.replica_id in range(1, 6) for i in instances)
    for cell, _ in cases:
        group = [i for i in instances if i.scenario == cell]
        assert len(group) == 5
        for item in group[1:]:
            assert_array_equal(item.ccd.points, group[0].ccd.points)
            assert_array_equal(item.truth, group[0].truth)
            assert_array_equal(item.sigma_squared, group[0].sigma_squared)
            assert not np.array_equal(item.noise, group[0].noise)


def test_noise_expectation_no_clipping_no_recentering_and_independent_centers(cases):
    cell, a = cases[0]
    item = generate_instance(cell, a, 1, 42)
    sf = np.var(item.truth, axis=0, ddof=1)
    assert_array_equal(item.sigma_squared, sf / 19)
    assert_allclose(sf / (sf + item.sigma_squared), 0.95, atol=2e-16, rtol=0)
    expected = np.random.Generator(np.random.PCG64(item.seed)).normal(
        0, np.sqrt(sf / 19), size=item.truth.shape
    )
    assert_array_equal(item.noise, expected)
    assert_array_equal(item.observed, item.truth + expected)
    assert len(np.unique(item.noise[-5:, 0])) == 5
    draws = experimental_noise(np.tile([[0.0], [1.0]], (100000, 1)), 777)
    assert abs(draws.mean()) < 0.002
    assert_allclose(
        draws.var(ddof=1), np.var(np.tile([[0.0], [1.0]], (100000, 1)), ddof=1) / 19, rtol=0.02
    )
    assert np.any(np.tile([[0.0], [1.0]], (100000, 1)) + draws < 0)


def test_reverse_order_and_worker_count_do_not_change_experiments(cases):
    jobs = [(c, a, r) for c, a in cases[::9] for r in range(1, 6)]

    def run(job):
        return generate_instance(*job, master_seed=31415)

    forward = {i.instance_id: i for i in map(run, jobs)}
    with ThreadPoolExecutor(max_workers=3) as pool:
        reverse = tuple(pool.map(run, reversed(jobs)))
    for item in reverse:
        assert_array_equal(item.observed, forward[item.instance_id].observed)
        assert_array_equal(item.fit.coefficients, forward[item.instance_id].fit.coefficients)


def test_fits_diagnostics_loocv_and_raw_covariance_use_existing_apis(cases):
    cell, a = cases[6]  # nx2,m8,only seven residual df: singular covariance expected
    item = generate_instance(cell, a, 2, 42)
    independent = fit_multivariate_rsm(item.ccd.points, item.observed)
    assert_array_equal(item.fit.coefficients, independent.coefficients)
    diag = diagnose_rsm(independent, item.ccd.points, [f"y{j + 1}" for j in range(cell.m)])
    assert item.diagnostics.responses == diag.responses
    assert_array_equal(item.fit.residual_covariance, item.fit.residuals.T @ item.fit.residuals / 7)
    covariance = covariance_diagnostics(item)
    assert covariance["residual_covariance_rank"] == 7
    assert covariance["residual_covariance_condition"] is None
    assert not covariance["residual_covariance_regularized"]
    for i in range(len(item.ccd.points)):
        keep = np.arange(len(item.ccd.points)) != i
        loo = fit_multivariate_rsm(item.ccd.points[keep], item.observed[keep])
        error = item.observed[i] - loo.predict(item.ccd.points[i])
        assert_allclose(error, item.diagnostics.press_residuals[i], atol=5e-14, rtol=1e-12)


def test_external_validation_is_independent_and_shared_without_refitting(cases):
    cell, a = cases[12]
    first = generate_instance(cell, a, 1, 42)
    before = first.fit.coefficients.copy()
    sample = external_sample(cell, a, 42)
    assert sample.points.shape == (4096, cell.nx)
    assert sample.seed != first.seed
    assert_array_equal(sample.points, external_sample(cell, a, 42).points)
    assert np.all(np.linalg.norm(sample.points, axis=1) <= first.ccd.alpha)
    assert not any(np.any(np.all(sample.points == point, axis=1)) for point in first.ccd.points)
    metric = external_metrics(first.fit.predict(sample.points), sample.truth)
    assert metric.shape == (cell.m, 4)
    assert np.all(metric[:, 0:2] >= 0) and np.all(metric[:, 2] <= 1)
    assert_array_equal(first.fit.coefficients, before)
    perfect = external_metrics(sample.truth, sample.truth)
    assert_array_equal(perfect[:, 0], np.zeros(cell.m))
    assert_array_equal(perfect[:, 2], np.ones(cell.m))
    predictions = [
        generate_instance(cell, a, r, 42).fit.predict(sample.points) for r in range(1, 6)
    ]
    assert replica_prediction_spread(predictions)["replica_prediction_sd_mean"] > 0


def test_export_and_oracle_free_reload_preserve_float64_without_ols(cases, tmp_path, monkeypatch):
    selected = cases[::9]
    instances = tuple(generate_instance(c, a, 1, 42) for c, a in selected)
    anchors = {c.scenario_id: a for c, a in selected}
    samples = {c.scenario_id: external_sample(c, a, 42) for c, a in selected}
    diagnostics, external = export_tables(tmp_path, instances, anchors, samples)
    assert len(diagnostics) == len(external) == sum(i.scenario.m for i in instances)

    def forbidden(*args, **kwargs):
        raise AssertionError("reload must not fit or call an oracle")

    monkeypatch.setattr("cnbi_v2.model.fit_multivariate_rsm", forbidden)
    monkeypatch.setattr("cnbi_v2.synthetic.rsm_generation.fit_multivariate_rsm", forbidden)
    monkeypatch.setattr("cnbi_v2.synthetic.rsm_generation.evaluate", forbidden)
    models = load_models(tmp_path)
    for item in instances:
        loaded = models[item.instance_id]
        assert_array_equal(loaded.coefficients, item.fit.coefficients)
        assert_array_equal(loaded.predict(item.ccd.points), item.fit.fitted_values)
        assert not hasattr(loaded, "truth") and not hasattr(loaded, "anchors")
    with (tmp_path / "synthetic_rsm_coefficients.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    for item in instances:
        for j in range(item.scenario.m):
            column = [
                float(r["coefficient"])
                for r in rows
                if r["instance_id"] == item.instance_id and r["response_id"] == f"y{j + 1}"
            ]
            assert_array_equal(column, item.fit.coefficients[:, j])
    with pytest.raises(ValueError):
        loaded.predict([[0]])


@pytest.mark.parametrize(
    "values", [np.ones((5, 2)), [[1]], [[1, np.nan], [2, 3]], [[1, np.inf], [2, 3]], [], [1, 2]]
)
def test_invalid_signal_variance_rejected(values):
    with pytest.raises((ValueError, FloatingPointError)):
        noise_variance(values)


@pytest.mark.parametrize(
    "master,sid,r",
    [
        (-1, "nx2_delta1_rho025", 1),
        (True, "nx2_delta1_rho025", 1),
        (1, "missing", 1),
        (1, "nx2_delta1_rho025", 6),
        (1, "nx2_delta1_rho025", 1.0),
        (1, "nx2_delta1_rho025", True),
    ],
)
def test_invalid_stream_identification(master, sid, r):
    with pytest.raises(ValueError):
        stream_seed(master, sid, r)


def test_invalid_arrays_rank_and_duplicate_instances(cases):
    c, a = cases[0]
    for bad in (np.zeros((1, 1)), [[np.nan]], []):
        with pytest.raises(ValueError):
            generate_instance(c, bad, 1, 42)
    for replica in (0, 6, True):
        with pytest.raises(ValueError):
            generate_instance(c, a, replica, 42)
    with pytest.raises(ValueError, match="rank deficient"):
        fit_multivariate_rsm(np.zeros((13, 2)), np.ones((13, 2)))
    item = generate_instance(c, a, 1, 42)
    for invalid in ((), (item, item)):
        with pytest.raises(ValueError):
            validate_instances(invalid)
    with pytest.raises(ValueError):
        experimental_noise([[1], [2]], -1)
    with pytest.raises(ValueError):
        true_coefficients([1, 2])
    with pytest.raises(ValueError):
        hessian_eigenvalues([[1]], 2)
    with pytest.raises(ValueError):
        external_metrics([[1]], [[1]])
    with pytest.raises(ValueError):
        external_metrics([[1, 2]], [[1]])
    with pytest.raises(ValueError):
        replica_prediction_spread(np.zeros((4, 2, 2)))
    with pytest.raises(ValueError):
        external_sample(c, np.zeros((1, 2)), 42)
    with pytest.raises(ValueError):
        write_csv(Path("unused"), [])


def test_incomplete_checksums_and_corrupted_models_rejected(cases, tmp_path):
    with pytest.raises(FileNotFoundError):
        verify_checksums(tmp_path)
    manifest = tmp_path / "checksums.sha256"
    manifest.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        verify_checksums(tmp_path)
    manifest.write_text("0" * 64 + "  checksums.sha256\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mismatch"):
        verify_checksums(tmp_path)
    c, a = cases[0]
    item = generate_instance(c, a, 1, 42)
    write_models(tmp_path, (item,))
    index_path = tmp_path / "models_index.json"
    original = index_path.read_text(encoding="utf-8")
    for edit in ("id", "duplicate", "shape", "terms", "coefficients", "empty", "checksum"):
        meta = json.loads(original)
        if edit == "id":
            meta["models"][0]["instance_id"] = ""
        if edit == "duplicate":
            meta["models"] *= 2
        if edit == "shape":
            meta["models"][0]["m"] += 1
        if edit == "terms":
            meta["models"][0]["term_names"] = ["wrong"]
        if edit == "coefficients":
            meta["models"][0]["coefficients_sha256"] = "0" * 64
        if edit == "empty":
            meta["models"] = []
        if edit == "checksum":
            meta["models_sha256"] = "0" * 64
        index_path.write_text(json.dumps(meta), encoding="utf-8")
        with pytest.raises(ValueError):
            load_models(tmp_path)


def test_expected_design_counts_independently_of_fits():
    cells = factorial_design()
    assert len(cells) == 27
    assert sum(5 * (2**c.nx + 2 * c.nx + 5) for c in cells) == 3555
    assert sum(5 * c.m for c in cells) == 990


def test_predefined_diagnostic_figures_have_no_grids(cases, tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/validation"))
    from synthetic_rsm_diagnostics import figures

    selected = [cases[k] for k in (4, 13, 22)]
    instances = tuple(generate_instance(c, a, 1, 42) for c, a in selected)
    anchors = {c.scenario_id: a for c, a in selected}
    samples = {c.scenario_id: external_sample(c, a, 42) for c, a in selected}
    diagnostics, external = export_tables(tmp_path, instances, anchors, samples)
    plots = figures(instances, anchors, samples, diagnostics, external)
    assert len(plots) == 6
    for fig in plots.values():
        for ax in fig.axes:
            assert not any(line.get_visible() for line in ax.get_xgridlines())
            assert not any(line.get_visible() for line in ax.get_ygridlines())


@pytest.mark.parametrize("defect", ["status", "ids", "metadata", "anchors"])
def test_structural_input_validation_rejects_invalid_archive(defect, tmp_path):
    import hashlib
    import shutil

    for name in (
        "calibration_manifest.json",
        "synthetic_scenarios.csv",
        "synthetic_anchors.csv",
        "synthetic_correlation_matrices.npz",
    ):
        shutil.copyfile(STRUCTURAL / name, tmp_path / name)
    if defect == "status":
        path = tmp_path / "calibration_manifest.json"
        meta = json.loads(path.read_text(encoding="utf-8"))
        meta["status"] = "FAILED"
        path.write_text(json.dumps(meta), encoding="utf-8")
    if defect in ("ids", "metadata"):
        path = tmp_path / "synthetic_scenarios.csv"
        text = path.read_text(encoding="utf-8")
        if defect == "ids":
            text = text.replace("nx2_delta1_rho025", "missing")
        else:
            text = text.replace(",MIN,1,True", ",MAX,1,True")
        path.write_text(text, encoding="utf-8")
    if defect == "anchors":
        path = tmp_path / "synthetic_anchors.csv"
        rows = path.read_text(encoding="utf-8").splitlines()
        rows[1] = rows[1].rsplit(",", 1)[0] + ",999"
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    paths = sorted(tmp_path.iterdir())
    (tmp_path / "checksums.sha256").write_text(
        "".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n" for p in paths),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_structural_cases(tmp_path)
