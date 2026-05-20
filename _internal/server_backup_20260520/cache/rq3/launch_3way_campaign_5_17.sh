#!/bin/bash
# 3-way 통합 병렬 측정 캠페인 runner — 5/17 세션 (전권 위임, 서버 자원 최대 활용).
# 서버 128 core / 1TB RAM. tasks_3way_5_17.txt (~1556 측정) — 각 측정이
# measure_paper_exact.py --mode 3way 로 B1·CaseA·CaseB 를 matched 동시 산출.
#   sf1/sf10 : N=16 동시 / sf100 : N=8 동시 (80M NPY 최대 82GB × 8 = 656GB, 1TB 내 안전)
#   측정당 BLAS thread=8.
# idempotent: 결과 JSON 존재 시 skip — 고정 출력 dir, tmux 중단/서버 재부팅 후 재실행 안전.
#   사용: tmux new -d -s campaign 'bash /tmp/launch_3way_campaign_5_17.sh'
set -u
export SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
export TASKS=${1:-/tmp/tasks_3way_5_17.txt}
export OUT_BASE=${2:-/mnt/hdd0/home/capstone2026/results_3way_5_17}
export LOG=$OUT_BASE/logs
mkdir -p "$LOG"

# --- 측정 1건: "cell|sf|sel|K|method" → 3-way 측정. idempotent skip. ---
run_one() {
  local line="$1"
  local CELL SF SEL K METHOD
  IFS='|' read -r CELL SF SEL K METHOD <<< "$line"
  local OUT="$OUT_BASE/${CELL}_sel${SEL}_K${K}"
  mkdir -p "$OUT"
  local JF="$OUT/${CELL}_3way_${METHOD}.json"
  if [ -f "$JF" ]; then echo "[$(date +%H:%M:%S)] SKIP $line"; return 0; fi
  local KENV=""
  [ "$K" != "20" ] && KENV="STRATA_K=$K"
  if env OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 $KENV \
       python3 "$SCRIPT" --rq 3 --phase B --cell "$CELL" --mode 3way --method "$METHOD" \
       --sel "$SEL" --output "$OUT" \
       > "$LOG/${CELL}_sel${SEL}_K${K}_${METHOD}.log" 2>&1; then
    echo "[$(date +%H:%M:%S)] OK $line"
  else
    echo "[$(date +%H:%M:%S)] WARN $line"
  fi
}
export -f run_one

TOTAL=$(grep -c . "$TASKS")
echo "[$(date)] ======== 3-WAY CAMPAIGN START — $TOTAL tasks ========" | tee -a "$LOG/_main.log"

# --- sf 버킷별 병렬 (가벼운 버킷 먼저) ---
# N: 측정당 ~1-2 core·NPY RAM 기준 — sf1(NPY<3GB) 64동시, sf10(<27GB) 24동시,
#    sf100(80M NPY 30~82GB) 8동시 = 656GB worst, 1TB 내 안전.
for BUCKET in "1:64" "10:24" "100:2"; do
  SF="${BUCKET%:*}"; N="${BUCKET#*:}"
  CNT=$(awk -F'|' -v sf="$SF" '$2==sf' "$TASKS" | grep -c .)
  echo "[$(date)] === sf=$SF 버킷: $CNT tasks, 병렬 N=$N ===" | tee -a "$LOG/_main.log"
  awk -F'|' -v sf="$SF" '$2==sf' "$TASKS" \
    | xargs -P "$N" -I {} bash -c 'run_one "$@"' _ {} \
    2>&1 | tee -a "$LOG/_main.log"
done

NJSON=$(find "$OUT_BASE" -name '*_3way_*.json' -type f 2>/dev/null | wc -l)
NWARN=$(grep -c '\] WARN ' "$LOG/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] ======== 3-WAY CAMPAIGN DONE — JSON $NJSON / $TOTAL, WARN $NWARN ========" | tee -a "$LOG/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
