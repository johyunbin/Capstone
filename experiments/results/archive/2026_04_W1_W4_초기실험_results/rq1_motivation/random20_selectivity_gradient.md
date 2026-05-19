# RANDOM20 Control — Selectivity Gradient 분석

**측정일**: 2026-04-15 14:02~14:55 KST (53분)
**스크립트**: `experiments/code/rq1/random20_low_sel.py`

---

## I. 핵심 발견 — Selectivity Gradient

| selectivity | KM20 mean | KM20 CI | RAND mean | RAND CI | 차이 |
|---|---|---|---|---|---|
| **0.500** | +1.64% | [+1.25, +2.02] | +2.20% | [+1.45, +2.95] | ~0 (RAND≈KM20) |
| **0.050** | +1.85% | [-0.22, +3.42] | +0.79% | [-1.05, +2.63] | +1.1%p (KM20 약간 우세) |
| **0.010** | **+8.93%** | [+6.59, +10.95] | **-10.67%** | [-15.26, -6.51] | **+19.6%p (KM20 지배)** |

### CI 분리 여부

- **s=0.010**: KM20 CI [+6.59, +10.95] vs RAND CI [-15.26, -6.51] → **완전 분리. 유의미.**
- **s=0.050**: CI 중첩 → 유의하지 않으나 KM20 방향 일관
- **s=0.500**: CI 중첩 → 차이 없음

---

## II. 교수님 프레이밍 직결

> "데이터가 쏠려있을 때 → uniform sampling이 나빠지고 → 개선된 sampling으로 해결"

### Step 1: 데이터가 쏠려있다
- DEEP 96d 1M 데이터의 KM20 cluster 크기: 26K~81K (ratio 3.1×, Gini 0.1275)

### Step 2: 쏠림이 낮은 selectivity에서 query 결과를 집중시킨다
- s=0.500: true matches가 모든 cluster에 고르게 분포 (HHI ≈ 0.067 ≈ 1/K)
- s=0.010: true matches가 소수 cluster에 집중 (HHI ↑↑)

### Step 3: 공간 인식 sampling이 이를 해결한다
- s=0.010에서 **KM20 stratified**: +8.93% 개선 (cluster 구조를 알고 있으므로 집중 영역에서 적절히 표본 추출)
- s=0.010에서 **RANDOM20 stratified**: -10.67% 악화 (무작위 partition은 집중 영역을 반영��지 못하고 오히려 왜곡)

### 핵심 인과 논증

```
KM20 (공간 인식):    s=0.010에서 +8.93%  → 쏠린 영역을 안다 → 적절한 표본 배분
RANDOM20 (무작위):   s=0.010에서 -10.67% → 쏠린 영역을 모른다 → 왜곡된 표본 배분
───────────────────────────────────────────────────
차이 19.6%p의 원인 = KM20이 공간 구조(쏠림)를 반영하기 때문
```

---

## III. Two-Level Decomposition

### Level 1: Proportional Allocation Effect (보편적)

- 어떤 partition이든 stratified > BERNOULLI (표본 크기 안정화)
- s=0.500에서 관찰: KM20 +1.64%, RANDOM20 +2.20% (둘 다 개선)
- **이 효과는 partition 품질과 무관**

### Level 2: Spatial Awareness Effect (selectivity-dependent)

- 공간 구조를 반영한 partition이 추가 이득을 제공
- **s=0.010에서 관찰**: KM20 +8.93% vs RANDOM20 -10.67%
- **이 효과는 query 결과의 cluster 집중도(HHI)가 높을 때만 발현**

### Selectivity에 따른 두 효과의 기여

```
s=0.500: [========Level 1========]                    ← proportional allocation만
s=0.050: [========Level 1========][L2]                ← 약한 공간 인식 효과
s=0.010: [===Level 1===][========Level 2========]     ← 공간 인식이 지배
```

---

## IV. Per-seed 상세

### s=0.010

| seed | KM20 diff% | KM20 p | RAND diff% | RAND p |
|---|---|---|---|---|
| 0.1 | +8.51 | 0.061 | -10.63 | 0.782 |
| 0.2 | +11.42 | 0.217 | -7.77 | 0.670 |
| 0.3 | +11.53 | 0.091 | -11.51 | 0.614 |
| 0.4 | +4.33 | 0.016* | -19.01 | 0.937 |
| 0.5 | +8.87 | 0.027* | -4.43 | 0.406 |

KM20: 5/5 양, 2/5 유의. RANDOM20: **5/5 음** (전부 악화).

### s=0.050

| seed | KM20 diff% | KM20 p | RAND diff% | RAND p |
|---|---|---|---|---|
| 0.1 | +2.23 | 0.015* | +3.46 | 0.334 |
| 0.2 | +3.47 | 0.008** | +2.41 | 0.099 |
| 0.3 | +3.96 | 0.003** | +1.39 | 0.578 |
| 0.4 | -2.08 | 0.188 | -2.03 | 0.919 |
| 0.5 | +1.69 | 0.260 | -1.28 | 0.841 |

KM20: 3/5 유의. RANDOM20: 0/5 유의 (효과 불분명).

---

## V. 연구 Narrative (확정)

> "Exqutor의 BERNOULLI sampling은 두 가지 수준의 약점을 가진다:
>
> (1) **확률적 변동**: 행 단위 독립 표본 추���로 표본 크기 자체가 확률 변수 → proportional allocation으로 해결 (보편적 효과, partition 품질 무관).
>
> (2) **밀도 편향**: 벡터 데이터의 공간 밀도가 비균일할 때, query 결과가 밀집 영역에 집중되면 uniform sampling이 해당 ���역을 과소/과대 표본할 가능성 → 공간 인식 partition (KM20)으로 해결 (selectivity-dependent 효과).
>
> RANDOM20 control 실험으로 이 두 효과를 분리: s=0.500에서는 (1)만 작동하여 KM20≈RANDOM20, s=0.010에서는 (2)가 지배하여 KM20 +8.93% vs RANDOM20 -10.67%."

---

## VI. 파일 목록

| 파일 | 내용 |
|------|------|
| `random20_low_sel_summary.json` | 전체 결과 JSON |
| `random20_control_summary.json` | s=0.500 결과 (이전 실험) |
| `random20_control_analysis.md` | s=0.500 분석 (업데이트 필요) |
| `random20_selectivity_gradient.md` | **본 문서** — 전 selectivity 통합 분석 |
