# experiments/results/archive — W1~W4 sprint archive (5/14 정리)

> 4/16 ~ 5/8 진행한 W1~W4 sprint 측정 결과 보존. paper exact 측정 (5/9~) 으로 superseded 되었으나 측정 변천 timeline 의 reference 로 유지.

## 디렉토리 구조

```
archive/
├── README.md                          [본 파일]
├── 2026_05_08_cleanup/                [기존 archive, 5/7 옛 km/opq/reservoir/ssn 6 file]
└── w1_w4_sprint_results/              [신규 archive, 5/14 정리]
    ├── master_drafts/                 [W1~W4 master draft 5 건]
    ├── 10cell_narrative/              [5/8 회의 자료]
    ├── w2_sprint/                     [W2 5/7 sprint 종합 2 file]
    ├── rq1_motivation/                [97 file, W1 4/16 RQ1 motivation]
    ├── rq2_aware/                     [14 file, W3 5/6-5/7 KM20 alloc]
    ├── rq3_agnostic/                  [245 file, W4 5/8 RQ3 16 method]
    ├── cache_rq1/                     [434 file, 5/8-5/9 server mirror]
    └── phase_g/                       [REPORT.md (5/10, paper-exact 직전)]
```

## sub-dir 별 내용 + superseded 사유

### `master_drafts/` — W1~W4 master draft 5 건

- `RQ1_RQ2 실험 결과 정리.md/.pdf` (4/28 중간 발표 결과)
- `RQ1_RQ2_RQ3_종합_master.md` (W1 5/6 1-page 종합, 4강 narrative)
- `RQ1_RQ2_RQ3_종합_master_v6_draft.md` (W4 5/8 skeleton)
- `RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md/.pdf` (W4 5/8 final)
- `master_v6_§10.6_Multi_광범위_*.md` (§10.6 fill)
- `master_v6_§10.7_Adaptive_분석_*.md` (§10.7 fill)

**superseded by**: paper exact REPORT v11 (server `/mnt/hdd0/.../paper_exact/REPORT_paper_exact.md`, 1362 line) + 본 연구 narrative v1 (`submission/_drafts/속도는벡터_본연구_narrative_최종정리_v1.md`).

### `10cell_narrative/` — 5/8 회의 자료

- `10cell_narrative_종합_20260508.md/.pdf` (master_v6 압축 narrative, 10 cell × 4강 method)

**superseded by**: 5/14 신규 4 file 자료 (`submission/_drafts/속도는벡터_5_27_최종발표_storyline_v1.md` 등).

### `w2_sprint/` — W2 5/7 sprint 종합

- `W2_sprint_8m_종합_20260507.md` (8M cross-scale 외적 타당성)
- `W2_sprint_부록_gap_fill_20260507.md` (gap fill 4건 + 종합 paired CI/Cohen's d)

**superseded by**: paper exact 1065 file portfolio + `_internal/analysis/` 9 분석 file.

### `rq1_motivation/` — W1 RQ1 motivation (97 file)

- Phase 4~7 main measurement (4/16, 47 file: parquet/meta/csv/json)
- `archive/` 9 file (Phase 7 8m 이전 측정, 4/15)
- `*.md` 9 file (RQ1 narrative doc, W1 결과 정리)
- `deep_s*_numpy_remeasure*.parquet/json` 10 file (5/8 numpy remeasure)
- `sift_rq1_2026_05_06/` 7 file (5/6 sift 재측정)
- `2026_05_06_8m_midsel/` 2 file (5/6 8m mid-sel)

**superseded by**: paper exact RQ1 측정 결과 (`_internal/validation/data/REPORT_paper_exact.md:42-63`).

### `rq2_aware/` — W3 5/6-5/7 KM20 alloc (14 file)

- Top-level 8 file (W1 RQ2 KM20 alloc 결과)
- `2026_05_06_alloc/` 15 file (RQ2 W3 5-mode 비교 + Anti-Neyman cell 분석)
- `2026_05_07_8m_alloc/` 12 file (RQ2 W3 8m 5-mode cross-scale)

**superseded by**: paper exact RQ2 측정 (REPORT_paper_exact 5-way 결과 + CLAUDE.md Anti 1.540 / Prop 1.580 / Neyman 1.595 paradox).

### `rq3_agnostic/` — W4 5/8 RQ3 16 method (245 file)

모두 5/8 16:27 mtime — paper exact 측정 (5/9~) 직전 intermediate.

- RQ3 16 method × 1m sift
- RQ3 16 method × 8m
- 5 dataset × cross-scale
- Wilcoxon / paired_ci / cohen_d 통계 검증 산출

**superseded by**: paper exact 1065 file portfolio (43 method × 9 cell × 2 mode).

### `cache_rq1/` — 5/8-5/9 server mirror (434 file)

- `rq1_YFCC_sf10_km_k_*.parquet` (4 file, YFCC K sweep)
- `rq3_{DEEP,SIFT,SSN,YFCC,WIKI}_sf{1,10}_<method>.parquet` (43 method × 5 dataset × 2 sf = 430 file)

paper exact 직전 intermediate (5/8-5/9 hyperparam, 본 연구 narrative 인용 X).

**superseded by**: paper exact 1001 file (server `/mnt/hdd0/.../paper_exact/`).

### `phase_g/` — REPORT.md (5/10, paper-exact 직전)

- `REPORT.md` (36 method × 26 cell skeleton, 측정 server-side)

**superseded by**: paper exact REPORT v11 (1362 line, 5/12 02:50 완성).

## 활성 archive (참고용)

- `2026_05_08_cleanup/` (5/7 옛 km/opq/reservoir/ssn 6 file) — 이미 격리됨, 추가 정리 X

## 활성 file 위치 (archive 외)

`experiments/results/` 직속에 활성 유지:

- `RQ_Limitation_4종_명시.md` (5/5 회의록 line 122-126 Limitation 표준)
- `phase_f/algorithm1_box.md` (B1 baseline Algorithm 1 의사코드)

---

작성: 2026-05-14 15:42 KST · 회의 의견 #9 archive 정리
