# 속도는벡터 — 박광현 교수 5/22 사전 보고 (v11 framing 정리)

> **수신**: 박광현 교수님 (BDAI 연구실) / 임채림 석사
> **발신**: 속도는벡터 (박세은·강재현·조현빈·이동욱)
> **일시**: 2026-05-16 작성, 5/22 (목) 미팅 사전 배포 (D-5 자문 자리)
> **목적**: 5/27 최종 발표 D-5 시점 framing 단순화 (v11) 정리 + Phase 1+2+3 + dynamic 할당 mechanism 자문 요청

---

## 0. 한 문장 요약

본 5/22 사전보고는 5/15 미팅 이후 박세은 framing 단순화 의도 (5/15 카톡 + 5/16 00:18 정리) 를 완전히 반영한 v11 framing 으로의 전환 — paper 영역의 cardinality 추정 mechanism 은 그대로 인정하고 본 연구는 그 estimation 의 input 인 **Sample Selection 영역만** contribution 으로 한정 — 을 전제로, 사용 16 method × 12 cell × CaseB only 측정 portfolio (약 2039 file) 와 dynamic 할당 mechanism 의 5/27 발표 D-5 시점 자문 사항 6 건을 정리한다.

---

## 1. v11 framing 핵심 (5/15 → 5/22 변경 영역)

### 1.1 main theme 변경

| 영역 | 이전 (v10, 5/15 기준) | 변경 (v11, 5/22 기준) |
|---|---|---|
| 본 연구 main theme | "Measurement-driven Distribution-aware **Cardinality Estimation** for VAQ" | "**Distribution-aware Sample Selection** for VAQ Cardinality Estimation" |

본 변경의 핵심 의의는 두 가지다. 첫째, "Cardinality Estimation" 영역은 paper Exqutor (arXiv:2512.09695v2) 본인의 contribution 영역 — 본 연구는 paper §V-B Adaptive Sampling 의 cardinality 추정 mechanism 자체에 contribution 을 주장하지 않는다. 둘째, 본 연구의 영역은 그 estimation 의 **input 인 Sample Selection** — 즉 paper 의 random Bernoulli sampling 자리에 분포 인지 sample selection method 를 augment 하여, sample 의 quality 가 estimation accuracy (Q-error) 에 미치는 영향을 정량 검증한다. 본 framing 은 학부 capstone 의 이론 검증 자세에 부합하며 paper 와의 contribution 경계가 명확하다.

### 1.2 framing layer 명확 분리

본 v11 framing 은 두 layer 로 명확 분리된다.

| layer | 영역 | 본 발표 영역 |
|---|---|---|
| **paper 영역 (그대로 유지)** | (a) §V-A ECQO HNSW range query (인덱스 있을 때 정확 cardinality 1-2ms) (b) §V-B Adaptive Sampling Eq 1-6 momentum 보정 (c) cardinality 추정 mechanism 자체 (Bernoulli est) | 간단 소개 (paper 본인 contribution 인정) |
| **우리 contribution 영역** | (a) Phase 1 = 분포 인지 sample selection (sample 추출 mechanism) (b) Phase 2 = dynamic 할당 mechanism (Type 별 best method 자동 선택) (c) Phase 3 의 결합 영역만 = est_b1 + est_method 산술 평균 (minimal augmentation) | 본 발표 핵심 |

본 두 layer 의 분리가 v11 framing 의 base axis 다. paper 영역의 cardinality 추정 mechanism (Bernoulli + Adaptive Eq 1-6) 은 그대로 유지하고, 본 연구는 paper baseline 위 sample selection 영역 augment — Phase 1+2 의 분포 인지 stratification + sample 추출 + Phase 3 의 결합 minimal — 만 contribution 으로 한정한다.

---

## 2. Phase 1 + 2 + 3 (우리 contribution 영역 자세히)

### 2.1 Phase 1 — 분포 인지 stratification (offline, 1회)

데이터셋 load 시 sample selection 영역 stratification 을 수행한다. 본 Phase 는 본 연구 핵심 contribution 의 first half 다. 데이터셋 진입 시 (① Type 판별 = row 수 / structure / dimension 기준 Type 1/2/3/4a/4b 분류 → ② Type 별 best sample selection method 자동 선택 = §3 dynamic 할당 mechanism 직접 적용 → ③ K=20 stratum 영역 sample selection = 16 method 中 dynamic 선택) 의 3 step 으로 진행되며 결과는 row → stratum_id (sid 0..K-1) 매핑이다. 본 Phase 의 fit_time 은 sparse_rp 3.67s ~ hilbert_real 43.50s range (Pareto Top 5 method) — 11.9× 차이 — 의 직접 측정으로 cover 된다. paper 의 random Bernoulli 가 분포 정보를 활용하지 않는 반면, 본 Phase 는 sample selection 영역에서 분포를 빠르게 catch 한다는 점이 핵심 차이다.

### 2.2 Phase 2 — sample 추출 (online, 매 query)

쿼리 진입 시 sample selection 영역 추출을 수행한다. 본 Phase 는 본 연구 핵심 contribution 의 second half 다. (① **sample budget N=385** = paper Eq 1 verbatim 100% 정합 유지, paper 영역 그대로 → ② 각 stratum 비례 sample 추출 = proportional allocation, K=20 → ③ 추출된 sample 영역 → est_method 계산 = matching × weight) 의 3 step. paper 의 sample budget 영역은 그대로 유지하고 추출 mechanism 영역만 분포 인지 stratification 영역 base 위에서 변경한다는 점이 핵심이다. 본 Phase 는 paper §V-B 의 sample budget 정합성을 위반하지 않으면서 분포 인지 sample selection 의 효과만 정량 검증할 수 있는 minimal augmentation 영역 base 다.

### 2.3 Phase 3 — 결합 minimal (online, 매 query)

쿼리 진입 시 결합 단계. 본 Phase 의 결합 영역만 우리 contribution 이며, paper Adaptive Eq 1-6 영역은 그대로 유지된다. (① **est_b1** = paper Bernoulli random sample est, paper 영역 그대로 → ② **est_method** = 우리 sample selection method est, 우리 영역 → ③ **est_final = (est_b1 + est_method) / 2.0** = 산술 평균 결합, α=0.5 fixed minimal → ④-⑦ paper Eq 2-6 verbatim 영역 보정 = 그대로 유지, paper 영역) 의 7 step. 산술 평균 (α=0.5 fixed) 의 의의는 두 가지다. 첫째, paper 영역의 mechanism 을 위반하지 않는 minimal augmentation — Adaptive Eq 1-6 의 momentum 보정 trajectory 가 변동하지 않는다. 둘째, est_b1 (Bernoulli, bias 0 high variance) + est_method (분포 인지, distribution-aware low variance) 의 보완성이 산술 평균 1 회로 의미 있는 효과를 발현하는지를 정량 검증할 수 있는 cleanest comparison 영역 base 다.

---

## 3. 사용 16 sample selection method + Pareto Top 5

본 v11 framing 의 사용 16 sample selection method 는 7 paradigm 영역 covering — Cluster (3) / Spatial (3) / Streaming (1) / DimReduction (4) / QMC (2) / Quantization (2) / InfoTheoretic (1). 본 16 method 는 모두 sample selection 영역 mechanism 이며 cardinality 추정 algorithm 영역이 아니다. 5/15 미팅 이전 폐기 결정된 40 method (정합성 위반 10 + 측정 미커버 7 + algorithm audit drop 23) 는 본 발표 자료에서 완전히 제외된다.

| Paradigm | 사용 method | count | reference |
|---|---|---:|---|
| **P1 Cluster** | minibatch_partial / gmm / faiss_ivf | 3 | Sculley 2010 KDD / Dempster-Laird-Rubin 1977 EM JRSS / Johnson-Douze-Jégou 2017 FAISS IEEE |
| **P2 Spatial** | hilbert_real ★ / zorder_morton / skilling_hilbert | 3 | Faloutsos 1989 PODS / Morton 1966 IBM / Skilling 2004 AIP |
| **P3 Streaming** | chao_weighted ★ | 1 | Chao 1982 *Biometrika* |
| **P4 DimReduction** | sparse_rp ★ / pca1d ★ / rsvd / ica_fastica | 4 | Li-Hastie-Church 2006 KDD / Pearson 1901 Phil. Mag. / Halko-Martinsson-Tropp 2011 SIAM Rev. / Hyvärinen 1999 IEEE TNN |
| **P5 QMC** | cum_sqrtf / lavallee_hidiroglou | 2 | Dalenius-Hodges 1959 JASA / Lavallée-Hidiroglou 1988 Survey Methodology |
| **P6 Quantization** | rabitq_strat / mhist2 | 2 | Gao-Lin 2024 VLDB Best Paper / Poosala 1997 VLDB |
| **P9 InfoTheoretic** | hyperloglog ★ | 1 | Flajolet-Fusy-Gandouet-Meunier 2007 AofA |

★ = Pareto Top 5 (정확도 best = 자원 best). Pareto Top 5 method 는 sparse_rp (fit_time 3.67s 최단) / chao_weighted (Type 1 small sf=1 −14.11% best) / hyperloglog (메모리 O(m × log log n) 최compact) / pca1d (10/10 textbook audit pass) / hilbert_real (★3 정정 후 raw Wikipedia 표준 Hilbert curve, Type 4a multi 224-288d edge) 영역. 본 5 method 가 §4 정확도 evidence 의 직접 base 다.

본 §3 의 영역 주의 사항은 두 가지다. 첫째, **HyperLogLog 자체는 paper 영역에서 cardinality estimation sketch 영역 알려진 algorithm 이지만**, 본 연구는 이 sketch 결과를 sample selection 영역의 stratum 부여 mechanism 의 input 으로 활용한다 — cardinality estimation 영역에 contribution 을 주장하지 않는다. 둘째, ★3 hilbert 의 PCA 2D + lex sort alias 정정 (5/10 audit) 후 raw Wikipedia 표준 Hilbert curve (`hilbert_real`) 로 별도 9 cell × 2 mode 재측정 했고 본 v11 framing 의 사용 16 method 中 본 정정된 `hilbert_real` 만 활용한다.

---

## 4. Q-error paired Δ% 92.5% evidence (sample selection vs random Bernoulli)

본 v11 framing 의 핵심 정량 evidence 는 **paired CaseB < CaseA = 92.5%** (455/492 cells, p<10⁻⁴⁵) 다 (5/12 02:50 REPORT v11 측정 base, 1001 file). 본 evidence 의 의미는 sample selection 영역에서 우리 method 의 `est_method` 와 paper Bernoulli 의 `est_b1` 의 산술 평균 결합 (CaseB) 이 paper Bernoulli 단독 (B1 baseline) 대비 Q-error 영역에서 거의 모든 cell 에서 우위를 보인다는 paper review-grade evidence 다.

| 지표 | 값 | 의미 |
|---|---:|---|
| paired CaseB < B1 | **92.5%** (455/492) | sample selection 영역 결합 minimal 이 paper Bernoulli baseline 대비 거의 모든 cell 우위 |
| Cliff's δ large better | **63.0%** (311/494) | non-parametric effect size large 비율 |
| Hedges' g large | **55.7%** (275/494) | parametric standardized mean diff large 비율 |
| one-sided p<0.05 outperform | **45.3%** (224/494) | BH-FDR 통계 유의 cell 비율 |
| **paired test p-value** | **< 10⁻⁴⁵** | paper review-grade evidence |
| **negative control: CaseA 단독 대체** | **0/493 = 0%** | sample selection 영역 단독 대체 무효 (5/15 framing 폐기 결정) |

본 evidence 의 framing 영역 핵심은 **"sample selection 영역 우리 method 가 random Bernoulli 대비 Q-error paired Δ% 개선"** — cardinality 추정 algorithm 영역 contribution 표현이 아니다. 5/15 미팅 이후 단독 대체 (CaseA) 가설은 폐기되었으며 (757 file rm 완료), 본 5/22 사전보고는 결합 (CaseB only) framing 으로 일관 통일된다.

paradigm rollup mean Δ% 영역도 본 framing 일관 — 본 측정 8 paradigm 中 P10 Density (−11.93%, n=1) / P9 InfoTheoretic (−7.60%, n=9) / P3 Streaming (−6.63%, n=44) / P4 DimReduction (−6.03%, n=104) / P2 Spatial (−5.57%, n=107) 의 5 paradigm 통계 압도. 본 5 paradigm 모두 sample selection 영역 mechanism 이며, 본 mean Δ% 영역도 sample selection 영역 Q-error paired 개선의 정량 표현이다.

---

## 5. dynamic 할당 mechanism (Type 1/2/3/4a/4b)

본 v11 framing 의 dynamic 영역은 sample selection 영역만 dynamic 이며, paper Adaptive Eq 1-6 영역은 그대로 유지 (dynamic X) 된다. 본 dynamic 할당 mechanism 의 base axis 는 데이터셋 4 type 분류 (Type 1/2/3/4a/4b) — scale × structure × dimension 기준 — 다.

| Type | 정의 | dim | 본 측정 cell | 권장 sample selection method |
|---|---|---:|---|---|
| **Type 1** | small single sf=1 (0.1M rows) | 96~768 | DEEP/SIFT/SSN/WIKI/YFCC A5-sf1 + v6/v7 | chao_weighted K=20 (−14.11% best) |
| **Type 2** | medium single sf=10 (1M rows) | 96~768 | DEEP/SIFT/SSN/WIKI A5-sf10 + v6 | chao_weighted K=20 (sweet spot 약함, sf=1/sf=100 의 절반) |
| **Type 3** | large single sf=100 (10M rows, 저-중차원) | 96~256 | DEEP/SIFT/SSN A1 | chao_weighted / sparse_rp K=20 (−11~−12%) |
| **Type 4a** | large multi 224-288d (10M rows) | 224~288 | DEEP+SIFT/DEEP+YFCC | hilbert_real K=30 (slight edge) |
| **Type 4b** | large multi 864d (10M rows) | 864 | DEEP+WIKI | Centroid tuple (−7.37% best, 학습 비용 0) |

본 dynamic 할당 mechanism 의 4-step flow 는 (① 데이터셋 진입 → ② Type 판별 = row 수 / structure / dimension 기준 → ③ Type 별 best sample selection method 자동 선택 → ④ CaseB ensemble = Phase 3 minimal augmentation) 영역 sample selection 영역만 dynamic 이며, 본 4-step 다음 paper §V-B Adaptive Eq 1-6 영역은 그대로 유지된다. 본 dynamic 영역의 핵심 의의는 데이터셋 특성에 따라 best sample selection method 가 다르며, 본 4 type axis 가 그 자동 선택 mechanism 의 base 라는 점이다 — 이 axis 자체가 본 연구 핵심 contribution 영역의 second half 다 (Phase 1 의 step ②).

---

## 6. 측정 portfolio (~2039 file, B1 + CaseB only)

본 v11 framing 의 측정 portfolio 는 **약 2039 file** — B1 (대조군 = paper Bernoulli + Adaptive) + CaseB (실험군 = sample selection + Adaptive) 두 영역 only 영역. 5/15 미팅 이전 단독 대체 가설 (CaseA) 은 폐기 결정 후 757 file rm 완료. 본 portfolio 는 5/12 02:50 REPORT v11 측정 691 file (B1 9 + CaseB 682 부분) 영역 base 위, 5/15-16 새벽 chain 측정 약 1348 file 영역 추가 — v6_caseB (Pareto Top 5 + B1 × 9 cell, 약 50 file) + v7_extras (Pareto Top 5 + B1 × 3 cell, 약 18 file) + v8_full (12 cell × 16 method × CaseB, 약 192 file) + v9_sel_sweep (16 cell × 2 sel × 17 method, 약 680 file) + v6v7_fix (K=10 KeyError + A8 NPY symlink fix, 약 18 file) — 영역 합산. dataset 5 종 (DEEP/SIFT/SSN/WIKI/YFCC + multi-table 3 종) × sf 3 종 (1/10/100) × method 16 × selectivity 3 종 (0.001/0.01/0.10) 영역 cover.

본 portfolio 의 framing 일관성은 두 가지로 보장된다. 첫째, B1 + CaseB only — CaseA 폐기 결정 후 framing 안에 단독 대체 가설 표현이 남아있지 않다. 둘째, 사용 16 method 만 측정 — 폐기 40 method (정합성 위반 10 + 측정 미커버 7 + algorithm audit drop 23) 영역 새 측정 X. 본 portfolio 영역 base 위 §4 정확도 evidence (paired Δ% 92.5%) + §5 dynamic 할당 mechanism (Type 별 best method 매핑) 영역 직접 도출.

---

## 7. 5/27 발표 D-5 자문 요청 사항 (6 건)

본 5/22 미팅에서 박광현 교수님 / 임채림 석사께 다음 6 건 자문 요청:

첫째, **v11 framing 단순화 의도의 적절성** — paper 영역의 cardinality 추정 mechanism 을 그대로 인정하고 본 연구는 sample selection 영역만 contribution 으로 한정 + main theme "Distribution-aware Sample Selection for VAQ Cardinality Estimation" 영역 학부 capstone 이론 검증 자세에 부합 + paper 와의 contribution 경계 명확성에 대한 자문 요청.

둘째, **Phase 1+2+3 의 base axis 적절성** — Phase 1 (분포 인지 stratification, offline) + Phase 2 (sample 추출, online) + Phase 3 (결합 minimal, est_final = (est_b1 + est_method) / 2.0 산술 평균) 의 3 phase 영역 본 연구 핵심 contribution 영역 축으로의 적절성 + α=0.5 fixed (산술 평균 1 회) minimal augmentation 영역 paper 영역 mechanism 위반 방지의 충분성에 대한 자문 요청.

셋째, **사용 16 method 영역 paradigm coverage 의 충분성** — 7 paradigm × 16 method 영역 sample selection 영역 cover (P1 Cluster 3 + P2 Spatial 3 + P3 Streaming 1 + P4 DimReduction 4 + P5 QMC 2 + P6 Quantization 2 + P9 InfoTheoretic 1) + Pareto Top 5 (sparse_rp / chao_weighted / hyperloglog / pca1d / hilbert_real) 영역 5/27 발표 detail slide (8-15) 핵심 axis 의 적절성에 대한 자문 요청.

넷째, **paired Δ% 92.5% evidence 영역 paper review-grade anchor 의 적절성** — sample selection vs random Bernoulli 영역 Q-error paired 92.5% (p<10⁻⁴⁵) + Cliff's δ 63.0% / Hedges' g 55.7% / one-sided p<0.05 45.3% + negative control (CaseA 단독 대체 0/493) 영역 5/27 발표 climax slide (18) 영역 거대 수치 표현의 적절성에 대한 자문 요청.

다섯째, **dynamic 할당 mechanism 영역 4 type 분류 axis 의 적절성** — 데이터셋 4 type (Type 1/2/3/4a/4b) × scale × structure × dimension 기준 분류 + Type 별 best sample selection method 자동 선택 (chao_weighted / sparse_rp / hilbert_real / Centroid tuple) + sample selection 영역만 dynamic + paper Adaptive Eq 1-6 영역 그대로 유지 영역 framing 일관성에 대한 자문 요청.

여섯째, **5/27 발표 D-5 시점 deck v11 (25 slide) 영역 framing 일관성의 점검 필요성** — slide 2 main theme + slide 3 framing layer 분리 + slide 5 우리 영역 3 phase 흐름 + slide 8-15 paradigm 별 사용 16 method + slide 17 dynamic 할당 mechanism flow + slide 18 거대 수치 evidence + slide 23 결론 Finding 5 영역 cardinality 추정 표현의 완전 제거 + Sample Selection 표현 일관성 영역 점검 필요성에 대한 자문 요청.

---

## 8. 첨부 자료 (서버 또는 GitHub)

- **v11 framing prompt 3 part** (5/16 00:50 작성, claude.ai/design Keynote_Capstone paste 대기): `submission/_drafts/속도는벡터_5_27_키노트_prompt_v11_part{1,2,3}_*.md`
- **v6 narrative draft Phase A** (5/16 작성, Phase B chain 의존 §6/§8/§10-§13 placeholder): `submission/_drafts/속도는벡터_본연구_narrative_v6_draft_20260516.md`
- **v5 narrative 최종정리** (5/15 21:00 박세은 review base): `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v5_draft.md`
- **REPORT v11 1362 line** (paired Δ% table + paradigm rollup + drop list 9 카테고리): 서버 `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md`
- **handoff v32** (5/16 01:16 chain 진행 중, K=10 fix + A8 NPY symlink + chain monitor PID 87193): `_internal/handoff/active/handoff_v32_*.md`
- **이전 5/15 미팅 자료 4 file** (5/12 11:56 PDF + 12:15 README, 본 5/22 사전보고 narrative base reference): `submission/_drafts/archive/박광현_미팅_예상질문_답변_가이드_20260511.{md,pdf}` + `archive/박광현+임채림_5월15일_사전보고_요약_20260512.{md,pdf}` + `archive/속도는벡터_박광현미팅_5월15일_slide_draft_20260511.{md,pdf}` + `archive/속도는벡터_5_15_박광현미팅_핵심정리_v1.{md,pdf}`
- **GitHub**: https://github.com/johyunbin/Capstone

---

## 9. END

작성: 2026-05-16 KST · 5/22 (목) 박광현 교수 미팅 D-5 사전 배포 · v11 framing (박세은 5/15 카톡 + 5/16 00:18 정리 단순화 의도 완전 반영) · main theme "Distribution-aware Sample Selection for VAQ Cardinality Estimation" + framing layer 명확 분리 (paper 영역 cardinality 추정 + 우리 영역 sample selection augment) + Phase 1+2+3 (분포 인지 stratification + sample 추출 + 결합 minimal α=0.5) + 사용 16 method × 7 paradigm + Pareto Top 5 + paired Δ% 92.5% evidence + dynamic 할당 mechanism (Type 1/2/3/4a/4b) + 측정 portfolio ~2039 file (B1 + CaseB only) + 5/27 발표 D-5 자문 요청 6 건. 다음 단계: 5/22 미팅 confirm 결과 → 5/27 발표 deck v11 framing 일관성 최종 정정 → 5/26 finalize → 5/27 19:00 최종 발표 (D-11).
