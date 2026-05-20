#!/usr/bin/env python3
"""DEEP 8M KM20 + BERN sel_expand — Gap #3 보강 (5/7 manager session).

기존: rq3_8m_km20.parquet 은 sel=0.10, 0.30 만 (2,000 cells).
보강: sel=0.01, 0.05, 0.50 × 5 seed × 100 q × 2 mode = 3,000 cells.

→ 8M KM20 baseline 5 sel 완전성 확보 (recovery_rate denominator 완전 측정).
"""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")

import _measure_common as mc

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
mc.DATASETS = [
    {
        "name": "DEEP_8M",
        "table": "partsupp_deep_10_phase7_8m_subset",
        "embed_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity_8m.parquet",
    }
]
mc.SELECTIVITIES = [0.01, 0.05, 0.50]

import run_km20

sys.argv = ["run_km20.py", "--out-prefix", "rq3_8m_km20_sel_expand", "--include-bernoulli"]
run_km20.main()
