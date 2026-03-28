#!/bin/bash
# [07] 07_발표_실행.sh — Phase별 독립 claude 세션으로 발표 준비 실행
# 사용: cd ~/Capstone && ./guideline/07_발표지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/발표.log"
STATE="guideline/PHASE_STATE_07_발표.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== 발표 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4 5 6)
PHASE_NAMES=(
  "발표 유형 식별 + 샘플 확인"
  "슬라이드 구조 설계"
  "슬라이드 내용 작성"
  "발표 스크립트"
  "포스터/팜플렛 (전시회)"
  "리허설 체크리스트 + Q&A"
  "종합 리포트"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 발표 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/07_발표지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. templates/samples/ 참조, 슬라이드당 핵심 메시지 1개" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 발표 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
