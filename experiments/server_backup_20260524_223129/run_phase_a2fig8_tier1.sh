#!/bin/bash
# A2-Fig8 (DEEP+WIKI 4-way) × Tier 1 11 method (B1 + CaseA + CaseB) launch
# Agent C (5/10 22:46) NPY symlink unblocker 빌드 후 가능 — partsupp_deep_wiki_10_vectors.npy → partsupp_deep_10_vectors.npy

cd /mnt/hdd0/home/capstone2026/cache/rq3

# Tier 1 11 method (handoff §9.3 verbatim)
TIER1_METHODS="sparse_rp random_projection minibatch hilbert gmm minibatch_partial lsh pca1d sobol reservoir faiss_ivf"

LOG_DIR="/mnt/hdd0/home/capstone2026/log"
TS=$(date +%Y%m%d_%H%M)
log="${LOG_DIR}/paper_exact_a2fig8_tier1_${TS}.log"

# B1 1번 + CaseA 11 + CaseB 11 = 23 measurements
cmd="cd /mnt/hdd0/home/capstone2026/cache/rq3 && export OMP_NUM_THREADS=128 && {"

# B1 baseline (method-agnostic)
cmd="$cmd echo '[\$(date +%H:%M:%S)] === A2-Fig8 × B1 baseline ===' | tee -a $log;"
cmd="$cmd python3 -u measure_paper_exact.py --rq 3 --phase A --cell A2-Fig8 --mode B1 2>&1 | tee -a $log;"

# CaseA + CaseB × Tier 1 11 method
for method in $TIER1_METHODS; do
  for mode in CaseA CaseB; do
    cmd="$cmd echo '[\$(date +%H:%M:%S)] === A2-Fig8 × ${method} × ${mode} ===' | tee -a $log;"
    cmd="$cmd python3 -u measure_paper_exact.py --rq 3 --phase B --cell A2-Fig8 --mode $mode --method $method 2>&1 | tee -a $log;"
  done
done
cmd="$cmd echo '[\$(date +%H:%M:%S)] DONE A2-Fig8 × Tier 1' | tee -a $log; }"

tmux new -d -s "a2fig8_tier1" "$cmd"
echo "[$(date +%H:%M:%S)] launched a2fig8_tier1 → $log"
echo "[$(date +%H:%M:%S)] Total: 1 B1 + 11 method × 2 mode = 23 measurements"
echo "[$(date +%H:%M:%S)] ETA ~30-60 min (1 fetch 22min + 23 measurements × 1-2min)"
