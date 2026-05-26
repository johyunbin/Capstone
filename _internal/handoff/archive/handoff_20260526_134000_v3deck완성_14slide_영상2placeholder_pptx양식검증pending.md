# handoff 20260526 13:40 — v3 deck 14 slide 완성 (영상 2 placeholder) · Gemini 영상 사용자 진행 중 · 다음 세션 = 스크린샷 PPT vs 편집 가능 PPT 시각 정밀 비교 → 편집 가능 PPTX 양식 시각 일치 fix

> 직전 handoff (`handoff_20260525_232336_v17deck완성_v18prompt_박세은피드백3건.md` → archive) → 본 문서. self-contained 0% loss 인계.
>
> **★ 핵심 한 줄**: 본 세션 = (1) v17 → v18 (slide 2·3·5 박세은 피드백) → **v19 (사용자 피드백 13건, slide 2·3·5·6·7·8·9·10·11)** → **v20 (피드백 6건, slide 2·3·4·5·6·9·11)** → **v21 (영상 2개 placeholder 추가, slide 3 baseline + 새 slide 12 결합, 14 slide deck)** 진화. 사용자 시스템 = **forward-versioning** (`속도는벡터_기말발표_v0~v3.pptx`, v0 = 최초 클로드 디자인 작업, 이후 수정은 v1·v2·v3 순). (2) **Gemini Ultra Veo 3.1 영상 2개 (baseline + 결합) 정밀 prompt 작성 완료** — 사용자 manual 진행 중. (3) **PPTX 검증 영구 룰 추가** — Claude Design HTML preview ≠ LibreOffice PPTX→PDF 변환 (gradient text + Apple SD Gothic Neo fallback 손상). 다음 = **사용자 명시 task — 스크린샷 모드 PPT vs 편집 가능 모드 PPT 비교 + 편집 가능 PPTX 양식을 시각적으로 정확 일치하도록 fix**. (4) 마감 5/26 23:59 LearnUs PPTX 업로드 — **10h 19m 남음** (현 13:40 KST).

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계
- **★ 직전 handoff (archive)**: `_internal/handoff/archive/handoff_20260525_232336_v17deck완성_v18prompt_박세은피드백3건.md`
- **★ v3 PPTX (현 최신 · LearnUs 후보)**: `submission/_drafts/속도는벡터_기말발표_v3.pptx` (925 KB · 14 slide · 영상 2 placeholder)
- **★ Forward-versioning PPTX 4세트**:
  - v0: `속도는벡터_기말발표_v0.pptx` (909K · 13 slide · 클로드 디자인 첫 작업)
  - v1: `속도는벡터_기말발표_v1.pptx` (827K · 13 slide · 사용자 피드백 9건 반영, 1,508 분해 정합)
  - v2: `속도는벡터_기말발표_v2.pptx` (768K · 13 slide · 피드백 6건 + slide 3 영상 placeholder 전환)
  - v3: `속도는벡터_기말발표_v3.pptx` (925K · 14 slide · 영상 2 placeholder 추가)
- **★ Claude Design 정본 deck (현 최신)**: `deck_v26.html` (claude.ai/design 대화창 `019e1a41-701c-7134-9ce1-1247262c1563`)
- **★ deck 진화**: deck_v22 (사용자 별도 22 slide trial, 폐기) → deck_v23 (사용자 첫 prompt 적용 13 slide) → deck_v24 → deck_v25 → **deck_v26 (현 최신 14 slide)**
- **★ Gemini Veo 3.1 + Claude Design HTML animation 영상 4 prompt**: `submission/_drafts/영상_4prompt_gemini_claude_design_5_26_13_00.md` — 사용자 manual 진행 (Gemini Ultra 웹앱 인증)
- **★ v0 → v1 polishing prompt (이력)**: `submission/_drafts/v0_polishing_prompt_9slide_5_26_02_00.md`
- **★ v1 → v2 polishing prompt (이력)**: `submission/_drafts/v1_polishing_prompt_6slide_plus_video_5_26_02_35.md`
- **★ v18 → v19 5slide prompt (이력)**: `submission/_drafts/v18_polishing_prompt_5slide_5_26_00_18.md`
- **★ v18 → v19 full deck prompt (이력)**: `submission/_drafts/v18_polishing_prompt_full_5_26_01_00.md`
- **★ Gemini Ultra v23 검증결과**: `submission/_drafts/gemini_v23_검증결과_5_26_02_10.md` (47줄 응답, 평결 = PASS, 보완 3건 모두 발표 스크립트 수준)
- **★ Gemini Ultra v23 검증 brief**: `submission/_drafts/gemini_ultra_v23_검증_brief_5_26_01_45.md`
- **★ deck_v22.html (carry, 폐기 trial)**: `submission/_drafts/deck_v22.html` (128 KB · 22 slide)
- **★ storyline v4 정본**: `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.md`
- **★ TPC-H Q3 SQL**: `reference/exqutor_query_plans/tpc_h/q3.sql`
- **★ Exqutor §V-B Adaptive Sampling 정본**: `reference/analysis/(01) Exqutor 상세분석.md`
- **★ 보고서 6/11 정본**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.91 MB)
- **★ 자료 A v2 양식 정합 (지도확인서 10회차)**: `submission/_drafts/속도는벡터_연구지도확인서_10회차_v2_양식정합_20260524_233327.{md,pdf}` — 5/26 동반 제출
- **★ PPTX 검증용 PDF·PNG (v3)**: `/tmp/v3_verify/속도는벡터_기말발표_v3.pdf` + `pptx_slide-01~14.png` (LibreOffice 변환, **★ 손상 — 폰트 fallback + gradient text 손실**)
- **★ 1,508 분해 정본**: 보고서 §3 line 115 "5 조작변인 교차 — 데이터셋(단일 5종 + 다중 조합 = 9종), scale factor(sf=1/10/100), selectivity(0.001/0.01/0.10), **K(10/20/30)**, method 16종" / 의도 max 3,600 中 실측 1,508 (41.9% 구조화)

## 1. ★★★ 본 세션 완료 작업 (한 줄 요약)

| Phase | 작업 | 산출 | 상태 |
|:--:|---|---|:--:|
| 1 | 직전 handoff 정독 + v18 PPTX 14 slide 추출 + 검증 | session start | ✓ |
| 2 | slide 1~14 사용자 디테일 검토 (slide 2·3·5·6·7 5건 피드백) | 5slide prompt 작성 | ✓ |
| 3 | v18 → v19 full deck prompt (slide 8·9·10·11·12·13·14 추가 변경) | full deck prompt 작성 + claude.ai/design 적용 → v23 deck (13 slide) | ✓ |
| 4 | v23 13 slide Chrome MCP Present 모드 시각 정합 검증 PASS | 13 slide PNG 확인 + 사용자 피드백 9건 모두 반영 검증 | ✓ |
| 5 | Gemini Ultra (gemini-3.1-pro-preview) headless 독립 재검증 (text-base) | `gemini_v23_검증결과_5_26_02_10.md` (47줄, **평결 = PASS**, 보완 3건 모두 발표 스크립트 수준) | ✓ |
| 6 | PPTX export `속도는벡터_최종발표_v23_20260526_0128.pptx` (909K · 13 slide) | 사용자 자동 다운로드 + _drafts 이동 + 13 slide 검증 PASS | ✓ |
| 7 | 사용자 forward-versioning rename: `속도는벡터_기말발표_v0.pptx` | v0 = 시작점 (방금 만든 v23 사본) | ✓ |
| 8 | v0 → v1 사용자 피드백 9건 polishing prompt + Claude Design 적용 → v1 PPTX (827K · 13 slide) | 1,508 = 5×sf3×sel3×K3×16 + K 변인 + 16 中 강한 13 paradigm + cardinality 용어 통일 + 최적 plan 선택 + broken axis 시각 재설계 | ✓ |
| 9 | v1 → v2 사용자 피드백 6건 polishing prompt + Claude Design 적용 → v2 PPTX (768K · 13 slide) | slide 3 = 영상 placeholder 전환 + slide 5 BATCH dot/설명 삭제 + slide 4 한 줄 통합 등 | ✓ |
| 10 | v2 → v3 영상 2개 placeholder 추가 prompt + Claude Design 자동 적용 → v3 PPTX (925K · 14 slide) | slide 3 = baseline 영상 placeholder + 새 slide 12 = 결합 영상 placeholder, deck = 14 slide | ✓ |
| 11 | Gemini Ultra Veo 3.1 + Claude Design HTML animation 영상 4 prompt 정밀 작성 (Adaptive Sampling pipeline 반영, ② cardinality 추정 단계 = 본 연구 위치 강조) | `영상_4prompt_gemini_claude_design_5_26_13_00.md` | ✓ |
| 12 | PPTX 검증 영구 룰 작성 + 메모리 저장 + v3 PPTX LibreOffice 검증 시도 | `feedback_pptx_export_verification.md` + `/tmp/v3_verify/` (LibreOffice fallback 손상 발견) | ✓ |
| 13 | 발표물 영구 룰 메모리 저장 (4 룰) | `feedback_slide_universal_rules.md` (약어 풀어쓰기·텍스트 정렬·시각 자료 우선·청중 친숙 단어) | ✓ |
| 14 | handoff 작성 + archive | 본 handoff | ✓ |

**전체 task 14/14 completed**.

## 2. ★★★ Forward-versioning PPTX 시스템 (사용자 명시 영구 룰)

★ **`속도는벡터_기말발표_v{N}.pptx` 시스템** (사용자 2026-05-26 01:50 명시):
- **v0** = 시작점 (방금 클로드 디자인 작업)
- **새 수정 = v1, v2, v3, ... 순차 증가** (forward)
- 이전 파일 (v17·v18 등 다른 이름) **원래 이름 carry** (rename X)

현 시점 (v3) 까지 진화:
- v0 → v1 (피드백 9건, 1,508 분해 정합)
- v1 → v2 (피드백 6건, slide 3 영상 placeholder 전환)
- v2 → v3 (영상 2개 placeholder, 14 slide deck)

향후 다음 세션 = v4, v5, ... 식.

## 3. ★★★ v3 deck 14 slide 구조 (LearnUs 후보)

| slide | 컨셉 | 핵심 시각 |
|:--:|---|---|
| 1 | 표지 (carry from v0) | hero "인덱스 부재 시 / Adaptive Sampling 개선" + 부제 + 팀·교수·멘토 |
| 2 | 배경 (VAQ) | 분석가 박스 + 예시 SQL (TPC-H Q3) + VAQ 결과 |
| **3 ★** | 배경 (1만 배) | **영상 placeholder (baseline 작동 원리)** + 부제 + hero "10,000× 응답 시간 차이" |
| 4 | 배경 (33/50/100%) | pgvector 33.3% · VBASE 50% · DuckDB 100% + 한 줄 통합 캡션 |
| 5 | 방법 (Adaptive Sampling) | 5 단계 pipeline + BATCH N₀=385/N₁/N₂ + "→ N 갱신 →" 가로 |
| 6 | 방법 (본 연구 RQ) | RESEARCH QUESTION + 2x2 grid (baseline ↔ 샘플링 방식 탐색) + 대조 화살표 |
| 7 | 방법 (통제 실험) | 3 박스 (baseline + 단독 대체 + 결합 CORE) + cardinality 용어 |
| 8 | 방법 (1,508 측정) | 5 데이터셋 + sf/sel/K/method 4 변인 + COMBINATIONS 1,508 분해 |
| 9 | 방법 (paradigm) | baseline + 13 method 7 paradigm + paradigm 별 method 개수 chip |
| 10 | 결과 (Q-error 89.1%) | hero 89.1% + paired 비교 + broken axis 막대 (baseline 1.4582 · 결합 1.4019) |
| 11 | 적용 (latency + plan 회복) | 3 막대 latency + 도넛 91/156 vs 148/156 + "+57 최적 plan" |
| **12 ★** | 적용 (결합 작동 원리) | **영상 placeholder (결합 작동 원리)** + 부제 "정확한 cardinality → 정답 plan → 빠른 응답" |
| 13 | 적용 (Future Work 두 갈래) | Group A 확장 평면 + Group B History-aware |
| 14 | 마무리 (감사합니다) | hero gradient + 팀·교수·멘토 + GitHub |

## 4. ★★★ 사용자 다음 세션 명시 task — 스크린샷 PPT vs 편집 가능 PPT 시각 정밀 비교

사용자 명시 (2026-05-26 13:39 KST): "**스크린샷 PPT랑, 편집가능한 PPT랑 비교해서 편집가능한 pptx 양식들좀 정확하게 시각적으로 일치하게끔 작업하자**"

### 의도 해석

Claude Design 의 PPTX export 는 두 모드:
1. **편집 가능 모드 (editable)** — native 텍스트·도형 (PowerPoint 에서 텍스트 수정 가능, 단 일부 시각 손상 발생 가능: gradient text, 폰트 fallback, 박스 배경 추가 등)
2. **스크린샷 모드 (screenshot)** — 각 slide 가 image 로 embed (PowerPoint 에서 수정 불가, 단 Claude Design HTML preview 와 시각 100% 일치)

★ 사용자 의도 = **편집 가능 모드 PPTX 의 시각 손상을 fix 하여 스크린샷 모드 PPTX 와 정확 일치하게** 만들기. 즉 양쪽 다 다운로드 → 비교 → 편집 가능 PPTX 의 차이를 Claude Design 보정 prompt (또는 PowerPoint manual) 로 fix.

### 검증 절차 (영구 룰 `feedback_pptx_export_verification.md` 참조)

1. **두 모드 PPTX 모두 export** — Claude Design 에 요청:
   - "deck_v26.html 을 **편집 가능 모드** PPTX 로 export — `속도는벡터_기말발표_v4_editable.pptx`"
   - "deck_v26.html 을 **스크린샷 모드** PPTX 로 export — `속도는벡터_기말발표_v4_screenshot.pptx`"
2. **두 PPTX → PDF → PNG 변환** (LibreOffice + pdftoppm):
   ```bash
   /opt/homebrew/bin/soffice --headless --convert-to pdf 속도는벡터_기말발표_v4_editable.pptx --outdir /tmp/v4_editable
   /opt/homebrew/bin/soffice --headless --convert-to pdf 속도는벡터_기말발표_v4_screenshot.pptx --outdir /tmp/v4_screenshot
   /opt/homebrew/bin/pdftoppm -r 100 -png ...
   ```
3. **14 slide 페이지별 비교** — 두 PNG 세트 시각 일치 여부:
   - 편집 가능 vs 스크린샷 시각 차이 (gradient text, 폰트, 박스, 배경) 식별
4. **차이 발견 시 Claude Design 보정 prompt 작성** 또는 PowerPoint manual 수정
5. **★ PowerPoint (macOS) 직접 열기 의무** — LibreOffice 결과 ≠ PowerPoint 실제 렌더링 (Apple SD Gothic Neo 미설치 fallback 발생). 진짜 검증은 macOS PowerPoint open 후 시각 확인.

### 현 v3 LibreOffice 검증 결과 (다음 세션 carry)

`/tmp/v3_verify/pptx_slide-01~14.png` 14 PNG 추출 완료 — 검증 시 발견된 손상:
- **slide 1**: hero gradient → 검정 단색 / 하단 "속도는벡터·연세대학교..." + 지도교수·연구원·멘토 → **필기체 손글씨 폰트로 변환** (Apple SD Gothic Neo fallback)
- **slide 3**: video placeholder navy 배경 carry ✓ · "10,000× 응답 시간 차이" gradient → 검정 단색
- **slide 12**: video placeholder navy 배경 carry ✓ · "5.70× 응답 시간 단축" gradient → 검정 단색
- **slide 14**: "감사합니다" hero gradient → **큰 navy 배경 박스 + 검정 텍스트로 잘못 변환** (LibreOffice 가 gradient text 를 background box 으로 오해석)
- 그 외 slide 도 비슷한 패턴 가능 (다음 세션에서 확인)

★ 단 **LibreOffice 변환 결과 ≠ PowerPoint 실제 렌더링** — Apple SD Gothic Neo 미설치 fallback 이므로 macOS PowerPoint 에서 직접 열면 정상 가능성. 우선 PowerPoint open 후 시각 확인.

## 5. ★★★ Gemini Veo 3.1 + Claude Design HTML animation 영상 작업 (사용자 manual 진행 중)

★ 사용자 명시 (5/26 13:39): "**제미나이에 영상 요청해놨고**"

영상 2개 (baseline 작동 원리 + 결합 작동 원리) 작업 진행 중:

| 영상 | 컨셉 | 도구 | 사용자 진행 |
|:--:|---|:--:|---|
| 영상 1 | baseline (엔진 탑재 이전) 작동 원리 | Gemini Veo 3.1 (사용자 manual) | 진행 중 |
| 영상 2 | 결합 (최종 엔진) 작동 원리 | Gemini Veo 3.1 (사용자 manual) | 진행 중 |

영상 핵심 spec (사용자 요청 정합):
- Adaptive Sampling 5 단계 pipeline 상단 표시 (Query → ① 표본 추출 → ② cardinality 추정 ★ → ③ Q-error 측정 → ④ N 갱신)
- ② cardinality 추정 단계 = 우리 연구 위치 highlight + zoom-in close-up
- **영상 1** = ② 단계 = 무작위 베르누이 sample 1개 → 단일 추정값 (잘못) → Hash plan → 5,677ms
- **영상 2** = ② 단계 = **두 sample 동시 (베르누이 + 분포 인지) → 두 추정값 → 산술 평균 = 결합 cardinality (정확) → Nested Loop plan → 983.5ms**
- 15초 silent (보이스 X) cinematic
- 색상: baseline = navy + RED / 결합 = navy + CYAN

★ 사용자가 Gemini 영상 받으면 다음 세션에서 **PowerPoint manual embed 가이드** 제공 — slide 3 placeholder + slide 12 placeholder 자리에 Insert → Video → From File.

## 6. ★★★ 영구 룰 (메모리 저장 완료, 다음 세션 carry)

### 6.1 `feedback_pptx_export_verification.md` (★ 다음 세션 핵심 적용)

Claude Design → PPTX 추출 시마다 의무 검증:
1. LibreOffice PPTX → PDF 변환
2. PDF 페이지별 PNG 추출
3. Claude Design HTML preview screenshot 추출
4. 두 PNG 세트 비교
5. 차이 발견 시 보고
6. **★ macOS PowerPoint 직접 열기 의무** — LibreOffice ≠ PowerPoint 실제 렌더링

### 6.2 `feedback_slide_universal_rules.md` (4 룰)

1. 약어 처음 등장 시 풀어쓰기
2. 텍스트 줄 정렬 일관성
3. 수치 강조보다 시각 자료 활용 우선
4. 청중 친숙 단어 우선

### 6.3 forward-versioning 시스템

`속도는벡터_기말발표_v{N}.pptx` 순차 증가 — 새 수정 시 v{N+1}.

## 7. ★★★ 다음 세션 task (★ 마감 critical path — 5/26 23:59 LearnUs PPT 마감 약 10h 19m 남음)

### 7.1 Phase 1 critical (사용자 명시 task)

1. **claude.ai/design 동일 대화창 `019e1a41-...` 진입** (또는 새 대화창)
2. **deck_v26.html 을 두 모드로 다시 export**:
   - 편집 가능 모드 → `속도는벡터_기말발표_v4_editable.pptx`
   - 스크린샷 모드 → `속도는벡터_기말발표_v4_screenshot.pptx`
3. **두 PPTX → PDF → 14 PNG 변환** (LibreOffice + pdftoppm 자동)
4. **14 slide 페이지별 시각 비교**:
   - 편집 가능 vs 스크린샷 차이 식별 (gradient text, 폰트, 박스, 배경 등)
5. **차이 fix**:
   - Option A: Claude Design 에 보정 prompt 작성 → v5 PPTX export
   - Option B: PowerPoint manual 수정 가이드
6. **★ macOS PowerPoint (사용자) 직접 열기 의무 확인** (LibreOffice fallback 손상 거짓 양성일 수 있음)

### 7.2 Phase 2 — Gemini 영상 embed (사용자 manual)

7. **사용자 Gemini 영상 결과 받기** (baseline + 결합 영상 2개 MP4)
8. **PowerPoint manual embed 가이드**:
   - slide 3 placeholder 자리에 baseline 영상 insert
   - slide 12 placeholder 자리에 결합 영상 insert
   - Insert → Video → From File → MP4 선택

### 7.3 Phase 3 — LearnUs 업로드 (사용자 manual)

9. **최종 PPTX 파일명 = `속도는벡터_최종발표_슬라이드.pptx`** (또는 학교 양식 정합 명) 으로 사본 생성
10. **LearnUs 업로드** (5/26 23:59 마감)
11. **자료 A v2 양식 정합 (지도확인서 10회차)** 동반 제출: `submission/_drafts/속도는벡터_연구지도확인서_10회차_v2_양식정합_20260524_233327.{md,pdf}`

### 7.4 Phase 4 — 5/27 (수) · 5/29 (금) 15:00 D504호 발표

12. 10 분 발표 + 5 분 Q&A
13. 발표자 narrative = storyline v4 carry
14. PowerPoint Mac open → 영상 재생 사전 점검

### 7.5 Phase 5 — 5/28 (목) 12:00 정오 포스터 + 소개영상 LearnUs 마감

15. 포스터 (900×1200 mm PDF) — Nano Banana Pro brief v4 carry
16. 소개영상 (3-5 분) — Veo 3.1 + ElevenLabs

### 7.6 Phase 6 — 6/11 (목) 23:59 최종 보고서·상호평가 LearnUs 제출

17. 보고서 6/11 정본 carry (변경 X)

## 8. 산출물 경로 (총정리)

| 산출물 | 경로 | 크기·상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260526_134000_v3deck완성_14slide_영상2placeholder_pptx양식검증pending.md` | 본 파일 |
| ★ 본 세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260526_134000.md` | 본 세션 함께 작성 |
| ★ 직전 handoff (archive) | `_internal/handoff/archive/handoff_20260525_232336_v17deck완성_v18prompt_박세은피드백3건.md` | archive |
| **★ v3 PPTX (현 최신 LearnUs 후보)** | `submission/_drafts/속도는벡터_기말발표_v3.pptx` | 925K · 14 slide |
| **★ v2 PPTX** | `submission/_drafts/속도는벡터_기말발표_v2.pptx` | 768K · 13 slide |
| **★ v1 PPTX** | `submission/_drafts/속도는벡터_기말발표_v1.pptx` | 827K · 13 slide |
| **★ v0 PPTX (시작점)** | `submission/_drafts/속도는벡터_기말발표_v0.pptx` | 909K · 13 slide |
| **★ Claude Design deck (최신)** | claude.ai/design `019e1a41-...` deck_v26.html | 14 slide |
| **★ 영상 4 prompt (Gemini + Claude Design)** | `submission/_drafts/영상_4prompt_gemini_claude_design_5_26_13_00.md` | 사용자 manual 진행 |
| **★ v0→v1 polishing prompt** | `submission/_drafts/v0_polishing_prompt_9slide_5_26_02_00.md` | 이력 |
| **★ v1→v2 polishing prompt** | `submission/_drafts/v1_polishing_prompt_6slide_plus_video_5_26_02_35.md` | 이력 |
| **★ v18→v19 5slide prompt** | `submission/_drafts/v18_polishing_prompt_5slide_5_26_00_18.md` | 이력 |
| **★ v18→v19 full deck prompt** | `submission/_drafts/v18_polishing_prompt_full_5_26_01_00.md` | 이력 |
| **★ Gemini v23 검증 brief** | `submission/_drafts/gemini_ultra_v23_검증_brief_5_26_01_45.md` | carry |
| **★ Gemini v23 검증결과** | `submission/_drafts/gemini_v23_검증결과_5_26_02_10.md` | PASS · 47줄 |
| ★ v3 PPTX LibreOffice 검증 PDF·PNG | `/tmp/v3_verify/속도는벡터_기말발표_v3.pdf` + `pptx_slide-01~14.png` | 14 PNG · LibreOffice fallback 손상 발견 |
| ★ 영구 룰 메모리 | `~/.claude/projects/-Users-hyunbin-Capstone/memory/feedback_pptx_export_verification.md` + `feedback_slide_universal_rules.md` | carry |
| ★ storyline v4 정본 | `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.{md,pdf}` | carry |
| ★ 자료 B v3 정본 | `submission/_drafts/속도는벡터_채림님_전달용_구체적_데이터_v3_20260525_001258.{md,pdf}` | carry |
| ★ 156 plan 표 raw | `_internal/cache/rq3/latency/phase2/table_156plan_20260525_001258.{csv,md}` | carry |
| ★ TPC-H Q3 SQL | `reference/exqutor_query_plans/tpc_h/q3.sql` | carry |
| ★ Exqutor §V-B 정본 | `reference/analysis/(01) Exqutor 상세분석.md` | carry |
| ★ 보고서 6/11 정본 | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` | 1.91 MB · carry |
| ★ 자료 A v2 양식 정합 (지도확인서 10회차) | `submission/_drafts/속도는벡터_연구지도확인서_10회차_v2_양식정합_20260524_233327.{md,pdf}` | 5/26 동반 제출 |
| ★ Claude Design 대화창 | `https://claude.ai/design/p/019e1a41-701c-7134-9ce1-1247262c1563?file=deck_v26.html&slide=1` | 14 slide deck |

## 9. 환경·자원 (carry · 변경 X)

- 서버: 165.132.140.240 (capstone2026), Intel Xeon Gold 6530 · 128 vCPU · 1.0 TB RAM · 4× RTX 6000 Ada · PG port 55435
- 로컬 Mac: SSD 1.8 TB
- claude·codex 단일 호스트 = macmini (Tailscale 100.85.223.63)
- Chrome MCP macmini 자동 선택 룰 carry (사용자 영구 위임)
- 본 세션 commit 미진행 — 다음 세션 commit + push 권장 (v0~v3 PPTX · v0/v1 polishing prompt · 영상 4 prompt · Gemini 검증 brief/결과 · 영구 룰 메모리 · 본 handoff)
- LibreOffice + poppler 모두 설치 OK (`/opt/homebrew/bin/soffice` + `/opt/homebrew/bin/pdftoppm`)

## 10. 일정 (carry · 변경 X)

- **5/26 (월) 23:59** ★★ 발표 슬라이드 LearnUs 마감 — 약 **10h 19m 남음** (현 2026-05-26 13:40 KST 기준)
- **5/26 (월)** 연구지도확인서 10회차 (자료 A v2) LearnUs 제출
- **5/27 (수) 15:00 D504호** · **5/29 (금) 15:00 D504호** 최종 발표 (10 분 + 5 분 Q&A)
- **5/28 (목) 12:00 정오** 포스터 + 소개영상 LearnUs 제출 마감
- **6/5 (금) 9-18** 전시회
- **6/10 (수)** 박광현 교수님 마지막 세미나
- **6/11 (목) 23:59** 최종 보고서·상호평가 LearnUs 제출 마감

## 11. 환각 회피 룰 (carry · 본 세션 추가)

### 11.1 method 명칭 정정 후 carry (직전 세션 carry)

`pca2d_hilbert_xy2d` · `pca4_skilling_hilbert_approx` · `pca2d_zorder_morton` · `pca2d_equi_depth_grid` · `md5_prefix_hash_bucket` · `takeall_cumsqrtf` · `rabitq_1bit_bucket` · `chao_weighted` · `ica_fastica` · `pca1d` · `sparse_rp` (Li 2006 정정) · `rsvd` · `gmm` · `minibatch_partial` · `faiss_ivf` · `cum_sqrtf` — 16 method (베르누이 1 + 분포 인지 15) = 1,508 측정 전수

### 11.2 paradigm 정정 후 carry

7 paradigm 분류 — baseline + 강한 13 method (16 中 클러스터링 3 폐기: gmm·minibatch_partial·faiss_ivf). 각 paradigm method 개수 chip: P1:2 · P2:3 · P3:2 · P4:2 · P5:1 · P6:1 · P7:2 = 13

### 11.3 ★ 1,508 정확 분해 (본 세션 추가, 다음 세션 carry)

**1,508 = 5 조작변인 교차 (보고서 §3 line 115 정본)**:
- 데이터셋 = 9종 (단일 5종 + 다중 조합)
- scale factor sf = 3 (1/10/100)
- selectivity sel = 3 (0.001/0.01/0.10)
- **K (계층 수) = 3 (10/20/30)** ★ 핵심 차원
- method = 16종

의도 max 3,600 中 실측 1,508 (41.9% 구조화 부분 측정)

slide 8 = "1,508 측정 전수 = 16 method" / slide 9 = "16 中 강한 13 paradigm 분류 (클러스터링 3 폐기)" — 정합

### 11.4 ★ 변천사 제거 룰 (carry · 본 세션 검증 통과)

외부 발표·자료 (v3 deck·포스터·소개영상·자료 A v2) 안:
- 명칭 정정·이전 vs 정정 후 표·audit 결과 reference·v14~v26 캠페인 변천사 모두 **제거**
- "분포 인지" → "샘플링 방식 탐색" 으로 swap
- 단 한계 자체 (다중 벡터 이상치·통계 floor·sf=10 한정 일반화·plan_diff 분포 의존성) carry

### 11.5 정본 수치 (carry · 변경 X)

1.4582 · 1.4019 · 89.1% (1,344/1,508) · -4.38% (median Δ%) · 5.77× · 5.70× · 5.65× · 92.7%/7.3% · 7/12 (cell, 58.3%) · 148/156 (plan, 94.9%) · +57 최적 plan · plan_same 96 / plan_diff 60 · plan_diff Δ% std 4.91 vs plan_same 2.82 ≈ 1.74× · 5,677 ms (pgvector 기본) · 977.6 ms (baseline) · 983.5 ms (결합) · 0.07× latency 격차

### 11.6 ★ Adaptive Sampling 정확 메커니즘 (carry)

- 한 쿼리 = N개 sample **1회** 추출 (무작위 베르누이) → cardinality 추정 → Q-error 계산
- **UPDATE PERIOD = 50 쿼리** batch — 누적 Q-error 로 조정 인자 δ → 모멘텀 m=0.9 → 학습률 η 감쇠 → N 갱신
- 초기 N=385 (식 1, 통계 신뢰도)

### 11.7 ★ 결합 메커니즘 (본 세션 신규 carry — 영상·slide 7 정합 base)

본 연구 = Adaptive Sampling **② cardinality 추정 단계** 의 단일 개입:
- baseline = 무작위 베르누이 sample 1개 → cardinality 단일 추정값
- 결합 (본 연구) = baseline + 분포 인지 추정값 **두 추정값 산술 평균**
- 정확한 cardinality → 정답 plan 선택 → 빠른 응답

### 11.8 ★ PPTX 검증 영구 룰 (본 세션 신규 carry)

Claude Design → PPTX export 시마다 의무 검증:
- LibreOffice → PDF → PNG vs Chrome MCP HTML screenshot 비교
- macOS PowerPoint 직접 open 검증 의무
- LibreOffice 변환 결과 ≠ PowerPoint 실제 렌더링 (Apple SD Gothic Neo fallback)
- 상세: `~/.claude/projects/-Users-hyunbin-Capstone/memory/feedback_pptx_export_verification.md`

### 11.9 ★ 발표물 영구 룰 4 (carry)

1. 약어 처음 등장 시 풀어쓰기
2. 텍스트 줄 정렬 일관성
3. 수치 강조보다 시각 자료 활용 우선
4. 청중 친숙 단어 우선

### 11.10 일반 룰 (carry · 변경 X)

- 측정 portfolio: 1,508 / 의도 max 3,600 = 41.9% 구조화 (full factorial 아님)
- A2-Fig8 4/16 method · A4-sel 희소 cell · WIKI sf=10 engine timeout · sf=1/100 engine 부분 — 의도된 한계
- 비가역 작업 (git push --force · DB DROP · rm -rf) — 사용자 사전 위임 없음
- handoff 룰: 종료 시 active 직전 archive → 신본 timecode 작성 ✓
- 사용자 commit OK (자율 위임) · push 명시 요청 시만
- ★ 다음 세션 진입 시 본 handoff 정독 + v3 PPTX 정본 carry · 스크린샷 vs 편집 가능 PPTX 비교 작업

## 12. 본 세션 핵심 의사결정 (다음 세션 carry)

1. **slide 1·4·6·7·8·9·10·11·12·13·14 순차 검토** + v18 → v19 5slide prompt 작성 (slide 2·3·5 박세은 피드백) → 사용자 적용 → 9 slide full prompt → v23 (13 slide) PPTX (v0) 생성

2. **사용자 forward-versioning 시스템 명시** — `속도는벡터_기말발표_v{N}.pptx` 순차 증가. v0 = 시작점, v1·v2·v3 = 수정 결과

3. **Chrome MCP + Gemini Ultra 병행 검증** — Chrome MCP 시각 + Gemini text-base 정합. Gemini 평결 = LearnUs 업로드 가능 (PASS) + 보완 3건 모두 발표 스크립트 수준

4. **사용자 피드백 누적 polishing** — v0 → v1 (9건) → v2 (6건) → v3 (영상 2 placeholder 추가, 14 slide 확장)

5. **★ slide 3 영상 placeholder 전환 + 새 slide 12 영상 placeholder 추가** — 사용자 명시 "한 페이지 = 영상 dominant" 컨셉. 영상 컨셉 = baseline (엔진 탑재 이전) + 결합 (최종 엔진) 작동 원리

6. **Gemini Veo 3.1 + Claude Design HTML animation 두 트랙 영상 prompt 작성** — 사용자 manual 진행. 영상 핵심 = Adaptive Sampling pipeline 안 ② cardinality 추정 단계 = 우리 연구 위치 highlight + 결합 메커니즘 (두 sample → 두 추정값 → 산술 평균) close-up

7. **★ PPTX 검증 영구 룰 작성** (사용자 명시 영구 룰) — Claude Design HTML preview ≠ LibreOffice PPTX→PDF 변환 ≠ PowerPoint 실제 렌더링. 의무 검증 절차 + macOS PowerPoint 직접 열기 의무 + 메모리 저장

8. **★ 다음 세션 critical task = 스크린샷 PPT vs 편집 가능 PPT 비교 → 편집 가능 PPTX 시각 정확 일치 fix** (사용자 명시 task) — 두 모드 PPTX export + 14 slide 페이지별 비교 + 차이 fix (Claude Design 보정 prompt 또는 PowerPoint manual)

9. **Gemini 영상 결과 받아 PowerPoint manual embed** — slide 3 + slide 12 placeholder 자리에 Insert Video

10. **LearnUs 업로드 + 5/27 발표** — 마감 5/26 23:59 (~10h 19m), 발표 5/27 (수) 15:00 D504

---

작성 2026-05-26 13:40 KST. v3 deck 14 slide 완성 (영상 2 placeholder slide 3·12) · forward-versioning v0~v3 시스템 · Gemini 영상 사용자 manual 진행 중 · 영구 룰 4 메모리 저장 (영상물 룰 + PPTX 검증 룰). 다음 = **스크린샷 PPT vs 편집 가능 PPT 시각 정밀 비교 + 편집 가능 PPTX 양식 시각 일치 fix** (사용자 명시 task) + PowerPoint 직접 열기 검증 + Gemini 영상 PPT embed + LearnUs 업로드 (5/26 23:59 마감 약 10h 19m 남음) + 5/27 발표 + 5/28 포스터·영상 + 6/11 보고서 carry.
