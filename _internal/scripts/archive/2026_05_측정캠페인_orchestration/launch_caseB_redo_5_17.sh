#!/bin/bash
# CaseB 1단계 재측정 runner — 5/17 세션 (전권 위임, 정확성 우선).
# caseA_tasks_5_17.txt 의 1364 (cell,sel,K,method) 를 --mode CaseB 로 재측정.
# measure_case_b 의 est_b1 을 1단계(all_vecs)로 fix 한 코드 기준 — paper-faithful 1단계
# Bernoulli + method stratified 의 산술평균 ensemble.
# idempotent: 결과 JSON 존재 시 skip — 고정 출력 dir, tmux 중단/서버 재부팅 후 재실행 안전.
#   사용: bash launch_caseB_redo_5_17.sh /tmp/caseA_tasks_5_17.txt [OUT_BASE]
set -u
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TASKS=${1:-/tmp/caseA_tasks_5_17.txt}
OUT_BASE=${2:-/mnt/hdd0/home/capstone2026/results_caseB_redo_1stage}
LOG=$OUT_BASE/logs
mkdir -p "$LOG"
TOTAL=$(wc -l < "$TASKS")
echo "[$(date)] === CaseB 1단계 재측정 — $TOTAL measurement → $OUT_BASE ===" | tee -a "$LOG/_main.log"
N=0
while IFS='|' read -r CELL SEL K METHOD; do
  [ -z "$CELL" ] && continue
  N=$((N+1))
  OUT=$OUT_BASE/${CELL}_sel${SEL}_K${K}
  mkdir -p "$OUT"
  JF=$OUT/${CELL}_CaseB_${METHOD}.json
  if [ -f "$JF" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $N/$TOTAL $CELL sel$SEL K$K $METHOD" | tee -a "$LOG/_main.log"
    continue
  fi
  echo "[$(date +%H:%M:%S)] === $N/$TOTAL $CELL sel$SEL K$K CaseB $METHOD ===" | tee -a "$LOG/_main.log"
  ENV=""
  [ "$K" != "20" ] && ENV="STRATA_K=$K"
  env $ENV python3 "$SCRIPT" --rq 3 --phase B --cell "$CELL" --mode CaseB \
      --method "$METHOD" --sel "$SEL" --output "$OUT" \
      2>&1 | tee "$LOG/${CELL}_sel${SEL}_K${K}_CaseB_${METHOD}.log" \
      || echo "[WARN] $CELL sel$SEL K$K $METHOD failed" | tee -a "$LOG/_main.log"
done < "$TASKS"
NJSON=$(find "$OUT_BASE" -name '*_CaseB_*.json' -type f 2>/dev/null | wc -l)
NWARN=$(grep -c '\[WARN\]' "$LOG/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] === CaseB 1단계 재측정 DONE — JSON $NJSON / $TOTAL, WARN $NWARN ===" | tee -a "$LOG/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
