#!/usr/bin/env python3
"""
RQ3 #6 — A. LSH (Locality-Sensitive Hashing) 측정.

P4 commit 의 lsh/lsh.py 에서 결정론적 hyperplane 생성 + bucket 부여 import,
_measure_common.py 의 측정 백엔드로 5 sel × 5 seed × 100 query × 2 dataset 산출.

흐름:
1. fetch_all_vectors_safe(ds): 전체 vector 회수 (~1M~1.5M rows)
2. make_hyperplanes(dim=ds['vec_dim'], k=20, seed): 결정론적 5 hyperplanes
3. assign_lsh(W, all_vecs, k=20): mod 20 → stratum_id (0~19)
4. run_method_measurement(): equal allocation 측정 (+ 옵션 bernoulli)

가설 H3-A: recovery_rate 30~60% (LSH cosine 유사도 보존, KM20 oracle 의 절반 회수).

사용:
    python3 experiments/code/rq3/run_lsh.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_lsh.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_lsh.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_lsh_meta.json

예상 시간: ~1h (DEEP fetch 5m + SIFT fetch 7m + assign <1s × 2 + 측정 30m)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
# NOTE: ROOT/lsh 를 sys.path 에 추가하면 'lsh.py' 파일과 'lsh/' namespace package
# 사이의 path resolution 충돌로 `from lsh.lsh import` 가 fail. ROOT 만 두면 'lsh'
# 가 ROOT/lsh/ namespace package 로 resolve 되어 'lsh.lsh' 정상 작동.

from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from lsh.lsh import (  # noqa: E402
    assign_lsh, cluster_size_summary, make_hyperplanes,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #6 — A. LSH (Random Hyperplane) 측정")
    ap.add_argument("--out-prefix", default="rq3_lsh")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42,
                    help="hyperplane seed (결정론, default 42)")
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #6 — A. LSH (Random Hyperplane, k={N_STRATA}) ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, seed={args.seed}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _km20_sids = fetch_all_vectors_safe(ds)

        W = make_hyperplanes(dim=ds["vec_dim"], k=N_STRATA, seed=args.seed)
        print(f"[{kst()}]   hyperplanes: shape={W.shape} seed={args.seed}")

        stratum_ids = assign_lsh(W, all_vecs, k=N_STRATA)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   LSH bucket sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="lsh",
            all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "LSH Random Hyperplane (A)",
            "k": N_STRATA,
            "n_hyperplanes": 5,
            "hyperplane_seed": args.seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
