#!/usr/bin/env python3
"""
Multi-cell σ-allocation 5-mode supplement measurement.

기존 measure_multi_vector.py / measure_multi_table_join.py 는 KM20 4 mode (emb1/emb2/concat/product)
+ equal_alloc 만 측정. 본 스크립트는 single 12 cell 의 RQ2 5mode (bernoulli/equal/proportional/
neyman/anti_neyman) format 과 통일하기 위해 Multi 3 cell 에 대해 σ-allocation ablation 측정.

Multi 3 cell:
  - deep_sift_10:   partsupp_deep_sift_10 (emb1=deep 96d, emb2=sift 128d)
  - deep_wiki_10:   partsupp_deep_wiki_10 (emb1=deep 96d, emb2=wiki 768d)
  - multi_join_deep_wiki: partsupp_deep_10 ⋈ part_wiki_10 (deep 96d + wiki 768d, FK join)

Stratification: KM20 on concat([emb1 || emb2]) — multi-vector 의 "best stratum" 으로 일관 사용
                (4 mode 측정에서 km20_concat 이 emb1/emb2/product 중 best 또는 비등으로 확인됨)

Allocation modes (5):
  - bernoulli:   stratification 없이 SRS budget=385 (control)
  - equal:       budget/K 균등 분배
  - proportional: w_j = N_j (size 비례)
  - neyman:      w_j = N_j × σ_j (size × spread)
  - anti_neyman: w_j = N_j / σ_j (역 — diagnostic)

Output format: rq2_multi_5mode_<cell>.parquet (5 sel × 5 mode × 5 seed × 100 query = 12500 rows / cell)

Usage:
    python3 measure_multi_5mode.py --cell deep_sift_10
    python3 measure_multi_5mode.py --cell deep_wiki_10
    python3 measure_multi_5mode.py --cell multi_join_deep_wiki
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from sklearn.cluster import KMeans
except ImportError as e:
    raise RuntimeError("scikit-learn required (KMeans)") from e


CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq3")

SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_STRATA = 20
CACHE_PER_CLUSTER = 500
N_QUERIES = 100

ALLOC_MODES = ["equal", "proportional", "neyman", "anti_neyman"]
ALL_MODES = ["bernoulli"] + ALLOC_MODES


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# data loading
# ---------------------------------------------------------------------------

def load_cell(cell: str) -> tuple[np.ndarray, np.ndarray, str]:
    """cell 별 emb1, emb2 NPY load.

    Returns:
        emb1: (N, dim1)
        emb2: (N, dim2)
        table_pair: meta 용 라벨
    """
    if cell == "deep_sift_10":
        emb1 = np.load(CACHE / "partsupp_deep_sift_10_emb1.npy")
        emb2 = np.load(CACHE / "partsupp_deep_sift_10_emb2.npy")
        return emb1, emb2, "partsupp_deep_sift_10"
    if cell == "deep_wiki_10":
        emb1 = np.load(CACHE / "partsupp_deep_wiki_10_emb1.npy")
        emb2 = np.load(CACHE / "partsupp_deep_wiki_10_emb2.npy")
        return emb1, emb2, "partsupp_deep_wiki_10"
    if cell == "deep_sift_1":
        emb1 = np.load(CACHE / "partsupp_deep_sift_1_emb1.npy")
        emb2 = np.load(CACHE / "partsupp_deep_sift_1_emb2.npy")
        return emb1, emb2, "partsupp_deep_sift_1"
    if cell == "deep_wiki_1":
        emb1 = np.load(CACHE / "partsupp_deep_wiki_1_emb1.npy")
        emb2 = np.load(CACHE / "partsupp_deep_wiki_1_emb2.npy")
        return emb1, emb2, "partsupp_deep_wiki_1"
    if cell == "multi_join_deep_wiki":
        # FK join: partsupp_deep_10 (deep 96d) ⋈ part_wiki_10 (wiki 768d)
        ps_vec = np.load(CACHE / "partsupp_deep_10_vectors.npy")
        ps_keys = np.load(CACHE / "partsupp_deep_10_partkeys.npy")
        p_vec = np.load(CACHE / "part_wiki_10_vectors.npy")
        p_keys = np.load(CACHE / "part_wiki_10_partkeys.npy")
        # FK lookup: partsupp 각 row 에 part embedding broadcast
        sort_idx = np.argsort(p_keys, kind="stable")
        sorted_p_keys = p_keys[sort_idx]
        pos = np.searchsorted(sorted_p_keys, ps_keys)
        if pos.max() >= len(p_keys) or not np.all(sorted_p_keys[pos] == ps_keys):
            valid = (pos < len(p_keys)) & (sorted_p_keys[np.clip(pos, 0, len(p_keys) - 1)] == ps_keys)
            n_invalid = int((~valid).sum())
            print(f"[{kst()}]   WARNING: {n_invalid:,} partsupp rows have no matching part (FK gap)")
            pos = np.where(valid, pos, 0)
        p_row_idx = sort_idx[pos]
        wiki_join = p_vec[p_row_idx]
        deep_join = ps_vec
        del p_vec, p_keys, ps_keys, ps_vec
        return deep_join, wiki_join, "partsupp_deep_10__part_wiki_10"
    if cell == "multi_join_deep_wiki_1":
        # FK join SF1: partsupp_deep_1 (deep 96d) ⋈ part_wiki_1 (wiki 768d)
        ps_vec = np.load(CACHE / "partsupp_deep_1_vectors.npy")
        ps_keys = np.load(CACHE / "partsupp_deep_1_partkeys.npy")
        p_vec = np.load(CACHE / "part_wiki_1_vectors.npy")
        p_keys = np.load(CACHE / "part_wiki_1_partkeys.npy")
        sort_idx = np.argsort(p_keys, kind="stable")
        sorted_p_keys = p_keys[sort_idx]
        pos = np.searchsorted(sorted_p_keys, ps_keys)
        if pos.max() >= len(p_keys) or not np.all(sorted_p_keys[pos] == ps_keys):
            valid = (pos < len(p_keys)) & (sorted_p_keys[np.clip(pos, 0, len(p_keys) - 1)] == ps_keys)
            n_invalid = int((~valid).sum())
            print(f"[{kst()}]   WARNING: {n_invalid:,} partsupp rows have no matching part (FK gap)")
            pos = np.where(valid, pos, 0)
        p_row_idx = sort_idx[pos]
        wiki_join = p_vec[p_row_idx]
        deep_join = ps_vec
        del p_vec, p_keys, ps_keys, ps_vec
        return deep_join, wiki_join, "partsupp_deep_1__part_wiki_1"
    raise ValueError(f"unknown cell: {cell}")


# ---------------------------------------------------------------------------
# stratification — KM20 on concat
# ---------------------------------------------------------------------------

def stratify_concat(emb1: np.ndarray, emb2: np.ndarray,
                    K: int = N_STRATA, seed: int = 42,
                    sample_n: int = 100_000) -> np.ndarray:
    """[emb1 || emb2] concat 후 K-means K=20."""
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    e1 = emb1 / n1
    e2 = emb2 / n2
    concat = np.concatenate([e1, e2], axis=1).astype(np.float32)
    print(f"[{kst()}]   strat: concat ({concat.shape[1]}d) K={K} fit (sample {sample_n})")
    rng = np.random.default_rng(seed)
    if sample_n is not None and concat.shape[0] > sample_n:
        idx = rng.choice(concat.shape[0], size=sample_n, replace=False)
        kmeans = KMeans(n_clusters=K, random_state=seed, n_init=3, max_iter=50).fit(concat[idx])
    else:
        kmeans = KMeans(n_clusters=K, random_state=seed, n_init=3, max_iter=50).fit(concat)
    sids = kmeans.predict(concat).astype(np.int32)
    return sids


# ---------------------------------------------------------------------------
# σ computation (joint stratum spread on concat)
# ---------------------------------------------------------------------------

def compute_sigmas(emb1: np.ndarray, emb2: np.ndarray, sids: np.ndarray,
                   n_strata: int = N_STRATA) -> tuple[dict[int, int], dict[int, float]]:
    """stratum 별 size + σ (concat-space distance to centroid std).

    σ definition: 각 stratum 의 concat embedding 을 centroid 와의 거리로 변환,
    그 거리들의 표준편차. RQ2 single 의 vector_stratum_sigma 와 같은 개념.
    """
    # concat space 에서 σ 계산 (allocation 의 정의 단위 통일)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    e1 = emb1 / n1
    e2 = emb2 / n2
    concat = np.concatenate([e1, e2], axis=1).astype(np.float32)
    sizes: dict[int, int] = {}
    sigmas: dict[int, float] = {}
    for sid in range(n_strata):
        idx = np.where(sids == sid)[0]
        n = int(len(idx))
        sizes[sid] = n
        if n <= 1:
            sigmas[sid] = 0.0
            continue
        cv = concat[idx]
        centroid = cv.mean(axis=0)
        d2c = np.linalg.norm(cv - centroid, axis=1)
        sigmas[sid] = float(d2c.std())
    return sizes, sigmas


# ---------------------------------------------------------------------------
# allocation
# ---------------------------------------------------------------------------

def allocate_samples(mode: str, sizes: dict[int, int], sigmas: dict[int, float],
                     budget: int = SAMPLE_SIZE, n_strata: int = N_STRATA) -> np.ndarray:
    """rq2_alloc_python.py 의 allocate_samples 와 동일 logic."""
    w = np.zeros(n_strata)
    for j in range(n_strata):
        N_j = sizes.get(j, 0)
        sg = sigmas.get(j, 0.0)
        if mode == "proportional":
            w[j] = N_j
        elif mode == "neyman":
            w[j] = N_j * sg
        elif mode == "anti_neyman":
            w[j] = N_j / sg if sg > 1e-9 else N_j
        else:  # equal
            w[j] = 1.0
    sum_w = w.sum()
    if sum_w <= 0:
        sum_w = n_strata
        w[:] = 1.0
    f = w / sum_w * budget
    s = np.maximum(f.astype(int), 1)
    frac = f - f.astype(int)
    extra = budget - int(s.sum())
    if extra > 0:
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    return s


# ---------------------------------------------------------------------------
# cluster sample cache (multi-vector — emb1, emb2 둘 다)
# ---------------------------------------------------------------------------

def cache_dual_samples(emb1: np.ndarray, emb2: np.ndarray, sids: np.ndarray,
                       n_strata: int = N_STRATA, cache_per: int = CACHE_PER_CLUSTER,
                       seed: int = 42) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray], dict[int, int]]:
    rng = np.random.default_rng(seed)
    s1: dict[int, np.ndarray] = {}
    s2: dict[int, np.ndarray] = {}
    sizes: dict[int, int] = {}
    for sid in range(n_strata):
        mask = sids == sid
        n = int(mask.sum())
        sizes[sid] = n
        if n == 0:
            s1[sid] = np.zeros((1, emb1.shape[1]), dtype=np.float32)
            s2[sid] = np.zeros((1, emb2.shape[1]), dtype=np.float32)
            continue
        idx_in_strat = np.flatnonzero(mask)
        if n > cache_per:
            pick = rng.choice(idx_in_strat, size=cache_per, replace=False)
        else:
            pick = idx_in_strat
        s1[sid] = emb1[pick]
        s2[sid] = emb2[pick]
    return s1, s2, sizes


# ---------------------------------------------------------------------------
# query pool (재계산 — measure_multi_vector 와 동일 로직)
# ---------------------------------------------------------------------------

def build_query_pool(emb1: np.ndarray, emb2: np.ndarray,
                     n_queries: int = N_QUERIES, sample_for_calib: int = 50_000,
                     seed: int = 1234) -> tuple:
    rng = np.random.default_rng(seed)
    N = emb1.shape[0]
    qids = rng.choice(N, size=n_queries, replace=False)
    q1 = emb1[qids].copy()
    q2 = emb2[qids].copy()

    calib_idx = rng.choice(N, size=min(sample_for_calib, N), replace=False)
    calib1 = emb1[calib_idx]
    calib2 = emb2[calib_idx]

    D1_by_sel: dict[float, np.ndarray] = {}
    D2_by_sel: dict[float, np.ndarray] = {}
    for sel in SELECTIVITIES:
        p = float(np.sqrt(sel))
        d1_vec = np.empty(n_queries, dtype=np.float32)
        d2_vec = np.empty(n_queries, dtype=np.float32)
        for i in range(n_queries):
            d1 = np.linalg.norm(calib1 - q1[i], axis=1)
            d2 = np.linalg.norm(calib2 - q2[i], axis=1)
            d1_vec[i] = float(np.quantile(d1, p))
            d2_vec[i] = float(np.quantile(d2, p))
        D1_by_sel[sel] = d1_vec
        D2_by_sel[sel] = d2_vec
        print(f"[{kst()}]   calib sel={sel:.2f} p={p:.4f} "
              f"D1[mean={d1_vec.mean():.3f}] D2[mean={d2_vec.mean():.3f}]")

    print(f"[{kst()}]   computing true cards ({n_queries} q × {len(SELECTIVITIES)} sel) on N={N:,}")
    true_card: dict[tuple[int, float], int] = {}
    t0 = time.time()
    for i, qid in enumerate(qids):
        d1_full = np.linalg.norm(emb1 - q1[i], axis=1)
        d2_full = np.linalg.norm(emb2 - q2[i], axis=1)
        for sel in SELECTIVITIES:
            D1 = D1_by_sel[sel][i]
            D2 = D2_by_sel[sel][i]
            tc = int(((d1_full < D1) & (d2_full < D2)).sum())
            true_card[(int(qid), sel)] = tc
        if (i + 1) % 20 == 0:
            print(f"[{kst()}]     true_card progress {i+1}/{n_queries} ({(time.time()-t0):.0f}s)")
    print(f"[{kst()}]   true_card done in {time.time()-t0:.1f}s")
    return qids, q1, q2, D1_by_sel, D2_by_sel, true_card


# ---------------------------------------------------------------------------
# estimators
# ---------------------------------------------------------------------------

def stratified_estimate_dual(s1: dict[int, np.ndarray], s2: dict[int, np.ndarray],
                              sizes: dict[int, int], alloc: np.ndarray,
                              q1v: np.ndarray, q2v: np.ndarray, D1: float, D2: float,
                              rng: np.random.Generator, n_strata: int = N_STRATA) -> float:
    est = 0.0
    for sid in range(n_strata):
        cache1 = s1[sid]
        cache2 = s2[sid]
        n_cache = cache1.shape[0]
        s_i = min(int(alloc[sid]), n_cache)
        if s_i < 1:
            s_i = 1
        idxs = rng.choice(n_cache, size=s_i, replace=False)
        sub1 = cache1[idxs]
        sub2 = cache2[idxs]
        d1 = np.linalg.norm(sub1 - q1v, axis=1)
        d2 = np.linalg.norm(sub2 - q2v, axis=1)
        hits = int(((d1 < D1) & (d2 < D2)).sum())
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
    return est


def bernoulli_estimate_dual(s1: dict[int, np.ndarray], s2: dict[int, np.ndarray],
                             sizes: dict[int, int], q1v: np.ndarray, q2v: np.ndarray,
                             D1: float, D2: float, rng: np.random.Generator,
                             budget: int = SAMPLE_SIZE, n_strata: int = N_STRATA) -> float:
    total = sum(sizes.values())
    flat1 = np.concatenate([s1[sid] for sid in range(n_strata)], axis=0)
    flat2 = np.concatenate([s2[sid] for sid in range(n_strata)], axis=0)
    n = flat1.shape[0]
    s = min(int(budget), n)
    if s == 0:
        return float(total)
    idxs = rng.choice(n, size=s, replace=False)
    sub1 = flat1[idxs]
    sub2 = flat2[idxs]
    d1 = np.linalg.norm(sub1 - q1v, axis=1)
    d2 = np.linalg.norm(sub2 - q2v, axis=1)
    hits = int(((d1 < D1) & (d2 < D2)).sum())
    return hits * (total / s)


# ---------------------------------------------------------------------------
# measurement loop — 5 mode × 5 sel × 5 seed × 100 q
# ---------------------------------------------------------------------------

def measure_5mode(s1: dict[int, np.ndarray], s2: dict[int, np.ndarray],
                  sizes: dict[int, int], sigmas: dict[int, float],
                  qids: np.ndarray, q1: np.ndarray, q2: np.ndarray,
                  D1_by_sel: dict[float, np.ndarray], D2_by_sel: dict[float, np.ndarray],
                  true_card: dict[tuple[int, float], int],
                  table_label: str) -> list[dict]:
    rows: list[dict] = []
    # alloc per mode 미리 계산 (mode 마다 동일)
    alloc_by_mode = {m: allocate_samples(m, sizes, sigmas) for m in ALLOC_MODES}
    for mode_name, alloc in alloc_by_mode.items():
        print(f"[{kst()}]   alloc {mode_name}: min={int(alloc.min())} mean={int(alloc.mean())} "
              f"max={int(alloc.max())} (sum={int(alloc.sum())})")

    for sel in SELECTIVITIES:
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        for seed in SEEDS:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            for mode_name in ALL_MODES:
                rng = np.random.default_rng(seed_int)
                t0 = time.time()
                qe_list = []
                for i, qid in enumerate(qids):
                    D1 = float(D1_vec[i])
                    D2 = float(D2_vec[i])
                    tc = true_card[(int(qid), sel)]
                    if mode_name == "bernoulli":
                        est = bernoulli_estimate_dual(s1, s2, sizes, q1[i], q2[i],
                                                       D1, D2, rng)
                    else:
                        alloc = alloc_by_mode[mode_name]
                        est = stratified_estimate_dual(s1, s2, sizes, alloc,
                                                        q1[i], q2[i], D1, D2, rng)
                    qerr = (max(est / tc, tc / est)
                            if (est > 0 and tc > 0) else None)
                    rows.append({
                        "table": table_label, "dataset": table_label,
                        "mode": mode_name,
                        "selectivity": sel, "seed": seed, "query_id": int(qid),
                        "D1_target": D1, "D2_target": D2, "true_card": tc,
                        "est": est, "q_error": qerr,
                    })
                    qe_list.append(qerr if qerr else float("nan"))
                elapsed = time.time() - t0
                med_qe = float(np.nanmedian(qe_list))
                print(f"[{kst()}]     {mode_name:>13} sel={sel:.2f} seed={seed} "
                      f"({elapsed*1000:.0f}ms) med_qe={med_qe:.4f}")
    return rows


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", required=True,
                    choices=["deep_sift_10", "deep_wiki_10", "multi_join_deep_wiki",
                             "deep_sift_1", "deep_wiki_1", "multi_join_deep_wiki_1"])
    ap.add_argument("--out-dir", default=str(CACHE))
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_pq = out_dir / f"rq2_multi_5mode_{args.cell}.parquet"
    out_meta = out_dir / f"rq2_multi_5mode_{args.cell}_meta.json"

    print(f"[{kst()}] === measure_multi_5mode (cell={args.cell}) ===")
    print(f"[{kst()}] out: {out_pq}")

    # 1) load embeddings
    emb1, emb2, table_label = load_cell(args.cell)
    N = emb1.shape[0]
    print(f"[{kst()}] loaded N={N:,} (emb1={emb1.shape[1]}d, emb2={emb2.shape[1]}d) "
          f"label={table_label}")

    # 2) stratification (KM20 on concat)
    print(f"[{kst()}] === stratification ===")
    sids = stratify_concat(emb1, emb2)
    sizes_chk = np.bincount(sids, minlength=N_STRATA)
    print(f"[{kst()}]   strata sizes: min={sizes_chk.min()} mean={int(sizes_chk.mean())} "
          f"max={sizes_chk.max()}")

    # 3) σ per stratum (concat space)
    sizes, sigmas = compute_sigmas(emb1, emb2, sids)
    sg_arr = np.array([sigmas[k] for k in range(N_STRATA)])
    print(f"[{kst()}]   σ_avg={sg_arr.mean():.4f} σ_min={sg_arr.min():.4f} "
          f"σ_max={sg_arr.max():.4f}")

    # 4) cache dual samples
    s1, s2, sizes_cache = cache_dual_samples(emb1, emb2, sids)
    # sizes_cache 와 sizes 일치 확인
    for sid in range(N_STRATA):
        assert sizes_cache[sid] == sizes[sid], f"size mismatch at sid={sid}"

    # 5) query pool + true cards
    print(f"[{kst()}] === query pool + true cardinality ===")
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = build_query_pool(
        emb1, emb2, n_queries=args.n_queries,
    )

    # 6) measurement (5 mode × 5 sel × 5 seed × 100 q = 12500 rows)
    print(f"[{kst()}] === measurement ({len(ALL_MODES)} mode × {len(SELECTIVITIES)} sel × "
          f"{len(SEEDS)} seed × {args.n_queries} q) ===")
    all_rows = measure_5mode(s1, s2, sizes, sigmas, qids, q1, q2,
                              D1_by_sel, D2_by_sel, true_card, table_label)

    # 7) save
    df = pd.DataFrame(all_rows)
    df.to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq} ({len(df):,} rows)")

    smry = (df.groupby(["mode", "selectivity"])["q_error"]
              .agg(["mean", "std", "median", "count"]).round(4))
    print(f"\n=== q_error (mode × sel) ===\n{smry}\n")

    meta = {
        "kst": kst(),
        "cell": args.cell,
        "table_label": table_label,
        "emb1_dim": int(emb1.shape[1]),
        "emb2_dim": int(emb2.shape[1]),
        "N": int(N),
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "n_queries": args.n_queries,
        "n_rows": len(df),
        "modes": ALL_MODES,
        "stratification": "concat (KM20 on [emb1/||emb1|| || emb2/||emb2||])",
        "sigma_definition": "stratum-wise std of distance-to-centroid in normalized concat space",
        "calibration": "per-query D1=quantile(d1, sqrt(sel)), D2=quantile(d2, sqrt(sel))",
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")
    print(f"[{kst()}] === done ===")


if __name__ == "__main__":
    main()
