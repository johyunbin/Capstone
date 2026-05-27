# handoff 20260527 13:45 KST — Task 2 (소개영상) 1단계 완료: Veo 3.1 19 segment cinematic prompt 작성 → 2단계 (사용자가 Gemini Ultra Veo 3.1 실행) carry

> 직전 handoff (`handoff_20260527_005000_QnA완성_소개영상Task2carry.md` → archive) → 본 문서. self-contained 0% loss 인계.
>
> **★ 핵심 한 줄 (본 세션 5/27 13:30–13:45 KST 완료)**: 사용자 명시 (5/27 13:30 KST) — "**슬라이드 넘기는 방식 말고 영상 자체로 흐름 이어갈 수 있게 제미나이나 veo로 그렇게 제작**" + "**gemini veo만 적극 활용해서 만들려고. 오디오랑 같이**". 본 세션은 **cinematic 영상 흐름 19 segment × 8초 = 2:32 short film** 의 Veo 3.1 (Ultra) 직접 복붙 prompt 19 개를 작성 완료. 다음 단계 = 사용자가 Gemini Ultra Veo 3.1 에서 19 prompt 순차 실행 → segment mp4 19 개 → Gemini Flow / DaVinci 합성 → YouTube Unlisted → QR → 포스터. **5/28 12:00 LearnUs 영상·포스터 마감 — 약 22 시간 남음 critical path**.

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계
- **★ 직전 handoff (archive)**: `_internal/handoff/archive/handoff_20260527_005000_QnA완성_소개영상Task2carry.md`
- **★ 본 세션 신규 산출 (Task 2 1단계 완료)**: `submission/_drafts/속도는벡터_소개영상_Veo3_1_cinematic_19segment_20260527_134000.{md,pdf}` (md 31KB · PDF 754KB · 13 페이지)
- **★ Q&A 신본 (직전 세션, 5/27 발표 대비 reference)**: `submission/_drafts/속도는벡터_QnA_예상질문_답변_20260527_004000.{md,pdf}` (37KB md · 692KB PDF 8 페이지)
- **★ 발표 제출본 (LearnUs 5/26 23:59 마감 완료)**: `submission/_drafts/archive/TEAM륾_최종발표자료.pdf` · `submission/_drafts/archive/TEAM륾_포스터.pdf` · `submission/_drafts/archive/속도는벡터_기말발표_v5.pptx`
- **★ 보고서 6/11 (carry)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.91 MB)
- **★ 학부생 알고리즘 설명 (5/27 carry)**: `submission/_drafts/속도는벡터_알고리즘_학부생수준_설명_paradigm_method별_20260527_001500.{md,pdf}`
- **★ 4 case raw 156 paired**: `submission/_drafts/archive/속도는벡터_plan회복_4case_raw_156paired_20260526_220000.csv`
- **★ 영상 storyboard carry (5분 8 slide base 폐기 — 본 세션 19 segment cinematic 으로 전환)**: `submission/_drafts/archive/2026_05_26_postsubmit/video/속도는벡터_소개영상_storyboard_20260523_235540.md`
- **★ 영상 Veo brief carry (이전 작성)**: `submission/_drafts/archive/2026_05_26_postsubmit/video/속도는벡터_소개영상_Veo_3_1_brief_20260524_010021.md`

## 1. 본 세션 (5/27 13:30 → 13:45 KST · 15 min) 완료 작업

| Phase | 작업 | 산출 |
|:--:|---|---|
| 1 | 사용자 결정 받기 (AskUserQuestion 2 질문) — 영상 길이·구조 + 제작 path | "슬라이드 transition 폐기 · cinematic 영상 흐름 · Gemini Veo only · native audio" |
| 2 | carry 정독 — storyboard 5분 8 슬라이드 base, 5/20 Phase 2 신설 11b·11c, 영상 4 prompt 5/26 13:00 작성 | 정본 3 종 carry 정독 완료 |
| 3 | cinematic scene script v2 작성 — 6 막 19 segment 구조 (도입·본 연구 위치·통제 실험·89.1% 우위·5.67× 가속·기여) | md §1 |
| 4 | Veo 3.1 prompt 19 개 작성 — 각 8 초 segment cinematic 형식 (VISUAL · CAMERA · LIGHTING · MOOD · KOREAN AUDIO NARRATION · KOREAN SUBTITLE · SOUND EFFECTS · MUSIC) | md §2 |
| 5 | 합성 workflow 작성 — Gemini Flow / DaVinci Resolve / Clipchamp 3 옵션 + YouTube Unlisted + QR 생성 + 포스터 통합 | md §3 |
| 6 | 환각 회피 룰 + 핵심 수치 + Q&A 신본 carry 반영 위치 명시 | md §4·5·6 |
| 7 | md → PDF 변환 (compact, Apple SD Gothic Neo) | 13 페이지 PDF |
| 8 | handoff archive + 신본 작성 | 본 파일 |

## 2. ★★★ 다음 세션 task — Task 2 2단계 (사용자 진행)

### Task 2.2 (★★ critical · 5/28 12:00 마감 약 22 시간 남음) — Gemini Ultra Veo 3.1 실행 + 합성

**목적**: 본 세션 산출 19 segment prompt 를 Gemini Ultra Veo 3.1 (preview) 에서 실행 → 19 mp4 segment 회수 → 합성 → final.mp4 → YouTube Unlisted → QR → 포스터.

**5 단계 워크플로우** (예상 시간 3-4 시간):

1. **Gemini Ultra 앱 접속** — https://gemini.google.com (AI Ultra 구독 carry)
2. **Veo 3.1 model 선택** — 모델 선택 메뉴에서 "Veo 3.1 (preview)" + Image-to-Video 옵션 검토
3. **19 prompt 순차 실행** — 본 세션 산출 `submission/_drafts/속도는벡터_소개영상_Veo3_1_cinematic_19segment_20260527_134000.md` §2 의 Segment 1A → 6B 까지 19 개 prompt 를 Gemini Veo 3.1 에 복붙 → 각 prompt 당 약 2-5 분 generation → 8 초 mp4 다운로드 (파일명 `segment_<NN>_<scene>.mp4`)
4. **품질 검수** — 각 segment 의 (a) 비주얼 일관성 (navy + 청록 톤) (b) 한국어 narration 발음 정확성 (c) 한국어 자막 burn-in 가독성. 미흡하면 prompt 미세 조정 후 재생성.
5. **합성** — 옵션 A: Gemini Flow (추천, Ultra 한도, cross-dissolve 0.3-0.5초 자동) / 옵션 B: DaVinci Resolve (무료, 학습 30 분) / 옵션 C: Clipchamp (Windows 무료, 가장 단순) → final.mp4 (1080p, H.264, AAC)
6. **YouTube Unlisted 업로드** + **QR 생성** (qr-code-generator.com 또는 `python3 -c "import qrcode; img=qrcode.make('https://youtu.be/XXX'); img.save('/tmp/yt_qr.png')"`) → **포스터 우측 footer 갱신** → LearnUs 마감 전 final 제출

### Task 2.2 의 중간 결정 사항 (사용자 진행 중 carry)

- **narration 음성 톤** — Veo 3.1 native audio 가 자동 한국어 voice 생성, 톤 미흡 시 prompt 의 "(calm academic male voice, slow pace)" 부분 미세 조정
- **자막 한글 폰트** — Apple SD Gothic Neo (Veo 3.1 가 자동 렌더링하지 못하면 후처리 자막 burn-in 별도 진행 — 일반적 비디오 편집 도구에서 SRT 파일 import)
- **background music** — Veo 3.1 native music 이 19 segment 간 끊김 발생 시 합성 단계에서 audio crossfade 0.3 초 적용 또는 별도 background music track 추가 (CC0 cinematic ambient)
- **재생 도중 멈춤 점검** — final.mp4 합성 후 핸드폰에서 QR scan → 영상 끝까지 재생 + 자막 표시 + audio 정상 출력 확인

### Task 2.3 (보조 · 사용자 진행 시 carry)

- 보고서 6/11 마감 (carry, §4.2.3 CaseC 포함)
- 5/29 (금) 최종발표 2차 Q&A 동일 reference 사용

## 3. ★ 본 세션 신규 산출 핵심 요약

### 3.1 영상 사양

| 항목 | 값 |
|---|---|
| 총 길이 | **2:32 (152 초)** |
| Segment | **19 개 × 8 초** |
| 해상도 | 1920 × 1080, 24fps |
| 오디오 | Veo 3.1 native audio (한국어 narration + 효과음 + soft cinematic music) |
| 자막 | 한국어 burn-in (Apple SD Gothic Neo, white + navy shadow) |
| 톤 | 학술 발표 · 정중 · 차분 · cinematic |

### 3.2 cinematic 6 막 구조

| 막 | 시간 | segment | 핵심 메시지 | hero shot |
|:--:|---|:--:|---|---|
| **I 도입** | 0:00–0:24 | 3 (1A·1B·1C) | VAQ 시나리오 + 33.3·50·100 한계 | 분석가 SQL 작성 |
| **II 본 연구 위치** | 0:24–0:48 | 3 (2A·2B·2C) | Exqutor §V-B 표본 선택 한 곳만 개입 | §V-B 5 단계 도식 |
| **III 통제 실험** | 0:48–1:12 | 3 (3A·3B·3C) | 4 mode matched 1,508 cell | 4 갈래 도식 |
| **IV 89.1% 우위** | 1:12–1:44 | 4 (4A·4B·4C·4D) | 89.1% + 35.2% 음성 → 앙상블 효과 | hero "89.1%" |
| **V 엔진 적용** | 1:44–2:16 | 4 (5A·5B·5C·5D) | 5.67× 가속 + 94.9% 회복 · 추정 ↑ ≠ latency ↑ | hero "5.67×" + "94.9%" |
| **VI 기여·팀** | 2:16–2:32 | 2 (6A·6B) | 기여 4 + 속도는벡터 팀 5 인 + 지도진 3 인 | 팀 + BDAI 로고 |

### 3.3 핵심 정량 수치 (Veo prompt 안 직접 사용)

- Segment 4A hero **89.1%** (1,344/1,508 cell)
- Segment 4B **−4.38%** (paired Δ% 중앙값)
- Segment 4C **35.2%** (단독 대체 better, 음성 대조군)
- Segment 5B hero **5.67×** (12 cell 평균 가속)
- Segment 5C hero **94.9%** (plan 회복, 148/156)
- Segment 5C 보조 **89.2%** · **1.1%** (결합 회복률 vs 망친 비율 비대칭)
- Segment 5D **86.9% small effect** (latency 동등)

## 4. 산출물 경로 (총정리)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260527_134500_소개영상_Veo3_1_19segment_prompt완성.md` | 본 파일 |
| ★ 직전 handoff (archive) | `_internal/handoff/archive/handoff_20260527_005000_QnA완성_소개영상Task2carry.md` | archive |
| ★ **소개영상 Veo 3.1 19 segment 정본 (본 세션 신규)** | `submission/_drafts/속도는벡터_소개영상_Veo3_1_cinematic_19segment_20260527_134000.{md,pdf}` (31KB md · 754KB PDF 13 페이지) | **사용자 Veo 3.1 실행 reference** |
| ★ Q&A 신본 (직전 세션, 5/27·29 발표 reference) | `submission/_drafts/속도는벡터_QnA_예상질문_답변_20260527_004000.{md,pdf}` (37KB md · 692KB PDF 8 페이지) | 발표 reference |
| ★ 발표 제출본 (5/26 LearnUs 마감 완료) | `submission/_drafts/archive/TEAM륾_최종발표자료.pdf` · `archive/TEAM륾_포스터.pdf` · `archive/속도는벡터_기말발표_v5.pptx` | 제출 완료 |
| ★ 보고서 6/11 신본 | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.91 MB) | 6/11 마감 |
| ★ 학부생 알고리즘 설명 (5/27 carry) | `submission/_drafts/속도는벡터_알고리즘_학부생수준_설명_paradigm_method별_20260527_001500.{md,pdf}` | 발표 대본 자료 |
| ★ 4 case raw 156 paired | `submission/_drafts/archive/속도는벡터_plan회복_4case_raw_156paired_20260526_220000.csv` | slide 13 데이터 |

## 5. 환경·자원 (carry · 변경 X)

- 서버 1007 GB · CPU 128 vCPU · 4× RTX 6000 Ada · uptime 11+ days
- 자원 watchdog v6 256GB SIGSTOP/CONT 서버 가동 중
- PG port 55435
- macbook .claude rsync 양방향 carry (직전 세션 완료)
- ★ **Gemini AI Ultra 구독 carry** — Veo 3.1 (preview) 한도 사실상 자유 (사용자 영구 활용 명시 5/24 carry)

## 6. 일정 (carry · 변경 X · ★ 마감 critical)

- **5/27 (수) 오늘** ★ 최종발표 1차 — Q&A reference reading 30분 권장 (Q&A 신본 §마무리 3분 안 핵심 5개 항목)
- **5/28 (목) 12:00** ★★★ **포스터·영상 LearnUs 마감 — 영상 제작 Task 2.2 critical, 약 22 시간 남음**
- **5/29 (금)** 최종발표 2차 — Q&A 신본 동일 reference 활용
- **6/5 (금)** 전시회
- **6/11 (목) 23:59** 최종 보고서·상호평가 결과 마감

## 7. 환각 회피 룰 (carry · 본 세션 변경 X)

- 발표는 **3-way (B1·CaseA·CaseB) 만**, CaseC 제외 carry (5/24 회의 결정)
- 한국어 라벨 통일 (베이스라인·단독 대체·결합) · 코드명 노출 금지 (영상에도 동일)
- v13 1,508 cell 정본 · v14·v15·v16 CaseC carry · 12 cell engine carry — 모두 진짜 측정
- 89% Q-error 우위 = 분포 인지 X · 결합 형태에 가치 (음성 대조군 CaseA 입증) · 95 측정 전수 100% 재확인 (carry §4.2.3)
- 엔진 latency 4 inject 동등 (|Δ%| ≤ 1.12%) · 추정 정확도 ↑ ≠ latency ↑ 구조적 한계
- plan 회복 4 case (TP 90·FN 1·FP 58·TN 7) — 결합 회복률 89.2% · 망친 비율 1.1% 비대칭 우위
- method ranking carry — chao_weighted offline 1위 · mhist2 engine 1위 · pca1d 균형 1위
- 측정 범위 honest carry — engine = **DEEP sf=10 only · sel=0.001 본문 12 cell**
- 비가역 작업 carry · push 사용자 명시 시만
- handoff 룰 — active 직전 archive → 신본 timecode 작성 ✓
- ★ **영상 cinematic 흐름** — 슬라이드 transition 폐기 · 영상 컨텐츠 자체 흐름 · Veo 3.1 native audio + 한국어 자막 burn-in

---

작성: 2026-05-27 13:45 KST. 본 세션 = Task 2 1단계 (Veo 3.1 19 segment cinematic prompt 작성) 완료. 다음 세션 = **사용자가 Gemini Ultra Veo 3.1 에서 19 prompt 순차 실행 → 합성 → YouTube Unlisted → QR → 포스터 통합**. 5/28 12:00 영상·포스터 마감 약 22 시간 남음 critical path. cinematic 19 segment × 8초 = 2:32 short film, native audio 한국어 narration + 자막 burn-in.
