# Cluster Granularity Sensitivity — K=10 vs K=20 (5/13 02:00 분석)

> **분석 시점**: 2026-05-13 02:00 KST  
> **데이터 source**: paper_exact_km10/ (40 file, K=10) + paper_exact/ (K=20 base, 기존 1001 file 안)  
> **목적**: 강재현 5/13 1:00 피드백 "stratified 수가 multi-join 시 cardinality 추정에 미치는 영향" 정량 검증  
> **K=30 측정 진행 중** (km30_relaunch tmux, ETA 5/13 04:30) — 회수 후 3-way 비교 완성

---

## 0. 분석 scope

- 4 anchor method: **sparse_rp, hilbert_real, hyperloglog, chao_weighted** (paradigm anchor 대표)
- 5 cells: single (A1-DEEP/SIFT/SSN sf=100) + multi (A2-Fig7/Fig9)
- 2 modes 중 CaseB ensemble augment 결과만 비교
- 4 method × 5 cells = 20 paired cells × {K=10, K=20} = 40 measurement 비교

---

## 1. K=10 vs K=20 paired Δ% — method 별 sensitivity 차이

각 cell 의 K=10 baseline 대비 Δ% 와 K=20 baseline 대비 Δ% 비교 (단위: %, 음수 = 개선).

### sparse_rp (P4 DimReduction anchor) ★ 매우 K-sensitive

| Cell | K=10 Δ% | K=20 Δ% | diff (K=10 − K=20) |
|---|---:|---:|---:|
| A1-DEEP | +5.60 | -11.20 | **+16.81** |
| A1-SIFT | -1.28 | -13.28 | +11.99 |
| A1-SSN | +2.80 | -11.50 | +14.30 |
| A2-Fig7 (multi) | +7.19 | -10.46 | +17.65 |
| A2-Fig9 (multi) | +10.93 | -6.58 | +17.51 |

→ **K=10 에서 효과 무효 또는 악화** (+10% 까지), **K=20 에서 강력 개선** (-10~-13%).

sparse_rp 는 random projection 으로 차원 축소 후 stratum 분할 — projection 후 dimension 이 K=10 의 거친 분할로는 stratum 내 분산 추정이 불안정. K=20 이 sparse RP 의 sweet spot.

### hilbert_real (P2 Spatial anchor) — K-robust

| Cell | K=10 Δ% | K=20 Δ% | diff |
|---|---:|---:|---:|
| A1-DEEP | -12.37 | -10.91 | -1.46 |
| A1-SIFT | -13.47 | -13.18 | -0.29 |
| A1-SSN | -11.15 | -10.58 | -0.57 |
| A2-Fig7 (multi) | -11.41 | -11.52 | +0.11 |
| A2-Fig9 (multi) | -5.88 | -6.07 | +0.19 |

→ **K=10 와 K=20 거의 동일** (diff |1.5% 이내|). Hilbert curve 의 space-filling locality 가 cluster granularity 에 insensitive.

### hyperloglog (P9 InfoTheoretic anchor) — K-robust

| Cell | K=10 Δ% | K=20 Δ% | diff |
|---|---:|---:|---:|
| A1-DEEP | -9.08 | -10.54 | +1.46 |
| A1-SIFT | -12.14 | -12.20 | +0.06 |
| A1-SSN | -10.11 | -10.67 | +0.56 |
| A2-Fig7 (multi) | -9.63 | -8.77 | -0.86 |
| A2-Fig9 (multi) | -6.61 | -5.15 | -1.45 |

→ K=10 와 K=20 거의 동일 (|diff| < 1.5%). HyperLogLog 의 hash-based distinct count 추정이 cluster granularity 와 독립.

### chao_weighted (P3 Streaming anchor) — 약간 K-sensitive

| Cell | K=10 Δ% | K=20 Δ% | diff |
|---|---:|---:|---:|
| A1-DEEP | -10.43 | -12.20 | +1.77 |
| A1-SIFT | -11.85 | -14.80 | +2.95 |
| A1-SSN | -12.74 | -15.28 | +2.54 |
| A2-Fig7 (multi) | -10.99 | -11.77 | +0.79 |
| A2-Fig9 (multi) | -7.13 | -6.00 | -1.13 |

→ single cell 에서 **K=20 가 K=10 보다 약 2-3% 더 우수**. multi cell 에서는 거의 동일. chao_weighted 의 weighted reservoir 가 K=20 의 미세 stratum 분할에서 약간 더 효율.

---

## 2. 핵심 narrative — cluster granularity 효과는 method 의존적

본 분석의 핵심 finding:

**1. sparse_rp (차원 축소 paradigm anchor) 는 cluster granularity 에 결정적 sensitive**:
- K=10 의 거친 분할로는 효과 무효화 (+5~+11% 악화)
- K=20 가 sweet spot (-10~-13% 강력 개선)
- 단일 측정 결과 sparse_rp 는 K=20 환경에서만 유효

**2. hilbert_real / hyperloglog 는 K-insensitive**:
- 두 method 모두 K=10 와 K=20 에서 거의 동일 효과 (|diff| < 1.5%)
- Hilbert space-filling curve 와 HyperLogLog hash 함수 모두 cluster granularity 와 독립적인 방식

**3. chao_weighted 는 약간 K-sensitive (K=20 우세)**:
- single cell 에서 K=20 가 약 2-3% 더 우수
- weighted reservoir 가 K=20 의 균등 분할에서 약간 더 효율

**4. multi-table cell 에서도 method 별 sensitivity 패턴 동일**:
- A2-Fig7/Fig9 의 K-sensitivity 가 single cell 과 유사. sparse_rp 만 큰 차이 (+17%), 다른 anchor 들은 robust.
- 강재현 1번 의도 "stratification 수가 multi-join 시 cardinality 추정에 미치는 영향" 의 정량 답변: **multi-join cell 에서도 sparse_rp 만 큰 영향, 다른 anchor 들은 robust**

---

## 3. K=30 측정 진행 중 — 3-way 비교 완성 예정

km30_relaunch tmux 진행 중 (wrapper v2 사용, 40 measurement, ETA 5/13 04:30 KST).

회수 후 3-way 비교 plan:
- sparse_rp 의 K=10 / K=20 / K=30 trend — K=20 가 sweet spot 인지 또는 K=30 가 더 우수한지
- hilbert_real / hyperloglog 의 K=30 robustness 확인 (예상 유사)
- chao_weighted 의 K=30 우세 패턴 확인 (예상 K=30 ≥ K=20 ≥ K=10)

---

## 4. v5 deck 정정 plan — cluster granularity sensitivity narrative

신규 slide 추가 가능:

**S18 (또는 신규) — K-sensitivity by method**:
- 4 anchor method × K=10/20/30 line chart
- "sparse RP 는 cluster granularity 에 결정적 sensitive, Hilbert/HyperLogLog 는 robust"
- caption: "본 결과는 method 별 cluster granularity 의존성이 다름을 정량 입증. 균일한 sweet spot 보다 method 특성 별 sensitivity 매핑이 더 의미"

또는 limitation slide 에 명시:
- "cluster 수 K 의 선택이 method 별로 다른 영향을 미친다. 본 발표는 K=20 base 측정에서 가장 큰 개선 효과 결과를 보고하며, K-sensitivity 자체는 method 별로 다른 향후 분석 영역."

---

## 5. 5/15 박광현 미팅 confirm 추가 항목

- cluster granularity (K=10/20/30) sensitivity 가 method 의존적이라는 발견의 학술적 의미
- sparse RP 의 K-sensitivity 가 random projection 의 차원 축소 효과와 cluster 분할의 trade-off 로 해석 가능한가
- multi-join cell 에서도 same sensitivity 패턴 — multi-table 영역의 stratification 처리 방식과 무관

---

작성: 2026-05-13 02:00 KST · 강재현 1:00 피드백 정량 검증 + K=30 회수 후 3-way 비교 완성 예정
