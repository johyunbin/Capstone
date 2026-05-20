#!/bin/bash
# v9 → concat chain — v9_sel_sweep 측정 완료 후 concat 측정 트랙 자동 launch.
# 5/16 작성 — handoff v31 chain script 패턴 (v10_v9_chain.sh) 차용.
#
# 동작:
#   1. v9_sel_sweep result dir 의 COMPLETE.flag 를 60s 간격 polling
#   2. flag 출현 → verify_concat_npy.py 실행 (concat NPY 빌드 sanity 게이트)
#   3. verify exit 0 (ALL PASS) → concat 측정 트랙 launch (tmux session=concat_track)
#   4. verify exit !=0 (FAIL) → alert 로그만 남기고 launch 안 함
#      (= concat NPY 빌드가 불완전 — build_concat_cells.py --all 미완 / 깨짐)
#   5. 종료
#
# v10_v9_chain.sh 와 차이: 이 script 는 v9 를 launch 하지 않고 "이미 돌고 있는"
# v9_sel_sweep 의 완료만 기다린다. 그리고 launch 전에 verify 게이트를 한 단계 더 둔다.
#
# 사용 (server 영역 — nohup 백그라운드 가동):
#   nohup bash /mnt/hdd0/home/capstone2026/_internal/scripts/v9_concat_chain.sh \
#     > /dev/null 2>&1 &
#   tail -f /tmp/v9_concat_chain.log        # 진행 확인
#
# 또는 tmux 로:
#   tmux new-session -d -s v9_concat_chain \
#     "bash /mnt/hdd0/home/capstone2026/_internal/scripts/v9_concat_chain.sh"
#
# 가동 여부는 사용자가 결정 — 이 script 는 작성만 되어 있고 자동 실행 X.

set -uo pipefail

# --- 경로 ------------------------------------------------------------------
V9_RESULT_DIR=/mnt/hdd0/home/capstone2026/results_v9_sel_sweep_20260515_1855
V9_FLAG="$V9_RESULT_DIR/COMPLETE.flag"
VERIFY=/mnt/hdd0/home/capstone2026/cache/rq3/verify_concat_npy.py
CONCAT_SCRIPT=/mnt/hdd0/home/capstone2026/_internal/scripts/launch_concat_track.sh
LOG=/tmp/v9_concat_chain.log

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

echo "[$(KST)] === v9 → concat chain START ===" | tee "$LOG"
echo "[$(KST)] v9 flag 감시: $V9_FLAG" | tee -a "$LOG"
echo "[$(KST)] verify 게이트: $VERIFY" | tee -a "$LOG"
echo "[$(KST)] concat launch: $CONCAT_SCRIPT" | tee -a "$LOG"

# === Step 1: v9_sel_sweep COMPLETE.flag polling (60s 간격) ===
echo "[$(KST)] step 1: v9 COMPLETE.flag polling 시작 (60s 간격)" | tee -a "$LOG"
POLL_COUNT=0
while true; do
    POLL_COUNT=$((POLL_COUNT + 1))
    if [ -f "$V9_FLAG" ]; then
        echo "[$(KST)] v9 COMPLETE.flag 감지 — $POLL_COUNT polls (~${POLL_COUNT} min)" \
            | tee -a "$LOG"
        break
    fi
    # 10분마다 살아있다는 로그 한 줄
    if [ $((POLL_COUNT % 10)) -eq 0 ]; then
        echo "[$(KST)] v9 still running ($POLL_COUNT min 경과)" | tee -a "$LOG"
    fi
    sleep 60
done

# === Step 2: concat NPY 빌드 sanity 게이트 (verify_concat_npy.py) ===
echo "[$(KST)] step 2: verify_concat_npy.py 실행 (concat NPY 빌드 검증 게이트)" \
    | tee -a "$LOG"
python3 "$VERIFY" 2>&1 | tee -a "$LOG"
VERIFY_RC=${PIPESTATUS[0]}
echo "[$(KST)] verify_concat_npy.py exit code = $VERIFY_RC" | tee -a "$LOG"

# === Step 3: 게이트 판정 ===
if [ "$VERIFY_RC" -ne 0 ]; then
    # verify FAIL — concat NPY 빌드 불완전. launch 하지 않는다.
    echo "[$(KST)] !!! ALERT: verify_concat_npy.py FAIL (rc=$VERIFY_RC) !!!" \
        | tee -a "$LOG"
    echo "[$(KST)] concat NPY 빌드가 불완전 — concat 측정 트랙 launch 중단." \
        | tee -a "$LOG"
    echo "[$(KST)] 조치: build_concat_cells.py --all 완료 여부 확인 후," \
        | tee -a "$LOG"
    echo "[$(KST)]       verify FAIL 항목 해결 → concat_track 수동 launch:" \
        | tee -a "$LOG"
    echo "[$(KST)]       tmux new -d -s concat_track \"bash $CONCAT_SCRIPT\"" \
        | tee -a "$LOG"
    echo "[$(KST)] === v9 → concat chain ABORTED (verify 게이트 FAIL) ===" \
        | tee -a "$LOG"
    exit 1
fi

# verify PASS — concat 측정 트랙 launch
echo "[$(KST)] verify ALL PASS ✓ — concat 측정 트랙 launch 진행" | tee -a "$LOG"
echo "[$(KST)] step 3: concat_track launch (tmux session=concat_track)" \
    | tee -a "$LOG"
tmux new-session -d -s concat_track \
    "bash $CONCAT_SCRIPT 2>&1 | tee /tmp/concat_track_console.log"
sleep 5

# tmux session 이 실제로 떴는지 확인
if tmux has-session -t concat_track 2>/dev/null; then
    echo "[$(KST)] concat_track tmux session 가동 확인 ✓" | tee -a "$LOG"
else
    echo "[$(KST)] !!! ALERT: concat_track tmux session 가동 실패 — 수동 확인 필요 !!!" \
        | tee -a "$LOG"
fi

echo "[$(KST)] === v9 → concat chain DONE — concat 측정 background 진행 중 ===" \
    | tee -a "$LOG"
echo "[$(KST)] concat 측정 monitoring: tmux attach -t concat_track" | tee -a "$LOG"
