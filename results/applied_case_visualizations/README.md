# Applied-case scientific visualizations

Official package: `turning_visuals_20261025`,from scientific base
`d938695b7fdaf9c871d331a42ff277e0c3fbd2d1`. No scientific pipeline is rerun.
The operational baseline is standalone H5,409 ND; historical parent-grid408
is not used as baseline. The independent reference remains18503/zeroCNBI.

46 catalog entries:38 scientific figure families plus eight requested individual
C1 presentation alternatives. 21 main and25 supplementary compositions,each
in Portuguese and English. PNG600dpi and full-vector PDF throughout; SVG is
omitted only for the dense16-panel D3,which retains its vector PDF.
92 language variants,274 figure exports. No coordinate grid lines.

Start at `turning_visuals_20261025/index.html` for the offline language-switching
gallery,or figure_catalog.csv. The data/ directory contains the actual tables
used by both renderings,including PCA/ellipse/representative-selection audits.
Source identities and SHA256 are verified before/after presentation. Captions
and reporting are also at docs/figures/applied_case_*.md.

Reproduce into an empty destination:

~~~powershell
uv run python -m scripts.visualization.generate_applied_case_figures --language both --set all --output <directory>
~~~

Options include --language pt/en/both,--set main/supplementary/all,--only,
--formats and --dpi. Nonofficial previews may use lower resolution. Scientific
artifact directories and raw data are never overwritten. No original-NBI or
new VRF-NBI algorithm/timing,adaptive refinement or automatic merge is included.
