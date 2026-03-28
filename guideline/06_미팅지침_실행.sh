#!/bin/bash
# 미팅지침 자동 실행 스크립트
# 사용법: cd ~/Capstone && ./guideline/06_미팅지침_실행.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/06_미팅지침.log"

echo "=== 미팅지침 시작: $(date) ===" | tee "$LOG_FILE"

# Claude Code 세션 실행
claude --print "guideline/06_미팅지침_auto.md 읽고 전체 Phase 실행" \
  2>&1 | tee -a "$LOG_FILE"

echo "=== 미팅지침 완료: $(date) ===" | tee -a "$LOG_FILE"
