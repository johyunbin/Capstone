#!/bin/bash
# v7 extras — 미커버 3 cell (LAION 제외 PG 적재 dataset 모두 cover)
# 5/15 23:25 session — v6 완료 후 launch
#
# Scope:
#   A6-WIKI-sf1: small 고차원 single (0.1M × 768d) = 6 file
#   A7-YFCC-sf1: small 중차원 single (0.1M × 192d) = 6 file
#   A8-DEEP+SIFT-sf10: medium multi 224d (1M × 96+128d) = 6 file
# Total: 18 file, 추정 1-2h.

set -e
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_v7_extras_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p $LOG_DIR

echo "[$(date)] === v7 extras launch START ===" | tee $LOG_DIR/_main.log
echo "OUT_BASE=$OUT_BASE" | tee -a $LOG_DIR/_main.log

PARETO5=("sparse_rp" "chao_weighted" "hilbert_real" "hyperloglog" "pca1d")

run_caseB_only() {
  local CELL=$1
  local OUT=$2
  shift 2
  local METHODS=("$@")
  mkdir -p $OUT
  echo "[$(date +%H:%M:%S)] === $CELL B1 (대조군) ===" | tee -a $LOG_DIR/_main.log
  python3 $SCRIPT --rq 3 --phase A --cell $CELL --mode B1 --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_B1.log || echo "[WARN] $CELL B1 failed"
  for m in "${METHODS[@]}"; do
    echo "[$(date +%H:%M:%S)] === $CELL CaseB $m (실험군) ===" | tee -a $LOG_DIR/_main.log
    python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseB --method $m --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_CaseB_${m}.log || echo "[WARN] $CELL CaseB $m failed"
  done
}

for CELL in A6-WIKI-sf1 A7-YFCC-sf1 A8-DEEP+SIFT-sf10; do
  run_caseB_only $CELL $OUT_BASE/$CELL "${PARETO5[@]}"
done

echo "[$(date)] === v7 ALL DONE ===" | tee -a $LOG_DIR/_main.log
touch $OUT_BASE/COMPLETE.flag
