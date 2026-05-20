#!/bin/bash
# v9 selectivity sweep — FIXED 5/16 — 모든 cell × sel = 0.001/0.10 × 사용 16 method + B1
# 5/16 세션 — 이전 v9 (results_v9_sel_sweep_20260515_1855) 무효 fix 재launch
#
# 무효 원인: 측정 명령에 --sel 미전달 → 전부 sel=0.01 로 고정 측정됨.
# fix: measure_paper_exact.py 에 --sel CLI 인자 추가 완료 (검증: A5-sf1-SIFT B1
#      sel=0.001 → qe_trim 2.299 vs sel=0.10 → 1.778 으로 명확히 다름).
#      이 script 는 모든 측정 호출에 --sel $SEL 전달.
#
# Scope:
#   16 cell × 2 sel (sel=0.001, sel=0.10) × 17 (B1 + 16 method) = 544 file
#   + K granularity 4 cell (A1-SIFT/A1-SSN × K=10/30) × 2 sel × 17 = 136 file
#   = 680 file
#   - sel=0.01 는 기존 v6/v7/v10 측정 완료 → v9 는 0.001/0.10 만
# 추정 server time: ~27-30h
#
# 목적: selectivity-dependent 대조군 vs 실험군 비교 evidence (narrative §5)

set -e
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
# 새 timestamp 디렉토리 — 기존 무효 results_v9_sel_sweep_20260515_1855 는 건드리지 X
OUT_BASE=/mnt/hdd0/home/capstone2026/results_v9_sel_sweep_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p $LOG_DIR

echo "[$(date)] === v9 sel sweep (FIXED) launch START ===" | tee $LOG_DIR/_main.log
echo "OUT_BASE=$OUT_BASE" | tee -a $LOG_DIR/_main.log

# 사용 16 method (Pareto Top 5 + paradigm rep 11) — 기존 M16 그대로
M16=(sparse_rp chao_weighted hilbert_real hyperloglog pca1d \
     minibatch_partial gmm faiss_ivf \
     zorder_morton skilling_hilbert \
     rsvd ica_fastica \
     cum_sqrtf lavallee_hidiroglou \
     rabitq_strat mhist2)

# 16 cell (K granularity 4 별도 처리)
CELLS_ALL=(\
  A5-scale-sf1-SIFT A5-scale-sf10-SIFT A5-scale-sf1-SSN A5-scale-sf10-SSN \
  A6-WIKI-sf10 A6-WIKI-sf1 A7-YFCC-sf1 A8-DEEP+SIFT-sf10 \
  A1-DEEP A1-SIFT A1-SSN \
  A5-scale-sf1 A5-scale-sf10 A5-scale-sf100 \
  A2-Fig7 A2-Fig9)

run_sel_cell() {
  local CELL=$1
  local SEL=$2
  local OUT=$3
  local SUFFIX=$4  # K10 / K30 또는 ""
  shift 4
  local METHODS=("$@")
  mkdir -p $OUT
  # --- B1 ---
  if [ -f "$OUT/${CELL}_B1.json" ]; then
    echo "[$(date +%H:%M:%S)] [skip] $CELL${SUFFIX} sel=$SEL B1 (JSON 존재)" | tee -a $LOG_DIR/_main.log
  else
    echo "[$(date +%H:%M:%S)] === $CELL${SUFFIX} sel=$SEL B1 ===" | tee -a $LOG_DIR/_main.log
    python3 $SCRIPT --rq 3 --phase A --cell $CELL --mode B1 --sel $SEL --output $OUT 2>&1 | tee $LOG_DIR/${CELL}${SUFFIX}_sel${SEL}_B1.log || echo "[WARN] B1 failed"
  fi
  # --- CaseB × 16 method ---
  for m in "${METHODS[@]}"; do
    if [ -f "$OUT/${CELL}_CaseB_${m}.json" ]; then
      echo "[$(date +%H:%M:%S)] [skip] $CELL${SUFFIX} sel=$SEL CaseB $m (JSON 존재)" | tee -a $LOG_DIR/_main.log
      continue
    fi
    echo "[$(date +%H:%M:%S)] === $CELL${SUFFIX} sel=$SEL CaseB $m ===" | tee -a $LOG_DIR/_main.log
    python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseB --method $m --sel $SEL --output $OUT 2>&1 | tee $LOG_DIR/${CELL}${SUFFIX}_sel${SEL}_CaseB_${m}.log || echo "[WARN] $m failed"
  done
}

# ==== 16 cell × 2 sel = 544 file ====
echo "[$(date)] === 16 cell × 2 sel (0.001 + 0.10) × 17 method = 544 file ===" | tee -a $LOG_DIR/_main.log
for CELL in "${CELLS_ALL[@]}"; do
  for SEL in 0.001 0.10; do
    OUT=$OUT_BASE/${CELL}_sel${SEL}
    run_sel_cell $CELL $SEL $OUT "" "${M16[@]}"
  done
done

# ==== K granularity 4 cell × 2 sel × 17 method = 136 file ====
echo "[$(date)] === K granularity 4 cell × 2 sel × 17 = 136 file ===" | tee -a $LOG_DIR/_main.log
for CELL in A1-SIFT A1-SSN; do
  for K in 10 30; do
    for SEL in 0.001 0.10; do
      OUT=$OUT_BASE/${CELL}_K${K}_sel${SEL}
      mkdir -p $OUT
      # --- B1 ---
      if [ -f "$OUT/${CELL}_B1.json" ]; then
        echo "[$(date +%H:%M:%S)] [skip] $CELL K=$K sel=$SEL B1 (JSON 존재)" | tee -a $LOG_DIR/_main.log
      else
        echo "[$(date +%H:%M:%S)] === $CELL K=$K sel=$SEL B1 ===" | tee -a $LOG_DIR/_main.log
        STRATA_K=$K python3 $SCRIPT --rq 3 --phase A --cell $CELL --mode B1 --sel $SEL --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_K${K}_sel${SEL}_B1.log || echo "[WARN] B1 failed"
      fi
      # --- CaseB × 16 method ---
      for m in "${M16[@]}"; do
        if [ -f "$OUT/${CELL}_CaseB_${m}.json" ]; then
          echo "[$(date +%H:%M:%S)] [skip] $CELL K=$K sel=$SEL CaseB $m (JSON 존재)" | tee -a $LOG_DIR/_main.log
          continue
        fi
        echo "[$(date +%H:%M:%S)] === $CELL K=$K sel=$SEL CaseB $m ===" | tee -a $LOG_DIR/_main.log
        STRATA_K=$K python3 $SCRIPT --rq 3 --phase B --cell $CELL --mode CaseB --method $m --sel $SEL --output $OUT 2>&1 | tee $LOG_DIR/${CELL}_K${K}_sel${SEL}_CaseB_${m}.log || echo "[WARN] $m failed"
      done
    done
  done
done

echo "[$(date)] === v9 ALL DONE ===" | tee -a $LOG_DIR/_main.log
touch $OUT_BASE/COMPLETE.flag
