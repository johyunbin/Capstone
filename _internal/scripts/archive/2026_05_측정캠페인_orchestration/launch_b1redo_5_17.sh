#!/bin/bash
# task A 후속 — B1 1단계(paper-faithful) 재측정 runner. gen_b1redo_launch.py 생성. 5/17.
# b1redo_tasks_5_17.txt 의 80건을 --mode B1 로 재측정. 현재 코드 B1 mode = 1단계(all_vecs).
# idempotent: 결과 JSON 존재 시 skip.
#   사용: bash launch_b1redo_5_17.sh /tmp/b1redo_tasks_5_17.txt
set -u
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TASKS=${1:-/tmp/b1redo_tasks_5_17.txt}
OUT_BASE=${2:-/mnt/hdd0/home/capstone2026/results_b1redo_1stage}
LOG=$OUT_BASE/logs
mkdir -p "$LOG"
TOTAL=$(wc -l < "$TASKS")
echo "[$(date)] === B1 1단계 재측정 — $TOTAL measurement → $OUT_BASE ===" | tee -a "$LOG/_main.log"
N=0
while IFS='|' read -r CELL SEL K; do
  [ -z "$CELL" ] && continue
  N=$((N+1))
  OUT=$OUT_BASE/${CELL}_sel${SEL}_K${K}
  mkdir -p "$OUT"
  JF=$OUT/${CELL}_B1.json
  if [ -f "$JF" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $N/$TOTAL $CELL sel$SEL K$K B1" | tee -a "$LOG/_main.log"
    continue
  fi
  echo "[$(date +%H:%M:%S)] === $N/$TOTAL $CELL sel$SEL K$K B1 (1단계) ===" | tee -a "$LOG/_main.log"
  ENV=""
  [ "$K" != "20" ] && ENV="STRATA_K=$K"
  env $ENV python3 "$SCRIPT" --rq 3 --phase A --cell "$CELL" --mode B1 \
      --sel "$SEL" --output "$OUT" \
      2>&1 | tee "$LOG/${CELL}_sel${SEL}_K${K}_B1.log" \
      || echo "[WARN] $CELL sel$SEL K$K B1 failed" | tee -a "$LOG/_main.log"
done < "$TASKS"
NJSON=$(find "$OUT_BASE" -name '*_B1.json' -type f 2>/dev/null | wc -l)
NWARN=$(grep -c '\[WARN\]' "$LOG/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] === B1 1단계 재측정 DONE — JSON $NJSON / $TOTAL, WARN $NWARN ===" | tee -a "$LOG/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
