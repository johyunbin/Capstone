#!/bin/bash
# K granularity 6 cell 재측정 — K10/K30 빠진 12 method 보강. 5/17 작성.
#
# --- 배경 ------------------------------------------------------------------
# K granularity 측정에서 6개 cell 이 K10/K30 에서 4 method 만 측정됐다.
# 사용 16 method 중 12개가 빠졌다. 본 script 는 그 12 method 를 재측정한다.
#   이미 측정된 4 method (재측정 X): chao_weighted / hilbert_real /
#                                    hyperloglog / sparse_rp
#   빠진 12 method (본 script 측정): minibatch_partial / gmm / faiss_ivf /
#     zorder_morton / skilling_hilbert / rsvd / ica_fastica / cum_sqrtf /
#     lavallee_hidiroglou / rabitq_strat / mhist2 / pca1d
#
# K20 은 default 측정에 이미 있으므로 본 script 는 K10/K30 만.
#
# --- 측정 대상 -------------------------------------------------------------
# 6 cell:
#   A5-scale-sf1     DEEP sf1   (800K rows)   — 가벼움
#   A5-scale-sf10    DEEP sf10  (8M rows)     — 중간
#   A2-Fig7          YFCC sf10  (8M rows, TPC-H 8 query) — 중간
#   A2-Fig9          DEEP+WIKI cross sf10 (8M rows, TPC-H 8 query) — 중간
#   A1-DEEP          DEEP sf100 (80M rows)    — 무거움
#   A5-scale-sf100   DEEP sf100 (80M rows)    — 무거움
#
# cell+K 1조합 = B1 1개 + CaseB 12 method = 13 file.
# 전체 = 6 cell x 2 K(10,30) x 13 = 156 file.
#
# B1 도 K10/K30 재측정한다 — 별도 agent 가 measure_paper_exact.py 의
# B1 K-의존 결함을 수정 중이다. 그 수정이 끝난 뒤 본 script 를 launch 하면
# B1 도 올바른 STRATA_K 로 측정된다. (launch 전 확인 사항 참조.)
#
# --- selectivity ------------------------------------------------------------
# 6 cell 모두 CellSpec.selectivities = [PAPER_SEL_DEFAULT] = 0.01 로 정의돼
# 있다 (measure_paper_exact.py L98-99, L205/231/248/279). sel=0.01 이 이미
# cell default 이므로 기존 4 method 측정과 정합. 현재 measure_paper_exact.py
# (v6) 에는 --sel CLI 인자가 없으므로 측정 명령에 --sel 을 전달하지 않는다.
#   (--sel 은 concat track 용 미래 수정 사항 — 본 K granularity 트랙 무관.)
#
# --- K override 방식 --------------------------------------------------------
# STRATA_K env → measure_paper_exact.py L45-49 → mc.N_STRATA 를 K 로 override.
# measure_paper_exact.py 의 결과 JSON 파일명은 {cell.sub}_B1.json /
# {cell.sub}_CaseB_{method}.json 으로 고정 — K 미포함. 따라서 K10/K30 결과를
# 같은 디렉토리에 쓰면 덮어쓰기 된다. OUT 디렉토리를 {CELL}_K{K}/ 로 분리한다.
#
# --- 선행 조건 (이 script launch 전 반드시) --------------------------------
#   1. B1 K-의존 결함 수정 완료 — 별도 agent 가 measure_paper_exact.py 수정 중.
#      수정 전 launch 하면 B1 측정 156 中 12개가 잘못된 값으로 나온다.
#   2. NPY/strata/query artifact 가 6 cell 모두 빌드돼 있는지
#      (cache/rq1/*.npy + cache/rq1/query_selectivity_*.parquet).
#   3. measure_paper_exact.py --dry-run --cell {CELL} 로 6 cell sub 이름 대조.
#
# --- 사용법 ----------------------------------------------------------------
#   tmux new -d -s k_gran_6cell \
#     'bash /mnt/hdd0/home/capstone2026/_internal/scripts/launch_k_granularity_6cell_5_17.sh'
#   tmux attach -t k_gran_6cell           # 진행 확인
#   tail -f $OUT_BASE/logs/_main.log      # 로그 추적
#
# --- 출력 ------------------------------------------------------------------
#   /mnt/hdd0/home/capstone2026/results_k_granularity_6cell_{TS}/
#     {CELL}_K{K}/{CELL}_B1.json
#     {CELL}_K{K}/{CELL}_CaseB_{method}.json
#     logs/_main.log + logs/{CELL}_K{K}_*.log
#     COMPLETE.flag                       <- 전부 끝나면 touch
#
# 결과 JSON 이 이미 있으면 해당 측정은 skip — 중단 후 재실행 안전 (idempotent).
#
# --- 추정 소요 (cell별 ETA 는 script 하단 주석 + 요약 참조) ----------------
#   sf1  cell : ~25-45 min / K  (13 file, NPY warm)
#   sf10 cell : ~1.5-3 h / K    (13 file; A2-Fig7/Fig9 는 TPC-H 8 query 라 상한)
#   sf100 cell: ~6-14 h / K     (13 file, 80M rows — method당 수십 분~1h+)
#   전체 6 cell x 2 K = 156 file : 대략 35-60 h.
#   가벼운 cell(sf1) 먼저 -> 무거운 sf100(A1-DEEP/A5-scale-sf100) 마지막.

set -u   # set -e 는 쓰지 않음 — 1 측정 실패가 전체를 죽이면 안 됨.
         # 각 측정은 || 로 개별 처리, fail 은 _main.log 에 [WARN] 기록.

SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_k_granularity_6cell_${TS}
LOG_DIR=$OUT_BASE/logs
mkdir -p "$LOG_DIR"

echo "[$(date)] === K granularity 6 cell 재측정 (K10/K30) launch START ===" \
  | tee "$LOG_DIR/_main.log"
echo "OUT_BASE=$OUT_BASE" | tee -a "$LOG_DIR/_main.log"

# --- 재측정 12 method (이미 측정된 4 method 제외) --------------------------
# 제외: chao_weighted / hilbert_real / hyperloglog / sparse_rp
M12=(minibatch_partial gmm faiss_ivf zorder_morton skilling_hilbert rsvd \
     ica_fastica cum_sqrtf lavallee_hidiroglou rabitq_strat mhist2 pca1d)

# --- K 목록 (K20 은 default 측정에 이미 있음) ------------------------------
KS=(10 30)

# --- cell+K 1조합 측정: B1 1개 + CaseB 12 method ---------------------------
# STRATA_K env 로 mc.N_STRATA override. 결과 JSON 존재 시 skip (idempotent).
run_cell_k() {
  local CELL=$1
  local K=$2
  local OUT=$OUT_BASE/${CELL}_K${K}
  mkdir -p "$OUT"

  # --- B1 (대조군, paper §V-B Bernoulli) ---
  # B1 도 K10/K30 재측정 — B1 K-의존 결함 수정 후 올바른 STRATA_K 로 측정된다.
  local b1_json="$OUT/${CELL}_B1.json"
  if [ -f "$b1_json" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $CELL K$K B1 (결과 JSON 존재)" \
      | tee -a "$LOG_DIR/_main.log"
  else
    echo "[$(date +%H:%M:%S)] === $CELL K$K B1 (대조군) ===" \
      | tee -a "$LOG_DIR/_main.log"
    STRATA_K=$K python3 "$SCRIPT" --rq 3 --phase A --cell "$CELL" --mode B1 \
      --output "$OUT" \
      2>&1 | tee "$LOG_DIR/${CELL}_K${K}_B1.log" \
      || echo "[WARN] $CELL K$K B1 failed" | tee -a "$LOG_DIR/_main.log"
  fi

  # --- CaseB 12 method (실험군, B1+method ensemble) ---
  local m
  for m in "${M12[@]}"; do
    local m_json="$OUT/${CELL}_CaseB_${m}.json"
    if [ -f "$m_json" ]; then
      echo "[$(date +%H:%M:%S)] SKIP $CELL K$K CaseB $m (결과 JSON 존재)" \
        | tee -a "$LOG_DIR/_main.log"
      continue
    fi
    echo "[$(date +%H:%M:%S)] === $CELL K$K CaseB $m (실험군) ===" \
      | tee -a "$LOG_DIR/_main.log"
    STRATA_K=$K python3 "$SCRIPT" --rq 3 --phase B --cell "$CELL" \
      --mode CaseB --method "$m" --output "$OUT" \
      2>&1 | tee "$LOG_DIR/${CELL}_K${K}_CaseB_${m}.log" \
      || echo "[WARN] $CELL K$K CaseB $m failed" | tee -a "$LOG_DIR/_main.log"
  done
}

# --- cell 1개를 K10/K30 전부 측정 ------------------------------------------
run_cell() {
  local CELL=$1
  local K
  for K in "${KS[@]}"; do
    run_cell_k "$CELL" "$K"
  done
}

# --- 측정 순서: 가벼운 cell 먼저, 무거운 sf100 마지막 ----------------------
# [1] 가벼운 cell — A5-scale-sf1(800K), A5-scale-sf10(8M)
echo "[$(date)] === [1/3] 가벼운 cell: A5-scale-sf1 / A5-scale-sf10 ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in A5-scale-sf1 A5-scale-sf10; do
  run_cell "$CELL"
done

# [2] 중간 cell — A2-Fig7(YFCC sf10), A2-Fig9(DEEP+WIKI cross sf10)
#     둘 다 TPC-H 8 query 라 sf10 치고는 무거운 편.
echo "[$(date)] === [2/3] 중간 cell: A2-Fig7 / A2-Fig9 (TPC-H 8 query) ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in A2-Fig7 A2-Fig9; do
  run_cell "$CELL"
done

# [3] 무거운 cell — A1-DEEP, A5-scale-sf100 (둘 다 DEEP sf100, 80M rows)
echo "[$(date)] === [3/3] 무거운 cell: A1-DEEP / A5-scale-sf100 (80M rows) ===" \
  | tee -a "$LOG_DIR/_main.log"
for CELL in A1-DEEP A5-scale-sf100; do
  run_cell "$CELL"
done

# --- 마무리 ----------------------------------------------------------------
N_JSON=$(find "$OUT_BASE" -name '*.json' -type f 2>/dev/null | wc -l)
N_WARN=$(grep -c '\[WARN\]' "$LOG_DIR/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] === K granularity 6 cell 재측정 DONE — JSON $N_JSON / 156, WARN $N_WARN ===" \
  | tee -a "$LOG_DIR/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
