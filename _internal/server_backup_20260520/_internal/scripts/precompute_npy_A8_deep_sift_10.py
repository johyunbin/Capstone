#!/usr/bin/env python3
"""
A8-DEEP+SIFT-sf10 NPY cache pre-compute script.

목적:
  measure_paper_exact.py 의 A8-DEEP+SIFT-sf10 cell 측정 시 fetch_all_vectors_safe()
  가 NPY cache fast-path 를 시도하지만 다음 두 file 이 부재 → PG fallback 진입 →
  partsupp_deep_sift_10 table 에 stratum_id column 이 없어 fail.

  필요 file (cache/rq1/):
    partsupp_deep_sift_10_vectors.npy   (8M × 96 float32, ~2.9G)
    partsupp_deep_sift_10_strata.npy    (8M, int16, KM20)

발견 사실 (5/16 00:54 검증):
  1. partsupp_deep_sift_10 table = 8M rows (사용자 prompt "80M" 은 SF100 오타)
  2. partsupp_deep_10 table 도 동일 8M rows + 동일 ps_partkey range (1~2M)
  3. partsupp_deep_10_vectors.npy (8M × 96 float32) 와
     _DROPPED_imgimg/partsupp_deep_sift_10_emb1.npy 의 row[0,1M,-1] vector 가 완전 일치
     → ps_embedding_deep column 동일 base + ORDER BY ps_partkey 동일 순서로 build 됨
  4. partsupp_deep_10_strata.npy 도 동일 base 기반 KM20 fit 결과 → 그대로 재사용 가능
  5. 기존 partsupp_deep_wiki_10_*.npy 는 partsupp_deep_10_*.npy 의 symlink (5/10 13:43)
     → 동일 패턴 적용

해결 (옵션 A — 권장, 기본 mode):
  partsupp_deep_10_vectors.npy + _strata.npy 를 partsupp_deep_sift_10_*.npy 로 symlink.
  ~수초 완료, storage 추가 X.

해결 (옵션 B — fresh fit, --fit 옵션):
  PG 에서 partsupp_deep_sift_10 의 ps_embedding_deep 을 직접 fetch + KM20 fresh fit.
  ~30분, storage +3.2G.

사용:
  # 옵션 A (default)
  python3 precompute_npy_A8_deep_sift_10.py
  # 옵션 A + dry-run sanity
  python3 precompute_npy_A8_deep_sift_10.py --check
  # 옵션 B (fresh fit)
  python3 precompute_npy_A8_deep_sift_10.py --fit

서버: /mnt/hdd0/home/capstone2026/_internal/scripts/precompute_npy_A8_deep_sift_10.py
배포: scp 또는 rsync 로 서버 동일 path 에 placement
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np


CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
SRC_BASE = "partsupp_deep_10"           # 8M × 96 float32, KM20 strata 동일 base
DST_NAME = "partsupp_deep_sift_10"      # measure_paper_exact A8 cell table 명


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# 옵션 A — symlink (default)
# ---------------------------------------------------------------------------

def link_one(src: Path, dst: Path, dry: bool = False) -> str:
    """absolute path 로 symlink. 이미 존재 + correct → skip, 다른 link → repoint, file → abort."""
    if not src.exists():
        return f"FAIL: source missing {src}"
    if dst.exists() or dst.is_symlink():
        if dst.is_symlink():
            current = os.readlink(dst)
            if current == str(src):
                return f"SKIP: already linked → {src.name}"
            else:
                if dry:
                    return f"DRY: would repoint {dst.name} ({current} → {src})"
                dst.unlink()
        else:
            return f"FAIL: {dst.name} is real file (not symlink) — manual review needed"
    if dry:
        return f"DRY: would create symlink {dst.name} → {src.name}"
    dst.symlink_to(src)
    return f"OK : {dst.name} → {src.name}"


def run_symlink(dry: bool = False) -> int:
    print(f"[{kst()}] === A8 NPY symlink mode (src={SRC_BASE}, dst={DST_NAME}) ===")
    pairs = [
        (CACHE / f"{SRC_BASE}_vectors.npy", CACHE / f"{DST_NAME}_vectors.npy"),
        (CACHE / f"{SRC_BASE}_strata.npy",  CACHE / f"{DST_NAME}_strata.npy"),
    ]
    fail = 0
    for src, dst in pairs:
        msg = link_one(src, dst, dry=dry)
        print(f"[{kst()}] {msg}")
        if msg.startswith("FAIL"):
            fail += 1
    return fail


# ---------------------------------------------------------------------------
# 옵션 B — fresh fit (PG fetch + KM20)
# ---------------------------------------------------------------------------

def run_fit() -> int:
    """PG 에서 partsupp_deep_sift_10.ps_embedding_deep 을 fetch + KM20 fit.

    fetch 패턴은 _measure_common.fetch_all_vectors_safe 의 PG fallback 과 동일하지만
    stratum_id 가 없으므로 단일 SELECT (ORDER BY ps_partkey) — 8M rows 면 메모리 부담.
    1M chunk 로 stream + np.lib.format.open_memmap 으로 disk 직접 write.
    """
    try:
        import psycopg
    except ImportError:
        print(f"[{kst()}] FAIL: psycopg unavailable — server only", file=sys.stderr)
        return 1
    try:
        from sklearn.cluster import MiniBatchKMeans
    except ImportError:
        print(f"[{kst()}] FAIL: sklearn unavailable", file=sys.stderr)
        return 1

    PORT = 55435
    DB = "wns41559"
    USER = "wns41559"
    TABLE = DST_NAME
    EMBED = "ps_embedding_deep"
    DIM = 96
    N_STRATA = 20
    CHUNK = 100_000

    out_vec = CACHE / f"{DST_NAME}_vectors.npy"
    out_str = CACHE / f"{DST_NAME}_strata.npy"
    if out_vec.exists() or out_str.exists():
        print(f"[{kst()}] FAIL: target NPY already exists — manual remove first", file=sys.stderr)
        return 1

    # row count
    with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f"SELECT count(*) FROM {TABLE}")
        n_rows = int(cu.fetchone()[0])
    print(f"[{kst()}] PG row count: {n_rows:,}")

    # vectors disk-stream
    print(f"[{kst()}] streaming {EMBED} → {out_vec.name} ({n_rows:,} × {DIM} float32, ~{n_rows*DIM*4/1e9:.1f}G)")
    vecs = np.lib.format.open_memmap(
        str(out_vec), mode="w+", dtype=np.float32, shape=(n_rows, DIM)
    )
    t0 = time.time()
    fetched = 0
    with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor(name="a8_stream")
        cu.itersize = CHUNK
        cu.execute(f"SELECT {EMBED}::real[] FROM {TABLE} ORDER BY ps_partkey, ps_suppkey")
        for row in cu:
            vecs[fetched] = np.asarray(row[0], dtype=np.float32)
            fetched += 1
            if fetched % CHUNK == 0:
                elapsed = time.time() - t0
                eta = elapsed / fetched * (n_rows - fetched)
                print(f"[{kst()}]   fetched {fetched:,}/{n_rows:,} "
                      f"({100*fetched/n_rows:.1f}%) elapsed={elapsed/60:.1f}m eta={eta/60:.1f}m")
    vecs.flush()
    print(f"[{kst()}] fetch done — {fetched:,} rows in {(time.time()-t0)/60:.1f}m")

    # KM20 fit
    print(f"[{kst()}] KM20 MiniBatchKMeans fit_predict ({N_STRATA} clusters)...")
    t1 = time.time()
    km = MiniBatchKMeans(
        n_clusters=N_STRATA,
        random_state=42,
        batch_size=4096,
        n_init=10,
        max_no_improvement=20,
    )
    sids = km.fit_predict(vecs).astype(np.int16)
    np.save(str(out_str), sids)
    print(f"[{kst()}] KM20 done in {(time.time()-t1)/60:.1f}m — wrote {out_str.name}")
    return 0


# ---------------------------------------------------------------------------
# Sanity check (--check)
# ---------------------------------------------------------------------------

def run_check() -> int:
    """sample sanity: 산출물 NPY load + shape + 첫 row vs partsupp_deep_10 비교."""
    print(f"[{kst()}] === sanity check ===")
    out_vec = CACHE / f"{DST_NAME}_vectors.npy"
    out_str = CACHE / f"{DST_NAME}_strata.npy"
    src_vec = CACHE / f"{SRC_BASE}_vectors.npy"
    src_str = CACHE / f"{SRC_BASE}_strata.npy"

    if not out_vec.exists():
        print(f"[{kst()}] FAIL: {out_vec.name} missing — run without --check first")
        return 1
    if not out_str.exists():
        print(f"[{kst()}] FAIL: {out_str.name} missing")
        return 1

    a = np.load(str(out_vec), mmap_mode="r")
    s = np.load(str(out_str), mmap_mode="r")
    b = np.load(str(src_vec), mmap_mode="r")
    t = np.load(str(src_str), mmap_mode="r")

    print(f"[{kst()}] out vectors: {a.shape} {a.dtype}  ({a.nbytes/1e9:.2f} GB)")
    print(f"[{kst()}] out strata : {s.shape} {s.dtype}  unique={len(np.unique(s))}")
    print(f"[{kst()}] src vectors: {b.shape} {b.dtype}")
    print(f"[{kst()}] src strata : {t.shape} {t.dtype}  unique={len(np.unique(t))}")

    # 1M sample 비교 (전체 8M 면 5분 → sample만)
    sample_idx = [0, 1, 100, 10_000, 1_000_000, len(a)//2, len(a)-1]
    diffs = []
    for i in sample_idx:
        eq_v = np.allclose(a[i], b[i])
        eq_s = int(s[i]) == int(t[i])
        diffs.append((i, eq_v, eq_s))
        print(f"[{kst()}]   idx {i:>10,}: vec eq={eq_v} stratum eq={eq_s} (out_sid={int(s[i])} src_sid={int(t[i])})")

    all_ok = all(eq_v and eq_s for _, eq_v, eq_s in diffs)
    print(f"[{kst()}] === sanity {'PASS' if all_ok else 'FAIL'} ===")
    return 0 if all_ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="A8-DEEP+SIFT-sf10 NPY cache pre-compute")
    ap.add_argument("--fit", action="store_true",
                    help="fresh KM20 fit from PG (option B). default = symlink to partsupp_deep_10")
    ap.add_argument("--check", action="store_true",
                    help="sanity check existing NPY (no write)")
    ap.add_argument("--dry-run", action="store_true",
                    help="symlink dry-run (print only, no fs change)")
    args = ap.parse_args()

    if args.check:
        return run_check()
    if args.fit:
        return run_fit()
    return run_symlink(dry=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
