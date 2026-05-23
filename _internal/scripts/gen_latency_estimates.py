#!/usr/bin/env python3
"""VAQ 쿼리 벡터별 카디널리티 추정치 생성 — 엔진 적용 검증 실험 Phase 1.

특정 (dataset, sf)의 query pool 벡터들에 대해, 각 selectivity·method 조합의
B1 / CaseA / CaseB / CaseA_mean / CaseC 추정치와 참 카디널리티를 산출한다.
measure_paper_exact.py의 measure_b1_paper / measure_case_b / measure_case_c 추정
로직을 단일 query·고정 budget(N=385)으로 축소 재사용 — AdaptiveState 동적 루프
없이 paper Eq1 초기 budget만 사용.

산출 parquet 1행 = (dataset, sf, sel, query_id, method):
  est_b1         B1 무작위 Bernoulli 추정 (method 무관 — 같은 query_id면 동일)
  est_caseA      method stratified 추정 (완전 대체)
  est_caseB      (est_b1 + est_caseA) / 2  (결합)
  est_caseA_mean 강한 13 method stratified 평균 (method-agnostic — 같은 query_id면 동일,
                  v13_summary §4.4 불안정 클러스터링 3종 gmm·minibatch_partial·faiss_ivf 제외)
  est_caseC      dual-Bernoulli ensemble (B1 + B1' 다른 rng) / 2 (method-agnostic)
  true_card      참 카디널리티 (query_selectivity parquet의 true_cardinality)
  D              거리 임계값 (query_selectivity parquet의 D_target)
  qvec           쿼리 벡터 (harness가 VAQ SQL에 주입)

harness(measure_latency_realengine.py)가 이 parquet을 읽어 조건별 주입값을 결정한다.
CaseB 결합 method = 강한 13종 (v13_summary §4.4 — 불안정 클러스터링 3종 제외).
CaseA_mean·CaseC 는 method-agnostic — 같은 (dataset, sf, sel, query_id) row 들이
동일 값을 공유한다 (parquet schema 단순화 — 별도 (sel, query_id) 테이블 분리 회피).

서버 실행:
    python3 gen_latency_estimates.py --dataset DEEP --sf 10 --n-qvec 30 --output latency/

로컬에서는 import 검증·--help 만 가능 (벡터 fetch에 PG 필요).
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

# 서버 측 측정 백엔드 재사용 (measure_paper_exact.py와 동일 경로 패턴).
# SERVER 판정 = 서버 작업 디렉토리 존재 여부 — _measure_common.py는 repo에도 있어
# import 성공만으로는 서버 여부를 가릴 수 없다 (repo 로컬에서도 import됨).
SERVER = Path("/mnt/hdd0/home/capstone2026").is_dir()
sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
mc = None       # 서버에서 _measure_common 모듈로 채워짐
mpe = None      # 서버에서 measure_paper_exact 모듈로 채워짐
try:
    import _measure_common as mc
    import measure_paper_exact as mpe
    mc.PORT = 55435                       # _measure_common.py의 PORT=55436은 stale
except ImportError as e:
    if SERVER:
        print(f"[WARN] 측정 백엔드 import 실패: {e}")

# 강한 method 13종 (v13_summary §4.4 — 불안정 클러스터링 3종 gmm·minibatch_partial·faiss_ivf 제외)
DEFAULT_CASEB_METHODS = (
    "hilbert_real", "skilling_hilbert", "chao_weighted", "ica_fastica", "pca1d",
    "zorder_morton", "hyperloglog", "cum_sqrtf", "lavallee_hidiroglou", "rsvd",
    "sparse_rp", "mhist2", "rabitq_strat",
)
PAPER_SELECTIVITIES = (0.001, 0.01, 0.10)   # paper Fig 13 verbatim
BUDGET = 385                                # paper Eq 1 초기 sample size
EST_TRIALS = 10                             # 추정치 안정화용 평균 draw 수

DS_TABLE_SHORT = {                                        # partsupp_* PG 테이블명 prefix
    "DEEP": "deep", "SIFT": "sift", "SSN": "fb",
    "WIKI": "wiki", "YFCC": "yfcc",
    "DEEP_SIFT": "deep_sift", "DEEP_WIKI": "deep_wiki", "DEEP_YFCC": "deep_yfcc",
}
DS_ALIAS = {                                              # RQ1 cache 파일명 매칭 (query_pool_{ALIAS}_sf*.parquet)
    "DEEP": "DEEP", "SIFT": "SIFT", "SSN": "SSN",
    "WIKI": "WIKI", "YFCC": "YFCC",
    "DEEP_SIFT": "DEEP_SIFT_CONCAT", "DEEP_WIKI": "DEEP_WIKI_CONCAT",
    "DEEP_YFCC": "DEEP_YFCC_CONCAT",
}
DS_DIM = {
    "DEEP": 96, "SIFT": 128, "SSN": 256,
    "WIKI": 768, "YFCC": 192,
    "DEEP_SIFT": 224, "DEEP_WIKI": 864, "DEEP_YFCC": 288,
}
CACHE_RQ1 = Path("/mnt/hdd0/home/capstone2026/cache/rq1")


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")


def build_ds(dataset: str, sf: int) -> dict:
    """measure_paper_exact.py CellSpec 패턴의 ds dict 구성 (query pool/sel 경로 포함)."""
    short, alias = DS_TABLE_SHORT[dataset], DS_ALIAS[dataset]
    return {
        "name": dataset,
        "table": f"partsupp_{short}_{sf}",
        "embed_col": "ps_embedding",
        "vec_dim": DS_DIM[dataset],
        "query_pool": CACHE_RQ1 / f"query_pool_{alias}_sf{sf}.parquet",
        "query_sel": CACHE_RQ1 / f"query_selectivity_{alias}_sf{sf}.parquet",
    }


def gen_estimates(dataset: str, sf: int, n_qvec: int, methods, est_trials: int,
                  output_dir: Path) -> Path:
    """(dataset, sf)의 query pool 앞 n_qvec개 벡터에 대해 추정치 parquet 생성."""
    if not SERVER:
        raise RuntimeError("서버 전용 — _measure_common.py 필요 (165.132.140.240 capstone2026)")
    assert mc is not None and mpe is not None   # SERVER=True ⇒ import 성공 (정적 분석 narrowing)

    ds = build_ds(dataset, sf)
    for key in ("query_pool", "query_sel"):
        if not ds[key].exists():
            raise FileNotFoundError(f"{key} 미존재: {ds[key]}")

    print(f"[{kst()}] {dataset} sf{sf}: 벡터 fetch (table={ds['table']})")
    all_vecs, km20_sids = mc.fetch_all_vectors_safe(ds)
    samples_b1, sizes_b1 = mc.cache_cluster_samples_inmem(
        all_vecs, km20_sids, n_strata=mc.N_STRATA, seed=42)

    qp, qs_full, qvecs = mc._load_query_pool(ds)
    print(f"[{kst()}]   query 벡터 {len(qp)}개, rows {len(all_vecs):,}")

    # method별 strata + cluster sample 캐시 (method당 1회).
    # 한 method 가 특정 데이터셋서 degenerate 해도 parquet 전체 생성이 죽지 않게 — skip.
    method_cache: dict[str, tuple] = {}
    for m in methods:
        print(f"[{kst()}]   {m} strata 계산…")
        try:
            sids = mpe._get_method_strata(m, all_vecs, n_strata=mc.N_STRATA)
            method_cache[m] = mc.cache_cluster_samples_inmem(
                all_vecs, sids, n_strata=mc.N_STRATA, seed=42)
        except Exception as e:
            print(f"[{kst()}]   ! {m} skip — {type(e).__name__}: {str(e)[:140]}")
    if not method_cache:
        raise RuntimeError("모든 method strata 계산 실패 — 추정치 생성 불가")
    ok_methods = [m for m in methods if m in method_cache]
    print(f"[{kst()}]   method {len(ok_methods)}/{len(methods)}종 준비 완료")

    alloc = mc.equal_alloc(n_strata=mc.N_STRATA, budget=BUDGET)
    rng = np.random.default_rng(20260520)
    # ★ CaseC dual-Bernoulli — B1 a-side rng (20260520) 과 독립된 b-side rng (+1M offset,
    #   measure_paper_exact.py L1250 measure_case_c 의 seed pattern 과 동일).
    rng_caseC_b = np.random.default_rng(20260520 + 1_000_000)
    rows: list[dict] = []
    n_q = min(n_qvec, len(qp))
    for q_idx in range(n_q):
        qvec = qvecs[q_idx]
        for sel in PAPER_SELECTIVITIES:
            match = qs_full[(np.isclose(qs_full["selectivity"], sel)) &
                            (qs_full["query_id"] == q_idx)]
            if len(match) == 0:
                continue
            D = float(match.iloc[0]["D_target"])
            true_card = float(match.iloc[0]["true_cardinality"])
            # est_b1 — est_trials회 draw 평균 (Bernoulli 분산 큼 → 안정화)
            # 1단계 fix (5/21): all_vecs 전달 → 2단계 strata 캐시 (cluster당 500 cap,
            #   큰 cluster 과소대표 corr -0.98) 우회, 전체 벡터 직접 random sample.
            #   measure_paper_exact.py L469·L1197 의 v13 메인 캠페인과 동일 통일.
            est_b1 = float(np.mean([
                mc.bernoulli_estimate(samples_b1, sizes_b1, qvec, D, rng,
                                      budget=BUDGET, all_vecs=all_vecs)
                for _ in range(est_trials)]))
            # ★ est_caseC — dual-Bernoulli ensemble (method-agnostic 통제군).
            # B1 a-side 와 같은 samples cache, 다른 rng 로 독립 draw → 평균.
            # measure_paper_exact.py measure_case_c L1269-1271 과 동일 구조.
            est_b1_b = float(np.mean([
                mc.bernoulli_estimate(samples_b1, sizes_b1, qvec, D, rng_caseC_b,
                                      budget=BUDGET, all_vecs=all_vecs)
                for _ in range(est_trials)]))
            est_caseC = (est_b1 + est_b1_b) / 2.0
            # ★ est_caseA_mean — 16 method stratified 추정 평균 (method-agnostic).
            #   먼저 모든 method estimate 산출 → row 작성 단계에서 mean 주입.
            est_methods: dict[str, float] = {}
            for m in ok_methods:
                s_m, sz_m = method_cache[m]
                est_methods[m] = float(np.mean([
                    mc.stratified_estimate(s_m, sz_m, alloc, qvec, D, rng)
                    for _ in range(est_trials)]))
            est_caseA_mean = float(np.mean(list(est_methods.values()))) if est_methods else 0.0
            for m, est_method in est_methods.items():
                rows.append({
                    "dataset": dataset, "sf": sf, "sel": sel, "query_id": q_idx,
                    "method": m, "est_b1": est_b1, "est_caseA": est_method,
                    "est_caseB": (est_b1 + est_method) / 2.0,
                    "est_caseA_mean": est_caseA_mean,
                    "est_caseC": est_caseC,
                    "true_card": true_card, "D": D,
                    "qvec": qvec.astype(np.float32).tolist(),
                })
        if (q_idx + 1) % 10 == 0:
            print(f"[{kst()}]   {q_idx + 1}/{n_q} query 처리")

    import pandas as pd
    df = pd.DataFrame(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"estimates_{dataset}_sf{sf}.parquet"
    df.to_parquet(out, index=False)
    print(f"[{kst()}] saved {out} ({len(df)} rows)")

    # 정합성 표본 — 오프라인 v13 결과와 부호·크기 비교용
    if len(df):
        smp = df.groupby(["sel", "method"])[
            ["est_b1", "est_caseA", "est_caseB", "true_card"]].mean()
        print(f"\n=== (sel × method) 평균 추정치 — v13 대조용 ===\n{smp.round(1)}")
        # CaseA_mean·CaseC 는 (sel, query_id) 단위로 unique — sel 단위 평균 표시
        smp2 = df.groupby(["sel"])[
            ["est_b1", "est_caseA_mean", "est_caseC", "true_card"]].mean()
        print(f"\n=== (sel) method-agnostic 추정치 (CaseA_mean·CaseC — v14 대조용) ===\n{smp2.round(1)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="VAQ 카디널리티 추정치 생성 (Phase 1)")
    ap.add_argument("--dataset",
                    choices=["DEEP", "SIFT", "SSN", "WIKI", "YFCC",
                             "DEEP_SIFT", "DEEP_WIKI", "DEEP_YFCC"],
                    default="DEEP")
    ap.add_argument("--sf", type=int, default=10)
    ap.add_argument("--n-qvec", type=int, default=30, help="query pool 앞 N개 벡터")
    ap.add_argument("--methods", nargs="+", default=list(DEFAULT_CASEB_METHODS),
                    help="CaseB 결합 method 목록 (기본: 강한 13종)")
    ap.add_argument("--est-trials", type=int, default=EST_TRIALS)
    ap.add_argument("--output", type=Path, default=Path("latency"))
    args = ap.parse_args()

    if not SERVER:
        print("서버 전용 스크립트 — 165.132.140.240 capstone2026에서 실행.")
        print("로컬에선 import 검증·--help 만 가능 (벡터 fetch에 PostgreSQL 필요).")
        return

    gen_estimates(args.dataset, args.sf, args.n_qvec, args.methods,
                  args.est_trials, args.output)


if __name__ == "__main__":
    main()
