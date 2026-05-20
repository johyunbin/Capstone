#!/usr/bin/env python3
"""
SIFT D_target 5 selectivity 풀그리드 재계산.

기존 sift_dtarget_multsel.json 은 [0.01, 0.05, 0.5] 3점.
5/6 RQ1 보강 — [0.01, 0.05, 0.10, 0.30, 0.50] 5점으로 확장.

방법: 1.5M SIFT 벡터를 메모리 적재 → 100 query 각각 거리 정렬 → 5 quantile 추출.
같은 method 로 5 점 동시 계산 (consistency 보장).

산출:
  - cache/rq1/query_selectivity_sift_v2.parquet — 500 row (100 query × 5 sel)
  - cache/rq1/sift_dtarget_multsel_v2.json — 동일 정보 json
"""
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
TOTAL = 1_500_000


def kst():
    from datetime import datetime, timedelta, timezone
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def main():
    print(f"[{kst()}] load SIFT vectors")
    vecs_path = CACHE / "customer_sift_10_phase7_noidx_subset_vectors.npy"
    vecs = np.load(vecs_path).astype(np.float32, copy=False)  # (N, 128)
    print(f"[{kst()}]   shape={vecs.shape}, dtype={vecs.dtype}, mem={vecs.nbytes/1e9:.2f}GB")
    n = vecs.shape[0]
    assert n == TOTAL, f"unexpected N={n}"

    print(f"[{kst()}] load query_pool_sift")
    qp = pq.read_table(CACHE / "query_pool_sift.parquet").to_pandas()
    print(f"[{kst()}]   {len(qp)} queries")

    rows = []
    json_out = {"total": TOTAL, "queries": {f"{s}": [] for s in SELECTIVITIES}}

    for qi in range(len(qp)):
        emb = np.asarray(qp.iloc[qi]["embedding"], dtype=np.float32)
        # L2 distance to all 1.5M vectors
        diff = vecs - emb  # (N, 128)
        dists = np.sqrt(np.einsum("ij,ij->i", diff, diff))  # (N,)
        # quantiles per selectivity
        for s in SELECTIVITIES:
            true_card = int(round(s * n))
            d_target = float(np.partition(dists, true_card - 1)[true_card - 1])
            rows.append({
                "query_id": int(qp.iloc[qi]["query_id"]),
                "selectivity": s,
                "D_target": d_target,
                "true_cardinality": true_card,
            })
            json_out["queries"][f"{s}"].append({
                "query_id": int(qp.iloc[qi]["query_id"]),
                "D_target": d_target,
                "true_card": true_card,
                "selectivity": s,
            })
        if (qi + 1) % 10 == 0:
            print(f"[{kst()}]   query {qi+1}/100")

    df = pd.DataFrame(rows)
    out_pq = CACHE / "query_selectivity_sift_v2.parquet"
    df.to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq} ({len(df)} rows)")

    out_json = CACHE / "sift_dtarget_multsel_v2.json"
    with open(out_json, "w") as f:
        json.dump(json_out, f, indent=2)
    print(f"[{kst()}] saved {out_json}")

    print(f"\n--- D_target medians by selectivity ---")
    for s in SELECTIVITIES:
        med = df[df.selectivity == s].D_target.median()
        print(f"  s={s}: median D={med:.3f}, true_card={int(round(s*n)):,}")

    print(f"[{kst()}] done")


if __name__ == "__main__":
    main()
