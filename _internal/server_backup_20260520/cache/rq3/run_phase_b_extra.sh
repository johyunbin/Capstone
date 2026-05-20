#!/bin/bash
# Phase B extra: 8 NEW methods × 9 cells = 72 measurements
set -uo pipefail
CELL="$1"
LOG="/mnt/hdd0/home/capstone2026/log/paper_exact_phase_b_extra_${CELL}.log"
OUT="/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact"
cd /mnt/hdd0/home/capstone2026/cache/rq3
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
METHODS=(pq kdtree halton hammersley coreset birch agglomerative dense_rp)
echo "[$(date +%H:%M:%S)] === Phase B extra $CELL × 8 NEW methods ===" | tee -a $LOG
for method in "${METHODS[@]}"; do
  out_json="$OUT/${CELL}_CaseA_${method}.json"
  if [ -f "$out_json" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $CELL × $method" | tee -a $LOG
    continue
  fi
  echo "[$(date +%H:%M:%S)] === $CELL × $method ===" | tee -a $LOG
  python3 -u measure_paper_exact.py --rq 3 --phase B --cell $CELL --mode CaseA --method $method \
    --n-queries 1000 --trials 10 --output $OUT 2>&1 | tee -a $LOG
done
echo "[$(date +%H:%M:%S)] === END Phase B extra $CELL ===" | tee -a $LOG
