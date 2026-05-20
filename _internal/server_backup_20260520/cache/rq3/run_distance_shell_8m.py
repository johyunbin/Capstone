#!/usr/bin/env python3
"""8M Distance-Shell wrapper."""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/online_weight")

import distance_shell as ds

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
ds.DATASETS = [
    {
        "name": "DEEP_8M",
        "table": "partsupp_deep_10_phase7_8m_subset",
        "embed_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity_8m.parquet",
    }
]
ds.SELECTIVITIES = [0.10, 0.30]

sys.argv = ["distance_shell.py", "--out-prefix", "rq3_8m_distance_shell"]
ds.main()
