#!/bin/bash
# [03] 03_제출물_실행.sh — Phase별 독립 claude 세션으로 제출물 작성
# 사용: cd ~/Capstone && ./guideline/03_제출물지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/제출물.log"
STATE="guideline/PHASE_STATE_03_제출물.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep,WebFetch"

echo "=== 제출물 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4 5 6)
PHASE_NAMES=(
  "일정 확인 + 다음 마감 식별"
  "양식 확인"
  "기존 자료 수집"
  "제출물 작성"
  "검증 + 최종본 저장"
  "일정 동기화"
  "결과 보고"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 제출물 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/03_제출물지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. 팀명 '속도는벡터' 일관 표기, 한국어 학술 산문" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 제출물 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
