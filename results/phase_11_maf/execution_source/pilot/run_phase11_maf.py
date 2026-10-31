"""Checkpointed direct MaF campaign. Pilot is mandatory before remaining jobs."""

import os

for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'

import argparse
import hashlib
import json
import platform
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from cnbi_v2.maf import OPTIONS, MaF, metrics, run

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'results/phase_11_maf'
V1 = Path('C:/Users/gabri/Documents/CNBI')
CONFIGS = [(n, m) for n in (8, 9) for m in (4, 6, 8, 10, 15)]


def clean(value):
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def write_json(path, value):
    path.write_text(json.dumps(clean(value), indent=2, allow_nan=False)+'\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance():
    sources = {}
    for p in ('cnbi_experiments/benchmarks.py', 'cnbi_experiments/parallel_analysis.py',
              'cnbi_experiments/solver.py', 'cnbi_experiments/pilot.py',
              'cnbi_experiments/campaign.py', 'cnbi_experiments/references/provenance.json',
              'Papper/Manuscript - CNBI.docx'):
        b = subprocess.check_output(['git', '-C', str(V1), 'show', '7bd4915:'+p])
        sources[p] = hashlib.sha256(b).hexdigest()
    notebook = subprocess.check_output([
        'git', '-C', str(V1/'CNBI-Synthetic-Benchmarks'), 'show',
        'bdd64313:notebooks/04_analise_resultados.ipynb'])
    sources['submodule@bdd64313/notebooks/04_analise_resultados.ipynb'] = (
        hashlib.sha256(notebook).hexdigest())
    saved = V1/'experimental_results/maf_cnbi_unlimited/MAF_CNBI_SUMMARY.csv'
    v1 = pd.read_csv(saved)
    v1 = v1[v1.scenario_id.str.match(r'maf[89]_')]
    return dict(v1_commit='7bd4915a9aea94b9dca1d70014ba5186b4b4e44d',
                v1_sources_sha256=sources, v1_saved_summary_sha256=digest(saved),
                v1_saved_summary_status='LOCAL_SAVED_RESULTS_NOT_VERIFIED_PUBLICATION',
                v1_saved_summary=v1.to_dict('records'))


def worker(task):
    number, m, seed = task
    case = f'maf{number}_m{m}_seed{seed}'
    target = OUTPUT/'cases'/case
    target.mkdir(parents=True, exist_ok=False)
    try:
        result = run(number, m, seed)
        problem = MaF(number, m)
        ref = np.load(OUTPUT/'references'/f'maf{number}_m{m}.npz')
        ids = result['nd']
        f = result['F'][ids]/ref['amplitude']
        evaluation_start = perf_counter()
        indicators = metrics(f, ref['F']/ref['amplitude'], seed)
        evaluation_seconds = perf_counter()-evaluation_start
        accepted = [r for r in result['subproblems'] if r['accepted']]
        if result['geometry_failures']:
            raise ValueError('Selected subset has invalid local geometry')
        if not accepted or not problem.feasible(result['X']).all():
            raise ValueError('Invalid or empty pilot/front')
        # A campaign with only vertices and no successful interior weight is blocked.
        if not any(r['accepted'] and r['weight'] not in (0, 5) for r in result['subproblems']
                   if len(r['indices']) == 2):
            raise ValueError('No successful pairwise interior weight')
        np.savez_compressed(target/'solutions.npz', X=result['X'], F=result['F'],
                            nd_indices=ids, anchors=result['anchors'], payoff=result['payoff'])
        screen = result['screen']
        np.savez_compressed(target/'spectral.npz',
                            **{k: screen[k] for k in ('sample_x', 'sample_f', 'null',
                                                       'observed', 'q95', 'singular')})
        write_json(target/'diagnostics.json', dict(
            rank=screen['rank'], floor=screen['floor'], ceiling=screen['ceiling'],
            subsets=screen['subsets'], anchor_trials=result['anchor_trials'],
            subproblems=result['subproblems'], origins=result['origins'],
            gradient_calls=result['gradient_calls'], geometry_failures=result['geometry_failures']))
        row = dict(case=case, problem=f'MaF{number}', m=m, seed=seed, status='COMPLETED',
                   rank=screen['rank'], candidate_subsets=len(screen['subsets']),
                   selected_subsets=sum(s['selected'] for s in screen['subsets']),
                   subproblems=len(result['subproblems']), accepted_subproblems=len(accepted),
                   failed_subproblems=len(result['subproblems'])-len(accepted),
                   attempts=sum(r['attempts'] for r in result['subproblems']),
                   evaluations=result['evaluations'], raw_cardinality=len(result['X']),
                   nd_cardinality=len(ids), max_eq_l2=max(r['eq_l2'] for r in accepted),
                   min_margin=min(r['margin'] for r in accepted),
                   seconds=result['seconds'], diagnostic_seconds=result['diagnostic_seconds'],
                   nbi_seconds=result['nbi_seconds'], evaluation_seconds=evaluation_seconds,
                   **indicators)
        write_json(target/'completed.json', row)
        return row
    except Exception as error:
        write_json(target/'failure.json', dict(case=case, error=f'{type(error).__name__}: {error}'))
        raise


def collect():
    return pd.DataFrame([json.loads(p.read_text()) for p in sorted(
        (OUTPUT/'cases').glob('*/completed.json'))])


def finish(manifest, wall):
    data = collect()
    data.to_csv(OUTPUT/'runs.csv', index=False)
    indicators = ['GD', 'IGD', 'HV', 'HV_se', 'Spacing', 'Sparsity', 'nd_cardinality',
                  'seconds', 'evaluations', 'selected_subsets', 'failed_subproblems']
    summary = data.groupby(['problem', 'm'])[indicators].agg(['median', 'min', 'max', 'mean'])
    summary.columns = ['_'.join(c) for c in summary.columns]
    summary = summary.reset_index()
    summary['runs'] = summary.apply(lambda r: len(data[(data.problem == r.problem)
                                                       & (data.m == r.m)]), axis=1)
    v1 = pd.DataFrame(manifest['provenance']['v1_saved_summary'])
    for metric in ('IGD', 'HV'):
        lookup = v1.set_index('scenario_id')[metric+'_median']
        summary['V1_'+metric+'_median'] = [lookup[f'{p.lower()}_m{m}']
                                          for p, m in zip(summary.problem, summary.m, strict=True)]
        summary[metric+'_delta_V1'] = summary[metric+'_median']-summary['V1_'+metric+'_median']
    summary.to_csv(OUTPUT/'summary.csv', index=False)
    manifest.update(completed=len(data), expected=100,
                    status='COMPLETED' if len(data) == 100 else 'PILOT_VALIDATED',
                    wall_seconds=manifest.get('wall_seconds', 0)+wall,
                    kernel_seconds_sum=float(data.seconds.sum()),
                    local_failures=int(data.failed_subproblems.sum()),
                    max_accepted_eq_l2=float(data.max_eq_l2.max()))
    manifest['hashes'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in (
        ROOT/'src/cnbi_v2/maf.py', Path(__file__), ROOT/'tests/test_maf.py', ROOT/'uv.lock',
        ROOT/'src/cnbi_v2/nbi/solver.py', ROOT/'src/cnbi_v2/nbi/geometry.py',
        ROOT/'src/cnbi_v2/chim/normalization.py', ROOT/'src/cnbi_v2/nbi/sensitivity.py')}
    manifest['artifact_sha256'] = {p.relative_to(OUTPUT).as_posix(): digest(p)
                                  for p in sorted(OUTPUT.rglob('*'))
                                  if p.is_file() and p.name not in ('manifest.json', 'report.md')}
    write_json(OUTPUT/'manifest.json', manifest)
    lines = ['# Phase 11: direct MaF8/MaF9 C-NBI V2', '',
             f"Completed: {len(data)}/100. Wall time: {manifest['wall_seconds']:.2f} s; "
             f"summed optimizer time: {data.seconds.sum():.2f} s.", '',
             '|Problem|m|Runs|IGD median|HV median|V1 IGD|V1 HV|ND median|',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in summary.to_dict('records'):
        lines.append(f"|{r['problem']}|{r['m']}|{r['runs']}|{r['IGD_median']:.7g}|"
                     f"{r['HV_median']:.7g}|{r['V1_IGD_median']:.7g}|{r['V1_HV_median']:.7g}|"
                     f"{r['nd_cardinality_median']:.0f}|")
    lines += ['', '## Protocol and limitations', '',
              'Direct distance objectives, nx=2, box [-10000,10000]^2; MaF9 forbidden regions '
              'are enforced without repair. All anchors are optimized, including the V1 '
              'minimum-norm tie rule for its nonunique line minima.',
              '500 independent known-Pareto samples per seed are used only for correlation '
              'Horn PA (ddof=1, 1000 column permutations, linear q95, sequential strict rank). '
              'The V1 difference-SVD window is preserved using the V2 vertex-difference helper. '
              'RSM uncertainty screening/early stopping is inapplicable and unused.',
              'Subsets k=2,3; H=5; local CHIM/normalization, lattice traversal, SLSQP and '
              'full-objective dominance are V2. No V1 solver imports. Necessary implementation '
              'differences: V2 warm starts/retries, centered CHIM normal, analytic piecewise '
              'domain Jacobian, and L2 equality acceptance <=1e-5 (V1 used infinity norm). '
              'MaF settings retain maxiter=100 and ftol=1e-10, t in [-10,10]. '
              'This is protocol replication, not an assertion of identical fronts.',
              'External reference: 5000 area-uniform polygon points, seed404, independent of '
              'the diagnostic. Scaling is zero ideal and vertex-objective maximum, without '
              'clipping. GD/IGD and Sparsity reuse V2 Euclidean nearest distances; '
              'MaF Spacing uses population SD (ddof=0) as V1, unlike the corrected RSM study.',
              'HV follows V1 exactly: one scrambled Sobol net of8192, seed2026+run_seed, '
              'fixed [0,1.1]^m. HV_se is the historical binomial proxy, not a calibrated QMC '
              'confidence interval. Precision is especially limited at m=15; no escalation '
              'or cross-study statistical test was added.',
              'The V1 figures above are verified local saved summary values, hashed in the '
              'manifest, not independently verified published table entries. The manuscript '
              'confirms MaF stress-test scope. V1 recorded identical optimizer fronts across '
              'seeds within each configuration; HV variability includes integration seeds '
              'and must not be interpreted as optimizer variability.',
              f"Rejected local subproblems: {int(data.failed_subproblems.sum())}; "
              f"maximum accepted L2 equality residual: {data.max_eq_l2.max():.5g}. "
              'Failures are retained in each case diagnostic, never replaced with fabricated points.',
              'Pilot MaF8/m4 and MaF9/m4/seed101 passed before remaining jobs. '
              'Completed checkpoints are hash-verified and never rerun. '
              'Earlier science/results and the applied case remain unchanged.']
    (OUTPUT/'report.md').write_text('\n\n'.join(lines)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    start = perf_counter()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT/'references').mkdir(exist_ok=True)
    manifest_path = OUTPUT/'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for p, sha in manifest.get('hashes', {}).items():
            if digest(ROOT/p) != sha:
                raise ValueError(f'Code changed since pilot: {p}')
        for p, sha in manifest.get('artifact_sha256', {}).items():
            if digest(OUTPUT/p) != sha:
                raise ValueError(f'Checkpoint integrity failed: {p}')
    else:
        manifest = dict(base_commit=subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            python=platform.python_version(), platform=platform.platform(),
            versions={k: version(k) for k in ('numpy', 'scipy', 'pandas')},
            settings=dict(configurations=CONFIGS, seeds=list(range(101, 111)), nx=2,
                          diagnostic_n=500, permutations=1000, q=.95, reference_n=5000,
                          reference_seed=404, lattice_H=5, solver=asdict(OPTIONS),
                          spacing_ddof=0, hv_n=8192, hv_ref=1.1, hv_seed='2026+seed',
                          workers=args.workers), provenance=provenance())
    for number, m in CONFIGS:
        path = OUTPUT/'references'/f'maf{number}_m{m}.npz'
        if not path.exists():
            p = MaF(number, m)
            x, f = p.sample(5000, 404)
            amplitude = p.values(p.vertices).max(axis=0)
            saved = V1/f'experimental_results/maf_cnbi_unlimited/maf{number}_m{m}_reference.npz'
            old = np.load(saved)
            if not (np.array_equal(f, old['F']) and np.array_equal(amplitude, old['amplitude'])):
                raise ValueError('Reference/scaling differs from saved V1 protocol')
            np.savez_compressed(path, X=x, F=f, ideal=np.zeros(m), amplitude=amplitude)
    pilot = [(8, 4, 101), (9, 4, 101)]
    for task in pilot:
        if not (OUTPUT/'cases'/f'maf{task[0]}_m{task[1]}_seed{task[2]}'/'completed.json').exists():
            worker(task)
    finish(manifest, perf_counter()-start)
    print('PILOT PASS: MaF8 and MaF9; references identical to V1', flush=True)
    if args.pilot:
        return
    remaining = [(n, m, s) for n, m in CONFIGS for s in range(101, 111)
                 if not (OUTPUT/'cases'/f'maf{n}_m{m}_seed{s}'/'completed.json').exists()]
    start = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker, task) for task in remaining]
        for count, future in enumerate(as_completed(futures), start=1):
            future.result()
            if count % 10 == 0:
                print(f'Completed checkpoints: {len(collect())}/100', flush=True)
    finish(manifest, perf_counter()-start)
    print(f'COMPLETE {len(collect())}/100', flush=True)


if __name__ == '__main__':
    main()
