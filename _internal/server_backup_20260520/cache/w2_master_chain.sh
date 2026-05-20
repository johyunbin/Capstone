#!/bin/bash
# W2 sprint master chain — 5/7 morning
#
# 흐름:
#   1. SIFT-RAND mid-sel 종료 대기 (w2_sift_rand_mid_sel.log 의 'total elapsed' 감지)
#   2. DEEP s=0.05 numpy 재측정 (Phase 6/7 분리)
#   3. compute_stratum_sigma 8M (DEEP 8M sigma 사전 계산)
#   4. RQ2 8M alloc (5 mode: bernoulli/equal/proportional/neyman/anti_neyman)
#   5. KDE-pilot 8M
#   6. Distance-Shell 8M
#   7. Importance Sampling 8M (4 mode)
#   8. /tmp/w2_chain_done.flag 생성

set -uo pipefail

CACHE=/mnt/hdd0/home/capstone2026/cache
LOG=$CACHE/w2_master_chain.log
DONE_FLAG=/tmp/w2_chain_done.flag
SIFT_LOG=$CACHE/w2_sift_rand_mid_sel.log

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

run_step() {
    local name="$1"
    local cmd="$2"
    local out_log="$3"
    echo ""
    echo "[$(KST)] === Step: $name START ==="
    eval "$cmd 2>&1 | tee $out_log | tail -3"
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "[$(KST)] $name DONE"
    else
        echo "[$(KST)] $name FAILED — continuing"
    fi
}

echo "[$(KST)] w2_master_chain START"

# === 1. SIFT-RAND mid-sel 종료 대기 ===
echo "[$(KST)] waiting for SIFT-RAND mid-sel measurement (poll log)..."
while ! grep -q "total elapsed" "$SIFT_LOG" 2>/dev/null; do
    sleep 30
done
echo "[$(KST)] SIFT-RAND done — proceeding to W2 chain"

cd "$CACHE"

# === 2. DEEP s=0.05 numpy ===
run_step "DEEP s=0.05 numpy" \
    "python3 deep_s005_numpy_remeasure.py" \
    "$CACHE/w2_deep_s005_numpy.log"

# === 3. 8M sigma 사전 계산 ===
run_step "compute_stratum_sigma 8M" \
    "python3 compute_stratum_sigma_8m.py" \
    "$CACHE/w2_compute_sigma_8m.log"

# === 4. RQ2 8M alloc (5 mode) ===
run_step "RQ2 8M alloc (Neyman/Anti-Neyman 포함)" \
    "python3 rq2_alloc_python_8m.py" \
    "$CACHE/w2_rq2_8m_alloc.log"

# === 5. KDE-pilot 8M ===
run_step "KDE-pilot 8M" \
    "python3 rq3/run_kde_pilot_8m.py" \
    "$CACHE/w2_kde_8m.log"

# === 6. Distance-Shell 8M ===
run_step "Distance-Shell 8M" \
    "python3 rq3/run_distance_shell_8m.py" \
    "$CACHE/w2_distance_8m.log"

# === 7. IS 8M (4 mode) ===
run_step "Importance Sampling 8M (4 mode)" \
    "python3 rq3/run_importance_sampling_8m.py" \
    "$CACHE/w2_is_8m.log"

# === 8. final flag ===
echo ""
echo "[$(KST)] w2_master_chain END" > "$DONE_FLAG"
echo "[$(KST)] $DONE_FLAG generated. 모든 W2 측정 완료."
