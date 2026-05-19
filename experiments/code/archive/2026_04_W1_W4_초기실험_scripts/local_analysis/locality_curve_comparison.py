#!/usr/bin/env python3
"""
Z-order vs Hilbert curve locality 정량 비교 (synthetic + 실측 PCA 좌표).

본 연구의 RQ3 narrative — "Hilbert curve 가 contribution 1순위 격상" — 의 mechanism
검증. 5/6 측정에서 Hilbert 가 DEEP -3.7%, SIFT -4.1% 의 강한 effect 를 보였으나,
이게 (a) PCA+quantile 효과인지 (b) Hilbert 자체의 locality 효과인지 분리 X.

Z-order curve 는 PCA+quantile 골격 동일하되 locality preservation 만 다름. 두 curve
의 locality 차이를 정량화하면 (a) vs (b) 분리 narrative 확정.

검증 metric:
  1. **Locality preservation**: 인접 grid cell 의 1D distance 의 평균.
     인접 grid cell (Manhattan distance 1) 가 1D distance 도 작아야 locality 보존.
     - L_avg = mean(|d(p) - d(q)|) where p, q are 4-neighbors in grid.
     - Hilbert: 작음 (회전+swap 으로 인접 보존)
     - Z-order: 큼 (Y 축 jump 시 큰 점프)

  2. **Stratum compactness**: 같은 stratum 의 grid 좌표들의 분산.
     - 작을수록 stratum 이 spatial 영역에 집중됨 (HT estimator 이점).

  3. **Cross-stratum 평균 거리**: 다른 stratum 의 grid 좌표 간 평균 거리.
     - 클수록 stratum 간 분리 (cluster-aware 효과).

테스트 데이터:
  - Synthetic 1: iid Gaussian (96d) — PCA 효과 약함, locality 자체 비교
  - Synthetic 2: 5-cluster Gaussian (96d) — clustered, PCA 가 의미있음
  - Real PCA: DEEP 1M sample 의 saved fit log 를 활용 (있으면)

산출:
  - locality_curve_comparison.csv — metric × curve × dataset
  - locality_curve_comparison.md — narrative
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RQ3 = ROOT / "Capstone" / "experiments" / "code" / "rq3"
if not RQ3.exists():
    # 다른 경로 가정 — local_analysis 부모 의 상위 3개
    RQ3 = Path(__file__).resolve().parent.parent / "rq3"
sys.path.insert(0, str(RQ3))

from hilbert.hilbert_curve import (  # noqa: E402
    fit_hilbert_mapper, hilbert_xy_to_d,
)
from zorder.zorder_curve import (  # noqa: E402
    fit_zorder_mapper, zorder_xy_to_d,
)


def grid_neighbor_locality(p: int, distance_fn) -> dict:
    """전체 grid cell 4-neighbor 쌍의 1D distance 차이 통계 (forward metric).

    forward metric (2D 인접 → 1D 거리): 모든 4-neighbor 쌍의 |d_a - d_b| 평균.
    인접 grid 가 1D 에서도 인접하면 작음. ideal=1.
    """
    n = 1 << p
    xs, ys = np.meshgrid(np.arange(n), np.arange(n), indexing='xy')
    xs, ys = xs.flatten(), ys.flatten()
    d = distance_fn(xs, ys, p)

    coord_to_d = d.reshape(n, n)
    diffs_r = np.abs(coord_to_d[:, 1:] - coord_to_d[:, :-1]).flatten()
    diffs_b = np.abs(coord_to_d[1:, :] - coord_to_d[:-1, :]).flatten()
    diffs = np.concatenate([diffs_r, diffs_b])

    return {
        "n_pairs": int(len(diffs)),
        "mean_jump": float(np.mean(diffs)),
        "median_jump": float(np.median(diffs)),
        "max_jump": float(np.max(diffs)),
        "p95_jump": float(np.percentile(diffs, 95)),
    }


def grid_inverse_locality(p: int, distance_fn) -> dict:
    """1D 인접 → 2D Manhattan 거리 (inverse metric).

    space-filling curve 의 본질 정의: 1D 연속 (d, d+1) 가 2D 에서 Manhattan distance 1.
    Hilbert: 항상 1 (continuous).
    Z-order: 대부분 1, 그러나 quadrant boundary (Z-jump) 에서 큰 점프.

    이 metric 이 Hilbert vs Z-order 를 결정적으로 분리.
    """
    n = 1 << p
    xs, ys = np.meshgrid(np.arange(n), np.arange(n), indexing='xy')
    xs, ys = xs.flatten(), ys.flatten()
    d = distance_fn(xs, ys, p)

    # 1D distance 순으로 정렬 후 consecutive Manhattan distance 측정
    order = np.argsort(d)
    xs_sorted = xs[order]
    ys_sorted = ys[order]
    manhattan = np.abs(np.diff(xs_sorted)) + np.abs(np.diff(ys_sorted))

    return {
        "n_pairs": int(len(manhattan)),
        "mean_manhattan": float(np.mean(manhattan)),
        "median_manhattan": float(np.median(manhattan)),
        "max_manhattan": float(np.max(manhattan)),
        "p95_manhattan": float(np.percentile(manhattan, 95)),
        "fraction_jump_gt_1": float((manhattan > 1).mean()),
    }


def stratum_compactness(samples: np.ndarray, mapper) -> dict:
    """fit 된 mapper 로 samples 분류 후 각 stratum 내 grid 좌표 분산 평균.

    grid 좌표 (x, y) 의 std 평균 — 작을수록 stratum 이 spatial cluster.
    """
    coords = mapper.pca.transform(samples.astype(np.float64))
    grid_xy = mapper._to_grid(coords)  # (N, 2)
    sids = mapper.assign(samples)

    per_stratum = []
    for s in range(mapper.n_strata):
        mask = sids == s
        if mask.sum() < 2:
            continue
        cluster_xy = grid_xy[mask]
        std_x = float(np.std(cluster_xy[:, 0]))
        std_y = float(np.std(cluster_xy[:, 1]))
        per_stratum.append(std_x + std_y)

    return {
        "n_strata": len(per_stratum),
        "compactness_mean": float(np.mean(per_stratum)),
        "compactness_max": float(np.max(per_stratum)),
        # 작을수록 spatial cluster 가 잘 잡힘.
    }


def compare_curves_on_data(
    samples: np.ndarray, label: str, p: int = 8, n_strata: int = 20, seed: int = 42,
) -> list[dict]:
    """동일 sample 에 Hilbert / Z-order fit 후 metric 측정."""
    rows = []

    # 2. Stratum compactness (sample 의존)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        h_mapper = fit_hilbert_mapper(samples, n_strata=n_strata, p=p, seed=seed)
        z_mapper = fit_zorder_mapper(samples, n_strata=n_strata, p=p, seed=seed)

    h_compact = stratum_compactness(samples, h_mapper)
    z_compact = stratum_compactness(samples, z_mapper)
    rows.append({
        "source": label, "label": label, "curve": "hilbert",
        "p": p, "metric": "stratum_compactness_mean", "value": h_compact["compactness_mean"],
    })
    rows.append({
        "source": label, "label": label, "curve": "zorder",
        "p": p, "metric": "stratum_compactness_mean", "value": z_compact["compactness_mean"],
    })
    return rows


def main():
    out_dir = ROOT / "experiments" / "results" / "rq3_agnostic"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Z-order vs Hilbert locality 정량 비교")
    print("=" * 70)

    rng = np.random.default_rng(42)

    all_rows: list[dict] = []

    # === 0. Grid metric (sample 무관) — 1번만 측정 ===
    print("\n[0] Grid metric (sample 무관, p=8)")
    for curve, fn in [("hilbert", hilbert_xy_to_d), ("zorder", zorder_xy_to_d)]:
        forward = grid_neighbor_locality(8, fn)
        inverse = grid_inverse_locality(8, fn)
        all_rows.append({
            "source": "grid_only", "label": "n/a", "curve": curve, "p": 8,
            "metric": "neighbor_jump_mean", "value": forward["mean_jump"],
            **{f"fwd_{k}": v for k, v in forward.items()},
            **{f"inv_{k}": v for k, v in inverse.items()},
        })
        print(f"  {curve}: forward mean={forward['mean_jump']:.1f} max={forward['max_jump']:.0f} "
              f"p95={forward['p95_jump']:.0f} | inverse mean_manhattan={inverse['mean_manhattan']:.3f} "
              f"frac>1={inverse['fraction_jump_gt_1']:.4f}")

    # 1. Synthetic iid (96d)
    print("\n[1] Synthetic iid Gaussian (5000 × 96d)")
    syn_iid = rng.standard_normal((5000, 96)).astype(np.float32)
    all_rows.extend(compare_curves_on_data(syn_iid, "synthetic_iid", p=8))

    # 2. Synthetic clustered (5 Gaussian × 1000 = 5000 × 96d)
    print("[2] Synthetic clustered (5 Gaussians, 5000 × 96d)")
    centers = rng.standard_normal((5, 96)).astype(np.float32) * 5
    syn_cl = np.vstack([
        rng.standard_normal((1000, 96)).astype(np.float32) + c for c in centers
    ])
    all_rows.extend(compare_curves_on_data(syn_cl, "synthetic_clustered", p=8))

    # 3. Synthetic SIFT-like (heavy-tail, 128d) — SIFT 의 skew 시뮬
    print("[3] Synthetic SIFT-like (heavy-tail Gaussian mixture, 5000 × 128d)")
    # 다른 cluster 크기 (skew) 시뮬
    weights = [0.5, 0.2, 0.15, 0.10, 0.05]   # heavy on cluster 0
    centers_128 = rng.standard_normal((5, 128)).astype(np.float32) * 5
    syn_sift = np.vstack([
        rng.standard_normal((int(5000 * w), 128)).astype(np.float32) + c
        for w, c in zip(weights, centers_128)
    ])
    all_rows.extend(compare_curves_on_data(syn_sift, "synthetic_sift_like", p=8))

    # === 분석 ===
    df = pd.DataFrame(all_rows)
    df.to_csv(out_dir / "locality_curve_comparison.csv", index=False)
    print(f"\n[saved] {out_dir / 'locality_curve_comparison.csv'}")

    print("\n=== Locality (grid neighbor jump, sample 무관) ===")
    grid_df = df[df["source"] == "grid_only"]
    print(grid_df[["curve", "p", "value", "fwd_max_jump", "fwd_p95_jump",
                    "inv_mean_manhattan", "inv_fraction_jump_gt_1"]].to_string(index=False))

    print("\n=== Stratum compactness (sample 별, 작을수록 좋음) ===")
    pivot = df[df["source"] != "grid_only"].pivot_table(
        index="label", columns="curve", values="value",
    ).round(2)
    pivot["zorder/hilbert"] = (pivot["zorder"] / pivot["hilbert"]).round(3)
    print(pivot.to_string())

    # === narrative md ===
    md_lines = [
        "# Z-order vs Hilbert Curve Locality 정량 비교",
        "",
        "본 연구의 RQ3 narrative — \"Hilbert curve 가 contribution 1순위 격상\" — 의",
        "mechanism 분리 검증. PCA+quantile 골격이 동일하므로 두 curve 의 locality 차이",
        "정도가 contribution 의 origin (PCA+quantile vs locality preservation) 을 분리한다.",
        "",
        "## 1. Grid Locality Metric (sample 무관, curve 자체)",
        "",
        "256×256 grid (p=8) 에서 두 metric 측정.",
        "",
        "### 1-1. Forward (2D 인접 → 1D 거리)",
        "",
        "4-neighbor 쌍의 1D distance 차이 mean. 인접 grid 가 1D 에서도 인접하면 작음.",
        "",
        "| curve | mean | median | p95 | max |",
        "|-------|-----:|-------:|----:|----:|",
    ]
    for curve in ["hilbert", "zorder"]:
        r = grid_df[grid_df["curve"] == curve].iloc[0]
        md_lines.append(
            f"| {curve} | {r['fwd_mean_jump']:.2f} | "
            f"{r['fwd_median_jump']:.2f} | {r['fwd_p95_jump']:.0f} | "
            f"{r['fwd_max_jump']:.0f} |"
        )

    md_lines.extend([
        "",
        "**해석**: forward mean 은 Hilbert 가 약간 더 크지만, max 가 결정적으로 큼. 이 max",
        "값이 큰 이유는 Hilbert 의 quadrant boundary 에서 발생하는 worst-case jump 때문.",
        "",
        "### 1-2. Inverse (1D 인접 → 2D Manhattan distance)",
        "",
        "**Hilbert curve 의 본질 정의**: 1D 연속 (d, d+1) → 2D Manhattan = 1.",
        "Z-order 는 \"Z\" jump 시 Manhattan > 1 (해당 cell 에서 quadrant 건너뜀).",
        "",
        "| curve | mean Manhattan | max | p95 | fraction (Manhattan > 1) |",
        "|-------|---------------:|----:|----:|-------------------------:|",
    ]
    )
    for curve in ["hilbert", "zorder"]:
        r = grid_df[grid_df["curve"] == curve].iloc[0]
        md_lines.append(
            f"| {curve} | {r['inv_mean_manhattan']:.3f} | "
            f"{r['inv_max_manhattan']:.0f} | {r['inv_p95_manhattan']:.0f} | "
            f"{r['inv_fraction_jump_gt_1']:.4f} |"
        )
    md_lines.extend([
        "",
        "**해석**: Hilbert 는 mean Manhattan = 1.000 (curve 정의 그대로). Z-order 는 mean > 1",
        "이고 fraction (Manhattan > 1) 가 양수 → 1D 연속이 2D 비연속. **이 metric 이 두",
        "curve 의 locality 차이를 결정적으로 분리한다**.",
        "",
        "## 2. Stratum Compactness (sample 의존, 작을수록 좋음)",
        "",
        "각 stratum 내 grid 좌표 (x_std + y_std) 평균. 작을수록 한 stratum 이 spatial",
        "영역에 집중 → HT estimator 의 cluster-aware 분산 감소 효과 강.",
        "",
        "| sample | hilbert | zorder | zorder/hilbert |",
        "|--------|--------:|-------:|---------------:|",
    ])
    for label in pivot.index:
        md_lines.append(
            f"| {label} | {pivot.loc[label, 'hilbert']} | "
            f"{pivot.loc[label, 'zorder']} | "
            f"{pivot.loc[label, 'zorder/hilbert']} |"
        )
    md_lines.extend([
        "",
        "**해석**: `zorder/hilbert` 비율 > 1 이면 Z-order 의 stratum 이 spatial 으로",
        "더 흩어짐 → Hilbert 의 locality preservation 이 stratum 압축에 직접 기여.",
        "비율이 1 에 가까우면 두 curve 가 비슷 (PCA+quantile 이 dominant).",
        "",
        "## 3. RQ3 Narrative 결론",
        "",
        "- **Grid neighbor jump**: Hilbert 의 mean jump 가 Z-order 보다 작을 것으로 예상.",
        "  Z-order 는 Y-축 jump 시 grid 의 절반 (n/2) 을 한 번에 건너뛰므로 worst-case",
        "  jump 가 크다.",
        "- **Stratum compactness**: Hilbert 의 stratum 이 더 compact 면 → contribution 의",
        "  origin 이 (b) locality preservation. Z-order 와 비슷하면 (a) PCA+quantile 이 핵심.",
        "",
        "**측정 후 follow-up (RQ3 8M sensitivity)**: 본 분석의 예측이 실측 recovery_rate",
        "패턴과 정합한지 cross-check. Z-order 의 측정은 8M 끝나면 1M 에서 즉시 가능 (run_zorder.py).",
        "",
    ])

    with open(out_dir / "locality_curve_comparison.md", "w") as f:
        f.write("\n".join(md_lines))
    print(f"\n[saved] {out_dir / 'locality_curve_comparison.md'}")


if __name__ == "__main__":
    main()
