#!/bin/bash
# 8M post-pipeline 종료 후 자동 진행 chain.
#
# 흐름:
#   1. /tmp/post_8m_done.flag 감지 (post_8m_pipeline.sh 종료 → 8M sensitivity 5종 끝남)
#   2. 1M extra 8 method 순차 측정 (zorder/hybrid/partial/pca1d/kdtree/pq/spectral/birch)
#   3. SIFT mid-sel 보강 측정
#   4. /tmp/final_chain_done.flag 생성
#
# 주의: gmm/hdbscan/sobol/sparse_rp (4종 — run_*.py 미존재) 는 본 chain 미포함.
#        DEEP s=0.05 numpy 는 prerequisite 검증 필요 (별도 wrapper).

set -uo pipefail  # -e 제거 — 일부 method 실패해도 다음 method 진행

CACHE=/mnt/hdd0/home/capstone2026/cache
RQ3=$CACHE/rq3
LOG=$CACHE/final_chain.log
LOGS=$RQ3/logs

POST_FLAG=/tmp/post_8m_done.flag
FINAL_FLAG=/tmp/final_chain_done.flag

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

mkdir -p "$LOGS"

echo "[$(KST)] final_chain.sh START — waiting for $POST_FLAG"

# === 1. post_8m_done.flag 대기 ===
while [ ! -f "$POST_FLAG" ]; do
    sleep 60
done
echo "[$(KST)] $POST_FLAG detected — proceed to 1M extra methods"

cd "$RQ3"

# === 2. 1M extra 8 method 순차 측정 ===
METHODS=(zorder hybrid minibatch_partial pca1d kdtree pq spectral birch)
for m in "${METHODS[@]}"; do
    echo ""
    echo "[$(KST)] === 1M extra: run_${m}.py START ==="
    if python3 "run_${m}.py" 2>&1 | tee "$LOGS/rq3_${m}_1m.log" | tail -3; then
        echo "[$(KST)] run_${m}.py DONE"
    else
        echo "[$(KST)] run_${m}.py FAILED — continuing"
    fi
done

# === 3. SIFT mid-sel 보강 측정 ===
echo ""
echo "[$(KST)] === SIFT mid-sel boost START ==="
cd "$CACHE"
if python3 sift_mid_sel_measurement.py 2>&1 | tee "$LOGS/sift_mid_sel.log" | tail -5; then
    echo "[$(KST)] sift_mid_sel DONE"
else
    echo "[$(KST)] sift_mid_sel FAILED"
fi

# === 4. final flag ===
echo ""
echo "[$(KST)] final_chain.sh END" > "$FINAL_FLAG"
echo "[$(KST)] $FINAL_FLAG generated. 산출 회수 가능."
echo ""
echo "산출 location:"
echo "  /mnt/hdd0/home/capstone2026/cache/rq1/rq3_*.parquet (1M extra 8 method)"
echo "  /mnt/hdd0/home/capstone2026/cache/rq1/sift_mid_sel*.{parquet,json}"
echo ""
echo "회수 명령 (로컬):"
echo "  scp 'capstone:$CACHE/rq1/rq3_zorder*.parquet' experiments/results/rq3_agnostic/"
echo "  scp 'capstone:$CACHE/rq1/rq3_hybrid*.parquet' experiments/results/rq3_agnostic/"
echo "  ... etc"
