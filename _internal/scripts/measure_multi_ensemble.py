#!/usr/bin/env python3
"""
Multi-cell × 11 method × Adaptive Sampling ensemble 측정 — RQ3 ⭐⭐⭐ 확장.

5/9 사용자 결정 (single+multi 모두 강한 RQ3 method 후보 brainstorming):
    "Adaptive 의 dynamic budget × RQ3 stratification 결합" 의 multi 환경 검증.
    단일 ensemble 측정 (10 cell × 11 method, 110 set) 에서 minibatch ensemble
    rank 1 (10/10 win + 9/10 sig vs Adaptive) 확인 → multi 환경에서도 동일
    효과인지 측정.

구조:
    1. multi cell (4-way 또는 join) 에서 emb1+emb2 fetch + norm-aware concat
       (measure_multi_paradigm.py 와 동일)
    2. 11 method 별 stratify_method() 호출 → stratum_id 부여
    3. cache_dual_samples 으로 cluster 별 dual sample 캐시
    4. AdaptiveState (식 1~6) 가 매 50 query 마다 total budget S_t 갱신
    5. cluster 별 sample size = S_t × proportional weight (cluster N_i / total N)
    6. estimator: stratified_estimate_dual (alloc 만 동적)

paired alignment:
    동일 (cell × seed × sel × query_id) 격자 → multi_adaptive_<cell>.csv
    + multi_paradigm_<cell>.csv 와 inner-join Δ% 계산 가능. mode 컬럼:
    'ensemble_<base>' (e.g. ensemble_HDBSCAN).

규모:
    6 cell × 11 method × 5 sel × 5 seed × 100 q = 16,500 measurement
    예상 ~10-12h (Adaptive 학습 cost 0 + multi paradigm 의 4h46m 측정 reference).

산출:
    {CACHE}/multi_ensemble/multi_ensemble_<cell>.csv  (cell 별 통합)
    columns: table, mode, base_method, paradigm, selectivity, seed, query_id,
             D1_target, D2_target, true_card, est, q_error,
             sample_size_used, total_sample_size

CLI:
    python3 _internal/scripts/measure_multi_ensemble.py \
        --cells partsupp_deep_sift_10 partsupp_deep_wiki_10 multi_join_deep_wiki \
                partsupp_deep_sift_1  partsupp_deep_wiki_1  multi_join_deep_wiki_1 \
        --methods HDBSCAN MiniBatch GMM Hilbert faiss_ivf MB_partial \
                  Reservoir sparse_rp PCA1D LSH Sobol

서버 launch (cell × method loop):
    nohup python3 _internal/scripts/measure_multi_ensemble.py \
        --cells partsupp_deep_sift_10 ... \
        --methods HDBSCAN ... \
        > /mnt/hdd0/home/capstone2026/log/multi_ensemble_$(date +%Y%m%d_%H%M).log 2>&1 &
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup — 서버 우선, 로컬 dry-run fallback
# ---------------------------------------------------------------------------

ROOT_SERVER = Path("/mnt/hdd0/home/capstone2026/cache/rq3")
ROOT_LOCAL = Path("/Users/hyunbin/Capstone/experiments/code/rq3")
ROOT = ROOT_SERVER if ROOT_SERVER.exists() else ROOT_LOCAL
sys.path.insert(0, str(ROOT))

SCRIPTS_PATH = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_PATH))

# measure_multi_paradigm 의 cell config + stratify_method + build_concat 재사용
from measure_multi_paradigm import (  # noqa: E402
    CELL_4WAY, CELL_JOIN, ALL_CELLS,
    METHOD_MAP, PARADIGM,
    build_concat, stratify_method,
    _lazy_imports, _FALLBACK_CONSTS,
)


# ---------------------------------------------------------------------------
# AdaptiveState (식 1~6) — run_adaptive_sampling.py 의 in-memory 재현
# ---------------------------------------------------------------------------

class AdaptiveState:
    """Exqutor §V-B Algorithm 1: Adaptive Sample Size Update.

    매 update_period (default 50) query 마다 다음 budget S_t+1 갱신:
        prev_loss = abs(median(qe_recent) - β) ≥ threshold τ?
        velocity_t = γ * velocity_{t-1} + (1 - γ) * gradient
        S_{t+1} = clip(S_t + α * velocity_t, min_size, max_size)
    """

    def __init__(self, *, momentum=0.9, learning_rate=0.1,
                  alpha=50.0, beta=1.5, gamma=0.99, update_period=50,
                  min_size=50, max_size=5000, init_S=385):
        self.m = momentum
        self.eta0 = learning_rate
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.period = update_period
        self.min_size = min_size
        self.max_size = max_size
        self.S = float(init_S)
        self.velocity = 0.0
        self.eta = self.eta0

    def step(self, recent_median_qerror: float):
        """Update budget based on prev period median qerror."""
        if not np.isfinite(recent_median_qerror):
            return
        prev_loss = abs(recent_median_qerror - self.beta)
        # gradient: qerror 가 β 보다 크면 + (budget 늘려야), 작으면 -
        gradient = (recent_median_qerror - self.beta)
        self.velocity = self.gamma * self.velocity + (1 - self.gamma) * gradient
        self.eta = self.eta0 * (self.m ** prev_loss)
        delta = self.alpha * self.eta * self.velocity
        self.S = float(np.clip(self.S + delta, self.min_size, self.max_size))


# ---------------------------------------------------------------------------
# proportional_alloc_dynamic — run_ensemble_4kang_adaptive.py 와 동일
# ---------------------------------------------------------------------------

def proportional_alloc_dynamic(sizes: dict, total_budget: int,
                                 n_strata: int = 20) -> np.ndarray:
    """매 query 마다 호출. total_budget (Adaptive S_t) 을 cluster N_i 비례 분배."""
    sz = np.array([sizes.get(j, 0) for j in range(n_strata)], dtype=float)
    if sz.sum() <= 0:
        base = int(total_budget) // n_strata
        extra = int(total_budget) - base * n_strata
        s = np.full(n_strata, base, dtype=int)
        s[:extra] += 1
        return np.maximum(s, 1)
    f = sz / sz.sum() * total_budget
    s = np.maximum(f.astype(int), 1)
    extra = int(total_budget) - int(s.sum())
    if extra > 0:
        frac = f - f.astype(int)
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    return s


# ---------------------------------------------------------------------------
# 4-way cell ensemble measurement
# ---------------------------------------------------------------------------

def measure_ensemble_4way(cell_name: str, methods_user: list[str],
                            consts: dict, helpers: dict,
                            n_queries: int, learn_frac: float, learn_seed: int,
                            adaptive_kwargs: dict) -> list[dict]:
    """multi-vector cell ensemble 측정 (dual stratified estimator + Adaptive budget)."""
    from measure_multi_vector import cache_dual_samples, stratified_estimate_dual  # noqa

    cfg = CELL_4WAY[cell_name]
    table = cfg["table"]
    kst = consts["kst"]
    SELECTIVITIES = consts["SELECTIVITIES"]
    SEEDS = consts["SEEDS"]
    N_STRATA = consts["N_STRATA"]
    SAMPLE_SIZE = consts["SAMPLE_SIZE"]

    print(f"[{kst()}] === ensemble 4way: cell={cell_name} ===")

    emb1, emb2 = helpers["fetch_dual_vectors"](
        table, cfg["emb1_col"], cfg["emb2_col"],
        cfg["emb1_dim"], cfg["emb2_dim"],
    )
    N = emb1.shape[0]
    print(f"[{kst()}] N={N:,} dims=({emb1.shape[1]}, {emb2.shape[1]})")

    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = helpers["build_query_pool"](
        emb1, emb2, n_queries=n_queries,
    )

    concat = build_concat(emb1, emb2)
    print(f"[{kst()}]   concat shape={concat.shape}")

    all_rows: list[dict] = []
    for m_user in methods_user:
        m_canon = METHOD_MAP[m_user]
        print(f"\n[{kst()}] === ensemble_{m_user} ({m_canon}, {PARADIGM[m_user]}) ===")
        sids = stratify_method(
            m_canon, concat, kst,
            learn_frac=learn_frac, seed=learn_seed,
            n_strata=N_STRATA,
        )
        s1, s2, sizes = cache_dual_samples(emb1, emb2, sids)
        print(f"[{kst()}]   stratum sizes "
              f"min={min(sizes.values())} max={max(sizes.values())}")

        for sel in SELECTIVITIES:
            D1_vec = D1_by_sel[sel]
            D2_vec = D2_by_sel[sel]
            for seed in SEEDS:
                seed_int = int(seed * 10**9) % (2**31 - 1)
                rng = np.random.default_rng(seed_int)
                state = AdaptiveState(
                    init_S=SAMPLE_SIZE, **adaptive_kwargs,
                )
                qe_recent = []

                t0 = time.time()
                for i, qid in enumerate(qids):
                    D1 = float(D1_vec[i])
                    D2 = float(D2_vec[i])
                    tc = true_card[(int(qid), sel)]

                    alloc = proportional_alloc_dynamic(
                        sizes, int(state.S), n_strata=N_STRATA,
                    )
                    used = int(alloc.sum())
                    est = stratified_estimate_dual(
                        s1, s2, sizes, alloc, q1[i], q2[i], D1, D2, rng,
                        n_strata=N_STRATA,
                    )
                    qerr = (max(est / tc, tc / est)
                            if (est > 0 and tc > 0) else None)
                    qe_recent.append(qerr if qerr else float("nan"))

                    all_rows.append({
                        "table": table, "dataset": table,
                        "mode": f"ensemble_{m_user}",
                        "base_method": m_user, "paradigm": PARADIGM[m_user],
                        "selectivity": sel, "seed": seed,
                        "query_id": int(qid),
                        "D1_target": D1, "D2_target": D2, "true_card": tc,
                        "est": est, "q_error": qerr,
                        "sample_size_used": used,
                        "total_sample_size": int(state.S),
                    })

                    # Adaptive update
                    if (i + 1) % state.period == 0 and len(qe_recent) >= state.period:
                        med = float(np.nanmedian(qe_recent[-state.period:]))
                        state.step(med)

                elapsed = time.time() - t0
                med_q = float(np.nanmedian(qe_recent))
                print(f"[{kst()}]     ensemble_{m_user:>10} sel={sel:.2f} "
                      f"seed={seed} ({elapsed*1000:.0f}ms) med_qe={med_q:.4f} "
                      f"final_S={int(state.S)}")
    return all_rows


# ---------------------------------------------------------------------------
# join cell ensemble measurement
# ---------------------------------------------------------------------------

def measure_ensemble_join(cell_name: str, methods_user: list[str],
                            consts: dict, helpers: dict,
                            n_queries: int, learn_frac: float, learn_seed: int,
                            adaptive_kwargs: dict) -> list[dict]:
    """multi-table-join cell ensemble 측정."""
    from measure_multi_vector import cache_dual_samples, stratified_estimate_dual  # noqa

    cfg = CELL_JOIN[cell_name]
    kst = consts["kst"]
    SELECTIVITIES = consts["SELECTIVITIES"]
    SEEDS = consts["SEEDS"]
    N_STRATA = consts["N_STRATA"]
    SAMPLE_SIZE = consts["SAMPLE_SIZE"]

    print(f"[{kst()}] === ensemble join: cell={cell_name} ===")

    ps_emb, ps_keys = helpers["fetch_partsupp"](
        cfg["partsupp_table"], cfg["partsupp_emb_col"], cfg["partsupp_emb_dim"],
    )
    p_emb, p_keys = helpers["fetch_part"](
        cfg["part_table"], cfg["part_emb_col"], cfg["part_emb_dim"],
    )
    deep_join, wiki_join = helpers["build_join"](ps_emb, ps_keys, p_emb, p_keys)
    print(f"[{kst()}] join: deep {deep_join.shape}, wiki {wiki_join.shape}")

    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = helpers["build_query_pool_join"](
        deep_join, wiki_join, n_queries=n_queries,
    )

    concat = build_concat(deep_join, wiki_join)
    print(f"[{kst()}]   concat shape={concat.shape}")

    table_name = f"{cfg['partsupp_table']}_join_{cfg['part_table']}"
    all_rows: list[dict] = []
    for m_user in methods_user:
        m_canon = METHOD_MAP[m_user]
        print(f"\n[{kst()}] === ensemble_{m_user} ({m_canon}, {PARADIGM[m_user]}) ===")
        sids = stratify_method(
            m_canon, concat, kst,
            learn_frac=learn_frac, seed=learn_seed,
            n_strata=N_STRATA,
        )
        s1, s2, sizes = cache_dual_samples(deep_join, wiki_join, sids)
        print(f"[{kst()}]   stratum sizes "
              f"min={min(sizes.values())} max={max(sizes.values())}")

        for sel in SELECTIVITIES:
            D1_vec = D1_by_sel[sel]
            D2_vec = D2_by_sel[sel]
            for seed in SEEDS:
                seed_int = int(seed * 10**9) % (2**31 - 1)
                rng = np.random.default_rng(seed_int)
                state = AdaptiveState(
                    init_S=SAMPLE_SIZE, **adaptive_kwargs,
                )
                qe_recent = []

                t0 = time.time()
                for i, qid in enumerate(qids):
                    D1 = float(D1_vec[i])
                    D2 = float(D2_vec[i])
                    tc = true_card[(int(qid), sel)]

                    alloc = proportional_alloc_dynamic(
                        sizes, int(state.S), n_strata=N_STRATA,
                    )
                    used = int(alloc.sum())
                    est = stratified_estimate_dual(
                        s1, s2, sizes, alloc, q1[i], q2[i], D1, D2, rng,
                        n_strata=N_STRATA,
                    )
                    qerr = (max(est / tc, tc / est)
                            if (est > 0 and tc > 0) else None)
                    qe_recent.append(qerr if qerr else float("nan"))

                    all_rows.append({
                        "table_pair": table_name, "dataset": table_name,
                        "mode": f"ensemble_{m_user}",
                        "base_method": m_user, "paradigm": PARADIGM[m_user],
                        "selectivity": sel, "seed": seed,
                        "query_id": int(qid),
                        "D_deep_target": D1, "D_wiki_target": D2, "true_card": tc,
                        "est": est, "q_error": qerr,
                        "sample_size_used": used,
                        "total_sample_size": int(state.S),
                    })

                    if (i + 1) % state.period == 0 and len(qe_recent) >= state.period:
                        med = float(np.nanmedian(qe_recent[-state.period:]))
                        state.step(med)

                elapsed = time.time() - t0
                med_q = float(np.nanmedian(qe_recent))
                print(f"[{kst()}]     ensemble_{m_user:>10} sel={sel:.2f} "
                      f"seed={seed} ({elapsed*1000:.0f}ms) med_qe={med_q:.4f} "
                      f"final_S={int(state.S)}")
    return all_rows


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--cells", nargs="+", required=True, choices=ALL_CELLS,
                    help="측정할 multi cell")
    ap.add_argument("--methods", nargs="+", required=True,
                    choices=list(METHOD_MAP.keys()),
                    help="11 paradigm method")
    ap.add_argument("--out-dir", default=None,
                    help="CSV 출력 dir (default: server cache/rq3/multi_ensemble)")
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)

    # AdaptiveState hyperparam — Exqutor §VI 그대로
    ap.add_argument("--momentum", type=float, default=0.9)
    ap.add_argument("--lr0", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=50.0)
    ap.add_argument("--beta", type=float, default=1.5)
    ap.add_argument("--gamma", type=float, default=0.99)
    ap.add_argument("--update-period", type=int, default=50)
    ap.add_argument("--min-size", type=int, default=50)
    ap.add_argument("--max-size", type=int, default=5000)

    ap.add_argument("--dry-run", action="store_true",
                    help="DB X — CLI / import 검증만")
    args = ap.parse_args()

    if args.dry_run:
        print("=== dry-run: CLI + import 검증 ===")
        print(f"cells:   {args.cells}")
        print(f"methods: {args.methods}")
        print(f"  paradigm map:")
        for m in args.methods:
            print(f"    {m:>12} → {METHOD_MAP[m]:<12} ({PARADIGM[m]})")
        consts = _FALLBACK_CONSTS
        n_per_cm = (
            len(consts["SELECTIVITIES"]) * len(consts["SEEDS"]) * args.n_queries
        )
        total = len(args.cells) * len(args.methods) * n_per_cm
        print(f"\n[estimate] {len(args.cells)} cell × {len(args.methods)} method "
              f"× {len(consts['SELECTIVITIES'])} sel × {len(consts['SEEDS'])} seed "
              f"× {args.n_queries} q = {total:,} measurement (~10-12h estimated)")
        print(f"adaptive: m={args.momentum}, η₀={args.lr0}, α={args.alpha}, "
              f"β={args.beta}, γ={args.gamma}, period={args.update_period}, "
              f"S_init={consts['SAMPLE_SIZE']}, range=[{args.min_size},{args.max_size}]")
        print("\n=== dry-run OK ===")
        return

    consts, helpers = _lazy_imports()
    kst = consts["kst"]

    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        if consts.get("CACHE") and Path(consts["CACHE"]).exists():
            out_dir = Path(consts["CACHE"]) / "multi_ensemble"
        else:
            out_dir = SCRIPTS_PATH.parent / "cache" / "rq3" / "multi_ensemble"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{kst()}] out_dir: {out_dir}")

    print(f"[{kst()}] === measure_multi_ensemble (Adaptive × 11 method) ===")
    print(f"[{kst()}] cells:   {args.cells}")
    print(f"[{kst()}] methods: {args.methods}")
    print(f"[{kst()}] adaptive: m={args.momentum}, η₀={args.lr0}, α={args.alpha}, "
          f"β={args.beta}, γ={args.gamma}, period={args.update_period}")

    adaptive_kwargs = {
        "momentum": args.momentum, "learning_rate": args.lr0,
        "alpha": args.alpha, "beta": args.beta, "gamma": args.gamma,
        "update_period": args.update_period,
        "min_size": args.min_size, "max_size": args.max_size,
    }

    t_total = time.time()
    for cell in args.cells:
        print(f"\n[{kst()}] ###### CELL {cell} ######")
        out_csv = out_dir / f"multi_ensemble_{cell}.csv"
        out_meta = out_dir / f"multi_ensemble_{cell}_meta.json"
        if out_csv.exists():
            print(f"[{kst()}] SKIP — {out_csv.name} already exists")
            continue

        t_cell = time.time()
        if cell in CELL_4WAY:
            rows = measure_ensemble_4way(
                cell, args.methods, consts, helpers,
                args.n_queries, args.learn_frac, args.learn_seed,
                adaptive_kwargs,
            )
            kind = "4way"
        else:
            rows = measure_ensemble_join(
                cell, args.methods, consts, helpers,
                args.n_queries, args.learn_frac, args.learn_seed,
                adaptive_kwargs,
            )
            kind = "join"

        df = pd.DataFrame(rows)
        df.to_csv(out_csv, index=False)
        meta = {
            "cell": cell, "kind": kind, "n_rows": len(rows),
            "methods": args.methods,
            "elapsed_s": round(time.time() - t_cell, 1),
            "adaptive_hyperparam": adaptive_kwargs,
            "init_S": consts["SAMPLE_SIZE"], "n_strata": consts["N_STRATA"],
            "n_queries": args.n_queries,
            "selectivities": consts["SELECTIVITIES"], "seeds": consts["SEEDS"],
            "build_time_kst": kst(),
        }
        with open(out_meta, "w") as f:
            json.dump(meta, f, indent=2)
        print(f"[{kst()}] CELL {cell} done ({len(rows)} rows, "
              f"{time.time() - t_cell:.0f}s)")

    print(f"\n[{kst()}] === all cells done ({time.time() - t_total:.0f}s) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
