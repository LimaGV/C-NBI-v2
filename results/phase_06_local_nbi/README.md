# Local NBI / internal Simplex-Lattice resolution sensitivity

Explicit Phase6 request. Exact37 B2000 subsets, original nominal coded RSMs,
nominal sphere anchors/payoff and fixed full-space Phase5 normalization.
No new PA/MC/anchor optimization or RC. NBI uses a separate local deterministic
normalization, unit ideal-oriented normal and analytic-Jacobian SLSQP.

Reviewed archive: turning_local_nbi_h20_20261024. One H20 parent lattice/solution
set, exact membership for H2,4,5,10,20, all-eight-response evaluation, complete
attempt/provenance logs and full-space ND/coverage diagnostics. Only this exact
run is allowed by .gitignore. Other runs stay ignored; nonempty output dirs
cannot be overwritten. H20 is an internal finest resolution, not true Pareto.
No final H accepted, external benchmark, automatic merge or new phase.

See docs/mathematics/local_nbi.md and turning_local_nbi_h_sensitivity.md.
