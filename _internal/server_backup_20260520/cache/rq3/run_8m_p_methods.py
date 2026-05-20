#!/usr/bin/env python3
"""P1/P2/P4/P5 의 8M variant — DEEP_8M에서 추가 method 측정.

CLI 로 method 선택. 5 sel 모두 측정.
"""
import sys
from pathlib import Path
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3')

import _measure_common as mc

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
mc.DATASETS = [
    {'name': 'DEEP_8M', 'table': 'partsupp_deep_10_phase7_8m_subset',
     'embed_col': 'ps_embedding', 'vec_dim': 96,
     'query_pool': CACHE / 'query_pool.parquet',
     'query_sel': CACHE / 'query_selectivity_8m.parquet'}
]
mc.SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]

method = sys.argv[1] if len(sys.argv) > 1 else 'reservoir'

if method == 'reservoir':
    import run_reservoir
    sys.argv = ['run_reservoir.py', '--out-prefix', 'rq3_8m_reservoir']
    run_reservoir.main()
elif method == 'opq':
    import run_opq
    sys.argv = ['run_opq.py', '--out-prefix', 'rq3_8m_opq', '--m', '2']
    run_opq.main()
elif method == 'km10':
    import run_km_k_sweep
    sys.argv = ['run_km_k_sweep.py', '--out-prefix', 'rq3_8m_km_k', '--K', '10']
    run_km_k_sweep.main()
elif method == 'km50':
    import run_km_k_sweep
    sys.argv = ['run_km_k_sweep.py', '--out-prefix', 'rq3_8m_km_k', '--K', '50']
    run_km_k_sweep.main()
elif method == 'hilbert3d':
    import run_hilbert_dim
    sys.argv = ['run_hilbert_dim.py', '--out-prefix', 'rq3_8m_hilbert_dim', '--dim', '3']
    run_hilbert_dim.main()
elif method == 'hilbert4d':
    import run_hilbert_dim
    sys.argv = ['run_hilbert_dim.py', '--out-prefix', 'rq3_8m_hilbert_dim', '--dim', '4']
    run_hilbert_dim.main()
else:
    print(f'unknown method: {method}'); sys.exit(1)
