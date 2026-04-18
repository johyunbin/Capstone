# Experiments — "쏠림 → 성능 저하 → 공간 인식 Sampling 개선"

## 개요

Exqutor(arXiv:2512.09695v2)의 uniform BERNOULLI sampling이 벡터 데이터의 공간 밀도 비균일성(쏠림)에 의해 카디널리티 추정 정확도가 저하되는 문제를 실증하고, 공간 인식 stratified sampling(KM20)으로 이를 개선한다. RANDOM20 대조 실험으로 "쏠림이 원인"임을 직접 증명.

## 환경

- **서버**: BDAI Lab GPU 서버 (`165.132.140.240`)
- **DB**: Exqutor-patched PostgreSQL 16.9 (port 55436) + pgvector 0.7.1
- **데이터**: TPC-H SF10 + DEEP 96d (8M), SIFT 128d (1.5M)
- **주 실험 테이블**: `partsupp_deep_10_subset_1m` (1M, KM20 stratum_id 부여)

## 디렉토리 구조

```
experiments/
├── config/                     실험 파라미터
│   └── experiment_params.yaml
├── code/rq1/                   실험 스크립트 (서버에서 실행)
│   ├── phase4_native.py        Pivot A: SYSTEM vs BERNOULLI
│   ├── phase5_local_skew.py    로컬 skewness 4지표
│   ├── phase6_strat_native.py  KM20 stratified native 측정
│   ├── phase6_multiseed.py     Phase 6 multi-seed (5 seeds)
│   ├── random20_control.py     ★ RANDOM20 대조 실험 (s=0.500)
│   ├── random20_low_sel.py     ★ RANDOM20 저selectivity (s=0.010, 0.050)
│   ├── hhi_python.py           ★ Per-selectivity HHI (Python 거리계산)
│   ├── phase7_8m_redo.py       8M 외적 타당성 (D_target 재계산)
│   └── ...
├── results/rq1_motivation/     실험 결과
│   ├── unified_random20_analysis.md  ★ 통합 분석 (핵심 참조 문서)
│   ├── random20_selectivity_gradient.md  selectivity gradient 분석
│   ├── summary.md              Phase 1~7 상세 (717줄)
│   ├── direction_pivot_rationale.md  Pivot 경위 (187줄)
│   ├── phase7_artifact_verification_20260415.md  Phase 7 artifact 검증
│   ├── deep_review_20260415.md  3축 딥리뷰
│   ├── *.json                  측정 데이터 (meta, paired, summary)
│   └── *.parquet               원시 데이터 (per-query Q-error)
├── results/rq2_aware/          (예정)
├── results/rq3_agnostic/       (예정)
└── figures/rq1_motivation/     시각화
```

## 실험 Phase 매핑

### RQ1 — 벡터 데이터의 공간 밀도 비균일성과 uniform sampling의 편향

| Phase | 실험 | 결과 | 파일 |
|-------|------|------|------|
| Stage 1~5 | 100 query × 6 sel × 5 seed 기초 데이터 | — | `stage*_meta.json` |
| Phase 1~2 | 글로벌 skew 4지표 × 6 sel = 24 조합 | 전부 \|ρ\|<0.2 → H1 기각 | `stage5_summary.json` |
| Phase 3 | Exqutor design constraint 검증 | 5종 발견 | `equivalence_check.md` |
| Phase 5 | 로컬 skew 4지표 × 6 sel = 24 조합 | 전부 \|ρ\|<0.2 → 재확인 | `phase5_local_skew_*.json` |
| **HHI** | **Per-selectivity cluster 집중도** | **s=0.001 HHI 12.5× → s=0.500 1.3×** | `hhi_python_summary.json` |

### RQ2 — Distribution-Aware Stratified Sampling

| Phase | 실험 | 결과 | 파일 |
|-------|------|------|------|
| Phase 4 | Pivot A: SYSTEM→BERNOULLI | +3.8~9.6% (4구간 p<0.001) | `phase4_*.json` |
| Phase 6 | KM20 stratified native | **+1.64% CI [1.25, 2.02]** (5-seed) | `phase6_multiseed_summary.json` |
| Phase 7 | 8M/SIFT 외적 확장 | artifact 철회 | `phase7_artifact_verification*.md` |
| Phase 7 redo | 8M D_target 재계산 + 재측정 | 진행 중 | `phase7_8m_redo_summary.json` |
| **RANDOM20** | **대조 실험 (s=0.500)** | **KM20 ≈ RANDOM20** | `random20_control_summary.json` |
| **RANDOM20 low-sel** | **대조 실험 (s=0.010, 0.050)** | **KM20 +8.93% vs RAND −10.67%** | `random20_low_sel_summary.json` |

### RQ3 — Distribution-Agnostic (최종발표, W7)

예정: KDE-pilot, LSH-bucket

## 핵심 결과 요약

### RANDOM20 Selectivity Gradient (본 연구 최강 증거)

| sel | HHI (ratio) | KM20 vs BERN | RAND vs BERN | KM20−RAND |
|-----|------------|-------------|-------------|-----------|
| 0.010 | 0.50 (10.1×) | +8.93% | −10.67% | **19.6%p** |
| 0.050 | 0.29 (5.8×) | +1.85% | +0.79% | 1.1%p |
| 0.500 | 0.07 (1.3×) | +1.64% | +2.20% | ~0 |

### Two-Level Decomposition

- **Level 1** (Proportional Allocation): partition 무관, 보편적 → s=0.500에서 지배
- **Level 2** (Spatial Awareness): selectivity-dependent → s=0.010에서 지배

## 재현 방법

```bash
# 서버 접속
ssh capstone2026@165.132.140.240
cd /mnt/hdd0/home/capstone2026

# Exqutor PG 기동 확인
PG_BIN=Exqutor/PostgreSQL/pgvector/psql/bin
$PG_BIN/pg_ctl status -D exqutor_sf10

# 실험 스크립트 실행 (예: RANDOM20)
python3 cache/rq1_random20_control.py

# 결과 확인
cat cache/rq1/random20_control_summary.json | python3 -m json.tool
```

## 지표

- **Q-error**: max(estimated/actual, actual/estimated) — hook_est 기준
- **Paired Wilcoxon**: signed-rank test (alternative: strat < bern)
- **HHI** (Herfindahl-Hirschman Index): cluster 집중도 (1/K=균일, 1.0=단일 cluster)
- **Bootstrap 95% CI**: 5-seed mean diff% 의 bootstrap resampling

## 참조

- Exqutor 논문: arXiv:2512.09695v2
- 연구 재설계안: `plans/연구재설계안_20260415_131400.md`
- 통합 분석: `experiments/results/rq1_motivation/unified_random20_analysis.md`
