# Ultra Review — guideline + scripts (20260508 22:30 KST)

작성: 2026-05-08 22:30 KST (백그라운드 에이전트 U5)
대상: `/Users/hyunbin/Capstone/_internal/{guideline,scripts}/`
긴급도: MEDIUM — 자동화 지침의 5/27 발표 / 6/11 보고서 가용성 확보

---

## 1. guideline/ 5 active 지침 update 결과

5 active 지침 모두 5/8 22:00 finalize 결과 반영 update. 각 지침의 본 내용은 보존하고 도입부에 "5/8 22:00 finalize 후 핵심 패턴" 섹션만 추가하는 패턴으로 진행.

| 지침 | update 내용 | 신규 추가 섹션 |
|---|---|---|
| 01_실험지침 | chain_unified.py CELLS dict + monkey-patch 패턴 명시. silent skip risk 방지 (5/7 STAGE 2 사고 재발 방지) assertion + print 권장. paired query_id alignment 강조. 측정기 → analyze → fill 파이프라인 명시. | "5/8 22:00 finalize 후 핵심 패턴 (W2~W3 active)" |
| 02_제출물지침 | 자문 메일 v4 박성원 멘토 단독 발송 vs 박광현 교수님 별도 분기 명시. 5/8 회의 자문 outline 3줄 합의 인용. `자문메일_발송체크리스트_20260508.md` 참조 추가. | "5/8 22:00 finalize 후 핵심 패턴 (W2 active)" |
| 03_문서생성지침 | md2pdf.py + Apple SD Gothic Neo 변경 X. 다만 docx 변환은 `_build_docx_v1.py` 만 active 명시 (v0/v2/4_28 archive 됨). PPT 변환 stack `build_native_pptx_5_8.py` + `build_charts_5_8.py` 추가. | "5/8 22:00 정합성 재확인" |
| 04_미팅지침 | **5/22 박광현 교수님 미팅 framework** 신규 추가. 사전 brief 4 항목 (W2 자문 회신 / W2 측정 결과 / W3 발표 초안 / 5/27 D-day) 정리. 브리핑 파일명 규칙 명시. | "5/22 박광현 교수님 미팅 framework (W3, D-14 from 5/8)" |
| 05_발표지침 | **5/27 deck redesign v2 framework** 명시. `_internal/slide_redesign_v2_20260508.md` 참조 link. 18 page (S6.5 + S10.5 신규 2 page) + ★4 sparse RP 교체 + P5 LSH Wave 0 honest reporting. 변환 도구 `build_native_pptx_5_8.py` 명시. | "5/27 최종 발표 deck redesign v2 framework (W4 active)" |

manual.md / .sh 는 변경 없음 (기존 내용 보존). archive/ (00점검 / 01논문분석 / 05주간보고 / 08설계 / 09학습 / 10CC활용) 손대지 않음 — 이미 정리됨.

## 2. scripts/ active vs stale 분류

총 39 .py 파일 + 5 .sh + README.md + 1 dir + __pycache__/ 점검.

**Active 보존** (35 .py + 5 .sh + README, 5/8 22:00 시점 사용 중):

- 변환: `md2pdf.py`, `md2docx.py`, `md2pdf_academic.py`, `_build_docx_v1.py` (4/27 19:02 commit, v0/v2/4_28 superseded)
- 측정 (5/8 신규): `chain_unified.py`, `measure_multi_paradigm.py`, `measure_multi_adaptive_sampling.py`, `measure_multi_4kang.py`, `measure_multi_5mode.py`, `measure_multi_all.py`, `measure_multi_table_join.py`, `measure_multi_vector.py`, `setup_multi_sf1.py`, `prepare_cell.py`
- 분석 (5/8): `analyze_multi_paradigm.py`, `analyze_tier_elimination.py`, `analyze_k_optimal.py`, `analyze_bern_qerr_per_dataset.py`, `analyze_ssn_ceiling.py`, `master_v6_fill_partial.py`, `plot_w4_partial.py`
- 차트/PPT (5/8 redesign v2 변환용): `build_charts_5_8.py`, `build_native_pptx_5_8.py`
- 데이터셋 빌드: `build_wiki.py`, `build_yfcc.py`
- Tier 1 method 측정용 (`run_*.py` 11종): agglomerative, coresets, dbscan, faiss_ivf, fixed_rate_baselines, hierarchical_kmeans, kmeans_pp, optics, pca_kmeans, subset_training
- shell: `run_cell_full.sh`, `parallel_download.sh`, `watch_final_chain.sh`, `watch_phase2.sh`, `watch_post_8m.sh`

**Stale 9개** archive 이동 — `_internal/scripts/archive/2026_05_08_cleanup/`:

- `_build_docx_v0.py` (4/27 14:31, v1 superseded)
- `_build_docx_v2.py` (4/27 12:57, v1 superseded)
- `_build_docx_4_28.py` (4/28 22:58, 마감 후 미사용)
- `build_midterm_pptx.py` (4/19 02:58, 중간발표 archive)
- `midterm_pptx/` 디렉토리 전체 (15 파일, 4/27, 중간발표 archive)
- `build_charts_5_8.py.bak.20260508` (5/8 morning .bak)
- `build_charts_5_8.py.bak.20260508_1050` (5/8 morning .bak)
- `build_native_pptx_5_8.py.bak.20260508` (5/8 morning .bak)
- `build_native_pptx_5_8.py.bak.20260508_1050` (5/8 morning .bak)

`__pycache__/` (5 .pyc) 삭제. .bak 파일들은 git 미추적 상태였으므로 plain `mv` 사용. 나머지는 모두 `git mv` 사용.

## 3. cleanup verification

`ls /Users/hyunbin/Capstone/_internal/scripts/` 결과:
- 35 .py + 5 .sh + 1 README.md + 1 archive/ 디렉토리만 잔존
- midterm_pptx/, __pycache__/ 모두 정리됨

`ls .../archive/2026_05_08_cleanup/` 결과:
- 4 .py (build_docx v0/v2/4_28 + build_midterm_pptx) + 4 .bak + midterm_pptx/ 폴더

git status 로 확인 시 `git mv` 한 5건은 staged R 상태, .bak 4건은 untracked → ignored (이전부터 untracked).

## 4. commit 결과

본 작업의 모든 staged 변경 (5 guideline updates + 9 scripts archive moves + 본 ultra_review_guideline_scripts 보고서) 은 commit `15accbd` ("ultra-review root + templates/ — README.md 5/8 update + 루트 정리") 에 다른 에이전트의 root + templates 작업과 함께 합쳐서 commit 되었음. 동시 진행되던 다른 에이전트가 staged area 의 모든 변경을 함께 가져갔음 — 단일 commit 메시지가 root + templates 만 명시했지만 file list 에는 본 작업 산출 전부가 포함됨.
