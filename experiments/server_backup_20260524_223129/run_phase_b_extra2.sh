#!/bin/bash
set -uo pipefail
CELL="$1"
LOG="/mnt/hdd0/home/capstone2026/log/paper_exact_phase_b_extra2_${CELL}.log"
OUT="/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact"
cd /mnt/hdd0/home/capstone2026/cache/rq3
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
# Tier S+/A/B 20 NEW methods
METHODS=(opq kdpp banditucb1 neuram thompson_sampling mfmc epsilon_net ams_count_sketch neurocard_lite adaptive_bucket_probing ccsketch factor_join lp_bound cca1d cocluster_nystrom tucker vinecopula hkbu_repsample lhs lpm2)
echo "[$(date +%H:%M:%S)] === Phase B extra2 $CELL × 20 NEW methods ===" | tee -a $LOG
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
echo "[$(date +%H:%M:%S)] === END Phase B extra2 $CELL ===" | tee -a $LOG
