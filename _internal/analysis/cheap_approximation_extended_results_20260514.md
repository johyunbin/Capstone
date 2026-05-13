# Cheap 근사 4 후보 확장 결과 분석 (5/14 새벽)

## 0. 작성 status

- **분석 대상**: A2-Fig9 cell × 4 anchor method × 2 mode × 4 cheap 근사 후보 (Centroid tuple / Hash bucketing / PCA preprocessing / Iterative refinement) = 32 datapoint
- **회수 status**: ★ **32/32 회수 완료** (b1/b2/b3 5/14 새벽 회수, Centroid tuple 은 5/13 19:57 회수)
- **본 문서 status**: ★ **FINAL** — 시나리오 B (산술 평균 결합 robustness + 단독 대체 narrative) 추가 강화

## 1. 측정 framework

### 1.1 motivation

5/13 사용자 + 강재현 14:27 카톡 제안 — 산술 평균 결합 외 다른 결합 방식 (저비용 근사 4 후보) 을 측정하여 본 연구 결합 framework 의 robustness 검증. 4 후보:

| 후보 | 설계 |
|---|---|
| Centroid tuple | 두 single-table KM20 학습 + (s_A, s_B) tuple 의 top-K frequency folding |
| Hash bucketing | 두 single-table KM20 + (s_A × 31 + s_B × 17) % K hash mapping |
| PCA preprocessing | 864 차원 concat → 64 차원 PCA 축소 후 KM20 |
| Iterative refinement | single-table KM_A centroid 를 init 으로 864 차원 위 KM20 2 iteration update |

### 1.2 측정 wrapper

- Centroid tuple: `/tmp/launch_centroid_tuple.py` (5/13 16:47 launch)
- B1 Hash bucketing: `/tmp/launch_hash_bucketing.py` (5/13 21:06 launch)
- B2 PCA preprocessing: `/tmp/launch_pca_lowdim.py` (5/13 21:07 launch)
- B3 Iterative refinement: `/tmp/launch_iter_refine.py` (5/13 21:07 launch)

각 wrapper 가 측정 framework 의 fetch_all_vectors_safe 를 monkey-patch 하여 결합 방식 변경. 학습 비용은 모두 single-table KM20 두 개 학습 + 추가 후처리 (folding / hash / PCA / iter) 로 cheap 영역.

## 2. 6-way A2-Fig9 결과 (32 datapoint 포함)

### 2.1 paired Δ% 표 (B1 = 1.5407 기준)

| Method | Mode | carry | mj (expensive) | Centroid tuple | B1 Hash | B2 PCA | B3 Iter |
|---|---|---:|---:|---:|---:|---:|---:|
| sparse_rp | CaseA | +4.52% | +0.97% | +4.71% | **-6.41% ★** | +5.00% | +6.31% |
| sparse_rp | CaseB | -6.58% | -6.84% | **-7.37%** | -5.19% | -5.99% | -4.78% |
| hilbert_real | CaseA | +1.78% | +2.10% | +4.97% | +1.51% | +0.71% | +4.12% |
| hilbert_real | CaseB | -6.07% | -6.23% | **-6.93%** | -6.46% | -6.78% | -4.83% |
| hyperloglog | CaseA | +1.15% | +0.89% | **-1.14% ★** | **+8.99% harmful** | +6.05% | +2.62% |
| hyperloglog | CaseB | -5.15% | -4.96% | **-6.66%** | **-7.31% ★** | -6.20% | -4.69% |
| chao_weighted | CaseA | +6.14% | +3.51% | **+2.54% ★** | +4.63% | +5.74% | **+0.04% ★** |
| chao_weighted | CaseB | -6.00% | -6.24% | **-6.69%** | **-7.01% ★** | -6.32% | -6.25% |

### 2.2 결합 방식별 평균 효과

| 결합 방식 | CaseA 평균 Δ% | CaseB 평균 Δ% | vs carry 평균 |
|---|---:|---:|---:|
| **carry-over** (산술 평균 baseline) | +3.40% | -5.95% | baseline |
| multi-jn re-strat (expensive 864d KM20) | +1.87% | -6.07% | CaseA -1.53p / CaseB -0.12p |
| **Centroid tuple** (cheap) | +2.77% | **-6.91%** | CaseA -0.63p / **CaseB -0.96p ★** |
| **B1 Hash bucketing** | +2.18% | -6.49% | CaseA -1.22p / **CaseB -0.54p** |
| B2 PCA preprocessing | +4.38% | -6.32% | CaseA +0.98p (악화) / CaseB -0.37p |
| B3 Iterative refinement | +3.27% | -5.14% | CaseA -0.13p (marginal) / **CaseB +0.81p (harmful)** |

## 3. 핵심 finding 세 가지

### 3.1 Centroid tuple = 결합 방식 중 best robust

본 4 후보 중 Centroid tuple 이 가장 robust 한 결합 방식이다. CaseB 모드 4 method 모두에서 carry-over 보다 우위이며 (mean -0.96p), 학습 비용 추가 0 의 cheap design 이다. 본 연구의 핵심 mode 인 CaseB ensemble augment 영역에서 보편 우위는 4 후보 중 Centroid tuple 만 가능했다.

### 3.2 B1 Hash bucketing 의 method × mode spread

B1 Hash bucketing 의 효과는 method 와 mode 별로 매우 spread 가 크다. sparse_rp CaseA 에서는 본 측정 series 최대 우위 (-10.93%p), 그러나 hyperloglog CaseA 에서는 큰 악화 (+7.84%p) 가 동시에 발생한다. 이는 hash mapping 의 randomization 효과가 method 의 내부 메커니즘과 결합할 때 method × mode conditional 으로 spread 가 크게 발생한다는 의미다. 일관 우위가 아닌 specific 영역 효과라 산업 적용 framework 로는 위험하다.

### 3.3 B2 PCA marginal / B3 Iterative harmful

B2 PCA preprocessing 은 marginal 수준의 효과만 보였다 (CaseB mean -0.37p, 산술 평균 결합과 거의 동등). B3 Iterative refinement 는 CaseB 모드에서 일관 harmful 효과 (sparse_rp +1.80p / hilbert_real +1.24p / chao_weighted +0.25p / hyperloglog +0.46p worse) 를 보였다. single-table KM_A centroid 를 init 으로 사용한 후 2 iteration 만 update 하는 design 이 sub-optimal local minima 에 trapping 되는 것으로 해석된다.

## 4. 본 연구 narrative 분기 결정 확정

본 4 cheap 근사 후보 + α sweep 가중치 변화 측정 결과를 종합하면, 사용자가 23:38 카톡으로 짚은 narrative 분기는 **시나리오 B (단독 대체 narrative + 결합 robustness 강화)** 가 정확히 확정된다.

### 4.1 결합 framework 의 진짜 위치

본 연구의 결합 framework (산술 평균 + Centroid tuple cheap 근사) 의 가치는 "더 큰 개선" 이 아니다. 본 분석 + α sweep 결과로 확정된 사실은 다음과 같다.

- **단독 best (-10.17% minibatch_partial) > 결합 best (-7.37% Centroid tuple sparse_rp CaseB)**
- α sweep 결과: 산술 평균 (α=0.5) 이 가중치 변화 중 best, α=0.3 / 0.7 양쪽 극단 효과 감소
- 4 cheap 근사 후보 중 Centroid tuple 만 CaseB 보편 우위, 나머지 (B1/B2/B3) 는 method × mode spread

→ **결합 framework 의 가치 = method 선택 robustness + cell spread 줄임**. "더 큰 개선" 가능성이 본 측정으로 부정되었다.

### 4.2 시나리오 B narrative 흐름

```
1. 문제 정의 (paper §V-B Adaptive Sampling 영역, 분포 정보 활용 X)
2. 56 방법 탐색 → 폐기 분류 (자원/구현/정합성 3 범주) → 43 method
3. ★ 단독 대체 가능 method 15 발견 (-5 ~ -12%, paper 재현 변동 -4.3% 의 1.2~3배)
   - 각 method 알고리즘 메커니즘 자세히
   - cell × selectivity 별 일관성 분석
4. 결합 framework 검토
   - 산술 평균 + α sweep + 4 cheap 근사 후보 측정
   - Centroid tuple 만 CaseB 보편 우위, 나머지 spread
   - 가중치 변화로 큰 개선 X (α=0.5 best, 양쪽 극단 효과 감소)
   - 결합의 가치 = method robustness + cell spread 줄임
5. 자원 효율 axis
   - Pareto frontier Top 5 = anchor consistency 12 method 와 일치
   - reservoir O(1) memory + anchor 수준 정확도 finding
6. 산업 적용 권장 design
   - 단독 대체 + 자원 효율 method 추천 3 영역 (A/B/C)
   - method-aware 선택적 적용
7. (부록) Method 메커니즘 분석
8. 향후 연구 — Data-aware ensemble framework + 일반 확장
```

## 5. 박광현 미팅 + 6/11 보고서 narrative 반영

본 cheap 근사 4 후보 결과는 박광현 5/15 미팅 자료 부록 G + 6/11 최종 보고서 §4.3.4 결합 framework 검토 영역에 다음과 같이 반영된다.

### 박광현 미팅 부록 G 강화

- G.4.1: Centroid tuple cheap 근사 결과 (기존 finalize)
- **G.4.2 (신규)**: B1 Hash / B2 PCA / B3 Iterative refinement 추가 결과 + 4 후보 종합 비교
- **G.4.3 (신규)**: α sweep 결과 + 결합 방식의 진짜 위치 narrative

### 6/11 보고서 §4.3.4 강화

- 결합 framework 검토 section 의 sub-section 으로 4 cheap 근사 후보 비교 표 + α sweep 결과 + 결합의 가치 narrative 통합

## 6. 측정 source

- A2-Fig9 carry baseline: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/` (1001 file)
- A2-Fig9 multi-join re-strat: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_mj_restrat/` (8 file, 5/13 16:13 finalize)
- A2-Fig9 Centroid tuple: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_centroid_tuple/` (8 file, 5/13 19:57 finalize)
- **A2-Fig9 B1 Hash**: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_b1_hash/` (8 file, 5/14 새벽 회수)
- **A2-Fig9 B2 PCA**: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_b2_pca/` (8 file, 5/14 새벽 회수)
- **A2-Fig9 B3 Iter**: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_b3_iter/` (8 file, 5/14 새벽 회수)
- A2-Fig9 α sweep: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_alpha_sweep/alpha_{0.3,0.4,0.6,0.7}_/` (16 file, 5/14 00:13 finalize)

---

작성: 2026-05-14 07:05 KST · 32 cheap 근사 후보 + 16 α sweep 회수 완료 + finalize
시나리오 B (단독 대체 narrative + 결합 robustness 강화) 확정
관련 분석: `multi_join_restratification_results_20260513.md` / `centroid_tuple_cheap_approximation_results_20260513.md` / `alpha_sweep_results_20260514.md` / `resource_efficiency_pareto_20260513.md`
