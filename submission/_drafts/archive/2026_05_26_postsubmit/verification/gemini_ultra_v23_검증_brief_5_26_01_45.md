# Gemini Ultra · deck_v23 13 slide 검증 brief (5/26 01:45 KST 작성)

> **사용처**: Gemini Ultra 웹앱 (multimodal) — 사용자가 PPTX 또는 13 slide screenshot 업로드 + 본 brief 단일 메시지
> **목적**: 발표 deck 의 전반 구성·시각·내러티브 정합성 독립 검증 + 피드백
> **마감**: 5/26 23:59 LearnUs 업로드 · 발표 5/27 (수) 15:00 D504호 · 10 분 + Q&A 5 분

---

## 📎 첨부물 (사용자가 Gemini 웹앱에 업로드)

1. **deck_v23.pptx** (Claude Design 에서 export, 13 slide) — multimodal 분석용
2. (선택) 13 slide PNG screenshot — 시각 정밀 점검 시
3. 본 brief 단일 메시지 — context

---

## 🎯 검증 요청 항목 (각 항목별 피드백)

### 1. 전반 storyline 정합성

본 연구 = Exqutor §V-B Adaptive Sampling 의 **표본 선택 단계 한 곳만** 통제 실험으로 분리. 추정 정확도 (Q-error) + 실제 엔진 응답 시간 (latency + plan 회복) 두 축 검증.

**13 slide narrative arc**:
- slide 1 표지 (인덱스 부재 시 Adaptive Sampling 개선)
- slide 2-4 배경 (VAQ 시나리오 → 1만 배 차이 → 기존 시스템 33/50/100%)
- slide 5-7 방법 (Adaptive Sampling 5 단계 → 본 연구 RQ → 통제 실험 3 방식 동시 적용)
- slide 8-9 측정 (1,508 조합 + 13 method 7 paradigm)
- slide 10 결과 1 (Q-error 89.1% paired better)
- slide 11 결과 2 (engine latency 사실상 동등 + plan 회복 +57)
- slide 12 Future Work (검증 범위 확장 + History-aware)
- slide 13 감사합니다

**질문**: 이 narrative arc 가 학술 발표 (10 분 강제 중단) 에 적절한가? slide 간 논리 끊김·중복 있나? 청중 인지 부하 적정?

### 2. 시각 디자인 정합성

design system:
- navy `#1E3A5F` (앵커) · cyan `#0EA5E9` (강조)
- chapter badge: 배경(cyan) · 방법(purple) · 결과(green) · 적용(orange)
- 폰트: Apple SD Gothic Neo · 흰 배경
- hero gradient: slide 1·13 만

**질문**: 시각 위계·일관성·여백 처리 적절한가? 슬라이드별 시각 강조가 narrative 와 정합? 학술 발표 절제미 vs 시각 임팩트 균형?

### 3. 사용자 피드백 13건 반영 정합성

다음 변경이 정확히 시각으로 표현됐는지 검증:

| slide | 변경 사항 (검증 포인트) |
|:--:|---|
| **2** | VAQ 풀어쓰기 첫 등장 · "TPC-H" 단어 제거 · SQL 라벨 한국어 풀이 (가정용 카테고리·1995-03-14) · "유사 부품의 매출 상위 주문 도출" |
| **3** | plan tree node 옆 한국어 caption (Hash·한꺼번에 묶기 / Nested Loop·하나씩 인덱스로) · 부제 padding · "벡터 데이터셋 DEEP · 표준 분석 쿼리 예시" |
| **5** | "Adaptive Sampling (적응적 표본 추출)" 풀어쓰기 · STEP ④ "표본 크기 조정" (Momentum 단어 제거) · BATCH "샘플링 1~50회 (1단계)" · "N 갱신" 가로 표기 · m=0.9 / η 감쇠 모두 삭제 |
| **6** | **2x2 grid** (1행 RQ 가로 전체 / 2행 baseline ↔ 샘플링 방식 탐색) · 대조 화살표 `↔` + "대조" 라벨 · 하단 텍스트 삭제 |
| **7** | "동일 쿼리에 세 가지 추정 방식을 동시 적용" 자연 한국어 · "같은 쿼리 · 같은 데이터에서" · **baseline** 영문 통일 + 풀어쓰기 caption 3건 · 메타 텍스트 3건 삭제 (paper carry / 본 연구 핵심 / 결과 표시 X) · 결합 박스 양쪽 점 cluster (navy + cyan) |
| **8** | **1,508 분해** ("5 데이터셋 × sf {1·10·100} × sel {.001·.01·.1} × 16 method") · 측정환경 박스 완전 삭제 · ★ "엔진 응답 시간 별도 — DEEP sf=10 · 다음 슬라이드 11" 안내 |
| **9** | "총괄" 단어 삭제 · 각 paradigm method 개수 chip (P1:2 / P2:3 / P3:2 / P4:2 / P5:1 / P6:1 / P7:2 = 13) · paper carry §V-B 삭제 |
| **10** | 89.1% paired better 의미 명확화 ("1,508 측정 중 1,344 cell 에서 결합이 baseline 보다 더 낮은 Q-error") · 왼쪽 paired Δ% histogram 완전 삭제 · **broken axis (≈ 표시) 1.30~1.50 구간** baseline 1.4582 vs 결합 1.4019 차이 시각 강조 |
| **11 ★ 통합** | 구 slide 11+12 합본 · 상단 3 막대 latency (5,677 / 977.6 5.77× / 983.5 5.70×) + "사실상 동등 0.07× 격차" · 하단 2 도넛 (baseline 91/156 · 결합 148/156) + **+57 plan 회복** orange chip · "cell × method" 풀어쓰기 ("DEEP sf=10 · 12개 매개변수 조합 × 13개 분포 인지 method = 156개 plan") · plan 회복 의미 caption ("카디널리티 추정 정확 → 정답 실행 plan 선택") |
| **12** | Future Work 두 갈래 (구 13) · Group A 추상 아이콘 (SCALE·ENGINE·RESOURCE) 모두 제거 → **단일 cube 도식 (작은 cube → 큰 cube + 4 chip)** · Group B carry |
| **13** | 구 14 감사합니다 carry (위치만 이동) |

### 4. 정본 수치 정합성

다음 수치가 슬라이드에 정확히 표시됐는지:

- Q-error: **baseline 1.4582 vs 결합 1.4019** (median, -4.38% paired)
- paired better: **1,344 / 1,508 cell = 89.1%**
- 측정 평면: **5 데이터셋 × sf{1·10·100} × sel{.001·.01·.1} × 16 method = 의도 max 3,600 中 1,508 (41.9% 구조화)**
- engine latency (DEEP sf=10 12 cell × 13 method = 156 plan): pgvector 기본 **5,677 ms** · baseline **977.6 ms (5.77×)** · 결합 **983.5 ms (5.70×)**
- plan 회복: baseline **91/156 (58.3% cell 7/12)** · 결합 **148/156 (94.9%)** · **+57 plan**

### 5. 청중 인지 부하 (10 분 발표)

- 슬라이드별 텍스트 양 (5-7 초 안에 읽을 정도?)
- 약어 첫 등장 풀어쓰기 완성도
- 기술 용어 (Hash·Nested Loop·Index Scan 등) 청중 친숙도
- 그림 vs 텍스트 균형 (발표자가 그대로 읽지 않고 가리키며 설명 가능?)

### 6. 발표 risk 항목

- 박광현 교수님 transcript 룰 8 (Acronym 첫 등장 풀어쓰기 · 분야 전문가 X 청중 이해 · 시각 임팩트 우선) 정합
- 5/27 발표 (10 분 강제 중단) · 5/29 Q&A 5 분
- 6/11 보고서 narrative 와의 일관성 (deck 의 simplification 정도)

---

## 💬 Gemini Ultra 에 요청하는 응답 구조

각 검증 항목 (1~6) 별로:
- **PASS / 보완 / FAIL** 명확한 평결
- 구체 근거 (어떤 slide 의 무엇이 문제인지)
- 개선 제안 (구체적 변경 사항)

마지막에:
- **종합 평결** (LearnUs 업로드 가능 수준? 또는 추가 polishing 필요?)
- **최우선 보완 3건** (마감 22h 남음 기준)

---

## 📋 본 deck context (carry 자료)

- **본 연구 framing**: Exqutor §V-B Adaptive Sampling 의 표본 선택 단계 controlled verification — baseline (논문 원본 무작위 베르누이) vs 결합 (baseline + 분포 인지 추정값 산술 평균) paired 비교
- **핵심 인사이트**:
  - Q-error: 결합이 baseline 을 paired 89.1% 우위 (median 1.4582 → 1.4019)
  - latency: baseline 과 결합 사실상 동등 (0.07× 격차)
  - 진짜 우위 = plan 회복 (91 → 148 plan, +57)
- **방법 portfolio**: 5 데이터셋 · 3 sf · 3 sel · 16 method (baseline 1 + 분포 인지 13 + 폐기 2) = 1,508 cell
- **paradigm**: 7 종 (P1 공간 곡선 · P2 차원 축소 · P3 고전 stratification · P4 양자화 · P5 클러스터링 · P6 ★ 스트리밍 · P7 해시)
- **chao_weighted** (P6 스트리밍) = 최저 Q-error method (Chao 1982 priority sampling u^(1/w))
- **honest limitation**: 다중 벡터 측정 극단 이상치 2건 · P1 Cluster paradigm 비일관성 · concat sf=100 부분 미측정
- **확장 영역 (Future Work Group A)**: sf=100 · sel≥0.5 · 다중 벡터 · 다른 엔진 (pgvector·VBASE·DuckDB·Milvus)
- **확장 영역 (Future Work Group B)**: History-aware Adaptive Sampling — 과거 query feedback 누적 → 현재 query sampling cost ↓

---

작성 2026-05-26 01:45 KST · v23 13 slide 정합 검증 PASS 후 Gemini Ultra 독립 재검증용. PPTX export 후 사용자 manual 적용.
