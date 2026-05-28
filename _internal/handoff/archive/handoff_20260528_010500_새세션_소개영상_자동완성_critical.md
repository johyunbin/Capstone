# handoff 20260528 01:05 KST — 새 세션 자동 인계: 소개영상 완성 (Chrome MCP 화면 제어) · 5/28 12:00 마감 critical

> **★ self-contained 0% loss 인계. 본 문서 하나로 새 세션이 모든 컨텍스트 파악 + 즉시 작업 시작.**
>
> **★ 사용자 명시 5/28 01:00 KST 전권 위임 (verbatim)**:
> > "새로운 세션 시작해줄테니까 새벽동안에 너가 mcp로 크롬제어해서 진행해. 토큰 무한이니까. 전권 위임함. 무조건 아침에 완료된 상태로 보고해야 함. 완료 전까지는 chrome 제어 유지할거야. 다음 세션 인계해서 바로 진행하자"
>
> **★ 목표**: 아침 (5/28 07:00-09:00 추정) 사용자 일어났을 때 = **한국어 음성 + 한국어 자막 burn-in 완료된 mp4 + YouTube Unlisted 업로드 + QR + 포스터 갱신 = LearnUs 12:00 마감 final 제출 준비 완료** 상태.
>
> **★ 완료 전까지 멈춤 X. 완료 후만 보고**. Chrome MCP 끊김 발생 시 재연결 + 작업 재개. Veo 깨짐 발생 시 재시도. 모든 자동화 가능 단계 진행. **불가능한 경우만 보고 + 사유 명시**.

---

## 0. 즉시 진행 (새 세션 첫 작업)

### 0.1 Chrome MCP 연결

```
1. mcp__Claude_in_Chrome__list_connected_browsers
2. macmini deviceId = "644dba75-3349-4c8d-ba29-1507743d45a5" → 자동 select_browser
   (사용자 영구 위임 룰 carry — AskUserQuestion 없이 macmini 자동 선택)
3. mcp__Claude_in_Chrome__tabs_context_mcp (createIfEmpty: true)
4. navigate to Flow 프로젝트 URL (아래 §1.1)
5. screenshot → 현재 상태 확인
```

### 0.2 핵심 자료 정독

| 자료 | 경로 | 용도 |
|---|---|---|
| ★ **본 handoff** | `_internal/handoff/active/handoff_20260528_010500_*.md` | 본 문서 |
| ★ **강화 prompt 8개** | `submission/_drafts/속도는벡터_소개영상_강화prompt_8개_20260528.md` | Flow chat 복붙 |
| ★ **26 Veo prompt 정본** | `submission/_drafts/속도는벡터_소개영상_slide14_26segment_Veo_20260527_235800.md` | 누락 segment prompt |
| ★ **한국어 자막 SRT** | `submission/_drafts/속도는벡터_소개영상_한국어자막_SRT_20260528.srt` | FFmpeg burn-in 입력 |
| ★ **아침 진행 가이드** | `submission/_drafts/속도는벡터_소개영상_아침진행가이드_20260528.md` | 6 단계 step-by-step |
| 발표 스크립트 | `submission/제출완료/기말발표_스크립트.pdf` | narration 정본 |
| 발표 슬라이드 | `submission/제출완료/속도는벡터_기말발표.pptx` | 시각 base |

---

## 1. Flow 프로젝트 상태 (현재)

### 1.1 Flow URL
```
https://labs.google/fx/ko/tools/flow/project/8fc58d63-6239-42d6-816f-bac3fb337ce2
```

### 1.2 Flow 설정 (`에이전트 설정`, 우측 패널)

- 동영상 모델 = **Veo 3.1 - Quality** ✓ 설정 완료
- 비율 = 16:9 ✓
- 횟수 = 1x ✓
- 생성 전 확인 = "안 함" 으로 변경 권장 (자동 진행 위해)

### 1.3 정상 segment 확보 (약 10-12 박스, 검수 완료)

| Segment | 영상 안 텍스트 | 위치 매핑 |
|---|---|---|
| **5A** Sampling: 4 Steps ✓ | "Sampling: 4 Steps" | 정정안 성공 |
| **7A** 3 Modes ✓ | "3 Modes" + X 표시 timeline | 정정안 성공 |
| **8A** DATASETS · VARIABLES ✓ | "DATASETS (5) VARIABLES (4)" + 보라 막대 | 원본 정상 |
| **11B** Optimal Plan Selection ✓ | "Optimal Plan Selection" + 작은 점 | 원본 정상 |
| **12B** 5.70× hero ✓ | "5.70x" timeline 7 frame 정확 | 정정안 성공 (좌상 위치) |
| **13A** Future ✓ | "Future" + "Future Work Two Directions" | 원본 정상 |
| **14A** THANK YOU ✓ | "- THANK YOU" + "Q&A welcome" | 원본 정상 |
| **3B** 도식 ✓ (텍스트 X) | 빨강·파랑 우산 split panel | "Two panels showing estimates" |
| **3A** Cardinality and Selectivity ✓ (희미) | "Cardinality and Selectivity" | 정상 추정 |
| **2C** Optimizer ✓ (텍스트 X) | 톱니바퀴 + 3 화살표 | 정상 시각 |
| **2A** Vector ✓ (희미) | "Vector" 텍스트 | 정상 추정 |

### 1.4 삭제 완료 (12 깨짐 박스, 5/28 01:00 KST 작업)

- 11A 정정안 "Engine Latentcy" ✗
- 6A 정정안 "Better sampulling" ✗
- 12A "Compled Method" ✗
- 12B 원본 "Commanted final methron" ✗
- 11C "Latency Sanne, Staboly" ✗
- 실패 박스 1건
- 9A 원본·정정안 "Methoos Paradipms" ✗
- 8B "5 disbulees x ~f1" ✗
- 7A 원본 "Tiree Essedention" ✗
- 5B 원본 "Sample Size N adglists" ✗
- 5A 원본 "Adaltive Sampling" ✗
- "1n" (4B 추정) ✗

### 1.5 누락 segment (재진행 필요, **새 세션이 진행할 핵심 작업**)

**강화 정정 prompt 8개** (`강화prompt_8개_20260528.md` 정본 carry, Flow chat 복붙):
1. **11A** Engine Speed 3 bars (5,677·977.6·983.5 ms)
2. **9A** 13 + 7 Groups + P1-P7
3. **6A** Research Q (Better way?)
4. **8B** 1,508 hero (= 1,508 cells)
5. **11C** Same Time, Better Plan
6. **5B** Sample N over Time (B1·B2·B3)
7. **4B** Exqutor No Index
8. **12A** Final Engine

**누락 segment prompt** (`slide14_26segment_Veo_20260527_235800.md` §2 carry):
- **1A** 표지 (인덱스 부재 시 Adaptive Sampling 개선)
- **2A·2B·2C** VAQ 정의·SQL·optimizer (2A·2C 일부 정상, 2B 추가)
- **3A·3C** Cardinality 정의·10,000× (3A 일부 정상, 3C 추가)
- **4A** 33.3%·50%·100% 고정 비율
- **10A** 89.1% hero (1,344/1,508)
- **10B** baseline 1.4582 vs 결합 1.4019

**합산**: 강화 8 + 누락 7 = **약 15 prompt 입력 필요** (이미 정상인 segment 제외).

---

## 2. ★ 새 세션 작업 단계 (자동 진행)

### Phase 1: Flow prompt 입력 (예상 60-90분)

**Action**:
1. Flow chat 입력창 (우하단, 좌표 ~575, 988 또는 화면 layout 에 따라 보정) 클릭
2. 강화 prompt 1번 (11A Engine Speed) **type** → 화살표 click (좌표 ~806, 988)
3. AI assistant 응답 + Approve 자동 ("do not ask again" 모드 활성화 권장)
4. **다음 prompt 입력 (generation 완료 대기 X)** — Flow 가 generation queue 에 push
5. 강화 prompt 2번·3번··· 8번 연속 입력
6. 누락 prompt 7개 연속 입력
7. 모든 prompt 입력 후 wait + 모든 generation 완료 (약 30-40분)

**Chrome MCP 끊김 발생 시**:
- 자동 재연결: `list_connected_browsers` → `select_browser` (macmini deviceId)
- 화면 복귀: `tabs_context_mcp` → `navigate` 또는 기존 tab 사용
- 남은 prompt 입력 재개

### Phase 2: Generation 결과 검증 + 깨진 것 재시도 (예상 30-60분)

**Action**:
1. 모든 미디어 view → 각 박스 click → edit view → timeline 끝 click → screenshot → 영상 안 텍스트 확인
2. **깨진 segment 식별** (영문 단어 깨짐, 핵심 수치 오류)
3. 깨진 박스 → hover ⋮ menu → "휴지통으로 이동" 삭제
4. 동일 strong prompt **재입력** → 새 generation
5. 3-4회 재시도 후에도 깨지면 prompt 더 단순화 (예: "Speed" → "ms")

**좌표 reference (이전 세션 carry)**:
- 박스 ⋮ menu = 박스 우상단 (X+129, Y-70)
- ⋮ menu 의 "휴지통으로 이동" = ⋮ click 위치 + Y=337 (빨간색 메뉴 가장 아래)
- 박스 Y=873+ 위치 → 휴지통 menu 화면 밖. **스크롤 다운 후 진행**

**Veo 깨짐 pattern (참고)**:
- "Latency" → "Latentcy" 깨짐
- "Methods" → "Methos" 깨짐
- "Sampling" → "Sampulling/Adaltive" 깨짐
- "Estimate" → "Estoınte" 깨짐
- "Combined" → "Commanted/Compled/Combaged" 깨짐
- → 모두 5자 이상 영문 단어가 자모 깨짐. 강화 prompt 의 5자 이하 단어 룰 + `Display EXACTLY` 명시로 회피.

### Phase 3: Flow Storyboard 합성 (예상 15-20분)

**Action**:
1. Flow 좌측 sidebar → **"장면" tab** click
2. **새 장면 만들기** 또는 기존 장면 click → Storyboard editor 진입
3. **26 segment timeline 배치** (순서):
   - 1A 표지 (0:00–0:08)
   - 2A·2B·2C VAQ (0:08–0:32)
   - 3A·3B·3C 카디널리티 (0:32–0:56)
   - 4A·4B 33.3% (0:56–1:12)
   - 5A·5B Adaptive 4단계 (1:12–1:28)
   - 6A Research Q (1:28–1:36)
   - 7A·7B 3 modes (1:36–1:52)
   - 8A·8B 1,508 (1:52–2:08)
   - 9A 7 Groups (2:08–2:16)
   - 10A·10B 89.1% (2:16–2:32)
   - 11A·11B·11C 엔진 (2:32–2:56)
   - 12A·12B 5.70× (2:56–3:12)
   - 13A Future (3:12–3:20)
   - 14A THANK YOU (3:20–3:28)
4. **transition** = fade through white 0.2s (Flow default)
5. **Export** → 1080p mp4
6. **다운로드** → 파일명 `속도는벡터_소개영상_원본_20260528.mp4` → 저장 위치 `~/Downloads/` 또는 `/tmp/`

### Phase 4: FFmpeg 자막 burn-in (예상 2-5분, **Bash MCP 자동**)

**Action** (Bash tool):
```bash
cd ~/Downloads  # 또는 mp4 위치

# 한국어 폰트 확인
fc-list :lang=ko | grep -i "Apple SD Gothic"

# 자막 burn-in
ffmpeg -i 속도는벡터_소개영상_원본_20260528.mp4 \
  -vf "subtitles=/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_소개영상_한국어자막_SRT_20260528.srt:force_style='Fontname=Apple SD Gothic Neo,Fontsize=36,PrimaryColour=&HFFFFFF&,OutlineColour=&H3A1E1E&,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=40,Bold=1'" \
  -c:a copy -c:v libx264 -preset slow -crf 18 \
  속도는벡터_소개영상_자막burnin_FINAL_20260528.mp4
```

**검증**:
- ffprobe 로 duration·codec·자막 확인
- QuickTime 자동 재생 (computer-use mcp 로 검증) — 가능

### Phase 5: YouTube Unlisted 업로드 (예상 5-10분, **Chrome MCP 자동**)

**Action** (Chrome MCP):
1. https://studio.youtube.com 접속
2. 사용자 Google 계정 = 이미 로그인 상태 추정 (이전 세션 carry)
3. **만들기** → **동영상 업로드** → 자막 burn-in mp4 선택
4. 제목: `속도는벡터 — 캡스톤 종합설계 결과 (연세대학교 BDAI 연구실)`
5. 설명: `26-1 인공지능종합설계. 벡터 증강 분석 쿼리의 카디널리티 추정에서 단일 개입의 controlled verification. 결합 89.1% 우위·5.70× 가속·plan 회복 94.9% + 메커니즘 = 분포 인지 X · 앙상블 효과.`
6. **공개 설정**: **Unlisted (일부 공개)**
7. **카테고리**: 교육
8. **업로드 완료** → URL 회수

**로그인 안 된 경우**:
- 사용자 매뉴얼 단계 표기 + 작업 일시 정지 + 아침 진행 가이드에 명시

### Phase 6: QR 생성 + 포스터 갱신 (예상 5-10분, **Bash + 사용자 매뉴얼**)

**Action**:
```bash
# QR 코드 생성 (Bash MCP)
python3 -c "import qrcode; img=qrcode.make('https://youtu.be/XXXXXXXX'); img.save('/Users/hyunbin/Downloads/소개영상_QR.png')"
```

**포스터 갱신** (자동화 가능 시도):
- 기존 포스터 PPTX 위치: `submission/_drafts/archive/TEAM륾_포스터.pdf` 또는 `submission/_drafts/archive/2026_05_26_postsubmit/poster/`
- 포스터 QR placeholder 위치 = 우측 footer
- 자동화 어려우면 사용자 매뉴얼 단계로 표기

---

## 3. ★ Veo prompt 정본 — 새 세션 직접 복붙용

### 3.1 강화 prompt 8개 (정본)

각 prompt 는 `submission/_drafts/속도는벡터_소개영상_강화prompt_8개_20260528.md` §1-8 carry. 새 세션이 본 md 정독 후 Flow chat 에 그대로 복붙.

**핵심 룰**:
- 영상 안 텍스트 = 영문 + 숫자 only (5자 이하 단어 위주)
- audio narration = 한국어 (Veo TTS 처리)
- prompt 끝에 `Display EXACTLY these words only` 명시

### 3.2 누락 segment prompt (정본)

`submission/_drafts/속도는벡터_소개영상_slide14_26segment_Veo_20260527_235800.md` §2 의 다음 prompt 복붙:

- Slide 1 — **Segment 1A** (표지)
- Slide 2 — **Segment 2B** (SQL 코드, 2A·2C 는 정상 가능성)
- Slide 3 — **Segment 3C** (10,000×)
- Slide 4 — **Segment 4A** (33.3%·50%·100%)
- Slide 10 — **Segment 10A, 10B** (89.1% · 1.4582 vs 1.4019)

**중복 방지**: 새 세션이 Flow 모든 미디어 view 정독해서 어느 segment 가 이미 정상 확보됐는지 확인 → 누락만 입력.

---

## 4. 자동화 한계 + 대처

### 4.1 Chrome MCP disconnect

**증상**: `mcp__Claude_in_Chrome__*` 도구 호출 시 "Claude in Chrome is not connected" 에러
**대처**: `list_connected_browsers` → `select_browser` (macmini deviceId) → tab 복귀 → 작업 재개

### 4.2 Veo 깨짐 (정정안도 깨짐)

**증상**: 정정안 영상도 영문 단어 자모 깨짐 (예: "Better way" → "Better wat" 또는 일부 단어 짤림)
**대처**:
1. **3-4회 재시도** (Veo 가 매번 다른 결과 generation)
2. 그래도 깨지면 **prompt 더 단순화** (예: "Better way?" → "Q?" 1자만)
3. **자막 SRT 에서 한국어 정보 carry** (영상 안 텍스트 깨져도 자막으로 메시지 전달)

### 4.3 YouTube 로그인 X

**증상**: studio.youtube.com 접속 시 로그인 화면
**대처**:
- 사용자 Google 계정 비밀번호 = 자동 입력 불가 (security)
- **사용자 매뉴얼 진행 표기**: 자막 burn-in mp4 까지 완성 + YouTube 업로드 단계는 사용자 아침 진행

### 4.4 포스터 PDF 자동 갱신 어려움

**증상**: 포스터 PPTX → PDF 자동 변환 + QR PNG 삽입 자동화 복잡
**대처**:
- QR PNG 생성 ✓ (Bash 자동)
- 포스터 PPTX 의 QR placeholder 위치 매뉴얼 갱신 표기

### 4.5 context 한계

**증상**: 새 세션 context 도달 (장시간 작업)
**대처**: 사용자 명시 "토큰 무한이니까" → context 제한 X 가정. 정말 한계 도달 시 = handoff 새 작성 + 다음 세션 인계.

---

## 5. 합성·자막·업로드 최종 검증

**Phase 4 자막 burn-in 후 검증**:
- [ ] mp4 duration ≈ 3:28 (208s)
- [ ] 해상도 1920×1080
- [ ] 한국어 자막 모든 segment 표시 (timing 8s 단위)
- [ ] 폰트 = Apple SD Gothic Neo (한국어 자모 정상)
- [ ] 영상 안 영문 텍스트 = 정정안 적용 후 정확 (또는 자막으로 보완)
- [ ] audio narration 한국어 발음 정확
- [ ] 파일 크기 50-150 MB

**Phase 5 YouTube 검증**:
- [ ] URL 회수 (`https://youtu.be/...`)
- [ ] Unlisted 설정 확인 (검색 X · URL 알면 시청 가능)
- [ ] 영상 재생 검증 (자동 또는 사용자)

**Phase 6 포스터 검증**:
- [ ] QR PNG 생성 (500×500)
- [ ] QR scan test (실제 핸드폰)
- [ ] 포스터 우측 footer QR 갱신 (사용자 매뉴얼 일 수도)

---

## 6. 산출물 경로 (총정리)

| 산출 | 경로 | 상태 |
|---|---|---|
| ★ **본 handoff** | `_internal/handoff/active/handoff_20260528_010500_새세션_소개영상_자동완성_critical.md` | 본 파일 |
| ★ 새세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260528_010500.md` | 다음 세션 첫 입력 |
| ★ 강화 prompt 8개 md | `submission/_drafts/속도는벡터_소개영상_강화prompt_8개_20260528.md` | Flow chat 복붙 |
| ★ 26 Veo prompt 정본 md | `submission/_drafts/속도는벡터_소개영상_slide14_26segment_Veo_20260527_235800.md` | 누락 prompt carry |
| ★ 한국어 자막 SRT | `submission/_drafts/속도는벡터_소개영상_한국어자막_SRT_20260528.srt` | FFmpeg burn-in 입력 |
| ★ 아침 진행 가이드 (사용자 대비) | `submission/_drafts/속도는벡터_소개영상_아침진행가이드_20260528.md` | 사용자 fallback |
| 직전 handoff (archive) | `_internal/handoff/archive/handoff_20260527_134500_*.md` | archive |
| Flow URL | https://labs.google/fx/ko/tools/flow/project/8fc58d63-6239-42d6-816f-bac3fb337ce2 | 자동 접속 |
| Chrome MCP macmini deviceId | `644dba75-3349-4c8d-ba29-1507743d45a5` | 영구 위임 |

---

## 7. 시간 일정 (현실적 평가)

| Phase | 예상 시간 | 자동화 가능 |
|---|---:|---:|
| Phase 1 prompt 입력 | 60-90분 | ✓ |
| Phase 2 generation 검증·재시도 | 30-60분 | ✓ |
| Phase 3 Storyboard 합성 | 15-20분 | ✓ |
| Phase 4 FFmpeg 자막 burn-in | 2-5분 | ✓ |
| Phase 5 YouTube 업로드 | 5-10분 | △ (로그인 X 시 매뉴얼) |
| Phase 6 QR + 포스터 | 5-10분 | △ (포스터 매뉴얼 가능성) |
| **합계** | **약 2-3시간** | — |

**새벽 작업 진행 시간**: 5/28 01:30 → 04:30 추정. 아침 7-9시 사용자 일어났을 때 완성 상태.

---

## 8. 환각 회피 룰 (모든 작업 공통)

- 영상 안 텍스트 = 영문 + 숫자 only · 한국어 자막은 SRT 후처리
- audio narration = 한국어 (발표 스크립트 carry)
- prompt 깨짐 시 3-4회 재시도 후 단순화
- Chrome MCP 끊김 = 즉시 재연결
- 자동화 불가 단계 = 사용자 매뉴얼 명시
- 결과 검증 매번 (영상 텍스트·자막·duration·해상도)
- **사용자 인터럽트 없는 한 완료 전까지 진행**

---

## 9. 작업 완료 보고 형식 (아침 사용자)

완료 후 사용자에게 보고할 항목:

1. **최종 mp4 파일 경로**: `/Users/hyunbin/Downloads/속도는벡터_소개영상_자막burnin_FINAL_20260528.mp4`
2. **YouTube URL** (Unlisted): `https://youtu.be/XXXXXXXX` (업로드 성공 시)
3. **QR PNG 경로**: `/Users/hyunbin/Downloads/소개영상_QR.png`
4. **포스터 갱신 상태** (자동 완료 or 사용자 매뉴얼 필요)
5. **검증 결과**: 영상 안 텍스트 정확성·자막 timing·duration·해상도·발음
6. **알려진 문제** (Veo 깨짐 일부 segment 등) + 처리 방법
7. **남은 단계**: LearnUs 12:00 마감 전 사용자 진행할 것

---

작성: 2026-05-28 01:05 KST · 새 세션 인계용 · self-contained 0% loss · 전권 위임 · 사용자 새벽 수면 동안 자동 진행 · 아침 완료 보고. **새 세션이 본 문서 정독 후 §0.1 부터 즉시 작업 시작.**
