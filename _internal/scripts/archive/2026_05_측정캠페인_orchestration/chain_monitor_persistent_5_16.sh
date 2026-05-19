#!/bin/bash
# chain_monitor_persistent_5_16.sh — v6/v7/v8/v9/v10 chain 영역 fault tolerance + persistent monitor
#
# 작성: 5/16 01:00 KST 세션 (조현빈)
# 목적: 본 세션 종료 후도 살아있는 monitor — file count + KeyError detection + stuck detection
#
# 사용:
#   nohup bash _internal/scripts/chain_monitor_persistent_5_16.sh \
#     > _internal/chain_monitor_persistent_5_16.log 2>&1 &
#   echo $! > _internal/chain_monitor_persistent_5_16.pid
#
# 출력:
#   - main log: _internal/chain_monitor_persistent_5_16.log (1분 마다 progress line)
#   - alert log: _internal/chain_monitor_alerts_5_16.log (KeyError/stuck/anomaly 감지 시)
#   - status JSON: _internal/chain_monitor_status_5_16.json (매 cycle 갱신, 다음 세션 read)
#
# 다음 세션 영역 read:
#   cat _internal/chain_monitor_status_5_16.json | python3 -m json.tool
#   tail -50 _internal/chain_monitor_alerts_5_16.log

set -uo pipefail

# bash 3.2 (macOS default) 영역 associative array 영역 X → /usr/bin/env bash 5+ 영역 강제
# OR 함수 영역 case 영역 사용 (호환성 우선)

LOCAL_ROOT="/Users/hyunbin/Capstone"
INTERNAL="$LOCAL_ROOT/_internal"
MAIN_LOG="$INTERNAL/chain_monitor_persistent_5_16.log"
ALERT_LOG="$INTERNAL/chain_monitor_alerts_5_16.log"
STATUS_JSON="$INTERNAL/chain_monitor_status_5_16.json"
PID_FILE="$INTERNAL/chain_monitor_persistent_5_16.pid"

# server config
SERVER="capstone"
SERVER_ROOT="/mnt/hdd0/home/capstone2026"

# Expected file counts (launch script 영역 base) — case function 영역 bash 3.2 호환
expected_count() {
    case "$1" in
        v6_caseB) echo 50 ;;        # 8 cell × 6 (PARETO5 + B1) — 실측 40 (K=10 fail 10 빠짐)
        v7_extras) echo 18 ;;       # 3 cell × 6 — 실측 12 (A8 fail 6 빠짐)
        v6v7_fix) echo 18 ;;        # 3 cell × 6 (A1-K10 + A1-SSN-K10 + A8 재측정)
        v8_full) echo 600 ;;        # 12 cell × 50 method (STOP, history)
        v10_full16) echo 129 ;;     # 12 cell × 11 method (A5-sf1-SIFT × 3 skip)
        v9_sel_sweep) echo 680 ;;   # 16 cell × 2 sel × 17 + K granularity 136
        *) echo 0 ;;
    esac
}

# stale threshold (분)
STALE_MIN=30

# poll interval (초)
INTERVAL=60

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

log() {
    # log 영역 stdout 영역 + main log 영역 둘 다 (JSON gen 영역 외부 영역 호출됨)
    echo "[$(KST)] $*" >> "$MAIN_LOG"
    echo "[$(KST)] $*"
}

# dedupe 영역 alert (같은 alert 영역 매 cycle 영역 반복 영역 X — STUCK 영역 escalation 영역만 매 30 cycle)
ALERT_SEEN_FILE="$INTERNAL/.chain_monitor_alert_seen"
touch "$ALERT_SEEN_FILE"

alert() {
    local msg="$1"
    # key = STUCK/KeyError/EMPTY_LOG + stage 추출 (msg 영역 head)
    local key
    key=$(echo "$msg" | awk '{print $1, $2}')

    # 이미 영역 raise 됐나? (key 영역 첫 16 char + cycle 영역 100 차이 시 reset)
    local last_cycle
    last_cycle=$(grep -F "|$key|" "$ALERT_SEEN_FILE" 2>/dev/null | tail -1 | cut -d'|' -f1)
    if [ -n "$last_cycle" ] && [ $((CYCLE - last_cycle)) -lt 30 ]; then
        # 30 cycle (=30분) 영역 이내 영역 같은 alert 영역 → silent 영역
        return 0
    fi

    # alert 영역 stderr 영역 + 별도 log 영역 ONLY (stdout 영역 절대 X — JSON gen 영역 섞이면 망)
    echo "[$(KST)] ALERT: $msg" >> "$ALERT_LOG"
    echo "[$(KST)] ALERT: $msg" >> "$MAIN_LOG"
    # macOS notification (best effort)
    osascript -e "display notification \"$msg\" with title \"Capstone Chain Monitor\"" 2>/dev/null || true

    # mark seen
    echo "$CYCLE|$key|" >> "$ALERT_SEEN_FILE"
}

# Save PID
echo $$ > "$PID_FILE"
log "===== chain_monitor_persistent START — PID=$$ ====="
log "MAIN_LOG=$MAIN_LOG"
log "ALERT_LOG=$ALERT_LOG"
log "STATUS_JSON=$STATUS_JSON"
log "INTERVAL=${INTERVAL}s, STALE_THRESHOLD=${STALE_MIN}min"

CYCLE=0

while true; do
    CYCLE=$((CYCLE + 1))
    NOW_EPOCH=$(date +%s)

    # SSH 단일 connection 영역 모든 정보 수집 (network 영역 효율)
    REMOTE_OUT=$(ssh -o ConnectTimeout=10 -o ServerAliveInterval=5 "$SERVER" '
        STALE_SEC='"$((STALE_MIN * 60))"'
        NOW=$(date +%s)
        SERVER_ROOT="'"$SERVER_ROOT"'"

        # 각 chain dir 영역 file count + latest mtime + KeyError count + Traceback count + empty log count
        for stage in v6_caseB v7_extras v6v7_fix v8_full v10_full16 v9_sel_sweep; do
            DIRS=$(ls -d $SERVER_ROOT/results_${stage}_*/ 2>/dev/null)
            if [ -z "$DIRS" ]; then
                echo "STAGE|$stage|NOT_FOUND|0|0|0|0|0|0|"
                continue
            fi
            for D in $DIRS; do
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
                # empty log count (lpm1_proper 같은 silent fail)
                EMPTY=$(find $D/logs/ -type f -size 0 -name "*.log" 2>/dev/null | wc -l | tr -d " ")
                # latest log file 영역 1줄 (debug)
                LATEST_LOG_FILE=$(ls -t $D/logs/*.log 2>/dev/null | head -1 | xargs -I {} basename {} 2>/dev/null)
                LATEST_LOG_FILE=${LATEST_LOG_FILE:-none}
                echo "STAGE|$stage|$D|$COUNT|$LATEST_MT|$AGE_SEC|$COMPLETE|$KEYERR|$TRACEBACK|$EMPTY|$LATEST_LOG_FILE"
            done
        done

        # active processes
        echo "PROCS|$(ps -efww | grep -E "measure_paper_exact.py|launch_v" | grep -v grep | wc -l | tr -d " ")"

        # tmux sessions
        echo "TMUX|$(tmux ls 2>/dev/null | wc -l | tr -d " ")"

        # chain watcher script alive
        for script in /tmp/v6_v7_chain.sh /tmp/v7_v8_chain.sh /tmp/v8_v9_chain.sh /tmp/v10_v9_chain.sh /mnt/hdd0/home/capstone2026/_internal/scripts/v10_v9_chain.sh; do
            if [ -f "$script" ]; then
                # 해당 script 영역 process 영역 alive?
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

    # 측정 process 영역 0 영역 + 모든 stage 영역 NOT_COMPLETE 영역 watcher 영역 dead 영역 → alert
    if [ "${PROCS:-0}" -eq 0 ]; then
        # 어떤 stage 영역 incomplete 영역 있나?
        INCOMPLETE_STAGES=$(echo "$REMOTE_OUT" | awk -F'|' '$1=="STAGE" && $7=="0" {print $2}' | sort -u | tr '\n' ',')
        if [ -n "$INCOMPLETE_STAGES" ]; then
            alert "NO_PROCESS — measurement halted. Incomplete stages: $INCOMPLETE_STAGES"
        fi
    fi

    sleep "$INTERVAL"
done
