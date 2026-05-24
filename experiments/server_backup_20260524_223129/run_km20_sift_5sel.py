#!/usr/bin/env python3
"""SIFT 1.5M KM20 + BERN 5-sel canonical — Gap #1 보강 (5/7 manager session).

기존: sift_mid_sel.parquet 은 sel=0.10, 0.30 만 (3,000 cells).
보강: SIFT 5 sel × 5 seed × 100 q × 2 mode = 5,000 cells (re-measurement, 일관성).

mid-sel 재측정 포함 → 측정 일관성 + s=0.01/0.05/0.50 보강 동시.
"""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")

import _measure_common as mc

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
mc.DATASETS = [
    {
        "name": "SIFT",
        "table": "customer_sift_10_phase7_noidx_subset",
        "embed_col": "c_embedding",
        "vec_dim": 128,
        "query_pool": CACHE / "query_pool_sift.parquet",
        "query_sel": CACHE / "query_selectivity_sift_v2.parquet",
    }
]
mc.SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]

import run_km20

sys.argv = ["run_km20.py", "--out-prefix", "rq1_sift_km20_5sel", "--include-bernoulli"]
run_km20.main()
