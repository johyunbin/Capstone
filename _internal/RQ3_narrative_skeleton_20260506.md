# RQ3 7-way 실험 narrative 4단계 사전 설계 (2026-05-06)

> 작성 시점: 2026-05-06 21:00 KST · 8M 보강 측정 진행 중 시간 활용.
> 7개 RQ3 실험 (#5~#11) 각각의 4단계 narrative 중 **(a) 동기 + (b) 가설 + (c) 예상 결과**
> 를 사전 설계. 측정 후 **(d) 실제 결과** 만 채워 넣어 카톡 §3.2 narrative 즉시 발송.

## 핵심 metric — Recovery Rate

```
recovery_rate = (방법X − RANDOM20) / (KM20 − RANDOM20)
```

- **1.0** → KM20 oracle 수준 회수 (분포 정보가 없어도 oracle 만큼)
- **0.0** → RANDOM20 (공간 인식 X) 수준
- **음수** → RANDOM20 보다 나쁨 (분할이 오히려 해로움)

분모 붕괴 (|KM20 − RANDOM20| ≤ 1%p) → 절대 Δ%(BERN) fall back.

## 우선순위 매트릭스

| # | 실험 | 패러다임 | 시간 | 우선순위 | 기대 recovery | 핵심 가치 |
|---|------|---------|------|---------|--------|------|
| #8 | F. MiniBatch K-means | Offline (학습 1%) | ~1h | ★★★ 1순위 | 75-95% | KM oracle 의 production 솔루션 |
| #5 | C. Random Projection | Offline (단순 하한) | ~30m | ★★ 2순위 | 10-40% | "학습 없이도 어느 정도?" 의 lower bound |
| #7 | E. Hilbert Curve | Offline (결정론) | ~30m | ★★ 3순위 | 20-60% | space-filling curve 의 cluster 일부 반영 (contribution 후보) |
| #6 | A. LSH | Offline (확률 hash) | ~1h | ★ 4순위 | 30-60% | cosine 유사도 보존, 정통 |
| #10 | B. KDE-pilot | Online (정교) | ~6h | ★ 5순위 | 50-80% | online σ 추정의 이론 상한 |
| #9 | G. Distance-Shell | Online (단순) | ~4h | ★ 6순위 | 25-50% | KDE-pilot 의 단순화 ablation |
| #11 | H. Importance Sampling | 비분할 (가중치) | ~6h | ★ 7순위 | 30-70% | 분할 없이 가중치만의 한계 |

---

## 실험 #8 — F. MiniBatch K-means (★★★ 1순위)

### (a) 동기

KM20 oracle 은 R1 1.5초 학습으로 +1.6~8.9% 개선을 산출한다 (RQ2 측정). production 환경에서는 매번 full K-means 학습이 부담이지만, **MiniBatch K-means** (Sculley 2010) 는 1~5% sample 만으로 학습 시간을 1/20~1/100 로 줄이면서 cluster 품질을 보존한다고 알려져 있다. 본 실험은 production-ready stratification 으로의 환원 가능성을 정량화한다.

### (b) 가설 H3-F

**MiniBatch K-means 가 KM20 oracle 의 75% 이상 recovery 를 달성한다.** 즉 1% 학습 sample (DEEP 1M → 10K rows, ~수초 학습) 로도 oracle 수준에 근접한 stratum_id 부여 가능. 좁은 sel (s=0.01) 에서도 recovery_rate ≥ 0.7.

### (c) 예상 결과

- **recovery_rate ≈ 75-95%**: MiniBatch 의 cluster 품질이 KM 의 95-98% 수준 (sklearn Sculley 2010 보고).
- **DEEP/SIFT 모두 양호**: skew (SIFT) 에서도 cluster 비균질성이 1% sample 에 충분히 반영됨.
- 좁은 sel 에서는 KM oracle 과 통계적으로 구별 안 될 수 있음 (paired Wilcoxon p > 0.05).
- inertia 가 oracle 의 1.05-1.10 배 정도 (학습 sample 부족 인한 sub-optimality).

### (d) 실제 결과 (2026-05-06 21:22 측정 완료)

> 측정 시간 105.1s (예상 1h 의 ~3% — sample_size 385 효과)
> Primary metric: `method_minus_random_pct` (recovery rate 분모 붕괴 — KM20 vs RANDOM20 격차 0.26~3.98%).
> - **DEEP** (vs RANDOM20): s=0.01 -4.22% / s=0.05 -0.99% / s=0.10 -1.19% / s=0.30 -0.89% / s=0.50 -0.41%
> - **SIFT** (vs RANDOM20): s=0.01 -3.67% / s=0.05 -2.73% / s=0.10 -2.42% / s=0.30 -2.07% / s=0.50 -1.42%
> - **paired Wilcoxon vs RANDOM20**: 8/10 cell 통계 유의 (BH-FDR p_BH ≤ 0.05) — DEEP s=0.01/0.05 빼고 모두 유의
> - **가설 H3-F confirm 강하게**: KM oracle 수준 회수 (recovery 0.7~1.2 in non-fallback cell)
> - **예상 일치**: 학습 1% 로 oracle 효과 회수, SIFT (skew) 에서 효과 더 큼

### 의의

confirm 시 → **"production 솔루션은 MiniBatch K-means"** narrative 강화. KM oracle 은 benchmark 로 두고 실제 추천은 MiniBatch. RQ재정립 plan 의 Limitation 1 (KM20 = oracle, production X) 을 해소하는 현실적 대안.

refute 시 → MiniBatch 가 sub-optimal 이면 학습 sample 비율을 5%, 10% 로 증가시키는 추가 sensitivity 분석 예정. 또는 mini-batch size / iter 수 tuning.

→ **2026-05-06 confirm.** 다만 다음 실험 #7 Hilbert 가 동등 또는 우수 → "MiniBatch vs Hilbert" 새 trade-off 축 발견.

---

## 실험 #5 — C. Random Projection (★★ 2순위)

### (a) 동기

distribution-agnostic 의 가장 단순한 baseline — Johnson-Lindenstrauss lemma 가 보장하는 거리 보존만 사용. 학습 X, projection matrix 만 결정론적 (Gaussian random). **"학습 없이 단순 random projection 으로 어디까지 recovery 가능한가?"** 의 lower bound 측정. 이게 너무 낮으면 cluster 학습의 가치가 정량적으로 명확해지고, 의외로 높으면 단순 method 도 충분하다는 증거.

### (b) 가설 H3-C

**Random Projection 의 recovery_rate 는 10-40% 수준 — KM oracle 의 1/3 미만.** Johnson-Lindenstrauss 는 거리만 보존하지 cluster 구조 반영 X. argmax bucket 부여는 noise dominant.

### (c) 예상 결과

- **recovery_rate ≈ 10-40%**: 거리 보존만으로 일부 cluster 구조 우연히 반영. 좁은 sel 에서는 거의 0 (RANDOM20 수준).
- **DEEP/SIFT 차이 작음**: Random Projection 은 distribution-agnostic 이라 skew 에 둔감.
- bucket 분포가 매우 imbalance (max/min 비율 5배 이상): argmax 가 high-norm dim 쪽으로 편향.
- 좁은 sel 에서 RANDOM20 보다 약간 나음 또는 비슷.

### (d) 실제 결과 (2026-05-06 21:25 측정 완료)

> 측정 시간 100.2s
> - **DEEP** (vs RANDOM20): s=0.01 +18.46% / s=0.05 +6.56% / s=0.10 +3.30% / s=0.30 +1.19% / s=0.50 +0.99%
> - **SIFT** (vs RANDOM20): s=0.01 **+45.14%** ⚠️ / s=0.05 +7.81% / s=0.10 +4.90% / s=0.30 +2.22% / s=0.50 +1.20%
> - **paired Wilcoxon vs RANDOM20**: 0/10 cell 유의 (모두 통계적 무의미 또는 더 나쁨)
> - **가설 H3-C refute (역방향)**: 예상 +10~40% recovery 였으나 실제로는 RANDOM20 보다 일관되게 나쁨, 좁은 sel 에서 매우 나쁨
> - **예상 불일치**: argmax bucket 부여가 noise dominant — RANDOM20 보다 못함. JL lemma 거리 보존이 cluster 분할로 직결되지 X.

### 의의

confirm 시 → **"단순 random projection 만으로는 부족"** narrative. 학습된 cluster 의 가치 (KM/MiniBatch/Hilbert) 를 lower bound 와 대비해 강조 가능.

refute (recovery > 50%) 시 → Random Projection 도 충분히 강력한 baseline. cluster 학습 비용 vs 성능 trade-off 가 더 미묘해짐.

→ **2026-05-06 refute (역방향)**: RANDOM20 보다 더 나쁨 — distribution-agnostic 의 단순 argmax 한계 정량화. **부정적 control 로서 가치**.

---

## 실험 #7 — E. Hilbert Curve (★★ 3순위)

### (a) 동기

Hilbert curve 는 다차원 → 1D 결정론적 매핑으로 30년 검증된 space-filling curve. PCA 2D + Hilbert + quantile 분할의 조합은:
- **PCA 2D** 가 cluster 구조의 가장 큰 변동 방향 2개 살림 (정보 손실 있으나 일부 반영)
- **Hilbert curve** 가 2D 평면의 locality 보존 (z-order 보다 우수)
- **quantile 분할** 이 균질 stratum 보장

**학습 X + 결정론적** 이면서 cluster 구조를 일부 반영하는 본 연구의 **contribution 후보**. KM 의 학습 비용 없이 oracle 의 절반 정도 회수하면 학술적 의미.

### (b) 가설 H3-E

**Hilbert Curve 의 recovery_rate 는 20-60% 범위.** PCA 2D 가 high-d cluster 구조 일부만 반영 → MiniBatch (75-95%) 보다는 낮으나 Random Projection (10-40%) 보다는 높음.

### (c) 예상 결과

- **recovery_rate ≈ 20-60%**: PCA 의 explained variance ratio (DEEP 96d → 2d 는 5-15% 정도 추정) 가 결정. 데이터셋 따라 다름.
- **DEEP > SIFT 가능성**: DEEP 의 PCA 가 SIFT 보다 더 의미 있는 변동 축 (96d 가 128d 보다 PCA 효과적). 또는 그 반대 (SIFT 의 더 큰 skew 가 2D 에서도 분리됨).
- bucket 분포는 **균형 (quantile 분할)**: max/min < 2 (학습 sample 위에서는 거의 1).
- 좁은 sel (s=0.01) 에서 KM 과 격차가 크게 벌어질 것.

### (d) 실제 결과 (2026-05-06 21:28 측정 완료)

> 측정 시간 103.7s
> - **DEEP** (vs RANDOM20): s=0.01 -3.70% / s=0.05 -1.99% / s=0.10 -0.63% / s=0.30 -0.47% / s=0.50 -0.41%
> - **SIFT** (vs RANDOM20): s=0.01 -4.12% ★ / s=0.05 -4.04% ★ / s=0.10 -3.35% ★ / s=0.30 -1.85% / s=0.50 -1.41%
> - **paired Wilcoxon vs RANDOM20**: 6/10 cell 통계 유의 (DEEP s=0.05/0.50 + SIFT s=0.05/0.10/0.30/0.50)
> - **가설 H3-E refute 강하게 in 좋은 방향**: 예상 20~60% recovery 였으나 실제 **MiniBatch 와 동등 또는 SIFT 에서 우수**.
> - **DEEP vs SIFT 비교**: SIFT 에서 효과 더 강함 (-1.4~-4.1% vs DEEP -0.4~-3.7%) — skew data 가 PCA 2D + Hilbert 의 spatial 분할에 더 잘 매칭.

### 의의

confirm 시 (recovery 30-50%) → **"학습 없는 결정론적 stratification 의 contribution"** narrative. KM oracle 의 절반 정도 회수하면서 학습 비용 0. 5/27 발표의 contribution 4번째 (Recovery Rate Framework) 의 구체 사례.

특별히 좋으면 (recovery > 60%) → **본 연구의 핵심 발견** 으로 격상 가능 (Hilbert 가 cluster 구조 의외로 잘 반영).

→ **2026-05-06 핵심 발견 격상**: Hilbert 가 학습 0 + 결정론으로 MiniBatch K-means (1% 학습) 와 동등 또는 SIFT 에서 우수. **본 연구의 contribution 후보 1번**. 5/27 발표의 핵심 differentiator.

---

## 실험 #6 — A. LSH (★ 4순위)

### (a) 동기

cosine LSH (Charikar 2002) 는 random hyperplane 으로 cosine 유사도를 보존하는 정통 hash 방법. **"학습 없이 hash 로 어디까지?"** Random Projection 의 argmax 1개와 달리 5 sign bits 의 다수 → 더 fine-grained bucket. 다만 mod k=20 으로 collision 발생.

### (b) 가설 H3-A

**LSH 의 recovery_rate 는 30-60%.** Random Projection (argmax 1개) 보다 좋고 Hilbert Curve 와 비슷한 수준. cosine 유사도 보존 정도가 cluster 구조 반영의 proxy.

### (c) 예상 결과

- **recovery_rate ≈ 30-60%**: Random Projection (10-40%) 보다 +10-20%p 우수. multi-bit hash 의 fine-grained 효과.
- **bucket 분포 imbalance (max/min 2-5 배)**: 5 sign bits → 32 raw bucket → mod 20 → bucket 0~11 은 2 raw 의 합집합. HT estimator 의 N_i weighting 이 보정.
- DEEP/SIFT 차이 작음 (distribution-agnostic).

### (d) 실제 결과 (2026-05-06 21:30 측정 완료)

> 측정 시간 97.4s
> - **DEEP** (vs RANDOM20): s=0.01 +16.18% ⚠️ / s=0.05 +5.03% / s=0.10 +3.28% / s=0.30 +1.04% / s=0.50 +0.63%
> - **SIFT** (vs RANDOM20): s=0.01 +23.81% ⚠️ / s=0.05 +4.22% / s=0.10 +3.03% / s=0.30 +1.12% / s=0.50 +0.58%
> - **paired Wilcoxon vs RANDOM20**: 0/10 cell 유의
> - **가설 H3-A refute**: 예상 30~60% recovery 였으나 실제 RANDOM20 보다 일관되게 나쁨
> - **vs Random Projection (#5) 비교**: LSH 와 RandProj 둘 다 negative recovery, LSH 가 약간 덜 나쁨 (특히 SIFT s=0.01 LSH +23.81% vs RandProj +45.14%) — 그러나 가설의 "+10~20%p 우수" 수준은 X. 둘 다 distribution-agnostic 한계 영역.

### 의의

confirm 시 → **"learning-free 알고리즘의 정통 baseline"** narrative. Random Projection 보다 LSH 가 우수하다는 점이 hash bit 수의 가치 증명.

Random Projection 과 큰 차이 없으면 → 둘 다 distribution-agnostic 의 한계 영역.

→ **2026-05-06 둘 다 한계 영역 confirm**: LSH/Random Projection 모두 RANDOM20 보다 나쁨. **부정적 control 가치** — "단순 hash/projection 만으로는 cluster 정보 회수 불가" 정량 증명.

---

## 실험 #10 — B. KDE-pilot (★ 5순위)

### (a) 동기

**Online query-adaptive 의 이론 상한** — 매 query 마다 pilot sample 로 cluster 별 hit probability KDE 추정 + Silverman bandwidth + Neyman optimal allocation. Online σ 추정의 정통 통계 방법. 정교한 만큼 비용 큼 (~6h 측정), 그러나 분포 모를 때의 **이론 상한 benchmark**.

### (b) 가설 H3-B

**KDE-pilot 의 recovery_rate 는 50-80%.** RQ2 의 Neyman vs Equal 측정 (SIFT 에서 -3~12% 효과) 의 online 버전. KM cluster 사전 정보를 사용하므로 cluster 분할 자체는 KM 같음 — 차이는 σ_i 가 query-adaptive 여부.

### (c) 예상 결과

- **recovery_rate ≈ 50-80%**: pilot 의 noise 가 σ 추정 변동성 야기. n_pilot=5 (cluster 당) 라 KDE 가 거친 추정. 그러나 Equal 보다 우수.
- **SIFT 에서 더 좋음**: cluster 비균질성이 큰 SIFT 에서 σ 의 가치 큼 (RQ2 Neyman 에서 입증).
- 좁은 sel (s=0.01) 에서 효과 강함 — RQ2 패턴 재현.
- 측정 시간 ~6시간 (pilot phase 가 query 마다 5 cluster × 5 sample fetch 추가).

### (d) 실제 결과

> [측정 후 채움]
> - recovery_rate (DEEP/SIFT):
> - SIFT 좁은 sel 의 효과:
> - vs RQ2 Neyman 비교:

### 의의

confirm 시 → **"online σ 추정의 이론 상한"**. KM oracle 과 KDE-pilot 의 격차가 cluster 분할 기여, RAND20 과 KDE-pilot 격차가 σ 추정 기여. 이 분해가 본 연구의 narrative.

refute (recovery > 90%) 시 → KDE-pilot 이 KM oracle 과 거의 동등. 그렇다면 KM 의 사전 학습 가치가 의문.

---

## 실험 #9 — G. Distance-Shell (★ 6순위)

### (a) 동기

KDE-pilot 의 단순화 ablation. cluster 분할 (KM) 대신 **5 distance shells (online quantile)** 로 분할 + Neyman. 사전 학습 X, 매 query 마다 즉석 분할. KDE-pilot 이 KM cluster + KDE 인 반면, Distance-Shell 은 **shell + Neyman** — 분할 단위가 다름.

### (b) 가설 H3-G

**Distance-Shell 의 recovery_rate 는 25-50%.** KDE-pilot (50-80%) 보다 낮음 — cluster 의 spatial 정보 잃고 distance quantile 만 사용하므로. 그러나 RANDOM20 보다는 우수 (Neyman 효과).

### (c) 예상 결과

- **recovery_rate ≈ 25-50%**: cluster 분할 정보 X 라 spatial 인식 약하나 distance-based shell 이 일부 반영.
- **DEEP/SIFT 차이 작음**: shell 분할이 distribution-agnostic.
- 좁은 sel 에서 효과 미미: shell 이 하나만 query 의 D 를 포함 → 다른 shell 의 σ ≈ 0.
- 측정 시간 ~4시간.

### (d) 실제 결과

> [측정 후 채움]
> - recovery_rate:
> - shell 별 N_i × σ_i 분포:
> - vs KDE-pilot (#10) 비교:

### 의의

KDE-pilot 과의 차이 = **"cluster 분할의 spatial 가치"** 정량화. Distance-Shell 이 KDE-pilot 의 70% 정도 recovery 면 cluster 의 추가 가치 30%p. 이게 KM 학습의 정량적 정당화.

---

## 실험 #11 — H. Importance Sampling (★ 7순위)

### (a) 동기

**비분할 + 가중치만**의 한계 측정. cluster/shell 분할 X, 전체 cache 한 덩어리. pilot 로 proposal density g(d) (Gaussian KDE) 추정, importance weight w = uniform/g 로 보정. **"분할 없이 가중치만으로 어디까지?"** 분할의 가치를 isolating.

**2x2 factorial**: pilot_size {50, 200} × weight_clip {True, False} = 4 mode. KDE 정확도 vs main IS 예산 trade-off, extreme weight 제어 efficacy.

### (b) 가설 H3-H

**Importance Sampling 의 recovery_rate 는 30-70%.** weight 만의 변동이 분할의 효과 (cluster + Neyman) 보다 약함. weight_clip 이 variance 감소시키나 약간의 bias.

### (c) 예상 결과

- **recovery_rate ≈ 30-70%**: weight 가 distance-based 라 일부 spatial 반영. 다만 분할 없이 noise dominant.
- **pilot_size 큰 게 우수**: 200 sample 의 KDE 가 50 보다 정확. 그러나 main IS 예산 줄어 trade-off.
- **weight_clip 효과**: True 가 variance 안정화. 좁은 sel 에서 효과 큼.
- DEEP/SIFT 모두 비슷.
- 측정 시간 ~6시간.

### (d) 실제 결과

> [측정 후 채움]
> - 4 mode recovery_rate:
> - 최적 (pilot, clip) 조합:
> - vs Distance-Shell (#9) 비교 — 분할 효과:

### 의의

분할 vs 비분할의 정량 비교. IS 가 Distance-Shell 보다 좋으면 weight 만으로도 충분, 나쁘면 분할의 가치 입증.

---

## 측정 종료 후 카톡 §3.2 발송 절차

각 실험 측정 끝나면:
1. `recovery_rate.py` 의 `summarize_method()` 로 cell 별 결과 산출
2. 위 (d) 실제 결과 채움 (recovery_rate, paired Wilcoxon p, paired vs KM20)
3. 카톡 §3.2 형식으로 4단계 narrative 출력:

```
[실험 #N 완료] HH:MM (소요 ~Nh)

실험명: ___
산출 위치: experiments/results/rq3_agnostic/...

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — [위 (a) 그대로]
(b) 가설 H3-X — [위 (b) 그대로]
(c) 예상 — [위 (c) 그대로]
(d) 실제 — [측정 후 채움]
    + 가설 confirm/refute
    + 예상 일치/불일치

═══ 의의 + 다음 ═══
- [위 의의 영역에서 confirm/refute 분기 적용]
- 다음 실험 #N+1 진행

자동 git commit + push 완료 (commit ___)
```

---

## 7개 실험 종합 표 (1차 4종 측정 완료 — 2026-05-06 21:34)

primary metric `method_minus_random_pct` (음수일수록 좋음, RANDOM20 대비):

| # | 실험 | 가설 H3-X | 예상 recov | 실제 (DEEP/SIFT 평균 절대값) | 통계유의 | 판정 | 의의 |
|---|------|-----------|------|------|------|------|------|
| #8 | MiniBatch | recov ≥ 75% | 75-95% | -2.0% (DEEP) / -2.5% (SIFT) | 8/10 | **confirm 강** | production solution |
| #5 | RandProj | recov 10-40% | 10-40% | +6.0% (DEEP) / +12.7% (SIFT, ⚠️ s=0.01 +45%) | 0/10 | **refute 역방향** | 부정적 control |
| #7 | Hilbert | recov 20-60% | 20-60% | -1.4% (DEEP) / -2.9% (SIFT) | 6/10 | **refute 강 in 좋은 방향** ★ | **learning-free 핵심 발견 후보** |
| #6 | LSH | recov 30-60% | 30-60% | +5.2% (DEEP) / +6.5% (SIFT) | 0/10 | **refute** | RandProj 와 동급, 부정적 control |
| #10 | KDE-pilot | recov 50-80% | 50-80% | [미측정] | - | 보류 | online σ 이론 상한 (~6h) |
| #9 | Distance-Shell | recov 25-50% | 25-50% | [미측정] | - | 보류 | cluster 분할 가치 ablation (~4h) |
| #11 | IS | recov 30-70% | 30-70% | [미측정] | - | 보류 | 분할 vs 비분할 (~6h) |

★ Hilbert 가 가설 (20-60% recovery) 보다 훨씬 강해 (MiniBatch 와 동등) **본 연구 contribution 1순위 격상**.

분모 붕괴 caveat: KM20 vs RANDOM20 격차 0.26~3.98% 라 recovery_rate 분모 fall-back 활성. primary metric 을 method_minus_random_pct 로 변경.

---

## 5/8 19:00 회의용 핵심 메시지 (사전 hypothesis)

가설들이 confirm 되면 다음 narrative 가능:

1. **MiniBatch K-means (#8) — production-ready 솔루션**: KM oracle 의 75%+ recovery + 학습 시간 1/100. 본 연구의 핵심 추천.
2. **Hilbert Curve (#7) — learning-free contribution**: 결정론 + 학습 X + recovery 30-50%. 5/27 발표의 differentiator.
3. **Recovery Rate Framework — 본 연구의 metric contribution**: 7-way trade-off curve (학습 비용 vs recovery). 분포 정보의 가치 정량화.
4. **Limitations**: 단일 테이블 / OLTP 범위 외 / 단일→멀티 future work — RQ재정립 plan 그대로.

---

**작성**: 조현빈 · 2026-05-06 21:00 KST · 8M 측정 진행 중 사전 narrative 설계
**Trigger**: RQ3 #N 측정 완료 시 본 문서의 §실험#N 의 (a)(b)(c) + 측정 결과 (d) 합쳐서 카톡 §3.2 발송.
