#!/bin/bash
# [08] 08_연구설계_실행.sh — Phase별 독립 claude 세션으로 연구설계 실행
# 사용: cd ~/Capstone && ./guideline/08_연구설계지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/연구설계.log"
STATE="guideline/PHASE_STATE_08_연구설계.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== 연구설계 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4 5 6)
PHASE_NAMES=(
  "현재 설계 상태 파악"
  "연구 질문 정의"
  "실험 설계서 작성"
  "방법론 상세화 — Cascade Decomposition"
  "피드백 반영 + 버전 관리"
  "확정 + 연동"
  "종합 리포트"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 연구설계 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/08_연구설계지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. plans/ 에 타임스탬프 파일명으로 저장" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 연구설계 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
