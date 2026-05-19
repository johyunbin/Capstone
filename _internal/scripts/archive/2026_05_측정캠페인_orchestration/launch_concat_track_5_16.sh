#!/bin/bash
# multi-vector concat 측정 트랙 + sel sweep — 7 concat cell x 3 sel x (B1 1 + CaseB 16).
# 5/16 작성 — launch_concat_track.sh 의 sel sweep 확장판 (기존 script 보존).
#
# --- launch_concat_track.sh 대비 변경점 ------------------------------------
#   1. sel 루프 추가: for SEL in 0.001 0.01 0.10 — paper §V-B 3 sel 전부 측정.
#      measure 명령에 --sel $SEL 전달 (measure_paper_exact.py L1477 CLI 인자).
#   2. OUT 디렉토리를 sel 별로 분리: {CELL}_sel{SEL}/
#      → measure_paper_exact.py 의 결과 JSON 파일명은 {cell.sub}_B1.json 으로
#        고정 (sel 미포함). 같은 디렉토리에 sel 3개를 쓰면 덮어쓰기 되므로
#        sel 별 하위 디렉토리로 분리해야 한다.
#   3. CELLS_* 배열의 sub 이름 정정 — DEEP+SIFT=A9 / DEEP+WIKI=A10 /
#      DEEP+YFCC=A11. (기존 script 는 7 cell 전부 A9 로 박아 둬서 WIKI/YFCC
#      cell 이 측정 불능이었음 — measure_paper_exact.py --dry-run 으로 대조 후 정정.)
#
# --- 측정 대상 -------------------------------------------------------------
# 7 concat cell (build_concat_cells.py 가 NPY/strata/query artifact 빌드):
#   DEEP+SIFT concat : sf1 / sf10 / sf100   -> 224d   (A9)
#   DEEP+WIKI concat : sf1 / sf10           -> 864d   (A10)
#   DEEP+YFCC concat : sf1 / sf10           -> 288d   (A11)
#
# cell 1개 = sel 3개 x (B1 1 + CaseB 16 method) = 51 file.
# 전체 = 7 cell x 3 sel x 17 = 357 file.
#
# --- 선행 조건 (이 script 실행 전 반드시) ----------------------------------
#   1. build_concat_cells.py --all  완료 (7 cell NPY/parquet 빌드)
#   2. verify_concat_npy.py  ->  ALL PASS (산출물 sanity 게이트)
#   3. measure_paper_exact.py 에 concat CellSpec 7개(A9/A10/A11) + --sel CLI 인자
#      추가 완료 — --dry-run 으로 sub 이름 대조
#
# --- 사용법 ----------------------------------------------------------------
#   tmux new -d -s concat_track \
#     'bash /mnt/hdd0/home/capstone2026/_internal/scripts/launch_concat_track_5_16.sh'
#   tmux attach -t concat_track            # 진행 확인
#   tail -f $OUT_BASE/logs/_main.log       # 로그 추적
#
# --- 출력 ------------------------------------------------------------------
#   /mnt/hdd0/home/capstone2026/results_concat_track_{TS}/
#     {CELL_SUB}_sel{SEL}/{CELL_SUB}_B1.json
#     {CELL_SUB}_sel{SEL}/{CELL_SUB}_CaseB_{method}.json
#     logs/_main.log + logs/{CELL_SUB}_sel{SEL}_*.log
#     COMPLETE.flag        <- 전부 끝나면 touch
#
# 결과 JSON 이 이미 있으면 해당 측정은 skip — 중단 후 재실행 안전 (idempotent).
#
# --- 추정 소요 -------------------------------------------------------------
#   cell 1개 측정 = sel 3개 x 17 = 51 file.
#   sf1   cell  (800K rows)  : ~1.5-2.5h  (sel 3개 x 17, NPY warm)
#   sf10  cell  (8M rows)    : ~3-6h
#   sf100 cell  (80M, 224d)  : ~9-15h  <- DEEP+SIFT sf100 만, 그래서 맨 마지막
#   전체 7 cell : 대략 36-54h. 가벼운 cell(sf1) 먼저 -> 무거운 sf100 마지막.

set -u   # set -e 는 쓰지 않음 — 1 측정 실패가 전체를 죽이면 안 됨
         # (각 측정은 || 로 개별 처리, fail 은 _main.log 에 [WARN] 기록)

SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_concat_track_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p "$LOG_DIR"

echo "[$(date)] === concat 측정 트랙 + sel sweep launch START ===" | tee "$LOG_DIR/_main.log"
echo "OUT_BASE=$OUT_BASE" | tee -a "$LOG_DIR/_main.log"

# --- sel sweep (paper §V-B 3 sel) ------------------------------------------
SELS=(0.001 0.01 0.10)

# --- 사용 16 method (handoff v31 §3) ---------------------------------------
# Pareto Top 5 + paradigm rep 11 = 16. CaseB 모드로 측정.
M16=(minibatch_partial gmm faiss_ivf hilbert_real zorder_morton skilling_hilbert \
     chao_weighted sparse_rp pca1d rsvd ica_fastica cum_sqrtf lavallee_hidiroglou \
     rabitq_strat mhist2 hyperloglog)

# --- concat cell 의 CellSpec.sub 이름 (measure_paper_exact.py --dry-run 대조) ---
# 가벼운 순서로 나열 — sf1 먼저, sf10 다음, sf100(DEEP+SIFT) 맨 마지막.
# ★ DEEP+SIFT=A9 / DEEP+WIKI=A10 / DEEP+YFCC=A11 (combo 별 prefix 다름).
CELLS_SF1=("A9-DEEP+SIFT-concat-sf1" "A10-DEEP+WIKI-concat-sf1" "A11-DEEP+YFCC-concat-sf1")
CELLS_SF10=("A9-DEEP+SIFT-concat-sf10" "A10-DEEP+WIKI-concat-sf10" "A11-DEEP+YFCC-concat-sf10")
CELLS_SF100=("A9-DEEP+SIFT-concat-sf100")

# --- cell+sel 1조합 측정: B1 1개 + CaseB 16 method --------------------------
# 결과 JSON 이 이미 있으면 skip (idempotent — 중단 후 재실행 안전).
run_concat_cell_sel() {
  local CELL=$1
  local SEL=$2
  local OUT=$OUT_BASE/${CELL}_sel${SEL}
  mkdir -p "$OUT"

  # --- B1 (대조군, paper §V-B Bernoulli) ---
  local b1_json="$OUT/${CELL}_B1.json"
  if [ -f "$b1_json" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $CELL sel$SEL B1 (결과 JSON 존재)" | tee -a "$LOG_DIR/_main.log"
  else
    echo "[$(date +%H:%M:%S)] === $CELL sel$SEL B1 (대조군) ===" | tee -a "$LOG_DIR/_main.log"
    python3 "$SCRIPT" --rq 3 --phase A --cell "$CELL" --mode B1 --sel "$SEL" --output "$OUT" \
      2>&1 | tee "$LOG_DIR/${CELL}_sel${SEL}_B1.log" \
      || echo "[WARN] $CELL sel$SEL B1 failed" | tee -a "$LOG_DIR/_main.log"
  fi

  # --- CaseB 16 method (실험군, B1+method ensemble) ---
  local m
  for m in "${M16[@]}"; do
    local m_json="$OUT/${CELL}_CaseB_${m}.json"
    if [ -f "$m_json" ]; then
      echo "[$(date +%H:%M:%S)] SKIP $CELL sel$SEL CaseB $m (결과 JSON 존재)" \
        | tee -a "$LOG_DIR/_main.log"
      continue
    fi
    echo "[$(date +%H:%M:%S)] === $CELL sel$SEL CaseB $m (실험군) ===" \
      | tee -a "$LOG_DIR/_main.log"
    python3 "$SCRIPT" --rq 3 --phase B --cell "$CELL" --mode CaseB --method "$m" \
      --sel "$SEL" --output "$OUT" \
      2>&1 | tee "$LOG_DIR/${CELL}_sel${SEL}_CaseB_${m}.log" \
      || echo "[WARN] $CELL sel$SEL CaseB $m failed" | tee -a "$LOG_DIR/_main.log"
  done
}

# --- cell 1개를 sel 3개 전부 측정 ------------------------------------------
run_concat_cell() {
  local CELL=$1
  local SEL
  for SEL in "${SELS[@]}"; do
    run_concat_cell_sel "$CELL" "$SEL"
  done
}

# --- 측정 순서: 가벼운 cell 먼저, sf100(DEEP+SIFT) 마지막 -------------------

echo "[$(date)] === [1/3] sf1 concat cell (3 cell x 3 sel x 17 = 153 file) ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in "${CELLS_SF1[@]}"; do
  run_concat_cell "$CELL"
done

echo "[$(date)] === [2/3] sf10 concat cell (3 cell x 3 sel x 17 = 153 file) ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in "${CELLS_SF10[@]}"; do
  run_concat_cell "$CELL"
done

echo "[$(date)] === [3/3] sf100 concat cell (1 cell x 3 sel x 17 = 51 file, 가장 무거움) ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in "${CELLS_SF100[@]}"; do
  run_concat_cell "$CELL"
done

# --- 마무리 ----------------------------------------------------------------
N_JSON=$(find "$OUT_BASE" -name '*.json' -type f 2>/dev/null | wc -l)
N_WARN=$(grep -c '\[WARN\]' "$LOG_DIR/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] === concat 측정 트랙 + sel sweep DONE — JSON $N_JSON / 357, WARN $N_WARN ===" \
  | tee -a "$LOG_DIR/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
