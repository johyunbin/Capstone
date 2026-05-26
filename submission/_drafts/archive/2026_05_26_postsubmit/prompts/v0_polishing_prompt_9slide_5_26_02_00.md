# v0 → v1 polishing prompt — slide 2·3·5·6·7·8·9·10·11 (사용자 피드백 9건)

> 작성 2026-05-26 02:00 KST · 사용자 v0 검토 피드백 9건 정밀 반영
> 적용처: claude.ai/design 동일 대화창 `019e1a41-...`
> 기존: deck_v23.html (13 slide, v0 = `속도는벡터_기말발표_v0.pptx`)
> 결과: deck v24 (또는 deck_v23.html 위 update) — 13 slide 유지, 9 slide polishing

---

## ▼ ▼ ▼ 단일 복붙 시작 ▼ ▼ ▼

기존 deck_v23.html (13 slide) 위에 **slide 2·3·5·6·7·8·9·10·11 (9 slide) 정밀 polishing**. slide 1·4·12·13 = 변경 없음 carry. 결과 = 새 v24 파일 또는 v23 update.

design system (navy `#1E3A5F` · cyan `#0EA5E9` · purple · green · coral · Apple SD Gothic Neo · 흰 배경) 동결.

---

## Slide 2 — 배경 (VAQ) 변경 1건

- SQL 박스 상단의 **"한 SQL 안에 — VAQ"** 텍스트 **완전 삭제**
- 그 아래 caption "예시 분석 쿼리 — 관계형 조건과 벡터 유사도를 한 SQL 안에" carry (변경 X)
- 나머지 모두 carry (분석가 박스·SQL·결과 박스)

---

## Slide 3 — 배경 (1만 배) 변경 1건 ★ 시각화 재설계

**현 v0 문제** (사용자 지적): 두 plan tree 가 단순히 "Seq Scan vs Index Scan" 차이로 읽힘 — **카디널리티 추정에 의해 plan 이 달라진다**는 framing 부족.

**변경** — plan tree 위·옆에 **카디널리티 추정 박스** 명시. 즉 "카디널리티 추정 → plan 선택" 흐름이 시각적으로 명확하게:

레이아웃 옵션 (둘 중 선택):

**옵션 A (추천) — plan tree 위에 cardinality 추정 박스 추가**:
- 왼쪽 박스 (잘못된 plan):
  - 상단에 **카디널리티 추정 박스** 추가 — 예: "**카디널리티 추정** / Partsupp_deep WHERE vector ≈ 0.86 → **예상 333,333 행** (33.3%)" (빨간 ✕ icon)
  - 아래 화살표 **↓ "큰 행 수 추정 → Hash plan 선택"**
  - 그 아래 현 plan tree (Hash·Seq Scan) carry
- 오른쪽 박스 (정확한 plan):
  - 상단에 **카디널리티 추정 박스** 추가 — 예: "**카디널리티 추정** / Partsupp_deep WHERE vector ≈ 0.86 → **예상 100 행** (HNSW 정확 추정)" (cyan ✓ icon)
  - 아래 화살표 **↓ "작은 행 수 추정 → Nested Loop plan 선택"**
  - 그 아래 현 plan tree (Nested Loop·Index Scan) carry

**옵션 B (대안) — plan tree 의 root 노드 위에 큰 caption**:
- 왼쪽 plan tree root 위: "**카디널리티 잘못 추정 (333,333 행)** → 왼쪽 plan"
- 오른쪽 plan tree root 위: "**카디널리티 정확 추정 (~100 행)** → 오른쪽 plan"
- plan tree 내부 cardinality estimate vs actual 차이 강조

→ **옵션 A 우선** (시각 임팩트 ↑, 청중에게 cardinality 추정의 영향 직관).

나머지: hero "10,000× 응답 시간 차이" + 메타 "벡터 데이터셋 DEEP · 표준 분석 쿼리 예시" carry.

---

## Slide 5 — 방법 (Adaptive Sampling) 변경 3건

1. **"N 갱신" 글자 정렬** — BATCH 박스 사이 화살표 옆의 "N 갱신" 텍스트가 일부 회전됐거나 기울어져 있다면 **가로 정상 표기**로 정렬

2. **BATCH 박스 안 설명 텍스트 삭제** — N₀·N₁·N₂ 의 변화만으로 충분히 표본 크기 변화 시각화됨. 각 BATCH 박스 안의 다음 설명 텍스트 **모두 삭제**:
   - BATCH 1: "초기 표본 크기 385개 · 각 쿼리 한 번 추출 → 오차 측정" 삭제
   - BATCH 2: "누적 오차로 N 자체 갱신" 삭제
   - BATCH 3: "누적 오차로 N 또 갱신 · 반복" 삭제
   - 박스 안에는 **BATCH 라벨 + N₀=385 / N₁ / N₂** 만 남김

3. **빈 공간 layout 조정** — 텍스트 삭제로 생기는 빈 공간은 박스 height 축소 또는 박스 위치 재정렬해서 적절히 메꿈. 위·아래 padding 균일.

나머지: 제목·STEP 4단계·하단 캡션 carry.

---

## Slide 6 — 방법 (본 연구 RQ) 변경 1건

- **RQ 박스를 위쪽으로 이동** — 현 위쪽 빈 여백이 너무 큼. RQ 박스를 제목 바로 아래로 약 30-50px 위로 이동
- 1행 RQ 박스 + 2행 baseline ↔ 샘플링 방식 탐색 grid carry

---

## Slide 7 — 방법 (통제 실험 3 방식) 변경 3건

1. **하단 캡션 "동시 산출 → 외생 변수 통제" 변경 또는 삭제** — 청중 이해 X
   - 옵션 A (삭제): 캡션 완전 삭제
   - 옵션 B (직관 표현): **"같은 조건에서 직접 비교 가능"** 또는 **"동일 환경 paired 측정"**
   - 추천: **옵션 B** "**같은 조건에서 직접 비교 가능**"

2. **baseline 박스 안 "추정값 1개" → "cardinality 추정 1개"** 로 변경
   - "추정값" → "cardinality" 로 용어 통일 (사용자 명시)

3. **단독 대체 박스 + 결합 박스 의 "추정값" 모두 "cardinality" 로 변경**:
   - 단독 대체: "추정값 1개 (회색)" → "**cardinality 추정 1개 (회색)**"
   - 결합: "추정값 A" / "추정값 B" → "**cardinality A**" / "**cardinality B**"
   - 결합 박스 하단 "결합 추정값" → "**결합 cardinality**"

나머지: 제목·상단 호·세 박스 라벨·풀어쓰기 caption·시각 자료 carry.

---

## Slide 8 — 방법 (1,508 측정) 변경 3건 ★ 정합성 critical

**현 v0 문제** (사용자 지적):
- "5 × sf3 × sel3 × 16 method = 1,508" 식 곱셈 안 맞음 (5 × 3 × 3 × 16 = 720)
- 가운데 박스 "16 method (베르누이 + 분포 탐색 15)" — 정확 (사용자 확인)
- 우측 박스 하단 "각 cell 에서 baseline · 결합 동시 산출 → 직접 비교" — 표현 수정 필요

### 변경 사항

1. **COMBINATIONS 박스 안 1,508 정확 분해** — 보고서 §3 정본:
   - 현: "5 데이터셋 × sf {1·10·100} × sel {.001·.01·.1} × 16 method = 1,508"
   - 신: **"5 데이터셋 × sf {1·10·100} × sel {.001·.01·.1} × K {10·20·30} × 16 method"** + 아래 **"의도 max 3,600 中 실측 1,508 (41.9% 구조화 부분 측정)"**
   - **K (계층 수 10·20·30) 차원 추가** — 5 차원 측정 평면 명시
   - 단순 곱셈 표기 X — 부분 측정임을 명시

2. **VARIABLES 박스 안 SCALE FACTOR · SELECTIVITY 외 K 추가**:
   - 현: SCALE FACTOR · SELECTIVITY · METHOD 3 변인
   - 신: SCALE FACTOR · SELECTIVITY · **K (계층 수)** · METHOD 4 변인 (또는 5 변인 = 데이터셋 + 위 4 변인)
   - K 박스 추가: "**K · 계층 수 / 10 · 20 · 30**"

3. **우측 박스 하단 캡션 수정** — "각 cell 에서 baseline · 결합 동시 산출 → 직접 비교":
   - 신: **"같은 조건 paired 측정 → 외생 변수 통제하고 baseline vs 결합 직접 비교"**
   - 또는 더 단순: **"동일 조건 동시 측정 → 직접 비교"**

4. **하단 안내 텍스트 carry** — "엔진 응답 시간 측정은 별도 — DEEP sf=10 환경 · 다음 슬라이드 11 에서 156 plan 소개"

5. **MEASUREMENT ENVIRONMENT 박스 carry** — v0 에서 이미 삭제됨, 변경 X

---

## Slide 9 — 방법 (paradigm) 변경 2건 ★ 정합성 critical

**현 v0 문제** (사용자 지적): slide 8 = "16 method" / slide 9 = "13 method" — 둘이 다름. **정합성 노출 필요**.

**진실**:
- 1,508 측정 전수 = **16 method** (베르누이 1 + 분포 인지 15)
- paradigm 분류 = **16 中 강한 13 method** (클러스터링 3 폐기: gmm · minibatch_partial · faiss_ivf)

### 변경 사항

1. **제목 풀어쓰기 보강**:
   - 현: "표본 추출 방식 — baseline vs 샘플링 방식 탐색 13 method"
   - 신: "**표본 추출 방식 — baseline + 분포 인지 16 method 中 강한 13 paradigm 분류**" (16 中 13 명시)
   - 또는 짧게: "**baseline vs 분포 인지 13 method (16 中 클러스터링 3 폐기)**"

2. **baseline 박스 옆 caption 추가** — 현 baseline 점 cluster 박스 아래에 작은 caption:
   - 현: "균일 무작위 점들"
   - 신: "균일 무작위 점들" + 그 아래 작은 글씨 **"분포 인지 16 method 中 강한 13 paradigm 분류 (클러스터링 3 폐기)"**

3. **METHOD chip 박스 carry** — 13 METHOD · 7 paradigm carry. 또 각 paradigm method 개수 chip (P1:2 / P2:3 / P3:2 / P4:2 / P5:1 / P6:1 / P7:2 = 13) carry.

---

## Slide 10 — 결과 (Q-error 89.1%) 변경 3건 ★ 시각 재설계

### 변경 사항

1. **"격차는 median Q-error 1.4582 → 1.4019 (-4.38%)" 텍스트 삭제**:
   - 현 framing line: "결합이 baseline 을 paired 89.1% 우위 — 격차는 median Q-error 1.4582 → 1.4019 (-4.38%)"
   - 신: **"결합 방식이 baseline 보다 Q-error 우위"** (짧고 명확, 격차 수치 부분 삭제)
   - 또는 더 간결: **"결합 방식이 더 정확한 카디널리티 추정"**

2. **"결합 우위" → "결합 방식 우위"** — 89.1% 아래 caption:
   - 현: "1,344 / 1,508 cell · 결합 우위"
   - 신: "1,344 / 1,508 cell · **결합 방식 우위**"

3. **★ broken axis 막대 시각화 재설계** (사용자 지적: 푸른색 그래프라 baseline 이 더 좋아 보이는 느낌):

   현 v0: baseline (navy) + 결합 (cyan) 두 막대 모두 푸른색 계열 — 결합이 더 짧은데 cyan 이 ↑ 강조 X.

   **재설계 옵션** (둘 중 선택):

   **옵션 A (추천) — 색상 + 시각 명시 강화**:
   - baseline 막대 = **회색 (grey-concept `#94A3B8`)** — 비교 reference 강조 X
   - 결합 막대 = **cyan bold (`#0EA5E9`)** + 두께 ↑ — 우위 시각 강조
   - 두 막대 위에 **★ "▼ 낮을수록 더 정확한 추정"** 아이콘 명시 (방향성 직관)
   - 결합 막대 끝에 **체크 아이콘 ✓** + cyan 라벨 "**더 정확**"
   - baseline 막대 끝에 작은 X 아이콘 또는 단순 라벨

   **옵션 B (대안) — bar 방향 역전 (역수 시각화)**:
   - bar 길이 = 1/Q-error · 100 = 정확도 점수 (높을수록 좋음)
   - baseline 정확도 = 68.6 / 결합 정확도 = 71.3 → 결합이 긴 bar
   - 청중 직관 정합 (긴 bar = 좋음)

   **옵션 C (대안) — scatter / density 분포 chart**:
   - 1,508 cell 의 paired Δ% 분포 (또는 Q-error 점 분포)
   - 결합이 더 왼쪽 (낮은 Q-error) 으로 치우친 분포 — 청중에게 직관 정합

   → **옵션 A 우선 추천** (현 구조 유지하면서 시각 강조만 변경).

---

## Slide 11 — 적용 (엔진 latency + plan 회복) 변경 1건

**현 v0 표현**: "plan 회복 = 카디널리티 추정이 정확 → 정답 실행 plan 선택 (latency 폭주 방지)"

**사용자 지적**: "**정확한 plan 을 고르는 게 plan 회복**" 이라는 표현이 어색. 더 좋은 표현 필요.

### 변경 옵션

**옵션 A (추천)**: "**plan 회복**" → "**최적 plan 선택**" (또는 "**정답 plan 선택**")
- 도넛 라벨: "baseline 최적 plan 선택" / "결합 최적 plan 선택"
- caption: "**최적 plan 선택 = 카디널리티 추정 정확 → 빠른 plan 도달**"

**옵션 B**: "**plan 회복**" → "**plan 정확도**" — 정확한 plan 선택률
- caption: "**plan 정확도 = 정답 실행 계획을 고르는 비율**"

**옵션 C**: "**plan 회복**" → "**올바른 plan 비율**"
- caption: "**카디널리티 추정 정확 → 옳은 실행 plan 선택 (느린 plan 회피)**"

→ **옵션 A** "**최적 plan 선택**" 우선 추천 (간결·직관·정답 의미 명확).

### 변경 사항 종합

- 제목: "엔진 응답 시간 — 사실상 동등 · 진짜 우위는 **최적 plan 선택**" (plan 회복 → 최적 plan 선택)
- 도넛 라벨: "baseline 최적 plan 선택 (91/156)" / "결합 최적 plan 선택 (148/156)"
- 가운데 chip: "+57 plan 회복" → "**+57 최적 plan**"
- 하단 caption: "최적 plan 선택 = 카디널리티 추정 정확 → 빠른 plan 도달 (느린 plan 회피)"

나머지: 3 막대 latency · 도넛 visual · cell × method 풀어쓰기 carry.

---

## 변경 X — carry slide (4 slide)

slide **1·4·12·13** 모두 v0 그대로 carry.

---

## ▲ ▲ ▲ 단일 복붙 끝 ▲ ▲ ▲

## 적용 방법

1. claude.ai/design 동일 대화창 (`019e1a41-...`) 진입
2. 본 prompt 의 ▼ ~ ▲ 구간 전체 복붙
3. deck_v24.html (또는 deck_v23.html update) → PPTX export → `속도는벡터_기말발표_v1.pptx` 로 저장

## 핵심 정합성 확인 사항 (Claude Design 에 명시)

- **1,508 = 5 차원 부분 측정** (데이터셋 · sf · sel · K · method, 의도 max 3,600 中 41.9%)
- **slide 8 = 16 method** (베르누이 1 + 분포 인지 15) — 1,508 측정 전수
- **slide 9 = 13 method** (16 中 강한 13, 클러스터링 3 폐기) — paradigm 분류용
- "**cardinality**" 용어 통일 (slide 7 박스 안 추정값 → cardinality)
- "**최적 plan 선택**" 용어 통일 (slide 11)
