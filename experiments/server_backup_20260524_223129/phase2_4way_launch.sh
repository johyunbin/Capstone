#!/bin/bash
# phase2 4-way 12 cell launch — 5/24 02:30 KST
# carry phase2 (3-way) cell list 와 동일 + CaseA·CaseC variant 추가 (4-way)
# 12 cell = (q3,q9,q10,q12) × (qid 0,1,2) × sel 0.001 × sf 10 × DEEP
# 추정: ~10-15분/cell × 12 = 2.0-3.0시간 sequential
set -u
cd /mnt/hdd0/home/capstone2026/cache/rq3
TS=$(TZ=Asia/Seoul date +%Y%m%d_%H%M%S)
OUTDIR=latency/phase2_4way_$TS
mkdir -p "$OUTDIR"
LOG="$OUTDIR/phase2_4way.log"
ESTIMATES=latency/smoke_estimates_4way/estimates_DEEP_sf10.parquet
ts() { TZ=Asia/Seoul date +'%FT%H:%M:%S'; }
echo "[$(ts) KST] phase2 4-way launch start — 12 cells sequential" > "$LOG"
echo "[$(ts) KST] OUTDIR=$OUTDIR" >> "$LOG"
echo "[$(ts) KST] PID=$$" >> "$LOG"
total_start=$(date +%s)
ok=0; fail=0
for q in q3 q9 q10 q12; do
  for qid in 0 1 2; do
    cell_start=$(date +%s)
    echo "" >> "$LOG"
    echo "[$(ts) KST] === $q qid$qid start ===" >> "$LOG"
    python3 -u measure_latency_realengine.py \
      --query $q --dataset DEEP --sf 10 --sel 0.001 --query-id $qid \
      --estimates "$ESTIMATES" \
      --n-warmup 5 --n-timed 15 \
      --statement-timeout 60s \
      --output "$OUTDIR" >> "$LOG" 2>&1
    rc=$?
    cell_elapsed=$((  $(date +%s) - cell_start ))
    if [ $rc -eq 0 ]; then ok=$((ok+1)); echo "[$(ts) KST] === $q qid$qid OK (${cell_elapsed}s) ===" >> "$LOG"
    else fail=$((fail+1)); echo "[$(ts) KST] === $q qid$qid FAIL rc=$rc (${cell_elapsed}s) ===" >> "$LOG"
    fi
  done
done
total_elapsed=$((  $(date +%s) - total_start ))
echo "" >> "$LOG"
echo "[$(ts) KST] phase2 4-way done — $ok/12 OK, $fail FAIL, total ${total_elapsed}s ($((total_elapsed/60))min)" >> "$LOG"
ls -la "$OUTDIR"/*.json 2>/dev/null | wc -l >> "$LOG"
