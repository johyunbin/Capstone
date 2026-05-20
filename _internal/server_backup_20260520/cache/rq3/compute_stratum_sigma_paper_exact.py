#!/usr/bin/env python3
"""
RQ2 paper exact 사전 계산 — KM20 cluster σ_j (vector_stratum_sigma).

paper Fig 13 sf=100 환경 (partsupp_deep_100, partsupp_sift_100, partsupp_fb_100)
의 KM20 cluster 별 σ_j 빌드.

σ_j 정의: σ_j² = mean_q[ p_{j,q} × (1 - p_{j,q}) ]
- p_{j,q} = (cluster j 안에서 query q 결과에 hit 한 row 수) / N_j
- query 풀 100개 × selectivity 0.1 D_target 기준 (mid selectivity)

NPY cache 활용 (PG query 회피, 80M rows mmap):
- /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_{deep,sift,fb}_100_vectors.npy
- /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_{deep,sift,fb}_100_strata.npy
- /mnt/hdd0/home/capstone2026/cache/rq1/query_pool_{DEEP,SIFT,SSN}_sf100.parquet

PG INSERT vector_stratum_sigma (table_name, stratum_id, sigma).

서버에서 실행: cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 compute_stratum_sigma_paper_exact.py
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import psycopg
import pyarrow.parquet as pq

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
SF_LIST = [100]  # paper exact (Fig 13)
N_STRATA = 20  # KM20
SEL_FOR_SIGMA = 0.1  # mid selectivity D_target (paper Fig 13)
N_QUERIES = 100  # query pool

DATASETS = [
    {"name": "DEEP", "alias": "DEEP", "table_fmt": "partsupp_deep_{sf}", "dim": 96},
    {"name": "SIFT", "alias": "SIFT", "table_fmt": "partsupp_sift_{sf}", "dim": 128},
    {"name": "SimSearchNet++", "alias": "SSN", "table_fmt": "partsupp_fb_{sf}", "dim": 256},
]


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def compute_sigmas_for_dataset(table: str, alias: str, sf: int, dim: int) -> dict[int, float]:
    """KM20 cluster σ_j 계산 — NPY mmap, query 100개, sel=0.1 D_target."""
    vecs_path = CACHE / f"{table}_vectors.npy"
    strata_path = CACHE / f"{table}_strata.npy"
    qp_path = CACHE / f"query_pool_{alias}_sf{sf}.parquet"
    qs_path = CACHE / f"query_selectivity_{alias}_sf{sf}.parquet"

    for p in (vecs_path, strata_path, qp_path, qs_path):
        if not p.exists():
            print(f"[{kst()}]   ⚠️ missing: {p}")
            return {}

    t0 = time.time()
    vecs = np.load(vecs_path, mmap_mode="r")
    strata = np.load(strata_path)
    print(f"[{kst()}]   mmap {len(vecs):,} × {vecs.shape[1]}d, strata {len(strata):,} ({time.time()-t0:.1f}s)")

    qp = pq.read_table(qp_path).to_pandas().reset_index(drop=True)
    qs = pq.read_table(qs_path).to_pandas()
    qs_sel = qs[np.isclose(qs["selectivity"], SEL_FOR_SIGMA)].sort_values("query_id").head(N_QUERIES)
    if len(qs_sel) == 0:
        print(f"[{kst()}]   ⚠️ no queries at sel={SEL_FOR_SIGMA}")
        return {}
    qvecs = np.stack([
        np.asarray(qp.iloc[int(r["query_id"])]["embedding"], dtype=np.float32)
        for _, r in qs_sel.iterrows()
    ])
    d_targets = qs_sel["D_target"].values.astype(np.float32)
    print(f"[{kst()}]   {len(qvecs)} queries (sel={SEL_FOR_SIGMA})")

    sigmas: dict[int, float] = {}
    for sid in range(N_STRATA):
        mask = (strata == sid)
        N_i = int(mask.sum())
        if N_i == 0:
            sigmas[sid] = 0.0
            continue
        # cluster vectors materialize (mmap → contiguous array for fast distance)
        # cluster N_i ~ 4M rows / 80M total. memory ~1.5GB max (256d × 4M × 4B).
        cluster_vecs = np.ascontiguousarray(vecs[mask])
        # per-query hit count (chunked to avoid 4M×100×dim memory blowup)
        chunk = 200_000
        p_var_acc = 0.0
        for q_idx in range(len(qvecs)):
            qvec = qvecs[q_idx]
            D = float(d_targets[q_idx])
            hits = 0
            for cs in range(0, N_i, chunk):
                ce = min(cs + chunk, N_i)
                d = np.linalg.norm(cluster_vecs[cs:ce] - qvec, axis=1)
                hits += int((d < D).sum())
            p_iq = hits / N_i
            p_var_acc += p_iq * (1.0 - p_iq)
        sigma_sq = p_var_acc / len(qvecs)
        sigmas[sid] = float(np.sqrt(sigma_sq))
        print(f"[{kst()}]     stratum {sid:2d}: N={N_i:>10,} σ={sigmas[sid]:.6f}")
        del cluster_vecs  # free RAM
    return sigmas


def main():
    conn = psycopg.connect(host="/tmp", port=55436, dbname="wns41559", user="wns41559",
                           autocommit=False)
    cur = conn.cursor()
    print(f"[{kst()}] === RQ2 paper exact σ_j 빌드 (sf=100, KM20, sel={SEL_FOR_SIGMA}) ===")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vector_stratum_sigma (
            table_name TEXT,
            stratum_id SMALLINT,
            sigma DOUBLE PRECISION,
            n_i BIGINT,
            sel_used DOUBLE PRECISION,
            PRIMARY KEY (table_name, stratum_id)
        );
    """)
    conn.commit()

    cur.execute("SELECT table_name, COUNT(*) FROM vector_stratum_sigma GROUP BY table_name ORDER BY table_name")
    before = cur.fetchall()
    print(f"[{kst()}] BEFORE state: {before}")

    for ds in DATASETS:
        for sf in SF_LIST:
            table = ds["table_fmt"].format(sf=sf)
            t_ds = time.time()
            print(f"[{kst()}] === {ds['name']} sf={sf} ({table}) ===")
            sigmas = compute_sigmas_for_dataset(table, ds["alias"], sf, ds["dim"])
            if not sigmas:
                print(f"[{kst()}]   skip {table}")
                continue
            cur.execute("DELETE FROM vector_stratum_sigma WHERE table_name = %s", (table,))
            for sid, sigma in sigmas.items():
                strata = np.load(CACHE / f"{table}_strata.npy")
                n_i = int((strata == sid).sum())
                cur.execute(
                    "INSERT INTO vector_stratum_sigma (table_name, stratum_id, sigma, n_i, sel_used) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (table, sid, sigma, n_i, SEL_FOR_SIGMA),
                )
            conn.commit()
            print(f"[{kst()}]   ✓ INSERT {len(sigmas)} rows for {table} ({time.time()-t_ds:.1f}s)")

    cur.execute("SELECT table_name, COUNT(*) FROM vector_stratum_sigma GROUP BY table_name ORDER BY table_name")
    after = cur.fetchall()
    print(f"[{kst()}] AFTER state: {after}")

    conn.close()
    print(f"[{kst()}] === DONE ===")


if __name__ == "__main__":
    main()
