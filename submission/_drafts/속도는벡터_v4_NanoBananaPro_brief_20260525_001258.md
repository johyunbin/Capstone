# 속도는벡터 — 최종 발표 deck Nano Banana Pro illustration brief v4

> **대상**: Gemini Ultra Nano Banana Pro (`gemini-3-pro-image-preview`) — 웹앱·Flow·Whisk
> **목적**: 12 슬라이드 deck 안 illustration 자산 생성 brief. Claude Design 으로 만든 layout 위에 합성.
> **자산 6 종** (slide 2·3·5·6·8·11) — 슬라이드 9·10 의 histogram·bar chart·도넛은 데이터 시각화이므로 Claude Design 또는 분석 script (matplotlib) 산출
> **storyline v4 동반**: `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.md`
> **Claude Design prompt 동반**: `submission/_drafts/속도는벡터_v4_ClaudeDesign_prompt_20260525_001258.md`

---

## 0. 공통 design system 동결 (모든 자산 공통)

```
모든 illustration 은 다음 design system 을 일관 적용:

## 팔레트
- navy 앵커: #1E3A5F (선·외곽·주 텍스트)
- cyan: #0EA5E9 (강조·하이라이트)
- purple: #8B5CF6 (방법 chapter 강조)
- green: #10B981 (결과 chapter 강조)
- orange: #F97316 (적용 chapter 강조)
- red: #DC2626 (X 표시·오류)
- light gray: #F3F4F6 (배경 박스)
- medium gray: #9CA3AF (보조 텍스트)
- 흰색 배경 #FFFFFF (모든 자산)

## 스타일
- flat design — 그림자·gradient 최소 (hero 영역만 navy → cyan gradient)
- minimal line illustration — pretendard / Apple SD Gothic Neo 호환 가는 선
- 사람·물건 illustration: anonymous 톤, 색감 navy + cyan palette
- 아이콘: 둥근 모서리 (radius 4-8px) navy 선·cyan 채움
- 도형: clean geometric shapes, decorative element 최소

## 이미지 내 한국어 텍스트
- 폰트: Apple SD Gothic Neo (Nano Banana Pro 의 강점, 한국어 가독성 1위)
- 모든 라벨 한국어 명시 — 영문 alias 병기 X (storyline 룰 carry)
- 텍스트 색: navy #1E3A5F · opacity 1.0 본문 / opacity 0.55 보조

## 종횡비·해상도
- slide 안 부분 illustration: 가로 또는 세로 비율 자유 (slide layout 에 맞춤)
- 출력 해상도: 2x retina 권장 (slide 1920×1080 기준)
- 배경 투명 (transparent PNG 권장, slide 합성 시 백색 배경에 자연 통합)

## 금지
- 어두운 배경 X (모두 흰 배경)
- 별표 ★ 또는 emoji 노출 X
- 영문 메타 라벨 X
- 사진 합성 (photorealistic) X — illustration·diagram 만
- 캐릭터 얼굴 detail X — anonymous 학부생·연구자 톤
```

---

## 1. Asset 1 — Slide 2 분석가 illustration + VAQ 분해 그림

### 1.1 자산 1A: 분석가 illustration (좌측 1/5)

```
illustration 1 장 생성:

피사체:
- 1 명의 학부생 또는 연구자 (anonymous, 얼굴 detail X)
- 책상 앞 모니터 1 개 (navy 외곽, cyan glow)
- 한 손을 모니터 화면을 가리키는 손짓 (질문 하는 톤)

스타일:
- minimal line illustration · navy 선 1.5pt
- 피부색: 부드러운 light gray opacity 0.3 (anonymous 강조)
- 옷: cyan 한 톤 (sweater 또는 hoodie)
- 의자: navy 가는 선

말풍선:
- 둥근 corner 말풍선 (radius 8-12px)
- 외곽: navy 1pt · 배경: 흰색
- 화살표: 학부생 입을 가리킴
- 안의 텍스트 (Apple SD Gothic Neo, 14-16pt navy):
  〝공급자 부품과 비슷한 부품들의
   2024년 매출 분석〟
- 따옴표 〝〟 verbatim 포함

종횡비: 세로 (2:3, slide 2 좌측 1/5 영역)
배경: transparent
출력: PNG 2x retina · 약 480×720px

스토리: 일반 학부생/주니어 분석가가 모니터 앞에서 SQL 질문을 던지는 톤. 학술 발표용이라 진중하되 친근.
```

### 1.2 자산 1B: VAQ 분해 → 결합 그림 (우측 1/5)

```
diagram 1 장 생성:

상단 영역 (벡터 유사도 검색):
- 부품 이미지 1 장 (anonymous 기계 부품 아이콘 — bolt, gear, 또는 abstract 모양)
- 아래 화살표 → "벡터로 변환" 라벨
- 유사 벡터 cluster (작은 cyan 점 6-8 개가 가까이 모여 있음)
- 외곽 라벨 (12pt navy): "벡터 유사도 검색"

하단 영역 (관계형 분석):
- 3 테이블 아이콘 (둥근 사각형 3 개, 각각 다른 라벨)
  - customer (navy 외곽)
  - orders (navy 외곽)
  - lineitem (navy 외곽)
- 3 테이블 사이 연결선 (navy 가는 선 + 작은 다이아몬드 = JOIN 표시)
- 외곽 라벨 (12pt navy): "관계형 분석"

두 영역 사이:
- 굵은 합쳐지는 화살표 2 개 (각 영역 끝 → 중앙으로) — cyan 색
- 중앙 큰 박스 (cyan #0EA5E9 외곽 굵은 3pt + 흰 배경):
  - 텍스트 (Apple SD Gothic Neo 24-28pt navy Bold):
  VAQ
  (벡터 증강 분석 쿼리)

종횡비: 세로 (2:3, slide 2 우측 1/5 영역)
배경: transparent
출력: PNG 2x retina · 약 480×720px

스토리: 두 영역 (벡터 검색 + 관계형 분석) 이 한 SQL = VAQ 에 결합되는 다이어그램. 청중이 그림만 봐도 "두 분야 만남" 이해.
```

---

## 2. Asset 2 — Slide 3 plan 트리 비교 (좌·우 plan tree)

```
diagram 1 장 (또는 좌·우 2 장 분리) 생성:

전체 layout: 가로 (slide 중앙 hero 영역, 전체 폭의 70%, 약 1344×540px)
가운데 굵은 수직 분리선 (navy 2pt) — 두 트리 영역 분리

## 좌측 (잘못된 plan)

외곽: 빨강 #DC2626 dashed 3pt · 배경: 흰색 · 내부 padding 24px

상단 라벨 (24pt red Bold, 중앙 정렬):
❌ 카디널리티 추정 틀림

plan tree (수직 layout, 거대한 트리):
- 루트 박스: 빨강 톤 "Hash Join" (red opacity 0.15 채움 + red 외곽 2pt)
  - 크기: 약 200×60px
- 좌 자식: "HashAggregate"
- 우 자식: "Hash"
- HashAggregate 의 자식: "Seq Scan" (큰 박스, 라벨 "lineitem 전체 6M 행")
- Hash 의 자식: "Seq Scan" (라벨 "orders 전체 1.5M 행")
- 모든 박스: navy 외곽 가는 1pt · 흰 배경 · navy 텍스트 (14pt)
- 연결선: navy 가는 1pt · 트리 일반 layout

트리 하단 라벨 (16pt navy Bold, 중앙):
pgvector 고정 selectivity 33.3%
→ 약 333,333 행 예측

더 아래 (14pt 회색 navy Regular):
"메모리에 큰 중간 테이블이 쌓임 → 느림"

## 우측 (정확한 plan)

외곽: cyan #0EA5E9 실선 3pt · 배경: 흰색 · 내부 padding 24px

상단 라벨 (24pt cyan Bold, 중앙 정렬):
✓ 정확한 카디널리티

plan tree (수직 layout, 작은 트리):
- 루트 박스: cyan 톤 "Nested Loop" (cyan opacity 0.15 채움 + cyan 외곽 2pt)
  - 크기: 약 200×60px
- 좌 자식: "Index Scan" (라벨 "벡터 인덱스 ~100 행")
- 우 자식: "Nested Loop"
  - 그 아래: "Index Scan" × 2 (작은 박스, "lineitem index" · "orders index")
- 모든 박스: navy 외곽 가는 1pt · 흰 배경 · navy 텍스트 (14pt)

트리 하단 라벨 (16pt navy Bold, 중앙):
Exqutor 정확 추정
→ 실제 ~100 행

더 아래 (14pt 회색 navy Regular):
"벡터 결과 먼저 → 한 행씩 빠르게 풀어냄"

## 두 트리 사이 (가운데 분리선 위쪽)

라벨 (14pt navy opacity 0.7, 중앙):
같은 SQL · 같은 데이터

종횡비: 가로 약 2.5:1
배경: transparent
출력: PNG 2x retina

스토리: 한 곳 (vector selectivity) 카디널리티 오차가 plan 트리 전체를 뒤집는 인과 다리. 좌측 거대 트리 (warm tone, 잘못) vs 우측 작은 트리 (cool tone, 정확) — 색·크기 대비만으로 청중이 즉시 "어느 게 좋은가" 파악.
```

---

## 3. Asset 3 — Slide 5 Adaptive Sampling 5 단계 흐름도

```
diagram 1 장 생성:

전체 layout: 가로 (slide 중앙 hero, 전체 폭의 90%, 약 1728×360px)
5 노드 + 화살표 (좌→우 흐름 + 마지막 루프 화살표)

## 5 노드 디자인

1. **Query** (시작점)
- 박스: 회색 작은 박스 (light gray opacity 0.6 채움 + 가는 navy 1pt 외곽)
- 크기: 약 100×60px
- 텍스트: "Query" (14pt navy)

2. **① 표본 추출** (★ 본 연구 집중 단계)
- 박스: purple #8B5CF6 굵은 외곽 3pt + light purple opacity 0.1 배경 채움
- 크기: 약 200×140px
- 상단 ★ 별 마크 (cyan/purple, 큰)
- 라벨 1 (Apple SD Gothic Neo 18-20pt purple Bold):
① 표본 추출
- 아이콘 (중앙): 균일 무작위 점들 (cyan 작은 점 9-12 개)
- 라벨 2 (12pt navy):
무작위 베르누이
N=385
- 박스 위쪽 추가 라벨 (16pt purple Bold, 박스 위 약 12px 위치):
본 연구가 집중하는 한 단계

3. **② 카디널리티 추정**
- 박스: navy opacity 0.5 (흐림) + 가는 navy 1pt 외곽
- 크기: 약 180×120px
- 라벨 (16pt navy 흐림):
② 카디널리티 추정
- 아이콘: 막대 그래프 (작게, navy)
- 메모: "표본 위에서 추정"

4. **③ Q-error 측정**
- 박스: 동일 (navy 흐림)
- 라벨 (16pt navy 흐림):
③ Q-error 측정
- 아이콘: 두 막대 비교
- 메모: "추정 오차 측정"

5. **④ Momentum 조정**
- 박스: 동일 (navy 흐림)
- 라벨 (16pt navy 흐림):
④ Momentum 조정
- 아이콘: 회전 화살표
- 메모: "momentum 으로 다음 표본 크기 조정"

## 화살표

- 노드 간 화살표: 굵기 2pt navy · 일반 화살촉
- 마지막 ④ → Query 루프 화살표: 굵은 곡선 화살표 (위로 가서 돌아옴), 라벨 "(다음 Query)" 작게

## 메모 (다이어그램 우상단)

작은 메모 (12pt navy opacity 0.55):
매 50 쿼리마다 표본 크기 갱신
표본 예산 N=385 고정

종횡비: 가로 약 5:1 (긴 가로)
배경: transparent
출력: PNG 2x retina

스토리: 5 단계 sequential 흐름 안에서 ① 표본 추출 단계만 본 연구가 통제 변인으로 분리. ★ 강조 + purple 굵은 테두리 + 다른 4 노드 흐림으로 시각 위계.
```

---

## 4. Asset 4 — Slide 6 베르누이 vs 분포 인지 층화 시각 대비

```
diagram 2 장 (위 베르누이 + 아래 분포 인지) 생성:

전체 layout: 세로 2 패널 (slide 6 우측 1/3 영역)

## 위 패널 — 베르누이 (무작위)

박스: 가는 navy 1pt 외곽 · padding 16px
상단 라벨 (18-20pt navy Bold):
베르누이 (무작위)

아이콘 (중앙 영역):
- 점 30-40 개 균일 무작위 배치 (cyan)
- 점 크기 4-6px · 점 간격 균일 무작위
- 일부 점이 살짝 빠진 cell 있음 (베르누이의 임의성 표현)

하단 메모 (12pt navy opacity 0.55):
모든 데이터 위에 균일 확률로 표본 추출

## 아래 패널 — 분포 인지 (층화)

박스: 가는 navy 1pt 외곽 · padding 16px
상단 라벨 (18-20pt navy Bold):
분포 인지 (층화)

아이콘 (중앙 영역):
- 점 30-40 개를 4-5 개 cluster 로 그룹화 (각 cluster 다른 색: cyan·purple·green·orange)
- 각 cluster 외곽에 가는 dashed circle (cluster boundary 표시)
- cluster 별 점 개수 비례 추출 (큰 cluster = 더 많은 점)

하단 메모 (12pt navy opacity 0.55):
데이터 분포 그룹별로 비례 추출

## 두 패널 사이 (가운데)

큰 ? 또는 vs (navy 28-32pt Bold):
?

종횡비: 세로 (1:2, slide 6 우측 영역)
배경: transparent
출력: PNG 2x retina · 약 720×1080px

스토리: 위 (무작위) vs 아래 (분포 인지) 시각 대비. 같은 점 개수지만 분포 위에 어디서 뽑느냐가 다름. ? 가 본 연구 질문 "어떤 방식이 더 정확한가" 시각화.
```

---

## 5. Asset 5 — Slide 7 통제 실험 3 카드 아이콘

```
3 카드 안 아이콘 3 종 (각 카드 안 작은 아이콘):

## 좌 카드 (베이스라인) 아이콘

- 균일 무작위 점들 12-16 개 (cyan #0EA5E9)
- 균일 분포 (격자 아님, random)
- 크기 약 240×120px
- 외곽 라벨 X (slide 안 텍스트와 별도)

## 중앙 카드 (단독 대체 ❌) 아이콘

- cluster 점들 12-16 개 (회색 #9CA3AF)
- 4 개 cluster 그룹화 (cluster boundary 가는 dashed)
- 크기 약 200×100px
- 대각선 굵은 ❌ X 표시 overlay (red #DC2626, 카드 전체 가로 지름)

## 우 카드 (결합 ★) 아이콘

- 두 화살표 합쳐져 → 평균 박스
- 좌측 화살표 (cyan): 균일 무작위 점들 → 화살표
- 우측 화살표 (cyan): cluster 점들 → 화살표
- 두 화살표 끝에서 합쳐지는 cyan 화살표
- 합쳐진 화살표 끝: 작은 박스 (navy 외곽) 안 "평균" 텍스트 (Apple SD Gothic Neo 12pt navy Bold)
- 우상단 ★ 마크 (cyan)
- 크기 약 240×140px

3 아이콘 모두 흰 배경 + navy/cyan 색감.

종횡비: 가로 (각 아이콘 약 2:1)
배경: transparent
출력: PNG 2x retina

스토리: 좌 (베이스라인 그대로) · 중 (단독 대체 ❌) · 우 (결합 ★) — 세 아이콘만으로 측정 설계의 본질이 한 호흡에 전달.
```

---

## 6. Asset 6 — Slide 8 7 paradigm 아이콘 grid

```
7 paradigm 아이콘 (각 약 200×140px, slide 8 우측 grid 안 합성):

## 1. 클러스터링 (P1)

- 점 12-16 개를 3-4 개 cluster 색별 그룹화
- 각 cluster: cyan·purple·green·orange 한 색
- cluster boundary 가는 dashed circle (navy opacity 0.4)
- 각 cluster 안 1 개 큰 점 (대표 sample) — 굵은 외곽

## 2. 공간 곡선 (P2, PCA 환원)

- 2D plane (작은 격자 배경 light gray)
- 지그재그 Hilbert curve (cyan 굵은 2pt, 4-5 회 꺾인 S-curve 형태)
- 점 8-12 개가 curve 위에 따라 위치
- 우상단 작은 라벨 (10pt navy opacity 0.55): "PCA 2D"

## 3. 스트리밍 (P3)

- 점들이 좌→우 한 방향으로 흘러가는 모습
- 12-16 개 점 (cyan), 좌측에 큰 점·우측으로 갈수록 작아짐
- 큰 점에 우선순위 표시 (작은 ⭐ 마크 또는 굵은 외곽)
- 화살표 (cyan, 좌→우)

## 4. 차원 축소 (P4)

- 좌측 3D cube (다차원 표현, 점 8-12 개 안)
- 우측 2D plane (point cloud, 같은 점들이 평면에 투영)
- 사이 굵은 화살표 (cyan, "투영" 라벨 작게)

## 5. 고전 stratification (P5)

- 누적 분포 곡선 (CDF S-curve, navy)
- x축에 5 stratum 구분선 (수직 점선, cyan)
- 각 stratum 안 작은 점 (sample 위치 표시)
- 우상단 작은 라벨 (10pt): "cum-√f"

## 6. 양자화·히스토그램 (P6)

- 2D pixel grid (light gray, 5×5 또는 6×6 격자)
- 각 cell 안 점 개수 가시화 (cyan, 진하기 다양)
- 일부 cell 굵은 외곽 강조 (대표 sample cell)

## 7. 해시 partitioning (P5b)

- 4-6 개 bucket 박스 (각 navy 외곽, 가로 일렬 또는 2×3)
- 각 bucket 위에 hash 함수 시각화 (작은 #️⃣ 또는 hash 도형)
- 점들이 hash 결과에 따라 bucket 으로 떨어지는 화살표

각 아이콘 공통:
- 흰 배경
- 점 크기 4-6px · cluster size 약 24-32px diameter
- 라벨 X (slide 안에 텍스트와 별도)

종횡비: 각 아이콘 약 7:5
배경: transparent
출력: PNG 2x retina · 7 장

스토리: 7 paradigm 의 본질을 아이콘 한 장으로 압축 — 청중이 paradigm 이름 안 들어도 그림만 봐도 알고리즘 본질 어렴풋이 짐작 가능.
```

---

## 7. Asset 7 — Slide 11 Future Work 두 갈래 카드 아이콘

### 7.1 자산 7A: Group A — 검증 범위 확장 아이콘

```
illustration 1 장 (slide 11 좌 카드 상단 영역):

좌측: 작은 점 cluster (3-4 개 점, cyan)
중앙: 굵은 화살표 (orange #F97316, "확장" 표현)
우측: 큰 점 cluster (12-16 개 점, cyan + 일부 새로운 색 추가 — purple·green 등)

위쪽 작은 라벨 (12pt navy opacity 0.55):
"검증 범위 확장"

아래쪽 3 보조 아이콘 (수직 list, 각 16×16px):
- scale 게이지 아이콘 (cyan)
- DB 4 로고 작게 (cyan, 4 개 작은 사각)
- 자원 미터 (orange)

종횡비: 가로 (2:1)
배경: transparent
출력: PNG 2x retina · 약 400×200px
```

### 7.2 자산 7B: Group B — History-aware Adaptive Sampling 아이콘

```
illustration 1 장 (slide 11 우 카드 상단 영역):

상단: 과거 query 박스 3 개 (가로 일렬, 작은 box, cyan opacity 0.3-0.7 점진 진해짐 = 시간 순서)
- 각 박스 안 작은 점 (query) + 위쪽 화살표 ↑ "selectivity feedback"
중앙: feedback 화살표 누적 (3 화살표 모이는 모습, cyan 굵은 2pt)
하단: 현재 query 박스 1 개 (cyan 굵은 외곽 + 우상단 ★ 마크)
- 박스 안 작은 점 + 라벨 "현재 query"

위쪽 작은 라벨 (12pt navy opacity 0.55):
"History-aware sampling"

종횡비: 가로 (1:1)
배경: transparent
출력: PNG 2x retina · 약 400×400px

스토리: 과거 query 들의 selectivity feedback 누적 → 현재 query 의 cardinality 추정에 활용 → sampling cost ↓.
```

---

## 8. 사용 절차

### 8.1 생성 순서

Gemini Ultra 웹앱 (또는 Flow / Whisk) 에서 다음 순서로 7 자산 일괄 생성:

1. **Asset 1A** 분석가 illustration (slide 2 좌측)
2. **Asset 1B** VAQ 분해 → 결합 그림 (slide 2 우측)
3. **Asset 2** plan 트리 비교 (slide 3 중앙 hero)
4. **Asset 3** Adaptive Sampling 5 단계 흐름도 (slide 5 중앙 hero)
5. **Asset 4** 베르누이 vs 분포 인지 시각 대비 (slide 6 우측 1/3)
6. **Asset 5** 통제 실험 3 카드 아이콘 (slide 7 각 카드 안)
7. **Asset 6** 7 paradigm 아이콘 grid (slide 8 우측 grid)
8. **Asset 7A** Group A 확장 아이콘 (slide 11 좌 카드)
9. **Asset 7B** Group B history-aware 아이콘 (slide 11 우 카드)

총 약 9 장 (자산 1A·1B 두 장 분리 · 자산 6 7 paradigm 은 7 장 = 합 약 14 장).

### 8.2 합성 워크플로우

1. Claude Design 으로 slide layout 12 장 생성 (Claude Design prompt v4 carry)
2. Nano Banana Pro 로 자산 14 장 생성 (본 brief carry)
3. 백지 구글 PPT 새 deck 열기 (또는 Google Slides 신규)
4. 각 슬라이드에 Claude Design layout PNG 삽입 → 그 위에 Nano Banana Pro 자산 합성
5. 텍스트 검증 (storyline v4 §2-§13 carry) · 색·폰트 일관성 확인
6. PPTX export → 5/26 23:59 LearnUs 업로드

### 8.3 일관성 검증

자산 14 장 생성 후 확인:
- [ ] 모든 자산 navy `#1E3A5F` 주 색 통일
- [ ] cyan `#0EA5E9` 강조 통일
- [ ] 폰트 Apple SD Gothic Neo 통일 (한국어 가독성)
- [ ] 흰 배경 + transparent PNG 합성
- [ ] 별표 ★ 노출 자산 안에서 storyline 강조용만 (slide 5 ① 표본 추출, slide 7 우 카드, slide 8 좌 카드 등)
- [ ] 사람·사물 illustration anonymous 톤 (얼굴 detail X)

---

## 9. Veo 3.1 동영상 brief (5/28 마감, 별도 작업)

본 brief 는 **5/26 마감 deck (정적 슬라이드)** 만 다룸. 5/28 12:00 정오 소개영상 마감 별도 작업:

- 소개영상 (3-5 분) — Veo 3.1 활용 (네이티브 동기화 오디오)
- ElevenLabs 한국어 TTS narration
- 별도 brief 작성 예정 (5/27 발표 후 진행)

본 brief 는 slide deck용 정적 자산에 집중.

---

## 10. storyline v4 동반

본 brief 의 자산은 다음 storyline v4 안 시각 spec 과 1:1 매칭:

- `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v4_20260525_001258.md`

각 slide 별 텍스트·시각·발표자 narrative + 본 brief 의 illustration spec + Claude Design prompt 의 layout spec 셋이 통합되어 deck 완성.

---

작성: 2026-05-25 00:13 KST · 12 slide illustration brief v4. 5/26 23:59 PPT 마감 critical path. Gemini Ultra Nano Banana Pro 활용 자산 14 장 생성 → Claude Design layout 위 합성.
