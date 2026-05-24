#!/bin/bash
# v14 CaseC launch — 5/23 20:50 KST
# 9 cells × CaseC (method-independent, v13 carry-matchable)
# Estimated time: 30-90 min sequential
# Server: aigpu-6000ada1, load high (~56) → sequential best

set -u

OUTDIR=/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v14_20260523
LOG=/tmp/v14_launch_20260523.log
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py

mkdir -p "$OUTDIR"
cd /mnt/hdd0/home/capstone2026/cache/rq3

cells=(
    A1-DEEP
    A1-SIFT
    A1-SSN
    A2-Fig7
    A2-Fig9
    A4-sel
    A5-scale-sf1
    A5-scale-sf10
    A5-scale-sf100
)

ts() { TZ=Asia/Seoul date +"%FT%H:%M:%S"; }

echo "[$(ts) KST] v14 CaseC launch start — ${#cells[@]} cells sequential" > "$LOG"
echo "[$(ts) KST] OUTDIR=$OUTDIR" >> "$LOG"
echo "[$(ts) KST] PID=$$" >> "$LOG"

total_start=$(date +%s)
ok=0
fail=0

for cell in "${cells[@]}"; do
    cell_start=$(date +%s)
    echo "" >> "$LOG"
    echo "[$(ts) KST] ============================================" >> "$LOG"
    echo "[$(ts) KST] === $cell CaseC start ===" >> "$LOG"

    python3 -u "$SCRIPT" \
        --rq 3 --phase E \
        --cell "$cell" \
        --mode CaseC \
        --output "$OUTDIR" \
        >> "$LOG" 2>&1
    rc=$?

    cell_end=$(date +%s)
    cell_dur=$((cell_end - cell_start))

    if [ "$rc" -eq 0 ]; then
        ok=$((ok + 1))
        status="OK"
    else
        fail=$((fail + 1))
        status="FAIL rc=$rc"
    fi
    echo "[$(ts) KST] === $cell CaseC done ($status, ${cell_dur}s) ===" >> "$LOG"
done

total_end=$(date +%s)
total_dur=$((total_end - total_start))
echo "" >> "$LOG"
echo "[$(ts) KST] ============================================" >> "$LOG"
echo "[$(ts) KST] v14 CaseC launch COMPLETE — ok=$ok fail=$fail total=${total_dur}s" >> "$LOG"
echo "[$(ts) KST] outputs in $OUTDIR:" >> "$LOG"
ls -la "$OUTDIR"/*CaseC.json 2>&1 | head -20 >> "$LOG"
