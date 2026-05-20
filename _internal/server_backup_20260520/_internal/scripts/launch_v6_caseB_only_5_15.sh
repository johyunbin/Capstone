#!/bin/bash
# v6 narrative — CaseB only (실험군 vs 대조군 framing)
# 5/15 23:00 session — CaseA 완전 폐기 + KeyError fix 적용 + Type 별 출력 dir
#
# Scope:
#   P1 (Type 1/2 evidence): SIFT/SSN sf=1/sf=10 × B1 + CaseB × Pareto Top 5 = 4 cell × 6 = 24 file
#   P3a (Type 4b single baseline): WIKI sf=10 × B1 + CaseB × 5 = 6 file
#   P5 (K granularity Type 3): SIFT/SSN A1 × K=10/30 × B1 + CaseB × 4 anchor = 2×2×5 = 20 file
# Total: 50 file, 추정 server time 3-6h.
#
# 사용법:
#   tmux new -d -s v6_caseB 'bash /mnt/hdd0/home/capstone2026/_internal/scripts/launch_v6_caseB_only_5_15.sh'
#
# Out: /mnt/hdd0/home/capstone2026/results_v6_caseB_${TS}/

set -e
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_v6_caseB_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p $LOG_DIR

echo "[$(date)] === v6 caseB-only launch START ===" | tee $LOG_DIR/_main.log
echo "OUT_BASE=$OUT_BASE" | tee -a $LOG_DIR/_main.log

PARETO5=("sparse_rp" "chao_weighted" "hilbert_real" "hyperloglog" "pca1d")
K_ANCHOR=("sparse_rp" "chao_weighted" "hilbert_real" "hyperloglog")

# B1 + CaseB only (CaseA framing 안 제거)
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

run_caseB_K() {
  local CELL=$1
  local K=$2
  local OUT=$3
  shift 3
  local METHODS=("$@")
  mkdir -p $OUT
  echo "[$(date +%H:%M:%S)] === $CELL K=$K B1 ===" | tee -a $LOG_DIR/_main.log
  STRATA_K=$K python3 $SCRIPT --rq 3 --phase A --cell $CELL --mode B1 --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_K${K}_B1.log || echo "[WARN] $CELL K=$K B1 failed"
  for m in "${METHODS[@]}"; do
    echo "[$(date +%H:%M:%S)] === $CELL K=$K CaseB $m ===" | tee -a $LOG_DIR/_main.log
    STRATA_K=$K python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseB --method $m --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_K${K}_CaseB_${m}.log || echo "[WARN] $CELL K=$K CaseB $m failed"
  done
}

# ==== P1: Type 1/2 evidence (SIFT/SSN sf=1/10) ====
echo "[$(date)] === P1 START (4 cell × 6 file = 24 file) ===" | tee -a $LOG_DIR/_main.log
for CELL in A5-scale-sf1-SIFT A5-scale-sf10-SIFT A5-scale-sf1-SSN A5-scale-sf10-SSN; do
  run_caseB_only $CELL $OUT_BASE/$CELL "${PARETO5[@]}"
done

# ==== P3a: Type 4b single baseline (WIKI sf=10) ====
echo "[$(date)] === P3a START (1 cell × 6 file = 6 file) ===" | tee -a $LOG_DIR/_main.log
run_caseB_only A6-WIKI-sf10 $OUT_BASE/A6-WIKI-sf10 "${PARETO5[@]}"

# ==== P5: K granularity Type 3 (SIFT/SSN A1 K=10/30) ====
echo "[$(date)] === P5 START (2 dataset × 2 K × 5 file = 20 file) ===" | tee -a $LOG_DIR/_main.log
for CELL in A1-SIFT A1-SSN; do
  for K in 10 30; do
    run_caseB_K $CELL $K $OUT_BASE/${CELL}_K${K} "${K_ANCHOR[@]}"
  done
done

echo "[$(date)] === ALL DONE ===" | tee -a $LOG_DIR/_main.log
touch $OUT_BASE/COMPLETE.flag
