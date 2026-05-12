# 5/27 발표 deck REVAMP — 청중 친화 + AI 흔적 제거

> **사용자 피드백** (5/11 20:49): "발표 청중은 우리 연구 모르는 학부생. 발표는 스크립트로, PPT는 시각 자료만. 누가 봐도 AI 만든 티 내지 마라. v4 / ★3 / 4강 / W4 / V7 / 5/11 신규 같은 내부 표기 제거. 단어 자연스럽게. 1 slide = 1 메시지 + figure."

---

## 1. 현재 deck 문제 진단 — 8 카테고리

### A. Cover slide (S1) — 결과 부제 문제
- ❌ 부제 "paired CaseB > CaseA = 92.9% · paradigm rollup 5 paradigm 모두 statistical 압도"
- ❌ 메타 "CAPSTONE 2026-1 · FINAL · YONSEI CSE · 18 SLIDES"
- ❌ footer DATE "2026.05.27 · paper exact · 5/11 measurement"
- **원칙**: Cover = 연구 주제 + 방향. 결과는 본문에서 전개.
- ✅ 부제: "벡터 데이터베이스의 카디널리티 추정에서 분포 인지형 표본 추정 ensemble 의 정량적 가치"
- ✅ 메타: "CAPSTONE 2026 · YONSEI CSE" (slide count / paper exact 표기 제거)
- ✅ DATE: "2026.05.27" 만

### B. TOC slide (S2) — 이름 + 레이아웃
- ❌ 제목 "오늘의 구성" (인위적)
- ❌ 7-card grid 위아래 늘린 빡빡한 느낌
- ❌ subtitle "Problem / Prior Exqutor / Approach ensemble avg / RQ1 distribution gap / Paradigm 9 / RQ2 Paradox / CaseB Climax" — 영문 jargon
- ✅ 제목: "발표 순서" 또는 "목차"
- ✅ 4 chapter 그룹화 (배경 4 + 접근 3 + 결과 9 + 한계 2 = 18 slide):
  1. **배경** — 문제 / 기존 연구 / 본 연구 위치
  2. **접근** — 우리 방법 / 검증 설계
  3. **결과** — 분포 차이 / paradigm framework / 결합 추정 효과
  4. **한계와 향후** — 정직 한계 / 후속 연구

### C. 표기 정리 — 내부 버전/시점 표기
| 제거 | 대체 |
|---|---|
| `v3 / v4` | 모두 제거 |
| `ACADEMIC v4 · 5/11` (footer) | `속도는벡터 · CAPSTONE 2026` |
| `★3 / ★4` | 단순 method 이름만 |
| `★3 RECTIFY` ribbon | "정정" 또는 단순 표기 |
| `★ NEW` (P9/P10) | 단순 paradigm grid (P9/P10이 추가됐다는 narrative만 speaker notes) |
| `4강 framing` | 직접 "9 paradigm 확장" |
| `V1 / W4 / V7 audit / 5/11 신규` | 모두 제거 + "최근 발견" 또는 카테고리 분류 |
| `5/11 measurement` | 제거 |
| `paper exact` (footer) | 제거 (본문에서 1번 언급) |
| `★ MAIN` ribbon (S12) | 제거 또는 "본 연구의 핵심 기여" 한 줄 |
| `RQ1/RQ2/RQ3` (eyebrow) | "첫 번째 검증 / 두 번째 검증 / 세 번째 검증" 한국어 |
| `audit / rectify / honest finding` | "검증 / 정정 / 정직 보고" 자연스러운 한국어 |

### D. 텍스트 최소화 — 시각화 우선
- ❌ 현재 일부 slide 의 본문 설명 텍스트
- ✅ 본문 narrative 모두 speaker notes 로 이동
- ✅ slide 본문 = 핵심 수치 (50-80px navy) + 결론 1줄 (implication bar) + 시각화 (chart / heatmap / card)
- ✅ bullet list 0 — 모두 시각 카드 / 다이어그램

### E. 단어 선택 자연스럽게 (학부생도 이해)
| 기존 | 재정 |
|---|---|
| `paper §V-B Bernoulli 보존 + KM20 stratified estimator 산술 평균 ensemble augment` | "본 논문의 표본 추정 절차는 그대로 두고, 분포 인지형 추정량을 산술 평균으로 결합" |
| `paper main result 인정` | "본 논문의 주요 결과는 그대로 수용하면서" |
| `paradigm rollup` | "추정 방법 분류 통합 평균" |
| `Bernoulli baseline` | "무작위 균등 표본 (Bernoulli)" |
| `KM20 stratified` | "k-means 20 클러스터 층화 표본" |
| `ensemble augment` | "결합 추정 보강" |
| `paradox` | "예상과 다른 결과" |
| `RECTIFY` ribbon | "정정" 한국어 |
| `★3 hilbert defect rectify` | "Hilbert 곡선 색인 — 학술적 정정" |
| `byte-identical cells` | "동일 cell" |
| `cherry-pick prevention` | "선별 편향 방지" |
| `Deterministic 100%` | "재현성 100%" |

### F. AI 흔적 제거
- ❌ Speaker notes 안 "★3 hilbert defect rectify, top winners, negative control..." 같은 AI agent 톤
- ❌ "Reload for new version" 버튼 / "Fork verifier agent" 같은 작업 메타
- ❌ "audit / rectify / fix / hand-coded SVG / 18 SLIDES" 등 작업 흔적
- ✅ 학생 작성 톤 — 학술 산문 한국어. AI agent 표현 없음.
- ✅ deck 본문 footer "ACADEMIC v4 · 5/11" → 단순 "속도는벡터 · CAPSTONE 2026"
- ✅ Slide number 표기는 OK ("17 / 18")

### G. 청중 친화성 (학부생도 이해 가능)
- ❌ 학술 용어 첫 등장 시 풀어쓰기 누락
- ❌ §V-A / §V-B 같은 본 논문 section 표기를 그대로 사용 (한 번은 "본 논문의 V절 B항 Adaptive Sampling" 풀어쓰기)
- ❌ paradigm 9 갑자기 등장 — 왜 9개인지 narrative 필요
- ✅ 각 slide 1 메시지 + 시각화 + 결론 1줄
- ✅ 학술 용어 + 한국어 풀이 첫 등장 시 병기

### H. Speaker notes — 자연 한국어 학술 산문
- ❌ "★3 hilbert defect rectify" 같은 내부 표기 그대로
- ❌ "v3 narrative 정정" 등 작업 메타 언급
- ✅ 학부생 청중 톤 + 자연어 한국어
- ✅ 각 slide 30-45초 분량 (총 12-15분)
- ✅ 강재현 발표자가 그대로 읽을 수 있는 스크립트

---

## 2. 18 slide 재구성 plan

| # | 새 제목 | 핵심 메시지 | 시각화 |
|:-:|---|---|---|
| 01 | (cover) Skew-Aware Stratified Sampling Ensemble | 연구 주제 한 줄 | hero text only |
| 02 | 목차 / 발표 순서 | 4 chapter 구성 | 4 chapter 카드 + 18 slide 흐름 |
| 03 | 해결하고자 하는 문제 | 고정 비율 → 잘못된 plan → 1000-10000× 느린 query | 좌 베이스라인 카드 + 우 실분포 |
| 04 | 기존 연구 — Exqutor 두 보완책 | ECQO 인덱스 활용 + Adaptive Sampling 본 연구 영역 | 좌-우 카드 + 본 연구 위치 강조 |
| 05 | 우리 접근 — 두 추정량 산술 평균 결합 | 본 논문 절차 보존 + 분포 인지 추정량 layer 추가 | ensemble 다이어그램 + 의사 비유 |
| 06 | 첫 번째 검증 — 분포 차이가 정확도에 미치는 영향 | +3.74% 평균 격차 | 5 cell bar chart + paper Fig 12 일치 |
| 07 | 추정 방법 분류 — 9가지 paradigm framework | 30+ method를 9개 paradigm 으로 통합 | 3×3 paradigm grid |
| 08 | 두 번째 검증 — 분포 정보가 있을 때 최적 배분 | 4 가지 배분 방식 비교 + 예상과 다른 발견 | 5-way bar |
| 09 | 세 번째 검증 — 분포를 모를 때 전 paradigm 성능 | 5 paradigm 통계 압도 | horizontal bar (9 paradigm) |
| 10 | Hilbert 곡선 색인 — 학술적 정정 | PCA proxy vs 진짜 Hilbert 분리 검증 | 4 anchor card |
| 11 | 가장 강한 효과 method | DEEP sf=1 에서 효과 최대 | Top 5 ranking |
| 12 | 본 연구의 핵심 기여 — 결합 추정 효과 | 4 큰 수치 (92.9 / 63.5 / 56.4 / 71.8%) + 한 줄 비유 | 4 big number card |
| 13 | 단독 대체 vs 결합 보강 — 효과의 차이 | 단독은 통계 무효, 결합만 유효 | 좌-우 대비 카드 |
| 14 | scale factor 1, 10, 100 일관성 | 부호 일관 + paper Fig 14 일치 | 3 scale card |
| 15 | mechanism — locality 분리 검증 | 4 method × 9 cell heatmap | heatmap |
| 16 | 효과 크기 정직 보고 — 4축 통계 | Hedges' g / Cliff's δ / 재현성 / 결정론 | 4 stat card |
| 17 | 본 연구의 한계 | 18 한계 → 4 카테고리 분류 | 4 column grid |
| 18 | 향후 연구 + 마무리 | 8 future + 본 연구 한 줄 요약 + 감사 | 4×2 future card |

---

## 3. <실험중, 데이터만 채우면 됨> 미완 영역

- **S11 Top winners 수치**: 현재 추정값. 측정 정확치는 Q4 회수 후 확정
- **S15 mechanism heatmap data**: 4 anchor × 9 cell 의 정확한 측정치는 paper exact 측정 회수 후 확정
- **S14 sf=100 cross-scale**: SF=100 측정이 현재 부분만 — 5/12 회수 후 확정

---

## 4. footer / chrome 디자인 정정

- **footer 좌측**: "속도는벡터 · CAPSTONE 2026"
- **footer 우측**: "2026.05.27" 또는 페이지 번호만
- **stripe**: navy 그대로
- **numbered badge**: "01 02 ... 18" 그대로
- **page counter**: "01 / 18" 그대로
- **implication bar**: 그대로 (시각 강조 효과)
- **deck title 표기 영역**: 모든 slide 메타 "ACADEMIC v4 · 5/11" → "속도는벡터" 만

---

## 5. 실행 전략

1. claude.ai/design 에 정정 prompt 전달
2. monitoring (약 5-8 분)
3. 핵심 slide visual 검증 (S1, S2, S10, S17, S18)
4. 추가 정정 필요 시 iteration

---

작성: 2026-05-11 20:55 KST
