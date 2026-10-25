# Official standalone Phase8 correction

C-NBI(H5)=standalone H5 repetition1,492 accepted/411 unique/409 ND.
H2/H4/H10/H20 are independent sensitivity runs, not parent-grid sources.
Nine measured outputs plus full starts/trials are preserved; five H5 repetitions
are bitwise identical and used only to describe timing noise.

Parent-grid results remain immutable under the old Phase6/7/8 locations and map
to historical_parent_grid_analysis in baseline_registry.json. The old408-point
set is CNBI_H5_extracted_from_H20_parent_grid, never the official baseline.
The independent reference18503/zeroCNBI,seed indices,lineages/FPS and all EA/VRF
runs and EA timings are reused byte-for-byte. No new EA/VRF campaign.

launch.json identifies the clean executed source; execution_source_audit.json
checks its Git version and unchanged AST after formatting. completion.json
records actual filesystem isolation of Phase6/7 results during all solves.
metadata.json identifies targeted analysis and reused input hashes. Twelve new
figures PDF/SVG/PNG600dpi and named24-case diagnostics accompany the tables.
checksums.sha256 covers every payload except itself. Figure rendering/reporting
is postprocessing and never supplies runtime figures.

Authoritative report: ../../../docs/mathematics/turning_final_benchmark.md
(relative from repository root: docs/mathematics/turning_final_benchmark.md).
Full verification and40 delivery items: docs/phase_8_verification.md.
No automatic merge,adaptive refinement,new scenarios or solver change.
