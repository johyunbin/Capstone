# 속도는벡터 — 5/27 최종 발표 deck v4 (Academic · paper exact)

5/8 v3 Academic deck (16 slide) → 5/11 paper exact 측정 결과 반영 **18 slide v4**.

> **변경 핵심** (5/8 v3 → 5/11 v4):
> - 16 → **18 slide** 확장 (S7 Paradigm 9 + S12 CaseB Ensemble Climax 신규)
> - 4강 framing 폐기 → **9 paradigm rollup** narrative
> - CaseA 단독 대체 → **CaseB ensemble augment climax**
> - ★3 Hilbert "production sweet spot" → **PCA proxy alias + 진짜 Hilbert 3건 anchor 분리 검증**
> - RQ2 "40/40 cells" → **Anti < Prop < Neyman paradox honest finding**
> - Limitation 4 → **18 (Group A/B/C/D)**
> - Future Work 4 → **8건 (P7/P8 + multi-table + SF=100 + paradox + 가중평균 + acceptance + 2024-25 integration)**

## 디자인 시스템 — Academic (5/8 v3 base 유지)

### Surface
- **배경**: 전체 흰색 `#FFFFFF` (다크 슬라이드 없음)
- **상단 navy stripe**: full-width 6px navy bar (`#1B3DAD`)
- **하단 implication bar**: navy 배경 + red 4px left border + 흰 텍스트 1줄 결론

### Typography
- **국문**: IBM Plex Sans KR (Google Fonts) → Inter fallback → Apple SD Gothic Neo fallback
- **수치**: Inter (tabular figures `font-feature: tnum 1, lnum 1`)
- **mono**: JetBrains Mono (caption / pill / badge)

### Color tokens
| token | hex | 용도 |
|---|---|---|
| `C.navy` | `#1B3DAD` | primary accent · big number · stripe |
| `C.navyDeep` | `#14307F` | hover / shadow |
| `C.blue` | `#4A7BD8` | secondary chart |
| `C.blueSoft` | `#E4ECF8` | tint / background |
| `C.red` | `#E03A3A` | negative · warning · ★3 ★4 marker |
| `C.green` | `#2A9D6E` | ★ 신규 (P9 / P10 / hilbert_real) |
| `C.gold` | `#D9A53B` | SSN++ ceiling / paradox marker |
| `C.ink` | `#0B0F1C` | numbered badge 배경 |
| `C.g100~g700` | warm slate | hairline / caption |

### Numbered badge + page counter
- 좌상단: 36×36px ink 배경 흰 텍스트 numbered badge (`01` `02` … `16` 등)
- 우상단: `01 / 18` navy mono page counter

### Cards
- `card` : 1px g200 border + 2px border-radius
- `card.navy-top` : 3px navy top border
- `card.red-top` : 3px red top border
- `card.green-top` : 3px green top border (★ 신규 paradigm)
- `card.gold-top` : 3px gold top border (paradox)

## 18 Slide 구성

| # | num | 제목 | 핵심 메시지 | figures |
|---|---|---|---|---|
| 01 | — | Cover | "Skew-Aware Stratified Sampling **Ensemble**" + paired 92.9% subtitle | — |
| 02 | — | TOC | 7-card grid (Problem / Prior / Approach / RQ1 / Paradigm 9 / RQ2 / CaseB Climax) | — |
| 03 | 01 | Problem | pgvector 33.3 / VBASE 50 / DuckDB 100% + 실제 0.001~90% 분포 + 1000~10000× plan cost gap | — |
| 04 | 02 | Prior · Exqutor §V-A/§V-B | ECQO 1-2ms (인정) + Adaptive N=385 (본 연구 영역) + 본 연구 위치 | — |
| 05 | 03 | Approach · ensemble avg | est_b1 + est_method / 2.0 다이어그램 + paper exact 보존 + 의사 비유 | — |
| 06 | 04 | RQ1 · distribution gap | mean +3.74% gap + paper exact 1.6180 vs 1.69 (−4.26%) + 5 cell bar | — |
| 07 | 05 | Paradigm 9 framework | 9 paradigm card grid (P1-P10 + Future) — P9/P10 green ★ 신규 | — |
| 08 | 06 | RQ2 · Paradox | 5-way bar (Anti 1.540 < Prop 1.580 < Neyman 1.595) + Root cause σ range narrow | — |
| 09 | 07 | RQ3 · Paradigm Rollup CaseB | 9 paradigm CaseB Δ% bar + Top 5 anchor (P10 -11.93 / P9 -7.60 / P3 -6.53 / P4 -5.92 / P2 -5.52) | F1 |
| 10 | 08 | ★3 Hilbert defect rectify | 4 card (★3 alias / M6 / M7 / hilbert_real) + PCA proxy vs 진짜 분리 검증 | — |
| 11 | 09 | Top winners | Top 5 winners @ A5-sf1 (pq / sparse_rp / vinecopula / hilbert_real / hyperloglog) | F4 |
| 12 | 10 | **CaseB Ensemble Climax** ⭐ | 4 큰 수치 (92.9% / 63.5% / 56.4% / 71.8%) + 의사 비유 + main contribution | — |
| 13 | 11 | Negative Control · CaseA broken | CaseA 0/437 outperform + CaseB 284/447 large better 좌우 대비 | F2 |
| 14 | 12 | Cross-scale sf 1/10/100 | sf 별 Δ% 트렌드 + paper Fig 14 1.6180 vs 1.69 | — |
| 15 | 13 | Mechanism · locality 분리 | 4 anchor × 9 cell heatmap (★3 alias vs M6 vs M7 vs hilbert_real) | — |
| 16 | 14 | Effect Size honesty | 4축 통계 (Hedges' g 56.4% + Cliff's δ 63.5% + Reproducibility 280/280 + Determ 100%) | F5 |
| 17 | 15 | Limitation 18종 | 4 group grid (A v1 4 + B W4 4 + C V7 3 + **D 5/11 신규 5건 red border**) | — |
| 18 | 16 | Future Work 8 + Closing | 4×2 future card (P7 / P8 / multi-table / SF=100 / σ range / 가중평균 / ★3 acceptance / 2024-25) + 본 연구 한 줄 요약 + 감사 + Q&A | — |

> 18 slide 총 **약 12분** (slide 별 30-45초). figures 6건은 별도 image asset 사용 가능 (`figures/F1~F6.png`) — Slides.jsx 안에서 `<img src="figures/F1_paradigm_rollup_caseB.png">` 로 통합 가능.

## Speaker Notes
`index.html` 안 `<script id="speaker-notes">` JSON 19개 entry (S1~S18 + intro). 한국어 학술 산문 — 강재현 발표 스크립트.

## 핵심 수치 정확 반영 (5/11 paper exact 측정)
- **paper exact 검증**: 8 cells mean qe_trim 1.6180 vs paper 1.69 (-4.26%), reproducibility 280/280 byte-identical
- **CaseB ensemble climax**: paired CaseB > CaseA 92.9% (404/435) / Cliff's δ large better 63.5% (284/447) / Hedges' g large 56.4% (252/447) / sign test 71.8% p=3.1e-46
- **9 paradigm rollup CaseB mean Δ%**: P10 -11.93 / P9 -7.60 / P3 -6.53 / P4 -5.92 / P2 -5.52 / P1 +0.17 / P6 +0.63 / P5 +1.47
- **RQ1 분포 차이**: mean +3.74% (5 cell × 5 trial)
- **RQ2 paradox**: Anti 1.540 < Prop 1.580 < Neyman 1.595 + Bern→Prop -9.53%
- **★3 hilbert_real CaseB**: 9 cells mean -8.2% + 6/9 cells signif p_adj<0.05
- **Top winners**: pq @ A5-sf1 g=-7.15 / sparse_rp @ A5-sf1 g=-7.14 / vinecopula @ A5-sf1 g=-7.05 (Top 5 all @ A5-sf1)
- **Cross-scale**: sf=1 -11.01 / sf=10 -4.57 / sf=100 -9.23

## 파일 구조

```
academic-deck-v4/
├── index.html          ← deck-stage host + Academic style block + 18 speaker notes JSON
├── Slides.jsx          ← 18 React 컴포넌트 (S1 … S18) + Chrome + Impl base
├── deck-stage.js       ← v3 base 그대로 복사 (scaling + nav + ⌘P print)
├── figures/            ← F1~F6 paper exact figures (image asset, 5/11 v8.6)
│   ├── F1_paradigm_rollup_caseB.png
│   ├── F2_cliffs_delta_bucket.png
│   ├── F3_caseA_vs_caseB_violin.png
│   ├── F4_top_winners_caseB.png
│   ├── F5_effect_size_scatter.png
│   └── F6_narrative_diagram.png
└── README.md           ← 이 file
```

## 로컬 사용
```bash
# 브라우저에서 직접 열기 (Babel inline compile, 인터넷 필요)
open /Users/hyunbin/Capstone/submission/_drafts/academic-deck-v4/index.html

# 또는 정적 서버 (Babel 컴파일 안정성 ↑)
cd /Users/hyunbin/Capstone/submission/_drafts/academic-deck-v4
python3 -m http.server 8080
# → http://localhost:8080
```

## PDF Export
1. 브라우저에서 `index.html` 열기
2. ⌘P (Mac) / Ctrl+P (Windows)
3. 인쇄 대상 → "PDF로 저장"
4. 페이지 크기: A4 가로 또는 16:9 사용자 정의 (1280×720 비율)
5. 여백: 없음
6. 배경 그래픽: 체크 (필수)
7. 저장 → `속도는벡터 — Academic v4 · Final 5_27.pdf`

## claude.ai/design 작업 흐름 (5/16 ~ 5/19)

1. claude.ai/design 에서 새 프로젝트 또는 기존 (academic-deck) 그룹 진입
2. `index.html` + `Slides.jsx` + `deck-stage.js` 3 file 입력
3. ULTRAPLAN 의 "클로드 디자인 직접 input prompt" 복붙 + 본 README §"18 Slide 구성" 표 paste
4. iteration:
   - 1차: 18 slide 모두 렌더 검증
   - 2차: 시각 hierarchy 점검 (수치 크기 / 색상 / 간격)
   - 3차: figures 통합 (F1~F6 image asset)
   - 4차: speaker notes 18 slide × 30-45초 분량 점검
   - 5차: PDF export visual 일치
5. PDF export → `submission/_drafts/속도는벡터 — Academic v4 · Final 5_27.{pdf,pptx}` 저장
6. 강재현 발표 리허설 (5/25 ~ 5/26)

## 5/15 박광현 미팅 후 정정 (5/16 ~)

미팅 confirm 결과에 따라 minor 정정만:
- S8 RQ2 paradox 표현 (만약 narrative 변경 시)
- S17 Limitation 추가 또는 정정
- S18 Future Work 우선순위 조정

미팅 자료: `submission/_drafts/박광현_5월15일_미팅/속도는벡터_박광현미팅_5월15일_slide_draft_20260511.md`

## 검증 checklist (5/26 finalize 직전)

- [ ] 18 slide × 1 메시지 원칙 준수 (텍스트 최소)
- [ ] 핵심 수치 50-80px navy bold 시각 강조 일관성
- [ ] figures 6건 통합 OK (Korean font Apple SD Gothic Neo / IBM Plex Sans KR)
- [ ] speaker notes 18 slide × 30-45초 분량 (총 12-15분)
- [ ] 5/8 v3 디자인 시스템 (색상 / 타이포 / 레이아웃) 정합성
- [ ] PDF export OK (Chrome ⌘P)
- [ ] 강재현 발표 리허설 (5/25~5/26)

---

작성: 2026-05-11 20:05 KST  
참조 spec: `submission/_drafts/5_27_발표_deck_v4_ULTRAPLAN_20260511.md`  
참조 narrative: `submission/_drafts/팀원_효과적_method_종합_20260511.md`  
참조 미팅 자료: `submission/_drafts/박광현_5월15일_미팅/`
