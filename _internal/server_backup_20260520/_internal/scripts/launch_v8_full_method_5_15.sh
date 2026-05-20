#!/bin/bash
# v8 전수 method 보강 — 새 cell 12개 × 잔여 50 method (Pareto Top 5 제외)
# 5/15 23:30 session — v6 → v7 → v8 chain 마지막 단계
#
# Scope:
#   12 cell × 50 method × CaseB = 600 file
#   B1 은 v6/v7 에서 측정 완료 → 추가 X
# 추정 server time: ~27h (5/17 새벽 완료)
#
# 목적: dynamic method selection mechanism 정확성 위해 모든 method 측정 → cell × method best 식별

set -e
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_v8_full_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p $LOG_DIR

echo "[$(date)] === v8 full method launch START ===" | tee $LOG_DIR/_main.log
echo "OUT_BASE=$OUT_BASE" | tee -a $LOG_DIR/_main.log

# 잔여 50 method (Pareto Top 5 제외)
EXTRA50=(adaptive_bucket_probing agglomerative ams_count_sketch banditucb1 cca1d ccsketch cocluster_nystrom coreset cum_sqrtf dbscan dense_rp epsilon_net factor_join faiss_ivf gmm halton hammersley hilbert hkbu_repsample ica_fastica idistance idistance_neyman kdpp kdtree kmeans_neyman lavallee_hidiroglou lhs lp_bound lpm1_proper lpm2 lsh mfmc mhist2 minibatch minibatch_partial neuram neurocard_lite opq pq rabitq_strat random_projection reservoir rsvd skilling_hilbert sobol thompson_sampling tucker vinecopula wavelet_hist zorder_morton)

run_caseB_full() {
  local CELL=$1
  local OUT=$2
  shift 2
  local METHODS=("$@")
  mkdir -p $OUT
  for m in "${METHODS[@]}"; do
    echo "[$(date +%H:%M:%S)] === $CELL CaseB $m ===" | tee -a $LOG_DIR/_main.log
    python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseB --method $m --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_CaseB_${m}.log || echo "[WARN] $CELL CaseB $m failed"
  done
}

run_caseB_K() {
  local CELL=$1
  local K=$2
  local OUT=$3
  shift 3
  local METHODS=("$@")
  mkdir -p $OUT
  for m in "${METHODS[@]}"; do
    echo "[$(date +%H:%M:%S)] === $CELL K=$K CaseB $m ===" | tee -a $LOG_DIR/_main.log
    STRATA_K=$K python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseB --method $m --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_K${K}_CaseB_${m}.log || echo "[WARN] $CELL K=$K CaseB $m failed"
  done
}

# ==== P1 (4 cell × 50 method = 200 file) ====
echo "[$(date)] === P1 full method boost ===" | tee -a $LOG_DIR/_main.log
for CELL in A5-scale-sf1-SIFT A5-scale-sf10-SIFT A5-scale-sf1-SSN A5-scale-sf10-SSN; do
  run_caseB_full $CELL $OUT_BASE/$CELL "${EXTRA50[@]}"
done

# ==== P3a (1 cell × 50 method = 50 file) ====
echo "[$(date)] === P3a full method boost ===" | tee -a $LOG_DIR/_main.log
run_caseB_full A6-WIKI-sf10 $OUT_BASE/A6-WIKI-sf10 "${EXTRA50[@]}"

# ==== P5 K granularity (2 dataset × 2 K × 50 method = 200 file) ====
echo "[$(date)] === P5 K granularity full method boost ===" | tee -a $LOG_DIR/_main.log
for CELL in A1-SIFT A1-SSN; do
  for K in 10 30; do
    run_caseB_K $CELL $K $OUT_BASE/${CELL}_K${K} "${EXTRA50[@]}"
  done
done

# ==== v7 cell (3 cell × 50 method = 150 file) ====
echo "[$(date)] === v7 extras full method boost ===" | tee -a $LOG_DIR/_main.log
for CELL in A6-WIKI-sf1 A7-YFCC-sf1 A8-DEEP+SIFT-sf10; do
  run_caseB_full $CELL $OUT_BASE/$CELL "${EXTRA50[@]}"
done

echo "[$(date)] === v8 ALL DONE ===" | tee -a $LOG_DIR/_main.log
touch $OUT_BASE/COMPLETE.flag
