#!/bin/bash
set -uo pipefail
cd /mnt/hdd0/home/capstone2026/cache/rq3
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
LOG=/mnt/hdd0/home/capstone2026/log/paper_exact_sparse_rp_retry.log
OUT=/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact

CELLS=(A5-scale-sf1 A5-scale-sf10 A2-Fig9 A2-Fig7)
METHODS=(sparse_rp random_projection)

for cell in "${CELLS[@]}"; do
  for method in "${METHODS[@]}"; do
    out_json="$OUT/${cell}_CaseA_${method}.json"
    if [ -f "$out_json" ]; then
      echo "[$(date +%H:%M:%S)] SKIP $cell × $method" | tee -a $LOG
      continue
    fi
    echo "[$(date +%H:%M:%S)] === $cell × $method ===" | tee -a $LOG
    python3 -u measure_paper_exact.py --rq 3 --phase B --cell $cell --mode CaseA --method $method \
      --n-queries 1000 --trials 10 --output $OUT 2>&1 | tee -a $LOG
  done
done
echo "DONE retry" | tee -a $LOG
