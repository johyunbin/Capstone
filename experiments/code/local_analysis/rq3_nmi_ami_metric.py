#!/usr/bin/env python3
"""
RQ3 method 간 정보 redundancy — NMI / AMI metric 보강 (W3 P2).

ARI orthogonality ranking 의 robustness check. 동일 synthetic data + 동일
`_fit_methods` (rq3_method_redundancy_ari.py 재사용) 로 partition label
일관 확보, ARI / NMI / AMI 3 metric 동시 계산.

- NMI (Normalized MI): chance correction X, 0~1 normalized
- AMI (Adjusted MI): chance correction O — ARI 의 information theoretic 대응
- ARI (Adjusted Rand): chance correction O — pairwise agreement

3 condition (iid 96d / clustered DEEP-like 96d / skewed SIFT-like 128d) avg
기준. 3 metric 모두 sparse_rp 1위 / cluster method redundant 면 본 연구의
7-way 정보 직교성 narrative 강화 (자문 메일 / 보고서 보강 input).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import (
    adjusted_mutual_info_score,
    adjusted_rand_score,
    normalized_mutual_info_score,
)

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RQ3 = ROOT / "Capstone" / "experiments" / "code" / "rq3"
if not RQ3.exists():
    RQ3 = Path(__file__).resolve().parent.parent / "rq3"
sys.path.insert(0, str(RQ3))

# 같은 디렉토리 ARI driver 의 _fit_methods 재사용 → assignments 100% 동일성 확보
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rq3_method_redundancy_ari import _fit_methods  # noqa: E402

CONDITION_SHORT = {
    "iid_96d": "iid",
    "deep_like_clustered_96d": "clust",
    "sift_like_skewed_128d": "skew",
}


def pairwise_metric(assignments: dict, metric_fn) -> pd.DataFrame:
    """method 쌍의 metric matrix (대각=1.0)."""
    names = list(assignments.keys())
    n = len(names)
    matrix = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            v = metric_fn(assignments[names[i]], assignments[names[j]])
            matrix[i, j] = v
            matrix[j, i] = v
    return pd.DataFrame(matrix, index=names, columns=names)


def avg_offdiag(df: pd.DataFrame) -> pd.Series:
    """각 method 의 평균 pairwise score (자기 제외) — 낮을수록 직교."""
    n = len(df)
    s = df.values.sum(axis=1) - np.diag(df.values)
    return pd.Series(s / (n - 1), index=df.index)


def _build_synthetic_datasets(rng: np.random.Generator) -> dict:
    """rq3_method_redundancy_ari.main 의 dataset 생성 logic 복제 (same RNG → same data)."""
    datasets = {
        "iid_96d": (
            rng.standard_normal((10000, 96)).astype(np.float32),
            rng.standard_normal((50000, 96)).astype(np.float32),
        ),
    }

    centers_deep = rng.standard_normal((20, 96)).astype(np.float32) * 5
    sizes_deep = rng.integers(2000, 5000, size=20)
    deep_like = np.vstack([
        rng.standard_normal((s, 96)).astype(np.float32) + c
        for c, s in zip(centers_deep, sizes_deep)
    ])
    rng.shuffle(deep_like)
    datasets["deep_like_clustered_96d"] = (deep_like[:5000], deep_like)

    centers_sift = rng.standard_normal((20, 128)).astype(np.float32) * 5
    weights_sift = rng.dirichlet(np.ones(20) * 0.3)
    sizes_sift = (weights_sift * 50000).astype(int)
    sizes_sift = np.maximum(sizes_sift, 100)
    sift_like = np.vstack([
        rng.standard_normal((s, 128)).astype(np.float32) + c
        for c, s in zip(centers_sift, sizes_sift)
    ])
    rng.shuffle(sift_like)
    datasets["sift_like_skewed_128d"] = (sift_like[:5000], sift_like)

    return datasets


def _build_narrative(rank_df: pd.DataFrame, ari_avg: pd.DataFrame,
                     nmi_avg: pd.DataFrame, ami_avg: pd.DataFrame) -> str:
    md: list[str] = []
    md.append("# RQ3 Method Redundancy — NMI / AMI Robustness Check (W3 P2)")
    md.append("")
    md.append("ARI orthogonality ranking 의 robustness 점검. 동일 synthetic data +")
    md.append("동일 `_fit_methods` (`rq3_method_redundancy_ari.py` 재사용) 로 partition")
    md.append("label 일관 확보, ARI / NMI / AMI 3 metric 동시 계산.")
    md.append("")
    md.append("- **NMI** (Normalized MI): chance correction X, 0~1 normalized")
    md.append("- **AMI** (Adjusted MI): chance correction O — ARI 의 information theoretic 대응")
    md.append("- **ARI** (Adjusted Rand): chance correction O — pairwise agreement (기존 metric)")
    md.append("")
    md.append("3 condition (iid 96d / clustered 96d / skewed 128d) avg 기준.")
    md.append("")

    md.append("## Orthogonality Ranking — avg pairwise off-diag (lower = more orthogonal)")
    md.append("")
    md.append("| method | ARI_avg | rank | NMI_avg | rank | AMI_avg | rank |")
    md.append("|---|---:|---:|---:|---:|---:|---:|")
    rank_sorted = rank_df.sort_values("ARI_rank")
    for m in rank_sorted.index:
        r = rank_sorted.loc[m]
        md.append(
            f"| `{m}` | {r['ARI_avg']:+.3f} | {int(r['ARI_rank'])} | "
            f"{r['NMI_avg']:+.3f} | {int(r['NMI_rank'])} | "
            f"{r['AMI_avg']:+.3f} | {int(r['AMI_rank'])} |"
        )
    md.append("")

    top1_ari = rank_df["ARI_rank"].idxmin()
    top1_nmi = rank_df["NMI_rank"].idxmin()
    top1_ami = rank_df["AMI_rank"].idxmin()

    md.append("## Robustness 점검")
    md.append("")
    md.append(f"- **Top-1 (가장 직교)**: ARI=`{top1_ari}`, NMI=`{top1_nmi}`, AMI=`{top1_ami}`")
    if top1_ari == top1_nmi == top1_ami:
        md.append(f"  → **3 metric 모두 일치** — 직교성 1위 결과 robust.")
    else:
        md.append("  → 불일치 — metric 별 ranking 해석 차이 확인 필요.")
    md.append("")

    rho_ari_nmi = spearmanr(rank_df["ARI_rank"], rank_df["NMI_rank"]).correlation
    rho_ari_ami = spearmanr(rank_df["ARI_rank"], rank_df["AMI_rank"]).correlation
    rho_nmi_ami = spearmanr(rank_df["NMI_rank"], rank_df["AMI_rank"]).correlation
    md.append("- **Spearman rank correlation** (3 metric ranking 일관성)")
    md.append(f"  - ARI ↔ NMI: ρ = {rho_ari_nmi:+.3f}")
    md.append(f"  - ARI ↔ AMI: ρ = {rho_ari_ami:+.3f}  (chance correction 동일 — 가장 유사 기대)")
    md.append(f"  - NMI ↔ AMI: ρ = {rho_nmi_ami:+.3f}")
    md.append("")

    cluster_methods = [
        m for m in ["minibatch", "minibatch_partial", "birch", "spectral", "hdbscan", "gmm"]
        if m in rank_df.index
    ]
    md.append("- **Cluster paradigm method redundancy** (3 metric avg off-diag, ≥0.5 = redundant)")
    md.append("")
    md.append("  | method | ARI_avg | NMI_avg | AMI_avg |")
    md.append("  |---|---:|---:|---:|")
    for m in cluster_methods:
        r = rank_df.loc[m]
        md.append(f"  | `{m}` | {r['ARI_avg']:+.3f} | {r['NMI_avg']:+.3f} | {r['AMI_avg']:+.3f} |")
    md.append("")

    md.append("## 3-condition별 NMI/AMI matrix")
    md.append("")
    md.append("- iid 96d: `rq3_method_redundancy_{nmi,ami}_iid.csv`")
    md.append("- clustered 96d: `rq3_method_redundancy_{nmi,ami}_clust.csv`")
    md.append("- skewed 128d: `rq3_method_redundancy_{nmi,ami}_skew.csv`")
    md.append("- 3-condition 평균: `rq3_method_redundancy_{nmi,ami}.csv`")
    md.append("- 3 metric ranking 비교: `rq3_method_redundancy_metric_ranking.csv`")
    md.append("")

    md.append("## 결론 — RQ3 7-way 정보 직교성 narrative")
    md.append("")
    md.append("3 metric (ARI / NMI / AMI) 가 같은 ranking 을 산출하면, 본 연구의 7-way")
    md.append("ablation (offline 4 / online 2 / weight 1) 이 정보적으로 직교한다는 narrative")
    md.append("는 단일 metric 의 artifact 가 아니라 robust 한 결과다. 특히 AMI 가 ARI 와")
    md.append("유사하면서 (chance correction 동일) NMI 와도 일치하면, '본 분석 결과는")
    md.append("metric 선택에 둔감하다' 는 자문 메일 / 보고서 보강 narrative 가 가능.")
    md.append("")
    md.append("기존 ARI 5 CSV 는 보존, NMI/AMI 8 CSV + ranking CSV 1 + summary md 만 추가.")
    md.append("")
    return "\n".join(md)


def main() -> None:
    out_dir = ROOT / "experiments" / "results" / "rq3_agnostic"
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(42)

    print("=" * 70)
    print("RQ3 NMI / AMI metric (ARI orthogonality robustness check, W3 P2)")
    print("=" * 70)

    datasets_syn = _build_synthetic_datasets(rng)

    nmi_dfs: dict[str, pd.DataFrame] = {}
    ami_dfs: dict[str, pd.DataFrame] = {}
    ari_dfs: dict[str, pd.DataFrame] = {}

    for name, (samples, all_vecs) in datasets_syn.items():
        print(f"\n[fit] {name}: samples={samples.shape}, all_vecs={all_vecs.shape}")
        assignments = _fit_methods(samples, all_vecs, seed=42)
        print(f"  assigned {len(assignments)} methods: {list(assignments.keys())}")

        short = CONDITION_SHORT[name]
        nmi_dfs[short] = pairwise_metric(assignments, normalized_mutual_info_score).round(3)
        ami_dfs[short] = pairwise_metric(assignments, adjusted_mutual_info_score).round(3)
        ari_dfs[short] = pairwise_metric(assignments, adjusted_rand_score).round(3)

        nmi_dfs[short].to_csv(out_dir / f"rq3_method_redundancy_nmi_{short}.csv")
        ami_dfs[short].to_csv(out_dir / f"rq3_method_redundancy_ami_{short}.csv")
        print(f"  [saved] rq3_method_redundancy_{{nmi,ami}}_{short}.csv")

    nmi_avg = (sum(nmi_dfs.values()) / len(nmi_dfs)).round(3)
    ami_avg = (sum(ami_dfs.values()) / len(ami_dfs)).round(3)
    ari_avg = (sum(ari_dfs.values()) / len(ari_dfs)).round(3)

    nmi_avg.to_csv(out_dir / "rq3_method_redundancy_nmi.csv")
    ami_avg.to_csv(out_dir / "rq3_method_redundancy_ami.csv")
    print(f"\n[saved] rq3_method_redundancy_{{nmi,ami}}.csv (3-condition avg)")

    rank_ari = avg_offdiag(ari_avg)
    rank_nmi = avg_offdiag(nmi_avg)
    rank_ami = avg_offdiag(ami_avg)

    rank_df = pd.DataFrame({
        "ARI_avg": rank_ari,
        "ARI_rank": rank_ari.rank(method="min").astype(int),
        "NMI_avg": rank_nmi,
        "NMI_rank": rank_nmi.rank(method="min").astype(int),
        "AMI_avg": rank_ami,
        "AMI_rank": rank_ami.rank(method="min").astype(int),
    }).round(3).sort_values("ARI_rank")

    print("\n=== Method orthogonality ranking (lower = more orthogonal, 3-cond avg) ===")
    print(rank_df.to_string())

    rank_df.to_csv(out_dir / "rq3_method_redundancy_metric_ranking.csv")
    print(f"\n[saved] rq3_method_redundancy_metric_ranking.csv")

    md = _build_narrative(rank_df, ari_avg, nmi_avg, ami_avg)
    summary_path = out_dir / "rq3_method_redundancy_nmi_ami_summary.md"
    with open(summary_path, "w") as f:
        f.write(md)
    print(f"[saved] {summary_path}")


if __name__ == "__main__":
    main()
