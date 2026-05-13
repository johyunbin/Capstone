# 가중치 평균 α sweep 결과 분석 (5/14)

## 0. 작성 status

- **분석 대상**: A2-Fig9 cell × 4 anchor method × CaseB 모드 × 5 α 값 (0.3, 0.4, 0.5, 0.6, 0.7) = 20 datapoint
- **측정 launch**: 5/13 23:55 KST tmux alpha_sweep
- **회수 status**: ★ **16/16 회수 완료 (5/14 00:13 KST DONE flag)**
- **본 문서 status**: ★ **FINAL** — narrative 분기 시나리오 B (단독 대체 narrative + 결합 robustness) 확정

## 1. 측정 framework

### 1.1 motivation

본 연구가 산술 평균 (α=0.5, 가중치 0.5/0.5) 결합 방식으로 92.5% paired 일관 우위를 보고하였으나 단독 best (-10.17% minibatch_partial) 와 비슷한 수준이라 다음 hypothesis 검증 필요:

> "결합 가중치 변화로 산술 평균보다 더 큰 개선 가능한가?"

만약 α=0.3 또는 α=0.7 같은 비대칭 가중치에서 더 큰 개선 발견 시 결합 framework 의 핵심 finding 강화 가능. 비슷한 수준이면 산술 평균이 robust 한 best 결합 방식이라는 결론 확정.

### 1.2 wrapper v4 design

measure_paper_exact.py 의 line 1067 `est_final = (est_b1 + est_method) / 2.0` 를 다음으로 변경:

```python
alpha = float(os.environ.get("ALPHA_SWEEP", "0.5"))
est_final = alpha * est_b1 + (1 - alpha) * est_method
```

ALPHA_SWEEP 환경 변수로 α 값 동적 조정. 5 α 값 측정:
- α=0.3: 우리 method 가중치 0.7 (method 우세)
- α=0.4: 우리 method 가중치 0.6
- **α=0.5: 산술 평균 (기존 측정)**
- α=0.6: Bernoulli 가중치 0.6
- α=0.7: Bernoulli 가중치 0.7 (Bernoulli 우세)

scope: 4 anchor method (sparse_rp, hilbert_real, hyperloglog, chao_weighted) × A2-Fig9 cell × CaseB 모드 × 4 α 값 (0.3, 0.4, 0.6, 0.7) = 16 measurement (α=0.5 기존 측정 재사용).

## 2. 결과 — 16/16 회수

### 2.1 paired Δ% (B1=1.5407 기준)

| Method | α=0.3 | α=0.4 | **α=0.5** | α=0.6 | α=0.7 | CaseA 단독 | **best α** |
|---|---:|---:|---:|---:|---:|---:|---|
| sparse_rp | -2.17% | -5.41% | **-6.58%** | -5.92% | -1.98% | +4.52% | **α=0.5** |
| hilbert_real | -3.91% | -5.57% | **-6.07%** | -5.05% | -2.65% | +1.78% | **α=0.5** |
| hyperloglog | -3.72% | -4.26% | -5.15% | **-5.41%** | -3.36% | +1.15% | α=0.6 |
| chao_weighted | -3.71% | -4.41% | **-6.00%** | -5.16% | -3.31% | +6.14% | **α=0.5** |

### 2.2 통합 패턴

| α 값 | 효과 평균 | 의미 |
|---|---|---|
| α=0.3 (method 가중 0.7) | -2.17% ~ -3.91% | 우리 method 가중치 ↑ — 개선 약함 (단독 비슷한 한계) |
| α=0.4 (균형 약간 method 측) | -4.26% ~ -5.57% | 약간 개선 |
| **α=0.5 (산술 평균)** | **-5.15% ~ -6.58%** | ★ **best (4 method 중 3)** |
| α=0.6 (균형 약간 Bernoulli 측) | -5.05% ~ -5.92% | hyperloglog 만 marginal best |
| α=0.7 (Bernoulli 가중 0.7) | -1.98% ~ -3.36% | Bernoulli 가중치 ↑ — 개선 약함 (Bernoulli 한계로 회귀) |

## 3. 핵심 finding 세 가지

### 3.1 산술 평균 (α=0.5) 이 가장 robust 한 결합 방식

4 method 중 3 method (sparse_rp / hilbert_real / chao_weighted) 가 α=0.5 best. hyperloglog 만 α=0.6 best 이지만 α=0.5 와 차이가 0.26 퍼센트포인트 만으로 marginal 차이.

→ **가중치 균등 결합 (산술 평균) 이 본 연구의 결합 방식 sweet spot**. 가중치 변화로 의미 있는 추가 개선이 어렵다.

### 3.2 α 양쪽 극단에서 효과 감소 (U-shape sensitivity)

α=0.3 (우리 method 가중): -2.17% ~ -3.91%  
α=0.5 (산술 평균): -5.15% ~ -6.58%  
α=0.7 (Bernoulli 가중): -1.98% ~ -3.36%

→ U-shape 의 sweet spot 이 α=0.5 부근. 두 estimator 의 균등 결합이 분명한 최적이다.

해석: 
- α=0.3 (method 가중치 0.7) 은 우리 method 의 학습 variance 가 dominant 되어 효과 약화
- α=0.7 (Bernoulli 가중치 0.7) 은 Bernoulli 의 unstratified variance 가 dominant 되어 효과 약화
- α=0.5 는 두 estimator 의 약점 (method 학습 variance + Bernoulli unstratified variance) 이 서로 cancel 되는 정확한 균형점

### 3.3 결합 best (-6.58%) 가 단독 best (-10.17%) 보다 약함

결합 방식 α sweep 의 best 인 sparse_rp α=0.5 = -6.58%.  
단독 대체 가능 method 의 best 인 minibatch_partial CaseA = -10.17%.

→ **결합의 효과가 단독 best 보다 약함**. 즉 "결합으로 더 큰 개선" 이 본 연구의 결론이 아니라:

- **단독 대체로 의미 있는 개선 가능 (15 method, -5 ~ -12%)**
- **결합은 단독 best 보다 효과 약함**
- **그러나 결합은 method 선택 robustness + cell spread 줄임 의 가치**

## 4. Narrative 분기 결정 — 시나리오 B 확정

본 α sweep 결과는 사용자가 23:38 카톡에서 짚은 narrative 분기 의 시나리오 B (단독 대체 narrative + 결합 robustness 강화) 를 정확히 확정한다.

### 시나리오 B 의 narrative 흐름

```
1. 문제 정의 (paper §V-B Adaptive Sampling 영역)

2. 56 방법 탐색 → 폐기 분류 (자원/구현/정합성 3 범주) → 43 method 패러다임별 소개

3. ★ 단독 대체 가능 method 발견 (15 method, -5 ~ -12%)
   - 각 알고리즘 메커니즘 자세히 소개
   - paper 재현 변동 -4.3% 의 1.2 ~ 3 배 의미 있는 개선

4. 결합 framework 검토
   - 산술 평균 (α=0.5) 결합 → 12 anchor method -9 ~ -10% 안정 + 92.5% paired 일관성
   - ★ 가중치 sweep (α=0.3 ~ 0.7) 결과: 산술 평균이 best, 다른 α 변화로 더 큰 개선 X
   - cheap 근사 후보 (Centroid tuple, Hash bucketing, PCA, Iterative refinement) 결과: Centroid tuple 만 보편 우위, 나머지 method × mode conditional
   - 결합의 가치 = method 선택 robustness, "더 큰 개선" 아님

5. 자원 효율 axis 분석
   - 43 method 의 학습 시간 / 메모리 / 차원 한계
   - Pareto frontier Top 5: sparse_rp / chao_weighted / neuram / pca1d / hilbert
   - 산업 적용 3 영역 추천 (A Best of Both Worlds / B 정확도 우선 / C Resource-First — reservoir O(1) memory)

6. 산업 적용 권장 design
   - 단독 대체 후보 + 자원 효율 가장 좋은 method 추천
   - method-aware 선택적 적용
   - PostgreSQL pgvector / Exqutor 모듈 통합 영역

7. (부록) Method 메커니즘 분석 — paradigm 평균 한계 + anchor method consistency + 3 axis 일치 패턴

8. 향후 연구 — Data-aware ensemble framework 5 방향 + 일반 확장 6 방향
```

### 시나리오 B 의 narrative 강점

1. **정직 disclosure**: "결합으로 단독 대체 능가 X" 라는 본 연구 finding 정직 표기
2. **단독 대체 method 의 가치 명시**: 15 method 의 알고리즘 메커니즘 + 개선폭 + 자원 효율
3. **결합 framework 의 진짜 가치**: "더 큰 개선" 이 아닌 "method 선택 robustness + cell spread 줄임"
4. **자원 효율 axis 추가**: 산업 적용 가능성 + reservoir O(1) memory finding
5. **method-aware 선택적 적용** 의 학술 contribution

## 5. 본 연구 narrative 안의 의미

본 α sweep 분석은 사용자가 22:51 + 22:57 + 23:38 카톡으로 정리한 narrative 흐름이 정량 검증으로 확정되었음을 입증한다. 그리고 사용자가 23:31 카톡에서 짚은 "결합했는데도 10퍼센트 내/외면 의미가 없잖아" 라는 우려가 정확함을 입증한다 — 결합으로 단독 best 능가 X.

본 연구의 진짜 main contribution 은 다음 세 영역으로 정리된다.

### Main contribution 1: 단독 대체 가능 method 의 발견 + 정량 분석

15 method 가 paper 베르누이를 단독 대체할 수 있고 -5 ~ -12% 의미 있는 개선을 보인다. 다만 cell 별 spread 가 커서 산업 적용 안정성 부족.

### Main contribution 2: 결합 framework 의 정확한 위치 입증

산술 평균 (α=0.5) 이 결합 방식 중 best 이며 다른 가중치 변화로 더 큰 개선 어려움. 결합의 가치는 "더 큰 개선" 이 아닌 "method 선택 robustness" 와 "cell spread 줄임".

### Main contribution 3: 자원 효율 axis + 산업 적용 추천

Pareto frontier 분석으로 정확도와 자원 두 axis 위의 최적 method 추출. reservoir 의 O(1) memory + anchor 수준 정확도 finding 이 산업 적용 narrative 의 강력한 evidence.

## 6. 측정 source

- 측정 launch: 5/13 23:55 KST tmux alpha_sweep
- 회수 완료: 5/14 00:13 KST DONE flag
- 출력 dir: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_alpha_sweep/alpha_{0.3, 0.4, 0.6, 0.7}_/`
- wrapper: `/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact_alpha.py` (line 1067 의 est_final 계산을 ALPHA_SWEEP 환경 변수 적용)
- 기존 α=0.5 (산술 평균) 측정: `paper_exact/A2-Fig9_CaseB_{method}.json`
- B1 baseline: `paper_exact/A2-Fig9_B1.json` qe_trim=1.5407

---

작성: 2026-05-14 00:20 KST · 16/16 회수 완료 + finalize · 시나리오 B (단독 대체 narrative + 결합 robustness) 확정
다음: 4 file narrative 분기 결정 반영 4차 정정 + 박세은 + 강재현 paste form (α sweep finding)
