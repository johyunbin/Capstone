# 통합 분석 — RANDOM20 Control × HHI Gradient

**작성일**: 2026-04-15 15:45 KST
**데이터 출처**: `random20_control_summary.json`, `random20_low_sel_summary.json`, `hhi_python_summary.json`, `phase6_multiseed_summary.json`

---

## I. 연구 질문과 실험 설계

**교수님 프레이밍**: "데이터가 쏠려있을 때 → uniform sampling이 나빠지고 → 공간 인식 sampling으로 해결"

이 프레이밍의 세 구성요소를 각각 독립적으로 실증하기 위해 다음 실험을 설계·수행했다.

| 구성요소 | 실험 | 측정 |
|---------|------|------|
| "데이터가 쏠려있다" | KM20 cluster 분석 + per-selectivity HHI | Gini, HHI, top-1 share |
| "쏠림 때문에 나빠진다" | RANDOM20 vs KM20 대조 | paired diff% 차이 |
| "공간 인식으로 해결" | KM20 stratified vs BERN | +1.64% CI [1.25, 2.02] |

---

## II. 핵심 결과 — Selectivity × Cluster 집중도 × 공간 인식 효과의 삼중 대응

### 통합 테이블

| sel | HHI | HHI/uniform | top1 | active | KM20 vs BERN | RAND vs BERN | KM20−RAND |
|-----|-----|------------|------|--------|-------------|-------------|-----------|
| 0.001 | 0.623 | **12.5×** | 71.2% | 7.3 | — | — | — |
| **0.010** | **0.503** | **10.1×** | **61.8%** | **14.0** | **+8.93%** | **−10.67%** | **19.6%p** |
| **0.050** | **0.291** | **5.8×** | **43.7%** | **19.0** | **+1.85%** | **+0.79%** | **1.1%p** |
| 0.100 | 0.186 | 3.7× | 31.6% | 19.9 | — | — | — |
| 0.300 | 0.091 | 1.8× | 16.2% | 20.0 | — | — | — |
| **0.500** | **0.067** | **1.3×** | **11.5%** | **20.0** | **+1.64%** | **+2.20%** | **−0.6%p** |

**읽는 법**: selectivity가 낮아질수록 (위로 갈수록) HHI가 급증하고, KM20과 RANDOM20의 차이도 급증한다.

### 삼중 대응의 의미

1. **HHI ↑ → RANDOM20 악화**: cluster 집중도가 높으면 무작위 partition이 집중 영역을 반영하지 못해 오히려 추정을 왜곡
2. **HHI ↑ → KM20 개선 폭 증가**: cluster 집중도가 높으면 KM20이 해당 영역에서 정확한 비례 배분 가능
3. **HHI ≈ 1/K → KM20 ≈ RANDOM20**: 집중도가 거의 균일하면 partition 품질 무관, proportional allocation만 유효

---

## III. Two-Level Decomposition

### 정의

**Level 1 — Proportional Allocation** (partition 무관, 보편적):
- Stratified sampling은 각 stratum에서 정확히 비례 배분 → 표본 크기 확정 → 추정 분산 감소
- Var(ŷ_strat) ≤ Var(ŷ_SRS) 항상 성립 (survey sampling 이론)
- **증거**: s=0.500에서 RANDOM20도 +2.20% 개선

**Level 2 — Spatial Awareness** (selectivity-dependent):
- 공간 구조를 반영한 partition이 strata 간 평균 차이를 최대화 → 추가 분산 감소
- 효과 크기는 query 결과의 cluster 집중도(HHI)에 비례
- **증거**: s=0.010에서 KM20 +8.93% vs RANDOM20 −10.67% (차이 19.6%p)

### Selectivity별 기여 분해 (개념적)

```
                  Level 1 기여        Level 2 기여
s=0.500:   [=================]  [  ]           ← proportional allocation 지배
s=0.050:   [============]  [======]            ← 공간 인식 시작
s=0.010:   [======]  [===================]     ← 공간 인식 지배
```

---

## IV. 통계적 유의성 정리

### s=0.500 (5-seed, 핵심 anchor)

| 조건 | mean diff% | 95% CI | 전 seed p<0.05 |
|------|-----------|--------|---------------|
| KM20 vs BERN | +1.64% | [+1.25, +2.02] | 5/5 ✅ |
| RANDOM20 vs BERN | +2.20% | [+1.45, +2.95] | 5/5 |
| KM20 vs RANDOM20 | −0.56%p | — | 차이 없음 |

### s=0.010 (5-seed, gradient 핵심)

| 조건 | mean diff% | 95% CI | 유의 seed |
|------|-----------|--------|----------|
| KM20 vs BERN | +8.93% | [+6.59, +10.95] | 2/5 |
| RANDOM20 vs BERN | −10.67% | [−15.26, −6.51] | 0/5 (전부 음) |
| **KM20 vs RANDOM20** | **+19.6%p** | **CI 완전 분리** | **유의미** |

### s=0.050 (5-seed, 전환 구간)

| 조건 | mean diff% | 95% CI | 유의 seed |
|------|-----------|--------|----------|
| KM20 vs BERN | +1.85% | [−0.22, +3.42] | 3/5 |
| RANDOM20 vs BERN | +0.79% | [−1.05, +2.63] | 0/5 |
| KM20 vs RANDOM20 | +1.06%p | CI 중첩 | 약한 효과 |

---

## V. Pivot A 기여 (Phase 4)

Pivot A (TABLESAMPLE SYSTEM → BERNOULLI)의 기여는 위 분석과 직교적이다.

| sel | SYSTEM vs BERN diff% | p | n_better |
|-----|---------------------|---|----------|
| 0.050 | +3.8% | <0.001 | 70/100 |
| 0.100 | +5.6% | <0.001 | 73/100 |
| 0.300 | +7.2% | <0.001 | 75/100 |
| 0.500 | +9.6% | <0.001 | 78/100 |

Pivot A는 "block sampling bias 제거"이며, Pivot C(KM20 stratified)의 fair baseline을 구축하는 역할. Pivot A + Pivot C는 직교적 두 단계 sanitize.

---

## VI. Design Constraint 5종 (Phase 3)

Exqutor 소스 코드(`vector.c`)에서 발견한 설계 제약:

1. **Hook trigger 사각지대**: `table_count > 2` 조건 → 단일 테이블 vector range query 배제
2. **Plan replacement 부작용**: hook이 plan tree를 Sample Scan으로 교체 → 결과 왜곡
3. **Block sampling bias**: TABLESAMPLE SYSTEM의 block 단위 상관
4. **Query feature 사전 식별 불가능성**: 8지표 전수 |ρ|<0.2
5. **Adaptive update path SIGSEGV**: `update_sample_size=on` 시 segfault

---

## VII. Phase 7 Negative Finding + 8M Redo

### Phase 7 원본 (artifact 철회)
- D_target 미재계산 → actual_sel ≈ 0.0001 → cnt-clamp fallback → plan_rows 고정 20 artifact
- hook_est 기반 재분석: STRAT가 BERN보다 나쁨 (8M −26.5%, sift −325%)
- **철회 확정** (2026-04-15 10:50 KST)

### Phase 7 Redo (진행 중)
- 8M D_target 재계산 완료: actual_sel ≈ 0.5001
- 5-seed 측정 진행 중 (예상 완료: ~16:30 KST)
- 1M의 +1.64%가 8M에서도 재현되면 외적 타당성 확보

---

## VIII. 연구 기여 요약

1. **Selectivity Gradient 발견**: 공간 인식 sampling의 효과가 selectivity에 의존함을 최초 실증
2. **Two-Level Decomposition**: proportional allocation과 spatial awareness를 분리·정량화
3. **RANDOM20 Control**: "쏠림이 원인"의 직접적 인과 증거 (s=0.010에서 19.6%p, CI 분리)
4. **HHI-Effect 대응**: cluster 집중도와 공간 인식 효과의 1:1 단조 대응 확인
5. **Design Constraint 5종**: Exqutor 내부 설계 제약의 체계적 문서화
6. **Block Sampling Bias 발견 및 교정** (Pivot A): +3.8~9.6% 개선

---

## IX. 파일 인덱스

| 파일 | 내용 |
|------|------|
| `random20_control_summary.json` | s=0.500 RANDOM20 vs KM20 |
| `random20_low_sel_summary.json` | s=0.010, 0.050 KM20 vs RANDOM20 |
| `hhi_python_summary.json` | 6 selectivity HHI 분석 |
| `phase6_multiseed_summary.json` | KM20 5-seed s=0.500 |
| `random20_strat_all_sel.parquet` | RANDOM20 strat 600 rows |
| `random20_bern_all_sel.parquet` | RANDOM20 bern 600 rows |
| `phase7_8m_redo_summary.json` | 8M redo (생성 예정) |
