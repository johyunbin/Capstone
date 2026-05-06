# 핸드오프: RQ3 7-way 측정 완료 → 메인 세션 (2026-05-06 22:02 KST)

> **이번 세션 (병렬, 8M 보강 측정 동안)**: RQ3 7-way 측정 + 3 contributions 발견 + git push 2회. 5/8 회의 자료 ready.
> **메인 세션 (서버 점유)**: 8M 보강 측정 — setup 9시간 완료, 21:57:49 에 measurement phase 진입. 진행 중.

---

## ★ TL;DR (30초)

- **RQ3 7-way (DEEP 1M + SIFT 1.5M) 측정 완전 완료**. 측정 시간 12분 (sample_size 작은 환경 + warm cache).
- **3 contributions 확정**: (1) Hilbert Curve = learning-free contribution 1순위 (2) MiniBatch = production solution (3) Distance-Shell + IS = cluster 분할 결정적 가치 정량 증명.
- **commit 2개 push 완료**: [5cfb92c](https://github.com/johyunbin/Capstone/commit/5cfb92c) (1차) + [589d66e](https://github.com/johyunbin/Capstone/commit/589d66e) (2차).
- **분모 붕괴 caveat**: KM20 vs RANDOM20 격차 0.26~3.98% → primary metric `method_minus_random_pct` 로 변경.
- **8M 영향 X**: 우리 RQ3 측정 (21:43~21:45) 동안 8M PG query 가 13:00부터 active 였으므로 충돌 X.

---

## 1. 측정 완료 산출

### 1-1. 9 parquet (DEEP+SIFT 모두 포함)

| 파일 | method | rows | 측정 시간 |
|------|--------|------|----------|
| `cache/rq1/rq3_random20.parquet` | RANDOM20 (DEEP only) | 5K | 42s |
| `cache/rq1/rq3_random20_sift.parquet` | RANDOM20 (SIFT only) | 5K | 56s |
| `cache/rq1/rq3_km20.parquet` | KM20 oracle | 10K | 96s |
| `cache/rq1/rq3_minibatch.parquet` | MiniBatch K-means | 10K | 105s |
| `cache/rq1/rq3_random_proj.parquet` | Random Projection | 10K | 100s |
| `cache/rq1/rq3_hilbert.parquet` | Hilbert Curve | 10K | 104s |
| `cache/rq1/rq3_lsh.parquet` | LSH | 10K | 97s |
| `cache/rq1/rq3_kde_pilot.parquet` | KDE-pilot | 10K | 14s |
| `cache/rq1/rq3_distance_shell.parquet` | Distance-Shell | 10K | 9s |
| `cache/rq1/rq3_importance_sampling.parquet` | IS (4 mode factorial) | 25K | 98s |

local 회수: `experiments/results/rq3_agnostic/` 동일.

### 1-2. 분석 산출

| 파일 | 용도 |
|------|------|
| `experiments/results/rq3_agnostic/recovery_summary.csv` | 10 method × cell × {recovery, method_minus_random_pct, denom_pct} |
| `experiments/results/rq3_agnostic/wilcoxon_vs_random20.csv` | paired Wilcoxon + BH-FDR (분모 비교) |
| `experiments/results/rq3_agnostic/wilcoxon_vs_bern.csv` | paired Wilcoxon + BH-FDR (BERN 비교, RQ1/RQ2 metric) |
| `experiments/results/rq3_agnostic/RQ3_1차_결과정리.md` | 상세 결과 정리 (7-way 완성) |
| `submission/_drafts/속도는벡터_RQ3_1차결과정리_20260506.{md,pdf}` | **팀원 공유용 (5/8 회의 자료)** |
| `experiments/code/local_analysis/rq3_recovery_analysis.py` | 10 method 자동 분석 driver |

### 1-3. 신규 wrapper

| 파일 | 용도 |
|------|------|
| `experiments/code/rq3/run_km20.py` | KM20 oracle baseline (이번 세션 신규) |

---

## 2. 핵심 발견 — 3 contributions

### 2-1. Hilbert Curve (#7) — **본 연구 핵심 contribution 1순위 격상** ★

**측정 결과** (`method_minus_random_pct`, 음수=좋음):
- DEEP: -0.41% ~ -3.70%, 통계 유의 2/5
- SIFT: -1.41% ~ **-4.12%**, 통계 유의 4/5 (SIFT s=0.05/0.10 에서 MiniBatch 보다 우수)
- 가설 H3-E (20-60% recovery) **refute 좋은 방향 강** — 예상 훨씬 초과.

**Mechanism 분석** (서버 측 fit log 추출):
- PCA 2D explained variance: SIFT 22.0% > DEEP 12.3%
- Hilbert bucket max/min ratio 1.16~1.18 (매우 균질, quantile 분할 효과)
- vs MiniBatch 자연 cluster 비율 2.45~4.77

**narrative**: "learning-free + 결정론 stratification 도 oracle 수준 가능".

### 2-2. MiniBatch K-means (#8) — production-ready 솔루션 ★

- DEEP: -0.41% ~ -4.22%, 통계 유의 3/5
- SIFT: -1.42% ~ -3.67%, 통계 유의 5/5
- 가설 H3-F (75% 이상 recovery) **confirm 강**

### 2-3. Distance-Shell (#9) + IS (#11) — cluster 분할 결정적 가치 ★

본 연구의 **negative control 로서 가장 강한 결과**:
- **Distance-Shell**: 모든 cell +1.4 ~ +17% (cluster 정보 X 의 한계)
- **IS** (4 mode factorial): best -17%, worst **+866%** (분할 X 의 massive failure)
- **LSH/RandProj**: +0.6~+45% (단순 hash/projection 한계)

→ "stratification 의 가치는 cluster-aware 분할에서 온다" 의 정량 증명.

### 2-4. KDE-pilot (#10) — 부분 confirm

- SIFT mid-sel (s=0.05) 에서만 -3.28% 효과
- 가설 H3-B (50-80% recovery) 부분 confirm — pilot noise 한계.

---

## 3. ⚠️ 분모 붕괴 caveat — primary metric 변경

```
recovery_rate = (방법X − RANDOM20) / (KM20 − RANDOM20)
```

**측정 결과**: KM20 vs RANDOM20 격차 0.26~3.98% (분모 붕괴).
- DEEP s=0.05: 0.26% / s=0.10: 0.42% / s=0.30: 0.58% / s=0.50: 0.54%
- SIFT s=0.01: 0.86% (모두 1%p 이하 fall-back threshold)

**해결**: `recovery_rate.py` 의 사전 등록 fall-back 활성. **primary metric = `method_minus_random_pct`** (음수일수록 좋음, RANDOM20 대비 q_error 변동률).

**향후 sensitivity 후보**: sample_size 100/200/1000 에서 격차 회복 검증.

---

## 4. 8M 측정 (메인 세션 진행 중) 상태

- **PID 2146460** 12:57 시작, 9시간째 active (setup 8h59m + measurement 진입).
- 21:57:49 에 sel=0.1 system mode 첫 EXPLAIN ANALYZE 시작 — measurement phase 막 진입.
- `/tmp/measure_8m_done.flag` 없음 (완료 시 생성).
- 추정 ETA: handoff 의 "24:00" 보다 늦을 가능성 (setup 이 9h 걸린 점 고려).
- 우리 RQ3 측정은 같은 PG 55436 의 **다른 테이블 (DEEP 1M + SIFT 1.5M)** 이라 영향 X.

---

## 5. 다음 작업 후보 (메인 세션 영향 X)

### 5-1. A. **시각화** (5/8 회의 자료 임팩트 ↑) — 우선순위 1
- `experiments/code/local_analysis/rq3_figures.py` skeleton 활용
- 7-way bar chart (DEEP/SIFT × 7 method × 5 sel)
- recovery rate heatmap
- Hilbert vs MiniBatch cell-by-cell scatter
- 출력: `experiments/figures/rq3_*.png`

### 5-2. D. **8M dataset RQ3 wrapper 준비** — 우선순위 2
- `_measure_common.py` 의 DATASETS 에 8M 추가 (1 line):
  ```python
  {"name": "DEEP_8M", "table": "partsupp_deep_10_phase7_8m_subset", ...}
  ```
- 8M 끝난 후 즉시 7-way 8M 측정 시작 가능 (sensitivity 분석)
- 코드만 준비, 측정은 8M 메인 세션 종료 후

### 5-3. E. **CLAUDE.md / next_session_prompt update** — 우선순위 3
- RQ3 7-way 완료 상태 반영
- 5/8 회의 자료 ready 명시
- next priority: 시각화 → 자문 메일 → 슬라이드 초안

### 5-4. B. **5/8 회의 통합 보고서** (1-2 page)
- RQ1 + RQ2 + RQ3 합친 한 페이지 요약
- 카톡 §3.2 narrative 통합본 (7 method × 4단계)

### 5-5. C. **자문 요청 메일 초안** (5/15 마감)
- 채림 석사: Hilbert mechanism 정량 검증
- 지도교수: contribution 격상 + 학술 가치

### 5-6. F. **5/27 발표 슬라이드 초안** (5/26 마감)
- 핵심 3 contributions 슬라이드 구조
- Hilbert mechanism diagram

---

## 6. git 상태

```
main 브랜치, push 완료
  589d66e  RQ3 7-way 측정 완료 + 종합 결과 정리        ← 최신
  5cfb92c  RQ3 1차 측정 (offline 4종 + RANDOM20/KM20)
  f7a2a09  RQ3 진입 사전 작업 + 8M 보강 측정 스크립트  (이전 세션)
```

untracked (다른 세션 산출, 본 세션 commit 안 함):
- `submission/_drafts/속도는벡터_실험진행공유_20260506.{md,pdf}` — 다른 병렬 세션이 만든 듯, 별도 처리 필요

---

## 7. 5/8 19:00 회의 자료 (5/8 D-2 → 1.5일 남음)

✅ **준비 완료**:
- `submission/_drafts/속도는벡터_RQ3_1차결과정리_20260506.{md,pdf}` (팀원 공유용 7-way)
- 카톡 §3.1 시작 메시지 7개 (`_internal/RQ3_카톡_§31_시작메시지_7개_20260506.md`)
- 카톡 §3.2 narrative skeleton (a/b/c/d 모두 채움) (`_internal/RQ3_narrative_skeleton_20260506.md`)
- git push (5cfb92c + 589d66e)

⬜ **추가 권장** (5/8 전):
- 시각화 (7-way bar chart, heatmap) — 회의 자료에 즉시 합칠 수 있음
- RQ1 + RQ2 + RQ3 통합 1-page summary

---

## 8. 결정 트리

```
[메인 세션 8M 측정 완료 알림]
    ↓
git pull --no-rebase origin main → 본 핸드오프 read
    ↓
8M 산출 (cache/rq1/2026_05_06_8m_midsel/*.parquet) 회수 → analyze
    ↓
[추가 작업 선택]
    ├─ A 시각화 (즉시 가치, 5/8 임박)
    ├─ D 8M dataset RQ3 wrapper 준비 → 8M 끝난 후 sensitivity 측정
    ├─ E CLAUDE.md update
    └─ B/C/F 후속 작업
    ↓
[5/8 19:00 회의 자료 마감]
```

---

**작성**: 조현빈 (RQ3 측정 병렬 세션) · 2026-05-06 22:02 KST
**다음 트리거**: 메인 세션이 8M 끝낸 후 또는 새 세션에서 `cat _internal/handoff_RQ3_7way_to_main_20260506_2202.md`
