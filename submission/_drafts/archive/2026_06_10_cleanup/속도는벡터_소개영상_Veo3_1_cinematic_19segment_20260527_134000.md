# 속도는벡터 · 소개영상 cinematic short film — Veo 3.1 19 segment 정본

> 26-1 인공지능종합설계 · 캡스톤 디자인 · 연세대학교 BDAI 연구실
>
> 작성 2026-05-27 13:40 KST · 5/28 12:00 LearnUs 포스터·영상 마감 (약 22 시간 남음)
>
> ★ **본 영상은 슬라이드 transition 방식이 아닌 cinematic 영상 흐름** — 사용자 명시 5/27 13:30 KST ("슬라이드 넘기는 방식 말고 영상 자체로 흐름 이어갈 수 있게 제미나이나 veo로 그렇게 제작 못하나? 그냥 슬라이드 건너뛰는 식 말고. 전체적인 흐름이나 슬라이드 내용 가지고서 새롭게 제작한다는 느낌으로"). Gemini Veo 3.1 (Ultra) 만 적극 활용, native audio 포함.

---

## 0. 영상 사양

| 항목 | 값 |
|---|---|
| 총 길이 | **2:32 (152 초)** |
| Segment | **19 개 × 8 초** (Veo 3.1 segment 한계 8 초) |
| 해상도 | 1920 × 1080 (16:9 가로, 1080p) |
| 프레임 | 24 fps cinematic |
| 오디오 | **Veo 3.1 native audio** — 한국어 narration + 효과음 + soft cinematic music |
| 자막 | 한국어 burn-in (Apple SD Gothic Neo, 흰 텍스트 + navy 그림자, 화면 하단) |
| 비주얼 톤 | navy `#1E3A5F` + 청록 그라데이션 (`#2E8B8B` → `#1E3A5F`) + 흰 배경 base · cinematic film noir × clean academic |
| 톤 | 학술 발표 · 정중 · 차분 · cinematic |
| 마감 | 5/28 12:00 KST LearnUs 포스터·영상 마감 |

---

## 1. cinematic 흐름 구조 — 6 막 19 segment

각 막은 narrative arc 의 한 단계이며, 막 안 segment 는 cinematic flow 로 자연스럽게 이어진다.

| 막 | 시간 | segment 수 | 핵심 메시지 | hero shot |
|:--:|---|:--:|---|---|
| **I. 도입 — VAQ 시나리오** | 0:00–0:24 | 3 | 벡터 + 분석 한 SQL · 기존 시스템 한계 (고정 비율 오류) | 분석가 SQL 작성 + 33.3·50·100 오류 |
| **II. 본 연구 위치** | 0:24–0:48 | 3 | Exqutor §V-B 표본 선택 단계 한 곳만 개입 | §V-B 베르누이 표본 5 단계 도식 |
| **III. 통제 실험 설계** | 0:48–1:12 | 3 | 베이스라인·단독 대체·결합 3 mode · 1,508 cell matched | 4 갈래 도식 + 측정 평면 |
| **IV. 89.1% 우위 + 메커니즘 규명** | 1:12–1:44 | 4 | 결합 89.1% 우위 + 단독 대체 35.2% 음성 → 결합 형태 효과 | hero "89.1%" reveal |
| **V. 엔진 적용 — 5.67× + 94.9% 회복** | 1:44–2:16 | 4 | pgvector 패치 5.67× 가속 + plan 회복 94.9% · 추정 ↑ ≠ latency ↑ | hero "5.67×" + "94.9%" |
| **VI. 기여 + 팀** | 2:16–2:32 | 2 | 본 연구 기여 4 + 속도는벡터 팀 5 인 + 지도진 3 인 | 팀 + 연세대 BDAI 로고 |

**총 19 segment × 8 초 = 152 초 = 2:32** (Veo 3.1 8 초 segment × 19 합성)

---

## 2. Veo 3.1 prompt — 19 segment (Gemini Veo 3.1 직접 복붙)

각 prompt 는 Veo 3.1 (Ultra) 에 그대로 복붙 가능한 형식. 영어 prompt + Korean narration·subtitle text (Veo 3.1 한국어 audio·자막 렌더링 지원).

---

### Segment 1A · 0:00–0:08 — 분석가 화면 (VAQ SQL 작성)

```text
8-second cinematic clip, 1920x1080 24fps, photorealistic, shallow depth of field.

VISUAL: Over-the-shoulder shot of a data analyst at a clean modern desk, illuminated by soft afternoon light from a side window. Two monitors visible. Left monitor displays a SQL editor with syntax-highlighted code being typed character by character. The SQL combines a vector similarity search WHERE clause (e.g., `WHERE image_emb <-> query_emb < 0.3`) with a standard analytical aggregate (e.g., `SELECT SUM(revenue) GROUP BY region`). Right monitor shows a dashboard with vector visualization in the background.

CAMERA: Slow dolly-in from over-the-shoulder to over-the-keyboard angle, focusing on the SQL code as it appears. Subtle parallax.

LIGHTING: Soft natural daylight + warm desk lamp. Navy and cyan color tones in the monitor glow.

MOOD: Cinematic, focused, slightly enigmatic — the moment a complex question is posed.

KOREAN AUDIO NARRATION (calm academic male voice, slow pace): "벡터 증강 분석 쿼리. 이미지 유사도 검색과 매출 집계 분석을 한 SQL 안에 결합한 새로운 워크로드입니다."

KOREAN SUBTITLE (burn-in, bottom, Apple SD Gothic Neo, white text with navy shadow): "벡터 증강 분석 쿼리 — 유사도 검색 + 분석을 한 SQL 안에"

SOUND EFFECTS: Soft keyboard typing, distant ambient room tone.

MUSIC: Soft cinematic ambient pad (no melody), low tempo, BPM 60, in C minor — building a sense of inquiry.
```

---

### Segment 1B · 0:08–0:16 — SQL 벡터 술어 + 검색 결과 카드

```text
8-second cinematic clip, 1920x1080 24fps, photorealistic, macro detail.

VISUAL: Close-up macro shot of the SQL editor. The vector similarity predicate `<->` operator glows cyan, highlighted. Above it, three small floating cards materialize one by one — each card shows a thumbnail (handbag, sneaker, watch) with a similarity score (0.12, 0.18, 0.27). The cards orbit the WHERE clause gently.

CAMERA: Push-in from medium shot to extreme close-up on the `<->` operator. Slight handheld shake to feel organic.

LIGHTING: Cool cyan glow from the monitor + warm desk lamp from off-screen left.

MOOD: Reveal of the vector similarity mechanism — fascination.

KOREAN AUDIO NARRATION: "벡터 술어는 매우 선택적이지만, 데이터베이스는 이 선택도를 정확히 모릅니다."

KOREAN SUBTITLE (burn-in, bottom): "벡터 술어 — 매우 선택적이지만 카디널리티 추정 어려움"

SOUND EFFECTS: Subtle UI chime as each thumbnail card appears, low hum.

MUSIC: Cinematic ambient continues, slight rise in suspense.
```

---

### Segment 1C · 0:16–0:24 — 33.3% · 50% · 100% 고정 비율 오류

```text
8-second cinematic clip, 1920x1080 24fps, abstract data visualization with photorealistic elements.

VISUAL: Split-screen showing three database systems labeled "pgvector · 33.3%", "VBASE · 50%", "DuckDB · 100%". Each panel shows a stylized PostgreSQL-like plan tree. A red error indicator pulses on each panel, showing that the cardinality estimate is off (actual: 0.1%, estimate: 33.3% / 50% / 100%). The bad estimates cause the plan trees to twist into suboptimal shapes (showing a wrong Hash Join instead of a good Nested Loop).

CAMERA: Wide static shot of the three panels, slow zoom into the center "33.3%" indicator.

LIGHTING: Cool blue + red alarm tones, slight vignette.

MOOD: Problem statement — the existing systems get it wrong.

KOREAN AUDIO NARRATION: "기존 시스템은 고정 비율로 카디널리티를 추정합니다. 잘못된 추정은 잘못된 실행 계획을 만듭니다."

KOREAN SUBTITLE (burn-in, bottom): "기존 시스템 한계 — 고정 비율 카디널리티 → 잘못된 plan"

SOUND EFFECTS: Three soft "error" chimes (one per panel), low rumble building tension.

MUSIC: Cinematic ambient deepens, slight discordant note signaling the problem.
```

---

### Segment 2A · 0:24–0:32 — Exqutor 논문 표지 + ECQO 흐름

```text
8-second cinematic clip, 1920x1080 24fps, photorealistic paper texture + UI overlay.

VISUAL: Open academic paper page on screen, title "Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries" highlighted. The page transitions into an isometric diagram: a vector index (HNSW graph, depicted as a 3D network of nodes) with a range query sweeping through it, labeled "ECQO — 정확 카디널리티 (1-2ms)". The diagram is rendered in navy + cyan.

CAMERA: Slow tilt-down from the paper title to the ECQO diagram. Subtle zoom on the HNSW graph as it pulses.

LIGHTING: Paper-white background + cyan glow from the index visualization.

MOOD: Academic, foundational — the paper that opened this work.

KOREAN AUDIO NARRATION: "Exqutor 논문은 두 메커니즘을 제안합니다. 인덱스가 있을 때는 정확 카디널리티 ECQO 를 1 밀리초 안에."

KOREAN SUBTITLE (burn-in, bottom): "Exqutor — ECQO 정확 카디널리티 (인덱스 있음)"

SOUND EFFECTS: Subtle paper flip sound, soft UI ping when ECQO diagram appears.

MUSIC: Cinematic ambient transitions to a slightly more hopeful tone.
```

---

### Segment 2B · 0:32–0:40 — Adaptive Sampling §V-B 베르누이 표본 5 단계

```text
8-second cinematic clip, 1920x1080 24fps, abstract data visualization.

VISUAL: A horizontal flow diagram of 5 stages, each represented by a navy circle with a cyan label: "Stage 1 — Bernoulli sample (N=385)", "Stage 2 — Q-error update", "Stage 3 — Momentum δ", "Stage 4 — Sample size adjust", "Stage 5 — Repeat". The Bernoulli sample circle (Stage 1) glows brighter than others — it is the focal point. Small particles (dots) flow through the pipeline left to right, depicting the 385 sampled vectors moving through the loop.

CAMERA: Slow horizontal pan left to right, following the data flow. Slight push-in on Stage 1 at the end.

LIGHTING: Cool navy + cyan, slight bloom on the bright Stage 1 circle.

MOOD: Mechanical, precise — the existing algorithm.

KOREAN AUDIO NARRATION: "인덱스가 없을 때는 적응적 표본 추출. 무작위 베르누이로 표본 385개를 뽑고 모멘텀으로 크기를 조정합니다."

KOREAN SUBTITLE (burn-in, bottom): "Adaptive Sampling §V-B — 베르누이 표본 추출 5 단계"

SOUND EFFECTS: Soft mechanical ticks as each stage activates, particle whoosh.

MUSIC: Cinematic ambient with subtle clockwork rhythm.
```

---

### Segment 2C · 0:40–0:48 — 표본 선택 단계 zoom in (본 연구 개입 지점)

```text
8-second cinematic clip, 1920x1080 24fps, dramatic zoom.

VISUAL: The 5-stage pipeline from Segment 2B is shown in the background, but the camera dramatically zooms into Stage 1 (Bernoulli sample) until it fills the screen. The Bernoulli sample circle expands and reveals two options inside: on the left, "무작위 베르누이 (논문 그대로)"; on the right, "분포 인지 stratification (본 연구)". A glowing arrow points from the original to the right alternative.

CAMERA: Dramatic dolly-in from wide to extreme close-up on Stage 1.

LIGHTING: Spotlight effect on Stage 1, rest of the pipeline darkens.

MOOD: Pivotal moment — this is the single intervention.

KOREAN AUDIO NARRATION: "본 연구는 이 표본 선택 단계 한 곳만 분포 인지 층화 표본 추출로 바꿉니다. 나머지는 모두 논문 그대로."

KOREAN SUBTITLE (burn-in, bottom): "본 연구의 단일 개입 — 표본 선택 단계 한 곳만"

SOUND EFFECTS: Whoosh of zoom, subtle "click" as the alternative is highlighted.

MUSIC: Cinematic ambient rises, anticipation building.
```

---

### Segment 3A · 0:48–0:56 — 4 갈래 도식 (4 mode)

```text
8-second cinematic clip, 1920x1080 24fps, clean motion graphics.

VISUAL: A central node splits into 4 paths radiating outward, each labeled in Korean:
- 상단: "기본 엔진 — 고정 비율 33.3%"
- 우측: "베이스라인 — 베르누이 표본 (논문 그대로)"
- 하단: "정답 — 실제 카디널리티"
- 좌측: "결합 — 베이스라인 + 분포 인지 평균"
Each path is colored: 기본 엔진 (회색), 베이스라인 (코랄), 정답 (그린), 결합 (청록). The paths animate outward from the central node.

CAMERA: Slow zoom out from the central node to reveal all 4 paths.

LIGHTING: Clean white background, each path glowing in its color.

MOOD: Structural reveal — the experimental design.

KOREAN AUDIO NARRATION: "한 측정 안에서 네 방식을 동시에 산출합니다. 기본 엔진, 베이스라인, 정답, 결합."

KOREAN SUBTITLE (burn-in, bottom): "4 mode matched 측정 — 기본 엔진·베이스라인·정답·결합"

SOUND EFFECTS: Subtle "whoosh" as each path appears, soft chime when all 4 are present.

MUSIC: Clean cinematic motif, slight ascending melody.
```

---

### Segment 3B · 0:56–1:04 — 1,508 cell 측정 평면

```text
8-second cinematic clip, 1920x1080 24fps, data visualization.

VISUAL: A 3D isometric grid emerges: 5 datasets (DEEP·SIFT·SSN·DEEP+SIFT·DEEP+WIKI) on the X axis, 5 manipulation variables (A1 baseline·A2 query·A3 K·A4 selectivity·A5 scale) on the Y axis, 13 methods (strong paradigm representatives) on the Z axis. The grid is filled with small cubes (1,508 in total) each pulsing with cyan glow. A counter on the top right increments: "0 → 1,508 cell".

CAMERA: Orbit around the 3D grid, full 360° rotation slowed for cinematic effect.

LIGHTING: Cool cyan glow from the cubes, navy background.

MOOD: Scale and rigor of the measurement.

KOREAN AUDIO NARRATION: "5 데이터셋, 5 조작변인, 13 method 의 1,508 cell 전수에서 측정했습니다."

KOREAN SUBTITLE (burn-in, bottom): "1,508 cell 전수 측정 — 5 데이터셋 × 5 조작변인 × 13 method"

SOUND EFFECTS: Soft data "tick" as the counter increments, ambient hum.

MUSIC: Cinematic ambient with subtle granular synth texture.
```

---

### Segment 3C · 1:04–1:12 — matched 측정 강조 (3-way 동시 산출)

```text
8-second cinematic clip, 1920x1080 24fps, data visualization.

VISUAL: A single cell from the grid (from Segment 3B) is selected and zoomed in. Three measurements run in parallel from the same cell — labeled "베이스라인", "단독 대체", "결합". Three Q-error values appear simultaneously below: "B1: 1.944", "CaseA: 1.984", "CaseB: 1.477". The three values are linked by a glowing "matched" connector.

CAMERA: Push-in on the single cell, then split-screen to show 3 parallel measurements.

LIGHTING: Spotlight on the 3 measurements, rest of the grid dims.

MOOD: Precision — controlled experiment.

KOREAN AUDIO NARRATION: "한 셀에서 세 mode 가 동시에 산출됩니다. 외생 요소가 통제된 짝지은 측정입니다."

KOREAN SUBTITLE (burn-in, bottom): "3-way matched 측정 — 외생 요소 통제"

SOUND EFFECTS: Three "snap" sounds as the 3 values lock in, soft confirmation chime.

MUSIC: Cinematic ambient holds steady, anticipation.
```

---

### Segment 4A · 1:12–1:20 — hero "89.1%" reveal

```text
8-second cinematic clip, 1920x1080 24fps, dramatic typography reveal.

VISUAL: Black-to-navy gradient background. A massive number "89.1%" materializes from particle assembly in the center of the screen, navy → cyan gradient typography. Below it, smaller text in Korean: "1,344 / 1,508 cell — 결합이 베이스라인보다 정확". Subtle particles continue to swirl around the number.

CAMERA: Slow dolly-in toward the giant number, slight upward tilt for grandeur.

LIGHTING: Particle bloom, navy + cyan tones, central spotlight on the number.

MOOD: Dramatic result reveal — the headline finding.

KOREAN AUDIO NARRATION: "결합 방식이 베이스라인을 1,344 셀에서 이깁니다. 우위 비율은 89.1 퍼센트."

KOREAN SUBTITLE (burn-in, bottom): "결합 89.1% 우위 — 1,344 / 1,508 cell"

SOUND EFFECTS: Particle assembly "shimmer", subtle bass impact when "89.1%" locks in.

MUSIC: Cinematic crescendo — the climax of the first finding.
```

---

### Segment 4B · 1:20–1:28 — paired Δ% 중앙값 −4.38% 분포

```text
8-second cinematic clip, 1920x1080 24fps, data visualization.

VISUAL: A histogram of paired Δ% values (1,508 measurements) materializes on screen. The distribution is centered at -4.38%, with a vertical median line glowing cyan. Below the histogram, large text "중앙값 Δ% = -4.38%". The histogram bars rise in sequence from left to right.

CAMERA: Slow zoom out from the median line to show the full distribution.

LIGHTING: Clean white background, cyan histogram bars, navy axes.

MOOD: Statistical clarity — the distribution backs up the finding.

KOREAN AUDIO NARRATION: "추정 오차 중앙값은 결합이 4.38 퍼센트 더 작습니다. 좌측 꼬리로 치우친 분포입니다."

KOREAN SUBTITLE (burn-in, bottom): "paired Δ% 중앙값 −4.38% — 좌측 꼬리 분포"

SOUND EFFECTS: Subtle "tick" for each bar rising, then a soft chime when the median line appears.

MUSIC: Cinematic ambient resumes after the crescendo.
```

---

### Segment 4C · 1:28–1:36 — 단독 대체 CaseA 35.2% 음성 대조

```text
8-second cinematic clip, 1920x1080 24fps, comparative visualization.

VISUAL: Split-screen comparison. Left side: a coin flip animation (random/Bernoulli) showing "35.2%" — labeled "단독 대체 (CaseA)" in coral red. Right side: the "89.1%" from Segment 4A, labeled "결합 (CaseB)" in cyan. The contrast is stark — coin flip vs decisive win.

CAMERA: Static wide shot showing both sides, slow inward push.

LIGHTING: Coral red on the left side, cyan on the right, sharp visual divide.

MOOD: Contrast — the negative control reveals the truth.

KOREAN AUDIO NARRATION: "그런데 단독 대체 방식은 35.2 퍼센트에서만 이깁니다. 동전 던지기 수준입니다."

KOREAN SUBTITLE (burn-in, bottom): "단독 대체 35.2% — 음성 대조군 (분포 인지 단독으로는 효과 X)"

SOUND EFFECTS: Coin flip clinks (left side), confirmation chime (right side).

MUSIC: Cinematic ambient with slight tension — the twist.
```

---

### Segment 4D · 1:36–1:44 — 메커니즘 결론 (앙상블 효과)

```text
8-second cinematic clip, 1920x1080 24fps, conceptual visualization.

VISUAL: Two arrows merge into one — labeled "베이스라인 추정" + "method 추정" → "(b1 + method) / 2.0 평균". The merged arrow leads to a glowing center labeled "결합의 가치 = 두 독립 추정량 평균 효과 (앙상블)". Below: "분포 인지 효과 X · 결합 형태 자체의 가치".

CAMERA: Slow push-in on the merging arrows, then zoom to the final conclusion.

LIGHTING: Cyan glow on the merged arrow, navy background, subtle particle effects.

MOOD: Revelation — the mechanism is laid bare.

KOREAN AUDIO NARRATION: "89 퍼센트 우위의 메커니즘은 분포 인지 효과가 아니라, 두 독립 추정량을 평균한 일반 통계 효과입니다."

KOREAN SUBTITLE (burn-in, bottom): "메커니즘 = 분포 인지 X · 두 추정량 평균 효과 (앙상블)"

SOUND EFFECTS: Two soft "whoosh" sounds as arrows merge, confirmation chime at the end.

MUSIC: Cinematic ambient transitions to a slightly resolved tone — the answer is here.
```

---

### Segment 5A · 1:44–1:52 — pgvector 엔진 vector.c 패치

```text
8-second cinematic clip, 1920x1080 24fps, photorealistic with UI overlay.

VISUAL: A close-up of a code editor showing pgvector's `vector.c` source file. Specific lines highlighted in cyan: the `SeqScan` cardinality estimation function. An arrow points from the original line (`return DEFAULT_CARDINALITY * total_rows`) to a new injected line (`return GetGUC("vector.injected_card")`). The patch glows briefly to emphasize the modification.

CAMERA: Slow pan from left to right across the code, focusing on the patch.

LIGHTING: Monitor glow (cyan code on dark background), warm desk lamp from off-screen.

MOOD: Engineering precision — the actual code change.

KOREAN AUDIO NARRATION: "pgvector 의 vector.c 에 카디널리티 주입 경로를 패치했습니다. 결합 추정값을 엔진에 직접 주입합니다."

KOREAN SUBTITLE (burn-in, bottom): "pgvector vector.c 패치 — vector.injected_card GUC"

SOUND EFFECTS: Keyboard "click" as the patch line appears, subtle data hum.

MUSIC: Cinematic ambient with a slight technical, mechanical undertone.
```

---

### Segment 5B · 1:52–2:00 — hero "5.67×" + 12 cell 가속 매트릭스

```text
8-second cinematic clip, 1920x1080 24fps, dramatic typography + data visualization.

VISUAL: Black-to-navy gradient background. Massive "5.67×" materializes in center, navy → cyan gradient typography (matching Segment 4A's style). Below the number, a 3x4 heatmap grid (12 cells = Q3·Q9·Q10·Q12 × qid 0·1·2) shows speedup values from 2.93× to 7.40× in cyan gradient. Each cell pulses briefly.

CAMERA: Slow zoom in on "5.67×", then quick pan to the heatmap.

LIGHTING: Particle bloom on the number, cyan heatmap glow.

MOOD: Engineering triumph — the speedup is real.

KOREAN AUDIO NARRATION: "12 cell 평균 5.67 배 가속. Q3 는 7 배대, Q9 는 3 배대까지."

KOREAN SUBTITLE (burn-in, bottom): "엔진 가속 5.67× 평균 — 12 cell 전수 가속"

SOUND EFFECTS: Particle assembly + subtle bass impact for "5.67×", then 12 quick "ticks" for each heatmap cell.

MUSIC: Cinematic crescendo (smaller than 4A's) — the engineering win.
```

---

### Segment 5C · 2:00–2:08 — hero "94.9%" + 4 case 매트릭스

```text
8-second cinematic clip, 1920x1080 24fps, dramatic typography + data visualization.

VISUAL: "94.9%" materializes in cyan gradient (same style as previous heros). Below: a 2x2 confusion-style matrix labeled "B1 정답·CaseB 정답: TP 90 | B1 정답·CaseB 오답: FN 1 | B1 오답·CaseB 정답: FP 58 | B1 오답·CaseB 오답: TN 7". The FP 58 cell glows brightest — the asymmetric win.

CAMERA: Push-in on "94.9%", then dolly to the matrix, ending on FP 58.

LIGHTING: Cyan glow on the matrix, particularly bright on FP 58.

MOOD: Plan recovery — the structural advantage.

KOREAN AUDIO NARRATION: "결합은 정답 plan 을 94.9 퍼센트 회복합니다. 베이스라인이 놓친 plan 의 89.2 퍼센트를 결합이 살립니다."

KOREAN SUBTITLE (burn-in, bottom): "plan 회복 94.9% — 결합 회복률 89.2% · 망친 비율 1.1%"

SOUND EFFECTS: Particle assembly for "94.9%", 4 chimes for the 4 case cells.

MUSIC: Cinematic ambient with a confident, structural tone.
```

---

### Segment 5D · 2:08–2:16 — "추정 정확도 ↑ ≠ latency ↑" 비대칭 구조

```text
8-second cinematic clip, 1920x1080 24fps, conceptual visualization.

VISUAL: Two arrows side by side — left arrow labeled "추정 정확도" with an upward "↑" + value "94.9% plan 회복", right arrow labeled "latency" with a flat "→" + value "86.9% small effect". Between them, a large "≠" sign (cyan, glowing). Below: "엔진의 구조적 한계 — 정확도가 latency 로 변환되지 않음".

CAMERA: Slow zoom out from "≠" to reveal both arrows.

LIGHTING: Cool blue-navy tones, cyan accents on the arrows.

MOOD: Structural finding — the honest limitation.

KOREAN AUDIO NARRATION: "다만 추정 정확도의 향상이 latency 의 차이로 변환되지 않습니다. 엔진의 구조적 한계입니다."

KOREAN SUBTITLE (burn-in, bottom): "추정 정확도 ↑ ≠ latency ↑ — 엔진 구조적 한계"

SOUND EFFECTS: Two "whoosh" sounds for each arrow, a soft "ding" for the "≠".

MUSIC: Cinematic ambient with a slight melancholic undertone — honest about the limit.
```

---

### Segment 6A · 2:16–2:24 — 본 연구 기여 4

```text
8-second cinematic clip, 1920x1080 24fps, motion graphics.

VISUAL: 4 cards arrange in a 2x2 grid, each materializing in sequence. Card titles in Korean:
- 좌상: "메커니즘 분리"
- 우상: "음성 대조군"
- 좌하: "구조적 한계 규명"
- 우하: "엔지니어링 5.67× 가속"
Each card has a small icon (analytical brain · scale · stop sign · gear). Cyan accents.

CAMERA: Slow zoom out from each card as it appears, ending with all 4 visible.

LIGHTING: Clean white background, cyan card borders.

MOOD: Closing summary — what we contributed.

KOREAN AUDIO NARRATION: "본 연구의 기여 네 가지. 메커니즘 분리, 음성 대조군, 구조적 한계 규명, 엔지니어링 가속."

KOREAN SUBTITLE (burn-in, bottom): "본 연구 기여 — 메커니즘·대조군·한계 규명·엔지니어링"

SOUND EFFECTS: 4 soft "appear" chimes as each card materializes.

MUSIC: Cinematic ambient with a confident, summarizing tone.
```

---

### Segment 6B · 2:24–2:32 — 팀 소개 + 마무리

```text
8-second cinematic clip, 1920x1080 24fps, motion graphics + photorealistic logo.

VISUAL: A horizontal lineup of 4 abstract avatar silhouettes labeled "박세은 · 강재현 · 조현빈 · 이동욱" (속도는벡터 팀). Below, 3 smaller silhouettes labeled "박광현 교수님 · 임채림 박사 · 박성원 멘토". At the top, "속도는벡터" team name in large navy typography. At the very bottom, "연세대학교 BDAI 연구실 · 26-1 인공지능종합설계 캡스톤 디자인".

CAMERA: Slow pull-back from the team name to reveal everyone, then gentle fade-to-navy.

LIGHTING: Clean white background, soft cyan glow on the team name.

MOOD: Warm closing — thanks and team identity.

KOREAN AUDIO NARRATION: "감사합니다. 속도는벡터 팀이었습니다."

KOREAN SUBTITLE (burn-in, bottom): "감사합니다 — 속도는벡터 · 연세대학교 BDAI 연구실"

SOUND EFFECTS: Subtle warm chime at "감사합니다", gentle fade-out tone.

MUSIC: Cinematic ambient resolves to a warm major chord, slow fade to silence.
```

---

## 3. 합성 workflow — Gemini Veo 3.1 (Ultra) · 19 segment

### 3.1 Gemini Veo 3.1 실행 단계

1. **Gemini Ultra 앱 접속** — https://gemini.google.com (Ultra 한도, AI Ultra 구독)
2. **Veo 3.1 model 선택** — 모델 선택 메뉴에서 Veo 3.1 (preview)
3. **각 segment prompt 순차 실행**:
   - 위 §2 의 prompt 19 개 각각을 Gemini Veo 3.1 에 복붙
   - 한 prompt 당 약 2-5 분 generation 시간 (Ultra 한도)
   - 출력: 8 초 mp4 (1080p, native audio 포함)
4. **각 segment mp4 다운로드** — 파일명 `segment_<N>_<scene>.mp4` 로 저장 (예: `segment_01_VAQ_analyst.mp4`)
5. **품질 검수** — 각 segment 의 (a) 비주얼 일관성 (navy + 청록 톤) (b) 한국어 narration 발음 정확성 (c) 한국어 자막 burn-in 가독성 확인. 미흡하면 prompt 미세 조정 후 재생성.

### 3.2 합성 단계 (Gemini Flow 우선, fallback DaVinci/Clipchamp)

**옵션 A: Gemini Flow (추천, Ultra 한도)**
1. Flow 에서 새 프로젝트 생성
2. 19 segment mp4 를 순서대로 업로드 → timeline 배치
3. segment 간 transition 효과 = **cross-dissolve 0.3-0.5 초** (cinematic 자연 흐름)
4. 전체 길이 152 초 확인
5. background music 통합 — 19 segment 의 native music 이 끊김 없이 이어지도록 audio crossfade 적용
6. Export → final.mp4 (1080p, H.264, AAC)

**옵션 B: DaVinci Resolve (무료, Mac/Windows)**
1. New Project → 1080p 24fps timeline
2. 19 segment mp4 import → Media Pool
3. Edit page 에서 순서대로 timeline 배치
4. Inspector > Cross Dissolve transition 0.3 초 적용 (segment 사이 18 개 transition)
5. Audio track 에 background music separate track 추가 (선택, 보조)
6. Color > navy/cyan 톤 일관성 보정 (Color Wheels 또는 LUT)
7. Deliver page > YouTube 1080p preset → final.mp4

**옵션 C: Clipchamp (Windows 무료, 간단)**
1. New Video → 16:9 1080p
2. 19 segment mp4 순서 import → timeline
3. 각 segment 사이 "Fade" transition 0.3 초
4. Export 1080p mp4

### 3.3 YouTube + QR + 포스터 통합

1. **YouTube Unlisted 업로드**:
   - 제목: "속도는벡터 — 캡스톤 종합설계 결과 (연세대학교 BDAI 연구실)"
   - 설명: "26-1 인공지능종합설계. 벡터 증강 분석 쿼리의 카디널리티 추정에서 단일 개입의 controlled verification. 결합 89.1% 우위·5.67× 가속·plan 회복 94.9% + 메커니즘 = 분포 인지 X · 앙상블 효과."
   - 카테고리: 교육
   - 공개 설정: **Unlisted (검색 X · URL 알면 시청 가능)**
2. **URL 회수** — `https://youtu.be/XXXXXXXX` 형식 (11 자 ID)
3. **QR 코드 생성**:
   ```bash
   python3 -c "import qrcode; img=qrcode.make('https://youtu.be/XXXXXXXX'); img.save('/tmp/yt_qr.png')"
   ```
   또는 https://qr-code-generator.com → URL 입력 → PNG 다운로드 (500×500 px 권장)
4. **포스터 우측 footer 갱신** — 포스터 PDF 의 QR placeholder 위치에 PNG 삽입 → PDF re-export

### 3.4 검증 체크리스트

- [ ] 19 segment 모두 생성 완료 (각 8 초)
- [ ] 합성 후 총 길이 152 초 (2:32 ± 5 초)
- [ ] 한국어 narration 19 segment 모두 발음 정확
- [ ] 한국어 자막 burn-in 19 segment 모두 표시
- [ ] navy + 청록 톤 일관성 (cross-segment color matching)
- [ ] segment 전환 cross-dissolve 자연스러움
- [ ] background music 끊김 없이 이어짐
- [ ] 해상도 1920×1080, 24fps
- [ ] 파일 크기 100MB 이하 (YouTube 권장)
- [ ] YouTube Unlisted 업로드 → URL 회수
- [ ] QR 코드 핸드폰 scan test (실제 영상 재생 확인)
- [ ] 포스터 QR placeholder 갱신 완료
- [ ] LearnUs 5/28 12:00 마감 전 영상 + 포스터 final 제출 완료

---

## 4. 환각 회피 룰 (carry · 5/24 작업물에서 동일)

- 코드명 노출 금지 (B1·CaseA·CaseB·oracle·baseline) — 한국어 라벨 (기본 엔진·베이스라인·정답·결합) 만
- "영역" 필러 토큰 금지 — "구간"·"단계"·"방식" 의미 있는 명사로
- 수식 노출 금지 — `est_final = (est_b1 + est_method) / 2.0` 식 X · "두 추정값을 평균" 한국어로
- 영문 메타 라벨 금지 (Phase 2·INPUT·OUTPUT·STEP·PANEL) — "엔진 적용 검증" 한국어로
- 이분법 강조 금지 — 4 갈래 (기본 엔진·베이스라인·정답·결합) 흐름 명시
- 별표 ★ 금지 — 강조는 typography·color
- 텍스트 잘림·단어 중간 줄바꿈 금지
- design system 유지 — navy `#1E3A5F` + 청록 그라데이션 + Apple SD Gothic Neo (한글) + Inter (숫자) + 흰 배경 base

---

## 5. 영상 핵심 정량 수치 (Veo prompt 안 직접 사용)

| 위치 | 수치 | 의미 |
|---|---|---|
| Segment 4A hero | **89.1%** | 결합 vs 베이스라인 better 비율 (1,344 / 1,508) |
| Segment 4B | **−4.38%** | paired Δ% 중앙값 |
| Segment 4C | **35.2%** | 단독 대체 CaseA better 비율 (음성 대조군) |
| Segment 5B hero | **5.67×** | 12 cell 평균 엔진 가속 (oracle vs baseline) |
| Segment 5C hero | **94.9%** | 결합 13종 평균 plan 회복 (148/156) |
| Segment 5C 보조 | **89.2%** | 결합 회복률 (B1 오답 cell 중 결합 정답 = 58/65) |
| Segment 5C 보조 | **1.1%** | 결합 망친 비율 (B1 정답 cell 중 결합 오답 = 1/91) |
| Segment 5D | **86.9% small effect · 13/168 = 7.7% 유의** | latency 동등성 |

---

## 6. Q&A 신본 §C-1·E-1·H-3 carry 반영 위치

- Segment 4D 메커니즘 결론 = Q&A §C-1 "분포 인지 X · 두 독립 추정량 평균 효과 (앙상블)" 직접 인용
- Segment 5D 비대칭 구조 = Q&A §E-1 "추정 정확도 ↑ ≠ latency ↑ · 86.9% small effect 분포" 인용
- Segment 6A 본 연구 기여 4 = Q&A §H-3 "negative result 의 학술적 가치" 의 4 측면 압축 (메커니즘 분리·음성 대조·구조적 한계·엔지니어링)

---

*작성 2026-05-27 13:40 KST · 5/28 12:00 LearnUs 영상 마감 약 22 시간 남음 · 19 segment cinematic short film 2:32 · Gemini Veo 3.1 (Ultra) native audio · 슬라이드 transition 폐기, 영상 컨텐츠 자체 흐름.*
