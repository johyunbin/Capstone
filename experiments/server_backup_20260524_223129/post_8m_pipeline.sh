#!/bin/bash
# 8M 측정 종료 후 자동 chain 실행 watchdog.
#
# 흐름 (전부 서버 cache/ 기준):
#   1. /tmp/measure_8m_done.flag 출현 대기 (poll 60s)
#   2. phase7_8m_dtarget_*.json → query_selectivity_8m.parquet 변환
#   3. RQ3 8M sensitivity 측정 (12 method × DEEP_8M × 2 sel × 5 seed × 100 query)
#   4. 12 parquet 산출 → cache/rq1/rq3_8m_*.parquet
#   5. summary 출력 — q_error mean per (method × dataset × sel)
#   6. /tmp/post_8m_done.flag 생성 (사용자 깨면 회수 트리거)
#
# 사용 (서버 tmux 안에서):
#   tmux new-session -d -s post_8m
#   tmux send-keys -t post_8m "bash /mnt/hdd0/home/capstone2026/cache/rq3/post_8m_pipeline.sh 2>&1 | tee /mnt/hdd0/home/capstone2026/cache/post_8m_pipeline.log" C-m
#
# 또는 백그라운드:
#   nohup bash post_8m_pipeline.sh > /mnt/hdd0/home/capstone2026/cache/post_8m_pipeline.log 2>&1 &
#
# 회수 (로컬 자고 일어나서):
#   ssh capstone "ls /tmp/post_8m_done.flag" && \
#       scp 'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_*.parquet' \
#           experiments/results/rq3_agnostic/

set -euo pipefail

CACHE=/mnt/hdd0/home/capstone2026/cache
RQ3=$CACHE/rq3
LOG=$CACHE/post_8m_pipeline.log

DONE_FLAG=/tmp/measure_8m_done.flag
POST_DONE_FLAG=/tmp/post_8m_done.flag

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

echo "[$(KST)] post_8m_pipeline.sh START — waiting for $DONE_FLAG"

# === 1. 8M 측정 종료 대기 ===
while [ ! -f "$DONE_FLAG" ]; do
    sleep 60
done
echo "[$(KST)] $DONE_FLAG detected. content:"
cat "$DONE_FLAG"
echo ""

# === 2. dtarget JSON → parquet 변환 ===
echo "[$(KST)] step 2: convert dtarget JSON → query_selectivity_8m.parquet"
cd "$RQ3"
python3 convert_8m_dtarget_to_parquet.py 2>&1 || {
    echo "[$(KST)] CRITICAL: convert failed — aborting"
    exit 1
}

# === 3. 8M sensitivity 측정 (6 method) ===
echo "[$(KST)] step 3: run_8m_sensitivity.py (6 methods)"
cd "$RQ3"
python3 run_8m_sensitivity.py 2>&1 || {
    echo "[$(KST)] WARNING: 8M sensitivity 일부 실패 (다음 method 계속됨)"
    # exit 안 함 — 부분 산출이라도 보존
}

# === 4. 산출 확인 ===
echo "[$(KST)] step 4: 산출 확인"
ls -la "$CACHE"/rq1/rq3_8m_*.parquet 2>&1 || echo "[$(KST)] WARNING: 8M sensitivity 산출 없음"

# === 5. summary — q_error 평균 per (method × dataset × sel) ===
echo ""
echo "[$(KST)] step 5: q_error mean summary"
python3 - <<'PYEOF' 2>&1 || echo "[$(KST)] summary 실패 (parquet 일부 없음 가능)"
import glob
import pandas as pd
files = sorted(glob.glob("/mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_*.parquet"))
if not files:
    print("(8M parquet 없음)")
    exit()
frames = []
for f in files:
    df = pd.read_parquet(f)
    frames.append(df)
all_df = pd.concat(frames, ignore_index=True).dropna(subset=["q_error"])
print(f"총 {len(all_df):,} rows from {len(files)} files")
print()
piv = all_df.groupby(["dataset", "mode", "selectivity"])["q_error"].mean().unstack().round(4)
print(piv.to_string())
PYEOF

# === 6. done flag ===
echo "[$(KST)] post_8m_pipeline.sh END" > "$POST_DONE_FLAG"
echo "[$(KST)] $POST_DONE_FLAG generated. 사용자 회수 가능 상태."
echo ""
echo "회수 명령 (로컬):"
echo "  scp 'capstone:$CACHE/rq1/rq3_8m_*.parquet' experiments/results/rq3_agnostic/"
echo "  ssh capstone 'cat $LOG'  # 본 로그 직접 확인"
