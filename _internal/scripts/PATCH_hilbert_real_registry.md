# Patch — measure_paper_exact.py registry: hilbert rename + hilbert_real 추가

> 목적: ★3 hilbert (PCA 2D lex sort, fraud risk) → `pca2d_lex` rename, 진짜 Hilbert curve `hilbert_real` 추가
> 사용자 결정 (5/10 22:25): (C) 분리 검증 — "Hilbert curve 진짜 locality 효과 vs PCA proxy 효과"
> 사용자 confirm 후 메인 세션이 적용

## 변경 위치

`_internal/scripts/measure_paper_exact.py` L446-457 (현재 inline `hilbert` 분기)

## 현재 코드 (L446-457)

```python
    if method_name == "hilbert":
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/hilbert")
        # run_hilbert.py 의 PCA + Hilbert curve assignment
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2, random_state=seed)
        pca_vecs = pca.fit_transform(all_vecs)
        # Hilbert curve order에 매핑
        hilbert_order = np.argsort(pca_vecs[:, 0] * 1000 + pca_vecs[:, 1])  # simple proxy
        sids = np.zeros(len(all_vecs), dtype=np.int32)
        chunk_size = (len(all_vecs) + n_strata - 1) // n_strata
        for i, idx in enumerate(hilbert_order):
            sids[idx] = min(i // chunk_size, n_strata - 1)
        return sids
```

## 신규 코드

```python
    if method_name == "pca2d_lex":
        # 기존 ★3 hilbert 의 정직한 명칭 — PCA 2D + lex sort + chunk 분할
        # (handoff_v3 §1.1 #1: Hilbert curve 가 아님, naming fraud 회피)
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2, random_state=seed)
        pca_vecs = pca.fit_transform(all_vecs)
        order = np.argsort(pca_vecs[:, 0] * 1000 + pca_vecs[:, 1])
        sids = np.zeros(len(all_vecs), dtype=np.int32)
        chunk_size = (len(all_vecs) + n_strata - 1) // n_strata
        for i, idx in enumerate(order):
            sids[idx] = min(i // chunk_size, n_strata - 1)
        return sids

    if method_name == "hilbert_real":
        # 진짜 Hilbert curve (Wikipedia xy2d 표준) — handoff_v3 §0.2 ★3 정정
        # raw module: /mnt/hdd0/home/capstone2026/cache/rq3/hilbert/hilbert_curve.py
        # wrapper:    /mnt/hdd0/home/capstone2026/cache/rq3/method_hilbert_real.py
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from method_hilbert_real import assign_hilbert_real
        return assign_hilbert_real(all_vecs, n_strata=n_strata,
                                    hilbert_order=10, seed=seed)
```

## sed-style 정확한 patch (참고)

```diff
-    if method_name == "hilbert":
-        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/hilbert")
-        # run_hilbert.py 의 PCA + Hilbert curve assignment
+    if method_name == "pca2d_lex":
+        # 기존 ★3 hilbert 의 정직한 명칭 (handoff_v3 §1.1 #1: Hilbert ❌)
         from sklearn.decomposition import PCA
         pca = PCA(n_components=2, random_state=seed)
         pca_vecs = pca.fit_transform(all_vecs)
-        # Hilbert curve order에 매핑
-        hilbert_order = np.argsort(pca_vecs[:, 0] * 1000 + pca_vecs[:, 1])  # simple proxy
+        order = np.argsort(pca_vecs[:, 0] * 1000 + pca_vecs[:, 1])
         sids = np.zeros(len(all_vecs), dtype=np.int32)
         chunk_size = (len(all_vecs) + n_strata - 1) // n_strata
-        for i, idx in enumerate(hilbert_order):
+        for i, idx in enumerate(order):
             sids[idx] = min(i // chunk_size, n_strata - 1)
         return sids
+
+    if method_name == "hilbert_real":
+        # 진짜 Hilbert curve (Wikipedia xy2d 표준)
+        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
+        from method_hilbert_real import assign_hilbert_real
+        return assign_hilbert_real(all_vecs, n_strata=n_strata,
+                                    hilbert_order=10, seed=seed)
```

## 부수 변경 사항

1. **method portfolio**: 기존 `hilbert` 1개 → `pca2d_lex` + `hilbert_real` 2개 (★3 분리 검증)
2. **paradigm 매핑**: 둘 다 P2 Spatial 유지 (PCA 2D 기반 stratification 공통)
3. **★ 표기**:
   - `pca2d_lex`: ★ 제거 (paradigm anchor 자격 박탈, 단순 proxy baseline)
   - `hilbert_real`: ★3 승격 (진짜 Hilbert curve = paradigm anchor 자격)
4. **outcome label**: 측정 후 비교 — "진짜 Hilbert locality > PCA 2D proxy" 검증 가능

## 측정 plan 영향

- 추가 method 1개 (hilbert_real) → 측정 cell 수 +N (current portfolio 의 (DEEP/SIFT/SSN/Wiki) × (SF=10/100) = 8 cell 추가 예상)
- 진행 중 22 procs 영향 X (registry 정정 = 신규 cell 만 추가, 기존 진행 계속)

## 검증 결과 (smoke test, 100K × 96d synthetic)

| 항목 | hilbert_real | pca2d_lex | 차이 |
|---|---|---|---|
| stratum count balance (max-min) | 259 (quantile) | 0 (chunk exact) | quantile 균등성 약간 손실 |
| same stratum_id ratio | — | — | **0.0101** (random 0.05 보다 낮음 → 거의 다른 묶음) |
| avg intra-stratum L2 | **9.09** | 13.54 | **ratio 0.67** = hilbert_real 33% 더 강한 locality |
| 결정론 | ✓ | ✓ | (둘 다 deterministic) |

→ 진짜 Hilbert curve 가 측정 가능한 locality 차이 확인. 흥미로운 finding 후보.
