#!/usr/bin/env python3
"""SIFT 1M subset — BIGANN raw read + KMeans K=20 + PG UPDATE + σ + npy cache."""
import time
from pathlib import Path
import numpy as np
import psycopg
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from datetime import datetime, timezone, timedelta

PORT = 55436; DB = 'wns41559'; USER = 'wns41559'
BIGANN = '/mnt/hdd0/home/kgh1030/vecdb_dataset/bigann/learn.100M.u8bin'
TABLE = 'customer_sift_1m_subset'
DIM = 128
N_TARGET = 1_000_000
N_STRATA = 20
LEARN_FRAC = 0.05  # 1M × 5% = 50K (8M 의 1% = 80K 와 비교 시 절대값 더 작음 → 5% 안전)
NPY_DIR = Path('/mnt/hdd0/home/capstone2026/cache/rq1')


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def main():
    print(f'[{kst()}] === SIFT 1M KMeans START ===', flush=True)
    NPY_DIR.mkdir(parents=True, exist_ok=True)
    vecs_npy = NPY_DIR / f'{TABLE}_vectors.npy'
    keys_npy = NPY_DIR / f'{TABLE}_custkeys.npy'

    if vecs_npy.exists() and keys_npy.exists():
        print(f'[{kst()}] loading cached npy', flush=True)
        all_vecs = np.load(vecs_npy)
        custkeys = np.load(keys_npy)
    else:
        print(f'[{kst()}] reading BIGANN raw', flush=True)
        HEADER = 8
        with open(BIGANN, 'rb') as f:
            f.seek(HEADER)
            vecs_u8 = np.fromfile(f, dtype=np.uint8, count=N_TARGET * DIM).reshape(N_TARGET, DIM)
        all_vecs = (vecs_u8.astype(np.float32) / 255.0)
        del vecs_u8
        custkeys = np.arange(N_TARGET, dtype=np.int64)
        np.save(vecs_npy, all_vecs)
        np.save(keys_npy, custkeys)
        print(f'[{kst()}]   saved npy cache', flush=True)
    print(f'[{kst()}]   {len(all_vecs):,} × {all_vecs.shape[1]}', flush=True)

    n_learn = max(int(len(all_vecs) * LEARN_FRAC), N_STRATA * 50)
    rng = np.random.default_rng(42)
    learn_idx = rng.choice(len(all_vecs), size=n_learn, replace=False)
    print(f'[{kst()}] KMeans K={N_STRATA} fit on {n_learn:,}', flush=True)
    t0 = time.time()
    mbk = MiniBatchKMeans(n_clusters=N_STRATA, batch_size=4096, max_iter=100,
                           random_state=42, n_init=3, max_no_improvement=20).fit(all_vecs[learn_idx])
    print(f'[{kst()}]   fit {time.time()-t0:.1f}s', flush=True)
    stratum_ids = mbk.predict(all_vecs).astype(np.int16)
    sizes = np.bincount(stratum_ids, minlength=N_STRATA)
    print(f'[{kst()}]   sizes min={sizes.min()}, max={sizes.max()}, ratio={sizes.max()/sizes.min():.2f}', flush=True)

    print(f'[{kst()}] PG UPDATE {TABLE}.stratum_id', flush=True)
    t0 = time.time()
    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        cu.execute('CREATE TEMP TABLE _sift1m_strata (c_custkey BIGINT, sid SMALLINT)')
        with cu.copy('COPY _sift1m_strata (c_custkey, sid) FROM STDIN') as copy:
            for k, s in zip(custkeys.tolist(), stratum_ids.tolist()):
                copy.write_row((k, s))
        cu.execute('CREATE INDEX ON _sift1m_strata (c_custkey)')
        cu.execute(f'UPDATE {TABLE} t SET stratum_id = s.sid FROM _sift1m_strata s WHERE t.c_custkey = s.c_custkey')
        c.commit()
    print(f'[{kst()}]   UPDATE {time.time()-t0:.1f}s', flush=True)

    print(f'[{kst()}] computing σ per stratum (PC1 std)', flush=True)
    sigmas = np.zeros(N_STRATA, dtype=np.float64)
    for sid in range(N_STRATA):
        mask = stratum_ids == sid
        if mask.sum() < 2:
            continue
        pc1 = PCA(n_components=1, random_state=42).fit_transform(all_vecs[mask])
        sigmas[sid] = float(pc1.std())
    print(f'[{kst()}]   σ avg={sigmas.mean():.4f}, min={sigmas.min():.4f}, max={sigmas.max():.4f}', flush=True)

    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        cu.execute(f"DELETE FROM vector_stratum_sigma WHERE table_name = '{TABLE}'")
        for sid, sig in enumerate(sigmas):
            cu.execute(f"INSERT INTO vector_stratum_sigma (table_name, stratum_id, sigma) VALUES ('{TABLE}', {sid}, {sig})")
        c.commit()
    print(f'[{kst()}] === SIFT 1M KMeans DONE ===', flush=True)


if __name__ == '__main__':
    main()
