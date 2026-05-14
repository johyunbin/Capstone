# 6/11 보고서 §5.3 Honest Limitations 18종 본문 sketch (5/11 19:05)

> **base**: `plans/6_11_보고서_outline_v3_update_plan_20260511.md` §2.4 §5.3
> **목적**: Limitation 18종 (v2 8 + V7 audit 5 + 5/11 신규 5)의 5/29~6/10 sprint 본문 작성 부담 ↓
> **owner**: 박세은 (Discussion 통합) + 조현빈 (V7 audit 3건 + 5/11 신규 5건)
> **분량**: ~3p (~70 line dense 학술 산문)
> **v2 → v3 변경**: L1~L13 (v2 + V7 audit 5) → L1~L18 (5/11 신규 5건 추가)

---

## §5.3 Honest Limitations 18종

본 연구는 측정과 narrative의 honest disclosure를 원칙으로, paradigm framework와 측정 결과 모두에서 한계와 trade-off를 명시한다. 18종 Limitation은 v1 (5/7 sprint) 4건 + 5/8 W4 sprint 4건 + V7 audit (5/8) 3건 method-level + 5/11 paper exact 결과 5건의 누적이다. Production deployment 권고와 future work 우선순위는 §5.4-§6.2에서 별도 논의한다.

### Group A — Paradigm framework 한계 (L1~L4, v1)

**L1. Single-table only**: paper Exqutor §V-A multi-relation join 영역은 본 연구 scope 외이다. 단일 테이블 정확성이 multi-table 정확성의 *필요조건*만 성립하며, 5/8 측정에서 multi-vector AND predicate은 단일 대비 25× shrinkage (sweet spot 17.13% → multi 0.67%)로 확인된다. multi-relation 일반화는 future work으로 명시한다.

**L2. Multi-vector / multi-table 일반화 부담**: A2-Fig8 (DEEP+WIKI multi-vector) 4 file only 측정으로 paper §V-A scope 외. joint-aware clustering 또는 multi-vector decomposition이 별도 설계가 필요하다.

**L3. SF=100 (80M) cross-scale validation 부담**: 본 연구는 5/11 paper exact 측정에서 SF=100 cells (DEEP/SIFT/SimSearchNet++ × sf=100)을 모두 회수하였으나, A1-SSN cell만 80GB NPY fetch에 method당 37-88분이 소요되어 14 sequential method cascade 시 timeout 발생. 측정된 cells의 paradigm rollup은 valid이며, 일부 method × cell 조합 누락은 §5.3.G drop list 9 카테고리에서 명시한다.

**L4. KM20 oracle 학습 부담**: Production 환경에서 KM20 stratification 사전 계산은 ~30분 (DEEP sf=100 기준)의 one-time cost를 요구한다. 본 연구는 minibatch_partial M2 (P1, Sculley 2010 partial_fit) 또는 hilbert_real (P2, learning-free Wikipedia xy2d 표준)을 production-friendly replacement로 권고한다.

### Group B — 5/8 W4 sprint 신규 (L5~L8)

**L5. RQ1 measurement methodology robustness**: Phase 6 vs Phase 7의 5-cell 측정 격차 (4/15 시점 발견)는 measurement 방식 자체의 sensitivity로, BERN baseline의 cluster_id 결정성에 따른 1.6-4.4% 차이를 caveat으로 명시한다.

**L6. Effect size practical small (5/8 시점) → 5/11 정정**: 5/8 시점 보고서 narrative는 ★3 Hilbert d=−0.156 (negligible-small)으로 effect size를 honest로 표명하였으나, 5/11 paper exact 측정에서 CaseB ensemble의 Cliff's δ large better 63.5% (284/447) + Hedges' g large 56.4% (252/447)로 effect size가 statistical large로 정정된다. 5/8 시점 표명은 RQ3 single method 비교 영역으로 한정되며, CaseB ensemble augment 영역에서는 large effect가 입증된다.

**L7. P5 Quasi-random LSH Wave 0 fail**: LSH (Indyk-Motwani 1998) 측정에서 +2,092% Wave 0 fail이 발생, 5 paradigm 중 P5만 paradigm winner ★ 없음. K=20 stratification과 n_hyperplanes=5 hyperparameter mismatch가 algorithmic origin (V7 audit L12). 본 연구는 K=20 fixed로 honest limitation 보고하며, K=2^n_hp 정합 (K=16 또는 K=32)은 future work이다.

**L8. 5 paradigm 외 누락 method**: Sketch family (Count-Min Cormode-Muthukrishnan 2005)는 distinct count로 architectural mismatch / Mean-Shift (Comaniciu-Meer 2002)는 K-fixed mismatch / R-tree (Guttman 1984)는 bbox overlap으로 disjoint partition mismatch / MinHash (Broder 1997)는 set similarity mismatch로 모두 future work 명시. 단 본 연구의 P9 InfoTheoretic (HyperLogLog Flajolet 2007)으로 Sketch family의 paradigm anchor가 부분 cover된다.

### Group C — V7 audit 신규 (L9~L11, method-level)

**L9. Reservoir single-cell = RANDOM20 proxy**: single-cell `run_reservoir.py`는 `rng.integers(0, K, size=N)`로 K=20 RANDOM20 proxy 구현 (Vitter Algorithm R 가 아님). multi-cell `_fit_reservoir`는 `rng.choice(N, K, replace=False)` + nearest-centroid으로 Vitter 통계 동치 — P3 streaming sub-paradigm representative로서는 multi-cell 측정만 valid, single-cell 결과는 RANDOM20 variant로 honest 해석.

**L10. LSH K=20 vs n_hp=5 hyperparameter misalignment**: Charikar 2002 sign(W·v) random projection 자체는 정확하나 K=20 vs n_hyperplanes=5 misalignment로 mod 20 collision 발생 (buckets 0~11의 ~2× over-density). Wave 0 +2,092% fail의 algorithmic origin.

**L11. sparse_rp = Li-Hastie-Church 2006 1/√D variant**: Achlioptas 2003 *PODS* 의 density 1/3 가 아니라 Li et al. 2006 *KDD*의 1/√D variant 구현 (코드 line 420-423 verbatim 정정). 두 reference (Achlioptas 2003 + Li 2006)를 본 연구 narrative + §7 References에 정확 명시.

### Group D — 5/11 paper exact 신규 (L12~L18, 5건)

**L12. 측정 미커버 233 cells (20.5%) 9 카테고리 정직 분류**: 9 cells × 56 method × 2 modes = 1008 명목 + 추가 measurement = 1130 — 측정 완료 908+ file (coverage 80.4%, 5/11 18:48 기준). 미커버 233 cells는 9 카테고리로 정직 분류된다: (1) algorithm audit drop 23 method (vinecopula = rank+PCA1D / neuram = PCA1D 100% 동일 / kdtree = idx % n_strata random hash 등가 / ams_count_sketch = lsh line-by-line 동일 등), (2) 자원 한계 (birch CFNode tree 50-200GB RSS, agglomerative 256d sub-pass OOM, A1-SSN 80GB NPY fetch timeout), (3) paper §V-A scope 외 (A2-Fig8 multi-vector, A3-TPCDS ECQO PG segfault), (4) wrapper timeout 부재 (Q1+Q4 batch hung process), (5) 사용자 결정 (★1 hdbscan sklearn KMeans fallback 등가).

**L13. RQ2 Neyman/Anti paradox**: KM20 5-way 측정에서 Anti 1.540 < Prop 1.580 < Neyman 1.595 (DEEP sf=100 sel=0.01 paired n=455)이 paper §V-B 이론 (Neyman optimal allocation)을 위배한다. Root cause는 σ_j range 1.3-1.6× 좁음 + N_i CV=0 (KM20 cluster 균등) → σ-weighted Neyman alloc cos_sim 0.99 (L1 diff 21-39/385) → budget=385 hit count noise (~50/seed @ sel=0.1) > Neyman signal의 자연 결과이다. PartSupp PK가 uniform stratum density 분포로 Neyman 우위가 marginal이 되는 boundary case이며, σ range 큰 cluster imbalance 영역 (RQ3)에서 Neyman 우위 재검증이 필요하다 (future work). 본 paradox는 "분포 알면 prop allocation이 답이며, RQ3 추정 framework로 자연 전환"의 honest narrative + 학술 contribution이다.

**L14. ★3 hilbert PCA 2D lex sort alias**: 5/8 시점 4강 ★3 Hilbert는 코드 차원에서 PCA 2D lex sort로 구현되어 Faloutsos 1989 *Hilbert curve indexing* (SIGMOD)의 진짜 locality 효과가 아닌 PCA proxy 효과를 측정한 것임 (5/10 8 agent algorithm audit 발견). 코드 line 449에서 `("hilbert", "pca2d_lex") alias` 정직 명명되며, 진짜 Hilbert curve의 paradigm anchor는 M6 zorder_morton (Morton 1966) + M7 skilling_hilbert (Skilling 2004 conditional swap simplification 1줄 disclosure) + hilbert_real (Wikipedia xy2d 표준) 3건으로 보강된다 (§4.4.3 학술 contribution).

**L15. byte-identical cells 7쌍 (cells inflation)**: 9 명목 cells × 56 method × 2 modes = 1008 cell 측정 중 (A1-DEEP ≡ A5-scale-sf100, A2-Fig9 ≡ A5-scale-sf10) 7 cell pair가 byte-identical 일치 — DEEP sf=100/sf=10의 동일 setup, query set 만 다른 결과. 명목 9 cells / **실제 6 unique cells × 56 method = 672**. 본 연구는 paradigm rollup 산출 시 unique 6 cells 기반 obs count (e.g. 12 method × 106 obs P2 등)로 보고하며, byte-identical 7쌍을 §3.6 측정 매트릭스 표 caveat에 명시한다.

**L16. A4-sel sel=0.001 calibration parquet 부재 → fallback heuristic**: A4-sel cell의 sel=0.001 측정에서 D_target calibration parquet이 부재하여 D=0.86 fallback heuristic + true_card = N × 0.001로 진행. 정확 calibration 시 ~6h 재측정 필요. 5/27 발표 backup slide caveat으로 명시 권고 (재측정 우선순위 ↓, sel=0.01/0.10 cells의 narrative anchor가 강력함).

**L17. P9/P10 신규 paradigm anchor 측정 coverage (5/11 18:16 launch 진행 중)**: P9 InfoTheoretic (HyperLogLog) + P10 Density (KDE Parzen)는 본 연구가 신규 도입한 paradigm으로, 5/11 18:16 KST 8 cells × 2 modes 확장 measurement launch 후 18:48 KST hyperloglog 9 cells 회수 완료 (P9 anchor mean -7.60% 강화). kde_parzen / mhist2 / rsvd / wavelet_hist 4 method 64 measurement는 background 진행 중이며, 회수 후 P10 / P6 / P4 paradigm rollup 신뢰성 모두 9 cells 평균으로 강화 예정 (5/12 morning 회수).

**L18. 본 연구 framework의 honest scope 한정**: 본 연구는 Exqutor 논문 §V-B Adaptive Sampling 영역의 paper exact 재현 + ensemble augment의 정량적 가치 검증으로 contribution을 한정한다. ECQO (§V-A 인덱스 있을 때 HNSW range query) 영역은 paper main result로 그대로 인정하며, multi-relation join (§V-A multi-table) 영역은 future work이다 (사용자 5/11 14:18 verbatim "Exqutor 외 영역 / 외의 조건을 억지로 추가하는 개념이 아닌 정확히 비교할 수 있도록"). 본 연구는 paper §V-B sampling step에 우리 method estimate를 산술 평균으로 layer 추가하는 paper-friendly augment 구조이며, paper §V-B 자체는 변경하지 않는다.

---

## 본 sketch 사용 가이드 (5/29~6/10 W5~W6 sprint, 박세은 owner)

1. §5.3 Group A/B/C/D 본문 sketch는 그대로 학술 산문 직접 사용 가능 (한국어 + 영어 학술 용어 병기)
2. Q4 4 method 회수 후 L17 update (kde_parzen / mhist2 / rsvd / wavelet_hist 회수 결과 + P10/P6/P4 paradigm rollup 강화 수치)
3. 5/15 박광현 미팅 confirm 사항 반영 (만약 limitation 추가 또는 narrative 변경 시 minor 조정)
4. 본문 분량 ~3p (~70 line) — 학교 양식 적정 dense
5. Group 분류는 v1 history (Group A) + 5/8 sprint (Group B) + V7 audit (Group C) + 5/11 신규 (Group D)로 timeline + 카테고리 동시 표현

---

작성: 2026-05-11 19:05 KST  
다음: Q4 4 method 회수 후 L17 수치 update + 5/15 박광현 미팅 confirm 후 narrative 정합성 점검 → 5/29~6/10 sprint 본문 작성 (박세은 통합)
