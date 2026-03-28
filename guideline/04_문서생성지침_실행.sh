#!/bin/bash
# [04] 04_문서생성_실행.sh — Phase별 독립 claude 세션으로 문서생성 실행
# 사용: cd ~/Capstone && ./guideline/04_문서생성지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/문서생성.log"
STATE="guideline/PHASE_STATE_04_문서생성.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== 문서생성 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4 5)
PHASE_NAMES=(
  "환경 확인"
  "누락 PDF 탐지"
  "PDF 변환 실행"
  "품질 검증"
  "docx 변환 (선택)"
  "종합 리포트"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 문서생성 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/04_문서생성지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. 절대 fpdf2 사용 금지 — Chrome CDP(scripts/md2pdf.py)만 사용" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 문서생성 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
