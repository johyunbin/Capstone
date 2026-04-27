#!/bin/bash
# pptx → pdf 변환. Keynote AppleScript (한국어 폰트 정확).
# 결과 pptx 는 PowerPoint 호환 (open with PowerPoint 정상 작동).
set -e
PPTX="$1"
PDF="${PPTX%.pptx}.pdf"

if [[ ! -f "$PPTX" ]]; then
  echo "ERR: pptx not found: $PPTX" >&2
  exit 1
fi

[[ -f "$PDF" ]] && rm "$PDF"

osascript <<EOF
tell application "Keynote"
  activate
  set theDoc to open POSIX file "$PPTX"
  delay 2
  export theDoc to POSIX file "$PDF" as PDF
  delay 1
  close theDoc saving no
end tell
EOF

if [[ -f "$PDF" ]]; then
  echo "OK: $PDF ($(du -h "$PDF" | cut -f1))"
else
  echo "ERR: PDF conversion failed: $PPTX" >&2
  exit 2
fi
