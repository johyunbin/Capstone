#!/usr/bin/env python3
"""
rq3_figures.py — RQ3 7-way distribution-agnostic 시각화 4종

산출:
    experiments/figures/rq3_distribution_agnostic/fig6_7way_recovery_rate.png
    experiments/figures/rq3_distribution_agnostic/fig7_paradigm_split.png
    experiments/figures/rq3_distribution_agnostic/fig8_selectivity_gradient_method.png
    experiments/figures/rq3_distribution_agnostic/fig9_cost_recovery_tradeoff.png

입력:
    --rq3 <parquet>     RQ3 측정 long-form (dataset/mode/selectivity/seed/query_id/q_error).
                        여러 실험 (#5~#11) 결과를 concat 한 통합 parquet 권장.
    --rq2 <parquet>     RQ2 km20·bernoulli baseline 통합 parquet (rq2_alloc.parquet 재활용 가능).
                        (RQ2 의 'equal' 등은 사용 안 함, 'bernoulli' 만 BERN baseline 으로 사용.)
    --random20 <parquet> RANDOM20 측정 parquet (실험 #5 직전 보강 측정 권장. 없으면 rq3 안에 random20 mode 포함).
    --km20 <parquet>    (옵션) KM20 측정 parquet. 없으면 rq2 의 'neyman' 또는 'proportional' 중 변환 사용.

사용법:
    python3 experiments/code/local_analysis/rq3_figures.py \\
        --rq3 experiments/results/rq3/2026_05_07/rq3_all.parquet

스타일:
    - 폰트: Apple SD Gothic Neo
    - dpi=150
    - 논문용 단조 팔레트 (rq2_figures.py 와 일관)

★ 측정 데이터 미존재 시: --demo 플래그로 placeholder 데이터로 dry-run.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import rcParams

from recovery_rate import (
    DENOM_COLLAPSE_THRESHOLD_PCT,
    summarize_method,
)


# ---------------------------------------------------------------------------
# 스타일 (rq2_figures.py 와 일관)
# ---------------------------------------------------------------------------

rcParams["font.family"] = ["Apple SD Gothic Neo", "AppleGothic", "Nanum Gothic", "sans-serif"]
rcParams["axes.unicode_minus"] = False
rcParams["font.size"] = 11
rcParams["axes.titlesize"] = 12
rcParams["axes.labelsize"] = 11
rcParams["xtick.labelsize"] = 10
rcParams["ytick.labelsize"] = 10
rcParams["legend.fontsize"] = 10
rcParams["figure.dpi"] = 150
rcParams["savefig.dpi"] = 150
rcParams["savefig.bbox"] = "tight"
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["axes.grid"] = True
rcParams["grid.alpha"] = 0.25
rcParams["grid.linestyle"] = "--"

C_DARK = "#2b2b2b"
C_BLUE = "#1f77b4"
C_ORANGE = "#e07a00"
C_GRAY = "#9aa0a6"
C_GREEN_DARK = "#2e7d32"
C_RED = "#c62828"
C_PURPLE = "#7b1fa2"
C_TEAL = "#00838f"

# paradigm 별 색
PARADIGM_COLORS = {
    "offline": C_BLUE,
    "online": C_ORANGE,
    "weight": C_PURPLE,
}

# 7-way method 정의 (RQ재정립 §RQ3)
METHOD_ORDER = [
    # (mode, label, paradigm, expected_recovery_low, expected_recovery_high)
    ("random_proj",    "C. Random Projection",  "offline", 0.10, 0.40),
    ("lsh",            "A. LSH",                "offline", 0.30, 0.60),
    ("hilbert",        "E. Hilbert Curve",      "offline", 0.20, 0.60),
    ("minibatch",      "F. MiniBatch K-means",  "offline", 0.75, 0.95),
    ("distance_shell", "G. Distance-Shell",     "online",  0.25, 0.50),
    ("kde_pilot",      "B. KDE-pilot",          "online",  0.50, 0.80),
    ("importance",     "H. Importance Sampling","weight",  0.30, 0.70),
]

# fig9 — 사전 학습 비용 (초 단위, RQ재정립 §RQ3 의 구현 시간 + 실측 보강)
# 측정 후 메타 json 의 fit/train timing 으로 갱신 권장. 0.0 = pure online.
PRE_TRAIN_COST_S = {
    "random_proj":    0.05,   # numpy random matrix init
    "lsh":            0.10,   # hyperplane gen + sign hash
    "hilbert":        1.00,   # PCA SVD + Hilbert grid build
    "minibatch":      5.00,   # 1% sample MiniBatchKMeans 학습
    "distance_shell": 0.00,   # online pilot only, no offline
    "kde_pilot":      0.00,   # online pilot only, no offline
    "importance":     0.00,   # online pilot only, no offline
    "km20":          60.00,   # KM20 oracle (full batch K-means) 비교 reference
    "random20":       0.00,   # RANDOM20 baseline (분류 cost 0)
}

OUT_DIR = Path("/Users/hyunbin/Capstone/experiments/figures/rq3_distribution_agnostic")


# ---------------------------------------------------------------------------
# 데이터 로딩
# ---------------------------------------------------------------------------

def load_inputs(args: argparse.Namespace) -> pd.DataFrame:
    """RQ2 + RQ3 + (random20/km20) parquet 들을 long-form 으로 합쳐 반환.

    합쳐지면 mode 컬럼에 random20, km20, bernoulli 및 7개 method 가 모두 존재해야 함.
    """
    if args.demo:
        return _make_demo_df()

    parts: list[pd.DataFrame] = []
    if args.rq3:
        parts.append(pd.read_parquet(args.rq3))
    if args.rq2:
        rq2 = pd.read_parquet(args.rq2)
        # bernoulli 만 baseline 으로 사용
        parts.append(rq2[rq2["mode"] == "bernoulli"])
    if args.random20:
        parts.append(pd.read_parquet(args.random20))
    if args.km20:
        parts.append(pd.read_parquet(args.km20))

    if not parts:
        raise SystemExit("no input parquet provided. use --demo for dry-run.")

    df = pd.concat(parts, ignore_index=True)
    required = {"dataset", "mode", "selectivity", "seed", "query_id", "q_error"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"missing columns: {missing}")
    return df


def _make_demo_df(seed: int = 42) -> pd.DataFrame:
    """측정 데이터 미존재 시 fig 레이아웃 검증용 placeholder.

    expected_recovery_high 의 평균값을 반영한 q_error 시뮬레이션.
    """
    rng = np.random.default_rng(seed)
    rows = []
    datasets = ["DEEP", "SIFT"]
    sels = [0.01, 0.05, 0.1, 0.3, 0.5]
    seeds = [0.1, 0.2, 0.3, 0.4, 0.5]
    n_query = 30

    # baseline 가정: BERN q_error ≈ 1.5, RANDOM20 ≈ 1.4, KM20 ≈ 1.0
    base = {"bernoulli": 1.5, "random20": 1.4, "km20": 1.0}

    for ds in datasets:
        for sel in sels:
            ds_factor = 1.0 if ds == "DEEP" else 1.3  # SIFT q_error 더 큼
            sel_factor = 1.0 + (0.5 - sel) * 0.4       # 좁은 sel 일수록 q_error 큼
            for mode in list(base.keys()):
                for sd in seeds:
                    for q in range(n_query):
                        noise = rng.normal(0, 0.1)
                        rows.append({
                            "dataset": ds, "mode": mode, "selectivity": sel,
                            "seed": sd, "query_id": q,
                            "q_error": base[mode] * ds_factor * sel_factor + noise,
                        })
            # 7-way method: RANDOM20 와 KM20 사이 중간값
            for mode, _, _, lo, hi in METHOD_ORDER:
                rec_target = (lo + hi) / 2
                method_q_target = base["random20"] + rec_target * (base["km20"] - base["random20"])
                for sd in seeds:
                    for q in range(n_query):
                        noise = rng.normal(0, 0.12)
                        rows.append({
                            "dataset": ds, "mode": mode, "selectivity": sel,
                            "seed": sd, "query_id": q,
                            "q_error": method_q_target * ds_factor * sel_factor + noise,
                        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 공통 — 7-way × dataset 의 recovery_rate 매트릭스
# ---------------------------------------------------------------------------

def build_recovery_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """7 method × 2 dataset × 5 selectivity recovery 통계 통합 DataFrame.

    각 method 에 대해 summarize_method() 호출 후 method 컬럼 부착.
    """
    parts = []
    for mode, label, paradigm, _, _ in METHOD_ORDER:
        if mode not in df["mode"].unique():
            continue
        sm = summarize_method(df, method=mode)
        sm["method"] = mode
        sm["label"] = label
        sm["paradigm"] = paradigm
        parts.append(sm)
    if not parts:
        raise SystemExit("no method columns found in input — check mode names")
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# Figure 6 — 7-way Recovery Rate (가로 막대, dataset × method 평균)
# ---------------------------------------------------------------------------

def figure_6_7way_recovery(rec: pd.DataFrame, out_dir: Path) -> Path:
    """방법별 평균 recovery_rate 가로 막대.

    dataset 으로 색 분리, paradigm 으로 그룹.
    분모 붕괴 (metric=='fallback_abs_pct') 셀은 점선 마커로 별도 표시.
    """
    fig, ax = plt.subplots(figsize=(10.5, 6.0))

    methods = [m for m, *_ in METHOD_ORDER if m in rec["method"].unique()]
    labels = [next(label for m, label, *_ in METHOD_ORDER if m == mm) for mm in methods]
    paradigms = [next(p for m, _, p, *_ in METHOD_ORDER if m == mm) for mm in methods]

    y = np.arange(len(methods))
    height = 0.35

    for i, ds in enumerate(("DEEP", "SIFT")):
        means = []
        n_fallback = []
        for mm in methods:
            sub = rec[(rec["method"] == mm) & (rec["dataset"] == ds)]
            valid = sub[sub["metric"] == "recovery"]["recovery"].dropna()
            means.append(valid.mean() if len(valid) else math.nan)
            n_fallback.append((sub["metric"] == "fallback_abs_pct").sum())

        offset = -height / 2 if i == 0 else height / 2
        color = C_BLUE if ds == "DEEP" else C_ORANGE
        bars = ax.barh(
            y + offset, means, height=height, color=color,
            edgecolor=C_DARK, linewidth=0.7, alpha=0.88, label=ds,
        )

        # 막대 끝 수치
        for yi, m, nfb in zip(y + offset, means, n_fallback):
            if math.isnan(m):
                ax.text(0.02, yi, "N/A", va="center", fontsize=9, color=C_GRAY)
            else:
                ax.text(m + 0.015 if m >= 0 else m - 0.015, yi,
                        f"{m:+.2f}", va="center",
                        ha="left" if m >= 0 else "right",
                        fontsize=9.5, color=C_DARK, fontweight="bold")
            if nfb > 0:
                ax.text(0.0 - 0.06, yi, f"fb={nfb}", va="center", ha="right",
                        fontsize=8, color=C_RED, fontstyle="italic")

    # 0/1 reference
    ax.axvline(0, color=C_DARK, linewidth=0.8, linestyle=":", zorder=1, label="RANDOM20 수준")
    ax.axvline(1, color=C_GREEN_DARK, linewidth=1.0, linestyle="--", zorder=1, label="KM20 oracle 수준")

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()  # 위에 #5 부터

    ax.set_xlabel("Recovery Rate  (1.0 = KM20 oracle, 0.0 = RANDOM20)")
    ax.set_xlim(-0.4, 1.3)

    # paradigm 구분 배경
    for yi, p in zip(y, paradigms):
        c = PARADIGM_COLORS.get(p, C_GRAY)
        ax.axhspan(yi - 0.5, yi + 0.5, alpha=0.04, color=c, zorder=0)

    ax.legend(loc="lower right", frameon=True, edgecolor=C_DARK, ncols=2)

    fig.suptitle(
        "Figure 6 · 7-way Distribution-Agnostic 방법별 Recovery Rate (dataset 평균)",
        fontweight="bold", fontsize=13, y=1.00,
    )
    caption = (
        "주: Recovery Rate = (방법X − RANDOM20) / (KM20 − RANDOM20). 1.0 = KM20 oracle 수준 회수, 0.0 = RANDOM20 수준.\n"
        "fb=N: 분모 붕괴 (|KM20−RANDOM20|/RANDOM20 ≤ 1%p) 셀 수 — 해당 셀은 평균에서 제외, 별도 fall-back metric (방법X−BERN%) 로 보고.\n"
        "paradigm 배경 음영: Offline (파랑) / Online (주황) / Weight (보라)."
    )
    fig.text(0.06, -0.02, caption, fontsize=8.5, color=C_DARK, va="top")

    out = out_dir / "fig6_7way_recovery_rate.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {out}")
    return out


# ---------------------------------------------------------------------------
# Figure 7 — Paradigm 별 분리 (3 subplot)
# ---------------------------------------------------------------------------

def figure_7_paradigm_split(rec: pd.DataFrame, out_dir: Path) -> Path:
    """Offline 4 / Online 2 / Weight 1 — 3 subplot 으로 paradigm 비교.

    각 subplot 안에서 method 별 dataset 평균 recovery 값 + expected band.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5),
                              gridspec_kw={"width_ratios": [4, 2, 1]}, sharey=True)

    paradigm_methods: dict[str, list[tuple]] = {"offline": [], "online": [], "weight": []}
    for mode, label, p, lo, hi in METHOD_ORDER:
        if mode in rec["method"].unique():
            paradigm_methods[p].append((mode, label, lo, hi))

    paradigm_titles = {
        "offline": "(a) Offline Partition (1회 사전 계산)",
        "online":  "(b) Online Query-Adaptive (쿼리 시점)",
        "weight":  "(c) Weight-based (분할 X, 가중치)",
    }

    for ax, p in zip(axes, ("offline", "online", "weight")):
        items = paradigm_methods[p]
        x = np.arange(len(items))

        for i, ds in enumerate(("DEEP", "SIFT")):
            means = []
            for mm, *_ in items:
                sub = rec[(rec["method"] == mm) & (rec["dataset"] == ds)
                          & (rec["metric"] == "recovery")]
                m = sub["recovery"].dropna().mean()
                means.append(m if not math.isnan(m) else 0.0)

            offset = -0.18 if i == 0 else 0.18
            color = C_BLUE if ds == "DEEP" else C_ORANGE
            ax.bar(
                x + offset, means, width=0.34, color=color,
                edgecolor=C_DARK, linewidth=0.7, alpha=0.88, label=ds,
            )

        # expected band (RQ재정립 §RQ3 표)
        for xi, (_, _, lo, hi) in enumerate(items):
            ax.fill_betweenx([lo, hi], xi - 0.45, xi + 0.45,
                             color=PARADIGM_COLORS[p], alpha=0.10, zorder=0)
            ax.plot([xi - 0.45, xi + 0.45], [lo, lo],
                    color=PARADIGM_COLORS[p], linewidth=0.9, linestyle="--", zorder=1)
            ax.plot([xi - 0.45, xi + 0.45], [hi, hi],
                    color=PARADIGM_COLORS[p], linewidth=0.9, linestyle="--", zorder=1)

        ax.axhline(0, color=C_DARK, linewidth=0.7, linestyle=":", zorder=1)
        ax.axhline(1, color=C_GREEN_DARK, linewidth=0.9, linestyle="--", zorder=1)

        ax.set_xticks(x)
        ax.set_xticklabels([label.split(". ", 1)[1] if ". " in label else label
                            for _, label, *_ in items], rotation=15, ha="right")
        ax.set_title(paradigm_titles[p], fontweight="bold", pad=8,
                     color=PARADIGM_COLORS[p])
        ax.set_ylim(-0.4, 1.3)
        if p == "offline":
            ax.legend(loc="upper left", frameon=True, edgecolor=C_DARK)

    axes[0].set_ylabel("Recovery Rate")

    fig.suptitle(
        "Figure 7 · Paradigm 별 분리 — 음영대는 RQ재정립 §RQ3 의 사전 기대 범위",
        fontweight="bold", fontsize=13, y=1.02,
    )
    caption = (
        "주: 음영 밴드 = (lo, hi) 사전 기대 recovery (예: F. MiniBatch 75~95%, C. Random Projection 10~40%).\n"
        "측정 결과가 밴드 안에 들어오면 사전 등록 가설 입증, 밖이면 새 발견.\n"
        "Offline > Online > Weight 순으로 정확도-비용 trade-off curve 형성 예상."
    )
    fig.text(0.06, -0.04, caption, fontsize=8.5, color=C_DARK, va="top")

    out = out_dir / "fig7_paradigm_split.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {out}")
    return out


# ---------------------------------------------------------------------------
# Figure 8 — Selectivity Gradient × Method (heatmap-line hybrid)
# ---------------------------------------------------------------------------

def figure_8_selectivity_gradient_method(rec: pd.DataFrame, out_dir: Path) -> Path:
    """selectivity 5점 × 7 method 의 recovery 곡선.

    DEEP / SIFT 2 panel. fall-back 셀은 별도 마커 (×) 로 표시.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.0), sharey=True)

    methods = [m for m, *_ in METHOD_ORDER if m in rec["method"].unique()]
    labels = {m: label for m, label, *_ in METHOD_ORDER}
    paradigm_of = {m: p for m, _, p, *_ in METHOD_ORDER}

    line_colors = plt.cm.tab10(np.linspace(0, 1, max(len(methods), 1)))

    for ax, ds in zip(axes, ("DEEP", "SIFT")):
        for mm, color in zip(methods, line_colors):
            sub = rec[(rec["method"] == mm) & (rec["dataset"] == ds)].sort_values("sel")
            sels = sub["sel"].to_numpy()
            recs = sub["recovery"].to_numpy()
            metrics = sub["metric"].to_numpy()

            valid_mask = (metrics == "recovery") & ~np.isnan(recs)
            fb_mask = metrics == "fallback_abs_pct"

            # 정상 점은 연결, fall-back 은 별도 X 마커
            ax.plot(sels[valid_mask], recs[valid_mask],
                    marker="o", markersize=6, linewidth=1.7,
                    color=color, label=labels[mm], zorder=3)
            if fb_mask.any():
                # fall-back 표시는 y=0 위치에 X
                ax.scatter(sels[fb_mask], np.zeros(fb_mask.sum()),
                           marker="x", s=70, color=color, linewidth=2.0, zorder=4)

        ax.axhline(0, color=C_DARK, linewidth=0.8, linestyle=":", zorder=1)
        ax.axhline(1, color=C_GREEN_DARK, linewidth=0.9, linestyle="--", zorder=1)

        ax.set_xscale("log")
        ax.set_xticks([0.01, 0.05, 0.1, 0.3, 0.5])
        ax.set_xticklabels([f"{s:.2f}" for s in [0.01, 0.05, 0.1, 0.3, 0.5]])
        ax.invert_xaxis()
        ax.set_xlabel("Selectivity (로그)")
        ax.set_title(f"({'a' if ds == 'DEEP' else 'b'}) {ds}", fontweight="bold", pad=8)
        ax.set_ylim(-0.4, 1.3)

    axes[0].set_ylabel("Recovery Rate")
    # 범례는 두번째 subplot 바깥에
    axes[1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5),
                   frameon=True, edgecolor=C_DARK, fontsize=9)

    fig.suptitle(
        "Figure 8 · Selectivity Gradient × 7-way Method — 좁은 쿼리에서의 Recovery 거동",
        fontweight="bold", fontsize=13, y=1.00,
    )
    caption = (
        "주: × 마커 = 분모 붕괴 셀 (|KM20−RANDOM20| ≤ 1%p). y=0 위치에 표시되었으나 의미상 미정 — 본문 fall-back 표 참조.\n"
        "RQ1 결과처럼 좁은 sel (s=0.01) 에서 oracle KM20 의 우위가 클수록 7-way 방법의 recovery 거동이 가장 도전적.\n"
        "MiniBatch (F) 가 모든 sel 에서 1.0 근처면 'oracle 대용' 가능, Random Projection (C) 이 0 근처면 하한 입증."
    )
    fig.text(0.06, -0.03, caption, fontsize=8.5, color=C_DARK, va="top")

    out = out_dir / "fig8_selectivity_gradient_method.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {out}")
    return out


# ---------------------------------------------------------------------------
# Figure 9 — Cost-Recovery Tradeoff (사전 학습 비용 × Recovery)
# ---------------------------------------------------------------------------

def figure_9_cost_recovery_tradeoff(rec: pd.DataFrame, out_dir: Path,
                                    cost_overrides: dict | None = None) -> Path:
    """방법별 (사전 학습 비용 vs 평균 Recovery Rate) scatter — Pareto frontier 시각화.

    paradigm 색 + dataset 마커 분리. KM20 oracle (1.0) 과 RANDOM20 (0.0) 의
    reference 선 표시. 비용은 PRE_TRAIN_COST_S 기본값 (사전 등록) 또는 측정
    후 cost_overrides 로 실측치 갱신 가능.

    이 그림의 메시지:
      - 좌상단 (low cost, high recovery) = production 솔루션 후보
      - 우상단 (high cost, high recovery) = oracle 또는 그에 근접한 method (KM20)
      - 좌하단 (low cost, low recovery) = baseline (RANDOM20)
    """
    cost_map = dict(PRE_TRAIN_COST_S)
    if cost_overrides:
        cost_map.update(cost_overrides)

    fig, ax = plt.subplots(figsize=(11, 6.2))

    methods = [m for m, *_ in METHOD_ORDER if m in rec["method"].unique()]
    paradigm_of = {m: p for m, _, p, *_ in METHOD_ORDER}
    label_of = {m: label for m, label, *_ in METHOD_ORDER}

    # 각 method 의 (cost, recovery_DEEP, recovery_SIFT)
    plot_rows = []
    for mm in methods:
        cost = cost_map.get(mm, 0.0)
        for ds in ("DEEP", "SIFT"):
            sub = rec[(rec["method"] == mm) & (rec["dataset"] == ds)
                      & (rec["metric"] == "recovery")]
            mean_rec = sub["recovery"].dropna().mean()
            if math.isnan(mean_rec):
                continue
            plot_rows.append({
                "method": mm, "label": label_of[mm], "paradigm": paradigm_of[mm],
                "dataset": ds, "cost": cost, "recovery": mean_rec,
            })
    pd_plot = pd.DataFrame(plot_rows)

    # paradigm 색 + dataset 마커
    DATASET_MARKER = {"DEEP": "o", "SIFT": "^"}
    DATASET_FACE = {"DEEP": "white", "SIFT": None}    # SIFT 채움, DEEP 빈 원

    drawn_paradigms = set()
    for _, r in pd_plot.iterrows():
        c = PARADIGM_COLORS.get(r["paradigm"], C_GRAY)
        marker = DATASET_MARKER[r["dataset"]]
        face = DATASET_FACE[r["dataset"]] if r["dataset"] == "DEEP" else c
        # x = max(cost, ε) — log scale 위해
        x = max(float(r["cost"]), 0.02)
        ax.scatter(
            x, r["recovery"], s=160, marker=marker,
            facecolor=face, edgecolor=c, linewidth=1.8, zorder=3,
            label=(f"{r['paradigm']}, {r['dataset']}"
                   if (r["paradigm"], r["dataset"]) not in drawn_paradigms else None),
        )
        drawn_paradigms.add((r["paradigm"], r["dataset"]))

        # method label annotation (DEEP 만 — 중복 방지)
        if r["dataset"] == "DEEP":
            short = r["label"].split(". ", 1)[1] if ". " in r["label"] else r["label"]
            ax.annotate(short, xy=(x, r["recovery"]),
                        xytext=(8, 4), textcoords="offset points",
                        fontsize=9, color=C_DARK, fontweight="bold")

    # KM20 oracle reference (cost=60s, recovery=1.0)
    km_cost = cost_map.get("km20", 60.0)
    ax.scatter(km_cost, 1.0, s=200, marker="*",
               facecolor=C_GREEN_DARK, edgecolor=C_DARK, linewidth=1.4, zorder=4)
    ax.annotate("KM20 oracle", xy=(km_cost, 1.0), xytext=(8, 4),
                textcoords="offset points", fontsize=10,
                color=C_GREEN_DARK, fontweight="bold")

    # RANDOM20 reference (cost=0, recovery=0)
    ax.scatter(0.02, 0.0, s=140, marker="s",
               facecolor=C_GRAY, edgecolor=C_DARK, linewidth=1.2, zorder=4)
    ax.annotate("RANDOM20", xy=(0.02, 0.0), xytext=(8, 4),
                textcoords="offset points", fontsize=10,
                color=C_DARK, fontweight="bold")

    ax.axhline(0, color=C_DARK, linewidth=0.7, linestyle=":", zorder=1)
    ax.axhline(1, color=C_GREEN_DARK, linewidth=0.9, linestyle="--", zorder=1)
    ax.set_xscale("log")
    ax.set_xlim(0.015, 200)
    ax.set_ylim(-0.4, 1.3)
    ax.set_xlabel("사전 학습 비용 (초, 로그)")
    ax.set_ylabel("Recovery Rate (DEEP+SIFT 평균)")

    # 범례 — paradigm 색 + dataset 마커 별도
    from matplotlib.lines import Line2D
    legend_paradigm = [
        Line2D([], [], marker="o", color="w", markerfacecolor=C_BLUE,
               markeredgecolor=C_DARK, markersize=10, label="Offline (offline 사전 분할)"),
        Line2D([], [], marker="o", color="w", markerfacecolor=C_ORANGE,
               markeredgecolor=C_DARK, markersize=10, label="Online (query-adaptive)"),
        Line2D([], [], marker="o", color="w", markerfacecolor=C_PURPLE,
               markeredgecolor=C_DARK, markersize=10, label="Weight (분할 X)"),
    ]
    legend_dataset = [
        Line2D([], [], marker="o", color="w", markerfacecolor="white",
               markeredgecolor=C_DARK, markersize=10, label="DEEP (빈 원)"),
        Line2D([], [], marker="^", color="w", markerfacecolor=C_DARK,
               markeredgecolor=C_DARK, markersize=10, label="SIFT (채워진 삼각형)"),
    ]
    leg1 = ax.legend(handles=legend_paradigm, loc="upper left", title="Paradigm",
                     frameon=True, edgecolor=C_DARK, fontsize=9)
    ax.add_artist(leg1)
    ax.legend(handles=legend_dataset, loc="lower right", title="Dataset",
              frameon=True, edgecolor=C_DARK, fontsize=9)

    fig.suptitle(
        "Figure 9 · Cost-Recovery Tradeoff — 좌상단이 production 솔루션 후보",
        fontweight="bold", fontsize=13, y=1.00,
    )
    caption = (
        "주: x = 사전 학습 비용 (초, 로그스케일). y = Recovery Rate (DEEP+SIFT × 5 sel 평균).\n"
        "KM20 oracle (★, 초록) = 비용 ~60초, recovery=1.0 (정의상). RANDOM20 (■, 회색) = 비용 0, recovery=0.\n"
        "F. MiniBatch 가 좌상단 (low cost ~5초, high recovery 80%+) 에 위치하면 production 솔루션 명확.\n"
        "Online (G/B) 와 Weight (H) 는 cost=0 라인에 위치 — recovery 차이가 paradigm 의 가치 결정."
    )
    fig.text(0.06, -0.03, caption, fontsize=8.5, color=C_DARK, va="top")

    out = out_dir / "fig9_cost_recovery_tradeoff.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {out}")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _check_baselines(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """recovery 계산에 필요한 baseline mode (random20, km20, bernoulli) 확인.

    누락 시 main() 에서 경고 출력 후 진행 (해당 셀은 metric='missing' 으로 표시됨).
    'km20' 이 없을 경우 RQ2 alloc parquet 의 'equal' 모드를 'km20' 으로 rename 권장.
    """
    required = {"random20", "km20", "bernoulli"}
    present = set(df["mode"].unique())
    missing = sorted(required - present)
    return (len(missing) == 0), missing


def main():
    parser = argparse.ArgumentParser(description="RQ3 figures (fig6/7/8/9)")
    parser.add_argument("--rq3", type=Path, default=None, help="RQ3 통합 parquet")
    parser.add_argument("--rq2", type=Path, default=None, help="RQ2 alloc parquet (bernoulli baseline)")
    parser.add_argument("--random20", type=Path, default=None)
    parser.add_argument("--km20", type=Path, default=None)
    parser.add_argument("--demo", action="store_true",
                        help="placeholder 데이터로 dry-run (측정 데이터 미존재 시)")
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Output dir: {args.out}")

    df = load_inputs(args)
    print(f"Loaded {len(df):,} rows; modes = {sorted(df['mode'].unique())}")

    ok, missing = _check_baselines(df)
    if not ok:
        print(f"⚠ baseline 누락: {missing}. recovery 계산에서 해당 셀은 metric='missing' 으로 처리됨.")
        if "random20" in missing:
            print("  → run_random20.py 측정 후 --random20 인자로 추가하세요.")
        if "km20" in missing:
            print("  → RQ2 alloc parquet 의 'equal' 모드를 'km20' 으로 rename 후 concat (handoff §6.3 참조).")
        if "bernoulli" in missing:
            print("  → --rq2 인자로 RQ2 alloc parquet 를 추가하세요 (bernoulli baseline 포함).")

    rec = build_recovery_matrix(df)
    figure_6_7way_recovery(rec, args.out)
    figure_7_paradigm_split(rec, args.out)
    figure_8_selectivity_gradient_method(rec, args.out)
    figure_9_cost_recovery_tradeoff(rec, args.out)
    print("\n완료. fig6/7/8/9 생성됨.")


if __name__ == "__main__":
    main()
