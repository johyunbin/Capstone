#!/usr/bin/env python3
"""8M KM20 + BERN wrapper — _measure_common.DATASETS/SELECTIVITIES patch 후 run_km20.main() 호출.

KM20: equal allocation (RQ3 oracle baseline)
BERN: bernoulli mode 동시 측정 (--include-bernoulli) — RQ3 분모용
"""
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

import run_km20  # from _measure_common import DATASETS — 이미 8M binding

sys.argv = ['run_km20.py', '--out-prefix', 'rq3_8m_km20', '--include-bernoulli']
run_km20.main()
