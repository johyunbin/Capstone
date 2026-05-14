#!/usr/bin/env python3
"""
RQ1 Phase 6 Step 4 — KM20 stratum_id를 (ps_partkey, stratum_id) CSV로 export.

본 export 는 Phase 6 Step 4 (Native vector.c 구현) 의 사전 작업이다.
phase6_layer_compare.py 의 build_layer_kmeans (seed=42 고정) 함수를 그대로
재사용해서 1M × stratum_id 결과를 파생, ps_partkey 와 zip 해서 CSV 로 dump.

서버에서 본 CSV 를 COPY 로 임시 테이블에 적재 → UPDATE 로 subset_1m 의
새 stratum_id INT2 컬럼에 배정한다 (Step 4 의 setup 단계).

서버 사용 위치:
  /mnt/hdd0/home/capstone2026/cache/rq1_phase6_export_km20_strata.py
  → 결과는 cache/rq1/km20_strata.csv (8.7 MB, 1M+1 행)
"""

import argparse
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq


# ---- phase6_layer_compare.py 의 함수를 inline 복사 (서버 파일명 충돌 회피) -----


def load_parquet_vectors(path: str) -> tuple[np.ndarray, np.ndarray]:
    table = pq.read_table(path)
    pks = np.asarray(table.column("ps_partkey").to_numpy(), dtype=np.int64)
    emb_col = table.column("embedding").combine_chunks()
    flat = emb_col.flatten().to_numpy(zero_copy_only=False)
    n = len(pks)
    dim = len(flat) // n
    vecs = flat.reshape(n, dim).astype(np.float32, copy=False)
    return pks, vecs


def build_layer_kmeans(
    vectors: np.ndarray,
    k: int,
    batch_size: int = 4096,
    n_iter: int = 100,
    seed: int = 42,
) -> tuple[np.ndarray, dict]:
    """phase6_layer_compare.build_layer_kmeans 와 정확 동일 (Sculley 2010 mini-batch k-means)."""
    n, dim = vectors.shape
    rng = np.random.default_rng(seed)
    init_idx = rng.choice(n, size=k, replace=False)
    centroids = vectors[init_idx].astype(np.float64).copy()
    counts = np.zeros(k, dtype=np.int64)

    t0 = time.time()
    for it in range(n_iter):
        batch_idx = rng.choice(n, size=batch_size, replace=False)
        batch = vectors[batch_idx].astype(np.float64)
        b_sq = (batch * batch).sum(axis=1)
        c_sq = (centroids * centroids).sum(axis=1)
        dots = batch @ centroids.T
        d2 = b_sq[:, None] + c_sq[None, :] - 2 * dots
        labels = np.argmin(d2, axis=1)
        for kk in range(k):
            mask = labels == kk
            n_k = int(mask.sum())
            if n_k == 0:
                continue
            counts[kk] += n_k
            eta = n_k / counts[kk]
            centroids[kk] = (1 - eta) * centroids[kk] + eta * batch[mask].mean(axis=0)
    t_train = time.time() - t0

    t1 = time.time()
    x_sq = (vectors.astype(np.float32) * vectors.astype(np.float32)).sum(axis=1)
    c_sq32 = (centroids * centroids).sum(axis=1).astype(np.float32)
    dots = vectors.astype(np.float32) @ centroids.T.astype(np.float32)
    d2_full = x_sq[:, None] + c_sq32[None, :] - 2 * dots
    stratum_id = np.argmin(d2_full, axis=1).astype(np.int16)
    t_assign = time.time() - t1

    sizes = np.bincount(stratum_id, minlength=k)
    inertia = float(np.mean(np.min(d2_full, axis=1)))

    info = {
        "layer": f"kmeans_k{k}",
        "n_strata": int(k),
        "batch_size": int(batch_size),
        "n_iter": int(n_iter),
        "seed": int(seed),
        "t_train_s": round(t_train, 2),
        "t_assign_s": round(t_assign, 2),
        "size_min": int(sizes.min()),
        "size_max": int(sizes.max()),
        "size_std": float(sizes.std()),
        "inertia_mean": inertia,
    }
    return stratum_id, info


def kst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now()}] {msg}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    ap.add_argument("--out", default=None, help="기본 in-dir/km20_strata.csv")
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--kmeans-iter", type=int, default=100)
    ap.add_argument("--kmeans-batch", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    in_dir = Path(args.in_dir)
    out_path = Path(args.out) if args.out else in_dir / "km20_strata.csv"

    log(f"loading subset {in_dir / 'subset_1m.parquet'}")
    pks, vecs = load_parquet_vectors(str(in_dir / "subset_1m.parquet"))
    log(f"  loaded shape={vecs.shape}, pk min={int(pks.min())}, max={int(pks.max())}")

    log(f"building kmeans K={args.k} (seed={args.seed}) ...")
    t0 = time.time()
    stratum_id, info = build_layer_kmeans(
        vecs,
        k=args.k,
        batch_size=args.kmeans_batch,
        n_iter=args.kmeans_iter,
        seed=args.seed,
    )
    log(
        f"  done ({time.time() - t0:.2f}s, sizes [{info['size_min']},{info['size_max']}], "
        f"std={info['size_std']:.1f}, inertia={info['inertia_mean']:.4f})"
    )

    # 안정성 체크: phase6_layer_compare 에서 본 KM20 의 sizes 와 일치해야 한다.
    assert len(pks) == len(stratum_id), "pk vs stratum length mismatch"
    sizes = np.bincount(stratum_id, minlength=args.k)
    log(f"  per-stratum sizes (top 5): {sizes[:5].tolist()}")

    # CSV write — 1M+1 줄, header 포함 ~ 8.7 MB
    log(f"writing {out_path}")
    t1 = time.time()
    with open(out_path, "w") as f:
        f.write("ps_partkey,stratum_id\n")
        for i in range(len(pks)):
            f.write(f"{int(pks[i])},{int(stratum_id[i])}\n")
    log(f"  saved ({time.time() - t1:.2f}s, {out_path.stat().st_size / 1e6:.2f} MB)")

    # 안정성 마커 — meta json 도 같이 dump
    meta_path = out_path.with_suffix(".meta.json")
    import json

    with open(meta_path, "w") as f:
        json.dump(
            {
                "kst": kst_now(),
                "args": vars(args),
                "n_rows": int(len(pks)),
                "k": int(args.k),
                "sizes": sizes.tolist(),
                "kmeans_info": info,
            },
            f,
            indent=2,
            default=str,
        )
    log(f"  saved {meta_path}")
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
