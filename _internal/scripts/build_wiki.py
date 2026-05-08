#!/usr/bin/env python3
"""WIKI raw extract → partsupp_wiki_{1,10,100} PG load (800K/8M/80M × 768d).

Sources (kgh1030):
  /mnt/BDAI_NAS/kgh1030/vecdb_dataset/wiki-all/
    1M/base.1M.fbin           (3 GB,   1M × 768d float32)
    10M/base.10M.fbin         (~30 GB, 10M × 768d float32)
    full_88M/base.88M.fbin    (268 GB, 88M × 768d float32)

Target row counts (TPC-H natural scaling): sf1=800K, sf10=8M, sf100=80M.

Usage:
  python build_wiki.py --sf 1     # → partsupp_wiki_1 (800K, from 1M raw first 800K)
  python build_wiki.py --sf 10    # → partsupp_wiki_10 (8M, from 10M raw first 8M)
  python build_wiki.py --sf 100   # → partsupp_wiki_100 (80M, from 88M raw first 80M)
"""
import argparse
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
import numpy as np
import psycopg

WIKI_ROOT = Path('/mnt/BDAI_NAS/kgh1030/vecdb_dataset/wiki-all')
SF_SOURCE = {
    1:   (WIKI_ROOT / '1M' / 'base.1M.fbin', 800_000),
    10:  (WIKI_ROOT / '10M' / 'base.10M.fbin', 8_000_000),
    100: (WIKI_ROOT / 'full_88M' / 'base.88M.fbin', 80_000_000),
}
DIM = 768
NPY_DIR = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
PG_PORT = 55435
DB = 'wns41559'
USER = 'wns41559'


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def read_fbin_prefix(path: Path, n_target: int, dim: int):
    """fbin format: 8-byte header (n, d as int32) + float32 data."""
    print(f'[{kst()}] reading first {n_target:,} rows from {path}', flush=True)
    with open(path, 'rb') as f:
        header = np.frombuffer(f.read(8), dtype=np.int32)
        n_total, d_file = int(header[0]), int(header[1])
        if d_file != dim:
            raise SystemExit(f'dim mismatch: file={d_file}, expected={dim}')
        if n_total < n_target:
            raise SystemExit(f'file has {n_total:,} rows, need {n_target:,}')
        n_bytes = n_target * dim * 4
        print(f'[{kst()}]   file header: n={n_total:,}, d={d_file}; reading {n_bytes/1e9:.1f} GB', flush=True)
        t0 = time.time()
        buf = f.read(n_bytes)
        vecs = np.frombuffer(buf, dtype=np.float32).reshape(n_target, dim).copy()
    print(f'[{kst()}]   read {n_target:,} × {dim} in {time.time()-t0:.1f}s', flush=True)
    return vecs


def create_pg_table(table: str, dim: int, n: int):
    print(f'[{kst()}] PG create table {table}', flush=True)
    with psycopg.connect(host='/tmp', port=PG_PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f'DROP TABLE IF EXISTS {table}')
        # Use composite PK ps_partkey + ps_suppkey to mirror partsupp schema (4 suppkey per partkey)
        cu.execute(f"""
            CREATE TABLE {table} (
                ps_partkey BIGINT NOT NULL,
                ps_suppkey BIGINT NOT NULL,
                ps_availqty INTEGER,
                ps_supplycost NUMERIC,
                ps_comment TEXT,
                ps_embedding vector({dim}),
                stratum_id SMALLINT,
                PRIMARY KEY (ps_partkey, ps_suppkey)
            )
        """)
    print(f'[{kst()}]   table created', flush=True)


def copy_to_pg(table: str, vecs: np.ndarray):
    """COPY rows to PG. Use synthetic ps_partkey/ps_suppkey to mirror partsupp scaling.

    For sf1 (800K rows): partkey 1..200K, suppkey ∈ {p, p+10K, p+20K, p+30K} (4 suppkey per partkey).
    For sf10 (8M): partkey 1..2M, similar.
    For sf100 (80M): partkey 1..20M, similar.
    """
    n = len(vecs)
    n_partkeys = n // 4  # 4 suppliers per part in TPC-H
    print(f'[{kst()}] COPY {n:,} rows to {table} (partkeys 1..{n_partkeys:,})', flush=True)
    t0 = time.time()
    with psycopg.connect(host='/tmp', port=PG_PORT, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        with cu.copy(f'COPY {table} (ps_partkey, ps_suppkey, ps_embedding) FROM STDIN') as copy:
            for i in range(n):
                pk = (i % n_partkeys) + 1
                sk_offset = i // n_partkeys  # 0, 1, 2, 3
                sk = pk + sk_offset * n_partkeys
                # vector format for pgvector: '[v1,v2,...]'
                vec_str = '[' + ','.join(f'{v:.6f}' for v in vecs[i]) + ']'
                copy.write_row((pk, sk, vec_str))
                if (i + 1) % 1_000_000 == 0:
                    print(f'[{kst()}]     copied {i+1:,} ({time.time()-t0:.0f}s)', flush=True)
        c.commit()
    print(f'[{kst()}]   COPY done in {time.time()-t0:.1f}s', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sf', type=int, required=True, choices=[1, 10, 100])
    args = ap.parse_args()

    src_path, n_target = SF_SOURCE[args.sf]
    table = f'partsupp_wiki_{args.sf}'
    print(f'[{kst()}] === WIKI sf{args.sf} → {table} ({n_target:,} × {DIM}d) ===', flush=True)

    NPY_DIR.mkdir(parents=True, exist_ok=True)
    npy_path = NPY_DIR / f'{table}_vectors.npy'

    # Read raw + save NPY (skip if NPY exists)
    if npy_path.exists():
        vecs = np.load(npy_path)
        if len(vecs) != n_target or vecs.shape[1] != DIM:
            print(f'[{kst()}]   stale NPY (shape {vecs.shape}, want ({n_target},{DIM})) — refetch', flush=True)
            vecs = read_fbin_prefix(src_path, n_target, DIM)
            np.save(npy_path, vecs)
        else:
            print(f'[{kst()}]   loaded NPY cache: {vecs.shape}', flush=True)
    else:
        vecs = read_fbin_prefix(src_path, n_target, DIM)
        np.save(npy_path, vecs)
        print(f'[{kst()}]   saved {npy_path.name}', flush=True)

    # PG load
    create_pg_table(table, DIM, n_target)
    copy_to_pg(table, vecs)

    # Verify
    with psycopg.connect(host='/tmp', port=PG_PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f'SELECT COUNT(*) FROM {table}')
        n_pg = cu.fetchone()[0]
    print(f'[{kst()}]   PG verify: {n_pg:,} rows', flush=True)
    if n_pg != n_target:
        raise SystemExit(f'load mismatch: NPY={n_target:,} vs PG={n_pg:,}')

    print(f'[{kst()}] === WIKI sf{args.sf} DONE ===', flush=True)


if __name__ == '__main__':
    main()
