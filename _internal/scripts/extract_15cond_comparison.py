#!/usr/bin/env python3
"""15-condition latency × 정답plan 회복 비교 — baseline + B1 + 13 method × 12 cell.

DEEP sf=10 sel=0.001 phase2 (정본 핵심 12 cell) raw JSON 에서:
  · 각 cell × condition trimmed-mean latency
  · plan vs oracle plan 일치 여부 (정답plan 회복)
  · CaseB method 의 q_error
를 추출하고, condition 단위로 집계한다.

조건 라벨:
  · baseline   = 기본 pgvector (주입 없음, 33.3% 고정 selectivity)
  · B1         = 1-stage Bernoulli (Exqutor §V-B 논문 그대로)
  · oracle     = true_card 주입 (정답 plan 정의 기준)
  · 13 method  = CaseB:method (B1 + method 산술평균 결합)

산출:
  1. 집계 표 (15 row + oracle = 16) — md + csv
  2. per-cell breakdown (12 × 16 = 192 row) — csv

  실행:
    python3 _internal/scripts/extract_15cond_comparison.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from analyze_latency import (  # noqa: E402
    load_results, plan_signature, _variant_label, cell_label,
)

REPO = SCRIPTS.parent.parent
PHASE2 = REPO / "_internal/cache/rq3/latency/phase2"
OUT_DIR = PHASE2

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

NODE_ABBR = {
    "Nested Loop": "NL", "Hash Join": "HJ", "Merge Join": "MJ",
    "Index Scan": "IS", "Index Only Scan": "IOS", "Seq Scan": "Seq",
    "Bitmap Heap Scan": "BHS", "Bitmap Index Scan": "BIS",
    "Gather Merge": "Gather", "Gather": "Gather",
    "Sort": "Sort", "Hash": "Hash",
    "Aggregate": "Agg", "GroupAggregate": "GAgg", "HashAggregate": "HAgg",
    "Materialize": "Mat", "Memoize": "Memo", "Limit": "Lim", "Append": "App",
}


def plan_short(plan_json, maxlen: int = 70) -> str:
    sig = plan_signature(plan_json)
    short = [NODE_ABBR.get(t, t) for t in sig]
    out = " > ".join(short)
    return out if len(out) <= maxlen else (out[: maxlen - 1] + "…")


def condition_label(vlabel: str) -> str:
    if vlabel in ("baseline", "B1", "oracle"):
        return vlabel
    if vlabel.startswith("CaseB:"):
        m = vlabel.split(":", 1)[1]
        return RENAME.get(m, m)
    return vlabel


def main():
    ts = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d_%H%M%S")
    print(f"[info] timestamp: {ts}")

    results = load_results(PHASE2)
    print(f"[info] cells loaded: {len(results)}")

    per_cell_rows = []
    for r in results:
        by = {_variant_label(v): v for v in r["variants"]}
        oracle_v = by.get("oracle")
        if oracle_v is None:
            print(f"[warn] cell {cell_label(r)}: missing oracle, skip")
            continue
        oracle_sig = plan_signature(oracle_v["plan_json"])
        cell = cell_label(r)
        true_card = r.get("true_card")

        for vlabel, v in by.items():
            cond = condition_label(vlabel)
            sig = plan_signature(v["plan_json"])
            per_cell_rows.append({
                "cell": cell,
                "condition": cond,
                "raw_label": vlabel,
                "exec_ms_trimmed": v.get("exec_ms_trimmed"),
                "exec_ms_median": v.get("exec_ms_median"),
                "plan_short": plan_short(v["plan_json"]),
                "recovers_oracle": (sig == oracle_sig),
                "q_error": v.get("q_error"),
                "injected_card": v.get("injected_card"),
                "true_card": true_card,
                "injection_fired": v.get("injection_fired", False),
            })

    per_cell_df = pd.DataFrame(per_cell_rows)
    print(f"[info] per-cell rows: {len(per_cell_df)} (expected 12 × 16 = 192)")

    # ---- 집계 ----
    agg = (
        per_cell_df.groupby("condition", as_index=False, sort=False)
        .agg(
            n_cells=("cell", "nunique"),
            ms_median=("exec_ms_trimmed", "median"),
            ms_mean=("exec_ms_trimmed", "mean"),
            ms_min=("exec_ms_trimmed", "min"),
            ms_max=("exec_ms_trimmed", "max"),
            plan_ok=("recovers_oracle", "sum"),
            plan_ok_pct=("recovers_oracle", lambda s: 100.0 * s.mean()),
            q_error_median=("q_error", "median"),
        )
    )

    # round
    for c in ["ms_median", "ms_mean", "ms_min", "ms_max"]:
        agg[c] = agg[c].round(1)
    agg["plan_ok_pct"] = agg["plan_ok_pct"].round(1)
    agg["q_error_median"] = agg["q_error_median"].round(3)

    # 정렬: anchor 3 (baseline → B1 → oracle) → 13 method (ms_median asc)
    ANCHOR_ORDER = ["baseline", "B1", "oracle"]
    anchor = agg[agg["condition"].isin(ANCHOR_ORDER)].copy()
    anchor["_ord"] = anchor["condition"].map({c: i for i, c in enumerate(ANCHOR_ORDER)})
    anchor = anchor.sort_values("_ord").drop(columns=["_ord"])
    method = agg[~agg["condition"].isin(ANCHOR_ORDER)].sort_values("ms_median")
    agg = pd.concat([anchor, method], ignore_index=True)

    # baseline 대비 speedup·delta
    base_ms = anchor[anchor["condition"] == "baseline"]["ms_median"].iloc[0]
    agg["vs_base_pct"] = ((agg["ms_median"] - base_ms) / base_ms * 100).round(2)

    # ---- 출력 ----
    csv_path = OUT_DIR / f"table_15cond_{ts}.csv"
    md_path = OUT_DIR / f"table_15cond_{ts}.md"
    per_cell_csv = OUT_DIR / f"table_15cond_percell_{ts}.csv"

    agg.to_csv(csv_path, index=False)
    per_cell_df.to_csv(per_cell_csv, index=False)

    md_lines = [
        f"# 15-condition latency × 정답plan 회복 비교 — phase2 DEEP sf=10 sel=0.001 12 cell",
        "",
        f"_생성_: {ts} KST · 스크립트 `_internal/scripts/extract_15cond_comparison.py`",
        f"_데이터_: `_internal/cache/rq3/latency/phase2/latency_*.json` (12 cell × 16 variant = 192 측정)",
        "",
        "## 조건 정의",
        "",
        "| 조건 | 의미 |",
        "|---|---|",
        "| `baseline` | **기본 pgvector** — 카디널리티 주입 없음 (33.3% 고정 selectivity, default plan) |",
        "| `B1` | Exqutor §V-B 1-stage Bernoulli (논문 그대로 — 본 연구의 대조군) |",
        "| `oracle` | `true_card` 주입 — **정답 plan 정의 기준** |",
        "| 13 method | CaseB:method = `(B1_est + method_est) / 2` 결합 추정 주입 |",
        "",
        "## 표 — 조건별 12 cell aggregate",
        "",
        "- `ms_*` = end-to-end exec time (trimmed mean, ms) — pgvector Exqutor-패치 엔진 측정",
        "- `plan_ok_pct` = (cell 중 plan 시그니처 = oracle plan 시그니처) 비율 (= 정답plan 회복률)",
        "- `vs_base_pct` = baseline median 대비 (`+` = baseline 보다 느림, `-` = baseline 보다 빠름)",
        "- `q_error_median` = max(injected/true, true/injected) — `baseline·oracle` 은 정의상 1.0 또는 NaN",
        "",
        agg.to_markdown(index=False, floatfmt=".1f"),
        "",
    ]
    md_path.write_text("\n".join(md_lines) + "\n")

    print(f"[ok] aggregated csv: {csv_path}")
    print(f"[ok] aggregated md: {md_path}")
    print(f"[ok] per-cell csv: {per_cell_csv}")

    print("\n=== 15-condition 집계 ===")
    print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
