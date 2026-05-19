#!/bin/bash
# 로컬 watchdog v2 — final_chain_done.flag 출현 시 자동 회수.
#
# 사용:
#   nohup bash _internal/scripts/watch_final_chain.sh > _internal/watch_final_chain.log 2>&1 &
#
# 동작:
#   1. 60s 마다 ssh capstone "ls /tmp/final_chain_done.flag" 체크
#   2. flag 출현 → scp 로 1M extra 8 method parquet + sift_mid_sel 회수
#   3. RQ3 분석 driver 자동 실행 → 산출 갱신
#   4. macOS 알림 발송
#   5. 종료
#
# 본 watchdog 는 watch_post_8m.sh (v1) 와 병렬 실행. v1 은 post_8m_done.flag,
# v2 는 final_chain_done.flag 전용.

set -uo pipefail

LOCAL_ROOT="/Users/hyunbin/Capstone"
RESULTS_DIR="$LOCAL_ROOT/experiments/results/rq3_agnostic"
RQ1_DIR="$LOCAL_ROOT/experiments/results/rq1_motivation"
LOG="$LOCAL_ROOT/_internal/watch_final_chain.log"
SERVER_CACHE="/mnt/hdd0/home/capstone2026/cache"
DONE_FLAG="/tmp/final_chain_done.flag"

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

notify() {
    local msg="$1"
    osascript -e "display notification \"$msg\" with title \"Capstone Final Chain Watchdog\"" 2>/dev/null || true
    echo "[$(KST)] NOTIFY: $msg"
}

echo "[$(KST)] watch_final_chain.sh START — polling $DONE_FLAG every 60s"
notify "final chain watchdog started"

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
echo "[$(KST)] step 1: rsync 1M extra 8 method parquet + meta"
for m in zorder hybrid minibatch_partial pca1d kdtree pq spectral birch; do
    rsync -avz "capstone:$SERVER_CACHE/rq1/rq3_${m}*.parquet" "$RESULTS_DIR/" 2>&1 | tail -2 || true
    rsync -avz "capstone:$SERVER_CACHE/rq1/rq3_${m}*.json" "$RESULTS_DIR/" 2>&1 | tail -2 || true
done

echo "[$(KST)] step 2: rsync SIFT mid-sel"
rsync -avz "capstone:$SERVER_CACHE/rq1/sift_mid_sel*.parquet" "$RQ1_DIR/" 2>&1 | tail -3 || true
rsync -avz "capstone:$SERVER_CACHE/rq1/sift_mid_sel*.json" "$RQ1_DIR/" 2>&1 | tail -3 || true

echo "[$(KST)] step 3: rsync final_chain.log + 측정 logs"
rsync -avz "capstone:$SERVER_CACHE/final_chain.log" "$LOCAL_ROOT/_internal/final_chain_$(date +%Y%m%d_%H%M).log" 2>&1 | tail -3 || true
rsync -avz "capstone:$SERVER_CACHE/rq3/logs/" "$LOCAL_ROOT/_internal/rq3_logs_$(date +%Y%m%d_%H%M)/" 2>&1 | tail -3 || true

echo "[$(KST)] step 4: RQ3 분석 driver 자동 재실행 (1M extra 합산)"
cd "$LOCAL_ROOT"
python3 experiments/code/local_analysis/rq3_recovery_analysis.py 2>&1 | tee -a "$LOG" | tail -20

echo "[$(KST)] step 5: 보강 분석 갱신"
python3 experiments/code/local_analysis/rq3_bootstrap_effect_size.py 2>&1 | tee -a "$LOG" | tail -10
python3 experiments/code/local_analysis/rq3_per_query_ranking.py 2>&1 | tee -a "$LOG" | tail -5
python3 experiments/code/local_analysis/rq3_method_redundancy_ari.py 2>&1 | tee -a "$LOG" | tail -5 || true
python3 experiments/code/local_analysis/rq3_oltp_cost_and_routing.py 2>&1 | tee -a "$LOG" | tail -5 || true
python3 experiments/code/local_analysis/rq3_sampling_metrics_ess_deff_icc.py 2>&1 | tee -a "$LOG" | tail -5 || true

echo "[$(KST)] step 6: RQ1 단조성 재검정 (sift mid-sel 합산 후)"
python3 experiments/code/local_analysis/rq1_gradient_monotonicity.py 2>&1 | tee -a "$LOG" | tail -10 || true

echo "[$(KST)] step 7: figures 재생성"
python3 experiments/code/local_analysis/rq3_figures_supplementary.py 2>&1 | tee -a "$LOG" | tail -5 || true

PARQUET_COUNT=$(ls "$RESULTS_DIR"/rq3_zorder*.parquet "$RESULTS_DIR"/rq3_hybrid*.parquet \
    "$RESULTS_DIR"/rq3_minibatch_partial*.parquet "$RESULTS_DIR"/rq3_pca1d*.parquet \
    "$RESULTS_DIR"/rq3_kdtree*.parquet "$RESULTS_DIR"/rq3_pq*.parquet \
    "$RESULTS_DIR"/rq3_spectral*.parquet "$RESULTS_DIR"/rq3_birch*.parquet 2>/dev/null \
    | wc -l | tr -d ' ')

notify "final chain 회수 완료 — 1M extra $PARQUET_COUNT files + sift_mid_sel"
echo "[$(KST)] watch_final_chain.sh END — $PARQUET_COUNT 1M extra parquet retrieved"
