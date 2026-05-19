# Handoff v4 — 5/10 21:08~21:44 세션 진행 + 자동 chain 설정

> 이 세션이 종료/단절돼도 새 세션이 0% loss로 이어가기.
> handoff_main_session_FULL_STATE_20260510_2045.md (16 sections) 의 후속.

---

## 0. TL;DR — 새 세션 즉시 액션

1. SSH: `ssh capstone2026@165.132.140.240 "date"` (ed25519 등록됨)
2. 측정 진행: `ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json | wc -l"` (현재 316/702, ETA 5/11 02-03시)
3. sigma 진행: `ssh capstone "tail -10 /mnt/hdd0/home/capstone2026/log/sigma_build_paper_exact_20260510_1240.log"`
4. tmux session: `ssh capstone "tmux ls | grep -E 'sigma_build_pe|rq2_pe'"`
5. **자동 chain monitor가 설정됨** — 측정+sigma 완료 시 분석 + RQ2 launch + 분석 2차 (총 4단계)
6. 만약 monitor 끊겼으면 새 monitor 시작 (아래 §3 명령)

---

## 1. 이 세션 (5/10 21:08~21:44) 작업

### 1.1 코드 수정 — server scp 완료
| File | 변경 | server md5 / size |
|---|---|---|
| `_internal/scripts/analyze_paper_exact.py` | CaseB analysis (`load_case_b_results`, `analyze_phase_c`, `analyze_caseb_vs_casea`) + 5단계 narrative §4/§5 auto-fill | 20764 bytes (5/10 12:27 server) |
| `_internal/scripts/_measure_common.py` | `fetch_stratum_sigmas` + `neyman_alloc` + `anti_neyman_alloc` + run_method_measurement modes loop 확장 | md5 1964d30b... |
| `_internal/scripts/measure_paper_exact.py` | measure_rq2_paper_exact modes = 5-way ("bernoulli", "equal", "proportional", "neyman", "anti_neyman") | md5 eb3b9d6b... |
| `_internal/scripts/compute_stratum_sigma_paper_exact.py` | **신규** — NPY mmap 기반 σ_j 빌드 (DEEP/SIFT/SSN sf=100), KM20 cluster, sel=0.1 D_target | 6326 bytes |

### 1.2 tmux session 신규
- `sigma_build_pe` — compute_stratum_sigma_paper_exact.py 진행 중 (PID 3429378 wrapper / 3429380 python)
- `rq2_pe` — **자동 launch 예정** (sigma + 측정 완료 시)

### 1.3 paired_delta() bug fix
- `analyze_paper_exact.py` early return의 dict key 불일치 → `_NAN_DELTA` 상수 통일

### 1.4 검증 세션 (5/10 20:30~20:46) 결과 통합 — validation 정정 (21:48~21:54)

두 검증 세션 결과 메인 세션에 도착:
- **handoff_v3** (method audit, 8 agent / 5,777 lines) — 41 method 中 30+ critical defect
- **handoff_back** (validation statistics, 4 layer audit) — paper Fig 12 영역 분리 등

#### analyze_paper_exact.py validation 정정 (server scp md5 26f12822)
- **§2.1 Fig 12/13 영역 분리** — `FIG_12_CELLS={A1-DEEP,SIFT,SSN, A2-Fig7,Fig9, A5-scale-sf{1,10,100}}` (8 cells), `FIG_13_CELLS={A4-sel}` 분리. paper 1.69 비교는 Fig 12 영역만 → narrative #2 +25.5% → **−4.3%** (강화)
- **§2.3 CaseA outlier caveat** — `CASEA_OUTLIER_METHODS={lsh, RP, sobol, ccsketch, ams_count_sketch}` worse signif 카운트 (cluster imbalance 명시)
- **§2.4 one-sided greater Wilcoxon** — `wilcoxon_p_greater` 추가 (n=10 small sample power 향상). 두 alternative 모두 보고

#### memory 추가
- `feedback_method_audit_findings.md` — 41 method audit findings + Q1~Q5 결정 + paradigm 5→9 권고
- MEMORY.md 인덱스 갱신

#### 사용자 confirm 필요 (Q1~Q5)
- Q1 ★3 hilbert: 권고 (C) `pca2d_lex` rename + 진짜 hilbert 별도 추가
- Q2 10건 폐기: 권고 모두 폐기
- Q3 P6 폐지 vs P9/P10 신규: 권고 (B) 9 paradigm 확장
- Q4 Tier 1 6 method 추가: 권고 진행 (DBSCAN/KDE/MHIST-2/HyperLogLog/randomized SVD/wavelet histogram)
- Q5 handoff_v2 5 paper exact decisions: 별도 confirm (Fig 5 dataset별 queries / min/max bound 제거 / sel paper subset / A3 ECQO 분리 / Q-error+wall-clock)

---

## 2. 자동 chain monitor 설정 (5/10 22:06 sigma kill + 재구성)

### 2.1 sigma builder kill 사유
- 21:40 launch → 27분 동안 stratum 0 fancy indexing on 30GB mmap NPY (page cache contention)
- 측정 procs와 NPY 동시 access → memory available 60GB 이하
- log 진행 X (stratum 0 finishing print 안 옴) — RAM 압박이 큰 위험
- 22:06 kill (PID 3429380) → 메모리 60GB → 204GB 회복

### 2.2 새 monitor (task `bdrhrddyb`, persistent)
sequential chain:
- 측정만 모니터 (60s polling)
- `act=0` AND `cnt>300` 시 trigger:
  - **Step 1/4**: 분석 1차 (`python3 analyze_paper_exact.py` — Fig 12 영역 분리 + one-sided greater 적용된 코드)
  - **Step 2/4**: sigma builder launch (tmux `sigma_build_pe`) + 180s polling 대기 (자원 충분, 15-45분 예상)
  - **Step 3/4**: RQ2 5-way launch (tmux `rq2_pe`, `--rq 2`) + 180s polling 대기 (~30분)
  - **Step 4/4**: 분석 2차 (`python3 analyze_paper_exact.py` — RQ2 Neyman/Anti 데이터 포함)
  - COMPLETE break

이전 `bj5faiujf` (병렬 sigma+측정) 폐기. sigma는 측정 끝난 후 sequential 진행이 안전.

---

## 3. monitor 끊겼을 시 재시작 명령

```bash
# Monitor (Claude Code MCP) 재시작 명령:
# description: 측정+sigma persistent 모니터 — 완료 시 분석 + RQ2 자동 trigger
# timeout: 3600000ms, persistent: true
```

명령 본문은 `_internal/handoff_v4_session_20260510_2144.md` 에서 복사 또는 위 §2 의 흐름 직접 코딩.

핵심 trigger script:
```bash
prev=0; first=1; sigma_prev=""; loop=0
while true; do
  data=$(ssh -o ConnectTimeout=15 capstone2026@165.132.140.240 "
    cnt=\$(ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json 2>/dev/null | wc -l);
    act=\$(pgrep -af measure_paper | grep -v grep | wc -l);
    sigma_act=\$(pgrep -af compute_stratum_sigma_paper_exact | grep -v grep | wc -l);
    sigma_last=\$(tail -1 /mnt/hdd0/home/capstone2026/log/sigma_build_paper_exact_*.log 2>/dev/null | head -c 100);
    printf '%s|%s|%s|%s\n' \"\$cnt\" \"\$act\" \"\$sigma_act\" \"\$sigma_last\"
  " 2>/dev/null)
  cnt=$(echo "$data" | head -1 | cut -d'|' -f1 | tr -d ' \n\r')
  act=$(echo "$data" | head -1 | cut -d'|' -f2 | tr -d ' \n\r')
  sigma_act=$(echo "$data" | head -1 | cut -d'|' -f3 | tr -d ' \n\r')
  sigma_last=$(echo "$data" | head -1 | cut -d'|' -f4-)
  [[ ! "$cnt" =~ ^[0-9]+$ ]] && { sleep 60; loop=$((loop+1)); continue; }
  ts=$(date '+%H:%M KST'); loop=$((loop+1))
  # ... (alert + trigger logic, 위 §2 참조)
done
```

---

## 4. 진행 상태 (5/10 21:44 KST 기준)

### 측정 (Phase A B1 + Phase B/C Tier 1 완료, extra/extra2 진행)
- Total: **316/702** (45%)
  - B1: 9 ✅
  - CaseA: 204 (Tier 1 99 + extra/extra2 105)
  - CaseB: 112 (Tier 1 99 + extra 13)
- Active procs: 22
- ETA: **5/11 02-03시 KST**
- 진행 분당 ~+0.5건 (NPY fetch SF=100 22분 bottleneck)

### Sigma 빌드 (sf=100 paper exact 신규)
- 시작: 21:40:13
- 진행: DEEP sf=100 (partsupp_deep_100) — 100 queries load 완료, stratum 0~19 cluster materialize 진행 중
- ETA: **5/10 23~24시 KST** (DEEP/SIFT/SSN 순차)
- log: `/mnt/hdd0/home/capstone2026/log/sigma_build_paper_exact_20260510_1240.log`

### System
- Memory: 1007GB total / 142GB available
- Load: 1min=39.97 / 5min=56.24 / 15min=51.40 (줄어드는 추세)
- 23 active procs (측정) + 1 sigma builder

---

## 5. 자동 chain 완료 후 산출물

### 1차 분석 (측정+sigma 완료 시 자동 trigger)
- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md`
- 5단계 narrative §1~§5 auto-fill (Phase A B1 + RQ1/RQ2 + CaseA + CaseB + final ranking)

### RQ2 5-way 측정 (자동 launch)
- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/rq2_paper_exact_DEEP_sf100.csv`
- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/rq2_paper_exact_SIFT_sf100.csv`
- 각 5 modes × 2 sel × 5 seed × 100 query = 5000 rows / dataset
- log: `/mnt/hdd0/home/capstone2026/log/rq2_paper_exact_5way_*.log`

### 2차 분석 (RQ2 완료 시 자동 trigger)
- 위 REPORT.md 갱신 — RQ2 §2.2에 Neyman/Anti 결과 포함

---

## 6. 사용자 복귀 시 (5/11 새벽 예상)

### 즉시 확인
1. `cat /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md` — 자동 생성된 5단계 narrative
2. `tail -50 /mnt/hdd0/home/capstone2026/log/rq2_paper_exact_5way_*.log` — RQ2 5-way 결과
3. `tail -30 /mnt/hdd0/home/capstone2026/log/sigma_build_paper_exact_20260510_1240.log` — σ_j 값
4. monitor stream 마지막 message — `=== COMPLETE PIPELINE FINISHED ===` 확인

### 후속 작업 (RQ2/Phase D 결과 보고)
- 5/27 최종발표 storyline 7단계 (handoff §11.6) finalize
- A2-Fig8 (multi-vector stratum_id 부재) post-fix
- A3-TPCDS (ECQO PG crash) post-fix — Exqutor source 분석 필요
- 박세은/이동욱/강재현 팀원 공유 (RQ2 paper exact + CaseB ensemble narrative)

---

## 7. 5/27 최종발표 storyline 7단계 (handoff §11.6 verbatim, RQ2/CaseB 결과 후 finalize)

| # | 단계 | 현재 상태 |
|---|---|---|
| 1 | 단일 random sampling skew 부정확 | RQ1 paper exact 5% 격차 ✓ |
| 2 | 분포 알면 Neyman 답 | RQ2 paper exact 9% 격차 ✓ (Bernoulli/Equal/Prop) — Neyman/Anti 진행 중 |
| 3 | 분포 모르니까 추정 활용 | RQ3 5 paradigm × 11 method (이전 narrative) |
| 4 | 단일 Adaptive 대비 평균 -8% | Phase B/C Tier 1 완료 ✓ — minibatch_partial -7.41%, ensemble -2~-7% |
| 5 | multi-table 일반화 X (0/66) | RQ3 multi 영역 (이전 narrative) |
| 6 | 신규 method 발굴 single+multi 모두 강한 방식 | Phase B/C extra 진행 중 (28 NEW methods) |
| 7 | Adaptive 단독 vs Adaptive + 우리 ensemble climax | CaseB ensemble 6 methods -2~-7% ✓ — 추가 28 methods 결과 후 finalize |

---

## 8. 핵심 파일 위치

### Local
- `_internal/handoff_v4_session_20260510_2144.md` (이 file)
- `_internal/handoff_main_session_FULL_STATE_20260510_2045.md` (16 sections, 모든 context)
- `_internal/handoff_v2_paper_verbatim_decisions_20260510_1418.md` (5 critical decisions)
- `_internal/scripts/analyze_paper_exact.py` (427 lines, CaseB analysis 추가)
- `_internal/scripts/_measure_common.py` (~410 lines, neyman/anti 추가)
- `_internal/scripts/measure_paper_exact.py` (1100+ lines, RQ2 5-way)
- `_internal/scripts/compute_stratum_sigma_paper_exact.py` (신규, 165 lines)

### Server (`/mnt/hdd0/home/capstone2026/`)
- `cache/rq3/{analyze_paper_exact,_measure_common,measure_paper_exact,compute_stratum_sigma_paper_exact}.py` (모두 5/10 12:30+ KST 갱신)
- `cache/rq3/paper_exact/` (B1/CaseA/CaseB JSON + RQ1/RQ2 CSV + REPORT.md)
- `cache/rq1/{partsupp_*}_{vectors,strata,pks}.npy` (sf=1/10/100 모두 빌드)
- `log/paper_exact_phase_*.log`, `log/sigma_build_paper_exact_*.log`, `log/rq2_paper_exact_5way_*.log` (자동 생성)

### Memory
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/reference_exqutor_paper_verbatim.md`
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/feedback_paper_exact_principle.md`
- `~/.claude/projects/-Users-hyunbin-Capstone/memory/MEMORY.md`

---

## 9. END

작성: 2026-05-10 21:44 KST
세션 시간: 36분 (21:08 → 21:44)
다음 step: monitor `bj5faiujf` 자동 chain 진행 → 사용자 복귀 시 REPORT.md + RQ2 결과 검토 → 5/27 storyline finalize

**핵심**: 자동 chain monitor가 측정+sigma 완료 시 분석 1차 + RQ2 launch + 분석 2차 자동 진행. 사용자 복귀 시 REPORT_paper_exact.md 만 읽으면 모든 결과 확인 가능.
