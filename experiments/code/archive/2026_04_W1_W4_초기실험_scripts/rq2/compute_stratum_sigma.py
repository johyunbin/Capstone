#!/usr/bin/env python3
"""
RQ2 사전 계산 — KM20 cluster 별 σ_i (Neyman Allocation 용).

σ_i 정의: σ_i² = mean_q[ p_{i,q} × (1 - p_{i,q}) ]
- p_{i,q} = (cluster i 안에서 query q 결과에 hit 한 row 수) / N_i
- query 풀 100개 × selectivity 0.1 D_target 기준
- single σ_i across selectivity (limitation: 더 정교한 query-aware Neyman 은 RQ3 영역)

PG 테이블 vector_stratum_sigma 에 (table_name, stratum_id, sigma) 저장.
서버에서 직접 실행: python3 -u compute_stratum_sigma.py
"""
import psycopg
import pyarrow.parquet as pq
import numpy as np
import time
from pathlib import Path

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")

DATASETS = [
    {
        "name": "DEEP",
        "table": "partsupp_deep_10_subset_1m",
        "vec_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity.parquet",
        "qid_col": None,  # row index 사용
    },
    {
        "name": "SIFT",
        "table": "customer_sift_10_phase7_noidx_subset",
        "vec_col": "c_embedding",
        "vec_dim": 128,
        "query_pool": CACHE / "query_pool_sift.parquet",
        "query_sel": CACHE / "query_selectivity_sift_v2.parquet",
        "qid_col": "query_id",
    },
]

SEL_FOR_SIGMA = 0.1  # mid selectivity 의 D_target 사용

def kst():
    import datetime
    t = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    return t.strftime("%H:%M:%S")

def emb_to_pgvec(emb):
    return "[" + ",".join(f"{float(x):.6f}" for x in emb) + "]"

def main():
    conn = psycopg.connect(host='/tmp', port=55436, dbname='wns41559', user='wns41559', autocommit=False)
    cur = conn.cursor()

    print(f"[{kst()}] === RQ2 σ_i 사전 계산 (vector_stratum_sigma 테이블) ===")

    # 테이블 생성 + 초기화
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
    cur.execute("DELETE FROM vector_stratum_sigma")
    conn.commit()
    print(f"[{kst()}] table ready, cleared")

    for ds in DATASETS:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        # cluster 별 N_i
        cur.execute(f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} GROUP BY stratum_id ORDER BY stratum_id")
        N_dict = dict(cur.fetchall())
        n_strata = max(N_dict.keys()) + 1
        N_arr = np.array([N_dict.get(i, 0) for i in range(n_strata)], dtype=float)
        print(f"  N_i = {N_arr.astype(int).tolist()}  (sum={int(N_arr.sum())})")

        # query pool 로드
        qp = pq.read_table(ds['query_pool']).to_pandas().reset_index(drop=True)
        qs = pq.read_table(ds['query_sel']).to_pandas()
        qs_mid = qs[np.isclose(qs['selectivity'], SEL_FOR_SIGMA)].set_index('query_id')
        print(f"  loaded {len(qp)} queries, {len(qs_mid)} selectivity rows at sel={SEL_FOR_SIGMA}")

        # 각 query 마다 cluster 별 hit count
        n_q = min(len(qp), len(qs_mid))
        p_iq = np.zeros((n_q, n_strata))
        t0 = time.time()
        for q_idx in range(n_q):
            qid = q_idx if ds['qid_col'] is None else int(qp.iloc[q_idx][ds['qid_col']])
            if qid not in qs_mid.index:
                continue
            D_target = float(qs_mid.loc[qid, 'D_target'])
            qvec = emb_to_pgvec(qp.iloc[q_idx]['embedding'])

            # l2_distance(a, b) 함수 호출로 KNN-plan / hook trigger 우회
            cur.execute(
                f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} "
                f"WHERE l2_distance({ds['vec_col']}, %s::vector) < %s "
                f"GROUP BY stratum_id",
                (qvec, D_target)
            )
            hits = dict(cur.fetchall())
            for sid in range(n_strata):
                h = hits.get(sid, 0)
                N = N_arr[sid]
                p_iq[q_idx, sid] = (h / N) if N > 0 else 0.0
            if (q_idx + 1) % 25 == 0:
                el = time.time() - t0
                print(f"    progress {q_idx+1}/{n_q} ({el:.1f}s)")

        elapsed = time.time() - t0
        print(f"  done {n_q} queries in {elapsed:.1f}s")

        # σ_i = sqrt(mean_q[p × (1-p)])
        bern_var = p_iq * (1 - p_iq)
        sigma = np.sqrt(bern_var.mean(axis=0))
        p_mean = p_iq.mean(axis=0)
        print(f"  p_i (mean hit rate per cluster):")
        for i in range(n_strata):
            print(f"    cluster {i:2d}  N={int(N_arr[i]):>7}  p_i={p_mean[i]:.4f}  σ_i={sigma[i]:.4f}")

        # INSERT
        for sid in range(n_strata):
            cur.execute(
                "INSERT INTO vector_stratum_sigma (table_name, stratum_id, sigma, n_i, sel_used) "
                "VALUES (%s, %s, %s, %s, %s)",
                (ds['table'], sid, float(sigma[sid]), int(N_arr[sid]), SEL_FOR_SIGMA)
            )
        conn.commit()
        print(f"  inserted {n_strata} rows for {ds['table']}")

    # 최종 확인
    print(f"\n[{kst()}] === vector_stratum_sigma 최종 테이블 ===")
    cur.execute("SELECT table_name, count(*), avg(sigma), min(sigma), max(sigma) FROM vector_stratum_sigma GROUP BY table_name ORDER BY table_name")
    for row in cur.fetchall():
        print(f"  {row[0]}: n={row[1]}, avg σ={row[2]:.4f}, min={row[3]:.4f}, max={row[4]:.4f}")

    cur.close()
    conn.close()
    print(f"[{kst()}] === done ===")

if __name__ == "__main__":
    main()
