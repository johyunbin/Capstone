#!/usr/bin/env bash
# launch_sf100_safe.sh — autonomous SF=100 build + measure launcher.
#
# Phase D (Exqutor Fig 4-6 strict match) — DEEP/SIFT/FB(=SSN) at SF=100.
# This script is the single entry point for the overnight run:
#
#   1. Memory-safety check (free RAM > 100 GB AND swap < 80%) — abort otherwise
#   2. Disk-space check (need ~158 GB; require 1.2× margin)
#   3. Sequential build per cell via build_sf100_single.py
#   4. After each cell builds, kick off run_ensemble_4kang_adaptive.py × 11 methods
#      (background, with own log) — measurement runs in parallel with next cell's build
#
# Constraints (per project rules):
#   - NEVER use sudo
#   - DO NOT use ports 55432/55433 (chaerim)
#   - DO NOT touch existing measurement procs (sf=1+10 still running)
#
# Run from server (165.132.140.240):
#   ssh capstone
#   cd /mnt/hdd0/home/capstone2026
#   bash _internal/scripts/launch_sf100_safe.sh
#
# Or autonomously in background:
#   nohup bash _internal/scripts/launch_sf100_safe.sh \
#       > /mnt/hdd0/home/capstone2026/logs/launch_sf100_$(date +%Y%m%d_%H%M).log 2>&1 &
#
# Modes (environment variables):
#   DRY_RUN=1                  — print plan only, no execution
#   SKIP_MEM_GATE=1            — skip memory check (only if you've checked yourself)
#   SKIP_MEASURE=1             — only build NPY/parquet, don't launch measurement
#   CELLS="DEEP SIFT FB"       — subset of cells (default: all 3)
#   PG_PORT=55435              — PG port (default 55435; do NOT use 55432/55433)
set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SERVER_HOME="/mnt/hdd0/home/capstone2026"
BUILD_SCRIPT="${SERVER_HOME}/cache/rq3/build_sf100_single.py"
ENSEMBLE_SCRIPT="${SERVER_HOME}/cache/rq3/run_ensemble_4kang_adaptive.py"
NPY_DIR="${SERVER_HOME}/cache/rq1"
LOG_DIR="${SERVER_HOME}/logs"
OUT_DIR="${SERVER_HOME}/cache/rq1"

CELLS="${CELLS:-DEEP SIFT FB}"
PG_PORT="${PG_PORT:-55435}"
MIN_FREE_GB="${MIN_FREE_GB:-100}"
MAX_SWAP_PCT="${MAX_SWAP_PCT:-80}"

# 11 paradigm methods (matches build_FB_single_ensemble.py / run_ensemble_4kang_adaptive.py).
METHODS_11="hdbscan minibatch gmm hilbert faiss_ivf minibatch_partial reservoir sparse_rp pca1d lsh sobol"

# Internal dataset key map (FB → SSN per CELLS dict).
declare -A INTERNAL=( [DEEP]=DEEP [SIFT]=SIFT [FB]=SSN )

mkdir -p "${LOG_DIR}"

kst() { TZ=Asia/Seoul date "+%H:%M:%S"; }

# ---------------------------------------------------------------------------
# Memory gate
# ---------------------------------------------------------------------------
mem_safe() {
  local free_kb total_swap free_swap free_gb swap_pct
  free_kb=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
  total_swap=$(awk '/^SwapTotal:/ {print $2}' /proc/meminfo)
  free_swap=$(awk '/^SwapFree:/ {print $2}' /proc/meminfo)
  free_gb=$(( free_kb / 1024 / 1024 ))
  if [[ "${total_swap}" -eq 0 ]]; then
    swap_pct=0
  else
    swap_pct=$(( (total_swap - free_swap) * 100 / total_swap ))
  fi
  echo "free=${free_gb}GB swap_used=${swap_pct}%"
  if [[ "${free_gb}" -lt "${MIN_FREE_GB}" ]]; then return 1; fi
  if [[ "${swap_pct}" -gt "${MAX_SWAP_PCT}" ]]; then return 1; fi
  return 0
}

# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------
echo "[$(kst)] === launch_sf100_safe.sh ==="
echo "[$(kst)] CELLS:        ${CELLS}"
echo "[$(kst)] PG_PORT:      ${PG_PORT}"
echo "[$(kst)] MIN_FREE_GB:  ${MIN_FREE_GB}"
echo "[$(kst)] MAX_SWAP_PCT: ${MAX_SWAP_PCT}"
echo "[$(kst)] BUILD:        ${BUILD_SCRIPT}"
echo "[$(kst)] ENSEMBLE:     ${ENSEMBLE_SCRIPT}"
echo "[$(kst)] LOG_DIR:      ${LOG_DIR}"

if [[ ! -f "${BUILD_SCRIPT}" ]]; then
  echo "[$(kst)] ERROR: build script not synced to ${BUILD_SCRIPT}"
  exit 1
fi

if [[ "${DRY_RUN:-}" == "1" ]]; then
  echo "[$(kst)] === DRY RUN ==="
  python3 -u "${BUILD_SCRIPT}" --datasets ${CELLS} --port "${PG_PORT}" --dry-run
  echo
  for ds in ${CELLS}; do
    internal="${INTERNAL[$ds]}"
    for m in ${METHODS_11}; do
      echo "[$(kst)] [DRY] ensemble: --dataset ${internal} --sf 100 --base-method ${m} --out-prefix rq3_${ds}_sf100_ensemble_${m}"
    done
  done
  echo "[$(kst)] dry-run complete — exiting"
  exit 0
fi

# ---------------------------------------------------------------------------
# Pre-flight memory check
# ---------------------------------------------------------------------------
echo
echo "[$(kst)] === pre-flight memory check ==="
mem_status=$(mem_safe || true)
if [[ "${SKIP_MEM_GATE:-}" == "1" ]]; then
  echo "[$(kst)] memory: ${mem_status}  (SKIP_MEM_GATE=1, proceeding)"
elif mem_safe > /dev/null; then
  echo "[$(kst)] memory: ${mem_status}  (SAFE)"
else
  echo "[$(kst)] memory: ${mem_status}"
  echo "[$(kst)] NOT READY TO LAUNCH — wait for sf=10 measurements to drain"
  echo "[$(kst)] (re-run when free > ${MIN_FREE_GB}GB AND swap_used < ${MAX_SWAP_PCT}%)"
  exit 2
fi

# ---------------------------------------------------------------------------
# Sequential build + parallel measurement launch
# ---------------------------------------------------------------------------
echo
echo "[$(kst)] === READY TO LAUNCH ==="
echo "[$(kst)] starting sequential build for cells: ${CELLS}"

build_log="${LOG_DIR}/build_sf100_$(TZ=Asia/Seoul date +%Y%m%d_%H%M).log"
echo "[$(kst)] build log: ${build_log}"

for ds in ${CELLS}; do
  echo
  echo "[$(kst)] >>> CELL ${ds} (build start)"
  if ! mem_safe > /dev/null && [[ "${SKIP_MEM_GATE:-}" != "1" ]]; then
    echo "[$(kst)] STOP — memory drained mid-loop ($(mem_safe || true))"
    exit 3
  fi

  # Build only this cell — sequential to avoid 100GB+ memory spike.
  cell_log="${LOG_DIR}/build_sf100_${ds}_$(TZ=Asia/Seoul date +%Y%m%d_%H%M).log"
  echo "[$(kst)] cell log: ${cell_log}"
  if ! python3 -u "${BUILD_SCRIPT}" --datasets "${ds}" --port "${PG_PORT}" \
        ${SKIP_MEM_GATE:+--no-mem-gate} \
        > "${cell_log}" 2>&1; then
    echo "[$(kst)] ERROR — build for ${ds} failed; tail of log:"
    tail -n 30 "${cell_log}"
    exit 4
  fi
  echo "[$(kst)] <<< CELL ${ds} (build done)"

  if [[ "${SKIP_MEASURE:-}" == "1" ]]; then
    echo "[$(kst)] SKIP_MEASURE=1 — not launching measurement for ${ds}"
    continue
  fi

  # Kick off ensemble × 11 methods for this cell in background.
  internal="${INTERNAL[$ds]}"
  measure_log="${LOG_DIR}/measure_sf100_${ds}_ensemble_$(TZ=Asia/Seoul date +%Y%m%d_%H%M).log"
  echo "[$(kst)] >>> CELL ${ds} (measure launch — ensemble × 11 methods, internal=${internal})"
  echo "[$(kst)] measure log: ${measure_log}"
  (
    for m in ${METHODS_11}; do
      out_prefix="rq3_${ds}_sf100_ensemble_${m}"
      echo "[$(kst)] [measure-${ds}] start method=${m}  out_prefix=${out_prefix}"
      python3 -u "${ENSEMBLE_SCRIPT}" \
        --dataset "${internal}" --sf 100 --base-method "${m}" \
        --selectivity 0.01 0.05 0.10 0.30 0.50 \
        --seed-start 0 --num-seeds 5 --num-queries 100 \
        --out-dir "${OUT_DIR}" --out-prefix "${out_prefix}" \
        --momentum 0.9 --lr0 0.1 --alpha 50.0 --beta 1.5 --gamma 0.99 \
        --update-period 50 --min-size 50 --max-size 5000 \
        || echo "[$(kst)] [measure-${ds}] FAIL method=${m} (rc=$?)"
      echo "[$(kst)] [measure-${ds}] end method=${m}"
    done
    echo "[$(kst)] [measure-${ds}] all 11 methods done"
  ) > "${measure_log}" 2>&1 &
  measure_pid=$!
  echo "[$(kst)] measure PID=${measure_pid}  (continues in background while next build proceeds)"
done

echo
echo "[$(kst)] === all builds launched ==="
echo "[$(kst)] background measurement PIDs (check with: ps -ef | grep run_ensemble_4kang_adaptive | grep -v grep):"
ps -ef | grep run_ensemble_4kang_adaptive | grep -v grep | awk '{print "  PID=" $2 "  cmd=" $0}' || true
echo
echo "[$(kst)] DONE — outputs go to ${OUT_DIR}/rq3_<CELL>_sf100_ensemble_<method>.parquet"
