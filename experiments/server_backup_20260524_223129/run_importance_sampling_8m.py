#!/usr/bin/env python3
"""8M Importance Sampling wrapper (4 mode: p50/p200 × clip/noclip)."""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/online_weight")

import importance_sampling as imp

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
imp.DATASETS = [
    {
        "name": "DEEP_8M",
        "table": "partsupp_deep_10_phase7_8m_subset",
        "embed_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity_8m.parquet",
    }
]
imp.SELECTIVITIES = [0.10, 0.30]

sys.argv = ["importance_sampling.py", "--out-prefix", "rq3_8m_importance_sampling"]
imp.main()
