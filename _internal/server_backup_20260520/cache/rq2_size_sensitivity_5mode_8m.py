#!/usr/bin/env python3
"""P3 — RQ2 size sensitivity 5-mode 확장 (Equal/Neyman/Anti-Neyman 추가).

기존 rq2_size_sensitivity_8m.py 는 BERN+Prop 만. 본 wrapper 는 5 mode 모두.
size sensitivity × allocation mode × DEEP_8M = 4 ssize × 5 mode × 5 sel ×
5 seed × 100 q = 50,000 cells.
"""
import sys
from pathlib import Path
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache')

import rq2_size_sensitivity as ss
ss.DATASETS = [
    {'name': 'DEEP_8M', 'table': 'partsupp_deep_10_phase7_8m_subset',
     'embed_col': 'ps_embedding', 'vec_dim': 96,
     'query_pool': Path('/mnt/hdd0/home/capstone2026/cache/rq1/query_pool.parquet'),
     'query_sel': Path('/mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_8m.parquet')}
]
ss.SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
ss.SAMPLE_SIZES = [100, 385, 1000, 3000]

# 5 mode 모두 (기본 wrapper 가 BERN+Prop 만 → ALL_MODES 사용 강제)
sys.argv = ['rq2_size_sensitivity.py', '--out-prefix', 'rq2_size_sensitivity_8m_5mode',
            '--modes', 'bernoulli', 'equal', 'proportional', 'neyman', 'anti_neyman']
ss.main()
