#!/bin/bash
# launch_ensemble_4kang_adaptive.sh
#
# Ensemble (4강 stratification × Adaptive dynamic budget) 측정 launcher.
# 5/8 박세은 팀장 결정 + V5 audit 권장 ⭐⭐⭐.
#
# 측정 격자: 5 cell × 2 SF × 4 base_method = 40 runs.
#   cell ∈ {DEEP, SIFT, SSN, WIKI, YFCC} × SF ∈ {1, 10}
#   base ∈ {hdbscan, minibatch_partial, hilbert, sparse_rp}
#
# 시간 예측 (chain 기반):
#   - DEEP/SIFT SF1 :  ~13~19 min/cell  ×  4 base ≈  ~70 min
#   - DEEP/SIFT SF10:  ~115 min/cell    ×  4 base ≈  ~460 min (~8h, 2 cell)
#   - SSN/WIKI/YFCC SF1: 비슷 ~70~90 min/cell × 4 base
# 동시성: 단일 process 순차 (HDD IO 경합 + 다른 measurement 진행 중 → 안정성)
# Multi 11-method + Multi SF1 + YFCC K-sweep 진행 중이므로 sequential 유지.
#
# 산출:
#   /mnt/hdd0/home/capstone2026/cache/rq1/rq3_<DS>_sf<sf>_ensemble_<base>.parquet
#   /mnt/hdd0/home/capstone2026/logs/ensemble_<DS>_sf<sf>_<base>_<DATE>.log
#
# 사용 (서버 165.132.140.240, capstone2026 계정):
#   nohup bash launch_ensemble_4kang_adaptive.sh \
#       > /mnt/hdd0/home/capstone2026/logs/ensemble_launcher_20260508.log 2>&1 &
#
# 검증:
#   ls /mnt/hdd0/home/capstone2026/cache/rq1/rq3_*_ensemble_*.parquet
#   tail -50 /mnt/hdd0/home/capstone2026/logs/ensemble_*_20260508.log
#   cat /tmp/ensemble_4kang_adaptive_done.flag

set -uo pipefail

# === 환경 ===
SERVER_HOME=/mnt/hdd0/home/capstone2026
RQ3_CODE=$SERVER_HOME/cache/rq3
LOG_DIR=$SERVER_HOME/logs
OUT_DIR=$SERVER_HOME/cache/rq1

mkdir -p "$LOG_DIR" "$OUT_DIR"

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

DATE_TAG=$(TZ='Asia/Seoul' date '+%Y%m%d')

echo "[$(KST)] launch_ensemble_4kang_adaptive.sh START"
echo "[$(KST)] code dir = $RQ3_CODE"
echo "[$(KST)] log dir  = $LOG_DIR"
echo "[$(KST)] out dir  = $OUT_DIR"

OVERALL_RC=0
N_RUN=0
N_OK=0
N_FAIL=0

# 측정 격자: cell 5 × SF 2 × base 4 = 40
DATASETS=(DEEP SIFT SSN WIKI YFCC)
SFS=(1 10)
BASES=(hdbscan minibatch_partial hilbert sparse_rp)

for ds in "${DATASETS[@]}"; do
    for sf in "${SFS[@]}"; do
        for base in "${BASES[@]}"; do
            N_RUN=$((N_RUN + 1))
            LOG=$LOG_DIR/ensemble_${ds}_sf${sf}_${base}_${DATE_TAG}.log
            echo ""
            echo "[$(KST)] [$N_RUN/40] $ds-SF$sf × $base START → $LOG"
            python3 -u "$RQ3_CODE/run_ensemble_4kang_adaptive.py" \
                --dataset "$ds" --sf "$sf" \
                --base-method "$base" \
                --selectivity 0.01 0.05 0.10 0.30 0.50 \
                --seed-start 0 --num-seeds 5 \
                --num-queries 100 \
                --out-dir "$OUT_DIR" \
                > "$LOG" 2>&1
            RC=$?
            if [ $RC -eq 0 ]; then
                N_OK=$((N_OK + 1))
                echo "[$(KST)] [$N_RUN/40] $ds-SF$sf × $base END ✓ (exit=0)"
            else
                N_FAIL=$((N_FAIL + 1))
                OVERALL_RC=$RC
                echo "[$(KST)] [$N_RUN/40] $ds-SF$sf × $base END ✗ (exit=$RC, log=$LOG)"
            fi
        done
    done
done

echo ""
echo "[$(KST)] === 산출 확인 ==="
ls -la "$OUT_DIR"/rq3_*_ensemble_*.parquet 2>&1 | tail -50 || echo "(parquet 없음)"

echo ""
echo "[$(KST)] launch_ensemble_4kang_adaptive.sh END (OK=$N_OK / FAIL=$N_FAIL / total=$N_RUN)"

DONE_FLAG=/tmp/ensemble_4kang_adaptive_done.flag
{
    echo "[$(KST)] ensemble 4강 × Adaptive launcher 종료"
    echo "OK=$N_OK / FAIL=$N_FAIL / total=$N_RUN, overall_exit=$OVERALL_RC"
    echo "out_dir=$OUT_DIR"
    echo "datasets=${DATASETS[*]} sfs=${SFS[*]} bases=${BASES[*]}"
} > "$DONE_FLAG"
echo "[$(KST)] $DONE_FLAG generated."
