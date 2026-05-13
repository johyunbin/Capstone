# Multi-join re-stratification 결과 분석 (5/13)

## 0. 작성 status

- **분석 대상**: A2-Fig9 cell (DEEP+WIKI cross) × 4 anchor method × 2 mode = 8 measurement
- **회수 status (5/13 14:32 KST)**: **3/8 회수 완료** (sparse_rp CaseA/CaseB, hilbert_real CaseA)
- **회수 진행 중**: hilbert_real CaseB (14:31 ~ 14:52 예상)
- **전체 ETA**: 5/13 16:16 KST
- **본 문서 status**: **PARTIAL — 회수 진행 중 (3/8)**, 8/8 회수 후 finalize 예정

---

## 1. 측정 framework

### 1.1 scope

- cell: A2-Fig9 (Fig 9, DEEP+WIKI cross, sf=10)
- query: TPC-H q3, q10, q12 (DEEP 96 차원 space)
- table: partsupp_deep_10 ⨝ part_wiki_10 ON ps_partkey = p_partkey
- vector dim: partsupp_deep 96d + part_wiki 768d = 864d concat
- method: sparse_rp / hilbert_real / hyperloglog / chao_weighted (4 paradigm anchor)
- mode: CaseA (단독 대체) / CaseB (Bernoulli + stratified 산술 평균 ensemble)
- 총 measurement: 4 × 1 × 2 = 8

### 1.2 wrapper v2 design (5/13 13:30 fix)

초기 wrapper v1 (5/13 12:25 launch) 은 864d concat vector pool 을 그대로 반환하는 design 으로 stratified_estimate 단계에서 query (96d) 와 dimension mismatch broadcasting 실패가 발생하였다 (sparse_rp CaseA 38분 fail, CaseB 22분 fail). 

wrapper v2 (5/13 13:30 fix) 는 두 단계 분리:

1. **Stratification 학습**: 864d concat vector (DEEP 96 + WIKI 768) 위에서 MiniBatch K-means K=20 fresh 학습. 두 테이블 vector 정보 모두 활용하여 stratum 형성.
2. **Vector pool 반환**: 96d query space (partsupp_deep 측) 만 추출하여 반환. stratum_id 는 학습 결과 그대로 carry-over.

이로써 query (96d) 와 vector pool (96d) dimension 정합성 확보 + stratum 정보는 multi-join 결합 학습 결과 반영.

---

## 2. Partial 결과 (3/8 회수, 5/13 14:32 시점)

### 2.1 측정값 raw table

| Method | Mode | B1 baseline qe_trim | carry-over qe_trim | multi-join re-strat qe_trim |
|---|---|---:|---:|---:|
| sparse_rp | CaseA | 1.5407 | 1.6104 | 1.5556 |
| sparse_rp | CaseB | 1.5407 | 1.4393 | 1.4353 |
| hilbert_real | CaseA | 1.5407 | 1.5681 | 1.5730 |
| hilbert_real | CaseB | 1.5407 | 1.4471 | [TBD ~14:52 회수] |
| hyperloglog | CaseA | 1.5407 | 1.5584 | [TBD ~15:13 회수] |
| hyperloglog | CaseB | 1.5407 | 1.4613 | [TBD ~15:34 회수] |
| chao_weighted | CaseA | 1.5407 | 1.6353 | [TBD ~15:55 회수] |
| chao_weighted | CaseB | 1.5407 | 1.4483 | [TBD ~16:16 회수] |

### 2.2 paired Δ% 비교 (vs B1 baseline)

| Method | Mode | carry-over Δ% | multi-join re-strat Δ% | 차이 (re-strat - carry) |
|---|---|---:|---:|---:|
| **sparse_rp** | CaseA | **+4.52%** | **+0.97%** | **-3.55%p ★ 큰 개선** |
| sparse_rp | CaseB | -6.58% | -6.84% | -0.26%p (거의 동등) |
| hilbert_real | CaseA | +1.78% | +2.10% | +0.32%p (거의 동등) |
| hilbert_real | CaseB | -6.07% | [TBD] | [TBD] |
| hyperloglog | CaseA | +1.15% | [TBD] | [TBD] |
| hyperloglog | CaseB | -5.15% | [TBD] | [TBD] |
| chao_weighted | CaseA | +6.14% | [TBD] | [TBD] |
| chao_weighted | CaseB | -6.00% | [TBD] | [TBD] |

---

## 3. Partial finding (3/8 회수 기반)

### 3.1 sparse_rp 의 비대칭 sensitivity

본 partial 결과의 가장 두드러진 발견은 sparse random projection 의 mode 별 비대칭 sensitivity 다. CaseA (단독 대체) 에서 multi-join re-stratification 이 carry-over 대비 3.55 퍼센트포인트 큰 개선을 보이며 (carry-over +4.52% → re-strat +0.97%), 이는 stratification 학습이 단독 estimator 의 정확도를 직접 결정짓는 mode 에서 두 테이블 vector 결합 학습이 본질적 정보 추가 효과를 발휘함을 시사한다.

반면 CaseB (증강) 에서는 carry-over 와 re-strat 가 거의 동등하다 (-6.58% vs -6.84%, 0.26%p 차이). 이는 CaseB 가 Bernoulli random sampling estimator 와 stratified estimator 의 산술 평균 ensemble 이므로, stratification 자체의 marginal 효과가 ensemble 평균 안에서 희석되기 때문으로 해석된다.

### 3.2 hilbert_real 의 method-robust 가능성

hilbert_real CaseA 는 carry-over 와 re-strat 가 거의 동등 (+1.78% vs +2.10%, 0.32%p) 이며, 본 partial 결과 만으로는 hilbert curve 기반의 space-filling locality 가 multi-join 결합 학습과 무관한 stratification 효과를 발휘함을 시사할 가능성이 있다. hilbert_real CaseB 회수 후 (14:52 KST 예상) 패턴 confirm 필요.

### 3.3 부록 F (km granularity sensitivity) 의 패턴 일치

본 partial finding 은 5/13 부록 F 의 cluster granularity sensitivity 분석 결과와 일관된 패턴을 보인다. 부록 F 에서 sparse_rp 만 K-sensitive (U-shape, K=20 sweet spot 결정적) 였고 hilbert_real / hyperloglog / chao_weighted 3 anchor 는 K-robust 였다. 본 multi-join re-stratification 결과에서도 sparse_rp 가 stratification 학습 방식 변화 (carry-over vs 864d concat re-strat) 에 가장 sensitive 하며 다른 method 는 robust 한 일치 패턴이다.

즉 sparse_rp 는 stratification 의 quality 자체에 sensitive 한 method 이며 (K 변화 + multi-join re-strat 모두 큰 영향), hilbert / hyperloglog / chao 는 stratification quality 와 무관하게 robust 한 method 다. 이는 paradigm 분류 (P4 차원 축소 vs P2 공간 분할 vs P9 정보 이론 vs P3 스트리밍) 와 약하게 correlate 하며, paradigm 정확한 분류보다 **stratification quality 의존도** 라는 새로운 axis 가 method 분류에 더 본질적일 가능성을 시사한다.

---

## 4. 강재현 14:27 카톡 cheap 근사 방향 (partial 결과 기반)

강재현은 14:27 카톡에서 "multi-reclustering 이 더 좋다면 기존 table 별 clustering 의 저비용 multi-reclustering 근사 방법" 의 가능성을 제시하였다. 본 partial 결과 (sparse_rp CaseA 큰 개선 + 다른 method 거의 동등) 는 다음 cheap 근사 전략을 시사한다.

### 4.1 Method-specific selective application

본 연구의 anchor method 가 모두 multi-join re-stratification 효과를 보이지 않는다면, "**sensitivity 큰 method 에만 expensive treatment, robust method 는 cheap carry-over**" 전략이 합리적이다. 즉 sparse_rp 같은 stratification-sensitive method 에는 multi-join 시점에 864d concat KM20 학습을 적용하고, hilbert_real / hyperloglog / chao_weighted 같은 robust method 는 single-table KM20 carry-over 그대로 두는 hybrid framework.

이 전략은 km granularity sensitivity 의 부록 F 발견과 동일한 narrative arc 를 형성한다 — "sensitivity 큰 method 에는 정밀 처리, robust method 에는 단순 처리" 가 본 연구의 일관된 design principle.

### 4.2 4 가지 cheap 근사 후보 (회수 후 시나리오 A 시 적용)

회수 결과 시나리오 A (multi-join re-strat 우위) 시 적용 가능한 cheap 근사 후보:

1. **Centroid tuple 방식** — single-table KM20 학습 그대로 + multi-join 시점에 (s_A, s_B) tuple 을 새 stratum 으로 (K^2 = 400 잠재 strata, sparse 유지). 학습 비용 추가 0.

2. **Hash-based bucketing** — 두 측 stratum_id 의 hash 를 새 stratum 으로. 학습 비용 0, K_eff 는 hash space.

3. **PCA preprocessing 후 low-dim 학습** — 864d → 32d 또는 64d PCA 축소 후 KM20. 비용 = PCA + 저차원 KM20, 864d 직접 KM20 대비 cheap.

4. **Iterative refinement** — single-table KM20 centroid 를 init 으로 multi-join 후 KM20 1-2 iteration 만 update. 비용 = full KM20 의 일부.

본 partial 결과 (sparse_rp 만 큰 차이) 에 따르면 (1) Centroid tuple 방식이 가장 simple + 학습 비용 0 이며, sparse_rp 같은 stratification-sensitive method 에 적용 시 multi-join re-strat 의 효과를 cheap 하게 근사할 가능성이 가장 높은 후보다.

---

## 5. 회수 후 finalize plan (5/13 16:16 KST 이후)

### 5.1 8/8 완성 후 검증 항목

1. hilbert_real CaseB / hyperloglog CaseA + CaseB / chao_weighted CaseA + CaseB 추가 회수 후 partial finding (sparse_rp 우위 + 다른 method 동등) 패턴 confirm
2. CaseB ensemble 모두 거의 동등 가설 검증 — 4 method × CaseB 모두 carry-over 와 re-strat 차이 ±1%p 이내?
3. CaseA 단독 대체 비대칭 — sparse_rp 큰 개선이 다른 method 에서도 발견되는가?
4. method-specific selective application 전략의 적용 범위 결정

### 5.2 부록 G + v5 prompt 정정 6 finalize

- 박광현 slide_draft 부록 G — G.3 표 [TBD] 데이터 채움 + G.4 narrative arc 시나리오 (A/B/C) 중 회수 결과 일치 시나리오 선택 + G.5 confirm 요청 항목 finalize
- v5 prompt 정정 6 — multi-join re-stratification slide 의 데이터 + caption + speaker note finalize

### 5.3 PDF 재생성 + 박광현 미팅 자료 준비

- 박광현 slide_draft.pdf 재생성 (부록 G finalize 후)
- 5/15 14:00 박광현 교수님 미팅 D-2 자료 ready

---

작성 (partial): 2026-05-13 14:35 KST · 3/8 회수 시점 · finalize 예정 5/13 16:16 KST 후
실측 source: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_mj_restrat/` (3 file, 회수 진행 중)
carry-over baseline: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/` (108 file, A2-Fig9 전체)
B1 baseline: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/A2-Fig9_B1.json` qe_trim=1.5407
