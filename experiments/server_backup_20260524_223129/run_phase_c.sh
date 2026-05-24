#!/bin/bash
# Phase C CaseB ensemble: B1 + method × all cells × 11 methods sequential
set -uo pipefail
CELL="$1"
LOG="/mnt/hdd0/home/capstone2026/log/paper_exact_phase_c_${CELL}.log"
OUT="/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact"
cd /mnt/hdd0/home/capstone2026/cache/rq3
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
METHODS=(sparse_rp random_projection minibatch hilbert gmm minibatch_partial lsh pca1d sobol reservoir faiss_ivf)
echo "[$(date +%H:%M:%S)] === Phase C $CELL × all methods ===" | tee -a $LOG
for method in "${METHODS[@]}"; do
  out_json="$OUT/${CELL}_CaseB_${method}.json"
  if [ -f "$out_json" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $CELL × $method" | tee -a $LOG
    continue
  fi
  echo "[$(date +%H:%M:%S)] === $CELL × $method ===" | tee -a $LOG
  python3 -u measure_paper_exact.py --rq 3 --phase C --cell $CELL --mode CaseB --method $method \
    --n-queries 1000 --trials 10 --output $OUT 2>&1 | tee -a $LOG
done
echo "[$(date +%H:%M:%S)] === END Phase C $CELL ===" | tee -a $LOG
