#!/bin/bash
# multi-vector concat 측정 트랙 — 7 concat cell x (B1 1 + CaseB 16) launch.
# 5/16 작성 — handoff v31 사용 16 method 영역 framing 일치.
#
# --- 측정 대상 -------------------------------------------------------------
# 7 concat cell (build_concat_cells.py 가 NPY/strata/query artifact 빌드):
#   DEEP+SIFT concat : sf1 / sf10 / sf100   -> 224d
#   DEEP+WIKI concat : sf1 / sf10           -> 864d
#   DEEP+YFCC concat : sf1 / sf10           -> 288d
#
# cell 당 측정 = B1 1 (대조군) + CaseB 16 method (실험군) = 17 file.
# 전체 = 7 cell x 17 = 119 file.
#
# --- CellSpec sub 이름 -----------------------------------------------------
# measure_paper_exact.py --cell 인자는 CellSpec.sub 와 일치해야 한다.
# concat CellSpec 은 별도 agent 가 measure_paper_exact.py 에 추가 중 —
# build_concat_cells.py docstring 예시("A9-DEEP+SIFT-concat-sf1")와 기존 v7
# multi cell 명명("A8-DEEP+SIFT-sf10")을 따라 아래 CELLS_* 배열에 sub 이름을
# 박아 두었다. CellSpec 추가가 끝나면:
#     python3 measure_paper_exact.py --rq 3 --phase A --cell all --dry-run
# 로 실제 sub 목록을 출력해서 아래 CELLS_* 와 1자도 안 틀리는지 대조할 것.
# (sub 명명 규칙이 다르면 CELLS_* 3줄만 고치면 됨 — 그 외 로직은 불변)
#
# --- 선행 조건 (이 script 실행 전 반드시) ----------------------------------
#   1. build_concat_cells.py --all  완료 (7 cell NPY/parquet 빌드)
#   2. verify_concat_npy.py  ->  ALL PASS (산출물 sanity 게이트)
#   3. measure_paper_exact.py 에 concat CellSpec 7개 + DATASET_ALIAS 매핑 추가
#      (별도 agent 작업) — --dry-run 으로 sub 이름 대조
# 위 3개가 다 끝난 뒤 사용자가 실행 여부를 결정한다. 이 script 는 작성만 —
# 자동 실행하지 않는다.
#
# --- 사용법 ----------------------------------------------------------------
#   # 선행 게이트 통과 후:
#   tmux new -d -s concat_track \
#     'bash /mnt/hdd0/home/capstone2026/_internal/scripts/launch_concat_track.sh'
#   tmux attach -t concat_track            # 진행 확인
#   tail -f $OUT_BASE/logs/_main.log       # 로그 추적
#
# --- 출력 ------------------------------------------------------------------
#   /mnt/hdd0/home/capstone2026/results_concat_track_{TS}/
#     {CELL_SUB}/{CELL_SUB}_B1.json
#     {CELL_SUB}/{CELL_SUB}_CaseB_{method}.json
#     logs/_main.log + logs/{CELL_SUB}_*.log
#     COMPLETE.flag        <- 전부 끝나면 touch
#
# 결과 JSON 이 이미 있으면 해당 측정은 skip — 중단 후 재실행 안전 (idempotent).
#
# --- 추정 소요 -------------------------------------------------------------
#   sf1   cell  (800K rows)  : ~30-50 min  (NPY warm)
#   sf10  cell  (8M rows)    : ~60-120 min
#   sf100 cell  (80M, 224d)  : ~3-5h  <- DEEP+SIFT sf100 만, 그래서 맨 마지막
#   전체 7 cell : 대략 12-18h. 가벼운 cell(sf1) 먼저 -> 무거운 sf100 마지막.

set -u   # set -e 는 쓰지 않음 — 1 cell 측정 실패가 전체를 죽이면 안 됨
         # (각 측정은 || 로 개별 처리, fail 은 _main.log 에 [WARN] 기록)

SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_concat_track_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p "$LOG_DIR"

echo "[$(date)] === concat 측정 트랙 launch START ===" | tee "$LOG_DIR/_main.log"
echo "OUT_BASE=$OUT_BASE" | tee -a "$LOG_DIR/_main.log"

# --- 사용 16 method (handoff v31 §3) ---------------------------------------
# Pareto Top 5 + paradigm rep 11 = 16. CaseB 모드로 측정.
#   PARETO5 : sparse_rp chao_weighted hilbert_real hyperloglog pca1d
#   + rep 11: minibatch_partial gmm faiss_ivf (P1)
#             zorder_morton skilling_hilbert (P2)
#             rsvd ica_fastica (P4)
#             cum_sqrtf lavallee_hidiroglou (P5)
#             rabitq_strat mhist2 (P6)
M16=(minibatch_partial gmm faiss_ivf hilbert_real zorder_morton skilling_hilbert \
     chao_weighted sparse_rp pca1d rsvd ica_fastica cum_sqrtf lavallee_hidiroglou \
     rabitq_strat mhist2 hyperloglog)

# --- concat cell 의 CellSpec.sub 이름 --------------------------------------
# 가벼운 순서로 나열 — sf1 먼저, sf10 다음, sf100(DEEP+SIFT) 맨 마지막.
CELLS_SF1=("A9-DEEP+SIFT-concat-sf1" "A9-DEEP+WIKI-concat-sf1" "A9-DEEP+YFCC-concat-sf1")
CELLS_SF10=("A9-DEEP+SIFT-concat-sf10" "A9-DEEP+WIKI-concat-sf10" "A9-DEEP+YFCC-concat-sf10")
CELLS_SF100=("A9-DEEP+SIFT-concat-sf100")

# --- cell 1개 측정: B1 1개 + CaseB 16 method --------------------------------
# 결과 JSON 이 이미 있으면 skip (idempotent — 중단 후 재실행 안전).
run_concat_cell() {
  local CELL=$1
  local OUT=$OUT_BASE/$CELL
  mkdir -p "$OUT"

  # --- B1 (대조군, paper §V-B Bernoulli) ---
  local b1_json="$OUT/${CELL}_B1.json"
  if [ -f "$b1_json" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $CELL B1 (결과 JSON 존재)" | tee -a "$LOG_DIR/_main.log"
  else
    echo "[$(date +%H:%M:%S)] === $CELL B1 (대조군) ===" | tee -a "$LOG_DIR/_main.log"
    python3 "$SCRIPT" --rq 3 --phase A --cell "$CELL" --mode B1 --output "$OUT" \
      2>&1 | tee "$LOG_DIR/${CELL}_B1.log" \
      || echo "[WARN] $CELL B1 failed" | tee -a "$LOG_DIR/_main.log"
  fi

  # --- CaseB 16 method (실험군, B1+method ensemble) ---
  for m in "${M16[@]}"; do
    local m_json="$OUT/${CELL}_CaseB_${m}.json"
    if [ -f "$m_json" ]; then
      echo "[$(date +%H:%M:%S)] SKIP $CELL CaseB $m (결과 JSON 존재)" \
        | tee -a "$LOG_DIR/_main.log"
      continue
    fi
    echo "[$(date +%H:%M:%S)] === $CELL CaseB $m (실험군) ===" \
      | tee -a "$LOG_DIR/_main.log"
    python3 "$SCRIPT" --rq 3 --phase B --cell "$CELL" --mode CaseB --method "$m" \
      --output "$OUT" \
      2>&1 | tee "$LOG_DIR/${CELL}_CaseB_${m}.log" \
      || echo "[WARN] $CELL CaseB $m failed" | tee -a "$LOG_DIR/_main.log"
  done
}

# --- 측정 순서: 가벼운 cell 먼저, sf100(DEEP+SIFT) 마지막 -------------------

echo "[$(date)] === [1/3] sf1 concat cell (3 cell x 17 = 51 file) ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in "${CELLS_SF1[@]}"; do
  run_concat_cell "$CELL"
done

echo "[$(date)] === [2/3] sf10 concat cell (3 cell x 17 = 51 file) ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in "${CELLS_SF10[@]}"; do
  run_concat_cell "$CELL"
done

echo "[$(date)] === [3/3] sf100 concat cell (1 cell x 17 = 17 file, 가장 무거움) ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in "${CELLS_SF100[@]}"; do
  run_concat_cell "$CELL"
done

# --- 마무리 ----------------------------------------------------------------
N_JSON=$(find "$OUT_BASE" -name '*.json' -type f 2>/dev/null | wc -l)
N_WARN=$(grep -c '\[WARN\]' "$LOG_DIR/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] === concat 측정 트랙 DONE — JSON $N_JSON / 119, WARN $N_WARN ===" \
  | tee -a "$LOG_DIR/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
