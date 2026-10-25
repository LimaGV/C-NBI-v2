"""Read frozen Git identities, prepare auditable plot tables, never run solvers."""

import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import norm

from cnbi_v2.data import sha256_file

from .style import DIRECTIONS, RESPONSES, TERMS
from .transforms import ellipse_parameters, evaluate_visual_slice, pca_projection, project

ROOT = Path(__file__).resolve().parents[2]
BASE = "d938695b7fdaf9c871d331a42ff277e0c3fbd2d1"
RUN_ID = "turning_visuals_20261025"
OUTPUT = ROOT / "results/applied_case_visualizations" / RUN_ID
P2 = "results/phase_02_anchors/turning_original_codes_20261024/"
P3 = "results/phase_03_coefficient_mc/turning_original_codes_mc_777_20261024/"
P4 = "results/phase_04_anchor_mc/turning_original_codes_anchor_mc_777_20261024/"
P5 = "results/phase_05_chim_pa/turning_fixed_nominal_chim_pa_777_20261024/"
GAP = "results/phase_05_chim_pa/turning_spectral_gap_policy_v2_20261024/"
P6 = "results/phase_06_local_nbi/turning_local_nbi_h20_20261024/"
P7 = "results/phase_07_reference_front/turning_multifamily_loo_20261024/"
P8 = "results/phase_08_final_benchmark/turning_reference_sensitivity_20261024/"
COR = "results/phase_08_final_benchmark/turning_standalone_correction_20261025/"


def read_table(payload):
    """Parse literals by Python conversion, without changing CSV bytes.

    Blank cells stay missing,boolean tokens stay boolean,integer literals stay
    integers,and decimals/exponents use float(). No deprecated parser option.
    """
    source = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    frame = pd.DataFrame(list(source), columns=source.fieldnames)
    for name in frame.columns:
        strings = list(frame[name])
        present = [v for v in strings if v != ""]
        if not present:
            frame[name] = np.full(len(strings), np.nan)
            continue
        if set(present) <= {"True", "False"}:
            frame[name] = [v == "True" if v else np.nan for v in strings]
            continue
        try:
            integer = all(v.strip().lstrip("+-").isdigit() for v in present) and len(
                present
            ) == len(strings)
            values = [int(v) if integer else float(v) if v else np.nan for v in strings]
        except ValueError:
            values = [v if v else np.nan for v in strings]
        frame[name] = values
    return frame


class FrozenReader:
    def __init__(self):
        self.sources = {}

    def read(self, name):
        path = (ROOT / name).resolve()
        path.relative_to(ROOT)
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if name not in self.sources:
            blob = subprocess.check_output(["git", "cat-file", "blob", f"{BASE}:{name}"], cwd=ROOT)
            if hashlib.sha256(blob).hexdigest() != digest:
                raise ValueError(f"frozen input differs from scientific base: {name}")
            self.sources[name] = dict(sha256=digest, bytes=len(payload), git_commit=BASE)
        return payload

    def csv(self, name):
        return read_table(self.read(name))

    def npz(self, name):
        with np.load(io.BytesIO(self.read(name)), allow_pickle=False) as d:
            return {k: d[k] for k in d.files}

    def json(self, name):
        return json.loads(self.read(name))

    def verify_unchanged(self):
        for name, info in self.sources.items():
            if sha256_file(ROOT / name) != info["sha256"]:
                raise ValueError(f"source mutated during visualization: {name}")


def prepare(output):
    reader = FrozenReader()
    tables = {}
    dependencies = {}

    def add(name, frame, sources):
        tables[name] = pd.DataFrame(frame)
        dependencies[name] = list(sources)

    # Read all normalization and response identities from preserved artifacts.
    coding = reader.json("data/metadata/turning_application/phase_02_coding.json")
    reader.read("data/metadata/turning_application/variables.yaml")
    norm_table = reader.csv(P5 + "nominal_normalization.csv")
    if list(norm_table.response) != list(RESPONSES) or tuple(norm_table.direction) != DIRECTIONS:
        raise ValueError("response order/directions changed")
    u, amp, sign = (
        norm_table.utopia.to_numpy(),
        norm_table.amplitude.to_numpy(),
        norm_table.sign.to_numpy(),
    )
    anchor_table = reader.csv(P2 + "anchors_sphere.csv")
    anchors = anchor_table[["x1", "x2", "x3"]].to_numpy()
    if anchors.shape != (8, 3):
        raise ValueError("eight three-factor nominal anchors are required")
    coefficients = reader.csv(P2 + "coded_models.csv")[list(RESPONSES)].to_numpy()
    payoff = reader.csv(P2 + "payoff_sphere.csv")[list(RESPONSES)].to_numpy()
    normalized = reader.npz(P5 + "nominal_chim.npz")["normalized"]
    if not np.array_equal((sign[:, None] * payoff - u[:, None]) / amp[:, None], normalized):
        raise ValueError("nominal payoff normalization changed")
    # Rows displayed are anchor optima, columns are attained responses.
    add(
        "payoff",
        [
            dict(anchor=r, response=s, loss=float(normalized[j, i]), natural=float(payoff[j, i]))
            for i, r in enumerate(RESPONSES)
            for j, s in enumerate(RESPONSES)
        ],
        [P2 + "payoff_sphere.csv", P5 + "nominal_chim.npz", P5 + "nominal_normalization.csv"],
    )
    add(
        "conflict",
        [
            dict(anchor=r, response=s, asymmetry=float(normalized[j, i] - normalized[i, j]))
            for i, r in enumerate(RESPONSES)
            for j, s in enumerate(RESPONSES)
        ],
        dependencies["payoff"],
    )
    x1, x2, inside, values = evaluate_visual_slice(coefficients, coding["sphere_radius"])
    add(
        "contours",
        dict(
            x1=x1.ravel(),
            x2=x2.ravel(),
            x3=0.0,
            inside_domain=inside.ravel(),
            **{r: values[:, :, j].ravel() for j, r in enumerate(RESPONSES)},
        ),
        [P2 + "coded_models.csv", "data/metadata/turning_application/phase_02_coding.json"],
    )
    add("anchors", anchor_table, [P2 + "anchors_sphere.csv"])
    selected = reader.csv(P5 + "selected_subsets_B2000.csv")
    selected = selected.sort_values(
        "subset_id", key=lambda c: c.map(lambda s: tuple(map(int, s.split("_")[1:])))
    )
    selected = selected.sort_values("k", kind="stable").reset_index(drop=True)
    if len(selected) != 37 or dict(selected.k.value_counts()) != {2: 19, 3: 18}:
        raise ValueError("selected subset identities changed")
    incidence = np.array([[int(r in s.split("|")) for r in RESPONSES] for s in selected.responses])
    add(
        "subsets",
        dict(
            subset=selected.subset_id,
            k=selected.k,
            **dict(zip(RESPONSES, incidence.T, strict=True)),
        ),
        [P5 + "selected_subsets_B2000.csv"],
    )
    co = incidence.T @ incidence
    add(
        "cooccurrence",
        [
            dict(
                response1=r,
                response2=s,
                cooccurrence=int(co[i, j]),
                frequency1=int(co[i, i]),
                frequency2=int(co[j, j]),
            )
            for i, r in enumerate(RESPONSES)
            for j, s in enumerate(RESPONSES)
            if i < j
        ],
        dependencies["subsets"],
    )
    add("pa", reader.csv(P5 + "global_pa_B2000.csv"), [P5 + "global_pa_B2000.csv"])
    covariance = np.load(
        io.BytesIO(reader.read(P3 + "theoretical_covariance.npy")), allow_pickle=False
    )
    se = np.sqrt(np.diag(covariance)).reshape((10, 8), order="F")
    z95 = float(norm.ppf(0.975))
    add(
        "coefficients",
        [
            dict(
                response=r,
                term=term,
                term_index=i,
                beta=coefficients[i, j],
                SE=se[i, j],
                lower=coefficients[i, j] - z95 * se[i, j],
                upper=coefficients[i, j] + z95 * se[i, j],
                beta_over_SE=coefficients[i, j] / se[i, j],
                z_quantile=z95,
            )
            for j, r in enumerate(RESPONSES)
            for i, term in enumerate(TERMS)
        ],
        [P2 + "coded_models.csv", P3 + "theoretical_covariance.npy"],
    )
    mc = reader.npz(P4 + "anchor_samples.npz")
    pmc = reader.npz(P4 + "payoff_samples.npz")
    if (
        mc["anchors"].shape != (2000, 8, 3)
        or not mc["valid_anchors"].all()
        or not pmc["valid_payoffs"].all()
    ):
        raise ValueError("MC eligibility or sample count changed")
    add(
        "mc_decision",
        [
            dict(
                sample=b,
                anchor=r,
                **dict(zip(("x1", "x2", "x3"), mc["anchors"][b, j], strict=True)),
            )
            for j, r in enumerate(RESPONSES)
            for b in range(2000)
        ],
        [P4 + "anchor_samples.npz"],
    )
    add(
        "mc_responses",
        [
            dict(sample=b, anchor=r, **dict(zip(RESPONSES, pmc["payoffs"][b, :, j], strict=True)))
            for j, r in enumerate(RESPONSES)
            for b in range(2000)
        ],
        [P4 + "payoff_samples.npz"],
    )
    zn = (pmc["payoffs"] * sign[None, :, None] - u[None, :, None]) / amp[None, :, None]
    mean, width = zn.mean(axis=0), np.quantile(zn, 0.95, axis=0) - np.quantile(zn, 0.05, axis=0)
    add(
        "payoff_uncertainty",
        [
            dict(anchor=r, response=s, mean=float(mean[j, i]), q95_q05=float(width[j, i]))
            for i, r in enumerate(RESPONSES)
            for j, s in enumerate(RESPONSES)
        ],
        [P4 + "payoff_samples.npz", P5 + "nominal_normalization.csv"],
    )
    add(
        "coefficient_stability",
        reader.csv(P3 + "mc_prefix_sensitivity.csv"),
        [P3 + "mc_prefix_sensitivity.csv"],
    )
    add(
        "spectral_gaps",
        reader.csv(GAP + "global_spectral_gap_trajectory.csv"),
        [GAP + "global_spectral_gap_trajectory.csv"],
    )
    stop = reader.json(GAP + "early_stop_validation.json")
    add("early_stop", stop["trajectory"], [GAP + "early_stop_validation.json"])
    if stop["first_B_stop"] != 1300:
        raise ValueError("frozen retrospective early stop changed")
    # Current official baseline always comes directly from the standalone archive.
    official = reader.npz(COR + "official_cnbi5.npz")
    raw = reader.npz(COR + "H5_rep1.npz")
    canonical = reader.npz(P8 + "canonical_candidates.npz")
    reference = reader.npz(P8 + "reference_final.npz")
    provenance = reader.csv(P8 + "provenance.csv")
    if len(official["x"]) != 409 or len(raw["x"]) != 492 or not raw["accepted"].all():
        raise ValueError("official standalone H5 identity changed")
    if len(reference["x"]) != 18503 or reference["point_ids"].max() >= 19866:
        raise ValueError("independent reference membership changed")
    if (
        not np.array_equal(provenance.point_id.to_numpy(), np.arange(len(canonical["x"])))
        or (provenance.iloc[reference["point_ids"]].family == "CNBI").any()
    ):
        raise ValueError("CNBI provenance in independent reference")
    native = reader.csv(COR + "native_metrics.csv")
    ordering = reader.npz(P8 + "candidate_farthest_orderings.npz")
    representatives = {}
    groups = [
        (
            "Reference",
            reference["x"],
            canonical["natural_f"][reference["point_ids"]],
            reference["z"],
            0,
        ),
        ("CNBI5", official["x"], official["natural_f"], official["z"], 0),
    ]
    for family in ("NSGA3", "MOEAD"):
        rows = native[(native.method == family) & (native.label == "HISTORICAL_COMMON_H20_TARGET")]
        chosen = rows.sort_values(["IGD", "seed"], kind="stable").iloc[0]
        seed = int(chosen.seed)
        ids = ordering[f"{family}_seed{seed}"]
        representatives[family] = dict(
            seed=seed,
            stored_IGD=float(chosen.IGD),
            rule=(
                "minimum frozen native IGD on historical common target; smallest seed on exact tie"
            ),
            use="display representative only; no new run or metric",
        )
        groups.append(
            (family, canonical["x"][ids], canonical["natural_f"][ids], canonical["z"][ids], seed)
        )
    ids = ordering["VRF_seed0"]
    groups.append(("VRF", canonical["x"][ids], canonical["natural_f"][ids], canonical["z"][ids], 0))
    pca = pca_projection(reference["z"])
    lo = np.minimum(canonical["z"].min(axis=0), official["z"].min(axis=0))
    hi = np.maximum(canonical["z"].max(axis=0), official["z"].max(axis=0))
    fronts = []
    for family, x, f, z, seed in groups:
        pc = project(z, pca)
        for j in range(len(x)):
            fronts.append(
                dict(
                    method=family,
                    seed=seed,
                    point_id=j,
                    **dict(zip(("x1", "x2", "x3"), x[j], strict=True)),
                    **dict(zip(RESPONSES, f[j], strict=True)),
                    **{f"z_{r}": z[j, k] for k, r in enumerate(RESPONSES)},
                    **{
                        f"performance_{r}": (hi[k] - z[j, k]) / (hi[k] - lo[k])
                        for k, r in enumerate(RESPONSES)
                    },
                    PC1=pc[j, 0],
                    PC2=pc[j, 1],
                )
            )
    front_sources = [
        COR + "official_cnbi5.npz",
        COR + "native_metrics.csv",
        P8 + "canonical_candidates.npz",
        P8 + "candidate_farthest_orderings.npz",
        P8 + "reference_final.npz",
        P8 + "provenance.csv",
    ]
    add("fronts", fronts, front_sources)
    apc = project(normalized.T, pca)
    add(
        "anchor_pca",
        dict(response=RESPONSES, PC1=apc[:, 0], PC2=apc[:, 1]),
        [P5 + "nominal_chim.npz", P8 + "reference_final.npz"],
    )
    k = 15
    ref_pc = project(reference["z"], pca)
    distances = cKDTree(ref_pc).query(ref_pc, k=k + 1, workers=1)[0][:, -1]
    add(
        "pca_density",
        dict(
            PC1=ref_pc[:, 0], PC2=ref_pc[:, 1], log1p_density=np.log1p(k / (np.pi * distances**2))
        ),
        [P8 + "reference_final.npz"],
    )
    nn = []
    for name, ids in ordering.items():
        method, seed = name.split("_seed")
        if method == "CNBI5":
            continue  # Never use the historical408 points, including diagnostics.
        points = canonical["z"][ids]
        d = cKDTree(points).query(points, k=2, eps=0.0, workers=1)[0][:, 1]
        nn.extend(
            dict(method=method, seed=int(seed), point_id=int(i), distance=float(v), N=len(ids))
            for i, v in zip(ids, d, strict=True)
        )
    d = cKDTree(official["z"]).query(official["z"], k=2, eps=0.0, workers=1)[0][:, 1]
    nn.extend(
        dict(method="CNBI5", seed=0, point_id=i, distance=float(v), N=409) for i, v in enumerate(d)
    )
    add("nearest_neighbor", nn, [*front_sources, COR + "official_cnbi5.npz"])
    # Reuse original coefficient/model fitting, optimization and metric tables.
    for name, path in (
        ("cardinality", COR + "cardinality_curve_metrics.csv"),
        ("cost_ea", COR + "cost_quality_ea_preserved.csv"),
        ("cost_cnbi", COR + "cost_quality_cnbi.csv"),
        ("timing_cnbi", COR + "timing_cnbi.csv"),
        ("reference_replicates", COR + "reference_run_sensitivity_replicates.csv"),
        ("reference_cardinality", COR + "reference_cardinality_sensitivity.csv"),
        ("reference_composition", COR + "reference_composition_sensitivity.csv"),
        ("contributions", P7 + "reference_contributions.csv"),
    ):
        add(name, reader.csv(path), [path])
    for family in ("nsga3", "moead"):
        add(
            "timing_" + family,
            reader.csv(P8 + f"timing_{family}.csv"),
            [P8 + f"timing_{family}.csv"],
        )
    cost = tables["cost_cnbi"]
    central = (
        cost[cost.label == "LEAVE_ONE_FAMILY_OUT"]
        .groupby("H", sort=True)
        .agg(T_total=("T_total", "median"), IGD=("IGD", "first"), HV=("HV", "first"))
        .reset_index()
    )
    add(
        "marginal_gain",
        [
            dict(
                H_from=int(central.H[i]),
                H_to=int(central.H[i + 1]),
                delta_time=central.T_total[i + 1] - central.T_total[i],
                IGD_reduction_per_second=(central.IGD[i] - central.IGD[i + 1])
                / (central.T_total[i + 1] - central.T_total[i]),
                HV_gain_per_second=(central.HV[i + 1] - central.HV[i])
                / (central.T_total[i + 1] - central.T_total[i]),
            )
            for i in range(4)
        ],
        [COR + "cost_quality_cnbi.csv"],
    )
    # Local geometry is unchanged nominal evidence; only standalone H5 solutions
    # enter the local panels. Ignore the historical H20 processing_order field.
    geometries = reader.json(P6 + "local_geometry.json")
    catalog = reader.csv(P5 + "selected_subsets_B2000.csv")
    ids = []
    for size in (2, 3):
        group = selected[selected.k == size]
        ids.extend([group.iloc[0].subset_id, group.iloc[-1].subset_id])
    local = []
    local_mc = []
    ellipse_rows = []
    local_definitions = {}
    for name in ids:
        g = next(g for g in geometries if g["subset_id"] == name)
        indices = g["indices"]
        vertices = np.array(g["vertices"])
        center = vertices.mean(axis=1)
        if len(indices) == 2:
            basis = np.eye(2)
            origin = np.zeros(2)
        else:
            basis = np.linalg.svd(vertices - center[:, None], full_matrices=False)[0][:, :2]
            for col in basis.T:
                if col[np.argmax(abs(col))] < 0:
                    col *= -1
            origin = center
        local_definitions[name] = dict(
            basis=basis.tolist(),
            origin=origin.tolist(),
            normal=g["normal"],
            normal_in_projection=(np.array(g["normal"]) @ basis).tolist(),
            indices=indices,
        )
        subset_index = int(catalog.index[catalog.subset_id == name][0])
        rows = np.flatnonzero(raw["subsets"] == subset_index)
        beta = raw["compositions"][rows, : len(indices)] / 5
        norm_f = (raw["natural_f"][rows][:, indices] * sign[indices] - g["utopia"]) / g[
            "amplitudes"
        ]
        weights = beta @ vertices.T
        for kind, points in (("anchor", vertices.T), ("weight", weights), ("solution", norm_f)):
            xy = (points - origin) @ basis
            for j, p in enumerate(xy):
                local.append(
                    dict(
                        subset=name,
                        k=len(indices),
                        kind=kind,
                        index=j,
                        u=p[0],
                        v=p[1],
                        t=raw["t"][rows[j]] if kind == "solution" else np.nan,
                        response=RESPONSES[indices[j]] if kind == "anchor" else "",
                    )
                )
        for index in indices:
            cloud = (pmc["payoffs"][:, indices, index] * sign[indices] - g["utopia"]) / g[
                "amplitudes"
            ]
            xy = (cloud - origin) @ basis
            local_mc.extend(
                dict(subset=name, anchor=RESPONSES[index], sample=b, u=p[0], v=p[1])
                for b, p in enumerate(xy)
            )
            ellipse_rows.append(
                dict(
                    figure="C5", projection=name, anchor=RESPONSES[index], **ellipse_parameters(xy)
                )
            )
    for r1, r2 in (("T", "Kp"), ("Ra", "ROI"), ("WR", "OEE"), ("MTTF", "Rt")):
        i1, i2 = RESPONSES.index(r1), RESPONSES.index(r2)
        for j, anchor in enumerate(RESPONSES):
            ellipse_rows.append(
                dict(
                    figure="C4",
                    projection=f"{r1}|{r2}",
                    anchor=anchor,
                    **ellipse_parameters(pmc["payoffs"][:, [i1, i2], j]),
                )
            )
    add(
        "local_geometry",
        local,
        [P6 + "local_geometry.json", COR + "H5_rep1.npz", P5 + "selected_subsets_B2000.csv"],
    )
    add("local_mc", local_mc, [P6 + "local_geometry.json", P4 + "payoff_samples.npz"])
    add("ellipses", ellipse_rows, [P4 + "payoff_samples.npz", P6 + "local_geometry.json"])
    workflow_pt = [
        "Dados experimentais CCD",
        "Oito RSMs quadráticos",
        "Covariância residual",
        "Monte Carlo dos coeficientes",
        "Reotimização das âncoras",
        "Ensemble payoff",
        "CHIM / SVD",
        "PA calibrada pela incerteza",
        "37 subconjuntos selecionados",
        "Simplex-lattice local H5",
        "NBI local",
        "Reavaliação em 8 objetivos",
        "Não dominância no espaço completo",
        "Benchmark empírico",
    ]
    workflow_en = [
        "Experimental CCD data",
        "Eight quadratic RSMs",
        "Residual covariance",
        "Coefficient Monte Carlo",
        "Anchor reoptimization",
        "Payoff ensemble",
        "CHIM / SVD",
        "Uncertainty-calibrated PA",
        "37 selected subsets",
        "Local simplex-lattice H5",
        "Local NBI",
        "Reevaluation in 8 objectives",
        "Full-space nondominance",
        "Empirical benchmark",
    ]
    add(
        "workflow",
        dict(step=np.arange(1, 15), pt=workflow_pt, en=workflow_en),
        ["docs/mathematics/turning_final_benchmark.md"],
    )
    reader.read("docs/mathematics/turning_final_benchmark.md")
    audit = dict(
        csv_numeric_parsing="stdlib csv with explicit Python int/float literal conversion; "
        "17 significant digits in visual tables; no pandas float inference",
        base_commit=BASE,
        coding=coding,
        response_order=RESPONSES,
        directions=DIRECTIONS,
        factor_order=["Vc (cs)", "f", "ap (md)"],
        nominal_payoff_orientation="rows responses,columns anchors; transposed for plots",
        pca=pca,
        pca_fit="independent frozen18503-point reference only",
        representatives=representatives,
        visual_performance=dict(
            formula="(hi_i-z_i)/(hi_i-lo_i)",
            lower=lo.tolist(),
            upper=hi.tolist(),
            bounds_source=(
                "full canonical Phase7 candidates plus official standalone H5; frozen global MIN z"
            ),
            purpose="display only; official normalization/metrics unchanged",
        ),
        conflict=(
            "A3=loss(anchor_i,response_j)-loss(anchor_j,response_i), supplementary asymmetry only"
        ),
        ellipse_source=P4 + "payoff_samples.npz",
        ellipse_source_sha256=reader.sources[P4 + "payoff_samples.npz"]["sha256"],
        ellipse_definition=(
            "sample mean/covariance ddof1,n2000,chi2_2(.95); "
            "descriptive covariance-based MC uncertainty ellipse,not "
            "exact confidence region"
        ),
        coefficient_intervals=(
            "normal Wald beta +/- norm.ppf(.975)*SE from frozen "
            "analytic coefficient covariance; approximate,not "
            "multiplicity-adjusted"
        ),
        selected_local_subsets=ids,
        selection_rule="first and last lexicographic pair and trio; independent of outcome",
        local_coordinates=local_definitions,
        gridlines=False,
        gridline_exceptions=[],
        reference_points=18503,
        reference_CNBI_origins=0,
        official_CNBI_ND=409,
        missing_runtime="VRF: no reproducible timing; no new execution",
        historical_contributions=(
            "D5 only: Phase7 historical common envelope,CNBI=H20,not official H5 contribution"
        ),
    )
    data_dir = output / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(
            data_dir / f"plot_data_{name}.csv",
            index=False,
            float_format="%.17g",
            lineterminator="\n",
        )
    (data_dir / "visual_transform_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    # Renderers consume these exact tabular bytes,shared by both languages.
    reloaded = {
        name: read_table((data_dir / f"plot_data_{name}.csv").read_bytes()) for name in tables
    }
    return reloaded, audit, dependencies, reader
