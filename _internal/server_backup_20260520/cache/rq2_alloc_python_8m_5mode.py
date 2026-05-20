#!/usr/bin/env python3
"""DEEP 8M RQ2 5-mode allocation × 5 sel — rq2_alloc_python.py wrapper.

Worker_L (5/7) 핸드오프 따른 측정:
- 5 mode (BERN/Equal/Prop/Neyman/Anti-Neyman) × 5 sel × 5 seed × 100 q = 12,500 rows
- 동일 seed 로 Anti-Neyman 결과는 기존과 일관 (cross-scale 보존)
- PG stratum_id 보존 (재 fit X), σ table 8M σ 활용
"""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache")
import rq2_alloc_python as rq2

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
rq2.DATASETS = [
    {
        "name": "DEEP_8M",
        "table": "partsupp_deep_10_phase7_8m_subset",
        "embed_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity_8m.parquet",
    }
]
rq2.SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]

sys.argv = ["rq2_alloc_python.py", "--out-prefix", "rq2_alloc_DEEP_8M_5mode"]
rq2.main()
