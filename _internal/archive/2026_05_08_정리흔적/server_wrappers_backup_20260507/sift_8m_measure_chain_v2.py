#!/usr/bin/env python3
"""SIFT 8M RQ1+RQ2+RQ3 chain v2 — runner name mapping fix + subdir imports."""
import sys
from pathlib import Path
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3')
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache')

import _measure_common as mc

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
SIFT_8M = {
    'name': 'SIFT_8M',
    'table': 'customer_sift_8m_subset',
    'embed_col': 'c_embedding',
    'vec_dim': 128,
    'query_pool': CACHE / 'query_pool_sift_8m.parquet',
    'query_sel': CACHE / 'query_selectivity_sift_8m.parquet',
}
mc.DATASETS = [SIFT_8M]
mc.SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]

stage = sys.argv[1] if len(sys.argv) > 1 else None

if stage == 'rq1_km20':
    import run_km20
    sys.argv = ['run_km20.py', '--out-prefix', 'rq1_sift_8m_km20', '--include-bernoulli']
    run_km20.main()

elif stage == 'rq3_random20':
    import run_random20
    sys.argv = ['run_random20.py', '--out-prefix', 'rq3_sift_8m_random20']
    run_random20.main()

elif stage == 'rq2_5mode':
    sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache')
    import rq2_alloc_python as rq2
    rq2.DATASETS = [SIFT_8M]
    rq2.SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
    sys.argv = ['rq2_alloc_python.py', '--out-prefix', 'rq2_alloc_SIFT_8M_5mode']
    rq2.main()

elif stage and stage.startswith('rq3_'):
    method = stage[4:]
    out_prefix = f'rq3_8m_sift_{method}'

    if method in ('distance_shell', 'importance_sampling'):
        sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3/online_weight')
        runner = __import__(method)
        runner.DATASETS = [SIFT_8M]
        runner.SELECTIVITIES = mc.SELECTIVITIES
        sys.argv = [f'{method}.py', '--out-prefix', out_prefix]
        runner.main()
    elif method == 'kde_pilot':
        sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3/kde')
        import kde_pilot as runner
        runner.DATASETS = [SIFT_8M]
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
