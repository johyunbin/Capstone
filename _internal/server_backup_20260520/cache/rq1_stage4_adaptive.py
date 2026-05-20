"""
RQ1 Stage 4 — Adaptive Sampling 시뮬레이션 (Exqutor bitwise 동치 재구현)

입력:
  - cache/rq1/subset_1m.parquet
  - cache/rq1/query_pool.parquet
  - cache/rq1/query_selectivity.parquet

출력:
  - cache/rq1/adaptive_runs.parquet  (60 run, flat 스키마)
  - cache/rq1/stage4_meta.json

실험 축:
  - selectivities: [0.001, 0.01, 0.05, 0.10, 0.30, 0.50]
  - modes:         [bernoulli, block_system]   (D5: block ablation 포함)
  - seeds:         [0, 1, 2, 3, 4]             (D2: 5회 반복)
  total: 60 runs

각 run: 100 query 순차 실행 → q_errors 100개 + 최종 상태 + sample_size trajectory

파이프라인 문서: experiments/plans/RQ1_motivation_pipeline_20260414_162857.md §II.2 §IV.Stage4
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

# ---- Exqutor 파라미터 (소스 L442~455에서 추출, 본 재구현 불변) ----
ALPHA = 50.0
BETA = 1.5
MOMENTUM = 0.9
LR_LAMBDA = 0.99
LR_INIT = 0.1
SAMPLE_SIZE_INIT = 385.0
SAMPLE_UPDATE_CYCLE = 50
# -------------------------------------------------------------


def kst_now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now_iso()}] {msg}", flush=True)


def load_parquet_vectors(path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    table = pq.read_table(path)
    pks = np.asarray(table.column("ps_partkey").to_numpy(), dtype=np.int32)
    sks = np.asarray(table.column("ps_suppkey").to_numpy(), dtype=np.int32)
    emb_col = table.column("embedding").combine_chunks()
    flat = emb_col.flatten().to_numpy(zero_copy_only=False)
    n = len(pks)
    dim = len(flat) // n
    vecs = flat.reshape(n, dim).astype(np.float32, copy=False)
    return pks, sks, vecs


def compute_distance_matrix(subset: np.ndarray, queries: np.ndarray) -> np.ndarray:
    subset = subset.astype(np.float32, copy=False)
    queries = queries.astype(np.float32, copy=False)
    subset_sq = (subset * subset).sum(axis=1, dtype=np.float32)
    queries_sq = (queries * queries).sum(axis=1, dtype=np.float32)
    dots = subset @ queries.T
    d2 = subset_sq[:, None] + queries_sq[None, :] - 2.0 * dots
    np.maximum(d2, 0, out=d2)
    return np.sqrt(d2, dtype=np.float32)


def run_adaptive_session(
    dist_matrix: np.ndarray,
    D_per_query: np.ndarray,
    mode: str,
    seed: int,
    rows_per_block: int = 14,  # Stage 1 측정값 (13.8 반올림)
) -> dict:
    """
    Exqutor bitwise 동치 Adaptive Sampling 시뮬레이션.

    dist_matrix: (N, Q) 거리 행렬
    D_per_query: (Q,) query별 range threshold
    mode: "bernoulli" (행 단위) or "block_system" (블록 단위)
    seed: 결정론적 RNG seed
    """
    rng = np.random.default_rng(seed)
    N, Q = dist_matrix.shape

    sample_size = SAMPLE_SIZE_INIT
    lr = LR_INIT
    v_grad = 0.0
    q_errors = []
    sample_sizes = []  # 매 쿼리마다 기록 (trajectory)

    # 블록 샘플링용 precompute
    n_blocks = (N + rows_per_block - 1) // rows_per_block

    for i in range(Q):
        sample_ratio = sample_size / N  # fraction (0~1)

        # ---- 샘플링 ----
        if mode == "bernoulli":
            # 행 단위 Bernoulli
            mask = rng.random(N, dtype=np.float32) < sample_ratio
        elif mode == "block_system":
            # 블록 단위 선택 → 해당 블록 전체 포함
            block_pick = rng.random(n_blocks, dtype=np.float32) < sample_ratio
            mask = np.repeat(block_pick, rows_per_block)[:N]
        else:
            raise ValueError(f"unknown mode: {mode}")

        # ==== Exqutor bitwise 동치 핵심 ====
        d_i = dist_matrix[:, i]
        cnt = int((d_i[mask] < D_per_query[i]).sum())
        if cnt == 0:                           # L1228 clamp
            cnt = 1
        est = cnt * N / sample_size            # L1232: 분모 = 요청 sample_size
        true_card = int((d_i < D_per_query[i]).sum())  # instrument->ntuples 동치

        q_err = max(est / max(true_card, 1.0), max(true_card, 1.0) / est)
        q_errors.append(q_err)
        sample_sizes.append(sample_size)
        # ================================

        # Exqutor L655~661: 50-query cycle마다 momentum 업데이트
        if (i + 1) % SAMPLE_UPDATE_CYCLE == 0:
            med = float(np.median(q_errors[-SAMPLE_UPDATE_CYCLE:]))
            grad = ALPHA * (med - BETA) - (100.0 - ALPHA) * (sample_size / N)
            v_grad = MOMENTUM * v_grad + lr * grad
            lr *= LR_LAMBDA
            sample_size = max(sample_size + v_grad, 1.0)

    return {
        "q_errors": np.array(q_errors, dtype=np.float64),
        "sample_size_trajectory": np.array(sample_sizes, dtype=np.float64),
        "final_sample_size": float(sample_size),
        "final_lr": float(lr),
        "final_v_grad": float(v_grad),
        "mask_actual_mean": None,  # 필요 시 기록
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RQ1 Stage 4 — Adaptive Sampling 시뮬")
    parser.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    parser.add_argument("--selectivities", default="0.001,0.01,0.05,0.10,0.30,0.50")
    parser.add_argument("--modes", default="bernoulli,block_system")
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--rows-per-block", type=int, default=14)
    args = parser.parse_args()

    selectivities = [float(x) for x in args.selectivities.split(",")]
    modes = [x.strip() for x in args.modes.split(",")]
    seeds = [int(x) for x in args.seeds.split(",")]

    subset_path = os.path.join(args.in_dir, "subset_1m.parquet")
    query_path = os.path.join(args.in_dir, "query_pool.parquet")
    sel_path = os.path.join(args.in_dir, "query_selectivity.parquet")
    out_path = os.path.join(args.in_dir, "adaptive_runs.parquet")
    meta_path = os.path.join(args.in_dir, "stage4_meta.json")

    t0 = time.time()
    log(f"시작 — in={args.in_dir}")
    log(f"  selectivities={selectivities}")
    log(f"  modes={modes}")
    log(f"  seeds={seeds}")
    log(f"  총 run: {len(selectivities) * len(modes) * len(seeds)}")

    log("Stage 4.1 — parquet 로드 + 거리 행렬")
    _, _, subset_vecs = load_parquet_vectors(subset_path)
    q_pks, q_sks, query_vecs = load_parquet_vectors(query_path)
    sel_table = pq.read_table(sel_path)
    log(
        f"  subset: {subset_vecs.shape}, queries: {query_vecs.shape}, "
        f"selectivity_rows: {sel_table.num_rows}"
    )

    t1 = time.time()
    dist_matrix = compute_distance_matrix(subset_vecs, query_vecs)
    log(f"  거리 행렬 {dist_matrix.shape}, 소요 {time.time()-t1:.1f}s")

    # selectivity별로 D_per_query (100,) 배열 준비
    sel_df = sel_table.to_pandas()
    D_by_selectivity = {}
    for s in selectivities:
        sub = sel_df[np.isclose(sel_df["selectivity"], s)].sort_values("query_id")
        assert len(sub) == 100, f"s={s}에서 query 100개 기대, 실제 {len(sub)}"
        D_by_selectivity[s] = sub["D_target"].to_numpy(dtype=np.float64)

    log(f"Stage 4.2 — {len(selectivities) * len(modes) * len(seeds)} run 실행")
    t2 = time.time()
    records = []
    run_idx = 0
    total_runs = len(selectivities) * len(modes) * len(seeds)

    for s in selectivities:
        D = D_by_selectivity[s]
        for mode in modes:
            for seed in seeds:
                res = run_adaptive_session(
                    dist_matrix, D, mode, seed, rows_per_block=args.rows_per_block
                )
                records.append(
                    {
                        "selectivity": s,
                        "mode": mode,
                        "seed": seed,
                        "q_errors": res["q_errors"],
                        "sample_size_trajectory": res["sample_size_trajectory"],
                        "final_sample_size": res["final_sample_size"],
                        "final_lr": res["final_lr"],
                        "final_v_grad": res["final_v_grad"],
                        "median_q_error": float(np.median(res["q_errors"])),
                        "mean_q_error": float(np.mean(res["q_errors"])),
                        "p95_q_error": float(np.quantile(res["q_errors"], 0.95)),
                        "max_q_error": float(np.max(res["q_errors"])),
                    }
                )
                run_idx += 1
                if run_idx % 10 == 0:
                    log(f"  진행 {run_idx}/{total_runs}, 경과 {time.time()-t2:.1f}s")

    log(f"  전체 {total_runs} run 완료, 소요 {time.time()-t2:.1f}s")

    # parquet 저장 — q_errors와 trajectory는 FixedSizeList<float64>
    log("Stage 4.3 — parquet 저장")
    qe_flat = np.concatenate([r["q_errors"] for r in records])
    ss_flat = np.concatenate([r["sample_size_trajectory"] for r in records])
    table = pa.table(
        {
            "selectivity": pa.array([r["selectivity"] for r in records], type=pa.float64()),
            "mode": pa.array([r["mode"] for r in records]),
            "seed": pa.array([r["seed"] for r in records], type=pa.int32()),
            "q_errors": pa.FixedSizeListArray.from_arrays(
                pa.array(qe_flat, type=pa.float64()), 100
            ),
            "sample_size_trajectory": pa.FixedSizeListArray.from_arrays(
                pa.array(ss_flat, type=pa.float64()), 100
            ),
            "final_sample_size": pa.array(
                [r["final_sample_size"] for r in records], type=pa.float64()
            ),
            "final_lr": pa.array([r["final_lr"] for r in records], type=pa.float64()),
            "final_v_grad": pa.array([r["final_v_grad"] for r in records], type=pa.float64()),
            "median_q_error": pa.array(
                [r["median_q_error"] for r in records], type=pa.float64()
            ),
            "mean_q_error": pa.array(
                [r["mean_q_error"] for r in records], type=pa.float64()
            ),
            "p95_q_error": pa.array([r["p95_q_error"] for r in records], type=pa.float64()),
            "max_q_error": pa.array([r["max_q_error"] for r in records], type=pa.float64()),
        }
    )
    pq.write_table(table, out_path, compression="snappy")
    log(f"  저장: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB, {len(records)} rows)")

    # 요약 출력
    log("===== Stage 4 결과 요약 (median Q-error, 5 seed 평균) =====")
    log(f"{'selectivity':>12} | {'mode':>13} | {'med_qe':>10} {'mean_qe':>10} {'max_qe':>12} | {'final_ss':>12}")
    for s in selectivities:
        for mode in modes:
            sub = [r for r in records if r["selectivity"] == s and r["mode"] == mode]
            med = np.mean([r["median_q_error"] for r in sub])
            mean = np.mean([r["mean_q_error"] for r in sub])
            mx = np.mean([r["max_q_error"] for r in sub])
            ss = np.mean([r["final_sample_size"] for r in sub])
            log(
                f"{s:>12.3f} | {mode:>13} | "
                f"{med:>10.3f} {mean:>10.3f} {mx:>12.1f} | {ss:>12.1f}"
            )

    meta = {
        "timestamp_kst": kst_now_iso(),
        "script": "scripts/rq1_stage4_adaptive.py",
        "selectivities": selectivities,
        "modes": modes,
        "seeds": seeds,
        "rows_per_block": args.rows_per_block,
        "total_runs": int(total_runs),
        "total_time_s": round(time.time() - t0, 2),
        "exqutor_params": {
            "alpha": ALPHA,
            "beta": BETA,
            "momentum": MOMENTUM,
            "lr_lambda": LR_LAMBDA,
            "lr_init": LR_INIT,
            "sample_size_init": SAMPLE_SIZE_INIT,
            "sample_update_cycle": SAMPLE_UPDATE_CYCLE,
        },
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    log(f"메타: {meta_path}")
    log(f"===== Stage 4 완료 (총 {time.time()-t0:.1f}s) =====")
    return 0


if __name__ == "__main__":
    sys.exit(main())
