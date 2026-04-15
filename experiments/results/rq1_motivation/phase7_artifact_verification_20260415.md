# Phase 7 ARTIFACT 검증 결과 — 2026-04-15 10:50 KST

**검증자**: 조현빈 (+ Claude Opus 4.6 심층 딥리뷰)
**근거 리뷰**: `experiments/results/rq1_motivation/deep_review_20260415.md` §B.1
**검증 대상**: `phase7_8m_paired_qerror.json` / `phase7_sift_paired_qerror.json` 의 "BERN median q-error 20810 vs STRAT 9.60, ratio 2168×, p=1.95e-18, 100/100 win" 주장 및 sift 의 "ratio 409×, 409×" 주장

**검증 결론**: **주장이 artifact 임이 결정적으로 확정됨**. Phase 7 narrative 의 양대 anchor 중 Phase 7 측은 **완전 철회 필요**.

---

## 1. 검증 방법

본 검증은 딥리뷰 §B.1 에서 제시한 5 증거 (A~E) 의 경험적 확인 단계로, 다음 두 액션을 수행했다.

**액션 1**: `experiments/results/rq1_motivation/phase7_{8m,sift}_strat.parquet` 의 `plan_rows` 열을 직접 조회해 분포 확인. 가설 확정 조건은 "거의 모든 row 가 19~20 근처".

**액션 2**: `phase7_{8m,sift}_paired.json` (hook_est 기반, 현재 "garbage" 로 배제됨) 과 `phase7_{8m,sift}_paired_qerror.json` (plan_rows 기반, 현재 primary) 의 결과를 직접 대조해 BERN/STRAT 방향 반전 확인.

## 2. 검증 결과

### 2.1 plan_rows 분포 — **정확히 20 고정**

```
phase7_8m_strat.parquet (100 rows):
  plan_rows describe:
    count = 100.0
    mean  = 20.0
    std   = 0.0
    min   = 20.0
    25%   = 20.0
    50%   = 20.0
    75%   = 20.0
    max   = 20.0
    unique = 1
  plan_rows value_counts:
    20: 100
```

```
phase7_sift_strat.parquet (100 rows):
  plan_rows describe:
    count = 100.0
    mean  = 20.0
    std   = 0.0
    min   = 20.0, max  = 20.0
    unique = 1
  plan_rows value_counts:
    20: 100
```

**해석**: 두 데이터셋 모두 100 query 전부 `plan_rows = 20` 으로 **정확히 상수**. 이는 stratified sampling 의 estimator 출력이 아니라 plan tree 의 `Aggregate → Append → [Subquery Scan × 20 stratum]` 구조에서 `find_scan_node` 가 첫 Subquery Scan 의 `Plan Rows = LIMIT 20` 값을 반환한 결과임을 결정적으로 증명한다. 즉 20 은 estimator 가 아니라 **stratum 당 LIMIT 상한 상수**이다.

### 2.2 q_error 산술 일치

Phase 7-1 deep 8M:
- `true_card_median = 192.83` (mean), `192` (median), std=13.36, min=161, max=228
- `plan_rows = 20` (정확히 상수)
- 예측 q_error median = `max(20/192, 192/20) = 9.6` → **저장된 `strat_median = 9.6` 과 정확히 일치**

Phase 7-2 sift 128d:
- `true_card_median = 192`
- `plan_rows = 20`
- 예측 q_error median = `192/20 = 9.6` → **저장된 `strat_median = 9.475` 과 일치** (std=13 의 변동 범위 내)

**해석**: q_error 의 수학적 구조가 `true_card / stratum_limit` 패턴임을 직접 확인. 이는 딥리뷰 §B.1 증거 B 와 완전히 일치한다.

### 2.3 hook_est 기반 결과 (paired.json) — 완전 반전

**phase7_8m_paired.json** (hook_est 기반, `alternative='less'` — STRAT < BERN 의 paired 검정):
```json
{
  "n_paired": 100,
  "bern_median": 16687.474273685835,
  "strat_median": 21111.171688819944,
  "diff_pct": -26.50908904836339,
  "w_stat": 4365.0,
  "p_less": 0.9999999998746222,
  "n_better": 26,
  "n_worse": 74,
  "n_tie": 0
}
```

**해석**:
- hook_est 기반으로는 `STRAT median (21111) > BERN median (16687)` 즉 **STRAT 가 BERN 보다 26.5% 더 나쁨**
- 100 query 중 **26 query 만 STRAT 가 이김**, 74 query 는 STRAT 가 짐
- `p_less = 0.9999` 는 "STRAT < BERN" 가설에 대한 p-value 로, 1.0 에 가까움은 **해당 가설이 완전 반증됨** 을 의미 (반대로 "STRAT > BERN" 가설은 유의)

**phase7_sift_paired.json** (hook_est 기반):
```json
{
  "n_paired": 100,
  "bern_median": 3968.7990580832184,
  "strat_median": 16867.123931467137,
  "diff_pct": -324.99314489389457,
  "w_stat": 3791.0,
  "p_less": 0.9999932831680253,
  "n_better": 37,
  "n_worse": 63,
  "n_tie": 0
}
```

**해석**:
- sift 128d 에서 `STRAT (16867) > BERN (3968)` 즉 **STRAT 가 BERN 보다 325% 더 나쁨**
- 100 query 중 **37 query 만 STRAT 가 이김**, 63 query 는 STRAT 가 짐
- 8M deep 보다 패배 폭이 더 큼

### 2.4 plan_rows 기반 결과 (paired_qerror.json) 대조

**phase7_8m_paired_qerror.json**:
```json
{
  "actual_selectivity_median": 2.4125e-05,
  "actual_true_card_median": 193,
  "bern_median": 20810.20895522388,
  "strat_median": 9.6,
  "diff_pct_median": 99.95386879574033,
  "improvement_ratio": 2167.7300995024875,
  "w_stat": 0.0,
  "p_less": 1.948279922547955e-18
}
```

**해석**:
- plan_rows 기반은 "BERN 20810 vs STRAT 9.6, ratio 2168×" 를 보고하며, 이는 `w_stat = 0.0` (모든 paired 가 한 방향) 에서 scipy wilcoxon 의 saturation floor p-value `1.948e-18`
- 이 결과가 바로 자문 이메일 §5 line 84 / 중간보고서 §4.7 / 슬라이드 Slide 10 의 **"양대 anchor" 주장의 유일한 근거**

**phase7_sift_paired_qerror.json**:
```json
{
  "actual_selectivity_median": 0.000128,
  "actual_true_card_median": 192,
  "bern_median": 3875.342800453515,
  "strat_median": 9.475,
  "improvement_ratio": 409.0071557206876,
  "w_stat": 0.0,
  "p_less": 1.948... (동일한 saturation floor)
}
```

## 3. 결정적 판정

### 3.1 Artifact 확정

두 metric 채택에서 나오는 결과가 완전히 반대다. 어느 것이 맞는가?

**hook_est 기반이 맞다는 근거**:
1. Phase 6 Step 4 `summary.md §IX.2` 가 명시적으로 선언: "find_scan_node 가 첫 Subquery Scan 의 Plan Rows 를 반환하면 엉뚱한 값" + "hook_est 가 authoritative"
2. Phase 6 Step 4 의 모든 ★ 신호 (s=0.500 p=4.01e-05 포함) 는 hook_est 기반으로 얻어졌으며, 본 연구의 정당화된 metric
3. Phase 7 코드가 hook_est 를 "alignment 깨짐" 으로 배제한 근거는 `EXPLAIN ANALYZE` 의 log 파싱 문제였는데, 이는 **측정 도구의 문제**이지 hook_est 자체의 품질 문제가 아님
4. plan_rows = 20 은 수학적으로 `LIMIT` 상수일 뿐이며, **어떤 의미에서도 stratified estimator 의 출력이 아님**

**plan_rows 기반이 맞다는 근거**: **없음**. plan_rows 20 이 estimator 출력이라는 어떤 기술적 근거도 확인되지 않음.

### 3.2 철회 범위

**철회 대상 주장**:
1. ❌ "Phase 7-1 deep 8M 에서 BERN 20810 vs STRAT 9.60, ratio 2168× 개선"
2. ❌ "Phase 7-2 sift 128d 에서 BERN 3875 vs STRAT 9.48, ratio 409× 개선"
3. ❌ "둘 다 100/100 query win, p < 1e-18"
4. ❌ "Phase 7-1 의 ratio 2168× 는 본 연구 전체 단일 최강 신호"
5. ❌ "Phase 6 Step 4 의 s=0.500 p=4.01e-05 와 함께 RQ2 본선의 양대 anchor"
6. ❌ "Pivot C 의 효과가 정상 selectivity 영역과 small selectivity 영역 양쪽에서 보완적으로 확인됨"

**새 정직 보고**:
1. ✅ Phase 7-1 deep 8M 에서 `actual selectivity ≈ 2.4e-5` 의 극극소 영역 측정 결과, KM20 stratification 의 hook_est 기반 median q-error 가 BERN 대비 **26.5% 나쁨 (STRAT 21111 vs BERN 16687)**, 100 query 중 STRAT 가 이긴 쿼리는 26/100
2. ✅ Phase 7-2 sift 128d 에서 같은 극극소 영역 (actual sel ≈ 1.3e-4), STRAT 가 BERN 대비 **325% 나쁨 (STRAT 16867 vs BERN 3968)**, 100 중 37/100
3. ✅ 이 결과는 Phase 4 의 `s=0.001` SYSTEM=BERN=2.597 tie 패턴 (양 모드가 cnt-clamp fallback 동일 발동) 과 Phase 6 Step 4 의 `s=0.001` STRAT=BERN=2.5806 동률 (Horvitz-Thompson estimator 가 극극소 영역에서 fallback) 과 **일관된 방향성을 보임**
4. ✅ 결론: **KM20 stratification 은 cnt-clamp fallback 영역 (s ≤ 0.001) 에서 효과 없음**. Phase 7 은 이 fallback 영역의 외적 확장 재현이며, 의도했던 정상 selectivity 영역의 외적 확장은 측정되지 않았다.

### 3.3 남은 유효 신호

본 철회 후 RQ1 + RQ2 의 유효 학술 신호는 다음으로 축소된다.

**핵심 anchor (단일)**:
- **Phase 6 Step 4 native s=0.500 deep 96d 1M**: KM20 stratified 가 BERN 대비 `+1.81%` 정량 개선, paired Wilcoxon `p=4.01e-05`, 66/100 query 가 STRAT 우세
  - 본 신호는 약 110 검정 Bonferroni 보정 (`α_adj = 4.5e-04`) 후에도 유일하게 생존
  - 단 1 seed 측정이므로 effect size CI 미확보, Python counterfactual (+0.33%) 과의 5× gap 원인 미분리

**보조 신호**:
- **Phase 4 native (Pivot A, SYSTEM→BERNOULLI 1 줄 교체)**: `s=0.050~0.500` 4 구간에서 paired p<0.001, median diff +3.8~9.6%, 78/100 query 가 BERN 우세 → Exqutor 의 `TABLESAMPLE SYSTEM` block bias 를 BERNOULLI 로 제거하면 median q-error 가 3.8~9.6% 감소
  - 단 이는 Pivot C 의 기여가 아닌 Pivot A 의 기여

**구조적 finding (negative result)**:
- **Phase 3 + Phase 5**: 글로벌 4 + 로컬 4 = 8 skewness 지표 × 6 selectivity = 48 조합 전수 `|ρ| < 0.2` → query-conditional layer 사전 식별 불가능성 확정
  - 단 n=100 에서 `ρ=0.2` 탐지 power 는 α=0.05 기준 약 0.47 → 조건부 negative (n=500+ 에서 재검증 필요)

**Exqutor design constraint finding**:
- Hook trigger 사각지대 (`vector.c` L243 `table_count > 2`)
- Plan replacement 부작용 (hook 우회 시 base relation Sample Scan 격하)
- TABLESAMPLE SYSTEM block bias (L889 hard-coded)
- 기술 부록 3 종 (q-error inf 발산, sample_size NaN, Adaptive SIGSEGV)

## 4. 새 narrative 골격 (Phase 7 철회 후)

```
4/3 교수님 합의 (Skew-Aware Sampling v3)
 ↓
4/14 오전: H1 (Fisher γ 기반) 기각
 ↓
4/14 오후: Exqutor design constraint 4~5 개 발견
 ↓
4/14 저녁: Pivot A + Pivot C 병합 노선 확정
 ↓
Phase 4 native: Pivot A 가 block bias 제거 (4 구간 p<0.001)
 ↓
Phase 5: Local 4 지표 전수 negative (24 조합 |ρ|<0.2)
 ↓
Phase 6 Step 3' Python: KM20 가 PCA decile / KM10 대비 최대 effect (s=0.1 +2.25%)
 ↓
★ Phase 6 Step 4 Native: KM20 stratified 가 s=0.500 에서 +1.81% 개선, p=4.01e-05
 ↓
Phase 7: 8M + sift 128d 로 외적 확장 시도 → **cnt-clamp fallback 영역으로 이동해 STRAT 효과 실종**
 ↓
결론: Phase 6 Step 4 s=0.500 의 단일 신호가 본 연구의 최강 정량 증거
      Phase 7 의 외적 확장은 "정상 sel 영역 확장 실패 + fallback 영역 재현" 으로 기록
```

## 5. 긴급 후속 액션 (D-13)

### 5.1 최우선 (D+0 오늘 오후)

1. **본 검증 결과를 자문 이메일에 반영** — 자문 이메일 §5 를 "Phase 7 의 의도된 외적 확장은 D_target 재계산 부재로 fallback 영역으로 이동했으며, hook_est 기반 paired 분석에서 KM20 stratification 은 이 영역에서 효과 없음을 확인했습니다. 본 결과는 Phase 4/6 의 fallback 영역 일관된 발견과 부합하며, RQ2 본선의 유효 anchor 는 Phase 6 Step 4 의 s=0.500 단일 신호로 축소됩니다" 로 재작성
2. **자문 3 항목 재설계** — (a) 시나리오 전환 정당성, (b) Pivot 병합 기여 정당성 은 유지, (c) 는 "Phase 6 Step 4 단일 anchor 의 학술적 강도 (1.81% + p=4e-05) 가 중간발표 본선 narrative 로 충분한가" 로 재편
3. **중간보고서 §4.7 재작성** — Phase 7 을 "외적 확장 실패 + fallback 재현 finding" 으로 재분류, §5.1 RQ 진행률 표에서 RQ2 완료율 하향
4. **중간발표 슬라이드 Slide 10 대체** — "Phase 7 외적 타당성" → "Phase 7 외적 확장의 한계 — 정상 sel 영역 재진입의 조건과 fallback 영역의 일관성" 으로 재구성

### 5.2 차순위 (D+1~2)

5. **deep_review_20260415.md §0 / §B.1 업데이트** — 확정 상태 반영
6. **Phase 6 Step 4 Native 추가 seed 측정** — `SELECT setseed(0.1~0.5)` 3 회 재측정해 effect size CI 확보. `+1.81%` 가 noise range 안에 있는지 확인
7. **Phase 7 의 진짜 외적 확장 재실행** — 8M 에서 D_target 을 *재계산* 해서 `actual_sel ≈ 0.5` 가 되도록 만든 후 100 query × 5 seed × 2 mode 재측정. 여기서 +1~2% 재현되면 외적 타당성 확보.

### 5.3 긴급 수정 3 산출물 라인 리스트

| 파일 | 라인 | 현재 표현 | 수정 방향 |
|---|---|---|---|
| `submission/속도는벡터_자문이메일_20260415.md` | §5 line 79~96 | "중요한 부수적 발견 + 2168×/409× 양대 anchor + 단일 최강 신호" | Phase 7 을 "외적 확장의 한계 발견 — fallback 영역 재현" 으로 재작성 |
| `submission/속도는벡터_중간보고서.md` | §4.7 line 110~130 | Phase 7 결과 표 + "양대 anchor 확보" | 위와 동일 재작성 + §5.1 RQ 진행률 표 RQ2 완료율 하향 |
| `submission/속도는벡터_중간발표.md` | Slide 10 line 220~250 | "Phase 7 외적 타당성 sf10 + sift" + 결과 표 | "Phase 7 외적 확장 한계 + fallback 영역 일관성" 으로 재구성 |
| `submission/속도는벡터_중간발표.md` | Slide 12 line 270~280 | "양대 anchor" 결론 | "Phase 6 Step 4 s=0.500 단일 anchor + Phase 7 negative finding" 으로 재작성 |
| `records/kakaotalk/20260415_작업완료 내일계획.md` | A 본문 | "양대 anchor" | 주의: 이미 commit 된 상태, 새 commit 에서 수정 |
| `records/kakaotalk/20260415_톡방공유 압축본.md` | §A [2] 핵심 결과 표 | "2168×" | 새 commit 에서 수정 |
| `records/kakaotalk/20260415_톡방공유 요약본.md` | ③ 핵심 수치 | "2168×, 409×" | 새 commit 에서 수정 |
| `experiments/results/rq1_motivation/summary.md` | Phase 7 (있다면) | - | 확인 후 수정 |
| `experiments/results/rq1_motivation/direction_pivot_rationale.md` | Phase 7 (있다면) | - | 확인 후 수정 |
| `plans/수정 연구 설계안_20260415_001500.md` | §V, §VIII 기여, §IX | 2168× / 양대 anchor | §V Phase 7 재작성 + §VIII 기여 수정 + §IX 일정에 Phase 7 재실행 추가 |

## 6. 본 검증의 학술적 의미

본 검증은 단순한 버그 수정이 아니라 **"자체 발견한 negative result 가 narrative 를 더 정직하게 만든다"** 는 학술 정직성의 본보기다. reviewer 가 동일한 검증을 수행할 때 나올 결과를 팀이 **자체적으로 먼저 발견하고 공개**하는 것이 본 연구의 학술 가치를 오히려 높인다. Phase 7 의 철회는 학술적 약화가 아니라 *measurement 엄밀성의 증거* 로 재framing 가능하다.

**본 검증 문서는 중간보고서와 자문 이메일의 첨부로 포함되어야 한다** — reviewer 와 멘토가 팀의 측정 엄밀성을 직접 확인할 수 있는 자료로서의 가치가 본 narrative 재작성의 비용보다 크다.

## 7. 검증 로그 원본

```
================================================================================
PHASE 7 ARTIFACT VERIFICATION — 2026-04-15 10:50 KST
================================================================================

[1] phase7_8m_strat.parquet — STRAT mode plan_rows 분포
  plan_rows: count=100, mean=20.0, std=0.0, min=20, max=20, unique=1
  value_counts: {20: 100}
  true_card: mean=192.83, median=192, std=13.36, min=161, max=228

[2] phase7_sift_strat.parquet — STRAT mode plan_rows 분포
  plan_rows: count=100, mean=20.0, std=0.0, min=20, max=20, unique=1
  value_counts: {20: 100}

[3] paired.json (hook) vs paired_qerror.json (plan_rows)

  8M hook:
    bern_median=16687.47, strat_median=21111.17
    diff_pct=-26.51 (STRAT 나쁨)
    n_better=26, n_worse=74
    p_less=0.9999999998746222

  8M plan_rows:
    bern_median=20810.21, strat_median=9.6
    improvement_ratio=2167.73
    w_stat=0.0, p_less=1.948e-18 (saturation floor)

  SIFT hook:
    bern_median=3968.80, strat_median=16867.12
    diff_pct=-325.0 (STRAT 325% 나쁨)
    n_better=37, n_worse=63
    p_less=0.9999932831680253

  SIFT plan_rows:
    bern_median=3875.34, strat_median=9.475
    improvement_ratio=409.01
    w_stat=0.0, p_less=1.948e-18 (saturation floor)
================================================================================
```

---

**본 검증 결과는 2026-04-15 10:50 KST 에 확정되었으며, 이후 모든 산출물 수정 작업의 근거가 된다. 본 문서는 `experiments/results/rq1_motivation/` 에 영구 보존되며, 중간발표 Q&A 및 자문 첨부에 사용된다.**
