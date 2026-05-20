#!/usr/bin/env python3
"""B1 2단계 subsampling vs 1단계 direct — 통계적 동등성 검증.

measure_paper_exact.py 의 측정 로직을 그대로 재사용. B1 을 두 경로로 측정:
  OLD: bernoulli_estimate(samples, sizes, ..., all_vecs=None)  → strata-flatten 2단계
  NEW: bernoulli_estimate(samples, sizes, ..., all_vecs=all_vecs) → 80M 직접 1단계
각각 N_SEED 개의 독립 trial seed 로 측정 → qe 분포 (mean/std/min/max) 비교.

추가: strata 캐시가 큰 cluster 를 과소대표하는지 (population reweighting bias) 분석.
"""
import sys, json, time
import numpy as np

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
import _measure_common as mc
import measure_paper_exact as mpe

CELL = sys.argv[1] if len(sys.argv) > 1 else "A1-SIFT"
N_SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 30   # trial seed 개수
N_QUERIES = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
SEL = 0.01

cells = {c.sub: c for c in mpe.build_cell_specs()}
cell = cells[CELL]
print(f"[verify] cell={cell.sub} table={cell.table} N_SEED={N_SEED} N_QUERIES={N_QUERIES} sel={SEL}")

alias = mpe.DATASET_ALIAS.get(cell.dataset, cell.dataset)
from pathlib import Path
ds = {
    "name": cell.dataset, "table": cell.table,
    "embed_col": cell.embed_col, "vec_dim": cell.vec_dim,
    "query_pool": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_pool_{alias}_sf{cell.sf}.parquet"),
    "query_sel": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_{alias}_sf{cell.sf}.parquet"),
}

t0 = time.time()
all_vecs, km20_sids = mc.fetch_all_vectors_safe(ds)
print(f"[verify] all_vecs {all_vecs.shape} loaded in {time.time()-t0:.1f}s")
samples, sizes = mc.cache_cluster_samples_inmem(all_vecs, km20_sids, n_strata=mc.N_STRATA, seed=42)
total_rows = sum(sizes.values())

# --- strata 캐시 bias 분석 ---
flat = np.concatenate([samples[sid] for sid in sorted(samples.keys())], axis=0)
n_flat = flat.shape[0]
print(f"\n[BIAS] === strata 캐시 모집단 분석 ===")
print(f"[BIAS] total_rows(80M)={total_rows:,}  flatten 모집단={n_flat:,}  축소율={n_flat/total_rows*100:.4f}%")
clust_n = np.array([sizes[s] for s in sorted(sizes.keys())])
cache_n = np.array([samples[s].shape[0] for s in sorted(samples.keys())])
print(f"[BIAS] cluster 실제 size: min={clust_n.min():,} mean={clust_n.mean():.0f} max={clust_n.max():,} CV={clust_n.std()/clust_n.mean():.4f}")
print(f"[BIAS] cluster 캐시 size: min={cache_n.min()} mean={cache_n.mean():.0f} max={cache_n.max()}")
# flatten 모집단에서 각 cluster 의 점유 비율 vs 실제 모집단 점유 비율
w_true = clust_n / clust_n.sum()         # 80M 에서 cluster j 비율
w_cache = cache_n / cache_n.sum()        # flatten 모집단에서 cluster j 비율
print(f"[BIAS] cluster 점유비율 — 실제 80M:  {np.round(w_true,4).tolist()}")
print(f"[BIAS] cluster 점유비율 — 캐시 flat: {np.round(w_cache,4).tolist()}")
ratio = w_cache / w_true
print(f"[BIAS] 캐시/실제 점유비 (1=무편향, <1=과소대표, >1=과대대표):")
print(f"[BIAS]   min={ratio.min():.4f}  max={ratio.max():.4f}  큰 cluster일수록 과소대표면 음의 상관")
corr = np.corrcoef(clust_n, ratio)[0,1]
print(f"[BIAS]   corr(cluster_size, 캐시점유비) = {corr:.4f}  (음수 = 큰 cluster 과소대표)")

# --- query pool ---
qp, qs_full, qvecs = mc._load_query_pool(ds)
print(f"\n[verify] query pool {len(qp)} loaded")


def run_b1(seed_base, use_direct):
    """measure_b1_paper 의 trial loop 1회 재현. use_direct=True → NEW(all_vecs 직접)."""
    rng = np.random.default_rng(seed_base)
    state = mpe.AdaptiveState()
    q_errs = []
    for q_idx in range(N_QUERIES):
        q_row_idx = q_idx % len(qp)
        qvec = qvecs[q_row_idx]
        qs_match = qs_full[(np.isclose(qs_full["selectivity"], SEL)) & (qs_full["query_id"] == q_row_idx)]
        if len(qs_match) > 0:
            D = float(qs_match.iloc[0]["D_target"])
            true_card = float(qs_match.iloc[0]["true_cardinality"])
        else:
            D = mpe.TPC_H_THRESHOLD
            true_card = total_rows * SEL
        if use_direct:
            est = mc.bernoulli_estimate(samples, sizes, qvec, D, rng,
                                        budget=state.size, all_vecs=all_vecs)
        else:
            est = mc.bernoulli_estimate(samples, sizes, qvec, D, rng,
                                        budget=state.size)  # all_vecs=None → 기존
        qe = mpe.q_error(est, true_card)
        q_errs.append(qe)
        state.update(qe, state.size / total_rows)
    finite = [v for v in q_errs if np.isfinite(v)]
    return float(np.mean(finite)) if finite else float("inf"), state.size


# --- 측정: 각 경로 N_SEED trial ---
for label, use_direct in [("OLD_2단계", False), ("NEW_1단계", True)]:
    vals, sizes_final = [], []
    t = time.time()
    for s in range(N_SEED):
        # measure_b1_paper 의 seed 식 trial_idx*13+7 을 확장 — 독립 seed
        seed_base = s * 13 + 7
        avg_qe, fsize = run_b1(seed_base, use_direct)
        vals.append(avg_qe); sizes_final.append(fsize)
    vals = np.array(vals)
    # paper trimmed (lowest+highest 1 제외) 도 같이
    trimmed = mpe.trimmed_mean(list(vals), mpe.TRIM)
    print(f"\n[{label}] N_SEED={N_SEED}  ({time.time()-t:.1f}s)")
    print(f"[{label}]   mean={vals.mean():.4f}  std={vals.std():.4f}  min={vals.min():.4f}  max={vals.max():.4f}")
    print(f"[{label}]   trimmed_mean(paper)={trimmed:.4f}  range(max-min)={vals.max()-vals.min():.4f}")
    print(f"[{label}]   final_size mean={np.mean(sizes_final):.0f}")
    print(f"[{label}]   all vals: {np.round(vals,4).tolist()}")
    # 저장
    json.dump({"label": label, "cell": CELL, "vals": vals.tolist(),
               "mean": float(vals.mean()), "std": float(vals.std()),
               "min": float(vals.min()), "max": float(vals.max()),
               "trimmed": float(trimmed), "n_seed": N_SEED},
              open(f"/tmp/b1verify/result_{CELL}_{label}.json", "w"), indent=2)

print("\n[verify] done")
