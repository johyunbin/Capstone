# Handoff v6 — Smart Coordinator + 새 세션 인계 (5/11 01:25 KST)

> **목적**: 메인 세션 (이 세션) context 한도 정리 후 **새 세션이 monitor 인계**받아 내일 아침까지 자율 진행.
> **사용자 명시 (5/11 01:24)**:
> - "병렬로 진행중인 Organize capstone deliverables and documentation 세션 완료 후 너한테 보고할게"
> - "그 후 새 세션 시작 — context 한도 정리 목적"
> - "거기서 실험 모니터링 내일 아침까지 진행하도록"
> - "내가 자러 가더라도 실험 계속 진행해서 내일 아침에는 최대한 완료된 결과 볼 수 있도록"

---

## 0. 새 세션 즉시 액션 5단계

1. **MASTER_README.md read** (Organize 세션 완료 시 작성됨, 단일 진입점)
2. **본 handoff_v6 read** (smart coordinator 코드 + 인계 instruction)
3. **SSH 검증**: `ssh capstone2026@165.132.140.240 "date && pgrep -af measure_paper_exact | wc -l"`
4. **Smart coordinator v2 launch** (Monitor 도구 호출, §2 코드 verbatim 복붙)
5. **모니터 진행 모니터** (cnt 변화 + chain trigger + 자동 stuck/memory fix)

---

## 0.5 🚨 절대 룰 (사용자 강조 다수, handoff_main §4.2 / §5 + 채림님 메일 verbatim)

**다른 사용자 작업 절대 건드리지 말 것**:
- ❌ **PG port 55432, 55433** 사용 절대 X (다른 사용자 PG instances — postgres 55432 PIDs 319643/127176, sihyunkim2 55433)
- ✅ **우리 port 55435 active** + 55436 가용 (채림님 룰)
- ❌ **sudo 권한 없음** — system 변경 X
- ❌ **다른 사용자 procs kill X** — `pgrep -af measure_paper_exact` (우리 procs 이름만 match) 만 사용
- ❌ **/mnt/hdd0/home/{다른_user}/** 디렉토리 access X
- ✅ **우리 작업 dir만**: `/mnt/hdd0/home/capstone2026/`

**Smart coordinator monitor의 모든 명령은 위 룰 준수**:
- `pgrep -af measure_paper_exact` — 우리 측정 procs만 match (다른 사용자는 다른 cmd)
- `kill -TERM <pid>` — 우리 PID만 (pgrep 결과로 한정)
- `ssh capstone2026@...` — 우리 계정만 access
- `tmux new -d -s pb_*/sigma_*/rq2_*` — 우리 session prefix만

**위반 시**: 채림님 admin 통보 + 캡스톤 server access 차단 위험. 절대 X.

---

---

## 1. 현재 진행 상태 (5/11 01:53 KST 갱신, 다음 세션 인계용)

### 1.1 측정 진행
- **cnt: 466/702 (66%)** ↑ 26 (5/11 01:25 → 01:53)
- **procs: 30** (메인 20 + Phase 4 P0 6 + P1 5 = 11, 단 birch/vinecopula 일부 kill)
- **메모리 available: 200-300GB** (변동, 위험 시 자동 fix)
- 이전 측정 (5/11 01:25): cnt=440/702, procs=31

### 1.2 Phase 4 launch 완료 (11 tmux)
- pb_p4_chao_weighted, pb_p4_lpm1_proper, pb_p4_cum_sqrtf, pb_p4_lavallee_hidiroglou
- pb_p4_idistance, pb_p4_zorder_morton, pb_p4_skilling_hilbert, pb_p4_ica_fastica
- pb_p4_kmeans_neyman, pb_p4_rabitq_strat, pb_p4_idistance_neyman
- 각 method × 9 cells × 2 modes (CaseA + CaseB) = 198 cells

### 1.3 메인 chain (Phase B/C extra + extra2) — 미완료
- Tier 1 11 + extra 8 + extra2 20 = 39 method × cells
- 진행 중 (메인 procs 20개 cells loop)

### 1.4 자동 chain post (smart coordinator가 trigger)
- **trigger 조건**: 메인 측정 끝 (`main_act = 0` + `cnt > 650`)
- **chain 내용** (tmux `main_chain_post`):
  - Step 1: analyze 1차
  - Step 2: sigma builder (compute_stratum_sigma_paper_exact.py)
  - Step 3: RQ2 5-way (Bernoulli/Equal/Prop/Neyman/Anti)
  - Step 4: analyze 2차 (RQ2 포함)
- **최종 trigger**: Phase 4 + main chain post 모두 끝 → analyze 3차 → COMPLETE

---

## 2. Smart Coordinator v2 코드 (verbatim — 새 세션 Monitor 도구로 복붙 launch)

### 2.1 Monitor 도구 옵션
- `description`: `"Smart coordinator — stuck/memory auto-fix + chain trigger (persistent, 30s)"`
- `timeout_ms`: `3600000` (1시간 — auto re-arm)
- `persistent`: `true` (session 종료까지)

### 2.2 Monitor command (verbatim 복붙)

```bash
prev_cnt=0; first=1; loop=0; main_chain_done=0; final_done=0
P4_PAT="chao_weighted\|lpm1_proper\|cum_sqrtf\|lavallee_hidiroglou\|idistance\|zorder_morton\|skilling_hilbert\|ica_fastica\|kmeans_neyman\|rabitq_strat\|idistance_neyman"

while true; do
  loop=$((loop+1))
  ts=$(date '+%H:%M KST')

  data=$(ssh -o ConnectTimeout=15 capstone2026@165.132.140.240 "
    cnt=\$(ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json 2>/dev/null | wc -l)
    total_act=\$(pgrep -af measure_paper_exact | grep -v grep | wc -l)
    p4_act=\$(pgrep -af measure_paper_exact | grep -v grep | grep -E '$P4_PAT' | wc -l)
    main_act=\$((total_act - p4_act))
    mem=\$(free -m | awk '/Mem:/{print \$7}')
    stuck30=\$(find /mnt/hdd0/home/capstone2026/log/paper_exact_*.log -mmin +30 2>/dev/null | wc -l)
    chain_post=\$(pgrep -af 'compute_stratum_sigma_paper_exact\|measure_paper_exact.*--rq 2' | grep -v grep | wc -l)
    printf '%s|%s|%s|%s|%s|%s|%s' \"\$cnt\" \"\$main_act\" \"\$p4_act\" \"\$total_act\" \"\$mem\" \"\$stuck30\" \"\$chain_post\"
  " 2>/dev/null)

  cnt=$(echo "$data" | cut -d'|' -f1 | tr -d ' \n\r')
  main_act=$(echo "$data" | cut -d'|' -f2 | tr -d ' \n\r')
  p4_act=$(echo "$data" | cut -d'|' -f3 | tr -d ' \n\r')
  total_act=$(echo "$data" | cut -d'|' -f4 | tr -d ' \n\r')
  mem=$(echo "$data" | cut -d'|' -f5 | tr -d ' \n\r')
  stuck30=$(echo "$data" | cut -d'|' -f6 | tr -d ' \n\r')
  chain_post=$(echo "$data" | cut -d'|' -f7 | tr -d ' \n\r')

  if [[ ! "$cnt" =~ ^[0-9]+$ ]] || [[ ! "$mem" =~ ^[0-9]+$ ]] || [[ ! "$total_act" =~ ^[0-9]+$ ]]; then
    sleep 30; continue
  fi

  # Sanity check — total_act = 0이지만 cnt < 700 이면 SSH 결과 의심 → confirm 한 번 더
  if [ "$total_act" = "0" ] && [ "$cnt" -lt "700" ] && [ "$first" = "0" ]; then
    confirm=$(ssh -o ConnectTimeout=15 capstone2026@165.132.140.240 "pgrep -af measure_paper_exact | grep -v grep | wc -l" 2>/dev/null | tr -d ' \n\r')
    if [[ ! "$confirm" =~ ^[0-9]+$ ]] || [ "$confirm" != "0" ]; then
      echo "[$ts] ⚠️ false-zero detected (total_act=$total_act vs confirm=$confirm) — skip trigger"
      sleep 30; continue
    fi
  fi

  # Memory emergency (< 10GB) — kill 가장 오래 stuck procs
  if [ "$mem" -lt 10000 ]; then
    killed=$(ssh -o ConnectTimeout=15 capstone2026@165.132.140.240 "
      stuck_log=\$(find /mnt/hdd0/home/capstone2026/log/paper_exact_*.log -mmin +30 2>/dev/null | head -1)
      if [ -n \"\$stuck_log\" ]; then
        cell=\$(basename \$stuck_log .log | sed 's/paper_exact_//;s/_[0-9]*_[0-9]*\$//')
        pid=\$(pgrep -af measure_paper_exact | grep -v grep | grep \$cell | head -1 | awk '{print \$1}')
        [ -n \"\$pid\" ] && kill -TERM \$pid 2>&1 && echo \"\$pid (\$cell)\"
      fi
    " 2>/dev/null | tr -d ' \n\r')
    [ -n "$killed" ] && echo "[$ts] 🚨 MEM EMERGENCY mem=${mem}MB — killed PID $killed"
  fi

  # Stuck 30min+ + CPU<50% kill
  if [ "$stuck30" -gt "5" ]; then
    killed_count=$(ssh -o ConnectTimeout=15 capstone2026@165.132.140.240 "
      n=0
      for log in \$(find /mnt/hdd0/home/capstone2026/log/paper_exact_*.log -mmin +30 2>/dev/null); do
        cell=\$(basename \$log .log | sed 's/paper_exact_//;s/_[0-9]*_[0-9]*\$//')
        for pid in \$(pgrep -af measure_paper_exact | grep -v grep | grep \$cell | awk '{print \$1}'); do
          cpu=\$(ps -p \$pid -o pcpu= 2>/dev/null | awk '{print int(\$1)}')
          if [ -n \"\$cpu\" ] && [ \$cpu -lt 50 ]; then
            kill -TERM \$pid 2>&1 && n=\$((n+1))
          fi
        done
      done
      echo \$n
    " 2>/dev/null | tr -d ' \n\r')
    if [ -n "$killed_count" ] && [ "$killed_count" -gt "0" ] 2>/dev/null; then
      echo "[$ts] 🔧 STUCK kill — $killed_count procs"
    fi
  fi

  # cnt alert
  if [ "$first" = "1" ]; then
    echo "[$ts] START cnt=$cnt/702 main=$main_act p4=$p4_act total=$total_act mem=${mem}MB stuck30=$stuck30"
    prev_cnt=$cnt; first=0
  elif [ "$cnt" != "$prev_cnt" ]; then
    delta=$((cnt - prev_cnt))
    echo "[$ts] cnt=$cnt/702 (+$delta) main=$main_act p4=$p4_act mem=${mem}MB"
    prev_cnt=$cnt
  fi

  # Heartbeat (60 loop = 30min)
  if [ "$((loop % 60))" = "0" ]; then
    echo "[$ts] ❤️ HEARTBEAT cnt=$cnt main=$main_act p4=$p4_act total=$total_act mem=${mem}MB stuck30=$stuck30 done=$main_chain_done"
  fi

  # Main chain trigger — main_act=0 + cnt>650 + total_act=p4_act 검증
  if [ "$main_act" = "0" ] && [ "$main_chain_done" = "0" ] && [ "$cnt" -gt "650" ] && [ "$total_act" = "$p4_act" ]; then
    echo "[$ts] === ✅ MAIN MEASUREMENT DONE (cnt=$cnt) — chain trigger ==="
    ssh -o ConnectTimeout=15 capstone2026@165.132.140.240 "
      tmux new -d -s main_chain_post 'cd /mnt/hdd0/home/capstone2026/cache/rq3 && {
        echo \"[Step 1] analyze 1차\";
        python3 analyze_paper_exact.py 2>&1 | tee /mnt/hdd0/home/capstone2026/log/main_chain_post.log;
        echo \"[Step 2] sigma builder\";
        python3 -u compute_stratum_sigma_paper_exact.py 2>&1 | tee -a /mnt/hdd0/home/capstone2026/log/main_chain_post.log;
        echo \"[Step 3] RQ2 5-way\";
        OMP_NUM_THREADS=128 python3 -u measure_paper_exact.py --rq 2 --output paper_exact 2>&1 | tee -a /mnt/hdd0/home/capstone2026/log/main_chain_post.log;
        echo \"[Step 4] analyze 2차\";
        python3 analyze_paper_exact.py 2>&1 | tee -a /mnt/hdd0/home/capstone2026/log/main_chain_post.log;
      }'
    " 2>&1
    main_chain_done=1
  fi

  # Final analysis (Phase 4 + main chain post 모두 끝)
  if [ "$total_act" = "0" ] && [ "$main_chain_done" = "1" ] && [ "$chain_post" = "0" ] && [ "$final_done" = "0" ] 2>/dev/null; then
    echo "[$ts] === ✅ ALL DONE — final analysis ==="
    ssh -o ConnectTimeout=15 capstone2026@165.132.140.240 "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 analyze_paper_exact.py 2>&1 | tail -15" 2>&1
    final_done=1
    echo "[$ts] === 🎉 COMPLETE ==="
    break
  fi

  sleep 30
done
```

---

## 3. 자동 trigger 흐름

```
[현재] 메인 측정 (Tier 1+extra+extra2) 진행 + Phase 4 11 method 진행
       ↓
[main_act=0 + cnt>650] 메인 측정 끝 → main_chain_post tmux launch
       ├─ Step 1: analyze 1차 (현재 측정 결과 분석)
       ├─ Step 2: sigma builder (RQ2 Neyman/Anti 위해 σ_j 빌드)
       ├─ Step 3: RQ2 5-way 측정 (Bernoulli/Equal/Prop/Neyman/Anti)
       └─ Step 4: analyze 2차 (RQ2 포함)
       ↓
[total_act=0 + main_chain_done=1] Phase 4 + main chain post 모두 끝
       ↓
[final analysis] analyze 3차 (Phase 4 결과 + RQ2 + 모든 측정 종합)
       ↓
[🎉 COMPLETE] REPORT_paper_exact.md 최종 갱신 → break
```

---

## 4. Auto-fix logic

### 4.1 Memory emergency (`mem < 10GB`)
- 가장 오래 stuck (log mtime 30분+) procs 1건 kill
- log: `🚨 MEM EMERGENCY mem=${mem}MB — killed PID ${pid} (${cell})`

### 4.2 Stuck procs (log mtime 30분+ + CPU<50%)
- 모두 kill (handoff §10.2 stuck 정의)
- log: `🔧 STUCK kill — ${n} procs`

### 4.3 Sanity check (false-zero 방지)
- `total_act=0` + `cnt<700` 이면 한 번 더 confirm
- 일치 안 하면 skip trigger (잘못된 chain trigger 방지)

---

## 5. 인계 시점에 사용자 응답 받을 사항 (메인 세션 종료 전 사용자 명시)

1. **Organize capstone deliverables 세션 완료 보고 받기** (사용자 명시)
2. **MASTER_README.md** + 5건 통합 문서 read 검증
3. **새 세션 시작 OK confirm**

---

## 6. 메인 세션 종료 후 새 세션 시작 절차

### Step 1 — 새 Claude Code 세션 시작 (`/Users/hyunbin/Capstone`)

### Step 2 — 1 file read (단일 진입점)
```bash
cat _internal/MASTER_README.md
```

### Step 3 — 본 handoff_v6 read (smart coordinator 코드 인계)
```bash
cat _internal/handoff/active/handoff_v6_smart_coordinator_handoff_20260511_0125.md
# (Organize 세션 5/11 02:00 mv: _internal/handoff_v6_*.md → _internal/handoff/active/handoff_v6_*.md)
```

### Step 4 — 진행 상태 검증
```bash
ssh capstone2026@165.132.140.240 "
  date '+%H:%M KST'
  echo cnt=\$(ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json 2>/dev/null | wc -l)/702
  echo procs=\$(pgrep -af measure_paper_exact | grep -v grep | wc -l)
  echo mem_avail=\$(free -m | awk '/Mem:/{print \$7}') MB
"
```

### Step 5 — Smart coordinator v2 launch (§2 코드 verbatim Monitor 도구로 복붙)

### Step 6 — 자율 진행 — 내일 아침 결과 확인

---

## 7. 다음 세션 종료 후 사용자 확인 사항 (내일 아침)

1. **monitor stream 마지막 message** — `=== 🎉 COMPLETE ===` 또는 진행 단계
2. **`/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md`** — 최종 5단계 narrative
3. **`/mnt/hdd0/home/capstone2026/log/main_chain_post.log`** — sigma + RQ2 + analyze 결과
4. **Phase 4 결과** — `cache/rq3/paper_exact/*_CaseA_*chao_weighted*.json` 등 11 method 결과

---

## 8. 핵심 file 위치 (참조)

### Local (5/11 02:00 Organize 세션 mv 후 새 path)
- `_internal/handoff/active/handoff_v6_smart_coordinator_handoff_20260511_0125.md` (이 file)
- `_internal/MASTER_README.md` (Organize 세션 작성, 281 line, 단일 진입점)
- `_internal/MASTER_HANDOFF.md` (Organize 세션 작성, 469 line)
- `_internal/METHOD_REGISTRY.md` (57 method × 10 paradigm)
- `_internal/EXPERIMENT_REGISTRY.md` (9 cells × 57 methods × 3 modes)
- `_internal/SERVER_REGISTRY.md` (server SSH/PG/tmux/log inventory)
- `_internal/CHANGELOG.md` (5/10~5/11 timeline)
- `_internal/scripts/measure_paper_exact.py` (Phase 4 분기 추가됨)
- `_internal/scripts/method_phase4_extra.py` (11 method, smoke 11/11 PASS)
- `_internal/scripts/run_phase_b_phase4.sh` (Phase 4 launcher, --n-queries fix)

### Server (`/mnt/hdd0/home/capstone2026/`)
- `cache/rq3/{measure_paper_exact,method_phase4_extra,run_phase_b_phase4.sh}` (모두 5/11 01:00 갱신)
- `cache/rq3/paper_exact/*Case*.json` (440+ 측정 결과)
- `log/paper_exact_phase4_*.log` (Phase 4 11 cell)
- `log/paper_exact_phase_*.log` (메인 chain log)
- tmux: pb_*, pbe_*, pbe2_*, pc_*, pce_*, pb_p4_*

---

## 8.5 ⚠️ Smart Coordinator v3 권고 추가 logic (사용자 명시 5/11 01:33 verbatim)

> "내일도 작업하다가 kill 하면 다시 나중에 launch하는 식으로 해서 결국엔 모든 method 진행하는 거"

**현재 v2 logic 한계**:
- stuck/memory kill만 — kill된 method **재 launch 없음**
- 결과: kill되면 영원히 미완료 → 모든 method 진행 보장 X

**v3 추가 logic (새 세션 monitor에 추가 필수)**:

```bash
# Auto-relaunch killed Phase 4 method (매 cycle 또는 5분 주기)
P4_METHODS="chao_weighted lpm1_proper cum_sqrtf lavallee_hidiroglou idistance zorder_morton skilling_hilbert ica_fastica kmeans_neyman rabitq_strat idistance_neyman"
EXPECTED_RESULTS_PER_METHOD=18  # 9 cells × 2 modes (CaseA + CaseB)

for m in $P4_METHODS; do
  session_alive=$(ssh capstone "tmux ls 2>/dev/null | grep -c \"^pb_p4_${m}:\"" | tr -d ' \n')
  result_count=$(ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*_CaseA_${m}.json /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*_CaseB_${m}.json 2>/dev/null | wc -l" | tr -d ' \n')

  if [ "$session_alive" = "0" ] && [ "$result_count" -lt "$EXPECTED_RESULTS_PER_METHOD" ]; then
    # session 죽음 + 결과 미완료 → 재 launch
    ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && tmux new -d -s pb_p4_${m} './run_phase_b_phase4.sh --method ${m} 2>&1 | tee /mnt/hdd0/home/capstone2026/log/paper_exact_phase4_${m}_relaunch_\$(date +%Y%m%d_%H%M).log'"
    echo "[$ts] 🔄 RELAUNCH ${m} (results ${result_count}/${EXPECTED_RESULTS_PER_METHOD})"
  fi
done
```

**완료 조건 (final trigger)**:
- 모든 Phase 4 method × cells × modes 결과 file 생성 = 11 × 18 = 198건
- 메인 측정 결과 = 메인 portfolio × cells × modes
- 합 모두 완료 → final analysis trigger

**핵심**: kill되어도 다음 cycle에서 detect → 재 launch → 결국 모든 method 완료.

---

## 8.6 ⚠️ Method-specific Memory 폭증 발견 (5/11 01:34 verbatim)

**birch method × SF=100 cells**:
- 단일 procs RSS **50-200GB** (cluster CFNode tree 빌드 시)
- 4 procs 동시 (A5-scale-sf100/A2-Fig9/A2-Fig7/A5-scale-sf10) → swap 위험
- 5/11 01:34 emergency kill 발생 (mem 8GB → 320GB 회복)

**다른 위험 method 추정** (handoff_main §12.2 + 5/11 발견):
- **birch** ★ — SF=100 측정 부적합 (현재 sample 10K + nearest centroid 우회 부족)
- **agglomerative** — O(n²) memory (handoff §12.2)
- **HDBSCAN** — 8M+ OOM (이미 폐기)
- **kdpp** — DPP 시간 (50K subset 우회)

**v3 monitor 추가 권고**:
- 매 cycle PSS RSS check: `RSS > 50GB` procs 자동 alert
- birch × SF=100 cells (A2-Fig7/A2-Fig9/A5-scale-sf10/sf100) 자동 skip 또는 chunked 강화
- 또는 `MEM_PER_PROC_LIMIT=30GB` 설정 — 초과 시 즉시 kill

```bash
# v3 추가: 메모리 폭증 procs 자동 kill
high_mem_pids=$(ssh capstone "ps -eo pid,rss,cmd --no-headers --sort -rss | grep measure_paper_exact | awk '\$2 > 30000000 {print \$1}'")
for pid in $high_mem_pids; do
  ssh capstone "kill -TERM $pid"
  echo "[$ts] 💥 HIGH-MEM kill PID $pid (RSS > 30GB)"
done
```

---

## 8.7 자원 최대 활용 logic (v3 추가, 사용자 5/11 01:36 명시)

> "monitor나 coordinator는 자원 최대 활용 + stuck 시 kill 하면 재 launch 통해서 결국 어쨋든 모든 실험은 계속 진행"
> "완료하면 당연히 베스트. 아니어도 계속 내가 아침에 와도 실험 진행 중 또는 완료 상태"

**v3 통합 logic flow** (매 30s cycle):

```
1. State fetch (cnt, procs by method, mem, stuck)
2. Auto-fix:
   a. RSS > 30GB → 즉시 kill (high-mem)
   b. mem < 10GB → 가장 오래 stuck procs kill
   c. log mtime 30min+ + CPU<50% → kill (stuck)
3. Auto-relaunch (5분 주기):
   - 각 Phase 4 method × cells × modes 결과 file 카운트
   - session 죽음 + 결과 < 18 → 재 launch
   - 메인 method 동일 logic (run_phase_b_*.sh)
4. 자원 idle 활용:
   - procs < 20 + mem > 200GB + 미완료 method 있음 → 추가 launch
5. Trigger:
   - 메인 measurement 끝 + Phase 4 끝 → main_chain_post launch
   - 모든 끝 → final analysis → COMPLETE
```

**어쨋든 보장**:
- ✅ 완료 = 모든 method × cells × modes 결과 file 198+ (Phase 4) + 메인
- ⚠️ 진행 中 = 아침 도착 시 monitor 가 계속 retry → 결국 완료
- ❌ 멈춤 = 거의 불가능 (kill → relaunch → 다음 cycle)

---

## 9. 주의사항 / 함정

### 9.1 pgrep filter 정확성 (중요!)
- ✅ `pgrep -af measure_paper_exact` (literal substring)
- ❌ `pgrep -af 'measure_paper.py'` (regex `.` = any-char → match 안 됨)
- 5/11 01:25 false-zero trigger 사고 발견 — 위 v2 코드는 fix 적용

### 9.2 Sanity check 필수
- false-zero 발생 시 잘못된 chain trigger → 측정 중인데 sigma builder launch → 자원 contention
- v2는 confirm 한 번 더로 회피

### 9.3 Memory 압박 처리
- mem < 10GB 시 emergency kill (가장 오래 stuck 1건)
- 단 측정 procs RSS 작음 (mmap 공유) — emergency 거의 트리거 X 예상

### 9.4 chain trigger 조건 보수적
- `cnt > 650` (이전 400 → 보수적 — 메인 측정 거의 완료 시점)
- `total_act = p4_act` (메인 measurement procs 0 확실)

---

## 10. END

작성: 2026-05-11 01:25 KST (메인 세션 context 한도 정리 직전)
다음: Organize 세션 완료 → 새 세션 시작 → §0 5단계 즉시 액션 → 자율 진행 (내일 아침 결과)

**핵심**: 새 세션이 본 handoff + MASTER_README.md 만 read → smart coordinator launch → 0% loss 인계.
