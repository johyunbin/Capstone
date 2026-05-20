#!/bin/bash
set -uo pipefail
cd /mnt/hdd0/home/capstone2026/cache/rq3
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
LOG=/mnt/hdd0/home/capstone2026/log/paper_exact_phase_b_smoke.log
OUT=/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact

# CaseA smoke: 5 핵심 method × A5-scale-sf1 (작은 cell, 빠른 검증)
METHODS=(sparse_rp random_projection minibatch hilbert gmm)

for method in "${METHODS[@]}"; do
  echo "[$(date '+%H:%M:%S')] === START CaseA $method on A5-scale-sf1 ===" | tee -a $LOG
  python3 -u measure_paper_exact.py --rq 3 --phase B --cell A5-scale-sf1 --mode CaseA --method $method \
    --n-queries 1000 --trials 10 --output $OUT 2>&1 | tee -a $LOG
  echo "[$(date '+%H:%M:%S')] === END CaseA $method ===" | tee -a $LOG
done
echo "[$(date '+%H:%M:%S')] === Phase B smoke (5 methods × A5-sf1) DONE ===" | tee -a $LOG
