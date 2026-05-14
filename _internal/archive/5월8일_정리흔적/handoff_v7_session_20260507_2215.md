# 통합 manager 세션 인계 v7 — 5/7 22:15 KST (W4 sprint 진행 중, sf1+sf10 거의 완성)

> **이전 세션**: 5/7 18:24~22:15 KST, Opus 4.7 1M, context ~65%.
> **인계 목적**: 22 active server tmux + 1 background agent + 모든 자동화 ready 상태에서 깨끗한 context 로 인계.

---

## 1. 사용자 결정 누적 (절대 변경 금지)

1. **15-cell 매트릭스**: 6 dataset (DEEP/SIFT/SSN/WIKI/YFCC/**YFCC_DL**) × {sf1, sf10} = **12 단일** + multi (deep_sift_10, deep_wiki_10, multi-join) = **3 multi** = **총 15 cell**
2. **YFCC vs YFCC_DL 분리**: YFCC = 채림 vanilla_sf100 적재본, YFCC_DL = build_yfcc.py 으로 직접 build. PCA basis 비교용
3. **sf100 deferred**: 5/8 회의 후 자문 합의 후 진행
4. **Legacy 모두 무시**: SIFT 1.5M, BIGANN 1M, BIGANN 8M 모두 narrative 에서 제외. partsupp_*_{1,10,100} 패턴만
5. **모든 RQ1+RQ2+RQ3 필수**: 5/8 회의 전 sf1+sf10 5 dataset 의 RQ1/2/3 모두 측정 + multi
6. **YFCC raw 41GB 까지만 다운로드** (sf10 8M 분량). 5/8 회의 후 추가 결정
7. **PPT 양식**: academic v3 HTML deck (Slides.jsx React 컴포넌트) **양식 95%+ 정밀 재현 필요**. PDF/PPTX/HTML 모두 산출
8. **회의 자료 핵심**: 토의 + 편집 가능한 native PPTX (image-based 백업 별도)

---

## 2. 핵심 narrative (5/8 회의)

**4강 method (Hilbert / Hybrid / MiniBatch_partial / HDBSCAN) × 9 cell paired Δ% vs bern (sel=0.10)**:

| Cell | Hilbert | Hybrid | MB_partial | HDBSCAN |
|---|---:|---:|---:|---:|
| DEEP_sf1 | -0.43% | -1.06% | -1.36% | -1.84% |
| DEEP_sf10 | -1.20% | -1.91% | -2.07% | -1.77% |
| **SIFT_sf1** | **-32.08%** | **-28.95%** | **-31.58%** | **-32.63%** |
| SIFT_sf10 | -10.72% | -10.20% | -10.22% | -10.47% |
| **SSN_sf1** ⚠️ | +2.34% | +1.35% | +1.73% | +1.56% |
| SSN_sf10 | +2.06% | +1.25% | +2.04% | +1.39% |
| WIKI_sf1 | -9.61% | -7.69% | -9.86% | -9.96% |
| YFCC_sf1 | -6.88% | -5.71% | -7.15% | -7.23% |
| YFCC_DL_sf1 | -4.89% | -4.22% | -2.18% | -4.12% |

**Distribution Sweet Spot**:
- imbalanced (cluster_ratio > 1.3) + low intrinsic dim (< 0.85) → LARGE improve
- balanced (SSN++ ratio 1.29 + intrinsic 0.88) → BERN ceiling boundary case (mild hurt)

**SSN++ ceiling 가설 confirmed (HIGH confidence)**:
- Norm CV 0.0049 (DEEP normalized 0 / SIFT 0.0932)
- Intrinsic dim ratio 0.8828 (DEEP 0.6771)
- BERN qerr 1.139 (8 cell 중 최저)
- KM20-to-BERN headroom 0.5% (vs SIFT 34.5%)

**YFCC 분포 검증**:
- 채림 적재본 (random_state=?) -7%
- build_yfcc test (random_state=42) -4%
- → direction 일관, size PCA fit 영향 (caveat)

---

## 3. 산출물 위치

### 분석 자료
- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft.md` (332 lines, W4 only narrative + §6.5 SSN ceiling + Limitation 9)
- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md` (partial fill 결과 자동 추가)
- `experiments/figures/w4_partial/` (13장 PNG: 4강 heatmap + per-cell ranking + distribution effect)
- `_internal/_w4_partial_summary.csv` (830 rows, 모든 cell × 25 method × 5 sel paired CI)
- `experiments/results/ssn_ceiling_results_20260507.json` (4 analyses raw)
- `experiments/results/ssn_bern_qerr_per_dataset_20260507.csv`

### 회의 자료
- `submission/_drafts/속도는벡터_5월8일회의_v1.pdf` (1.42 MB, 15 page)
- `submission/_drafts/속도는벡터_5월8일회의_v1.pptx` (73 KB, **native 100% 편집 가능, 양식 85%**) — 95%+ agent 진행 중
- `submission/_drafts/속도는벡터_5월8일회의_v1_image.pptx` (1.41 MB, image 백업)
- `submission/_drafts/속도는벡터_5월8일회의_v1.html` (56 KB)
- `submission/_drafts/academic_deck_5월8일회의/index.html` (1321 lines source)
- `submission/_drafts/속도는벡터_5월8일회의_PPT_outline.md` (454 lines)
- `submission/_drafts/속도는벡터_자문메일초안_W4_20260507.md` (채림 + 지도교수)

### Reference
- `Capstone/__5_27__v3_Academic.zip` (사용자 root 에 둔 academic v3 deck zip)
- `submission/_drafts/academic_deck_v3_source/academic-deck/` (압축 풀어둔 source — Slides.jsx + index.html + deck-stage.js)
- `속도는벡터 — 5_27 최종발표 (v3 Academic).pdf` (root, 18 slide PDF reference)

### Scripts (서버 + 로컬)
- 서버 `/mnt/hdd0/home/capstone2026/cache/`:
  - `prepare_cell.py` (NPY-only / --pg-update dual mode)
  - `rq3/chain_unified.py` (CELLS dict 에 YFCC_DL 1/10/100 추가됨)
  - `rq2_alloc_python.py` (NPY-first dual mode patched)
  - `analyze_15cell_w4.py` / `analyze_multi_w4.py` / `compare_yfcc_distributions.py`
  - `orchestrator.sh` (v6, sf10_SSN→NEW9 SSN auto, build_wiki_sf10→WIKI sf10 chain auto)
  - `yfcc_dl_pause_monitor.sh` (v2, 41GB SIGSTOP done)
  - `build_yfcc.py` (PCA fit + sf{1,10,100} build)
  - `build_strata_aux.py` (NPY → strata table — 미사용)
- 로컬 `_internal/scripts/`:
  - `master_v6_fill_partial.py`
  - `plot_w4_partial.py`
  - `build_native_pptx_5_8.py` (~900 lines, 11 helper)

---

## 4. 활성 작업 (22:15 KST, 14 server tmux + 1 local agent)

```
서버 (14 active):
  capstone (idle base) | orchestrator v6 (watching)
  sf1_NEW9_DEEP/SIFT/SSN/WIKI (NEW9 9 method 진행 ~30min ETA)
  sf10_NEW9_DEEP/SSN (DEEP=spectral 진행, SSN 진행)
  wiki_sf10 (orch trigger 됨, PG fetch 4M/8M)
  yfcc_dl_pipeline (YFCC_DL sf10 UPDATE 진행)
  yfcc_sf1 / yfcc_sf10 (chain 진행)
  multi_pipeline (deep_sift fetch 5.55M 1h+ stuck, autovacuum 경쟁)
  yfcc_dl (paused @ 41GB)

로컬 background agent (1 active):
  PPT 95%+ 정밀 재현 agent (aef5ec33 후속, Slides.jsx 분석 + helper 미세조정)
```

---

## 5. 다음 세션 즉시 actions

### 알림 수신 시 자동 처리 흐름
1. **WIKI sf10 chain done** (~22:30) → orchestrator v6 자동 NEW9 진행 + 분석 trigger 일부
2. **YFCC sf10 / YFCC_DL sf10 chain done** (~23:30) → 5 dataset × 2 scale 단일 매트릭스 완성
3. **multi-pipeline done** (~01:00) → 3 multi cell 완성
4. **모든 cell done** → orchestrator analyze auto (analyze_15cell + plot + compare_yfcc)
5. **05:00~09:00 5/8** → master_v6 final fill + PPT update + 회의 자료 finalize

### 즉시 모니터 명령
```bash
ssh capstone "tmux ls 2>&1 | wc -l; ls -lat /tmp/*_done.flag | head -10"
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && python3 analyze_15cell_w4.py 2>&1 | tail -25"
scp capstone:/tmp/w4_15cell_summary.csv /Users/hyunbin/Capstone/_internal/_w4_partial_summary.csv
python3 _internal/scripts/master_v6_fill_partial.py
python3 _internal/scripts/plot_w4_partial.py
python3 _internal/scripts/build_native_pptx_5_8.py  # PPT 재빌드
```

### 다음 세션 시작 prompt
```
@_internal/handoff_v7_session_20260507_2215.md 읽고 이어서 진행.
현재 W4 sprint 측정 진행 중 (sf1+sf10 5 dataset 거의 완성, multi-pipeline 진행).
5/8 19:00 회의용 자료 (master_v6 + figures + Native PPTX) 자동 finalize 진행.
PPT 95%+ 정밀 재현 agent (background) 결과 받으면 적용.
```

---

## 6. PG 상태 (검증된 정보)

- vanilla_sf100 instance pid 1136097 정상 동작 (port 55435, host=/tmp, db=USER=wns41559)
- partsupp_yfcc_pca_1 / partsupp_yfcc_pca_10 적재됨 (build_yfcc 결과)
- partsupp_wiki_1 (800K) / partsupp_wiki_10 (8M) 적재됨
- partsupp_yfcc_1 (800K, SQL extract from yfcc_10) 적재됨
- partsupp_deep/sift/fb 100 모두 80M 적재 (sf100 진행 시 사용 가능)
- partsupp_deep_sift_10 + partsupp_deep_wiki_10 + part_wiki_10 (multi-vector + multi-join) 적재
- HNSW UPDATE 매우 느림 → NPY-only mode 우선 + rq2_alloc NPY-first patch 적용

---

## 7. Critical 운영 원칙

- PG 백엔드 종료 시 `pg_terminate_backend(pid)` 사용 (SIGKILL 금지 — recovery mode 트리거)
- HDD 1개 → 동시 작업 너무 많으면 IO 경쟁 심함 (multi-pipeline 1h stuck 사례)
- chain_unified 의 method dispatch — `kde_pilot` 은 sf 모두 missing (online_weight/kde_pilot.py 없음, 8m runner 만 있고 main() 없음). 무시 가능 (negative control 후보)
- rq2_alloc_python.py NPY-first patch 가 sf10/sf100 의 stratum_id NULL 환경에서 RQ2 5mode 가능하게 함
- 4강 method (Hilbert/Hybrid/MB_partial/HDBSCAN) 결과는 모두 paired bootstrap CI 0 제외 (위 8/9 cell), narrative 강력
- master_v6 의 §6.5 (SSN ceiling 분석) 와 Limitation 9 가 narrative 정직성 핵심

---

**작성**: Claude Opus 4.7 1M, 통합 manager session, 2026-05-07 22:15 KST
**Context**: 본 세션 ~65% 사용, 다음 세션 깨끗한 context 로 진행 권장
