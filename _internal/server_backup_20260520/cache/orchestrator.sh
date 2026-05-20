#!/bin/bash
LOG=/tmp/orchestrator.log
echo "[$(date +%H:%M:%S)] === orchestrator v6 (15-cell + analysis auto) ===" | tee -a "$LOG"
declare -A FIRED
fire_once() { if [ -z "${FIRED[$1]}" ]; then FIRED[$1]=1; echo "[$(date +%H:%M:%S)] FIRE: $1" | tee -a "$LOG"; return 0; fi; return 1; }

while true; do
  if [ -f /tmp/run_SSN_sf10_done.flag ] && fire_once "sf10_NEW9_SSN"; then
    tmux new-session -d -s sf10_NEW9_SSN "cd /mnt/hdd0/home/capstone2026/cache && for m in dbscan agglomerative hierarchical_kmeans faiss_ivf pca_kmeans kmeans_pp coresets spectral; do python3 rq3/chain_unified.py --dataset SSN --sf 10 --stage rq3_\$m 2>&1 | tee -a /tmp/sf10_NEW9_SSN.log; done; touch /tmp/sf10_NEW9_SSN_done.flag" 2>&1 | tee -a "$LOG"
  fi
  if [ -f /tmp/build_wiki_sf10_done.flag ] && fire_once "wiki_sf10_chain"; then
    tmux new-session -d -s wiki_sf10 "cd /mnt/hdd0/home/capstone2026/cache && python3 prepare_cell.py --dataset WIKI --sf 10 --pg-update 2>&1 | tee /tmp/wiki_sf10_full.log && python3 rq3/chain_unified.py --dataset WIKI --sf 10 --stage rq1_km20 2>&1 | tee -a /tmp/wiki_sf10_full.log && for K in 10 50 100 200; do python3 rq3/chain_unified.py --dataset WIKI --sf 10 --stage rq1_km_k_\$K 2>&1 | tee -a /tmp/wiki_sf10_full.log; done && python3 rq3/chain_unified.py --dataset WIKI --sf 10 --stage rq3_random20 2>&1 | tee -a /tmp/wiki_sf10_full.log && python3 rq3/chain_unified.py --dataset WIKI --sf 10 --stage rq2_5mode 2>&1 | tee -a /tmp/wiki_sf10_full.log && for m in hilbert hybrid minibatch minibatch_partial kdtree zorder pca1d gmm lsh pq sobol distance_shell random_proj kde_pilot sparse_rp importance_sampling hdbscan birch dbscan agglomerative hierarchical_kmeans faiss_ivf pca_kmeans kmeans_pp coresets spectral; do python3 rq3/chain_unified.py --dataset WIKI --sf 10 --stage rq3_\$m 2>&1 | tee -a /tmp/wiki_sf10_full.log; done; touch /tmp/wiki_sf10_full_done.flag" 2>&1 | tee -a "$LOG"
  fi
  # Analysis auto-trigger (15 cell summary + figures)
  if [ -f /tmp/yfcc_dl_pipeline_done.flag ] && [ -f /tmp/wiki_sf10_full_done.flag ] && fire_once "analyze_15cell"; then
    tmux new-session -d -s analyze_15cell "cd /mnt/hdd0/home/capstone2026/cache && python3 analyze_15cell_w4.py 2>&1 | tee /tmp/analyze_15cell.log && python3 plot_master_figures.py 2>&1 | tee -a /tmp/analyze_15cell.log && python3 compare_yfcc_distributions.py 2>&1 | tee -a /tmp/analyze_15cell.log; touch /tmp/analyze_15cell_done.flag" 2>&1 | tee -a "$LOG"
  fi
  sleep 60
done
