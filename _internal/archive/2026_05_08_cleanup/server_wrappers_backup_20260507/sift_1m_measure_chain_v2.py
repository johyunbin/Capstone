#!/usr/bin/env python3
"""SIFT 1M (Option 1) RQ1+RQ2+RQ3 chain v2 — runner name mapping fix.

Stage:
- rq1_km20 — BERN+KM20 5 sel
- rq3_random20 — Recovery rate 분모
- rq2_5mode — 5 mode allocation
- rq3_<method> — 19 method 각각 (special handling for online_weight + kde subdirectories)
"""
import sys
from pathlib import Path
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3')
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache')

import _measure_common as mc

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
SIFT_1M = {
    'name': 'SIFT_1M',
    'table': 'customer_sift_1m_subset',
    'embed_col': 'c_embedding',
    'vec_dim': 128,
    'query_pool': CACHE / 'query_pool_sift_1m.parquet',
    'query_sel': CACHE / 'query_selectivity_sift_1m.parquet',
}
mc.DATASETS = [SIFT_1M]
mc.SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]

stage = sys.argv[1] if len(sys.argv) > 1 else None

if stage == 'rq1_km20':
    import run_km20
    sys.argv = ['run_km20.py', '--out-prefix', 'rq1_sift_1m_km20', '--include-bernoulli']
    run_km20.main()

elif stage == 'rq3_random20':
    import run_random20
    sys.argv = ['run_random20.py', '--out-prefix', 'rq3_sift_1m_random20']
    run_random20.main()

elif stage == 'rq2_5mode':
    sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache')
    import rq2_alloc_python as rq2
    rq2.DATASETS = [SIFT_1M]
    rq2.SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
    sys.argv = ['rq2_alloc_python.py', '--out-prefix', 'rq2_alloc_SIFT_1M_5mode']
    rq2.main()

elif stage and stage.startswith('rq3_'):
    method = stage[4:]
    out_prefix = f'rq3_1m_sift_{method}'

    if method in ('distance_shell', 'importance_sampling'):
        sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3/online_weight')
        runner = __import__(method)
        runner.DATASETS = [SIFT_1M]
        runner.SELECTIVITIES = mc.SELECTIVITIES
        sys.argv = [f'{method}.py', '--out-prefix', out_prefix]
        runner.main()
    elif method == 'kde_pilot':
        sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3/kde')
        import kde_pilot as runner
        runner.DATASETS = [SIFT_1M]
        runner.SELECTIVITIES = mc.SELECTIVITIES
        sys.argv = ['kde_pilot.py', '--out-prefix', out_prefix]
        runner.main()
    else:
        runner_map = {
            'minibatch': 'run_minibatch',
            'hilbert': 'run_hilbert',
            'random_proj': 'run_random_projection',
            'lsh': 'run_lsh',
            'kdtree': 'run_kdtree',
            'pca1d': 'run_pca1d',
            'zorder': 'run_zorder',
            'hybrid': 'run_hybrid',
            'minibatch_partial': 'run_minibatch_partial',
            'pq': 'run_pq',
            'spectral': 'run_spectral',
            'birch': 'run_birch',
            'sobol': 'run_sobol',
            'sparse_rp': 'run_sparse_rp',
            'gmm': 'run_gmm',
            'hdbscan': 'run_hdbscan',
        }
        runner_name = runner_map.get(method)
        if not runner_name:
            print(f'unknown method: {method}'); sys.exit(1)
        runner = __import__(runner_name)
        sys.argv = [f'{runner_name}.py', '--out-prefix', out_prefix]
        runner.main()

else:
    print(f'usage: {sys.argv[0]} <stage>')
    print('  stage: rq1_km20 | rq2_5mode | rq3_random20 | rq3_<method>')
    sys.exit(1)
