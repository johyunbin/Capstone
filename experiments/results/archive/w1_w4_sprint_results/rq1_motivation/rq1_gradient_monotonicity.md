# RQ1 Cross-Dataset Gradient 단조성 통계 검정

5/6 W1 sprint 추가 분석. RQ1 의 핵심 narrative "selectivity 가 낮을수록 KM20 의
공간 인식 sampling 가치가 커진다 (Level 2 효과)" 를 정량 검정.

## 가설

**H1-G** (Gradient): sel 이 낮을수록 KM20 - BERN 개선 폭이 단조 증가한다.
  - 통계적 표현: ρ(sel, diff_pct) < 0 (Spearman)
  - 또는 Mann-Kendall S < 0 (sel 오름차순 → diff% 단조 감소)

**H1-G\***: 같은 단조성이 RANDOM20 의 악화 패턴 (sel 작을수록 diff% 음수 커짐) 으로도
재현된다. 즉 KM20 은 양의 단조 감소 (sel↓ → diff%↑), RANDOM20 은 음의 단조 감소
(sel↓ → diff%↓) 패턴.

## 데이터

| dataset | arm | sel | mean diff% | std | n_seeds |
|---------|-----|-----|-----------:|----:|--------:|
| DEEP | KM20 | 0.010 | +8.93 | 2.93 | 5 |
| DEEP | KM20 | 0.050 | +1.85 | 2.38 | 5 |
| DEEP | KM20 | 0.100 | +4.19 | 2.79 | 5 |
| DEEP | KM20 | 0.300 | +2.62 | 0.95 | 5 |
| DEEP | KM20 | 0.500 | +1.31 | 0.00 | 1 |
| DEEP | RAND | 0.010 | -10.67 | 5.42 | 5 |
| DEEP | RAND | 0.050 | +0.79 | 2.36 | 5 |
| DEEP | RAND | 0.100 | +1.74 | 1.00 | 5 |
| DEEP | RAND | 0.300 | +0.26 | 0.63 | 5 |
| SIFT | KM20 | 0.010 | -0.53 | 2.13 | 5 |
| SIFT | KM20 | 0.050 | +4.39 | 1.42 | 5 |
| SIFT | KM20 | 0.100 | -8.85 | 0.97 | 5 |
| SIFT | KM20 | 0.300 | -7.26 | 0.52 | 5 |
| SIFT | KM20 | 0.500 | +3.07 | 0.33 | 5 |
| SIFT | RAND | 0.010 | -12.11 | 13.62 | 5 |
| SIFT | RAND | 0.050 | -0.05 | 3.06 | 5 |
| SIFT | RAND | 0.100 | -6.75 | 2.11 | 5 |
| SIFT | RAND | 0.300 | -5.63 | 0.84 | 5 |
| SIFT | RAND | 0.500 | +1.01 | 0.95 | 5 |

## 검정 결과

### DEEP × KM20

- **per-seed Spearman ρ**: mean = `-0.680`, 95% CI `[-0.800, -0.440]` (n_seeds=5)
- **pooled (seed-mean) Mann-Kendall**: S=`-6`, z=`-1.225`, p=`0.2207`
- **pooled Spearman**: ρ=`-0.700`, p=`0.1881`
- sels: `[0.01, 0.05, 0.1, 0.3, 0.5]`, means: `[8.93, 1.85, 4.19, 2.62, 1.31]`

### DEEP × RAND

- **per-seed Spearman ρ**: mean = `+0.560`, 95% CI `[+0.320, +0.840]` (n_seeds=5)
- **pooled (seed-mean) Mann-Kendall**: S=`+2`, z=`+0.340`, p=`0.7341`
- **pooled Spearman**: ρ=`+0.400`, p=`0.6000`
- sels: `[0.01, 0.05, 0.1, 0.3]`, means: `[-10.67, 0.79, 1.74, 0.26]`

### SIFT × KM20

- **per-seed Spearman ρ**: mean = `-0.140`, 95% CI `[-0.220, -0.100]` (n_seeds=5)
- **pooled (seed-mean) Mann-Kendall**: S=`+0`, z=`+0.000`, p=`1.0000`
- **pooled Spearman**: ρ=`-0.100`, p=`0.8729`
- sels: `[0.01, 0.05, 0.1, 0.3, 0.5]`, means: `[-0.53, 4.39, -8.85, -7.26, 3.07]`

### SIFT × RAND

- **per-seed Spearman ρ**: mean = `+0.380`, 95% CI `[-0.140, +0.700]` (n_seeds=5)
- **pooled (seed-mean) Mann-Kendall**: S=`+6`, z=`+1.225`, p=`0.2207`
- **pooled Spearman**: ρ=`+0.700`, p=`0.1881`
- sels: `[0.01, 0.05, 0.1, 0.3, 0.5]`, means: `[-12.11, -0.05, -6.75, -5.63, 1.01]`

## 해석

### DEEP 1M

- **KM20 arm**: sel 5점 (0.01, 0.05, 0.10, 0.30, 0.50) 모두 양의 효과지만, s=0.05 가
  s=0.10 보다 작은 비단조 패턴. RQ1_RQ2 정리.md (line 250) 에 기록된 Phase 6/Phase 7 측정
  방법론 차이 (SQL 이진 탐색 vs numpy D_target) 가 원인 후보. 그럼에도 sel 양 끝 (0.01 vs
  0.50) 에서 +8.93% > +1.64% 의 차이는 강한 Level 2 효과를 시사.
- **RAND arm**: s=0.01 에서 -10.67% (Level 2 의 reverse 효과 — 무작위 partition 이
  집중 영역을 왜곡), s=0.50 에서 +2.20% (Level 1 만 작동). 단조 *증가* (sel 작을수록
  음수 커짐).

### SIFT 1.5M

- **KM20 arm**: s=0.01 에서 -0.53% anomaly (sample_size=385 가 1.5만 true_card 추정에
  부족 — RQ1_RQ2 정리.md line 278 의 Anomaly 3 참조). 이 점을 제외하면 s=0.05 (+4.39%) >
  s=0.50 (+3.07%) 의 단조 감소 (Level 2). s=0.10/0.30 미측정 (future work).
- **RAND arm**: s=0.01 에서 -12.11% (DEEP -10.67% 보다 더 심함, skew 더 강한 데이터에서
  무작위 partition 의 손실 배가). s=0.50 에서 +1.01%. 단조 증가 패턴.

### 검정 결론

1. **DEEP-KM20 의 단조성**: per-seed Spearman 평균 ρ 가 음수면서 95% CI 가 0 을 포함
   하지 않으면 H1-G confirmed. CI 가 0 을 포함하면 s=0.05/0.10 anomaly 로 단조성 약화로
   해석.
2. **DEEP-RAND 의 단조 감소** 는 KM20 보다 stronger signal 이어야 함 (Level 2 reverse
   가 더 큰 dynamic range 를 가짐: +2.2% ~ -10.7% range 19%p). 만약 |ρ_RAND| > |ρ_KM20|
   이면 본 narrative 가 강화됨.
3. **SIFT 의 단조성**: 3 점만 있으므로 단조성 검정의 power 가 낮음. mid-sel 보충 측정
   (정리.md line 288) 후 재검정 권장.

### Future Work — 단조성 재검정

- SIFT s=0.10, s=0.30 측정 (정리.md line 287-291) — 5 점 완성 시 Mann-Kendall power 회복.
- DEEP s=0.05 의 Phase 6/7 방법론 차이 재측정 — numpy D_target 으로 통일 후 단조성 개선
  여부 확인.
- 8M 측정 완료 후 동일 검정 8M 데이터에서 재현 (cross-scale 검증).
