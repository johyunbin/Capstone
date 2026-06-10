#!/usr/bin/env python3
"""팀 최종보고서(초초안 채움) 5번 항목 figure + 베이스 데이터 표 생성.

산출:
  experiments/figures/보고서_6_11/team_20260610/
    fig1_true_vs_est_engine.png      엔진 주입 평면 true vs estimated cardinality (sel 3단)
    fig2_scatter_offline_{sel}.png   오프라인 대표 cell 산점도 (B1 vs 결합)
    fig3_latency_12cell.png          12 cell end-to-end latency 4-mode
    table1_engine_truth_vs_est.csv   fig1 베이스 표
    table2_scatter_deciles_{sel}.csv fig2 베이스 표 (십분위)
    table3_latency_12cell.csv        fig3 베이스 표
  + stdout 에 본문 인용 수치 검증값 출력
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd

ROOT = Path("/Users/hyunbin/Capstone")
OUT = ROOT / "experiments/figures/보고서_6_11/team_20260610"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = ["Apple SD Gothic Neo", "AppleGothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

PARTSUPP_ROWS = 8_000_000          # TPC-H sf=10 partsupp = 800만 행
PG_DEFAULT = PARTSUPP_ROWS / 3.0   # pgvector 고정 33.3% 추정

C_PG = "#c0392b"; C_B1 = "#e67e22"; C_CB = "#1a5276"; C_TRUE = "#111111"; C_OR = "#27ae60"

# ---------------------------------------------------------------- fig1
est = pd.read_parquet(ROOT / "_internal/cache/rq3/latency/estimates_DEEP_sf10.parquet")
rows = []
for (sel, qid), g in est.groupby(["sel", "query_id"]):
    rows.append(dict(sel=sel, qid=qid, true_card=g.true_card.iloc[0],
                     pg_default=PG_DEFAULT, est_b1=g.est_b1.iloc[0],
                     est_caseB_median=g.est_caseB.median()))
t1 = pd.DataFrame(rows).sort_values(["sel", "qid"])
t1.to_csv(OUT / "table1_engine_truth_vs_est.csv", index=False)

fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2), sharey=True)
for ax, sel in zip(axes, [0.001, 0.01, 0.1]):
    sub = t1[t1.sel == sel]
    x = np.arange(len(sub)); w = 0.26
    ax.bar(x - w, sub.pg_default, w, color=C_PG, label="pgvector 기본 (33.3% 고정)")
    ax.bar(x, np.maximum(sub.est_b1, 1.0), w, color=C_B1, label="베이스라인 (무작위 표본)")
    ax.bar(x + w, np.maximum(sub.est_caseB_median, 1.0), w, color=C_CB, label="결합 (13개 method 중앙값)")
    for i, tc in enumerate(sub.true_card):
        ax.hlines(tc, i - 1.6 * w, i + 1.6 * w, color=C_TRUE, lw=2.2,
                  label="참 카디널리티" if i == 0 else None)
    ax.set_yscale("log"); ax.set_xticks(x)
    ax.set_xticklabels([f"질의 {q}" for q in sub.qid])
    ax.set_title(f"selectivity = {sel}", fontsize=11)
    ax.grid(axis="y", alpha=0.25, which="both")
axes[0].set_ylabel("카디널리티 (행 수, 로그 눈금)")
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.02), fontsize=9.5, frameon=False)
fig.suptitle("참 카디널리티 대 추정 카디널리티 — DEEP sf=10 partsupp (800만 행), 질의 벡터 5종",
             y=1.12, fontsize=12.5)
fig.tight_layout()
fig.savefig(OUT / "fig1_true_vs_est_engine.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print("=== fig1 / table1 (engine true vs est) ===")
print(t1.round(1).to_string(index=False))
print(f"pg_default = {PG_DEFAULT:,.0f}")
for sel in [0.001, 0.01, 0.1]:
    sub = t1[t1.sel == sel]
    print(f"sel={sel}: pg기본 과대 추정 배율 = {(PG_DEFAULT / sub.true_card).min():,.0f}~{(PG_DEFAULT / sub.true_card).max():,.0f}x")

# ---------------------------------------------------------------- fig2
def load_cell(cell_dir, method):
    d = json.load(open(ROOT / f"_internal/cache/rq3/results_3way_5_17/{cell_dir}/A1-DEEP_3way_{method}.json"))
    true = np.array(d["true_cards"], dtype=float)
    out = {}
    for mode in ["B1", "CaseB"]:
        ests = np.concatenate([np.array(t["estimates"], dtype=float) for t in d[mode]["trial_results"]])
        out[mode] = ests
    return true, out, d

for sel_tag, cell_dir in [("0.01", "A1-DEEP_sel0.01_K20"), ("0.1", "A1-DEEP_sel0.1_K20")]:
    true, modes, meta = load_cell(cell_dir, "chao_weighted")
    true10 = np.tile(true, 10)
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.0), sharex=True, sharey=True)
    x_lo, x_hi = true.min() * 0.985, true.max() * 1.015
    y_hi = float(np.quantile(np.concatenate(list(modes.values())), 0.999)) * 1.08
    xs = np.linspace(x_lo, x_hi, 50)
    for ax, (mode, label, color) in zip(
            axes, [("B1", "베이스라인 (무작위 베르누이 표본)", C_B1),
                   ("CaseB", "결합 (베르누이 + 분포 인지 층화 평균)", C_CB)]):
        e = modes[mode]
        ax.fill_between(xs, 0.5 * xs, 1.5 * xs, color="#bbbbbb", alpha=0.30,
                        label="±50% 상대 오차 구간" if mode == "B1" else None)
        ax.scatter(true10, e, s=5, alpha=0.07, color=color, edgecolors="none")
        ax.plot(xs, xs, color=C_TRUE, lw=1.4, ls="--", label="y = x (완전 일치)")
        ax.set_xlim(x_lo, x_hi); ax.set_ylim(0, y_hi)
        within = np.mean(np.abs(e - true10) / true10 <= 0.5) * 100
        ax.set_title(f"{label}\n|상대 오차| ≤ 50% 비율: {within:.1f}%", fontsize=10.5)
        ax.set_xlabel("참 카디널리티"); ax.grid(alpha=0.25)
        ax.ticklabel_format(axis="both", style="plain")
        ax.tick_params(axis="x", labelsize=8.5)
    axes[0].set_ylabel("추정 카디널리티")
    axes[0].legend(fontsize=9, loc="upper left", frameon=False)
    fig.suptitle(f"질의별 추정 대 참 카디널리티 산점 — DEEP sf=100 (8,000만 행), selectivity {sel_tag}, "
                 f"chao_weighted, 10회 반복 × 1,000 질의", fontsize=11.5)
    fig.tight_layout()
    fig.savefig(OUT / f"fig2_scatter_offline_sel{sel_tag}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    dec = pd.qcut(true10, 10, labels=False, duplicates="drop")
    t2 = pd.DataFrame({"decile": dec, "true": true10, "B1": modes["B1"], "CaseB": modes["CaseB"]})
    t2g = t2.groupby("decile").agg(n=("true", "size"), true_mean=("true", "mean"),
                                   b1_mean=("B1", "mean"), caseB_mean=("CaseB", "mean")).round(0)
    t2g.to_csv(OUT / f"table2_scatter_deciles_sel{sel_tag}.csv")
    print(f"\n=== fig2 / table2 (offline scatter, sel={sel_tag}) ===")
    print("true range:", true.min(), "-", true.max(), "| n_queries:", len(true))
    for mode in ["B1", "CaseB"]:
        e = modes[mode]
        print(f"{mode}: zero-est 비율 {np.mean(e == 0) * 100:.1f}% | |상대오차|<=50% {np.mean(np.abs(e - true10) / true10 <= 0.5) * 100:.1f}% | median est/true {np.median(np.maximum(e, 1) / true10):.3f}")
    print(t2g.to_string())

# ---------------------------------------------------------------- fig3
P2 = ROOT / "_internal/cache/rq3/latency/phase2"
cells = []
for q in ["q3", "q9", "q10", "q12"]:
    for qid in [0, 1, 2]:
        d = json.load(open(P2 / f"latency_tpc_h_{q}_DEEP_sf10_sel0.001_qid{qid}.json"))
        def tmean(v):
            xs = sorted(v["exec_ms"]); return float(np.mean(xs[1:-1]))
        vmap = {}
        caseb = []
        for v in d["variants"]:
            cond = v["condition"]
            if cond in ("baseline", "B1", "oracle"):
                vmap[cond] = tmean(v)
            else:
                caseb.append(tmean(v))
        cells.append(dict(cell=f"{q.upper()}·질의{qid}", query=q, qid=qid,
                          true_card=d["true_card"], D=round(d["D"], 4),
                          기본엔진=vmap["baseline"], 베이스라인=vmap["B1"],
                          결합13평균=float(np.mean(caseb)), 정답주입=vmap["oracle"],
                          n_caseb=len(caseb)))
t3 = pd.DataFrame(cells)
t3["speedup_정답"] = t3.기본엔진 / t3.정답주입
t3.to_csv(OUT / "table3_latency_12cell.csv", index=False)

fig, ax = plt.subplots(figsize=(12.6, 4.6))
x = np.arange(len(t3)); w = 0.2
ax.bar(x - 1.5 * w, t3.기본엔진, w, color=C_PG, label="기본 엔진 (고정 33.3%)")
ax.bar(x - 0.5 * w, t3.베이스라인, w, color=C_B1, label="베이스라인 주입")
ax.bar(x + 0.5 * w, t3.결합13평균, w, color=C_CB, label="결합 주입 (13개 method 평균)")
ax.bar(x + 1.5 * w, t3.정답주입, w, color=C_OR, label="참 카디널리티 주입")
ax.set_xticks(x); ax.set_xticklabels(t3.cell, rotation=30, ha="right", fontsize=9)
ax.set_ylabel("실행 시간 (ms, 15회 절사 평균)")
ax.set_title("TPC-H 4개 질의 × 질의 벡터 3종 = 12 cell end-to-end 실행 시간 — DEEP sf=10, selectivity 0.001")
ax.legend(ncol=4, fontsize=9.5, frameon=False); ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "fig3_latency_12cell.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print("\n=== fig3 / table3 (latency 12 cell) ===")
print(t3.round(1).to_string(index=False))
print(f"\n정답 주입 speedup: min {t3.speedup_정답.min():.2f}x / max {t3.speedup_정답.max():.2f}x / 12-cell 평균 {t3.speedup_정답.mean():.2f}x")
print(f"베이스라인 12-cell 평균 {t3.베이스라인.mean():.0f}ms | 결합 {t3.결합13평균.mean():.0f}ms | 정답 {t3.정답주입.mean():.0f}ms | 기본 {t3.기본엔진.mean():.0f}ms")
print(f"기본/결합 = {t3.기본엔진.mean() / t3.결합13평균.mean():.2f}x | 기본/베이스라인 = {t3.기본엔진.mean() / t3.베이스라인.mean():.2f}x")
print("CaseB method 수 per cell:", sorted(t3.n_caseb.unique()))
