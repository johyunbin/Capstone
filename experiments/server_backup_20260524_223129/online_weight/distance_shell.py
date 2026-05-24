#!/usr/bin/env python3
"""
RQ3 #9 (P6) — G. Distance-Shell Online Stratification + Neyman 측정 (Python 시뮬레이션).

알고리즘 (per query q with target distance D):
  1. Pilot phase: cache 전체에서 pilot_k 개 uniform sample → distance d_j = ||v - q||
  2. 5개 동심원 shell 분할: pilot 거리의 quantile 5등분 → boundary q_1..q_4
       shell i = [q_{i-1}, q_i)  (i=0..4)
  3. shell 별 σ_i = √(p_i (1-p_i)) (binary hit indicator, pilot 기반)
       N_i = N_total × (pilot_in_shell_i / pilot_k)  (quantile-equal 가정 보정)
  4. Neyman main allocation: target_add_i ∝ N_i × σ_i, sum to (budget - pilot_k)
  5. Main phase: pool size 5×B_rem 만큼 non-pilot uniform sample → 거리 → shell 분류
       각 shell 의 pool 에서 first target_add_i 개 채택 (rejection-based Neyman)
  6. HT estimator (pilot + main 결합):
       est = Σ_i (pilot_hits_i + main_hits_i) × N_i / (pilot_in_shell_i + main_n_i)

KDE-pilot (P5) 와 차이:
  - 분할 단위가 KM20 (precomputed cluster) → **5 distance shells (online, query-adaptive)**
  - σ 추정도 quantile shell 위에서 (KDE-pilot 은 KM cluster 별 σ 추정)
  - 공간 인식이 query 시점에 즉석 — 사전 학습 없음, 단순 (Hilbert/LSH 와 다른 패러다임)

vector.c 패치 우회 — 이미 rq2 에서 검증된 Python 시뮬레이션 패턴 그대로 (cluster 별
LIMIT 500 캐시, fresh conn per cluster, HT 거리 numpy 계산).

서버 실행: scp 후 `python3 -u distance_shell.py` (default n_pilot=50, n_shells=5)
산출: /mnt/hdd0/home/capstone2026/cache/rq1/rq3_distance_shell.parquet
"""
import argparse
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import pyarrow.parquet as pq

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
PORT = 55436
DB = "wns41559"
USER = "wns41559"
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_STRATA = 20            # KM cache 단위 (shell 과 무관, cache 로딩에만 사용)
CACHE_PER_CLUSTER = 500
N_PILOT = 50             # query 별 pilot 개수 (5 shell ⇒ avg 10/shell)
N_SHELLS = 5

DATASETS = [
    {
        "name": "DEEP",
        "table": "partsupp_deep_10_subset_1m",
        "embed_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity.parquet",
    },
    {
        "name": "SIFT",
        "table": "customer_sift_10_phase7_noidx_subset",
        "embed_col": "c_embedding",
        "vec_dim": 128,
        "query_pool": CACHE / "query_pool_sift.parquet",
        "query_sel": CACHE / "query_selectivity_sift_v2.parquet",
    },
]

ALL_MODES = ["bernoulli", "distance_shell"]


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def cache_cluster_samples(ds):
    """NPY cache fast-path (5/8 fix): {table}_vectors.npy + {table}_strata.npy → no PG roundtrip.

    Falls back to PG-based (LIMIT/cluster) loading when NPY caches are missing.
    """
    from pathlib import Path as _P
    import numpy as _np

    _CACHE = _P("/mnt/hdd0/home/capstone2026/cache/rq1")
    table = ds["table"]
    vec_npy = _CACHE / f"{table}_vectors.npy"
    strata_npy = _CACHE / f"{table}_strata.npy"

    if vec_npy.exists() and strata_npy.exists():
        print(f"[{kst()}]   caching {ds['name']} cluster samples (NPY fast-path)...")
        t0 = time.time()
        all_vecs = _np.load(vec_npy)
        all_sids = _np.load(strata_npy).astype(int)
        rng = _np.random.default_rng(42)
        samples = {}
        sizes = {}
        for sid in range(N_STRATA):
            mask = all_sids == sid
            n_cluster = int(mask.sum())
            sizes[sid] = n_cluster
            if n_cluster == 0:
                samples[sid] = _np.zeros((0, all_vecs.shape[1]), dtype=_np.float32)
                continue
            cluster_vecs = all_vecs[mask].astype(_np.float32)
            if n_cluster > CACHE_PER_CLUSTER:
                idx = rng.choice(n_cluster, size=CACHE_PER_CLUSTER, replace=False)
                samples[sid] = cluster_vecs[idx]
            else:
                samples[sid] = cluster_vecs
        elapsed = time.time() - t0
        total_mb = sum(s.nbytes for s in samples.values()) / 1e6
        total_rows = sum(s.shape[0] for s in samples.values())
        print(f"[{kst()}]   cached {total_rows} rows ({total_mb:.1f} MB) in {elapsed:.1f}s [npy]")
        return samples, sizes

    # Fallback: PG-based loading (original logic)
    print(f"[{kst()}]   caching {ds['name']} cluster samples (LIMIT {CACHE_PER_CLUSTER}/cluster, PG)...")
    samples = {}
    sizes = {}

    with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(
            f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} "
            f"GROUP BY stratum_id ORDER BY stratum_id"
        )
        for sid, n in cu.fetchall():
            sizes[sid] = int(n)

    t0 = time.time()
    for sid in range(N_STRATA):
        with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT {ds['embed_col']}::real[] FROM {ds['table']} "
                f"WHERE stratum_id = {sid} LIMIT {CACHE_PER_CLUSTER}"
            )
            rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
        if not rows:
            samples[sid] = np.zeros((0, ds["vec_dim"]), dtype=np.float32)
        else:
            samples[sid] = np.stack(rows)
    elapsed = time.time() - t0
    total_mb = sum(s.nbytes for s in samples.values()) / 1e6
    total_rows = sum(s.shape[0] for s in samples.values())
    print(f"[{kst()}]   cached {total_rows} rows ({total_mb:.1f} MB) in {elapsed:.1f}s")
    return samples, sizes


def distance_shell_estimate(flat_cache, total_rows, qvec, D, rng,
                            budget=SAMPLE_SIZE, pilot_k=N_PILOT, n_shells=N_SHELLS):
    """
    Online distance-shell stratification with Neyman allocation.

    flat_cache: shape (n_cache, dim). 모든 cluster sample 합친 numpy array.
    """
    n_cache = flat_cache.shape[0]
    if n_cache == 0:
        return float(total_rows)
    pilot_k = min(int(pilot_k), n_cache)

    # ── Phase 1: pilot uniform ──
    pilot_idxs = rng.choice(n_cache, size=pilot_k, replace=False)
    pilot_dists = np.linalg.norm(flat_cache[pilot_idxs] - qvec, axis=1)
    pilot_hits = (pilot_dists < D).astype(np.int64)

    # ── Phase 2: 5 quantile shells (boundaries from pilot distances) ──
    qs_inner = np.quantile(pilot_dists, np.linspace(0.0, 1.0, n_shells + 1))[1:-1]
    pilot_shells = np.minimum(np.searchsorted(qs_inner, pilot_dists), n_shells - 1)

    # ── Phase 3: σ_i, N_i per shell (pilot 기반 추정) ──
    sigma_i = np.zeros(n_shells, dtype=np.float64)
    pilot_in_shell = np.zeros(n_shells, dtype=np.int64)
    pilot_hits_in_shell = np.zeros(n_shells, dtype=np.int64)
    for i in range(n_shells):
        m = pilot_shells == i
        n = int(m.sum())
        pilot_in_shell[i] = n
        pilot_hits_in_shell[i] = int(pilot_hits[m].sum())
        if n > 0:
            p = pilot_hits_in_shell[i] / n
            sigma_i[i] = float(np.sqrt(max(p * (1.0 - p), 1e-9)))
    N_i = np.array(
        [total_rows * (pilot_in_shell[i] / pilot_k) for i in range(n_shells)],
        dtype=np.float64,
    )

    # ── Phase 4: Neyman main allocation ──
    B_rem = int(budget) - pilot_k
    if B_rem <= 0:
        # pilot 만 사용한 shell-stratified 추정
        est = 0.0
        for i in range(n_shells):
            if pilot_in_shell[i] > 0:
                est += pilot_hits_in_shell[i] * (N_i[i] / pilot_in_shell[i])
        return float(est)

    w = N_i * sigma_i
    if w.sum() <= 1e-12:
        # 모든 σ 0 (pilot hit 0 또는 전부 1) → proportional fallback
        w = N_i.copy()
        if w.sum() <= 1e-12:
            w = np.ones(n_shells)
    f = w / w.sum() * B_rem
    target_add = np.maximum(f.astype(np.int64), 1)
    extra = B_rem - int(target_add.sum())
    if extra > 0:
        order = np.argsort(-(f - f.astype(np.int64)))
        for j in range(extra):
            target_add[order[j % n_shells]] += 1
    elif extra < 0:
        # 최소 1 보장으로 budget 초과 (드뭄, n_shells=5 ≪ B_rem)
        order = np.argsort(-target_add)
        decrements = -extra
        idx = 0
        while decrements > 0 and idx < 100 * n_shells:
            slot = order[idx % n_shells]
            if target_add[slot] > 1:
                target_add[slot] -= 1
                decrements -= 1
            idx += 1

    # ── Phase 5: rejection sampling per shell from non-pilot pool ──
    pilot_mask = np.zeros(n_cache, dtype=bool)
    pilot_mask[pilot_idxs] = True
    remaining_idxs = np.where(~pilot_mask)[0]
    if len(remaining_idxs) == 0:
        return float(np.dot(pilot_hits_in_shell,
                            np.where(pilot_in_shell > 0, N_i / np.maximum(pilot_in_shell, 1), 0.0)))
    pool_size = min(len(remaining_idxs), max(B_rem * 5, 1000))
    pick_idxs = rng.choice(remaining_idxs, size=pool_size, replace=False)
    pick_dists = np.linalg.norm(flat_cache[pick_idxs] - qvec, axis=1)
    pick_shells = np.minimum(np.searchsorted(qs_inner, pick_dists), n_shells - 1)
    pick_hits = (pick_dists < D).astype(np.int64)

    add_n = np.zeros(n_shells, dtype=np.int64)
    add_hits = np.zeros(n_shells, dtype=np.int64)
    for i in range(n_shells):
        m = pick_shells == i
        if not m.any():
            continue
        avail = int(m.sum())
        n_take = min(int(target_add[i]), avail)
        # pool 은 이미 random 순서이므로 first n_take 채택해도 무작위
        shell_local_idx = np.where(m)[0][:n_take]
        add_n[i] = n_take
        add_hits[i] = int(pick_hits[shell_local_idx].sum())

    # ── Phase 6: HT estimator (pilot + main 결합) ──
    est = 0.0
    for i in range(n_shells):
        n_used = int(pilot_in_shell[i] + add_n[i])
        h = int(pilot_hits_in_shell[i] + add_hits[i])
        if n_used > 0:
            est += h * (N_i[i] / n_used)
    return float(est)


def bernoulli_estimate(flat_cache, total_rows, qvec, D, rng, budget=SAMPLE_SIZE):
    """TABLESAMPLE BERNOULLI baseline — RANDOM20 와 동일 (rq2_alloc 동등 로직)."""
    n = flat_cache.shape[0]
    s = min(int(budget), n)
    if s == 0:
        return float(total_rows)
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat_cache[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (total_rows / s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-prefix", default="rq3_distance_shell")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--modes", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--n-pilot", type=int, default=N_PILOT,
                    help="query 별 pilot uniform sample 수 (default 50)")
    ap.add_argument("--n-shells", type=int, default=N_SHELLS,
                    help="distance quantile shell 수 (default 5)")
    args = ap.parse_args()

    print(f"[{kst()}] === RQ3 #9 (P6) — G. Distance-Shell Online (Python 시뮬레이션) ===")
    use_modes = ALL_MODES if not args.modes else [m for m in ALL_MODES if m in args.modes]
    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d["name"] in args.datasets]
    print(f"[{kst()}] modes: {use_modes}, n_pilot={args.n_pilot}, n_shells={args.n_shells}, "
          f"budget={SAMPLE_SIZE}")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}")

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        samples, sizes = cache_cluster_samples(ds)
        total_rows = sum(sizes.values())
        flat_cache = np.concatenate([samples[sid] for sid in range(N_STRATA)
                                     if samples[sid].shape[0] > 0], axis=0)
        print(f"[{kst()}]   N_total={total_rows}, flat_cache shape={flat_cache.shape}")

        qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
        qs_full = pq.read_table(ds["query_sel"]).to_pandas()
        qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32)
                          for i in range(len(qp))])
        print(f"[{kst()}]   loaded {len(qp)} queries (dim={qvecs.shape[1]}), "
              f"{len(qs_full)} sel rows")

        for mode in use_modes:
            t_mode = time.time()
            for sel in SELECTIVITIES:
                qs_sel = qs_full[
                    (np.isclose(qs_full["selectivity"], sel)) &
                    (qs_full["query_id"] < args.n_queries)
                ].sort_values("query_id").reset_index(drop=True)
                if len(qs_sel) == 0:
                    continue
                for seed in SEEDS:
                    seed_int = int(seed * 10**9) % (2**31 - 1)
                    rng = np.random.default_rng(seed_int)
                    t0 = time.time()
                    qe_list = []
                    for _, row in qs_sel.iterrows():
                        qid = int(row["query_id"])
                        D = float(row["D_target"])
                        true_card = int(row["true_cardinality"])
                        qvec = qvecs[qid]
                        if mode == "bernoulli":
                            est = bernoulli_estimate(flat_cache, total_rows, qvec, D, rng,
                                                     SAMPLE_SIZE)
                        else:  # distance_shell
                            est = distance_shell_estimate(flat_cache, total_rows, qvec, D, rng,
                                                          SAMPLE_SIZE, args.n_pilot,
                                                          args.n_shells)
                        if est > 0 and true_card > 0:
                            qerr = max(est / true_card, true_card / est)
                        else:
                            qerr = None
                        all_rows.append({
                            "dataset": ds["name"], "mode": mode, "selectivity": sel,
                            "seed": seed, "query_id": qid, "D_target": D,
                            "true_card": true_card, "est": est, "q_error": qerr,
                            "n_pilot": args.n_pilot, "n_shells": args.n_shells,
                        })
                        qe_list.append(qerr if qerr else float("nan"))
                    elapsed = time.time() - t0
                    valid = sum(1 for q in qe_list if q == q)
                    med = float(np.nanmedian(qe_list)) if valid else float("nan")
                    print(f"[{kst()}]   {ds['name']} {mode:>14} s={sel:.2f} seed={seed} "
                          f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} med_qe={med:.4f}")
            print(f"[{kst()}] {ds['name']} {mode:>14}: total {time.time() - t_mode:.1f}s")

    full_df = pd.DataFrame(all_rows)
    out_pq = CACHE / f"{args.out_prefix}.parquet"
    full_df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(full_df)} rows)")

    print("\n=== mean q_error per (dataset × mode × sel) ===")
    smry = full_df.groupby(["dataset", "mode", "selectivity"])["q_error"].agg(
        ["mean", "std", "median", "count"]
    ).round(4)
    print(smry)

    meta = {
        "kst": kst(),
        "args": vars(args),
        "datasets": [d["name"] for d in use_datasets],
        "modes": use_modes,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "n_queries": args.n_queries,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "n_pilot": args.n_pilot,
        "n_shells": args.n_shells,
        "elapsed_s": round(time.time() - t_total, 1),
    }
    with open(CACHE / f"{args.out_prefix}_meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] total elapsed {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
