# 실험 B — RANDOM20 Control 결과 분석

**측정일**: 2026-04-15 13:23~13:53 KST
**소요시간**: 29분 30초 (1766초)
**스크립트**: `experiments/code/rq1/random20_control.py`

---

## I. 실험 목적

교수님 프레이밍 "데이터가 쏠려있을 때 → uniform sampling이 나빠지고 → 개선된 sampling으로 해결"의 **인과관계를 직접 증명**하기 위한 대조 실험.

**예상**: KM20 stratified (공간 구조 반영) → 개선 있음 / RANDOM20 stratified (무작위 partition) → 개선 없음

---

## II. 실험 설계

| 조건 | partition | Gini 계수 | 의미 |
|------|-----------|-----------|------|
| KM20 | k-means 20 cluster | 0.1275 | 공간 밀도 비균일성 반영 |
| RANDOM20 | `floor(random() * 20)` | 0.0027 | 균일 무작위 → 공간 구조 무시 |

동일 100 query × 6 selectivity, 동일 `vector.sampling_method = 'stratified'` 코드.
Multi-seed (5 seeds) 측정은 s=0.500에 집중.

---

## III. 핵심 결과 — 예상과 반대

### A. s=0.500 multi-seed (5 seeds) 비교

| 조건 | BERN 대비 개선 | 95% CI | 해석 |
|------|---------------|--------|------|
| **KM20 stratified** | +1.64% | [+1.25, +2.02] | Phase 6 Step 4 기존 결과 |
| **RANDOM20 stratified** | +2.20% | [+1.45, +2.95] | **예상 ≈ 0%, 실제 +2.20%** |

CI 중첩 구간: 0.57%p → **두 partition의 개선 폭이 통계적으로 구별 불가**.

### B. 절대 Q-error 직접 비교 (s=0.500)

| 측정 | median Q-error | IQR |
|------|---------------|-----|
| KM20 STRAT | 1.0339 | [1.0166, 1.0526] |
| RANDOM20 STRAT | **1.0340** | [1.0186, 1.0634] |
| KM20 BERN | 1.0529 | [1.0251, 1.0904] |
| RANDOM20 BERN | 1.0477 | [1.0259, 1.0948] |

**KM20 STRAT vs RANDOM20 STRAT 차이: -0.01%** (Mann-Whitney p=0.317)

→ 공간 구조를 반영한 partition과 무작위 partition이 **사실상 동일한** Q-error를 산출.

### C. 전 selectivity 절대 Q-error 비교 (seed=0.1)

| sel | KM20 STRAT | RAND STRAT | 차이 | KM20 BERN | RAND BERN |
|-----|-----------|-----------|------|----------|----------|
| 0.001 | 2.5806 | 3.3156 | -28.5% | 2.5806 | 3.3156 |
| 0.010 | 1.3874 | 1.2998 | +6.3% | 1.2917 | 1.5080 |
| 0.050 | 1.1429 | 1.1894 | -4.1% | 1.2109 | 1.1600 |
| 0.100 | 1.1083 | 1.1157 | -0.7% | 1.1097 | 1.1222 |
| 0.300 | 1.0523 | 1.0454 | +0.7% | 1.0623 | 1.0921 |
| **0.500** | **1.0339** | **1.0340** | **-0.01%** | 1.0529 | 1.0477 |

- s=0.001: cnt-clamp fallback 영역 (STRAT = BERN), 차이는 seed에 의한 BERN 측정 분산
- s=0.010~0.050: 방향 불규칙 (신호 미약)
- **s=0.100~0.500**: 두 partition 사실상 동일

### D. BERN baseline 일관성 검증

KM20-era BERN (1.0529) vs RANDOM20-era BERN (1.0477): 차이 0.50%, Mann-Whitney p=0.842
→ partition 교체(UPDATE + ANALYZE)가 BERN 측정에 미친 영향 **무시 가능**.

---

## IV. 해석

### A. 왜 RANDOM20 stratified도 개선되는가?

**Proportional allocation의 분산 축소 효과** (survey sampling 이론의 고전적 결과):

- BERNOULLI: 각 행이 독립적으로 p 확률로 선택 → 표본 크기 자체가 확률 변수
- Stratified (proportional): 각 stratum에서 정확히 `ceil(n × N_k/N)` 행 선택 → 표본 크기 확정
- 이 "표본 크기 확정" 효과만으로 추정 분산이 감소하며, **이 효과는 stratum 정의와 무관**

```
Var(ŷ_strat) ≤ Var(ŷ_SRS) — 항상 성립, partition 품질과 무관
추가 이득 = Σ W_k (μ_k - μ)² — strata 간 평균 차이가 클 때만 발생
```

s=0.500에서 true matches가 거의 모든 cluster에 분포 (HHI ≈ 0.067 ≈ 1/K)하므로, strata 간 평균 차이가 작아 **추가 이득이 거의 없음**. Proportional allocation 효과만 남음.

### B. "쏠림이 원인" 가설의 상태

| 가설 구성 요소 | 상태 |
|---------------|------|
| 데이터의 공간 밀도가 비균일하다 | ✅ (Gini=0.1275, cluster ratio 3.1×) |
| 비균일성이 uniform sampling을 나빠지게 한다 | ⚠️ **미확인** — BERN의 나쁜 성능은 비균일성 때문이 아니라 단순히 확률적 변동 |
| 공간 구조를 반영한 stratified가 이를 해결한다 | ❌ **부정** — 무작위 partition도 동일한 개선 |

### C. 연구 방향 시사점

1. **"stratified > BERN" 자체는 유효한 finding** — 다만 원인이 "공간 인식"이 아니라 "proportional allocation"
2. **s=0.500은 쏠림 효과를 관찰하기에 부적합** — matches가 전 cluster에 고르게 분포하므로 partition 품질 무관
3. **낮은 selectivity (s=0.010~0.050)에서 차이가 나타날 가능성** — cluster 집중도(HHI)가 높아지면 KM20이 유리할 수 있음
4. **교수님 프레이밍 수정 필요** — "쏠림 → 성능 저하 → 공간 인식 sampling 개선"이 아니라 "확률적 변동 → 성능 저하 → 구조적 sampling(proportional allocation) 개선"

---

## V. 후속 실험 제안

### 즉시 (실험 C 확장)

**Per-selectivity KM20 vs RANDOM20 multi-seed**:
- s=0.050, s=0.100에서 5-seed 재측정
- cluster 집중도(HHI)가 높은 selectivity에서 KM20이 유리한지 확인
- 만약 HHI가 높은 영역에서 KM20 > RANDOM20이면 "쏠림이 원인" 가설 부분 구제

### 중기

**가변 K (strata 수) 실험**:
- K=5, 10, 20, 50에서 KM20 vs RANDOM 비교
- K가 커질수록 proportional allocation 효과 증가 vs KM의 공간 분해능 증가

---

## VI. 파일 목록

| 파일 | 내용 |
|------|------|
| `random20_control_summary.json` | 전체 결과 JSON |
| `random20_strat_all_sel.parquet` | RANDOM20 stratified 전 selectivity (600 rows) |
| `random20_bern_all_sel.parquet` | RANDOM20 BERN 전 selectivity (600 rows) |
| `random20_control.py` | 실험 스크립트 (`experiments/code/rq1/`) |
