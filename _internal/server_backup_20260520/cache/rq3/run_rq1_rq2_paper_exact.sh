#!/bin/bash
set -uo pipefail
cd /mnt/hdd0/home/capstone2026/cache/rq3
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
LOG=/mnt/hdd0/home/capstone2026/log/paper_exact_rq1_rq2.log
OUT=/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact

echo "[$(date '+%H:%M:%S')] === RQ1 paper exact (DEEP/SIFT × sel {0.01, 0.10}) ===" | tee -a $LOG
python3 -u measure_paper_exact.py --rq 1 --output $OUT 2>&1 | tee -a $LOG
echo "[$(date '+%H:%M:%S')] === RQ1 done ===" | tee -a $LOG

echo "[$(date '+%H:%M:%S')] === RQ2 paper exact (DEEP/SIFT × Bernoulli/Equal/Prop) ===" | tee -a $LOG
python3 -u measure_paper_exact.py --rq 2 --output $OUT 2>&1 | tee -a $LOG
echo "[$(date '+%H:%M:%S')] === RQ2 done ===" | tee -a $LOG
