# handoff 20260525 00:13 — 변천사 제거 · 156 plan 상세 표 · storyline v4 · Claude Design prompt + Nano Banana Pro brief · PDF 4 신본 · Phase 4 전권 위임

> 직전 handoff (`handoff_20260524_233327_methodNamingAudit완료_정정반영_PDF4종.md`) → 본 문서. self-contained 0% loss 인계.
>
> **★ 핵심 한 줄**: 본 세션에서 (1) **변천사·메커니즘 규명 변경 framing 27 곳 제거** (사용자 5/25 00:00 명시: "수정이 어떻게 되었든 간에 최종 결과만 중요"), (2) **156 plan (12 cell × 13 결합 method) B1 vs CaseB 완전 상세 비교 표 추출·문서화** (extract_156plan_table.py 60 줄, CaseB oracle 회복 148/156 = 94.9%), (3) **자료 B v3 + storyline v4 + Claude Design prompt + Nano Banana Pro brief 4 신본 + PDF** 완성, (4) **plan_diff/latency saturate 통찰을 §5.10·§7.4·§8.1 + slide 11 Group A 에 Future Work 로 carry** (사용자 5/25 00:45 통찰 → 5/25 01:00 결정 "나중에 더 확인해봐야 하는 부분으로 전달"). **다음 세션 = Phase 4 — Claude Code 가 직접 Claude Design 12 slide + Nano Banana Pro 14 자산 시안 생성** (전권 위임 · 사용자 5/25 01:00 명시). 백지 PPT 합성 부분은 사용자가 storyline 반영 carry → Phase 4 에서 제외. **5/26 23:59 LearnUs deck 마감 약 47 시간 남음**.

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계
- **★ 직전 handoff (archive)**: `_internal/handoff/archive/handoff_20260524_233327_methodNamingAudit완료_정정반영_PDF4종.md` (method 명칭 audit 완료 + 정정 8 + paradigm 재분류 carry)
- **★ 자료 B v3 (채림님 전달용 신본, 변천사 제거 + 156 plan §5 신규)**: `submission/_drafts/속도는벡터_채림님_전달용_구체적_데이터_v3_20260525_001258.{md,pdf}` (pdf 984 KB · 9 section)
- **★ storyline v4 (5/27·29 발표, 변천사 제거)**: `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.{md,pdf}` (pdf 1.48 MB · 12 slide × 텍스트·시각·발표자 narrative)
- **★ Claude Design prompt v4**: `submission/_drafts/속도는벡터_v4_ClaudeDesign_prompt_20260525_001258.{md,pdf}` (pdf 783 KB · 12 slide layout 지시)
- **★ Nano Banana Pro brief v4**: `submission/_drafts/속도는벡터_v4_NanoBananaPro_brief_20260525_001258.{md,pdf}` (pdf 705 KB · 자산 14 장 brief)
- **★ 156 plan 표 raw**: `_internal/cache/rq3/latency/phase2/table_156plan_20260525_001258.{csv,md}` (12 cell × 13 method = 156 row)
- **★ 156 plan 추출 script**: `_internal/scripts/extract_156plan_table.py` (60 줄, analyze_latency.py 함수 carry)
- **★ 보고서 6/11 정본 (직전 세션 carry, 변경 X)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (pdf 1.91 MB) — 본 세션은 보고서 미수정 (보고서 내부 §4.7 명칭 정정·§4.2.3·§4.6.1 BLOCKER E reference 등 변천사 영역은 보고서 안에 carry, 외부 발표·자료에는 반영 X 룰)

## 1. ★★★ 본 세션 완료 작업 (한 줄 요약)

| Phase | 작업 | 산출 | 상태 |
|:--:|---|---|:--:|
| 1 | 156 plan latency 추출 script (analyze_latency.py 함수 차용) | `extract_156plan_table.py` 60 줄 · csv·md 2 파일 산출 | ✅ |
| 2 | 자료 B v3 재구성 (변천사 9 곳 제거 + §5 NEW 156 plan 상세 표) | `자료 B v3 .md + .pdf` (9 section, pdf 984 KB) | ✅ |
| 3 | storyline v4 재구성 (변천사 9 곳 제거, 12 slide carry) | `storyline v4 .md + .pdf` (12 slide, pdf 1.48 MB) | ✅ |
| 4 | Claude Design prompt 12 slide (claude.ai/design 그대로 복붙 가능) | `Claude Design prompt v4 .md + .pdf` (pdf 783 KB) | ✅ |
| 5 | Gemini Nano Banana Pro illustration brief (자산 14 장) | `Nano Banana Pro brief v4 .md + .pdf` (pdf 705 KB) | ✅ |
| 6 | 변천사 키워드 검증 (16 키워드 × 4 신본 grep = 0 hit) | 검증 통과 | ✅ |
| 7 | PDF 변환 4 신본 + handoff 직전 archive 이동 + 신본 작성 | 본 handoff | ✅ |
| 8 | plan_diff/latency saturate 통찰 carry (사용자 5/25 00:45 ~ 01:00) — std 1.74× 정량 검증 → §5.10·§7.4·§8.1 + slide 11 Group A 한 줄 추가 + Phase 4 전권 위임 + 백지 PPT 합성 제외 carry | 자료 B v3 + storyline v4 + handoff update + PDF 재변환 | ✅ |

**전체 task 8/8 completed**.

## 2. ★★★ 변천사 제거 — 사용자 룰

### 2.1 사용자 명시 (5/25 00:00 KST)

> "메커니즘 규명을 바꿨다느니 하는 그런 내용 필요없어. 우리의 변천사가 아니라 가치있는 의미있는 데이터 자체만이 중요해. 변천사가 중요한 게 아니고 우리는 최종 결과(수정이 어떻게 되었든 간에)가 중요한거야. 실험하다 안됐다 됐다. 이런 거 변천사 이런 게 중요한 게 아니고 구체적인 의미 + 구체적인 실제 측정 데이터 이런 게 중요"

### 2.2 변천사 분류·처리 룰 (carry · 본 세션 추가)

다음 패턴들이 "변천사" → 외부 발표·자료에서 제거 또는 재서술:

| 패턴 | 처리 | 사례 |
|---|---|---|
| "이전 명칭 vs 정정 후 명칭" 표 | **제거** (정정 후 명칭만 본문 carry) | hilbert_real → pca2d_hilbert_xy2d 같은 8 rename 표 |
| "본 자료는 ... 처음엔 X 였으나 audit 후 Y" | **재서술 (의미만 carry)** | 메커니즘 규명 변천사 |
| "3-multi-AI audit 신뢰도 87/100 conditional pass" | **제거** | 검증 변천사 |
| "negative · methodological 결과" framing | **재서술** | "negative" 라벨 제거, 실측 결과만 |
| "구조적 한계 드러남" framing | **재서술** | "92.7% same plan · median Δ% +0.11% 동등" 실측만 |
| "음성 대조군 가치만 carry" / "해봤지만 폐기" | **재서술** | "본 발표에 결과 표시 X" 단순 표현 |
| "이전 캠페인 92.2% → 본 캠페인 89.1% 약화" | **제거** | 캠페인 변천사 |
| "v14 → v15 → v16 patch · fix 완료" | **제거** | 코드 fix 변천사 |
| "BLOCKER E rng-stream-independent fix" | **제거** | 코드 변경 reference |
| "Gemini Deep Think 적대 검증" / "Codex review" | **제거** | 외부 검증 절차 reference |
| "v2 폐기 carry · 본 v3 신본" | **제거** | 작성 변천사 |
| 한계 자체 (다중 벡터 이상치·통계 floor·sf=10 한정 일반화) | **carry** | 한계는 의미 있는 결과의 일부 |

본 룰은 **보고서 6/11 안** 에는 **carry** (학술 정직성), **외부 발표·자료** 에는 **반영 X** (변천사 제거).

### 2.3 본 세션 제거 27 곳 분포

| 문서 | 제거 곳 |
|---|--:|
| 자료 B v2 → v3 | 9 곳 (§6 메커니즘 규명·§7 명칭 정정·§10 검증 수준 표·§11 결론 재서술) |
| storyline v3 → v4 | 9 곳 (머리말·룰 #3·slide 7·8·9·10·§14·§15) |
| 보고서 6/11 (carry, v3·v4 발표에 미반영) | 9 곳 (보고서 안 carry, 외부 발표·자료엔 실측만) |

각 문서별 line-level 제거 위치 상세는 `_internal/state/변천사_제거_식별_20260525.md` (있다면, 본 handoff §2 carry로 충분 — 신규 작성 X) 또는 직전 작업 plan `/Users/hyunbin/.claude/plans/validated-dazzling-turtle.md` 참조.

### 2.4 검증 — 변천사 키워드 0 hit

본 세션 산출 4 신본 (자료 B v3 + storyline v4 + Claude Design prompt + Nano Banana Pro brief) 에 다음 16 키워드 grep 검증:

```
정정 사유 · audit · 이전 명칭 · 메커니즘 규명 · 진짜 메커니즘 · negative · methodological
해봤지만 폐기 · 음성 대조군 · 구조적 한계 · v2 폐기 · BLOCKER E · 3-multi-AI · 이전 캠페인 · drift · fix 완료
```

**4 신본 × 16 키워드 = 0 hit 통과**. 변천사 제거 검증 완료.

## 3. ★★★ 156 plan 상세 표 — 본 연구 핵심 신규 정본

### 3.1 측정 정의

- 측정 환경: **DEEP sf=10 · 4 query (Q3·Q9·Q10·Q12) × 3 qid (0·1·2) = 12 cell · sel=0.001**
- 각 cell × 13 결합 method (B1 추정 + 분포 인지 method 추정의 산술 평균) = **156 row 정확**
- 각 row 의 latency = 15 trial × trim mean (보고서 §5.2 정본 metric)
- plan 비교 = `plan_signature` (pre-order Node Type tuple) 일치 / 불일치
- raw 원자료: `_internal/cache/rq3/latency/phase2/latency_tpc_h_{q3,q9,q10,q12}_DEEP_sf10_sel0.001_qid{0,1,2}.json` × 12 file
- 추출 산출물: `_internal/cache/rq3/latency/phase2/table_156plan_20260525_001258.{csv,md}`
- 추출 스크립트: `_internal/scripts/extract_156plan_table.py` (60 줄)

### 3.2 핵심 결과 (자료 B v3 §5 carry)

| 측면 | 값 |
|---|--:|
| plan_same | 96/156 = 61.5% |
| plan_diff | 60/156 = 38.5% |
| CaseB oracle 회복 | **148/156 = 94.9%** |
| B1 oracle 회복 (12 cell × 13 반복) | 91/156 = 7 cell × 13 method (B1 7/12 cell carry) |
| Δ% median (전체 156) | −0.06% |
| Δ% mean (전체 156) | −0.66% |
| |Δ%| < 5% | 134/156 = 85.9% |
| injection_fired True | 156/156 = 100% |

### 3.3 cell × plan 회복 분포 (12-row summary)

| Cell | B1 plan 회복 | CaseB plan 회복 / 13 | plan_same / 13 | B1 trim mean (ms) | CaseB Δ% median |
|---|:--:|:--:|:--:|--:|--:|
| Q10 qid=0 | ❌ | **13** | 0 | 973.9 | +1.81% |
| Q10 qid=1 | ✓ | 13 | 13 | 1065.4 | −2.07% |
| Q10 qid=2 | ✓ | 13 | 13 | 1060.2 | +0.34% |
| Q12 qid=0 | ❌ | **13** | 0 | 952.6 | +3.40% |
| Q12 qid=1 | ✓ | 13 | 13 | 899.2 | −1.20% |
| Q12 qid=2 | ✓ | 13 | 13 | 830.2 | +2.50% |
| Q3 qid=0 | ❌ | **12** | 0 | 1018.1 | −2.76% |
| Q3 qid=1 | ✓ | 12 | 12 | 936.8 | +1.37% |
| Q3 qid=2 | ❌ | 7 | 6 | 1217.5 | −9.21% |
| Q9 qid=0 | ❌ | **13** | 0 | 894.6 | +1.24% |
| Q9 qid=1 | ✓ | 13 | 13 | 860.9 | −2.67% |
| Q9 qid=2 | ✓ | 13 | 13 | 915.3 | −1.19% |
| **합계** | **7/12 cell** | **148/156 = 94.9%** | 96/156 = 61.5% | — | — |

핵심 결과:
- 7 cell 은 B1 이 이미 정답 plan — CaseB 13/13 도 같은 plan 유지 (overhead 없음)
- B1 plan 회복 못한 5 cell 중 4 cell 에서 CaseB 13/13 또는 12/13 이 정답 plan 으로 회복
- 유일한 부분 회복 cell = **Q3 qid=2** (6-way join 의 가장 복잡한 plan 공간, B1 trim mean 1217.5 ms 12 cell 중 최대)
- **결합 13 method 가 B1 가 놓친 정답 plan 을 일관되게 회복** — plan recovery robustness 가 결합 방식의 주된 가치

## 4. ★★★ 핵심 정본 수치 (carry · 변경 X)

직전 handoff §3 verbatim carry — 본 세션은 수치 변경 X, 156 plan 추출 추가만:

- v13 B1 qe_trim mean **1.4582** · CaseA **1.6359** · CaseB **1.4019** (1,508 cell)
- 결합 vs B1 paired: **89.1%** better · median Δ% **−4.38%**
- 단독 대체 vs B1: 35.2% · mean Δ% **+12.90%**
- v14 사전 등록 통제군 9 cell mean **1.3729** (CaseC dual-Bernoulli)
- v16 95 tuple 전수: CaseC mean **1.3060**, CaseC vs B1 95/95 = 100% median Δ% **−11.32%**, CaseC vs CaseB 95/95 = 100% median Δ% **−5.98%**
- engine (DEEP sf=10 12 cell): baseline 5,677 ms · B1 977.6 ms · CaseB 983.5 ms · oracle 992.3 ms (median, 12 cell 평균) · **mean gain B1 5.77× · CaseB 5.70× · oracle 5.65×**
- 보고서 §5.2 verbatim: 12 cell oracle gain 평균 **5.67×** (trim mean)
- B1 정답 plan 회복 **7/12 = 58.3%** · 결합 13 method **148/156 = 94.9%**
- paired Wilcoxon vs B1 (168 비교): **13/168 = 7.7%** 유의 · 86.9% small effect
- plan recovery (3 평면 700 paired B1 anchor): **92.7%** same / **7.3%** different
- variance condition % SS **0.00%** · p=0.866 (poc_6_4 legacy) 또는 p=0.945 (poc_6_4_extended)
- 4-way (5/24, 12 cell × 18 variant): CaseC vs B1 paired mean +0.30% · median +0.11% · 17 inject 모두 |Δ%| ≤ 1.12%
- baseline vs B1: mean +**409.7%**

### 4.1 method ranking 상위 5 (정정 후 명칭, carry)

| 순위 | Method | paradigm | better% | median Δ% | algorithm |
|:--:|---|---|--:|--:|---|
| 1 | **chao_weighted** | P3 Streaming | 100.0% | **−6.22%** | Chao 1982 priority sampling u^(1/w), PCA 환원 X |
| 2 | **pca2d_hilbert_xy2d** | P2 Spatial (PCA-reduced) | 98.9% | −5.91% | PCA 2D + Wikipedia xy2d Hilbert |
| 3 | **pca4_skilling_hilbert_approx** | P2 Spatial (PCA-reduced) | 100.0% | −5.75% | PCA 4D + Skilling 2004 알고리즘 근사 |
| 4 | **ica_fastica** | P4 DimReduction | 100.0% | −5.69% | Hyvärinen 1999 FastICA |
| 5 | **pca1d** | P4 DimReduction | 97.9% | −5.55% | Pearson 1901 PCA 1D |

★ **본 연구 최저 Q-error method = chao_weighted** (P3 Streaming · PCA 환원 X · 명칭 학술 정합)

## 5. ★★★ 다음 세션 task (Phase 4 — Claude Code 전권 위임)

### Phase 4 (critical, 5/26 deck 마감 약 47 시간 남음) — Claude Code 가 직접 시안 생성

★ **사용자 5/25 00:50 KST 명시**: "다음 세션에서 클로드 디자인 + 제미나이 작업 전권 위임받아서 할 수 있도록 세션 인계". 다음 세션 Claude Code 가 본 산출물 직접 진행.
★ **백지 PPT 합성 부분은 제외 carry**: 사용자가 storyline v4 update 과정에서 백지 구글 PPT 내용 이미 반영 — Phase 4 에서 합성 단계 X. 시안 생성·export 까지가 본 세션 범위, PPT 최종 합성·업로드는 사용자 영역.

**critical path 약 47 시간** (5/25 00:13 KST 시작 → 5/26 23:59 KST 마감).

1. **Claude Design 12 slide 시안 생성 (Claude Code 직접 진행)**:
   - claude.ai/design "최종발표" 대화창 `/p/019e1a41-701c-7134-9ce1-1247262c1563` 진입 (Chrome MCP macmini 자동 선택 carry · 새 대화창 X · design system 동결)
   - 본 세션 Claude Design prompt v4 (`submission/_drafts/속도는벡터_v4_ClaudeDesign_prompt_20260525_001258.md`) §0 design foundation → §1 → §12 순서대로 복붙
   - 각 slide 생성 후 export (PNG·SVG) → `submission/_drafts/claude_design_export/slide_{01..12}.png` 식 경로 carry
   - 12 slide 일관성 검증 (navy 앵커·chapter badge·hero gradient·폰트 통일)

2. **Gemini Nano Banana Pro 자산 14 장 생성 (Claude Code 직접 진행)**:
   - Gemini Ultra (웹앱 또는 API · `gemini-3-pro-image-preview`) 활용
   - 본 세션 Nano Banana Pro brief v4 (`submission/_drafts/속도는벡터_v4_NanoBananaPro_brief_20260525_001258.md`) carry
   - Asset 1A·1B·2·3·4·5 (3 아이콘)·6 (paradigm 7 장)·7A·7B 총 14 장
   - 산출 경로 `submission/_drafts/nano_banana_export/asset_{1A,1B,2,...,7B}.png`
   - 한국어 텍스트 가독성·navy + cyan palette·flat design 일관성 검증

3. **사용자 manual 단계 (Claude Code X)**:
   - 사용자가 본 시안 12 slide + 자산 14 장을 본인 이미 update 한 백지 PPT 에 합성·텍스트 정합·PPTX export
   - **5/26 23:59 LearnUs 업로드** — 파일명 `속도는벡터_최종발표_슬라이드.pptx`
   - **자료 A v2 양식 정합** (지도확인서 10회차) 동반 제출 (`submission/_drafts/속도는벡터_연구지도확인서_10회차_v2_양식정합_20260524_233327.{md,pdf}`)

4. **plan_diff/latency saturate 통찰 carry (다음 세션 참고용)**:
   - 사용자 5/25 00:45 통찰: "엔진 측정이 sf=10 한정이라 plan_diff 와 latency 개선이 saturate 됐을 가능성"
   - **156 plan 데이터로 정량 검증 완료** — plan_diff Δ% std 4.91 vs plan_same 2.82 (≈ 1.74× 큼), plan_diff range [−12.06%, +7.54%] vs plan_same [−6.78%, +7.22%]
   - **사용자 결정**: "일단 이건 그냥 앞으로 나중에 더 확인해봐야 하는 부분으로 전달" — 본 세션 추가 측정 X, Future Work 로 자료 B v3 §7.4·§8.1 + storyline v4 slide 11 Group A carry 완료
   - 향후 확장 검증 환경 우선순위 (Future Work): sf=100 Disk I/O bound · 큰 selectivity (≥ 0.5) · 다중 벡터·WIKI 768d · 타 엔진 (VBASE·DuckDB-vss·Milvus)

### Phase 5 (5/27-5/28) — 포스터·소개영상 별도 작업 (5/28 12:00 정오 마감)

- 포스터 (900×1200 mm PDF) + Nano Banana Pro 5 자산 활용
- 소개영상 (3-5 분) + Veo 3.1 활용 + ElevenLabs 한국어 TTS narration
- 별도 brief 작성 예정 (5/27 발표 후)

### Phase 6 (5/27-6/11) — 발표 후 보고서·상호평가

- 5/27·29 발표 결과 반영
- 6/11 23:59 LearnUs 최종 보고서·상호평가 결과 제출

## 6. 산출물 경로 (총정리)

| 산출물 | 경로 | 크기·상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260525_001258_변천사제거_156plan_storylineV4_designPrompt.md` | 본 파일 |
| ★ 직전 handoff (archive) | `_internal/handoff/archive/handoff_20260524_233327_methodNamingAudit완료_정정반영_PDF4종.md` | archive |
| ★ 직전 직전 handoff (archive) | `_internal/handoff/archive/handoff_20260524_232149_*.md` | archive |
| **★ 자료 B v3 (채림님)** | `submission/_drafts/속도는벡터_채림님_전달용_구체적_데이터_v3_20260525_001258.{md,pdf}` | pdf 984 KB · 정본 |
| **★ storyline v4** | `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.{md,pdf}` | pdf 1.48 MB · 정본 |
| **★ Claude Design prompt v4** | `submission/_drafts/속도는벡터_v4_ClaudeDesign_prompt_20260525_001258.{md,pdf}` | pdf 783 KB · 정본 |
| **★ Nano Banana Pro brief v4** | `submission/_drafts/속도는벡터_v4_NanoBananaPro_brief_20260525_001258.{md,pdf}` | pdf 705 KB · 정본 |
| **★ 156 plan 표 raw** | `_internal/cache/rq3/latency/phase2/table_156plan_20260525_001258.{csv,md}` | csv + md · 156 row 정합 |
| **★ 156 plan 추출 script** | `_internal/scripts/extract_156plan_table.py` | 60 줄 · analyze_latency.py 함수 carry |
| 본 세션 plan | `/Users/hyunbin/.claude/plans/validated-dazzling-turtle.md` | carry (작업 추적·실행 순서·검증 룰) |
| 자료 B v2 (직전, 변천사 영역 carry) | `submission/_drafts/속도는벡터_채림님_전달용_구체적_데이터_v2_재구성_20260524_233327.{md,pdf}` | deprecated (v3 신본 사용) |
| storyline v3 (직전, 변천사 영역 carry) | `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v3_3way_20260524_220405.{md,pdf}` | deprecated (v4 신본 사용) |
| 보고서 6/11 정본 (변경 X) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.91 MB) | carry · 보고서 안 변천사 영역은 학술 정직성 carry, 외부 발표·자료엔 반영 X |
| 자료 A v2 양식 정합 (지도확인서 10회차, 변경 X) | `submission/_drafts/속도는벡터_연구지도확인서_10회차_v2_양식정합_20260524_233327.{md,pdf}` (596 KB) | carry · 5/26 동반 제출 |
| METHOD_REGISTRY (변경 X) | `_internal/METHOD_REGISTRY.md` | carry |
| v13 정본 raw | `_internal/cache/rq3/aggregated_v13_full.parquet` · `paired_delta_v13.parquet` | carry |
| 보고서·storyline 의 핵심 carry 자산 | `_internal/state/ICDE_verbatim_발췌_20260523.md` · `submission/_drafts/전시회 및 최종발표에 대한 안내 수업_transcript.txt` · `submission/_drafts/최종 발표와 자료, 제출물 양식.txt` | carry |

## 7. 환경·자원 (carry · 변경 X)

- 서버: 165.132.140.240 (capstone2026), Intel Xeon Gold 6530 · 128 vCPU · 1.0 TB RAM · 4× RTX 6000 Ada · PG port 55435
- 자원 watchdog v6 서버 가동 중
- 로컬 Mac: SSD 1.8 TB · 사용 1.0 TB · 여유 795 GB
- claude·codex 단일 호스트 = macmini (Tailscale 100.85.223.63)
- 본 세션 commit 미진행 — 다음 세션 commit + push 권장 (자료 B v3 + storyline v4 + Claude Design prompt + Nano Banana Pro brief + 156 plan 표·script + handoff 신본)

## 8. 일정 (carry · 변경 X)

- **5/26 (월) 23:59** ★★ 발표 슬라이드 LearnUs 마감 — Phase 4 critical path (약 47 시간 남음)
- **5/26 (월)** 연구지도확인서 10회차 (자료 A v2) LearnUs 제출
- **5/27 (수) 15:00 D504호** · **5/29 (금) 15:00 D504호** 최종 발표 (10 분 + 5 분 Q&A)
- **5/28 (목) 12:00 정오** 포스터 + 소개영상 LearnUs 제출 마감
- **6/5 (금) 9:00-18:00** 전시회
- **6/10 (수)** 박광현 교수님 마지막 세미나
- **6/11 (목) 23:59** 최종 보고서·상호평가 LearnUs 제출 마감

## 9. 환각 회피 룰 (carry · 본 세션 추가)

### 9.1 method 명칭 정정 후 carry (직전 세션 carry, 본 세션 그대로 carry)

- `pca2d_hilbert_xy2d` · `pca4_skilling_hilbert_approx` · `pca2d_zorder_morton` · `pca2d_equi_depth_grid` · `md5_prefix_hash_bucket` · `takeall_cumsqrtf` · `rabitq_1bit_bucket` · `chao_weighted` (정합) · `ica_fastica` (정합) · `pca1d` (정합) · `sparse_rp` (Li 2006 정정 carry) · `rsvd` (정합) · `gmm` (정합) · `minibatch_partial` (정합) · `faiss_ivf` (정합) · `cum_sqrtf` (정합) — 8 rename + 8 정합 = 16 method

### 9.2 paradigm 정정 후 carry

- P9 InfoTheoretic 폐지 · P5b Hashing 신설 · P5 QMC → P5 Classical Stratification · P2 Spatial PCA-reduced 명시

### 9.3 ★ 변천사 제거 룰 (본 세션 신규)

외부 발표·자료 (storyline v4·자료 B v3·Claude Design prompt·Nano Banana Pro brief·deck·포스터·소개영상·자료 A v2) 안에:
- 명칭 정정·이전 vs 정정 후 표 · audit 결과 reference 등 변천사 **모두 제거**
- 메커니즘 규명 과정·"진짜 메커니즘은 X 가 아니라 Y" 비교 framing · "negative · methodological" 라벨 **재서술 (의미만 carry)**
- "구조적 한계 드러남" · "음성 결과" 같은 평가 framing **재서술 (실측 결과만)**
- v14·v15·v16 캠페인 변천사·BLOCKER E fix reference **제거**
- 단 한계 자체 (다중 벡터 이상치·통계 floor·sf=10 한정 일반화) 는 **carry** (한계 = 의미 있는 결과의 일부)

보고서 6/11 안에는 학술 정직성 차원에서 변천사 영역 carry, 외부 발표·자료엔 반영 X.

### 9.4 정본 수치 (직전 세션 carry, 본 세션 그대로 carry)

1.4582·1.4019·89.1%·−4.38%·5.77×·5.70×·5.65×·92.7%/7.3%·variance 0.00% (p=0.866 legacy / p=0.945 extended)·CaseC v16 1.3060·−11.32%·−5.98%·**156 plan 안 148/156 = 94.9% (본 세션 신규 추출)** · **plan_same 96 / plan_diff 60**

### 9.5 일반 룰 (carry · 변경 X)

- 측정 portfolio: 1,508 / 의도 max 3,600 = 41.9% 구조화 (full factorial 아님)
- A2-Fig8 4/16 method · A4-sel 희소 cell · WIKI sf=10 engine timeout · sf=1/100 engine 부분 — 의도된 한계
- 비가역 작업 (git push --force · DB DROP · rm -rf) — 사용자 사전 위임 없음
- handoff 룰: 종료 시 active 직전 archive → 신본 timecode 작성 ✓
- 사용자 commit OK (자율 위임) · push 명시 요청 시만
- ★ 다음 세션 진입 시 본 handoff 정독 + 자료 B v3 + storyline v4 + Claude Design prompt + Nano Banana Pro brief 모두 정본 carry — 이전 v1·v2·v3 자료는 deprecated, 사용 X

## 10. 본 세션 핵심 의사결정 (다음 세션 carry)

1. **변천사 제거 critical** — 사용자 5/25 00:00 명시 ("메커니즘 규명을 바꿨다느니 그런 내용 필요없어 · 최종 결과만 중요")
2. **156 plan B1 vs CaseB 완전 상세 표 추출** — 사용자 5/25 00:01 명시 ("156 plan을 상세하게 ... 완벽하게 표로 정리. latency 값 매우 정확하게")
3. **storyline·내러티브·덱 모두 변천사 X 적용** — 사용자 5/25 00:05 명시 ("실험하다 안됐다 됐다 이런 거 변천사 이런 게 중요한 게 아니고 구체적인 의미 + 구체적인 실제 측정 데이터 이런 게 중요")
4. **156 plan = phase2 DEEP sf=10 12 cell × 13 결합 method** — analyze_latency.py 함수 차용 가능 검증 (Phase 1 Explore 결과)
5. **자료 B v3 + storyline v4 + Claude Design prompt + Nano Banana Pro brief 4 신본 동시 작성** — 5/26 마감 critical path
6. **plan_diff/latency saturate 통찰 = Future Work 로 carry** — 사용자 5/25 00:45 통찰 (plan_diff 환경 한정으로 latency 개선 saturate). 156 plan 데이터로 std 1.74× 정량 검증 후 자료 B v3 §5.10·§7.4·§8.1 + storyline v4 slide 11 Group A 에 carry. 본 세션 추가 측정 X — 사용자 5/25 01:00 결정 ("일단 나중에 더 확인해봐야 하는 부분으로 전달")
7. **다음 세션 = Phase 4 (Claude Code 전권 위임)** — 사용자 5/25 01:00 명시 ("다음 세션에서 클로드 디자인 + 제미나이 작업 전권 위임받아서 할 수 있도록 세션 인계"). 백지 PPT 합성 부분 제외 (사용자가 storyline v4 update 과정에서 이미 반영 carry).

---

작성 2026-05-25 00:13 KST · 갱신 5/25 01:00 KST (Phase 4 전권 위임 + 백지 PPT 제외 + plan_diff Future Work). 변천사 27 곳 제거 · 156 plan 상세 표 추출 (12 cell × 13 method = 156 row · CaseB oracle 회복 148/156 = 94.9% · plan_diff Δ% std 4.91 vs plan_same 2.82) · 자료 B v3 + storyline v4 + Claude Design prompt + Nano Banana Pro brief 4 신본 + PDF · 변천사 키워드 검증 0 hit 통과. 다음 세션 = Phase 4 (Claude Code 직접 Claude Design 12 slide + Nano Banana Pro 14 자산 시안 생성, 5/26 23:59 마감 약 47 시간 남음).
