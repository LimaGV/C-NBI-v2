# Applied-case figure documentation

Current state (2026-10-29): PR11/12 are integrated in main; see
../consolidation_20261029.md. Hashed reports/captions inside the archived run
describe their original launch state and remain byte-identical.

The generator writes applied_case_captions_pt.md,applied_case_captions_en.md and
applied_case_visualization_report.md directly from the shared scientific catalog.
Each entry identifies question,source tables,transformation,observation,limits
and recommended use. The package itself includes identical copies and hashes.

The visual policy uses no coordinate grids. Contours,domain boundaries,zero
reference lines,PA thresholds,K66 and the frozen retrospective stopping window
carry scientific meaning and remain explicitly described. No grid exception is
needed in the current package. Main composed panels are designed for double
column/full-page widths; C1 individual variants fit a single column. Do not
shrink the eight-response or37-subset composites to illegible single-column size.

All PDFs retain vector geometry,including heatmap cells; no automatic scatter
or colorbar rasterization. SVG is omitted for the dense D3 board only,with vector
PDF retained. Font family DejaVu Sans,compact legends,white background and exact
central palette are defined in scripts/visualization/style.py.

Formal validation and the42 requested delivery items are recorded separately in
applied_case_verification.md after artifact review; it does not change captions
or scientific sources. This is presentation of frozen results,not a new method.
