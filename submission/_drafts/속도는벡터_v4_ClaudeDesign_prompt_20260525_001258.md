# 속도는벡터 — 최종 발표 deck (12 slide) Claude Design prompt v4

> **대상**: claude.ai/design "최종발표" 대화창 `/p/019e1a41-701c-7134-9ce1-1247262c1563`
> **목적**: 본 prompt 안 12 slide design system 지시를 그대로 복붙해 12 슬라이드 시안 일괄 생성. design system 동결 carry — 새 대화창 X, 동일 대화창 안에서 design 일관성 유지.
> **사용법**:
>   1. claude.ai/design 위 대화창 열기
>   2. 본 문서 §0 design system foundation 부분 먼저 한 번 복붙 (한 번 명령)
>   3. §1 ~ §12 각 slide prompt 차례로 복붙해 슬라이드 한 장씩 생성
>   4. 12 슬라이드 완성 후 export → 백지 구글 PPT 에 합성
> **storyline v4 동반**: `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.md` 본문·발표자 narrative carry

---

## 0. Design System Foundation (대화창에 1 회 복붙)

```
이번 대화창에서 12 슬라이드 deck 을 만들어 줘. 모든 슬라이드에 공통으로 적용할 design system 부터 동결할게.

## Design System (12 slide 공통 · 변경 X)

**캔버스**
- 종횡비: 16:9 (1920×1080 권장)
- 배경색: 흰색 #FFFFFF
- 슬라이드 사이드 여백: 좌우 80px · 상하 56px

**팔레트**
- navy 앵커: #1E3A5F (모든 슬라이드의 주 텍스트 · 강조선 · 헤더)
- 악센트 (chapter 별 차등):
  - 배경 chapter (slide 2·3·4): cyan #0EA5E9
  - 방법 chapter (slide 5·6·7·8): purple #8B5CF6
  - 결과 chapter (slide 9): green #10B981
  - 적용 chapter (slide 10·11): orange #F97316
- hero gradient (slide 1·12 표지·마감): navy #1E3A5F → cyan #0EA5E9 좌→우
- 보조 회색:
  - light gray #F3F4F6 (배경 박스)
  - medium gray #9CA3AF (보조 텍스트·dimmed 요소)
  - red #DC2626 (X 표시 · 오류 indicator)
- 모든 hero number (89.1%·5.77× 등) navy → 악센트 그라데이션 적용

**타이포그래피**
- 폰트: Apple SD Gothic Neo (또는 Pretendard·Noto Sans KR fallback)
- hero 제목 (slide 1·12): 60-72pt Bold
- 헤더 (slide 2-11 상단): 36-42pt Bold
- 부제: 28-32pt Regular
- 본문 강조: 18-22pt Regular
- 본문: 14-18pt Regular
- 라벨·메모: 11-14pt Regular opacity 0.55
- 표 내부: 12-14pt
- monospace (SQL 등): Menlo / SF Mono 14-16pt
- 자간 -1%, 줄 간격 1.3-1.4

**chapter badge (slide 2-11 좌상단)**
- 크기: 64×24px 둥근 사각 (radius 4px)
- 색: 해당 chapter 악센트 + 흰 글자 (cyan/purple/green/orange)
- 텍스트: "배경" · "방법" · "결과" · "적용" (12-14pt Bold)
- 위치: 좌상단 여백 80px · 56px 안

**공통 layout 룰**
- 모든 슬라이드 hero 위치: 중앙 또는 헤더 바로 아래
- 좌·우 1/3-2/3 분할 또는 상·하 1/2 분할 권장 (slide 별 명시)
- 텍스트 박스 padding 24px
- 박스 테두리: 가는 navy 1pt 또는 악센트 굵은 3pt (강조 시)
- 그림자 사용 X (flat design)
- 페이지 번호 X (강제 룰)

**절대 금지**
- 어두운 배경·매거진 스타일 X
- 별표 ★ 노출 X (storyline 안에서만 강조용)
- 영문 메타 라벨 X (한국어 통일)
- "영역" 필러 토큰 X
- 텍스트 잘림·박스 겹침 X
- 코드명 (B1·CaseA·CaseB) 노출 X — 한국어 라벨 "베이스라인·단독 대체·결합" 통일

OK 하면 이제 slide 1 부터 보내줄게.
```

---

## 1. 슬라이드 1 — 표지

```
slide 1 — 표지. hero treatment, navy → cyan 그라데이션 강조.

## Layout

좌상단 1/2 영역: hero 제목 영역
중앙 약간 좌측 1/3 영역: 큰 여백 (절제미)
우하단 1/3 영역: 팀 + 메타 영역

## 텍스트 (그대로 입력)

**hero 메인 (60-72pt navy → cyan 그라데이션 좌→우, Bold)**
인덱스 부재 시 Adaptive Sampling 개선

**hero 부제 (28-32pt navy Regular, "—" 대시로 메인과 분리)**
— 표본 선택 단계의 통제 실험

**팀명 (22-26pt navy Bold)**
속도는벡터

**팀원 (18-20pt navy Regular, "·" 점 구분자)**
박세은 · 강재현 · 조현빈 · 이동욱

**메타 라인 1 (12-14pt navy opacity 0.55)**
2026-1학기 캡스톤 디자인 · 연세대학교 컴퓨터과학과

**메타 라인 2 (12-14pt navy opacity 0.55)**
지도교수 박광현 (BDAI 연구실) · 지도연구원 임채림 · 멘토 박성원 (삼성전자 AI센터)

## Visual

- chapter badge: 없음 (hero 영역)
- 하단 마감 라인: navy 1pt 가는 가로 선 (슬라이드 좌·우 끝 잇기, 하단 56px 위)
- 우상단 작은 dotted 패턴 (cyan 점, opacity 0.15) — 액센트만, 너무 크지 않게

표지 톤은 절제·정돈·여백 강조. 청중이 한 호흡으로 제목과 팀 모두 읽을 수 있는 layout.
```

---

## 2. 슬라이드 2 — VAQ 분석가 시나리오 + 실제 SQL

```
slide 2 — VAQ 분석가 시나리오 + 실제 측정 SQL. chapter "배경" cyan 진입.

## Layout

좌상단: chapter badge "배경" cyan #0EA5E9
상단 헤더: 슬라이드 전폭
좌측 1/5: 분석가 illustration (Gemini Nano Banana Pro 자산 placeholder)
중앙 3/5: SQL 쿼리 박스 (hero)
우측 1/5: 분해 → 결합 illustration (Gemini Nano Banana Pro 자산 placeholder)
하단: 한 줄 정의

## 텍스트

**chapter badge (좌상단)**: 배경

**헤더 (36-42pt navy Bold)**
벡터 증강 분석 쿼리 (VAQ)

**좌측 분석가 말풍선 (14-16pt navy Regular, 둥근 말풍선 모양)**
〝공급자 부품과 비슷한 부품들의 2024년 매출 분석〟

**중앙 SQL 박스 (hero)**

박스 스펙:
- 외곽: 가는 navy 1pt
- 배경: 흰색
- padding 24px
- 폰트: Menlo 14-16pt

SQL 내용 (verbatim, 색 코딩):
```
SELECT l_orderkey, SUM(l_extendedprice * (1 - l_discount)) AS revenue
FROM customer JOIN orders JOIN lineitem
WHERE lineitem.emb <-> :부품_이미지_벡터 < 0.3       ← 벡터 유사도 검색
  AND o_orderdate < '1995-03-15'                     ← 관계형 필터·조인
  AND c_mktsegment = 'BUILDING'
GROUP BY l_orderkey ORDER BY revenue DESC;
```

색 코딩:
- "lineitem.emb <-> :부품_이미지_벡터 < 0.3" 한 줄 = cyan #0EA5E9 highlight (배경 박스)
- "o_orderdate < ..." · "c_mktsegment = ..." 두 줄 = navy #1E3A5F highlight (배경 박스)
- 우측 끝에 화살표 + 라벨: "← 벡터 유사도 검색" · "← 관계형 필터·조인" (12pt navy)

**우측 illustration placeholder**: "[Nano Banana Pro 자산: 부품 이미지 → 유사 벡터 클러스터 + 3 테이블 → 두 화살표 합쳐져 VAQ]" 영역만 잡아주고 실제 이미지는 후속 합성

**하단 정의 한 줄 (24-28pt navy Bold, 가로 중앙 정렬)**
벡터 유사도 검색 + 관계형 분석이 한 SQL 안에 — VAQ
```

---

## 3. 슬라이드 3 — 카디널리티 → 1만 배

```
slide 3 — 카디널리티 한 곳이 잘못되면 최대 1만 배. plan 트리 좌·우 비교.

## Layout

좌상단: chapter badge "배경" cyan
상단 헤더
좌상단 작은 영역 (좌측 상단 1/4): JOIN 개념 박스
중앙 hero: plan 트리 두 개 좌우 비교 (전체 폭의 70%)
하단 hero: "10,000× 응답 시간 차이"

## 텍스트

**chapter badge**: 배경

**헤더 (36-40pt navy Bold)**
카디널리티 한 곳이 잘못되면 — 최대 1만 배 느려짐

**좌상단 JOIN 개념 박스 (light gray #F3F4F6 배경, padding 16px, 약 320×200px)**

| 개념 | 한 줄 설명 |
|---|---|
| **JOIN** | 여러 테이블의 행을 연결하는 연산 |
| **Nested Loop** | 작은 데이터에 빠름 — 한 행씩 짚어가며 |
| **Hash Join** | 큰 데이터에 빠름 — 해시 테이블에 올려놓고 한꺼번에 |
| **선택 기준** | **카디널리티** — 각 단계 행 수 예측 값 |

표 폰트: 12-14pt navy, 헤더 굵은체

**중앙 hero plan 트리 비교 (전체 폭의 70%, 가로 양분)**

좌측 (❌ 카디널리티 추정 틀림):
- 외곽: 빨강 #DC2626 dashed 테두리 3pt
- 위 라벨: "❌ 카디널리티 추정 틀림" (red 18pt Bold)
- plan 트리: 큰 Hash Join 루트 (꼭대기) · 거대한 sub-tree
  - "Hash Join" navy 박스 (붉은 톤 boundary)
  - 하위 노드: HashAggregate · Hash · Seq Scan (큰 박스, "lineitem 전체 6M 행" 라벨)
- 트리 하단 라벨: "pgvector 고정 selectivity 33.3% → 약 333,333 행 예측"
- 더 아래: "메모리에 큰 중간 테이블이 쌓임 → 느림"

우측 (✓ 정확한 카디널리티):
- 외곽: cyan #0EA5E9 실선 3pt
- 위 라벨: "✓ 정확한 카디널리티" (cyan 18pt Bold)
- plan 트리: 작은 Nested Loop 루트 (꼭대기) · 작은 sub-tree
  - "Nested Loop" navy 박스 (cyan boundary)
  - 하위 노드: Index Scan · Index Scan · Index Scan (작은 박스, "벡터 결과 ~100 행" 라벨)
- 트리 하단 라벨: "Exqutor 정확 추정 → 실제 ~100 행"
- 더 아래: "벡터 결과 먼저 → 한 행씩 빠르게 풀어냄"

두 트리 사이: 굵은 수직 분리선 (navy 2pt) + 위쪽 라벨 "같은 SQL · 같은 데이터" (14pt navy opacity 0.7)

**하단 hero (대형)**

큰 텍스트 (60-72pt navy → red #DC2626 그라데이션 좌→우, Bold):
**10,000× 응답 시간 차이**

부제 (16pt navy opacity 0.55):
TPC-H Q3 VAQ on DEEP
```

---

## 4. 슬라이드 4 — 기존 시스템 고정 비율

```
slide 4 — 기존 3 시스템 고정 비율 33/50/100%. 데이터 무관 한계 명시.

## Layout

좌상단: chapter badge "배경" cyan
상단 헤더
좌측 1/2: 3 시스템 비교 hero (가로 막대 3 개)
우측 1/2: 실제 selectivity 분포 그래프
하단: 한 줄 강조

## 텍스트

**chapter badge**: 배경

**헤더 (36-40pt navy Bold)**
기존 시스템 — 데이터 무관 고정 비율

**좌측 3 시스템 비교 (수직 layout, 3 가로 막대)**

| 시스템 | 막대 길이 | 큰 % 숫자 |
|---|---|---|
| **pgvector** | 1/3 채움 (cyan #0EA5E9) | **33.3%** (44-48pt navy Bold) |
| **VBASE** | 1/2 채움 (cyan #0EA5E9) | **50%** (44-48pt navy Bold) |
| **DuckDB-vss** | 가득 채움 (cyan #0EA5E9) | **100%** (44-48pt navy Bold) |

3 막대 모두:
- 막대 외곽: navy 1pt
- 막대 채움 색: cyan #0EA5E9
- 빈 영역: light gray #F3F4F6
- 막대 좌측에 시스템 이름 (20-24pt navy Bold)
- 막대 우측에 큰 % (44-48pt navy Bold)
- 막대 폭: 약 240px · 높이 40px

**우측 selectivity 분포 그래프**

- x축: 거리 임계값 D (로그 스케일, 0.001 ~ 10)
- y축: 실제 selectivity (로그 스케일, 0.0001 ~ 1.0)
- 데이터: cyan 점들 폭넓게 분포 (네 자릿수 변동 시각화)
- 3 고정 비율 가로 점선 (회색 dashed): 33.3% · 50% · 100% 수평선
- 그래프 상단 라벨: "실제 vector selectivity (DEEP·SIFT·SSN·YFCC sf=10)"
- 그래프 폭: 약 480×300px

**두 영역 분리**: 좌·우 사이에 굵은 "vs" navy 텍스트 (28pt) + 양방향 화살표 (작게)

**하단 한 줄 강조 박스**:
- 빨강 #DC2626 dashed 테두리 2pt 박스 (가로 폭 60%, 중앙 정렬)
- 내부 텍스트 (20-24pt navy Bold):
**데이터·임계값 무관 — 거의 모든 쿼리에서 잘못된 plan**
```

---

## 5. 슬라이드 5 — Adaptive Sampling 5 단계

```
slide 5 — Adaptive Sampling 5 단계 흐름도. chapter "방법" purple 진입.

## Layout

좌상단: chapter badge "방법" purple #8B5CF6
상단 헤더
중앙 hero (전체 폭의 90%): 5 단계 흐름 다이어그램 (좌→우)
하단 강조 박스

## 텍스트

**chapter badge**: 방법 (purple #8B5CF6 색)

**헤더 (36-40pt navy Bold)**
인덱스가 없을 때 — Adaptive Sampling

**중앙 hero — 5 단계 흐름도**

5 노드 + 화살표 (좌→우):

1. **Query** (회색 작은 박스, 시작점) →
2. **① 표본 추출** (purple 굵은 테두리 3pt + ★ 마크 + "본 연구 집중 단계" 라벨)
   - 아이콘: 균일 무작위 점들 (cyan)
   - 라벨: "무작위 베르누이 / N=385"
3. → **② 카디널리티 추정** (navy opacity 0.5 박스)
   - 아이콘: 막대 그래프
   - 라벨: "표본 위에서 추정"
4. → **③ Q-error 측정** (navy opacity 0.5 박스)
   - 아이콘: 두 막대 비교
   - 라벨: "추정 오차 측정"
5. → **④ Momentum 조정** (navy opacity 0.5 박스)
   - 아이콘: 회전 화살표
   - 라벨: "momentum 으로 다음 표본 크기 조정"
6. → 루프 화살표 → (다음 Query)

★ ① 표본 추출 노드만 다른 4 노드와 시각 차등:
- 외곽: purple #8B5CF6 굵은 3pt
- 배경: light purple opacity 0.1
- 상단 ★ 별 마크 (cyan/purple)
- 위쪽 라벨: "본 연구가 집중하는 한 단계" (16-18pt purple Bold)

각 노드 박스 폭 약 200×140px · 화살표 굵기 2pt navy

**하단 강조 박스 (purple 좌측 굵은 세로선 4pt + 흰 배경, 폭 80% 중앙)**

내부 텍스트 (20-24pt navy Bold):
다섯 단계 중 **표본 추출 단계 한 곳만** 통제 변인으로 분리 → 본 연구

**우측 작은 메모 (12pt navy opacity 0.55)**:
"매 50 쿼리마다 표본 크기 갱신 / 표본 예산 N=385 고정"
```

---

## 6. 슬라이드 6 — 본 연구 문제 정의 + 제목

```
slide 6 — 본 연구 문제 정의 + 제목. slide 5 ★ 표본 추출 단계 zoom-in.

## Layout

좌상단: chapter badge "방법" purple
상단 (1/5): slide 5 흐름도 축약 thumbnail
중앙 hero (3/5): 문제 정의 + 우측 두 방식 시각 대비
하단 (1/5): 본 연구 제목 + 메모

## 텍스트

**chapter badge**: 방법

**헤더 (28-32pt navy Bold)**
본 연구

**상단 thumbnail (slide 5 흐름도 축약)**
- 5 단계 노드 회색 thumbnail (작게)
- ★ 표본 추출 단계만 purple zoom-in 박스로 확대 (시각적 zoom 화살표)

**중앙 hero — 좌·우 분할**

좌측 (60%, 문제 정의 hero):
- 큰 질문 박스
  - 외곽: 가는 navy 1pt + 좌측 굵은 purple 세로선 6pt
  - 배경: light gray #F3F4F6
  - 텍스트 (36-48pt navy → cyan 그라데이션 Bold, 따옴표 〝〟 포함):

〝카디널리티 추정을 더 잘할 수 있는
 표본 추출 방식은 무엇일까?〟

우측 (40%, 두 방식 시각 대비):
- 위 박스 (24-28pt navy Bold "베르누이"):
  - 균일 무작위 점들 아이콘 (cyan)
- 사이 굵은 "vs" 또는 "?" navy
- 아래 박스 (24-28pt navy Bold "분포 인지 층화"):
  - cluster 그룹화 점들 아이콘 (purple/green)

**하단 (1/5)**:

본 연구 제목 (24-28pt navy Bold, 좌측 정렬):
인덱스 부재 시 Adaptive Sampling 개선
— 표본 선택 단계의 통제 실험

회색 한 줄 (14pt navy opacity 0.55):
표본 예산 N=385, momentum 조정 — paper carry
```

---

## 7. 슬라이드 7 — 통제 실험 3 카드

```
slide 7 — 통제 실험 3 카드 (베이스라인·단독 대체 ❌·결합 ★).

## Layout

좌상단: chapter badge "방법" purple
상단 헤더
상단 라벨 + 분기 화살표
중앙 hero: 3 카드 (좌·중·우, 폭 차등)
하단 hero: 측정 수 강조

## 텍스트

**chapter badge**: 방법

**헤더 (36-40pt navy Bold)**
통제 실험 설계 — 한 측정 안에 세 방식 동시 산출

**상단 라벨 + 분기**

상단 가로 중앙 (14pt navy opacity 0.6):
"한 측정 cell 에서"

분기 ∨ 모양 화살표 (navy 2pt):
중앙 시작 → 좌 · 중앙 · 우 세 카드로 갈라짐

**중앙 hero 3 카드**

| 위치 | 카드 | 외곽·배경 | 메모 |
|---|---|---|---|
| **좌측 (1/3 hero, 큰 카드)** | **베이스라인** | navy 굵은 3pt + 흰 배경 | "Exqutor §V-B paper" |
| **중앙 (1/3 작은 카드, 흐림)** | **단독 대체** | 회색 #9CA3AF opacity 0.45 + 대각선 굵은 ❌ overlay (red #DC2626 8pt) | "본 발표에 포함하지 않음" |
| **우측 (1/3 hero, 큰 카드, ★ 표시)** | **결합** | cyan 굵은 3pt + 흰 배경 + 우상단 ★ (cyan) | "★ 본 연구 핵심" |

각 카드 내용:

좌 카드 (베이스라인):
- 상단 (24-28pt navy Bold): 베이스라인
- 아이콘: 균일 무작위 점들 (cyan)
- 본문 (16-18pt navy Regular): 무작위 베르누이 / Exqutor §V-B 그대로

중앙 카드 (단독 대체):
- 상단 (24-28pt 회색 #9CA3AF Bold): 단독 대체
- 대각선 굵은 ❌ X 표시 (red, 카드 전체 가로 지름)
- 아이콘 (회색): cluster 점들 + ❌
- 본문 (14pt 회색 Regular): 분포 인지로 통째 바꿈 / 결과 표시 X

우 카드 (결합):
- 상단 (24-28pt navy Bold): **결합**
- 우상단 ★ 마크 (cyan)
- 아이콘: 두 화살표 합쳐져 → 평균 박스 (cyan + navy)
- 본문 (16-18pt navy Regular): 두 추정값 산술 평균 / 본 연구 핵심

세 카드 폭: 좌·우 큰 카드 각 30% · 중앙 작은 카드 25% · 사이 여백 5% 씩

**세 카드 하단 라벨 (가로, 14pt navy opacity 0.6)**:
"동시 산출 → 외생 변수 통제"

**하단 hero**:
- 큰 텍스트 (40-48pt navy Bold, 중앙 정렬):
**1,508 cell × 3 방식 = 4,524 짝 비교**
```

---

## 8. 슬라이드 8 — 표본 추출 방식 분류 7 paradigm

```
slide 8 — 표본 추출 방식 분류. 좌측 베이스라인 단일 카드 + 우측 7 paradigm grid.

## Layout

좌상단: chapter badge "방법" purple
상단 헤더
좌측 1/4: 베이스라인 단일 카드 (큰 hero)
우측 3/4: 7 paradigm grid (4+3 또는 3×3 with 빈 2)
하단 한 줄

## 텍스트

**chapter badge**: 방법

**헤더 (32-36pt navy Bold)**
표본 추출 방식 — 베르누이 vs 분포 인지 13 method

**좌측 베이스라인 카드 (큰 hero, 폭 23%)**:
- 외곽: navy 굵은 3pt
- 상단 (28-32pt navy Bold): 베르누이
- 아이콘: 균일 무작위 점들 (cyan, 큰 그림)
- 본문 (16pt navy Regular): 무작위 균일 추출 / paper carry
- 하단 메모 (12pt navy opacity 0.55): Exqutor §V-B

**중앙 분리 (좌·우 사이)**:
- 굵은 "vs" navy (24pt) + 양방향 화살표
- 위쪽 라벨 (14pt navy opacity 0.6): "단 한 단계만 다른"

**우측 7 paradigm grid (폭 70%, 4 행 × 2 열 또는 3 행 × 3 열)**

각 paradigm 카드:
- 외곽: cyan #0EA5E9 가는 2pt 테두리
- 배경: light gray #F3F4F6
- 크기: 약 220×140px
- padding: 12px

각 카드 내용:

| paradigm | 아이콘 | 한국어 라벨 (16-18pt navy Bold) | 대표 method (12-14pt navy Regular) |
|---|---|---|---|
| 1. **클러스터링** (P1) | 점 색 그룹 (3 색 cluster) | 클러스터링 | MiniBatch-KMeans · KMeans |
| 2. **공간 곡선** (P2) | 지그재그 Hilbert curve | 공간 곡선 (PCA 환원) | PCA 2D + Hilbert · PCA 4D + Skilling |
| 3. **스트리밍** (P3) | 점이 줄지어 흐름 | 스트리밍 | Chao priority sampling |
| 4. **차원 축소** (P4) | 다차원 → 평면 투영 | 차원 축소 | PCA1D · Sparse RP · ICA |
| 5. **고전 stratification** (P5) | 누적 분포 곡선 | 고전 stratification | cum-√f · take-all + cum-√f |
| 6. **양자화·히스토그램** (P6) | pixel grid | 양자화·히스토그램 | 2D equi-depth grid · 1-bit sign bucket |
| 7. **해시 partitioning** (P5b) | bucket hash 도형 | 해시 partitioning | md5 prefix hash |

각 아이콘은 우측 navy 작은 그림으로 위치 (Nano Banana Pro 자산 placeholder).

**하단 한 줄 (가로 라인 위 hero, 20-22pt navy Bold, 중앙 정렬)**:
13 method 모두 **표본 추출 방식**만 다름 · momentum 조정·표본 예산 N=385 는 동일 carry
```

---

## 9. 슬라이드 9 — 결합 89.1% 결과 + 단독 대체 sidebar

```
slide 9 — 결합 89.1% paired 우위 + 우측 단독 대체 sidebar. chapter "결과" green 진입.

## Layout

좌상단: chapter badge "결과" green #10B981
상단 헤더
좌측 메인 (2/3): paired Δ% histogram + 우측 hero 89.1%
우측 sidebar (1/3): 단독 대체 회색 + ❌
하단: 한 줄 mean 비교

## 텍스트

**chapter badge**: 결과 (green #10B981 색)

**헤더 (36-40pt navy Bold)**
결합이 베이스라인을 89.1% 이긴다

**좌측 메인 (2/3)**:

상단 paired Δ% histogram (폭 60% · 높이 약 360px):
- x축: paired Δ% (-30% ~ +30%)
- y축: 셀 개수
- 좌측 영역 (Δ%<0): cyan #0EA5E9 fill (89.1% 영역)
- 우측 영역 (Δ%>0): red #DC2626 fill (10.9% 영역)
- 0% 수직선: navy 2pt 굵은 선
- 중앙값 −4.38% dashed marker (navy)
- 라벨: "paired Δ% 분포 — 결합 vs 베이스라인 (1,508 cell)"

histogram 우측 hero (40% 영역):
- 큰 숫자 (80-100pt navy → cyan 그라데이션 Bold):
**89.1%**
- 부제 (18pt navy Regular):
1,344 / 1,508 cell
결합 우위

**하단 mean 비교 미니 bar (전체 폭, 높이 약 80px)**:
- 베이스라인 navy ▆ "1.4582" (왼쪽)
- 결합 cyan ▃ "1.4019" (오른쪽, 약 3.86% 작음)
- 우측 라벨 (14pt navy): "약 3.86% 더 정확 (mean) · median Δ% −4.38%"

**우측 sidebar (1/3, 단독 대체)**:
- 외곽: 회색 #9CA3AF 가는 1pt
- 배경: light gray #F3F4F6
- 좌상단 굵은 빨강 ❌ X 표시 (slide 7 visual signature 와 동일)
- 위쪽 라벨 (16-18pt 회색 navy Bold):
단독 대체 ❌
- 메모 (12pt 회색 navy opacity 0.6):
(slide 7 에서 ❌ 표시한 그 방식)

- 큰 숫자 (40-48pt 회색 navy Bold):
35.2%

- 부제 (16pt red Bold):
평균 Δ% +12.90% 악화

- 하단 한 줄 (14pt 회색 navy):
→ 단독 대체 = 베이스라인보다 나쁨

- 우상단 작은 화살표 + "from slide 7" (12pt navy opacity 0.5)
```

---

## 10. 슬라이드 10 — 엔진 속도 + plan 회복 94.9%

```
slide 10 — 3-way 엔진 속도 + plan 회복 94.9%. chapter "적용" orange 진입.

## Layout

좌상단: chapter badge "적용" orange #F97316
상단 헤더
상단 1/2: 3-way 가로 막대 bar chart hero
하단 1/2: 좌측 plan 일치 도넛 + 중앙 plan 회복 bar + 우측 hero 박스 94.9%

## 텍스트

**chapter badge**: 적용 (orange #F97316 색)

**헤더 (36-40pt navy Bold)**
실제 엔진 응답 시간 — 속도와 plan 회복

**상단 (1/2) 3-way 속도 비교**

3 가로 막대 (수직 layout, 막대 폭 약 60% · 막대 높이 40px):

| 시스템 | 막대 길이 | 큰 배수 |
|---|---|---|
| **pgvector 기본** | 가장 짧음 (navy 흐림) | **1.0×** (44-48pt navy Bold) |
| **베이스라인 inject** | 5.77 배 길음 (cyan #0EA5E9) | **5.77×** (44-48pt navy Bold) |
| **결합 inject** | 5.70 배 길음 (cyan 진함) | **5.70×** (44-48pt navy Bold) |
| oracle reference | dashed (회색) | (5.65×, 작게) |

오른쪽 끝 화살표 + 라벨 (16-18pt cyan Bold):
"주입만 하면 ~5-6×"

부제 (14pt navy opacity 0.55):
참고 oracle 5.65× · 12 cell trim mean 평균 5.67×

**하단 (1/2) 3 단 layout**

좌측 (1/4) plan 일치 도넛:
- 도넛 외경 약 240px
- 92.7% cyan #0EA5E9 (same plan)
- 7.3% orange #F97316 (different plan)
- 중앙 라벨 (14pt navy): "700 paired cell (3 평면 통합)"
- 도넛 우측 mini legend: "● 92.7% 같은 plan / ● 7.3% 다른 plan"

중앙 (1/4) plan 회복 robustness bar (수직 layout):
- "베이스라인 7/12 cell" navy bar
- "결합 148/156 plan (94.9%)" cyan bar (훨씬 김)
- 라벨 (14pt navy): "plan 회복 robustness"

우측 (2/4) hero 박스:
- 외곽: navy 굵은 3pt
- 배경: navy #1E3A5F (어두운 hero)
- 흰 텍스트 (24-28pt Bold):
**결합 13 method 의**
**plan 회복 robustness 94.9%**
- cyan 부제 (16pt):
B1 단독 7/12 cell → CaseB 148/156 plan

**하단 마무리 (전체 폭, 가로 중앙)**:
- 작은 navy 한 줄 (12pt opacity 0.55):
"통계: variance condition % SS 0.00% · p=0.945 (3 평면 통합)"
```

---

## 11. 슬라이드 11 — Future Work 두 갈래

```
slide 11 — Future Work 두 갈래 카드 (Group A 검증 확장 + Group B history-aware).

## Layout

좌상단: chapter badge "적용" orange
상단 헤더
좌·우 2 카드 (각 1/2 폭)
하단 한 줄

## 텍스트

**chapter badge**: 적용

**헤더 (36-40pt navy Bold)**
Future Work — 두 갈래 후속 방향

**좌 카드 (1/2, Group A: 검증 범위 확장 + 산업 자원 분석)**:
- 외곽: orange #F97316 가는 2pt
- 배경: light gray #F3F4F6
- 상단 아이콘 (Nano Banana Pro placeholder): 확장 화살표 (작은 점 클러스터 → 큰 점 클러스터)
- 상단 라벨 (20-24pt navy Bold):
Group A — 검증 범위 확장

본 측정의 제한 (14-16pt navy Regular):
· pgvector 한 엔진 · 일부 scale factor

**확장 방향 3 줄 (16-18pt navy Regular, 좌측 정렬, ① ② ③ 번호 cyan Bold)**:
① **scale factor 확장** — sf 1 ~ 100+ 전 범위
② **다른 엔진** — VBASE · DuckDB-vss · Milvus
③ **산업 자원 trade-off** — RAM · CPU · sample storage 소모 분석

각 줄 좌측에 작은 보조 아이콘 (cyan/navy):
- ① scale 게이지
- ② DB 4 로고 (작게)
- ③ 자원 미터

**우 카드 (1/2, Group B: History-aware Adaptive Sampling)**:
- 외곽: cyan #0EA5E9 가는 2pt
- 배경: light gray #F3F4F6
- 상단 아이콘 (Nano Banana Pro placeholder): 과거 query 박스 3 개 → 현재 query 박스 1 개 + feedback 화살표 누적
- 상단 라벨 (20-24pt navy Bold):
Group B — History-aware Adaptive Sampling

**3 단계 흐름 다이어그램 (각 단계 박스 + 아래 화살표)**:

박스 1 (16-18pt navy):
유사 query 의 **과거 selectivity feedback** 누적
↓
박스 2:
현재 vector predicate cardinality 를
**더 적은 sampling 으로** 추정
↓
박스 3 (cyan Bold):
sampling cost ↓ · 정확도 carry · **latency 개선 후보**

**두 카드 하단 (각 카드 안)**:
좌 카드: "Group A: 본 연구 검증 carry-on" (14pt navy opacity 0.55)
우 카드: "Group B: 새 알고리즘 후보" (14pt navy opacity 0.55)

**하단 한 줄 (전체 폭, navy 가는 라인 위 hero, 20-22pt navy Bold, 중앙 정렬)**:
둘 다 본 연구 controlled verification 결과 위에서 다음 사람이 이어할 수 있는 방향
```

---

## 12. 슬라이드 12 — 감사합니다 + Q&A

```
slide 12 — 마감 표지. slide 1 표지와 hero 그라데이션 호응.

## Layout

slide 1 표지와 동일 hero 구조 carry:
좌상단 1/2 영역: hero 감사 영역
우하단 1/3 영역: 팀 + 메타 영역
중앙: 큰 여백

## 텍스트 (그대로 입력)

**hero 메인 (60-80pt Apple SD Gothic Neo Bold, navy → cyan 그라데이션 좌→우)**
감사합니다

**부제 (24-28pt navy Regular)**
Q&A 환영합니다

**팀명 (22-26pt navy Bold, slide 1 carry)**
속도는벡터

**팀원 (18-20pt navy Regular, · 점 구분자)**
박세은 · 강재현 · 조현빈 · 이동욱

**감사 라인 1 (12-14pt navy opacity 0.55)**
지도교수 박광현 (BDAI 연구실) · 지도연구원 임채림

**감사 라인 2 (12-14pt navy opacity 0.55)**
멘토 박성원 (삼성전자 AI센터)

**우하단 작게 (선택, 12pt navy opacity 0.55)**
자료 · 코드 — github.com/johyunbin/Capstone

## Visual

- chapter badge: 없음 (hero 영역)
- 하단 마감 라인: navy 1pt 가는 가로 선 (slide 1 carry)
- 우상단 작은 dotted 패턴 (cyan 점, opacity 0.15) — slide 1 carry

slide 1 과 시각 양식이 완벽히 호응해서 청중에게 "처음과 끝" 의 narrative arc 가 닫힌 느낌을 주는 게 핵심.
```

---

## 13. 사용 체크리스트

### 13.1 사용 직전 확인

- [ ] claude.ai/design "최종발표" 대화창 (`/p/019e1a41-701c-7134-9ce1-1247262c1563`) 열기 — 새 대화창 X
- [ ] §0 design system foundation 복붙 → "OK" 응답 대기
- [ ] §1 (slide 1) 부터 §12 (slide 12) 순서대로 복붙
- [ ] 각 slide 생성 후 export (PNG·SVG) → 백지 구글 PPT 한 슬라이드씩 합성

### 13.2 12 slide 일관성 검증

12 슬라이드 생성 후 다음 항목 일관성 확인:

- [ ] navy `#1E3A5F` 앵커 색 모든 슬라이드 통일
- [ ] chapter badge (배경 cyan · 방법 purple · 결과 green · 적용 orange) 좌상단 통일
- [ ] hero gradient (navy → cyan) slide 1·12 일관성
- [ ] Apple SD Gothic Neo 폰트 통일
- [ ] 텍스트 잘림·박스 겹침 0 건
- [ ] 페이지 번호 X (강제 룰)
- [ ] 별표 ★ slide 안 X (storyline 안에서만)
- [ ] 코드명 (B1·CaseA·CaseB) 노출 X — "베이스라인·단독 대체·결합" 한국어 통일

### 13.3 Nano Banana Pro 자산 합성

- 각 slide 안 illustration placeholder (slide 2·3·5·6·8·11) 에 Gemini Nano Banana Pro brief 로 생성한 자산 합성
- 자산 brief: `submission/_drafts/속도는벡터_v4_NanoBananaPro_brief_<TS>.md` carry

---

## 14. storyline v4 동반

본 prompt 의 슬라이드별 텍스트·시각 spec 은 다음 storyline v4 정본에서 carry:

- `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.md`

storyline v4 의 §2-§13 slide 별 텍스트·시각·발표자 narrative 와 본 prompt 의 layout·design spec 이 1:1 매칭. 발표자 발화 (narrative) 는 본 prompt 에는 포함 X — storyline v4 carry.

---

작성: 2026-05-25 00:13 KST · 12 slide design prompt v4. 5/26 23:59 PPT 마감 critical path. 본 prompt 그대로 claude.ai/design 대화창에 복붙 진행 가능.
