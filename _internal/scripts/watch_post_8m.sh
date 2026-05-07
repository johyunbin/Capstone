#!/bin/bash
# 로컬 watchdog — post_8m_done.flag 출현 시 자동 회수.
#
# 사용:
#   nohup bash _internal/scripts/watch_post_8m.sh > _internal/watch_post_8m.log 2>&1 &
#   # 또는 foreground:
#   bash _internal/scripts/watch_post_8m.sh
#
# 동작:
#   1. 60s 마다 ssh capstone "ls /tmp/post_8m_done.flag" 체크
#   2. flag 출현 → scp 로 모든 8M sensitivity parquet + log 회수
#   3. RQ3 분석 driver 자동 실행 → recovery_summary.csv 갱신
#   4. macOS 알림 발송 (osascript)
#   5. 종료
#
# 회수 후 사용자가 깨어나면 모든 산출 + 분석 ready 상태.

set -euo pipefail

LOCAL_ROOT="/Users/hyunbin/Capstone"
RESULTS_DIR="$LOCAL_ROOT/experiments/results/rq3_agnostic"
LOG="$LOCAL_ROOT/_internal/watch_post_8m.log"
SERVER_CACHE="/mnt/hdd0/home/capstone2026/cache"
DONE_FLAG="/tmp/post_8m_done.flag"

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

notify() {
    local msg="$1"
    osascript -e "display notification \"$msg\" with title \"Capstone 8M Watchdog\"" 2>/dev/null || true
    echo "[$(KST)] NOTIFY: $msg"
}

echo "[$(KST)] watch_post_8m.sh START — polling $DONE_FLAG every 60s"
notify "watchdog started — waiting for 8M sensitivity"

POLL_COUNT=0
while true; do
    POLL_COUNT=$((POLL_COUNT + 1))
    if ssh -o ConnectTimeout=10 capstone "ls $DONE_FLAG" >/dev/null 2>&1; then
        echo "[$(KST)] $DONE_FLAG detected after $POLL_COUNT polls"
        break
    fi
    if [ $((POLL_COUNT % 30)) -eq 0 ]; then
        echo "[$(KST)] still waiting ($POLL_COUNT polls = $((POLL_COUNT)) min)"
    fi
    sleep 60
done

# === 회수 ===
echo "[$(KST)] step 1: rsync 8M sensitivity parquet"
rsync -avz "capstone:$SERVER_CACHE/rq1/rq3_8m_*.parquet" "$RESULTS_DIR/" 2>&1 | tail -5 || {
    notify "rsync 실패 — 수동 확인 필요"
    exit 1
}

echo "[$(KST)] step 2: rsync auxiliary (8M dtarget + log)"
rsync -avz "capstone:$SERVER_CACHE/rq1/query_selectivity_8m.parquet" "$RESULTS_DIR/" 2>&1 | tail -3 || true
rsync -avz "capstone:$SERVER_CACHE/post_8m_pipeline.log" "$LOCAL_ROOT/_internal/post_8m_pipeline_$(date +%Y%m%d_%H%M).log" 2>&1 | tail -3 || true

echo "[$(KST)] step 3: 8M 측정 산출 회수"
rsync -avz "capstone:$SERVER_CACHE/rq1/2026_05_06_8m_midsel/" "$LOCAL_ROOT/experiments/results/rq1_motivation/2026_05_06_8m_midsel/" 2>&1 | tail -5 || true

echo "[$(KST)] step 4: RQ3 분석 driver 자동 실행"
cd "$LOCAL_ROOT"
python3 experiments/code/local_analysis/rq3_recovery_analysis.py 2>&1 | tee -a "$LOG" | tail -20

echo "[$(KST)] step 5: 보강 분석 갱신 (8M 데이터 포함)"
python3 experiments/code/local_analysis/rq3_bootstrap_effect_size.py 2>&1 | tee -a "$LOG" | tail -10
python3 experiments/code/local_analysis/rq3_per_query_ranking.py 2>&1 | tee -a "$LOG" | tail -5

echo "[$(KST)] step 6: figures 재생성"
python3 experiments/code/local_analysis/rq3_figures_supplementary.py 2>&1 | tee -a "$LOG" | tail -5

PARQUET_COUNT=$(ls "$RESULTS_DIR"/rq3_8m_*.parquet 2>/dev/null | wc -l | tr -d ' ')

notify "회수 완료 — 8M sensitivity $PARQUET_COUNT files. 분석 갱신됨."
echo "[$(KST)] watch_post_8m.sh END — $PARQUET_COUNT 8M parquet retrieved"
