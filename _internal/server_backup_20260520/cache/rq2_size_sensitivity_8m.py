#!/usr/bin/env python3
"""DEEP 8M sample size sensitivity wrapper — 4 sizes × 5 sel × BERN/Proportional."""
import sys
from pathlib import Path
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache')

import rq2_size_sensitivity as base

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
base.DATASETS = [
    {
        'name': 'DEEP_8M',
        'table': 'partsupp_deep_10_phase7_8m_subset',
        'embed_col': 'ps_embedding',
        'vec_dim': 96,
        'query_pool': CACHE / 'query_pool.parquet',
        'query_sel': CACHE / 'query_selectivity_8m.parquet',
    }
]

# 8M에서 stratum 크기가 더 크므로 cache_per_cluster 늘려야
base.CACHE_PER_CLUSTER = 1500  # max alloc 3000 × 0.5 partition share

sys.argv = ['rq2_size_sensitivity.py', '--out-prefix', 'rq2_size_sensitivity_8m']
base.main()
