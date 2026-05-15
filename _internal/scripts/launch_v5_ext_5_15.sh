#!/bin/bash
# v5 narrative extension measurement launch
# 5/15 21:30 session — measurement gap 보강 (P1 + P3a + P5)
#
# Scope:
#   P1 (Type 1/2 evidence): SIFT/SSN sf=1/sf=10 × Pareto Top 5 × CaseA/CaseB + B1 = 44 file
#   P3a (Type 4b single baseline): WIKI sf=10 × Pareto Top 5 × CaseA/CaseB + B1 = 11 file
#   P5 (K granularity dataset 확장): SIFT/SSN A1 × K=10/30 × 4 anchor × CaseA/CaseB + B1 = 36 file
# Total: ~91 file, 추정 12-15h server time.
#
# 사용법 (server):
#   tmux new -s v5_ext
#   bash /mnt/hdd0/home/capstone2026/_internal/scripts/launch_v5_ext_5_15.sh
#   (또는) nohup bash ... > log 2>&1 &
#
# 완료 신호: $OUT_BASE/COMPLETE.flag

set -e
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_v5_ext_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p $LOG_DIR

echo "[$(date)] === v5 extension launch START ===" | tee $LOG_DIR/_main.log
echo "OUT_BASE=$OUT_BASE" | tee -a $LOG_DIR/_main.log

PARETO5=("sparse_rp" "chao_weighted" "hilbert_real" "hyperloglog" "pca1d")
K_ANCHOR=("sparse_rp" "chao_weighted" "hilbert_real" "hyperloglog")

run_cell_full() {
  local CELL=$1
  local OUT=$2
  shift 2
  local METHODS=("$@")
  mkdir -p $OUT
  echo "[$(date +%H:%M:%S)] === $CELL B1 ===" | tee -a $LOG_DIR/_main.log
  python3 $SCRIPT --rq 3 --phase A --cell $CELL --mode B1 --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_B1.log || echo "[WARN] $CELL B1 failed"
  for m in "${METHODS[@]}"; do
    echo "[$(date +%H:%M:%S)] === $CELL CaseA $m ===" | tee -a $LOG_DIR/_main.log
    python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseA --method $m --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_CaseA_${m}.log || echo "[WARN] $CELL CaseA $m failed"
    echo "[$(date +%H:%M:%S)] === $CELL CaseB $m ===" | tee -a $LOG_DIR/_main.log
    python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseB --method $m --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_CaseB_${m}.log || echo "[WARN] $CELL CaseB $m failed"
  done
}

run_cell_K() {
  local CELL=$1
  local K=$2
  local OUT=$3
  shift 3
  local METHODS=("$@")
  mkdir -p $OUT
  echo "[$(date +%H:%M:%S)] === $CELL K=$K B1 ===" | tee -a $LOG_DIR/_main.log
  STRATA_K=$K python3 $SCRIPT --rq 3 --phase A --cell $CELL --mode B1 --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_K${K}_B1.log || echo "[WARN] $CELL K=$K B1 failed"
  for m in "${METHODS[@]}"; do
    echo "[$(date +%H:%M:%S)] === $CELL K=$K CaseA $m ===" | tee -a $LOG_DIR/_main.log
    STRATA_K=$K python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseA --method $m --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_K${K}_CaseA_${m}.log || echo "[WARN] $CELL K=$K CaseA $m failed"
    echo "[$(date +%H:%M:%S)] === $CELL K=$K CaseB $m ===" | tee -a $LOG_DIR/_main.log
    STRATA_K=$K python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseB --method $m --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_K${K}_CaseB_${m}.log || echo "[WARN] $CELL K=$K CaseB $m failed"
  done
}

# ==== P1: SIFT/SSN sf=1/10 ====
echo "[$(date)] === P1 START (4 cell × 11 file = 44 file) ===" | tee -a $LOG_DIR/_main.log
for CELL in A5-scale-sf1-SIFT A5-scale-sf10-SIFT A5-scale-sf1-SSN A5-scale-sf10-SSN; do
  run_cell_full $CELL $OUT_BASE/$CELL "${PARETO5[@]}"
done

# ==== P3a: WIKI single sf=10 ====
echo "[$(date)] === P3a START (1 cell × 11 file = 11 file) ===" | tee -a $LOG_DIR/_main.log
run_cell_full A6-WIKI-sf10 $OUT_BASE/A6-WIKI-sf10 "${PARETO5[@]}"

# ==== P5: K granularity SIFT/SSN K=10/30 ====
echo "[$(date)] === P5 START (2 dataset × 2 K × 9 file = 36 file) ===" | tee -a $LOG_DIR/_main.log
for CELL in A1-SIFT A1-SSN; do
  for K in 10 30; do
    run_cell_K $CELL $K $OUT_BASE/${CELL}_K${K} "${K_ANCHOR[@]}"
  done
done

echo "[$(date)] === ALL DONE ===" | tee -a $LOG_DIR/_main.log
touch $OUT_BASE/COMPLETE.flag
