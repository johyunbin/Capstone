#!/bin/bash
# SIFT 8M dataset build + KMeans + query pool + RQ1/2/3 모든 측정
set +e  # 일부 method fail 해도 계속
LOG=/tmp/sift_8m_chain.out
echo "[$(date +%H:%M:%S)] === SIFT 8M CHAIN START ===" | tee -a $LOG

cd /mnt/hdd0/home/capstone2026/cache

# === STEP 1+2+3+4: BIGANN extract + PG 적재 ===
echo "[$(date +%H:%M:%S)] STEP 1-4: BIGANN extract + PG 적재" | tee -a $LOG
python3 build_sift_8m.py 2>&1 | tee /tmp/sift_8m_build.log
echo "[$(date +%H:%M:%S)] STEP 1-4 END (rc=${PIPESTATUS[0]})" | tee -a $LOG

# === STEP 5+6: KMeans + stratum_id + σ ===
echo "[$(date +%H:%M:%S)] STEP 5-6: KMeans + stratum_id + σ" | tee -a $LOG
python3 sift_8m_kmeans_strata.py 2>&1 | tee /tmp/sift_8m_kmeans.log
echo "[$(date +%H:%M:%S)] STEP 5-6 END" | tee -a $LOG

# === STEP 7: query pool + d_target ===
echo "[$(date +%H:%M:%S)] STEP 7: query pool + d_target" | tee -a $LOG
python3 sift_8m_querypool.py 2>&1 | tee /tmp/sift_8m_qp.log
echo "[$(date +%H:%M:%S)] STEP 7 END" | tee -a $LOG

# === STEP 8: RQ1 BERN + KM20 ===
echo "[$(date +%H:%M:%S)] STEP 8 RQ1: BERN + KM20" | tee -a $LOG
cd rq3
python3 sift_8m_measure_chain.py rq1_km20 2>&1 | tee /tmp/sift_8m_rq1.log
echo "[$(date +%H:%M:%S)] STEP 8 RQ1 END" | tee -a $LOG

# === STEP 9: RQ3 RANDOM20 (Recovery 분모) ===
echo "[$(date +%H:%M:%S)] STEP 9 RQ3 RANDOM20" | tee -a $LOG
python3 sift_8m_measure_chain.py rq3_random20 2>&1 | tee /tmp/sift_8m_rand20.log
echo "[$(date +%H:%M:%S)] STEP 9 END" | tee -a $LOG

# === STEP 10: RQ2 5-mode ===
echo "[$(date +%H:%M:%S)] STEP 10 RQ2 5-mode" | tee -a $LOG
python3 sift_8m_measure_chain.py rq2_5mode 2>&1 | tee /tmp/sift_8m_rq2.log
echo "[$(date +%H:%M:%S)] STEP 10 END" | tee -a $LOG

# === STEP 11: RQ3 19 method (parallel impossible — sequential) ===
echo "[$(date +%H:%M:%S)] STEP 11 RQ3 19 method" | tee -a $LOG
for METHOD in minibatch hilbert random_proj lsh kde_pilot kdtree pca1d zorder hybrid minibatch_partial pq spectral birch distance_shell sobol sparse_rp gmm hdbscan importance_sampling; do
  echo "[$(date +%H:%M:%S)]   - method=$METHOD" | tee -a $LOG
  python3 sift_8m_measure_chain.py rq3_$METHOD 2>&1 | tee /tmp/sift_8m_rq3_$METHOD.log
done
echo "[$(date +%H:%M:%S)] STEP 11 END" | tee -a $LOG

# 산출 inventory
echo "=== 산출 inventory ===" | tee -a $LOG
ls -la /mnt/hdd0/home/capstone2026/cache/rq1/rq*sift_8m*.parquet 2>&1 | tee -a $LOG

# 완료 flag
touch /tmp/sift_8m_chain_done.flag
echo "[$(date +%H:%M:%S)] === SIFT 8M CHAIN COMPLETE ===" | tee -a $LOG
