#!/usr/bin/env python3
"""주입 카디널리티 sweep — latency-vs-injected-card 곡선 측정 (Phase 3a).

measure_latency_realengine.py 의 빌딩블록을 재사용해, 한 cell 에 대해 벡터 술어
카디널리티 주입값을 그리드로 sweep 한다. baseline + B1 + oracle + 그리드(implied
selectivity 로그 간격) 를 한 세션 흐름에서 측정한다.

진단 맥락 — 기존 측정은 B1/CaseB/oracle 3점만 찍어 'condition 무관'을 관찰했다.
sweep 는 카디널리티 축 전체(매우 선택적 → pgvector 기본값 33%)를 훑어:
  · latency 가 어느 주입값에서 계단처럼 뒤집히나 (plan-flip cliff)
  · B1 의 q-error 분포가 그 cliff 를 넘나드는가
를 본다. cliff 를 넘나들면 CaseB 이득 구간이 존재, 아니면 한계 확정 — 어느 쪽이든 결론.

★ 측정은 sequential (latency 격리). 그리드 점은 cell 의 true_card 와 실제 행수에서
  implied_sel × table_rows 로 산출 — true_card 만 있으면 되고 추정 파이프라인 불필요.

서버 실행:
    python3 measure_card_sweep.py --query q3 --dataset DEEP --sf 10 --sel 0.001 \\
        --query-id 0 --estimates latency/estimates_DEEP_sf10.parquet \\
        --output latency/sweep/

로컬 dry-run (서버 미접속 — 그리드·GUC·SQL 검증):
    python3 measure_card_sweep.py --query q3 --dataset DEEP --sf 10 --dry-run
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path

import numpy as np

# measure_latency_realengine.py 빌딩블록 재사용 (같은 디렉토리)
from measure_latency_realengine import (
    DS_DIM, MIN_INJECT, TPC_H_QUERIES,
    _capture_plan, _connect, _iqr, _run_timed, _trimmed_mean,
    build_vaq_sql, kst, load_estimates, temp_view_ddls, vec_table_name,
)

# implied selectivity 그리드 — 매우 선택적(0.0001) → pgvector 기본값(0.333) 너머(0.60)
SWEEP_IMPLIED_SEL = (
    0.0001, 0.0003, 0.001, 0.003, 0.006, 0.01, 0.02, 0.04,
    0.08, 0.12, 0.20, 0.333, 0.45, 0.60,
)


def get_table_rows(vec_table: str) -> int:
    """벡터 테이블 실제 행수 — 그리드 산출용 (count(*) 1회, 이후 캐시)."""
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT count(*) FROM {vec_table}")
        row = cur.fetchone()
        return int(row[0]) if row else 0


def build_sweep_variants(true_card: float, est_b1: float, table_rows: int):
    """sweep variant 목록 — (condition, label, injected_card, implied_sel).

    baseline(주입X) + B1 + oracle + implied_sel 그리드. 그리드와 B1/oracle 의
    injected_card 가 우연히 겹쳐도 그대로 둔다(중복은 분석서 dedup).
    """
    variants = [
        ("baseline", "baseline", None, None),
        ("B1", "B1", est_b1, (est_b1 / table_rows) if table_rows else None),
        ("oracle", "oracle", true_card,
         (true_card / table_rows) if table_rows else None),
    ]
    for isel in SWEEP_IMPLIED_SEL:
        card = max(float(round(isel * table_rows)), MIN_INJECT)
        variants.append(("sweep", f"s{isel:g}", card, isel))
    return variants


def measure_sweep_cell(query, dataset, sf, sel, query_id, qvec, D, true_card,
                       est_b1, caseb_by_method, *, n_timed, n_warmup,
                       statement_timeout, analyze_plans=False, seed=20260523) -> dict:
    """한 cell 의 카디널리티 sweep 측정 — 전 그리드 variant.

    measure_latency_realengine.measure_cell 과 동일한 측정 규약:
    플랜 캡처(variant 1회) 후, 매 rep 마다 variant 순서를 fixed-seed 셔플해
    인접 측정(matched). latency 격리를 위해 단일 연결 sequential.
    """
    vec_tbl = vec_table_name(dataset, sf)
    table_rows = get_table_rows(vec_tbl)
    print(f"[{kst()}] {vec_tbl}: table_rows={table_rows:,} "
          f"true_card={true_card:,.0f} (actual_sel≈{true_card/table_rows:.5f})")

    sql = build_vaq_sql(query, qvec, D)
    view_ddls = temp_view_ddls(dataset, sf)
    variants = build_sweep_variants(true_card, est_b1, table_rows)
    keys = [(c, lab) for (c, lab, _, _) in variants]
    inj_by_key = {(c, lab): inj for (c, lab, inj, _) in variants}

    # --- 플랜 캡처 (variant 당 1회) ---
    captured: dict[tuple, dict] = {}
    for (c, lab, inj, _isel) in variants:
        captured[(c, lab)] = _capture_plan(query, qvec, D, view_ddls, c, inj,
                                           statement_timeout, analyze=analyze_plans)
        cap = captured[(c, lab)]
        print(f"[{kst()}]   plan-capture {lab:>10}: inj={inj} "
              f"fired={cap['injection_fired']} seen={cap['injected_card_seen']}")

    # --- timed 반복 (sequential, fixed-seed shuffle) ---
    samples: dict[tuple, list[float]] = {k: [] for k in keys}
    timeouts: dict[tuple, int] = {k: 0 for k in keys}
    rng = random.Random(seed)
    for rep in range(n_warmup + n_timed):
        order = keys[:]
        rng.shuffle(order)
        for k in order:
            c, _lab = k
            ms = _run_timed(sql, view_ddls, c, inj_by_key[k], statement_timeout)
            if rep >= n_warmup:
                if ms is None:
                    timeouts[k] += 1
                else:
                    samples[k].append(ms)
        print(f"[{kst()}]   rep {rep + 1}/{n_warmup + n_timed} 완료")

    # --- 집계 ---
    out_variants = []
    for (c, lab, inj, isel) in variants:
        k = (c, lab)
        vals = samples[k]
        cap = captured[k]
        qerr = None
        if inj is not None and true_card and inj > 0:
            qerr = max(inj / true_card, true_card / inj)
        out_variants.append({
            "condition": c, "label": lab, "method": (None if c != "sweep" else lab),
            "implied_sel": isel, "injected_card": inj, "q_error": qerr,
            "exec_ms": vals, "n_timeout": timeouts[k],
            "exec_ms_trimmed": _trimmed_mean(vals),
            "exec_ms_median": (statistics.median(vals) if vals else None),
            "exec_ms_iqr": _iqr(vals),
            "plan_json": cap["plan_json"],
            "plan_duration_ms": cap["plan_duration_ms"],
            "injection_fired": cap["injection_fired"],
            "injected_card_seen": cap["injected_card_seen"],
        })
    return {
        "family": "tpc_h", "kind": "card_sweep", "query": query, "dataset": dataset,
        "sf": sf, "sel": sel, "query_id": query_id, "D": D, "true_card": true_card,
        "vec_table": vec_tbl, "table_rows": table_rows,
        "est_b1": est_b1, "caseb_ests": caseb_by_method,
        "n_warmup": n_warmup, "n_timed": n_timed,
        "statement_timeout": statement_timeout, "analyze_plans": analyze_plans,
        "variants": out_variants, "kst": kst(),
    }


def _dry_run(args) -> None:
    dim = DS_DIM[args.dataset]
    print(f"=== dry-run: card-sweep {args.query} {args.dataset} sf{args.sf} ===\n")
    print(f"implied_sel 그리드 ({len(SWEEP_IMPLIED_SEL)}점): {SWEEP_IMPLIED_SEL}")
    print("  injected_card = implied_sel × table_rows  (table_rows 는 서버 count(*) 로 확정)")
    print("\n예시 — table_rows=80,000,000 가정 시 injected_card:")
    for isel in SWEEP_IMPLIED_SEL:
        print(f"  implied_sel={isel:<8} → injected_card={int(isel*80_000_000):,}")
    print(f"\nvariant = baseline + B1 + oracle + 그리드 {len(SWEEP_IMPLIED_SEL)} = "
          f"{3 + len(SWEEP_IMPLIED_SEL)}개")
    qvec = np.random.default_rng(0).standard_normal(dim).astype(np.float32)
    sql = build_vaq_sql(args.query, qvec, 0.86)
    assert "'image_embedding'" not in sql and sql.count("::vector") == 2
    print("\n✓ dry-run 통과 — 그리드·SQL 변환 정상 (measure_latency_realengine 빌딩블록 재사용)")


def main() -> None:
    ap = argparse.ArgumentParser(description="주입 카디널리티 sweep 측정")
    ap.add_argument("--query", required=True, choices=TPC_H_QUERIES)
    ap.add_argument("--dataset", default="DEEP",
                    choices=["DEEP", "SIFT", "SSN", "WIKI", "YFCC"])
    ap.add_argument("--sf", type=int, default=10)
    ap.add_argument("--sel", type=float, default=0.001)
    ap.add_argument("--query-id", type=int, default=0)
    ap.add_argument("--estimates", type=Path,
                    help="gen_latency_estimates.py 산출 parquet (qvec·D·true_card·est)")
    ap.add_argument("--methods", nargs="+", default=None,
                    help="caseb_ests 기록용 method 목록 (기본: parquet 의 전 method)")
    ap.add_argument("--n-timed", type=int, default=10)
    ap.add_argument("--n-warmup", type=int, default=1)
    ap.add_argument("--statement-timeout", default="180s")
    ap.add_argument("--analyze-plans", action="store_true",
                    help="플랜 캡처를 EXPLAIN ANALYZE 모드로 (노드별 Actual Total Time)")
    ap.add_argument("--output", type=Path, default=Path("latency/sweep"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        _dry_run(args)
        return
    if not args.estimates:
        ap.error("--estimates 필요 (real run) — 또는 --dry-run")

    from measure_latency_realengine import DEFAULT_CASEB_METHODS
    methods = args.methods or list(DEFAULT_CASEB_METHODS)
    qvec, D, true_card, est_b1, caseb = load_estimates(
        args.estimates, args.dataset, args.sf, args.sel, args.query_id, methods)
    print(f"[{kst()}] sweep cell tpc_h/{args.query} {args.dataset} sf{args.sf} "
          f"sel{args.sel} qid{args.query_id}: D={D:.4f} true={true_card:.0f} "
          f"est_b1={est_b1:.0f}")

    result = measure_sweep_cell(
        args.query, args.dataset, args.sf, args.sel, args.query_id,
        qvec, D, true_card, est_b1, caseb,
        n_timed=args.n_timed, n_warmup=args.n_warmup,
        statement_timeout=args.statement_timeout, analyze_plans=args.analyze_plans)

    args.output.mkdir(parents=True, exist_ok=True)
    out = args.output / (f"sweep_tpc_h_{args.query}_{args.dataset}"
                         f"_sf{args.sf}_sel{args.sel}_qid{args.query_id}.json")
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"[{kst()}] saved {out}")


if __name__ == "__main__":
    main()
