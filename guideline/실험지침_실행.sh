#!/bin/bash
# 실험지침 자동 실행 스크립트
# 사용법: cd ~/Capstone && ./guideline/실험지침_실행.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/실험지침.log"

echo "=== 실험지침 시작: $(date) ===" | tee "$LOG_FILE"

# Phase 0: 환경 확인
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 0: 환경 확인 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

echo "PostgreSQL: $(psql --version 2>/dev/null || echo '미설치')" | tee -a "$LOG_FILE"

PGVEC=$(psql -t -c "SELECT extversion FROM pg_extension WHERE extname='vector'" 2>/dev/null | tr -d ' ' || echo "미설치")
echo "pgvector: ${PGVEC}" | tee -a "$LOG_FILE"

DUCKDB_VER=$(python3 -c "import duckdb; print(duckdb.__version__)" 2>/dev/null || echo "미설치")
echo "DuckDB: ${DUCKDB_VER}" | tee -a "$LOG_FILE"

NUMPY_VER=$(python3 -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "미설치")
echo "NumPy: ${NUMPY_VER}" | tee -a "$LOG_FILE"

FAISS_VER=$(python3 -c "import faiss; print('설치됨')" 2>/dev/null || echo "미설치")
echo "FAISS: ${FAISS_VER}" | tee -a "$LOG_FILE"

MPL_VER=$(python3 -c "import matplotlib; print(matplotlib.__version__)" 2>/dev/null || echo "미설치")
echo "matplotlib: ${MPL_VER}" | tee -a "$LOG_FILE"

SEABORN_VER=$(python3 -c "import seaborn; print(seaborn.__version__)" 2>/dev/null || echo "미설치")
echo "seaborn: ${SEABORN_VER}" | tee -a "$LOG_FILE"

if [ -d "${PROJECT_ROOT}/exqutor" ]; then
  echo "Exqutor: 클론됨" | tee -a "$LOG_FILE"
else
  echo "Exqutor: 미클론" | tee -a "$LOG_FILE"
fi

DISK_FREE=$(df -h "$PROJECT_ROOT" | tail -1 | awk '{print $4}')
echo "디스크 여유: ${DISK_FREE}" | tee -a "$LOG_FILE"

# 실험 디렉토리 존재 확인
for d in experiments experiments/data experiments/results experiments/scripts experiments/logs experiments/figures; do
  if [ -d "${PROJECT_ROOT}/${d}" ]; then
    echo "${d}/: 존재" | tee -a "$LOG_FILE"
  else
    echo "${d}/: 미생성" | tee -a "$LOG_FILE"
  fi
done

# Phase 1 판단
NEED_SETUP=false
echo "$PGVEC" | grep -q "미설치" && NEED_SETUP=true
echo "$DUCKDB_VER" | grep -q "미설치" && NEED_SETUP=true
echo "$NUMPY_VER" | grep -q "미설치" && NEED_SETUP=true
echo "$FAISS_VER" | grep -q "미설치" && NEED_SETUP=true

echo "" | tee -a "$LOG_FILE"
if [ "$NEED_SETUP" = true ]; then
  echo "⚠️ 미설치 항목 있음 — Phase 1(환경 구축)이 필요합니다." | tee -a "$LOG_FILE"
  echo "Claude에게 위임: guideline/실험지침_auto.md Phase 1 실행" | tee -a "$LOG_FILE"
else
  echo "✅ 환경 구축 완료 — Phase 1 스킵 가능" | tee -a "$LOG_FILE"
fi

# Phase 2: 데이터셋 확인
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 2: 데이터셋 확인 ---" | tee -a "$LOG_FILE"

if [ -d "${PROJECT_ROOT}/experiments/data" ]; then
  DATA_COUNT=$(ls "${PROJECT_ROOT}/experiments/data/" 2>/dev/null | wc -l | tr -d ' ')
  echo "experiments/data/ 파일 수: ${DATA_COUNT}" | tee -a "$LOG_FILE"
  ls "${PROJECT_ROOT}/experiments/data/" 2>/dev/null | head -20 | tee -a "$LOG_FILE"
else
  echo "experiments/data/ 미생성" | tee -a "$LOG_FILE"
fi

# Phase 3~5: 기존 결과 확인
echo "" | tee -a "$LOG_FILE"
echo "--- 기존 실험 결과 확인 ---" | tee -a "$LOG_FILE"

RESULT_COUNT=0
if [ -d "${PROJECT_ROOT}/experiments/results" ]; then
  RESULT_COUNT=$(ls "${PROJECT_ROOT}/experiments/results/"*.csv 2>/dev/null | wc -l | tr -d ' ')
fi
echo "결과 CSV: ${RESULT_COUNT}건" | tee -a "$LOG_FILE"

FIGURE_COUNT=0
if [ -d "${PROJECT_ROOT}/experiments/figures" ]; then
  FIGURE_COUNT=$(ls "${PROJECT_ROOT}/experiments/figures/"*.png 2>/dev/null | wc -l | tr -d ' ')
fi
echo "차트: ${FIGURE_COUNT}건" | tee -a "$LOG_FILE"

LOG_COUNT=0
if [ -d "${PROJECT_ROOT}/experiments/logs" ]; then
  LOG_COUNT=$(ls "${PROJECT_ROOT}/experiments/logs/"*.md 2>/dev/null | wc -l | tr -d ' ')
fi
echo "실험 로그: ${LOG_COUNT}건" | tee -a "$LOG_FILE"

# 종합 리포트
echo "" | tee -a "$LOG_FILE"
echo "--- 종합 리포트 ---" | tee -a "$LOG_FILE"
echo "| 항목             | 상태 |" | tee -a "$LOG_FILE"
echo "|------------------|------|" | tee -a "$LOG_FILE"

if [ "$NEED_SETUP" = true ]; then
  echo "| 환경 구축        | ⚠️ 미완 |" | tee -a "$LOG_FILE"
else
  echo "| 환경 구축        | ✅ 완료 |" | tee -a "$LOG_FILE"
fi

if [ "$DATA_COUNT" -gt 0 ] 2>/dev/null; then
  echo "| 데이터셋         | ✅ ${DATA_COUNT}건 |" | tee -a "$LOG_FILE"
else
  echo "| 데이터셋         | ⬜ 미준비 |" | tee -a "$LOG_FILE"
fi

echo "| 벤치마크 결과    | ${RESULT_COUNT}건 CSV |" | tee -a "$LOG_FILE"
echo "| 시각화 차트      | ${FIGURE_COUNT}건 |" | tee -a "$LOG_FILE"
echo "| 실험 로그        | ${LOG_COUNT}건 |" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== 실험지침 완료: $(date) ===" | tee -a "$LOG_FILE"
echo "상세 로그: ${LOG_FILE}"

# Claude Code 연동 (전체 Phase를 Claude에게 위임할 경우)
# claude --print "guideline/실험지침_auto.md 읽고 전체 Phase 실행" 2>&1 | tee -a "$LOG_FILE"
