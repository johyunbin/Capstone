#!/bin/bash
# 5 디자인 일괄 빌드 + PowerPoint PDF 변환
set -e
cd "$(dirname "$0")"
DRAFT_DIR=/Users/hyunbin/Capstone/submission/_drafts

DESIGNS="navy editorial bold gemini academic swiss soft"  # 7 디자인 (4/27)

echo "=== Build $DESIGNS ==="
for v in $DESIGNS; do
  echo "→ build $v"
  python3 build_$v.py "$DRAFT_DIR/속도는벡터_중간발표_$v.pptx"
done

echo ""
echo "=== Convert to PDF ==="
for v in $DESIGNS; do
  echo "→ pdf $v"
  ./convert_pdf.sh "$DRAFT_DIR/속도는벡터_중간발표_$v.pptx"
done

echo ""
echo "=== Done ==="
ls -lh "$DRAFT_DIR"/속도는벡터_중간발표_*.{pptx,pdf} 2>/dev/null
