# 6/11 보고서 §1 Introduction — 본문 sketch (5/11 19:10)

> **base**: `plans/6_11_보고서_outline_v3_update_plan_20260511.md` §2.1 Introduction 3-4p
> **목적**: 본문 작성 부담 ↓ 위한 학술 산문 sketch
> **owner**: 박세은 (통합) + 조현빈 (선행 연구 narrative)
> **분량**: ~3p (~70 line dense 학술 산문)

---

## §1 Introduction

### §1.1 연구 배경 — Vector Database의 분석 쿼리와 카디널리티 추정의 중요성 (15-18 line)

벡터 데이터베이스 (Vector Database)는 고차원 임베딩 (image embedding, text embedding, multi-modal embedding)을 효율적으로 저장하고 검색하는 시스템으로, 추천 시스템 / 의미 검색 / 이상 탐지 / 멀티미디어 검색 등 광범위한 응용에서 핵심 인프라로 자리잡고 있다. 최근에는 단일 top-K 유사도 검색을 넘어, 벡터 거리 조건과 일반 SQL 조건을 결합한 **Vector-augmented Analytical Queries (VAQ)** 가 새로운 워크로드로 등장하였다. 예를 들어 "이미지가 주어진 query 임베딩과 거리 0.86 미만인 partsupp 행 중 ps_supplycost > 100 인 행의 평균 가격"과 같은 query는 단순 ANN 검색이 아닌 range query와 SQL 결합이며, 정확한 query plan 선택을 위해 vector range 조건의 카디널리티 추정 (cardinality estimation)이 결정적이다.

기존 PostgreSQL pgvector / VBASE / DuckDB는 vector range 조건의 카디널리티를 33.3% / 50% / 100% 등 고정 비율로 가정하여 추정하는데, 이는 데이터의 실제 분포 (data skew, intrinsic dimensionality, cluster structure)를 무시하는 한계가 있다. 본 연구의 base가 되는 **Exqutor** (BDAI Research, arXiv:2512.09695v2)는 이 문제를 두 paradigm으로 해결한다: (1) **§V-A ECQO** (Extended Cardinality Query Optimizer) — 벡터 인덱스가 있을 때 HNSW range query를 1-2ms에 활용하여 정확한 카디널리티 추정, (2) **§V-B Adaptive Sampling** — 벡터 인덱스가 없을 때 모멘텀 기반 동적 sample size 조정 (Eq 1-6) 으로 unstratified Bernoulli sampling의 정확도를 개선.

### §1.2 문제 정의 — Exqutor §V-B의 사각지대 (8-10 line)

본 연구는 Exqutor §V-B Adaptive Sampling 영역에 집중한다. 이 영역은 벡터 인덱스가 부재한 단일 테이블 시나리오에서 작동하며, paper에서는 unstratified Bernoulli sampling + momentum adjustment의 자체 내부 robustness만을 보고한다 (Adaptive vs Fixed sample size 내부 비교). 본 연구는 이 영역에서 **분포 인지 stratified sampling이 paper의 unstratified Bernoulli baseline을 augment하는 정량적 가치**를 paired Δ% + 효과크기 + paradigm rollup의 paper review-grade 통계로 검증한다. 즉 paper의 §V-B sampling step 위에 우리 method의 estimate를 산술 평균으로 layer 추가하는 ensemble 구조이며, paper §V-B 자체는 변경하지 않는 paper-friendly augment이다.

### §1.3 연구 질문 RQ1/RQ2/RQ3 (10-12 line)

본 연구는 5/5 회의에서 RQ를 다음 3 영역으로 재정립하였다.

- **RQ1** (skew motivation): 기존 random sampling이 skew 데이터셋에서 얼마나 부정확한가? Bernoulli random vs KM20 stratified의 mean Q-error gap 정량 비교.
- **RQ2** (분포 known oracle): 분포가 알려진 KM20 cluster에서 어떤 sample allocation 방식이 최적인가? Bernoulli / Equal / Proportional / Neyman / Anti-Neyman 5-way ablation.
- **RQ3** (분포 unknown estimation): 분포를 추정해야 할 때 어떤 paradigm이 효과적인가? 9 paradigm × 56 method × 9 cells × 2 modes (CaseA 단독 대체 + CaseB ensemble augment) 종합 비교.

본 연구의 contribution은 §V-B 영역에 한정되며 (사용자 5/11 14:18 verbatim "Exqutor 외 영역 / 외의 조건을 억지로 추가하는 개념이 아닌 정확히 비교할 수 있도록"), ECQO §V-A (인덱스 있을 때 HNSW range query 활용)는 paper main result로 그대로 인정한다.

### §1.4 본 연구의 9 contribution (15-18 line)

본 연구는 다음 9 contribution을 제시한다.

1. **RQ1 Selectivity Gradient 단조성 통계 입증**: DEEP/SIFT/SimSearchNet++ × sf=100 paper exact 측정에서 mean gap +3.74% (Bernoulli vs KM20 stratified, sel{0.01, 0.10}).
2. **RQ1-sub Measurement Methodology Robustness**: Phase 6 vs Phase 7의 5-cell 측정 격차로 baseline cluster_id 결정성 sensitivity 명시.
3. **RQ2 KM20 oracle의 sample-size robustness + Anti < Prop < Neyman paradox honest finding**: σ_j range 1.3-1.6× narrow + N_i CV=0의 자연 결과 root cause 학술 contribution.
4. **RQ3-1 9 paradigm × 56 method framework**: P1 Cluster / P2 Spatial / P3 Streaming / P4 Dim Reduction / P5 QMC / P6 Quantization / P9 InfoTheoretic / P10 Density (P7 Subspace + P8 Graph future work).
5. **RQ3-2 ★3 hilbert defect rectify**: PCA 2D lex sort alias 정직 명명 + M6 zorder_morton + M7 skilling_hilbert + hilbert_real 3건 paradigm anchor 추가로 "PCA proxy locality vs 진짜 Hilbert locality 분리 검증" 학술 finding.
6. **RQ3-3 sparse_rp ★4 reference 정정**: Achlioptas 2003 ❌ → Li-Hastie-Church 2006 ⭕ 1/√D variant.
7. **CaseA 단독 대체 narrative 무너짐의 정량 입증**: one-sided BH-FDR 0/437 (0.0%) + Cliff's δ worsening 36.8% > better 14.4%.
8. **CaseB ensemble augment의 통계 압도**: paired CaseB > CaseA 92.9% (404/435) + Cliff's δ large better 63.5% (284/447) + Hedges' g large 56.4% (252/447) + paradigm rollup 5 paradigm 모두 statistical signif.
9. **paper exact 측정 정합성 4축 검증**: JSON integrity 0 fail + Reproducibility 280/280 byte-identical + paper Eq 1-6 + hyperparam line-by-line 일치 + Fig 12 영역 mean qe_trim 1.6180 paper 1.69 -4.26% 일치 (paper review-grade).

### §1.5 본 보고서 구성 (5-6 line)

§2에서는 Exqutor 본 논문 구조와 5 paradigm clustering / sampling cardinality estimation의 학술적 위치를 정리한다. §3에서는 본 연구 paradigm 9 framework + 56 method registry + paper exact verbatim 재현 방법론을 명시한다. §4에서는 RQ1/RQ2/RQ3 + Adaptive 비교 (CaseA/CaseB) + 측정 정합성 4축 검증을 보고한다. §5에서는 학술 contribution 9종 + Limitation 18종 + Production deployment 권고 + 5/15/5/22 자문 의견을 논의한다. §6에서는 결론 + Future Work 8건을 명시한다.

---

## 본 sketch 사용 가이드 (5/29~6/10 W5~W6 sprint, 박세은 통합)

1. §1.1~§1.5 본문 sketch는 그대로 학술 산문 형식 직접 사용 가능
2. §1.4 contribution 9 numbering은 v3 outline plan 기반 (v2 7 → v3 9, 5/11 P9/P10 신규 paradigm 발굴 + RQ2 paradox honest finding 추가)
3. 5/15 박광현 미팅 confirm 결과 반영 시 §1.4 contribution 일부 minor 조정 가능
4. Q4 4 method 회수 후 §1.4 contribution 1 RQ1 mean gap +3.74% 등 수치 update 검토
5. 본문 분량 ~3p (~70 line) — 학교 양식 적정 dense

---

작성: 2026-05-11 19:10 KST  
다음: §2 Background sketch (이동욱 owner) + §6 Conclusion + Future Work sketch 추가 (선택), Q4 회수 후 §1.4 수치 update + 5/15 미팅 confirm 후 narrative 정합성 점검 → 5/29~6/10 sprint 본문 작성
