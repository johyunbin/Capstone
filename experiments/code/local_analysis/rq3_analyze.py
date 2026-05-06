#!/usr/bin/env python3
"""
rq3_analyze.py — RQ3 per-method 분석 driver (orchestration).

각 RQ3 측정 parquet (e.g., rq3_minibatch.parquet) 회수 직후 1회 실행하여
summary CSV + significance CSV + 4-stage narrative md 산출.

흐름:
  1. RQ3 method parquet 로드 → mode "equal" → method_name 으로 rename
     (단, kde_pilot/distance_shell/importance_sampling 등 monolithic 파일은
      이미 method-named mode 로 저장되어 있어 rename 불필요)
  2. RQ2 alloc parquet 로드 → mode "equal" → "km20" 으로 rename (oracle baseline)
     bernoulli 는 RQ3 method 측정 본 의 것 사용 (동일 조건 측정 → 더 paired-friendly)
  3. recovery_rate.summarize_method() 호출 → dataset × sel cell-level recovery rate
  4. recovery_rate.paired_wilcoxon_with_bh_fdr() 호출 → 다중 비교 BH-FDR
  5. narrative md skeleton 생성 (1줄요약/동기/가설/예상/실제/의의/카톡 §3.2 섹션 포함, 결과 표 자동 채움, 자유 narrative 부분은 placeholder)
  6. CSV + md 를 experiments/results/rq3_agnostic/{method}/ 에 저장

사용:
    python3 experiments/code/local_analysis/rq3_analyze.py \\
        --method minibatch \\
        --rq3-parquet experiments/results/rq3_agnostic/rq3_minibatch.parquet \\
        --rq2-parquet experiments/results/rq2_aware/2026_05_06_alloc/rq2_alloc.parquet

Demo (placeholder data 로 smoke test):
    python3 experiments/code/local_analysis/rq3_analyze.py --demo

서버에서 직접 측정 직후 실행도 가능 (parquet 경로만 맞추면 됨).
"""

from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from recovery_rate import (  # noqa: E402
    DENOM_COLLAPSE_THRESHOLD_PCT,
    paired_wilcoxon_with_bh_fdr,
    summarize_method,
)


REPO_ROOT = Path(__file__).resolve().parents[3]   # capstone/
DEFAULT_OUT_ROOT = REPO_ROOT / "experiments" / "results" / "rq3_agnostic"

# RQ재정립_20260505_2122 §RQ3 — 각 method 의 사전 등록 expected recovery 범위
EXPECTED_RECOVERY = {
    "minibatch": (0.75, 0.95),
    "random_proj": (0.10, 0.40),
    "hilbert": (0.20, 0.60),
    "lsh": (0.30, 0.60),
    "kde_pilot": (0.50, 0.80),
    "distance_shell": (0.25, 0.50),
    "importance_sampling": (0.30, 0.70),
    "is_p50_noclip": (0.30, 0.70),
    "is_p50_clip": (0.30, 0.70),
    "is_p200_noclip": (0.30, 0.70),
    "is_p200_clip": (0.30, 0.70),
}

METHOD_PARADIGM = {
    "minibatch": "Offline (학습 1~5%)",
    "random_proj": "Offline (단순 하한)",
    "hilbert": "Offline (결정론)",
    "lsh": "Offline (확률)",
    "kde_pilot": "Online (정교)",
    "distance_shell": "Online (단순)",
    "importance_sampling": "비분할 (가중치만)",
    "is_p50_noclip": "비분할 (가중치만)",
    "is_p50_clip": "비분할 (가중치만)",
    "is_p200_noclip": "비분할 (가중치만)",
    "is_p200_clip": "비분할 (가중치만)",
}


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")


# ---------------------------------------------------------------------------
# 1. Loader — parquet → long-form df with normalized mode names
# ---------------------------------------------------------------------------

def load_rq3_method(rq3_parquet: Path, method_name: str) -> pd.DataFrame:
    """RQ3 method parquet 로드 → mode "equal" → method_name 으로 rename.

    Monolithic (kde_pilot, distance_shell, importance_sampling) 은 이미
    method-named mode 라 rename 무시. 'bernoulli' mode 는 RANDOM20 baseline.
    """
    df = pd.read_parquet(rq3_parquet)
    if "mode" not in df.columns:
        raise ValueError(f"{rq3_parquet}: 'mode' column 없음")
    if "equal" in df["mode"].unique() and method_name != "equal":
        df = df.copy()
        df["mode"] = df["mode"].replace({"equal": method_name})
    return df


def load_rq2_km20(rq2_parquet: Path) -> pd.DataFrame:
    """RQ2 alloc parquet 로드 → mode "equal" → "km20" 으로 rename.

    KM20 oracle baseline. bernoulli 는 (RANDOM20) 은 RQ3 측정 본 것을 우선 사용
    (동일 측정 조건 paired) — RQ2 의 bernoulli 는 fallback 용.
    """
    df = pd.read_parquet(rq2_parquet)
    if "mode" not in df.columns:
        raise ValueError(f"{rq2_parquet}: 'mode' column 없음")
    keep = df[df["mode"].isin(["equal", "bernoulli"])].copy()
    keep.loc[keep["mode"] == "equal", "mode"] = "km20"
    keep.loc[keep["mode"] == "bernoulli", "mode"] = "rq2_bernoulli"  # ambiguity 방지
    return keep


def build_long_df(
    method_df: pd.DataFrame,
    rq2_km20: pd.DataFrame,
    method_name: str,
) -> pd.DataFrame:
    """method + km20 + bernoulli 통합 long-form df.

    method_df: method_name + bernoulli 포함
    rq2_km20: km20 + rq2_bernoulli 포함 (rq2_bernoulli 는 사용 안 함)
    """
    keep_cols = ["dataset", "mode", "selectivity", "seed", "query_id", "q_error"]
    method_keep = method_df[keep_cols].copy()
    rq2_keep = rq2_km20[rq2_km20["mode"] == "km20"][keep_cols].copy()
    combined = pd.concat([method_keep, rq2_keep], ignore_index=True)
    return combined


# ---------------------------------------------------------------------------
# 2. Demo data — synthetic for smoke test
# ---------------------------------------------------------------------------

def make_demo_data(method_name: str = "demo_method") -> tuple[pd.DataFrame, pd.DataFrame]:
    """2 ds × 5 sel × 5 seed × 100 q × 3 mode synthetic data.

    Mode 별 q_error 분포 (mean 기준):
      bernoulli   → 1.5  (RANDOM20)
      km20        → 1.1  (oracle, 1.0 + small skew)
      method_name → 1.2  (method between random20 and km20)

    selectivity 가 좁을수록 q_error 분산 큼 (실제 패턴 모사).
    """
    rng = np.random.default_rng(0)
    rows = []
    for ds in ["DEEP", "SIFT"]:
        ds_offset = 0.0 if ds == "DEEP" else 0.1   # SIFT 가 약간 더 어렵
        for sel in [0.01, 0.05, 0.10, 0.30, 0.50]:
            sel_scale = 0.5 / max(sel, 0.01)         # 좁을수록 분산↑
            for mode, base in [("bernoulli", 1.5), ("km20", 1.1), (method_name, 1.2)]:
                for seed in [0.1, 0.2, 0.3, 0.4, 0.5]:
                    for qid in range(100):
                        # mode 별 base + selectivity 의존 분산 + ds 페널티
                        val = base + ds_offset + rng.normal(0, sel_scale * 0.1)
                        val = max(val, 1.0)
                        rows.append({
                            "dataset": ds, "mode": mode, "selectivity": sel,
                            "seed": seed, "query_id": qid,
                            "true_card": 100, "est": int(100 * val),
                            "q_error": val,
                        })
    method_df = pd.DataFrame([r for r in rows if r["mode"] != "km20"])
    rq2_km20_df = pd.DataFrame([
        r for r in rows if r["mode"] == "km20"
    ] + [
        {**r, "mode": "rq2_bernoulli"} for r in rows if r["mode"] == "bernoulli"
    ])
    rq2_km20_df.loc[rq2_km20_df["mode"] == "km20", "mode"] = "km20"  # idempotent
    return method_df, rq2_km20_df


# ---------------------------------------------------------------------------
# 3. Narrative md skeleton 생성
# ---------------------------------------------------------------------------

def build_narrative_md(
    method_name: str,
    rq3_parquet: Path | None,
    rq2_parquet: Path | None,
    summary_df: pd.DataFrame,
    sig_df: pd.DataFrame,
    n_total_rows: int,
    elapsed_s: float | None = None,
) -> str:
    """4-stage narrative md skeleton.

    summary_df, sig_df 는 자동 채워짐. 1줄요약/동기/가설/예상/의의 부분은 placeholder.
    """
    paradigm = METHOD_PARADIGM.get(method_name, "?")
    expected = EXPECTED_RECOVERY.get(method_name)
    expected_str = (
        f"recovery_rate {expected[0]*100:.0f}~{expected[1]*100:.0f}%"
        if expected else "recovery_rate ___% (사전 등록 미설정)"
    )

    summary_table = _format_summary_table(summary_df)
    sig_table = _format_significance_table(sig_df)
    headline_metrics = _extract_headlines(summary_df, sig_df, method_name)

    now_hm = datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M")
    elapsed_str = f"{elapsed_s/3600:.1f}h" if elapsed_s else "_h"
    rq3_path_str = str(rq3_parquet) if rq3_parquet else "(미지정)"
    rq2_path_str = str(rq2_parquet) if rq2_parquet else "(미지정)"

    md = (
        f"# 실험 — RQ3 {method_name} ({paradigm})\n\n"
        f"> **분석 시각**: {kst()}\n"
        f"> **마감**: 5/8 (금) 19:00 비대면 회의\n"
        f"> **RQ3 parquet**: `{rq3_path_str}`\n"
        f"> **RQ2 baseline parquet**: `{rq2_path_str}`\n"
        f"> **연관 설계안**: `plans/RQ재정립_20260505_2122.md` v6 (§RQ3)\n"
        f"> **분석 자동 산출**: `experiments/code/local_analysis/rq3_analyze.py`\n"
        f"> **rows**: {n_total_rows} (method + km20 baseline)\n\n"
        f"---\n\n"
        f"## 한 줄 요약\n\n"
        f"`{method_name}` ({paradigm}) 측정 결과, {headline_metrics['overall']}.\n\n"
        f"> _자동 생성된 표 데이터 기반 한 줄 요약. 수동 narrative 가 들어갈 자리 (실험 종료 후 채움)._\n\n"
        f"---\n\n"
        f"## 1. 동기 — 왜 이 실험을 시작했나\n\n"
        f"_Placeholder — 측정 종료 후 채움._\n\n"
        f"{paradigm} 패러다임의 대표 방법인 `{method_name}` 을 측정하여 RQ3 7-way 비교의 한 자리를 채운다. "
        f"KM20 oracle 대비 회수율 (recovery_rate) 을 산출하고, 분포 정보 학습 없이도 (혹은 최소 학습으로) "
        f"RANDOM20 baseline 을 능가하는지를 통계적으로 검증한다.\n\n"
        f"---\n\n"
        f"## 2. 가설 — 확인하고자 한 것\n\n"
        f"**H3-{method_name[0].upper()}**: `{method_name}` recovery_rate 는 {expected_str} 범위. "
        f"KM20 oracle 의 부분적 회수가 가능하면 분포 학습 없이도 의미 있는 분포 인식 효과가 있다는 증거.\n\n"
        f"측정:\n"
        f"- 5 mode (method + km20 + bernoulli) × 2 dataset × 5 sel × 5 seed × 100 query\n"
        f"- paired Wilcoxon (vs bernoulli, vs km20) + BH-FDR 보정\n"
        f"- dataset × sel cell 별 recovery rate (분모 붕괴 시 절대 Q-error fall-back)\n\n"
        f"---\n\n"
        f"## 3. 예상 결과 — 진행 전 기대값\n\n"
        f"{expected_str}. {paradigm} 패러다임의 위치를 고려하면 _placeholder — 사전 등록 narrative 채움._\n\n"
        f"---\n\n"
        f"## 4. 실제 결과 — 측정값\n\n"
        f"### 4.1 Recovery Rate per (dataset × sel)\n\n"
        f"{summary_table}\n\n"
        f"### 4.2 Paired Wilcoxon BH-FDR (treatment vs bernoulli, treatment vs km20)\n\n"
        f"{sig_table}\n\n"
        f"### 4.3 핵심 수치\n\n"
        f"- **Best cell**: {headline_metrics['best']}\n"
        f"- **Worst cell**: {headline_metrics['worst']}\n"
        f"- **Fall-back cell 수** (|KM20−RANDOM20| ≤ 1%p): {headline_metrics['fallback_count']}\n"
        f"- **bernoulli 대비 BH-FDR 유의 cell 수** (α=0.05): {headline_metrics['sig_vs_bern_count']}\n"
        f"- **km20 대비 BH-FDR 유의 cell 수**: {headline_metrics['sig_vs_km_count']}\n\n"
        f"---\n\n"
        f"## 5. 가설 검증\n\n"
        f"H3-{method_name[0].upper()}: _Placeholder — 데이터 보고 채움 (입증/부분/반증 + 근거)._\n\n"
        f"---\n\n"
        f"## 6. 의의 + 다음\n\n"
        f"- {paradigm} 위치에서 본 측정의 의미: _placeholder._\n"
        f"- 다음 실험: _다음 RQ3 method (#N+1) 진행._\n\n"
        f"---\n\n"
        f"## 카톡 §3.2 (완료) 메시지 자동 작성\n\n"
        f"```\n"
        f"[실험 #_ 완료] {now_hm} (소요 ~{elapsed_str})\n\n"
        f"실험명: RQ3 {method_name} ({paradigm})\n"
        f"산출 위치: {rq3_path_str}\n\n"
        f"═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══\n"
        f"(a) 동기 — _placeholder_\n"
        f"(b) 가설 — H3-{method_name[0].upper()}: recovery_rate {expected_str}\n"
        f"(c) 예상 결과 — {expected_str}\n"
        f"(d) 실제 결과 — {headline_metrics['overall']}\n\n"
        f"═══ 의의 + 다음 ═══\n"
        f"- _narrative 보강 placeholder_\n"
        f"- 다음 실험 #_ 진행\n\n"
        f"자동 git commit + push 완료\n"
        f"```\n"
    )
    return md


def _df_to_markdown(df: pd.DataFrame) -> str:
    """Lightweight markdown table generator (tabulate 의존성 회피)."""
    if df.empty:
        return "_(no data)_"
    cols = df.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |",
             "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            if pd.isna(v):
                cells.append("nan")
            elif isinstance(v, bool):
                cells.append("True" if v else "False")
            elif isinstance(v, float):
                cells.append(f"{v:.4f}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _format_summary_table(summary_df: pd.DataFrame) -> str:
    if summary_df.empty:
        return "_(summary 데이터 없음)_"
    cols = ["dataset", "sel", "method_q", "random20_q", "km20_q", "denom_pct",
            "recovery", "metric", "method_minus_random_pct", "method_minus_bern_pct"]
    sub = summary_df[[c for c in cols if c in summary_df.columns]].copy()
    return _df_to_markdown(sub)


def _format_significance_table(sig_df: pd.DataFrame) -> str:
    if sig_df.empty:
        return "_(significance 데이터 없음)_"
    cols = ["dataset", "mode_treat", "mode_ctrl", "sel", "n_pairs",
            "delta_pct", "p_raw", "p_BH", "reject_005"]
    sub = sig_df[[c for c in cols if c in sig_df.columns]].copy()
    if "delta_pct" in sub.columns:
        sub["delta_pct"] = sub["delta_pct"].round(2)
    for c in ["p_raw", "p_BH"]:
        if c in sub.columns:
            sub[c] = sub[c].apply(lambda x: f"{x:.2e}" if pd.notna(x) else "nan")
    return _df_to_markdown(sub)


def _extract_headlines(summary_df: pd.DataFrame, sig_df: pd.DataFrame, method_name: str) -> dict:
    """summary + significance 에서 핵심 수치 추출 (한 줄 요약용)."""
    out = {
        "overall": "_(데이터 없음)_",
        "best": "_(데이터 없음)_",
        "worst": "_(데이터 없음)_",
        "fallback_count": 0,
        "sig_vs_bern_count": 0,
        "sig_vs_km_count": 0,
    }
    if summary_df.empty:
        return out
    rec = summary_df[summary_df["metric"] == "recovery"]
    fb = summary_df[summary_df["metric"] == "fallback_abs_pct"]
    out["fallback_count"] = int(len(fb))

    if not rec.empty:
        rec_mean = rec["recovery"].mean()
        out["overall"] = (
            f"평균 recovery_rate = {rec_mean:.3f} "
            f"(n={len(rec)}/{len(summary_df)} cells, "
            f"fall-back={out['fallback_count']})"
        )
        # best = KM20 oracle 에 가까움 (recovery 가 1 에 근접), worst = recovery 가장 낮음
        rec_local = rec.reset_index(drop=True)
        best_pos = rec_local["recovery"].sub(1.0).abs().idxmin()
        worst_pos = rec_local["recovery"].idxmin()
        best_row = rec_local.loc[best_pos]
        worst_row = rec_local.loc[worst_pos]
        out["best"] = (
            f"{best_row['dataset']} sel={best_row['sel']:.2f}, "
            f"recovery={best_row['recovery']:.3f}"
        )
        out["worst"] = (
            f"{worst_row['dataset']} sel={worst_row['sel']:.2f}, "
            f"recovery={worst_row['recovery']:.3f}"
        )
    elif not fb.empty:
        # 모든 셀 fall-back 인 극단 케이스
        fb_mean = fb["method_minus_bern_pct"].mean()
        out["overall"] = (
            f"모든 cell fall-back, 절대 (BERN 대비) Δ% 평균 {fb_mean:+.2f}%"
        )

    if not sig_df.empty:
        if "mode_ctrl" in sig_df.columns and "reject_005" in sig_df.columns:
            out["sig_vs_bern_count"] = int(
                sig_df[(sig_df["mode_ctrl"] == "bernoulli") & sig_df["reject_005"]].shape[0]
            )
            out["sig_vs_km_count"] = int(
                sig_df[(sig_df["mode_ctrl"] == "km20") & sig_df["reject_005"]].shape[0]
            )
    return out


# ---------------------------------------------------------------------------
# 4. main — orchestrate
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="RQ3 per-method analysis driver")
    ap.add_argument("--method", default=None,
                    help="method 이름 (예: minibatch / lsh / hilbert / kde_pilot / "
                         "distance_shell / is_p50_noclip ...)")
    ap.add_argument("--rq3-parquet", default=None,
                    help="RQ3 method 측정 parquet (mode 'equal' 또는 method-named 포함)")
    ap.add_argument("--rq2-parquet",
                    default=str(REPO_ROOT / "experiments" / "results" / "rq2_aware"
                                / "2026_05_06_alloc" / "rq2_alloc.parquet"),
                    help="RQ2 alloc parquet (KM20 oracle baseline)")
    ap.add_argument("--out-dir", default=None,
                    help="출력 dir (default experiments/results/rq3_agnostic/{method}/)")
    ap.add_argument("--demo", action="store_true",
                    help="placeholder 데이터로 smoke test (parquet 없이 동작)")
    ap.add_argument("--bh-n-compare", type=int, default=None,
                    help="BH-FDR 분모. None 이면 자동 (행 수, RQ3 7-way 통합 시 70 권장)")
    args = ap.parse_args()

    if args.demo:
        method_name = args.method or "demo_method"
        print(f"[{kst()}] === DEMO mode — synthetic data ({method_name}) ===")
        method_df, rq2_km20 = make_demo_data(method_name)
        rq3_parquet = None
        rq2_parquet = None
    else:
        if not args.method or not args.rq3_parquet:
            ap.error("--method 와 --rq3-parquet 필요 (또는 --demo)")
        method_name = args.method
        rq3_parquet = Path(args.rq3_parquet)
        rq2_parquet = Path(args.rq2_parquet)
        if not rq3_parquet.exists():
            ap.error(f"--rq3-parquet not found: {rq3_parquet}")
        if not rq2_parquet.exists():
            ap.error(f"--rq2-parquet not found: {rq2_parquet}")
        print(f"[{kst()}] loading {rq3_parquet}")
        method_df = load_rq3_method(rq3_parquet, method_name)
        print(f"[{kst()}] loading {rq2_parquet} (km20 only)")
        rq2_km20 = load_rq2_km20(rq2_parquet)

    # df 합치기 (method, bernoulli, km20)
    long_df = build_long_df(method_df, rq2_km20, method_name)
    print(f"[{kst()}] combined long-form: {len(long_df)} rows, "
          f"modes={sorted(long_df['mode'].unique().tolist())}")

    # 1) summarize_method (cell-level recovery rate)
    summary_df = summarize_method(
        long_df, method=method_name,
        baselines=("bernoulli", "km20", "bernoulli"),  # bern_q == random20
    )
    print(f"\n[{kst()}] === Recovery Rate Summary ===")
    print(summary_df.to_string(index=False))

    # 2) paired Wilcoxon BH-FDR (vs bernoulli, vs km20)
    sig_df = paired_wilcoxon_with_bh_fdr(
        long_df,
        compare_pairs=[(method_name, "bernoulli"), (method_name, "km20")],
        n_compare=args.bh_n_compare,
        alternative="less",  # treatment q_error < control 검증
    )
    print(f"\n[{kst()}] === Paired Wilcoxon BH-FDR ===")
    print(sig_df.to_string(index=False))

    # 3) 출력 dir 결정 + 저장
    out_dir = Path(args.out_dir) if args.out_dir else (DEFAULT_OUT_ROOT / method_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_csv = out_dir / f"{method_name}_summary.csv"
    sig_csv = out_dir / f"{method_name}_significance.csv"
    md_path = out_dir / f"{method_name}_analysis.md"

    summary_df.to_csv(summary_csv, index=False)
    sig_df.to_csv(sig_csv, index=False)
    print(f"\n[{kst()}] saved {summary_csv}")
    print(f"[{kst()}] saved {sig_csv}")

    md = build_narrative_md(
        method_name=method_name,
        rq3_parquet=rq3_parquet, rq2_parquet=rq2_parquet,
        summary_df=summary_df, sig_df=sig_df,
        n_total_rows=len(long_df),
    )
    md_path.write_text(md, encoding="utf-8")
    print(f"[{kst()}] saved {md_path} ({len(md)} chars)")
    print(f"\n[{kst()}] DONE. 다음: 의 narrative placeholder 채우고 git commit.")


if __name__ == "__main__":
    main()
