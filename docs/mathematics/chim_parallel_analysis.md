# Fixed nominal normalization and centered CHIM spectral screening

Phase 5, ADR 0008 ACCEPTED in the requested scope. The inputs are the Phase 2
sphere-only nominal payoff and the frozen 2000 Phase 4 reoptimized payoffs.
No fitting, draws or optimizer calls occur. The method is **Monte Carlo
uncertainty-calibrated Parallel Analysis / PA-inspired spectral screening**;
classical Horn equivalence is not asserted. [Sources and coverage](../../references/notes/phase_05_sources.md).

## Common geometry

Rows are responses, columns are their anchors, order T,MTTF,WR,Ra,Rt,Kp,ROI,OEE.
Directions MAX,MAX,MIN,MIN,MIN,MIN,MAX,MAX imply signs (-1,-1,1,1,1,1,-1,-1).
Define G=D_s A and from the nominal payoff alone:

\[
u_i=G_{ii}^{nom},\quad n_i^{payoff}=\max_jG_{ij}^{nom},\quad
a_i=n_i^{payoff}-u_i>0,\quad
Z_{ij}=(G_{ij}-u_i)/a_i.
\]

The diagonal is checked as the minimum of its nominal oriented row within only
the archived solver-certificate/objective-scale numerical allowance. Significant
violations fail; no values are corrected. The real allowance is 4*c_i*1e-10 plus
eps64*16*m*max_abs_nominal_row: on the normalized unit ball, point differences
have norm at most approximately two, so residual stationarity, shifted-PSD and
complementarity errors translate to a few certificate units of objective error.
The stored float64 allowance also accounts for evaluating/subtracting row values.
Numerically degenerate amplitudes a_i<=eps64*16*m*max_abs_nominal_row fail.
This is not a statistical PA margin, rank filter or a Nadir estimator.

Exactly the same u and a normalize every replica. Nominal diagonal is zero and
each nominal row maximum is one. Replicas may lie outside [0,1] and have nonzero
diagonals; no clipping or per-replica normalization is applied. The perturbation is

\[
\Delta^{(b)}=Z^{(b)}-Z^{nom}
 =D_a^{-1}D_s(A^{(b)}-A^{nom}).
\]

The implementation evaluates the latter expression directly, avoiding unnecessary
subtraction of two normalized arrays. Both forms agree within float64 roundoff.
No across-replica mean is subtracted: systematic optimizer/payoff shifts relative
to the nominal geometry remain part of the defined uncertainty reference.

For positive response-unit factor c_i and common shift t_i, oriented nominal and
sampled rows become c_i G_i+s_i t_i, u'_i=c_i u_i+s_i t_i and a'_i=c_i a_i.
Therefore Z'=Z and Delta'=Delta, subject to representable floating-point precision.
An equivalent sign-reversed MAX response marked MIN also leaves G unchanged.

## Centered CHIM and affine dimension

For C of size k, use **only** its corresponding responses and anchors:
Z_C=Z[C,C] (k by k). Vertices are its columns. With H_k=I_k-11'/k,

\[
M_C^{nom}=Z_C^{nom}H_k,\qquad N_C^{(b)}=\Delta_C^{(b)}H_k.
\]

H_k is symmetric, idempotent, H_k 1=0 and rank k-1. A common vertex translation
adds t1', annihilated on multiplication by H_k. Let z_bar be the mean vertex and
E_ref have columns z_j-z_ref. Every centered column z_j-z_bar is a linear
combination of reference differences; each reference difference is itself the
difference of two centered columns. Their column spans coincide. Thus

\[
\dim_{aff}\{z_1,...,z_k\}=rank(Z_C H_k)=rank(E_{ref})\le k-1.
\]

Reference-difference singular values need not coincide across reference choices;
only rank is equivalent. Canonical SVD/PA always uses the centered matrix.
For simultaneous row/anchor permutation P, P1=1 and P commutes with H_k;
the centered matrix becomes P M P', preserving singular values.

For each nominal and noise matrix use np.linalg.svd(compute_uv=False), retaining
the first k-1 descending singular values. Only the structural final null direction
is omitted. Remaining values are neither clipped nor discarded by rank tolerances.
Numerical rank is a separate NumPy-default roundoff diagnostic, not a PA gate.
Three decision factors do not force the affine dimension of a nonlinear response
image to be at most three. Global PA dimension never removes local candidates.

## Uncertainty-calibrated PA definition

The global case k=8 has seven nontrivial components. Local candidates are all
combinations for 2<=k<=n_x+1=4: 28 pairs, 56 triples, 70 quadruples. Indices are
increasing, k order first; IDs C_1_2 etc use one-based original response indices.

For each C,r and prefix B, compute q95_Cr(B)=quantile(noise_sigma_Cr[:B],.95,
method="linear"). This reference is formed from **Delta_C H_k**, not Z_b H_k
or a difference of already computed singular values. Compare strictly:

\[
pass_{C,r}=[\sigma^{obs}_{C,r}>q95_{C,r}],\quad
margin_{C,r}=\sigma^{obs}_{C,r}-q95_{C,r},\quad
selected(C)=\bigwedge_{r=1}^{k-1}pass_{C,r}.
\]

No extra statistical margin, qmax, singular-ratio, condition, determinant/volume,
global-dimension, sampler-moment or anchor-displacement filter is used. q=.95 is
fixed, not tuned. Global dimension is the number of consecutive leading passes;
PASS,FAIL,PASS yields dimension one and NON_MONOTONE_PA_PATTERN, never two.
Local selection directly evaluates all 154 candidates, including every component.

This is an explicitly defined screening procedure conditional on the canonical
RSMs and their plug-in coefficient ensemble, not a proven Horn-null-equivalent
factor test. q95 thresholds are not confidence intervals, universal rank cutoffs
or simultaneous multiple-testing error guarantees. No historical subset count
is a calibration target or acceptance oracle.

## Prefixes and original proposed stopping policy

SVD noise arrays are computed once and retained. Evaluate exactly 20 nested
prefixes B=100:100:2000, always retaining B=2000 as the scientific reference.
All 357 decision quantiles are tracked: 7 global +28+2*56+3*70 local values.
Selection stability compares exact IDs, not counts. Quantile identity/order is
also checked, so thresholds cannot be compared after relabeling components.

Consume docs/policies/pa_early_stop_policy.json unchanged, including epsilon_q
and PROPOSED status. First eligibility is 500 vs400. At every eligible checkpoint
require simultaneously equal selected ID sets, equal global dimension and

\[
\max_q\frac{|q_B-q_{B-100}|}
 {\max(|q_B|,|q_{B-100}|,\epsilon_q)}<.01.
\]

epsilon_q=2.2250738585072014e-308, exactly the original policy value. A relative
change equal to 1% fails. Two zero quantiles have zero change; zero versus a
nonzero normal float has relative change one. All global/local thresholds used
in decisions are compared, including those of rejected subsets.

Record the first eligible joint success, but do not truncate this validation.
If none occurs: EARLY_STOP_NOT_REACHED, B_reference=2000, no execution failure.
If B_stop<2000, compare its global dimension and selected identities against
**every later checkpoint**: all equal gives EARLY_STOP_RETROSPECTIVELY_STABLE;
any divergence gives PREMATURE_STOP_DETECTED with changed checkpoint IDs.
Stopping only at 2000 provides no later retrospective evidence. Do not revise
or promote the policy automatically after seeing these results.

## Software, reproducibility and scope

Public API in cnbi_v2.chim provides frozen normalization/spectral/decision arrays,
centering and difference diagnostics, programmatic candidates, prefix decisions
and retrospective policy checks. Tests cover unit/translation/direction and
vertex permutation invariance, known affine ranks, strict all-component decisions,
non-monotone patterns, exact subset identities, prefix quantiles, zero handling,
stable/premature/not-reached stops and immutable/finite outputs.

`uv run python -m scripts.validation.turning_chim_pa --run-id <fresh_id>` consumes
pinned nominal/Phase 4/certificate/policy/raw files. It checks the recorded
Phase 4 diagonal identity against the archived optimal values. No RNG or optimizer
is called. Nonempty output directories are refused. Hashes, exact source commit,
environment, complete noise spectra, component thresholds/decisions, selected
identities, all prefixes and retrospective results are archived.
See [real report](turning_chim_pa.md) and [verification](../phase_5_verification.md).

No new dependency, RC, lattice resolution H, weights, NBI/C-NBI, clustering or
Pareto metrics are implemented. H_k denotes centering only, not lattice H.
