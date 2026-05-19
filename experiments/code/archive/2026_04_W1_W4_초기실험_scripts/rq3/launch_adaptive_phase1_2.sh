#!/bin/bash
# launch_adaptive_phase1_2.sh
#
# Exqutor Adaptive Sampling 5h overnight launch (5/8 22:00 ~ 5/9 03:00).
# 5/8 회의 결정 ⭐⭐⭐ — 본 연구 4강 vs Adaptive paired Δ% 의 핵심 measurement.
#
# 패턴: chain_unified.py 와 동일한 cell-per-process loop.
#   run_adaptive_sampling.py 는 이제 single (--dataset, --sf) 만 받음.
#   multi-cell 처리는 본 launcher 가 for loop 으로 처리.
#
# Phase 1 (~3h, 22:00 ~ 01:00): SF1 5 cell 순차 — DEEP / SIFT / SSN / WIKI / YFCC.
#   HDD 단일 IO 경합 회피 위해 단일 process 순차. cell 당 ~13~19 min × 5 = ~75 min,
#   buffer 포함 ~3h.
#
# Phase 2 (~2h, 01:00 ~ 03:00): SF10 cell 2개 (DEEP-SF10 + SIFT-SF10) 동시 병렬.
#   서버 W1 sprint 검증된 동시성 한계 = 2 cell. cell 당 ~115 min, 2 cell 병렬
#   wall-clock ~115 min ≈ 2h.
#
# Phase 3 (deferred, 5/9 daytime): SSN / WIKI / YFCC SF10 3 cell — 자문 회신 대기 중
#   background 로 launch (현재 주석 처리).
#
# 산출:
#   /mnt/hdd0/home/capstone2026/cache/rq1/rq3_<DATASET>_sf<sf>_adaptive.parquet
#   /mnt/hdd0/home/capstone2026/logs/adaptive_phase{1,2}_<DATASET>_sf<sf>_<DATE>.log
#
# 사용 (서버 165.132.140.240, capstone2026 계정):
#   nohup bash launch_adaptive_phase1_2.sh \
#       > /mnt/hdd0/home/capstone2026/logs/adaptive_launcher_20260508.log 2>&1 &
#
# 검증 (자고 일어나서):
#   ls /mnt/hdd0/home/capstone2026/cache/rq1/rq3_*_adaptive.parquet
#   tail -50 /mnt/hdd0/home/capstone2026/logs/adaptive_phase2_DEEP_sf10_*.log
#   cat /tmp/adaptive_phase1_2_done.flag

set -uo pipefail   # set -e 는 wait 의 non-zero 에 즉시 abort → 부분 산출 보존 위해 제거

# === 환경 ===
SERVER_HOME=/mnt/hdd0/home/capstone2026
RQ3_CODE=$SERVER_HOME/cache/rq3
LOG_DIR=$SERVER_HOME/logs
OUT_DIR=$SERVER_HOME/cache/rq1   # 기존 4강 measurement 와 동일 경로

mkdir -p "$LOG_DIR" "$OUT_DIR"

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

DATE_TAG=$(TZ='Asia/Seoul' date '+%Y%m%d')

echo "[$(KST)] launch_adaptive_phase1_2.sh START"
echo "[$(KST)] code dir = $RQ3_CODE"
echo "[$(KST)] log dir  = $LOG_DIR"
echo "[$(KST)] out dir  = $OUT_DIR"

# === Phase 1 (~3h): SF1 5 cell 순차 ===
echo ""
echo "[$(KST)] === Phase 1 START (SF1 5 cell sequential) ==="

PHASE1_DATASETS=(DEEP SIFT SSN WIKI YFCC)
PHASE1_RC=0

for ds in "${PHASE1_DATASETS[@]}"; do
    LOG=$LOG_DIR/adaptive_phase1_${ds}_sf1_${DATE_TAG}.log
    echo "[$(KST)] Phase 1 — $ds-SF1 START → $LOG"
    python3 -u "$RQ3_CODE/run_adaptive_sampling.py" \
        --dataset "$ds" --sf 1 \
        --selectivity 0.01 0.05 0.10 0.30 0.50 \
        --seed-start 0 --num-seeds 5 \
        --num-queries 100 \
        --out-dir "$OUT_DIR" \
        > "$LOG" 2>&1
    RC=$?
    echo "[$(KST)] Phase 1 — $ds-SF1 END (exit_code=$RC)"
    if [ $RC -ne 0 ]; then
        PHASE1_RC=$RC
        echo "[$(KST)] WARNING: $ds-SF1 non-zero exit — 부분 산출 보존 후 다음 cell 진행"
    fi
done

echo "[$(KST)] === Phase 1 END (overall_exit_code=$PHASE1_RC) ==="

# === Phase 2 (~2h): SF10 DEEP + SIFT 동시 병렬 (2 cell) ===
echo ""
echo "[$(KST)] === Phase 2 START (SF10 DEEP + SIFT parallel) ==="

PHASE2_DEEP_LOG=$LOG_DIR/adaptive_phase2_DEEP_sf10_${DATE_TAG}.log
PHASE2_SIFT_LOG=$LOG_DIR/adaptive_phase2_SIFT_sf10_${DATE_TAG}.log

python3 -u "$RQ3_CODE/run_adaptive_sampling.py" \
    --dataset DEEP --sf 10 \
    --selectivity 0.01 0.05 0.10 0.30 0.50 \
    --seed-start 0 --num-seeds 5 \
    --num-queries 100 \
    --out-dir "$OUT_DIR" \
    > "$PHASE2_DEEP_LOG" 2>&1 &
DEEP_PID=$!
echo "[$(KST)] Phase 2 DEEP-SF10 launched (PID=$DEEP_PID, log=$PHASE2_DEEP_LOG)"

# stagger 30s — 두 process 의 PG fetch 동시 시작 회피 (vector::real[] cast 안정성)
sleep 30

python3 -u "$RQ3_CODE/run_adaptive_sampling.py" \
    --dataset SIFT --sf 10 \
    --selectivity 0.01 0.05 0.10 0.30 0.50 \
    --seed-start 0 --num-seeds 5 \
    --num-queries 100 \
    --out-dir "$OUT_DIR" \
    > "$PHASE2_SIFT_LOG" 2>&1 &
SIFT_PID=$!
echo "[$(KST)] Phase 2 SIFT-SF10 launched (PID=$SIFT_PID, +30s stagger)"

wait $DEEP_PID
DEEP_RC=$?
echo "[$(KST)] Phase 2 DEEP-SF10 END (exit_code=$DEEP_RC)"

wait $SIFT_PID
SIFT_RC=$?
echo "[$(KST)] Phase 2 SIFT-SF10 END (exit_code=$SIFT_RC)"

# === Phase 3 (deferred to 5/9 daytime) ===
# 자문 회신 대기 중 background 로 launch. 본 script 에서는 주석 처리.
# 활성화 시 아래 block uncomment.
#
# echo ""
# echo "[$(KST)] === Phase 3 START (SF10 SSN+WIKI+YFCC, deferred 가능) ==="
# PHASE3_RC=0
# for ds in SSN WIKI YFCC; do
#     LOG=$LOG_DIR/adaptive_phase3_${ds}_sf10_${DATE_TAG}.log
#     echo "[$(KST)] Phase 3 — $ds-SF10 START → $LOG"
#     python3 -u "$RQ3_CODE/run_adaptive_sampling.py" \
#         --dataset "$ds" --sf 10 \
#         --selectivity 0.01 0.05 0.10 0.30 0.50 \
#         --seed-start 0 --num-seeds 5 \
#         --num-queries 100 \
#         --out-dir "$OUT_DIR" \
#         > "$LOG" 2>&1
#     RC=$?
#     echo "[$(KST)] Phase 3 — $ds-SF10 END (exit_code=$RC)"
#     [ $RC -ne 0 ] && PHASE3_RC=$RC
# done

# === 산출 확인 + done flag ===
echo ""
echo "[$(KST)] === 산출 확인 ==="
ls -la "$OUT_DIR"/rq3_*_adaptive*.parquet 2>&1 || echo "(parquet 없음)"

echo "[$(KST)] launch_adaptive_phase1_2.sh END"

# done flag — 다음 session 회수 trigger
DONE_FLAG=/tmp/adaptive_phase1_2_done.flag
{
    echo "[$(KST)] adaptive Phase 1+2 종료"
    echo "Phase 1 overall_exit=$PHASE1_RC, Phase 2 DEEP exit=$DEEP_RC, Phase 2 SIFT exit=$SIFT_RC"
    echo "out_dir=$OUT_DIR"
    echo "Phase 1 cells: ${PHASE1_DATASETS[*]} (SF1)"
    echo "Phase 2 cells: DEEP, SIFT (SF10)"
    echo "Phase 3 cells: SSN, WIKI, YFCC (SF10) — deferred (commented out)"
} > "$DONE_FLAG"
echo "[$(KST)] $DONE_FLAG generated. 사용자 회수 가능."
