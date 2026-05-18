#!/usr/bin/env python3
"""3-way 통합 측정 캠페인 task 목록 생성 — 5/17 세션 (전권 위임).

각 task = (cell, sel, K, method) 1건 → measure_paper_exact.py --mode 3way 가
B1·CaseA·CaseB 를 matched 동시 산출. 따라서 셋의 coverage·건수가 본질적으로 동일.

grid:
  base    — aggregated_v12_full.parquet 의 CaseB (cell,sel,K,method) 1364
  K-gran  — 6 cell × K{10,30} × 16 method, sel=0.01 — 192 (기존 portfolio 의 K10/30 보강)
  합계 ~1556 (중복 dedup).

format (한 줄 = 한 3-way 측정): cell|sf|sel|K|method   (sf 오름차순 정렬)
"""
from pathlib import Path
import collections
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "_internal/cache/rq3/aggregated_v12_full.parquet"
OUT = Path(__file__).resolve().parent / "tasks_3way_5_17.txt"

df = pd.read_parquet(PARQUET)
cb = df[df["mode"] == "CaseB"].copy()
cb["K_eff"] = cb["K"].fillna(20).astype(int)
cb["sel_str"] = cb["sel"].astype(float).map(lambda x: f"{x:g}")

grid = set()  # (sf, cell, sel, K, method)
for r in cb[["cell", "sf", "sel_str", "K_eff", "method"]].drop_duplicates().itertuples():
    grid.add((int(r.sf), r.cell, r.sel_str, int(r.K_eff), r.method))
n_base = len(grid)

# K-granularity 확장 — 6 cell × K{10,30} × 16 method (8 paradigm 대표), sel=0.01
KGRAN = [("A5-scale-sf1", 1), ("A5-scale-sf10", 10), ("A2-Fig7", 10),
         ("A2-Fig9", 10), ("A1-DEEP", 100), ("A5-scale-sf100", 100)]
M16 = ["minibatch_partial", "gmm", "faiss_ivf", "hilbert_real", "zorder_morton",
       "skilling_hilbert", "chao_weighted", "sparse_rp", "pca1d", "rsvd",
       "ica_fastica", "cum_sqrtf", "lavallee_hidiroglou", "rabitq_strat",
       "mhist2", "hyperloglog"]
for cell, sf in KGRAN:
    for K in (10, 30):
        for m in M16:
            grid.add((sf, cell, "0.01", K, m))

rows = sorted(grid)
OUT.write_text("\n".join(f"{c}|{sf}|{s}|{k}|{m}" for sf, c, s, k, m in rows) + "\n")

print(f"3-way tasks: {len(rows)}  (base {n_base} + K-gran 확장 {len(rows) - n_base})  → {OUT.name}")
print("by sf:", dict(sorted(collections.Counter(r[0] for r in rows).items())))
print("by K:", dict(sorted(collections.Counter(r[3] for r in rows).items())))
print("cell 수:", len(set(r[1] for r in rows)), " method 수:", len(set(r[4] for r in rows)))
