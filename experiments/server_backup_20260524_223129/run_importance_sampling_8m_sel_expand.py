#!/usr/bin/env python3
"""8M importance_sampling sel 5단계 확장 wrapper (sel 0.01/0.05/0.50)."""
import sys
from pathlib import Path
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3')
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3/online_weight')

import importance_sampling as m

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
m.DATASETS = [
    {
        'name': 'DEEP_8M',
        'table': 'partsupp_deep_10_phase7_8m_subset',
        'embed_col': 'ps_embedding',
        'vec_dim': 96,
        'query_pool': CACHE / 'query_pool.parquet',
        'query_sel': CACHE / 'query_selectivity_8m.parquet',
    }
]
m.SELECTIVITIES = [0.01, 0.05, 0.50]
sys.argv = ['importance_sampling.py', '--out-prefix', 'rq3_8m_importance_sampling_sel_expand']
m.main()
