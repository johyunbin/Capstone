#!/bin/bash
# SIFT 8M resume — KMeans + querypool 완료, RQ1+RQ3+RQ2+19method 부터
set +e  # don't exit on individual method fail (for resilience)
cd /mnt/hdd0/home/capstone2026/cache/rq3
LOG=/tmp/sift_8m_resume_chain.out
TS() { date +%H:%M:%S; }

echo "[$(TS)] === SIFT 8M RESUME (skip kmeans+querypool) ===" | tee -a $LOG

echo "[$(TS)] RQ1 km20+bern" | tee -a $LOG
python3 -u sift_8m_measure_chain.py rq1_km20 2>&1 | tee /tmp/sift_8m_rq1_km20.log
echo "[$(TS)] RQ1 km20+bern END (rc=$?)" | tee -a $LOG

echo "[$(TS)] RQ3 random20" | tee -a $LOG
python3 -u sift_8m_measure_chain.py rq3_random20 2>&1 | tee /tmp/sift_8m_rq3_random20.log
echo "[$(TS)] RQ3 random20 END (rc=$?)" | tee -a $LOG

echo "[$(TS)] RQ2 5mode" | tee -a $LOG
python3 -u sift_8m_measure_chain.py rq2_5mode 2>&1 | tee /tmp/sift_8m_rq2_5mode.log
echo "[$(TS)] RQ2 5mode END (rc=$?)" | tee -a $LOG

for method in minibatch hilbert random_proj lsh kde_pilot kdtree pca1d zorder hybrid minibatch_partial pq spectral birch distance_shell sobol sparse_rp gmm hdbscan importance_sampling; do
    echo "[$(TS)] RQ3 $method" | tee -a $LOG
    python3 -u sift_8m_measure_chain.py rq3_$method 2>&1 | tee /tmp/sift_8m_rq3_$method.log
    echo "[$(TS)] RQ3 $method END (rc=$?)" | tee -a $LOG
done

touch /tmp/sift_8m_resume_done.flag
echo "[$(TS)] === SIFT 8M RESUME COMPLETE ===" | tee -a $LOG
