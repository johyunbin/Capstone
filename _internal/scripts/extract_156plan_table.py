#!/usr/bin/env python3
"""156 plan 상세 표 추출 — phase2 DEEP sf=10 12 cell × 13 결합 method.

본 연구의 결합 (CaseB) 13 method × 12 cell = 156 plan 각각을 B1 (베이스라인) 과
정확하게 비교한 표를 csv + md 두 형식으로 산출한다.

산출 컬럼:
  cell · method (정정 후 명칭) · B1_plan (short) · CaseB_plan (short) · plan_same
  · B1_ms (trim mean) · CaseB_ms (trim mean) · delta_pct
  · B1_recovers_oracle · CaseB_recovers_oracle
  · CaseB_injected_card · true_card · q_error · injection_fired
  · p_holm · hedges_g (paired_stats.csv 에서 join)

  실행:
    python3 _internal/scripts/extract_156plan_table.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd

# analyze_latency.py 같은 디렉토리 — import 위해 path 추가
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from analyze_latency import (  # noqa: E402
    load_results, plan_signature, _variant_label, cell_label
)

REPO = SCRIPTS.parent.parent
PHASE2 = REPO / "_internal/cache/rq3/latency/phase2"
PAIRED = PHASE2 / "figures/paired_stats.csv"

# 정정 후 명칭 매핑 (본 연구 정정 8 — handoff 20260524_233327 §2.3 carry)
RENAME = {
    "hilbert_real": "pca2d_hilbert_xy2d",
    "skilling_hilbert": "pca4_skilling_hilbert_approx",
    "zorder_morton": "pca2d_zorder_morton",
    "mhist2": "pca2d_equi_depth_grid",
    "hyperloglog": "md5_prefix_hash_bucket",
    "lavallee_hidiroglou": "takeall_cumsqrtf",
    "rabitq_strat": "rabitq_1bit_bucket",
    "kmeans_neyman": "kmeans_cluster_only",
}

# Node Type 사람-읽기용 약어
NODE_ABBR = {
    "Nested Loop": "NL",
    "Hash Join": "HJ",
    "Merge Join": "MJ",
    "Index Scan": "IS",
    "Index Only Scan": "IOS",
    "Seq Scan": "Seq",
    "Bitmap Heap Scan": "BHS",
    "Bitmap Index Scan": "BIS",
    "Gather Merge": "Gather",
    "Gather": "Gather",
    "Sort": "Sort",
    "Hash": "Hash",
    "Aggregate": "Agg",
    "GroupAggregate": "GAgg",
    "HashAggregate": "HAgg",
    "Materialize": "Mat",
    "Memoize": "Memo",
    "Limit": "Lim",
    "Append": "App",
}


def plan_short(plan_json: dict, maxlen: int = 80) -> str:
    sig = plan_signature(plan_json)
    short = [NODE_ABBR.get(t, t) for t in sig]
    out = " > ".join(short)
    return out if len(out) <= maxlen else (out[: maxlen - 1] + "…")


def main():
    ts = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d_%H%M%S")
    print(f"[info] timestamp: {ts}")

    results = load_results(PHASE2)
    print(f"[info] cells loaded: {len(results)}")
    if len(results) != 12:
        print(f"[warn] expected 12 cells (DEEP sf=10 sel=0.001 × 4 query × 3 qid), got {len(results)}")

    paired = pd.read_csv(PAIRED)
    print(f"[info] paired_stats rows: {len(paired)}")

    rows = []
    for r in results:
        by = {_variant_label(v): v for v in r["variants"]}
        b1 = by.get("B1")
        oracle = by.get("oracle")
        if b1 is None or oracle is None:
            print(f"[warn] cell {cell_label(r)}: missing B1 or oracle")
            continue
        b1_sig = plan_signature(b1["plan_json"])
        oracle_sig = plan_signature(oracle["plan_json"])
        b1_ms = b1.get("exec_ms_trimmed")
        cell = cell_label(r)

        # CaseB:* 만 추출
        for vlabel, v in by.items():
            if not vlabel.startswith("CaseB:"):
                continue
            method_raw = vlabel.split(":", 1)[1]
            method = RENAME.get(method_raw, method_raw)
            cb_sig = plan_signature(v["plan_json"])
            cb_ms = v.get("exec_ms_trimmed")
            delta_pct = ((cb_ms - b1_ms) / b1_ms * 100) if (cb_ms and b1_ms) else None
            rows.append({
                "cell": cell,
                "method": method,
                "method_raw": method_raw,
                "B1_plan": plan_short(b1["plan_json"]),
                "CaseB_plan": plan_short(v["plan_json"]),
                "plan_same": "same" if cb_sig == b1_sig else "diff",
                "B1_ms": round(b1_ms, 1) if b1_ms else None,
                "CaseB_ms": round(cb_ms, 1) if cb_ms else None,
                "delta_pct": round(delta_pct, 2) if delta_pct is not None else None,
                "B1_recovers_oracle": (b1_sig == oracle_sig),
                "CaseB_recovers_oracle": (cb_sig == oracle_sig),
                "true_card": round(r.get("true_card", 0), 1),
                "CaseB_injected_card": (round(v["injected_card"], 1)
                                         if v.get("injected_card") is not None else None),
                "q_error": (round(v["q_error"], 3)
                            if v.get("q_error") is not None else None),
                "injection_fired": v.get("injection_fired", False),
            })

    df = pd.DataFrame(rows)
    print(f"[info] rows extracted: {len(df)} (expected 156)")

    # paired_stats join — p_holm·hedges_g
    if not paired.empty:
        sub = paired[(paired["anchor"] == "B1") &
                     (paired["variant"].str.startswith("CaseB:"))].copy()
        sub["method_raw"] = sub["variant"].str.replace("CaseB:", "", regex=False)
        sub["method"] = sub["method_raw"].map(lambda m: RENAME.get(m, m))
        df = df.merge(
            sub[["cell", "method", "p_holm", "hedges_g", "cliffs_delta"]],
            on=["cell", "method"], how="left"
        )

    # 정렬: cell → 정확도 ranking 기준 method (대신 method 알파벳 정렬 — paper 표 호환)
    df = df.sort_values(["cell", "method"]).reset_index(drop=True)

    out_dir = PHASE2
    csv_path = out_dir / f"table_156plan_{ts}.csv"
    md_path = out_dir / f"table_156plan_{ts}.md"

    df.to_csv(csv_path, index=False)
    print(f"[ok] csv: {csv_path}")

    # md 표 — 컬럼 순서 정리
    md_cols = [
        "cell", "method",
        "B1_plan", "CaseB_plan", "plan_same",
        "B1_ms", "CaseB_ms", "delta_pct",
        "B1_recovers_oracle", "CaseB_recovers_oracle",
        "true_card", "CaseB_injected_card", "q_error", "injection_fired",
        "p_holm", "hedges_g", "cliffs_delta",
    ]
    md_cols = [c for c in md_cols if c in df.columns]
    md_text = df[md_cols].to_markdown(index=False, floatfmt=".3f")
    md_path.write_text(md_text + "\n")
    print(f"[ok] md: {md_path}")

    # 요약 통계 출력
    print("\n=== summary ===")
    print(f"  total rows: {len(df)}")
    print(f"  plan_same: {(df['plan_same'] == 'same').sum()}")
    print(f"  plan_diff: {(df['plan_same'] == 'diff').sum()}")
    print(f"  B1_recovers_oracle (12 cells × 13 = 156 entries): "
          f"{df['B1_recovers_oracle'].sum()}")
    print(f"  CaseB_recovers_oracle: {df['CaseB_recovers_oracle'].sum()} / {len(df)}")
    print(f"  CaseB injection_fired True: {df['injection_fired'].sum()}")
    if "delta_pct" in df.columns:
        print(f"  delta_pct median: {df['delta_pct'].median():.2f}%")
        print(f"  delta_pct |Δ%|<5%: {(df['delta_pct'].abs() < 5).sum()}")


if __name__ == "__main__":
    main()
