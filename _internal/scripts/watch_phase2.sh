#!/bin/bash
# 로컬 watchdog v3 — phase2_done.flag 출현 시 자동 회수.
#
# 동작:
#   1. 60s 마다 ssh capstone "ls /tmp/phase2_done.flag" 체크
#   2. flag 출현 → scp 로 4 method (gmm/hdbscan/sobol/sparse_rp) parquet 회수
#   3. RQ3 분석 driver 자동 재실행 (12 + 4 = 16 method 전체)
#   4. macOS 알림 발송
#   5. 종료

set -uo pipefail

LOCAL_ROOT="/Users/hyunbin/Capstone"
RESULTS_DIR="$LOCAL_ROOT/experiments/results/rq3_agnostic"
LOG="$LOCAL_ROOT/_internal/watch_phase2.log"
SERVER_CACHE="/mnt/hdd0/home/capstone2026/cache"
DONE_FLAG="/tmp/phase2_done.flag"

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

notify() {
    local msg="$1"
    osascript -e "display notification \"$msg\" with title \"Capstone Phase 2 Watchdog\"" 2>/dev/null || true
    echo "[$(KST)] NOTIFY: $msg"
}

echo "[$(KST)] watch_phase2.sh START — polling $DONE_FLAG every 60s"
notify "phase 2 watchdog started"

POLL_COUNT=0
while true; do
    POLL_COUNT=$((POLL_COUNT + 1))
    if ssh -o ConnectTimeout=10 capstone "ls $DONE_FLAG" >/dev/null 2>&1; then
        echo "[$(KST)] $DONE_FLAG detected after $POLL_COUNT polls"
        break
    fi
    if [ $((POLL_COUNT % 60)) -eq 0 ]; then
        echo "[$(KST)] still waiting ($POLL_COUNT min)"
    fi
    sleep 60
done

# === 회수 ===
echo "[$(KST)] step 1: rsync 4 missing method parquet + meta"
for m in gmm hdbscan sobol sparse_rp; do
    rsync -avz "capstone:$SERVER_CACHE/rq1/rq3_${m}*.parquet" "$RESULTS_DIR/" 2>&1 | tail -2 || true
    rsync -avz "capstone:$SERVER_CACHE/rq1/rq3_${m}*.json" "$RESULTS_DIR/" 2>&1 | tail -2 || true
done

echo "[$(KST)] step 2: rsync phase2_chain.log + 측정 logs"
rsync -avz "capstone:$SERVER_CACHE/phase2_chain.log" "$LOCAL_ROOT/_internal/phase2_chain_$(date +%Y%m%d_%H%M).log" 2>&1 | tail -3 || true
rsync -avz "capstone:$SERVER_CACHE/rq3/logs/" "$LOCAL_ROOT/_internal/rq3_logs_phase2_$(date +%Y%m%d_%H%M)/" 2>&1 | tail -3 || true

echo "[$(KST)] step 3: RQ3 분석 driver 자동 재실행 (16 method 전체)"
cd "$LOCAL_ROOT"
python3 experiments/code/local_analysis/rq3_recovery_analysis.py 2>&1 | tee -a "$LOG" | tail -20

echo "[$(KST)] step 4: 보강 분석"
python3 experiments/code/local_analysis/rq3_bootstrap_effect_size.py 2>&1 | tee -a "$LOG" | tail -10
python3 experiments/code/local_analysis/rq3_per_query_ranking.py 2>&1 | tee -a "$LOG" | tail -5
python3 experiments/code/local_analysis/rq3_method_redundancy_ari.py 2>&1 | tee -a "$LOG" | tail -5 || true
python3 experiments/code/local_analysis/rq3_oltp_cost_and_routing.py 2>&1 | tee -a "$LOG" | tail -5 || true
python3 experiments/code/local_analysis/rq3_sampling_metrics_ess_deff_icc.py 2>&1 | tee -a "$LOG" | tail -5 || true

echo "[$(KST)] step 5: figures 재생성"
python3 experiments/code/local_analysis/rq3_figures_supplementary.py 2>&1 | tee -a "$LOG" | tail -5 || true

PARQUET_COUNT=$(ls "$RESULTS_DIR"/rq3_gmm*.parquet "$RESULTS_DIR"/rq3_hdbscan*.parquet \
    "$RESULTS_DIR"/rq3_sobol*.parquet "$RESULTS_DIR"/rq3_sparse_rp*.parquet 2>/dev/null \
    | wc -l | tr -d ' ')

notify "phase 2 회수 완료 — $PARQUET_COUNT method files. RQ3 16-method 전체 갱신됨."
echo "[$(KST)] watch_phase2.sh END — $PARQUET_COUNT phase2 parquet retrieved"
