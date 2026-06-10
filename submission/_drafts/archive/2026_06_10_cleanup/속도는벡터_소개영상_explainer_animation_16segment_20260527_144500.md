# 속도는벡터 · 소개영상 explainer animation — Veo 3.1 16 segment 정본 (v3)

> 26-1 인공지능종합설계 · 캡스톤 디자인 · 연세대학교 BDAI 연구실
>
> 작성 2026-05-27 14:46 KST · 5/28 12:00 LearnUs 마감 약 21 시간 남음
>
> ★ **본 영상 = ref 영상 (`submission/_drafts/archive/2026_05_26_postsubmit/video/무제.mp4`, 31.8초 무음 explainer) base + Act 2·3·4 확장**. 사용자 명시 5/27 14:00 KST — "공상학적 cinematic X · 실제 알고리즘 동작 explainer animation · 발표 슬라이드 첨부 영상 느낌 살리기 · 쿼리 추출 → 우리 연구까지 narrative".
>
> ★ **이전 cinematic 19-segment storyboard (`속도는벡터_소개영상_Veo3_1_cinematic_19segment_20260527_134000.md`) 폐기** — 본 문서가 새 정본.

---

## 0. 영상 사양

| 항목 | 값 |
|---|---|
| 총 길이 | **2:08 (128 초)** |
| Segment | **16 개 × 8 초** (Veo 3.1 segment) |
| 해상도 | 1920 × 1080 (16:9 가로, 1080p) |
| 프레임 | 30 fps (또는 24 fps cinematic) |
| 오디오 | Veo 3.1 native audio — 한국어 narration + 효과음 + clean ambient (cinematic 음악 X) |
| 자막 | **영상 안 자막 없음** (Path A · 후처리 SRT) |
| 비주얼 톤 | **흰 배경 + coral `#D14F4F` (부정확) ↔ cyan `#3DAFC1` (정확) split** · clean academic explainer · ref 영상 동일 톤 |
| 톤 | clean academic · explainer animation · step-by-step algorithm reveal |

---

## 1. 4 막 16 segment 구조

| Act | 시간 | seg | hero | 핵심 메시지 |
|:--:|---|:--:|---|---|
| **I 한 cell explainer (ref carry)** | 0:00–0:32 | 4 (1A·1B·1C·1D) | "7,599 행" → "7.24× 격차" | 한 쿼리 → 한 추정 (33 vs 7,581) → 두 plan → 7,242 ms vs 1,000 ms |
| **II 본 연구 설계** | 0:32–1:04 | 4 (2A·2B·2C·2D) | "한 곳만 바꾼다" | §V-B 베르누이 5 단계 → 단일 개입 (분포 인지) → 4 mode matched → 1,508 cell |
| **III 결과** | 1:04–1:36 | 4 (3A·3B·3C·3D) | "89.1%" · "5.67×" · "94.9%" | 결합 우위 + 음성 대조 (메커니즘 분리) + 엔진 plan 회복 + 비대칭 구조 |
| **IV 결론·팀** | 1:36–2:08 | 4 (4A·4B·4C·4D) | "negative + methodological" | 기여 4 + honest limitation + 속도는벡터 + BDAI |

---

## 2. Veo 3.1 prompt — 16 segment

각 prompt 는 Veo 3.1 (Ultra) Flow 에 직접 복붙. 영문 prompt + Korean narration.

---

### Act I — 한 cell explainer (ref 영상 carry 재현)

#### Segment 1A · 0:00–0:08 — VECTOR RANGE QUERY 코드 + 의문

```text
8-second clean academic explainer animation, 1920x1080, white background, minimal flat design.

VISUAL: A clean white background. In the center of the screen, a code block fades in with a monospace terminal-style typography. The code block has a small dark-gray header showing "VECTOR RANGE QUERY" on the left and "DEEP SF=10 . SEL ≈ 0.001" on the right. Below the header, three lines of code appear character by character:
SELECT  ps_partkey, ps_supplycost
FROM    partsupp_deep_10
WHERE   (a blinking cursor)
Below the code block, a centered question in Korean fades in: "이 쿼리는 몇 행을 반환할까?" with a small gray question-mark icon. Below the question, a subtle gray subtitle: "PostgreSQL planner는 이 한 숫자로 plan을 결정한다."

CAMERA: Static framing, no camera movement. Subtle fade transitions for each element.

LIGHTING: Soft even white background. No dramatic lighting.

MOOD: Calm, academic, focused — a question is being posed.

KOREAN AUDIO NARRATION (calm academic male voice, slow pace): "벡터 술어를 포함한 분석 쿼리. PostgreSQL 플래너는 카디널리티 한 숫자로 실행 계획을 결정합니다."

SOUND EFFECTS: Soft typing sound as code appears. Subtle UI tick when the question appears.

MUSIC: Very subtle ambient pad in the background, low volume, no melody. No cinematic crescendos.
```

---

#### Segment 1B · 0:08–0:16 — GROUND TRUTH 7,599 행 reveal

```text
8-second clean academic explainer animation, 1920x1080, white background, minimal flat design.

VISUAL: A clean white background. At the top, a small monospace text: "WHERE p_vec . . :q < 0.86". Below it, a large grid of small square dots arranged in approximately 40 columns by 8 rows. Most dots are light gray; about 15 percent of the dots highlight in cyan color, scattered across the grid representing matched rows in candidate space. Below the dot grid, a centered small label: "PARTSUPP × SUPPLIER × LINEITEM · 후보 행 공간". Below that, an emphasized cyan label: "실제로 매칭되는 행 수 · GROUND TRUTH". In the lower center, a massive bold sans-serif number reveals with a smooth fade: "7,599" followed by a smaller superscript "행". Below the number, a thin gray subtitle: "이 숫자를 정확히 짚느냐가 plan을 가른다."

CAMERA: Static framing. Dots highlight in cyan sequentially with a wave effect. The "7,599" number reveals with a smooth scale-up.

LIGHTING: Soft even white background.

MOOD: Revealing, foundational — the ground truth.

KOREAN AUDIO NARRATION (calm academic male voice): "실제로 매칭되는 행 수는 칠천 오백 구십 구. 이 숫자를 정확히 짚느냐가 실행 계획을 결정합니다."

SOUND EFFECTS: Subtle dot tick sounds as dots highlight. A soft confirmation chime when 7,599 appears.

MUSIC: Very subtle ambient pad, low volume.
```

---

#### Segment 1C · 0:16–0:24 — PLANNER DEFAULT (33) vs ORACLE (7,581) split

```text
8-second clean academic explainer animation, 1920x1080, white background, side-by-side comparison.

VISUAL: A clean white background split into two equal panels with a thin vertical divider. The header at the top reads in small gray text: "PLANNER의 추정 · 둘은 같은 쿼리를 다르게 본다".
Left panel (coral-red color scheme): A small red label "A · 부정확" at top, then "PLANNER DEFAULT" in gray monospace. Below it, a small dot grid (40x8) with almost all dots in faded gray, only 2 dots highlighted in red. Bottom of panel: large red label "PLANNER ESTIMATE", then a massive bold number "≈ 33" with a smaller "행" subscript. Below the number, small gray text: "→ 작은 결과니까 hash join이면 충분".
Right panel (cyan color scheme): A small cyan label "B · 정확" at top, then "ORACLE INJECTION" in gray monospace. Below it, the same dot grid (40x8) with about 15% of dots highlighted in cyan. Bottom of panel: large gray label "PLANNER ESTIMATE", then a massive bold number "= 7,581" with smaller "행" subscript. Below the number, small gray text: "→ 큰 결과니까 index + nested loop".

CAMERA: Static framing. Left and right panels reveal simultaneously with a horizontal sweep.

LIGHTING: Soft even white background.

MOOD: Contrast — two different views of the same query.

KOREAN AUDIO NARRATION (calm academic male voice): "플래너 기본 추정은 약 삼십 삼 행. 정답 카디널리티 주입은 칠천 오백 팔십 일 행. 같은 쿼리를 두 추정이 완전히 다르게 봅니다."

SOUND EFFECTS: Two soft confirmation chimes — one for each panel.

MUSIC: Very subtle ambient pad, low volume.
```

---

#### Segment 1D · 0:24–0:32 — 실행 + 7,242 ms vs 1,000 ms · 7.24× 격차 hero

```text
8-second clean academic explainer animation, 1920x1080, white background, side-by-side comparison + final number reveal.

VISUAL: A clean white background. First half (0–4s): Side-by-side execution panels. Left (coral): "× PGVECTOR 기본" label, a small vertical plan tree with red boxes labeled "lineitem ~6.0M rows", "Seq Scan", "Hash Join", "Sort". Below it, a horizontal progress bar slowly filling with red color and a counter incrementing from 0 ms to 7,242 ms. Below the bar: small text "CPU 93% → 8% · MEM 98% → 12%". Right (cyan): "✓ ORACLE (TRUE_CARD 주입)" label, a vertical plan tree with cyan boxes labeled "partsupp_deep_10 HNSW index", "Index Scan", "Nested Loop ×3", "Gather Merge → Sort", "Result". A horizontal progress bar quickly fills with cyan and stops at 1,000 ms with a checkmark. Below: small text "CPU 27% → 6% · MEM 30% → 8%".
Second half (4–8s): The two panels shrink to the top edge. In the center of the screen, a final hero reveal — massive bold numbers side by side: red "7,242 ms" on the left, cyan "1,000 ms" on the right. In between them, a small framed box with "격차 ≈ 7.24× 차이". Below the two numbers, a centered emphasis: "추정 1건 → plan 1개 → 자원 7배".

CAMERA: Static framing. The two progress bars animate at different speeds. Numbers reveal with smooth scale-up.

LIGHTING: Soft even white background.

MOOD: Decisive — the cost of one mis-estimation.

KOREAN AUDIO NARRATION (calm academic male voice): "같은 쿼리, 같은 엔진, 같은 하드웨어에서 결과는 칠천 이백 사십 이 밀리초 대 천 밀리초. 약 칠 점 이 사 배 격차. 추정 한 건이 자원 일곱 배 차이를 만듭니다."

SOUND EFFECTS: Slow grinding sound for the red bar. Quick swoosh for the cyan bar. Final chime for "7.24×" reveal.

MUSIC: Very subtle ambient pad, slight emphasis at the final reveal.
```

---

### Act II — 본 연구 설계

#### Segment 2A · 0:32–0:40 — "이 한 숫자를 어떻게 더 잘 짚을 것인가?"

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. In the center, a large bold question in Korean: "이 한 숫자를 어떻게 더 잘 짚을 것인가?" The question slowly fades in. Below it, a small framed academic-paper-style box appears, showing the text "Exqutor · §V-B Adaptive Sampling" with a small page-icon. Below the paper reference, a horizontal flow diagram of 5 small circles connected by arrows, labeled left to right: "표본 추출 N=385", "Q-error 측정", "모멘텀 갱신", "표본 크기 조정", "반복". The first circle (표본 추출) glows slightly brighter, indicating it as the focal point.

CAMERA: Static framing. Question fades in. Then the diagram slides in from below.

LIGHTING: Soft even white background.

MOOD: Pivoting from problem to method — the research begins.

KOREAN AUDIO NARRATION (calm academic male voice): "이 한 숫자를 어떻게 더 잘 짚을 것인가. 한 논문이 제시한 적응적 표본 추출 다섯 단계가 출발점입니다."

SOUND EFFECTS: Soft paper sound when the paper box appears. Subtle ticks as each stage of the diagram appears.

MUSIC: Very subtle ambient pad, low volume.
```

---

#### Segment 2B · 0:40–0:48 — 단일 개입 (베르누이 → 분포 인지 stratification) zoom in

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. The 5-stage horizontal flow diagram from previous segment is shown at the top, smaller. The camera dramatically zooms into the first circle (표본 추출 N=385), which expands to fill the center of the screen. Inside the expanded circle, two side-by-side options appear: on the left, a small label "논문 그대로 · 무작위 베르누이" with a small dot pattern showing uniformly random dots. On the right, a label "본 연구 단일 개입 · 분포 인지 층화" with a small dot pattern showing dots organized into 4 distinct strata-groups. A glowing cyan arrow points from the random pattern on the left to the stratified pattern on the right. Below the comparison: "한 단계만 바꾼다. 나머지는 모두 논문 그대로."

CAMERA: Static framing with a dramatic push-in on the first circle as it expands. Arrow animates from left to right.

LIGHTING: Soft even white background.

MOOD: Pivotal — the single intervention.

KOREAN AUDIO NARRATION (calm academic male voice): "본 연구는 표본 선택 단계 한 곳만 분포 인지 층화 표본 추출로 바꿉니다. 나머지는 모두 논문 그대로."

SOUND EFFECTS: A whoosh sound as the camera zooms in. A confirmation chime when the cyan arrow lands.

MUSIC: Very subtle ambient pad, slight emphasis at "한 곳만".
```

---

#### Segment 2C · 0:48–0:56 — 4 mode matched 측정 (베이스라인·단독 대체·결합·정답)

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. In the center, a small black circle labeled "한 측정 셀" appears. From this center, 4 arrows radiate outward to 4 small boxes arranged in a 2x2 grid pattern around the center:
Top-left box (gray): "기본 엔진 · 고정 비율 추정"
Top-right box (red): "베이스라인 · 무작위 베르누이 (논문 그대로)"
Bottom-left box (yellow-orange): "단독 대체 · method 단독 (음성 대조군)"
Bottom-right box (cyan): "결합 · 베이스라인 + 분포 인지 평균"
Each arrow appears one by one in sequence. Below the diagram: "한 측정 셀에서 네 방식이 동시에 산출 · matched."

CAMERA: Static framing. The 4 arrows and boxes appear sequentially with subtle fade animations.

LIGHTING: Soft even white background.

MOOD: Structural reveal — the controlled experimental design.

KOREAN AUDIO NARRATION (calm academic male voice): "한 측정 셀에서 네 방식을 동시에 산출합니다. 기본 엔진, 베이스라인, 단독 대체, 결합."

SOUND EFFECTS: 4 soft "appear" chimes — one per box.

MUSIC: Very subtle ambient pad.
```

---

#### Segment 2D · 0:56–1:04 — 1,508 cell 측정 평면

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. In the center, a 3D isometric grid materializes — a transparent rectangular box subdivided into many small cubes. The grid axes are labeled in small gray monospace text: along the X axis (datasets): "DEEP · SIFT · SSN · DEEP+SIFT · DEEP+WIKI", along the Y axis (manipulation variables): "A1 · A2 · A3 · A4 · A5", along the Z axis (methods): "13 method". The total number of cubes equals 1,508. As the grid forms, each small cube fills with cyan color one by one rapidly. A large counter in the top-right increments rapidly: "0 → 1,508 cell". Below the grid: "5 데이터셋 × 5 조작변인 × 13 method = 1,508 측정 셀 전수."

CAMERA: Slow 360-degree rotation around the 3D grid for cinematic effect.

LIGHTING: Soft even white background. Subtle cyan glow from the cubes.

MOOD: Scale and rigor — the measurement plane.

KOREAN AUDIO NARRATION (calm academic male voice): "5 데이터셋, 5 조작변인, 13 method 의 천 오백 팔 측정 셀 전수에서 검증했습니다."

SOUND EFFECTS: A rapid sequence of soft ticks as the cubes fill.

MUSIC: Very subtle ambient pad.
```

---

### Act III — 결과

#### Segment 3A · 1:04–1:12 — hero "89.1%" + paired Δ% −4.38%

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. In the center, a massive bold sans-serif number reveals with a smooth scale-up: "89.1%" in cyan color. Below the number, a smaller label: "결합이 베이스라인을 이긴 비율 · 1,344 / 1,508 cell". Below the label, a horizontal histogram of paired Δ% values fades in — most bars are on the left side (negative Δ%), with a vertical dashed line marking the median at "-4.38%". A small cyan label below the histogram: "추정 오차 paired Δ% 중앙값 = -4.38%".

CAMERA: Static framing. Number reveals with smooth scale-up. Histogram bars rise in sequence from left to right.

LIGHTING: Soft even white background.

MOOD: Dramatic result reveal — the headline finding.

KOREAN AUDIO NARRATION (calm academic male voice): "1,508 측정 모두에서 짝지어 비교했습니다. 결합 방식이 89.1 퍼센트, 즉 천 삼백 사십 사 셀에서 베이스라인을 이깁니다. 추정 오차 중앙값은 4.38 퍼센트 더 작습니다."

SOUND EFFECTS: A soft confirmation chime when "89.1%" appears. Subtle ticks for histogram bars.

MUSIC: Very subtle ambient pad, slight emphasis at the number reveal.
```

---

#### Segment 3B · 1:12–1:20 — hero "35.2%" 음성 대조군 + 메커니즘 = 앙상블 효과

```text
8-second clean academic explainer animation, 1920x1080, white background, comparison reveal.

VISUAL: A clean white background. Left side: A small label "단독 대체" in muted yellow-orange tone, followed by a massive bold number "35.2%". Below the number, a small caption: "method 단독으로는 베이스라인을 거의 못 이긴다 (음성 대조군)". Right side: A small label "결합" in cyan, followed by the previous number "89.1%" recalled in smaller size. Between left and right, a large bold "≠" sign in dark gray. Below the comparison, in a clean horizontal layout: a centered key insight in bold: "메커니즘 = 분포 인지 X · 두 독립 추정량 평균의 앙상블 효과."

CAMERA: Static framing. Left side appears first, then "≠", then right side. The insight at the bottom fades in last.

LIGHTING: Soft even white background.

MOOD: Critical contrast — the mechanism revealed.

KOREAN AUDIO NARRATION (calm academic male voice): "그런데 단독 대체 방식은 35.2 퍼센트에서만 이깁니다. 동전 던지기 수준입니다. 89 퍼센트 우위의 진짜 메커니즘은 분포 인지가 아니라, 두 독립 추정량을 평균한 앙상블 효과입니다."

SOUND EFFECTS: Soft chime for "35.2%", a low click for "≠", a clear confirmation chime for the insight reveal.

MUSIC: Very subtle ambient pad.
```

---

#### Segment 3C · 1:20–1:28 — hero "5.67×" 엔진 가속 + 12 cell heatmap

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. Top half: A horizontal flow diagram showing "결합 추정값" arrow pointing to "pgvector vector.c 패치" arrow pointing to "엔진 실행". Below the flow, in the center, a massive bold number reveal: "5.67×" in cyan color, with a small subscript "평균 엔진 가속". Below the number, a small 3-row by 4-column heatmap, each cell colored in a cyan gradient (darker = faster speedup). The heatmap rows are labeled "Q3 · Q9 · Q10 · Q12" and columns labeled "qid 0 · qid 1 · qid 2". Below the heatmap, a small label: "12 cell × 16 variant × 15 rep = 2,880 회 측정 · 모두 가속."

CAMERA: Static framing. Number reveal first, then heatmap cells fill in sequence.

LIGHTING: Soft even white background.

MOOD: Engineering result — speedup is real.

KOREAN AUDIO NARRATION (calm academic male voice): "결합 추정값을 pgvector 엔진에 직접 주입했습니다. 12 셀 평균 5.67 배 가속. 큐 쓰리는 7 배, 큐 나인은 3 배."

SOUND EFFECTS: Soft chime for "5.67×". Sequential ticks as heatmap cells fill.

MUSIC: Very subtle ambient pad.
```

---

#### Segment 3D · 1:28–1:36 — hero "94.9%" plan 회복 + 4 case 매트릭스 + 비대칭

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. Center top: A massive bold number "94.9%" in cyan, with a smaller subscript "결합 13종 평균 정답 plan 회복 (148/156)". Below the number, a small 2x2 confusion-style matrix with four cells:
Top-left (cyan, TP): "TP · 90" with caption "둘 다 정답"
Top-right (light red, FN): "FN · 1" with caption "결합만 망친 (Q3 sparse_rp 1건)"
Bottom-left (cyan-highlighted, FP): "FP · 58 ★" with caption "결합이 회복한 cell"
Bottom-right (gray, TN): "TN · 7" with caption "둘 다 오답"
The FP cell glows brightest, highlighted with a thin cyan border. Below the matrix: a clear short insight: "결합 회복률 89.2% (58/65) vs 망친 비율 1.1% (1/91). 비대칭 우위."

CAMERA: Static framing. The 4 matrix cells reveal in sequence — TP first, then FN, then the highlighted FP, then TN.

LIGHTING: Soft even white background.

MOOD: Structural advantage — the asymmetric win.

KOREAN AUDIO NARRATION (calm academic male voice): "결합 13종이 정답 plan 을 94.9 퍼센트 회복합니다. 베이스라인이 놓친 plan 의 89.2 퍼센트를 결합이 살리고, 베이스라인이 잡은 plan 의 1.1 퍼센트만 망칩니다. 비대칭 우위입니다."

SOUND EFFECTS: A confirmation chime for "94.9%", 4 distinct chimes for each matrix cell, with the brightest chime on the FP cell.

MUSIC: Very subtle ambient pad.
```

---

### Act IV — 결론·팀

#### Segment 4A · 1:36–1:44 — 본 연구 기여 4

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. In the center, a horizontal arrangement of 4 small academic-style cards, each with a small icon and a Korean label below it:
Card 1: A small "fork-arrow" icon → label "메커니즘 분리"
Card 2: A small "balance-scale" icon → label "음성 대조군"
Card 3: A small "stop-sign" icon → label "구조적 한계 규명"
Card 4: A small "gear-fast" icon → label "엔지니어링 5.67× 가속"
Each card reveals in sequence from left to right. Below the cards, a centered emphasized text: "negative + methodological result · 통제 실험 설계 자체가 contribution".

CAMERA: Static framing. Cards reveal one by one.

LIGHTING: Soft even white background.

MOOD: Closing summary — what we contributed.

KOREAN AUDIO NARRATION (calm academic male voice): "본 연구의 기여 네 가지. 메커니즘 분리, 음성 대조군, 구조적 한계 규명, 엔지니어링 가속. 통제 실험 설계 자체가 핵심 기여입니다."

SOUND EFFECTS: 4 soft "appear" chimes — one per card.

MUSIC: Very subtle ambient pad.
```

---

#### Segment 4B · 1:44–1:52 — honest limitation 정직 보고

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. Top center: A small header "honest limitation · 정직하게 남기는 한계". Below, a vertical list of 4 short Korean bullet points, each with a small gray bullet marker:
"• 다중 벡터 864 차원 군집화 파탄 — 2 건 이상치 제외"
"• method 명칭 정직성 — 8 method PCA alias 정정"
"• 통계 검정 floor p = 1/1024 — 효과크기로 판단"
"• 엔진 latency 동등 86.9% small effect — 구조적 한계"
Each bullet point fades in one by one. Below the list: "학술적 정직성 자체가 본 연구의 contribution 가운데 하나."

CAMERA: Static framing. Bullets reveal sequentially.

LIGHTING: Soft even white background.

MOOD: Honest, transparent — no over-claiming.

KOREAN AUDIO NARRATION (calm academic male voice): "본 연구의 한계도 정직하게 남깁니다. 다중 벡터 군집화 파탄, method 명칭 정직성, 통계 검정 바닥값, 엔진 latency 의 구조적 한계."

SOUND EFFECTS: 4 small ticks as bullets appear.

MUSIC: Very subtle ambient pad.
```

---

#### Segment 4C · 1:52–2:00 — 속도는벡터 팀 + 지도진

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. Top center: A large bold team name "속도는벡터" in navy color. Below the team name: A horizontal line of 4 small abstract circular avatars in light gray, each labeled in small text: "박세은 · 강재현 · 조현빈 · 이동욱". Below the team row, a smaller second row with 3 smaller circular avatars and labels: "박광현 교수님 · 임채림 박사 · 박성원 멘토". Below the avatars, a footer line: "연세대학교 BDAI 연구실 · 26-1 인공지능종합설계 캡스톤 디자인".

CAMERA: Static framing. Team name reveals first, then team avatars, then mentors.

LIGHTING: Soft even white background.

MOOD: Warm team reveal.

KOREAN AUDIO NARRATION (calm academic male voice): "속도는벡터 팀. 박세은, 강재현, 조현빈, 이동욱. 지도해 주신 박광현 교수님, 임채림 박사님, 박성원 멘토님."

SOUND EFFECTS: A warm confirmation chime when the team name appears.

MUSIC: Very subtle ambient pad with a slight warm resolution.
```

---

#### Segment 4D · 2:00–2:08 — 감사합니다 + 마무리

```text
8-second clean academic explainer animation, 1920x1080, white background.

VISUAL: A clean white background. Center: A large bold text in Korean: "감사합니다." Below it, a smaller text: "속도는벡터 · 연세대학교 BDAI 연구실". Below that, a small URL placeholder text "QR · YouTube" (this will be where the QR code overlay points to). The text reveals with a smooth fade-in. The video gently fades to a clean white at the very end.

CAMERA: Static framing. Smooth fade in for the closing text, slow fade out at the very end.

LIGHTING: Soft even white background.

MOOD: Warm, calm closing.

KOREAN AUDIO NARRATION (calm academic male voice, warm tone): "감사합니다."

SOUND EFFECTS: A warm closing chime, then ambient silence.

MUSIC: Very subtle ambient pad resolves to silence at the end.
```

---

## 3. 합성 workflow

### 3.1 Flow 진행 (Veo 3.1 Quality)

1. https://labs.google/fx/ko/tools/flow → 기존 프로젝트 "속도는벡터 캡스톤 소개영상" 진입
2. 우측 chat 입력창에 위 §2 의 Segment 1A → 4D prompt 16 개 순차 복붙
3. 각 prompt 당 약 60-120s generation (Veo 3.1 Quality)
4. 각 segment 출력 mp4 확인 + 다운로드
5. **기존 cinematic 1A·1B·1C 영상은 무시** (Flow 의 동영상 라이브러리에서 자동 삭제 또는 무시)

### 3.2 합성

**옵션 A: Flow 자체 Storyboard 모드 (추천)**
- 좌측 "장면" tab → 새 storyboard → Act 1A-4D 순서대로 16 segment 배치
- segment 간 transition = **fade through white 0.2s** (clean academic 톤)
- Export → 1080p mp4 (128초)

**옵션 B: DaVinci Resolve**
- 16 mp4 import → timeline 순서 배치
- transition Cross Dissolve 0.2s
- (선택) 자막 burn-in SRT 추가 — Apple SD Gothic Neo 한국어 자막
- Deliver → YouTube 1080p preset

### 3.3 자막 burn-in 후처리 (Path A carry)

영상 안 한국어 자막 없음 (Veo 한글 깨짐 회피). 합성 단계에서 SRT 별도 추가:
- 각 segment 의 KOREAN AUDIO NARRATION 텍스트 = 자막 텍스트
- timing = segment 시작·종료 (8초 단위)
- 폰트 Apple SD Gothic Neo, 흰 텍스트 + navy `#1E3A5F` 그림자, 화면 하단 중앙

### 3.4 YouTube + QR + 포스터

1. YouTube Unlisted 업로드 (제목·설명 carry 메모)
2. URL → qr-code-generator.com PNG (500×500)
3. 포스터 우측 footer QR placeholder 갱신 → PDF re-export → LearnUs 5/28 12:00 마감 제출

---

## 4. ref 영상 frame 분석 carry (시각 디테일 참고)

| Frame | 시간 | 본 영상 매핑 | 핵심 시각 |
|:--:|:--:|:--:|---|
| 1 | 0–4s | Segment 1A | VECTOR RANGE QUERY code + "이 쿼리는 몇 행을 반환할까?" |
| 2 | 4–8s | Segment 1B | 도트 매트릭스 + "7,599 행" GROUND TRUTH |
| 3 | 8–12s | Segment 1C 좌·우 split | "≈ 33 행" coral vs "= 7,581 행" cyan |
| 4 | 12–16s | Segment 1C plan tree | plan tree 비교 (Hash Join vs Index+NL) |
| 5 | 16–20s | Segment 1D 실행 시작 | CPU·MEM·ELAPSED 0 ms |
| 6 | 20–24s | Segment 1D 진행 중 | 좌 3,828 ms 진행 / 우 1,000 ms 완료 |
| 7 | 24–28s | Segment 1D 완료 | 좌 7,242 ms 완료 / 우 1,000 ms 완료 |
| 8 | 28–32s | Segment 1D hero | "7.24× 격차" + "추정 1건 → plan 1개 → 자원 7배" |

---

## 5. 핵심 정량 수치 (Veo prompt 안 직접 사용)

| 위치 | 수치 | 의미 |
|---|---|---|
| Segment 1B | **7,599 행** | 한 cell ground truth |
| Segment 1C | **33 vs 7,581 행** | planner default vs oracle |
| Segment 1D | **7,242 ms vs 1,000 ms · 7.24×** | 한 cell latency 격차 (ref 영상 동일) |
| Segment 2D | **1,508 cell** | 5 데이터셋 × 5 조작변인 × 13 method |
| Segment 3A | **89.1%** | 1,344/1,508 cell better (paired Δ% 중앙값 −4.38%) |
| Segment 3B | **35.2%** | 단독 대체 better (음성 대조군) |
| Segment 3C | **5.67×** | 12 cell 평균 엔진 가속 |
| Segment 3D | **94.9%** · **89.2%** · **1.1%** | plan 회복 (148/156) · 회복률 · 망친 비율 |

---

## 6. 환각 회피 룰 (carry · 변경 X)

- 코드명 노출 금지 (B1·CaseA·CaseB·oracle·baseline)
- 한국어 라벨 통일 (기본 엔진·베이스라인·단독 대체·결합·정답)
- 영상 안 자막 X (Veo 한글 깨짐 회피 · Path A 후처리 SRT)
- ref 영상 톤 carry — 흰 배경 + coral/cyan split + 도트 매트릭스 + plan tree + CPU/MEM meter

---

*작성 2026-05-27 14:46 KST · 5/28 12:00 LearnUs 영상·포스터 마감 약 21 시간 남음 · 16 segment explainer animation 2:08 · ref 영상 (`무제.mp4` 31.8s) base + Act 2·3·4 확장 · 사용자 명시 (공상학적 X · 실제 알고리즘 동작 explainer animation · 발표 슬라이드 첨부 영상 느낌).*
