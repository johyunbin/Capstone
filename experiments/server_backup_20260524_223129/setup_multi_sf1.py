#!/usr/bin/env python3
"""
Multi-cell SF1 setup — NPY 캐시 생성 (PG 의존 없음).

목적: 기존 measure_multi_5mode.py / measure_multi_4kang.py / measure_multi_adaptive_sampling.py
가 사용하는 NPY pattern (partsupp_deep_sift_10_emb1.npy 등) 의 SF1 변종을
"이미 존재하는 SF1 source NPY (cache/rq1/)" 로부터 합성한다.

입력 NPY (이미 존재):
  /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_deep_1_vectors.npy   (800K × 96)
  /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_deep_1_pks.npy       (800K × 2 [partkey, suppkey])
  /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_sift_1_vectors.npy   (800K × 128)
  /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_sift_1_pks.npy       (800K × 2)
  /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_wiki_1_vectors.npy   (800K × 768)
  /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_wiki_1_pks.npy       (800K × 2)

출력 NPY (cache/rq3/ 에 생성):
  partsupp_deep_sift_1_emb1.npy    (800K × 96  float32)  — deep
  partsupp_deep_sift_1_emb2.npy    (800K × 128 float32)  — sift
                                                           (partkey, suppkey 1:1 동일 → 직접 align)

  partsupp_deep_wiki_1_emb1.npy    (800K × 96  float32)  — deep
  partsupp_deep_wiki_1_emb2.npy    (800K × 768 float32)  — wiki broadcast
                                                           (deep 의 각 partkey 에 wiki 의 같은 partkey first wiki embedding)

  part_wiki_1_vectors.npy          (200K × 768 float32)  — wiki dedup, partkey 별 first
  part_wiki_1_partkeys.npy         (200K × 1 int64)      — partkey

  partsupp_deep_1_vectors.npy → cache/rq3 에도 복사 (multi_join 용 path 일치)
  partsupp_deep_1_partkeys.npy → cache/rq3 에 복사

검증:
  - partkey alignment 확인 (모든 sf1 source 의 partkey range 1~200000 동일)
  - deep / sift 의 (partkey, suppkey) 가 완전 동일 → 이미 sorted 동일 순서로 저장됐는지 확인
  - wiki 의 suppkey 패턴이 다르므로 partkey-only broadcast (4 suppkeys per partkey 의 first wiki)

서버: /mnt/hdd0/home/capstone2026/_internal/scripts/setup_multi_sf1.py
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np


CACHE_RQ1 = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
CACHE_RQ3 = Path("/mnt/hdd0/home/capstone2026/cache/rq3")


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def load_source(name: str) -> tuple[np.ndarray, np.ndarray]:
    """cache/rq1/{name}_vectors.npy + _pks.npy load."""
    vec = np.load(CACHE_RQ1 / f"{name}_vectors.npy")
    pks = np.load(CACHE_RQ1 / f"{name}_pks.npy")
    print(f"[{kst()}]   loaded {name}: vec={vec.shape} pks={pks.shape}")
    return vec, pks


def sort_by_pks(vec: np.ndarray, pks: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(partkey, suppkey) lexicographic sort."""
    order = np.lexsort((pks[:, 1], pks[:, 0]))
    return vec[order], pks[order]


def build_deep_sift() -> None:
    """deep_sift_1: 두 source 의 (partkey, suppkey) 가 동일 → 직접 align."""
    print(f"[{kst()}] >>> build deep_sift_1")
    deep_vec, deep_pks = load_source("partsupp_deep_1")
    sift_vec, sift_pks = load_source("partsupp_sift_1")

    # 정렬해서 row order 일치 보장
    print(f"[{kst()}]   sorting by (partkey, suppkey)")
    deep_vec, deep_pks = sort_by_pks(deep_vec, deep_pks)
    sift_vec, sift_pks = sort_by_pks(sift_vec, sift_pks)

    if not np.array_equal(deep_pks, sift_pks):
        # 부분 mismatch 시 안전한 join (partkey, suppkey) 매칭
        print(f"[{kst()}]   WARNING: pks mismatch, doing key intersection")
        d_keys = deep_pks.astype(np.int64).copy()
        s_keys = sift_pks.astype(np.int64).copy()
        d_kk = d_keys[:, 0].astype(np.int64) * (10**8) + d_keys[:, 1].astype(np.int64)
        s_kk = s_keys[:, 0].astype(np.int64) * (10**8) + s_keys[:, 1].astype(np.int64)
        common = np.intersect1d(d_kk, s_kk)
        d_idx = np.searchsorted(d_kk, common)
        s_idx = np.searchsorted(s_kk, common)
        deep_vec = deep_vec[d_idx]
        sift_vec = sift_vec[s_idx]
        deep_pks = deep_pks[d_idx]
        print(f"[{kst()}]   intersection size = {len(common):,}")
    else:
        print(f"[{kst()}]   pks identical after sort — direct 1:1 alignment")

    out1 = CACHE_RQ3 / "partsupp_deep_sift_1_emb1.npy"
    out2 = CACHE_RQ3 / "partsupp_deep_sift_1_emb2.npy"
    np.save(out1, deep_vec.astype(np.float32))
    np.save(out2, sift_vec.astype(np.float32))
    print(f"[{kst()}]   saved {out1.name}: {deep_vec.shape}")
    print(f"[{kst()}]   saved {out2.name}: {sift_vec.shape}")


def build_deep_wiki() -> None:
    """deep_wiki_1: deep 의 각 row partkey 에 wiki 의 같은 partkey first wiki embedding broadcast.

    wiki 는 (partkey, suppkey) 패턴이 deep 과 다르므로 partkey-level group 후 first.
    """
    print(f"[{kst()}] >>> build deep_wiki_1")
    deep_vec, deep_pks = load_source("partsupp_deep_1")
    wiki_vec, wiki_pks = load_source("partsupp_wiki_1")

    deep_vec, deep_pks = sort_by_pks(deep_vec, deep_pks)
    wiki_vec, wiki_pks = sort_by_pks(wiki_vec, wiki_pks)

    # wiki: partkey 별 first wiki embedding (group by partkey, take first row after sort)
    print(f"[{kst()}]   building partkey -> first wiki row map")
    w_pk = wiki_pks[:, 0]
    # partkey 가 정렬된 상태에서 첫 출현 idx 만 추출
    _, first_idx = np.unique(w_pk, return_index=True)
    pk_to_wiki = {int(w_pk[i]): wiki_vec[i] for i in first_idx}

    # deep 의 각 row partkey -> wiki broadcast
    print(f"[{kst()}]   broadcasting wiki to deep rows ({len(deep_pks):,})")
    wiki_broadcast = np.empty((len(deep_pks), wiki_vec.shape[1]), dtype=np.float32)
    missing = 0
    for i, pk in enumerate(deep_pks[:, 0]):
        if int(pk) in pk_to_wiki:
            wiki_broadcast[i] = pk_to_wiki[int(pk)]
        else:
            missing += 1
            wiki_broadcast[i] = 0.0
    if missing > 0:
        print(f"[{kst()}]   WARNING: {missing:,} deep rows have no matching wiki partkey")

    out1 = CACHE_RQ3 / "partsupp_deep_wiki_1_emb1.npy"
    out2 = CACHE_RQ3 / "partsupp_deep_wiki_1_emb2.npy"
    np.save(out1, deep_vec.astype(np.float32))
    np.save(out2, wiki_broadcast)
    print(f"[{kst()}]   saved {out1.name}: {deep_vec.shape}")
    print(f"[{kst()}]   saved {out2.name}: {wiki_broadcast.shape}")


def build_part_wiki() -> None:
    """part_wiki_1: partkey 별 first wiki embedding (200K rows × 768d).

    multi_join_deep_wiki_1 cell 에서 사용 (load_cell 의 multi_join_deep_wiki branch
    가 part_wiki_*_vectors.npy + _partkeys.npy 두 파일을 기대).
    """
    print(f"[{kst()}] >>> build part_wiki_1")
    wiki_vec, wiki_pks = load_source("partsupp_wiki_1")
    wiki_vec, wiki_pks = sort_by_pks(wiki_vec, wiki_pks)
    w_pk = wiki_pks[:, 0]

    # partkey 별 first row 추출
    print(f"[{kst()}]   dedup by partkey (first occurrence)")
    _, first_idx = np.unique(w_pk, return_index=True)
    first_idx = np.sort(first_idx)
    part_keys = w_pk[first_idx].astype(np.int64)
    part_vec = wiki_vec[first_idx].astype(np.float32)

    out_v = CACHE_RQ3 / "part_wiki_1_vectors.npy"
    out_k = CACHE_RQ3 / "part_wiki_1_partkeys.npy"
    np.save(out_v, part_vec)
    np.save(out_k, part_keys)
    print(f"[{kst()}]   saved {out_v.name}: {part_vec.shape}")
    print(f"[{kst()}]   saved {out_k.name}: {part_keys.shape} (range {part_keys.min()}..{part_keys.max()})")


def build_partsupp_deep() -> None:
    """partsupp_deep_1_vectors.npy + _partkeys.npy 를 cache/rq3 에 복사 (multi_join 경로 호환).

    measure_multi_5mode.py 의 load_cell 'multi_join_deep_wiki' branch 가
    partsupp_deep_10_vectors.npy + _partkeys.npy 를 read.
    SF1 cell (multi_join_deep_wiki_1) 에서는 _10 → _1 만 다른 동일 패턴 필요.
    """
    print(f"[{kst()}] >>> copy partsupp_deep_1 to cache/rq3")
    deep_vec, deep_pks = load_source("partsupp_deep_1")
    deep_vec, deep_pks = sort_by_pks(deep_vec, deep_pks)
    # partkey only (multi_join load_cell 이 _partkeys.npy 를 1D ps_partkey 로 기대)
    deep_partkeys = deep_pks[:, 0].astype(np.int64)
    out_v = CACHE_RQ3 / "partsupp_deep_1_vectors.npy"
    out_k = CACHE_RQ3 / "partsupp_deep_1_partkeys.npy"
    np.save(out_v, deep_vec.astype(np.float32))
    np.save(out_k, deep_partkeys)
    print(f"[{kst()}]   saved {out_v.name}: {deep_vec.shape}")
    print(f"[{kst()}]   saved {out_k.name}: {deep_partkeys.shape}")


def main() -> None:
    t0 = time.time()
    print(f"[{kst()}] === Multi SF1 cell setup start ===")

    # 작업 1: partsupp_deep_sift_1 (single table multi-vector, deep + sift)
    build_deep_sift()

    # 작업 2: partsupp_deep_wiki_1 (single table multi-vector, deep + wiki broadcast)
    build_deep_wiki()

    # 작업 3: part_wiki_1 (multi-table join 의 우측 wiki dedup table)
    build_part_wiki()

    # 작업 4: partsupp_deep_1_vectors.npy / _partkeys.npy 복사 (multi_join load_cell 호환)
    build_partsupp_deep()

    elapsed = time.time() - t0
    print(f"[{kst()}] === setup complete in {elapsed:.1f}s ===")


if __name__ == "__main__":
    main()
