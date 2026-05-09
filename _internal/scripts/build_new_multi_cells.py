#!/usr/bin/env python3
"""
Build precomputed artifacts for 12 new multi-vector cells (Phase C, 5/9 plan).

Goal
----
Provide cached parquet/NPY artifacts (vectors, partkeys, strata, true_card,
query pool / query selectivity) for the 12 new multi cells before launching the
`measure_multi_paradigm.py` / `measure_multi_ensemble.py` measurement suite.

This script does NOT touch PostgreSQL — it only re-uses NPY caches that already
exist under ``/mnt/hdd0/home/capstone2026/cache/rq1/`` (per-source partsupp_*
vectors) and produces the multi-vector NPY layout under ``cache/rq3/`` plus the
two parquet files (``<cell>_query_pool.parquet`` / ``<cell>_query_selectivity.parquet``)
that downstream measurement scripts read.

New cells (12)
--------------
4-way (6 cells, single table, two embeddings broadcast to partsupp_<image>_<sf>):
    partsupp_sift_wiki_1   sift (128) + wiki (768)  ~ 800K rows
    partsupp_sift_wiki_10  sift (128) + wiki (768)  ~ 8M  rows
    partsupp_fb_wiki_1     fb   (256) + wiki (768)  ~ 800K rows
    partsupp_fb_wiki_10    fb   (256) + wiki (768)  ~ 8M  rows
    partsupp_yfcc_wiki_1   yfcc (192) + wiki (768)  ~ 800K rows
    partsupp_yfcc_wiki_10  yfcc (192) + wiki (768)  ~ 8M  rows

multi_join (6 cells, partsupp_<image>_<sf>  ⨝  part_wiki_<sf>, FK = ps_partkey):
    multi_join_sift_wiki_1   sift (128) joined with part_wiki (768)
    multi_join_sift_wiki_10  sift (128) joined with part_wiki (768)
    multi_join_fb_wiki_1     fb   (256) joined with part_wiki (768)
    multi_join_fb_wiki_10    fb   (256) joined with part_wiki (768)
    multi_join_yfcc_wiki_1   yfcc (192) joined with part_wiki (768)
    multi_join_yfcc_wiki_10  yfcc (192) joined with part_wiki (768)

Output layout (under ``CACHE_RQ3 = /mnt/hdd0/home/capstone2026/cache/rq3``)
------------------------------------------------------------------------
Per 4-way cell ``partsupp_<img>_wiki_<sf>``:
    {cell}_emb1.npy             (N, dim_img) float32
    {cell}_emb2.npy             (N, 768)     float32   (wiki broadcast by partkey)
    {cell}_query_pool.parquet           ps_partkey, ps_suppkey, embedding (concat float32)
    {cell}_query_selectivity.parquet    query_id, ps_partkey, selectivity, D1_target,
                                        D2_target, true_cardinality, true_selectivity
    {cell}_strata.npy           (N,) int32  (KM20 on concat([img/n1, wiki/n2]))
    {cell}_true_card.parquet    query_id, selectivity, true_card

Per multi_join cell ``multi_join_<img>_wiki_<sf>``:
    partsupp_<img>_<sf>_vectors.npy / _partkeys.npy   (already present in cache/rq1)
    part_wiki_<sf>_vectors.npy   / _partkeys.npy      (already present in cache/rq1)
    multi_join_<img>_wiki_<sf>_emb1_join.npy   (N_partsupp, dim_img)   — partsupp emb
    multi_join_<img>_wiki_<sf>_emb2_join.npy   (N_partsupp, 768)       — wiki broadcast
    multi_join_<img>_wiki_<sf>_query_pool.parquet
    multi_join_<img>_wiki_<sf>_query_selectivity.parquet
    multi_join_<img>_wiki_<sf>_strata.npy
    multi_join_<img>_wiki_<sf>_true_card.parquet

Schema parity
-------------
Schemas match the existing ``query_pool.parquet`` (RQ1) and the
``measure_multi_vector.build_query_pool()`` calibration logic
(``D1, D2 = quantile(d, sqrt(sel))``) so that downstream scripts can read the
new cells without modification.

CLI
---
    # default — build all 12 new cells (or skip if all expected outputs exist)
    python3 _internal/scripts/build_new_multi_cells.py

    # specific cells
    python3 _internal/scripts/build_new_multi_cells.py \\
        --cells partsupp_sift_wiki_1 multi_join_fb_wiki_10

    # validate + show what would be produced (no compute, no DB)
    python3 _internal/scripts/build_new_multi_cells.py --dry-run

References
----------
- ``_internal/scripts/setup_multi_sf1.py``  — broadcast / dedup pattern (deep+wiki, sf1)
- ``_internal/scripts/measure_multi_vector.py`` — build_query_pool() calibration
- ``_internal/scripts/measure_multi_paradigm.py`` — CELL_4WAY / CELL_JOIN schema we
  must mirror (so this builder can plug into the same measurement entrypoint).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - server has pandas
    raise RuntimeError("pandas required") from exc

try:
    from sklearn.cluster import MiniBatchKMeans
except ImportError:  # pragma: no cover
    MiniBatchKMeans = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Paths — server-first, local fallback (dry-run only)
# ---------------------------------------------------------------------------

CACHE_RQ1_SERVER = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
CACHE_RQ3_SERVER = Path("/mnt/hdd0/home/capstone2026/cache/rq3")

# Local fallback for `--dry-run` only (no real NPY here).
CACHE_RQ1_LOCAL = Path("/Users/hyunbin/Capstone/experiments/results/cache/rq1")
CACHE_RQ3_LOCAL = Path("/Users/hyunbin/Capstone/_internal/cache/rq3")

CACHE_RQ1 = CACHE_RQ1_SERVER if CACHE_RQ1_SERVER.exists() else CACHE_RQ1_LOCAL
CACHE_RQ3 = CACHE_RQ3_SERVER if CACHE_RQ3_SERVER.exists() else CACHE_RQ3_LOCAL


# ---------------------------------------------------------------------------
# Constants — keep in lock-step with measure_multi_vector / _table_join
# ---------------------------------------------------------------------------

SELECTIVITIES: tuple[float, ...] = (0.01, 0.05, 0.10, 0.30, 0.50)
N_STRATA: int = 20
N_QUERIES: int = 100
SAMPLE_FOR_CALIB: int = 50_000
QUERY_SEED: int = 1234
KMEANS_FIT_SAMPLE: int = 100_000
KMEANS_SEED: int = 42


def kst() -> str:
    """KST timestamp ``HH:MM:SS`` (project rule)."""
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Cell registry — 12 new cells (CLI choices + per-cell config)
# ---------------------------------------------------------------------------

#: 4-way cells: partsupp_<img>_wiki_<sf>.
#:   image_src — name of NPY family in cache/rq1 (partsupp_<img>_<sf>_vectors.npy + _pks.npy).
#:   wiki_src  — partsupp_wiki_<sf>_vectors.npy + _pks.npy in cache/rq1.
CELL_4WAY: dict[str, dict] = {
    f"partsupp_{img}_wiki_{sf}": {
        "kind": "4way",
        "image_src": f"partsupp_{img}_{sf}",
        "wiki_src":  f"partsupp_wiki_{sf}",
        "img_dim": dim,
        "wiki_dim": 768,
        "sf": sf,
    }
    for (img, dim) in (("sift", 128), ("fb", 256), ("yfcc", 192))
    for sf in (1, 10)
}

#: multi_join cells: partsupp_<img>_<sf>  ⨝  part_wiki_<sf>.
CELL_JOIN: dict[str, dict] = {
    f"multi_join_{img}_wiki_{sf}": {
        "kind": "join",
        "partsupp_src": f"partsupp_{img}_{sf}",  # cache/rq1 NPY family
        "part_src":     f"part_wiki_{sf}",        # cache/rq1 NPY family (or rq3 fallback)
        "img_dim": dim,
        "wiki_dim": 768,
        "sf": sf,
    }
    for (img, dim) in (("sift", 128), ("fb", 256), ("yfcc", 192))
    for sf in (1, 10)
}

ALL_CELLS: list[str] = list(CELL_4WAY.keys()) + list(CELL_JOIN.keys())


def _expected_n_rows(sf: int) -> int:
    """Expected partsupp row count: SF1 ~ 800K, SF10 ~ 8M (rough estimate)."""
    return 800_000 if sf == 1 else 8_000_000


def _expected_compute_minutes(sf: int) -> float:
    """Conservative minutes per cell (compute time only, dominated by true_card)."""
    # True cardinality is 100q × N pairwise distances on two columns. Empirically
    # SF1 (~800K) finishes in ~3-5 min; SF10 (~8M) in ~30-50 min on the lab box.
    return 5.0 if sf == 1 else 45.0


def _expected_memory_gb(cfg: dict) -> float:
    """Peak memory estimate (vectors + concat + cache) in GB."""
    n = _expected_n_rows(cfg["sf"])
    if cfg["kind"] == "4way":
        d_total = cfg["img_dim"] + cfg["wiki_dim"]
    else:
        d_total = cfg["img_dim"] + cfg["wiki_dim"]
    # 4 bytes/float × N × d × 2 (raw + concat) + 50K calib + buffers.
    return (4.0 * n * d_total * 2.0) / (1024.0 ** 3) + 0.5


# ---------------------------------------------------------------------------
# NPY source loader — handles cache/rq1 partsupp_*_pks.npy (2-col) and 1-col
# ---------------------------------------------------------------------------

def _load_partsupp_npy(name: str) -> tuple[np.ndarray, np.ndarray]:
    """Load partsupp_<...>_vectors.npy + _pks.npy from cache/rq1.

    Returns
    -------
    vec  : (N, dim) float32
    pks  : (N, 2)   int64    — (ps_partkey, ps_suppkey)
    """
    v_path = CACHE_RQ1 / f"{name}_vectors.npy"
    k_path = CACHE_RQ1 / f"{name}_pks.npy"
    if not (v_path.exists() and k_path.exists()):
        raise FileNotFoundError(
            f"missing NPY source for {name!r}: looked at {v_path} + {k_path}"
        )
    vec = np.load(v_path)
    pks = np.load(k_path)
    if pks.ndim == 1:
        # legacy single-column → promote to 2-col by zero-padding suppkey
        pks = np.stack([pks, np.zeros_like(pks)], axis=1)
    return vec, pks


def _load_part_wiki_npy(sf: int) -> tuple[np.ndarray, np.ndarray]:
    """Load part_wiki_<sf>_vectors.npy + _partkeys.npy (right-side join table).

    Falls back to building it from partsupp_wiki_<sf> via partkey-dedup if the
    derived file does not exist (cf. setup_multi_sf1.build_part_wiki()).
    """
    v_path = CACHE_RQ3 / f"part_wiki_{sf}_vectors.npy"
    k_path = CACHE_RQ3 / f"part_wiki_{sf}_partkeys.npy"
    if v_path.exists() and k_path.exists():
        return np.load(v_path), np.load(k_path)
    # also accept rq1 location (some setups store there)
    v_path2 = CACHE_RQ1 / f"part_wiki_{sf}_vectors.npy"
    k_path2 = CACHE_RQ1 / f"part_wiki_{sf}_partkeys.npy"
    if v_path2.exists() and k_path2.exists():
        return np.load(v_path2), np.load(k_path2)
    # Build on the fly from partsupp_wiki_<sf> (dedup by partkey, take first).
    print(f"[{kst()}]   part_wiki_{sf} not cached — building from partsupp_wiki_{sf}")
    wiki_vec, wiki_pks = _load_partsupp_npy(f"partsupp_wiki_{sf}")
    order = np.lexsort((wiki_pks[:, 1], wiki_pks[:, 0]))
    wiki_vec = wiki_vec[order]
    wiki_pks = wiki_pks[order]
    _, first_idx = np.unique(wiki_pks[:, 0], return_index=True)
    first_idx = np.sort(first_idx)
    part_vec = wiki_vec[first_idx].astype(np.float32)
    part_keys = wiki_pks[first_idx, 0].astype(np.int64)
    np.save(v_path, part_vec)
    np.save(k_path, part_keys)
    print(f"[{kst()}]   saved derived {v_path.name} {part_vec.shape}")
    return part_vec, part_keys


# ---------------------------------------------------------------------------
# Cell builders — produce {cell}_emb1.npy / _emb2.npy aligned row-for-row
# ---------------------------------------------------------------------------

def _sort_by_pks(vec: np.ndarray, pks: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    order = np.lexsort((pks[:, 1], pks[:, 0]))
    return vec[order], pks[order]


def build_4way_arrays(cell: str, cfg: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build aligned (emb1, emb2, partkeys) for a 4-way cell.

    Strategy: image source is the row spine; wiki is broadcast by partkey
    (each partkey -> first wiki embedding for that partkey).
    """
    print(f"[{kst()}] >>> 4way build: {cell}")
    img_vec, img_pks = _load_partsupp_npy(cfg["image_src"])
    wiki_vec, wiki_pks = _load_partsupp_npy(cfg["wiki_src"])

    img_vec, img_pks = _sort_by_pks(img_vec, img_pks)
    wiki_vec, wiki_pks = _sort_by_pks(wiki_vec, wiki_pks)
    print(f"[{kst()}]   image rows: {img_vec.shape}  wiki rows: {wiki_vec.shape}")

    # If the row keys match exactly, do direct alignment (cheaper, exact).
    if img_pks.shape == wiki_pks.shape and np.array_equal(img_pks, wiki_pks):
        print(f"[{kst()}]   pks identical after sort — direct 1:1 alignment")
        return (
            img_vec.astype(np.float32),
            wiki_vec.astype(np.float32),
            img_pks[:, 0].astype(np.int64),
        )

    # Otherwise broadcast wiki by partkey (first occurrence wins, mirrors setup_multi_sf1).
    print(f"[{kst()}]   pks differ — broadcasting wiki by partkey first occurrence")
    w_pk = wiki_pks[:, 0]
    _, first_idx = np.unique(w_pk, return_index=True)
    pk_to_first = dict(zip(w_pk[first_idx].tolist(), first_idx.tolist()))
    wiki_broadcast = np.empty((len(img_pks), wiki_vec.shape[1]), dtype=np.float32)
    missing = 0
    for i, pk in enumerate(img_pks[:, 0].tolist()):
        idx = pk_to_first.get(int(pk))
        if idx is None:
            missing += 1
            wiki_broadcast[i] = 0.0
        else:
            wiki_broadcast[i] = wiki_vec[idx]
    if missing:
        print(f"[{kst()}]   WARNING: {missing:,} image rows had no wiki match (zero-filled)")
    return img_vec.astype(np.float32), wiki_broadcast, img_pks[:, 0].astype(np.int64)


def build_join_arrays(cell: str, cfg: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build (partsupp_emb, part_wiki_broadcast, partsupp_partkeys) for join cell.

    Mirrors measure_multi_table_join.build_join() but works from NPY caches only.
    """
    print(f"[{kst()}] >>> join build: {cell}")
    ps_vec, ps_pks = _load_partsupp_npy(cfg["partsupp_src"])
    p_vec, p_keys = _load_part_wiki_npy(cfg["sf"])
    print(f"[{kst()}]   partsupp rows: {ps_vec.shape}  part rows: {p_vec.shape}")

    ps_vec, ps_pks = _sort_by_pks(ps_vec, ps_pks)
    sort_idx = np.argsort(p_keys, kind="stable")
    sorted_p_keys = p_keys[sort_idx]
    pos = np.searchsorted(sorted_p_keys, ps_pks[:, 0])
    valid = (pos < len(p_keys)) & (sorted_p_keys[np.clip(pos, 0, len(p_keys) - 1)] == ps_pks[:, 0])
    n_invalid = int((~valid).sum())
    if n_invalid:
        print(f"[{kst()}]   WARNING: {n_invalid:,} partsupp rows have no FK match — zero-filled")
        pos = np.where(valid, pos, 0)
    p_row_idx = sort_idx[pos]
    wiki_join = p_vec[p_row_idx].astype(np.float32)
    return ps_vec.astype(np.float32), wiki_join, ps_pks[:, 0].astype(np.int64)


# ---------------------------------------------------------------------------
# Stratification — KM20 on concat([emb1/n1, emb2/n2]) (matches paradigm framework)
# ---------------------------------------------------------------------------

def build_concat(emb1: np.ndarray, emb2: np.ndarray) -> np.ndarray:
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    return np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)


def km20_strata(concat: np.ndarray, *, fit_sample_n: int = KMEANS_FIT_SAMPLE,
                seed: int = KMEANS_SEED) -> np.ndarray:
    """KMeans K=20 on a 100K subsample, predict over all rows. Returns int32."""
    if MiniBatchKMeans is None:
        raise RuntimeError("scikit-learn required (MiniBatchKMeans) — install on server")
    rng = np.random.default_rng(seed)
    n = concat.shape[0]
    if fit_sample_n < n:
        idx = rng.choice(n, size=fit_sample_n, replace=False)
        fit_data = concat[idx]
    else:
        fit_data = concat
    km = MiniBatchKMeans(
        n_clusters=N_STRATA, batch_size=1000, random_state=seed, n_init=10,
    )
    km.fit(fit_data)
    return km.predict(concat).astype(np.int32)


# ---------------------------------------------------------------------------
# Query pool + selectivity targets + true cardinality (matches build_query_pool)
# ---------------------------------------------------------------------------

def build_query_artifacts(
    emb1: np.ndarray, emb2: np.ndarray, partkeys: np.ndarray,
    *, n_queries: int = N_QUERIES, sample_for_calib: int = SAMPLE_FOR_CALIB,
    seed: int = QUERY_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Compute query pool + per-(query, sel) D1/D2/true_card.

    Schema mirror
    -------------
    query_pool dataframe:        ps_partkey, ps_suppkey, embedding (concat as list)
        Note: ``ps_suppkey`` is set to 0 since per-cell suppkey is not retained.
    query_selectivity dataframe: query_id, ps_partkey, selectivity, D1_target,
                                 D2_target, true_cardinality, true_selectivity
    """
    rng = np.random.default_rng(seed)
    n = emb1.shape[0]
    qids = rng.choice(n, size=n_queries, replace=False)
    q1 = emb1[qids].copy()
    q2 = emb2[qids].copy()
    q_keys = partkeys[qids].copy()

    # Calibration subset — pre-compute distance distribution on 50K sample.
    calib_idx = rng.choice(n, size=min(sample_for_calib, n), replace=False)
    calib1 = emb1[calib_idx]
    calib2 = emb2[calib_idx]

    D1_by_sel: dict[float, np.ndarray] = {}
    D2_by_sel: dict[float, np.ndarray] = {}
    for sel in SELECTIVITIES:
        p = float(np.sqrt(sel))
        Dd = np.empty(n_queries, dtype=np.float32)
        Dw = np.empty(n_queries, dtype=np.float32)
        for i in range(n_queries):
            d1 = np.linalg.norm(calib1 - q1[i], axis=1)
            d2 = np.linalg.norm(calib2 - q2[i], axis=1)
            Dd[i] = float(np.quantile(d1, p))
            Dw[i] = float(np.quantile(d2, p))
        D1_by_sel[sel] = Dd
        D2_by_sel[sel] = Dw
        print(f"[{kst()}]     calib sel={sel:.2f} p={p:.4f} "
              f"D1[mean={Dd.mean():.3f}] D2[mean={Dw.mean():.3f}]")

    # Exact true cardinality on full N (chunked to bound peak memory).
    print(f"[{kst()}]     computing true cardinalities ({n_queries} q × {len(SELECTIVITIES)} sel) on N={n:,}")
    true_card: dict[tuple[int, float], int] = {}
    chunk = 200_000  # rows per pass; 200K × max(768d) × 4B ≈ 600MB working set
    t0 = time.time()
    for i in range(n_queries):
        d1_count = np.zeros(len(SELECTIVITIES), dtype=np.int64)
        # Pre-compute D thresholds per sel for this query.
        d1_thr = np.array([D1_by_sel[sel][i] for sel in SELECTIVITIES], dtype=np.float32)
        d2_thr = np.array([D2_by_sel[sel][i] for sel in SELECTIVITIES], dtype=np.float32)
        # Stream both columns chunk-by-chunk; AND mask per (sel) accumulated.
        for j0 in range(0, n, chunk):
            j1 = min(j0 + chunk, n)
            d1_block = np.linalg.norm(emb1[j0:j1] - q1[i], axis=1)
            d2_block = np.linalg.norm(emb2[j0:j1] - q2[i], axis=1)
            for k in range(len(SELECTIVITIES)):
                d1_count[k] += int(((d1_block < d1_thr[k]) & (d2_block < d2_thr[k])).sum())
        for k, sel in enumerate(SELECTIVITIES):
            true_card[(int(qids[i]), sel)] = int(d1_count[k])
        if (i + 1) % 20 == 0:
            print(f"[{kst()}]       progress {i + 1}/{n_queries} ({time.time() - t0:.0f}s)")
    print(f"[{kst()}]     true_card done in {time.time() - t0:.1f}s")

    # ---- Build dataframes ----------------------------------------------
    pool_rows = []
    for i in range(n_queries):
        emb_concat = np.concatenate([q1[i], q2[i]]).astype(np.float32).tolist()
        pool_rows.append({
            "ps_partkey": int(q_keys[i]),
            "ps_suppkey": 0,
            "embedding": emb_concat,
        })
    qp = pd.DataFrame(pool_rows)

    sel_rows = []
    for i in range(n_queries):
        qid = int(qids[i])
        for sel in SELECTIVITIES:
            tc = true_card[(qid, sel)]
            sel_rows.append({
                "query_id": i,
                "ps_partkey": int(q_keys[i]),
                "selectivity": float(sel),
                "D1_target": float(D1_by_sel[sel][i]),
                "D2_target": float(D2_by_sel[sel][i]),
                "true_cardinality": int(tc),
                "true_selectivity": float(tc) / float(n),
            })
    qs = pd.DataFrame(sel_rows)

    meta = {
        "n_queries": n_queries, "n_rows": int(n),
        "selectivities": list(SELECTIVITIES),
        "calibration": "per-query D1=quantile(d1, sqrt(sel)), D2=quantile(d2, sqrt(sel))",
        "calib_sample_n": int(min(sample_for_calib, n)),
        "query_seed": seed,
    }
    return qp, qs, meta


# ---------------------------------------------------------------------------
# Output writer per cell
# ---------------------------------------------------------------------------

def cell_output_paths(cell: str, cfg: dict) -> dict[str, Path]:
    if cfg["kind"] == "4way":
        emb1 = CACHE_RQ3 / f"{cell}_emb1.npy"
        emb2 = CACHE_RQ3 / f"{cell}_emb2.npy"
    else:
        emb1 = CACHE_RQ3 / f"{cell}_emb1_join.npy"
        emb2 = CACHE_RQ3 / f"{cell}_emb2_join.npy"
    return {
        "emb1":         emb1,
        "emb2":         emb2,
        "partkeys":     CACHE_RQ3 / f"{cell}_partkeys.npy",
        "strata":       CACHE_RQ3 / f"{cell}_strata.npy",
        "true_card":    CACHE_RQ3 / f"{cell}_true_card.parquet",
        "query_pool":   CACHE_RQ3 / f"{cell}_query_pool.parquet",
        "query_sel":    CACHE_RQ3 / f"{cell}_query_selectivity.parquet",
        "meta":         CACHE_RQ3 / f"{cell}_build_meta.json",
    }


def all_outputs_present(paths: dict[str, Path]) -> bool:
    return all(p.exists() for p in paths.values() if p.suffix in {".npy", ".parquet", ".json"})


def build_one_cell(cell: str, cfg: dict, *, force: bool, n_queries: int) -> dict:
    """Run the full build for one cell. Returns a meta dict for the cell."""
    paths = cell_output_paths(cell, cfg)
    if (not force) and all_outputs_present(paths):
        print(f"[{kst()}] SKIP {cell} — all outputs already present")
        return {"cell": cell, "status": "skipped", "outputs": {k: str(v) for k, v in paths.items()}}

    CACHE_RQ3.mkdir(parents=True, exist_ok=True)

    t_cell = time.time()
    if cfg["kind"] == "4way":
        emb1, emb2, partkeys = build_4way_arrays(cell, cfg)
    else:
        emb1, emb2, partkeys = build_join_arrays(cell, cfg)
    n = emb1.shape[0]
    print(f"[{kst()}]   {cell}: N={n:,} dim1={emb1.shape[1]} dim2={emb2.shape[1]} "
          f"({(emb1.nbytes + emb2.nbytes) / 1e9:.2f} GB)")

    np.save(paths["emb1"], emb1)
    np.save(paths["emb2"], emb2)
    np.save(paths["partkeys"], partkeys)
    print(f"[{kst()}]   saved {paths['emb1'].name}, {paths['emb2'].name}, {paths['partkeys'].name}")

    print(f"[{kst()}]   stratifying (KM20 on concat)")
    concat = build_concat(emb1, emb2)
    sids = km20_strata(concat)
    np.save(paths["strata"], sids)
    counts = np.bincount(sids, minlength=N_STRATA)
    print(f"[{kst()}]   strata sizes: min={int(counts.min())} max={int(counts.max())} "
          f"K_used={int((counts > 0).sum())}/{N_STRATA}")

    print(f"[{kst()}]   building query pool + true cardinality ({n_queries} queries)")
    qp, qs, q_meta = build_query_artifacts(emb1, emb2, partkeys, n_queries=n_queries)
    qp.to_parquet(paths["query_pool"], index=False)
    qs.to_parquet(paths["query_sel"], index=False)
    print(f"[{kst()}]   saved {paths['query_pool'].name} ({len(qp)} rows), "
          f"{paths['query_sel'].name} ({len(qs)} rows)")

    # true_card parquet (denormalized — handy for downstream paired joins).
    tc_df = qs[["query_id", "selectivity", "true_cardinality"]].rename(
        columns={"true_cardinality": "true_card"}
    )
    tc_df.to_parquet(paths["true_card"], index=False)

    meta = {
        "kst": kst(),
        "cell": cell, "kind": cfg["kind"], "sf": cfg["sf"],
        "img_dim": cfg["img_dim"], "wiki_dim": cfg["wiki_dim"],
        "n_rows": int(n),
        "strata_sizes_min": int(counts.min()),
        "strata_sizes_max": int(counts.max()),
        "strata_K_used": int((counts > 0).sum()),
        "outputs": {k: str(v) for k, v in paths.items()},
        "elapsed_s": round(time.time() - t_cell, 1),
        **q_meta,
    }
    with open(paths["meta"], "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}]   saved {paths['meta'].name} (elapsed {meta['elapsed_s']}s)")
    return {"cell": cell, "status": "built", **meta}


# ---------------------------------------------------------------------------
# Resource estimate helper (dry-run + final report)
# ---------------------------------------------------------------------------

def print_resource_table(cells: list[str]) -> None:
    print(f"\n[{kst()}] === resource estimate (per cell + total) ===")
    total_min = 0.0
    total_gb_peak = 0.0
    print(f"  {'cell':<28} {'kind':<5} {'sf':<3} {'rows':>10} {'dim1':>5} {'dim2':>5} "
          f"{'mem_GB':>7} {'min':>5}")
    for cell in cells:
        cfg = (CELL_4WAY | CELL_JOIN)[cell]
        n = _expected_n_rows(cfg["sf"])
        d1 = cfg["img_dim"]
        d2 = cfg["wiki_dim"]
        mem = _expected_memory_gb(cfg)
        mins = _expected_compute_minutes(cfg["sf"])
        total_min += mins
        total_gb_peak = max(total_gb_peak, mem)
        print(f"  {cell:<28} {cfg['kind']:<5} {cfg['sf']:<3} {n:>10,} "
              f"{d1:>5} {d2:>5} {mem:>7.2f} {mins:>5.0f}")
    print(f"  {'-' * 80}")
    print(f"  TOTAL elapsed (sequential): ~{total_min:.0f} min "
          f"= ~{total_min / 60:.1f} h, peak memory ~{total_gb_peak:.2f} GB")
    print(f"  (4-way × 6 + join × 6 = {len(cells)} cells)\n")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build precomputed artifacts for 12 new multi-vector cells.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--cells", nargs="+", choices=ALL_CELLS, default=None,
                    help="Cell names to build (default: all 12).")
    ap.add_argument("--n-queries", type=int, default=N_QUERIES,
                    help=f"Number of queries per cell (default {N_QUERIES}).")
    ap.add_argument("--force", action="store_true",
                    help="Re-build even if outputs already exist.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate inputs + print plan; no compute, no DB.")
    args = ap.parse_args()

    cells = args.cells or ALL_CELLS

    print(f"[{kst()}] === build_new_multi_cells ===")
    print(f"[{kst()}] CACHE_RQ1: {CACHE_RQ1}")
    print(f"[{kst()}] CACHE_RQ3: {CACHE_RQ3}")
    print(f"[{kst()}] cells ({len(cells)}): {cells}")

    print_resource_table(cells)

    if args.dry_run:
        print(f"\n[{kst()}] === dry-run: file plan ===")
        for cell in cells:
            cfg = (CELL_4WAY | CELL_JOIN)[cell]
            paths = cell_output_paths(cell, cfg)
            present = all_outputs_present(paths)
            print(f"  {cell} ({cfg['kind']}, sf={cfg['sf']}): "
                  f"{'OK (skip)' if present else 'NEEDS BUILD'}")
            for k, v in paths.items():
                tag = "exists" if v.exists() else "MISSING"
                print(f"      [{tag:>7}] {k:<11} -> {v}")
        # also check NPY sources presence (server-only)
        print(f"\n[{kst()}] === source NPY check (cache/rq1) ===")
        needed_sources: set[str] = set()
        for cell in cells:
            cfg = (CELL_4WAY | CELL_JOIN)[cell]
            if cfg["kind"] == "4way":
                needed_sources.update({cfg["image_src"], cfg["wiki_src"]})
            else:
                needed_sources.add(cfg["partsupp_src"])
                needed_sources.add(f"part_wiki_{cfg['sf']}")
        for src in sorted(needed_sources):
            if src.startswith("part_wiki"):
                v = CACHE_RQ3 / f"{src}_vectors.npy"
                k = CACHE_RQ3 / f"{src}_partkeys.npy"
            else:
                v = CACHE_RQ1 / f"{src}_vectors.npy"
                k = CACHE_RQ1 / f"{src}_pks.npy"
            tag_v = "OK " if v.exists() else "MISS"
            tag_k = "OK " if k.exists() else "MISS"
            print(f"  [{tag_v}] {v.name:<40}  [{tag_k}] {k.name}")
        print(f"\n[{kst()}] dry-run OK")
        return

    # ---- Real build ---------------------------------------------------
    if MiniBatchKMeans is None:
        raise SystemExit("scikit-learn (MiniBatchKMeans) required — run on server")

    t_total = time.time()
    summary: list[dict] = []
    for cell in cells:
        cfg = (CELL_4WAY | CELL_JOIN)[cell]
        try:
            res = build_one_cell(cell, cfg, force=args.force, n_queries=args.n_queries)
        except FileNotFoundError as exc:
            print(f"[{kst()}] ERROR {cell}: {exc}")
            summary.append({"cell": cell, "status": "error", "error": str(exc)})
            continue
        except Exception as exc:  # pragma: no cover  - server runtime
            import traceback
            traceback.print_exc()
            summary.append({"cell": cell, "status": "error", "error": str(exc)})
            continue
        summary.append(res)

    print(f"\n[{kst()}] === build summary ===")
    for s in summary:
        print(f"  {s['cell']:<28} {s.get('status'):<8} "
              f"elapsed={s.get('elapsed_s', '?')}s")
    n_built = sum(1 for s in summary if s.get("status") == "built")
    n_skipped = sum(1 for s in summary if s.get("status") == "skipped")
    n_error = sum(1 for s in summary if s.get("status") == "error")
    total_elapsed = time.time() - t_total
    print(f"[{kst()}] built={n_built} skipped={n_skipped} error={n_error} "
          f"total {total_elapsed:.1f}s")

    if n_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
