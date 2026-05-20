#!/bin/bash
# Full chain for one (dataset, sf) cell:
#   prep (if needed) → K-sweep RQ1 baselines (K=10/20/50/100/200) → RQ3 random20 → RQ2 5mode → 18 methods
#
# Usage: bash run_cell_full.sh DEEP 1
#        bash run_cell_full.sh SIFT 10
#        bash run_cell_full.sh SSN  100

set -e
DS=$1
SF=$2
LOG=/tmp/run_${DS}_sf${SF}.log
PYTHON=python3
CACHE=/mnt/hdd0/home/capstone2026/cache

cd "$CACHE"

echo "[$(date +%H:%M:%S)] === START $DS sf$SF ===" | tee "$LOG"

# 1. Prep (skip if NPY cache exists; prep_cell.py handles this)
$PYTHON prepare_cell.py --dataset "$DS" --sf "$SF" 2>&1 | tee -a "$LOG"

# 2. RQ1 K-sweep baselines (K=20 default, then 10/50/100/200)
$PYTHON rq3/chain_unified.py --dataset "$DS" --sf "$SF" --stage rq1_km20 2>&1 | tee -a "$LOG"
for K in 10 50 100 200; do
  $PYTHON rq3/chain_unified.py --dataset "$DS" --sf "$SF" --stage rq1_km_k_$K 2>&1 | tee -a "$LOG"
done

# 3. RQ3 random20 (recovery rate 분모) + RQ2 5mode allocation
$PYTHON rq3/chain_unified.py --dataset "$DS" --sf "$SF" --stage rq3_random20 2>&1 | tee -a "$LOG"
$PYTHON rq3/chain_unified.py --dataset "$DS" --sf "$SF" --stage rq2_5mode 2>&1 | tee -a "$LOG"

# 4. RQ3 methods (K=20 default — K_optimal sweeps separate)
# sf100 skips slow methods (hdbscan/birch/spectral) — handle separately if needed
METHODS="hilbert hybrid minibatch minibatch_partial kdtree zorder pca1d gmm lsh pq sobol distance_shell random_proj kde_pilot sparse_rp importance_sampling"
if [ "$SF" != "100" ]; then
  METHODS="$METHODS hdbscan birch"
fi
for m in $METHODS; do
  $PYTHON rq3/chain_unified.py --dataset "$DS" --sf "$SF" --stage rq3_$m 2>&1 | tee -a "$LOG" || echo "[WARN] method $m failed"
done

echo "[$(date +%H:%M:%S)] === DONE $DS sf$SF ===" | tee -a "$LOG"
touch /tmp/run_${DS}_sf${SF}_done.flag
