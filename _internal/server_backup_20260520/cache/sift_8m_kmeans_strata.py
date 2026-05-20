#!/usr/bin/env python3
"""SIFT 8M Step 5+6 v2 — BIGANN raw read 직접 (PG fetch 우회) + KMeans K=20 fit
+ stratum_id PG UPDATE + σ table 갱신 + npy cache 저장.

v1 의 `cursor(name=...)` + autocommit=True 충돌 (NoActiveSqlTransaction) 회피 +
8M × 128 vector::real[] cast slow path 회피.
"""
import sys, time
from pathlib import Path
import numpy as np
import psycopg
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from datetime import datetime, timezone, timedelta

PORT = 55436; DB = 'wns41559'; USER = 'wns41559'
BIGANN = '/mnt/hdd0/home/kgh1030/vecdb_dataset/bigann/learn.100M.u8bin'
TABLE = 'customer_sift_8m_subset'
DIM = 128
N_TARGET = 8_000_000
N_STRATA = 20
LEARN_FRAC = 0.01
NPY_DIR = Path('/mnt/hdd0/home/capstone2026/cache/rq1')


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def read_u8bin_subset(path, n_target, dim):
    HEADER = 8
    with open(path, 'rb') as f:
        f.seek(HEADER)
        data = np.fromfile(f, dtype=np.uint8, count=n_target * dim).reshape(n_target, dim)
    return data


def main():
    print(f'[{kst()}] === SIFT 8M KMeans v2 START (BIGANN raw read) ===', flush=True)

    NPY_DIR.mkdir(parents=True, exist_ok=True)
    vecs_npy = NPY_DIR / f'{TABLE}_vectors.npy'
    keys_npy = NPY_DIR / f'{TABLE}_custkeys.npy'

    if vecs_npy.exists() and keys_npy.exists():
        print(f'[{kst()}] loading cached npy...', flush=True)
        all_vecs = np.load(vecs_npy)
        custkeys = np.load(keys_npy)
        print(f'[{kst()}]   cached: {len(all_vecs):,} × {all_vecs.shape[1]}', flush=True)
    else:
        print(f'[{kst()}] reading BIGANN raw {BIGANN}...', flush=True)
        t0 = time.time()
        vecs_u8 = read_u8bin_subset(BIGANN, N_TARGET, DIM)
        print(f'[{kst()}]   raw read {time.time()-t0:.1f}s, {vecs_u8.nbytes/1e9:.2f}GB', flush=True)
        t0 = time.time()
        all_vecs = (vecs_u8.astype(np.float32) / 255.0)
        del vecs_u8
        print(f'[{kst()}]   convert+normalize {time.time()-t0:.1f}s, {all_vecs.nbytes/1e9:.2f}GB', flush=True)
        custkeys = np.arange(N_TARGET, dtype=np.int64)
        np.save(vecs_npy, all_vecs)
        np.save(keys_npy, custkeys)
        print(f'[{kst()}]   saved npy cache', flush=True)

    # KMeans fit on learn subset
    n_learn = max(int(len(all_vecs) * LEARN_FRAC), N_STRATA * 50)
    rng = np.random.default_rng(42)
    learn_idx = rng.choice(len(all_vecs), size=n_learn, replace=False)
    print(f'[{kst()}] KMeans K={N_STRATA} fit on {n_learn:,} learn samples', flush=True)
    t0 = time.time()
    mbk = MiniBatchKMeans(n_clusters=N_STRATA, batch_size=4096, max_iter=100,
                           random_state=42, n_init=3, max_no_improvement=20).fit(all_vecs[learn_idx])
    print(f'[{kst()}]   fit elapsed {time.time()-t0:.1f}s', flush=True)

    print(f'[{kst()}] predict 8M stratum_id', flush=True)
    t0 = time.time()
    # batch predict to reduce peak memory
    stratum_ids = np.empty(len(all_vecs), dtype=np.int16)
    BATCH = 200_000
    for i in range(0, len(all_vecs), BATCH):
        stratum_ids[i:i+BATCH] = mbk.predict(all_vecs[i:i+BATCH]).astype(np.int16)
    print(f'[{kst()}]   predict elapsed {time.time()-t0:.1f}s', flush=True)
    sizes = np.bincount(stratum_ids, minlength=N_STRATA)
    print(f'[{kst()}]   cluster sizes: min={sizes.min()}, max={sizes.max()}, max/min={sizes.max()/sizes.min():.2f}', flush=True)

    # PG UPDATE via temp + COPY
    print(f'[{kst()}] PG UPDATE {TABLE}.stratum_id via temp+COPY', flush=True)
    t0 = time.time()
    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        cu.execute('CREATE TEMP TABLE _sift8m_strata (c_custkey BIGINT, sid SMALLINT)')
        with cu.copy('COPY _sift8m_strata (c_custkey, sid) FROM STDIN') as copy:
            for k, s in zip(custkeys.tolist(), stratum_ids.tolist()):
                copy.write_row((k, s))
        print(f'[{kst()}]   COPY temp loaded ({time.time()-t0:.1f}s)', flush=True)
        cu.execute(f'CREATE INDEX ON _sift8m_strata (c_custkey)')
        cu.execute(f'UPDATE {TABLE} t SET stratum_id = s.sid FROM _sift8m_strata s WHERE t.c_custkey = s.c_custkey')
        print(f'[{kst()}]   UPDATE done ({time.time()-t0:.1f}s)', flush=True)
        c.commit()
    print(f'[{kst()}]   total UPDATE elapsed {time.time()-t0:.1f}s', flush=True)

    # σ per stratum (PC1 std)
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
        print(f'[{kst()}]   σ table updated', flush=True)

    print(f'[{kst()}] === SIFT 8M KMeans v2 DONE ===', flush=True)


if __name__ == '__main__':
    main()
