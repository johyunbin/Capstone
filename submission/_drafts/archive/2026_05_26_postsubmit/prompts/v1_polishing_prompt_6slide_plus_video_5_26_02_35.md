# v1 → v2 polishing prompt — slide 2·3·4·5·6·9·11 (피드백 6건 + slide 3 영상 page 전환)

> 작성 2026-05-26 02:35 KST · 사용자 v1 검토 피드백 6건 정밀 반영 + slide 3 = 영상 page 전환 spec
> 적용처: claude.ai/design 동일 대화창 `019e1a41-...`
> 기존: deck_v24.html (13 slide, v1 = `속도는벡터_기말발표_v1.pptx`)
> 결과: deck v25 (또는 v24 update) — 13 slide 유지, 7 slide polishing

---

## ▼ ▼ ▼ 단일 복붙 시작 ▼ ▼ ▼

기존 deck_v24.html (13 slide) 위에 **slide 2·3·4·5·6·9·11 (7 slide) 정밀 polishing**. slide 1·7·8·10·12·13 = 변경 없음 carry. design system 동결.

---

## Slide 2 — 배경 (VAQ) 변경 1건
- 분석가 박스 아래의 **"손가락 → SQL"** 텍스트 **완전 삭제**
- 분석가 박스 + SQL 박스 + 결과 박스 carry

---

## Slide 3 — 배경 (1만 배) ★ **영상 page 로 완전 전환**

**현 v1 정적 도식 (cardinality 추정 박스 + plan tree) 완전 삭제**.

새 layout (영상 page):
- 상단 제목 carry: "카디널리티 한 곳이 잘못되면 — 최대 1만 배 느려짐"
- 부제 carry: "벡터 테이블 100만 행 · 같은 SQL · 같은 데이터"
- **본문 영역 = 큰 영상 placeholder** (slide 의 ~70% 차지) — 16:9 aspect ratio, navy 외곽선 또는 dashed cyan border (영상 embed 영역)
  - HTML/CSS 에는 `<video>` placeholder 또는 `<div class="video-placeholder">` 으로 표시 (실제 영상은 PowerPoint 에 사용자가 manual insert)
  - placeholder 안 텍스트: "**작동 원리 영상** / Veo 3.1 으로 생성 · 15초 clip · 카디널리티 추정 → 잘못된 plan 선택 → 1만 배 latency 차이"
- 영상 영역 옆 또는 아래 짧은 caption: "**카디널리티 추정 오차 → 잘못된 실행 plan 선택 → 응답 시간 1만 배 폭주**" (한 줄, 청중 5초 안 이해)
- hero "10,000× 응답 시간 차이" — slide 하단 carry (또는 영상 아래 짧게)

### 영상 spec (PowerPoint 에 사용자 manual embed 후 발표 시 재생)
- 영상 placeholder 위치: slide 가운데 (가로 ~960px, 세로 ~540px 또는 16:9 비율)
- HTML 에서는 검은 배경 영역 + "VIDEO PLACEHOLDER" 텍스트 또는 흐릿한 미리보기 image 또는 단순 cyan dashed border 박스
- 사용자가 PowerPoint 에서 manual 영상 insert 시 placeholder 자리에 정확히 들어가도록 spec

---

## Slide 4 — 배경 (33/50/100% 고정 비율) 변경 1건
- 하단 두 줄 텍스트:
  - 현: "세 시스템 모두 — 데이터·임계값과 무관하게 고정 비율로 어림한다"
  - 현: (빨간 점선 박스) "거의 모든 쿼리에서 잘못된 plan"
- 신: **한 줄로 합치기** — "**세 시스템 모두 데이터·임계값과 무관하게 고정 비율로 어림 → 거의 모든 쿼리에서 잘못된 plan**" (빨간 점선 박스 안 한 줄)

---

## Slide 5 — 방법 (Adaptive Sampling) 변경 3건

1. **N₀·N₁·N₂ 박스 밑 점선/점들 제거** — 현 각 BATCH 박스 안에 표시된 점선 또는 점 그래픽 제거 (BATCH 박스 안의 가로 점선)

2. **각 BATCH 박스 size 축소** — 박스 width 와 height 모두 축소 (현 ~33% → ~25%)

3. **박스 간격 확대 + "N 갱신" 텍스트 한 줄 배치**:
   - 박스 사이 간격을 넓혀 (현 ~20px → ~80px)
   - 그 간격 사이에 **"N 갱신" 텍스트가 가로 한 줄로 명확히 표시**
   - 화살표 → 와 함께: "**→ N 갱신 →**" (purple 14pt bold)

나머지: 제목·STEP 4단계·UPDATE PERIOD caption·하단 캡션 carry.

---

## Slide 6 — 방법 (본 연구 RQ) 변경 1건
- **1행 RQ 박스와 2행 baseline ↔ 샘플링 방식 탐색 grid 사이 간격 확대** (현 ~16px → ~40px)
- RQ 박스 위치 + grid 위치 carry (간격만 확대)

---

## Slide 9 — 방법 (paradigm) 변경 1건
- 제목 텍스트 단순화:
  - 현: "표본 추출 방식 — baseline + 분포 인지 16 method 中 강한 13 method **(클러스터링 3 폐기)**"
  - 신: "**표본 추출 방식 — baseline + 분포 인지 16 method 中 강한 13 method**" (괄호 안 "클러스터링 3 폐기" 부분 삭제)
- baseline 박스 옆 caption 의 "(클러스터링 3 폐기)" 도 동일 삭제

---

## Slide 11 — 적용 (engine latency + plan 회복) 변경 1건
- 제목 변경:
  - 현: "엔진 응답 시간 — 사실상 동등 · 진짜 우위는 최적 plan 선택"
  - 신: **"엔진 응답 시간 동일 / 최적 plan 선택 비율 우위"**
  - "동일" 과 "비율 우위" 짧고 명확한 대비

나머지: 3 막대 latency · 도넛 visual · cell × method 풀어쓰기 · "+57 최적 plan" chip · caption carry.

---

## 변경 X — carry slide (6 slide)

slide **1·7·8·10·12·13** 모두 v1 그대로 carry.

---

## ▲ ▲ ▲ 단일 복붙 끝 ▲ ▲ ▲

## 적용 방법

1. claude.ai/design 동일 대화창 진입
2. 본 prompt ▼ ~ ▲ 구간 복붙
3. deck_v25.html → PPTX export → `속도는벡터_기말발표_v2.pptx`

## ★ 별도 작업 — Veo 3.1 영상 생성 (slide 3 embed 용)

사용자가 Gemini Ultra 웹앱 / Flow 에서 다음 brief 으로 Veo 3.1 적용:

```
Veo 3.1 Prompt (작동 원리 영상 · 15초 cinematic):

Theme: Vector database query planning — wrong cardinality estimate leads to
catastrophic slow execution plan, 10,000× slower.

Scene 1 (0-5초): 큰 데이터셋 표시 — 100만 개 벡터 (작은 점들로 시각화),
"100만 행" 라벨. 벡터 거리 ≈ 0.86 조건 표시.

Scene 2 (5-10초): 두 갈래 분기 — 
  왼쪽 (빨간 X): "잘못된 추정 — 33만 행" 큰 박스 → 대형 Hash Join plan tree
  → 메모리 폭주 시각화 (큰 빨간 box 가 화면 채움)
  오른쪽 (cyan ✓): "정확 추정 — 100점" 작은 점 → 가벼운 Nested Loop plan tree
  → Index Scan 으로 즉시 결과 (cyan 작은 점 빠르게 이동)

Scene 3 (10-15초): 시계 시각화 — 왼쪽 plan 응답 시간 막대 (긴 빨간 bar),
오른쪽 plan 응답 시간 막대 (짧은 cyan bar). 큰 텍스트 "10,000× 차이"
hero 등장 + fade-out.

Style:
- 색상: navy #1E3A5F · cyan #0EA5E9 · 빨강 강조 · 흰 배경
- 폰트: Apple SD Gothic Neo Bold · 한국어
- 톤: 학술 cinematic, 차분 + 직관
- 한국어 narration (선택): "카디널리티 추정이 잘못되면 잘못된 실행 plan
  으로 응답 시간이 1만 배 폭주합니다"
- 16:9 ratio, 1920×1080
- 15초

Reference 시각 자료: pgvector / DuckDB query plan tree, HNSW vector index.
```

## 사용자 다음 단계

1. **claude.ai/design 에 본 prompt 복붙** → v2 deck + PPTX 다운로드 (예상: `속도는벡터_기말발표_v2.pptx`)
2. **Gemini Ultra 웹앱 또는 Flow** 에서 위 Veo 3.1 brief 적용 → 15초 영상 생성·다운로드
3. **PowerPoint 안에서 slide 3 의 영상 placeholder 자리에 Veo 영상 manual insert** (Insert → Video → From File)
4. 발표 시 slide 3 에서 영상 재생 → 청중에게 작동 원리 직관 전달

## 핵심 정합성 확인 사항 (Claude Design 에 명시)

- slide 3 = 정적 도식 완전 삭제 + 영상 placeholder area 만 남김 (PPT manual embed 용)
- slide 5 = N 갱신 글자가 박스 사이 한 줄로 명확
- 모든 텍스트 변경 정확 반영
