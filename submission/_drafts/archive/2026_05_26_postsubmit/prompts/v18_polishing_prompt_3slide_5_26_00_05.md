# v18 → v19 polishing prompt (slide 2·3·5 fix)

> 작성 2026-05-26 00:05 KST · 사용자 피드백 (5/25 23:54) 정밀 반영
> 적용처: claude.ai/design 동일 대화창 `019e1a41-701c-7134-9ce1-1247262c1563`
> 기존: v18 14 slide deck (`____ (2).pptx`, 5/25 13:30 다운로드)
> 결과: v19 14 slide deck — 단 **slide 2·3·5 만 정밀 polishing**, 나머지 **11 carry slide (1·4·6·7·8·9·10·11·12·13·14) 변경 없음**

---

## ▼ ▼ ▼ 단일 복붙 시작 ▼ ▼ ▼

기존 v18 14 slide deck 에서 **slide 2·3·5 만 정밀 polishing** 진행합니다. 다른 11 slide (1·4·6·7·8·9·10·11·12·13·14) 는 **변경 없음 carry**.

design system (navy `#1E3A5F` · cyan `#0EA5E9` · purple `#8B5CF6` · green `#10B981` · coral `#F97316` · Apple SD Gothic Neo · 흰 배경 · chapter badge `배경/방법/결과/적용` · hero grad slide 11·13 등) 동결. 절대 규칙 9 (코드명 노출 금지 · 영역 필러 금지 · 수식 노출 금지 · 이분법 강조 금지 · 별표 ★ 노출 금지 · 페이지 번호 부재 · 텍스트 잘림·겹침 금지 · design system 동결 · 한국어 라벨 통일) 모두 carry.

---

## 전 슬라이드 공통 룰 (slide 2·3·5 모두 적용)

### 1. 약어 처음 등장 시 풀어쓰기 한 번 노출

모든 약어는 처음 등장 시 한국어 풀이를 함께 노출. 예시 형식:

- VAQ → **"벡터 증강 분석 쿼리 (Vector-Augmented Query, VAQ)"**
- HNSW → **"계층적 탐색 가능한 작은 세계 (Hierarchical Navigable Small World, HNSW)"**
- ECQO → **"Exqutor 의 Cardinality-aware Query Optimization (ECQO)"**
- TPC-H → **"표준 분석 벤치마크 (TPC-H)"** — 단 slide 2·3 에서는 TPC-H 단어 자체를 제거 (사용자 요청)
- Adaptive Sampling → **"Adaptive Sampling (적응적 표본 추출)"**
- DEEP → **"벡터 데이터셋 DEEP"**

### 2. 텍스트 줄 정렬 일관성

- 모든 텍스트 블록은 **좌측 정렬** (또는 명백한 가운데 정렬) 통일
- 들여쓰기·padding 동일 그리드 (16-20px)
- 라벨·캡션 폰트 크기·color 일관
- 세로 회전 텍스트 (90° / 180°) 금지 — 모든 라벨 가로 정상 표기

---

## Slide 2 — 배경 (벡터 증강 분석 쿼리 · VAQ) 정밀 변경

### 현 v18 시각 (간략)

- 제목 "벡터 증강 분석 쿼리 — VAQ" (VAQ 아래 점선 underline)
- 분석가 박스 (왼쪽): "이 부품 사진이랑 비슷한 부품들이 / 최근 가장 많이 팔린 주문은?" + 사람 icon + "손가락 → SQL"
- SQL 박스 (가운데): caption "한 SQL 안에 — VAQ / TPC-H Q3 변형 — 한 SQL 안에 관계형 JOIN + 벡터 유사도" + SQL 코드 (`SELECT ... FROM customer, orders, lineitem, partsupp_deep WHERE c_mktsegment='HOUSEHOLD' AND ... ps_embedding <-> '[쿼리 부품 벡터]' < 0.86 ORDER BY ps_embedding <-> '[쿼리 부품 벡터]'`) + "← 관계형 조건 (TPC-H)" 라벨 + "← 벡터 유사도 (VAQ)" 라벨
- VAQ 결과 (오른쪽): "유사 벡터 추출" + customer·orders·lineitem·partsupp_deep bullet + "매출 TOP 행 / 유사 부품 매출 분석 결과" 박스

### 변경 사항 6 건

1. **제목 풀어쓰기** — "벡터 증강 분석 쿼리 — VAQ" → **"벡터 증강 분석 쿼리 (Vector-Augmented Query, VAQ)"** (한 줄, VAQ 점선 underline 제거)

2. **SQL 박스 caption 단순화** — "한 SQL 안에 — VAQ / TPC-H Q3 변형 — 한 SQL 안에 관계형 JOIN + 벡터 유사도" → **"예시 분석 쿼리 — 관계형 조건과 벡터 유사도를 한 SQL 안에"** (단일 줄, TPC-H 단어 제거)

3. **SQL 옆 라벨 풀어쓰기**:
   - "← 관계형 조건 (TPC-H)" → **"← 관계형 조건 (예: 가정용 카테고리 · 1995-03-14 이전 주문)"**
   - "← 벡터 유사도 (VAQ)" → **"← 벡터 유사도 — 임베딩 비교"**

4. **분석가 박스 carry** — 박세은 피드백 자연어 그대로 유지: "이 부품 사진이랑 비슷한 부품들이 / 최근 가장 많이 팔린 주문은?"

5. **오른쪽 결과 박스 직관화**:
   - "유사 벡터 추출" → **"유사 부품 추출"** (한국어)
   - 4 컬럼 bullet (customer · orders · lineitem · partsupp_deep) — carry, 단 옆에 "← 관계형 데이터" / "← 벡터 데이터" 한 번 표시
   - "매출 TOP 행 / 유사 부품 매출 분석 결과" → **"→ 유사 부품의 매출 상위 주문 도출"** (단일 명확)

6. **텍스트 줄 정렬 통일** — 분석가 박스·SQL 박스·결과 박스 모두 좌측 정렬, padding 16px, 라벨 폰트 크기 11.5pt 통일

---

## Slide 3 — 배경 (카디널리티 한 곳이 잘못되면 — 최대 1만 배) 정밀 변경

### 현 v18 시각 (간략)

- 제목 "카디널리티 한 곳이 잘못되면 — 최대 1만 배 느려짐"
- 부제 "벡터 테이블 100만 행 · 같은 SQL · 같은 데이터" — 가로 라인 디자인 요소 부근 (시각 겹침)
- 왼쪽 박스 (빨간 테두리, 잘못된 plan): "X 카디널리티 추정 틀림" + plan tree (Sort → ⋈ Hash → ⋈ Hash → ⋈ Hash → σ Seq Scan Customer + σ Seq Scan Orders + σ Seq Scan Partsupp_deep ← contains vectors (cyan 점선 타원) + σ Seq Scan Lineitem ~100만 행) + 캡션 "큰 중간 테이블 누적 → 메모리·시간 폭주"
- 오른쪽 박스 (cyan 테두리, 정확한 plan): "✓ 카디널리티 추정 정확" + plan tree (Sort → ⋈ Nested Loop → ⋈ Nested Loop → ⋈ Nested Loop → σ Index Scan Customer + σ Index Scan Orders + σ Index Scan Partsupp_deep ← contains vectors ~100점만 조회 (cyan 점선 타원) + σ Index Scan Lineitem on l_orderkey) + 캡션 "한 행씩 인덱스로 정확히 풀어냄"
- 하단 hero "10,000× 응답 시간 차이" (큰 그라데이션) + 메타 "TPC-H Q3 VAQ on DEEP"

### 변경 사항 5 건

1. **부제 위치 fix** — 제목과 부제 사이 padding-top 20px 확보, 부제는 별도 line 처리. 가로 라인 디자인 요소 (cyan stripe) 와 시각 겹침 해소.
   - 부제 텍스트 carry: "벡터 테이블 100만 행 · 같은 SQL · 같은 데이터"
   - 위치: 제목 아래 20px, center 정렬, font 14pt navy soft

2. **plan tree node 옆 한국어 풀이 라벨 추가** (직관성 보강):

   **왼쪽 plan (잘못)**:
   - "⋈ Hash" 노드 옆 → "**Hash · 한꺼번에 묶기**" 작은 caption
   - "σ Seq Scan" 노드 옆 → "**Seq Scan · 전체 행 읽기**" 작은 caption
   - "σ Seq Scan Lineitem ~100만 행" → 그대로
   - "σ Seq Scan Partsupp_deep ← contains vectors" (cyan 점선 타원) — carry, 단 "333,333 행 통째 메모리" → **"전체 벡터 100만 행 메모리 폭주"**

   **오른쪽 plan (정확)**:
   - "⋈ Nested Loop" 노드 옆 → "**Nested Loop · 하나씩 인덱스로**" 작은 caption
   - "σ Index Scan" 노드 옆 → "**Index Scan · 인덱스로 부분만**" 작은 caption
   - "σ Index Scan Partsupp_deep ← contains vectors ~100점만 조회" — carry, 단 "~100점만 조회" → **"인덱스로 100점만 직접 조회"**

3. **양쪽 박스 하단 캡션 직관화**:
   - 왼쪽: "큰 중간 테이블 누적 → 메모리·시간 폭주" → **"전체 행을 모두 메모리에 → 100만 행 폭주"**
   - 오른쪽: "한 행씩 인덱스로 정확히 풀어냄" → **"인덱스로 100점만 직접 조회 → 즉시"**

4. **hero "10,000× 응답 시간 차이" carry** — 그라데이션·크기 변경 없음

5. **메타 풀어쓰기**: "TPC-H Q3 VAQ on DEEP" → **"벡터 데이터셋 DEEP · 표준 분석 쿼리 예시"**

---

## Slide 5 — 방법 (인덱스 없을 때 Adaptive Sampling) 정밀 변경

### 현 v18 시각 (간략)

- 제목 "인덱스가 없을 때 — Adaptive Sampling" (purple chapter badge `방법`)
- 4 STEP 가로 흐름: 
  - Query (SQL) →
  - **① STEP 표본 추출** (purple 강조, "본 연구 집중 단계 ★" badge, 무작위 베르누이 · 균일 random, "한 쿼리당 N=385 sample 1회 추출 → 50 쿼리마다 N 갱신")
  - **② STEP 카디널리티 추정** (표본 위에서 추정)
  - **③ STEP Q-error 측정** (추정 오차 측정)
  - **④ STEP Momentum 조정** (다음 표본 크기)
- 하단 BATCH 흐름:
  - "UPDATE PERIOD · 50 쿼리마다 N 자체가 갱신"
  - BATCH 1 · Q₁-Q₅₀: N₀ = 385 (초기 N · 각 쿼리 sample 1회 → Q-error)
  - **BATCH 1 → BATCH 2 사이 화살표 옆 "N 갱신" 세로 회전 텍스트 (시각 버그)**
  - BATCH 2 · Q₅₁-Q₁₀₀: N₁ (누적 Q-error · m=0.9 · η 감쇠)
  - BATCH 2 → BATCH 3 사이 화살표 옆 "N 갱신" 세로 회전 텍스트
  - BATCH 3 · Q₁₀₁-Q₁₅₀: N₂ (누적 Q-error → N 또 갱신 · 반복)
- 캡션: "한 쿼리 = N개 표본 1회 추출 · 50 쿼리 batch마다 N 자체가 동적 조정 (momentum m=0.9 · 학습률 η 감쇠)"

### 변경 사항 7 건

1. **제목 풀어쓰기** — "인덱스가 없을 때 — Adaptive Sampling" → **"인덱스가 없을 때 — Adaptive Sampling (적응적 표본 추출)"**

2. **STEP ④ 박스 단어 변경**: "Momentum 조정 (다음 표본 크기)" → **"표본 크기 조정 (다음 표본은 더 많이 / 적게)"** (Momentum 단어 제거)

3. **STEP ① 박스 caption 단순화**:
   - 현: "무작위 베르누이 · 균일 random / 한 쿼리당 N=385 sample 1회 추출 → 50 쿼리마다 N 갱신"
   - 신: **"무작위 균일 추출 (베르누이 방식) · 한 쿼리당 표본 385개 한 번"**

4. **BATCH 라벨 풀어쓰기** (Q 약어 제거, 청중 친숙 단어):
   - "BATCH 1 · Q₁-Q₅₀" → **"샘플링 1~50회 (1단계)"**
   - "BATCH 2 · Q₅₁-Q₁₀₀" → **"샘플링 51~100회 (2단계)"**
   - "BATCH 3 · Q₁₀₁-Q₁₅₀" → **"샘플링 101~150회 (3단계)"**
   - 상단 "UPDATE PERIOD · 50 쿼리마다 N 자체가 갱신" → **"50회 샘플링마다 표본 크기 자체가 갱신"**

5. **★ "N 갱신" 세로 회전 텍스트 제거** (시각 버그 fix):
   - BATCH 1 → BATCH 2 사이, BATCH 2 → BATCH 3 사이 모두
   - 회전 제거, **가로 정상 표기**로 변경
   - 화살표 위 caption: **"→ 표본 크기 N 갱신"** (가로, font 11pt navy)

6. **m=0.9 / η 감쇠 파라미터 모두 삭제** (사용자 명시: 자세 설명 안 할 거면 흐름상 중요 X):
   - BATCH 1 박스 안 "초기 N · 각 쿼리 sample 1회 → Q-error" → **"초기 표본 크기 385개 · 각 쿼리 한 번 추출 → 오차 측정"**
   - BATCH 2 박스 안 "누적 Q-error · m=0.9 · η 감쇠" → **"누적 오차로 N 자체 갱신"**
   - BATCH 3 박스 안 "누적 Q-error → N 또 갱신 · 반복" → **"누적 오차로 N 또 갱신 · 반복"**
   - 하단 캡션 현: "한 쿼리 = N개 표본 1회 추출 · 50 쿼리 batch마다 N 자체가 동적 조정 (momentum m=0.9 · 학습률 η 감쇠)" → 신: **"한 쿼리 = 표본 1회 추출 · 50 쿼리 모이면 표본 크기 N 자체가 갱신"**

7. **본 연구 집중 단계 ★ badge carry** — STEP ① 박스의 "본 연구 집중 단계 ★" purple badge 그대로 유지 (★ 별표 노출 단 이 위치만 절대 규칙 6 예외 — 슬라이드 안 본 연구 강조 단계 시각 표시 carry).

---

## 변경 X — carry slide (11 slide)

slide **1·4·6·7·8·9·10·11·12·13·14** 모두 v18 그대로 carry. 시각·텍스트·자산 모두 PNG byte 동일 검증 가능.

---

## ▲ ▲ ▲ 단일 복붙 끝 ▲ ▲ ▲

## 적용 방법

1. claude.ai/design 동일 대화창 (`019e1a41-701c-7134-9ce1-1247262c1563`) 진입
2. 본 prompt 의 ▼ ~ ▲ 구간 전체 복붙
3. v19 14 slide PPTX 다운로드 → 파일명 예상 `____ (3).pptx` 또는 직접 명명
4. Claude Code 가 v19 14 slide 추출 + visual 정합 검증 (3 polishing slide 변경 + 11 carry slide PNG byte 동일)
5. 사용자가 slide 1·4·6·7·8·9·10·11·12·13·14 순차 검토 진행

## 다음 세션 task carry (slide 1·4·6·7·8·9·10·11·12·13·14)

v19 적용 후 다음 11 slide 도 사용자 검토 → 추가 polishing prompt 누적 작성 → v20 → v21 → ... → 최종 LearnUs 업로드 (5/26 23:59 마감)

**전 슬라이드 공통 룰 (carry)**:
- 약어 처음 등장 시 풀어쓰기 (HNSW · ECQO · DEEP · SIFT 등)
- 텍스트 줄 정렬 일관성 (좌측 정렬·padding 16px)
- 수치 강조보다 시각 자료 활용
- 텍스트 작게 보이지 X, 큰 강조·직관 우선
- 청중 5-7 초 안에 읽을 수 있는 정도
- 코드명 / 기술 용어는 한국어 풀이 동반
