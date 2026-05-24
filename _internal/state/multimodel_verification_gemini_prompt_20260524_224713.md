# Gemini Ultra 적대 검증 prompt — 속도는벡터 storyline v3 문헌·통계 정합성

> 작성: 2026-05-24 22:47 KST · target: Gemini 3.1 Pro / Deep Research
> 검증 결과 critical: 5/27 최종 발표 슬라이드 deck + 채림님(BDAI 연구실) 보고용
> Multi-model verification (Claude·Codex·Gemini) 의 Gemini axis — 문헌·통계 method 정합성에 중점

## 0. 임무

당신은 **문헌·통계·구조적 narrative 정합성을 적대적으로 검증하는 평가자**다. 연세대 캡스톤 팀 "속도는벡터" 의 본 연구 narrative 와 정본 측정 결과의 (a) 문헌 정합성 (b) 통계 method 정확성 (c) 측정 평면 일반화 한계 (d) Multi-model verification (Claude·Codex·당신) 통합 시 발견될 결함·의심을 모두 보고.

## 1. 본 연구 framing

- **연구 정체성**: Exqutor 논문 (arXiv:2512.09695v2) §V-B Adaptive Sampling 의 **표본 선택 단계 한 곳만** 통제 변인 분리 controlled verification experiment (새 알고리즘 X · 벤치마크 검증)
- **개입**: 무작위 베르누이 표본 추출 → 분포 인지 층화 표본 추출 (paper momentum 식 1-6 · 표본 예산 N=385 그대로)
- **결과 narrative**: 결합 (CaseB) 이 89.1% 우위 (1344/1508), 중앙값 Δ% −4.38%. 그러나 89% 우위의 메커니즘은 분포 인지 효과가 아닌 **두 독립 추정량 평균의 분산 감소 효과** (v14·v15·v16 CaseC dual-Bernoulli ensemble 통제 측정으로 입증). engine latency 56 cell 측정에서 추정 정확도 ↑ 가 plan 회복 robustness (B1 7/12 → 결합 148/156 = 94.9%) 으로 이어지나, **latency 자체는 B1·CaseB·oracle 동등 (paired Wilcoxon 7.7% 유의·86.9% small effect, variance condition % SS 0%)**. → **음성·방법론적 결과** (negative + methodological finding).

## 2. 정본 측정 수치 (검증 대상)

[Codex prompt 와 동일한 수치 carry — 본 prompt 의 부담 줄이기 위해 핵심만 발췌]

### v13 (1,508 cell × 3-way matched)
- B1 qe_trim mean 1.4582 / median 1.5616 / std 0.1925
- CaseA qe_trim mean 1.6359 / median 1.5699 / std 2.7976 (extreme outlier max=96.79)
- CaseB qe_trim mean 1.4019 / median 1.4492 / std 0.4666
- paired CaseB_vs_B1: 1344/1508=89.1%, mean Δ% −3.06%, median Δ% −4.38%, 유의 65.3%, δ large 72.1%
- paired CaseA_vs_B1: 531/1508=35.2%, mean Δ% +12.90%, median Δ% +1.09%, 유의 6.8%

### v14 (사전 등록 통제군 CaseC, 9 cell)
- mean qe_trim = 1.3729, range [1.3452, 1.3948]
- 동일 9 cell v13 B1=1.5843, CaseB=1.4734
- CaseC < CaseB 9/9 cell (100%)

### v16 (95 tuple 전수, BLOCKER E fix 후)
- qe_trim_B1 mean 1.4595 / CaseA 1.6351 / CaseB 1.4022 / CaseC_v16 1.3060
- CaseC vs B1 paired: 95/95=100%, mean Δ% −10.05%, median Δ% −11.32%
- CaseC vs CaseB paired: 95/95=100%, mean Δ% −6.08%, median Δ% −5.98%

### Engine latency (3 평면 56 cell)
- phase2 12 cell DEEP sf=10 sel=0.001: baseline 5677.7ms · B1 977.6ms · CaseB 983.5ms · oracle 992.3ms (median)
- 12 cell oracle gain 평균 5.67× (보고서 §5.2 verbatim, trim mean) · range 2.93× ~ 7.40×
- B1 정답 plan 회복 7/12 (58.3%), CaseB 13 method 정답 plan 회복 148/156 (94.9%)
- paired Wilcoxon (anchor=B1, 168비교): 13/168 = 7.7% 유의, 86.9% small effect
- variance decomposition (poc_6_4 legacy, 20 cell, n=4500, R²=0.927): condition % SS 0%, p=0.866
- variance decomposition (poc_6_4_extended, 56 cell, n=2250, R²=0.827): condition % SS 0.000773%, p=0.945
- plan recovery (3 평면 700 paired B1 anchor): 92.7% same plan / 7.3% different
- 4-way 확장 (5/24 04:03, 12 cell × 18 variant): CaseC vs B1 mean Δ% +0.30%, 17 variant 모두 |Δ%| ≤ 1.12%, baseline vs B1 +409.7%

### Adaptive Sampling hyperparam (paper §V-B verbatim, 모든 mode 동일)
- N=385 (식 1: z²·P̂(1-P̂)/e² = 1.96²·0.25/0.05² = 384.16 → 385)
- m=0.9 (momentum coefficient)
- η₀=0.1 (initial learning rate)
- α=50 (target Q-error weight)
- β=1.5 (target Q-error)
- γ=0.99 (learning rate decay)
- update_period=50 (queries)
- trials=10, n_queries=1000 per measurement

## 3. 검증 임무 (Gemini 강점 활용)

### Task A — 문헌 정합성
1. **Exqutor §V-B verbatim** — 식 1-6 momentum 보정의 hyperparam (m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50, N=385) 가 paper 와 정확히 일치하는가? 본 연구의 carry 가 정확한가?
2. **Cochran 1977** "Sampling Techniques" §5.5 Optimum Allocation — 본 연구의 분포 인지 층화 (KMeans cluster·K=20 균등 배분) 의 이론적 근거 정합성. Neyman allocation 의 paradox (분포 균일 시 비례 배분 환원) 와 RQ2 narrative 의 직접 연결 정확?
3. **HNSW (Malkov-Yashunin 2020)** — Exqutor §V-A ECQO 의 HNSW range query 1-2ms — 본 연구 measurement 정합?
4. **Li-Hastie-Church 2006** "Very Sparse Random Projections" — sparse_rp method 의 1/√D 변형 reference 정정 (Achlioptas 2003 → Li 2006) 정합?
5. **TPC-H VAQ + DEEP/SIFT/SimSearchNet++ benchmark** — Exqutor 측정 환경과 본 연구 일치성. ICDE 자산 차용 (slide 2-5) 정합?
6. **ICDE slide 자산** 4종 (RAG analyst 시나리오 · HW spec · TPC-H VAQ plan viz · step-by-step VSS cardinality) carry 정확?

### Task B — 통계 method 정합성
1. **paired Wilcoxon 부호순위 검정** + Holm-Bonferroni 보정 — 168·180 비교에서 정확 적용?
2. **Hedges' g** (n=15 small sample 보정 j=1−3/(4n−9)) — paired 차이 표준화 효과크기 정의 정확?
3. **Cliff's δ** (15회 짝 한쪽 빠른 횟수 차이 비율) — 정의 정확? ±1.0=일관 우열?
4. **cluster paired bootstrap** (B=2,000, cell 단위 resample) — within-cell 상관 보정 정합?
5. **variance decomposition** (OLS Type-III SS 분해, sum-coded contrasts) — % SS Type-I 순차 vs p Type-III partial 혼용 정합?
6. **paired Δ% 정의** (delta = (exp_qe − base_qe)/base_qe × 100, trial 10 paired) — 음수 = exp 우위 정의 정확?

### Task C — 측정 평면 일반화 한계
1. **1,508 cell = 25 cell × 16 method × 3 sel × 3 K 구조화** vs 의도 max 3,600 (42%) — 통계 일반화 정당성?
2. **5 단일 dataset (DEEP·SIFT·SSN·WIKI·YFCC) + 4 multi/concat** — sample size 일반화 한계?
3. **A2-Fig8 4/16 method (희소)·A4-sel 16 measurement** — single-cell finding 인용 X 정당성?
4. **engine 56 cell coverage** (DEEP·SIFT·SSN·YFCC sf=10 only) — sf=1·sf=100·타 엔진 미측정의 일반화 한계?
5. **K=20 중심 portfolio (74.5%)** vs K=10·30 각 12.7% — K scaling 일반화?

### Task D — Adaptive Sampling 메커니즘 narrative
1. 89% 우위 메커니즘 = 분포 인지 X · **앙상블 평균 효과** — v14 dual-Bernoulli CaseC < CaseB 9/9 (100%) 가 충분 증거?
2. v16 95 tuple CaseC < CaseB 95/95 (100%, median Δ% −5.98%) 가 분포 인지의 양의 효과 부재 입증?
3. v16 CaseC vs B1 (−11.32% median) 의 **두 효과 분리** — (a) 두 독립 베르누이 평균의 분산 감소 (b) method (분포 인지) 의 검정 — 합 해석 정합?
4. v16 CaseC K-independent (paper §V-B verbatim all_vecs) vs v13 B1·CaseB K-dependence — paired 비교 fairness 한계 정합?
5. **단독 대체 (CaseA) 가 +12.90% 악화** vs **결합 (CaseB) 가 −4.38% 개선** — 결합 형태의 가치 narrative 정합?

### Task E — Multi-model verification cross-check
1. Claude 자체 분석 결과 (storyline v3 정정 10 항목) 의 정확성?
2. Codex 적대 검증 (병렬 dispatch 중) 와의 일치 예상?
3. 잠재적 결함·환각 — Claude 가 발견 못 한 정합성 위반?
4. 5/27 발표 deck + 채림님 보고용 자료의 **0 환각 0 오차 보장** 위한 추가 검증 권고?

## 4. 응답 형식

```
# 검증 결과 (Gemini axis)

## Summary
- 문헌 정합성 점수 (0-100):
- 통계 method 정확성 점수 (0-100):
- 측정 일반화 정당성 점수 (0-100):
- narrative 일관성 점수 (0-100):
- 종합 신뢰도 (0-100):
- pass / conditional pass / fail:

## Task A 문헌 정합성 발견
1. [발견]
   - Evidence (paper section·식 번호·reference):
   - Affected:
   - 권고:

## Task B 통계 method 발견 (동일 형식)
## Task C 측정 평면 발견 (동일 형식)
## Task D Adaptive Sampling narrative 발견 (동일 형식)
## Task E Multi-model cross-check 발견 (동일 형식)

## 종합 권고
- 0 환각 0 오차 보장 위한 추가 검증 / 추가 측정 / 추가 reference 권고
- 5/27 발표·채림님 보고용 자료에 들어가야 할 검증 결과 핵심
```

언어: 한국어 (수치·문헌·통계 용어는 영문/숫자 그대로).
응답 길이: 자세히 (1500-3500 자), 발견된 모든 의심·결함 명시. 점수는 정합성·정확성·정당성·일관성 4 축 모두 평가.
