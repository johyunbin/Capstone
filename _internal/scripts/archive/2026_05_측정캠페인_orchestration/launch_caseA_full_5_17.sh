#!/bin/bash
# task C — CaseA 전체 portfolio 측정 runner. gen_caseA_launch.py 가 생성. 5/17 세션.
# caseA_tasks_5_17.txt 의 1364건을 --mode CaseA 로 측정. CaseA = est_method 단독.
# idempotent: 결과 JSON 존재 시 skip — 중단 후 재실행 안전.
#   사용: tmux new -d -s caseA 'bash launch_caseA_full_5_17.sh /tmp/caseA_tasks_5_17.txt'
set -u
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TASKS=${1:-/tmp/caseA_tasks_5_17.txt}
OUT_BASE=${2:-/mnt/hdd0/home/capstone2026/results_caseA_full}
LOG=$OUT_BASE/logs
mkdir -p "$LOG"
TOTAL=$(wc -l < "$TASKS")
echo "[$(date)] === CaseA full portfolio — $TOTAL measurement → $OUT_BASE ===" | tee -a "$LOG/_main.log"
N=0
while IFS='|' read -r CELL SEL K METHOD; do
  [ -z "$CELL" ] && continue
  N=$((N+1))
  OUT=$OUT_BASE/${CELL}_sel${SEL}_K${K}
  mkdir -p "$OUT"
  JF=$OUT/${CELL}_CaseA_${METHOD}.json
  if [ -f "$JF" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $N/$TOTAL $CELL sel$SEL K$K $METHOD" | tee -a "$LOG/_main.log"
    continue
  fi
  echo "[$(date +%H:%M:%S)] === $N/$TOTAL $CELL sel$SEL K$K CaseA $METHOD ===" | tee -a "$LOG/_main.log"
  ENV=""
  [ "$K" != "20" ] && ENV="STRATA_K=$K"
  env $ENV python3 "$SCRIPT" --rq 3 --phase B --cell "$CELL" --mode CaseA \
      --method "$METHOD" --sel "$SEL" --output "$OUT" \
      2>&1 | tee "$LOG/${CELL}_sel${SEL}_K${K}_CaseA_${METHOD}.log" \
      || echo "[WARN] $CELL sel$SEL K$K $METHOD failed" | tee -a "$LOG/_main.log"
done < "$TASKS"
NJSON=$(find "$OUT_BASE" -name '*_CaseA_*.json' -type f 2>/dev/null | wc -l)
NWARN=$(grep -c '\[WARN\]' "$LOG/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] === CaseA full DONE — JSON $NJSON / $TOTAL, WARN $NWARN ===" | tee -a "$LOG/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
