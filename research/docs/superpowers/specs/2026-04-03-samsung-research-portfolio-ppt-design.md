# 삼성리서치 Spatial Audio 1차 면접 포트폴리오 PPT 설계 스펙

## 1. 개요

### 목적
삼성리서치 Visual Technology > Display Innovation Lab > Spatial Audio 파트 1차 면접용 20분 포트폴리오 발표 자료 제작

### 면접 구조
- **동료 인터뷰** (60분): 파트장 + 파트원 2:1 → 20분 PPT 발표 + Q&A
- **임원 인터뷰** (60분): 부서장 1:1 → 동일 20분 PPT 발표 + Q&A
- E직군(신호처리-음향/음성)으로 예외 승인, SW 코딩테스트 면제

### 핵심 메시지
- **차별점**: 신호처리 전공자들 사이에서 건축음향/사운드스케이프 출신이면서 Spatial Audio 경험이 풍부
- **AI 전환**: VT팀이 AI 기반 기술 전환을 강하게 주문받는 중 → AI 역량을 자연스럽게 어필
- **파트 시너지**: Holographic Displays 파트와의 협력 (팀장이 파트 간 시너지 중시)
- **한 줄 포지셔닝**: "신호처리가 만드는 기술 위에, 사용자가 경험하는 품질을 설계합니다"

---

## 2. 발표 사양

| 항목 | 사양 |
|---|---|
| 슬라이드 수 | 18매 |
| 발표 시간 | ~20분 (빠르게 말하면 맞출 수 있는 ~23분 분량) |
| 발표 언어 | 한국어 |
| 슬라이드 언어 | 영어/한국어 혼용 (기술 용어는 영어 유지) |
| 슬라이드 크기 | 와이드스크린 16:9 |
| 이미지 소스 | 기존 PPT + 논문 PDF에서 추출 |

---

## 3. 디자인 시스템

### 색상 팔레트 (삼성 브랜드 기반, 기존 Prototype 참조)

| 용도 | 색상 | HEX |
|---|---|---|
| Primary Navy | 삼성 블루 (제목, 강조, 카드 배경) | `#13289F` |
| Accent Blue | 보조 파란색 (서브 요소, 아이콘) | `#3D7DDE` |
| Sky Blue | 하이라이트, 링크 | `#0689D8` |
| Dark Text | 본문 텍스트 | `#1A1A2E` |
| Gray | 보조 텍스트, 캡션 | `#5B718D` / `#75787B` |
| Light BG | 카드/섹션 배경 | `#F0F4F8` |
| Warm Gray | 타이틀 슬라이드 보조, 구분선 | `#E7E6E2` |
| White | 타이틀 슬라이드 텍스트, 배경 | `#FFFFFF` |
| Black | 강조 도형 | `#000000` |

### 디자인 원칙
- 타이틀 슬라이드(S1, S18): Navy 풀 배경 + 흰색 텍스트
- 콘텐츠 슬라이드: 흰색 배경 + Navy 제목 + 회색 본문
- 핵심 수치 카드: Light BG(`#F0F4F8`) 카드 위 Navy 큰 숫자
- Implication 박스: Navy(`#13289F`) 배경 + 흰색 텍스트
- 섹션 구분 바: Accent Blue(`#3D7DDE`) 상단 라인
- 기존 Prototype S1, S2, S6~S10, S13~S14의 레이아웃·색감 참조

---

## 4. 슬라이드 상세 설계

### [도입부] ~3분

#### S1. Title Slide
- **디자인**: Navy 풀 배경
- **제목**: "Spatial Audio Research & Perception-driven Quality Evaluation"
- **부제**: Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio
- **이름**: 조현인 (Hyun In Jo, Ph.D.)
- **현직**: Senior Research Engineer, Hyundai Motor Company (NVH Division)
- **연락처**: best2012@naver.com | 010-6387-8402 | linkedin.com/in/hyunin-jo

#### S2. About Me
- **좌측**: 경력 타임라인 (세로 흐름)
  - 2013-2016: B.S. 건축공학, 한양대 (수석졸업, 조기졸업)
  - 2016-2022: Ph.D. 건축음향, 한양대 (석박통합, GPA 4.39/4.5)
  - 2022.03-08: Post-doc, 한국건설기술연구원
  - 2022.08-현재: 현대자동차 NVH 책임연구원
  - → Samsung Research, Spatial Audio
- **우측**: 핵심 실적 카드 4개
  - SCI(E) 24편 (주저자 21편), h-index 18
  - EAA Best Paper Award (ICA 2019), I-INCE Young Professional Award
  - 특허 6건 (국내+미국), 기술이전 5천만원
  - UCL·소르본 등 국제공동연구, SATP 18개국 표준화 참여
- **하단**: 핵심 전문성 4개 (발표 Part와 1:1 대응)
  1. Spatial Audio & Immersive Rendering → Part I
  2. Perception-driven Quality Evaluation → Part II
  3. Research-to-Product Execution → Part III
  4. AI-driven Audio Processing → Part IV

#### S3. 핵심 질문 제기
- **상단** (문제 제기, 구체적 수치):
  > THD 0.01%, 주파수 응답 ±0.5dB — 공학 스펙이 완벽해도 사용자가 "좋다"고 느끼지 않을 수 있다
  > 시각 맥락만으로 오디오 만족도가 **76% 좌우**된다면? (본인 연구 결과)
- **중단** (핵심 질문, 크게):
  > "사용자가 진짜 몰입을 느끼는 3D Audio-Visual 경험을 어떻게 설계하고 검증할 것인가?"
- **하단** (4 Part 로드맵):
  - Part I: Spatial Audio 기술 역량 (8분)
  - Part II: 지각 기반 평가 방법론 (3분)
  - Part III: 제품 적용 AVAS (3분)
  - Part IV: AI 확장 + Contribution (4분)

---

### [사운드스케이프 → Spatial Audio 브릿지] ~2분

#### S4. 사운드스케이프란?
- **상단**: 패러다임 전환 대비
  - 좌: Traditional (Noise Control) — "소음이 얼마나 큰가?" dB 기반 물리적 측정
  - 우: New Paradigm (Soundscape) — "소리가 어떻게 경험되는가?" 인간 지각 중심
- **중단**: ISO 12913 정의 인용
  > "Acoustic environment as **perceived** or **experienced** and/or **understood** by a person or people, **in context**"
- **하단**: Pleasant-Eventful 2차원 모델 다이어그램
- **그림**: 기존 PPT S5의 다이어그램 이미지 활용

#### S5. 왜 사운드스케이프가 Spatial Audio에 직결되는가
- **5행 연결 테이블**:

| # | 사운드스케이프 관점 | → | Spatial Audio 적용 |
|---|---|---|---|
| 1 | 소리를 **경험**으로 평가 (dB가 아닌 사용자 지각 중심 다차원 평가) | → | 렌더링 품질을 THD·주파수응답 같은 공학 지표가 아닌, **사용자가 느끼는 공간감·몰입감**으로 평가 |
| 2 | **오디오-비주얼 상호작용** (시각 맥락이 청각 지각을 최대 76% 좌우) | → | Display + Audio **통합 설계** — Holographic Displays × Spatial Audio 시너지의 지각적 근거 |
| 3 | **재생 환경**에 따라 동일 음원의 지각이 달라짐 (실내/실외/공간 특성) | → | 거실·침실·차량 등 **재생 공간별** 렌더링 최적화 — 같은 원리, 다른 스케일 |
| 4 | **개인차** (소음 민감도·성격·청력 프로필이 지각을 조절) | → | **Customized Audio** 개인화 — 사용자별 최적 렌더링의 이론적 근거 |
| 5 | **대규모 지각 평가 프로토콜** 설계·실행 역량 (ISO 12913 + SATP 18개국, 134명 청감평가) | → | Eclipsa Audio **품질 벤치마킹** 및 인증 기준 수립 — 체계적 평가 설계 역량 |

- **하단 강조**:
  > "신호처리가 '어떻게 구현할 것인가'라면, 저의 전문성은 **'사용자가 어떻게 경험할 것인가'를 설계하고 검증하는 것**입니다"

---

### [Part I. Spatial Audio 기술 역량] ~8분

#### S6. Spatial Audio 연구 체계도 (Overview)
- **상단**: "Part I. Spatial Audio 기술 역량" 섹션 타이틀
- **중앙**: 5개 기술 축 다이어그램 (트리 또는 카드 배치)
  - 축1: 시각 재현 방식 영향 (APAC'22)
  - 축2: 재생 방식 영향 (APAC'19)
  - 축3: 바이노럴-비주얼 상호작용 (B&E'19 ×2)
  - 축4: 시청각 정보 영향 (B&E'20)
  - 축5: 생태학적 타당성 (SCS'21)
- **하단**: "VR 환경에서 Spatial Audio의 각 기술 요소가 사용자 지각에 미치는 영향을 체계적으로 규명"

#### S7. 축1: 시각 재현 방식의 영향
- **논문**: APAC_2022_Jo&Jeon (Applied Acoustics, IF 3.4)
- **RQ**: 같은 Spatial Audio를 HMD vs 모니터로 볼 때, 사용자 지각이 얼마나 달라지는가?
- **핵심 수치**: 40명 × 8환경 / HMD에서 부정·긍정 요소 모두 더 민감하게 인식 (p<0.05)
- **한 줄 결과**: HMD = 공간 현실감↑ / 모니터 = 전반적 인식↑
- **→ Eclipsa Audio**: XR 디바이스 대응 시, 시각 조건 통제가 품질 평가의 전제
- **그림**: APAC_2022 논문 Fig — HMD vs 모니터 평가 결과 비교 차트

#### S8. 축2: 헤드폰 vs 스피커
- **논문**: APAC_2019_Jeon et al (Applied Acoustics, IF 3.4)
- **RQ**: 헤드폰과 스피커 재생 방식이 사용자의 소리 품질 판단을 어떻게 바꾸는가?
- **핵심 수치**: 허용한계 6% 차이 / 성가심 8% 차이 / 50% 성가심 도달 SPL 2.2 dBA 차이
- **한 줄 결과**: 스피커+HMD 조합이 실제 환경에 가장 근접한 평가
- **→ Eclipsa Audio**: 헤드폰(바이노럴) vs 스피커(멀티채널) 재생 시 지각 차이 정량화 기준
- **그림**: APAC_2019 논문 Fig — 4가지 재생 환경별 허용한계/성가심 그래프

#### S9. 축3: 바이노럴-비주얼 상호작용
- **논문**: B&E_2019_Jeon&Jo + B&E_2019_Jo et al (Building and Environment, IF 7.4) — 2편
- **RQ**: HRTF와 HMD, 어느 것이 사용자 공간 지각에 더 지배적인가?
- **핵심 수치 (크게)**: **HRTF 77%** vs **HMD 23%**
- **보조 수치**: HRTF+HMD 시 음상 외재화·몰입감 유의 증가, VR에서 허용한계 6~7 dB 하락
- **→ Eclipsa Audio**: HRTF 개인화 = 렌더러 최적화의 최우선 과제
- **그림**: B&E_2019 논문 Fig — 2×2 실험 설계 매트릭스 + HRTF 77% 기여도 차트 (기존 PPT S18 참조)

#### S10. 축4: 시청각 정보의 지각 영향
- **대표 논문**: B&E_2020_Jeon&Jo (Building and Environment, IF 7.4)
- **RQ**: Audio와 Visual 정보가 전체 만족도에 각각 얼마나 기여하는가?
- **핵심 수치 (크게)**: **청각 24%** vs **시각 76%**
- **보조 수치**: 만족도 모델 설명력 51% / 오디오가 landscape 자연스러움에도 영향 (cross-modal)
- **참고**: 구조방정식(SEM) 경로 모델은 B&E_2021_Jo&Jeon에서 발전적 제시
- **→ Eclipsa Audio**: Display + Audio 통합 설계가 만족도 극대화의 핵심 → Holographic Displays 시너지
- **그림**: B&E_2020 논문 Fig — Audio 24% vs Visual 76% 비율 바 + 만족도 모델

#### S11. 축5: 생태학적 타당성
- **논문**: SCS_2021_Jo&Jeon (Sustainable Cities and Society, IF 11.7)
- **RQ**: VR 실험실 평가 결과를 실제 현장(in-situ)과 동일하게 신뢰할 수 있는가?
- **핵심 수치**: 50명 × 10환경 / ISO 12913-2 3가지 프로토콜 모두에서 VR ≈ In-situ 유사 결과
- **한 줄 결과**: FOA 바이노럴 + 헤드트래킹의 높은 생태학적 타당성 실증
- **→ Eclipsa Audio**: VR 기반 실험실에서 렌더링 품질 평가 → 실사용 환경 결과를 신뢰할 수 있음
- **그림**: SCS_2021 논문 Appendix A — VR vs In-situ 비교 결과

---

### [Part II. 지각 기반 평가 방법론] ~3분

#### S12. 멀티모달 생리반응 모델링
- **논문**: SCS_2023 (IF 11.7, 교신저자) + SR_2022 + IJERPH_2024
- **RQ**: 물리적 음향 파라미터로부터 사용자의 생리적 지각 반응을 예측할 수 있는가?
- **실험**: 60명 × 9환경 × 2일 / FOA + HMD + 헤드트래킹
- **측정**: EEG (32ch, α/β ratio) · HRV (5지표) · Eye-tracking
- **핵심 수치 카드** (크게 4개):
  - 정준상관 0.80 — 물리음향 ↔ 심리반응
  - 정준상관 0.78 — 지각품질 ↔ 심리반응
  - SDNN +14.6% — 스트레스 저항력↑
  - TSI -9.5% — 스트레스 지수↓
- **→ Eclipsa Audio**:
  - EEG/HRV 프로토콜 → 렌더링 품질 객관 검증 (설문 의존 탈피)
  - 물리 파라미터 → 지각 예측 모델 → 렌더링 자동 최적화 기초
  - A-V 일치 시 회복 효과 → Display+Audio 통합의 생리적 근거
- **그림**: SCS_2023 Fig — HRV 환경별 차트 + IJERPH_2024 Fig — Eye-tracking 히트맵

#### S13. 사운드스케이프 디자인 응용
- **논문**: B&E_2021_Jo&Jeon (IF 7.4) + B&E_2022_Jo&Jeon (IF 7.4)
- **RQ**: 오디오-비주얼 상호작용이 실내 환경의 업무 품질과 생산성에 미치는 영향은?
- **핵심 결과**: SEM 모델로 Audio → Visual → 만족도 경로 정량화 / A-V 일치 시 업무 선호도·생산성 유의 향상
- **→ Eclipsa Audio**: TV·사운드바가 놓이는 실내 환경별 최적 렌더링 설계의 이론적 근거
- **그림**: B&E_2021 논문 Fig — SEM 경로 모델 다이어그램

---

### [Part III. 제품 적용 — 연구 → 양산] ~3분

#### S14. AVAS 사운드스케이프 디자인
- **출처**: HMG 학술대회 + JASA 논문 (심사 중)
- **배경**: EV 시대 → AVAS가 도시 음환경의 새로운 요소. 사운드스케이프 개념 최초 적용
- **데이터**: 17개 EV × 43개 AVAS 바이노럴 레코딩 DB / 134명 대규모 청감평가
- **방법론**: 3단계 감성어휘 선정 (272개 → 25쌍 → 18쌍) → PCA → 신규 감성축
- **핵심 수치 카드**:
  - Comfort–Metallic: 기존 Pleasant-Eventful로 구분 불가 → 신규 평가축 제안
  - 만족도 예측 92.5%: 물리지표만으로 자동 예측
  - 34대 경쟁 DB: 전 브랜드 벤치마킹 체계
- **→ Eclipsa Audio**:
  - 물리지표 → 만족도 예측 → 렌더링 파라미터 자동 튜닝 기초
  - 감성 평가 프레임워크 → Eclipsa vs Dolby Atmos 경쟁 분석 도구
  - 134명 대규모 청감평가 설계·실행 역량 → 디바이스 품질 인증 프로세스
- **그림**: HMG 학술대회 PPT — Comfort-Metallic PCA 브랜드 포지셔닝 차트

#### S15. 연구 → 양산 실행력
- **적용**: AVAS 브랜드 사운드 2.0 → EV3, IONIQ 5 등 양산 적용
- **프로세스**: 음향 설계 → 청취 평가 → 시스템 검증 → 양산 — 전 과정 주도
- **성과**: 특허 6건 (국내+미국), 기술이전 5천만원, HMG 학술대회 특별상
- **웹 툴**: Shiny 기반 만족도 예측 웹 앱 → 사내 품질 모니터링
- **→ 삼성리서치**:
  - 선행연구 → 제품 사양 전환 → 개발 일정·품질 기준 조율 실행력 입증
  - 디자인·법규·NVH 부서 간 AVAS 프로젝트 조율 경험 → 파트 간 협업 역량
- **그림**: HMG 학술대회 PPT S17 — 양산 적용 프로세스

---

### [Part IV. AI 확장성 + Contribution] ~4분

#### S16. AI 기반 오디오 처리
- **논문**: SENSORS_2021 (SCI)
- **문제**: AI 오디오 분류에서 학습 데이터 부족 (30명, 126건) + 기존 증강은 환경 음향 미반영
- **해결**: RIR Convolution 기반 증강 8건 → 43,000건 / 새 특징: Loudness + Energy Ratio
- **핵심 수치 카드** (AI vs 전문가 8명):
  - 정확도: AI 84.9% vs 전문가 56.4%
  - 민감도: AI 90.0% vs 전문가 40.7%
  - AUC: AI 0.84 vs 전문가 0.56
- **IP**: 국내 특허 + 미국 특허 + 기술이전 5천만원
- **→ Eclipsa Audio**:
  - RIR 기반 증강 → 다양한 재생 환경 학습 데이터 생성
  - 음향 도메인 + AI → 물리적 특성 반영한 특징 설계
  - 소량 → 대규모 학습셋 → 신규 디바이스 빠른 모델 적응
- **A-JEPA 비전** (하단 별도 박스):
  > Meta A-JEPA 자기지도 학습 + 음향 도메인 지식 결합
  > → AI 추출 오디오 표현 ↔ 사용자 지각 반응 대응 연구
  > → 지능형 적응 렌더링의 기초
- **그림**: SENSORS_2021 논문 Fig — 5층 LSTM 구조도 + ROC Curve/AUC 비교

#### S17. Contribution Plan (3단계 타임라인)

| | 입사 ~6개월 (즉시 기여) | 6개월~2년 (과제 확장) | 2년~ (Lab 비전 주도) |
|---|---|---|---|
| **Eclipsa Audio** | TV 2.0ch~사운드바 11.1.4ch 지각 품질 벤치마킹 체계 구축 / Eclipsa vs Dolby Atmos 비교 평가 프레임워크 | HRTF 바이노럴 개인화 (front-back confusion↓, externalization↑) / IAMF 2.0 Object-based 지각 품질 가이드라인 | |
| **AI 전환** | 기존 지각 평가 데이터 + AI 분석 파이프라인 구축 / RIR 증강으로 재생환경 학습 데이터 생성 | A-JEPA 기반 오디오 표현 학습 → 사용자 지각 대응 모델 / 재생 공간 자동 인식 + 적응형 렌더링 | AI 기반 Customized Audio 개인화 시스템 |
| **파트 시너지** | Holographic Displays 파트와 통합 A-V 지각 실험 설계 | 3D 시각 + Spatial Audio 동기화 렌더링 프로토콜 | Lab 통합 비전: 홀로그래픽 디스플레이 + 공간 오디오 통합 설계 가이드라인 주도 |
| **인증·표준** | THX/TTA 인증에 지각 평가 데이터 제공 | 사내 오디오 품질 인증 프로그램 체계화 | 국제 표준화 활동 (ISO/SATP 경험 활용) |

- **마무리 문구**: "신호처리가 만드는 기술 위에, 사용자가 경험하는 품질을 설계합니다"

#### S18. Thank You
- **디자인**: Navy 풀 배경 (S1과 대응)
- "경청해 주셔서 감사합니다. 질문 부탁드립니다."
- 조현인 (Hyun In Jo, Ph.D.)
- best2012@naver.com | 010-6387-8402
- linkedin.com/in/hyunin-jo
- Samsung Research · Visual Technology · Display Innovation Lab · Spatial Audio

---

## 5. 시간 배분

| 섹션 | 슬라이드 | 목표 시간 |
|---|---|---|
| 도입 (Title, About Me, 핵심 질문) | S1~S3 | ~3분 |
| 브릿지 (사운드스케이프 → Spatial Audio) | S4~S5 | ~2분 |
| Part I: Spatial Audio 기술 역량 | S6~S11 | ~8분 (체계도 1분 + 각 축 1~1.5분) |
| Part II: 지각 기반 평가 방법론 | S12~S13 | ~3분 |
| Part III: 제품 적용 (AVAS + 양산) | S14~S15 | ~3분 |
| Part IV: AI + Contribution + Thank You | S16~S18 | ~4분 |
| **합계** | **18슬라이드** | **~23분 (빠른 진행 시 20분)** |

---

## 6. 논문-슬라이드 매핑 (정확한 인용)

| 슬라이드 | 논문 | 저널 (IF) |
|---|---|---|
| S7 | APAC_2022_Jo&Jeon | Applied Acoustics (3.4) |
| S8 | APAC_2019_Jeon et al | Applied Acoustics (3.4) |
| S9 | B&E_2019_Jeon&Jo + B&E_2019_Jo et al | Building and Environment (7.4) × 2 |
| S10 | B&E_2020_Jeon&Jo (대표) / B&E_2021_Jo&Jeon (SEM 참고) | Building and Environment (7.4) × 2 |
| S11 | SCS_2021_Jo&Jeon | Sustainable Cities and Society (11.7) |
| S12 | SCS_2023_Jeon et al + SR_2022_Jo et al + IJERPH_2024_Jo&Jeon | SCS (11.7) + Scientific Reports + IJERPH |
| S13 | B&E_2021_Jo&Jeon + B&E_2022_Jo&Jeon | Building and Environment (7.4) × 2 |
| S14 | HMG 학술대회 + JASA (심사 중) | JASA |
| S16 | SENSORS_2021_Chung et al | Sensors (SCI) |

---

## 7. 그림 추출 계획

| 슬라이드 | 삽입할 그림 | 출처 |
|---|---|---|
| S4 | Pleasant-Eventful 2차원 모델 다이어그램 | 기존 PPT S5 |
| S7 | HMD vs 모니터 평가 결과 비교 차트 | APAC_2022 논문 Fig |
| S8 | 4가지 재생 환경별 허용한계/성가심 그래프 | APAC_2019 논문 Fig |
| S9 | 2×2 실험 매트릭스 + HRTF 77% 기여도 차트 | B&E_2019 논문 Fig + 기존 PPT S18 |
| S10 | Audio 24% vs Visual 76% 비율 바 + 만족도 모델 | B&E_2020 논문 Fig |
| S11 | VR vs In-situ 비교 결과 | SCS_2021 논문 Appendix A |
| S12 | HRV 환경별 차트 + Eye-tracking 히트맵 | SCS_2023 Fig + IJERPH_2024 Fig |
| S13 | SEM 경로 모델 다이어그램 | B&E_2021 논문 Fig |
| S14 | Comfort-Metallic PCA 브랜드 포지셔닝 차트 | HMG 학술대회 PPT |
| S15 | 양산 적용 프로세스 | HMG 학술대회 PPT S17 |
| S16 | 5층 LSTM 구조도 + ROC Curve/AUC 비교 | SENSORS_2021 논문 Fig + 기존 PPT |

---

## 8. 구현 방식

- python-pptx 기반으로 프로그래매틱 생성
- 논문 PDF에서 이미지 추출: pdftotext/pdf2image 또는 기존 PPT에서 shape 추출
- 기존 Prototype PPT의 레이아웃·색상·폰트 스타일을 최대한 재현
- 최종 산출물: `/Users/hyunbin/Research/Portfolio_HyunInJo_v2.pptx`

---

## 9. Q&A 대비 (슬라이드에 넣지 않지만 준비할 내용)

### 동료 인터뷰 예상 질문
- HRTF 개인화를 구체적으로 어떻게 접근할 것인가?
- Eclipsa Audio vs Dolby Atmos 비교 시 어떤 메트릭을 쓸 것인가?
- A-JEPA를 Spatial Audio에 어떻게 적용할 수 있는가?
- RIR 증강의 구체적 기술 (Convolution 방식, 공간 파라미터)
- 각 연구의 상세 방법론 (참가자 수, 장비, 분석 방법)
- 공간 구조 분석, 반사 경로 예측 기술에 대한 견해

### 임원 인터뷰 예상 질문
- 건축음향 출신이 Spatial Audio 팀에서 어떤 차별적 가치를 제공하는가?
- 현대차에서 삼성으로 이직하는 이유?
- 팀 내 갈등 해결 경험?
- 2년 내 어떤 성과를 낼 수 있는가?
- Holographic Displays 파트와의 구체적 시너지 아이디어?
- AI 기반 기술 전환에 어떻게 기여할 수 있는가?
