# Claude.ai Artifact 생성 prompt template

> **사용자가 claude.ai 에 직접 들어가서 본 prompt 그대로 붙여넣기 → 결과물 발표 prototype 으로 활용.**
> Claude Code 환경의 chrome MCP 는 Cloudflare 통과 X — 사용자 수동 진행.

---

## Prompt 1 — Interactive React Slide Deck (5/27 발표용)

```
캡스톤 연구 발표용 interactive React slide deck artifact 만들어줘.

연구 제목: "속도는벡터 — Vector-augmented Analytical Query 의 분포 인지 sampling 가치 정량 연구"

요구사항:
- React + Tailwind CSS + shadcn/ui 사용
- 12-14 슬라이드 (좌우 화살표 키 + 클릭 navigation)
- 각 슬라이드의 핵심 데이터는 다음 markdown 참고

[여기에 _internal/팀원이해도_RQ_직관설명_20260507.md 내용 + RQ1_RQ2_RQ3_종합_master.md 통계 결과 표 붙여넣기]

핵심 contribution 3종 (각각 한 슬라이드):
1. Hilbert Curve = learning-free 1순위 (mechanism: inverse Manhattan = 1.000 vs Z-order 1.992)
2. MiniBatch K-means = production-ready (N=1M 에서 1,189× speedup, partial_fit ARI 1.000)
3. Cluster 분할 가치 negative control (Distance-Shell/IS d=+0.5~+0.7 hurt-medium)

각 슬라이드 요소:
- 큰 제목
- 핵심 수치 (highlight)
- 보조 설명
- 최소한의 시각화 (chart 가능하면 recharts)

스타일:
- 연구실 발표 분위기 (블루/그레이 톤, sans-serif Korean font 우선)
- 전환 효과 부드럽게
- 다크 모드 토글 옵션

발표 시간 12-15분. 각 슬라이드 30~60초 분량.
```

---

## Prompt 2 — RQ1/RQ2/RQ3 Visualization Dashboard

```
캡스톤 연구 결과 dashboard React artifact 만들어줘.

목적: 팀원들이 RQ1/RQ2/RQ3 결과를 빠르게 이해하도록 interactive visualization.

기능:
1. RQ1 단조성 visualizer
   - x: selectivity (log scale, 0.01~0.50)
   - y: KM20 - BERN diff% (음수 = improve)
   - DEEP / SIFT / 8M 3 line plot
   - 각 sel 의 5-seed scatter + mean line
   - per-seed Spearman ρ + 95% CI 표시 (DEEP-KM20: ρ=-0.680, CI [-0.800, -0.440])

2. RQ2 5-mode allocation comparison
   - Heatmap (mode × sel) 의 diff% (vs BERN)
   - DEEP/SIFT 토글
   - Anti-Neyman 의 좁은 sel hurt 강조 (s=0.01: DEEP +5.21%, SIFT +9.49%)

3. RQ3 13-method comparison
   - Forest plot of Cohen's d (method 별 평균 ± min/max range)
   - CI 0 제외 method highlight (4/10 cells robust 등)
   - Best 빈도 horizontal bar chart (Hilbert 200, MiniBatch 190, etc.)

4. Method Routing Matrix
   - Difficulty quartile (Q1_easy ~ Q4_hard) × Method best 빈도 heatmap
   - "어려운 query → KDE-pilot/MiniBatch dominant" highlight

데이터 (CSV inline 또는 fetch):
[recovery_summary.csv / rq3_bootstrap_effect_size.csv / rq3_per_query_ranking.csv 의 핵심 row 붙여넣기]

기술 스택:
- React + Tailwind + recharts (또는 Plotly.js)
- shadcn/ui card / tabs / select 컴포넌트
- 한국어 인터페이스
- 모바일 반응형
```

---

## Prompt 3 — Hilbert vs Z-order Mechanism Visualizer

```
Hilbert curve 와 Z-order curve 의 locality 차이를 시각적으로 보여주는 React artifact 만들어줘.

배경:
- 본 연구의 RQ3 핵심 contribution: Hilbert curve = learning-free 1순위.
- Mechanism 분석: inverse Manhattan distance = 1.000 (Hilbert) vs 1.992 (Z-order).
- 50% Z-order 인접 1D pair 가 2D non-adjacent ("Z-jump").

시각화 요구:
1. 32×32 grid (p=5) 위에 Hilbert / Z-order curve path 좌우 동시 그리기
2. Path 의 색을 1D distance gradient (viridis)
3. "Manhattan jump > 1" 인 segment 만 빨간색 강조 (Z-order 에서 50%)
4. Slider 로 grid order p 변경 (p=2~7, 4×4 ~ 128×128)
5. 각 curve 의 metric live update:
   - Inverse mean Manhattan
   - Fraction (Manhattan > 1)
   - Forward mean jump (4-neighbor)

기술:
- React + canvas/SVG (path drawing)
- 인터랙티브 grid order slider
- 한국어 라벨 (한글 폰트 자동)
- 토글: Hilbert / Z-order / 두 curve overlap
```

---

## 사용자 진행 방법

1. claude.ai/new 접속 (Pro 계정 권장)
2. 위 3 prompt 중 하나 선택 후 붙여넣기
3. 데이터 부분은 본 repo 의 csv/md 에서 핵심 row 추출해 prompt 에 inline
4. Claude 가 React artifact 생성 → 클릭/탐색 가능 prototype
5. artifact 의 React 코드 export → submission/_drafts/발표prototype/ 에 저장

---

**작성**: 조현빈 · 2026-05-07 00:50 KST
