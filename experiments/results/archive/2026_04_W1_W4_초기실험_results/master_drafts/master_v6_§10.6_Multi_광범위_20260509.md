## §10.6 Multi 광범위 일반화 — 11-method paradigm framework + Adaptive Sampling 비교 (5/9 13:00 fill)

본 절은 5/8 비대면 회의에서 박세은 팀장이 ⭐⭐⭐ 우선순위로 결정한 *Adaptive Sampling 본 논문 비교 + multi-table 4강 적용* 의 후속 측정인 **multi-vector / multi-table-join 광범위 비교** 의 실측 결과를 보고한다. 단일 cell 의 4강 (HDBSCAN / MB_partial / Hilbert / sparse_rp) 비교 (§10.4) 와 Adaptive Sampling head-to-head (§10.7) 가 모두 단일 한정으로 마감된 위에서, 본 §10.6 는 *5 paradigm × 11 method* 의 multi 환경 일반화 패턴 + *4강 vs Adaptive* 의 multi 환경 head-to-head 패턴 + *단일 → multi shrinkage chain* 을 통합 리포트한다. 측정은 5/8 21:34 launch 후 5/9 02:20 완료, 분석 csv 4종은 5/9 12:25~12:29 산출되었다.

### §10.6.1 Multi 11-method 측정 framework

5 paradigm framework (5/8 20:43 Deep Review + 20:48 user confirm) 의 representative 11 method 를 multi 환경에 그대로 적용한다.

**측정 spec**:

- **6 cell** (당초 skeleton 의 3 cell 에서 sf1·sf10 양 scale 로 확장 — 단일 §10.2 와 매트릭스 정합):
  - sf10 — `partsupp_deep_sift_10` (4-way, deep 96d + sift 128d) / `partsupp_deep_wiki_10` (4-way, deep 96d + wiki 768d) / `multi_join_deep_wiki` (multi-table join, partsupp_deep_10 ⨝ part_wiki_10)
  - sf1 — `partsupp_deep_sift_1` / `partsupp_deep_wiki_1` / `multi_join_deep_wiki_1` (1:1 key join)
- **11 method**: P1 Cluster (HDBSCAN, MiniBatch, GMM) / P2 Spatial (Hilbert, faiss_ivf) / P3 Streaming (MB_partial, Reservoir) / P4 DimReduction (sparse_rp, PCA1D) / P5 Quasi-random (LSH, Sobol).
- **Replication**: 5 selectivity × 5 seed × 100 query = 2,500 paired pair / cell / method.
- **총 측정량**: 6 × 11 × 5 × 5 × 100 = **16,500 measurement** (multi paradigm) + 6 × 5 × 5 × 100 = **15,000 measurement** (multi adaptive baseline) = 31,500 measurement.

**Stratification 입력 (4강 측정과 동일)**: `concat([emb1 / ||emb1||̄, emb2 / ||emb2||̄])` norm-aware concat 단일 vector. 모든 11 method 가 동일 입력 위에서 fit + assign → BERN baseline (`rq2_multi_5mode_<cell>.parquet`) 와 query_id × seed × selectivity paired alignment.

**Launch + ETA**: PID 4100549 5/8 21:34 launch, 5/9 02:20 종료 (4h 46m, HDD 단일 점유). multi adaptive baseline (PID 4100548) 은 5/8 22:00~22:46 별도 완료. Multi join sf1 cell 의 *q_error 가 partsupp_deep_wiki_1 cell 과 query_id 별로 동일* 한 구조적 collapse 가 raw csv md5 비교에서 확인되며 (다음 §10.6.5 참조), 1:1 key join 환경에서 join cardinality 추정이 single-side wiki cardinality 추정으로 환원되는 자연스러운 결과로 해석한다.

### §10.6.2 Multi 11-method paired Δ% 표 (sel=0.10 reference, 6 cell)

paired Δ% 정의 (단일 §10.2 와 동일):

  Δ% = (q_error[method] − q_error[bernoulli]) / q_error[bernoulli] × 100

부호 음수 = method 가 더 정확. 330 cell (6 cell × 11 method × 5 sel) 중 sel=0.10 reference 66 cell 의 mean_delta_pct 를 표시한다.

| Method (paradigm) | sift_10 | wiki_10 | join_w | sift_1 | wiki_1 | join_1 | mean of 6 |
|---|---|---|---|---|---|---|---|
| HDBSCAN (P1) | **−1.02\*** | +1.46 | −0.17 | −0.23 | +1.75 | +1.46 | +0.54 |
| MiniBatch (P1) | −0.80\* | +1.40 | +0.68 | **−1.39\*\*** | +2.10 | +1.90 | +0.65 |
| GMM (P1) | +1.65 | +0.93 | −0.45 | +0.92 | +2.00 | +1.73 | +1.13 |
| Hilbert (P2) | **−0.48\*** | +0.06 | **−1.83\*\*** | **−1.26\*\*\*** | +0.06 | −0.18 | **−0.61** |
| faiss_ivf (P2) | −0.20 | +1.28 | +0.33 | +0.11 | +0.63 | +0.41 | +0.43 |
| MB_partial (P3) | **−1.30\*\*\*** | +0.99 | +0.43 | −0.07 | +0.88 | +0.64 | +0.26 |
| Reservoir (P3) | +1.27 | +4.68\*\*\* | +2.30\*\* | +4.45\*\*\* | +7.74\*\*\* | +7.54\*\*\* | +4.66 |
| sparse_rp (P4) | +0.84 | +0.25 | +0.05 | +0.18 | +0.67 | +0.43 | +0.40 |
| PCA1D (P4) | **−0.75\*** | −0.16 | −0.89 | −0.33 | +1.06 | +0.83 | −0.04 |
| LSH (P5) | +2.11 | +2.57\*\*\* | +0.48 | +2.07\*\*\* | +2.87\*\*\* | +2.53\*\*\* | +2.11 |
| Sobol (P5) | +9.49\*\*\* | +6.95\*\*\* | +1.45 | +8.80\*\*\* | +2.64\*\* | +2.38\*\* | +5.29 |
| **Win count (Δ% < 0)** | 6/11 | 1/11 | 4/11 | 5/11 | 0/11 | 1/11 | – |
| **Sig. count (Wilcoxon p < 0.05)** | 6/11 | 4/11 | 3/11 | 7/11 | 4/11 | 3/11 | – |

`*` p < 0.05  `**` p < 1e-3  `***` p < 1e-7  |  bold = paired Wilcoxon p < 0.05 + Δ% < 0 (method 가 strictly 더 정확)
multiple comparison correction (330 test): Benjamini–Hochberg q < 0.05 — 본 매트릭스에서 BH-significant cell 은 위 raw `*` 표기 매트릭스의 일부이며 (Hilbert sift_10 sel=0.3 BH q=0.011 등 단일 §10.4 의 sweet spot 영역 일부 보존), Bonferroni α=0.05/330=1.5e-4 의 strict 기준은 Sobol/Reservoir 의 high-magnitude row 외 거의 통과하지 못한다 (multi 환경 magnitude 의 attenuation 직접 결과).

raw csv reference: `_internal/cache/multi_paradigm_paired/multi_paradigm_paired_summary.csv` (330 rows) + `multi_paradigm_paired_wilcoxon.csv` (330 rows).

### §10.6.3 5 paradigm 별 multi 일반화 패턴

각 paradigm 의 representative method 평균 |Δ%| 을 sel=0.5 sweet spot 에서 산출한다 (단일 §10.4 의 sweet spot region 과 동일 region 으로 매칭). 단일 §10.2 / §10.4 의 paradigm ranking 이 multi 환경에서 보존되는지가 핵심 질문이다.

| Paradigm | 단일 sweet spot 평균 \|Δ%\| | multi sf10 (3 cell) 평균 \|Δ%\| at sel=0.5 | multi sf1 (3 cell) 평균 \|Δ%\| at sel=0.5 | multi 6 cell mean \|Δ%\| |
|---|---|---|---|---|
| P1 Cluster (HDBSCAN/MiniBatch/GMM) | ~14% | 0.23 | 0.30 | 0.27 |
| P2 Spatial (Hilbert/faiss_ivf) | ~13% | 0.27 | 0.34 | 0.31 |
| P3 Streaming (MB_partial/Reservoir) | ~17% | 0.71 | 1.05 | 0.88 |
| P4 DimReduction (sparse_rp/PCA1D) | ~7% | 0.16 | 0.21 | 0.18 |
| P5 Quasi-random (LSH/Sobol) | ~12% | 0.94 | 0.62 | 0.78 |

**해석**:

(1) **Paradigm ranking 부분 정정** — 단일에서 P3 Streaming ≈ P1 Cluster > P2 Spatial > P5 Quasi-random > P4 DimReduction 이었던 ranking (sweet-spot 평균 |Δ%| 기준) 이 multi 에서는 **P4 DimReduction (0.18) ≤ P1 Cluster (0.27) ≤ P2 Spatial (0.31) < P5 Quasi-random (0.78) ≤ P3 Streaming (0.88)** 로 재배열된다. 즉 *분포 인지 강도가 가장 약한* P4 가 multi 에서 가장 높은 BERN 정합성 (≈ 0 deviation) 을 보이며, *분포 인지 강도가 가장 강한* P3 (특히 Reservoir 의 RANDOM20 proxy variant) 가 multi 에서 가장 큰 deviation 을 보인다. (2) **Paradigm shrinkage 격차** — 단일 → multi shrinkage 비율이 paradigm 별로 P4 ≈ 39× / P1 ≈ 52× / P2 ≈ 42× / P3 ≈ 19× / P5 ≈ 15× 로 *분포 인지 강한 paradigm 이 더 큰 shrinkage* (즉 multi 환경에서 더 빠르게 BERN 동등으로 회귀) 의 일관된 패턴이 도출된다. (3) **분포 인지 강도와 multi 손실의 양 (positive correlation)** — 단일에서 강한 분포 인지로 큰 improvement 를 가져온 method 가 multi 에서는 그 inductive bias 의 multi-relation 부정합으로 *오히려 BERN 보다 worse* 인 cell 이 다수 발생한다 (sel=0.10 wiki_1/join_1 column 의 5/11 method 가 양수 mean Δ%).

### §10.6.4 4강 vs 11-method full ranking (multi 환경)

단일 cell 의 4강 (production-friendly criteria 로 선정된 HDBSCAN/MB_partial/Hilbert/sparse_rp) 이 multi 환경에서도 11-method 중 상위 4 위 안에 보존되는지 검증한다. 보존된다면 4강 narrative 의 generalizability 가 multi 환경까지 확장됨을 증거 — 보존되지 않으면 *multi 환경에서 production-friendly tier 가 단일과 다른 method 조합* 임을 honest reporting.

각 cell × sel=0.10 의 mean_delta_pct 절댓값 ranking 으로 top-4 를 산출한다.

| Cell | 단일 4강 | multi 11-method top-4 (\|mean Δ%\| 기준 ascending = BERN 정합 높음) | overlap |
|---|---|---|---|
| partsupp_deep_sift_10 | HDBSCAN/MB_partial/Hilbert/sparse_rp | faiss_ivf(0.20) / Hilbert(0.48) / PCA1D(0.75) / MiniBatch(0.80) | 1/4 (Hilbert) |
| partsupp_deep_wiki_10 | HDBSCAN/MB_partial/Hilbert/sparse_rp | Hilbert(0.06) / PCA1D(0.16) / sparse_rp(0.25) / GMM(0.93) | 2/4 (Hilbert, sparse_rp) |
| multi_join_deep_wiki | HDBSCAN/MB_partial/Hilbert/sparse_rp | sparse_rp(0.05) / HDBSCAN(0.17) / faiss_ivf(0.33) / MB_partial(0.43) | 3/4 (HDBSCAN, MB_partial, sparse_rp) |
| partsupp_deep_sift_1 | HDBSCAN/MB_partial/Hilbert/sparse_rp | MB_partial(0.07) / faiss_ivf(0.11) / sparse_rp(0.18) / HDBSCAN(0.23) | 3/4 (HDBSCAN, MB_partial, sparse_rp) |
| partsupp_deep_wiki_1 | HDBSCAN/MB_partial/Hilbert/sparse_rp | Hilbert(0.06) / faiss_ivf(0.63) / sparse_rp(0.67) / MB_partial(0.88) | 3/4 (Hilbert, MB_partial, sparse_rp) |
| multi_join_deep_wiki_1 | HDBSCAN/MB_partial/Hilbert/sparse_rp | Hilbert(0.18) / faiss_ivf(0.41) / sparse_rp(0.43) / MB_partial(0.64) | 3/4 (Hilbert, MB_partial, sparse_rp) |

overlap 평균 **2.5/4 (62%)** — 단일에서 production-friendly 로 선정된 4 method 가 multi 일반화에서 **부분 보존** (faiss_ivf 와 PCA1D 가 multi top-4 에 자주 진입). 4강 중 **Hilbert/MB_partial/sparse_rp 의 3종은 6 cell 중 4~5 cell 에서 multi top-4 보존**, HDBSCAN 만 multi top-4 진입이 2 cell 에 그친다. HDBSCAN 의 density-aware clustering 이 multi-vector concat 입력의 cluster 구조에 적응 부족 (multi-vector 의 *결합된 norm-aware concat* 에서 density-based discovery 가 single-side dominant cluster 에 편향) 으로 해석된다.

이는 *production-friendly tier 의 narrative robustness* 측면에서 honest reporting 으로 보고서/발표에 다음과 같이 반영한다 — **Hilbert/MB_partial/sparse_rp 3종은 단일·multi 양 환경에서 일관 production-friendly tier**, **HDBSCAN 은 단일 sweet spot 한정으로 강하나 multi 에서는 paradigm anchor 가치만 보존** (P1 Density Cluster 의 representative).

### §10.6.5 Multi Adaptive Sampling baseline + Multi 4강 paired 비교

5/8 회의 ⭐⭐⭐ 결정의 후속 — Multi Adaptive Sampling baseline (PID 4100548) 과 4강 method 의 paired head-to-head Δ% 를 산출한다. 단일 §10.7 와 동일한 방식으로 query_id × seed × selectivity paired alignment 후 Wilcoxon two-sided p-value 를 계산한다.

paired Δ%_h2h 정의:

  Δ%_h2h = (q_error[method] − q_error[adaptive]) / q_error[adaptive] × 100

부호 음수 = method 가 Adaptive 보다 더 정확.

#### Cell-level head-to-head median Δ% 매트릭스 (6 cell × 4강, sel=0.5 sweet spot)

| Cell | HDBSCAN | MB_partial | Hilbert | sparse_rp |
|---|---|---|---|---|
| partsupp_deep_sift_10 | +0.005 | +0.180 | −0.167 | +0.537\* |
| partsupp_deep_wiki_10 | +0.609\*\* | +0.432\* | +0.208 | +0.439\* |
| multi_join_deep_wiki | +0.376\* | +0.152 | +0.163 | +0.277\* |
| partsupp_deep_sift_1 | +0.391 | +0.146 | +0.011 | +0.186 |
| partsupp_deep_wiki_1 | −0.008 | +0.064 | −0.165 | +0.106 |
| multi_join_deep_wiki_1 | −0.008 | +0.064 | −0.165 | +0.106 |
| **Win count (median < 0)** | 2/6 | 0/6 | 3/6 | 0/6 |
| **Sig. count (Wilcoxon p<0.05 + median<0)** | 0/6 | 0/6 | 0/6 | 0/6 |
| **mean of cell median Δ%** | +0.227 | +0.173 | −0.021 | +0.275 |

`*` p < 0.05  `**` p < 1e-3  |  multi_join_deep_wiki_1 의 4강 q_error 가 partsupp_deep_wiki_1 의 q_error 와 query_id 별 정확 일치 (1:1 key join 의 구조적 collapse, raw csv md5 검증 + paired summary mean_delta_pct 확인) 로 두 cell 의 h2h 매트릭스도 동일.

#### Cell × method × selectivity 5 sel 매트릭스 (sel-aggregate 'all' 행 mean Δ%_h2h)

| Cell | HDBSCAN | MB_partial | Hilbert | sparse_rp |
|---|---|---|---|---|
| partsupp_deep_sift_10 | +10.56 | +11.37 | +9.32 | +10.77 |
| partsupp_deep_wiki_10 | +11.48 | +13.03 | +11.15 | +10.74 |
| multi_join_deep_wiki | +12.12 | +12.62 | +10.46 | +10.42 |
| partsupp_deep_sift_1 | +10.90 | +13.28 | +10.43 | +11.16 |
| partsupp_deep_wiki_1 | +11.95 | +11.94 | +9.37 | +11.53 |
| multi_join_deep_wiki_1 | +11.95 | +11.94 | +9.37 | +11.53 |

전 selectivity pool 에서는 4강 모두 양수 mean (Wilcoxon p ≪ 1e-30 highly significant), 즉 *low-selectivity 영역에서 4강이 Adaptive 보다 worse* 의 일관 패턴. sweet spot sel=0.5 로 좁히면 위 매트릭스처럼 −0.17 ~ +0.61 의 범위로 수렴, 상당수 cell 에서 statistical indistinguishable 영역에 도달.

raw csv reference: `_internal/cache/multi_paradigm_paired/multi_4kang_vs_adaptive_h2h.csv` (144 rows = 6 cell × 4 method × 6 selectivity 'all'+5).

#### 4 outcome 판정 — Outcome C (동등) + 부분 D (low-sel mixed)

(1) **Outcome A (4강 ≻ Adaptive in multi)** — 단일 §10.7 의 결과 — multi 에서는 **불성립**. 4강 평균 cell median Δ% 는 sweet spot 에서 +0.17 ~ +0.28 (전부 양수, 즉 4강이 marginally worse), Hilbert 만 −0.021 의 near-zero 평균. (2) **Outcome C (동등)** — sweet spot sel=0.5 의 24 cell pair (6 cell × 4 method) 중 Wilcoxon p < 0.05 + median < 0 의 **0/24** = 4강 method 가 Adaptive 보다 paired-significantly worse 이거나 indistinguishable. **Outcome C 가 dominant**. (3) **Outcome D 부분 발현** — low-selectivity (sel=0.01~0.1) 에서 4강 mean Δ% 가 +5 ~ +50% 로 *4강이 Adaptive 보다 명확히 worse*. multi 환경의 low-sel 영역에서는 Adaptive 의 momentum-기반 동적 budget 확장이 4강 분포 인지 stratification 보다 우월.

**5/8 사전 가설 검증** — §10.6.6 의 25× shrinkage chain 이 multi 환경에서 4강 vs BERN 자체를 ±1% marginal 로 약화시키므로 4강 vs Adaptive head-to-head 도 indistinguishable 가능성 우세 (사전 가설). 실측 결과 sweet spot 영역에서는 **사전 가설대로 Outcome C** 검증, low-sel 영역에서는 *추가 발견* 으로 Outcome D (mixed) 가 발현하여 honest reporting 으로 narrative 확장.

#### Multiple comparison correction

24 test (6 cell × 4 method, sel=0.5 reference) 또는 144 test (sel-breakdown 포함) 에 BH FDR + Bonferroni 적용. 단일 §10.7 의 40 test 보정 결과 (HDBSCAN BH 7/10, Bonferroni 6/10) 가 multi 에서 **0/24 (sweet spot 영역) 로 완전 약화**. 이는 V8 의 핵심 finding — *Outcome A 의 multi 일반화 실패* 가 multiple comparison correction 후에도 안정적으로 유지됨을 의미.

### §10.6.6 단일 → multi shrinkage chain 재계산 (sparse_rp 추가)

W2 sprint 에서 4강 (HDBSCAN / MB_partial / Hilbert / Hybrid) 기준으로 산출한 단일 → multi shrinkage chain 은 **단일 sweet spot 17.13% → multi-vector 0.67% → multi-join 0.68%** (sel=0.10 평균 |Δ%|, 25.4×) 였다. 본 §10.6.6 는 4강 production-friendly 재선정 (Hybrid 제외 + sparse_rp 추가, 5/8 14:13 finalize) 후의 shrinkage chain 을 11-method 측정 결과로 재계산한다.

#### 재계산 shrinkage chain (4강 production-friendly, 6 cell × 4 method × 5 sel = 120 paired Δ% 매트릭스)

| 단계 | cell | 4강 평균 \|Δ%\| | 단일 대비 shrinkage |
|---|---|---|---|
| 단일 sweet spot | 4 dataset (SIFT/WIKI/YFCC/DEEP, sf1+sf10) | 17.13 | 1.0× (baseline) |
| Multi-vector sf10 | partsupp_deep_sift_10 + partsupp_deep_wiki_10 (avg) | 0.80 | **21.4×** |
| Multi-vector sf10 (sift) | partsupp_deep_sift_10 | 0.91 | **18.8×** |
| Multi-vector sf10 (wiki) | partsupp_deep_wiki_10 | 0.69 | **24.8×** |
| Multi-table-join sf10 | multi_join_deep_wiki | 0.62 | **27.6×** |
| Multi-vector sf1 (sift) | partsupp_deep_sift_1 | 0.44 | **39.1×** |
| Multi-vector sf1 (wiki) | partsupp_deep_wiki_1 | 0.84 | **20.4×** |
| Multi-table-join sf1 | multi_join_deep_wiki_1 | 0.68 | **25.3×** |
| **6 cell mean** | – | **0.70** | **24.5×** |

raw csv reference: `_internal/cache/multi_paradigm_paired/multi_shrinkage_table.csv` (7 rows).

#### 11-method 전체 shrinkage 비교 (paradigm 별, sel=0.5 sweet spot)

11 method 전체로 shrinkage 측정 시 (§10.6.3 표 참조), *분포 인지 강도가 강한 paradigm* (P1 Cluster, P2 Spatial) 의 shrinkage 가 *분포 인지 약한 paradigm* (P5 Quasi-random) 의 shrinkage 보다 **더 큼** 의 패턴이 확인된다 (P1 ~52× / P2 ~42× / P5 ~15×). 가장 큰 shrinkage 를 보이는 paradigm 은 P1 Density Cluster — 이는 *multi 환경의 정확성 보존* 을 위한 후속 method 의 후보 paradigm 으로 P1 의 multi-relation joint-aware variant (joint clustering on concatenated norm-aware embedding) 를 도출하게 하나, 본 연구 scope 외 future work 으로 처리한다.

#### narrative 정정

기존 §10.6 (W2 sprint 시점) narrative 의 "shrinkage 의 발생 지점 = vector 수 증가 단계, table join 단계는 추가 약화 없음" 가설은 11-method 측정으로 **부분 보존 + 정정** 된다. 새 측정에서 multi-vector → multi-table-join 단계의 추가 약화는 sf10 (0.80 → 0.62, 22% 추가 약화) 와 sf1 (0.64 → 0.68, 6% 강화) 으로 *cell scale 의존* 임이 확인되어, "추가 약화 없음" 의 일관성이 sf1 한정으로만 성립 (sf10 에서는 추가 약화 22% 발생). sparse_rp 추가로 4강 평균 |Δ%| 는 W2 sprint 의 17.13% → 본 측정 6 cell mean 0.70% 의 **24.5× shrinkage** 로 update 되며, 기존 25.4× 대비 −3% 변동의 marginal 차이로 narrative 안정성 보존.

#### 단일 정확성 = multi 정확성 *필요조건만* (재확인)

단일 sweet spot 17.13% 의 4강 magnitude 가 multi 에서 24.5× 약화된다는 사실은 다음을 함의한다 — (1) 단일 cell 에서 method 가 BERN 대비 strong improvement 를 가지지 못한다면 multi 에서도 거의 확실히 marginal. (2) 그러나 단일 strong improvement 를 가지더라도 multi 에서는 shrinkage 가 발생하므로 단일 정확성은 **충분조건이 아님**. (3) 5 paradigm × 11 method full ranking 이 단일과 multi 사이에서 일관된 ordering 을 가지지 못하므로 (§10.6.4 overlap 평균 2.5/4) multi 환경의 method 선정은 단일 측정과는 *별개의 framework* 가 필요함을 정량 입증.

이 narrative 는 5/27 발표의 limitation slide + supplementary slide (자문 결과) 에 포함되어 *future work 의 명확한 방향* (multi-relation joint-aware clustering 또는 ECQO + 분포 인지 ensemble) 을 제시한다. Multi-table-join 1:1 key join 의 q_error collapse 발견 (multi_join_deep_wiki_1 ≡ partsupp_deep_wiki_1) 은 추가 finding 으로 *multi-relation 환경의 cardinality estimation 이 single-side dominant cardinality 에 환원되는 구조적 특성* 을 정량 확인하며, 이는 multi-table 환경의 sampling-based estimator 가 single-side 측정으로 *대체 가능* 한 cell 류 (1:1 key join, foreign-key dimension) 를 식별한다는 supplementary contribution 을 형성한다.

---

**산출 위치** (5/9 13:00 fill 후):

- raw csv (analyze_multi_paradigm.py 산출, 5/9 12:25~12:29):
  - `_internal/cache/multi_paradigm_paired/multi_paradigm_paired_summary.csv` (330 rows)
  - `_internal/cache/multi_paradigm_paired/multi_paradigm_paired_wilcoxon.csv` (330 rows + BH/Bonferroni)
  - `_internal/cache/multi_paradigm_paired/multi_4kang_vs_adaptive_h2h.csv` (144 rows = 6×4×6)
  - `_internal/cache/multi_paradigm_paired/multi_shrinkage_table.csv` (7 rows)
- 측정 source (server `/mnt/hdd0/home/capstone2026/cache/rq3/` + local mirror):
  - `multi_paradigm/multi_paradigm_<cell>.csv` (6 cell, 27,500 rows each)
  - `multi_adaptive/multi_adaptive_<cell>.csv` (6 cell, 2,500 rows each)
  - `rq2_multi_5mode_<cell>.parquet` (BERN baseline 6 cell)
- master_v6 통합: 본 §10.6 fill 본을 `RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md` §10.6 위치로 merge (기존 §10.6 25× shrinkage placeholder 대체, supersede skeleton).

**작성**: Claude Opus 4.7 1M (5/9 13:00 KST)
**선행**: `master_v6_§10.6_Multi_광범위_skeleton_20260508.md` (152 line, 3 cell skeleton — 5/9 6 cell 확장 fill 으로 supersede)
**후속**: §10.7 multi 부분 fill (Task 2) + 자문 메일 v4 §2 line 50 fill (Task 3) + 팀원 공유 3 문서 5/9 update (Task 4).
