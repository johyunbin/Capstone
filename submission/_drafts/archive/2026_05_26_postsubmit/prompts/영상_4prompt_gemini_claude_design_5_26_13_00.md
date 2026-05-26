# 영상 4 prompt — Gemini Veo 3.1 × Claude Design HTML animation 비교

> 작성 2026-05-26 13:00 KST · 사용자 결정: 두 도구 병행 → 비교 → 더 나은 쪽 PPT embed
> 영상 컨셉 2가지: (1) **엔진 탑재 이전 = baseline** · (2) **최종 엔진 = 결합 (본 연구)**
> 보이스 X · 자막 ok (silent visual)
> 15초 cinematic 또는 interactive mockup

## ★★ 영상 핵심 spec (사용자 요청 정밀 반영) ★★

**두 영상 모두**:
- Adaptive Sampling 5 단계 pipeline 을 상단에 표시: `Query → ① 표본 추출 → ② cardinality 추정 ★ → ③ Q-error 측정 → ④ N 갱신`
- **② cardinality 추정 단계가 우리 연구의 개입 위치** — 두 영상의 차이는 오직 이 ② 단계 작동 방식
- ② 단계를 zoom-in 또는 highlight 으로 강조 → 단계 안 메커니즘 close-up 시각화
- 결과 (plan tree + 응답 시간) 는 ② 단계 작동의 귀결로 표시

**영상 1 (baseline)** 의 ② 단계:
- 무작위 베르누이 sample 1개 추출 → cardinality **단일 추정값** (예: 333,333 행)
- 잘못된 추정 → Hash Join plan → 메모리 폭주 → 5,677 ms

**영상 2 (결합 = 본 연구)** 의 ② 단계:
- **두 추정값 동시 산출**:
  - (a) baseline 추정값 (무작위 베르누이) — 333,333 행
  - (b) 분포 인지 추정값 (예: chao_weighted 또는 다른 13 method) — ~200 행
- **산술 평균 = 결합 cardinality** ≈ 100 행 정확 (시각: 두 값이 가운데로 합쳐지는 merge animation)
- 정확한 추정 → Nested Loop plan → Index Scan → 983.5 ms

**대비 강조**: 두 영상은 **같은 pipeline · 다른 ② 단계** = 본 연구의 정확한 위치와 메커니즘이 한눈에.

---

## 트랙 A — Gemini Veo 3.1 (cinematic 합성, gemini.google.com)

### A-1 영상 1: baseline 작동 원리 (엔진 탑재 이전)

**Gemini Ultra 웹앱 또는 Flow 에 다음 prompt 복붙** (영어 권장 — Veo 효과 ↑):

```
Create a 15-second cinematic visualization for a Korean university research
presentation. NO voiceover (silent video with text overlays only).

THEME: Adaptive Sampling pipeline with BASELINE cardinality estimation (random
Bernoulli sample only) — wrong estimate leads to catastrophic slow query.

STYLE:
- Clean white background, navy blue (#1E3A5F) primary + RED accents
- Typography: Apple SD Gothic Neo Bold, Korean text labels
- Academic, minimal, technical-clean tone
- Smooth motion, 16:9 ratio, 1920×1080, 30fps

SCENE 1 (0-2s): Top of the screen shows Adaptive Sampling pipeline as 5-step
horizontal flow: "Query → ① 표본 추출 → ② cardinality 추정 ★ → ③ Q-error
측정 → ④ N 갱신". Step ② has a star/highlight badge. Below, a SQL query
appears: "WHERE ps_embedding <-> '쿼리벡터' < 0.86".

SCENE 2 (2-8s): ZOOM-IN on step ② cardinality 추정. Inside this step:
1. A 100만 vector dots cloud appears with "전체 100만 행" label
2. Random Bernoulli sample animation — small red dots scatter randomly from
   the cloud (Bernoulli 베르누이 sample · 385개 추출)
3. From these 385 dots, a single calculation arrow → produces ONE estimate
   in a large RED box: "추정 cardinality: 333,333 행 (33.3%)" with ✕ icon
4. Korean label: "baseline = 무작위 베르누이 sample 1개 → 단일 추정"

SCENE 3 (8-12s): Estimate "333,333 행" feeds into query planner. A Hash Join
plan tree builds (Hash + Seq Scan labels) with RED stroke. Memory bars fill
catastrophically (red progress, 100만 행 통째 메모리 로드).

SCENE 4 (12-15s): Counter ticks rapidly: "응답 시간 (ms): 0 → 500 → 5,677".
Final hero text fades in:
"엔진 탑재 이전 (baseline)"
"② cardinality 추정 = 단일 베르누이 추정 → 응답 시간 5,677 ms"
Fade to white.

VISUAL REFERENCES: pgvector EXPLAIN ANALYZE plan tree, Adaptive Sampling
pipeline (Exqutor §V-B), random Bernoulli sampling, slow query UI.

OUTPUT: 1920×1080 MP4, 15 seconds, no audio.
```

### A-2 영상 2: 결합 작동 원리 (최종 엔진 = 본 연구)

**Gemini Ultra 웹앱 또는 Flow 에 다음 prompt 복붙**:

```
Create a 15-second cinematic visualization for a Korean university research
presentation. NO voiceover (silent video with text overlays only).

THEME: Adaptive Sampling pipeline with COMBINED cardinality estimation
(baseline Bernoulli + distribution-aware sample, ARITHMETIC MEAN) — our
research's exact intervention point. Accurate estimate leads to fast query.

STYLE:
- Clean white background, navy blue (#1E3A5F) primary + CYAN (#0EA5E9) accents
- Typography: Apple SD Gothic Neo Bold, Korean text labels
- Academic, minimal, technical-clean tone
- Smooth motion, 16:9 ratio, 1920×1080, 30fps

SCENE 1 (0-2s): Same as baseline video — top of screen shows Adaptive Sampling
pipeline: "Query → ① 표본 추출 → ② cardinality 추정 ★ → ③ Q-error 측정 →
④ N 갱신". Step ② highlighted with cyan badge. SQL query below: "WHERE
ps_embedding <-> '쿼리벡터' < 0.86".

SCENE 2 (2-10s): ZOOM-IN on step ② cardinality 추정. Inside this step,
showing OUR RESEARCH'S COMBINED METHOD:
1. 100만 vector dots cloud with "전체 100만 행" label
2. TWO SAMPLES extracted IN PARALLEL (split-screen animation):
   - LEFT: Random Bernoulli sample (red dots scattered, 385개) — same as
     baseline. Label: "(a) baseline = 무작위 베르누이"
   - RIGHT: Distribution-aware sample (cyan dots in patterns — clusters,
     curves, hash-based, 385개) — our 13 methods.
     Label: "(b) 분포 인지 sample (13 method 중)"
3. Two estimates produced:
   - LEFT box: "baseline 추정: 333,333 행" (navy, faded)
   - RIGHT box: "분포 인지 추정: ~200 행" (cyan, faded)
4. MERGE ANIMATION — two boxes slide toward center, combine with "+ ÷ 2"
   arithmetic mean formula visualization → produce ONE large CYAN box:
   "결합 cardinality = (333,333 + 200) / 2 ≈ ~100 행 ✓" with check icon
5. Korean label: "★ 본 연구 = 두 추정값의 산술 평균"

SCENE 3 (10-13s): Accurate "~100 행" estimate feeds into query planner. A
Nested Loop plan tree builds with cyan stroke — clean Index Scan labels.
HNSW index navigation animation: search arrows through 3-layer HNSW graph,
100 specific points highlight (cyan glow). Memory bars stay tiny.

SCENE 4 (13-15s): Counter ticks small: "응답 시간 (ms): 0 → 983.5". Final
hero text fades in:
"최종 엔진 (결합 = 본 연구)"
"② cardinality 추정 = baseline + 분포 인지 산술 평균 → 응답 시간 983.5 ms"
Fade to white.

VISUAL REFERENCES: pgvector HNSW index navigation, Nested Loop plan tree,
combined estimation (arithmetic mean of two cardinality estimates), 
distribution-aware sampling (Hilbert curve, PCA, RaBitQ, chao_weighted,
md5 hash patterns), Exqutor §V-B Adaptive Sampling pipeline.

OUTPUT: 1920×1080 MP4, 15 seconds, no audio.
```

### A 사용 가이드
1. **gemini.google.com** 접속 (Ultra plan 로그인)
2. 새 chat → "Video generation (Veo 3.1)" 옵션 또는 직접 Veo 호출
3. 위 영문 prompt 복붙 → generate
4. 약 3-5분 대기 → MP4 다운로드
5. 또는 **Flow** (labs.google/flow) 사용 — 더 정밀 video editing

---

## 트랙 B — Claude Design HTML animation (interactive mockup, claude.ai/design)

### B-1 영상 1: baseline 작동 원리 (HTML animation page)

**Claude Design 동일 대화창 또는 새 대화창에 다음 복붙**:

```
새 HTML 단일 페이지 생성: `baseline_animation.html`

목적: 15초 silent CSS animation — Adaptive Sampling pipeline 안 baseline ②
cardinality 추정 작동 원리 시각화. 사용자가 Chrome 으로 재생 → 화면 녹화 →
MP4 → PowerPoint 의 slide 3 placeholder 에 manual embed 예정.

# 페이지 layout
- 1280×720 단일 HTML 페이지 (deck slide 형식 carry, design system 동결)
- design system: navy #1E3A5F · cyan #0EA5E9 · RED 강조 · Apple SD Gothic Neo · 흰 배경
- 음성 X · 자막 OK (CSS text overlay)
- CSS keyframes 으로 자동 재생, 15초 cycle

# 핵심 시각 spec
★ 상단에 Adaptive Sampling 5 단계 pipeline 박스 가로 흐름 항상 표시:
  "Query → ① 표본 추출 → ② cardinality 추정 ★ → ③ Q-error 측정 → ④ N 갱신"
  ② 단계 박스가 RED highlight (현 baseline 작동 위치).

본문 = ② 단계 zoom-in close-up (slide 70%) → 안에서 baseline 메커니즘 시각화.

# Animation timeline (CSS @keyframes, 15초)

| 시간 (s) | scene | 시각 요소 |
|---|---|---|
| 0-2 | pipeline + SQL fade-in | 상단 pipeline 5 단계 등장 (② 단계 RED 강조). 왼쪽 작은 SQL 박스 fade-in: SELECT ... WHERE ps_embedding <-> '[쿼리 벡터]' < 0.86 |
| 2-4 | ② 단계 zoom-in | ② "cardinality 추정 ★" 박스가 화면 가운데로 크게 확대 (CSS scale 1 → 2.5). 안에 작은 100만 벡터 dot cloud 등장 ("전체 100만 행" 라벨) |
| 4-7 | 무작위 베르누이 sample | 100만 dot 中 무작위 빨간 점 385개 scatter animation (CSS @keyframes 으로 dots scale-in, 0.5s stagger). 라벨: "(a) baseline = 무작위 베르누이 sample 1개 · 385개 추출" |
| 7-10 | 단일 추정값 산출 | 385개 빨간 dot → ↓ 화살표 → 큰 빨간 박스 등장 "추정 cardinality: 333,333 행 (33.3%)" + ✕ icon. pulse 효과 (1초 1회) |
| 10-13 | Hash Join plan + 메모리 폭주 | ② 박스 zoom out (CSS scale 2.5 → 1). pipeline 상단 carry. ② 단계 옆 화살표 → Hash Join plan tree (Hash·Seq Scan·빨간 stroke) + 메모리 바 0% → 100% width grow (3초 ease-out) "메모리: 100만 행 통째 로드" |
| 13-15 | 응답 시간 hero | 큰 빨간 bold 텍스트 (60pt) "응답 시간 5,677 ms" 화면 중앙 fade-in. 아래 작게 "엔진 탑재 이전 (baseline)" |

# 사용자 가이드
1. Claude Design 에서 본 HTML 생성·다운로드
2. Chrome 에서 file:// 로 열기 (또는 Claude Design deck preview)
3. macOS Cmd+Shift+5 → "선택한 영역 녹화" → 1280×720 → 15초 capture
4. .mov → .mp4 변환 (QuickTime "Export As" 또는 ffmpeg)
5. PowerPoint slide 3 placeholder 자리에 Insert → Video → From File
```

### B-2 영상 2: 결합 작동 원리 (HTML animation page · 본 연구)

**Claude Design 에 다음 복붙** (B-1 과 별도 페이지):

```
새 HTML 단일 페이지 생성: `combined_animation.html`

목적: 15초 silent CSS animation — Adaptive Sampling pipeline 안 결합 (본 연구)
② cardinality 추정 작동 원리 시각화. B-1 과 동일 layout + pipeline 표시, 단
② 단계 메커니즘만 다름 (단일 → 두 추정값 산술 평균).

# 페이지 layout (B-1 동일)
- 1280×720, design system 동결, CSS keyframes 자동 재생 15초

# 핵심 시각 spec
★ 상단 pipeline 가로 흐름: "Query → ① 표본 추출 → ② cardinality 추정 ★ →
  ③ Q-error 측정 → ④ N 갱신". ② 박스 CYAN highlight (본 연구 위치).
본문 = ② 단계 zoom-in close-up → 안에서 결합 메커니즘 (두 추정값 → 산술 평균)
시각화.

# Animation timeline (CSS @keyframes, 15초)

| 시간 (s) | scene | 시각 요소 |
|---|---|---|
| 0-2 | pipeline + SQL fade-in | 상단 pipeline 5 단계 (② CYAN 강조). 왼쪽 작은 SQL 박스 fade-in (B-1 과 같은 SQL) |
| 2-4 | ② 단계 zoom-in | ② 박스가 화면 가운데로 확대 (scale 1 → 2.5). 안에 100만 벡터 dot cloud + "전체 100만 행" 라벨 |
| 4-8 | 두 sample 동시 추출 (split-screen) | ② 박스 안 좌우 분할: 왼쪽에 무작위 베르누이 빨간 점 385개 scatter ("(a) baseline = 무작위 베르누이"). 오른쪽에 분포 인지 cyan 점 385개 패턴 형성 (cluster·curve·hash 패턴 시각) "(b) 분포 인지 sample (13 method 중 하나, 예: chao_weighted)". 두 sample 동시 진행 (0.5s stagger) |
| 8-11 | 두 추정값 → 산술 평균 결합 | 두 sample → 두 작은 박스 동시 등장: 왼쪽 navy soft "baseline 추정: 333,333 행" + 오른쪽 cyan soft "분포 인지 추정: ~200 행". 가운데에 "+ ÷ 2" 산술 평균 수식 visualization. 두 박스가 가운데로 슬라이드하며 merge → 큰 cyan 박스 등장: "결합 cardinality = (333,333 + 200) / 2 ≈ ~100 행 ✓" (cyan bold, 1s scale emphasis). 라벨: "★ 본 연구 = 두 추정값 산술 평균" |
| 11-13 | Nested Loop plan + HNSW index | ② 박스 zoom out → 옆 화살표 → Nested Loop plan tree (cyan stroke, Index Scan). 오른쪽에 HNSW 3-layer 그래프 — entry point → 100점 highlight (cyan glow). 메모리 바 tiny |
| 13-15 | 응답 시간 hero | 큰 cyan bold 텍스트 (60pt) "응답 시간 983.5 ms (5.70× ↑)" 화면 중앙 fade-in. 아래 작게 "최종 엔진 (결합 = 본 연구)" |

# 사용자 가이드
B-1 과 동일 — Chrome 재생 → 화면 녹화 → MP4 → PPT 새 slide 12 placeholder
```

### B 사용 가이드
1. **claude.ai/design** 동일 대화창 또는 새 대화창 진입
2. 두 prompt (B-1, B-2) 각각 별도 복붙 → HTML 페이지 2개 생성
3. Chrome 으로 각각 재생 → macOS Cmd+Shift+5 화면 녹화 → MP4 변환
4. PowerPoint manual embed

---

## 트랙 비교 기준 — 더 나은 영상 선택

| 항목 | 평가 |
|---|---|
| **1. 시각 임팩트** | 청중 attention 5초 안 잡는가? Gemini Veo = cinematic 임팩트 ↑ / Claude Design = 깔끔 학술 |
| **2. 정확성** | 본 연구 메커니즘·수치 정합? Claude Design 작성 시 우리 design system + 실제 SQL·수치 carry → 정확도 ↑ / Veo 합성 시 추상화 |
| **3. 직관성** | 카디널리티 추정 → plan 선택 흐름 명확? Veo = 추상 / Claude Design = 단계별 명확 |
| **4. 청중 친숙도** | 발표 청중 (DB 비전문가 포함) 이해 가능? 두 영상 모두 한국어 라벨 carry — 동등 |
| **5. PPT embed 안정성** | MP4 변환·재생 호환? 둘 다 MP4 → 동등 |
| **6. 작업 시간** | Gemini Veo = 5-15분 생성 / Claude Design + 화면 녹화 = 30-60분 |
| **7. 일관성** | Claude Design 작품 = 본 deck design system 정합 ↑ / Veo = 독립 cinematic |

### 추천 시나리오
- **시간 충분** (마감 11h 남음) → 두 트랙 모두 시도 → 비교 → 선택
- **빠른 결정** → Gemini Veo 우선 (작업 시간 ↓ + cinematic 임팩트)
- **정합성 우선** → Claude Design HTML animation (deck 와 통일된 시각)

---

## 사용자 다음 단계

1. **Gemini Ultra 웹앱** 에서 A-1 + A-2 prompt 적용 → MP4 2개 다운로드
2. **Claude Design** 에서 B-1 + B-2 prompt 적용 → HTML 2개 생성 → Chrome 재생 → 화면 녹화 → MP4 2개 변환
3. **비교** — 두 트랙 영상 4개 (또는 일부) 검토 → 더 나은 쪽 선택
4. **선택 결과 보고** → 우리가 PPT v3 placeholder 추가 + PowerPoint manual embed 가이드
5. **LearnUs 업로드** 마감 5/26 23:59 (~11h)
