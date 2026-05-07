#!/bin/bash
# SIFT 8M 모든 측정 sequential chain
# v2 wrapper deploy 후 실행

set -e
cd /mnt/hdd0/home/capstone2026/cache/rq3
LOG=/tmp/sift_8m_full_chain.out
TS() { date +%H:%M:%S; }

echo "[$(TS)] === SIFT 8M FULL CHAIN START ===" | tee -a $LOG

# RQ1 KM20 (with BERN baseline)
echo "[$(TS)] RQ1 km20+bern" | tee -a $LOG
python3 -u sift_8m_measure_chain.py rq1_km20 2>&1 | tee /tmp/sift_8m_rq1_km20.log
echo "[$(TS)] RQ1 km20+bern DONE" | tee -a $LOG

# RQ3 random20 (Recovery rate denominator)
echo "[$(TS)] RQ3 random20" | tee -a $LOG
python3 -u sift_8m_measure_chain.py rq3_random20 2>&1 | tee /tmp/sift_8m_rq3_random20.log
echo "[$(TS)] RQ3 random20 DONE" | tee -a $LOG

# RQ2 5-mode
echo "[$(TS)] RQ2 5mode" | tee -a $LOG
python3 -u sift_8m_measure_chain.py rq2_5mode 2>&1 | tee /tmp/sift_8m_rq2_5mode.log
echo "[$(TS)] RQ2 5mode DONE" | tee -a $LOG

# RQ3 19 methods sequential
for method in minibatch hilbert random_proj lsh kde_pilot kdtree pca1d zorder hybrid minibatch_partial pq spectral birch distance_shell sobol sparse_rp gmm hdbscan importance_sampling; do
    echo "[$(TS)] RQ3 $method" | tee -a $LOG
    python3 -u sift_8m_measure_chain.py rq3_$method 2>&1 | tee /tmp/sift_8m_rq3_$method.log
    echo "[$(TS)] RQ3 $method DONE" | tee -a $LOG
done

touch /tmp/sift_8m_full_chain_done.flag
echo "[$(TS)] === SIFT 8M FULL CHAIN COMPLETE ===" | tee -a $LOG
