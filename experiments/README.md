# Experiments — Skew-Aware Sampling for VAQ Cardinality Estimation

## 개요

Exqutor의 Adaptive Sampling이 skewed 거리 분포에서 카디널리티 추정 정확도가 떨어지는 문제를 검증하고, 분포 특성을 고려한 대안 샘플링 전략을 실험한다.

## 디렉토리 구조

```
experiments/
├── config/             실험 파라미터 (데이터셋, 선택도, 샘플 크기)
├── results/
│   ├── rq1_motivation/ RQ1: skewness vs Q-error 관계 검증
│   ├── rq2_aware/      RQ2: stratified sampling (분포 알 때)
│   └── rq3_agnostic/   RQ3: KDE-pilot 자동 층화 (분포 모를 때)
└── figures/            분석 시각화 (산점도, 박스플롯, 히트맵)
```

## RQ-실험 매핑

| RQ | 핵심 질문 | 판단 기준 |
|----|----------|----------|
| RQ1 | Adaptive sampling은 skew에 취약한가? | \|γ\|>1 그룹의 Q-error가 \|γ\|<0.5 대비 2배↑ |
| RQ2 | Stratified sampling으로 얼마나 개선? | Q-error 50%↓ (skew 심할수록 개선 폭↑) |
| RQ3 | KDE-pilot으로 자동 층화 가능한가? | Q-error 30%↓, pilot 오버헤드 20%↓ |

## 지표

- **Q-error**: max(estimated/actual, actual/estimated)
- **Recall@k**: top-k 정확도
- **QPS**: 초당 처리 쿼리 수
- **Latency**: p50, p99

## 데이터셋

| 규모 | 데이터셋 | 차원 | 크기 |
|------|---------|------|------|
| Small | SIFT1M | 128 | 1M |
| Small | GloVe-100 | 100 | 1.2M |
| Medium | Deep10M | 96 | 10M |
| Medium | GIST1M | 960 | 1M |
| Large | Deep1B | 96 | 1B (하드웨어 허용 시) |

## 선택도 구간

0.1% → 1% → 5% → 10% → 30% → 50%

## 환경 (대기 중)

- 연구실 서버 (석사분 제공 예정)
- Exqutor 코드 + 데이터 (4/7 주 수령 예정)
- pgvector (PostgreSQL), DuckDB
