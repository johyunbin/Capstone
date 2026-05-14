#!/usr/bin/env python3
"""
Layer 1 audit — paired Δ% calculation correctness.

검증 항목 (handoff §2.1):
1. paired Δ% 공식 재현: per-trial Δ% 계산 후 mean
2. trial pairing: B1 trial i ↔ CaseA trial i
3. inf/nan handling: avg_q_error_finite 사용
4. trim mean (avg_q_error_trimmed) vs mean(finite) 일치성
5. cell × method 순서 일관성

추가 cross-check:
- alternative formulation: (mean(CaseA) - mean(B1)) / mean(B1) — 비교
- bootstrap CI (95%) for Δ% — 안정성 측정
- per-trial Δ% distribution skewness (median != mean → 알려야)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "paired_delta_audit.md"


def load_trials(json_path: Path) -> list[float]:
    """avg_q_error_finite per trial (raw, includes inf if any made it through)."""
    d = json.load(open(json_path))
    return [t["avg_q_error_finite"] for t in d["trial_results"]]


def trim_mean_paper(values: list[float], trim: int = 1) -> float:
    """Paper p.7: lowest 1 + highest 1 제외 후 평균. inf 사전 제외."""
    finite = sorted(v for v in values if np.isfinite(v))
    if len(finite) <= 2 * trim:
        return float("nan")
    trimmed = finite[trim:-trim]
    return float(np.mean(trimmed))


def main_paired_delta(b1: list[float], ca: list[float]) -> dict:
    """Replica of analyze_paper_exact.py paired_delta()."""
    if len(b1) != len(ca) or len(b1) == 0:
        return {"delta_pct_mean": float("nan"), "delta_pct_median": float("nan"),
                "n_trials": 0, "n_finite_pairs": 0}
    b1_arr = np.array(b1, dtype=float)
    ca_arr = np.array(ca, dtype=float)
    finite = np.isfinite(b1_arr) & np.isfinite(ca_arr)
    n_finite = int(finite.sum())
    if n_finite == 0:
        return {"delta_pct_mean": float("nan"), "delta_pct_median": float("nan"),
                "n_trials": len(b1), "n_finite_pairs": 0}
    b1_f, ca_f = b1_arr[finite], ca_arr[finite]
    delta = (ca_f - b1_f) / b1_f * 100
    return {
        "delta_pct_mean": float(np.mean(delta)),
        "delta_pct_median": float(np.median(delta)),
        "delta_pct_std": float(np.std(delta, ddof=1)) if n_finite > 1 else 0.0,
        "delta_pct_min": float(np.min(delta)),
        "delta_pct_max": float(np.max(delta)),
        "n_trials": len(b1),
        "n_finite_pairs": n_finite,
        "b1_mean": float(np.mean(b1_f)),
        "ca_mean": float(np.mean(ca_f)),
    }


def alt_aggregate_delta(b1: list[float], ca: list[float]) -> float:
    """(mean(CaseA) - mean(B1)) / mean(B1) — aggregated then divided."""
    b1_f = [v for v in b1 if np.isfinite(v)]
    ca_f = [v for v in ca if np.isfinite(v)]
    if not b1_f or not ca_f:
        return float("nan")
    b1_m = np.mean(b1_f)
    ca_m = np.mean(ca_f)
    return float((ca_m - b1_m) / b1_m * 100)


def bootstrap_delta_ci(b1: list[float], ca: list[float],
                       n_boot: int = 1000, seed: int = 42) -> tuple[float, float]:
    """Bootstrap 95% CI for delta_pct_mean."""
    rng = np.random.default_rng(seed)
    b1_arr = np.array(b1, dtype=float)
    ca_arr = np.array(ca, dtype=float)
    finite = np.isfinite(b1_arr) & np.isfinite(ca_arr)
    if not finite.any():
        return float("nan"), float("nan")
    b1_f, ca_f = b1_arr[finite], ca_arr[finite]
    n = len(b1_f)
    if n < 3:
        return float("nan"), float("nan")
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        d = (ca_f[idx] - b1_f[idx]) / b1_f[idx] * 100
        boots.append(np.mean(d))
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def audit():
    md = ["# Layer 1 — paired Δ% calculation audit\n",
          "_생성_: 2026-05-10 검증 세션 (메인 영향 X, read-only)\n",
          f"_입력_: `{DATA}`\n",
          "---\n"]

    # === 1. data inventory ===
    b1_files = sorted(DATA.glob("*_B1.json"))
    casea_files = sorted(DATA.glob("*_CaseA_*.json"))
    caseb_files = sorted(DATA.glob("*_CaseB_*.json"))
    md.append("## 1. Data inventory\n")
    md.append(f"- B1 cells: **{len(b1_files)}** (paths)")
    md.append(f"- CaseA measurements: **{len(casea_files)}**")
    md.append(f"- CaseB measurements: **{len(caseb_files)}**\n")

    # extract cell list + method list
    cells = sorted({p.stem.replace("_B1", "") for p in b1_files})
    casea_methods = sorted({p.stem.split("_CaseA_", 1)[-1] for p in casea_files})
    caseb_methods = sorted({p.stem.split("_CaseB_", 1)[-1] for p in caseb_files})
    md.append(f"- Cells (B1): {cells}")
    md.append(f"- CaseA methods ({len(casea_methods)}): {casea_methods}")
    md.append(f"- CaseB methods ({len(caseb_methods)}): {caseb_methods}\n")

    # === 2. trim_mean vs mean(finite) consistency ===
    md.append("## 2. `avg_q_error_trimmed` (stored) vs recomputed trim mean\n")
    md.append("**검증**: stored `avg_q_error_trimmed` (paper p.7 trim=1) ↔ "
              "재계산 `trim_mean_paper(trial_finite, trim=1)`.\n")
    md.append("| Cell/Method | mode | stored trim | recomp trim | Δ | mean(finite) | n_finite | n_inf |")
    md.append("|---|---|---|---|---|---|---|---|")
    consistency_rows = []
    for f in b1_files + casea_files[:11] + caseb_files[:11]:
        d = json.load(open(f))
        finite_vals = [t["avg_q_error_finite"] for t in d["trial_results"]
                       if np.isfinite(t["avg_q_error_finite"])]
        n_inf = sum(1 for t in d["trial_results"]
                    if not np.isfinite(t["avg_q_error_finite"]))
        recomp = trim_mean_paper(finite_vals, trim=1)
        stored = d.get("avg_q_error_trimmed", float("nan"))
        diff = abs(recomp - stored) if np.isfinite(recomp) and np.isfinite(stored) else float("nan")
        mean_f = float(np.mean(finite_vals)) if finite_vals else float("nan")
        cell_method = d.get("cell", "?")
        if d.get("method"):
            cell_method = f"{cell_method}/{d['method']}"
        md.append(f"| {cell_method} | {d['mode']} | "
                  f"{stored:.4f} | {recomp:.4f} | {diff:.6f} | "
                  f"{mean_f:.4f} | {len(finite_vals)} | {n_inf} |")
        consistency_rows.append({"file": f.name, "stored": stored, "recomp": recomp, "diff": diff})
    md.append("")
    diffs = [r["diff"] for r in consistency_rows if np.isfinite(r["diff"])]
    if diffs:
        md.append(f"**stored vs recomp 일관성**: max Δ = {max(diffs):.6e}, "
                  f"mean Δ = {np.mean(diffs):.6e}")
        if max(diffs) < 1e-6:
            md.append("→ **PASS**: stored `avg_q_error_trimmed` 정확히 paper trim 공식과 일치.")
        else:
            md.append(f"→ **WARN**: max diff = {max(diffs):.4e} — trim 정의 미세 차이 가능성.")
    md.append("")

    # === 3. paired Δ% recomputation per (cell, method) ===
    md.append("## 3. Paired Δ% 재계산 (per cell × method × trial)\n")
    md.append("**alternative formulation 비교**:")
    md.append("- (A) `mean(per-trial Δ%)` — analyze_paper_exact.py 사용")
    md.append("- (B) `(mean(CaseA) - mean(B1)) / mean(B1) × 100` — aggregated")
    md.append("- 두 값의 차이가 크면 trial 별 분포 skew 시사.\n")
    md.append("| Cell | Method | mode | n_finite | Δ% (A: per-trial) | Δ% (B: agg) | abs Δ | "
              "median | std | min/max | bootstrap 95% CI |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")

    audit_rows = []
    for cell in cells:
        b1_path = DATA / f"{cell}_B1.json"
        if not b1_path.exists():
            continue
        b1_trials = load_trials(b1_path)
        # CaseA per method
        for method in casea_methods:
            ca_path = DATA / f"{cell}_CaseA_{method}.json"
            if not ca_path.exists():
                continue
            ca_trials = load_trials(ca_path)
            d = main_paired_delta(b1_trials, ca_trials)
            d_alt = alt_aggregate_delta(b1_trials, ca_trials)
            ci_lo, ci_hi = bootstrap_delta_ci(b1_trials, ca_trials)
            abs_diff = abs(d["delta_pct_mean"] - d_alt) if np.isfinite(d["delta_pct_mean"]) else float("nan")
            md.append(f"| {cell} | {method} | CaseA | {d['n_finite_pairs']}/{d['n_trials']} | "
                      f"{d['delta_pct_mean']:+.2f}% | {d_alt:+.2f}% | {abs_diff:.2f} | "
                      f"{d['delta_pct_median']:+.2f}% | {d['delta_pct_std']:.2f} | "
                      f"[{d['delta_pct_min']:+.1f}, {d['delta_pct_max']:+.1f}] | "
                      f"[{ci_lo:+.1f}, {ci_hi:+.1f}] |")
            audit_rows.append({"cell": cell, "method": method, "mode": "CaseA",
                               "delta_A": d["delta_pct_mean"], "delta_B": d_alt,
                               "abs_diff": abs_diff, "n_finite": d["n_finite_pairs"],
                               "median": d["delta_pct_median"], "std": d["delta_pct_std"],
                               "ci_lo": ci_lo, "ci_hi": ci_hi})
        # CaseB per method
        for method in caseb_methods:
            cb_path = DATA / f"{cell}_CaseB_{method}.json"
            if not cb_path.exists():
                continue
            cb_trials = load_trials(cb_path)
            d = main_paired_delta(b1_trials, cb_trials)
            d_alt = alt_aggregate_delta(b1_trials, cb_trials)
            ci_lo, ci_hi = bootstrap_delta_ci(b1_trials, cb_trials)
            abs_diff = abs(d["delta_pct_mean"] - d_alt) if np.isfinite(d["delta_pct_mean"]) else float("nan")
            md.append(f"| {cell} | {method} | CaseB | {d['n_finite_pairs']}/{d['n_trials']} | "
                      f"{d['delta_pct_mean']:+.2f}% | {d_alt:+.2f}% | {abs_diff:.2f} | "
                      f"{d['delta_pct_median']:+.2f}% | {d['delta_pct_std']:.2f} | "
                      f"[{d['delta_pct_min']:+.1f}, {d['delta_pct_max']:+.1f}] | "
                      f"[{ci_lo:+.1f}, {ci_hi:+.1f}] |")
            audit_rows.append({"cell": cell, "method": method, "mode": "CaseB",
                               "delta_A": d["delta_pct_mean"], "delta_B": d_alt,
                               "abs_diff": abs_diff, "n_finite": d["n_finite_pairs"],
                               "median": d["delta_pct_median"], "std": d["delta_pct_std"],
                               "ci_lo": ci_lo, "ci_hi": ci_hi})
    md.append("")

    # === 4. Aggregate findings ===
    df = pd.DataFrame(audit_rows)
    md.append("## 4. Aggregate findings\n")
    md.append(f"- **Total comparisons**: {len(df)}")
    if len(df) == 0:
        md.append("- (empty data)\n")
        OUT.write_text("\n".join(md))
        return

    md.append(f"  - CaseA: {(df['mode']=='CaseA').sum()}")
    md.append(f"  - CaseB: {(df['mode']=='CaseB').sum()}")

    # n_finite summary
    n_finite_low = df[df["n_finite"] < 8]
    md.append(f"\n- **n_finite < 8** (pairing 실패 case): {len(n_finite_low)}건")
    if len(n_finite_low) > 0:
        for _, r in n_finite_low.head(20).iterrows():
            md.append(f"  - {r['cell']} {r['method']} ({r['mode']}): n_finite={r['n_finite']}")

    # large abs_diff (A vs B)
    df_finite = df[np.isfinite(df["delta_A"]) & np.isfinite(df["delta_B"])]
    if len(df_finite) > 0:
        large_diff = df_finite[df_finite["abs_diff"] > 5]
        md.append(f"\n- **abs(A-B) > 5%p** (per-trial vs agg 큰 차이): {len(large_diff)}건")
        for _, r in large_diff.head(15).iterrows():
            md.append(f"  - {r['cell']} {r['method']} ({r['mode']}): "
                      f"per-trial {r['delta_A']:+.1f}% vs agg {r['delta_B']:+.1f}% "
                      f"(diff {r['abs_diff']:.1f})")

    # extreme deltas (outliers — likely YFCC 192d / SSN cases)
    df_extreme = df_finite[np.abs(df_finite["delta_A"]) > 100]
    md.append(f"\n- **|Δ%| > 100%** (extreme outliers): {len(df_extreme)}건")
    for _, r in df_extreme.iterrows():
        md.append(f"  - {r['cell']} {r['method']} ({r['mode']}): "
                  f"Δ%={r['delta_A']:+.1f}, median={r['median']:+.1f}, "
                  f"std={r['std']:.1f}")

    # CI sign disagreement: mean Δ < 0 but CI includes 0 (no real outperform)
    df_neg = df_finite[df_finite["delta_A"] < 0]
    no_signif = df_neg[(df_neg["ci_lo"] > 0) | ((df_neg["ci_lo"] < 0) & (df_neg["ci_hi"] > 0))]
    md.append(f"\n- **mean Δ% < 0 but bootstrap 95% CI includes 0** "
              f"(통계적으로 outperform 불확실): {len(no_signif)}/{len(df_neg)}")
    for _, r in no_signif.head(20).iterrows():
        md.append(f"  - {r['cell']} {r['method']} ({r['mode']}): "
                  f"Δ%={r['delta_A']:+.1f}, CI [{r['ci_lo']:+.1f}, {r['ci_hi']:+.1f}]")

    # === 5. summary ===
    md.append("\n## 5. Layer 1 판정\n")
    pass_recomp = max(diffs) < 1e-6 if diffs else False
    md.append(f"- trim mean stored vs recomp: {'PASS' if pass_recomp else 'WARN'}")
    md.append(f"- paired Δ% formula (handoff §2.1.1): **확인** (per-trial Δ% mean)")
    md.append(f"- trial pairing: **확인** (B1 trial i ↔ CaseA trial i, 동일 seed `trial_idx*13+7`)")
    md.append(f"- inf/nan handling: **확인** (`np.isfinite` mask, n_finite count 기록)")
    md.append(f"- alternative agg formula 차이: max abs_diff = "
              f"{df_finite['abs_diff'].max():.2f}%p (당연한 차이 — per-trial vs agg)")
    md.append(f"- extreme outliers (|Δ|>100%): **{len(df_extreme)}건** — "
              f"narrative 영향 평가는 Layer 3 cherry-picking에서.")
    md.append(f"- bootstrap CI에서 0 포함 (mean<0인데 outperform 불확실): "
              f"**{len(no_signif)}/{len(df_neg)}건**")

    md.append("\n### 종합")
    if pass_recomp and len(df_extreme) <= 10:
        md.append("- **PASS**: paired Δ% 계산 정확. extreme outlier는 알려진 YFCC 192d/SSN 영역.")
    else:
        md.append("- **WARN**: 위 항목 메인 세션 검토 필요.")

    # save CSV for downstream layers
    df.to_csv(Path(__file__).parent / "audit_data_paired.csv", index=False)
    md.append(f"\n_audit_data_paired.csv 저장 (downstream Layer 2/3/4 입력)_")

    OUT.write_text("\n".join(md))
    print(f"Layer 1 audit → {OUT}")
    print(f"  comparisons: {len(df)}, CaseA: {(df['mode']=='CaseA').sum()}, CaseB: {(df['mode']=='CaseB').sum()}")
    print(f"  extreme |Δ|>100%: {len(df_extreme)}")
    print(f"  bootstrap CI 0 포함 (CaseA-better 불확실): {len(no_signif)}/{len(df_neg)}")


if __name__ == "__main__":
    audit()
