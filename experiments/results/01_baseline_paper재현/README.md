# 01_baseline_paper재현 — paper §V-B Bernoulli baseline

Exqutor 논문 §V-B 의 **Bernoulli Adaptive Sampling** (B1) 을 그대로 재현한 cell별
baseline. 모멘텀 기반 동적 표본 (Eq 1~6, N=385). 본 연구의 모든 비교는 이 B1 대비
q-error 가 얼마나 줄었는지를 본다.

- file 17개 (cell 당 B1 1개)
- 구조: `{데이터셋}_{sf}/{측정캠페인}/{데이터셋}_{sf}_B1.json`
- `run-paper-exact/` = 5월 paper-exact portfolio, `run-v6-v10/` = 확장 측정 v6~v10
- 핵심 지표 `avg_q_error_trimmed` — paper Fig 12 의 평균 q-error 1.69 를 재현 (실측 mean 1.618, −4.3%)

> B1 은 method 가 없다 (Bernoulli 무작위 표본 그 자체). CaseB 측정과 짝지어 본다.
