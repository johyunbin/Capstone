# Handoff v9 — 5/8 10:35 KST (10 cell narrative 재정의 + build_yfcc 폐기 완료 + sf100 채림 요청)

> 5/7 23:00 시작 야간 자동화. 5/8 08:10 finalize. **5/8 09:50 4종 빈틈 회복 완료. 5/8 10:18 narrative 재정의 (10 cell 메인 + multi 부록 + build_yfcc 폐기). 5/8 10:35 sf100 채림 요청 결정 + build_yfcc 흔적 전량 회수 완료.** 회의 5/8 19:00 KST (~8.5h 여유).
>
> **10:35 변화 (사용자 결정 — sf100 finalize)**:
> - **sf100 = 채림 석사님께 정본 요청** (자체 다운로드 X) — source 일관성 + 다운로드 부담 회피
> - **build_yfcc 자체 다운로드 흔적 전량 회수 완료**: raw fbin 40GB + PG 테이블 partsupp_yfcc_pca_{1,10} (15GB) + parquet 119개 + done flag 3개 + tmux yfcc_dl session 모두 폐기
> - **메인 narrative = 10 cell** 집중 유지
>
> **10:18 변화 (사용자 결정)**:
> - **메인 narrative = 10 cell** (DEEP / SIFT / SSN / WIKI / YFCC × sf1 / sf10) — Exqutor 5 dataset × 2 scale 매트릭스
> - **YFCC = 채림 적재본 단일 정본** (`partsupp_yfcc_{1,10}` 기반)
> - **build_yfcc.py 다운로드 결과 폐기** — 자체 build 적재본 (YFCC_DL) 본 연구에서 사용하지 않음
> - **multi 3 cell = 추가 자료** (deep_sift_10, deep_wiki_10, multi_join_deep_wiki)
> - **sf100 다운로드 = 회의 후 진행** (10 cell 마무리 우선)
>
> **09:50 변화 (08:10 → 09:50, 유지)**:
> - **A1 YFCC vs YFCC_DL 비교** ✅ — `compare_yfcc_distributions.py` 첫 실행. norm A=1819 vs B=0.73, cosine ≈ 0 (직교).
> - **A2 multi 3 cell narrative 회복** ✅ — analyze_multi_w4.py null 원인 = path mismatch (rq1 vs rq3). 직접 parsing → multi_w4_recovered.json 11KB.
> - **A3 RQ2 5mode 13 cell paired CI** ✅ — rq2_5mode_recovered.json 91KB.
> - **A3 RQ1 13 cell 단조성 통계** ✅ — 13/13 ρ < 0 (100% 부호 일관, 범위 -0.366~-0.609).
> - **A4 OPTICS sf10 missing** ✅ → footnote 처리 결정.
> - **master_v6**: 465 lines 31KB → 623 lines 42KB → **10 cell 재정의 후 ~660 lines 추정**.

## 0. 즉시 결정 필요 actions (사용자 — 10:18 KST 갱신)

### 사용자 결정 (5/8 10:18 핵심)

1. **YFCC = 채림 적재본 단일 정본** (`partsupp_yfcc_{1,10}` 기반)
2. **build_yfcc.py 다운로드 결과 폐기** — 자체 build YFCC_DL 적재본은 본 연구에서 사용하지 않음 (5/8 AM agent M 결과 cosine ≈ 0 직교 검증 후 폐기 결정)
3. **메인 narrative = 5 dataset × 2 scale = 10 cell**: DEEP / SIFT / SSN / WIKI / YFCC × sf1 / sf10
4. **multi 3 cell = 추가 자료** (deep_sift_10, deep_wiki_10, multi_join_deep_wiki)
5. **sf100 다운로드 보류** — 회의 후 (10 cell 마무리 우선, BigANN base.80M.u8bin 권장 — 채림 정본 동일 source)

### 자료 finalize 상태

1. ✅ **빈틈 4종 회복 완료** — A1 YFCC vs YFCC_DL / A2 multi 3 cell / A3 RQ1 + RQ2 5mode / A4 OPTICS footnote
2. ✅ **master_v6 narrative 재정의** — 10 cell 메인 + multi 3 cell 부록 (build_yfcc 폐기)
3. ✅ **차트/PPTX rebuild** (09:47/09:49) — agent O 가 갱신 진행 중
4. **PPT 시각 검증** (Keynote 열어서 15장 흐름 확인) ← 사용자 결정
5. **YFCC sf10 retry** — 별도 sub-agent 처리 중 (~16:00 ETA, 메인 narrative 의 마지막 cell, 채림 정본 단일)
6. **Phase 2/3 시작 시점**: 회의 자료 ready. 10 cell 1 cell (yfcc_sf10) 진행 중

---

## 1. 산출물 상태 (5/8 09:50 KST 기준)

### 핵심 4종 (모두 mtime 09:47~09:49 갱신)

| 파일 | 사이즈 | 상태 |
|---|---|---|
| `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md` | mtime 10:18 갱신 | ✅ 10 cell 메인 × 4 method + §6 RQ1 11 cell + §7 RQ2 5mode 11 cell + §multi 3 cell + §yfcc_source (build_yfcc 폐기) |
| `_internal/_w4_partial_summary.csv` | 1235 rows / mtime 08:10 (변경 X, YFCC_DL 행은 narrative 에서 사용 X) | ✅ raw 측정값 유지 |
| `_internal/multi_w4_recovered.json` | **11 KB** / 09:44 | ✅ NEW — multi 3 cell × 4 method paired CI 직접 parsing |
| `_internal/rq2_5mode_recovered.json` | **91 KB** / 09:44 | ✅ NEW — RQ2 5mode 13 cell 모든 paired CI |
| `_internal/rq1_monotone_recovered.json` | **25 KB** / 09:44 | ✅ NEW — RQ1 13 cell Spearman + median qe |
| `_internal/yfcc_distribution_compare.json` | 693 B / 09:44 | ✅ NEW — A1 첫 실행 결과 |
| `_internal/yfcc_compare_20260508.log` | 903 B / 09:44 | ✅ NEW — script 실행 로그 |
| `submission/_drafts/속도는벡터_5월8일회의_v1.pptx` | 468,296 B / 15 slides / 5 images / mtime 09:49 | ✅ S6/S8/S10/S11/S14 차트 임베드 |
| `experiments/figures/w4_partial/*.png` | 13 PNG / mtime 09:47 | ✅ rank chart + heatmap + distribution |
| `experiments/figures/native_pptx_charts/*.png` | 5 PNG / mtime 09:49 | ✅ S6/S8/S10/S11/S14 |

### 차트 5장 (S6 / S8 / S10 / S11 / S14)

| 슬라이드 | 사이즈 | 내용 |
|---|---|---|
| S6 | 70.6 KB | (build_s6) |
| S8 | 69.7 KB | (build_s8) |
| S10 | 97.8 KB | (build_s10) |
| S11 | 82.9 KB | (build_s11) |
| S14 | 119.6 KB | (build_s14) |

---

## 2. narrative 표 — 10 cell 메인 (절대 측정 수치 변경 금지)

paired Δ% vs bern (sel=0.10):

### 10 cell 메인 (5 dataset × sf1/sf10) — Exqutor 매칭 narrative 핵심

| Cell | Hilbert | Hybrid | MB_partial | HDBSCAN |
|---|---:|---:|---:|---:|
| DEEP_sf1 | -1.07% | -1.71% | -1.99% | -2.48% |
| DEEP_sf10 | -1.98% | -2.73% | -2.87% | -2.51% |
| SIFT_sf1 | -33.53% | -30.46% | -33.13% | -34.17% |
| SIFT_sf10 | -12.02% | -11.48% | -11.63% | -11.79% |
| SSN_sf1 | +1.69% | +0.64% | +1.02% | +0.84% |
| SSN_sf10 | +1.38% | +0.56% | +1.35% | +0.67% |
| WIKI_sf1 | -10.92% | -8.99% | -11.30% | -11.29% |
| WIKI_sf10 | -5.70% | -5.43% | -3.77% | -5.54% |
| YFCC_sf1 | -8.07% | -6.98% | -8.37% | -8.40% |
| **YFCC_sf10** | **-5.21%** | **-4.78%** | **-5.62%** | **-5.77%** |

> **5/8 10:18 build_yfcc 다운로드 폐기**: 자체 build YFCC_DL (`partsupp_yfcc_pca_{1,10}`) 적재본은 본 연구에서 사용하지 않음. YFCC narrative 는 채림 정본 단일 (`partsupp_yfcc_{1,10}`).

**4강 method 일관 우위 (단일 100% 측정 완료, 5/8 14:13 KST)**: 10 cell 중 8 cell improve direction (SSN sf1/sf10 만 ceiling outlier). SIFT_sf1 -34.17% (최대 hdbscan), WIKI -11.30%, YFCC -8.40%, DEEP -2.87%. YFCC_sf10 4강 -4.78~-5.77% 모두 일관 improve.

> **5/8 14:13 가지치기 + 최적 해 단일 100% finalize** (master_v6 §10 갱신): 본 4강 = 30 method × 10 cell 종합 매트릭스 위 가지치기 결과의 production criteria 4강 — **★1 hdbscan / ★2 minibatch_partial / ★3 hilbert / ★4 hybrid**. Tier 1 = 17종, Tier 2 = 2종 (birch, kde_pilot), Tier 3 = 1 (pq), Pruned = 7종 (sobol/hammersley/halton/spectral/distance_shell/optics/importance_sampling), Wave 0 = 3종 (dbscan/lsh/random_proj variance explosion). Tier 1 spread 1.21%p (-8.04 ~ -6.83) — **method choice 차이 미미, 분포 인지 vs 미인지 boundary 결정적**. analyze_10cell_w4.py 재계산 (query_id paired alignment, 1000-vs-500 broadcast bug fix 포함). 본 § 의 4강 narrative 는 §10 의 가지치기 결과를 그대로 인용한다.

---

## 2.5. §yfcc_source — 채림 정본 단일 결정 (5/8 10:35 build_yfcc 흔적 전량 회수 완료)

### 결정 사항

- **YFCC narrative = 채림 정본 단일 source** (`partsupp_yfcc_{1,10}`)
- **build_yfcc.py 자체 다운로드/추출 적재본 (`partsupp_yfcc_pca_{1,10}` = YFCC_DL) 폐기 완료** (5/8 10:35)
- 5/8 AM agent M 의 cosine ≈ 0 직교 검증 결과는 폐기 사유의 정량 근거이며, 본 연구 narrative 에서는 사용하지 않음

### 5/8 10:35 build_yfcc 흔적 회수 (cleanup 실행 결과)

| 항목 | 사이즈 | 결과 |
|---|---:|---|
| `/mnt/hdd0/.../yfcc_full/yfcc100m_vecs.fbin` (raw) | 40GB → 0 | rm 완료 |
| PG `partsupp_yfcc_pca_1` | 1389 MB → 0 | DROP CASCADE |
| PG `partsupp_yfcc_pca_10` | 14 GB → 0 | DROP CASCADE |
| `/mnt/hdd0/.../cache/rq1/*YFCC_DL*` parquet/json | 119개 → 0 | find -delete |
| `/tmp/yfcc_dl*.flag` (3개: done/paused/pipeline_done) | 3 → 0 | rm |
| tmux session `yfcc_dl` | 41GB downloading paused | kill |

**서버 디스크 회수**: 1.7T avail → 1.8T avail (~100GB 회수, partial — index/wal flush 후 정확치)
**채림 정본 보존 확인**: `partsupp_yfcc_1` (1622 MB) + `partsupp_yfcc_10` (8280 MB) **건들지 않음** ✅

### agent M 결과 (참고 자료, narrative 에는 사용하지 않음)

**A. 채림 정본 출처 — BigANN 챌린지 pre-PCA u8bin**
- 출처: BigANN 챌린지 `base.10M.u8bin` (192d uint8, 0~255 raw)
- PCA basis: BigANN 측 unknown (random_state 미상)
- norm: √(192 × 150²) ≈ 2078 ≈ 1819 (실제 측정 일치, 평균 픽셀 강도 150)
- 적재: u8 raw → float32 cast 후 적재, 비정규화

**B. (폐기 완료) YFCC_DL 출처 — build_yfcc.py 자체 sklearn PCA**
- 출처: 본 연구 자체 다운로드 raw (~40GB, 8.4M rows incomplete) + build_yfcc.py
- PCA fit: sklearn `PCA(n_components=192, random_state=42)`, 첫 1M rows fit
- 처리: 1280d float32 raw → 192d PCA 변환 → centered + component-wise normalize
- norm: √(192 × var) ≈ 0.7 ≈ 0.7257 (실제 측정 정확 일치)
- **5/8 10:18 폐기 결정 → 5/8 10:35 흔적 전량 회수 완료** — cosine ≈ 0 직교 PCA basis 검증으로 채림 정본과 다른 임베딩 공간임을 확인 → 동일 source 통일 (채림 정본 단일)

### sf100 plan — 채림 석사님께 정본 요청 (5/8 10:35 사용자 결정)

- **자체 다운로드 X. 채림 측에 sf100 적재본 요청** (자문 메일 의제 1)
- 핵심 사유:
  1. **source 일관성** — 채림 정본 sf1/sf10 과 동일 BigANN benchmark source 로 sf100 까지 단일 narrative 유지
  2. **자체 다운로드 부담 회피** — 40GB+ 재다운로드 + PCA pipeline 재실행 공수 회피
  3. **메인 narrative = 10 cell 집중** — sf100 자체 다운로드 chain 의 PCA basis 직교 위험 회피
- 회의 5/8 19:00 → 자문 메일 5/15 발송 → 채림 회신 후 측정 launch (~5/22)
- WIKI sf100 build (full_88M 268GB) 도 별도 협의

---

## 2.6. §최적 해 — 가지치기 + 4강 결정 (5/8 11:40 master_v6 §10 신규, 본 § 인용)

본 § 는 master_v6 §10 의 가지치기 + 4강 결정 결과를 본 handoff 의 narrative 핵심으로 인용한다. 측정 수치 변경 없음 — §10 의 표·결정을 그대로 reference.

### 2.6.1 가지치기 결과 (30 method × 10 cell 단일 100% 매트릭스 기준, 5/8 14:13 finalize)

| Tier | N | Method | 핵심 |
|---|---:|---|---|
| **Wave 0 (outlier)** | 3 | dbscan / lsh / random_proj | variance explosion (+261245%, +2092%, +434%) → 측정 instability |
| **Tier 1 (강력 일관)** | 17 | hdbscan / pca_kmeans / coresets / zorder / kmeans_pp / faiss_ivf / minibatch_partial / minibatch / gmm / hilbert / pca1d / agglomerative / hybrid / hierarchical_kmeans / sparse_rp / kdtree / reservoir | avg_Δ% -8.04 ~ -6.78, neg_cells ≥ 8/10, CI excludes 0 ≥ 7/10 |
| **Tier 2 (boundary)** | 2 | birch / kde_pilot | birch avg -6.33 / kde_pilot -3.03, T1 boundary |
| **Tier 3 (특수)** | 1 | pq | DEEP/SSN sign positive, SIFT/WIKI/YFCC negative, sign 절반 |
| **Pruned (가지치기)** | 7 | sobol / hammersley / halton / spectral / distance_shell / optics / importance_sampling | sign 반대 또는 magnitude 약 |

**최종**: 30 → 17 (Tier 1) + 2 (T2) + 1 (T3) + 7 (Pruned) + 3 (Wave 0) = 30 partition.

### 2.6.2 4강 method (production criteria 결정, 단일 100% 기준)

17종 Tier 1 中 (1) cell 별 1위 횟수 (2) production cost 차별화 (3) interpretability 기준 4강 선정:

| Rank | Method | avg_Δ% | 핵심 narrative |
|---|---|---:|---|
| **★1** | **hdbscan** | -8.04 | **strongest narrative** — avg 1위 + SIFT_sf1 최강 1위 (-34.17%) + 8/10 sign + 8/10 CI. fit time 무거움 (4313s) → oracle 영역 (production X) |
| **★2** | **minibatch_partial** | -7.63 | **OLTP narrative 유일** — online partial_fit. CI 9/10 강력 일관. pre-computed cluster 없이 stream 처리 |
| **★3** | **hilbert** | -7.54 | **production sweet spot** — 매우 빠름 (수 초). SIFT sweet -33.53%. CI 9/10 강력. Z-order ablation 으로 locality mechanism 분리 |
| **★4** | **hybrid (MB+Hilbert)** | -7.13 | **mechanism narrative** — Hilbert 효과 분리 ablation (clustering vs ordering driver 검증) |

### 2.6.3 핵심 통찰 (회의 narrative 의 결정적 메시지)

1. **Tier 1 spread 1.21%p (-8.04 ~ -6.83)** — method choice 의 차이는 작음. Tier 1 내부 어느 method 든 강력 일관. **분포 정보 인지 vs 미인지 의 boundary 가 결정적**, "어느 method 인가" 는 부차.
2. **σ-allocation 격차 < 1%** — Neyman vs Anti-Neyman 격차 < 1% in 7/12 cell (RQ2 결과와 정합). σ_i 신호 약 → **단순 균등 stratification 으로 충분**.
3. **Distribution Sweet Spot 정량 정의**:
   - **Sweet (improve -7~-32%)**: SIFT (cluster_ratio 1.65 / intrinsic 0.71), WIKI (1.84 / 0.81), YFCC (~1.5 / ~0.85), DEEP (1.43 / 0.78 — boundary smaller magnitude).
   - **Ceiling (effect 약, ±2%)**: SSN++ (cluster_ratio 1.29 / intrinsic 0.88) — uniform-like distribution.
   - **Decision boundary**: cluster_ratio > 1.4 AND intrinsic_dim < 0.85 → distribution-aware method 효과 안정.
4. **Exqutor 미작동 영역 정량화**: single-table non-indexed skewed distribution 영역에서 Exqutor Adaptive Sampling 의 정확도 저하를 본 method 가 보완 — SIFT sf1 -34%p / WIKI sf1 -11%p / YFCC sf1 -8%p / DEEP -2.5%p.

### 2.6.4 회의 narrative + 자문 의제 (master_v6 §10.7 인용)

**5/8 19:00 회의 결정 항목**:
1. 4강 method 선정 confirm (hdbscan / hilbert / minibatch_partial / hybrid)
2. Tier 1 = 15종 narrative 합의 — RQ3 의 답 = "어느 분포 인지 method 든 Tier 1 이면 OK, 4강 = 대표"
3. SSN++ ceiling honest reporting confirm
4. Multi 일반화 future work 합의

**자문 의제 (~5/15 채림 석사 + 교수님)**:
- 4강 method 의 production cost 차별화 narrative validity
- Distribution Sweet Spot 정량 boundary (cluster_ratio 1.4 / intrinsic 0.85) 의 generalizability
- Multi 일반화 검증 plan (4강 × 3 multi cell) — 진행 중 agent Y4
- Exqutor 통합 ensemble plan 의 타당성

---

## 3. ERROR 분석 — 회의 narrative 영향 평가

### A. WIKI_sf10 HDBSCAN — 06:48 retry recovery 로 해결 (변경 X)

- **이전 (05:31)**: `psycopg.errors.UndefinedTable: relation "partsupp_wiki_10" does not exist` → NaN
- **현재 (06:50)**: 06:48 retry recovery 로 정상 측정 완료. paired Δ% = **-4.30%**
- **회의 narrative 영향**: WIKI_sf10 4강 method 모두 측정 — -4.48 / -4.21 / -2.58 / **-4.30**. footnote 불필요. 12 cell 완성.

### B. YFCC_sf10 — 측정 완료 (5/8 14:13 KST 단일 100% finalize)

- **상태**: 측정 완료. 31 method × YFCC_sf10 parquet 모두 도착. 4강 paired Δ% (sel=0.10): hilbert -5.21 / hybrid -4.78 / minibatch_partial -5.62 / hdbscan -5.77 모두 일관 improve direction.
- 단일 narrative: 10 cell × 30 method × RQ1/2/3 = **100% 측정 완료**. analyze_10cell_w4.py 재계산 (query_id paired alignment, 1000-vs-500 broadcast bug fix 포함).

### C. KDE_pilot 8M — `module 'run_kde_pilot_8m' has no attribute 'main'`

- chain_unified.py 의 stage routing 버그. 다른 chain 에서 multi_pipeline 진행에 영향 없음.
- 회의 narrative 영향 없음 (KDE_pilot 은 보강 method 가 아님).

### D. analyze_multi_w4.py null — path mismatch 원인 분석 ✅ (NEW 09:44)

- **null 원인**: `analyze_multi_w4.py` 의 `CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')` 인데, multi raw 결과는 **`cache/rq3/`** 에 위치 (`rq2_partsupp_deep_sift_10_4way.parquet` / `rq2_partsupp_deep_wiki_10_4way.parquet` / `rq2_multi_join_deep_wiki.parquet`).
- **처리**: script 수정 X (사용자 절대 원칙). 직접 parsing python (서버 직접 실행) 으로 multi_w4_recovered.json 생성 → master_v6 §multi 추가.
- **modes 발견**: multi-vector = `[bernoulli, km20_emb1, km20_emb2, km20_concat, km20_product]` / multi-join = `[bernoulli, km20_deep_only, km20_wiki_only, km20_product]`. 모드별 paired CI 모두 회복 (n=2500/sel).

### E. DEEP_sf10 OPTICS missing — sf10 전체 0 cell (footnote 결정)

- 측정: sf1 5 cell 만 (DEEP_sf1, SIFT_sf1, SSN_sf1, WIKI_sf1, YFCC_sf1), sf10 0 cell.
- **사유**: 의도적 skip — OPTICS 의 reachability distance 계산은 8M record 에서 메모리 + 시간 ~4-8h/cell, W4 sprint 일정 외.
- **처리**: master_v6 §6 끝에 footnote 명시 ("sf10 cell narrative 에서 OPTICS 행 비어있음은 측정 누락이 아니라 의도적 skip").
- **재측정 trigger**: 회의 전 8h 여유 부족 → 보강 X. Phase 3 (build/적재) 후 재고려.

---

## 3.5. 추가 method 진행 — Wave 1 sf1 sandbox 결과 (5/8 AM agent E)

### chain_unified.py 확장 (METHODS_NEW9)

- **이전**: 25 method (16 base + 9 NEW9: DBSCAN/OPTICS/Agglomerative/Hierarchical KMeans/Faiss IVF/PCA-KMeans/KMeans++/Coresets/Spectral)
- **현재**: **33 method** — METHODS_NEW9 추가 8종 (Halton, Hammersley, Reservoir + Wave 2 후보 5)
- **백업**: `chain_unified.py.bak.20260508` (수정 전 원본)
- **ALL_METHODS**: 30 → 33 확장

### Wave 1 sf1 sandbox 측정 (sel=0.10 paired Δ% vs bern, n=2418~2495)

| Cell | 4강 평균 (reference) | Halton | Hammersley | Reservoir | 가지치기 결과 |
|---|---:|---:|---:|---:|---|
| DEEP | -1.17% | +5.15% | +3.68% | +0.59% | 🔴 PRUNE (부호 반대) |
| SIFT | -31.31% | -26.86% | -26.90% | -30.00% | 🟢 SURVIVE (80%+ 매치) |
| SSN | +1.74% | +17.13% | +18.82% | +0.94% | 🟡 SSN++ ceiling 강화 |

### 핵심 발견

1. **QMC 한계**: Halton/Hammersley 가 PCA-skew dataset (DEEP) 에서 cluster size min=0 발생 → uniform sampling fail
2. **4강 우위 재확인**: SIFT 만 80%+ 매치 (skew 영역만 가치), DEEP 부호 반대
3. **SSN++ ceiling 강화**: QMC 에서 더 큰 부정 효과 (+17~+18% vs 4강 평균 +1.74%)
4. **Wave 2 skip 결정**: PCA-skew fail 패턴 명확 → Stratified Halton / Density-stratified 등 5 후보 deferred

### 산출

- `_internal/method_exploration_results_20260508.csv` — 105 rows (3 dataset × 7 method × 5 sel), master_v6 호환 schema (paired Δ% + bootstrap CI + n).
- master_v6 §6 끝에 footnote 통합 완료 (방법 catalog 25 → 33 확장 + Wave 1 PRUNE/SURVIVE/Ceiling 결과 narrative).

---

## 4. multi_pipeline 진척 (5/8 09:50 KST — narrative 회복 완료)

- **multi_pipeline_done @ 08:08** (raw)
- **analyze null 원인 해결** ✅ — path mismatch 식별 (rq1 vs rq3, §3-D 참조). script 수정 X, 직접 parsing 으로 회복.
- **multi_w4_recovered.json (11 KB) ✅** — 3 cell × 4-3 mode × 5 sel paired bootstrap CI 모두 추출.

### Multi-vector partsupp_deep_sift_10 sel=0.10 paired Δ%

| Mode | sel=0.01 | sel=0.10 | sel=0.50 |
|---|---:|---:|---:|
| km20_emb1 | +13.82%* | +0.98%* | +0.06% |
| km20_emb2 | +8.45%* | +0.21% | -0.36%* |
| km20_concat | +7.64%* | -0.35% | -0.42%* |
| km20_product | +9.50%* | **-1.15%*** | -0.41%* |

### Multi-table natural join (deep_10 ⨝ wiki_10) sel=0.10 paired Δ%

| Mode | sel=0.01 | sel=0.10 | sel=0.50 |
|---|---:|---:|---:|
| km20_deep_only | +21.12%* | +1.51%* | +0.06% |
| km20_wiki_only | +13.50%* | +1.72%* | +0.07% |
| km20_product | +14.31%* | +1.86%* | +0.63%* |

**핵심**: multi-vector sel ≥ 0.10 에서 km20_product/concat 가 가장 효과 (Δ% 거의 0~음수). multi-table join 은 모든 mode 모든 sel 에서 hurt direction → joint-aware clustering 가 future work 필요.

- **회의 narrative 영향**: master_v6 §multi 에 통합 완료. "multi 3 cell × 4-3 mode 모두 측정 완료" 으로 narrative 회복.

---

## 5. Phase 2/3 deferred 사유 (사용자 의도 + 서버 상태)

### 사용자 의도 (5/7 23:32 메시지)
> "사f1/sf10 측정 + 추가 method 완료 후 → build/적재 우선 → 측정은 회의 후"

→ 회의 직전까지는 **추가 측정 X**, build/적재 정리 우선

### 서버 PG 측정 점유 진행 중
- multi_pipeline (5.55M/8M chunk loading) 점유 중 → 14:00 까지 PG 동시 측정 어려움
- 14:00 후 Phase 2 (추가 method) 가능

### 권장 순서 (사용자 결정 후)
1. (06:00~14:00) PPT 검증 + ERROR 처리 결정 + multi 완료 대기
2. (14:00~) Phase 2 (추가 method 또는 ERROR 재build)
3. (회의 후) Phase 3 (build/적재)

---

## 6. v8 결정 누적 (변경 X)

- 4강 method × 10 cell 메인 표 narrative 변경 금지
- master_v6_fill_partial / plot_w4_partial / build_charts_5_8 / build_native_pptx_5_8 그대로 실행만
- 진행 중인 서버 tmux 유지: sf10_NEW9_SSN, wiki_sf10, yfcc_sf10, multi_pipeline
- 폐기 완료 (5/8 10:35): yfcc_dl tmux + raw fbin 40GB + partsupp_yfcc_pca_{1,10} (15GB) + parquet 119개 + flag 3개 — 자체 다운로드 흔적 전량 회수
- WIKI/YFCC sf10 의 ERROR 는 분석만 (사용자 결정 필요)

---

## 7. 회의 narrative 평가 (5/8 19:00 회의 자료 readiness — 99% ready)

✅ **충분**: 10 cell 메인 × 4강 method paired Δ% — 일관성 + outlier 둘 다 narrative 가능
✅ **차트 5장** (S6/S8/S10/S11/S14) — slide 흐름 확보, 09:49 갱신
✅ **PPTX 15 slide** — image embed 5/5, 09:49 갱신 (468KB)
✅ **WIKI sf10** — chain full done (07:58), 4강 method 모두 측정
✅ **§6 RQ1 단조성 11 cell** — 100% 부호 일관 (ρ -0.366~-0.609 모두 음수). NEW master_v6
✅ **§7 RQ2 5mode 11 cell × 4 mode** — sel=0.10 43/44 CI 0 제외. σ_i 신호 약함 honest evidence. NEW master_v6
✅ **§multi 3 cell × 4-3 mode** — analyze null 회복, paired CI 모두 추출. NEW master_v6
✅ **§yfcc_source** — 채림 정본 단일 결정 (5/8 10:18 build_yfcc 다운로드 폐기). NEW master_v6
✅ **A4 OPTICS sf10 footnote** — 의도적 skip 명시 (sprint 일정 외)
✅ **YFCC sf10 (단일)** — 측정 완료 (5/8 14:13 KST). 4강 paired Δ%: hilbert -5.21 / hybrid -4.78 / mb_partial -5.62 / hdbscan -5.77 모두 일관 improve direction. 단일 10 cell × 30 method × RQ1/2/3 = 100% finalize.

→ **변경 금지 원칙 준수** (raw 측정값 변경 X). master_v6 narrative 만 10 cell 메인 + multi 3 부록 + §yfcc_source 으로 재구성.

---

## 8. 10:18 변화 summary (요약)

| 항목 | 08:10 → 10:18 | 결과 |
|---|---|---|
| YFCC source 결정 | YFCC + YFCC_DL 부록 | ✅ 채림 정본 단일 (build_yfcc 다운로드 폐기) |
| 메인 narrative cell 수 | 12 단일 + 3 multi | ✅ 10 메인 + 3 multi 부록 |
| A2 multi narrative | analyze null | ✅ path mismatch 식별 + 직접 parsing 으로 회복 |
| A3 RQ1/2 master_v6 반영 | placeholder | ✅ 11 cell × 5 sel × 5 seed 정량 표 |
| A4 OPTICS missing | 미확정 | ✅ sf10 0 cell = 의도적 skip footnote |
| master_v6 narrative 섹션 | 4 | ✅ +§6 RQ1, +§7 RQ2, +§multi, +§yfcc_source = 8 섹션 |

---

작성: 5/8 05:33 (자동화 sub-agent), 06:50 (12 cell finalize), 08:10 (14 cell + multi raw done), **09:50 (4종 빈틈 회복 + master_v6 finalize 완료, 회의 자료 99% ready)**
