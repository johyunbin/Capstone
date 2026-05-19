# Ultra-Review experiments/ — 2026-05-08 KST 22:30

> **Scope**: `/Users/hyunbin/Capstone/experiments/` 디렉토리 전수 검토 + cleanup. 5/27 발표 / 6/11 보고서 ready 정리. **Conservative archive** 원칙 (over-archive 금지) 엄수.

## 1. Inventory 통계

| 항목 | Count |
|------|------|
| Cleanup 전 총 파일 (excl. `__pycache__`, `.DS_Store`) | **574** |
| Cleanup 후 active 파일 | **569** |
| Cleanup 후 archive (`*/archive/*`) | **16** (이전 9 + 신규 7) |
| 14일+ 미수정 (active 영역) | 91 (대부분 RQ1/RQ2 phase 4~7 동결 산출물 — load-bearing) |
| `.py` 스크립트 | 117 (rq1: 29, rq2: 5, rq3: 22 + 16 sub method, local_analysis: 41, etc.) |

서버에서 진행 중인 multi 측정 (`measure_multi_4kang.py` PID 11062/11064 — partsupp_deep_sift_1 / partsupp_deep_wiki_1 / join_deep_wiki_1) 의 parquet 산출은 서버 `/mnt/hdd0/home/capstone2026/cache/rq3/` 에 위치. **로컬 `/Users/hyunbin/Capstone/experiments/` 와 disjoint — cleanup 범위 외 (안전 확인됨)**.

## 2. Archive 이동 (총 7 파일, 5/8 cleanup)

### 2-1. Wave 0 / P-method 가지치기 잔류 parquet (4종)
30 method 분포·인덱스 leak audit (5/8) 에서 Wave 0 / P-method (Pruned) 로 분류된 method 의 8M scale 측정본만 잔류. 1M / 단일 cell 본은 보존 (master `_internal/Adaptive_Sampling_method_분석_20260508.md` 및 `_internal/scripts/measure_multi_paradigm.py` 에서 reservoir 만 reference). **8M scale 본은 active doc 어디에도 reference 없음** (active grep 결과 0 hit, archive handoff 만 mention).

- `experiments/results/rq3_agnostic/rq3_8m_km_k_10.parquet` (P-method KM k=10)
- `experiments/results/rq3_agnostic/rq3_8m_km_k_50.parquet` (P-method KM k=50)
- `experiments/results/rq3_agnostic/rq3_8m_opq.parquet` (Wave 0 OPQ)
- `experiments/results/rq3_agnostic/rq3_8m_reservoir.parquet` (Wave 0 Reservoir, ~~`rq3_reservoir.parquet` 1M 본은 multi script reference 로 보존~~)

### 2-2. SSN 5/7 ad-hoc auxiliary measurement (2종)
W2 sprint 5/7 시점의 1회용 ceiling/per-dataset bern qerr 측정. handoff_v7/v8 (이미 archived) 에서만 reference. active doc 0 hit.

- `experiments/results/ssn_bern_qerr_per_dataset_20260507.csv`
- `experiments/results/ssn_ceiling_results_20260507.json`

### 2-3. 미참조 ppt 보조 figure (1종)
- `experiments/figures/rq1_motivation/slide6_vector_c_snippet.png` (active doc 0 hit, vector.c 누수 슬라이드 보조 이미지)

### 2-4. 빈 nested directory 제거
- `experiments/experiments/results/rq3_agnostic/` (placeholder, 0 file) → `rmdir` 처리

## 3. 보존 결정 (over-archive 회피)

다음은 14일+ 미수정 또는 외관상 stale 이지만 active reference 가 있어 **명시적 보존**:

| 파일 | 보존 사유 |
|------|----------|
| `results/RQ1_RQ2 실험 결과 정리.{md,pdf}` (4/16) | CLAUDE.md 명시 보존 + master.md 4/16 baseline |
| `results/RQ1_RQ2_RQ3_종합_master.md` (5/7) | `plans/최종보고서_outline_v1_20260507.md` 인용 |
| `results/RQ1_RQ2_RQ3_종합_master_v6_draft.md` (5/8 14:47) | `_filled_partial.md` parent + 5/8 PPT outline 인용 |
| `results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.{md,pdf}` | **W4 본 master, 명시 보존** |
| `results/master_v6_§10.6_*`, `master_v6_§10.7_*` (5/8) | **§10.6/§10.7 분석, 명시 보존** |
| `results/10cell_narrative_종합_20260508.{md,pdf}` | **5/8 narrative, 명시 보존** |
| `results/W2_sprint_*_20260507.md` × 2 | master.md 인용 |
| `results/RQ_Limitation_4종_명시.md` | RQ Limitation 정리 단독 doc |
| `results/rq3_agnostic/RQ3_*.md` × 2 | master.md 직접 link |
| `figures/rq1_motivation/figure_{1,2,6}*.png` (4/27) | 4/15 카톡 + 중간보고서 인용 |
| `figures/rq2_aware/figure_{7,8,9,10}*.png` (4/27) | weekly 4/17 + RQ2 master 인용 |
| `figures/rq1_motivation/figure_{3,4,5}*.png` (4/16) | RQ1 phase6/7 핵심 |
| `code/rq1/phase{4,5,6,7}_*.py`, `random20_*.py`, `hhi_*.py` (4/19) | README §"실험 Phase 매핑" 명시 |

## 4. Rename 처리

CLAUDE.md 파일명 규칙 (`구조적 경계 _ / 제목 내 공백 / Title Case`) 위반 사례 검토:

- `master_v6_§10.{6,7}_*` — `§` 기호 비표준이지만 **task 본문 명시 보존 대상** → 유지
- `RQ1_RQ2 실험 결과 정리.{md,pdf}` — 한국어 제목 내 공백 (규칙 부합) → 유지
- `실험{1,2_3,4}_결과정리_20260506.md` — `_` 가 한글 단어 경계 (혼용 가능 case) + sub-dir 안 → 유지

**Rename 0건** — 활성 doc reference link 다수 (`master.md`, `master_v6_draft.md`, `_filled_partial.md`) 보호 우선.

## 5. 최종 검증

```
git status --short experiments/
R  experiments/figures/rq1_motivation/slide6_vector_c_snippet.png -> experiments/figures/archive/2026_05_08_cleanup/...
 D experiments/results/ssn_bern_qerr_per_dataset_20260507.csv
 D experiments/results/ssn_ceiling_results_20260507.json
?? experiments/results/archive/2026_05_08_cleanup/ssn_bern_qerr_per_dataset_20260507.csv
?? experiments/results/archive/2026_05_08_cleanup/ssn_ceiling_results_20260507.json
```

(8M km_k_10/50, opq, reservoir parquet 4 점은 git 미추적 untracked 였으므로 status 미표기 — 단순 fs move.)

- master_v6 본체 + §10.6/§10.7 + 5/8 audit 산출 + 5/27 발표 figure: **전부 보존 확인**
- 서버 multi 측정 (PID 11062/11064) parquet: **로컬 무관, 미접촉**
- 4 archive subdir 신규 생성 (`results/archive/`, `figures/archive/`, `code/archive/`) — `code/archive/` 는 빈 채로 유지 (현 시점 archive 대상 코드 0)

## 6. Commit hash

`2c9a9d7` — `ultra-review experiments/ — stale archive + naming 정정` (5/8 22:32 KST)
