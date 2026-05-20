#!/usr/bin/env python3
"""SIFT 8M dataset build — BIGANN learn.100M 에서 8M extract + PG 적재.

Step 1: read BIGANN learn.100M.u8bin (12.8GB, 100M × 128-dim uint8)
Step 2: extract 8M deterministic (seed=42)
Step 3: convert uint8 → float32 normalize ([0,1] / 255)
Step 4: PG 적재 customer_sift_8m_subset (c_custkey int, c_embedding vector(128), stratum_id smallint=0)
Step 5: KMeans K=20 fit + stratum_id 부여
"""
import sys
import time
from pathlib import Path
import numpy as np
import psycopg
from datetime import datetime, timezone, timedelta

PORT = 55436; DB = 'wns41559'; USER = 'wns41559'
BIGANN = '/mnt/hdd0/home/kgh1030/vecdb_dataset/bigann/learn.100M.u8bin'
DIM = 128
N_TARGET = 8_000_000
TABLE = 'customer_sift_8m_subset'

def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

def read_u8bin_header(path):
    """big-ann u8bin format: int32 N, int32 D, then N×D uint8."""
    with open(path, 'rb') as f:
        N = int.from_bytes(f.read(4), 'little')
        D = int.from_bytes(f.read(4), 'little')
    return N, D

def read_u8bin_subset(path, n_target, dim, seed=42):
    """Read first n_target rows (deterministic). RandomDeterministic seeds 가능하지만
    contiguous 가 disk read 효율적."""
    HEADER = 8
    with open(path, 'rb') as f:
        f.seek(HEADER)
        # contiguous read — first 8M
        data = np.fromfile(f, dtype=np.uint8, count=n_target * dim).reshape(n_target, dim)
    return data

def main():
    print(f'[{kst()}] === SIFT 8M build START ===')

    # Step 1+2: read BIGANN learn.100M, extract 8M
    print(f'[{kst()}] reading {BIGANN}...')
    N, D = read_u8bin_header(BIGANN)
    print(f'[{kst()}]   header: N={N}, D={D}')
    assert D == DIM, f'expected D={DIM}, got {D}'
    assert N >= N_TARGET, f'need {N_TARGET}, have {N}'

    t0 = time.time()
    vecs_u8 = read_u8bin_subset(BIGANN, N_TARGET, DIM, seed=42)
    print(f'[{kst()}]   read {N_TARGET:,} × {DIM} uint8 in {time.time()-t0:.1f}s, {vecs_u8.nbytes/1e9:.2f} GB')

    # Step 3: convert uint8 → float32 normalize
    t0 = time.time()
    vecs = (vecs_u8.astype(np.float32) / 255.0)  # [0,1] normalize
    print(f'[{kst()}]   convert + normalize {time.time()-t0:.1f}s')

    # Step 4: PG 적재
    print(f'[{kst()}] PG 적재 {TABLE}...')
    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        # drop existing
        cu.execute(f'DROP TABLE IF EXISTS {TABLE}')
        cu.execute(f"""
            CREATE TABLE {TABLE} (
                c_custkey BIGINT PRIMARY KEY,
                c_embedding vector({DIM}),
                stratum_id SMALLINT
            )
        """)
        c.commit()
        print(f'[{kst()}]   table created')

        # Bulk insert via COPY
        t0 = time.time()
        with cu.copy(f'COPY {TABLE} (c_custkey, c_embedding) FROM STDIN') as copy:
            for i in range(N_TARGET):
                vec_str = '[' + ','.join(f'{x:.6f}' for x in vecs[i]) + ']'
                copy.write_row((i, vec_str))
                if (i + 1) % 500_000 == 0:
                    print(f'[{kst()}]   COPY progress: {i+1:,}/{N_TARGET:,} ({(time.time()-t0):.1f}s)')
        c.commit()
        print(f'[{kst()}]   COPY done in {time.time()-t0:.1f}s')

        # Verify
        cu.execute(f'SELECT count(*) FROM {TABLE}')
        n_rows = cu.fetchone()[0]
        print(f'[{kst()}]   verified n_rows={n_rows:,}')

    print(f'[{kst()}] === SIFT 8M build PG INSERT DONE ===')

if __name__ == '__main__':
    main()
