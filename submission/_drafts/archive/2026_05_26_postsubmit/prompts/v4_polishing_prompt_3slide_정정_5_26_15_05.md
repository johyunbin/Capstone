# v4 polishing prompt — 3 slide 정정 (5/26 15:05)

deck_v27.html에 다음 3건만 정정. 디자인 시스템·다른 슬라이드·voice over는 건드리지 말 것 — 명시 항목만 surgical edit.

## ① Slide 11 — latency 배수 계산 오류 정정 (강재현 지적)

현재 표기:
- pgvector 기본 (Adaptive Sampling X) — 5,677 ms (1.0×) · grey
- baseline (논문 원본 그대로) — 977.6 ms (**5.77× ↑**) · navy
- 결합 (본 연구) — 983.5 ms (**5.70× ↑**) · cyan

문제:
1. **배수 계산 오류**
   - 5,677 ÷ 977.6 = **5.81×** (슬라이드 5.77× 오류, 0.04 차이)
   - 5,677 ÷ 983.5 = **5.77×** (슬라이드 5.70× 오류, 0.07 차이)
2. **↑ 화살표 방향 의미 거꾸로**
   - 977.6 / 983.5 는 5,677보다 **작은 (빠른)** 수치인데 `↑`로 표기 = "더 높음/느림"으로 읽힘
   - 정확한 표현 = `↓` (시간 단축) 또는 `× 더 빠름`

정정 후 표기:
- pgvector 기본 (Adaptive Sampling X) — 5,677 ms (기준, 1.0×) · grey
- baseline (논문 원본 그대로) — 977.6 ms (**5.81× 더 빠름 ↓**) · navy
- 결합 (본 연구) — 983.5 ms (**5.77× 더 빠름 ↓**) · cyan

캡션 (막대 옆): "**baseline 과 결합 latency 사실상 동등 (격차 +0.60%, 5.9 ms)**" 그대로 유지.

## ② Slide 14 (future work) — "두 갈래" 텍스트 제거 + 라벨 정리 (강재현 지적)

현재 표기 (deck_v22.html line 1357 + 1401):
- 슬라이드 헤더: `향후 작업 두 갈래`
- narration: `... 향후 작업 두 갈래 — Group A 메커니즘 후속과 Group B 산업 적용 framework — 는 placeholder 로 남깁니다.`

문제: "두 갈래" 는 군더더기 단어. Group A·Group B 두 카드가 시각적으로 이미 두 갈래임을 보여줌 → 텍스트 라벨로 중복.

정정:
- 슬라이드 헤더: `향후 작업` (만)
- narration: `... 향후 작업 — Group A 메커니즘 후속과 Group B 산업 적용 framework — 는 placeholder 로 남깁니다.` (`두 갈래 ` 단어만 삭제)

## ③ Slide 11/12 부근 — 13 method 두루뭉술 → 구체화 (강재현 지적)

현재 문제: 13 method 결합 결과가 한 막대로 통합되어 "어느 method가 어떻게 기여했는지" 시각이 부재. 청중이 본 연구 핵심 winner method (chao_weighted)와 paradigm 분포를 못 봄.

정정 — 2-slide pair 신규:

### 11.5 (신규 메인 슬라이드) — "본 연구 방법론 7 paradigm 대표 + winner 강조"

데이터 정합 정본 (DEEP sf=10 sel=0.001 Q3 qid=0):

| Paradigm | 대표 method | 추정 카디 | Q-error | latency (ms) | B1 대비 Δ% | oracle 회복 |
|---|---|---|---|---|---|---|
| Space-filling curve | hilbert_real ⚠️ | 8,546 | 1.1241 | 1,063.75 | +4.49% | ✗ |
| Dimensionality reduction | sparse_rp | 5,105 | 1.4892 | 1,032.09 | +1.38% | ✓ |
| Stratified sampling | cum_sqrtf | 6,226 | 1.2211 | 990.01 | −2.76% | ✓ |
| Quantization / grid bucketing | mhist2 | 3,457 | 2.1994 | 944.53 | −7.22% | ✓ |
| **Weighted reservoir sampling** | **chao_weighted ★** | **7,158** | **1.0622** | **927.05** | **−8.94%** | **✓** |
| Hash bucketing | hyperloglog | 3,222 | 2.3596 | 1,021.75 | +0.36% | ✓ |
| Clustering | — (N/A, 본 13 method에서 제외) | — | — | — | — | — |

구성:
- 헤더 큰 글씨: `7 paradigm × 대표 method — winner chao_weighted`
- 표 6행 (Clustering N/A 회색 표시)
- chao_weighted 행만 **cyan highlight + ★ 별표 + 좌측 winner ribbon**
- 표 아래 한 줄: `우리 winner = chao_weighted (Weighted reservoir, Chao 1982) — Q-error 1.0622·latency −8.94%·oracle plan 회복 ✓ 동시 달성`
- ⚠️ hilbert_real 행 좌측에 작은 주석 dot: `★3 PCA 2D lex sort alias — 정합성 honest 표시 (5/19 method audit)`

### 11.6 (신규 부록 슬라이드) — "13 method scatter (Q-error vs latency)"

scatter chart:
- x축: Q-error (log scale, 1.0 ~ 10.0)
- y축: latency (ms, 900 ~ 1080)
- 13 점 + B1 reference (마름모) + oracle reference (별)
- 색상: paradigm별 6색 (Clustering N/A 제외) — navy / cyan / red / amber / lime / violet
- chao_weighted 좌하단 점은 큰 cyan ring + label
- B1 = (∞, 1018) 우상단 화살표로 가리킴 + 빨간 dotted
- oracle = (1.0, 1000) 회색 별 + label

메시지 (slide 하단 한 줄):
`Q-error 개선이 항상 latency 개선으로 직결되지 않음 — 12/13 method 가 oracle plan 회복하면 latency 는 cell-level noise 안에 묶임`

## 데이터 정합 정본

모든 수치는 raw `_internal/cache/rq3/latency/phase2/latency_tpc_h_q3_DEEP_sf10_sel0.001_qid0.json` 한 파일 기준. 15-trial trim mean. true_card = 7,603. 본 prompt 외 다른 슬라이드의 수치는 절대 건드리지 말 것.

## 출력 요구

deck_v27.html → deck_v28.html 로 진화. 위 3 항목만 surgical edit:
1. Slide 11 latency 배수 정정 (5.77→5.81, 5.70→5.77, ↑→ "더 빠름 ↓")
2. Slide 14 (future work) "두 갈래" → "향후 작업" + narration 같은 단어 제거
3. Slide 11.5 (paradigm 7 winner 표) + 11.6 (13 method scatter) 2슬라이드 신규 추가

다른 모든 슬라이드·design system·spacing·voice over 는 동결.
