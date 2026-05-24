#!/bin/bash
# ★1 hdbscan launch (Campello 2013, V8 audit 4강) — 9 cells × 2 modes = 18 measurements
# 5/11 10:18 KST 사용자 명시 후 추가 launch
cd /mnt/hdd0/home/capstone2026/cache/rq3
OUT=/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact
LOG_DIR=/mnt/hdd0/home/capstone2026/log
TS=$(date +%Y%m%d_%H%M)
CELLS="A1-DEEP A1-SIFT A1-SSN A2-Fig7 A2-Fig9 A4-sel A5-scale-sf1 A5-scale-sf10 A5-scale-sf100"

for cell in $CELLS; do
  session="pb_hdbscan_${cell//-/_}"
  log="${LOG_DIR}/paper_exact_hdbscan_${cell}_${TS}.log"
  cmd="cd /mnt/hdd0/home/capstone2026/cache/rq3 && export OMP_NUM_THREADS=128 && {"
  for mode in CaseA CaseB; do
    cmd="$cmd echo \"[\$(date +%H:%M:%S)] === ${cell} × hdbscan × ${mode} ===\" | tee -a $log;"
    cmd="$cmd python3 -u measure_paper_exact.py --rq 3 --phase B --cell $cell --mode $mode --method hdbscan --output $OUT 2>&1 | tee -a $log;"
  done
  cmd="$cmd echo \"[\$(date +%H:%M:%S)] DONE ${cell}\" | tee -a $log; }"
  tmux new -d -s "$session" "$cmd"
  echo "launched $session"
  sleep 0.3
done
echo "All 9 cells × hdbscan × 2 modes = 18 measurements"
