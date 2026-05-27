# handoff 20260527 00:50 KST — Task 1 (Q&A 31 질문 8 카테고리) 완료 → Task 2 (소개영상 5/28 12:00 마감 critical) carry

> 직전 handoff (`handoff_20260527_002900_QnA준비_소개영상제작_2task인계.md` → archive) → 본 문서. self-contained 0% loss 인계.
>
> **★ 핵심 한 줄 (본 세션 5/27 00:35–00:50 KST 완료)**: 사용자 명시 다음 세션 2 task 중 **Task 1 (최종발표 후 Q&A 30+ 예상 질문·답변)** 우선 진행 완료 (사용자 결정 — 최종발표가 오늘 5/27(수) 또는 5/29(금) 둘 다 가능하여 Q&A 준비가 더 급함). 31 질문 8 카테고리 학술 산문 한국어 신본 작성 + PDF 변환 (8 페이지·692KB). **★ 다음 세션 = Task 2 (포스터 첨부용 소개영상 제작, 5/28 12:00 LearnUs 마감 — 약 35 시간 남음 critical path)**.

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계
- **★ 직전 handoff (archive)**: `_internal/handoff/archive/handoff_20260527_002900_QnA준비_소개영상제작_2task인계.md`
- **★ 본 세션 신규 Q&A 신본 (Task 1 완료)**: `submission/_drafts/속도는벡터_QnA_예상질문_답변_20260527_004000.{md,pdf}` (md 37KB · PDF 692KB · 8 페이지)
- **★ 발표 제출본 (LearnUs 5/26 23:59 마감 완료)**: `submission/_drafts/archive/TEAM륾_최종발표자료.pdf` · `submission/_drafts/archive/TEAM륾_포스터.pdf` · `submission/_drafts/archive/속도는벡터_기말발표_v5.pptx` (5/26 commit b13ac961 cleanup 후 archive 이동, git status D 표시는 이동 표식)
- **★ 보고서 6/11 (carry, CaseC §4.2.3 포함)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.91 MB)
- **★ 학부생 알고리즘 설명 (직전 세션 신규, 발표 대본 자료)**: `submission/_drafts/속도는벡터_알고리즘_학부생수준_설명_paradigm_method별_20260527_001500.{md,pdf}` (890 KB) — 7 paradigm × 16 method 학부생 톤 친절 설명 + 발표 대본 활용 가이드 §9
- **★ 4 case raw 156 paired**: `submission/_drafts/archive/속도는벡터_plan회복_4case_raw_156paired_20260526_220000.csv` (cell·method·case·b1_qe·b1_lat·caseb_qe·caseb_lat·oracle_lat·baseline_lat·b1_correct·caseb_correct, 156 행)
- **★ storyline v4 carry (4-way 포함, 발표 X)**: `_drafts/archive/2026_05_26_postsubmit/storyline/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.{md,pdf}`
- **★ 영상 brief carry (이전 작성)**: `_drafts/archive/2026_05_26_postsubmit/video/속도는벡터_소개영상_Veo_3_1_brief_20260524_010021.md` + `속도는벡터_소개영상_storyboard_20260523_235540.md` + `_drafts/archive/2026_05_26_postsubmit/prompts/영상_4prompt_gemini_claude_design_5_26_13_00.md`

## 1. 본 세션 (5/27 00:35 → 00:50 KST · 15 min) 완료 작업

| Phase | 작업 | 산출 |
|:--:|---|---|
| 1 | 정본 4종 정독 (보고서 §4.7 honest limitation 5–8종 + §5.3 plan recovery + §5.4 paired Wilcoxon 효과크기 + §5.6 4-way carry · 학부생 §9 발표 대본 활용 가이드 · 4 case raw 156 paired csv 11 cols · 학부생 §9 우선순위) | parallel Read·Bash 6 호출 |
| 2 | Task 1 신본 작성 — Q&A 예상 질문·답변 8 카테고리 31 질문 (A 연구 framing 4 · B 측정 방법론 4 · C 결과 해석 5 · D method 별 권장 4 · E plan 회복 vs latency 4 · F honest limitation 4 · G future work 3 · H 민감 질문 3) | `submission/_drafts/속도는벡터_QnA_예상질문_답변_20260527_004000.md` (37KB) |
| 3 | md → PDF 변환 (`_internal/scripts/md2pdf.py` compact, Apple SD Gothic Neo) | `submission/_drafts/속도는벡터_QnA_예상질문_답변_20260527_004000.pdf` (692KB · 8 페이지) |
| 4 | handoff archive + 신본 작성 | 본 파일 |
| 5 | TaskCreate 4건으로 진행 추적 (Q&A md · PDF · handoff · commit) | 본 세션 task 4건 모두 in_progress→completed |

## 2. ★★★ 다음 세션 task

### Task 2 (★★ critical · 5/28 12:00 마감 · 약 35 시간 남음) — 포스터 첨부용 소개영상 제작 (음성 포함)

**목적**: 5/28 (목) 12:00 LearnUs 포스터·영상 마감 — **포스터 우측 QR 첨부용 2-3분 소개영상**.

**도구 결정 (carry 분석, 두 path 선택지)**:

| Path | 장점 | 단점 | 시간 |
|---|---|---|---|
| **A. Gemini Veo 3.1 + 외부 TTS + DaVinci/Clipchamp** | cinematic 합성 가능, native audio = 효과음 | 한 segment 최대 8초 → 18-22 segment 다중 합성 필요, 외부 결합 도구 학습 | 3-4 시간 |
| **B. ★ Claude Design HTML + `<audio>` + 화면 녹화 (OBS/QuickTime)** | 학술 도식·그래프 정밀 (carry deck 와 동일 도구), 2-3분 단일 HTML, narration 완벽 sync | mp4 직접 export X (화면 녹화 필요), 한국어 TTS 외부 (ElevenLabs/Naver Clova) | **1-2 시간** (추천) |

**B path 선택 시 워크플로우** (5 단계, 약 1-2시간):

1. **한국어 narration script 작성** — Gemini 3.1 Pro 또는 Claude (carry 학부생 설명 §7 + §9 + ★ 본 세션 Q&A 신본 §C-1·E-1·F-1 활용, 2-3분 = ~450-500 단어)
2. **한국어 TTS mp3 생성** — ElevenLabs Korean voice "Yuna" (학술 발표 톤) 또는 Naver Clova Speech (무료)
3. **Claude Design HTML animation 생성** — claude.ai/design 대화창 `/p/019e1a41-701c-7134-9ce1-1247262c1563` carry (사용자 명시 영구 대화창). 6 단계 시퀀스 (각 25-30초) × `<audio>` autoplay sync
4. **OBS Studio (Mac/Windows 무료) 또는 QuickTime Cmd+Shift+5** 화면 녹화 → mp4
5. **YouTube Unlisted 업로드** → URL → qr-code-generator.com → PNG → 포스터 우측 footer

**narration script 6 단계 구조 (★ 본 세션 Q&A 신본 활용)**:
- 0:00-0:25 ① VAQ 시나리오 (ICDE 차용)
- 0:25-0:50 ② Exqutor 두 메커니즘 + 본 연구 위치 (§V-B 표본 선택 한 단계) — Q&A §A-1
- 0:50-1:15 ③ 통제 실험 3 방식 (베이스라인·단독 대체·결합) — 1,508 cell × 3 = 4,524 짝 비교 — Q&A §A-3
- 1:15-1:45 ④ 89.1% 우위 + 단독 대체 35.2% 음성 대조군 → 메커니즘 = 결합 형태 효과 — Q&A §C-1·C-2
- 1:45-2:15 ⑤ 엔진 적용 — 5.67× 가속 · plan 회복 94.9% · 추정 ↑ ≠ latency ↑ — Q&A §E-1·E-3
- 2:15-2:30 ⑥ 본 연구 기여 + 팀 소개 — Q&A §H-3 (negative result 의 학술적 가치)

**참조 정본**:
- `_drafts/archive/2026_05_26_postsubmit/video/속도는벡터_소개영상_storyboard_20260523_235540.md` — 5분 8 slide storyboard (압축 base)
- `_drafts/archive/2026_05_26_postsubmit/video/속도는벡터_소개영상_Veo_3_1_brief_20260524_010021.md` — Veo brief carry
- `_drafts/archive/2026_05_26_postsubmit/prompts/영상_4prompt_gemini_claude_design_5_26_13_00.md` — 5/26 13:00 작성, baseline + 결합 15초 cinematic prompt
- ★ `submission/_drafts/속도는벡터_QnA_예상질문_답변_20260527_004000.{md,pdf}` — 본 세션 Q&A 신본, narration script 작성 시 §A·C·E·H 직접 인용

### Task 1 결과 — 완료 (carry)

본 세션 완료. 5/27(수)·29(금) 최종발표 양일 후 Q&A 시간 (각 5분 안팎) 대비 발표자 reference 산출 — 31 질문 8 카테고리. 발표자 (조현빈) 가 발표 직전 약 30분 reading 만으로 모든 카테고리 핵심 답변·정량 수치를 reproduce 할 수 있도록 작성.

## 3. ★ 본 세션 신규 산출물 — Q&A 신본 (Task 1)

### 3.1 8 카테고리 31 질문 구성

| # | 카테고리 | 질문 수 | 핵심 질문 (대표 1건) |
|:--:|---|:--:|---|
| A | 연구 framing·범위 | 4 | "Exqutor 논문의 어떤 단계만 다루는가? 왜 §V-B Adaptive Sampling 의 표본 선택 단계 하나만 골랐는가?" |
| B | 측정 방법론 | 4 | "왜 1,508 cell 인가? 5 데이터셋 × 5 조작변인 × 16 method 인데 어떻게 1,508 이 나왔는가?" |
| C | 결과 해석 | 5 | "★ '결합 89.1% 우위' 의 메커니즘은 분포 인지 효과인가, 평균 효과인가? 어떻게 가렸는가?" |
| D | method 별 권장 | 4 | "offline q-error 1위 chao_weighted 의 권장 근거는?" |
| E | plan 회복 vs latency | 4 | "plan 회복률 94.9% 인데 latency 동등 (86.9% small effect) 이라는 게 모순 아닌가?" |
| F | 본 연구 honest limitation | 4 | "다중 벡터 이상치 2건은 무엇이고 왜 그것이 평균을 흔드는가?" |
| G | future work | 3 | "본 연구의 결과를 다른 벡터 DB (Milvus·Qdrant 등) 에서도 재현할 수 있을지?" |
| H | 민감 질문 | 3 | "★ 왜 발표에서 CaseC (dual-Bernoulli ensemble) 결과는 빼는가?" · "★ 본 연구의 핵심 음성 결과가 본 연구를 부정적으로 만드는 것 아닌가?" |
| **합계** | **8 카테고리** | **31** | — |

### 3.2 답변 톤 통일 룰 (Q&A 신본 §마무리 carry)

- **한국어 라벨**: 베이스라인·단독 대체·결합·정답 (코드명 B1·CaseA·CaseB·CaseC 는 보강 시만 괄호 병기)
- **정량 우선**: 89.1%·−4.38%·5.67×·94.9%·89.2%·1.1%·100% (180/180)·86.9% (146/168) 등 정본 수치 직접 인용
- **honest limitation 정직 답변** — 회피 X · "한계는 한계로 보고한다" · 본 연구의 학술적 정직성 자체가 contribution
- **모르면 모른다고 답** — 환각 금지 · §4.7 honest limitation 5–8종 (Codex BLOCKER E re-review 3종 carry) 명시

### 3.3 3분 안 핵심 우선순위 (Q&A 신본 §마무리 carry)

1. **A-1 단일 개입 framing** — Exqutor §V-B 표본 선택 단계 하나만 (40초)
2. **C-1 결합 89.1% 우위 메커니즘 — 분포 인지 X · 두 독립 추정량 평균 효과 (앙상블)** — 통제군 CaseC 95/95 = 100% 우위로 입증 (40초)
3. **D-1 chao_weighted offline 1위 · mhist2 엔진 plan 1위 · pca1d 균형 1위** (30초)
4. **E-1 plan recovery 94.9% vs latency 동등 86.9% — 추정 정확도 ↑ ≠ latency ↑ 비대칭 구조** (40초)
5. **F-1·F-2 honest limitation** — 다중 벡터 이상치 2건 · method 명칭 정직성 8 method (30초)

## 4. 산출물 경로 (총정리)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260527_005000_QnA완성_소개영상Task2carry.md` | 본 파일 |
| ★ 직전 handoff (archive) | `_internal/handoff/archive/handoff_20260527_002900_QnA준비_소개영상제작_2task인계.md` | archive |
| ★ **Q&A 신본 (본 세션 신규, Task 1 완료)** | `submission/_drafts/속도는벡터_QnA_예상질문_답변_20260527_004000.{md,pdf}` (37KB md · 692KB PDF 8 페이지) | **5/27·29 발표 reference** |
| ★ 발표 제출본 (5/26 LearnUs 마감 완료) | `submission/_drafts/archive/TEAM륾_최종발표자료.pdf` · `archive/TEAM륾_포스터.pdf` · `archive/속도는벡터_기말발표_v5.pptx` (22MB) | 제출 완료 |
| ★ 보고서 6/11 신본 | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.91 MB) | 6/11 마감 |
| ★ 학부생 알고리즘 설명 (직전 세션 신규) | `submission/_drafts/속도는벡터_알고리즘_학부생수준_설명_paradigm_method별_20260527_001500.{md,pdf}` (890 KB) | 발표 대본 자료 |
| ★ 4 case raw 156 paired | `submission/_drafts/archive/속도는벡터_plan회복_4case_raw_156paired_20260526_220000.csv` | slide 13 데이터 |
| ★ 영상 storyboard carry (5분 8 slide) | `_drafts/archive/2026_05_26_postsubmit/video/속도는벡터_소개영상_storyboard_20260523_235540.md` | Task 2 base |
| ★ Veo 3.1 brief carry | `_drafts/archive/2026_05_26_postsubmit/video/속도는벡터_소개영상_Veo_3_1_brief_20260524_010021.md` | Task 2 base |
| ★ 영상 4 prompt (baseline + 결합 15초) | `_drafts/archive/2026_05_26_postsubmit/prompts/영상_4prompt_gemini_claude_design_5_26_13_00.md` | Task 2 carry |

## 5. 환경·자원 (carry · 변경 X)

- 서버 1007 GB · CPU 128 vCPU · 4× RTX 6000 Ada · uptime 11+ days
- 자원 watchdog v6 256GB SIGSTOP/CONT 서버 가동 중 (PID 1769596 carry)
- PG port 55435
- 본 세션 commit 0건 (Task 1 작성·PDF 변환·handoff 신본 작성만 — commit·push 는 다음 작업 단위에서 일괄 진행)
- macbook .claude rsync 양방향 carry (직전 세션 완료)

## 6. 일정 (carry · 변경 X · ★ 마감 시간 critical)

- **5/27 (수) 오늘** ★ 최종발표 1차 — Q&A 준비 (Task 1) 완료. 발표자 reference reading 30분 권장
- **5/28 (목) 12:00** ★★ 포스터·영상 LearnUs 마감 — **소개영상 제작 (Task 2) critical, 약 35 시간 남음**
- **5/29 (금)** 최종발표 2차 — Q&A 준비 (Task 1) 동일 활용
- **6/5 (금)** 전시회
- **6/11 (목) 23:59** 최종 보고서·상호평가 결과 마감

## 7. 환각 회피 룰 (carry · 본 세션 변경 X)

- 발표는 **3-way (B1·CaseA·CaseB) 만**, CaseC 제외 carry (5/24 회의 결정)
- 한국어 라벨 통일 (베이스라인·단독 대체·결합) · 코드명 노출 금지
- v13 1,508 cell 정본 (3-way matched) · v14·v15·v16 CaseC carry · 12 cell engine carry — 모두 진짜 측정
- 89% Q-error 우위 = 분포 인지 X · 결합 형태에 가치 (음성 대조군 CaseA 입증) · 95 측정 전수 100% 재확인 (carry §4.2.3)
- 엔진 latency 4 inject 동등 (|Δ%| ≤ 1.12%) · 추정 정확도 ↑ ≠ latency ↑ 구조적 한계
- plan 회복 4 case (TP 90·FN 1·FP 58·TN 7) — 결합 회복률 89.2% · 망친 비율 1.1% 비대칭 우위
- method ranking carry — chao_weighted offline 1위 · mhist2 engine 1위 · pca1d 균형 1위
- 측정 범위 honest carry — engine = **DEEP sf=10 only · sel=0.001 본문 12 cell** (Phase 3 sel=0.01·0.1 carry-over 8 cell)
- 비가역 작업 carry · push 사용자 명시 시만
- handoff 룰 — active 직전 archive → 신본 timecode 작성 ✓

---

작성: 2026-05-27 00:50 KST. 본 세션 = Task 1 (Q&A 31 질문 8 카테고리) 완료 + 학술 산문 한국어 신본 작성 + PDF 변환 (8 페이지) + handoff 신본. **다음 세션 = Task 2 (소개영상 제작) critical path** — 5/28 12:00 마감 약 35 시간 남음. Q&A 신본 §C-1·E-1·F-1·H-3 narration script 6 단계 직접 활용 가능.
