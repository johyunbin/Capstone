#!/bin/bash
# SIFT 1M (Option 1) — build → kmeans → querypool → RQ1+RQ2+RQ3 measurement
set -e
cd /mnt/hdd0/home/capstone2026/cache
LOG=/tmp/sift_1m_full_chain.out
TS() { date +%H:%M:%S; }

echo "[$(TS)] === SIFT 1M FULL CHAIN START ===" | tee -a $LOG

# Step 1-4: build (PG INSERT 1M rows)
echo "[$(TS)] STEP 1-4 build_sift_1m" | tee -a $LOG
python3 -u build_sift_1m.py 2>&1 | tee /tmp/sift_1m_build.log
echo "[$(TS)] STEP 1-4 DONE" | tee -a $LOG

# Step 5-6: KMeans + UPDATE + σ
echo "[$(TS)] STEP 5-6 kmeans_strata" | tee -a $LOG
python3 -u sift_1m_kmeans_strata.py 2>&1 | tee /tmp/sift_1m_kmeans.log
echo "[$(TS)] STEP 5-6 DONE" | tee -a $LOG

# Step 7: query pool
echo "[$(TS)] STEP 7 querypool" | tee -a $LOG
python3 -u sift_1m_querypool.py 2>&1 | tee /tmp/sift_1m_querypool.log
echo "[$(TS)] STEP 7 DONE" | tee -a $LOG

# Step 8 RQ1 km20 + bern
cd /mnt/hdd0/home/capstone2026/cache/rq3
echo "[$(TS)] STEP 8 RQ1 km20" | tee -a $LOG
python3 -u sift_1m_measure_chain.py rq1_km20 2>&1 | tee /tmp/sift_1m_rq1_km20.log
echo "[$(TS)] STEP 8 RQ1 DONE" | tee -a $LOG

# RQ3 random20
echo "[$(TS)] STEP 9 RQ3 random20" | tee -a $LOG
python3 -u sift_1m_measure_chain.py rq3_random20 2>&1 | tee /tmp/sift_1m_rq3_random20.log
echo "[$(TS)] STEP 9 RQ3 random20 DONE" | tee -a $LOG

# RQ2 5-mode
echo "[$(TS)] STEP 10 RQ2 5mode" | tee -a $LOG
python3 -u sift_1m_measure_chain.py rq2_5mode 2>&1 | tee /tmp/sift_1m_rq2_5mode.log
echo "[$(TS)] STEP 10 RQ2 DONE" | tee -a $LOG

# RQ3 19 methods
for method in minibatch hilbert random_proj lsh kde_pilot kdtree pca1d zorder hybrid minibatch_partial pq spectral birch distance_shell sobol sparse_rp gmm hdbscan importance_sampling; do
    echo "[$(TS)] RQ3 $method" | tee -a $LOG
    python3 -u sift_1m_measure_chain.py rq3_$method 2>&1 | tee /tmp/sift_1m_rq3_$method.log
    echo "[$(TS)] RQ3 $method DONE" | tee -a $LOG
done

touch /tmp/sift_1m_full_chain_done.flag
echo "[$(TS)] === SIFT 1M FULL CHAIN COMPLETE ===" | tee -a $LOG
