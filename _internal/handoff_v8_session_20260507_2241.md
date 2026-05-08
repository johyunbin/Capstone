# 통합 manager 세션 인계 v8 — 5/7 22:41 KST (W4 sprint 진행 중, PPT 양식 99% + 측정 9/15 cell)

> **이전 세션**: 5/7 22:15~22:41 KST, Opus 4.7 1M, context ~30% 사용 (메인 절약 위해 sub-agent 위임 위주).
> **인계 목적**: 14 active server tmux 진행 중 + PPT 양식 99% + 9 cell narrative 완성 상태에서 깨끗한 context 로 인계. 5/8 새벽~오전 자동 finalize.

---

## 1. 사용자 결정 누적 (절대 변경 금지, v7 와 동일)

1. **15-cell 매트릭스**: 6 dataset (DEEP/SIFT/SSN/WIKI/YFCC/YFCC_DL) × {sf1, sf10} = 12 단일 + multi (deep_sift_10, deep_wiki_10, multi-join) = 3 multi = **총 15 cell**
2. **YFCC vs YFCC_DL 분리**: YFCC = 채림 vanilla_sf100 적재본, YFCC_DL = build_yfcc.py 직접 build. PCA basis 비교용
3. **sf100 deferred**: 5/8 회의 후 자문 합의 후 진행
4. **Legacy 모두 무시**: SIFT 1.5M, BIGANN 1M, BIGANN 8M 모두 narrative 에서 제외. partsupp_*_{1,10,100} 패턴만
5. **모든 RQ1+RQ2+RQ3 필수**: 5/8 회의 전 sf1+sf10 5 dataset 의 RQ1/2/3 모두 측정 + multi
6. **YFCC raw 41GB 까지만 다운로드**. 5/8 회의 후 추가 결정
7. **PPT 양식**: academic v3 HTML deck (Slides.jsx React 컴포넌트) **양식 95%+ 정밀 재현 필요**. PDF/PPTX/HTML 모두 산출
8. **회의 자료 핵심**: 토의 + 편집 가능한 native PPTX (image-based 백업 별도)
9. **(v8 추가) PPT 추가 작업은 sf1/sf10 모두 완료 후 진행** — 사용자 요청 (5/7 22:41). 즉 NEW9 OPTICS/Spectral / WIKI_sf10 / YFCC_sf10 / YFCC_DL_sf10 / multi 3 끝나야 차트 재출력 + PDF/HTML/image.pptx 갱신.

---

## 2. 핵심 narrative (5/8 회의, v7 와 동일 — 9 cell 측정값 그대로 보존)

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

> **변경 절대 금지**. 이 표가 회의 narrative의 핵심. 측정 진행에 따라 method 추가될 수 있으나 cell × bern Δ% 는 그대로.

**Distribution Sweet Spot / SSN++ ceiling / YFCC 분포 검증** — v7 §2 와 동일.

---

## 3. 산출물 위치 (5/7 22:41 시점)

### 분석 자료 (mtime)
- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft.md` (332 lines, W4 only narrative + §6.5 SSN ceiling + Limitation 9)
- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md` **22:20** (463 lines, 9 cell fill)
- `experiments/figures/w4_partial/*.png` **22:20** (11장: 4강 heatmap + per-cell ranking 9 + distribution effect)
- `_internal/_w4_partial_summary.csv` **22:20** (830 rows, 9 cell × method × 5 sel paired CI)
- `experiments/results/ssn_ceiling_results_20260507.json`
- `experiments/results/ssn_bern_qerr_per_dataset_20260507.csv`

### 회의 자료 (PPT 양식 99% 완성, v8 핵심 추가)
- `submission/_drafts/속도는벡터_5월8일회의_v1.pptx` **22:37** (468 KB, 15 slides, **양식 99%**, native 100% 편집 가능, 5 PNG embed = S6/S8/S10/S11/S14)
- `submission/_drafts/속도는벡터_5월8일회의_v1.pdf` 20:57 (1.42 MB, **재생성 필요 — sf1/sf10 완료 후**)
- `submission/_drafts/속도는벡터_5월8일회의_v1_image.pptx` 21:58 (1.41 MB, **재생성 필요**)
- `submission/_drafts/속도는벡터_5월8일회의_v1.html` 20:55 (56 KB, **재생성 필요**)
- `submission/_drafts/academic_deck_5월8일회의/index.html` (1321 lines source — 5/8 회의용 deck)
- `submission/_drafts/속도는벡터_5월8일회의_PPT_outline.md` (454 lines)
- `submission/_drafts/속도는벡터_자문메일초안_W4_20260507.md`

### Reference (v7 와 동일)
- `Capstone/__5_27__v3_Academic.zip` (사용자 root 의 academic v3 zip)
- `submission/_drafts/academic_deck_v3_source/academic-deck/` (압축 풀어둔 source — Slides.jsx + index.html)
- `속도는벡터 — 5_27 최종발표 (v3 Academic).pdf`

### Scripts
- 서버 `/mnt/hdd0/home/capstone2026/cache/`: prepare_cell.py / chain_unified.py / rq2_alloc_python.py / analyze_15cell_w4.py / analyze_multi_w4.py / compare_yfcc_distributions.py / orchestrator.sh (v6) / yfcc_dl_pause_monitor.sh / build_yfcc.py
- 로컬 `_internal/scripts/`:
  - `master_v6_fill_partial.py`
  - `plot_w4_partial.py`
  - `build_native_pptx_5_8.py` (**1865 lines, v8 갱신** — `spc_em` 파라미터 + `add_chart_image` 헬퍼 추가, 폰트 3종 직접 사용)
  - `build_charts_5_8.py` (**474 lines, v8 신규** — Recharts SVG 5장 matplotlib 재현)

### 폰트 (v8 추가, 사용자 ~/Library/Fonts/ 설치됨, 재설치 불필요)
- JetBrains Mono v2.304: 32 ttf
- Inter v4.0: 38 ttf (InterVariable + extras)
- Pretendard v1.3.9: 19 ttf+otf (PretendardVariable + static)

---

## 4. 활성 작업 (22:41 KST, 14 active server tmux + 0 local agent)

### 15 cell 진척 표

| # | Cell | RQ1/2 base | RQ3 25 method | NEW9 9 method | 4miss | 현재 stage | 진척 |
|---|---|:-:|:-:|:-:|:-:|---|:-:|
| 1 | DEEP sf1 | ✅ 11:24 | ✅ | ⏳ OPTICS | ✅ 12:17 | `rq3_optics` | ~95% |
| 2 | DEEP sf10 | ✅ 10:46 | ✅ 09:21 | ⏳ Spectral | – | `rq3_spectral` | ~90% |
| 3 | SIFT sf1 | ✅ 11:24 | ✅ | ⏳ OPTICS | ✅ 12:17 | `rq3_optics` | ~95% |
| 4 | SIFT sf10 | ✅ 10:47 | ✅ 09:34 | ✅ 11:58 | – | (완료) | **100%** |
| 5 | SSN sf1 | ✅ 11:24 | ✅ 08:46 | ⏳ OPTICS | ✅ 12:17 | `rq3_optics` | ~95% |
| 6 | SSN sf10 | ✅ 10:47 | ✅ 11:17 | ⏳ Spectral | – | `rq3_spectral` | ~90% |
| 7 | WIKI sf1 | ✅ 09:47 | ✅ | ⏳ OPTICS | – | `rq3_optics` | ~95% |
| 8 | WIKI sf10 | ⏳ build✅ 12:27 | ⏳ chain | – | – | (idle 화면, 점검 필요) | ~30% |
| 9 | YFCC sf1 | ✅ | ✅ | ⏳ OPTICS | – | `rq3_optics` | ~95% |
| 10 | YFCC sf10 | ⏳ | ⏳ | – | – | `rq3_hdbscan` | ~60% |
| 11 | YFCC_DL sf1 | ✅ | ✅ | ⏳ | – | (chain) | ~90% |
| 12 | YFCC_DL sf10 | ⏳ | – | – | – | `rq1_km_k_10` (초기) | ~15% |
| 13 | multi: deep_sift_10 | – | – | – | – | `multi_pipeline` 22:23 "=== done ===" | ? (점검) |
| 14 | multi: deep_wiki_10 | – | – | – | – | (확인 필요) | ? |
| 15 | multi: multi-join | – | – | – | – | (확인 필요) | ? |

### Active tmux (서버)
```
capstone (idle base) | orchestrator v6 (watching, 22:41 idle)
sf1_NEW9_DEEP/SIFT/SSN/WIKI (rq3_optics 진행, ETA ~23:30 KST)
sf10_NEW9_DEEP/SSN (rq3_spectral 진행, ETA ~01:00 KST)
wiki_sf10 (build 12:27 done, chain 진행 또는 정체 ⚠️)
yfcc_dl_pipeline (rq1_km_k_10 for YFCC_DL_sf10, ETA ~02:00 KST)
yfcc_sf1 / yfcc_sf10 (yfcc_sf10 = rq3_hdbscan ETA ~23:00 KST)
multi_pipeline (22:23 "=== done ===" — 어떤 multi cell 완료?)
yfcc_dl (paused @ 41GB)
```

### 점검 필요 항목 ⚠️ (5/8 새벽 세션이 즉시 확인할 것)
1. **`wiki_sf10` tmux 빈 화면** — `tmux capture-pane -t wiki_sf10 -p | tail -30` 으로 chain 진행 여부 확인. 만약 stuck 이면 strace / iostat 로 PG fetch 경합 점검.
2. **`multi_pipeline` 의 22:23 "=== done ===" 메시지** — `tmux capture-pane -t multi_pipeline -p | tail -50` 로 어떤 multi cell (deep_sift_10 / deep_wiki_10 / multi-join) 이 끝났는지 확인. 결과 파일: `/mnt/hdd0/home/capstone2026/cache/_4way_meta.json` 참조.

---

## 5. 다음 세션 즉시 actions

### 알림 수신 시 자동 처리 흐름 (v7 §5 + v8 갱신)

1. **sf1 NEW9 OPTICS done × 5종** (~23:30) → `analyze_15cell_w4.py` 재실행 → master_v6 fill → plot 갱신
2. **YFCC sf10 chain done** (~23:00) → 위 동일 + cell 10 row 추가
3. **sf10 NEW9 Spectral done × 2종** (~01:00) → 동일
4. **WIKI sf10 / YFCC_DL sf10 chain done** (~02:00) → 동일
5. **multi 3 cell done** → `analyze_multi_w4.py` 추가 분석
6. **15 cell 모두 done** → 최종 master_v6 fill + plot + **차트 5장 재출력 + PPTX/PDF/HTML/image.pptx 모두 재생성**

### 즉시 모니터 명령 (5/8 새벽 세션 시작 시)

```bash
# 1. 서버 상태 빠른 확인
ssh capstone "tmux ls 2>&1 | wc -l; ls -lat /tmp/*_done.flag | head -15"

# 2. WIKI sf10 / multi_pipeline 상세 점검 (점검 필요 항목)
ssh capstone "tmux capture-pane -t wiki_sf10 -p | tail -30; echo '---'; tmux capture-pane -t multi_pipeline -p | tail -50"

# 3. analyze 재실행 + scp
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && python3 analyze_15cell_w4.py 2>&1 | tail -25; echo '---'; python3 analyze_multi_w4.py 2>&1 | tail -25"
scp -q capstone:/tmp/w4_15cell_summary.csv /Users/hyunbin/Capstone/_internal/_w4_partial_summary.csv

# 4. master fill + plot
cd /Users/hyunbin/Capstone && python3 _internal/scripts/master_v6_fill_partial.py
cd /Users/hyunbin/Capstone && python3 _internal/scripts/plot_w4_partial.py

# 5. (15 cell 완성 시점) 차트 재출력 + PPTX 재빌드
cd /Users/hyunbin/Capstone && python3 _internal/scripts/build_charts_5_8.py
cd /Users/hyunbin/Capstone && python3 _internal/scripts/build_native_pptx_5_8.py

# 6. PDF/HTML/image.pptx 재생성 (스크립트 별도, 사용자 또는 sub-agent 진행)
#    - 현재 build_native_pptx_5_8.py 는 native PPTX 만 생성
#    - PDF/HTML/image.pptx 는 별도 단계 필요. 다음 세션이 가능 (Keynote/LibreOffice 사용 또는 별도 빌드 스크립트 작성)
```

### 다음 세션 시작 prompt

```
@_internal/handoff_v8_session_20260507_2241.md 읽고 이어서 진행.
PPT 양식 99% 완성됨 (폰트 3종 + 차트 5장 + spc XML). 단 측정 미완 6 cell 완료될 때까지 PPT 추가 작업 보류.
sf1/sf10 모두 완료 후 (a) 차트 5장 재출력 (b) build_native_pptx_5_8.py 재빌드 (c) PDF/HTML/image.pptx 재생성 진행.
점검 필요: WIKI sf10 chain / multi_pipeline done 상세.
```

---

## 6. PG 상태 (v7 와 동일)

- vanilla_sf100 instance pid 1136097 정상 동작 (port 55435, host=/tmp, db=USER=wns41559)
- partsupp_yfcc_pca_1 / partsupp_yfcc_pca_10 적재됨
- partsupp_wiki_1 (800K) / partsupp_wiki_10 (8M) 적재됨
- partsupp_yfcc_1 (800K) 적재됨
- partsupp_deep/sift/fb 100 모두 80M 적재
- partsupp_deep_sift_10 + partsupp_deep_wiki_10 + part_wiki_10 (multi-vector + multi-join) 적재
- HNSW UPDATE 매우 느림 → NPY-only mode 우선

---

## 7. Critical 운영 원칙 (v7 와 동일 + v8 추가)

- PG 백엔드 종료 시 `pg_terminate_backend(pid)` 사용 (SIGKILL 금지)
- HDD 1개 → 동시 작업 너무 많으면 IO 경쟁 심함
- chain_unified 의 `kde_pilot` 은 sf 모두 missing — 무시 가능
- rq2_alloc_python.py NPY-first patch 가 sf10/sf100 stratum_id NULL 환경에서 RQ2 5mode 가능
- 4강 method 결과는 모두 paired bootstrap CI 0 제외 (8/9 cell), narrative 강력
- master_v6 의 §6.5 (SSN ceiling 분석) 와 Limitation 9 가 narrative 정직성 핵심
- **(v8 추가) PPT 양식 99% 잔여 1%** = PPT 의 letter-spacing 렌더링이 브라우저와 미세 차이 (PPT 포맷의 본질적 한계). 추가 fix 시도 금지.
- **(v8 추가) 폰트 설치 검증**: `unzip -p submission/_drafts/속도는벡터_5월8일회의_v1.pptx ppt/slides/slide1.xml | grep -E "(JetBrains|Inter|Pretendard)"` 가 hit 해야 함. fallback (Apple SD Gothic Neo / Menlo / Helvetica) 모두 제거됨.

---

## 8. PPT 99% 작업 정합 (v8 신규 섹션)

### v8 세션에서 완료한 작업 (5/7 22:15~22:41)

1. **W4 master_v6 finalize**: analyze 재실행 (12:49 → 13:20) + scp + fill_partial + plot. 9 cell narrative 동일 보존.
2. **PPT 양식 95% → 99% 도약**:
   - 폰트 3종 설치 (~/Library/Fonts/): JetBrains Mono / Inter / Pretendard
   - Recharts SVG 차트 5장 matplotlib 재현 (S6 forest / S8 funnel / S10 scatter / S11 multi-cell / S14 limitation)
   - 음의 자간 spc XML 헬퍼 추가 + 표지 / hero / mono label 적용
   - flex grid EMU 산식 검증 (sub-pixel < 4 EMU, 보정 불필요)
   - Pretendard Variable 직접 사용 (fallback 제거)
3. **build_native_pptx_5_8.py 갱신**: 1787 → 1865 lines (+78). 측정 결과 fill 후 재실행 가능.
4. **build_charts_5_8.py 신규**: 474 lines. 측정 결과 변경 시 재실행으로 차트 갱신.

### 미완 작업 (sf1/sf10 모두 완료 후 진행)

1. **차트 5장 데이터 재반영**: NEW9 OPTICS/Spectral 결과 + WIKI sf10 / YFCC sf10 / YFCC_DL sf10 / multi 3 cell 측정값을 차트에 반영. `build_charts_5_8.py` 재실행만으로 가능.
2. **PPTX 재빌드**: `build_native_pptx_5_8.py` 재실행. 측정값 + 차트 자동 fill.
3. **PDF/HTML/image.pptx 재생성**:
   - PDF: LibreOffice headless 또는 Keynote export 또는 `python3 _internal/scripts/md2pdf.py` (PPT 용 별도 스크립트 작성 필요)
   - HTML: deck-stage.js 의 React 빌드 또는 academic_deck/index.html 의 측정값 갱신
   - image.pptx: PDF 의 각 페이지를 png 로 변환 후 PPTX 에 image embed (별도 스크립트)

### 시각 검증 권장 (5/8 회의 직전)

사용자가 Keynote/PowerPoint 로 직접 열어서:
1. **Pretendard 한글 렌더링** (S2 목차 / S3 RQ 카드 / 본문 전반)
2. **표지 "Skew-Aware" tight letter-spacing** (-0.03em 적용)
3. **5장 차트 위치/사이즈** (S6 forest / S8 funnel / S10 scatter / S11 multi-cell / S14 limitation)
4. **S8 funnel + S10 scatter 라벨 가독성**

---

**작성**: Claude Opus 4.7 1M, 통합 manager session, 2026-05-07 22:41 KST
**Context**: 본 세션 ~30% 사용 (sub-agent 위임 위주). 다음 세션 깨끗한 context 로 진행 권장.
**다음 회의**: 5/8 19:00 KST 비대면 회의. 측정 finalize + PPT 재빌드 자료 ready 목표.
