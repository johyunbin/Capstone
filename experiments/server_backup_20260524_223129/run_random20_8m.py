#!/usr/bin/env python3
"""8M RANDOM20 wrapper — _measure_common.DATASETS/SELECTIVITIES patch 후 run_random20.main() 호출."""
import sys
from pathlib import Path

sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache/rq3')

import _measure_common as mc

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
mc.DATASETS = [
    {
        'name': 'DEEP_8M',
        'table': 'partsupp_deep_10_phase7_8m_subset',
        'embed_col': 'ps_embedding',
        'vec_dim': 96,
        'query_pool': CACHE / 'query_pool.parquet',
        'query_sel': CACHE / 'query_selectivity_8m.parquet',
    }
]
mc.SELECTIVITIES = [0.10, 0.30]

import run_random20  # from _measure_common import DATASETS — 이미 8M binding

sys.argv = ['run_random20.py', '--out-prefix', 'rq3_8m_random20']
run_random20.main()
