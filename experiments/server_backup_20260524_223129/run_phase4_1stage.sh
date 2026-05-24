#!/bin/bash
# run_phase4_1stage.sh — Phase B/C 1-stage 재생성 + 측정 통합 자동 chain (5/21 15:00)
# codex finding #1: est_b1 2-stage cache → 1-stage fix 후 estimates 전체 재생성 + 전면 재측정
# 1. estimates 13 file 재생성 (1-stage, gen_latency_estimates.py all_vecs fix 적용본)
# 2. estimates 끝나면 launch_phase4_measure.sh all 자동 chain
set -u
cd /mnt/hdd0/home/capstone2026/cache/rq3
mkdir -p latency/phase4_extension
LOG=latency/phase4_extension/run_1stage.log
echo "=========== run_phase4_1stage start $(date +%F\ %T) ===========" | tee -a "$LOG"

gen_one() {
  local ds=$1 sf=$2
  if [ -f latency/phase4_extension/estimates_${ds}_sf${sf}.parquet ]; then
    echo "[$(date +%H:%M:%S)] estimates $ds sf=$sf exists, skip" | tee -a "$LOG"
    return
  fi
  echo "[$(date +%H:%M:%S)] estimates $ds sf=$sf start" | tee -a "$LOG"
  nice -n 10 ionice -c 2 -n 7 timeout 60m python3 gen_latency_estimates.py \
    --dataset $ds --sf $sf --n-qvec 1 --output latency/phase4_extension/ 2>&1 | tail -3 | tee -a "$LOG"
  echo "[$(date +%H:%M:%S)] estimates $ds sf=$sf done" | tee -a "$LOG"
}

# --- Step 1: estimates 1-stage 재생성 ---
# sf=1/10 단일 5종 (10 file) = 4 병렬
echo "--- estimates sf=1/10 단일 5종 (4 병렬) ---" | tee -a "$LOG"
CNT=0
for ds in DEEP SIFT SSN WIKI YFCC; do
  for sf in 1 10; do
    gen_one $ds $sf &
    CNT=$((CNT + 1))
    if [ $CNT -ge 4 ]; then wait; CNT=0; fi
  done
done
wait
# sf=100 단일 3종 (3 file) = 2 병렬 (IO 부담 — peak 회피)
echo "--- estimates sf=100 단일 3종 (2 병렬) ---" | tee -a "$LOG"
CNT=0
for ds in DEEP SIFT SSN; do
  gen_one $ds 100 &
  CNT=$((CNT + 1))
  if [ $CNT -ge 2 ]; then wait; CNT=0; fi
done
wait
N_EST=$(ls latency/phase4_extension/estimates_*.parquet 2>/dev/null | wc -l | xargs)
echo "[$(date +%H:%M:%S)] estimates 재생성 완료 — $N_EST/13" | tee -a "$LOG"

# --- Step 2: measure 자동 chain ---
echo "--- measure launch (launch_phase4_measure.sh all) ---" | tee -a "$LOG"
bash launch_phase4_measure.sh all >> "$LOG" 2>&1
echo "=========== run_phase4_1stage end $(date +%F\ %T) ===========" | tee -a "$LOG"
ls latency/phase4_extension/latency_*.json 2>/dev/null | wc -l | xargs -I {} echo "raw JSON: {}" | tee -a "$LOG"
