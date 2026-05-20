# ε 축 검증 — chapter shift 후 cross-reference + figure rename + md↔PDF↔DOCX 정합 (20 항목)

> 검증 대상: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.{md,pdf,docx}`
> 직전 본 (chapter shift 전): `submission/_drafts/archive/속도는벡터_6_11_최종보고서_20260519_135021.md` (453 line, Ch.1~7)
> 신본 (chapter shift 후): 579 line, Ch.1~8 (§5 신설로 chapter 1 추가)
> 검증 시각: 2026-05-20 KST
> 검증 mode: read-only — 본 md만 작성, 보고서/figure 수정 없음

---

## VERDICT: **FAIL**

20 항목 중 **PASS 14건 · WARN 3건 · FAIL 3건**.

치명적 결함 3건이 발견되었다 — 모두 chapter shift 후 cross-reference 갱신 누락. 본문 산문의 §6.1 표 cross-ref 1건, figure PNG 내부 embedded title 2건. 본 보고서 6/11 제출 전에 반드시 수정 필요.

| severity | 건수 | 항목 |
|---|---:|---|
| critical (FAIL) | 3 | §6.2 line 483 "5.1의 표" cross-ref 오류 · fig6_1 PNG 내부 title "그림 5-1" stale · fig7_1 PNG 내부 title "그림 6-1" stale |
| major (WARN) | 3 | PDF 페이지 수 task brief 44p vs 실제 46p discrepancy · 본문 "§5.5의 이론적 토대" (line 555 참고문헌 [2] Cochran) — 신본 §5.5는 Wilcoxon이며 Cochran은 §2.3에서 인용 · 도표 caption 표 6-1 (line 545) 위치는 §7.2 안인데 "표 6-X" 번호 규칙상 §7-Y 가 맞음 (장 번호 규칙 violation) |
| minor (PASS- ish) | 14 | 나머지 cross-ref 모두 정합 |

---

## §1 TOC ↔ 본문 chapter 정합 (2 항목)

### 항목 1: TOC 8 chapter 번호·제목·line range

| 번호 | TOC 제목 (line 12-19) | 본문 heading (line) | 정합 |
|---|---|---|:---:|
| 1 | 연구 주제·목표 및 개요 | `## 1. 연구 주제·목표 및 개요` (line 23) | ○ |
| 2 | 연구의 필요성 | `## 2. 연구의 필요성` (line 51) | ○ |
| 3 | 연구 내용·방법 | `## 3. 연구 내용·방법` (line 96) | ○ |
| 4 | 분석·실험 결과 — 오프라인 추정 검증 | `## 4. 분석·실험 결과` (line 199) | △ 부분 정합 (TOC suffix "— 오프라인 추정 검증" 본문 heading에 없음) |
| 5 | 엔진 적용 검증 — 실행 계획·end-to-end latency | `## 5. 엔진 적용 검증 — 실행 계획·end-to-end latency` (line 336) | ○ |
| 6 | 제안 모델·결론·향후 작업 | `## 6. 제안 모델·결론·향후 작업` (line 453) | ○ |
| 7 | 진행 및 역할 분담 | `## 7. 진행 및 역할 분담` (line 511) | ○ |
| 8 | 참고문헌 | `## 8. 참고문헌` (line 551) | ○ |

**VERDICT**: PASS — 8 chapter 번호와 제목이 본문과 정합. TOC §4 제목에 "— 오프라인 추정 검증" suffix가 있으나 본문 heading은 없다 — minor 표기 비대칭이며 의미 정합은 유지된다.

### 항목 2: TOC §X.Y sub-section 명시

TOC 는 chapter level (1~8) 까지만 나열되고 §X.Y sub-section은 명시되지 않는다. 본문에서는 §1.1~§7.2 (총 31 sub-section)가 모두 정합한다.

**VERDICT**: PASS — TOC가 chapter level only design이며 sub-section 별도 list가 없으므로 정합성 위반 아님.

---

## §2 chapter shift 후 cross-reference 정합 (4 항목)

### 항목 3: §6.4 향후 작업 4갈래 ↔ §5 cross-ref

§6.4 (line 497-507) 의 네 갈래는:
- 첫째 (line 501): "Ch.5의 본 검증은 DEEP·sf=10·sel=0.001의 12 cell — Phase 0의 사전 탐색이 plan 변화의 핵심 cell로 분류한 core 4 cell × 질의 벡터 3개 — 에 한정되었다" → §5.6 셋째·넷째 한계 (line 443, 445) carry. **정합**
- 둘째 (line 503): "Ch.5의 짝지은 Wilcoxon 검정은 p_holm으로 유의성을 보고하고 plan 회복 매트릭스로 cell 수준의 robustness를 정리하였으나" → §5.5의 검정 한계 carry. **정합**
- 셋째 (line 505): "박광현 교수님이 제안한 4 엔진 통합 개념 증명" — §5에 cross-ref 없음 (별도 신규 과제). 정합성 위반 아님.
- 넷째 (line 507): 측정 공간 확장 — §5.6 다섯째 한계 (plan signature precision) 보다는 §3.5 concat dataset 확장 carry. 정합성 위반 아님.

§5.6 한계 5건 중 첫째 (베이스라인 클램프) 와 둘째 (Q3 정확도 미달) 는 §6.4 향후 작업에서 carry 되지 않는다 — 이는 측정 노출이지 향후 과제가 아니므로 의도된 비대칭이다.

**VERDICT**: PASS — §6.4 4갈래가 §5 한계 5건 중 carry-over 가능한 셋째·넷째·다섯째를 모두 흡수.

### 항목 4: §7 진행 및 역할 분담의 Ch.4·Ch.5 분담 명시

§7.2 (line 535-547) 의 분담 표:

| 팀원 | 담당 장 | 본문 검증 |
|---|---|---|
| 박세은 (팀장) | Ch.1 · Ch.6 · Ch.7 + 전체 통합 | ○ shift 후 정합 (구 Ch.5/Ch.6 → 신 Ch.6/Ch.7) |
| 이동욱 | Ch.2 | ○ |
| 강재현 | Ch.3 | ○ |
| 조현빈 | Ch.4 · Ch.5 | ○ Ch.5 = 엔진 적용 검증 신본 — 조현빈 추가 분담 명시 |
| 공동 | Ch.8 | ○ shift 후 신본 (구 Ch.7 → 신 Ch.8) |

산문 line 547 "조현빈은 ... Ch.4와 그 검증된 추정치를 실제 PostgreSQL에 주입해 실행 계획과 end-to-end latency 효과를 측정한 엔진 적용 검증 Ch.5를 집필하였다" — 신본 Ch.5 분담 명시 정합.

**VERDICT**: PASS — Ch.5 신설에 따른 조현빈의 Ch.4+Ch.5 분담이 본문과 표 양쪽에서 명시.

### 항목 5: §3 결합 추정값·CaseB·est_b1·est_method 정의 → §5 carry 정합

§3.3 (line 127-145) 의 세 mode 정의:
- B1: `est = est_b1`
- CaseA: `est = est_method`
- CaseB: `est_final = (est_b1 + est_method) / 2.0`

§5.1 (line 342, 344) carry:
- "Ch.4에서 1,508건의 오프라인 측정으로 검증된 결합 추정값(est_b1과 method 추정값의 산술 평균)" → §3.3 정합
- "베이스라인 추정(B1, est_b1)은 Ch.3의 논문 그대로의 무작위 베르누이 표본 추출이 산출한 카디널리티 추정값을 주입한다" → §3.3 정합
- "결합(CaseB)은 본 연구가 권장하는 13종 강한 method 각각에 대해 est_b1과 method 추정값의 산술 평균을 주입한다" → §3.3 정합

**VERDICT**: PASS — §3.3의 세 mode 정의가 §5.1에서 변형 없이 carry.

### 항목 6: §4 89.1%·−4.38% 정본 수치 → §5.1 intro 산문 cross-ref

§4.1 (line 209-213): "CaseB better (Δ% < 0) | 1,344 / 1,508 = 89.1%" · "중앙값 Δ% | −4.38%"
§5 intro (line 338): "Ch.4의 1,508건 측정은 분포 인지 표본 선택의 결합 방식이 베르누이 대조군보다 카디널리티 추정의 Q-error를 약 9할에서 더 낮춘다는 사실을 정량적으로 보여 주었다"
§5.4 마지막 (line 406): "§4의 오프라인 측정이 보여 준 추정 정확도 우월(89.1% better)이 plan 회복 robustness(94.9% align)로 변환된 것이며"

**VERDICT**: PASS — §4 정본 수치 89.1%·−4.38% 가 §5.1 intro 와 §5.4 마지막에 정확히 carry.

---

## §3 §5 내부 자연 흐름 (5 항목)

### 항목 7: §5.1 intro → §5.2 측정 설계 자연 흐름

§5.1 마지막 (line 346): "이 둘에 대한 답을 본 장은 12 cell × 16 variant × 15 timed rep 의 총 2,880회 측정으로 제시한다."
§5.2 첫 줄 (line 350): "엔진 적용 검증의 측정 단위(cell)는 TPC-H의 네 분석 쿼리..."

**VERDICT**: PASS — §5.1 마지막에서 측정 평면 (12×16×15) 미리 노출 → §5.2에서 측정 단위 정의로 자연 진입.

### 항목 8: §5.2 측정 설계의 "core 4 cell" 분류 → §5.6 honest 한계 셋째 (sel=0.001 한정)

§5.2 (line 350): "Phase 0의 사전 탐색(prescan)에서 selectivity 0.001 조건에서 기본엔진과 베이스라인·정답의 plan signature가 서로 다르게 나타나 추정치가 실제로 plan을 흔드는 핵심 cell로 분류된 네 쿼리다"
§5.6 셋째 (line 443): "Phase 0의 사전 탐색은 sel 0.001·0.01·0.1의 세 단계와 4 쿼리를 교차한 12 cell을 본 연구의 측정 모집단으로 두고, 그 가운데 추정치 변동이 실제로 plan을 흔드는 cell을 core 4(sel=0.001)... 로 분류하였다"

**VERDICT**: PASS — core 4 cell 분류 정의가 §5.2 와 §5.6 양쪽에서 정합.

### 항목 9: §5.3 표 5-1 → §5.4 "다음 절(§5.4)" cross-ref

§5.3 line 377: "표의 가장 오른쪽 열은 베이스라인 추정값이 만든 plan이 정답 plan과 동일한지의 표시이며, 이 열의 해석은 다음 절(§5.4)에서 자세히 다룬다."
§5.4 (line 387~410) 의 표 5-2 plan 회복 매트릭스에서 그 해석 carry.

**VERDICT**: PASS — §5.3 → §5.4 explicit cross-ref 명시.

### 항목 10: §5.4 표 5-2 → §5.5 paired Wilcoxon 자연 흐름

§5.4 마지막 line 406: "§4의 오프라인 측정이 보여 준 추정 정확도 우월(89.1% better)이 plan 회복 robustness(94.9% align)로 변환된 것이며, 이것이 본 연구가 결합 방식을 권장하는 plan 측면의 근거다."
§5.5 첫 줄 line 414: "§5.3의 latency 매트릭스와 §5.4의 plan 회복 매트릭스에 나타난 두 사실을 통계적으로 확정하기 위해, 본 연구는 각 cell·variant의 15회 측정값을 짝지은 Wilcoxon 부호순위 검정..."

**VERDICT**: PASS — §5.4 → §5.5 자연 흐름 (plan 회복 robustness → 통계적 확정).

### 항목 11: §5.6 한계 5건 ↔ §6.4 향후 작업 4갈래 carry

| §5.6 한계 | §6.4 carry | 정합 |
|---|---|:---:|
| 첫째 베이스라인 클램프 노출 (line 439) | carry X (측정 노출, 향후 과제 아님) | ○ 의도된 비대칭 |
| 둘째 Q3에서만 정확도 미달 (line 441) | carry X (cell-specific 노출) | ○ 의도된 비대칭 |
| 셋째 sel=0.001 핵심 cell 한정 (line 443) | §6.4 첫째 carry-over (line 501) | ○ |
| 넷째 DEEP·sf=10 단일 데이터셋 (line 445) | §6.4 첫째에서 명시 "SIFT·SSN·다중 벡터 데이터셋과 sf=1·sf=100" (line 501) | ○ |
| 다섯째 plan signature 정밀도 (line 447) | §6.4 둘째 "통계 검증 도구의 확장" 로 우회 carry (line 503) | △ direct carry는 아니나 의미상 연결 |

**VERDICT**: PASS — 5개 한계 중 셋째·넷째가 직접 §6.4 첫째로 carry, 다섯째는 §6.4 둘째 통계 검증 확장으로 우회 carry, 첫째·둘째는 측정 노출로 carry 의도 없음.

---

## §4 figure inclusion 정합 (5 항목)

### 항목 12: §5.3 figure path "fig5_2_speedup_heatmap.png"

md line 383: `![그림 5-1](../../experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.png)`
파일 존재 확인: `/Users/hyunbin/Capstone/experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.png` (131,412 bytes, 2026-05-20 09:49)
PDF 페이지 32: 정상 inclusion (speedup heatmap 시각 검증 완료, x축 variant 14종 · y축 12 cell)

**VERDICT**: PASS — path 정합 + PDF inclusion 정상.

### 항목 13: §5.4 figure path "fig5_3_plan_recovery.png"

md line 408: `![그림 5-2](../../experiments/figures/보고서_6_11/fig5_3_plan_recovery.png)`
파일 존재 확인: 93,787 bytes, 2026-05-20 09:49
PDF 페이지 34: 정상 inclusion (plan recovery matrix)

★ **이슈**: PDF page 34의 plan recovery 매트릭스 figure title이 한글 깨짐 "□□ □□ □□ — oracle □ □□ plan □□" (제목·legend "□□"는 한글 글꼴 미반영) → minor cosmetic 문제 (caption 본문은 정상). figure 내부 텍스트 인코딩 이슈로 추정.

**VERDICT**: WARN — path 정합 · PDF inclusion 정상이나 PNG 내부 한글 일부 garbled.

### 항목 14: §5.5 figure path "fig5_4_wilcoxon_significance.png"

md line 431: `![그림 5-3](../../experiments/figures/보고서_6_11/fig5_4_wilcoxon_significance.png)`
파일 존재 확인: 108,792 bytes, 2026-05-20 09:49
PDF 페이지 36: 정상 inclusion (Wilcoxon significance heatmap)

★ **이슈**: PDF page 36 figure title에 "B1 vs □-B1 variant — paired Wilcoxon p_holm □ -log10" — "□" 가 garbled (non-B1 표기 깨짐). minor cosmetic.

**VERDICT**: WARN — path 정합 · 동일 cosmetic 깨짐.

### 항목 15: §6.1 figure rename "fig6_1_dynamic_method_selection.png"

md line 475: `![그림 6-1](../../experiments/figures/보고서_6_11/fig6_1_dynamic_method_selection.png)` — markdown caption 정합.
PNG 파일: `/Users/hyunbin/Capstone/experiments/figures/보고서_6_11/fig6_1_dynamic_method_selection.png` (89,832 bytes, **2026-05-19 13:11** — chapter shift 전 생성)

★★★ **CRITICAL ISSUE**: PDF page 40 inclusion 시 PNG 내부 embedded title "그림 5-1. 동적 method 선택 4단계 흐름도" 로 stale rendering. 파일 rename 은 됐으나 PNG 내부 title regeneration 누락. md caption "그림 6-1" vs PNG embedded title "그림 5-1" 불일치 → **독자 혼란 직접 유발**.

**VERDICT**: **FAIL** — markdown path/caption 정합이나 PNG 내부 embedded title 이 chapter shift 전 stale ("그림 5-1" 잔존).

### 항목 16: §7.1 figure rename "fig7_1_gantt.png"

md line 525: `![그림 7-1](../../experiments/figures/보고서_6_11/fig7_1_gantt.png)` — markdown caption 정합.
PNG 파일: `/Users/hyunbin/Capstone/experiments/figures/보고서_6_11/fig7_1_gantt.png` (78,473 bytes, **2026-05-19 13:11** — chapter shift 전 생성)

★★★ **CRITICAL ISSUE**: PDF page 44 inclusion 시 PNG 내부 embedded title "그림 6-1. 캡스톤 연구 진행 일정" 로 stale. md caption "그림 7-1" vs PNG embedded title "그림 6-1" 불일치.

**VERDICT**: **FAIL** — 동일 패턴 (figure rename 됐으나 PNG 내부 title regeneration 누락).

---

## §5 md ↔ PDF ↔ DOCX 동기화 (4 항목)

### 항목 17: PDF 페이지 수 검증

task brief 명시: "PDF 44p"
실제 PDF: **46p** (페이지 footer "1/46"~"46/46" 확인)

discrepancy 2p — 본문 chapter shift 후 §5 신설 약 7p 분량이 추가되었으나 task brief가 stale.

**VERDICT**: WARN — task brief 의 44p stale, 실제 46p 가 본문에 정합 (Ch.1~8 + 14 figure 모두 포함). 보고서 자체는 정상.

### 항목 18: DOCX 동기화

DOCX 검증: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.docx` (78,578 bytes)
- 8 chapter 모두 존재 (`## 1.`~`## 8.`)
- `## 5. 엔진 적용 검증 — 실행 계획·end-to-end latency` heading 존재 (paragraph 132)
- 6.1~6.4, 7.1~7.2 모두 정합
- 14 표 (tables) 존재 (md 의 표 5-1/5-2/5-3/6-1 + 본문 inline 표 모두 carry)

**VERDICT**: PASS — DOCX 가 md 와 chapter 동기화. 단, 78KB로 PDF 의 4MB 대비 figure 미포함 (table+text only) — 정상 docx 변환 결과.

### 항목 19: PDF chapter heading 번호 shift 후 정합

PDF 페이지 별 chapter heading 시각 검증:
- p2 "1. 연구 주제·목표 및 개요" ○
- (Ch.2~4 page 검증 skip — 핵심은 신설 Ch.5)
- p29 "5. 엔진 적용 검증 — 실행 계획·end-to-end latency" ○ (shift 정합)
- p38 "6. 제안 모델·결론·향후 작업" ○ (구 §5 → 신 §6)
- p43 "7. 진행 및 역할 분담" ○ (구 §6 → 신 §7)
- p46 "8. 참고문헌" ○ (구 §7 → 신 §8)

**VERDICT**: PASS — PDF chapter heading shift 정합.

### 항목 20: PDF figure inclusion 정상

PDF 의 14 figure (그림 1-1 ~ 그림 7-1) 모두 inclusion 확인 — 해상도·크기·caption 모두 정상. 단, 항목 15·16 (fig6_1, fig7_1) PNG 내부 stale title 이슈 존재.

추가 minor: 항목 13·14 (fig5_3, fig5_4) PDF 페이지 figure 내부 한글 일부 garbled — figure rendering 시 한글 글꼴 누락 추정.

**VERDICT**: WARN — 14 figure 모두 inclusion 되었으나 4 figure 내부 텍스트 이슈 (2 stale title + 2 cosmetic garble).

---

## §6 발견 issue catalog (severity 별)

### CRITICAL (FAIL) — 보고서 6/11 제출 전 반드시 fix

**C-1.** `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.md` line 483, §6.2 권장 첫 단락:
> "첫째는 Type별 강한 method의 자동 선택이다. 데이터셋이 들어오면 그 규모·구조·차원으로 Type을 판별하고, **5.1의 표**에 따라 해당 Type에 견고하게 우월한 강한 method를 자동으로 고른다."

문제: "5.1의 표" 는 chapter shift 전 §5.1 (= 구 제안 모델 = 신 §6.1) 의 Type별 권장 method 표를 가리켰다. shift 후에는 §6.1 의 표 (line 466-471) 가 정답이며 §5.1 (도입 — 추정 정확도에서 실행 시간까지) 에는 해당 표가 없다.

수정: "5.1의 표" → "6.1의 표".

**C-2.** `experiments/figures/보고서_6_11/fig6_1_dynamic_method_selection.png` PNG 내부 embedded title 이 "그림 5-1. 동적 method 선택 4단계 흐름도" 로 stale. PDF 페이지 40 에 그대로 노출되어 독자 입장에서 figure 번호 모순 (caption "그림 6-1" vs 이미지 내부 title "그림 5-1").

수정: 해당 figure 를 재렌더링하여 내부 title "그림 6-1" 로 갱신, 또는 제목을 PNG 외부로 빼고 markdown caption 으로만 운용.

**C-3.** `experiments/figures/보고서_6_11/fig7_1_gantt.png` PNG 내부 embedded title 이 "그림 6-1. 캡스톤 연구 진행 일정" 로 stale. PDF 페이지 44 노출.

수정: 동일 패턴 — 내부 title "그림 7-1" 로 재렌더링.

### MAJOR (WARN) — 정합성 또는 가독성에 영향

**M-1.** task brief 의 "PDF 44p" stale — 실제 PDF 46p. 보고서 자체 정합이나 인계 문서 갱신 필요.

**M-2.** `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.md` line 555, §8 참고문헌 [2] Cochran 항목:
> "Cochran, W. G. *Sampling Techniques*, 3rd ed. ... 본 연구의 분포 인지 층화 방식은 **§5.5**의 이론적 토대 위에 있다."

문제: "§5.5의 이론적 토대" 는 Cochran 1977 의 chapter 5 §5.5 (즉 책 안의 §5.5) 를 가리키는 것으로 보이나, 신본의 §5.5 (paired Wilcoxon 통계 검증) 와 표기 충돌 가능 — 독자가 "신본 §5.5" 로 오독할 수 있다. 본문 line 86 에서 "Cochran 1977 §5.5" 라고 일관되게 표기되어 있어 이 §8 항목도 "Cochran §5.5" 로 명시화 권고.

수정: line 555 의 "§5.5의 이론적 토대" → "Cochran §5.5의 이론적 토대" 또는 "Cochran 1977 §5.5".

**M-3.** `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.md` line 545, §7.2 의 분담 표 caption:
> "**표 6-1.** 최종 보고서 장별 집필 분담."

문제: 표는 §7.2 (Ch.7) 안에 위치하므로 "표 7-1" 이 chapter 번호 규칙상 맞다. 신본의 다른 표는 모두 "표 5-1/5-2/5-3" (Ch.5 안) 으로 chapter 번호와 일치한다.

수정: "표 6-1." → "표 7-1.".

### MINOR — 정합성 위반 아님, 보고용

- TOC §4 제목 "분석·실험 결과 — 오프라인 추정 검증" suffix 가 본문 heading (line 199) "## 4. 분석·실험 결과" 에 없음 → 의도된 TOC 확장 표기로 추정. 미수정 가능.
- PDF page 34·36 의 figure 내부 한글 텍스트 일부 (legend·title) garbled ("□") — figure rendering 한글 글꼴 미설정. cosmetic 문제로 markdown 및 PDF 본문 산문은 정상.

---

## §7 fix 권고 (우선순위)

### Priority 1 (P1) — 보고서 정합성 회복 (필수)

| ID | 파일 | line | 정정 |
|---|---|---:|---|
| C-1 | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.md` | 483 | "5.1의 표" → "6.1의 표" (1-char edit, 1 글자 fix) |

### Priority 2 (P2) — figure 내부 title regeneration

| ID | 파일 | 작업 |
|---|---|---|
| C-2 | `experiments/figures/보고서_6_11/fig6_1_dynamic_method_selection.png` (.pdf 동일) | 내부 title "그림 5-1" → "그림 6-1" 로 재렌더링 |
| C-3 | `experiments/figures/보고서_6_11/fig7_1_gantt.png` (.pdf 동일) | 내부 title "그림 6-1" → "그림 7-1" 로 재렌더링 |

권장 접근: figure rendering script (`_internal/scripts/` 또는 `experiments/code/`) 의 title 인자 변경 후 재실행. md→PDF 변환은 figure 파일만 갱신하면 자동 재반영.

### Priority 3 (P3) — 정합성 추가 정정

| ID | 파일 | line | 정정 |
|---|---|---:|---|
| M-2 | 동일 md | 555 | "§5.5의 이론적 토대" → "Cochran §5.5의 이론적 토대" |
| M-3 | 동일 md | 545 | "**표 6-1.**" → "**표 7-1.**" |

### Priority 4 (P4) — cosmetic 정리

- fig5_3, fig5_4 figure 내부 한글 글꼴 설정 (한글 깨짐) — matplotlib `font.family` 설정 권장. P1~P3 fix 후 여유 시 처리.
- task brief "PDF 44p" → "46p" — handoff 문서 인계 시 갱신.

---

## 결론

신본 6/11 보고서의 chapter shift (§5 신설 + §5→§6/§6→§7/§7→§8) 와 figure rename (fig5_1→fig6_1, fig6_1→fig7_1) 은 markdown level 에서는 거의 모두 정합하며, TOC·body cross-reference·§5 내부 흐름·figure inclusion path·docx/PDF 동기화 가 정상이다.

다만 **3건의 critical 정합성 결함** 이 남아 있다:
1. **C-1** §6.2 line 483 "5.1의 표" — 신본에서는 "6.1의 표" 가 정답이며, shift 시 미갱신.
2. **C-2** fig6_1_dynamic_method_selection.png 내부 embedded title 이 "그림 5-1" stale — PNG 파일 rename 은 됐으나 figure rendering 갱신 누락.
3. **C-3** fig7_1_gantt.png 도 동일 패턴, 내부 title "그림 6-1" stale.

6/11 최종 보고서 제출 전에 C-1 (1 char edit) 과 C-2/C-3 (figure 2종 재렌더링) 을 반드시 처리하고, 추가로 M-2/M-3 정합성 정정도 함께 반영하는 것을 권장한다.
