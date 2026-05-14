#!/bin/bash
# run_phase_b_phase4.sh — Phase 4 11 method × 9 cells × CaseA/B measurement launcher
#
# 작성: 2026-05-11 KST (Phase 4 별도 세션)
# 대상 server: capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/
# 사전 조건: method_phase4_extra.py + measure_paper_exact.py (PATCH 적용본) scp 완료
#
# Usage:
#   ./run_phase_b_phase4.sh [--cell A1-DEEP] [--mode CaseA] [--method idistance] [--dry-run]
#   ./run_phase_b_phase4.sh --all   # 11 methods × 9 cells × 2 modes (198 cells)
#
# Output:
#   /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/<cell>_<method>_<mode>.json
#   /mnt/hdd0/home/capstone2026/log/phase4_b_<timestamp>.log

set -euo pipefail

# Phase 4 11 method
PHASE4_METHODS=(
    "chao_weighted"      # M1 P3 weight reservoir
    "lpm1_proper"        # M2 P2+P3 spatial pivotal
    "cum_sqrtf"          # M3 P5 optimal univariate strata
    "lavallee_hidiroglou" # M4 P5 take-all + Neyman
    "idistance"          # M5 P2 reference distance
    "zorder_morton"      # M6 P2 SFC anchor
    "skilling_hilbert"   # M7 P2 true high-D Hilbert
    "ica_fastica"        # M8 P4 non-Gaussian
    "kmeans_neyman"      # M9 P1+RQ2
    "rabitq_strat"       # M10 P6 1-bit code
    "idistance_neyman"   # M11 P2+RQ2 synthesis
)

# 9 cells (handoff_main §7.1 Tier 1 99 measurement)
CELLS=(
    "A1-DEEP"      # paper Fig 5/6 DEEP partsupp_deep_100
    "A1-SIFT"      # paper Fig 5/6 SIFT partsupp_sift_100
    "A1-SSN"       # paper Fig 5/6 SimSearchNet++ partsupp_fb_100
    "A2-Fig7"      # paper Fig 7 YFCC tag filter
    "A2-Fig9"      # paper Fig 9 DEEP+WIKI cross-table
    "A4-sel"       # paper Fig 13 selectivity ablation
    "A5-scale-sf1" # paper Fig 14 scalability SF=1
    "A5-scale-sf10" # paper Fig 14 SF=10
    "A5-scale-sf100" # paper Fig 14 SF=100
)

MODES=("CaseA" "CaseB")  # CaseA = method 대체, CaseB = B1 + ensemble
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="/mnt/hdd0/home/capstone2026/log"
LOG_FILE="${LOG_DIR}/phase4_b_${TIMESTAMP}.log"
SCRIPT_DIR="/mnt/hdd0/home/capstone2026/cache/rq3"
N_QUERIES=100
N_TRIALS=10

# Default options
DRY_RUN=false
SELECTED_METHOD=""
SELECTED_CELL=""
SELECTED_MODE=""
RUN_ALL=false

# Argument parsing
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --all) RUN_ALL=true; shift ;;
        --method) SELECTED_METHOD="$2"; shift 2 ;;
        --cell) SELECTED_CELL="$2"; shift 2 ;;
        --mode) SELECTED_MODE="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    LOG_FILE="/dev/null"
else
    mkdir -p "$LOG_DIR"
fi

run_cell() {
    local method="$1"
    local cell="$2"
    local mode="$3"

    local cmd="python3 ${SCRIPT_DIR}/measure_paper_exact.py \
        --rq 3 --phase B \
        --cell ${cell} --mode ${mode} --method ${method} \
        --n-queries ${N_QUERIES} --trials ${N_TRIALS}"

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] $cmd"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] LAUNCH method=${method} cell=${cell} mode=${mode}" \
            | tee -a "$LOG_FILE"
        eval "$cmd" 2>&1 | tee -a "$LOG_FILE"
    fi
}

if [ "$RUN_ALL" = true ]; then
    # All 198 cells
    echo "=== Phase 4 FULL launch: 11 methods × 9 cells × 2 modes = 198 cells ==="
    for method in "${PHASE4_METHODS[@]}"; do
        for cell in "${CELLS[@]}"; do
            for mode in "${MODES[@]}"; do
                run_cell "$method" "$cell" "$mode"
            done
        done
    done
elif [ -n "$SELECTED_METHOD" ] && [ -n "$SELECTED_CELL" ] && [ -n "$SELECTED_MODE" ]; then
    # Single cell
    run_cell "$SELECTED_METHOD" "$SELECTED_CELL" "$SELECTED_MODE"
elif [ -n "$SELECTED_METHOD" ]; then
    # All cells × all modes for one method
    for cell in "${CELLS[@]}"; do
        for mode in "${MODES[@]}"; do
            run_cell "$SELECTED_METHOD" "$cell" "$mode"
        done
    done
else
    cat <<'EOF'
Usage:
  ./run_phase_b_phase4.sh --all                                    # 198 cells (5-7일 sequential)
  ./run_phase_b_phase4.sh --method idistance                       # 18 cells (1 method × 9 × 2)
  ./run_phase_b_phase4.sh --method idistance --cell A1-DEEP --mode CaseA  # 1 cell smoke
  ./run_phase_b_phase4.sh --dry-run --all                          # dry-run preview

Methods (11):
EOF
    for m in "${PHASE4_METHODS[@]}"; do
        echo "  - $m"
    done
    cat <<'EOF'

Cells (9):
EOF
    for c in "${CELLS[@]}"; do
        echo "  - $c"
    done
    cat <<'EOF'

Modes:
  - CaseA: method 가 sampling step 대체
  - CaseB: B1 baseline + method ensemble (paper Fig 6 + augment)

Recommended sequence:
  1. SCP method_phase4_extra.py + measure_paper_exact.py (PATCH 적용본)
  2. ssh capstone "python3 cache/rq3/method_phase4_extra.py"     # smoke test
  3. ./run_phase_b_phase4.sh --method idistance --cell A1-DEEP --mode CaseA  # 1-cell smoke
  4. ./run_phase_b_phase4.sh --method kmeans_neyman                # 1 method full
  5. ./run_phase_b_phase4.sh --all   # tmux 분할 권고
EOF
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] === Phase 4 launch complete ===" | tee -a "$LOG_FILE"
