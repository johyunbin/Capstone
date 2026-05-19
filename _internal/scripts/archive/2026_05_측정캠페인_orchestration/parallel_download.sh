#!/bin/bash
# Parallel HTTP Range download — 16 concurrent curl processes for single file.
# Usage: bash parallel_download.sh URL OUTPUT_FILE [N_CONNECTIONS]

set -e
URL=$1
OUT=$2
N=${3:-16}

TOTAL=$(curl -sI "$URL" | grep -i 'Content-Length' | awk '{print $2}' | tr -d '\r')
if [ -z "$TOTAL" ]; then
  echo "ERROR: cannot get Content-Length from $URL"
  exit 1
fi

echo "[$(date +%H:%M:%S)] Total: $TOTAL bytes ($(echo "scale=2; $TOTAL/1073741824" | bc) GB), N=$N parallel"

CHUNK=$((TOTAL / N))
TMP=$(mktemp -d)
echo "[$(date +%H:%M:%S)] Tmp: $TMP, chunks: $CHUNK bytes each"

PIDS=""
for i in $(seq 0 $((N-1))); do
  start=$((i * CHUNK))
  if [ "$i" -eq $((N-1)) ]; then
    range="${start}-"
  else
    end=$((start + CHUNK - 1))
    range="${start}-${end}"
  fi
  curl -s -H "Connection: close" -r "$range" -o "$TMP/part_$(printf '%03d' $i)" "$URL" &
  PIDS="$PIDS $!"
done

# Progress monitor in background
(
  while true; do
    sleep 30
    SIZE=$(du -bs "$TMP" 2>/dev/null | awk '{print $1}')
    if [ -n "$SIZE" ]; then
      PCT=$(echo "scale=1; $SIZE * 100 / $TOTAL" | bc)
      echo "[$(date +%H:%M:%S)] progress: $SIZE / $TOTAL ($PCT%)"
    fi
  done
) &
MON_PID=$!

# Wait for all curls
wait $PIDS
kill $MON_PID 2>/dev/null

echo "[$(date +%H:%M:%S)] All chunks downloaded. Concatenating..."
cat "$TMP"/part_*  > "$OUT"
rm -rf "$TMP"

ACTUAL_SIZE=$(stat -c '%s' "$OUT")
echo "[$(date +%H:%M:%S)] DONE. Final size: $ACTUAL_SIZE (expected $TOTAL)"
if [ "$ACTUAL_SIZE" != "$TOTAL" ]; then
  echo "WARNING: size mismatch"
  exit 2
fi
