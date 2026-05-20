#!/bin/bash
set -uo pipefail
cd /mnt/hdd0/home/capstone2026/cache/rq3
export OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16
LOG=/mnt/hdd0/home/capstone2026/log/paper_exact_phase_b_full.log
OUT=/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact

# 11 methods × 9 cells = 99 measurements
# A2-Fig8 (strata 빌드 후), A3-TPCDS (ECQO mode 별도) 제외
METHODS=(sparse_rp random_projection minibatch hilbert gmm minibatch_partial lsh pca1d sobol reservoir faiss_ivf)
CELLS=(A5-scale-sf1 A5-scale-sf10 A2-Fig9 A2-Fig7 A1-DEEP A1-SIFT A1-SSN A5-scale-sf100 A4-sel)

echo "[$(date '+%H:%M:%S')] === Phase B full START (11 methods × 9 cells = 99 measurements) ===" | tee -a $LOG

for cell in "${CELLS[@]}"; do
  for method in "${METHODS[@]}"; do
    out_json="$OUT/${cell}_CaseA_${method}.json"
    if [ -f "$out_json" ]; then
      echo "[$(date '+%H:%M:%S')] SKIP $cell × $method (already saved)" | tee -a $LOG
      continue
    fi
    echo "[$(date '+%H:%M:%S')] === START $cell × $method ===" | tee -a $LOG
    python3 -u measure_paper_exact.py --rq 3 --phase B --cell $cell --mode CaseA --method $method \
      --n-queries 1000 --trials 10 --output $OUT 2>&1 | tee -a $LOG
    echo "[$(date '+%H:%M:%S')] === END $cell × $method ===" | tee -a $LOG
  done
done
echo "[$(date '+%H:%M:%S')] === Phase B full DONE ===" | tee -a $LOG
