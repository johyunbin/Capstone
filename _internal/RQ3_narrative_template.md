# RQ3 Narrative Template — 7-way Distribution-Agnostic 결과 정리

> 본 파일은 7개 method 의 §3.2 4단계 narrative 를 한 곳에 모아둔 채움 폼입니다.
> 측정이 끝나면 `rq3_combine.py` 로 생성된 `rq3_summary.csv` 의 수치를 placeholder 에 삽입.

---

## 사용법

1. **측정 완료 후** `python3 experiments/code/local_analysis/rq3_combine.py` 실행
   → `experiments/results/rq3_agnostic/<YYYY_MM_DD>/rq3_summary.csv` 생성
2. CSV 의 `method × dataset × selectivity` 행에서 다음 컬럼 추출
   - `method_q` (mean q_error)
   - `recovery` (Recovery Rate, metric=='recovery' 인 셀만)
   - `metric` ('recovery' / 'fallback_abs_pct' / 'missing')
3. 같은 method 의 `rq3_pairwise.csv` 행에서 `p_BH` 추출
4. 아래 7개 템플릿의 `{placeholder}` 부분을 채움
5. 본 파일을 그대로 `experiments/results/RQ3 실험 결과 정리.md` 에 복사 → 한 단락씩 편집
6. 채운 narrative 는 `_internal/RQ3_카톡템플릿.md` 의 §3.2 부분에도 동일 텍스트 들어감

## Placeholder 약속

| placeholder | 의미 | 예시 |
|---|---|---|
| `{method_q_DEEP}` | DEEP 평균 q_error (5 sel 평균) | `1.42` |
| `{method_q_SIFT}` | SIFT 평균 q_error | `1.78` |
| `{recovery_DEEP}` | DEEP 평균 Recovery Rate | `0.62` |
| `{recovery_SIFT}` | SIFT 평균 Recovery Rate | `0.51` |
| `{p_BH_DEEP}` | DEEP paired Wilcoxon BH-FDR p-value | `1.2e-08` |
| `{p_BH_SIFT}` | SIFT BH-FDR p-value | `3.4e-05` |
| `{verdict}` | "가설 입증 ✅" / "가설 반증 ❌" / "부분 입증 ⚠️" | — |
| `{expected_band}` | 사전 등록 기대 범위 안/밖 한 줄 판단 | "기대 0.75~0.95 안 (0.85)" |
| `{narrative_extra}` | 1-2 줄의 추가 발견·설명 (분포 차이, fall-back 발생 등) | — |

> **가설 입증 기준** — recovery 평균이 사전 등록 band 안 + p_BH ≤ 0.05 (vs RANDOM20).
> **부분 입증** — DEEP/SIFT 중 하나만 입증, 또는 평균은 band 안인데 일부 sel 만 유의.
> **반증** — recovery 평균이 band 밖 (특히 RANDOM20 보다 못함, recovery < 0).

---

## #8 — F. MiniBatch K-means (P2, paradigm: Offline, 1순위)

[기대: 0.75~0.95 | 측정 ~1h | 패러다임: Offline 사전 분할]

**(a) 동기**
- KM20 oracle 의 학습 비용 (~30~60s 1회) 을 ~5초로 단축하는 production-realistic alternative.
- 1% sample 만으로 K=20 cluster 근사 → cluster 구조 거의 보존 예상.
- 가장 강력한 후보 — recovery 0.9+ 면 KM20 oracle 대용으로 정의 가능.

**(b) 가설**
- H3-F: recovery_rate 0.75~0.95. 사전 학습 비용 5초로 KM20 (60s) 의 80%+ 회수.

**(c) 예상 결과**
- DEEP/SIFT 모두 recovery 0.85 근처 평균. p_BH ≪ 0.05.
- cluster 균질성 (max/min ratio) ~3 이내, KM20 oracle 의 ~2 와 근접.

**(d) 실제 결과**
- DEEP recovery `{recovery_DEEP}` (mean q_error `{method_q_DEEP}`, p_BH `{p_BH_DEEP}`)
- SIFT recovery `{recovery_SIFT}` (mean q_error `{method_q_SIFT}`, p_BH `{p_BH_SIFT}`)
- `{verdict}` — `{expected_band}`. `{narrative_extra}`

---

## #5 — C. Random Projection (P2, paradigm: Offline, 2순위)

[기대: 0.10~0.40 | 측정 ~2h | 패러다임: Offline 사전 분할 (학습 X)]

**(a) 동기**
- 학습 X 의 단순 하한 baseline (Johnson-Lindenstrauss random matrix → argmax bucket).
- recovery 의 하한 후보로서 다른 method 의 reference 역할.
- argmax 방식 채택 — sign-based (4-bit binary, 16 bucket) 는 K=20 과 안 맞음, 1-d projection 은 정보 손실 큼.

**(b) 가설**
- H3-C: recovery_rate 0.10~0.40. RANDOM20 보다 약간 우수, KM20 절반 이하.

**(c) 예상 결과**
- DEEP/SIFT 모두 평균 recovery 0.20~0.30. p_BH ≤ 0.05 (RANDOM20 대비 미미하지만 유의).
- argmax bucket 균질성 unbalanced (max/min ratio 5+), 가장 큰 dimension 으로 쏠림.

**(d) 실제 결과**
- DEEP recovery `{recovery_DEEP}` (mean q_error `{method_q_DEEP}`, p_BH `{p_BH_DEEP}`)
- SIFT recovery `{recovery_SIFT}` (mean q_error `{method_q_SIFT}`, p_BH `{p_BH_SIFT}`)
- `{verdict}` — `{expected_band}`. `{narrative_extra}`

---

## #7 — E. Hilbert Curve (P3, paradigm: Offline, 3순위, contribution 후보)

[기대: 0.20~0.60 | 측정 ~4h | 패러다임: Offline 결정론적]

**(a) 동기**
- PCA 2D + space-filling curve + quantile 분할 = "결정론적 + 균질 cluster + 일부 cluster 구조 반영" 3박자.
- 학습 X (한 번의 SVD eigendecomposition), 같은 입력+seed → 항상 동일 stratum_id (reproducibility).
- 본 연구의 contribution 후보 — Hilbert > MiniBatch 면 학습 비용 0 으로 oracle 근접 달성.

**(b) 가설**
- H3-E: recovery_rate 0.20~0.60. SIFT (skew) 에서 DEEP (normal) 보다 우위 가능 (PCA 가 skew 방향 잡음).

**(c) 예상 결과**
- DEEP recovery 0.30~0.50, SIFT recovery 0.40~0.60 (skew 우위 가설).
- quantile 분할로 cluster 균질성 ratio < 3, p_BH ≪ 0.05.

**(d) 실제 결과**
- DEEP recovery `{recovery_DEEP}` (mean q_error `{method_q_DEEP}`, p_BH `{p_BH_DEEP}`)
- SIFT recovery `{recovery_SIFT}` (mean q_error `{method_q_SIFT}`, p_BH `{p_BH_SIFT}`)
- `{verdict}` — `{expected_band}`. `{narrative_extra}`

---

## #6 — A. LSH (P4, paradigm: Offline, 4순위)

[기대: 0.30~0.60 | 측정 ~4h | 패러다임: Offline 확률적 (Random Hyperplane Cosine LSH)]

**(a) 동기**
- 5 hyperplanes → 2^5=32 raw bucket → mod 20 → 20 strata (KM 과 동일 K=20).
- 코사인 유사도 보존 (Charikar 2002), 가까운 vector 가 같은 bucket 들어갈 확률 높음.
- 학습 X (random projection 한 번), 결정론 (HYPERPLANES_SEED=0 고정).

**(b) 가설**
- H3-A: recovery_rate 0.30~0.60. Random Projection 보다 우수 (locality-sensitive 효과).

**(c) 예상 결과**
- DEEP/SIFT 모두 recovery 0.40~0.50 평균. p_BH ≪ 0.05.
- bucket 균질성 unbalanced 가능 (mod 20 으로 일부 bucket 에 쏠림).

**(d) 실제 결과**
- DEEP recovery `{recovery_DEEP}` (mean q_error `{method_q_DEEP}`, p_BH `{p_BH_DEEP}`)
- SIFT recovery `{recovery_SIFT}` (mean q_error `{method_q_SIFT}`, p_BH `{p_BH_SIFT}`)
- `{verdict}` — `{expected_band}`. `{narrative_extra}`

---

## #10 — B. KDE-pilot (P5, paradigm: Online, 5순위) [측정 완료 시 채움]

[기대: 0.50~0.80 | 측정 ~6h | 패러다임: Online query-adaptive (Silverman+KDE+Neyman)]

**(a) 동기**
- KM20 strata 위에 query 마다 pilot 5개로 σ_i online 추정 → Silverman bandwidth + Gaussian KDE 로 hit probability 평활화 → Neyman main allocation.
- RQ2 의 정적 σ_i (sel=0.1 기준) 보다 query-adaptive 가 어느 정도 이득인지 정량.
- 이론 상한 (Online 의 best-case) 후보.

**(b) 가설**
- H3-B: recovery_rate 0.50~0.80. RQ2 의 Neyman (정적) 과 비교해 +5~15%p 이득.

**(c) 예상 결과**
- DEEP/SIFT 평균 recovery 0.65 근처. 좁은 sel (s=0.01) 에서 우위 큼 (σ 변동 큼).
- pilot 5×20=100 + main 285 budget split. p_BH ≪ 0.05.

**(d) 실제 결과**
- DEEP recovery `{recovery_DEEP}` (mean q_error `{method_q_DEEP}`, p_BH `{p_BH_DEEP}`)
- SIFT recovery `{recovery_SIFT}` (mean q_error `{method_q_SIFT}`, p_BH `{p_BH_SIFT}`)
- `{verdict}` — `{expected_band}`. `{narrative_extra}`

---

## #9 — G. Distance-Shell (P6, paradigm: Online, 6순위)

[기대: 0.25~0.50 | 측정 ~4h | 패러다임: Online query-adaptive (5-shell Neyman)]

**(a) 동기**
- KM cluster 무관, query 마다 pilot 50개 → distance quantile 5등분 → Neyman main allocation.
- KDE-pilot 보다 단순 (KDE 평활 X, quantile 만), 사전 학습·사전 분할 모두 X.
- "가장 단순한 query-adaptive" — KDE 가 의미있는 이득인지 ablation 역할.

**(b) 가설**
- H3-G: recovery_rate 0.25~0.50. KDE-pilot 보다 작지만 RANDOM20 보다 명확히 우수.

**(c) 예상 결과**
- DEEP/SIFT 평균 recovery 0.30~0.40. KDE-pilot 의 약 2/3 수준.
- 좁은 sel 에서 quantile-equal 가정의 한계 노출 가능.

**(d) 실제 결과**
- DEEP recovery `{recovery_DEEP}` (mean q_error `{method_q_DEEP}`, p_BH `{p_BH_DEEP}`)
- SIFT recovery `{recovery_SIFT}` (mean q_error `{method_q_SIFT}`, p_BH `{p_BH_SIFT}`)
- `{verdict}` — `{expected_band}`. `{narrative_extra}`

---

## #11 — H. Importance Sampling (P7, paradigm: Weight-based, 7순위)

[기대: 0.30~0.70 | 측정 ~6h | 패러다임: 비분할 + 가중치 (2x2 factorial)]

**(a) 동기**
- 분할 X — 모든 row 에 importance weight 만 부여 + uniform sample + IPW HT.
- 2x2 factorial: (가중치 형태: hard/soft) × (대역폭 출처: sample/pilot) — KDE 평활화 + pilot bandwidth 효과 분리.
- "분할의 가치" 가설 검증 — 비분할 method 가 분할 method 보다 못하면 분할의 의의 정량화.

**(b) 가설**
- H3-H: recovery_rate 0.30~0.70. 가장 정교한 (soft + pilot) 조합이 0.6+, 단순 (hard + sample) 은 0.3 근처.

**(c) 예상 결과**
- 4 mode 중 (soft + pilot) 이 KDE-pilot 의 80% 수준. (hard + sample) = bernoulli baseline.
- Factor A (smoothing) 효과 > Factor B (pilot) 효과 예상.

**(d) 실제 결과**
- DEEP recovery `{recovery_DEEP}` (mean q_error `{method_q_DEEP}`, p_BH `{p_BH_DEEP}`)
- SIFT recovery `{recovery_SIFT}` (mean q_error `{method_q_SIFT}`, p_BH `{p_BH_SIFT}`)
- `{verdict}` — `{expected_band}`. `{narrative_extra}`

---

## ⭐ 7-way 종합 narrative (모든 method 채워진 뒤 마지막에 작성)

**(α) Paradigm 별 ranking**
- Offline 4: F. MiniBatch ≈ E. Hilbert > A. LSH > C. Random Projection (예상)
- Online 2: B. KDE-pilot > G. Distance-Shell (예상)
- Weight 1: H. Importance Sampling (KDE-pilot 의 80% 예상)

→ 실제 ranking: `{actual_ranking_string}` (rq3_ranking.csv 의 method 순서)

**(β) Cost-Recovery Pareto frontier**
- 좌상단 (low cost, high recovery): {pareto_frontier_methods}
- production 솔루션 후보: {production_candidate}
- 학습 비용 0 인 online/weight method 가 high recovery 면 가장 매력적.

**(γ) DEEP vs SIFT 차이**
- 모든 method 가 DEEP > SIFT 인지, 일부 method (예: Hilbert PCA) 만 SIFT 우위인지.
- → `{cross_dataset_finding}`

**(δ) RQ1 narrative 강화 여부**
- RQ1 의 H1 (skew dataset 에서 cluster 정보 가치 큼) 이 RQ3 7-way 결과로 강화되는지.
- 모든 method 의 SIFT recovery 가 DEEP 보다 큰 경향이면 H1 강화.
- → `{rq1_reinforcement}`

---

**작성 규칙**
- 한국어 학술 산문, bullet 나열 지양 (단 4단계 (a)~(d) 는 헤딩 유지)
- 영문 method 이름 (MiniBatch K-means, LSH 등) 은 원표기 유지
- 수치는 소수점 둘째 자리, p_BH 는 과학 표기 (1.2e-08)
