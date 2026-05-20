#!/usr/bin/env python3
"""DEEP 8M RQ2 5-mode alloc wrapper — rq2_alloc_python.py monkey-patch."""
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
rq2.SELECTIVITIES = [0.10, 0.30]

sys.argv = ["rq2_alloc_python.py"]
rq2.main()
