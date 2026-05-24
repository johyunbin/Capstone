#!/usr/bin/env python3
"""
RQ3 #5 — C. Random Projection 측정.

P2 commit (39cfc3a) 의 offline_simple/random_projection.py 의 결정론적 Gaussian
projection + argmax bucket 으로 stratum_id 부여, _measure_common.py 백엔드로 측정.

흐름:
1. fetch_all_vectors_safe(ds): 전체 vector 회수
2. make_projection(dim, k=20, seed): (dim, 20) projection matrix (학습 X, seed 고정)
3. assign_random_projection(): vec @ matrix → argmax bucket → stratum_id
4. run_method_measurement(): equal allocation 측정

가설 H3-C: recovery_rate 10~40% (단순 하한, JL 거리 보존만 보장 — cluster 구조 X).

사용:
    python3 experiments/code/rq3/run_random_projection.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_random_projection.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_random_proj.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_random_proj_meta.json

예상 시간: ~30분 (학습 0초 + projection 부여 ~수초 + 측정 25분)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "offline_simple"))

from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from offline_simple.random_projection import (  # noqa: E402
    assign_random_projection, cluster_size_summary, make_projection,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #5 — C. Random Projection 측정")
    ap.add_argument("--out-prefix", default="rq3_random_proj")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--proj-seed", type=int, default=42,
                    help="projection matrix seed (결정론, 측정 seed 와 별개)")
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #5 — C. Random Projection ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, proj_seed={args.proj_seed}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _km20_sids = fetch_all_vectors_safe(ds)

        matrix = make_projection(dim=ds["vec_dim"], k=N_STRATA, seed=args.proj_seed)
        stratum_ids = assign_random_projection(matrix, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   RandProj argmax bucket sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f} (불균형 자연스러움)"
        )

        rows = run_method_measurement(
            method_name="random_proj",
            all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "Random Projection (C)",
            "proj_seed": args.proj_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
