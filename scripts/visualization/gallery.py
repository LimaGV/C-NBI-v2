"""Local,offline figure catalog; it displays existing exports without analysis."""

import html
import json

from .annotations import caption


def write_gallery(output, catalog):
    cards = []
    for row in catalog:
        identifier = row["figure_id"]
        versions = []
        for language in ("pt", "en"):
            files = json.loads(row["output_" + language])
            if not files:
                continue
            png = next((p for p in files if p.endswith(".png")), None)
            title = html.escape(row["title_" + language])
            image = (
                (
                    f'<a href="{html.escape(png)}"><img loading="lazy" '
                    f'src="{html.escape(png)}" alt="{title}"></a>'
                )
                if png
                else ""
            )
            links = " · ".join(
                f'<a href="{html.escape(p)}">{p.rsplit(".", 1)[1].upper()}</a>' for p in files
            )
            tables = " · ".join(
                f'<a href="{html.escape(p)}">{html.escape(p.rsplit("/", 1)[1])}</a>'
                for p in json.loads(row["data_tables"])
            )
            versions.append(
                f'<div class="version {language}"><h2>{identifier} — {title}</h2>'
                f"{image}<p>{links}</p><details><summary>Caption / Legenda</summary>"
                f"<p>{html.escape(caption(identifier, language))}</p></details>"
                f"<details><summary>Data / Dados</summary><p>{tables}</p></details></div>"
            )
        cards.append(
            '<article data-tier="'
            + row["main_or_supplementary"]
            + '">'
            + "".join(versions)
            + "</article>"
        )
    default = "pt" if json.loads(catalog[0]["output_pt"]) else "en"
    page = """<!doctype html>
<html lang="pt"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>C-NBI v2 — scientific visualizations</title>
<style>
body{font:16px system-ui,sans-serif;color:#222;margin:0;background:white}
header{padding:1.4rem 2rem;border-bottom:1px solid #ddd;position:sticky;
top:0;background:white;z-index:2}
h1{font-size:1.4rem;margin:0 0 .5rem}h2{font-size:1rem}
button,select{font:inherit;padding:.35rem .6rem}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:1.5rem;padding:1.5rem}
article{border:1px solid #ddd;border-radius:6px;padding:1rem;min-width:0}
img{max-width:100%;height:360px;object-fit:contain;display:block;margin:auto}
details{font-size:.9rem;line-height:1.5;margin-top:.5rem}a{color:#176198}
body[data-language="pt"] .en,body[data-language="en"] .pt{display:none}
article[hidden]{display:none}
</style>
<body data-language="LANGUAGE"><header>
<h1>C-NBI v2 — visualizações científicas / scientific figures</h1>
<p>H5 standalone: 409 ND · Independent reference: 18,503 · Offline frozen-artifact gallery</p>
<button onclick="document.body.dataset.language='pt'">Português</button>
<button onclick="document.body.dataset.language='en'">English</button>
<select aria-label="Figure tier" onchange="for(const e of document.querySelectorAll('article'))
{e.hidden=this.value!=='ALL' &amp;&amp; e.dataset.tier!==this.value}">
<option value="ALL">All / Todas</option><option value="MAIN">Main / Principais</option>
<option value="SUPPLEMENTARY">Supplementary / Suplementares</option></select>
<a href="figure_catalog.csv">CSV catalog</a> · <a href="checksums.sha256">SHA256</a>
</header><main>CARDS</main></body></html>
"""
    (output / "index.html").write_text(
        page.replace("LANGUAGE", default).replace("CARDS", "".join(cards)),
        encoding="utf-8",
        newline="\n",
    )
