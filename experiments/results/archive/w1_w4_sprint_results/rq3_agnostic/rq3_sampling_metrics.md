# RQ3 학술 표준 Sampling Metric — ESS / DEFF / ICC

기존 q_error / Cohen's d / paired Wilcoxon 외 **survey sampling 분야 표준 metric** 추가.
5/27 발표 / 6/11 보고서 의 학술 robust 강화.

## 정의

- **DEFF** (Design Effect, Kish 1965): `Var(stratified) / Var(SRS)`. < 1 → 우수.
- **ESS** (Effective Sample Size): `n / DEFF`. 본 연구 budget n=385 기준.
- **ICC** (Intraclass Correlation): query-level 동질성. ↑ → query-specific signal 강.

## Method 별 평균 DEFF / ESS / ICC (10 dataset × sel cells 평균)

```
                deff_mean  ess_mean  icc_mean  n_cells          deff_class
method                                                                    
distance_shell      2.516   218.872     0.048       10           나쁨 (>1.5)
hilbert             0.338  2324.814     0.024       10  매우 우수 (DEFF < 0.5)
is_p200_clip       18.676   109.829     0.176       10           나쁨 (>1.5)
is_p50_clip        39.741   255.770     0.203       10           나쁨 (>1.5)
kde_pilot           2.519  1477.849     0.110       10           나쁨 (>1.5)
km20                0.403  2215.304     0.014       10  매우 우수 (DEFF < 0.5)
lsh                 1.433   774.043     0.027       10   약간 나쁨 (1.0 ~ 1.5)
minibatch           0.377  2252.882     0.037       10  매우 우수 (DEFF < 0.5)
random20            0.449  1315.313     0.014       10  매우 우수 (DEFF < 0.5)
random_proj         2.563   634.559     0.009       10           나쁨 (>1.5)
```

## 해석

**DEFF 가 1.0 미만**인 method 만 통계학 표준 의미의 "우수":
- KM20 oracle / Hilbert / MiniBatch / KDE-pilot 의 DEFF 가 1.0 미만이면 stratification 효과 정량 입증
- IS / Distance-Shell 의 DEFF > 1.0 은 negative control 의 정량 evidence

**ESS** = 385 / DEFF — "stratified 385 표본의 효과 = SRS 의 ESS 표본":
- DEFF = 0.5 → ESS = 770 (SRS 의 770 표본과 동등)
- DEFF = 1.0 → ESS = 385 (동등)

**ICC** — query 의 difficulty signal 정량:
- ICC ↑ → query 별 q_error 가 inherent (seed 노이즈와 분리). method routing 의 정당성 ↑.
- 본 연구의 spread vs difficulty ρ=0.78 와 같은 방향의 정량.

## 5/27 발표용 narrative

본 metric 은 q_error mean 외 **variance 측면의 정량** 이므로 학술 발표의 robust 강화.
Cohen's d (effect size) + DEFF (variance reduction) + ICC (query signal) 3 metric 의
통합 framework 가 본 연구의 sampling 분야 standard contribution.
