# Scripts — 유틸리티 + 측정 + 분석 스크립트

> **마지막 update**: 2026-05-11 18:25 KST — paper exact 측정 완료 + ★3 hilbert_real / Q4 paradigm anchor 확장 launch 후 정합화.

## 1. 핵심 measurement + analyze (5/11 paper exact 진행 중)

| 스크립트 | 용도 |
|---|---|
| `measure_exqutor_replication_DRAFT.py` | paper exact 측정 메인 (local mirror, 진짜 측정은 server `/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py`) |
| `_measure_common.py` | 공통 inf cap / paired_delta / 5-way alloc (`fetch_stratum_sigmas`, `neyman_alloc`, `anti_neyman_alloc`) |
| `analyze_paper_exact.py` | Phase D 분석 + REPORT v7~v9 자동 생성 (PARADIGM_MAP P1-P10 + Hedges' g + Cliff's δ + paradigm rollup + cherry-pick + drop list + method-level limitation) |
| `compute_stratum_sigma_paper_exact.py` | σ_j NPY mmap (DEEP/SIFT/SSN sf=100 KM20 cluster, sel=0.1 D_target) |
| `figures_paper_exact.py` | 6 figure 자동 생성 (F1 paradigm rollup / F2 Cliff's δ bucket / F3 violin / F4 winners / F5 effect scatter / F6 narrative). Apple SD Gothic Neo 적용 |

## 2. Phase 4 + Q4 method modules (5/10~5/11)

| 스크립트 | 용도 |
|---|---|
| `method_phase4_extra.py` | Phase 4 11 method 통합 (M1 chao_weighted ~ M11 idistance_neyman) |
| `method_tier1_p9_p10.py` | Q4 Tier 1 6 method (DBSCAN/KDE/MHIST-2/HyperLogLog/RSVD/wavelet) |
| `method_hilbert_real.py` | ★3 hilbert_real (Wikipedia xy2d 표준, 9 cells × 2 modes) |
| `PATCH_phase4_registry.md` / `PATCH_hilbert_real_registry.md` | measure_paper_exact.py registry patch |
| `run_phase_b_phase4.sh` / `run_phase_b_q1q4.sh` / `run_phase_a2fig8_tier1.sh` | tmux launch wrapper |

## 3. 문서 변환

| 스크립트 | 용도 |
|---|---|
| `md2pdf.py` | Markdown → PDF (Chrome CDP, Apple SD Gothic Neo) |
| `md2docx.py` | Markdown → DOCX |
| `md2pdf_academic.py` | Academic 스타일 PDF (5/27 발표용) |
| `_build_docx_v1.py` | 학교 양식 docx 빌드 (중간보고서용, 4/28) |

## 4. 이전 시점 measurement / analyze (5/6~5/9, archive 후보)

| 스크립트 | 용도 |
|---|---|
| `chain_unified.py` | unified measurement chain (5/9 시점) |
| `measure_multi_*.py` (5건) | multi-vector + multi-table 측정 (4kang / 5mode / adaptive / all / ensemble) |
| `analyze_multi_paradigm.py` / `analyze_ensemble.py` / `analyze_phase_g.py` / `analyze_failure_modes.py` / `analyze_k_optimal.py` / `analyze_tier_elimination.py` / `analyze_ssn_ceiling.py` / `analyze_bern_qerr_per_dataset.py` | 이전 분석 (5/7~5/9) |
| `build_*.py` (6건) | chart / pptx / FB_single_ensemble / new_multi_cells / sf100_single / wiki / yfcc 빌드 (5/8 시점) |
| `finalize_5_9_morning.sh` / `launch_sf100_safe.sh` | 5/9 trigger |
| `master_v6_fill_partial.py` | master_v6 분석 보고 fill (5/8) |
| `midterm_pptx/` | 4/28 중간발표 PPT 빌드 (5 file: theme / common / content / build_*) |

## 5. archive (5/11 정리)

- `archive/5월8일_scripts_정리/` (이전 cleanup + .bak_v8 file 2건)

## 데이터 전처리 (Stage 1~5)

`rq1_stage1~5.py` 는 `experiments/code/local_analysis/` 에 위치 (Phase 1~2의 기초 데이터 전처리 파이프라인).
