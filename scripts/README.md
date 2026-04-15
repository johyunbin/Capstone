# Scripts — 유틸리티 스크립트

## 문서 변환

| 스크립트 | 용도 |
|---------|------|
| `md2pdf.py` | Markdown → PDF (Chrome CDP, Apple SD Gothic Neo) |
| `md2docx.py` | Markdown → DOCX |

## 실험 데이터 전처리 (Stage 1~5)

| 스크립트 | 용도 |
|---------|------|
| `rq1_stage1_dump.py` | 1M subset 임베딩 + 거리 행렬 추출 |
| `rq1_stage2_skew.py` | 글로벌 skewness 4지표 계산 |
| `rq1_stage3_selectivity.py` | D_target 계산 (6 selectivity) |
| `rq1_stage4_adaptive.py` | Adaptive Sampling 시뮬레이션 |
| `rq1_stage5_analyze.py` | Q-error 분석 + Spearman 상관 |

Stage 1~5는 Phase 1~2의 기초 데이터를 생성하는 전처리 파이프라인.
Phase 4+ 실험 스크립트는 `experiments/code/rq1/`에 위치.
