#!/bin/bash
# 주간보고지침 자동 실행 스크립트
# 사용법: cd ~/Capstone && ./guideline/05_주간보고지침_실행.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/05_주간보고지침.log"

echo "=== 주간보고지침 시작: $(date) ===" | tee "$LOG_FILE"

# records/weekly 디렉토리 확인
mkdir -p "${PROJECT_ROOT}/records/weekly"

# Claude Code 세션 실행
claude --print "guideline/05_주간보고지침_auto.md 읽고 전체 Phase 실행. 리포트를 records/weekly/주간보고_$(date +%Y-%m-%d).md 에 저장." \
  2>&1 | tee -a "$LOG_FILE"

echo "=== 주간보고지침 완료: $(date) ===" | tee -a "$LOG_FILE"
