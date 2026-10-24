# Full-precision turning RSM diagnostics

Reproduce: `uv run python -m scripts.validation.turning_diagnostics`.
model_diagnostics.csv: eight responses, physical_cells; R2 values are fractions.
all_cases_model_diagnostics.csv, anova.csv, lack_of_fit.csv and press_residuals.csv: all four previously recorded fits; Case is explicit.
published_summary_comparison.csv: secondary comparison, all four cases; S*100, R2*100, differences in printed units, half last printed unit.
R2_pred method in the article is unspecified; numeric agreement does not prove equivalence.
No rounded WR, changed observations, selected terms or later optimization.
See docs/mathematics/turning_rsm_diagnostics.md for scientific interpretation.
manifest.json binds actual execution commit, code/input hashes and environment; checksums.sha256 covers every artifact except itself.
