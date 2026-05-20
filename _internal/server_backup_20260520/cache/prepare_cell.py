#!/usr/bin/env python3
"""Unified prep for TPC-H natural tables (Exqutor 5-dataset matrix).

각 (dataset, sf) cell 에 대해:
  1. ALTER TABLE ADD COLUMN IF NOT EXISTS stratum_id smallint
  2. PG fetch (PK + embedding) → NPY cache
  3. MiniBatchKMeans K=20 → stratum_ids
  4. UPDATE PG stratum_id via COPY temp join
  5. σ per stratum (PC1 std) → vector_stratum_sigma table
  6. Query pool 100 × 5 sel → parquet (long format)

Usage:
  python prepare_cell.py --dataset DEEP --sf 1
  python prepare_cell.py --dataset SSN  --sf 100
  python prepare_cell.py --dataset YFCC --sf 10
"""
import argparse
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
import psycopg
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA

PORT = 55435  # vanilla PG — TPC-H natural tables
DB = 'wns41559'
USER = 'wns41559'
NPY_DIR = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
N_STRATA = 20
N_QUERIES = 100
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_FOR_SEL = 200_000

CELLS = {
    ('DEEP', 1):   {'table':'partsupp_deep_1',   'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':96},
    ('DEEP', 10):  {'table':'partsupp_deep_10',  'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':96},
    ('DEEP', 100): {'table':'partsupp_deep_100', 'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':96},
    ('SIFT', 1):   {'table':'partsupp_sift_1',   'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':128},
    ('SIFT', 10):  {'table':'partsupp_sift_10',  'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':128},
    ('SIFT', 100): {'table':'partsupp_sift_100', 'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':128},
    ('SSN',  1):   {'table':'partsupp_fb_1',     'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':256},
    ('SSN',  10):  {'table':'partsupp_fb_10',    'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':256},
    ('SSN',  100): {'table':'partsupp_fb_100',   'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':256},
    ('YFCC', 1):   {'table':'partsupp_yfcc_1',   'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':192},
    ('YFCC', 10):  {'table':'partsupp_yfcc_10',  'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':192},
    ('YFCC', 100): {'table':'partsupp_yfcc_100', 'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':192},
    ('YFCC_DL', 1):   {'table':'partsupp_yfcc_pca_1',   'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':192},
    ('YFCC_DL', 10):  {'table':'partsupp_yfcc_pca_10',  'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':192},
    ('YFCC_DL', 100): {'table':'partsupp_yfcc_pca_100', 'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':192},
    ('WIKI', 1):   {'table':'partsupp_wiki_1',   'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':768},
    ('WIKI', 10):  {'table':'partsupp_wiki_10',  'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':768},
    ('WIKI', 100): {'table':'partsupp_wiki_100', 'embed_col':'ps_embedding', 'pk_cols':('ps_partkey','ps_suppkey'), 'dim':768},
}

LEARN_FRAC_BY_SF = {1: 0.10, 10: 0.02, 100: 0.005}  # sf1 100K, sf10 160K, sf100 400K learn samples


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def cell_name(dataset, sf):
    return f'{dataset}_sf{sf}'


def npy_paths(table):
    return NPY_DIR / f'{table}_vectors.npy', NPY_DIR / f'{table}_pks.npy'


def fetch_vectors_pg(table, embed_col, pk_cols, dim, port=PORT, batch_rows=500_000):
    """Stream fetch via server-side cursor — memory-safe for 80M.

    pk_cols: tuple of PK column names (e.g. ('ps_partkey','ps_suppkey')).
    Returns:
        pks: (N, len(pk_cols)) int64 array — composite PK rows
        vecs: (N, dim) float32
    """
    n_pk = len(pk_cols)
    pk_select = ', '.join(pk_cols)
    print(f'[{kst()}]   PG fetch start (batch={batch_rows:,}, pk={pk_cols})', flush=True)
    pks_chunks = []
    vecs_chunks = []
    t0 = time.time()
    with psycopg.connect(host='/tmp', port=port, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor(name='fetch_cur')
        cu.itersize = batch_rows
        cu.execute(f'SELECT {pk_select}, {embed_col}::real[] FROM {table} ORDER BY {pk_select}')
        chunk_pks = []
        chunk_vecs = []
        n_total = 0
        for row in cu:
            chunk_pks.append(row[:n_pk])
            chunk_vecs.append(row[n_pk])
            if len(chunk_pks) >= batch_rows:
                pks_chunks.append(np.asarray(chunk_pks, dtype=np.int64))
                vecs_chunks.append(np.asarray(chunk_vecs, dtype=np.float32))
                n_total += len(chunk_pks)
                print(f'[{kst()}]     fetched {n_total:,} ({time.time()-t0:.0f}s)', flush=True)
                chunk_pks = []
                chunk_vecs = []
        if chunk_pks:
            pks_chunks.append(np.asarray(chunk_pks, dtype=np.int64))
            vecs_chunks.append(np.asarray(chunk_vecs, dtype=np.float32))
            n_total += len(chunk_pks)
        cu.close()
    pks = np.concatenate(pks_chunks)  # shape (N, n_pk)
    vecs = np.concatenate(vecs_chunks)
    print(f'[{kst()}]   fetched {len(vecs):,} × {vecs.shape[1]} in {time.time()-t0:.1f}s', flush=True)
    return pks, vecs


def ensure_stratum_column(table, port=PORT):
    with psycopg.connect(host='/tmp', port=port, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS stratum_id smallint')
    print(f'[{kst()}]   stratum_id column ensured on {table}', flush=True)


def update_strata_pg(table, pk_cols, pks, stratum_ids, port=PORT):
    """UPDATE via composite PK COPY into temp + indexed JOIN.

    pks: (N, len(pk_cols)) int64 array.
    """
    n_pk = len(pk_cols)
    print(f'[{kst()}]   UPDATE {table}.stratum_id ({len(pks):,} rows, pk_cols={pk_cols})', flush=True)
    t0 = time.time()
    pk_col_decl = ', '.join(f'{c} BIGINT' for c in pk_cols)
    pk_col_names = ', '.join(pk_cols)
    join_cond = ' AND '.join(f't.{c} = m.{c}' for c in pk_cols)
    idx_cols = pk_col_names
    with psycopg.connect(host='/tmp', port=port, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        cu.execute(f'CREATE TEMP TABLE _strata_map ({pk_col_decl}, sid SMALLINT)')
        with cu.copy(f'COPY _strata_map ({pk_col_names}, sid) FROM STDIN') as copy:
            pks_list = pks.tolist()
            sids_list = stratum_ids.tolist()
            for i in range(len(pks_list)):
                row = tuple(pks_list[i]) + (sids_list[i],)
                copy.write_row(row)
        cu.execute(f'CREATE INDEX ON _strata_map ({idx_cols})')
        cu.execute(f'UPDATE {table} t SET stratum_id = m.sid FROM _strata_map m WHERE {join_cond}')
        c.commit()
    print(f'[{kst()}]   UPDATE done in {time.time()-t0:.1f}s', flush=True)


def ensure_sigma_table(port=PORT):
    with psycopg.connect(host='/tmp', port=port, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute("""
            CREATE TABLE IF NOT EXISTS vector_stratum_sigma (
                table_name TEXT, stratum_id SMALLINT, sigma DOUBLE PRECISION,
                PRIMARY KEY (table_name, stratum_id)
            )
        """)


def write_sigmas(table, sigmas, port=PORT):
    with psycopg.connect(host='/tmp', port=port, dbname=DB, user=USER, autocommit=False) as c:
        cu = c.cursor()
        cu.execute(f"DELETE FROM vector_stratum_sigma WHERE table_name = '{table}'")
        for sid, sig in enumerate(sigmas):
            cu.execute(
                f"INSERT INTO vector_stratum_sigma (table_name, stratum_id, sigma) "
                f"VALUES ('{table}', {sid}, {sig})"
            )
        c.commit()


def kmeans_strata(all_vecs, learn_frac):
    n = len(all_vecs)
    n_learn = max(int(n * learn_frac), N_STRATA * 50)
    n_learn = min(n_learn, n)
    rng = np.random.default_rng(42)
    learn_idx = rng.choice(n, size=n_learn, replace=False)
    print(f'[{kst()}]   KMeans K={N_STRATA} fit on {n_learn:,}/{n:,}', flush=True)
    t0 = time.time()
    mbk = MiniBatchKMeans(n_clusters=N_STRATA, batch_size=4096, max_iter=100,
                          random_state=42, n_init=3, max_no_improvement=20).fit(all_vecs[learn_idx])
    print(f'[{kst()}]     fit {time.time()-t0:.1f}s', flush=True)
    t1 = time.time()
    chunk = 500_000
    sids = np.empty(n, dtype=np.int16)
    for i in range(0, n, chunk):
        sids[i:i+chunk] = mbk.predict(all_vecs[i:i+chunk]).astype(np.int16)
    print(f'[{kst()}]     predict {time.time()-t1:.1f}s', flush=True)
    sizes = np.bincount(sids, minlength=N_STRATA)
    print(f'[{kst()}]     sizes min={sizes.min():,}, max={sizes.max():,}, ratio={sizes.max()/max(sizes.min(),1):.2f}', flush=True)
    return sids, sizes


def compute_sigmas(all_vecs, sids):
    print(f'[{kst()}]   σ per stratum (PC1 std)', flush=True)
    sigmas = np.zeros(N_STRATA, dtype=np.float64)
    for sid in range(N_STRATA):
        mask = sids == sid
        if mask.sum() < 2:
            continue
        sub = all_vecs[mask]
        if len(sub) > 50_000:
            rng = np.random.default_rng(42 + sid)
            idx = rng.choice(len(sub), size=50_000, replace=False)
            sub = sub[idx]
        pc1 = PCA(n_components=1, random_state=42).fit_transform(sub)
        sigmas[sid] = float(pc1.std())
    print(f'[{kst()}]     σ avg={sigmas.mean():.4f}, range=[{sigmas.min():.4f}, {sigmas.max():.4f}]', flush=True)
    return sigmas


def gen_querypool(all_vecs, pks, name):
    print(f'[{kst()}]   query pool gen ({N_QUERIES} q × {len(SELECTIVITIES)} sel)', flush=True)
    rng = np.random.default_rng(42)
    n = len(all_vecs)
    q_idx = rng.choice(n, size=N_QUERIES, replace=False)
    q_vecs = all_vecs[q_idx]
    q_keys = pks[q_idx]
    sample_n = min(SAMPLE_FOR_SEL, n)
    sample_idx = rng.choice(n, size=sample_n, replace=False)

    rows = []
    t0 = time.time()
    chunk = 100_000
    for qi, qv in enumerate(q_vecs):
        all_d = np.empty(n, dtype=np.float32)
        for i in range(0, n, chunk):
            all_d[i:i+chunk] = np.linalg.norm(all_vecs[i:i+chunk] - qv, axis=1)
        sample_d = all_d[sample_idx]
        for sel in SELECTIVITIES:
            d_target = float(np.quantile(sample_d, sel))
            true_card = int((all_d <= d_target).sum())
            rows.append({
                'query_id': qi,
                'selectivity': sel,
                'D_target': d_target,
                'true_cardinality': true_card,
                'actual_sel': true_card / n,
            })
        if (qi + 1) % 25 == 0:
            print(f'[{kst()}]     {qi+1}/{N_QUERIES} ({time.time()-t0:.0f}s)', flush=True)

    sel_df = pd.DataFrame(rows)
    # q_keys may be 1D (single PK) or 2D (composite). Save as JSON-friendly list.
    qp_df = pd.DataFrame([{
        'query_id': qi,
        'embedding': q_vecs[qi].tolist(),
        'q_pk': q_keys[qi].tolist() if q_keys.ndim > 1 else [int(q_keys[qi])],
    } for qi in range(N_QUERIES)])

    qp_path = NPY_DIR / f'query_pool_{name}.parquet'
    sel_path = NPY_DIR / f'query_selectivity_{name}.parquet'
    qp_df.to_parquet(qp_path)
    sel_df.to_parquet(sel_path)
    print(f'[{kst()}]   saved {qp_path.name} ({len(qp_df)}) + {sel_path.name} ({len(sel_df)})', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', required=True, choices=['DEEP', 'SIFT', 'SSN', 'YFCC', 'WIKI', 'YFCC_DL'])
    ap.add_argument('--sf', type=int, required=True, choices=[1, 10, 100])
    ap.add_argument('--port', type=int, default=PORT)
    ap.add_argument('--skip-qp', action='store_true', help='skip querypool gen (for faster prep test)')
    ap.add_argument('--pg-update', action='store_true', help='also UPDATE PG stratum_id (slow with HNSW; NPY-only is default)')
    args = ap.parse_args()

    key = (args.dataset, args.sf)
    if key not in CELLS:
        raise SystemExit(f'unsupported cell: {key}')
    cfg = CELLS[key]
    name = cell_name(args.dataset, args.sf)
    print(f'[{kst()}] === PREP {name} ({cfg["table"]}) ===', flush=True)
    NPY_DIR.mkdir(parents=True, exist_ok=True)

    vecs_npy, pks_npy = npy_paths(cfg['table'])

    # 1. ensure stratum column + sigma table
    ensure_stratum_column(cfg['table'], port=args.port)
    ensure_sigma_table(port=args.port)

    # 2. fetch (or load NPY cache)
    if vecs_npy.exists() and pks_npy.exists():
        all_vecs = np.load(vecs_npy)
        pks = np.load(pks_npy)
        # Validate shape — old NPY (1D pks) is incompatible with new composite PK code
        n_pk = len(cfg['pk_cols'])
        if pks.ndim != 2 or pks.shape[1] != n_pk:
            print(f'[{kst()}]   NPY cache pk shape mismatch (got {pks.shape}, want (N,{n_pk})) — refetch', flush=True)
            pks, all_vecs = fetch_vectors_pg(cfg['table'], cfg['embed_col'], cfg['pk_cols'], cfg['dim'], port=args.port)
            np.save(vecs_npy, all_vecs)
            np.save(pks_npy, pks)
            print(f'[{kst()}]   saved NPY cache', flush=True)
        else:
            print(f'[{kst()}]   loaded NPY cache: {len(all_vecs):,} × {all_vecs.shape[1]} (pks {pks.shape})', flush=True)
    else:
        pks, all_vecs = fetch_vectors_pg(cfg['table'], cfg['embed_col'], cfg['pk_cols'], cfg['dim'], port=args.port)
        np.save(vecs_npy, all_vecs)
        np.save(pks_npy, pks)
        print(f'[{kst()}]   saved NPY cache', flush=True)

    # 3. KMeans
    sids, sizes = kmeans_strata(all_vecs, LEARN_FRAC_BY_SF[args.sf])

    # 4. Save strata NPY (option C — bypass PG UPDATE for HNSW-heavy tables)
    strata_npy = NPY_DIR / f'{cfg["table"]}_strata.npy'
    np.save(strata_npy, sids)
    print(f'[{kst()}]   saved {strata_npy.name}', flush=True)

    # PG UPDATE optional via flag (default: skip for speed)
    if args.pg_update:
        update_strata_pg(cfg['table'], cfg['pk_cols'], pks, sids, port=args.port)
    else:
        print(f'[{kst()}]   PG UPDATE skipped (NPY-only mode)', flush=True)

    # 5. σ
    sigmas = compute_sigmas(all_vecs, sids)
    write_sigmas(cfg['table'], sigmas, port=args.port)

    # 6. querypool
    if not args.skip_qp:
        gen_querypool(all_vecs, pks, name)

    print(f'[{kst()}] === PREP {name} DONE ===', flush=True)


if __name__ == '__main__':
    main()
