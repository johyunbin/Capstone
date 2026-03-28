#!/usr/bin/env bash
# 09_학습정리지침 오케스트레이터
# 사용: ./guideline/09_학습정리지침_실행.sh [폴더]
# 예시: ./guideline/09_학습정리지침_실행.sh kr
#       ./guideline/09_학습정리지침_실행.sh us

set -euo pipefail
cd "$(dirname "$0")/.."

FOLDER="${1:-kr}"
GUIDELINE="guideline/09_학습정리지침_auto.md"

if [[ ! -f "$GUIDELINE" ]]; then
  echo "❌ 지침 파일 없음: $GUIDELINE"
  exit 1
fi

echo "📚 학습정리지침 실행 — 대상: learning/$FOLDER/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Claude Code에 지침 전달
claude --print "
learning/$FOLDER/ 폴더의 모든 스크립트를 분석해줘.

지침 파일: $GUIDELINE
이 지침의 Phase 0부터 Phase 5까지 순서대로 자동 실행해줘.
전권 위임 — 모든 단계를 사용자 확인 없이 진행.
"
