#!/usr/bin/env python3
"""통합 병렬 측정 캠페인 task 목록 생성 — 5/17 세션 (전권 위임).

paper-faithful 1단계 측정 전 portfolio:
  b1redo 80 (B1) + CaseA 1364 + CaseB 1364 + K-gran 156 = 2964 측정.

format (한 줄 = 한 측정): mode|cell|sf|sel|K|method   (method 는 B1 시 빈칸)
sf 오름차순 정렬 (light cell 먼저 → 병렬 runner 가 sf 버킷별 병렬도 적용).
"""
from pathlib import Path
import collections
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "_internal/cache/rq3/aggregated_v12_full.parquet"
OUT = Path(__file__).resolve().parent / "unified_tasks_5_17.txt"

df = pd.read_parquet(PARQUET)
df_cb = df[df["mode"] == "CaseB"].copy()
df_b1 = df[df["mode"] == "B1"].copy()
for d in (df_cb, df_b1):
    d["K_eff"] = d["K"].fillna(20).astype(int)
    d["sel_str"] = d["sel"].astype(float).map(lambda x: f"{x:g}")

rows = []  # (sf, mode, cell, sel, K, method)

# --- B1 재측정 (b1redo) — 80, 1단계 ---
for r in df_b1[["cell", "sf", "sel_str", "K_eff"]].drop_duplicates().itertuples():
    rows.append((int(r.sf), "B1", r.cell, r.sel_str, int(r.K_eff), ""))

# --- CaseA + CaseB(1단계 재측정) — 각 1364 ---
for r in df_cb[["cell", "sf", "sel_str", "K_eff", "method"]].drop_duplicates().itertuples():
    rows.append((int(r.sf), "CaseA", r.cell, r.sel_str, int(r.K_eff), r.method))
    rows.append((int(r.sf), "CaseB", r.cell, r.sel_str, int(r.K_eff), r.method))

# --- K granularity — 6 cell × K{10,30} × (B1 + 12 CaseB method), sel=0.01 — 156 ---
KGRAN = [("A5-scale-sf1", 1), ("A5-scale-sf10", 10), ("A2-Fig7", 10),
         ("A2-Fig9", 10), ("A1-DEEP", 100), ("A5-scale-sf100", 100)]
KGRAN_M12 = ["minibatch_partial", "gmm", "faiss_ivf", "zorder_morton", "skilling_hilbert",
             "rsvd", "ica_fastica", "cum_sqrtf", "lavallee_hidiroglou", "rabitq_strat",
             "mhist2", "pca1d"]
for cell, sf in KGRAN:
    for K in (10, 30):
        rows.append((sf, "B1", cell, "0.01", K, ""))
        for m in KGRAN_M12:
            rows.append((sf, "CaseB", cell, "0.01", K, m))

rows.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4], x[5]))
OUT.write_text("\n".join(f"{m}|{c}|{sf}|{s}|{k}|{me}" for sf, m, c, s, k, me in rows) + "\n")

print(f"unified tasks: {len(rows)}  → {OUT.name}")
print("by sf:", dict(sorted(collections.Counter(r[0] for r in rows).items())))
print("by mode:", dict(collections.Counter(r[1] for r in rows)))
