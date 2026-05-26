# v18 → v19 polishing prompt — full deck (14 slide → 13 slide 재구성)

> 작성 2026-05-26 01:00 KST · 사용자 피드백 누적 (5/25 23:54 + 26 00:14 + 00:55) 정밀 반영
> 적용처: claude.ai/design 동일 대화창 `019e1a41-701c-7134-9ce1-1247262c1563`
> 기존: v18 14 slide deck (`____ (2).pptx`, 5/25 13:30 다운로드)
> 결과: **v19 13 slide deck** — slide 11+12 통합 + Future Work 위치 이동
> 직전 5slide prompt (`v18_polishing_prompt_5slide_5_26_00_18.md`) 의 변경 사항 모두 포함 + slide 8·9·10·11·12·13 신규 추가

---

## ▼ ▼ ▼ 단일 복붙 시작 ▼ ▼ ▼

기존 v18 14 slide deck 을 **v19 13 slide deck** 으로 재구성합니다. 핵심 구조 변경:

- **slide 11 + slide 12 통합** → 새 slide 11 (engine latency + plan 회복 합본, 간결화)
- **구 slide 13 (Future Work 두 갈래)** → 새 slide 12 (Group A 직관화)
- **구 slide 14 (감사합니다)** → 새 slide 13 (carry)
- slide 1·4 = 변경 없음 carry
- slide 2·3·5·6·7·8·9·10 = 정밀 polishing

design system (navy `#1E3A5F` · cyan `#0EA5E9` · purple `#8B5CF6` · green `#10B981` · coral `#F97316` · Apple SD Gothic Neo · 흰 배경 · chapter badge `배경/방법/결과/적용`) 동결.

---

## 전 슬라이드 공통 룰

### 1. 약어 처음 등장 시 풀어쓰기

- VAQ → "벡터 증강 분석 쿼리 (Vector-Augmented Query, VAQ)"
- TPC-H → slide 2·3 에서 단어 제거 (자연어 풀이)
- Adaptive Sampling → "Adaptive Sampling (적응적 표본 추출)"
- DEEP·SIFT·SSN++·YFCC → "벡터 데이터셋"
- HNSW → "Hierarchical Navigable Small World (HNSW)"

### 2. **baseline 라벨 전 슬라이드 통일** (사용자 명시)

모든 슬라이드 안 "베이스라인" 한국어 → **"baseline"** 영문 통일. slide 7 에서 첫 등장 시 풀어쓰기 caption "(= 논문 원본 · 무작위 베르누이 방식)" 한 번 노출, 이후 slide 9·10·11·12 에서는 "baseline" 만 노출.

### 3. 텍스트 줄 정렬 일관성

- 좌측 정렬 (또는 명백한 가운데 정렬) 통일
- 들여쓰기·padding 16-20px 동일 그리드
- 세로 회전 텍스트 금지 — 가로 정상 표기

### 4. "너무 클로드 출력같은" 메타 텍스트 회피

다음 표현은 **전 슬라이드 일관 삭제**:
- "paper carry · Exqutor §V-B"
- "결과 표시 X · 본 발표 미포함"
- "본 연구 핵심" (CORE badge 만 carry)
- "한 측정 cell" → "같은 쿼리 · 같은 데이터"
- "총괄" (slide 9)

자연 한국어 발화체 우선.

---

## Slide 1 — 표지 (carry, 변경 없음)

v18 그대로 carry. hero "인덱스 부재 시 / Adaptive Sampling 개선" + 부제 "표본 선택 단계의 통제 실험" + 하단 팀·교수·멘토. 추후 별도 검토.

---

## Slide 2 — 배경 (벡터 증강 분석 쿼리 · VAQ) 정밀 변경

(직전 5slide prompt 사항 carry)

1. **제목**: "벡터 증강 분석 쿼리 — VAQ" → **"벡터 증강 분석 쿼리 (Vector-Augmented Query, VAQ)"**
2. **SQL 박스 caption**: → **"예시 분석 쿼리 — 관계형 조건과 벡터 유사도를 한 SQL 안에"** (TPC-H 단어 제거)
3. **SQL 옆 라벨**:
   - "← 관계형 조건 (TPC-H)" → "← 관계형 조건 (예: 가정용 카테고리 · 1995-03-14 이전 주문)"
   - "← 벡터 유사도 (VAQ)" → "← 벡터 유사도 — 임베딩 비교"
4. **분석가 박스 carry** (자연어 그대로)
5. **오른쪽 결과 박스**:
   - "유사 벡터 추출" → "유사 부품 추출"
   - "매출 TOP 행 / 유사 부품 매출 분석 결과" → **"→ 유사 부품의 매출 상위 주문 도출"**
6. **텍스트 줄 정렬 통일** (좌측, padding 16px)

---

## Slide 3 — 배경 (카디널리티 1만 배) 정밀 변경

(직전 5slide prompt 사항 carry)

1. **부제 위치 fix** — padding-top 20px, 가로 라인 디자인과 시각 겹침 해소
2. **plan tree node 한국어 풀이**:
   - 왼쪽: "Hash · 한꺼번에 묶기" / "Seq Scan · 전체 행 읽기"
   - 오른쪽: "Nested Loop · 하나씩 인덱스로" / "Index Scan · 인덱스로 부분만"
3. **양쪽 박스 캡션 직관화**:
   - 왼쪽: "전체 행을 모두 메모리에 → 100만 행 폭주"
   - 오른쪽: "인덱스로 100점만 직접 조회 → 즉시"
4. hero "10,000× 응답 시간 차이" carry
5. **메타**: "TPC-H Q3 VAQ on DEEP" → **"벡터 데이터셋 DEEP · 표준 분석 쿼리 예시"**

---

## Slide 4 — 배경 (기존 시스템 33/50/100%) carry

v18 그대로 carry. 변경 없음.

---

## Slide 5 — 방법 (Adaptive Sampling) 정밀 변경

(직전 5slide prompt 사항 carry)

1. **제목**: → "인덱스가 없을 때 — **Adaptive Sampling (적응적 표본 추출)**"
2. **STEP ④**: "Momentum 조정" → **"표본 크기 조정 (다음 표본은 더 많이 / 적게)"**
3. **STEP ① caption**: → "무작위 균일 추출 (베르누이 방식) · 한 쿼리당 표본 385개 한 번"
4. **BATCH 라벨**:
   - "BATCH 1 · Q₁-Q₅₀" → **"샘플링 1~50회 (1단계)"**
   - "BATCH 2 · Q₅₁-Q₁₀₀" → "샘플링 51~100회 (2단계)"
   - "BATCH 3 · Q₁₀₁-Q₁₅₀" → "샘플링 101~150회 (3단계)"
5. **"N 갱신" 세로 회전 텍스트 → 가로 정상 표기** (시각 버그 fix)
6. **m=0.9 / η 감쇠 모두 삭제** — "누적 오차로 N 자체 갱신"
7. 본 연구 집중 단계 ★ badge carry

---

## Slide 6 — 방법 (본 연구 RQ) 정밀 변경

(직전 5slide prompt 사항 carry)

1. **2x2 grid 재배치**:
   - 1행 (col 1~2 가로 전체): RESEARCH QUESTION 박스
   - 2행 col 1: "baseline" 박스 (무작위 베르누이 점 cluster + caption)
   - 2행 col 2: "샘플링 방식 탐색" 박스
2. 두 박스 사이 **명확한 대조 화살표 `↔`** purple bold 24-32pt + caption "대조"
3. **하단 텍스트 "샘플링 방식 탐색 → 무작위 베르누이와 대조" 완전 삭제**
4. 양쪽 박스 height·padding 동일

(공통 룰) slide 6 의 "무작위 베르누이" 박스 라벨도 **"baseline"** 으로 통일.

---

## Slide 7 — 방법 (통제 실험) 정밀 변경

(직전 5slide prompt 사항 carry + baseline 통일)

1. **제목**: → **"동일 쿼리에 세 가지 추정 방식을 동시 적용"**
2. **상단 호 caption**: "한 측정 cell 에서" → **"같은 쿼리 · 같은 데이터에서"**
3. **baseline 박스** (왼쪽):
   - 라벨: 한국어 "베이스라인" → **"baseline"** 영문
   - 박스 상단 풀어쓰기 caption: **"(= 논문 원본 · 무작위 베르누이 방식)"** ★ 첫 등장 풀어쓰기
   - 박스 하단 "paper carry · Exqutor §V-B" **삭제**
4. **단독 대체 박스** (가운데):
   - 라벨 carry
   - 풀어쓰기 caption: **"(= 베르누이를 분포 인지 표본으로 완전 치환)"**
   - 박스 하단 "결과 표시 X · 본 발표 미포함" **삭제** — 큰 X 표시·회색 박스 carry
5. **결합 박스** (오른쪽):
   - 라벨 carry
   - 풀어쓰기 caption: **"(= baseline + 분포 인지 추정값의 산술 평균)"**
   - 박스 하단 "본 연구 핵심" **삭제** — CORE badge carry
6. **세 박스 내부 흐름 직관화**:
   - baseline: 무작위 점 cluster → "↓" → "추정값 1개"
   - 단독 대체: 분포 인지 점 cluster (회색·X) → "↓" → "추정값 1개 (회색)"
   - 결합: baseline 점 cluster (navy) **+** 분포 인지 점 cluster (cyan) 양쪽 모두 → "↓ 추정값 A + 추정값 B" → "↓ 산술 평균" → "결합 추정값"
7. 하단 캡션 carry: "동시 산출 → 외생 변수 통제"

---

## Slide 8 — 방법 (1,508 조합) 정밀 변경 ★ 신규

### 현 v18 시각

- 제목 "1,508가지 조합으로 검증"
- 3 박스: DATASETS 5 (DEEP·SIFT·SSN++·YFCC·PartSupp PK) + VARIABLES 3 (SCALE FACTOR sf=1·10·100 · SELECTIVITY 0.001·0.01·0.1 · METHOD 16 종) + COMBINATIONS (5 데이터셋 × 조건 · × 16 method = 1,508)
- 측정 평면 heatmap (purple cell grid)
- **MEASUREMENT ENVIRONMENT 박스** (서버 Intel Xeon Gold 6530·128 vCPU / 메모리 1.0 TB RAM·NVMe SSD / GPU 4× NVIDIA RTX 6000 Ada / 엔진 PostgreSQL 16 + pgvector 0.8 HNSW / 반복 각 cell 15회 평균·2,880회 측정·180 paired)

### 변경 사항 3 건

1. **1,508 구성 명확화** (사용자 피드백: "어떻게 나온거야 · 조건은 뭔데"):
   - 현 "5 데이터셋 × 조건 · × 16 method = 1,508" 식 → **명확하게 분해**:
     - "5 데이터셋 × 9개 매개변수 조합 (sf 3 × sel 3) × 16 method · 의도 max 3,600 (5 trial) · 실측 1,508 cell (41.9% 구조화)"
   - 또는 단순화: **"본 측정 평면 = 5 데이터셋 · {sf=1·10·100} · {sel=0.001·0.01·0.1} · 16 method · 1,508 측정 (의도 max 3,600 中 41.9% 구조화)"**
   - ★ 측정 평면 heatmap 옆에 명확한 caption: **"sf·sel·method 조합 1,508 = 카디널리티 추정 정확도 (Q-error) 측정 cell"**
   - ★ 하단 한 줄 추가: **"엔진 응답 시간 측정은 별도 (DEEP sf=10, 다음 slide 11 에서 156 plan)"**
2. **MEASUREMENT ENVIRONMENT 박스 완전 삭제** (서버·메모리·GPU·엔진·반복 모두) — 슬라이드 분량 ↓
3. **하단 캡션 carry**: "각 cell 에서 baseline · 결합 동시 산출 → 직접 비교"

---

## Slide 9 — 방법 (13 method paradigm) 정밀 변경 ★ 신규

### 현 v18 시각

- 제목 "표본 추출 방식 — 무작위 베르누이 vs 샘플링 방식 탐색 13 method"
- 왼쪽: 무작위 베르누이 단독 박스 (navy 점 cluster · 균일 무작위 점들 caption · "paper carry / Exqutor §V-B" 텍스트)
- 오른쪽 grid: P1 공간 곡선 (Hilbert·Z-order) · P2 차원 축소 (PCA·rSVD) · P3 고전 stratification (cum-√f) · P4 양자화 (RaBitQ·grid) · P5 클러스터링 (KMeans·GMM) · P6 ★ 스트리밍 (chao_weighted) · P7 해시 (md5 prefix)
- 우측 끝: "13 METHOD 총괄 / 7 paradigm" 박스

### 변경 사항 4 건

1. **"총괄" 단어 삭제** — "METHOD 총괄" → **"13 METHOD"** (또는 단순 "METHOD")
2. **각 paradigm 박스 안 method 개수 표시** (사용자 피드백: "각 paradigm에서 몇 개의 method 적용 알 수 있으면"):
   - 각 paradigm 박스 라벨 아래 작은 chip: "**· N method**" (font 11pt purple soft)
   - 정확 분포는 method_registry 참조 — 13 method 7 paradigm 분포 예시: P1 (2 method) · P2 (3 method) · P3 (2 method) · P4 (2 method) · P5 (1 method) · P6 (1 method) · P7 (2 method) 합 = 13
   - (정확 분포는 적용 시 보고서 §3 또는 method_registry 직접 grep — claude.ai/design 에서 채워넣기)
3. **baseline 박스 안 "paper carry / Exqutor §V-B" 텍스트 완전 삭제**
4. **baseline 박스 라벨 통일**: "무작위 베르누이" → **"baseline"** (영문, slide 7 통일)
   - 박스 안 caption carry: "균일 무작위 점들"

---

## Slide 10 — 결과 (Q-error 89.1%) 정밀 변경 ★ 신규

### 현 v18 시각

- 제목 "Q-error 비교 — 베이스라인 vs 결합" (green chapter badge `결과`)
- 왼쪽: paired Δ% histogram (cyan 분포 -30%~+30%, median -4.38%, 결합 우위 89.1% / baseline 우위 10.9%)
- 오른쪽 hero: **"89.1%"** 큰 navy 그라데이션 + caption "1,344 / 1,508 cell · 결합 우위" + 막대 (baseline 1.4582 · 결합 1.4019) + "-3.86% mean · median Δ% -4.38%"

### 변경 사항 4 건

1. **왼쪽 paired Δ% histogram 완전 삭제** (사용자 피드백: "왼쪽 막대그래프 삭제해도 될듯")

2. **89.1% 의미 명확화** (사용자 피드백: "baseline 대비 89.1%는 아닌 거 같은데"):
   - 89.1% 아래 caption 현 "1,344 / 1,508 cell · 결합 우위" 유지
   - **추가 명확 풀이 caption**: **"1,508 측정 중 1,344 cell 에서 결합이 baseline 보다 더 낮은 Q-error → paired better 89.1%"**
   - **★ 핵심 framing 한 줄 (89.1% 위 또는 아래)**: **"결합이 baseline 을 paired 89.1% 우위 — 격차는 median Q-error 1.4582 → 1.4019 (-4.38%)"**

3. **baseline vs 결합 막대 — broken axis 적용** (사용자 피드백: "구름 표시로 생략" + 차이 명확화 + 왜곡 과하지 않게):
   - 막대 시작점 = 0 X. **막대 왼쪽 1.0 부근까지 생략 표시 (`≈` 또는 zigzag 끊김 표시)**
   - 막대 visible 구간 = 1.30 ~ 1.50 (약 0.2 폭) — 차이 1.4582 vs 1.4019 = 0.0563 가 약 28% 길이로 보임 (왜곡 적절)
   - 막대 위 명시: "baseline **1.4582**" / "결합 **1.4019**" (font 18pt navy/cyan bold)
   - 막대 아래: "median Q-error · 낮을수록 더 정확"

4. **라벨 통일**: 제목 + 모든 caption 안 "베이스라인" → **"baseline"** (slide 7 첫 등장 풀어쓰기 이후 영문 통일)
   - 제목: "Q-error 비교 — **baseline vs 결합**"
   - 모든 caption 일관

---

## Slide 11 — 적용 (engine latency + plan 회복 통합) ★ 신규 통합

(현 v18 slide 11 + slide 12 합본 → 새 slide 11. 사용자 피드백: "11+12 합치면서 간결하게")

### 통합 시각 구조 (orange chapter badge `적용`)

- **제목**: **"엔진 응답 시간 — 사실상 동등 · 진짜 우위는 plan 회복"** (또는 "엔진 적용 — latency 동등 + plan 회복 우위")
- **상단 (latency 비교)**: 3 막대 가로
  - pgvector 기본 (Adaptive Sampling 적용 X) — 5,677 ms (1.0×) · grey
  - **baseline** (논문 원본 그대로) — 977.6 ms (5.77× ↑) · navy
  - 결합 (본 연구) — 983.5 ms (5.70× ↑) · cyan
  - 막대 옆 caption: "**baseline 과 결합 latency 사실상 동등 (0.07× 격차)**"
- **하단 (plan 회복)**: 2 도넛 + 풀이 박스
  - 왼쪽 도넛: **"baseline plan 회복 91 / 156"** · navy soft (또는 "7 / 12 cell · 58.3%")
  - 오른쪽 도넛: **"결합 plan 회복 148 / 156"** · cyan (94.9%)
  - 도넛 사이 큰 라벨: **"+57 plan 회복"** (orange 강조)
  - 도넛 아래 caption: **"plan 회복 = 카디널리티 추정 정확 → 정답 실행 plan 선택 (latency 폭주 방지)"**

### 변경 핵심 5 건

1. **현 slide 11 (Q-error 89.1% slide 의 다음 slide = 엔진 latency) + 현 slide 12 (plan 개선 CURRENT) 통합**
2. **"cell × method" 풀어쓰기** (사용자 피드백: "cell x method가 뭔데"):
   - 현 "12 cell × 13 method = 156 plan · 평균 latency" → **"DEEP 데이터셋 sf=10 환경 · 12개 매개변수 조합 × 13개 분포 인지 method = 156개 plan · 평균 응답 시간"**
   - 단 발표 시 청중 부담 ↓ — caption font 12pt navy soft (작게)
3. **"plan 회복" 의미 풀이** (사용자 피드백: "무슨 의미인지 모르겠어"):
   - 도넛 아래 명확 caption: **"plan 회복 = 카디널리티 정확 추정 → 정답 실행 plan 선택"**
   - 또는 "plan 회복 = 비최적 plan 에서 정답 plan 으로 복귀 (latency 폭주 방지)"
4. **Future Work / FUTURE 확장 영역 본 slide 에서 완전 삭제** → 새 slide 12로 이동
5. **baseline 라벨 통일** + **"exqutor 그대로" 같은 메타 표현 제거** → 단순 "baseline (논문 원본)" caption
6. **"본 연구" 라벨** 결합 막대 옆: carry (자연 한국어, "결합 = 본 연구") 또는 단순 "결합" 만

---

## Slide 12 — 적용 (Future Work 두 갈래) ★ 신규 (구 slide 13 layout 개선)

### 현 v18 시각 (구 slide 13)

- 제목 "Future Work — 두 갈래"
- 왼쪽 GROUP A — 검증 범위 확장 + 산업 자원:
  - 본 측정 평면 (sf=10·sel≤.10) → 확장 영역 (sf=100·sel≥.5·다중 벡터·다른 엔진) 박스
  - 아래: SCALE gauge · ENGINE 4 박스 (pgvec·VBASE·Duck·Milvus) · RESOURCE 막대
  - 라벨: scale · selectivity · engine · resource
  - 캡션: "큰 데이터 · 넓은 selectivity · 다른 엔진에서 더 큰 latency 개선 가능"
- 오른쪽 GROUP B — History-aware Adaptive Sampling:
  - 과거 query (Q-3·Q-2·Q-1) → 현재 query (Q₀) 화살표
  - feedback 누적 → sampling ↓ → cost ↓
  - 라벨: 과거 feedback · 더 적은 sampling · cost ↓

### 변경 사항 (사용자 피드백: "Group A 이해 어려움 · 내용·이미지 매칭")

1. **Group A 시각 단순화 + 직관 매칭**:
   - 현 SCALE gauge · ENGINE 4박스 · RESOURCE 막대 추상 아이콘 묶음 **제거** (어색)
   - **단일 직관 도식 (작은 cube → 큰 cube)**:
     - 왼쪽 작은 cube (navy line): "본 측정 평면" 라벨 + 안에 "sf=10 / sel≤.10" 작은 글씨
     - 화살표 오른쪽 (orange) → 
     - 오른쪽 큰 cube (orange dashed): "확장 평면" 라벨 + 안에 "sf=100 / sel≥.5 / 다중 벡터 / 다른 엔진" 글씨
   - 아래 4 차원 라벨 단순 chip 가로 배열: **"scale ↑ · selectivity ↑ · engine 다양 · resource 산업적"**
   - 캡션 단순: **"더 큰 데이터·넓은 selectivity·다른 엔진 에서 결합 효과 검증"**

2. **Group B carry** (이미지·내용 매칭 OK 사용자 피드백 X)
   - 과거 query Q-3·Q-2·Q-1 → 현재 query Q₀ 화살표
   - "과거 feedback 누적 → sampling ↓ → cost ↓"

3. **두 Group 가로 폭 balance** — 양쪽 동일 width (각 약 48%), 가운데 gap 4%

4. **제목 carry**: "Future Work — 두 갈래"

---

## Slide 13 — 마무리 (감사합니다 + Q&A) carry ★ 구 slide 14

위치만 이동 (구 slide 14 → 새 slide 13). 시각 carry 변경 X.

- hero "감사합니다" (navy → cyan gradient)
- Q&A 환영합니다
- 하단: 박세은·강재현·조현빈·이동욱 / 속도는벡터·연세대학교 컴퓨터과학과 캡스톤 / 박광현 교수 (BDAI 연구실)·지도교수 / 지도연구원 임채림·멘토 박성원 (삼성전자 AI센터) / 자료·코드 — github.com/johyunbin/Capstone

---

## ▲ ▲ ▲ 단일 복붙 끝 ▲ ▲ ▲

## 적용 방법

1. claude.ai/design 동일 대화창 (`019e1a41-701c-7134-9ce1-1247262c1563`) 진입
2. 본 prompt 의 ▼ ~ ▲ 구간 전체 복붙
3. v19 13 slide PPTX 다운로드 → 본 세션에 첨부
4. Claude Code 가 v19 13 slide 추출·검증 + 시각 정합 PASS 확인

## 다음 세션 task carry

v19 적용 후 사용자 재검토:
- 새 slide 11 (latency + plan 회복 통합) 시각 적절성 검토
- 새 slide 12 (Future Work Group A 직관화) 매칭 검토
- slide 1 (표지) 결정
- slide 4 (기존 시스템) carry 확인
- 모든 슬라이드 텍스트·시각 최종 검수

→ 추가 polishing 발생 시 v20 prompt 누적 작성 → 최종 LearnUs 업로드 (5/26 23:59 마감)

**전 슬라이드 공통 룰 (carry)**:
- 약어 처음 등장 시 풀어쓰기
- 텍스트 줄 정렬 일관성
- 메타 텍스트 회피 (paper carry · 본 연구 핵심 등)
- "베이스라인" → "baseline" 영문 통일
- 수치 강조보다 시각 자료 활용 우선
- 청중 5-7 초 안에 읽을 수 있는 정도
