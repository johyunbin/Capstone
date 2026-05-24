#!/usr/bin/env python3
"""
Multi-cell Exqutor Adaptive Sampling baseline (arXiv:2512.09695v2 §V-B).

5/8 회의 결정 ⭐⭐⭐: 본 연구 4강 (HDBSCAN / MB_partial / Hilbert / sparse RP)
대비 Exqutor 본 논문 Adaptive Sampling 의 multi-table paired Δ% 비교용 baseline.
단일 cell 용 `run_adaptive_sampling.py` (chain_unified 패턴, 식 1~6 + Section VI
hyperparam) 의 multi-cell 확장.

대상 cell 3종:
  - partsupp_deep_sift_10  : multi-vector (deep 96d + sift 128d, 단일 테이블 4-way)
  - partsupp_deep_wiki_10  : multi-vector (deep 96d + wiki 768d, 단일 테이블 4-way)
  - multi_join_deep_wiki   : multi-table join (partsupp_deep_10 ⨝ part_wiki_10)

Per-table separate state (Exqutor §V-B):
  본 논문 — "the optimizer maintains separate sample size states for each table".
  본 구현 — 각 cell 마다 두 vector view (table1 / table2) 별 AdaptiveState 를
  독립적으로 운영. 매 query 마다 두 view 가 각자 자기 sample_size 로 random
  sample → 두 표본의 hit-rate 를 곱한 뒤 N 을 곱해 joint cardinality 를 추정 (조건
  독립 가정, Adaptive 가 multi-table 에서 채택하는 표준 외삽).
  - multi-vector (4way): table1=emb1, table2=emb2. 표본은 row 인덱스 기준 독립.
  - multi-table join:    table1=partsupp deep_join, table2=part wiki_join (broadcast 후).
  state, q_error 은 per-table 로 추적되지만, 기록되는 q_error 는 *joint* est vs
  joint true_card (paired alignment 기준은 4강 / paradigm 측정과 동일하게 query_id ×
  selectivity × seed).

Hyperparameter (단일 run_adaptive_sampling.py 의 Section VI 기본값 그대로 유지):
  m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50, init_N=385, min=50, max=5000

산출 row schema (rq2_multi_5mode_* 호환 + adaptive 추가 컬럼):
  - 4way:  table, dataset, mode, selectivity, seed, query_id,
           D1_target, D2_target, true_card, est, q_error,
           sample_size_used_t1, sample_size_used_t2
  - join:  table_pair, dataset, mode, selectivity, seed, query_id,
           D_deep_target, D_wiki_target, true_card, est, q_error,
           sample_size_used_t1, sample_size_used_t2

CLI:
  python3 measure_multi_adaptive_sampling.py \\
      --cells partsupp_deep_sift_10 partsupp_deep_wiki_10 multi_join_deep_wiki

  python3 measure_multi_adaptive_sampling.py --dry-run --cells multi_join_deep_wiki

서버 launch (5/9 daytime 또는 evening, multi 11-method 와 sequential):
  nohup python3 -u /mnt/hdd0/home/capstone2026/cache/rq3/measure_multi_adaptive_sampling.py \\
      --cells partsupp_deep_sift_10 partsupp_deep_wiki_10 multi_join_deep_wiki \\
      > /mnt/hdd0/home/capstone2026/logs/multi_adaptive_20260509.log 2>&1 &
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Path setup — 서버 경로 우선, 로컬 dry-run fallback (measure_multi_paradigm 과 동일)
# ---------------------------------------------------------------------------

ROOT_SERVER = Path("/mnt/hdd0/home/capstone2026/cache/rq3")
ROOT_LOCAL = Path("/Users/hyunbin/Capstone/experiments/code/rq3")
ROOT = ROOT_SERVER if ROOT_SERVER.exists() else ROOT_LOCAL
sys.path.insert(0, str(ROOT))

SCRIPTS_PATH = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_PATH))


# ---------------------------------------------------------------------------
# 상수 — 단일 run_adaptive_sampling.py 와 동일 (_measure_common.SAMPLE_SIZE 등)
# ---------------------------------------------------------------------------

SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_QUERIES = 100


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Cell config (measure_multi_paradigm 와 동일 — 4way 2종 + join 1종)
# ---------------------------------------------------------------------------

CELL_4WAY = {
    "partsupp_deep_sift_10": {
        "table": "partsupp_deep_sift_10",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_sift", "emb2_dim": 128,
        "kind": "4way",
    },
    "partsupp_deep_wiki_10": {
        "table": "partsupp_deep_wiki_10",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_wiki", "emb2_dim": 768,
        "kind": "4way",
    },
    "partsupp_deep_sift_1": {
        "table": "partsupp_deep_sift_1",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_sift", "emb2_dim": 128,
        "kind": "4way",
    },
    "partsupp_deep_wiki_1": {
        "table": "partsupp_deep_wiki_1",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_wiki", "emb2_dim": 768,
        "kind": "4way",
    },
}

CELL_JOIN = {
    "multi_join_deep_wiki": {
        "partsupp_table": "partsupp_deep_10",
        "part_table": "part_wiki_10",
        "partsupp_emb_col": "ps_embedding", "partsupp_emb_dim": 96,
        "part_emb_col": "p_embedding", "part_emb_dim": 768,
        "kind": "join",
    },
    "multi_join_deep_wiki_1": {
        "partsupp_table": "partsupp_deep_1",
        "part_table": "part_wiki_1",
        "partsupp_emb_col": "ps_embedding", "partsupp_emb_dim": 96,
        "part_emb_col": "p_embedding", "part_emb_dim": 768,
        "kind": "join",
    },
}
ALL_CELLS = list(CELL_4WAY.keys()) + list(CELL_JOIN.keys())


# ---------------------------------------------------------------------------
# AdaptiveState — 단일 run_adaptive_sampling.py 의 AdaptiveState 정확 복제
#   Exqutor §V-B 식 1~6 + Section VI hyperparam (변경 X).
#   Per-table state 운영은 cell × seed × table_idx 단위로 *2개 인스턴스* 생성.
# ---------------------------------------------------------------------------

@dataclass
class AdaptiveState:
    """단일 run_adaptive_sampling.py 의 AdaptiveState 와 동일 (식 1~6).

    Per-table separate state (Exqutor §V-B 의 multi-table 운영 원칙) 구현 시
    table1 / table2 각각 1 instance 생성. 같은 cell × seed 안에서 update_period
    timing (50 query) 은 두 인스턴스가 공유 — query iteration 한 step 에서
    table1.step(qe1) + table2.step(qe2) 동시 호출.
    """

    sample_size: float = float(SAMPLE_SIZE)
    velocity: float = 0.0
    learning_rate: float = 0.1
    momentum: float = 0.9
    alpha: float = 50.0
    beta: float = 1.5
    gamma: float = 0.99
    update_period: int = 50
    min_size: int = 50
    max_size: int = 5000
    n_total: int = 0
    qerror_window: list = field(default_factory=list)

    def step(self, qerror) -> int:
        """매 query 마다 호출. update_period 마다 sample_size 갱신.

        식 1~6 정확 그대로 (단일 run_adaptive_sampling.py 와 line-by-line 일치).
        """
        self.n_total += 1
        if qerror is not None and np.isfinite(qerror):
            self.qerror_window.append(float(qerror))

        if self.n_total % self.update_period == 0 and self.qerror_window:
            mean_qe = float(np.mean(self.qerror_window))
            sampling_ratio = self.sample_size / max(self.max_size, 1)
            # 식 3
            delta = self.alpha * (mean_qe - self.beta) \
                - (100.0 - self.alpha) * sampling_ratio
            # 식 4
            self.velocity = self.momentum * self.velocity \
                + self.learning_rate * delta
            # 식 5
            self.sample_size = self.sample_size + self.velocity
            self.sample_size = float(
                np.clip(self.sample_size, self.min_size, self.max_size)
            )
            # 식 6
            self.learning_rate = self.gamma * self.learning_rate
            self.qerror_window.clear()
        return int(round(self.sample_size))


# ---------------------------------------------------------------------------
# Adaptive Bernoulli estimator — single-table (단일 run_adaptive_sampling.py 와 동일)
# ---------------------------------------------------------------------------

def adaptive_bernoulli_estimate_single(
    all_vecs: np.ndarray,
    qvec: np.ndarray,
    D: float,
    sample_size: int,
    rng: np.random.Generator,
) -> tuple[float, int, int]:
    """단일 vector view 에서 sample_size 만큼 random sample → hit-count 외삽.

    Returns:
        est:    HT 외삽 카디널리티 = hits * (n / s)
        hits:   sample 안에서 d < D 인 row 수
        s_used: 실제 사용 sample size (n 으로 clip)
    """
    n = all_vecs.shape[0]
    s = max(1, min(int(sample_size), n))
    idxs = rng.choice(n, size=s, replace=False)
    sub = all_vecs[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return float(hits) * (n / s), hits, s


# ---------------------------------------------------------------------------
# Multi-cell Adaptive measurement — per-table separate state (§V-B)
# ---------------------------------------------------------------------------

def _seed_int(seed: float) -> int:
    """단일 run_adaptive_sampling.py 와 동일 seed → int 변환."""
    return int(seed * 10**9) % (2**31 - 1)


def _make_state(state_kwargs: dict, max_size_clip: int) -> AdaptiveState:
    kw = dict(state_kwargs)
    kw["max_size"] = min(int(kw.get("max_size", 5000)), int(max_size_clip))
    return AdaptiveState(**kw)


def measure_multi_adaptive(
    *,
    cell_name: str,
    table_label: str,
    table_kind: str,
    vec1: np.ndarray,
    vec2: np.ndarray,
    qids: np.ndarray,
    q1: np.ndarray,
    q2: np.ndarray,
    D1_by_sel: dict,
    D2_by_sel: dict,
    true_card: dict,
    selectivities: list,
    seeds: list,
    n_queries: int,
    state_kwargs: dict,
) -> tuple[list[dict], dict]:
    """Per-table separate-state Adaptive Sampling on multi cell (4way or join).

    Args:
        cell_name:    측정 cell 식별자 (e.g. partsupp_deep_sift_10).
        table_label:  parquet 의 table / table_pair 컬럼 값.
        table_kind:   "4way" 또는 "join" — output schema 의 D 컬럼명을 결정.
        vec1, vec2:   per-row aligned 두 vector view (multi-vector emb1/emb2 또는
                      join broadcast 후 deep_join/wiki_join).
        qids:         query 의 row index (paired alignment 키).
        q1, q2:       query vector pair (n_queries × dim_i).
        D1_by_sel, D2_by_sel: sel → (n_queries,) target distance.
        true_card:    {(qid, sel): joint AND 카운트}.
        selectivities, seeds, n_queries: 측정 격자.
        state_kwargs: AdaptiveState 의 hyperparam (min_size / max_size 포함).

    Returns:
        rows:    list[dict] (parquet row, schema = 4way / join 에 따라 다름)
        summary: 진단 정보 (final / mean sample_size, per (sel, seed))
    """
    n_total = vec1.shape[0]
    method = "adaptive_sampling"
    rows: list[dict] = []
    final_sizes_per_seed: dict = {}

    for sel in selectivities:
        if sel not in D1_by_sel or sel not in D2_by_sel:
            print(f"[{kst()}]   WARNING: sel={sel} 에 D1/D2 없음 (skip)")
            continue
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        # paired alignment — qids 순서를 매 sel/seed 마다 동일하게 유지
        # (build_query_pool 에서 이미 random.choice 결정적 — seed 1234 고정).

        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            # Per-table separate state — 두 인스턴스 (Exqutor §V-B)
            state1 = _make_state(state_kwargs, n_total)
            state2 = _make_state(state_kwargs, n_total)
            # 첫 query 의 sample_size = 식 1 의 N=385 (양 table 동일)
            s1_next = SAMPLE_SIZE
            s2_next = SAMPLE_SIZE

            t0 = time.time()
            qe_list = []
            size1_trace = []
            size2_trace = []

            for i, qid in enumerate(qids):
                qid_int = int(qid)
                D1 = float(D1_vec[i])
                D2 = float(D2_vec[i])
                tc = int(true_card[(qid_int, sel)])

                # Per-table independent random samples — Exqutor multi-table 외삽
                # 표본은 두 view 의 row-index 공간에서 독립 추출. joint 추정은
                # 두 marginal hit-rate 의 곱 × N (조건 독립 가정, 본 논문이 multi-
                # table 에서 채택하는 외삽 — single-table 식 1 의 직접 확장).
                _, hits1, s1_used = adaptive_bernoulli_estimate_single(
                    vec1, q1[i], D1, s1_next, rng,
                )
                _, hits2, s2_used = adaptive_bernoulli_estimate_single(
                    vec2, q2[i], D2, s2_next, rng,
                )
                p1 = hits1 / max(s1_used, 1)
                p2 = hits2 / max(s2_used, 1)
                # joint estimate via marginal 독립 가정
                est = float(p1 * p2 * n_total)

                # joint q_error (paired alignment 기준 = 4강 / paradigm 과 동일)
                if est > 0 and tc > 0:
                    qerr_joint = max(est / tc, tc / est)
                else:
                    qerr_joint = None

                # per-table marginal q_error (state update 용)
                # marginal true card 가 없으므로 joint q_error 를 두 state 에 동일
                # 적용 — Exqutor 의 multi-table 운영 시 per-table feedback 이
                # 어차피 joint planning loss 로 driving 된다는 본 논문 설명과 부합.
                qe_for_state = qerr_joint

                row = {
                    "dataset": cell_name,
                    "mode": method,
                    "selectivity": sel,
                    "seed": seed,
                    "query_id": qid_int,
                    "true_card": tc,
                    "est": est,
                    "q_error": qerr_joint,
                    "sample_size_used_t1": int(s1_used),
                    "sample_size_used_t2": int(s2_used),
                }
                if table_kind == "4way":
                    row["table"] = table_label
                    row["D1_target"] = D1
                    row["D2_target"] = D2
                else:  # join
                    row["table_pair"] = table_label
                    row["D_deep_target"] = D1
                    row["D_wiki_target"] = D2
                rows.append(row)
                qe_list.append(qerr_joint if qerr_joint is not None
                               else float("nan"))
                size1_trace.append(s1_used)
                size2_trace.append(s2_used)

                # 다음 query sample_size 갱신 (per-table state.step)
                s1_next = state1.step(qe_for_state)
                s2_next = state2.step(qe_for_state)

            elapsed = time.time() - t0
            valid = sum(1 for q in qe_list if q == q)
            med = float(np.nanmedian(qe_list)) if valid else float("nan")
            mean_s1 = float(np.mean(size1_trace)) if size1_trace else float("nan")
            mean_s2 = float(np.mean(size2_trace)) if size2_trace else float("nan")
            final_sizes_per_seed[(sel, seed)] = {
                "final_size_t1": int(round(state1.sample_size)),
                "final_size_t2": int(round(state2.sample_size)),
                "mean_size_t1": mean_s1,
                "mean_size_t2": mean_s2,
                "final_velocity_t1": state1.velocity,
                "final_velocity_t2": state2.velocity,
                "final_lr_t1": state1.learning_rate,
                "final_lr_t2": state2.learning_rate,
            }
            print(
                f"[{kst()}]     {cell_name} {method} sel={sel:.2f} seed={seed} "
                f"({elapsed*1000:.0f}ms) valid={valid}/{len(qids)} "
                f"med_qe={med:.4f} mean_s1={mean_s1:.0f} mean_s2={mean_s2:.0f}"
            )

    summary = {
        "n_rows": len(rows),
        "n_total_in_cell": int(n_total),
        "final_sizes_per_seed": {
            f"sel={k[0]}_seed={k[1]}": v
            for k, v in final_sizes_per_seed.items()
        },
    }
    return rows, summary


# ---------------------------------------------------------------------------
# Lazy server-side imports — measure_multi_paradigm 과 동일 패턴
# ---------------------------------------------------------------------------

def _lazy_imports():
    """server 전용 PG / build / fetch helper import.

    로컬 dry-run 에서는 호출하지 않음. 반환:
      helpers: dict (fetch / build_query_pool 등)
    """
    from measure_multi_vector import (  # noqa: E402
        fetch_dual_vectors,
        build_query_pool as build_query_pool_4way,
    )
    from measure_multi_table_join import (  # noqa: E402
        fetch_partsupp, fetch_part, build_join,
        build_query_pool as build_query_pool_join,
    )
    return {
        "fetch_dual_vectors": fetch_dual_vectors,
        "build_query_pool_4way": build_query_pool_4way,
        "fetch_partsupp": fetch_partsupp,
        "fetch_part": fetch_part,
        "build_join": build_join,
        "build_query_pool_join": build_query_pool_join,
    }


# ---------------------------------------------------------------------------
# Cell-level dispatch
# ---------------------------------------------------------------------------

def run_cell_4way(
    cell_name: str, helpers: dict,
    n_queries: int, selectivities: list, seeds: list,
    state_kwargs: dict,
) -> tuple[list[dict], dict]:
    cfg = CELL_4WAY[cell_name]
    print(f"[{kst()}] === adaptive 4way: cell={cell_name} ({cfg['table']}) ===")

    emb1, emb2 = helpers["fetch_dual_vectors"](
        cfg["table"], cfg["emb1_col"], cfg["emb2_col"],
        cfg["emb1_dim"], cfg["emb2_dim"],
    )
    print(f"[{kst()}]   N={emb1.shape[0]:,} dims=({emb1.shape[1]}, {emb2.shape[1]})")

    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = helpers["build_query_pool_4way"](
        emb1, emb2, n_queries=n_queries,
    )

    rows, summary = measure_multi_adaptive(
        cell_name=cell_name,
        table_label=cfg["table"],
        table_kind="4way",
        vec1=emb1, vec2=emb2,
        qids=qids, q1=q1, q2=q2,
        D1_by_sel=D1_by_sel, D2_by_sel=D2_by_sel, true_card=true_card,
        selectivities=selectivities, seeds=seeds, n_queries=n_queries,
        state_kwargs=state_kwargs,
    )
    return rows, summary


def run_cell_join(
    cell_name: str, helpers: dict,
    n_queries: int, selectivities: list, seeds: list,
    state_kwargs: dict,
) -> tuple[list[dict], dict]:
    cfg = CELL_JOIN[cell_name]
    print(f"[{kst()}] === adaptive join: cell={cell_name} "
          f"({cfg['partsupp_table']} ⨝ {cfg['part_table']}) ===")

    ps_emb, ps_keys = helpers["fetch_partsupp"](
        cfg["partsupp_table"], cfg["partsupp_emb_col"], cfg["partsupp_emb_dim"],
    )
    p_emb, p_keys = helpers["fetch_part"](
        cfg["part_table"], cfg["part_emb_col"], cfg["part_emb_dim"],
    )
    deep_join, wiki_join = helpers["build_join"](ps_emb, ps_keys, p_emb, p_keys)
    print(f"[{kst()}]   join: deep {deep_join.shape}, wiki {wiki_join.shape}")
    # FK broadcast 이후 ps_emb 와 deep_join 은 동일 ndarray (참조). p_emb 만 free.
    del p_emb, p_keys, ps_keys

    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = helpers["build_query_pool_join"](
        deep_join, wiki_join, n_queries=n_queries,
    )

    table_label = f"{cfg['partsupp_table']}__{cfg['part_table']}"
    rows, summary = measure_multi_adaptive(
        cell_name=cell_name,
        table_label=table_label,
        table_kind="join",
        vec1=deep_join, vec2=wiki_join,
        qids=qids, q1=q1, q2=q2,
        D1_by_sel=D1_by_sel, D2_by_sel=D2_by_sel, true_card=true_card,
        selectivities=selectivities, seeds=seeds, n_queries=n_queries,
        state_kwargs=state_kwargs,
    )
    return rows, summary


# ---------------------------------------------------------------------------
# Output saving (measure_multi_paradigm 과 동일 schema 컨벤션, csv)
# ---------------------------------------------------------------------------

def _save_outputs(
    rows: list[dict], *,
    out_csv: Path, out_meta: Path, extra_meta: dict,
) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"[{kst()}] saved {out_csv} ({len(df):,} rows)")

    if not df.empty:
        smry = (df.groupby(["dataset", "mode", "selectivity"])["q_error"]
                  .agg(["mean", "std", "median", "count"]).round(4))
        print(f"\n=== q_error summary (cell × mode × sel) ===\n{smry}\n")

    meta = {
        "kst": kst(),
        "n_rows": len(df),
        "modes": sorted(df["mode"].unique().tolist()) if not df.empty else [],
        "datasets": sorted(df["dataset"].unique().tolist()) if not df.empty else [],
    }
    meta.update(extra_meta)
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--cells", nargs="+", required=True, choices=ALL_CELLS,
                    help="측정할 multi cell (3종 — 4way 2 + join 1)")
    ap.add_argument("--out-dir", default=None,
                    help="csv/meta 출력 dir (default: server CACHE/multi_adaptive 또는 "
                         "로컬 _internal/cache/rq3/multi_adaptive)")
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    ap.add_argument("--selectivity", nargs="*", type=float, default=SELECTIVITIES,
                    help=f"selectivity grid (default {SELECTIVITIES}).")
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--num-seeds", type=int, default=len(SEEDS))
    # AdaptiveState hyperparam (단일 run_adaptive_sampling.py 와 동일 default — Section VI)
    ap.add_argument("--momentum", type=float, default=0.9)
    ap.add_argument("--lr0", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=50.0)
    ap.add_argument("--beta", type=float, default=1.5)
    ap.add_argument("--gamma", type=float, default=0.99)
    ap.add_argument("--update-period", type=int, default=50)
    ap.add_argument("--min-size", type=int, default=50)
    ap.add_argument("--max-size", type=int, default=5000)
    ap.add_argument("--dry-run", action="store_true",
                    help="DB 접속/측정 X — CLI / config 검증만")
    args = ap.parse_args()

    end = args.seed_start + args.num_seeds
    seeds = SEEDS[args.seed_start:end]
    if not seeds:
        raise SystemExit(
            f"--seed-start={args.seed_start} --num-seeds={args.num_seeds} → "
            f"빈 seed list. SEEDS={SEEDS}")

    state_kwargs = {
        "momentum": args.momentum,
        "learning_rate": args.lr0,
        "alpha": args.alpha,
        "beta": args.beta,
        "gamma": args.gamma,
        "update_period": args.update_period,
        "min_size": args.min_size,
        "max_size": args.max_size,
    }

    print(f"[{kst()}] === measure_multi_adaptive_sampling — "
          f"Exqutor §V-B per-table separate state ===")
    print(f"[{kst()}] cells:        {args.cells}")
    print(f"[{kst()}] selectivity:  {args.selectivity}")
    print(f"[{kst()}] seeds:        {seeds}")
    print(f"[{kst()}] n_queries:    {args.n_queries}")
    print(f"[{kst()}] hyperparam:   m={args.momentum}, η₀={args.lr0}, "
          f"α={args.alpha}, β={args.beta}, γ={args.gamma}, "
          f"period={args.update_period}, init_N={SAMPLE_SIZE}")

    if args.dry_run:
        print(f"\n[{kst()}] === dry-run: validating cells + state config ===")
        for c in args.cells:
            kind = "4way" if c in CELL_4WAY else "join"
            print(f"  {c:>26}  kind={kind}")
        n_meas = (len(args.cells) * len(args.selectivity) * len(seeds)
                  * args.n_queries)
        print(f"\n[estimate] {len(args.cells)} cell × "
              f"{len(args.selectivity)} sel × {len(seeds)} seed × "
              f"{args.n_queries} q = {n_meas:,} measurement")
        print(f"[{kst()}] === dry-run OK ===")
        return

    helpers = _lazy_imports()

    # output dir
    if args.out_dir:
        out_dir = Path(args.out_dir)
    elif ROOT_SERVER.exists():
        out_dir = ROOT_SERVER / "multi_adaptive"
    else:
        out_dir = SCRIPTS_PATH.parent / "cache" / "rq3" / "multi_adaptive"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{kst()}] out_dir: {out_dir}")

    t_total = time.time()
    for cell in args.cells:
        out_csv = out_dir / f"multi_adaptive_{cell}.csv"
        out_meta = out_dir / f"multi_adaptive_{cell}_meta.json"
        if out_csv.exists():
            print(f"[{kst()}] SKIP — {out_csv.name} already exists")
            continue

        t_cell = time.time()
        print(f"\n[{kst()}] ###### CELL {cell} ######")
        if cell in CELL_4WAY:
            rows, summary = run_cell_4way(
                cell, helpers, args.n_queries,
                list(args.selectivity), seeds, state_kwargs,
            )
            kind = "4way"
        else:
            rows, summary = run_cell_join(
                cell, helpers, args.n_queries,
                list(args.selectivity), seeds, state_kwargs,
            )
            kind = "join"

        cell_meta = {
            "method": "Exqutor Adaptive Sampling (arXiv:2512.09695v2 §V-B, "
                      "per-table separate state, multi-table)",
            "cell": cell,
            "kind": kind,
            "hyperparameters": {
                "m": args.momentum, "eta0": args.lr0,
                "alpha": args.alpha, "beta": args.beta,
                "gamma": args.gamma, "update_period": args.update_period,
                "init_N": SAMPLE_SIZE,
                "min_size": args.min_size, "max_size": args.max_size,
            },
            "n_queries": args.n_queries,
            "selectivities": list(args.selectivity),
            "seeds": list(seeds),
            "joint_estimator": "marginal independence: est = (h1/s1) * (h2/s2) * N",
            "schema_note": "4way → table/D1_target/D2_target ; "
                           "join → table_pair/D_deep_target/D_wiki_target",
            "elapsed_s": round(time.time() - t_cell, 1),
            "summary": summary,
        }
        _save_outputs(rows, out_csv=out_csv, out_meta=out_meta,
                      extra_meta=cell_meta)
        print(f"[{kst()}] cell {cell} done in {cell_meta['elapsed_s']}s")

    print(f"\n[{kst()}] === all done in {time.time() - t_total:.1f}s ===")


if __name__ == "__main__":
    main()
