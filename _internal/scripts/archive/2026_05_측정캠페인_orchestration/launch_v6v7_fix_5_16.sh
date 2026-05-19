#!/bin/bash
# v6+v7 fail 3 cell 재측정 — 5/16 00:30 KST session
#
# 영역:
#   1. A1-SIFT K=10 (5 fail) — KeyError 10 fix 적용 (PARETO5 = 5 method)
#   2. A1-SSN  K=10 (5 fail) — 동일
#   3. A8-DEEP+SIFT-sf10 (6 fail) — column "stratum_id" does not exist
#      → A8 영역 다른 agent 영역 NPY cache pre-compute 영역 진행 (선행) →
#        NPY ready 시 launch (없으면 30 min wait, timeout 후 skip)
#
# 사용 16 method 영역 (handoff 5/15 23:55):
#   PARETO5 = sparse_rp / chao_weighted / hilbert_real / hyperloglog / pca1d
#   + paradigm rep 11 (P1: minibatch_partial / gmm / faiss_ivf,
#                      P2: zorder_morton / skilling_hilbert,
#                      P4: rsvd / ica_fastica,
#                      P5: cum_sqrtf / lavallee_hidiroglou,
#                      P6: rabitq_strat / mhist2)
# 단, 본 script 영역 PARETO5 영역 5 method 영역 (fail 영역 PARETO5 영역 영역 발생)
#
# Total: 3 cell × (B1 1 + CaseB 5) = 3 × 6 = 18 file
# 추정 ETA:
#   - A1-SIFT/SSN K=10: ~30-50 min/cell (NPY cache hit 가정)
#   - A8 sf=10 (M=120K rows): ~60-90 min (NPY warm + sf=10 무거움)
#   - Total ~3-4h
#
# 사용법:
#   tmux new -d -s v6v7_fix 'bash /mnt/hdd0/home/capstone2026/_internal/scripts/launch_v6v7_fix_5_16.sh'
#
# Out: /mnt/hdd0/home/capstone2026/results_v6v7_fix_${TS}/

set -e
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_v6v7_fix_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p $LOG_DIR

echo "[$(date)] === v6v7 fix launch START ===" | tee $LOG_DIR/_main.log
echo "OUT_BASE=$OUT_BASE" | tee -a $LOG_DIR/_main.log

# Pareto Top 5 영역 (handoff 5/15 23:55)
PARETO5=("sparse_rp" "chao_weighted" "hilbert_real" "hyperloglog" "pca1d")

# B1 + CaseB only (CaseA 폐기 — handoff narrative v5)
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

# K override 영역 (STRATA_K env)
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

# A8 영역 NPY + stratum_id 영역 ready 검증
# NPY pre-compute agent 영역 stratum_id ALTER + KM20 cluster 영역 영역 영역 영역
wait_for_a8_ready() {
  local PG_HOST=/tmp
  local PG_PORT=55435
  local PG_DB=wns41559
  local PG_USER=wns41559
  local TABLE=partsupp_deep_sift_10
  local TIMEOUT=1800   # 30 min wait max
  local INTERVAL=60    # poll every 60s
  local elapsed=0
  echo "[$(date +%H:%M:%S)] === A8 readiness wait (NPY + stratum_id, max 30 min) ===" | tee -a $LOG_DIR/_main.log
  while [ $elapsed -lt $TIMEOUT ]; do
    # check stratum_id column 존재
    local has_col=$(PGHOST=$PG_HOST PGPORT=$PG_PORT psql -d $PG_DB -U $PG_USER -tAc \
      "SELECT 1 FROM information_schema.columns WHERE table_name='$TABLE' AND column_name='stratum_id'" 2>/dev/null)
    if [ "$has_col" = "1" ]; then
      # column 있으면 NULL count 확인 (clustering 완료 검증)
      local null_cnt=$(PGHOST=$PG_HOST PGPORT=$PG_PORT psql -d $PG_DB -U $PG_USER -tAc \
        "SELECT COUNT(*) FROM $TABLE WHERE stratum_id IS NULL" 2>/dev/null)
      if [ "$null_cnt" = "0" ]; then
        echo "[$(date +%H:%M:%S)]   A8 ready (stratum_id column populated)" | tee -a $LOG_DIR/_main.log
        return 0
      else
        echo "[$(date +%H:%M:%S)]   A8 stratum_id present but $null_cnt NULL — still computing..." | tee -a $LOG_DIR/_main.log
      fi
    else
      echo "[$(date +%H:%M:%S)]   A8 stratum_id column missing — waiting ($elapsed/${TIMEOUT}s)..." | tee -a $LOG_DIR/_main.log
    fi
    sleep $INTERVAL
    elapsed=$((elapsed + INTERVAL))
  done
  echo "[$(date +%H:%M:%S)] [WARN] A8 not ready after ${TIMEOUT}s — skipping A8" | tee -a $LOG_DIR/_main.log
  return 1
}

# ==== A1-SIFT K=10 재측정 ====
echo "[$(date)] === A1-SIFT K=10 START (1 cell × 6 file = 6 file) ===" | tee -a $LOG_DIR/_main.log
run_caseB_K A1-SIFT 10 $OUT_BASE/A1-SIFT_K10 "${PARETO5[@]}"

# ==== A1-SSN K=10 재측정 ====
echo "[$(date)] === A1-SSN K=10 START (1 cell × 6 file = 6 file) ===" | tee -a $LOG_DIR/_main.log
run_caseB_K A1-SSN 10 $OUT_BASE/A1-SSN_K10 "${PARETO5[@]}"

# ==== A8-DEEP+SIFT-sf10 재측정 (NPY ready 영역 wait) ====
if wait_for_a8_ready; then
  echo "[$(date)] === A8-DEEP+SIFT-sf10 START (1 cell × 6 file = 6 file) ===" | tee -a $LOG_DIR/_main.log
  run_caseB_only A8-DEEP+SIFT-sf10 $OUT_BASE/A8-DEEP+SIFT-sf10 "${PARETO5[@]}"
else
  echo "[$(date)] === A8 SKIPPED (not ready in 30 min — re-run separately) ===" | tee -a $LOG_DIR/_main.log
fi

echo "[$(date)] === ALL DONE ===" | tee -a $LOG_DIR/_main.log
touch $OUT_BASE/COMPLETE.flag
