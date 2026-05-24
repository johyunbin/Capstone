#!/usr/bin/env python3
"""8M KDE-pilot wrapper — DATASETS + SELECTIVITIES patch 후 main() 호출."""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/kde")

import kde_pilot as kp

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
kp.DATASETS = [
    {
        "name": "DEEP_8M",
        "table": "partsupp_deep_10_phase7_8m_subset",
        "embed_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity_8m.parquet",
    }
]
kp.SELECTIVITIES = [0.10, 0.30]

# argparse default 와 호환되게
sys.argv = ["kde_pilot.py", "--out-prefix", "rq3_8m_kde_pilot"]
kp.main()
