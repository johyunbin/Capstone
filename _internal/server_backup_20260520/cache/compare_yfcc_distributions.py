#!/usr/bin/env python3
"""5/8 회의용 — YFCC 채림 적재본 vs build_yfcc 분포 비교.
Compares partsupp_yfcc_10 (chairim vanilla_sf100) vs partsupp_yfcc_pca_10 (build_yfcc_dl)."""
import json
import time
from pathlib import Path
import numpy as np
import psycopg

PORT = 55435
DB = USER = "wns41559"
NPY_DIR = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
N_STRATA = 20
N_SAMPLE = 100_000  # subsample for speed


def fetch_subsample(table, embed_col, n_sample):
    print(f"[fetch] {table} subsample {n_sample}...", flush=True)
    t0 = time.time()
    with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER) as c:
        cu = c.cursor()
        cu.execute(f"SELECT {embed_col}::real[] FROM {table} ORDER BY ps_partkey LIMIT {n_sample}")
        rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
    arr = np.stack(rows)
    print(f"[fetch] {table}: {arr.shape} in {time.time()-t0:.1f}s", flush=True)
    return arr


def compare(name, A, B):
    """Compare two equally-shaped vector arrays."""
    print(f"\n=== {name} ===")
    print(f"  shape A={A.shape}, B={B.shape}")
    norms_a = np.linalg.norm(A, axis=1)
    norms_b = np.linalg.norm(B, axis=1)
    print(f"  norm  A: mean={norms_a.mean():.4f} std={norms_a.std():.4f}")
    print(f"  norm  B: mean={norms_b.mean():.4f} std={norms_b.std():.4f}")
    # cosine similarity row-wise (only if same shape)
    if A.shape == B.shape:
        cos = (A * B).sum(axis=1) / (norms_a * norms_b + 1e-9)
        print(f"  row-wise cosine: mean={cos.mean():.4f} std={cos.std():.4f}")
        diff = np.linalg.norm(A - B, axis=1)
        print(f"  L2 diff: mean={diff.mean():.4f} std={diff.std():.4f}")
    return {
        "shape_A": list(A.shape), "shape_B": list(B.shape),
        "norm_A_mean": float(norms_a.mean()), "norm_A_std": float(norms_a.std()),
        "norm_B_mean": float(norms_b.mean()), "norm_B_std": float(norms_b.std()),
        "cos_mean": float(cos.mean()) if A.shape == B.shape else None,
        "L2_diff_mean": float(diff.mean()) if A.shape == B.shape else None,
    }


def main():
    out = {}
    for sf in [1, 10]:
        # chairim
        chairim_table = f"partsupp_yfcc_{sf}"
        # build_yfcc result
        dl_table = f"partsupp_yfcc_pca_{sf}"
        try:
            A = fetch_subsample(chairim_table, "ps_embedding", N_SAMPLE)
            B = fetch_subsample(dl_table, "ps_embedding", N_SAMPLE)
            out[f"sf{sf}"] = compare(f"YFCC sf{sf} chairim vs build_yfcc", A, B)
        except Exception as e:
            print(f"FAIL sf{sf}: {e}")
            out[f"sf{sf}"] = {"error": str(e)}
    Path("/tmp/yfcc_distribution_compare.json").write_text(json.dumps(out, indent=2))
    print("\n[done] saved /tmp/yfcc_distribution_compare.json")


if __name__ == "__main__":
    main()
