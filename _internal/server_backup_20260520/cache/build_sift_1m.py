#!/usr/bin/env python3
"""SIFT 1M subset (Option 1) — BIGANN learn.100M 첫 1M extract + PG 적재.

build_sift_8m.py 과 동일 로직, N_TARGET=1M.

용도: DEEP 1M vs SIFT 1M (scale-matched 2x2) + DEEP 8M vs SIFT 8M cross-scale.
"""
import time
from pathlib import Path
import numpy as np
import psycopg
from datetime import datetime, timezone, timedelta

PORT = 55436; DB = 'wns41559'; USER = 'wns41559'
BIGANN = '/mnt/hdd0/home/kgh1030/vecdb_dataset/bigann/learn.100M.u8bin'
DIM = 128
N_TARGET = 1_000_000
TABLE = 'customer_sift_1m_subset'


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def main():
    print(f'[{kst()}] === SIFT 1M build START ===', flush=True)

    HEADER = 8
    with open(BIGANN, 'rb') as f:
        N = int.from_bytes(f.read(4), 'little')
        D = int.from_bytes(f.read(4), 'little')
    assert D == DIM and N >= N_TARGET
    print(f'[{kst()}]   header N={N} D={D}', flush=True)

    t0 = time.time()
    with open(BIGANN, 'rb') as f:
        f.seek(HEADER)
        vecs_u8 = np.fromfile(f, dtype=np.uint8, count=N_TARGET * DIM).reshape(N_TARGET, DIM)
    print(f'[{kst()}]   read {N_TARGET:,}×{DIM} u8 in {time.time()-t0:.1f}s', flush=True)
    vecs = (vecs_u8.astype(np.float32) / 255.0)
    del vecs_u8

    print(f'[{kst()}] PG 적재 {TABLE}', flush=True)
    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        cu.execute(f'DROP TABLE IF EXISTS {TABLE}')
        cu.execute(f'CREATE TABLE {TABLE} (c_custkey BIGINT PRIMARY KEY, c_embedding vector({DIM}), stratum_id SMALLINT)')
        c.commit()
        t0 = time.time()
        with cu.copy(f'COPY {TABLE} (c_custkey, c_embedding) FROM STDIN') as copy:
            for i in range(N_TARGET):
                vec_str = '[' + ','.join(f'{x:.6f}' for x in vecs[i]) + ']'
                copy.write_row((i, vec_str))
                if (i + 1) % 200_000 == 0:
                    print(f'[{kst()}]   COPY {i+1:,}/{N_TARGET:,} ({time.time()-t0:.1f}s)', flush=True)
        c.commit()
        print(f'[{kst()}]   COPY done {time.time()-t0:.1f}s', flush=True)
        cu.execute(f'SELECT count(*) FROM {TABLE}')
        n = cu.fetchone()[0]
        print(f'[{kst()}]   verified n_rows={n:,}', flush=True)

    print(f'[{kst()}] === SIFT 1M build PG INSERT DONE ===', flush=True)


if __name__ == '__main__':
    main()
