#!/bin/bash
# SIFT 8M resume v2 — minibatch 완료, hilbert 부터 18 method (npy cache fast path)
set +e
cd /mnt/hdd0/home/capstone2026/cache/rq3
LOG=/tmp/sift_8m_resume2_chain.out
TS() { date +%H:%M:%S; }

echo "[$(TS)] === SIFT 8M RESUME2 (npy cache, hilbert 부터) ===" | tee -a $LOG

for method in hilbert random_proj lsh kde_pilot kdtree pca1d zorder hybrid minibatch_partial pq spectral birch distance_shell sobol sparse_rp gmm hdbscan importance_sampling; do
    if [ -f "/mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_sift_${method}.parquet" ]; then
        echo "[$(TS)] RQ3 $method already done, skip" | tee -a $LOG
        continue
    fi
    echo "[$(TS)] RQ3 $method" | tee -a $LOG
    python3 -u sift_8m_measure_chain.py rq3_$method 2>&1 | tee /tmp/sift_8m_rq3_$method.log
    echo "[$(TS)] RQ3 $method END" | tee -a $LOG
done

touch /tmp/sift_8m_resume_done.flag
echo "[$(TS)] === SIFT 8M RESUME2 COMPLETE ===" | tee -a $LOG
