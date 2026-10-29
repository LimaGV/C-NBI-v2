"""Visualization contracts: source identity,geometry,language and deterministic export."""

import ast
import json

import numpy as np
import pandas as pd
import pytest
from matplotlib import pyplot as plt
from numpy.testing import assert_allclose, assert_array_equal
from scripts.visualization.annotations import NOTES, caption, question
from scripts.visualization.generate_applied_case_figures import (
    export,
    render,
    scientific_artist_hash,
)
from scripts.visualization.sources import COR, OUTPUT, P2, P3, P4, ROOT, prepare, read_table
from scripts.visualization.style import (
    DIRECTIONS,
    FIGURES,
    PALETTE,
    RESPONSES,
    TEXT,
    method_label,
    tr,
)
from scripts.visualization.transforms import ellipse_parameters, project

from cnbi_v2.data import sha256_file


@pytest.fixture(scope="module")
def prepared(tmp_path_factory):
    output = tmp_path_factory.mktemp("visual_sources")
    tables, audit, dependencies, reader = prepare(output)
    yield output, tables, audit, dependencies, reader
    reader.verify_unchanged()


def test_complete_translation_palette_and_orders():
    assert len(FIGURES) == 46
    assert sum(value[2] == "main" for value in FIGURES.values()) == 21
    assert tuple(RESPONSES) == ("T", "MTTF", "WR", "Ra", "Rt", "Kp", "ROI", "OEE")
    assert DIRECTIONS == ("MAX", "MAX", "MIN", "MIN", "MIN", "MIN", "MAX", "MAX")
    for key, pair in TEXT.items():
        assert len(pair) == 2 and all(isinstance(x, str) and x.strip() for x in pair)
        assert tr(key, "pt") == pair[0] and tr(key, "en") == pair[1]
    for identifier, definition in FIGURES.items():
        assert all(definition[:2]) and question(identifier).endswith("?")
        for lang in ("pt", "en"):
            assert caption(identifier, lang)
            assert method_label("VRF", lang) == "VRF-NBI"
            assert "VRF histórico" not in caption(identifier, lang)
            assert "historical VRF" not in caption(identifier, lang)
            assert "Historical VRF" not in caption(identifier, lang)
    assert len(NOTES) == 38
    assert {
        key: PALETTE[key] for key in ("Reference", "CNBI5", "VRF", "NSGA3", "MOEAD", "Anchor")
    } == dict(
        Reference="#D0D0D0",
        CNBI5="#E69F00",
        VRF="#0072B2",
        NSGA3="#009E73",
        MOEAD="#CC3311",
        Anchor="#AA4499",
    )


def test_identity_and_payoff_transposition(prepared):
    _, t, audit, _, reader = prepared
    assert len(t["anchors"]) == 8 and len(t["subsets"]) == 37
    assert t["subsets"].k.value_counts().to_dict() == {2: 19, 3: 18}
    assert len(t["fronts"][t["fronts"].method == "CNBI5"]) == 409
    assert len(t["fronts"][t["fronts"].method == "Reference"]) == 18503
    assert audit["reference_CNBI_origins"] == 0
    assert audit["coding"]["coded_factor_order"] == ["Vc", "f", "ap"]
    saved = reader.csv(P2 + "payoff_sphere.csv")[list(RESPONSES)].to_numpy()
    shown = (
        t["payoff"]
        .pivot(index="anchor", columns="response", values="natural")
        .reindex(index=RESPONSES, columns=RESPONSES)
        .to_numpy()
    )
    assert_array_equal(shown, saved.T)
    cnbi = reader.npz(COR + "official_cnbi5.npz")
    assert_array_equal(
        t["fronts"].query("method=='CNBI5'")[["x1", "x2", "x3"]].to_numpy(), cnbi["x"]
    )
    assert (
        audit["visual_performance"]["purpose"]
        == "display only; official normalization/metrics unchanged"
    )


def test_stored_curve_values_and_visual_slice_no_refit(prepared):
    _, t, _, _, reader = prepared
    pd.testing.assert_frame_equal(
        t["cardinality"],
        reader.csv(COR + "cardinality_curve_metrics.csv"),
        check_dtype=False,
        check_exact=True,
    )
    frame = t["contours"]
    center = frame[(abs(frame.x1) < 1e-14) & (abs(frame.x2) < 1e-14)]
    assert len(center) == 1
    b = reader.csv(P2 + "coded_models.csv")[list(RESPONSES)].to_numpy()
    assert_allclose(center[list(RESPONSES)].to_numpy()[0], b[0], atol=1e-14, rtol=0)
    assert frame.loc[~frame.inside_domain, list(RESPONSES)].isna().all().all()
    cov = np.load(ROOT / (P3 + "theoretical_covariance.npy"), allow_pickle=False)
    expected = np.sqrt(np.diag(cov)).reshape(10, 8, order="F")
    shown = t["coefficients"].pivot(index="term_index", columns="response", values="SE")
    assert_allclose(shown[list(RESPONSES)], expected, atol=0, rtol=1e-14)


def test_ellipse_formula_and_mc_audit(prepared):
    _, t, audit, _, _ = prepared
    assert len(t["ellipses"]) == 42
    assert (t["ellipses"].n == 2000).all()
    assert (t["ellipses"].covariance_estimator == "sample covariance ddof1").all()
    assert (t["ellipses"].probability == 0.95).all()
    assert_allclose(t["ellipses"].chi2_quantile, -2 * np.log(0.05), atol=1e-13, rtol=0)
    cloud = t["mc_responses"].query("anchor=='T'")[["T", "Kp"]].to_numpy()
    expected = ellipse_parameters(cloud)
    row = t["ellipses"].query("figure=='C4' and projection=='T|Kp' and anchor=='T'").iloc[0]
    for key in (
        "center_x",
        "center_y",
        "width",
        "height",
        "covariance_xx",
        "covariance_xy",
        "covariance_yy",
    ):
        assert_allclose(row[key], expected[key], atol=1e-14, rtol=1e-14)
    assert audit["ellipse_source"] == P4 + "payoff_samples.npz"
    assert "not exact" in audit["ellipse_definition"]


def test_pca_one_shared_basis_and_visual_performance(prepared):
    _, t, audit, _, _ = prepared
    ref = t["fronts"].query("method=='Reference'")
    z = ref[["z_" + r for r in RESPONSES]].to_numpy()
    pca = audit["pca"]
    assert pca["n"] == 18503
    assert_allclose(project(z, pca), ref[["PC1", "PC2"]], atol=1e-14, rtol=1e-14)
    assert_allclose(
        np.array(pca["components"]).T @ np.array(pca["components"]), np.eye(2), atol=1e-14
    )
    assert abs(sum(pca["explained_variance_ratio"]) - 1) < 1e-14
    for component in np.array(pca["components"]).T:
        assert component[np.argmax(abs(component))] > 0
    performance = t["fronts"][["performance_" + r for r in RESPONSES]].to_numpy()
    assert performance.min() >= 0 and performance.max() <= 1


@pytest.mark.parametrize("identifier", list(FIGURES))
def test_every_figure_same_scientific_geometry_in_both_languages(identifier, prepared):
    _, tables, audit, _, _ = prepared
    signatures = []
    for lang in ("pt", "en"):
        fig, _ = render(identifier, tables, audit, lang)
        signatures.append(scientific_artist_hash(fig))
        assert all(
            not line.get_visible()
            for ax in fig.axes
            for line in [*ax.get_xgridlines(), *ax.get_ygridlines()]
        )
        if identifier.startswith("D1"):
            labels = [tick.get_text() for tick in fig.axes[0].get_xticklabels()]
            assert [label.split()[0] for label in labels] == list(RESPONSES)
            assert [label.split()[-1] for label in labels] == [
                "↑" if d == "MAX" else "↓" for d in DIRECTIONS
            ]
        if identifier == "C2":
            data = tables["coefficients"].query("term_index>0")
            values = data.pivot(index="response", columns="term_index", values="beta_over_SE")
            assert [text.get_text() for text in fig.axes[0].texts] == [
                f"{value:+.1f}" for value in values.reindex(RESPONSES).to_numpy().flat
            ]
        plt.close(fig)
    assert signatures[0] == signatures[1]


def test_export_deterministic_all_formats(prepared, tmp_path):
    _, tables, audit, _, _ = prepared
    hashes = []
    for number in (1, 2):
        fig, _ = render("A2", tables, audit, "en")
        files = export(fig, tmp_path / str(number), "A2", "en", ("png", "pdf", "svg"), 120)
        hashes.append([sha256_file(path) for path in files])
        plt.close(fig)
    assert hashes[0] == hashes[1]


def test_plot_sources_never_execute_scientific_pipelines():
    forbidden = {
        "fit_multivariate_rsm",
        "minimize",
        "solve_nbi_lattice",
        "run_evolutionary",
        "mc_prefix_sensitivity",
        "gd_igd",
        "spacing_sparsity",
    }
    for path in (ROOT / "scripts/visualization").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = (
                    node.func.id
                    if isinstance(node.func, ast.Name)
                    else getattr(node.func, "attr", "")
                )
                assert name not in forbidden, (path, name)


def test_csv_literals_round_trip_without_deprecated_float_inference():
    literals = ["0.03949173421958787", "-2.0103456789012345e-23", "1.681792830507429"]
    payload = (
        "id,value,flag\n" + "".join(f"{i},{v},True\n" for i, v in enumerate(literals))
    ).encode()
    frame = read_table(payload)
    assert [v.hex() for v in frame.value] == [float(s).hex() for s in literals]
    csv_bytes = frame.to_csv(index=False, float_format="%.17g", lineterminator="\n").encode()
    repeated = read_table(csv_bytes)
    assert_array_equal(frame.value, repeated.value)
    assert frame.flag.all()


def test_published_visual_archive():
    meta = json.loads((OUTPUT / "metadata.json").read_text(encoding="utf-8"))
    assert meta["status"] == "COMPLETE" and meta["png_dpi"] == 600
    assert meta["figures"] == 46 and meta["variants"] == 92 and meta["exports"] == 274
    assert meta["source_artifacts_unchanged"] and meta["working_tree_dirty_at_start"] is False
    assert not meta["render_warnings"]
    catalog = pd.read_csv(OUTPUT / "figure_catalog.csv")
    for _, row in catalog.iterrows():
        for language in ("pt", "en"):
            files = json.loads(row["output_" + language])
            assert len(files) == (2 if row.figure_id == "D3" else 3)
            for name in files:
                assert (OUTPUT / name).is_file()
            pdf = next(name for name in files if name.endswith(".pdf"))
            assert b"/Subtype /Image" not in (OUTPUT / pdf).read_bytes()
    for line in (OUTPUT / "checksums.sha256").read_text().splitlines():
        digest, name = line.split("  ")
        assert sha256_file(OUTPUT / name) == digest
    sources = json.loads((OUTPUT / "source_artifacts.json").read_text(encoding="utf-8"))
    for name, info in sources.items():
        assert sha256_file(ROOT / name) == info["sha256"]
