"""
Figure 6 (Phase 5 Local Skew × Q-error Spearman heatmap) A 등급 재생성.
보강: colorbar 범위 ±0.30 → ±0.20 (strong threshold 일치, 색 contrast 강화).
Raw: experiments/results/rq1_motivation/phase5_local_skew_spearman.json (4 metrics × 6 selectivity = 24).
"""

import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

rcParams["font.family"] = "Apple SD Gothic Neo"
rcParams["axes.unicode_minus"] = False

RAW = "experiments/results/rq1_motivation/phase5_local_skew_spearman.json"
OUT = "experiments/figures/rq1_motivation/figure_6_phase5_heatmap.png"

data = json.load(open(RAW))

metric_order = [
    ("kde_modality_count",   "KDE modality"),
    ("knn_distance_entropy", "k-NN 거리 entropy"),
    ("knn_pca_evr1",         "k-NN PCA EVR1"),
    ("nn_clustering_coef",   "NN clustering coef"),
]
sels = [0.001, 0.01, 0.05, 0.1, 0.3, 0.5]

M = np.full((4, 6), np.nan)
for c in data["all_combos"]:
    mi = next((i for i, (k, _) in enumerate(metric_order) if k == c["metric"]), None)
    si = sels.index(c["selectivity"])
    if mi is not None:
        M[mi, si] = c["spearman_rho"]

fig, ax = plt.subplots(figsize=(9.5, 3.5))
# inner suptitle 제거 — 보고서 캡션 "그림 2. Phase 5 ..." 와 중복 회피

VMAX = 0.20
im = ax.imshow(M, cmap="RdBu_r", vmin=-VMAX, vmax=VMAX, aspect="auto")

for i in range(4):
    for j in range(6):
        v = M[i, j]
        sign = "+" if v >= 0 else ""
        ax.text(j, i, f"{sign}{v:.2f}", ha="center", va="center",
                fontsize=10.5,
                color="black" if abs(v) < 0.13 else "white",
                fontweight="medium")

ax.set_xticks(range(6))
ax.set_xticklabels([f"{s:.3f}" for s in sels], fontsize=10)
ax.set_yticks(range(4))
ax.set_yticklabels([n for _, n in metric_order], fontsize=10)
ax.set_xlabel("Selectivity", fontsize=10.5, labelpad=6)

cbar = fig.colorbar(im, ax=ax, fraction=0.040, pad=0.02)
cbar.set_label("Spearman ρ  (clip ±0.20 = strong threshold)", fontsize=9)
cbar.ax.tick_params(labelsize=9)
cbar.set_ticks([-0.20, -0.10, 0.0, 0.10, 0.20])

for s in ax.spines.values():
    s.set_visible(False)

fig.text(
    0.5, 0.04,
    "주: |ρ| ≥ 0.2 를 strong correlation 임계로 정의. 24 조합 모두 임계 미만 (n_strong = 0).\n"
    "global 24 조합과 합산 시 총 48 조합 모두 |ρ| < 0.2 ⇒ Local skew 가 Q-error 의 단일 원인이 아님 (RQ1 Phase 5 negative result).",
    ha="center", fontsize=11, color="#222", linespacing=1.55,
)

plt.subplots_adjust(top=0.95, bottom=0.27, left=0.18, right=1.02)
plt.savefig(OUT, dpi=170, bbox_inches="tight", pad_inches=0.15)
plt.close()
print(f"saved: {OUT}")
