#!/bin/bash
# v10 사용 16 method 영역 12 cell 보강 — Pareto Top 5 외 paradigm rep 11 method
# 5/16 00:30 session — handoff v31 §3 = 사용 16 method 확정 후 framing 일치 launch
#
# Scope:
#   12 cell × 11 method (Pareto5 외 paradigm rep) × CaseB = 132 file
#   단, A5-scale-sf1-SIFT × {cum_sqrtf, faiss_ivf, gmm} 3 file 영역 v8 측정 완료 → skip
#   = 132 - 3 = 129 file
# 추정 server time: ~2.2h (5/16 02:30 완료 예상)
#
# 목적: handoff v31 = 사용 16 method 영역 dynamic method selection axis 정확성 확보
#       (v8 영역 50 method 영역 framing 영역 → v10 영역 16 method 영역 framing 일치)
#
# 사용 16 method 영역 분류:
#   PARETO5 (이미 측정 완료, 본 script skip):
#     sparse_rp / chao_weighted / hilbert_real / hyperloglog / pca1d
#   추가 11 method (본 script 영역 측정):
#     P1 Cluster (3): minibatch_partial / gmm / faiss_ivf
#     P2 Spatial (2): zorder_morton / skilling_hilbert
#     P4 DimReduction (2): rsvd / ica_fastica
#     P5 QMC (2): cum_sqrtf / lavallee_hidiroglou
#     P6 Quantization (2): rabitq_strat / mhist2

set -e
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_v10_full16_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p $LOG_DIR

echo "[$(date)] === v10 사용 16 method 영역 launch START ===" | tee $LOG_DIR/_main.log
echo "OUT_BASE=$OUT_BASE" | tee -a $LOG_DIR/_main.log

# 추가 11 method (Pareto Top 5 외)
M11=(minibatch_partial gmm faiss_ivf zorder_morton skilling_hilbert rsvd ica_fastica cum_sqrtf lavallee_hidiroglou rabitq_strat mhist2)

# v8 영역 A5-scale-sf1-SIFT cell 영역 이미 측정된 method (skip 대상)
# v8 result 영역 28 file 中 사용 16 method intersect = {cum_sqrtf, faiss_ivf, gmm}
M11_SKIP_A5_sf1_SIFT=(cum_sqrtf faiss_ivf gmm)

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

run_caseB_full_skip() {
  # A5-scale-sf1-SIFT cell 전용 — 3 method skip
  local CELL=$1
  local OUT=$2
  shift 2
  local METHODS=("$@")
  mkdir -p $OUT
  for m in "${METHODS[@]}"; do
    # skip check
    local SKIP=0
    for s in "${M11_SKIP_A5_sf1_SIFT[@]}"; do
      if [ "$m" = "$s" ]; then
        SKIP=1
        break
      fi
    done
    if [ $SKIP -eq 1 ]; then
      echo "[$(date +%H:%M:%S)] === SKIP $CELL CaseB $m (v8 측정 완료) ===" | tee -a $LOG_DIR/_main.log
      continue
    fi
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

# ==== P1 (4 cell × 11 method = 44 file, but A5-scale-sf1-SIFT skip 3 → 41 file) ====
echo "[$(date)] === P1 16method boost (A5-scale-sf1-SIFT skip 3) ===" | tee -a $LOG_DIR/_main.log
run_caseB_full_skip A5-scale-sf1-SIFT $OUT_BASE/A5-scale-sf1-SIFT "${M11[@]}"
for CELL in A5-scale-sf10-SIFT A5-scale-sf1-SSN A5-scale-sf10-SSN; do
  run_caseB_full $CELL $OUT_BASE/$CELL "${M11[@]}"
done

# ==== P3a (1 cell × 11 method = 11 file) ====
echo "[$(date)] === P3a 16method boost ===" | tee -a $LOG_DIR/_main.log
run_caseB_full A6-WIKI-sf10 $OUT_BASE/A6-WIKI-sf10 "${M11[@]}"

# ==== P5 K granularity (2 dataset × 2 K × 11 method = 44 file) ====
echo "[$(date)] === P5 K granularity 16method boost ===" | tee -a $LOG_DIR/_main.log
for CELL in A1-SIFT A1-SSN; do
  for K in 10 30; do
    run_caseB_K $CELL $K $OUT_BASE/${CELL}_K${K} "${M11[@]}"
  done
done

# ==== v7 cell (3 cell × 11 method = 33 file) ====
echo "[$(date)] === v7 extras 16method boost ===" | tee -a $LOG_DIR/_main.log
for CELL in A6-WIKI-sf1 A7-YFCC-sf1 A8-DEEP+SIFT-sf10; do
  run_caseB_full $CELL $OUT_BASE/$CELL "${M11[@]}"
done

echo "[$(date)] === v10 ALL DONE (129 file) ===" | tee -a $LOG_DIR/_main.log
touch $OUT_BASE/COMPLETE.flag
