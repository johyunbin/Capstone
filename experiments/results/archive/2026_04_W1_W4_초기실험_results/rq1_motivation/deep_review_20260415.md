# 2026-04-15 RQ1 + RQ2 심층 딥리뷰 — 연구 계획 v4 + Phase 1~7 실험 + 세 문서 narrative

**작성**: 조현빈 (+ Claude Opus 4.6)
**일시**: 2026-04-15 (수) 10:30 KST
**범위**: `plans/수정연구설계안_20260415_001500.md` (v4), `experiments/results/rq1_motivation/{summary.md, direction_pivot_rationale.md}`, Phase 1~7 측정 스크립트 + JSON 결과, `submission/{자문이메일_20260415, 중간보고서, 중간발표}.md`
**방법**: 3 축 병렬 agent 딥리뷰 (연구 계획 / Phase 실험 / narrative 일관성) → 본 문서에서 통합 + 긴급도 재배치
**목적**: 자문 이메일 발송 + 중간보고서 v2 편집 + 중간발표 준비 방향 결정 근거

---

## 0. 최종 판정과 긴급도 3 단계

본 딥리뷰의 가장 중요한 발견은 **축 B (Phase 1~7 실험)**에서 도출된 Phase 7 의 결과 해석에 대한 구조적 의심이다. 본 의심은 단순한 표현 수정이나 narrative 조정 수준이 아니라 *중간발표의 핵심 주장 자체를 철회해야 할 가능성*을 내포한다. 축 A (연구 계획 v4) 와 축 C (세 문서 narrative) 는 상대적으로 경미한 수준의 수정으로 정합성이 확보 가능하다.

### 🚨🚨 긴급도 1 (검증 완료 — **artifact 확정**, 즉시 narrative 철회 필요)

**2026-04-15 10:50 KST 에 artifact 가설이 경험적으로 확정됨**. 검증 결과는 `experiments/results/rq1_motivation/phase7_artifact_verification_20260415.md` 에 공식 기록. 핵심 결과:

- `phase7_8m_strat.parquet` 의 `plan_rows` 열: **100/100 row 가 정확히 20** (min=20, max=20, std=0, unique=1)
- `phase7_sift_strat.parquet` 의 `plan_rows` 열: **100/100 row 가 정확히 20** (동일 패턴)
- hook_est 기반 `phase7_8m_paired.json`: **STRAT median 21111 vs BERN median 16687, diff −26.5%, n_better 26/100, p_less=0.9999** → STRAT 가 BERN 보다 **26.5% 나쁨**
- hook_est 기반 `phase7_sift_paired.json`: **STRAT 16867 vs BERN 3968, diff −325%, n_better 37/100** → STRAT 가 BERN 보다 **325% 나쁨**
- q_error 9.6 = `193 (true_card median) / 20 (plan_rows 상수)` 정확히 일치 — stratum LIMIT 상수의 수학적 귀결

**즉시 철회 대상**: "Phase 7-1 2168× / Phase 7-2 409× 양대 anchor", "100/100 query win p<1e-18", "Phase 7 단일 최강 신호", "Pivot C 가 정상/small selectivity 양쪽에서 보완적으로 확인".

**새 narrative**: "Phase 7 의 외적 확장은 D_target 재계산 부재로 극극소 sel 영역 (actual ≈ 0.0001) 으로 이동했으며, hook_est 기반 분석에서 KM20 stratification 은 이 fallback 영역에서 효과 없음. 이는 Phase 4 s=0.001 tie 패턴 + Phase 6 Step 4 s=0.001 동률과 일관. RQ2 본선의 유효 anchor 는 Phase 6 Step 4 s=0.500 +1.81% p=4.01e-05 **단일**로 축소."

### ⚠️ 긴급도 2 (중간보고서 v2 필수 수정 — 약 90 분 편집)

- **Design constraint 수 "4" vs "5" 의 세 문서 내부 혼선**. 중간보고서 §5.1 line 137 의 RQ 진행률 표는 한 행 안에서 왼쪽 셀 "4 design constraint" 와 오른쪽 셀 "5 design constraint" 가 엇갈림. 자문 이메일 §2 line 39 (4) vs §7(c) line 112 (5). 슬라이드는 본문 2 + 부록 3 = 5 로 일관.
- **"3000 vs 6000" 표본 계산의 직접 모순**. 자문 이메일 line 37, 중간발표 Slide 5 line 85, 중간보고서 §2.2 line 26 은 "3000 측정", 중간보고서 §4.2 line 46 은 "6000 측정". 수학적으로 양립 가능하나 같은 수식 노출이 다른 값.

### 📝 긴급도 3 (부가 권장 — 4/22 1 차 팀 리뷰에서 자연스럽게 노출 + 정제)

- Phase 7 actual sel shift (0.5 → 0.0001) 의 해석 톤이 자문 이메일/슬라이드 ("부수적 발견" 긍정) 와 중간보고서 §5.2 ("honest 보고 필요" 한계) 로 분리됨.
- 전체 실험의 Multiple comparison 보정 (Bonferroni/FDR) 부재. 약 110 검정, Bonferroni 후 확실히 살아남는 신호는 Phase 6 Step 4 s=0.500 p=4.01e-05 1 개뿐.
- Phase 6 Step 4 Native 는 1 seed 측정이라 effect size CI 없음. Python counterfactual 과의 5× gap (+0.33% vs +1.81%) 이 RNG noise 인지 설계 차이인지 분리되지 않음.
- 연구 계획 v4 의 자문 (c) 는 팀 기본 결정이 이미 확정되어 실효성이 낮음. 제거된 direction_pivot_rationale.md §6.5 (Hook 우회 reviewer 노출) 가 자문 가치가 더 큼.

---

## A. 연구 계획 v4 심층 리뷰 (축 A)

### A.1 v3 → v4 변경 맵 — 정합적, "측정 정의 정교화" 표현이 실 변화 폭을 과소 표현

v3 (4/3, 244 줄) → v4 (4/15, 338 줄) 의 변화를 8 차원으로 분해하면 다음과 같다.

| 차원 | v3 (4/3 합의) | v4 (4/15 수정) |
|---|---|---|
| 본선 시나리오 | multi-table join + vector range filter (Exqutor 본 기여 영역과 일치) | **단일 테이블 vector range query 사각지대** (`vector.c` L243 `table_count > 2` hook trigger 우회) |
| RQ1 가설 | 수치 명제 "Fisher \|γ\|>1 그룹 Q-error 가 \|γ\|<0.5 대비 2 배↑" | **기술 보고형** "4 design constraint finding + 8 지표 전수 negative result" |
| RQ2 개선 도구 | EW/EF/Neyman × K(3/5/10/20) = 16 조합 매트릭스 | **Pivot A** (BERNOULLI 1 줄 교체) + **Pivot C** (KM20 단일 값 고정 stratified +228 줄) 병합 |
| RQ3 위치 | 2 단계와 동등 수준 본선, 중간발표 진입 모호 | **W7 (5/12~5/18) 완전 이월** — 중간발표 미진입 선언 |
| 데이터셋 | 1 데이터셋 (석사분 제공 1M subset) 단일 가정 | **1M deep + 8M deep + 128d sift + 768d wiki (W5)** 4 축 |
| 측정 규모 | 4800~9600 측정 (전략 × K × sel × query) | **270,000 측정** (3 dataset × 3 mode × 6 sel × 10 seed × 500 query) — 30~50× 확대, W6 이월 |
| 중간발표 범위 | β/γ 구분 없음 | **β 옵션** (sf10 8M + sift 1 구간) vs **γ 옵션** (wiki + 전 6 sel) 공식 분리 |
| 자문 형태 | 없음 | **이메일** 확정, 6 항목 → 3 항목 압축 |

v4 §I 이 주장하는 "큰 3 단계 구조와 핵심 동기는 그대로 유지, 측정 정의만 정교화" 라는 서술은 *3 단계 골격 (베이스라인 → Aware → Agnostic)* 과 *Exqutor Adaptive Sampling 의 skewed 환경 정확도 한계* 두 축에서는 검증된다. 다만 RQ1 가설이 수치 명제에서 기술 보고형으로 *형태 자체가 교체* 된 것은 "정교화" 가 아닌 "가설 형태 전환" 에 더 가까우며, 중간보고서 본문에서는 "3 단계 골격 보존 + 단계별 측정 정의 실질 교체" 로 표현 조정을 권고한다.

### A.2 Pivot A + Pivot C 병합의 논리 일관성 — 정당한 ablation matrix

두 pivot 의 직교성은 수학적 기반과 측정 수준 확보가 모두 갖춰져 있다. Pivot A (BERNOULLI 1 줄 교체) 는 *uniform 가정 내 granularity 차이* (block 8KB → row 독립 베르누이), Pivot C (KM20 stratified +228 줄) 는 *sampling design 의 차이* (naive uniform → per-stratum uniform + HT 가중). 두 차원은 원리상 직교하며, 3 mode (SYSTEM / BERNOULLI / STRATIFIED) × dataset × selectivity matrix 를 돌리면 SYSTEM→BERNOULLI 개선분이 Pivot A 단독 효과, BERNOULLI→STRATIFIED 개선분이 Pivot C 단독 효과로 분해된다.

**판정**: 정당한 ablation matrix. 기여 인플레이션 아님.

**권고**:
1. v4 §VIII 기여 3·4 의 표현을 "Pivot A 는 fair baseline 확립 도구 + Pivot C 의 단독 기여 분리 측정 역할" 로 명시.
2. 중간발표 슬라이드에 *Exqutor 원 코드 (L1188~1195 `TABLESAMPLE SYSTEM` hard-coded) vs 본 팀 1 줄 교체 diff* 를 병치한 figure 추가 — reviewer 가 "SYSTEM → BERNOULLI 가 근거 없는 선택의 교체" 임을 즉시 납득하게.
3. 3 mode (SYSTEM / BERNOULLI / STRATIFIED) × box plot 1 장 추가 — Pivot A 와 Pivot C 의 개선분이 시각적으로 분리되도록.

### A.3 시나리오 좁힘 (multi-table → 단일 테이블) — "새 학술 빈자리" 로 판정

"도망쳤다 vs 새 학술 빈자리" 판정의 핵심은 두 조건이다. 조건 1: 단일 테이블 우회 경로가 multi-table 본래 경로에 비해 *본질적으로 더 풍부한 학술 발견을 생산* 하는가. 조건 2: 단일 테이블 시나리오가 pgvector 커뮤니티 실무에서 *실제로 흔한* 가. 조건 1 은 4 finding 중 첫 두 가지 (Hook 사각지대, plan replacement 부작용) 가 단일 테이블 이동이 *구조적으로 생산한 발견* 이라는 점에서 충족 (multi-table 본래 경로로는 발견 불가능). 조건 2 는 v4 §II 의 세 사례 (이미지 검색, 추천, RAG retrieval) 가 학술적으로 즉시 납득 가능하나 *구체 인용* 이 없다.

**판정**: 새 학술 빈자리. 다만 다음 2 개 조정으로 설득력 강화.

**권고**:
1. v4 §II 에 단일 테이블 vector range query 의 실무적 중요성 인용 1~2 개 추가 (Supabase pgvector blog post, ANN benchmark 저장소 query set, pgvector github issues).
2. `direction_pivot_rationale.md` 의 시간 순서 narrative (4/3 합의 → 4/14 오전 실패 → 오후 신호 → 저녁 constraint 발견) 를 중간보고서의 **Discussion** 장에 *설계가 4 단계 검증 사이클로 정교화된 경로* 로 삽입 → *process transparency* 의 학술 미덕.

### A.4 RQ3 W7 이월 (5/12~5/18 KDE-pilot) — 실현 가능 하나 정량 이득 미지수

1D KDE 가 Phase 5 negative result 의 근본 원인을 우회하는 경로는 다음과 같다. Phase 5 negative 의 원인은 층 1 (고차원 거리 집중) + 층 2 (query feature 설명력 부재). 1D distance KDE 는 층 1 (고차원 geometry) 을 KDE 단계에서 우회하나, 층 2 는 여전히 *1D 거리 분포의 shape 이 q_error 와 무관* 할 수 있음을 시사한다. 다만 Phase 5 가 "query feature 의 q_error *사후 예측*" 을 측정했고, RQ3 는 "pilot-based quantile stratification 이 *naive uniform 대비 variance 감소*" 를 측정한다는 점에서 **두 주장이 logically compatible** 하다. Horvitz-Thompson estimator 의 variance 는 stratum 내 variance 가 total variance 보다 작으면 감소하므로, *1D 거리 분포가 얼마나 균일한가* 와 무관하게 *stratum 분할 자체가 within-variance 를 줄이면* 성립.

**판정**: 수학적으로 compatible, 구현 4 일 (Python 2 + Native 2) 은 타이트하나 가능. 정량 이득의 크기는 미지수.

**권고**:
1. v4 §III.RQ3 에 "1D KDE 는 수치 안정성 높음 + Phase 5 query feature 설명력 부재와 logically compatible" 한 문장 추가 — reviewer 의 "Phase 5 가 이미 1D skew feature 설명력 부재 보였는데 RQ3 는 왜 작동?" 공격 사전 차단.
2. v4 §VI.5 R3 대안 경로를 "histogram 기반 단순 층화" + "pilot 크기 축소 (500→100) + Python-only counterfactual" 2 단 degrade 로 확장 — Native 실패 시에도 W7 산출물 최소 확보.

### A.5 자문 3 항목 — (a)/(b) 적정, (c) 재편성 필요

| 항목 | 자문 가치 | 판정 |
|---|---|---|
| (a) 시나리오 전환 학술적 정당성 | 높음 — 팀 내부 결정 어려움, 멘토 외부 의견 결정적 | **적정** |
| (b) Pivot 병합 기여 정당성 | 높음 — 팀 내부 결정 일부 있으나 reviewer 관점 외부 검증 필요 | **적정** |
| (c) Design constraint 노출 수위 | 낮음 — 팀 기본 결정 "첫째·둘째만" 이 이미 내려짐, 멘토가 *기본 결정 확인* 이상의 답 가능성 낮음 | **재편성** |

한편 direction_pivot_rationale.md §6 의 6 → 3 압축 에서 제거된 §6.5 (Hook 우회 reviewer 노출) 는 *팀 내부가 자체 해결하기 어려운 외부 판정이 필요한 지점* 으로 (c) 보다 자문 가치가 높다.

**권고**:
1. 자문 (c) 를 "본 팀의 기본 결정 (첫째·둘째만 본문) 과 Hook 우회의 reviewer 관점 방어 전략" 으로 재표현 + §6.5 흡수.
2. (a)/(b) 는 현 표현 유지하되, 팀 입장의 "이중 역할" 표현이 *팀이 이미 결론 내린 인상* 을 주므로 *"팀 입장은 X 이나 다음 3 가지 대안 해석 가능, 멘토 판정 구함"* 형태로 대안 열거 추가.
3. v4 §VII 에 **자문 회신 부재 fallback 1 문장** 추가: "회신 부재 시 팀 기본 결정 (첫째·둘째만) 그대로 발표" — 일정 의존도 downgrade.

### A.6 v4 의 가장 약한 고리 3 개

**약점 1 — RQ1 가설 형태 전환으로 반증 가능성 약화**. v3 H1 은 수치 명제, v4 RQ1 은 기술 보고형. Reviewer 가 "96d DEEP 1M 에 국한된 결과" / "구현 관찰 vs 학술 명제" 로 공격 가능. 방어선: 중간보고서 본문에 "96d DEEP 국한성 명시 + RQ3 KDE-pilot 이 일반화 검증 경로" 한 문장 추가.

**약점 2 — β 옵션 1 seed × 1 sel 제약**. 5 seed × 6 sel × 1M 이 주 증거, 1 seed × 1 sel × 8M + 128d 가 보조 증거라는 hierarchy 가 슬라이드에서 시각적으로 전달되어야 함. 중간발표 슬라이드에서 "1 seed × 1 sel 예비 확장, 완전 ablation 은 W6" 제한 조건 명시 필요.

**약점 3 — Phase 7 일정 압축 + 자문 의존도**. 4/15~16 Phase 7 + 4/15~17 자문 회신의 병렬 일정. 자문 (a) 가 negative 면 Phase 7 의 학술 위치 가 흔들림. 방어선: v4 §VII 의 자문 fallback 1 문장 (위 A.5).

**전반 판정**: v4 는 중간보고서 Section 3~5 의 1 차 초안으로 *직접 사용 가능한 완성도*. 구조적 재설계 불필요. 축 A.2/A.3/A.5/A.6 의 권고는 모두 미세 조정 수준.

---

## B. Phase 1~7 실험 심층 리뷰 (축 B) — 🚨 긴급 이슈 포함

> **2026-04-15 10:50 KST 업데이트**: §B.1 의 "artifact 의심" 은 경험적으로 확정되었다. `phase7_{8m,sift}_strat.parquet` 의 `plan_rows` 열이 100/100 row 모두 정확히 20 (std=0) 임이 확인되었고, hook_est 기반 `phase7_*_paired.json` 에서 STRAT 가 BERN 대비 8M 에서 26.5%, sift 에서 325% 나쁘다는 완전 반전 결과를 얻었다. 상세는 `phase7_artifact_verification_20260415.md` 참조. 이하 §B.1 은 검증 전 원문이며, 검증 후 결론은 §0 긴급도 1 및 검증 문서에서 확인할 것.

### B.1 🚨 치명적 발견: Phase 7 의 `q_error = 9.6` 은 stratum LIMIT 20 artifact (확정)

**핵심 주장**: `phase7_8m_paired_qerror.json` 의 `strat_median = 9.6` 과 `phase7_sift_paired_qerror.json` 의 `strat_median = 9.48` 은 stratified sampling 의 estimator 품질이 아니라 *Aggregate → Append → [Subquery Scan × 20] plan tree 의 첫 Subquery Scan Plan Rows (= stratum LIMIT 값 19~20) 와 true_card (193/192) 의 비율 artifact* 일 가능성이 결정적이다.

**증거 A (Phase 6 Step 4 의 자체 기록)**: `summary.md §IX.2` 는 stratified mode 의 plan tree 구조를 명시적으로 기록: `Aggregate → Append → [Subquery Scan × 20 stratum]`. 각 Subquery Scan Plan Rows = `19~20` (= stratum LIMIT). 같은 문서에서 "find_scan_node 가 이 중 첫 Subquery Scan 을 반환하면 q_error 가 엉뚱한 값 (3749.98) 으로 나온다" 고 정확히 기록하고, 이 때문에 **Phase 6 Step 4 는 hook_est 를 authoritative 로 선언하고 plan_rows 를 배제했다**.

**증거 B (수치 재계산)**: Phase 7-1 의 `median_q_error = 9.6` × 20 ≈ 192 ≈ `true_card_median 193`. 즉 `q_error = 193 / 20 = 9.65` 로 **true_card / stratum_limit 패턴과 정확히 일치**. Phase 7-2 도 `9.48 × 20 ≈ 189.6 ≈ true_card 192` 로 같은 패턴.

**증거 C (hook_est 기반 결과는 반대)**: `phase7_8m_paired.json` (hook_est 기반, 현재 "garbage" 로 배제됨) 은 `BERN median 16687 vs STRAT 21111, n_better = 26/100, p_less ≈ 1.0` 즉 **STRAT 가 BERN 보다 오히려 나쁨**. `phase7_sift_paired.json` 도 `n_better = 37/100, p_less ≈ 1.0`. Plan_rows 기반 (`_qerror.json`) 은 `100/100 win, p = 1.95e-18`.

**증거 D (p-value saturation)**: `phase7_8m_paired_qerror.json` 과 `phase7_sift_paired_qerror.json` 의 p-value 는 둘 다 *정확히* `1.948279922547955e-18`. 이는 두 데이터셋 결과의 우연한 일치가 아니라 scipy `wilcoxon` 의 `w_stat = 0` (모든 paired 가 한 방향) 케이스에서 나오는 *고정 lower bound* 이다. 이론적으로 100-pair 에서 단측 wilcoxon 의 최소 p 는 `2^{-100} ≈ 7.9e-31` 이나 scipy normal approximation 은 `1.948e-18` 근방에서 saturate. 즉 이 숫자는 "통계 강력" 이 아니라 "측정 saturation artifact".

**증거 E (Phase 4 의 tie 패턴과 inconsistent)**: Phase 4 §V.2 에서 `s = 0.001` 은 `SYSTEM == BERN == 2.597` tie 였고, 이는 "fallback 경로 양 모드 동일" 로 해석됐다. Phase 7-1 의 actual sel = 2.4e-5 는 s=0.001 보다 40 배 작아서 *더 심한 fallback 영역* 이어야 하며, 그럼에도 2168× gap 이 나왔다는 것 자체가 구조적으로 모순.

**Phase 6 Step 4 와 Phase 7 의 metric 채택 모순**:
- Phase 6 Step 4 (`summary.md §IX.2`): "hook_est 가 authoritative, plan_rows 는 Subquery Scan 첫 번째 값이라 garbage → 제외"
- Phase 7 (`phase7_sf10_8m.py:539~541`): "plan_rows 가 authoritative, hook_est 는 alignment 깨짐 → 제외"

두 주장은 동시에 성립 불가능. **하나의 Phase 결정이 반드시 뒤집혀야 한다**.

**즉시 검증 방법** (약 20 분 소요):
```python
# phase7_8m_strat.parquet 의 plan_rows 열 직접 조회
import pandas as pd
df = pd.read_parquet('cache/rq1/phase7_8m_strat.parquet')
print(df['plan_rows'].describe())
print(df['plan_rows'].value_counts().head())
# 기대 결과 (artifact 가설 확정): 거의 모든 row 가 19~20 근처
```

만약 `plan_rows` 분포가 대부분 20 근처라면 artifact 가설 확정.

**확정 시 대응**:
1. `phase7_*_paired.json` (hook_est 기반) 을 primary 로 채택, `_qerror.json` 을 supplementary 로 강등
2. Phase 7 narrative 재작성: "96d 8M deep 과 128d 1.5M sift 의 actual sel ≈ 0.0001 영역 (= cnt-clamp fallback 영역) 에서 KM20 stratification 의 hook_est 기준 median q_error 가 BERN 보다 약간 크며 (26/37 win), 이는 Phase 4/6 의 fallback 영역 일관된 발견과 부합"
3. 중간발표 anchor 는 **Phase 6 Step 4 s=0.500 p=4.01e-05** 단일로 제한
4. "2168× / 409× 양대 anchor" 주장 철회
5. 3 산출물 (자문 이메일, 중간보고서, 슬라이드) 관련 부분 재작성

**artifact 가설 반증 시 대응**:
- `plan_rows` 가 20 이 아니라 실제 stratified estimator 결과라면 hook_est 쪽이 잘못된 metric 이었다는 뜻이 되며, Phase 6 Step 4 의 metric 선택이 반대로 뒤집혀야 함. 이 경우 Phase 6 Step 4 의 +1.81% p=4.01e-05 결과도 재검토 필요 — 이는 **Phase 6/7 모두의 narrative 재구성**을 의미.
- 어느 경로든 *중간발표 narrative 는 현재 상태로 유지 불가능*.

### B.2 통계 엄밀성 — Multiple comparison 보정 부재, effect size CI 미보고

본 실험 전체의 통계 검정 카운트는 약 **110 개**:

| 단계 | 검정 수 | 종류 |
|---|---:|---|
| Phase 3 Stage 4 §II.3 | 12 | Mann-Whitney U |
| Phase 3 §II.4 | 24 | Spearman ρ |
| Phase 4 §V.2 | 6 | paired Wilcoxon |
| Phase 5 §VI.3 | 24 | Spearman ρ |
| Phase 6 Step 1~3 §VII.3 | 6 | paired Wilcoxon |
| Phase 6 Step 3' §VIII.3 | 18 | paired Wilcoxon vs BERN |
| Phase 6 Step 3' §VIII.4 | 12 | paired Wilcoxon cross pair |
| Phase 6 Step 4 §IX.3 | 6 | paired Wilcoxon |
| Phase 7 | 2 | paired Wilcoxon |
| **합계** | **≈ 110** | |

α=0.05 × 110 검정의 family-wise error rate 는 `1 − 0.95^{110} ≈ 99.6%` → 우연으로 평균 5.5 개의 false positive. **Bonferroni 보정 후** α_adj = 4.5e-04:
- Phase 6 Step 3' KM20 의 s=0.100 (p=0.0042), s=0.300 (p=0.0157), s=0.500 (p=0.0157): **모두 Bonferroni 후 유의하지 않음**
- Phase 6 Step 4 native s=0.500 (p=4.01e-05): **유일하게 살아남음** (family 를 Phase 6 Step 4 만 6 검정으로 좁혀도, 전체 110 검정으로 넓혀도 양쪽 모두 생존)
- Phase 6 Step 4 native s=0.050 (p=0.00678), s=0.100 (p=0.0447): **Bonferroni 후 탈락**

Paired Wilcoxon 의 assumption (paired 차이 분포의 영점 대칭성) 은 명시적으로 검증되지 않음. q_error 는 `max(e/t, t/e) ≥ 1` 의 비대칭 분포이고 clamp fallback 영역에서는 `d_i ≈ 0` 이 지배적이라 대칭성이 깨짐. Wilcoxon p 는 보수적 방향으로 작용하므로 "p 작으면 더 신뢰" 방향성은 유지되나 effect size CI 해석은 불가능.

Effect size 지표 (Cohen d, Hedges g, CLES) 와 bootstrap 95% CI 가 한 번도 병기되지 않음. s=0.500 p=4.01e-05 + diff +1.81% 는 "통계 강력 but effect 작음" 의 전형. Reviewer 의 "p=4e-05 인데 왜 diff 가 1.81% 뿐?" 질문에 즉답 불가.

**권고**:
1. 모든 paired 테이블에 `p_raw`, `p_bonf` (또는 `p_bh_fdr`) 두 열 추가. "★" 는 `p_bh_fdr < 0.05` 에만.
2. 모든 ★ signal 에 Cohen d + bootstrap 95% CI 병기.
3. Phase 7 의 p=1.95e-18 는 철회 (saturation artifact) 하고 `n_better = 100/100` 또는 `binom_test p ≈ 7.9e-31` 로 대체.

### B.3 Phase 6 Step 4 Native — 1 seed + 5× gap 불확실성

Phase 6 Step 4 native 는 **1 seed 측정 + CI 없음**. Python counterfactual 5 seed 의 +0.33% 와 Native 1 seed 의 +1.81% 는 5× 차이.

**5× gap 원인 후보**:
- **가설 A**: Native 의 `ORDER BY random() LIMIT 20` 은 stratum 별로 *정확히 20 개* 반환 (상한 LIMIT), Python `rng.choice(n_i, size=s_i)` 는 *비례 배분*. 작은 stratum (26k row) 도 20 sample, 큰 stratum (81k row) 도 20 sample → Horvitz-Thompson weight 변동에 영향.
- **가설 B**: Python 은 같은 stratified sample 1 set 을 6 selectivity 에 재사용, Native 는 매 query 새 sample. RNG structure 차이가 within-seed variance 에 영향.
- **가설 C**: PG `random()` 은 session-local, seed 미고정 → native 측정은 "1 seed" 가 아니라 "PG session random state 의 1 snapshot". §IX.4 의 Python vs Native 일치성 표는 *Python 5 seed 평균 vs Native 1 snapshot* 비교이며, 엄밀한 동치성 증거가 아님.

**권고**:
1. Native 를 3~5 seed 로 재측정 (`SELECT setseed(0.1~0.5)`). s=0.500 의 effect size 분포 확보.
2. Python counterfactual 을 Native 설계 (stratum 당 LIMIT 20 상한 + query 간 새 sample) 로 맞춰 재측정. +0.33% 가 +1.81% 에 얼마나 가까워지는지 확인.
3. 슬라이드의 s=0.500 anchor 에는 "1 seed, CI 없음" 명시.

### B.4 재현성 — k-means 수렴 미검증, Phase 7 5 buggy fix

**강점**: seed 42 고정 + `vector.c` 빌드 md5 기록 + Python↔Native 소수점 셋째 자리 일치는 훌륭한 재현성 관행.

**약점 1**: 8M k-means 는 `batch=4096 × iter=100 = 400k` 로 **전체의 5% 만 본 상태** 로 centroid 확정 (1M 에서는 40% 본 상태). `inertia_mean` 이 1M (0.6925) 과 1% 차이 (0.6998) 여서 *겉보기 수렴* 이지만 centroid L2 이동 검증 없음.

**약점 2**: Phase 7 5 buggy fix 중 #5 (hook_est → plan_rows fallback) 는 버그 수정이 아니라 **metric 정의 변경이며, 그 변경 자체가 결과를 뒤집음** (B.1 참조).

**권고**: 8M k-means 를 `n_iter=1000` 또는 `sklearn.cluster.KMeans(n_init=10)` 로 재학습 후 centroid L2 차이 측정.

### B.5 외적 타당성 — 2 dataset 이 "2 독립 샘플" 아닌 "1 현상 2 관측"

deep 96d 와 sift 128d 는 *차원만 다르고 geometry 유사* (둘 다 random isotropic 근사 + distance concentration). Phase 5 §VI.3 이 명시적으로 "거리 집중 효과가 글로벌+로컬 지표 모두를 평탄화" 한다고 진단한 것처럼, 두 데이터셋의 query-side feature 통계가 유사할 가능성이 높다.

**진정한 외적 타당성 검증**: 차원 격차가 큰 (768d wikipedia, 1536d OpenAI) 또는 밀도가 낮은 (glove-100d sparse cluster) 데이터셋 필요. 768d+ 는 distance concentration 이 더 강해져 KM20 effect 가 오히려 약해질 수 있음 → negative result 가능성 존재.

**권고**: Phase 8 최종보고서 시점에 wiki 768d 필수. 중간발표에서는 "Phase 7 은 96d+128d 2 sample 외적 확장, 더 고차원은 최종보고서" 로 제한 명시.

### B.6 Reviewer Q&A 10 개 — 즉답 가능 0, 부분 답 3, 방어 불가 7

| # | 질문 | 준비 상태 |
|---|---|---|
| Q1 | Phase 7 STRAT median q_error 9.6 이 stratum LIMIT 20 / true_card artifact 아닌가? | **방어 불가** (B.1) |
| Q2 | Phase 7 actual_sel 이 0.5 가 아니라 2.4e-5 인데 "s=0.5 실험" 이라 부를 수 있나? | 부분 (honest 있음, 설명 약함) |
| Q3 | Phase 6 Step 4 는 hook_est authoritative, Phase 7 은 plan_rows authoritative 인 이유? | **방어 불가** (metric swap) |
| Q4 | Phase 4 s=0.001 SYSTEM=BERN=2.597 tie 인데, Phase 7 actual sel 2.4e-5 에서 2168× 차이 난 이유? | **방어 불가** (일관성 모순) |
| Q5 | BERN median 20810 산술적 출처? true_card 193 과 plan_rows 관계? | 방어 불가 (parquet 조회 필요) |
| Q6 | Phase 6 Step 4 Python vs Native 5× gap 이 RNG noise 로 설명되는가? Native multi-seed? | 부분 (1 seed 밖에 없음) |
| Q7 | 100 query 가 paired Wilcoxon power 에 충분한가? Power 분석? | 부분 (s=0.3 marginal 영역만) |
| Q8 | Spearman ρ 24 combo negative 인데 n=100 에서 ρ=0.2 power 0.47. n 늘리면? | 미흡 |
| Q9 | Bonferroni/FDR 보정 했나? 110 검정에서 ★ 몇 개 살아남나? | **방어 불가** (B.2) |
| Q10 | 8M k-means 가 batch 4096 iter 100 으로 5% 만 본 상태로 수렴? full-batch 비교? | 미흡 |

**Q1/Q3/Q4/Q9 는 실험 설계의 근간을 흔드는 질문이며, 이 중 하나라도 reviewer 가 발견하면 실험 전체 신뢰도 타격**.

### B.7 Phase 1~7 중 가장 약한 측정 3 개

**약점 1 (치명)**: Phase 7-1/7-2 의 `q_error` 채택 — stratum LIMIT 20 artifact 를 estimator quality 로 오독. hook_est 기반 재해석 시 STRAT 가 BERN 보다 오히려 나쁨. → B.1 참조.

**약점 2 (심각)**: Phase 6 Step 4 Native 1 seed + Python 과의 5× gap. +1.81% 가 noise range 안에 있을 가능성. → B.3 참조.

**약점 3 (중대)**: 전체 110 검정 Multiple comparison 보정 부재 + effect size CI 미보고. Bonferroni 후 Phase 6 Step 4 s=0.500 1 개만 확실히 생존. → B.2 참조.

---

## C. 세 문서 narrative 일관성 심층 리뷰 (축 C)

### C.1 핵심 수치 11 개 crosscheck — 본질적 일치 (word-for-word 수준)

| 수치 | 자문 이메일 | 중간보고서 | 슬라이드 | 일치 여부 |
|---|---|---|---|---|
| p=4.01e-05 | ✓ | ✓ | ✓ | **일치** |
| +1.81% | ✓ | ✓ | ✓ | **일치** |
| 66/100 | ✓ | ✓ ("66/100", "66/34" 두 포맷 혼재) | ✓ | 포맷만 차이 |
| 2168× | ✓ | ✓ | ✓ | **일치** |
| 409× | ✓ | ✓ | ✓ | **일치** |
| 100/100 | ✓ | ✓ | ✓ | **일치** |
| p=1.95e-18 / p<1e-18 | ✓ (두 표현 혼재) | ✓ | ✓ | 표기 혼재 |
| BERN 20810.21 vs STRAT 9.60 | ✓ | ✓ | ✓ | **일치** |
| BERN 3875.34 vs STRAT 9.48 | ✓ | ✓ | ✓ | **일치** |
| actual sel 0.000024 / 0.000128 | ✓ | ✓ | ✓ | **일치** |
| Python +0.33% vs Native +1.81% 5× gap | ✓ | 부분 (중간보고서에만) | ✗ | 슬라이드 누락 |

"양대 anchor", "단일 최강 신호", "본 연구 전체" 등 핵심 표현은 세 문서에서 **word-for-word** 일치. 한 팀이 작성한 산출물이라는 증거 강함.

### C.2 취약 1 — "3000 vs 6000" 표본 계산의 직접 모순

**문서/라인 인용**:
- 자문 이메일 line 37: "100 query × 6 selectivity × 5 seed = **3000** Adaptive Sampling 측정"
- 중간발표 Slide 5 line 85: "100 query × 6 selectivity × 5 seed = **3000**"
- 중간보고서 §2.2 line 26: "100 query × 6 selectivity × 5 seed = **3000** 측정"
- 중간보고서 §4.2 line 46: "5 seed × 2 mode × 100 query × 6 selectivity = **6000** 측정"

수학적으로 양립 가능 — 6000 은 individual measurement, 3000 은 paired 쌍. 그러나 같은 수식이 다른 값을 노출하면 지도교수 "RQ1 1차 실험 정확한 표본 크기는?" 에 두 답이 갈림.

**수정 방식 (권장)**: 모든 위치를 "6000 individual measurement (paired 3000 쌍)" 형식으로 통일. 슬라이드 공간 제약 시 "100 query × 6 sel × 5 seed × 2 mode = 6000" 압축.

### C.3 취약 2 — Design constraint 수 "4" vs "5" 의 내부 혼선 (**가장 구조적 위험**)

**문서/라인 인용**:
- 중간보고서 §5.1 line 137 RQ 진행률 표: 한 행 내 왼쪽 셀 "**4** design constraint finding" vs 오른쪽 셀 "**5** design constraint 모두 정량 확인"
- 자문 이메일 §2 line 39: "**4가지** design constraint"
- 자문 이메일 §7(c) line 112: "네 가지 모두를 드러낼지... 나머지 (iii) q-error inf, (iv) sample_size NaN, (v) Adaptive update path SIGSEGV" → **5개**
- 중간발표: 본문 2 + 부록 3 = **5** 로 일관 (Slide 6, Slide 13)

**수정 방식 (권장 — 방식 A)**: 본문 motivation 에서 "**5 design constraint** = 본문 4 (Hook trigger, plan replacement, TABLESAMPLE SYSTEM block bias, query feature 사전 식별 불가능성) + 기술 부록 1 (Adaptive SIGSEGV + q-error inf + sample_size NaN 세 하위 기술 finding)" 명시. 자문 이메일 §2 의 "4 design constraint" 와 §7(c) 의 "5 design constraint" 를 둘 다 사실로 만듦.

**중간보고서 §5.1 line 137 수정안**: "RQ1 | 5 design constraint finding (본문 4 + 부록 1) + 8 지표 negative result | ~95% | 전부 정량 확인"

### C.4 취약 3 — Phase 7 actual sel shift 해석 공통 프레임 부재

**문서/라인 인용**:
- 자문 이메일 §5 line 79: "**중요한 부수적 발견**" — **긍정** 해석
- 중간보고서 §4.7 line 112: "paired 비교의 타당성을 깨지 않으며" — **중립**
- 중간보고서 §5.2 line 149: "narrative 작성 시 honest 보고가 필요하다" — **한계** 경계
- 중간발표 Slide 10 line 230: "부수적 발견" — **긍정**
- 중간발표 Slide 10 Q&A line 242: "같은 D_target 위에서 valid" — **사후 방어**

**수정 방식 (권장)**: 6 문장 공통 프레임을 세 문서에 병합:
> "Phase 7 의 actual sel ≈ 0.0001 영역은 (a) 의도한 selectivity 0.500 에서 이동한 결과이며, (b) 1M subset 에서 계산한 D_target 을 8M/128d dataset 에 재계산 없이 적용한 방법론적 선택의 결과이고, (c) 이 영역은 Phase 6 Step 4 의 1M deep s=0.001 에서 BERN/STRAT 동률이었던 cnt-clamp fallback 영역과 구조적으로 같은 메커니즘 영역이며, (d) dataset 규모 (8M) 와 차원 (128d) 의 차이로 같은 메커니즘 영역에서 정반대 결과 (동률 vs 2168×) 가 나온 것은 예상하지 못한 부수적 발견이다. (e) paired 비교는 여전히 valid 하지만, (f) 의도된 측정 영역이 아니라는 점은 외적 타당성 한계로 기록한다."

**단 축 B.1 의 artifact 의심이 확정되면 본 프레임 자체가 무효화됨** — "2168× 는 plan tree artifact 였으며 실제로는 STRAT 가 BERN 보다 나쁨" 으로 완전 재작성 필요.

### C.5 축별 요약 채점 (Agent 3 의 5 점 척도)

| 축 | 점수 | 상태 |
|---|---:|---|
| 1. Narrative 사슬 순서/강조점 | 4.5 | 미세 조정 |
| 2. 핵심 수치 crosscheck | 3.5 | 3000 vs 6000 우선 수정 필요 |
| 3. 주장 강도 일치 | 4.0 | word-for-word 일치, 미세 약점 |
| 4. 한계/honest reporting | **2.5** | design constraint 4 vs 5 혼선 치명 |
| 5. 자문 3 항목 대응 | 4.0 | 세 문서 일관 |
| 6. 슬라이드 13 장 구조 설득력 | 4.0 | 10 분 시간 타이트 |
| **종합** | **3.75** | 90 분 편집으로 4.5 상승 가능 |

**Agent 3 의 결론**: "세 문서는 발송/제출 가능한 수준이나, 최우선 수정 3 건 처리 후 reviewer 위험 크게 감소". **단 축 B.1 의 치명 이슈가 미해결이면 본 결론은 효력 없음**.

---

## D. 통합 판정과 긴급 액션 로드맵 (D-13)

### D.1 발송/제출 가능성 판정

| 산출물 | 현재 상태 판정 | 조건부 발송 가능 여부 |
|---|---|---|
| 자문 이메일 | **보류 권고** | Phase 7 artifact 검증 전까지 발송 금지 권장. 단 본 딥리뷰를 첨부하지 않고 현재 상태로 발송 시 멘토 회신이 "2168× 결과를 전제로 한 판정" 이 되어 추후 Phase 7 철회 시 자문 결과 자체가 무효화됨. |
| 중간보고서 v1 | **조건부 가능** | 긴급도 2 (4 vs 5, 3000 vs 6000) 수정 후 v1.1 로 팀 회람. Phase 7 artifact 검증 결과에 따라 v2 구조 재편 여부 결정. |
| 중간발표 슬라이드 | **조건부 가능** | Phase 7 관련 Slide 10 를 잠정 보류하고, Phase 6 Step 4 중심으로 narrative 를 임시 재구성한 버전을 4/22 팀 리뷰 전에 준비. |

### D.2 긴급 액션 리스트 (우선순위 순, D-13)

**D+0 (오늘, 4/15 오후)** — 🚨 최우선 2 건
1. Phase 7 artifact 검증: `cache/rq1/phase7_8m_strat.parquet` 의 `plan_rows` 열 직접 조회 → 대부분 20 근처인지 확인 (20 분)
2. `phase7_*_paired.json` vs `phase7_*_paired_qerror.json` 직접 대조: BERN/STRAT 방향 반전 확인 (15 분)

**D+1 (4/16)** — 시나리오 분기
3. artifact 확정 시: Phase 7 narrative 철회 + 중간발표 anchor 를 Phase 6 Step 4 단일로 축소. 3 산출물의 Phase 7 관련 섹션 전면 재작성.
4. artifact 반증 시: Phase 6 Step 4 의 metric 결정 재검토 (hook_est vs plan_rows 어느 쪽이 맞는지 native EXPLAIN 직접 분석). Phase 6 Step 4 결과도 영향 받을 가능성.

**D+2 (4/17)** — narrative 통일
5. Design constraint 수 "4 vs 5" 통일 (방식 A: 본문 4 + 부록 1 = 5 명시)
6. "3000 vs 6000" 표본 계산 통일 (6000 individual measurement + paired 3000 쌍)
7. Phase 7 actual sel shift 해석 공통 프레임 (artifact 검증 결과에 따라)

**D+3 (4/18)** — 통계 보강
8. 모든 paired 테이블에 Bonferroni `p_bonf` 열 추가
9. 모든 ★ signal 에 Cohen d + bootstrap 95% CI 병기
10. Phase 7 p=1.95e-18 철회 → `n_better` 또는 `binom_test` 로 대체

**D+4~5 (4/19~20)** — 재측정
11. Phase 6 Step 4 Native 3 seed 재측정 (`SELECT setseed()`) → effect size 분포 + CI 확보
12. Python counterfactual 을 Native 설계 (stratum LIMIT 20 상한 + query 간 새 sample) 로 재측정 → 5× gap 원인 분리

**D+6~7 (4/21~22)** — 중간보고서 v2 + 자문 이메일 재검토
13. 중간보고서 v2 편집 (긴급도 1 + 2 반영, 약 2~3 시간)
14. 자문 이메일 v2 작성 (Phase 7 섹션 재작성 + 자문 (c) 재편성 + fallback 1 문장 추가)
15. 자문 이메일 발송 (또는 검증 결과에 따라 "수정 재발송" 경로)

**D+8 (4/22 화)** — 1 차 팀 리뷰

**D+9~10 (4/23~24)** — 자문 회신 반영 + 슬라이드 수정

**D+11 (4/24 목)** — 2 차 팀 리뷰 + 1 차 리허설

**D+12 (4/25 금)** — 슬라이드 PPT 변환

**D+13 (4/26 토)** — 2 차 리허설 + 중간보고서 최종

**D+14~15 (4/27 일 ~ 4/28 화)** — 발표 준비 + ★ **4/28 중간발표**

### D.3 시나리오 분기 트리

```
D+0 Phase 7 artifact 검증
├─ [확정] Phase 7 은 artifact
│    ├─ 중간발표 anchor = Phase 6 Step 4 s=0.500 단일
│    ├─ Phase 7 narrative 철회 ("2168× 양대 anchor" 주장 철회)
│    ├─ Phase 7 을 "8M/sift fallback 영역 재현 실패 + 구조적 한계 발견" 으로 재분류
│    ├─ 3 산출물 Phase 7 섹션 전면 재작성
│    └─ 자문 이메일 v2 로 발송 (본 딥리뷰 요약 첨부)
│
├─ [반증] plan_rows 가 20 이 아님
│    ├─ Phase 6 Step 4 의 hook_est authoritative 결정 재검토
│    ├─ Phase 6 Step 4 정확 측정치 재확인 (native EXPLAIN 직접 분석)
│    ├─ 가능성 A: Phase 6 Step 4 도 결과가 바뀜 → 두 Phase 모두 재분석
│    └─ 가능성 B: Phase 7 의 metric 은 맞고, Phase 6 만 hook_est 고수 → 둘 다 유효, 다만 metric swap 은 여전히 설명 필요
│
└─ [불확정] 검증 결과가 중간 영역
     └─ 보수 경로: 중간발표 narrative 는 Phase 6 Step 4 anchor 중심으로 먼저 재구성, Phase 7 은 "추가 검증 중" 로 임시 분류
```

---

## E. 3 축 agent 원본 리뷰 요약과 본 문서의 역할

본 딥리뷰는 3 개 독립 agent 를 병렬로 dispatch 해 얻은 결과를 본 문서에서 긴급도 기준으로 재배치한 것이다. 각 agent 는 서로의 결과를 공유하지 않은 상태에서 독립적으로 리뷰했기 때문에 세 관점이 서로의 blind spot 을 메운다.

- **축 A (연구 계획 v4)**: Agent 1 — v4 의 구조적 정합성 확인. v3 → v4 변경 사항의 학술 정당성 개별 평가. 판정: 중간보고서 1 차 초안으로 직접 사용 가능, 미세 조정만 필요. 가장 날카로운 발견: 자문 (c) 의 실효성 부족 + §6.5 복원 권고.
- **축 B (Phase 1~7 실험)**: Agent 2 — 측정 설계 + 통계 엄밀성 + 재현성 + 외적 타당성. **본 리뷰의 가장 치명적 발견이 본 축에서 나왔음**. Phase 7 의 `q_error = 9.6` 이 plan tree artifact 일 가능성은 본 문서 §B.1 에서 5 증거 (A~E) 로 구성됨. 본 발견은 Agent 1 과 Agent 3 은 포착하지 못했는데, 그 이유는 두 agent 는 *narrative 일관성* 과 *연구 계획 구조* 를 각각 검토했고, Phase 7 결과의 *수치 해석 층위* 는 측정 코드와 JSON 결과 직접 파싱이 필요한 영역이기 때문.
- **축 C (세 문서 narrative)**: Agent 3 — 자문 이메일 + 중간보고서 + 슬라이드 사이의 수치 crosscheck + 주장 강도 일치 + honest reporting 솔직함. 판정: 본질적 일관성 확보 (word-for-word 수준), 취약 3 지점은 90 분 편집으로 수정 가능. 가장 날카로운 발견: Design constraint 수 "4 vs 5" 의 중간보고서 §5.1 line 137 내 한 행 엇갈림.

**본 문서의 역할**: 3 agent 결과의 긴급도 재정렬 + 통합 액션 로드맵 + 시나리오 분기 트리 제시. 원본 agent 응답의 세부 분석 (특히 Agent 2 의 110 검정 Bonferroni 분석 + Agent 3 의 라인 번호 crosscheck 세부) 는 본 문서에 일부만 인용되었으며, 필요 시 원본 응답을 재참조 (agentId 로 SendMessage 재개 가능).

---

## 종결

본 딥리뷰의 한 줄 요약은 다음과 같다.

> **v4 연구 계획과 세 문서 narrative 는 구조적으로 건전하나, Phase 7 의 "2168× 양대 anchor" 주장이 plan tree artifact 의심으로 긴급 검증이 필요하며, 본 검증 결과가 중간발표 narrative 의 핵심 분기점을 결정한다.**

사용자는 본 문서 §D.2 의 D+0 액션 2 건 (parquet `plan_rows` 열 조회 + `paired.json` vs `paired_qerror.json` 대조) 을 **자문 이메일 발송 전에** 수행하는 것이 가장 안전한 경로다. 본 2 건의 검증은 약 35 분 소요되며, 검증 결과에 따라 시나리오 분기가 결정된다. 검증 없이 현재 상태로 자문 이메일을 발송하면 멘토 회신이 잘못된 전제 위에서 내려질 리스크가 있다.

본 딥리뷰 문서는 2026-04-15 10:30 KST 에 작성되었으며, 사용자가 긴급 액션 결과를 반영해 업데이트 (또는 별도 v2 작성) 할 수 있는 살아있는 문서다. 중간발표까지 D-13.
