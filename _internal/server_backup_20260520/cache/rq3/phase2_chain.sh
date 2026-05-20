#!/bin/bash
# Phase 2 chain — final_chain_done.flag 출현 후 4 missing method 추가 측정.
#
# 흐름:
#   1. /tmp/final_chain_done.flag 감지 (final_chain.sh 종료 → 1차 8 method + sift 끝남)
#   2. 4 추가 method 순차 측정 (gmm/hdbscan/sobol/sparse_rp)
#   3. /tmp/phase2_done.flag 생성
#
# 주의: DEEP s=0.05 numpy 는 prerequisite parquet (query_selectivity_5sel_numpy.parquet)
#        이 미존재 → phase2 미포함. 사용자 도착 후 별도 진행.

set -uo pipefail

CACHE=/mnt/hdd0/home/capstone2026/cache
RQ3=$CACHE/rq3
LOG=$CACHE/phase2_chain.log
LOGS=$RQ3/logs

DONE_FLAG=/tmp/final_chain_done.flag
PHASE2_FLAG=/tmp/phase2_done.flag

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

mkdir -p "$LOGS"

echo "[$(KST)] phase2_chain.sh START — waiting for $DONE_FLAG"

# === 1. final_chain_done.flag 대기 ===
while [ ! -f "$DONE_FLAG" ]; do
    sleep 60
done
echo "[$(KST)] $DONE_FLAG detected — proceed to phase 2 (4 missing methods)"

cd "$RQ3"

# === 2. 4 missing method 순차 측정 ===
METHODS=(gmm hdbscan sobol sparse_rp)
for m in "${METHODS[@]}"; do
    echo ""
    echo "[$(KST)] === Phase 2: run_${m}.py START ==="
    if python3 "run_${m}.py" 2>&1 | tee "$LOGS/rq3_${m}_1m.log" | tail -3; then
        echo "[$(KST)] run_${m}.py DONE"
    else
        echo "[$(KST)] run_${m}.py FAILED — continuing"
    fi
done

# === 3. phase2 flag ===
echo ""
echo "[$(KST)] phase2_chain.sh END" > "$PHASE2_FLAG"
echo "[$(KST)] $PHASE2_FLAG generated."
echo ""
echo "산출 location:"
echo "  /mnt/hdd0/home/capstone2026/cache/rq1/rq3_{gmm,hdbscan,sobol,sparse_rp}*.parquet"
