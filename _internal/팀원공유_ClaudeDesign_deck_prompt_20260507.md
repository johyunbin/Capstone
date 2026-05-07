# Claude Design용 — 팀원 공유 deck prompt (Academic v3 톤)

> **목적**: `팀원공유_RQ진행정리_구어체_20260507.md` 11 메시지를 Academic v3 톤 deck (10-12 slide) 으로 변환.
> **사용**: Claude Design (https://claude.ai/design) chat 에 본 prompt 통째로 붙여넣어 신규 deck 생성.
> **기존 5/27 발표 deck Academic v3** (16 slide) 와 일관 톤. 회의용 short version.

---

## Claude Design 입력 prompt (복붙)

```
다음 내용으로 학술 회의용 deck 을 만들어줘. 디자인 spec:

[디자인 시스템 — Academic v3 일관 톤]
- 1280×720, 10-12 slide
- 흰 배경 + 좌측 navy (#1B365D) 세로 bar (8px)
- 우측 상단 검정 사각형 numbered badge (slide 번호)
- 하단 page indicator (1/12 형태) + footer caption ("속도는벡터 캡스톤 · 5/8 회의")
- 폰트: Apple SD Gothic Neo (한글), Inter (영문 숫자)
- 강조 수치는 huge typography (60pt+)
- 표는 navy header + light gray (#F5F7FA) zebra
- 색: navy #1B365D / light #F5F7FA / gray #6B7280 / red accent #C53030 (negative)

[목적]
팀원 5/8 19:00 비대면 회의 직전 자료. 실험 처음 보는 사람도 바로 이해할 수 있게 핵심 단어 위주.

[slide 구성 — 10-12장]

Slide 1 — Cover
제목: "RQ1/2/3 W1 Sprint 결과 종합"
부제: "5/7 22 method 측정 완료 · 5/8 회의 D-1"
하단: "속도는벡터 · 박세은 · 강재현 · 조현빈 · 이동욱"

Slide 2 — 데이터셋 진행 상황 (4-card grid)
제목: "측정 진행 상황"
4-card:
1. DEEP 1M (Normal, 96차원) — 22 method ✓
2. SIFT 1.5M (Skew, 128차원) — 22 method ✓
3. DEEP 8M (Normal, 대용량) — 16 method ✓
4. 멀티 테이블 join — future work
하단 implication bar: "단일 테이블 22 method × 2 dataset 1차 측정 완료, 8M cross-scale 검증 ✓"

Slide 3 — RQ1 (분포 모르는 random sampling 부정확성)
좌측: 가설
- 데이터 한쪽에 쏠려있으면 (skew) random 더 부정확
- selectivity 낮을수록 더 부정확
우측: 결과
- huge stat: "ρ = −0.680" (per-seed Spearman, CI [−0.800, −0.440])
- 단조 감소 통계 확정 ✓
- gradient 19.6%p (KM20 +8.93% vs RANDOM20 −10.67%, s=0.01)
- 부제: Phase 6 (SQL D, vector.c hook, production-near)
하단: ✓ 가설 모두 적중

Slide 4 — RQ1 5/7 W2 발견 (Phase 6 vs Phase 7)
제목: "Methodology Robustness — 5/7 W2 추가 발견"
좌측: 의문
"같은 단조성이 numpy simulation 에서도 나올까?"
우측: 결과 (red accent)
- Phase 6 (SQL D): ρ=−0.680 CI 0 제외 ✓
- Phase 7 (numpy D): ρ=+0.240 CI 0 포함 ✗
- 5-cell 격차: s=0.01 Δ=−12.26%p, s=0.50 Δ=−9.44%p
하단: 결정 (옵션 2 정직 reporting)
- Phase 6 핵심 인용 (production-near)
- Phase 7 honest 별도 보고
- 5-cell 격차 → "measurement methodology robustness sub-contribution"

Slide 5 — RQ2 (분포 알 때 5 mode allocation)
좌측: 5 mode
1. BERN (random baseline)
2. Equal (cluster마다 같은 수)
3. Proportional (크기 비례)
4. Neyman (σ_i 분산 비례, 이론 최적)
5. Anti-Neyman (σ_i 반대, negative control)
우측: 결과
- huge stat: "40 / 40" (cell KM20 우위)
- ✓ 모든 stratified > BERN
- ⚠️ Neyman vs Equal 거의 차이 X (σ_i 신호 약함)
- ⚠️ Anti-Neyman vs Prop: 좁은 sel 만 systematic hurt
하단: σ_i 신호 약함 honest → RQ3 distribution-agnostic 추구의 motivation

Slide 6 — RQ3 22 method 분류 (5 paradigm)
제목: "RQ3 — 분포 모를 때 22 method 비교"
4-card grid + 1 column:
- Cluster (7개): KM20 / MiniBatch / partial_fit / HDBSCAN / GMM / BIRCH / Spectral
- Locality (3개): Hilbert / Z-order / Hybrid
- Projection (3개): Random Proj / Sparse RP / PCA-1D
- Tree (2개): KD-tree / PQ
- Online weight (4개): KDE-pilot / Distance-Shell / IS variants
하단: 5/5 회의 7-way → W1 16-method → 5/7 22-method 확장

Slide 7 — RQ3 4강 (★ paired bootstrap CI 0 제외 robust)
4-card grid:
★1 Hilbert: huge stat "d=−0.156", learning-free + 결정론, ~수초 fit
★2 MiniBatch partial: huge stat "ARI = 1.000", batch 동등 OLTP
★3 HDBSCAN (5/7 NEW): huge stat "−3.99%" SIFT mid-sel best, density-based
★4 Hybrid (5/7 NEW): huge stat "rank 5.83", KMeans + Hilbert 결합
하단: 모든 method |d| < 0.8 → "공간 인식 의 limit" honest

Slide 8 — RQ3 Negative Control (cluster 분할 가치 정량)
제목: "Cluster 분할 자체의 결정적 가치"
4-row table (red accent):
- PQ DEEP s=0.01: +23.64% (massive failure)
- Sobol SIFT s=0.01: +33.62% (가장 큰 hurt)
- IS variants: d = +0.5~+0.7 (medium hurt)
- Distance-Shell: d = +0.49 (cluster X 한계)
하단: 4 negative control 모두 CI 0 제외 hurt → "cluster 분할 자체"가 가치

Slide 9 — Hilbert mechanism (5/7 W1-C 분석)
제목: "Hilbert 가 강한 이유 — 정량 분리"
좌측: huge stat "1.000" (inverse Manhattan)
우측 비교:
- Hilbert: 1.000 (perfect 1D-2D continuity)
- Z-order: 1.992 (50% jumps)
- Stratum compactness: Hilbert 4.77 vs Z-order 12.12 (2.54×)
- ARI orthogonality: sparse_rp 1위 → pca1d → curve → tree → cluster
하단: 7-way 비교가 정보 직교성 5 region cover

Slide 10 — RQ2 vs RQ3 종합 비교 (상황별 권장)
제목: "분포 알 때 vs 분포 모를 때"
table (4 row × 2 col):
| 상황 | 권장 |
| 분포 알다 + 학습 OK | KM20 oracle (40/40 일관) |
| 분포 알다 + OLTP | MiniBatch partial_fit (ARI 1.000) |
| 분포 모름 + 학습 X | Hilbert (~수초, 결정론) |
| 분포 모름 + SIFT skew | HDBSCAN (mid-sel best −3.99%) |
하단 implication bar: "공간 인식 자체가 가치 — 분포 모르더라도 위치만 알면 OK"

Slide 11 — 향후 일정 + 추가 보강 후보
제목: "남은 실험 + 일정"
2 column:
좌측 — 8M / 멀티 테이블
- DEEP 8M: 16 → 22 method 확장 (W2)
- SIFT 8M 측정 (현재 1.5M만)
- 멀티 테이블 join: future work (Exqutor main scope)
우측 — 추가 보강 후보
- σ table 재계산 (DEEP 1M / SIFT)
- NMI / AMI metric (RQ3 robustness)
- Phase 6/7 root cause 정량
하단: 마감 D-day 표
- 5/8 (오늘) 19:00 비대면 회의
- 5/15 자문 발송
- 5/22 교수님 미팅
- ★ 5/27 최종 발표 (D-20)
- ★ 6/11 최종 보고서 (D-35)

Slide 12 — Closing (5/8 회의 안건)
제목: "5/8 회의 합의 안건"
5 numbered:
1. RQ1 narrative 옵션 2 (정직 reporting) 채택
2. RQ3 contribution 5종 (HDBSCAN + Hybrid 추가) 격상
3. Limitations 6종 (L1~L6) 명시
4. 자문 메일 합의 (5/15 발송)
5. W2 분담 + 5/27 발표 분담
하단: "질문/피드백 회의에서 부탁드립니다 🙏"

[수치 정확성 — master.md 1:1 대조 필수]
- ρ = −0.680 [−0.800, −0.440] (Phase 6 DEEP-KM20)
- ρ = +0.240 [−0.061, +0.480] (Phase 7 DEEP-KM20)
- 5-cell 격차: s=0.01 Δ=−12.26%p, s=0.50 Δ=−9.44%p
- gradient 19.6%p
- KM20 40/40 cell 우위
- Anti-Neyman DEEP s=0.01 +5.21%, SIFT s=0.01 +9.49%
- Hilbert d=−0.156, inverse Manhattan 1.000 vs Z-order 1.992
- MiniBatch partial ARI 1.000, SIFT s=0.10 −2.36% [−4.15, −0.43]
- HDBSCAN SIFT s=0.10 −3.99% [−5.34, −2.12]
- Hybrid SIFT s=0.10 −3.10% [−4.61, −1.19], rank 5.83
- PQ DEEP s=0.01 +23.64%, Sobol SIFT s=0.01 +33.62%
- IS d = +0.5~+0.7

[제약]
- 5/27 발표 deck Academic v3 (16 slide) 와 일관 톤 — slide 번호만 짧게 10-12
- 본 deck = 회의용 short. 발표용 deck 별도 (5/27 deck v3 보존)
- 한글 폰트 깨짐 X
- 모든 수치는 master 1:1 — 임의 변경 X
```

---

## 📌 발송 후 액션

### Claude Design chat 에서 deck 생성 후

1. URL 받기 → 카톡 단톡방 공유
2. PDF / PPTX export → `submission/_drafts/속도는벡터_5월8일회의_RQ진행정리_v1.{pdf,pptx}` 로 저장
3. 카톡 + 노션 둘 다 공유

### 사용자 결정 사항

- **deck 길이**: 10 slide (압축) vs 12 slide (여유) — 권장 12 (각 RQ 별 충분 분량)
- **공유 시점**: 회의 직전 (17~18시) vs 즉시 (11시)
- **공유 채널**: 카톡 단톡방 (URL) + 노션 첨부 (PDF) 둘 다 권장

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 11:42 KST
**기반**: `_internal/팀원공유_RQ진행정리_구어체_20260507.md` (commit 592b022) + Academic v3 deck (commit 21f4d5b)
