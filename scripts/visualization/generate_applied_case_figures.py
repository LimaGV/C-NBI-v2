"""Generate the official bilingual applied-case package from frozen results.

uv run python -m scripts.visualization.generate_applied_case_figures --language both --set all
Preview: --output experiments/runs/visual_preview --formats png --dpi 120
"""

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import textwrap
import warnings
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon, Rectangle

from cnbi_v2.data import sha256_file

from . import front_panels, problem_panels
from .annotations import caption, observation, question
from .gallery import write_gallery
from .sources import BASE, OUTPUT, ROOT, RUN_ID, prepare
from .style import FIGURES, PALETTE, SVG_OMISSIONS, clean_axes, configure


def write_json(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def scientific_artist_hash(fig):
    """Hash data-space geometry, excluding text, layout and translated legends."""
    digest = hashlib.sha256()

    def update(values):
        a = np.asarray(values)
        if a.dtype.kind not in "biufc":
            return
        a = np.ascontiguousarray(a, dtype=np.float64)
        digest.update(str(a.shape).encode())
        digest.update(a.tobytes())

    for ax in fig.axes:
        for line in ax.lines:
            update(line.get_xdata(orig=False))
            update(line.get_ydata(orig=False))
        for image in ax.images:
            update(image.get_array())
            update(image.get_clim())
        for collection in ax.collections:
            update(collection.get_offsets())
            array = collection.get_array()
            if array is not None:
                update(array)
            for path in collection.get_paths():
                update(path.vertices)
        for patch in ax.patches:
            if isinstance(patch, Rectangle):
                update([patch.get_x(), patch.get_y(), patch.get_width(), patch.get_height()])
            if isinstance(patch, Polygon):
                update(patch.get_xy())
            if hasattr(patch, "center"):
                update(patch.center)
                if hasattr(patch, "width"):
                    update([patch.width, patch.height, patch.angle])
    return digest.hexdigest()


def render(identifier, tables, audit, language):
    configure()
    if identifier[0] in "ABC":
        fig, used = problem_panels.plot(identifier, tables, audit, language)
    else:
        fig, used = front_panels.plot(identifier, tables, audit, language)
    clean_axes(fig)
    title = FIGURES[identifier][0 if language == "pt" else 1]
    fig.suptitle(textwrap.fill(title, width=86), fontsize=10, fontweight="normal")
    return fig, used


def export(fig, folder, identifier, language, formats, dpi):
    folder.mkdir(parents=True, exist_ok=True)
    output = []
    for fmt in formats:
        if fmt == "svg" and identifier in SVG_OMISSIONS:
            continue
        path = folder / f"{identifier}_{language}.{fmt}"
        if fmt == "pdf":
            metadata = {
                "CreationDate": None,
                "ModDate": None,
                "Creator": "C-NBI v2 applied scientific visualizations",
            }
        elif fmt == "svg":
            metadata = {"Date": None, "Creator": "C-NBI v2 applied scientific visualizations"}
        else:
            metadata = {"Software": "C-NBI v2 applied scientific visualizations"}
        with plt.rc_context({"svg.hashsalt": f"{RUN_ID}:{identifier}:{language}"}):
            fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.06, metadata=metadata)
        output.append(path)
    return output


def documents(output, catalog, audit, *, official):
    paths = []
    for language in ("pt", "en"):
        index = 0 if language == "pt" else 1
        text = (
            "# "
            + (
                "Legendas — caso aplicado C-NBI v2"
                if language == "pt"
                else "Captions — C-NBI v2 applied case"
            )
            + "\n\n"
        )
        for row in catalog:
            identifier = row["figure_id"]
            text += f"## {identifier} — {FIGURES[identifier][index]}\n\n"
            text += caption(identifier, language) + "\n\n"
        path = output / f"captions_{language}.md"
        path.write_text(text, encoding="utf-8", newline="\n")
        paths.append(path)
        if official:
            dest = ROOT / f"docs/figures/applied_case_captions_{language}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8", newline="\n")
            paths.append(dest)
    text = """# Pacote oficial de visualizações — caso aplicado

Este pacote apresenta exclusivamente evidências científicas congeladas no
commit d938695b7fdaf9c871d331a42ff277e0c3fbd2d1. O baseline é H5 standalone,
492 aceitos/411 únicos/409 ND. A referência independente tem18503 pontos e
zero proveniência CNBI. Nenhuma otimização,amostragem,refit ou métrica oficial
foi executada novamente. As tabelas oficiais de métricas são copiadas como
fontes; estatísticas de exibição e diagnósticos visuais são identificados.

Não há linhas de grade. Linhas de contorno,limites do domínio,zero dos Wald,
limiar PA,divisor pares/trios,K66 e janela/limiar de stop são referências
científicas explícitas,distintas de grades dos eixos.

## Base e nomenclatura

PR11 contém a correção e permaneceu aberto ao iniciar esta tarefa. A branch
feature/09-applied-case-visualizations parte de d938695 na branch corrigida,
sem fazer merge automático do PR11. O PR de visualizações usa essa base.
Fatores:x1=Vc(cabeçalho cs),x2=f,x3=ap(cabeçalho md),confirmados no metadata
de coding da Fase2. Não usar md como alias de Vc. Não existe inversa contínua
codificado→físico verificada. Respostas naturais não recebem a escala da
Tabela3; ROI/OEE não são convertidos para porcentagens.

## Transformações e limites

Auditáveis em data/visual_transform_audit.json. PCA única centrada na referência
18503,sem padronização extra,aplicada a todas as frentes e âncoras. Componentes,
média,variância e convenção de sinais estão salvos. As projeções não preservam
dominância em8D. O diagnóstico kNN mede densidade em2D,sem nova métrica principal.

As elipses descrevem a amostra MC já reotimizada:2000 payoff próprias,média
aritmética,covariância ddof1,nível.95,chi2df2. Os42 conjuntos de parâmetros,
variáveis de projeção e fonte estão nas tabelas de elipses e auditoria. Não são
regiões de confiança exatas nem intervalos para a média. Wald usa a covariância
analítica congelada e aproximação normal,sem multiplicidade. Nenhuma incerteza
foi reamostrada. A1 apenas avalia os coeficientes congelados no plano x3=0 para
desenhar o contorno; não estima coeficientes ou altera valores experimentais.

B6/C5 usam geometria nominal congelada e soluções H5 standalone; nunca usam
soluções H20 como baseline. Para trios,a normal é perpendicular ao plano CHIM
intrínseco e desaparece na projeção. O símbolo⊙ e o painel t tornam essa perda
de dimensão explícita. A projeção de um peso e de sua solução NBI pode coincidir.

E/F usam,quando comparativos,o alvo comum histórico22523 e deixam claro que
não é o alvo independente do CNBI. G usa as referências sem CNBI. D5 é apenas
proveniência histórica Fase7/CNBIH20,não contribuição do baseline409. Os tempos
por H são próprios standalone,n5 emH5/n1 nos demais; EAs têm10 seeds e suas
curvas de qualidade30 runs. Não existe runtime VRF-NBI reproduzível. A divergência
histórica H20 em1/4557 permanece como limitação já documentada,não é corrigida.

Representantes EA são escolhidos exclusivamente pelos IGDs já registrados,
com a menor seed em empate. Essa é uma seleção de exibição,não novo benchmark,
retuning,otimização ou alegação de run previamente nomeada como representante.
Os nomes,seeds e valores exatos estão na auditoria visual. Nenhuma legenda
apresenta uma run como mediana das30. Figuras quantitativas usam as30 quando
previsto. C1 inclui oito exports individuais solicitados,alternativas ao painel
composto,não oito resultados independentes adicionais. Não se gera radar,
UMAP,t-SNE,3D decorativo ou original NBI fora do benchmark.

## Reprodutibilidade

Entrada:scripts/visualization/generate_applied_case_figures.py. Opções:
--language pt/en/both,--set main/supplementary/all,--output,--formats,--dpi.
PNG600dpi,PDF e SVG vetoriais nas entregas oficiais. Prévia pode usar outro DPI.
SVG é omitido apenas para D3,cuja nuvem de referência é repetida em16 painéis;
o PDF totalmente vetorial e o PNG600dpi dessa figura continuam disponíveis.
Heatmaps usam células vetoriais e colorbars não são rasterizadas. O leitor CSV
preserva literais com conversão Python explícita e17 dígitos nas tabelas de
desenho,sem depender de float_precision depreciado no pandas3.1 instalado.
Context7 forneceu documentação Matplotlib,SciPy e NumPy; após o limite de
consultas,foi verificada a documentação oficial pandas e o código instalado:
https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html.
Sem LaTeX externo ou RNG. Metadados temporais de PDF/SVG são removidos e salts
SVG são fixos por figura/idioma. Reprodutibilidade bytewise é condicionada ao
mesmo ambiente/fontes/backends; as tabelas e identidades científicas permanecem
auditáveis entre plataformas. Os testes verificam exports repetidos e igualdade
dos dados/artistas entre PT/EN,integridade das fontes,paleta/ordens e baseline.
Os checksums incluem fontes de plotting,tabelas,figuras,metadata e captions.

## Catálogo e perguntas científicas

"""
    for row in catalog:
        identifier = row["figure_id"]
        tier = row["main_or_supplementary"]
        text += f"### {identifier} — {FIGURES[identifier][0]}\n\n"
        text += f"- Pergunta/finalidade: {row['scientific_purpose']}\n"
        text += f"- Tabelas de desenho: {row['data_tables']}\n"
        text += f"- Fontes congeladas: {row['source_artifacts']}\n"
        text += f"- Observação principal: {row['main_observation']}\n"
        text += f"- Transformação,observação e limites: {caption(identifier, 'pt')}\n"
        usage = (
            "artigo,dissertação,apresentação"
            if tier == "MAIN"
            else "material suplementar,dissertação,apresentação"
        )
        text += f"- Uso recomendado: {usage}.\n\n"
    text += (
        "## Representantes de exibição\n\n"
        + json.dumps(audit["representatives"], ensure_ascii=False, indent=2)
        + "\n"
    )
    path = output / "visualization_report.md"
    path.write_text(text, encoding="utf-8", newline="\n")
    paths.append(path)
    if official:
        dest = ROOT / "docs/figures/applied_case_visualization_report.md"
        dest.write_text(text, encoding="utf-8", newline="\n")
        paths.append(dest)
    return paths


def generate(
    output, *, language="both", figure_set="all", formats=("png", "pdf", "svg"), dpi=600, only=None
):
    output = Path(output)
    if (output / "metadata.json").exists():
        raise FileExistsError("completed visualization selection exists; choose an empty output")
    official = output.resolve() == OUTPUT.resolve()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
    )
    if official and dirty:
        raise ValueError("commit plotting source/protocol before official rendering")
    output.mkdir(parents=True, exist_ok=True)
    languages = ("pt", "en") if language == "both" else (language,)
    selected = [
        key for key, value in FIGURES.items() if figure_set == "all" or value[2] == figure_set
    ]
    if only is not None:
        selected = [key for key in selected if key in only]
    if not selected:
        raise ValueError("empty figure selection")
    tables, audit, dependencies, reader = prepare(output)
    catalog = []
    render_audit = []
    all_warnings = []
    for number, identifier in enumerate(selected, start=1):
        outputs = {}
        signatures = []
        used = None
        for lang in languages:
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                fig, used = render(identifier, tables, audit, lang)
                signature = scientific_artist_hash(fig)
                signatures.append(signature)
                grids = sum(
                    line.get_visible()
                    for ax in fig.axes
                    for line in [*ax.get_xgridlines(), *ax.get_ygridlines()]
                )
                folder = output / "figures" / FIGURES[identifier][2] / lang
                files = export(fig, folder, identifier, lang, formats, dpi)
                plt.close(fig)
            warning_text = [str(w.message) for w in captured]
            all_warnings.extend(
                dict(figure_id=identifier, language=lang, warning=w) for w in warning_text
            )
            outputs[lang] = [p.relative_to(output).as_posix() for p in files]
            render_audit.append(
                dict(
                    figure_id=identifier,
                    language=lang,
                    scientific_artist_sha256=signature,
                    visible_grid_lines=grids,
                    warnings=warning_text,
                )
            )
        if len(set(signatures)) != 1:
            raise ValueError(f"PT/EN data-space geometry differs: {identifier}")
        sources = sorted({path for table in used for path in dependencies[table]})
        data_paths = [f"data/plot_data_{table}.csv" for table in used]
        catalog.append(
            dict(
                figure_id=identifier,
                category=identifier[0],
                main_or_supplementary=FIGURES[identifier][2].upper(),
                title_pt=FIGURES[identifier][0],
                title_en=FIGURES[identifier][1],
                source_artifacts=json.dumps(sources),
                script="scripts/visualization/generate_applied_case_figures.py",
                output_pt=json.dumps(outputs.get("pt", [])),
                output_en=json.dumps(outputs.get("en", [])),
                scientific_purpose=question(identifier),
                main_observation=observation(identifier, tables, audit),
                data_tables=json.dumps(data_paths),
                scientific_artist_sha256=signatures[0],
            )
        )
        print(f"{number}/{len(selected)} {identifier}: " + ",".join(languages), flush=True)
    reader.verify_unchanged()
    pd.DataFrame(catalog).to_csv(output / "figure_catalog.csv", index=False, lineterminator="\n")
    write_json(output / "source_artifacts.json", reader.sources)
    write_json(output / "render_audit.json", render_audit)
    doc_paths = documents(output, catalog, audit, official=official)
    write_gallery(output, catalog)
    scripts = sorted((ROOT / "scripts/visualization").glob("*.py"))
    metadata = dict(
        run_id=RUN_ID,
        status="COMPLETE" if not all_warnings else "REVIEW_WARNINGS",
        generated_at_utc=datetime.now(UTC).isoformat(),
        scientific_base_commit=BASE,
        plotting_commit=subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        working_tree_dirty_at_start=dirty,
        languages=languages,
        formats=formats,
        png_dpi=dpi,
        figures=len(catalog),
        main=sum(r["main_or_supplementary"] == "MAIN" for r in catalog),
        supplementary=sum(r["main_or_supplementary"] == "SUPPLEMENTARY" for r in catalog),
        scientific_figure_families=len(
            [r for r in catalog if not r["figure_id"].startswith("C1_")]
        ),
        individual_C1_alternatives=sum(r["figure_id"].startswith("C1_") for r in catalog),
        palette=PALETTE,
        gridlines=False,
        gridline_exceptions=[],
        source_artifacts_unchanged=True,
        official_CNBI_ND=409,
        independent_reference_ND=18503,
        independent_CNBI_origins=0,
        no_new_optimization=True,
        no_RSM_refit=True,
        no_MC_draws=True,
        no_official_metric_recalculation=True,
        variants=len(catalog) * len(languages),
        exports=sum(
            len(json.loads(row["output_" + lang])) for row in catalog for lang in languages
        ),
        svg_omissions=SVG_OMISSIONS,
        pdf_all_vector=True,
        code_sha256={p.relative_to(ROOT).as_posix(): sha256_file(p) for p in scripts},
        data_sha256={
            p.relative_to(output).as_posix(): sha256_file(p) for p in (output / "data").glob("*")
        },
        data_rows={name: len(frame) for name, frame in tables.items()},
        versions={
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "matplotlib", "pandas")
        },
        base_PR=11,
        PR11_merge_performed=False,
        automatic_merge=False,
        render_warnings=all_warnings,
    )
    write_json(output / "metadata.json", metadata)
    readme = (
        "# Official applied-case visualization package\n\n"
        "Open index.html for the offline bilingual gallery. Scientific base: " + BASE + ".\n"
        "H5 standalone=409 ND; independent reference=18503,zero CNBI.\n"
        f"{metadata['figures']} catalog entries; {metadata['main']} main,"
        f"{metadata['supplementary']} supplementary,{metadata['variants']} language variants.\n"
        f"{metadata['exports']} exports in the requested formats;PNG DPI={dpi}.\n"
        "SVG excludes dense D3 (its full-vector PDF is retained when PDF is requested).\n"
        "No coordinate grid lines; scientific reference lines are described in captions.\n"
        "Source tables are shared exactly by PT/EN. Read visualization_report.md,\n"
        "source_artifacts.json,data/visual_transform_audit.json and checksums.sha256.\n"
        "No scientific rerun,model refit,metric change or automatic merge.\n"
    )
    (output / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    payloads = sorted(
        [p for p in output.rglob("*") if p.is_file() and p.name != "checksums.sha256"]
    )
    external = scripts + (
        [p for p in doc_paths if not p.is_relative_to(output)] if official else []
    )
    import os

    lines = [f"{sha256_file(p)}  {p.relative_to(output).as_posix()}\n" for p in payloads]
    lines += [
        f"{sha256_file(p)}  {Path(os.path.relpath(p, output)).as_posix()}\n" for p in external
    ]
    (output / "checksums.sha256").write_text("".join(lines), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                k: metadata[k]
                for k in ("figures", "main", "supplementary", "variants", "exports", "status")
            }
        ),
        flush=True,
    )
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("pt", "en", "both"), default="both")
    parser.add_argument(
        "--set", dest="figure_set", choices=("main", "supplementary", "all"), default="all"
    )
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument(
        "--formats", nargs="+", choices=("png", "pdf", "svg"), default=["png", "pdf", "svg"]
    )
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--only", nargs="+", choices=list(FIGURES))
    args = parser.parse_args()
    generate(
        args.output,
        language=args.language,
        figure_set=args.figure_set,
        formats=tuple(args.formats),
        dpi=args.dpi,
        only=args.only,
    )


if __name__ == "__main__":
    main()
