#!/bin/bash
# chain_monitor_persistent_5_16b.sh — v9 재측정 + concat_track 2 트랙 fault tolerance + persistent monitor
#
# 작성: 5/16 19:00 KST 세션 (조현빈)
# 목적: 본 세션 종료 후도 살아있는 monitor — file count + KeyError detection + stuck detection
#
# 5_16.sh 대비 변경점:
#   - 추적 stage 를 현재 진행 중인 2 트랙만으로 축소 (v9 재측정 + concat_track)
#   - glob `results_${stage}_*` 폐기 → timestamp 포함 full 경로 직접 하드코딩
#     (구 디렉토리 results_v9_sel_sweep_20260515_1855 무효 매칭 방지)
#   - 끝난/중단 트랙(v6/v7/v8/v10/구 v9) stage 목록에서 제거 → alert 노이즈 제거
#   - log/json/pid/alert 파일 경로 전부 _5_16b 로 (기존 5_16.sh 와 안 섞임)
#
# 사용:
#   nohup bash _internal/scripts/chain_monitor_persistent_5_16b.sh \
#     > _internal/chain_monitor_persistent_5_16b.log 2>&1 &
#   echo $! > _internal/chain_monitor_persistent_5_16b.pid
#
# 출력:
#   - main log: _internal/chain_monitor_persistent_5_16b.log (1분 마다 progress line)
#   - alert log: _internal/chain_monitor_alerts_5_16b.log (KeyError/stuck/anomaly 감지 시)
#   - status JSON: _internal/chain_monitor_status_5_16b.json (매 cycle 갱신, 다음 세션 read)
#
# 다음 세션 read:
#   cat _internal/chain_monitor_status_5_16b.json | python3 -m json.tool
#   tail -50 _internal/chain_monitor_alerts_5_16b.log

set -uo pipefail

# bash 3.2 (macOS default) — associative array X → case 함수로 호환성 우선

LOCAL_ROOT="/Users/hyunbin/Capstone"
INTERNAL="$LOCAL_ROOT/_internal"
MAIN_LOG="$INTERNAL/chain_monitor_persistent_5_16b.log"
ALERT_LOG="$INTERNAL/chain_monitor_alerts_5_16b.log"
STATUS_JSON="$INTERNAL/chain_monitor_status_5_16b.json"
PID_FILE="$INTERNAL/chain_monitor_persistent_5_16b.pid"

# server config
SERVER="capstone"
SERVER_ROOT="/mnt/hdd0/home/capstone2026"

# 추적 대상 트랙 — stage 이름 ↔ full 디렉토리 경로 직접 매핑.
# glob `_*` 안 씀 (구 디렉토리 results_v9_sel_sweep_20260515_1855 매칭 방지).
# 새 트랙 추가 시 STAGE_DIR + expected_count 두 군데 같이 수정.
stage_dir() {
    case "$1" in
        v9_resweep)   echo "$SERVER_ROOT/results_v9_sel_sweep_20260516_0530" ;;
        concat_track) echo "$SERVER_ROOT/results_concat_track_20260516_0537" ;;
        *) echo "" ;;
    esac
}

# Expected file counts (launch script base) — case 함수, bash 3.2 호환
expected_count() {
    case "$1" in
        v9_resweep)   echo 680 ;;   # v9 재측정 (sel sweep)
        concat_track) echo 357 ;;   # concat 측정 (sel sweep)
        *) echo 0 ;;
    esac
}

# 추적할 stage 목록 (위 두 함수에 정의된 것만)
STAGES="v9_resweep concat_track"

# stale threshold (분)
STALE_MIN=30

# poll interval (초)
INTERVAL=60

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

log() {
    # log = stdout + main log 둘 다 (JSON gen 외부에서 호출됨)
    echo "[$(KST)] $*" >> "$MAIN_LOG"
    echo "[$(KST)] $*"
}

# dedupe alert (같은 alert 매 cycle 반복 X — STUCK escalation 만 30 cycle 마다)
ALERT_SEEN_FILE="$INTERNAL/.chain_monitor_alert_seen_5_16b"
touch "$ALERT_SEEN_FILE"

alert() {
    local msg="$1"
    # key = STUCK/KeyError/EMPTY_LOG + stage 추출 (msg head)
    local key
    key=$(echo "$msg" | awk '{print $1, $2}')

    # 이미 raise 됐나? (30 cycle 이내 같은 key 면 silent)
    local last_cycle
    last_cycle=$(grep -F "|$key|" "$ALERT_SEEN_FILE" 2>/dev/null | tail -1 | cut -d'|' -f1)
    if [ -n "$last_cycle" ] && [ $((CYCLE - last_cycle)) -lt 30 ]; then
        # 30 cycle (=30분) 이내 같은 alert → silent
        return 0
    fi

    # alert = stderr + 별도 log ONLY (stdout 절대 X — JSON gen 섞이면 망)
    echo "[$(KST)] ALERT: $msg" >> "$ALERT_LOG"
    echo "[$(KST)] ALERT: $msg" >> "$MAIN_LOG"
    # macOS notification (best effort)
    osascript -e "display notification \"$msg\" with title \"Capstone Chain Monitor 5_16b\"" 2>/dev/null || true

    # mark seen
    echo "$CYCLE|$key|" >> "$ALERT_SEEN_FILE"
}

# Save PID
echo $$ > "$PID_FILE"
log "===== chain_monitor_persistent 5_16b START — PID=$$ ====="
log "MAIN_LOG=$MAIN_LOG"
log "ALERT_LOG=$ALERT_LOG"
log "STATUS_JSON=$STATUS_JSON"
log "추적 stage: $STAGES"
log "  v9_resweep   -> $(stage_dir v9_resweep) (expected $(expected_count v9_resweep))"
log "  concat_track -> $(stage_dir concat_track) (expected $(expected_count concat_track))"
log "INTERVAL=${INTERVAL}s, STALE_THRESHOLD=${STALE_MIN}min"

CYCLE=0

# SSH 로 넘길 stage→dir 쌍 (server 쪽 for loop 에서 파싱)
build_stage_pairs() {
    local out=""
    for s in $STAGES; do
        out="$out $s::$(stage_dir "$s")"
    done
    echo "$out"
}

while true; do
    CYCLE=$((CYCLE + 1))
    NOW_EPOCH=$(date +%s)

    STAGE_PAIRS=$(build_stage_pairs)

    # SSH 단일 connection 에 모든 정보 수집 (network 효율)
    REMOTE_OUT=$(ssh -o ConnectTimeout=10 -o ServerAliveInterval=5 "$SERVER" '
        STALE_SEC='"$((STALE_MIN * 60))"'
        NOW=$(date +%s)
        STAGE_PAIRS="'"$STAGE_PAIRS"'"

        # 각 트랙 = full 경로 직접 지정 (glob X). file count + latest mtime + KeyError/Traceback/empty log
        for PAIR in $STAGE_PAIRS; do
            stage="${PAIR%%::*}"
            D="${PAIR##*::}"
            if [ ! -d "$D" ]; then
                echo "STAGE|$stage|NOT_FOUND|0|0|0|0|0|0|0|none"
                continue
            fi
            # parquet+json count (excluding logs/)
            COUNT=$(find "$D" -mindepth 2 -type f \( -name "*.parquet" -o -name "*.json" \) ! -path "*/logs/*" 2>/dev/null | wc -l | tr -d " ")
            # latest mtime
            LATEST_MT=$(find "$D" -type f -newer /dev/null -printf "%T@\n" 2>/dev/null | sort -n | tail -1 | cut -d. -f1)
            LATEST_MT=${LATEST_MT:-0}
            AGE_SEC=$((NOW - LATEST_MT))
            # COMPLETE.flag 있는지
            if [ -f "$D/COMPLETE.flag" ]; then COMPLETE=1; else COMPLETE=0; fi
            # KeyError count in logs
            KEYERR=$(grep -l "KeyError" $D/logs/*.log 2>/dev/null | wc -l | tr -d " ")
            # Traceback count
            TRACEBACK=$(grep -l "Traceback" $D/logs/*.log 2>/dev/null | wc -l | tr -d " ")
            # empty log count (silent fail)
            EMPTY=$(find $D/logs/ -type f -size 0 -name "*.log" 2>/dev/null | wc -l | tr -d " ")
            # latest log file 1줄 (debug)
            LATEST_LOG_FILE=$(ls -t $D/logs/*.log 2>/dev/null | head -1 | xargs -I {} basename {} 2>/dev/null)
            LATEST_LOG_FILE=${LATEST_LOG_FILE:-none}
            echo "STAGE|$stage|$D|$COUNT|$LATEST_MT|$AGE_SEC|$COMPLETE|$KEYERR|$TRACEBACK|$EMPTY|$LATEST_LOG_FILE"
        done

        # active processes
        echo "PROCS|$(ps -efww | grep -E "measure_paper_exact.py|launch_v" | grep -v grep | wc -l | tr -d " ")"

        # tmux sessions
        echo "TMUX|$(tmux ls 2>/dev/null | wc -l | tr -d " ")"

        # chain watcher script alive
        for script in /tmp/v6_v7_chain.sh /tmp/v7_v8_chain.sh /tmp/v8_v9_chain.sh /tmp/v10_v9_chain.sh /mnt/hdd0/home/capstone2026/_internal/scripts/v10_v9_chain.sh; do
            if [ -f "$script" ]; then
                ALIVE=$(ps -efww | grep -F "$script" | grep -v grep | wc -l | tr -d " ")
                echo "WATCHER|$script|$ALIVE"
            fi
        done
    ' 2>&1)
    SSH_RC=$?

    if [ $SSH_RC -ne 0 ]; then
        alert "SSH FAIL (rc=$SSH_RC) cycle=$CYCLE"
        sleep "$INTERVAL"
        continue
    fi

    # Parse output → build JSON
    {
        echo "{"
        echo "  \"cycle\": $CYCLE,"
        echo "  \"timestamp_kst\": \"$(KST)\","
        echo "  \"timestamp_epoch\": $NOW_EPOCH,"
        echo "  \"stages\": ["

        FIRST=1
        TOTAL_KEYERR=0
        TOTAL_TRACEBACK=0
        TOTAL_EMPTY=0
        STUCK_DETECTED=0

        while IFS='|' read -r tag stage path count mt age complete keyerr traceback empty latest_log; do
            [ "$tag" != "STAGE" ] && continue
            [ "$path" = "NOT_FOUND" ] && continue

            if [ $FIRST -eq 0 ]; then echo "    ,"; fi
            FIRST=0

            EXPECTED_VAL=$(expected_count "$stage")
            PCT=0
            if [ "$EXPECTED_VAL" -gt 0 ]; then
                PCT=$(awk -v c="$count" -v e="$EXPECTED_VAL" 'BEGIN{printf "%.1f", c*100.0/e}')
            fi

            STUCK="false"
            if [ "$complete" -eq 0 ] && [ "$age" -gt $((STALE_MIN * 60)) ]; then
                STUCK="true"
                STUCK_DETECTED=1
            fi

            cat <<EOF
    {
      "stage": "$stage",
      "path": "$path",
      "file_count": $count,
      "expected": $EXPECTED_VAL,
      "progress_pct": $PCT,
      "latest_mtime_epoch": $mt,
      "latest_mtime_age_sec": $age,
      "latest_mtime_age_min": $((age / 60)),
      "complete_flag": $complete,
      "stuck": $STUCK,
      "keyerror_count": $keyerr,
      "traceback_count": $traceback,
      "empty_log_count": $empty,
      "latest_log_file": "$latest_log"
    }
EOF
            TOTAL_KEYERR=$((TOTAL_KEYERR + keyerr))
            TOTAL_TRACEBACK=$((TOTAL_TRACEBACK + traceback))
            TOTAL_EMPTY=$((TOTAL_EMPTY + empty))

            # alert detection
            if [ "$STUCK" = "true" ]; then
                alert "STUCK $stage path=$path age=$((age/60))min count=$count latest_log=$latest_log"
            fi
            if [ "$keyerr" -gt 0 ]; then
                alert "KeyError $stage count=$keyerr (silent fail in $path)"
            fi
            if [ "$empty" -gt 0 ]; then
                alert "EMPTY_LOG $stage count=$empty (likely silent crash in $path)"
            fi

        done <<< "$REMOTE_OUT"

        echo "  ],"

        # active processes / tmux / watcher status
        PROCS=$(echo "$REMOTE_OUT" | grep "^PROCS|" | head -1 | cut -d'|' -f2)
        TMUX=$(echo "$REMOTE_OUT" | grep "^TMUX|" | head -1 | cut -d'|' -f2)
        echo "  \"active_processes\": ${PROCS:-0},"
        echo "  \"tmux_sessions\": ${TMUX:-0},"
        echo "  \"watchers\": ["
        FIRST_W=1
        while IFS='|' read -r wtag wscript walive; do
            [ "$wtag" != "WATCHER" ] && continue
            if [ $FIRST_W -eq 0 ]; then echo "    ,"; fi
            FIRST_W=0
            echo "    {\"script\": \"$wscript\", \"alive\": $walive}"
        done <<< "$REMOTE_OUT"
        echo "  ],"

        echo "  \"summary\": {"
        echo "    \"total_keyerror\": $TOTAL_KEYERR,"
        echo "    \"total_traceback\": $TOTAL_TRACEBACK,"
        echo "    \"total_empty_log\": $TOTAL_EMPTY,"
        echo "    \"any_stuck\": $STUCK_DETECTED"
        echo "  }"
        echo "}"
    } > "$STATUS_JSON.tmp" && mv "$STATUS_JSON.tmp" "$STATUS_JSON"

    # progress line (1줄, main log)
    PROGRESS_LINE="cycle=$CYCLE procs=${PROCS:-0} tmux=${TMUX:-0} keyerr=$TOTAL_KEYERR empty=$TOTAL_EMPTY stuck=$STUCK_DETECTED"
    log "$PROGRESS_LINE"

    # 측정 process 0 + 모든 stage NOT_COMPLETE → alert
    if [ "${PROCS:-0}" -eq 0 ]; then
        INCOMPLETE_STAGES=$(echo "$REMOTE_OUT" | awk -F'|' '$1=="STAGE" && $7=="0" {print $2}' | sort -u | tr '\n' ',')
        if [ -n "$INCOMPLETE_STAGES" ]; then
            alert "NO_PROCESS — measurement halted. Incomplete stages: $INCOMPLETE_STAGES"
        fi
    fi

    sleep "$INTERVAL"
done
