#!/usr/bin/env python3
"""
RQ3 — Exqutor Adaptive Sampling baseline (arXiv:2512.09695v2 Section V-B 구현).

5/8 회의 결정 ⭐⭐⭐: Exqutor 본 논문의 momentum 기반 동적 sample size 알고리즘을
본 연구의 stratification 4강 (HDBSCAN / MB_partial / Hilbert / sparse RP) 와 paired
비교. 동일 query_id × seed × selectivity 격자를 사용해 inner-join Δ% 산출 가능.

Exqutor Adaptive Sampling 식 (본 논문 Section V-B):
    식 1 — N = ⌈z² · P̂ · (1 − P̂) / e²⌉ = 385 (z=1.96, P̂=0.5, e=0.05)
    식 2 — Q-error = max(est/true, true/est)
    식 3 — δ_t = α·(Q-error_t − β) − (100 − α)·sampling_ratio_t
    식 4 — V_t = m·V_{t−1} + η_t·δ_t
    식 5 — sample_size_{t+1} = sample_size_t + V_t
    식 6 — η_{t+1} = γ·η_t

Hyperparameter (본 논문 Section VI):
    m = 0.9, η₀ = 0.1, α = 50, β = 1.5, γ = 0.99, update_period = 50

호출 흐름 (chain_unified.py 패턴):
    1. CELLS[(args.dataset, args.sf)] lookup → cell config 조립
    2. _measure_common.DATASETS = [DS] monkey-patch (cell 별 정확 inject)
    3. fetch_all_vectors_safe(DS) — 전체 vector in-memory 회수 (PG → numpy)
    4. AdaptiveState (per cell × seed) — 매 50 query 마다 sample_size 갱신
    5. 매 query: random sample s_t rows → Bernoulli HT 외삽

산출 row schema (_measure_common 호환 + 추가 컬럼):
    {dataset, mode, selectivity, seed, query_id, D_target, true_card, est, q_error,
     sample_size_used}

CLI 예시:
    # 단일 cell 측정 (chain_unified 와 동일 인터페이스)
    python3 run_adaptive_sampling.py --dataset DEEP --sf 1
    python3 run_adaptive_sampling.py --dataset SIFT --sf 10 --num-queries 50

    # mode C (BERN baseline reference) — Adaptive off, sample_size=385 고정
    python3 run_adaptive_sampling.py --dataset DEEP --sf 1 --fixed-size 385

    # dry-run (1 measurement)
    python3 run_adaptive_sampling.py --dataset DEEP --sf 1 \\
        --num-queries 1 --num-seeds 1 --selectivity 0.10

서버 launch (cell loop 은 launcher script 가 담당):
    nohup python3 -u /mnt/hdd0/home/capstone2026/cache/rq3/run_adaptive_sampling.py \\
        --dataset DEEP --sf 1 \\
        > /mnt/hdd0/home/capstone2026/logs/adaptive_DEEP_sf1.log 2>&1 &
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import _measure_common as mc  # noqa: E402
from _measure_common import (  # noqa: E402
    SAMPLE_SIZE,
    SEEDS as DEFAULT_SEEDS,
    SELECTIVITIES as DEFAULT_SELECTIVITIES,
    fetch_all_vectors_safe,
    kst,
)

try:
    import pyarrow.parquet as pq
except ImportError:  # 로컬 dry-run import 시 OK
    pq = None


# ---------------------------------------------------------------------------
# CELLS — chain_unified.py 의 정확한 mirror (5/8 sprint 사용 cell 5종 × SF 2종)
# ---------------------------------------------------------------------------

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')

CELLS = {
    ('DEEP', 1):   {'table': 'partsupp_deep_1',   'embed_col': 'ps_embedding', 'dim': 96,  'pk_col': 'ps_partkey'},
    ('DEEP', 10):  {'table': 'partsupp_deep_10',  'embed_col': 'ps_embedding', 'dim': 96,  'pk_col': 'ps_partkey'},
    ('DEEP', 100): {'table': 'partsupp_deep_100', 'embed_col': 'ps_embedding', 'dim': 96,  'pk_col': 'ps_partkey'},
    ('SIFT', 1):   {'table': 'partsupp_sift_1',   'embed_col': 'ps_embedding', 'dim': 128, 'pk_col': 'ps_partkey'},
    ('SIFT', 10):  {'table': 'partsupp_sift_10',  'embed_col': 'ps_embedding', 'dim': 128, 'pk_col': 'ps_partkey'},
    ('SIFT', 100): {'table': 'partsupp_sift_100', 'embed_col': 'ps_embedding', 'dim': 128, 'pk_col': 'ps_partkey'},
    ('SSN',  1):   {'table': 'partsupp_fb_1',     'embed_col': 'ps_embedding', 'dim': 256, 'pk_col': 'ps_partkey'},
    ('SSN',  10):  {'table': 'partsupp_fb_10',    'embed_col': 'ps_embedding', 'dim': 256, 'pk_col': 'ps_partkey'},
    ('SSN',  100): {'table': 'partsupp_fb_100',   'embed_col': 'ps_embedding', 'dim': 256, 'pk_col': 'ps_partkey'},
    ('YFCC', 1):   {'table': 'partsupp_yfcc_1',   'embed_col': 'ps_embedding', 'dim': 192, 'pk_col': ('ps_partkey', 'ps_suppkey')},
    ('YFCC', 10):  {'table': 'partsupp_yfcc_10',  'embed_col': 'ps_embedding', 'dim': 192, 'pk_col': ('ps_partkey', 'ps_suppkey')},
    ('YFCC', 100): {'table': 'partsupp_yfcc_100', 'embed_col': 'ps_embedding', 'dim': 192, 'pk_col': ('ps_partkey', 'ps_suppkey')},
    ('WIKI', 1):   {'table': 'partsupp_wiki_1',   'embed_col': 'ps_embedding', 'dim': 768, 'pk_col': ('ps_partkey', 'ps_suppkey')},
    ('WIKI', 10):  {'table': 'partsupp_wiki_10',  'embed_col': 'ps_embedding', 'dim': 768, 'pk_col': ('ps_partkey', 'ps_suppkey')},
    ('WIKI', 100): {'table': 'partsupp_wiki_100', 'embed_col': 'ps_embedding', 'dim': 768, 'pk_col': ('ps_partkey', 'ps_suppkey')},
}


def cell_name(dataset: str, sf: int) -> str:
    """chain_unified 의 query_pool/query_sel 명명 규칙 정확 mirror."""
    return f'{dataset}_sf{sf}'


def build_dataset_entry(dataset: str, sf: int) -> dict:
    """chain_unified.main() 의 DS 조립 로직 정확 mirror (query_pool/query_sel 경로 포함)."""
    key = (dataset, sf)
    if key not in CELLS:
        raise SystemExit(f'unsupported cell: {key}')
    cfg = CELLS[key]
    name = cell_name(dataset, sf)
    return {
        'name': name,
        'table': cfg['table'],
        'embed_col': cfg['embed_col'],
        'vec_dim': cfg['dim'],
        'pk_col': cfg['pk_col'],
        'sf': sf,
        'query_pool': CACHE / f'query_pool_{name}.parquet',
        'query_sel': CACHE / f'query_selectivity_{name}.parquet',
    }


# ---------------------------------------------------------------------------
# Adaptive Sampling state — 식 3~6 구현 (Agent B 원본 그대로 유지)
# ---------------------------------------------------------------------------

@dataclass
class AdaptiveState:
    """Exqutor Adaptive Sampling state (per cell, per seed).

    본 논문 Section V-B 의 implementation 노트 ("the optimizer maintains separate
    sample size states for each table") 에 따라 cell × seed 단위로 독립 state.
    seed 단위 분리는 본 연구의 paired alignment (cell × seed × query_id) 를
    위해 추가된 차원으로, 같은 cell 안에서는 모든 seed 가 동일 갱신 trajectory
    를 갖도록 query 순서를 (sel × query_id) 로 통일.

    Args:
        sample_size: 식 1 의 N=385 (initial). float 으로 유지하다 query 직전 int 변환.
        velocity: 식 4 의 V_t (모멘텀).
        learning_rate: 식 6 의 η_t (감쇠 변수).
        momentum: 식 4 의 m (Sutskever et al. 2013, 0.9).
        alpha: 식 3 의 α (Q-error 항 가중치, 50).
        beta: 식 3 의 β (target Q-error, 1.5).
        gamma: 식 6 의 η decay (0.99).
        update_period: sample_size 갱신 주기 (50 query).
        min_size / max_size: 발산 방지 안전 clip (논문 명시 X — 운영상 추가).
        n_total: 누적 query count (update period trigger 용).
        qerror_window: 최근 update_period 의 q_error.
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

        Args:
            qerror: 직전 query 의 Q-error (None / non-finite 면 window 에서 제외).

        Returns:
            다음 query 에서 사용할 sample_size (int, clip 적용).
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
            # window reset (다음 50 query 평가 준비)
            self.qerror_window.clear()
        return int(round(self.sample_size))


# ---------------------------------------------------------------------------
# Bernoulli estimator — Adaptive 의 매 query random sample → HT 외삽
# (본 논문 "no-index → full-scan 일부 sampling" 의 in-memory simulation)
# ---------------------------------------------------------------------------

def adaptive_bernoulli_estimate(
    all_vecs: np.ndarray,
    qvec: np.ndarray,
    D: float,
    sample_size: int,
    rng: np.random.Generator,
) -> float:
    """all_vecs 에서 sample_size 만큼 무작위 추출 → 거리 계산 → HT 외삽.

    매 query 마다 새로 sample (replacement X). 본 논문의 single-shot 추정
    (planning stage 호출당 1회 carl. estimation) 정확 재현.
    """
    n = all_vecs.shape[0]
    s = max(1, min(int(sample_size), n))
    idxs = rng.choice(n, size=s, replace=False)
    sub = all_vecs[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return float(hits) * (n / s)


# ---------------------------------------------------------------------------
# Main 측정 loop — _measure_common.run_method_measurement 호환 row schema
# ---------------------------------------------------------------------------

def run_adaptive_measurement(
    all_vecs: np.ndarray,
    ds: dict,
    *,
    selectivities: list,
    seeds: list,
    n_queries: int = 100,
    fixed_size: int | None = None,
    state_kwargs: dict | None = None,
) -> tuple[list[dict], dict]:
    """단일 cell (dataset) Adaptive Sampling 측정.

    Args:
        all_vecs: fetch_all_vectors_safe 로 회수한 (N, dim) float32.
        ds: DATASETS 항목 (name / query_pool / query_sel 등 포함).
        selectivities / seeds: 측정 격자 — 기존 RQ3 framework 와 동일 default.
        n_queries: cell × sel 당 query 수 (default 100).
        fixed_size: None 이면 Adaptive ON, 정수면 sample_size 고정 (Adaptive OFF).
            fixed_size=385 → 본 연구의 BERN baseline 정확 재현 (sanity check).
        state_kwargs: AdaptiveState 의 기본 hyperparameter override (옵션).

    Returns:
        (rows, summary) — rows: list[dict] (parquet 행), summary: 진단 정보.
    """
    if pq is None:
        raise RuntimeError("pyarrow not available — cannot read query_pool parquet")

    qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
    qs_full = pq.read_table(ds["query_sel"]).to_pandas()
    qvecs = np.stack([
        np.asarray(qp.iloc[i]["embedding"], dtype=np.float32)
        for i in range(len(qp))
    ])
    print(f"[{kst()}]   loaded {len(qp)} queries (dim={qvecs.shape[1]})")

    n_total = all_vecs.shape[0]
    method = "adaptive_fixed" if fixed_size is not None else "adaptive_sampling"
    rows: list[dict] = []

    # cell 진단용 — 마지막 sample_size trajectory 보존
    final_sizes_per_seed: dict = {}

    base_kwargs = {
        # 본 논문 Section VI 기본값. fixed_size 모드에서도 instantiate 는 하지만
        # step() 미호출 → 의미 없음.
        "momentum": 0.9,
        "learning_rate": 0.1,
        "alpha": 50.0,
        "beta": 1.5,
        "gamma": 0.99,
        "update_period": 50,
        "min_size": 50,
        # max_size: 데이터 row 보다 작게 (안전 clip).
        "max_size": min(5000, n_total),
    }
    if state_kwargs:
        base_kwargs.update(state_kwargs)

    for sel in selectivities:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel)) &
            (qs_full["query_id"] < n_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if len(qs_sel) == 0:
            print(f"[{kst()}]   WARNING: sel={sel} 에 해당 query 없음 (skip)")
            continue

        for seed in seeds:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            rng = np.random.default_rng(seed_int)
            state = AdaptiveState(**base_kwargs)
            sample_size = SAMPLE_SIZE  # 첫 query 는 식 1 의 N=385

            t0 = time.time()
            qe_list = []
            size_trace = []

            for _, row in qs_sel.iterrows():
                qid = int(row["query_id"])
                D = float(row["D_target"])
                true_card = int(row["true_cardinality"])
                qvec = qvecs[qid]

                if fixed_size is not None:
                    s_used = int(fixed_size)
                else:
                    s_used = sample_size

                est = adaptive_bernoulli_estimate(all_vecs, qvec, D, s_used, rng)
                if est > 0 and true_card > 0:
                    qerr = max(est / true_card, true_card / est)
                else:
                    qerr = None

                rows.append({
                    "dataset": ds["name"],
                    "mode": method,
                    "selectivity": sel,
                    "seed": seed,
                    "query_id": qid,
                    "D_target": D,
                    "true_card": true_card,
                    "est": est,
                    "q_error": qerr,
                    "sample_size_used": s_used,
                })
                qe_list.append(qerr if qerr is not None else float("nan"))
                size_trace.append(s_used)

                if fixed_size is None:
                    sample_size = state.step(qerr)

            elapsed = time.time() - t0
            valid = sum(1 for q in qe_list if q == q)
            med = float(np.nanmedian(qe_list)) if valid else float("nan")
            mean_size = float(np.mean(size_trace)) if size_trace else float("nan")
            final_sizes_per_seed[(sel, seed)] = {
                "final_sample_size": int(round(state.sample_size))
                if fixed_size is None else int(fixed_size),
                "mean_sample_size": mean_size,
                "final_velocity": state.velocity,
                "final_learning_rate": state.learning_rate,
            }
            print(
                f"[{kst()}]   {ds['name']} {method:>20} s={sel:.2f} seed={seed} "
                f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} "
                f"med_qe={med:.4f} mean_size={mean_size:.1f}"
            )

    summary = {
        "n_rows": len(rows),
        "fixed_size": fixed_size,
        "n_total_rows_in_table": n_total,
        "final_sizes_per_seed": {
            f"sel={k[0]}_seed={k[1]}": v for k, v in final_sizes_per_seed.items()
        },
    }
    return rows, summary


# ---------------------------------------------------------------------------
# Output saving
# ---------------------------------------------------------------------------

def _save_outputs(
    rows: list[dict],
    *,
    out_path: Path,
    meta_path: Path,
    extra_meta: dict,
) -> None:
    """parquet + meta json 저장 (out_path 의 디렉토리는 미리 생성)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_parquet(out_path, index=False)
    print(f"[{kst()}] saved {out_path} ({len(df):,} rows)")

    if not df.empty:
        smry = df.groupby(["dataset", "mode", "selectivity"])["q_error"].agg(
            ["mean", "std", "median", "count"]
        ).round(4)
        print(f"\n=== mean q_error per (dataset × mode × sel) ===\n{smry}")

    meta = {
        "kst": kst(),
        "n_rows": len(df),
        "modes": sorted(df["mode"].unique().tolist()) if not df.empty else [],
        "datasets": sorted(df["dataset"].unique().tolist()) if not df.empty else [],
    }
    meta.update(extra_meta)
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {meta_path}")


# ---------------------------------------------------------------------------
# CLI entrypoint — chain_unified.py 와 동일 인터페이스 (single cell args)
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="RQ3 Exqutor Adaptive Sampling baseline (arXiv:2512.09695v2 §V-B)"
    )
    # chain_unified 와 동일 single-cell args (multi-cell 은 launcher 가 loop)
    ap.add_argument("--dataset", required=True,
                    choices=['DEEP', 'SIFT', 'SSN', 'YFCC', 'WIKI', 'YFCC_DL'],
                    help="Dataset name (single cell).")
    ap.add_argument("--sf", type=int, required=True, choices=[1, 10, 100],
                    help="Scale factor (single cell).")
    ap.add_argument("--port", type=int, default=55435,
                    help="PostgreSQL port (default 55435 = vanilla).")
    ap.add_argument("--selectivity", nargs="*", type=float,
                    default=DEFAULT_SELECTIVITIES,
                    help=f"Selectivity grid (default {DEFAULT_SELECTIVITIES}).")
    ap.add_argument("--seed-start", type=int, default=0,
                    help="seed index 시작 (default 0).")
    ap.add_argument("--num-seeds", type=int, default=len(DEFAULT_SEEDS),
                    help=f"seed 갯수 (default {len(DEFAULT_SEEDS)}).")
    ap.add_argument("--num-queries", type=int, default=100,
                    help="cell × sel 당 query 수 (default 100).")
    ap.add_argument("--fixed-size", type=int, default=None,
                    help="정수 부여 시 Adaptive OFF, sample_size 고정 (예: 385). "
                         "본 연구 BERN baseline 재현 / sanity check 용.")
    ap.add_argument("--out-dir", type=Path, default=CACHE,
                    help="parquet + meta 저장 디렉토리 "
                         "(default /mnt/hdd0/home/capstone2026/cache/rq1, "
                         "기존 4강 measurement 와 동일 경로).")
    ap.add_argument("--out-prefix", default=None,
                    help="parquet basename 명시. 미지정 시 "
                         "rq3_<DATASET>_sf<N>_adaptive 자동 생성 "
                         "(기존 4강 명명 일치).")

    # AdaptiveState hyperparameter override (디버그/sensitivity 용)
    ap.add_argument("--momentum", type=float, default=0.9)
    ap.add_argument("--lr0", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=50.0)
    ap.add_argument("--beta", type=float, default=1.5)
    ap.add_argument("--gamma", type=float, default=0.99)
    ap.add_argument("--update-period", type=int, default=50)
    ap.add_argument("--min-size", type=int, default=50)
    ap.add_argument("--max-size", type=int, default=5000)

    args = ap.parse_args()

    # seed 슬라이싱 — DEFAULT_SEEDS [0.1, 0.2, 0.3, 0.4, 0.5] 에서 [start:start+num]
    end = args.seed_start + args.num_seeds
    seeds = DEFAULT_SEEDS[args.seed_start:end]
    if not seeds:
        raise SystemExit(
            f"--seed-start={args.seed_start} --num-seeds={args.num_seeds} → "
            f"빈 seed list. DEFAULT_SEEDS 길이={len(DEFAULT_SEEDS)}")

    # === chain_unified.py 패턴: cell config 조립 + mc.DATASETS monkey-patch ===
    DS = build_dataset_entry(args.dataset, args.sf)
    mc.DATASETS = [DS]
    mc.PORT = args.port
    mc.SELECTIVITIES = list(args.selectivity)

    cell_label = f"{args.dataset}-SF{args.sf}"
    print(f"[{kst()}] === Exqutor Adaptive Sampling — "
          f"fixed_size={args.fixed_size} ===")
    print(f"[{kst()}] cell: {cell_label} ({DS['table']}, dim={DS['vec_dim']})")
    print(f"[{kst()}] query_pool: {DS['query_pool']}")
    print(f"[{kst()}] query_sel:  {DS['query_sel']}")
    print(f"[{kst()}] sel={args.selectivity}, seeds={seeds}, "
          f"n_queries={args.num_queries}")
    print(f"[{kst()}] hyperparam: m={args.momentum}, η₀={args.lr0}, "
          f"α={args.alpha}, β={args.beta}, γ={args.gamma}, "
          f"period={args.update_period}, init_N={SAMPLE_SIZE}")

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

    t_total = time.time()

    print(f"\n[{kst()}] === {cell_label} ({DS['table']}) ===")
    all_vecs, _ = fetch_all_vectors_safe(DS)

    rows, summary = run_adaptive_measurement(
        all_vecs, DS,
        selectivities=args.selectivity,
        seeds=seeds,
        n_queries=args.num_queries,
        fixed_size=args.fixed_size,
        state_kwargs=state_kwargs,
    )

    # output 명명 — 기존 4강 measurement 와 동일 패턴 (rq3_<DATASET>_sf<N>_<method>)
    if args.out_prefix:
        base = args.out_prefix
    else:
        mode_tag = f"adaptive_fixed{args.fixed_size}" if args.fixed_size is not None else "adaptive"
        base = f"rq3_{args.dataset}_sf{args.sf}_{mode_tag}"
    out_pq = args.out_dir / f"{base}.parquet"
    out_meta = args.out_dir / f"{base}_meta.json"

    cell_meta = {
        "method": ("Exqutor Adaptive Sampling (arXiv:2512.09695v2 §V-B)"
                   if args.fixed_size is None
                   else f"Fixed Bernoulli (size={args.fixed_size}, sanity)"),
        "hyperparameters": {
            "m": args.momentum, "eta0": args.lr0,
            "alpha": args.alpha, "beta": args.beta,
            "gamma": args.gamma, "update_period": args.update_period,
            "init_N": SAMPLE_SIZE,
            "min_size": args.min_size, "max_size": args.max_size,
        },
        "fixed_size": args.fixed_size,
        "n_queries": args.num_queries,
        "selectivities": list(args.selectivity),
        "seeds": list(seeds),
        "cell": cell_label,
        "table": DS["table"],
        "vec_dim": DS["vec_dim"],
        "elapsed_s": round(time.time() - t_total, 1),
        "summary": summary,
    }
    _save_outputs(rows, out_path=out_pq, meta_path=out_meta,
                  extra_meta=cell_meta)

    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
