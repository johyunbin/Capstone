#!/bin/bash
set -uo pipefail
CELL="$1"
LOG="/mnt/hdd0/home/capstone2026/log/paper_exact_phase_c_extra_${CELL}.log"
OUT="/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact"
cd /mnt/hdd0/home/capstone2026/cache/rq3
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
# Phase C CaseB extra: 8 NEW + 20 NEW2 = 28 methods
METHODS=(pq kdtree halton hammersley coreset birch agglomerative dense_rp opq kdpp banditucb1 neuram thompson_sampling mfmc epsilon_net ams_count_sketch neurocard_lite adaptive_bucket_probing ccsketch factor_join lp_bound cca1d cocluster_nystrom tucker vinecopula hkbu_repsample lhs lpm2)
echo "[$(date +%H:%M:%S)] === Phase C extra $CELL × 28 NEW methods ===" | tee -a $LOG
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
echo "[$(date +%H:%M:%S)] === END Phase C extra $CELL ===" | tee -a $LOG
