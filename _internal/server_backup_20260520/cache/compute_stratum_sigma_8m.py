#!/usr/bin/env python3
"""DEEP 8M sigma 사전 계산 wrapper — compute_stratum_sigma.py monkey-patch."""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache")
import compute_stratum_sigma as csm

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
csm.DATASETS = [
    {
        "name": "DEEP_8M",
        "table": "partsupp_deep_10_phase7_8m_subset",
        "vec_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity_8m.parquet",
        "qid_col": None,
    }
]

# main()이 SELECTIVITIES 를 사용한다면 8M sel 로 override
if hasattr(csm, "SELECTIVITIES"):
    csm.SELECTIVITIES = [0.10, 0.30]

# 기존 main() 호출
csm.main()
