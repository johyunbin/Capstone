# Handoff v28 — v5 narrative extension 측정 launch (5/15 22:00)

> 5/15 21:00 ~ 22:00 (1h) 본 세션 진행. handoff v27 → v28. 핵심: experiments/results inventory + Type matrix gap 식별 + measure_paper_exact.py 통합 + tmux v5_ext launch (91 file, 5/16 새벽 완료 예상).

---

## 1. 본 세션 진행 요약

| 시점 | 영역 |
|---|---|
| 21:23 | 세션 시작 + handoff v27 + narrative v5 read |
| 21:25 | experiments/results inventory (1352 file 정확 확인) |
| 21:35 | Type matrix gap 식별 (Type 1/2/4a/4b 각 1 cell 만 evidence weak) |
| 21:40 | DEEP+WIKI A2-Fig9 중복 발견 (hyphen vs underscore prefix) |
| 21:42 | 사용자 결정: P1+P3a+P5 launch (~120 file) |
| 21:45 | measure_paper_exact.py 통합 (cell 5 추가 + STRATA_K override + server fit_time 패치 merge) |
| 21:46 | tmux v5_ext launch (91 file 측정) |
| 21:50 | monitor background 띄움 + handoff v28 작성 |

---

## 2. Phase 1+2+4 inventory 결과

### 1352 file 정확 align ✓

| Type | 정의 | cell | dir | file | gap |
|---|---|---|---|---:|---|
| Type 1 | small sf=1 | DEEP A5-scale-sf1 | DEEP_96d/A5-scale-sf1_* | 140 | ★ SIFT/SSN sf=1 측정 X |
| Type 2 | medium sf=10 | DEEP A5-scale-sf10 | DEEP_96d/A5-scale-sf10_* | 138 | ★ SIFT/SSN sf=10 측정 X |
| Type 3 | large sf=100 | DEEP A1/A4/A5-sf100 + SIFT A1 + SSN A1 | (5 cells) | 693 | ✓ |
| Type 4a | large multi 288d | DEEP+YFCC A2-Fig7 | YFCC_192d/A2-Fig7_* | 146 | ★ 다른 multi-table 중차원 X |
| Type 4b | large multi 864d | DEEP+WIKI A2-Fig9 | DEEP+WIKI_864d/A2-Fig9_* | 214 (중복) | ★ 다른 고차원 X |

총: 140+138+693+146+214 + 12 (scope외) + 9 paper extras = **1352 ✓**

### Phase 4 outlier 발견

DEEP+WIKI_864d/A2-Fig9_RQ3_CaseB: 13 file 中 hyphen / underscore prefix 중복
- `A2-Fig9_CaseA_*` 4 method (pca1d 빠짐)
- `A2-Fig9_CaseB_*` 4 method (pca1d 빠짐)
- `A2_Fig9_CaseB_*` 5 method (pca1d 포함, **별도 byte size**)

같은 timestamp 1초 차 → 두 번 launch 흔적. **정본 결정 필요** (다음 세션):
- hyphen prefix 정본 추정 (pca1d 누락 → underscore 에서 pca1d 살려야 함)

---

## 3. measure_paper_exact.py 통합 변경 (1407→1456 line)

### 3.1 통합 영역

**Local fix**:
- line 45-49: STRATA_K 환경변수 override (P5 K granularity launch)
- line 282-314: v5 narrative cell 5 추가 (P1 4 + P3a 1)

**Server fix (5/15 fittime 측정 시 추가됨, server 만 있던 패치)**:
- line 938 + 1043: `t_fit_start` / `t_cache_start` 분리
- line 994-995, 1104-1105: `fit_time_sec` / `cache_time_sec` JSON output 추가

본 세션 변경: server file (1419 line) 위에 local 의 cell + STRATA_K override 추가 → 1456 line 통합 file 생성 → local + server 양쪽 동기화 완료.

### 3.2 통합 file 검증

```
local : /Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py (1456 line)
server: /mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py (1456 line)
backup: measure_paper_exact.py.bak_v5_20260515_2145 (local + server)
```

### 3.3 dry-run 검증 ✓

```
A5-scale-sf1-SIFT: dataset=SIFT sf=1 table=partsupp_sift_1 queries=['q3','q5','q20']
A6-WIKI-sf10:      dataset=WIKI sf=10 table=partsupp_wiki_10 queries=['q3','q10','q12']
STRATA_K=10 + A1-SIFT: [OVERRIDE] STRATA_K env → mc.N_STRATA = 10 ✓
```

---

## 4. tmux v5_ext launch (91 file)

### 4.1 launch script

`/mnt/hdd0/home/capstone2026/_internal/scripts/launch_v5_ext_5_15.sh`
+ local copy: `/Users/hyunbin/Capstone/_internal/scripts/launch_v5_ext_5_15.sh`

### 4.2 scope

| 영역 | cell | mode × method | file |
|---|---|---|---:|
| **P1** (Type 1/2 SF axis 확장) | A5-scale-sf1-SIFT / sf10-SIFT / sf1-SSN / sf10-SSN | B1 + CaseA × 5 + CaseB × 5 | 44 |
| **P3a** (Type 4b single baseline) | A6-WIKI-sf10 | B1 + CaseA × 5 + CaseB × 5 | 11 |
| **P5** (K granularity dataset 확장) | A1-SIFT / A1-SSN × K=10/30 | B1 + CaseA × 4 + CaseB × 4 | 36 |

총: **91 file**, 추정 server time **3-15h** (sparse_rp 12초/file 측정, 다른 method 더 오래)

Pareto Top 5: sparse_rp / chao_weighted / hilbert_real / hyperloglog / pca1d
K anchor 4: sparse_rp / chao_weighted / hilbert_real / hyperloglog (pca1d 제외)

### 4.3 launch 출력 디렉토리

`/mnt/hdd0/home/capstone2026/results_v5_ext_20260515_1245/`
- `A5-scale-sf1-SIFT/` 등 cell 별 sub-dir
- `logs/_main.log` (전체 진행)
- `COMPLETE.flag` (완료 신호)

### 4.4 측정 정상 시작 확인 ✓

21:46:02 첫 sparse_rp CaseB 측정 시작 → 21:46:13 완료 (10 trial × 1000 query, ~11초). fit_time 0.35s / cache_time 0.16s 정상 분리 ✓.

---

## 5. 본 세션 보류 영역 (P2/P3b/v9 paste)

| 영역 | 이유 | 다음 세션 |
|---|---|---|
| **P2** (multi-table 중차원 추가) | partsupp_deep_yfcc 같은 새 build 10+h 필요 | server build + measure |
| **P3b** (multi-table 고차원 SSN+WIKI 등) | 새 multi-table build 필요 | server build + measure |
| **claude.ai/design v9 paste** | 사용자 직접 paste 가 효율적 | 사용자 진행 |
| **DEEP+WIKI A2-Fig9 중복 정리** | 측정 launch 우선 | 다음 세션 정본 결정 + underscore prefix file archive |

---

## 6. 다음 세션 action (5/16 morning 예상)

### 즉시
1. **측정 결과 회수**: `/mnt/hdd0/home/capstone2026/results_v5_ext_20260515_1245/` 91 file rsync to local
2. **COMPLETE.flag 확인**: 측정 정상 완료 검증
3. **결과 분석**: paired Δ% + Type 별 method best 정리
4. **v5 narrative final update**: Type 1/2/4b evidence 보강 결과 반영

### 5/16 ~ 5/17 (D-10)
1. **DEEP+WIKI A2-Fig9 중복 정리**: hyphen 정본 + underscore prefix file 의 pca1d 만 카피 + 나머지 archive
2. **P2/P3b multi-table build 결정**: time/value trade-off 사용자 결정
3. **claude.ai/design v9 paste** (사용자 직접): deck v9 generate + 검토
4. **v5 narrative final + storyline v5 final**: 추가 측정 결과 + deck v9 align

### 5/27 발표 D-day
1. rehearsal + 정정 룰 8 영구 정리

---

## 7. 서버 + 측정 portfolio 상태

- server: 165.132.140.240 (capstone2026), /mnt/hdd0/home/capstone2026
- tmux: **v5_ext** session 진행 중 (5/15 21:45 ~ 5/16 새벽 예상)
- 측정 portfolio: 1352 file (paper exact 1001 + 추가 351) + **추가 91 file (본 세션 launch)** = 1443 file 예상
- monitor: local background tail (file count + error 감지)

---

## 8. 본 세션 commit chain

| commit | 시점 | 영역 |
|---|---|---|
| 6ac2cb5 | 21:35 | handoff v27 + storyline v4 + prompt v9 + outline v5 + 추가 측정 plan (이전 세션) |
| (본 commit) | 22:00 | handoff v28 + measure_paper_exact.py 통합 + launch_v5_ext_5_15.sh + tmux v5_ext launch |

---

## 9. 환각 회피 룰 (carry-over)

1. "영역" 의미 없는 반복 금지
2. 추상적 매핑 / 시뮬레이션 회피 — 사실 위주
3. 큰 블록 한 번에 작성 X — 작은 단위 Edit
4. commit 전 grep -c "영역" 검증

본 세션 적용 ✓: 작은 단위 Edit (cell 추가 + STRATA_K override 분리) + dry-run 검증 후 launch + fit_time 분리 측정 정상 출력 확인.

---

작성: 2026-05-15 22:00 KST · 본 세션 5/15 21:00 ~ 22:00 (1h) · Type matrix inventory + measure_paper_exact.py 통합 + v5_ext tmux launch (91 file) 완료
