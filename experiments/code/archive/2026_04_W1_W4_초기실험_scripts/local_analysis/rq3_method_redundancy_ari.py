#!/usr/bin/env python3
"""
RQ3 method 간 정보 redundancy 분석 (Adjusted Rand Index).

10+ method 가 같은 row 에 같은 stratum 부여하는가? ARI 가 1.0 → 완전 동의 (정보
redundant), 0.0 → 완전 독립. 본 분석은 두 method 가 capture 하는 정보의 *겹침*
을 정량.

PG 무관 — synthetic data (DEEP/SIFT 분포 모방) 에서 직접 fit + assign.

분석 목적:
1. **Hilbert vs Z-order vs PCA-1D** ARI: PCA + curve 의 contribution origin 분리
   (W1-C 의 보강 — locality vs PCA 의 정량).
2. **MiniBatch vs MiniBatch-partial** ARI: batch vs streaming 의 정보 차이 — partial_fit
   채택의 production cost 정량.
3. **Hybrid vs MiniBatch + Hilbert** ARI: hybrid 가 두 method 의 정보 정확히 합치는지.
4. **method 의 cluster** (계층적): 비슷한 method 들의 그룹 발견 — 본 연구의 7-way
   measurement 가 "정보적으로 7개 다른 method" 인지 검증.

산출:
  - rq3_method_redundancy_ari.csv  (pairwise ARI matrix)
  - rq3_method_redundancy_ari.md   (narrative + clustering)
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RQ3 = ROOT / "Capstone" / "experiments" / "code" / "rq3"
if not RQ3.exists():
    RQ3 = Path(__file__).resolve().parent.parent / "rq3"
sys.path.insert(0, str(RQ3))


def _fit_methods(samples: np.ndarray, all_vecs: np.ndarray, seed: int = 42) -> dict:
    """모든 method 를 fit + assign → dict[name → stratum_ids]."""
    out: dict[str, np.ndarray] = {}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        warnings.simplefilter("ignore", category=FutureWarning)

        # MiniBatch (batch fit)
        from offline_simple.minibatch_kmeans import (
            train_minibatch_kmeans, assign_minibatch as assign_mb,
        )
        out["minibatch"] = assign_mb(
            train_minibatch_kmeans(samples, n_clusters=20, random_state=seed), all_vecs,
        )

        # MiniBatch partial_fit
        from offline_simple.minibatch_partial import (
            train_minibatch_partial, assign_minibatch as assign_mbp,
        )
        out["minibatch_partial"] = assign_mbp(
            train_minibatch_partial(samples, n_clusters=20, chunk_size=500, random_state=seed),
            all_vecs,
        )

        # Random Projection
        from offline_simple.random_projection import (
            make_projection, assign_random_projection,
        )
        out["random_proj"] = assign_random_projection(
            make_projection(samples.shape[1], k=20, seed=seed), all_vecs,
        )

        # PCA-1D
        from pca1d.pca1d_quantile import fit_pca1d_mapper, assign_pca1d
        out["pca1d"] = assign_pca1d(
            fit_pca1d_mapper(samples, n_strata=20, seed=seed), all_vecs,
        )

        # Hilbert
        from hilbert.hilbert_curve import fit_hilbert_mapper, assign_hilbert
        out["hilbert"] = assign_hilbert(
            fit_hilbert_mapper(samples, n_strata=20, seed=seed), all_vecs,
        )

        # Z-order
        from zorder.zorder_curve import fit_zorder_mapper, assign_zorder
        out["zorder"] = assign_zorder(
            fit_zorder_mapper(samples, n_strata=20, seed=seed), all_vecs,
        )

        # Hybrid
        from hybrid.minibatch_hilbert import fit_hybrid_mapper, assign_hybrid
        out["hybrid"] = assign_hybrid(
            fit_hybrid_mapper(samples, k_outer=5, k_inner=4, seed=seed), all_vecs,
        )

        # KD-tree
        from kdtree.kdtree_partition import fit_kdtree_partition, assign_kdtree
        out["kdtree"] = assign_kdtree(
            fit_kdtree_partition(samples, n_strata=20, seed=seed), all_vecs,
        )

        # PQ
        from pq.product_quantization import fit_pq_mapper, assign_pq
        out["pq"] = assign_pq(
            fit_pq_mapper(samples, n_strata=20, m=2, seed=seed), all_vecs,
        )

        # LSH (k=20)
        from lsh.lsh import make_hyperplanes, assign_lsh
        out["lsh"] = assign_lsh(
            make_hyperplanes(samples.shape[1], k=20, seed=seed), all_vecs, k=20,
        )

        # 5/7 새벽 추가 method (Spectral / BIRCH / GMM / HDBSCAN / Sobol / SparseRP)
        try:
            from spectral.spectral_clustering import fit_spectral, assign_spectral
            out["spectral"] = assign_spectral(
                fit_spectral(samples, n_strata=20, seed=seed), all_vecs,
            )
        except Exception as e:
            print(f"  [skip] spectral: {type(e).__name__}: {e}")
        try:
            from birch.birch_partition import fit_birch, assign_birch
            out["birch"] = assign_birch(
                fit_birch(samples, n_strata=20, threshold=0.5, seed=seed), all_vecs,
            )
        except Exception as e:
            print(f"  [skip] birch: {type(e).__name__}: {e}")
        try:
            from gmm.gmm_partition import fit_gmm, assign_gmm
            out["gmm"] = assign_gmm(
                fit_gmm(samples, n_strata=20, seed=seed), all_vecs,
            )
        except Exception as e:
            print(f"  [skip] gmm: {type(e).__name__}: {e}")
        try:
            from hdbscan.hdbscan_partition import fit_hdbscan, assign_hdbscan
            out["hdbscan"] = assign_hdbscan(
                fit_hdbscan(samples, n_strata=20, min_cluster_size=50, seed=seed),
                all_vecs,
            )
        except Exception as e:
            print(f"  [skip] hdbscan: {type(e).__name__}: {e}")
        try:
            from sobol.sobol_stratification import fit_sobol, assign_sobol
            out["sobol"] = assign_sobol(
                fit_sobol(samples, n_strata=20, seed=seed), all_vecs,
            )
        except Exception as e:
            print(f"  [skip] sobol: {type(e).__name__}: {e}")
        try:
            from sparserp.sparse_random_projection import (
                fit_sparse_rp, assign_sparse_rp,
            )
            out["sparse_rp"] = assign_sparse_rp(
                fit_sparse_rp(samples.shape[1], n_strata=20, seed=seed),
                all_vecs, k=20,
            )
        except Exception as e:
            print(f"  [skip] sparse_rp: {type(e).__name__}: {e}")

    return out


def pairwise_ari(assignments: dict) -> pd.DataFrame:
    """method 쌍의 ARI matrix."""
    names = list(assignments.keys())
    n = len(names)
    matrix = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            ari = adjusted_rand_score(assignments[names[i]], assignments[names[j]])
            matrix[i, j] = ari
            matrix[j, i] = ari
    return pd.DataFrame(matrix, index=names, columns=names)


def hierarchical_groups(ari_df: pd.DataFrame, threshold: float = 0.3) -> list[list[str]]:
    """ARI > threshold 인 method 끼리 group. simple greedy."""
    names = ari_df.index.tolist()
    visited: set[str] = set()
    groups = []
    for name in names:
        if name in visited:
            continue
        group = [name]
        visited.add(name)
        for other in names:
            if other == name or other in visited:
                continue
            if ari_df.loc[name, other] > threshold:
                # 같은 group 내 모두와 threshold 이상이어야 group 멤버 (single-link 가 아님)
                # 단순 첫 멤버 기준 (loose)
                group.append(other)
                visited.add(other)
        groups.append(group)
    return groups


def main():
    out_dir = ROOT / "experiments" / "results" / "rq3_agnostic"
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(42)

    # === 3 데이터셋 시뮬 ===
    print("=" * 70)
    print("RQ3 method 간 정보 redundancy 분석 (Adjusted Rand Index)")
    print("=" * 70)

    datasets_syn = {
        "iid_96d": (rng.standard_normal((10000, 96)).astype(np.float32),
                    rng.standard_normal((50000, 96)).astype(np.float32)),
    }

    # clustered DEEP-like
    centers_deep = rng.standard_normal((20, 96)).astype(np.float32) * 5
    sizes_deep = rng.integers(2000, 5000, size=20)
    deep_like = np.vstack([
        rng.standard_normal((s, 96)).astype(np.float32) + c
        for c, s in zip(centers_deep, sizes_deep)
    ])
    rng.shuffle(deep_like)
    datasets_syn["deep_like_clustered_96d"] = (deep_like[:5000], deep_like)

    # skewed SIFT-like
    centers_sift = rng.standard_normal((20, 128)).astype(np.float32) * 5
    weights_sift = rng.dirichlet(np.ones(20) * 0.3)  # high skew
    sizes_sift = (weights_sift * 50000).astype(int)
    sizes_sift = np.maximum(sizes_sift, 100)
    sift_like = np.vstack([
        rng.standard_normal((s, 128)).astype(np.float32) + c
        for c, s in zip(centers_sift, sizes_sift)
    ])
    rng.shuffle(sift_like)
    datasets_syn["sift_like_skewed_128d"] = (sift_like[:5000], sift_like)

    all_ari_dfs: dict[str, pd.DataFrame] = {}
    for name, (samples, all_vecs) in datasets_syn.items():
        print(f"\n[fit] {name}: samples={samples.shape}, all_vecs={all_vecs.shape}")
        assignments = _fit_methods(samples, all_vecs, seed=42)
        print(f"  assigned {len(assignments)} methods")
        ari_df = pairwise_ari(assignments)
        all_ari_dfs[name] = ari_df

    # === 평균 ARI matrix (모든 dataset) ===
    avg_ari = sum(all_ari_dfs.values()) / len(all_ari_dfs)
    avg_ari = avg_ari.round(3)

    print("\n=== Pairwise ARI (3 dataset 평균) ===")
    print(avg_ari.to_string())
    avg_ari.to_csv(out_dir / "rq3_method_redundancy_ari.csv")
    print(f"\n[saved] {out_dir / 'rq3_method_redundancy_ari.csv'}")

    # 각 dataset 별로도 저장
    for name, df in all_ari_dfs.items():
        df.round(3).to_csv(out_dir / f"rq3_method_redundancy_ari_{name}.csv")

    # === group 분석 (clustered dataset 의 ARI 사용) ===
    cluster_ari = all_ari_dfs.get("deep_like_clustered_96d", avg_ari)
    groups = hierarchical_groups(cluster_ari, threshold=0.2)
    print(f"\n=== 정보 grouping (ARI > 0.2 on clustered dataset) ===")
    for i, g in enumerate(groups):
        print(f"  group {i}: {g}")

    # === 핵심 pair 분석 ===
    print("\n=== 핵심 pair ARI (clustered dataset) ===")
    interesting = [
        ("hilbert", "zorder"),
        ("hilbert", "pca1d"),
        ("zorder", "pca1d"),
        ("minibatch", "minibatch_partial"),
        ("hybrid", "minibatch"),
        ("hybrid", "hilbert"),
        ("kdtree", "minibatch"),
        ("pq", "minibatch"),
        ("lsh", "random_proj"),
        ("hilbert", "minibatch"),
    ]
    pair_results = []
    for a, b in interesting:
        if a in cluster_ari.columns and b in cluster_ari.columns:
            ari_iid = all_ari_dfs["iid_96d"].loc[a, b]
            ari_cl = all_ari_dfs["deep_like_clustered_96d"].loc[a, b]
            ari_sk = all_ari_dfs["sift_like_skewed_128d"].loc[a, b]
            print(f"  {a:20s} ↔ {b:20s}: iid={ari_iid:+.3f}, "
                  f"clustered={ari_cl:+.3f}, skewed={ari_sk:+.3f}")
            pair_results.append({
                "method_a": a, "method_b": b,
                "ari_iid": ari_iid, "ari_clustered": ari_cl, "ari_skewed": ari_sk,
            })
    pd.DataFrame(pair_results).to_csv(out_dir / "rq3_method_redundancy_ari_pairs.csv", index=False)

    # === narrative md ===
    md = [
        "# RQ3 Method 간 정보 Redundancy 분석 (Adjusted Rand Index)",
        "",
        "10 RQ3 method 가 같은 row 에 같은 stratum 부여하는 정도를 ARI 로 정량.",
        "ARI = 1.0 → 완전 동의 (정보 redundant). ARI = 0.0 → 완전 독립.",
        "",
        "synthetic data 3종 (iid 96d / clustered DEEP-like 96d / skewed SIFT-like 128d)",
        "에서 same fit sample (5K) + same all_vecs 로 fit + assign, pairwise ARI 측정.",
        "",
        "## Pairwise ARI (clustered DEEP-like, 5K samples × 50K all_vecs)",
        "",
        "| method ↓ \\ method → | " + " | ".join(cluster_ari.columns) + " |",
        "|" + "|".join(["---"] * (len(cluster_ari.columns) + 1)) + "|",
    ]
    for idx in cluster_ari.index:
        row = [f"`{idx}`"] + [f"{cluster_ari.loc[idx, col]:.2f}" for col in cluster_ari.columns]
        md.append("| " + " | ".join(row) + " |")

    md.extend([
        "",
        "## 핵심 pair 정보 redundancy",
        "",
        "| pair | iid 96d | clustered 96d | skewed 128d | 해석 |",
        "|------|--------:|--------------:|------------:|------|",
    ])
    interpretations = {
        ("hilbert", "zorder"): "PCA+quantile 동일, curve 만 다름 → ARI 가 PCA 효과 dominance 정량",
        ("hilbert", "pca1d"): "1D vs 2D curve — PCA 차원 효과",
        ("zorder", "pca1d"): "1D vs 2D curve (curve X) — Z-order 의 curve 효과",
        ("minibatch", "minibatch_partial"): "batch vs streaming — partial_fit production cost",
        ("hybrid", "minibatch"): "hybrid 가 outer KMeans 정보 보존?",
        ("hybrid", "hilbert"): "hybrid 가 inner Hilbert 정보 보존?",
        ("kdtree", "minibatch"): "tree paradigm vs cluster paradigm",
        ("pq", "minibatch"): "PQ 가 sub-vector 독립 학습 → MiniBatch 와 차이",
        ("lsh", "random_proj"): "둘 다 hyperplane 기반",
        ("hilbert", "minibatch"): "PCA(2D) curve vs full-D KMeans",
    }
    for r in pair_results:
        a, b = r["method_a"], r["method_b"]
        intp = interpretations.get((a, b), "")
        md.append(f"| `{a}` ↔ `{b}` | {r['ari_iid']:+.3f} | "
                  f"{r['ari_clustered']:+.3f} | {r['ari_skewed']:+.3f} | {intp} |")

    md.extend([
        "",
        "## 정보 grouping (ARI > 0.2 on clustered dataset)",
        "",
    ])
    for i, g in enumerate(groups):
        md.append(f"- **group {i}**: {', '.join('`' + m + '`' for m in g)}")

    md.extend([
        "",
        "## RQ3 narrative 결론",
        "",
        "1. **Hilbert vs Z-order ARI** 가 클수록 → curve 자체보다 PCA+quantile 가 핵심.",
        "   작을수록 → curve 의 locality 가 결정적 (W1-C 의 mechanism 분석과 cross-check).",
        "2. **Hilbert vs PCA-1D ARI** 가 클수록 → 2D curve 가 1D quantile 대비 추가 정보 X.",
        "   작을수록 → 2D 가 정보 추가.",
        "3. **MiniBatch vs MiniBatch-partial ARI** 가 클수록 → streaming 으로 batch 와",
        "   동일 cluster 회복 가능 (partial_fit production 채택 정당화).",
        "4. **Hybrid vs MiniBatch / Hilbert ARI** — hybrid 가 어느 쪽 information 더 가짐?",
        "   양쪽 모두 우수면 정보 직교 결합 성공. 한쪽 dominant 면 information loss.",
        "5. **method group**: 비슷한 method 들이 같은 group 에 모이면 본 연구의 N-way",
        "   measurement 가 정보적으로 N 개 method 인지 평가.",
        "",
        "**측정 결과 비교**: 본 분석의 ARI 패턴이 실측 recovery_rate 패턴과 일치하면",
        "narrative 강화. 다르면 — ARI 가 stratum 동의 정도만 측정, q_error 효과는 추가",
        "factor (stratum 내 variance 등) 라는 별도 분석 필요.",
        "",
    ])

    with open(out_dir / "rq3_method_redundancy_ari.md", "w") as f:
        f.write("\n".join(md))
    print(f"[saved] {out_dir / 'rq3_method_redundancy_ari.md'}")


if __name__ == "__main__":
    main()
