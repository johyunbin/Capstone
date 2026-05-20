#!/bin/bash
# DEEP 1M numpy D_target 일관 측정 (5 sel) — Phase 6/7 methodology 분리 완전화.
# W2 chain 끝난 후 별도 tmux 로 launch.

set -uo pipefail

CACHE=/mnt/hdd0/home/capstone2026/cache
LOG=$CACHE/w2_deep_5sel_numpy.log
CHAIN_FLAG=/tmp/w2_chain_done.flag

KST() { TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'; }

echo "[$(KST)] waiting for w2_chain done..."
while [ ! -f "$CHAIN_FLAG" ]; do
    sleep 60
done
echo "[$(KST)] w2_chain done — proceeding to DEEP 5-sel numpy"

cd "$CACHE"
for sel in 0.01 0.10 0.30 0.50; do
    echo ""
    echo "[$(KST)] === DEEP s=$sel numpy START ==="
    python3 deep_s005_numpy_remeasure.py --target-sel $sel 2>&1 | tee w2_deep_${sel}_numpy.log | tail -5
    # 산출 rename to avoid overwrite
    mv $CACHE/rq1/deep_s005_numpy_remeasure.parquet \
       $CACHE/rq1/deep_s${sel}_numpy_remeasure.parquet 2>/dev/null || true
    mv $CACHE/rq1/deep_s005_numpy_remeasure_summary.json \
       $CACHE/rq1/deep_s${sel}_numpy_remeasure_summary.json 2>/dev/null || true
done

# s=0.05 는 이미 측정됨 — rename 만
mv $CACHE/rq1/deep_s005_numpy_remeasure.parquet \
   $CACHE/rq1/deep_s0.05_numpy_remeasure.parquet 2>/dev/null || true
mv $CACHE/rq1/deep_s005_numpy_remeasure_summary.json \
   $CACHE/rq1/deep_s0.05_numpy_remeasure_summary.json 2>/dev/null || true

echo ""
echo "[$(KST)] DEEP 5-sel numpy 완료" > /tmp/w2_5sel_done.flag
echo "[$(KST)] all done"
