#!/bin/bash
TARGET_GB=41
PID=$(pgrep -x wget | head -1)
FILE=/mnt/hdd0/home/capstone2026/cache/yfcc_full/yfcc100m_vecs.fbin
LOG=/tmp/yfcc_dl_pause_monitor.log
echo "[$(date +%H:%M:%S)] monitor v2 start wget_pid=$PID target=${TARGET_GB}GB" | tee -a "$LOG"
while true; do
  size_gb=$(du -B 1G "$FILE" 2>/dev/null | awk "{print \$1}")
  if [ "${size_gb:-0}" -ge "$TARGET_GB" ]; then
    echo "[$(date +%H:%M:%S)] ${size_gb}GB ≥ ${TARGET_GB}GB → SIGSTOP wget pid=$PID" | tee -a "$LOG"
    kill -STOP $PID && echo "wget paused" | tee -a "$LOG"
    touch /tmp/yfcc_dl_paused.flag
    break
  fi
  sleep 20
done
echo "[$(date +%H:%M:%S)] launching yfcc_dl_pipeline" | tee -a "$LOG"
tmux new-session -d -s yfcc_dl_pipeline "cd /mnt/hdd0/home/capstone2026/cache && python3 build_yfcc.py --fit-only 2>&1 | tee /tmp/yfcc_dl_pipeline.log && python3 build_yfcc.py --sf 1 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && python3 build_yfcc.py --sf 10 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && python3 prepare_cell.py --dataset YFCC_DL --sf 1 --pg-update 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && python3 rq3/chain_unified.py --dataset YFCC_DL --sf 1 --stage rq1_km20 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && for K in 10 50 100 200; do python3 rq3/chain_unified.py --dataset YFCC_DL --sf 1 --stage rq1_km_k_\$K 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log; done && python3 rq3/chain_unified.py --dataset YFCC_DL --sf 1 --stage rq3_random20 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && python3 rq3/chain_unified.py --dataset YFCC_DL --sf 1 --stage rq2_5mode 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && for m in hilbert hybrid minibatch minibatch_partial kdtree zorder pca1d gmm lsh pq sobol distance_shell random_proj kde_pilot sparse_rp importance_sampling hdbscan birch dbscan agglomerative hierarchical_kmeans faiss_ivf pca_kmeans kmeans_pp coresets spectral; do python3 rq3/chain_unified.py --dataset YFCC_DL --sf 1 --stage rq3_\$m 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log; done && python3 prepare_cell.py --dataset YFCC_DL --sf 10 --pg-update 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && python3 rq3/chain_unified.py --dataset YFCC_DL --sf 10 --stage rq1_km20 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && for K in 10 50 100 200; do python3 rq3/chain_unified.py --dataset YFCC_DL --sf 10 --stage rq1_km_k_\$K 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log; done && python3 rq3/chain_unified.py --dataset YFCC_DL --sf 10 --stage rq3_random20 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && python3 rq3/chain_unified.py --dataset YFCC_DL --sf 10 --stage rq2_5mode 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log && for m in hilbert hybrid minibatch minibatch_partial kdtree zorder pca1d gmm lsh pq sobol distance_shell random_proj kde_pilot sparse_rp importance_sampling hdbscan birch dbscan agglomerative hierarchical_kmeans faiss_ivf pca_kmeans kmeans_pp coresets spectral; do python3 rq3/chain_unified.py --dataset YFCC_DL --sf 10 --stage rq3_\$m 2>&1 | tee -a /tmp/yfcc_dl_pipeline.log; done; touch /tmp/yfcc_dl_pipeline_done.flag"
echo "[$(date +%H:%M:%S)] yfcc_dl_pipeline launched" | tee -a "$LOG"
