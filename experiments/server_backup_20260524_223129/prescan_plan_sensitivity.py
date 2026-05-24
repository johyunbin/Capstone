#!/usr/bin/env python3
"""Phase 0 plan 민감도 prescan — 24 cell 빠른 스크리닝 + go/no-go 게이트.

「엔진 적용 검증」 Phase 0. 8 TPC-H 쿼리 × DEEP × sf10 × sel{0.001,0.01,0.1} × qid=0
에 대해 baseline·B1·oracle 3조건의 pass-2 실행 플랜을 캡처하고 injection_fired·플랜
변화 패턴으로 셀을 분류한다 — Phase 2 매트릭스 코어 cell 선정의 게이트.

cell 분류:
  core             baseline ≠ oracle, B1 ≠ oracle, injection_fired=True
                   → Phase 2 매트릭스 1순위 (CaseB 검증 의의 있음)
  plan-saturated   B1 = oracle ≠ baseline, injection_fired=True
                   → B1 만으로도 oracle 플랜에 도달 → CaseB 추가 정확도 무용
  plan-invariant   oracle = baseline, injection_fired=True
                   → 카디널리티 둔감 cell (제외)
  injection-MISS   injection_fired=False
                   → 벡터 테이블이 pkey IndexScan 경로 (제외)
  capture-fail     baseline 또는 oracle 캡처 실패 (B1 만 실패 시 보수적으로 core)

go/no-go:
  core ≥ 8/24      → GO Phase 2 전체 매트릭스
  core 3-7/24      → GO 축소 Phase 2 (core cell 만)
  core ≤ 2/24      → NO-GO (qid 1·2 확장 fallback 권장)

★ harness library 재사용 — measure_latency_realengine 의 (private convention)
   `_capture_plan` 을 직접 import 한다. 별도 세션·auto_explain·injection_fired
   캡처를 그대로 활용 (harness 모듈 import-time side effect 없음).

서버 실행 (전체 24 cell):
    python3 prescan_plan_sensitivity.py \\
        --estimates latency/estimates_DEEP_sf10.parquet \\
        --output latency/prescan --statement-timeout 600s

서버 sanity (1 cell):
    python3 prescan_plan_sensitivity.py --queries q3 --sels 0.01 \\
        --estimates latency/estimates_DEEP_sf10.parquet --output latency/prescan

로컬 dry-run (PG 없이):
    python3 prescan_plan_sensitivity.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# harness 모듈 import — 같은 디렉토리 (repo 로컬 + 서버 cache/rq3 동일 배치)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from measure_latency_realengine import (   # noqa: E402
    TPC_H_QUERIES, _capture_plan, build_vaq_sql, gucs_for, kst,
    load_estimates, temp_view_ddls,
)

DEFAULT_SELS = (0.001, 0.01, 0.10)


# ---------------------------------------------------------------------------
# 플랜 시그니처 + 분류
# ---------------------------------------------------------------------------

def plan_signature_v2(plan):
    """pre-order (node_type, relation_or_index, join_type) tuple.

    analyze_latency.plan_signature 의 강화판 — Hash Join build/probe swap·
    SeqScan↔IndexScan 분간. 빈 plan(캡처 실패)은 빈 tuple.
    """
    if not plan:
        return ()
    rel = plan.get("Relation Name") or plan.get("Index Name") or ""
    join = plan.get("Join Type", "")
    out = [(plan.get("Node Type", "?"), rel, join)]
    for child in plan.get("Plans", []):
        out.extend(plan_signature_v2(child))
    return tuple(out)


def classify(oracle_fired, base_sig, b1_sig, orcl_sig):
    """5-way 분류. baseline·oracle 둘 다 캡처돼야 의미 있는 분류 가능."""
    if not base_sig or not orcl_sig:
        return "capture-fail"
    if not oracle_fired:
        return "injection-MISS"
    if orcl_sig == base_sig:
        return "plan-invariant"
    if b1_sig and b1_sig == orcl_sig:
        return "plan-saturated"
    return "core"


def _go_no_go(class_counts, total):
    core = class_counts.get("core", 0)
    if core >= 8:
        decision = "GO Phase 2 (전체 매트릭스)"
    elif core >= 3:
        decision = "GO 축소 Phase 2 (core cell 만)"
    else:
        decision = "NO-GO (qid 1·2 확장 fallback 권장)"
    return {"core_count": core, "total": total, "decision": decision}


# ---------------------------------------------------------------------------
# 셀 prescan (서버 — psycopg 필요)
# ---------------------------------------------------------------------------

def prescan_cell(query, dataset, sf, sel, qid, estimates_path, statement_timeout):
    """1 cell 의 3 condition plan 캡처 + 분류."""
    qvec, D, true_card, est_b1, _ = load_estimates(
        estimates_path, dataset, sf, sel, qid, methods=[])
    view_ddls = temp_view_ddls(dataset, sf)

    def _cap(condition, inj):
        return _capture_plan(query, qvec, D, view_ddls, condition, inj, statement_timeout)

    base = _cap("baseline", None)
    b1 = _cap("B1", est_b1)
    orcl = _cap("oracle", true_card)
    base_sig = plan_signature_v2(base["plan_json"])
    b1_sig = plan_signature_v2(b1["plan_json"])
    orcl_sig = plan_signature_v2(orcl["plan_json"])
    klass = classify(orcl["injection_fired"], base_sig, b1_sig, orcl_sig)

    def _v(cap, sig):
        return {"plan_json": cap["plan_json"], "sig": list(sig),
                "fired": cap["injection_fired"],
                "card_seen": cap["injected_card_seen"],
                "plan_dur_ms": cap["plan_duration_ms"]}

    return {
        "query": query, "dataset": dataset, "sf": sf, "sel": sel, "qid": qid,
        "D": D, "true_card": true_card, "est_b1": est_b1,
        "baseline": _v(base, base_sig),
        "B1": _v(b1, b1_sig),
        "oracle": _v(orcl, orcl_sig),
        "classification": klass,
        "kst": kst(),
    }


# ---------------------------------------------------------------------------
# 콘솔 출력
# ---------------------------------------------------------------------------

def _print_table(rows):
    hdr = (f"{'cell':<32}{'base|n':>8}{'B1|n':>8}{'orcl|n':>8}"
           f"  {'B1=':<6}{'orcl=':<8}{'fired':>6}{'class':<18}{'★':>3}")
    print("\n" + hdr + "\n" + "-" * 100)
    for r in rows:
        cell = f"{r['query']} sel{r['sel']:g} qid{r['qid']}"
        bs = tuple(r['baseline']['sig']) if 'baseline' in r else ()
        b1s = tuple(r['B1']['sig']) if 'B1' in r else ()
        os_ = tuple(r['oracle']['sig']) if 'oracle' in r else ()
        b1_eq = "base" if b1s and b1s == bs else ("orcl" if b1s and b1s == os_ else "—")
        orcl_eq = "base" if os_ and os_ == bs else ("≠base" if os_ else "—")
        fired = ("T" if r.get('oracle', {}).get('fired') else "F") if 'oracle' in r else "—"
        star = "★" if r.get("classification") == "core" else ""
        print(f"{cell:<32}{len(bs):>8}{len(b1s):>8}{len(os_):>8}"
              f"  {b1_eq:<6}{orcl_eq:<8}{fired:>6}{r.get('classification','?'):<18}{star:>3}")
    print("-" * 100)


# ---------------------------------------------------------------------------
# 로컬 dry-run
# ---------------------------------------------------------------------------

def _dry_run():
    """PG 없이 plan_signature_v2·classify·SQL 변환·GUC·VIEW DDL·decision 검증."""
    import numpy as np
    print(f"=== prescan dry-run ({kst()}) ===\n")

    print("--- plan_signature_v2 unit ---")
    p_hash = {"Node Type": "Hash Join", "Plans": [
        {"Node Type": "Seq Scan", "Relation Name": "partsupp_deep_10", "Plans": []},
        {"Node Type": "Hash", "Plans": [
            {"Node Type": "Seq Scan", "Relation Name": "lineitem", "Plans": []}]}]}
    p_nl = {"Node Type": "Nested Loop", "Join Type": "Inner", "Plans": [
        {"Node Type": "Seq Scan", "Relation Name": "partsupp_deep_10", "Plans": []},
        {"Node Type": "Index Scan", "Index Name": "lineitem_pkey", "Plans": []}]}
    sig_h, sig_nl = plan_signature_v2(p_hash), plan_signature_v2(p_nl)
    assert sig_h != sig_nl and len(sig_h) == 4 and len(sig_nl) == 3
    print(f"  hash sig (n={len(sig_h)}): {sig_h}")
    print(f"  nl   sig (n={len(sig_nl)}): {sig_nl}")
    # Hash Join build/probe swap 분간 검증
    p_hash_swap = {"Node Type": "Hash Join", "Plans": [
        {"Node Type": "Hash", "Plans": [
            {"Node Type": "Seq Scan", "Relation Name": "lineitem", "Plans": []}]},
        {"Node Type": "Seq Scan", "Relation Name": "partsupp_deep_10", "Plans": []}]}
    assert plan_signature_v2(p_hash_swap) != sig_h, "build/probe swap 미분간"
    print(f"  ✓ Hash build/probe swap 분간 / Seq vs Index Scan 분간")

    print("\n--- classify 6 branches ---")
    cases = [
        (True, (), (1,), (1,), "capture-fail"),       # base 없음
        (True, (1,), (1,), (), "capture-fail"),       # orcl 없음
        (False, (1,), (1,), (1,), "injection-MISS"),  # fired False
        (True, (1,), (1,), (1,), "plan-invariant"),   # orcl=base
        (True, (1,), (2,), (2,), "plan-saturated"),   # B1=orcl≠base
        (True, (1,), (3,), (2,), "core"),             # 셋 다 다름
        (True, (1,), (), (2,), "core"),               # B1 missing → 보수적 core
    ]
    for fired, b, b1, o, want in cases:
        got = classify(fired, b, b1, o)
        assert got == want, f"classify({fired},{b},{b1},{o}) = {got} != {want}"
        print(f"  ✓ fired={fired} base={b} B1={b1} orcl={o} → {got}")

    print("\n--- 8쿼리 × 3 sel × 3 condition 변환 검증 ---")
    qvec = np.random.default_rng(0).standard_normal(96).astype(np.float32)
    n_ok = 0
    for q in TPC_H_QUERIES:
        for sel in DEFAULT_SELS:
            D = 0.5 + sel
            sql = build_vaq_sql(q, qvec, D)
            assert "'image_embedding'" not in sql
            assert "EXPLAIN" not in sql.upper()
            assert "/*+" not in sql
            for cond, inj in [("baseline", None), ("B1", 12345.0), ("oracle", 80000.0)]:
                gs = gucs_for(cond, inj)
                assert any("update_sample_size" in g for g in gs)
                if cond == "baseline":
                    assert any("disable_estimation = on" in g for g in gs)
                else:
                    assert any("injected_card" in g for g in gs)
                n_ok += 1
    print(f"  ✓ {n_ok} 변환 통과 (placeholder·EXPLAIN·hint 잔여 0)")

    ddls = temp_view_ddls("DEEP", 10)
    assert any("partsupp_deep AS SELECT * FROM partsupp_deep_10" in d for d in ddls)
    assert len(ddls) == 8
    print(f"  ✓ DEEP sf10 임시 VIEW DDL 8개 (partsupp_deep + base 7종)")

    print("\n--- go/no-go decision ---")
    for core in [0, 2, 3, 7, 8, 24]:
        cc = Counter({"core": core, "plan-invariant": 24 - core})
        d = _go_no_go(cc, 24)
        print(f"  core={core:>2}/24 → {d['decision']}")

    print("\n✓ dry-run 통과 — plan_signature_v2·classify·SQL 변환·GUC·VIEW DDL·decision 정상")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Phase 0 plan 민감도 prescan")
    ap.add_argument("--estimates", type=Path,
                    help="gen_latency_estimates.py 산출 parquet (real run 필수)")
    ap.add_argument("--dataset", choices=["DEEP", "SIFT", "SSN"], default="DEEP")
    ap.add_argument("--sf", type=int, default=10)
    ap.add_argument("--query-id", type=int, default=0)
    ap.add_argument("--queries", nargs="+", default=list(TPC_H_QUERIES),
                    choices=list(TPC_H_QUERIES))
    ap.add_argument("--sels", nargs="+", type=float, default=list(DEFAULT_SELS))
    ap.add_argument("--statement-timeout", default="600s")
    ap.add_argument("--output", type=Path, default=Path("latency/prescan"))
    ap.add_argument("--dry-run", action="store_true",
                    help="PG 없이 logic 검증")
    args = ap.parse_args()

    if args.dry_run:
        _dry_run()
        return

    if not args.estimates:
        ap.error("--estimates 필요 (real run) — 또는 --dry-run")

    args.output.mkdir(parents=True, exist_ok=True)
    cells = [(q, sel) for q in args.queries for sel in args.sels]
    print(f"[{kst()}] prescan 시작 — {len(cells)} cell × 3 condition "
          f"({args.dataset} sf{args.sf} qid{args.query_id}, "
          f"timeout={args.statement_timeout})")

    rows = []
    for idx, (q, sel) in enumerate(cells, 1):
        print(f"\n[{kst()}] ({idx}/{len(cells)}) {q} sel{sel:g} qid{args.query_id}")
        try:
            row = prescan_cell(q, args.dataset, args.sf, sel, args.query_id,
                               args.estimates, args.statement_timeout)
        except Exception as e:
            print(f"  ! {type(e).__name__}: {str(e)[:140]}")
            row = {"query": q, "dataset": args.dataset, "sf": args.sf, "sel": sel,
                   "qid": args.query_id, "classification": "capture-fail",
                   "error": f"{type(e).__name__}: {e}", "kst": kst()}
        rows.append(row)
        # 셀별 JSON 즉시 저장 — 중단해도 부분 결과 보존
        cell_path = args.output / (f"cell_{q}_{args.dataset}_sf{args.sf}"
                                   f"_sel{sel}_qid{args.query_id}.json")
        cell_path.write_text(json.dumps(row, indent=2, default=str))
        klass = row.get("classification", "?")
        b_fired = row.get("baseline", {}).get("fired")
        o_fired = row.get("oracle", {}).get("fired")
        print(f"  → {klass}{'  ★' if klass == 'core' else ''} "
              f"(base_fired={b_fired} oracle_fired={o_fired})")

    # 총괄
    class_counts = Counter(r.get("classification", "?") for r in rows)
    decision = _go_no_go(class_counts, len(rows))
    summary = {
        "kst": kst(), "dataset": args.dataset, "sf": args.sf,
        "query_id": args.query_id, "queries": args.queries, "sels": args.sels,
        "statement_timeout": args.statement_timeout,
        "n_cells": len(rows), "class_counts": dict(class_counts),
        "decision": decision,
        "core_cells": [(r["query"], r["sel"]) for r in rows
                       if r.get("classification") == "core"],
        "saturated_cells": [(r["query"], r["sel"]) for r in rows
                            if r.get("classification") == "plan-saturated"],
        "invariant_cells": [(r["query"], r["sel"]) for r in rows
                            if r.get("classification") == "plan-invariant"],
        "miss_cells": [(r["query"], r["sel"]) for r in rows
                       if r.get("classification") == "injection-MISS"],
        "rows": rows,
    }
    summary_path = args.output / "prescan_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))

    _print_table(rows)
    print(f"\n=== 분류 통계 ===")
    for k in ["core", "plan-saturated", "plan-invariant",
              "injection-MISS", "capture-fail"]:
        print(f"  {k:<18}{class_counts.get(k, 0):>3}/{len(rows)}")
    print(f"\n=== go/no-go decision ===")
    print(f"  core: {decision['core_count']}/{decision['total']} "
          f"→ {decision['decision']}")
    print(f"\n저장: {summary_path}")


if __name__ == "__main__":
    main()
