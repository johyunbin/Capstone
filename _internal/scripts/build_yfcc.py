#!/usr/bin/env python3
"""YFCC 1280d → PCA 192d → partsupp_yfcc_{1,10,100} PG load.

Source: /mnt/hdd0/home/capstone2026/cache/yfcc_full/yfcc100m_vecs.fbin
        (505 GB, 98.7M × 1280d float32, BigANN public release)

Pipeline:
  1. Read first 1M rows for PCA fit (random sample better but seq is fine for first pass)
  2. PCA fit 1280 → 192 (sklearn PCA, n_components=192)
  3. PCA transform on first N rows (N = 800K / 8M / 80M depending on sf)
  4. Save 192d float32 NPY + load to PG as partsupp_yfcc_{sf}

Usage:
  python build_yfcc.py --sf 1     # 800K
  python build_yfcc.py --sf 10    # 8M
  python build_yfcc.py --sf 100   # 80M
  python build_yfcc.py --fit-only # just fit + save PCA basis (call once before extracts)
"""
import argparse
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
import numpy as np
import psycopg
from sklearn.decomposition import PCA
import joblib

YFCC_RAW = Path('/mnt/hdd0/home/capstone2026/cache/yfcc_full/yfcc100m_vecs.fbin')
PCA_BASIS_PATH = Path('/mnt/hdd0/home/capstone2026/cache/yfcc_full/pca_1280_to_192.joblib')
SRC_DIM = 1280
TGT_DIM = 192
N_TOTAL = 98_735_605
PCA_FIT_N = 1_000_000
NPY_DIR = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
PG_PORT = 55435
DB = 'wns41559'
USER = 'wns41559'
SF_ROWS = {1: 800_000, 10: 8_000_000, 100: 80_000_000}


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def read_fbin_prefix(path: Path, n_rows: int, dim: int) -> np.ndarray:
    """fbin: 8-byte header (n, d as int32) + float32 data."""
    print(f'[{kst()}] reading {n_rows:,} rows × {dim}d from {path.name}', flush=True)
    with open(path, 'rb') as f:
        header = np.frombuffer(f.read(8), dtype=np.int32)
        n_total, d_file = int(header[0]), int(header[1])
        if d_file != dim:
            raise SystemExit(f'dim mismatch: file={d_file}, expected={dim}')
        if n_total < n_rows:
            raise SystemExit(f'file has {n_total:,} rows, need {n_rows:,}')
        n_bytes = n_rows * dim * 4
        t0 = time.time()
        # For large reads, do in chunks to allow progress reporting
        chunk_rows = 1_000_000
        out = np.empty((n_rows, dim), dtype=np.float32)
        for offset in range(0, n_rows, chunk_rows):
            cnt = min(chunk_rows, n_rows - offset)
            buf = f.read(cnt * dim * 4)
            out[offset:offset+cnt] = np.frombuffer(buf, dtype=np.float32).reshape(cnt, dim)
            if offset > 0 and offset % 10_000_000 == 0:
                print(f'[{kst()}]     read {offset:,} ({time.time()-t0:.0f}s)', flush=True)
    print(f'[{kst()}]   read complete: {n_rows:,} × {dim} ({time.time()-t0:.1f}s)', flush=True)
    return out


def fit_pca():
    print(f'[{kst()}] fitting PCA {SRC_DIM}→{TGT_DIM} on first {PCA_FIT_N:,}', flush=True)
    fit_data = read_fbin_prefix(YFCC_RAW, PCA_FIT_N, SRC_DIM)
    t0 = time.time()
    pca = PCA(n_components=TGT_DIM, random_state=42)
    pca.fit(fit_data)
    print(f'[{kst()}]   PCA fit {time.time()-t0:.1f}s, explained var ratio sum = {pca.explained_variance_ratio_.sum():.4f}', flush=True)
    PCA_BASIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pca, PCA_BASIS_PATH)
    print(f'[{kst()}]   saved {PCA_BASIS_PATH.name}', flush=True)
    return pca


def transform_chunked(pca, raw_path: Path, n_rows: int) -> np.ndarray:
    """Read fbin + apply PCA in chunks (memory-safe for 80M)."""
    print(f'[{kst()}] PCA transform {n_rows:,} rows', flush=True)
    chunk_rows = 1_000_000
    out = np.empty((n_rows, TGT_DIM), dtype=np.float32)
    t0 = time.time()
    with open(raw_path, 'rb') as f:
        f.read(8)  # skip header
        for offset in range(0, n_rows, chunk_rows):
            cnt = min(chunk_rows, n_rows - offset)
            buf = f.read(cnt * SRC_DIM * 4)
            chunk = np.frombuffer(buf, dtype=np.float32).reshape(cnt, SRC_DIM)
            out[offset:offset+cnt] = pca.transform(chunk).astype(np.float32)
            if offset > 0 and offset % 10_000_000 == 0:
                print(f'[{kst()}]     transformed {offset:,} ({time.time()-t0:.0f}s)', flush=True)
    print(f'[{kst()}]   transform complete: {n_rows:,} × {TGT_DIM} ({time.time()-t0:.1f}s)', flush=True)
    return out


def create_pg_table(table: str):
    with psycopg.connect(host='/tmp', port=PG_PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f'DROP TABLE IF EXISTS {table}')
        cu.execute(f"""
            CREATE TABLE {table} (
                ps_partkey BIGINT NOT NULL,
                ps_suppkey BIGINT NOT NULL,
                ps_embedding vector({TGT_DIM}),
                stratum_id SMALLINT,
                PRIMARY KEY (ps_partkey, ps_suppkey)
            )
        """)
    print(f'[{kst()}]   table {table} created', flush=True)


def copy_to_pg(table: str, vecs: np.ndarray):
    n = len(vecs)
    n_partkeys = n // 4
    print(f'[{kst()}] COPY {n:,} rows → {table}', flush=True)
    t0 = time.time()
    with psycopg.connect(host='/tmp', port=PG_PORT, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        with cu.copy(f'COPY {table} (ps_partkey, ps_suppkey, ps_embedding) FROM STDIN') as copy:
            for i in range(n):
                pk = (i % n_partkeys) + 1
                sk = pk + (i // n_partkeys) * n_partkeys
                vec_str = '[' + ','.join(f'{v:.6f}' for v in vecs[i]) + ']'
                copy.write_row((pk, sk, vec_str))
                if (i + 1) % 1_000_000 == 0:
                    print(f'[{kst()}]     copied {i+1:,} ({time.time()-t0:.0f}s)', flush=True)
        c.commit()
    print(f'[{kst()}]   COPY done {time.time()-t0:.1f}s', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sf', type=int, choices=[1, 10, 100])
    ap.add_argument('--fit-only', action='store_true', help='only fit + save PCA basis')
    args = ap.parse_args()

    if not YFCC_RAW.exists():
        raise SystemExit(f'YFCC raw not yet downloaded: {YFCC_RAW}')

    if args.fit_only:
        fit_pca()
        return

    if args.sf is None:
        raise SystemExit('--sf required (or use --fit-only)')

    # Load PCA basis (fit if missing)
    if PCA_BASIS_PATH.exists():
        pca = joblib.load(PCA_BASIS_PATH)
        print(f'[{kst()}] loaded PCA basis (explained var sum = {pca.explained_variance_ratio_.sum():.4f})', flush=True)
    else:
        pca = fit_pca()

    n_target = SF_ROWS[args.sf]
    table = f'partsupp_yfcc_pca_{args.sf}'
    print(f'[{kst()}] === YFCC sf{args.sf} → {table} ({n_target:,} × {TGT_DIM}d PCA) ===', flush=True)

    NPY_DIR.mkdir(parents=True, exist_ok=True)
    npy_path = NPY_DIR / f'{table}_vectors.npy'

    if npy_path.exists():
        vecs = np.load(npy_path)
        if len(vecs) != n_target:
            print(f'[{kst()}]   stale NPY ({len(vecs):,}) — retransform', flush=True)
            vecs = transform_chunked(pca, YFCC_RAW, n_target)
            np.save(npy_path, vecs)
        else:
            print(f'[{kst()}]   loaded NPY: {vecs.shape}', flush=True)
    else:
        vecs = transform_chunked(pca, YFCC_RAW, n_target)
        np.save(npy_path, vecs)
        print(f'[{kst()}]   saved {npy_path.name}', flush=True)

    create_pg_table(table)
    copy_to_pg(table, vecs)
    print(f'[{kst()}] === YFCC sf{args.sf} DONE ===', flush=True)


if __name__ == '__main__':
    main()
